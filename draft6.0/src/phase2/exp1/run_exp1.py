"""
Experiment P2.1 — the normalization x goodness grid (the make-or-break gate).

The one question: can a different norm and/or goodness make SCFF separability RISE with depth
(depth-slope < 0 -> >= 0), and does the substrate-feasible (per-sample / online) cell keep the gain?
P2.0 routed us here (verdict LOST, cause = both axes: squared-goodness deactivation + length-norm
rank-collapse). All cells run under the THRESHOLD-FREE CONTRAST loss (a shared theta does not transfer
across cells — linear goodness sits at G~35, saturating theta=2.0 to a dead loss; experiment-0.md).

The FOCUSED 9-cell grid (decided 2026-06-21; not the full 12-cell factorial):
  1 len+sq      length-norm + squared   THE WALL (P2.0 baseline, the line to beat)
  2 len+lin     length-norm + linear    goodness swap ALONE (norm held = wall)
  3 layer+lin   layer-norm  + linear     THE HERO (substrate-native, predicted winner; DeeperForward/ASGE)
  4 layer+sq    layer-norm  + squared    norm swap ALONE (goodness held = wall)
  5 group+lin   group-norm  + linear     per-sample, finer-grained
  6 obn+lin     online-BN   + linear     SUBSTRATE HERO CANDIDATE (running-stats, batch-1)
  7 bbn+lin     batch-norm  + linear     GPU reference for #6 (the online-vs-batch gap = Q2)
  8 bbn+sq      batch-norm  + squared    the TRIFECTA route (GPU ref)
  9 none+lin    no-norm     + linear     cheat/fail control (should collapse)

Per seed, per task: each cell -> per-layer probe (F3+), dead-units, effective-rank, Fisher, NCC,
goodness-gap (REPR/INV). Plus: a WALL_REF (length+squared+TWO-SIDED theta=2.0, exactly P2.0's wall) as
a regression guard + the historical reference line; the GD-hidden envelope (flat-high reference); CKA
layer x layer for wall vs hero; the online-vs-batch final-probe gap (Q2). Then a LIGHT continual preview
(winner cell only, vs wall + online-BN) on digits — the early veto catch (Continual-Norm predicts BN rots).

5 seeds [42,137,271,314,1729], median + IQR. Saves arrays.npz + manifest.json; plot_exp1.py regenerates.
Run:  python run_exp1.py cifar     (headline; the only surface with a real wall)
      python run_exp1.py synth     (dial / fast sanity; P2.0 proved synth is flat)
      add --quick for 2 seeds, --no-cont to skip the continual preview.
"""
from __future__ import annotations
import json, os, subprocess, sys, time, warnings
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)  # probe lbfgs cap is fine; keep logs clean
warnings.filterwarnings("ignore", category=RuntimeWarning)      # no-norm cheat-control overflows (handled
#                                                                 via the finite-check in cell_metrics)

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra (MLP, match_width)
from p2lib import SCFF2, probe_per_layer, probe_one, effective_rank, make_tierb, EPS  # noqa: E402
from models_extra import MLP, match_width                                             # noqa: E402

# CIFAR-10-flat parsed from the locally-cached OpenML ARFF.gz (fetch_openml is broken on this machine:
# truncated download -> md5 mismatch). Replicated from exp0/run_exp0.py (avoids the run_exp0 name clash
# with phase1/exp0). A depth PROBE, not a benchmark claim (README s2). Returns X in [0,1] [N,3072], Y [N].
_CIFAR_GZ = os.path.expanduser(
    "~/scikit_learn_data/openml/openml.org/data/v1/download/16797613/CIFAR_10.arff.gz")
_CIFAR_CACHE = None


def load_cifar_local(path=_CIFAR_GZ):
    global _CIFAR_CACHE
    if _CIFAR_CACHE is not None:
        return _CIFAR_CACHE
    import gzip
    if not os.path.exists(path):
        raise FileNotFoundError(f"CIFAR cache missing at {path} (point load_cifar_local at a CIFAR_10.arff.gz)")
    X = np.empty((30000, 3072), dtype=np.float32); Y = np.empty(30000, dtype=np.int64); i = 0
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        indata = False
        for line in f:
            if not indata:
                if line.strip().lower() == "@data":
                    indata = True
                continue
            vals = line.rstrip("\n").split(",")
            if len(vals) != 3073:
                continue
            X[i] = np.array(vals[:3072], dtype=np.float32); Y[i] = int(vals[3072]); i += 1
    X = X[:i]; Y = Y[:i]; X /= 255.0
    _CIFAR_CACHE = (X, Y)
    return _CIFAR_CACHE

SEEDS = [42, 137, 271, 314, 1729]
L, WIDTH, BATCH = 8, 64, 32

# (key, label, norm, goodness) — all under contrast loss; key is the npz suffix / plot id
CELLS = [
    ("c1_lensq",   "len+sq (wall)",      "lengthnorm", "squared"),
    ("c2_lenlin",  "len+lin",            "lengthnorm", "linear"),
    ("c3_layerlin", "layer+lin (HERO)",  "layernorm",  "linear"),
    ("c4_layersq", "layer+sq",           "layernorm",  "squared"),
    ("c5_grouplin", "group+lin",         "groupnorm",  "linear"),
    ("c6_obnlin",  "onlineBN+lin (HERO)", "online_bn", "linear"),
    ("c7_bbnlin",  "batchBN+lin (ref)",  "batchnorm",  "linear"),
    ("c8_bbnsq",   "batchBN+sq (Trifecta)", "batchnorm", "squared"),
    ("c9_nonelin", "none+lin (cheat)",   "none",       "linear"),
]
HERO_KEYS = ("c3_layerlin", "c6_obnlin")     # bold per result-format (substrate-feasible)
WALL_KEY = "c1_lensq"

CFG = {
    "synth": dict(n_train=6000, n_test=2000, scff_ep=30, gd_ep=60,
                  task=dict(dim=20, grid=4, n_active=2, overlap=0.30, label="random", n_class=2)),
    "cifar": dict(n_train=5000, n_test=2000, scff_ep=20, gd_ep=40, task=None),
}


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# ----------------------------------------------------------------------------- data
def load_task(name, seed):
    c = CFG[name]
    if name == "synth":
        t = c["task"]
        Xtr, Ytr = make_tierb(c["n_train"], np.random.default_rng(seed + 1), **t)
        Xte, Yte = make_tierb(c["n_test"], np.random.default_rng(seed + 2), **t)
        return Xtr, Ytr, Xte, Yte, int(t["n_class"]), Xtr.shape[1]
    if name == "cifar":
        X, Y = load_cifar_local()
        rng = np.random.default_rng(seed)
        idx = rng.permutation(len(X))
        tr, te = idx[:c["n_train"]], idx[c["n_train"]:c["n_train"] + c["n_test"]]
        return (X[tr].astype(np.float64), Y[tr], X[te].astype(np.float64), Y[te],
                int(Y.max() + 1), X.shape[1])
    raise ValueError(name)


# ----------------------------------------------------------------------------- metrics (result-format Layer B)
def fisher_ratio(F, Y):
    """tr(S_B)/tr(S_W): between- / within-class scatter — class separability margin, per layer."""
    mu = F.mean(0); sb = sw = 0.0
    for c in np.unique(Y):
        Fc = F[Y == c]; muc = Fc.mean(0)
        sb += len(Fc) * float(np.sum((muc - mu) ** 2))
        sw += float(np.sum((Fc - muc) ** 2))
    return sb / (sw + EPS)


def ncc_acc(Ftr, Ytr, Fte, Yte):
    """Nearest-class-mean accuracy — degree of neural collapse / how cleanly classes cluster."""
    cls = np.unique(Ytr)
    means = np.stack([Ftr[Ytr == c].mean(0) for c in cls])
    d = ((Fte[:, None, :] - means[None, :, :]) ** 2).sum(2)
    return float((cls[d.argmin(1)] == Yte).mean())


def linear_cka(X, Y):
    X = X - X.mean(0); Y = Y - Y.mean(0)
    num = np.linalg.norm(Y.T @ X) ** 2
    den = np.linalg.norm(X.T @ X) * np.linalg.norm(Y.T @ Y)
    return float(num / (den + EPS))


def cka_matrix(reps):
    Lr = len(reps); M = np.zeros((Lr, Lr))
    for i in range(Lr):
        for j in range(i, Lr):
            M[i, j] = M[j, i] = linear_cka(reps[i], reps[j])
    return M


# ----------------------------------------------------------------------------- train helpers
def train_scff(dims, norm, goodness, objective, Xtr, seed, epochs, theta=2.0):
    m = SCFF2(dims, seed=seed, objective=objective, goodness=goodness, norm=norm, theta=theta)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], rng)
    return m


def train_mlp(dims, Xtr, Ytr, Xte, Yte, seed, epochs, lr=1e-3):
    m = MLP(dims, seed, lr=lr); rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    return m, float(m.accuracy(Xte, Yte))


def gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte):
    gd.forward(Xtr); htr = [a.copy() for a in gd.cache[1:]]
    gd.forward(Xte); hte = [a.copy() for a in gd.cache[1:]]
    return [probe_one(a, Ytr, b, Yte) for a, b in zip(htr, hte)]


def n_w(dims):
    return sum((dims[i] + 1) * dims[i + 1] for i in range(len(dims) - 1))


def cell_metrics(m, Xtr, Ytr, Xte, Yte, C):
    """All per-layer reads for one trained SCFF cell. A diverged cell (no-norm overflows to NaN — the
    expected cheat-control failure) is recorded at chance, not allowed to crash the grid."""
    rtr, rte = m.infer(Xtr), m.infer(Xte)
    if not all(np.all(np.isfinite(a)) for a in rtr + rte):
        Lr = len(rte); ch = 1.0 / C
        return dict(probe=[ch] * Lr, fisher=[0.0] * Lr, ncc=[ch] * Lr,
                    erank=[0.0] * Lr, dead=[1.0] * Lr, gap=[0.0] * Lr, diverged=1.0)
    probe = [float(LogisticRegression(C=1.0, max_iter=3000).fit(a, Ytr).score(b, Yte))
             for a, b in zip(rtr, rte)]
    fisher = [fisher_ratio(b, Yte) for b in rte]
    ncc = [ncc_acc(a, Ytr, b, Yte) for a, b in zip(rtr, rte)]
    erank = [effective_rank(b) for b in rte]
    dead = m.dead_fraction(Xte).tolist()
    gap = m.goodness_gap(Xte).tolist()
    return dict(probe=probe, fisher=fisher, ncc=ncc, erank=erank, dead=dead, gap=gap, diverged=0.0)


# ----------------------------------------------------------------------------- light continual preview
def load_digits_cont(seed, n_train=1200, n_test=600):
    from sklearn.datasets import load_digits
    d = load_digits(); X = d.data / 16.0; Y = d.target
    rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    tr, te = idx[:n_train], idx[n_train:n_train + n_test]
    return X[tr], Y[tr], X[te], Y[te]


def continual_scff_probe(norm, goodness, seed, tasks=((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))):
    """Class-incremental stream (exp4 setup, light). Returns the SCFF all-class linear-probe trajectory
    over tasks — the BWT sniff: does this norm's SCFF FORGET as the stream shifts? (Continual-Norm
    predicts batch/online-BN rot under task shift; per-sample norms stay flat.)"""
    Xtr, Ytr, Xte, Yte = load_digits_cont(seed)
    D = Xtr.shape[1]
    m = SCFF2([D] + [WIDTH] * 4, seed=seed, objective="contrast", goodness=goodness, norm=norm)
    rng = np.random.default_rng(seed)
    pr = rng.permutation(len(Xtr))[:800]; Xpr, Ypr = Xtr[pr], Ytr[pr]  # fixed all-class probe-fit set
    traj = []
    for cls in tasks:
        msk = np.isin(Ytr, cls); Xt = Xtr[msk]
        for _ in range(8):
            idx = rng.permutation(len(Xt))
            for s in range(0, len(Xt), BATCH):
                m.train_step(Xt[idx[s:s + BATCH]], rng)
        clf = LogisticRegression(C=1.0, max_iter=2000).fit(np.concatenate(m.infer(Xpr), 1), Ypr)
        traj.append(float(clf.score(np.concatenate(m.infer(Xte), 1), Yte)))
    return traj  # [n_tasks]


# ----------------------------------------------------------------------------- one seed (the grid)
def run_seed(name, seed):
    c = CFG[name]
    Xtr, Ytr, Xte, Yte, C, D = load_task(name, seed)
    out = {"C": C, "D": D}
    dims = [D] + [WIDTH] * L

    # the 9 grid cells (contrast loss)
    for key, _lab, norm, good in CELLS:
        m = train_scff(dims, norm, good, "contrast", Xtr, seed, c["scff_ep"])
        met = cell_metrics(m, Xtr, Ytr, Xte, Yte, C)
        for mk, mv in met.items():
            out[f"{mk}_{key}"] = mv
        if key == WALL_KEY:
            out["cka_wall"] = cka_matrix(m.infer(Xte))
        if key == "c3_layerlin":
            out["cka_hero"] = cka_matrix(m.infer(Xte))

    # WALL_REF — exactly P2.0's wall (length+squared, TWO-SIDED theta=2.0): regression guard + ref line
    wref = train_scff(dims, "lengthnorm", "squared", "two_sided", Xtr, seed, c["scff_ep"], theta=2.0)
    out["wall_ref_probe"] = probe_per_layer(wref, Xtr, Ytr, Xte, Yte)

    # GD-hidden envelope (flat-high reference), matched depth + budget (exp-1 / P2.0 format)
    scff_budget = n_w(dims) + (L * WIDTH * C + C)
    w, _ = match_width(scff_budget, D, C, L)
    gd, out["gd_held"] = train_mlp([D] + [w] * L + [C], Xtr, Ytr, Xte, Yte, seed, c["gd_ep"])
    out["gd_perlayer"] = gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte)
    out["gd_width"] = w
    return out


def slope(v):
    return float(np.polyfit(np.arange(1, len(v) + 1), v, 1)[0])


# ----------------------------------------------------------------------------- aggregate + report
def main():
    name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "cifar"
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    do_cont = "--no-cont" not in sys.argv
    t0 = time.time()
    print(f"=== P2.1 [{name}] norm x goodness grid (9 cells, contrast loss) | seeds={seeds} ===", flush=True)
    runs = []
    for s in seeds:
        r = run_seed(name, s); runs.append(r)
        msg = "  seed %d:" % s
        for key, lab, _n, _g in CELLS:
            pr = r[f"probe_{key}"]; msg += f" {key.split('_')[0]}={pr[0]:.2f}->{pr[-1]:.2f}"
        print(msg + f" | GD {r['gd_held']:.3f}", flush=True)

    def st(k): return np.array([r[k] for r in runs])

    print(f"\n--- P2.1 [{name}] median, n={len(seeds)} ---")
    print(f"  {'cell':24s} {'L1->L8 probe':>16s} {'slope/layer':>12s} {'final[IQR]':>16s} "
          f"{'dead L8':>8s} {'erank L8':>9s}")
    cell_slopes = {}
    for key, lab, norm, good in CELLS:
        P = st(f"probe_{key}"); med = np.median(P, 0); sl = slope(med)
        cell_slopes[key] = sl
        fin = P[:, -1]
        dead = np.median(st(f"dead_{key}"), 0)[-1]; er = np.median(st(f"erank_{key}"), 0)[-1]
        flag = "  <-- slope>=0" if sl >= 0 else ""
        print(f"  {lab:24s} {med[0]:.3f}->{med[-1]:.3f}   {sl:+.4f}   "
              f"{np.median(fin):.3f}[{np.percentile(fin,25):.3f},{np.percentile(fin,75):.3f}]  "
              f"{dead:6.2f}   {er:7.1f}{flag}")
    wref = np.median(st("wall_ref_probe"), 0)
    gdpl = np.median(st("gd_perlayer"), 0)
    env_gap = float(np.median(gdpl) - np.median(wref))
    print(f"  {'WALL_REF (P2.0 two-sided)':24s} {wref[0]:.3f}->{wref[-1]:.3f}   {slope(wref):+.4f}"
          f"   (regression guard: should DECLINE on cifar)")
    print(f"  GD-hidden envelope median {np.round(gdpl,3)}  (gap vs WALL_REF {env_gap:+.3f})")

    # Q2 — online-vs-batch final-layer probe gap (does going single-sample forfeit the gain?)
    obn = np.median(st("probe_c6_obnlin")[:, -1]); bbn = np.median(st("probe_c7_bbnlin")[:, -1])
    print(f"  Q2 online-vs-batch (linear): online-BN {obn:.3f} vs batch-BN {bbn:.3f} "
          f"-> gap {obn-bbn:+.3f} (pass if |gap|<=0.03)")

    # the make-or-break verdict. CRITICAL: a COLLAPSED cell (learns nothing — flat at chance because
    # every unit died, e.g. squared goodness under a mean-zero norm) has slope ~0 and would FALSELY
    # "pass" the >=0 gate. A real pass must LEARN (final probe > chance) AND have slope >= 0.
    chance = 1.0 / max(int(np.median(st("C"))), 2)
    per_sample = {"c1_lensq", "c2_lenlin", "c3_layerlin", "c4_layersq", "c5_grouplin", "c9_nonelin"}

    def collapsed(k):
        fin = float(np.median(st(f"probe_{k}")[:, -1]))
        dead = float(np.median(st(f"dead_{k}"), 0)[-1]) if f"dead_{k}" in runs[0] else 0.0
        return fin <= chance + 0.02 or dead >= 0.99
    learning = [k for k, *_ in CELLS if not collapsed(k)]
    dead_cells = [k for k, *_ in CELLS if collapsed(k)]
    passed = [k for k in learning if cell_slopes[k] >= 0]   # genuine pass: learns AND non-declining
    winner = max(passed, key=lambda k: (np.median(st(f"probe_{k}")[:, -1]), k in per_sample)) \
        if passed else None
    print(f"\n  collapsed (chance/dead, excluded): {dead_cells or 'none'}")
    print(f"  PASS GATE: LEARNING cells with slope>=0 = {passed or 'NONE'}")
    print(f"  -> {'WINNER ' + winner if winner else 'NO LEARNING CELL BENT THE WALL UP -> STOP (README s5)'}")

    # ---- light continual preview (winner vs wall vs online-BN) ----
    cont = {}
    if do_cont and winner:
        cont_cfgs = {WALL_KEY: ("lengthnorm", "squared"), winner: None, "c6_obnlin": ("online_bn", "linear")}
        cont_cfgs[winner] = next((n, g) for k, l, n, g in CELLS if k == winner)
        cseeds = seeds[:3]
        print(f"\n  --- continual preview (digits, class-incremental, n={len(cseeds)}) ---")
        for key, (norm, good) in cont_cfgs.items():
            T = np.array([continual_scff_probe(norm, good, s) for s in cseeds])
            cont[f"cont_{key}"] = T
            med = np.median(T, 0)
            bwt = float(med[-1] - med.max())   # crude BWT sniff: final vs best-seen all-class probe
            print(f"    {key:12s} ({norm}+{good}) traj {np.round(med,3)}  final {med[-1]:.3f}  bwt~{bwt:+.3f}")

    # ---- save ----
    OUT = os.path.join(_HERE, f"figs_exp1_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {}
    for r0key in runs[0].keys():
        if r0key in ("gd_width",):
            continue
        try:
            saved[r0key] = st(r0key)
        except Exception:
            pass
    for k, v in cont.items():
        saved[k] = v
    saved["seeds"] = np.array(seeds); saved["L"] = L; saved["width"] = WIDTH
    saved["cell_keys"] = np.array([k for k, *_ in CELLS])
    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in saved.items()})

    manifest = {
        "experiment": f"exp1-{name}", "git_commit": _git(), "seeds": list(seeds), "task": name,
        "config": CFG[name], "L": L, "width": WIDTH, "batch": BATCH, "loss": "contrast",
        "cells": [{"key": k, "label": l, "norm": n, "goodness": g} for k, l, n, g in CELLS],
        "results_median": {
            "cell_slopes": {k: cell_slopes[k] for k in cell_slopes},
            "cell_final_probe": {k: float(np.median(st(f"probe_{k}")[:, -1])) for k, *_ in CELLS},
            "wall_ref_slope": slope(wref), "envelope_gap": env_gap,
            "q2_online_minus_batch": float(obn - bbn),
            "slope_pass_cells": passed, "winner": winner},
        "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

    try:
        import plot_exp1
        plot_exp1.draw_all(np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True), name, OUT)
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {manifest['git_commit'][:8]})")


if __name__ == "__main__":
    main()
