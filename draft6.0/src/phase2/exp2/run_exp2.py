"""
Experiment P2.2 — the objective: can CLASS-AWARE (hard) negatives build depth where transmission couldn't?

P2.1 closed the transmission axis (norm x goodness fixes the mechanism but not depth — the bottleneck is the
OBJECTIVE: SCFF clusters by density, not class). P2.2 is the DECISIVE rung (README s5): vary ONLY the negative
partner, on P2.1's healthy transmission baseline (layer-norm + linear + contrast), and ask whether a between-
class negative makes per-layer separability RISE with depth (slope -> >= 0) and lift the final probe.

The SCFF rule: x_pos = 2*x_k (coherent) ; x_neg = x_k + partner (a mixture, low goodness). Only the partner
changes (one variable):
  random      — any sample (the P2.1 ~baseline; mixture = density-agnostic)
  hard_oracle — a different TRUE-class sample (mixture = between-class -> the MECHANISM upper-bound)
  hard_proto  — a different-class MEAN (clean prototype vs a noisy sample)
  hard_unsup  — a different KMeans-cluster sample (the SUBSTRATE version, no labels; LUT is the online variant)

The decisive controls: hard_oracle answers "is the objective the lever?" (perfect class-aware negatives);
hard_unsup answers "can we get it unsupervised?" (cluster purity logged — on flat CIFAR the clustering is
itself density-based, the density!=class trap one level up). If even ORACLE can't bend the slope -> depth is
NOT the lever -> Phase-1 fallback (shallow + boosted blocks, P2.5).

5 seeds, median + IQR. Reuses run_exp1 metrics + p2lib. Saves arrays.npz + manifest.json; plot_exp2 regenerates.
Run:  python run_exp2.py cifar    (headline)
      python run_exp2.py synth    (sanity)   add --quick for 2 seeds.
"""
from __future__ import annotations
import json, os, subprocess, sys, time, warnings
import numpy as np
from sklearn.cluster import KMeans
warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))            # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "exp1"))    # run_exp1 helpers
from p2lib import SCFF2, make_tierb, probe_per_layer      # noqa: E402
from run_exp1 import (cell_metrics, train_mlp, gd_hidden_probe, n_w, load_cifar_local,  # noqa: E402
                      slope, match_width)

SEEDS = [42, 137, 271, 314, 1729]
L, WIDTH, BATCH = 8, 64, 32
TRANS = dict(norm="layernorm", goodness="linear", objective="contrast")   # P2.1 healthy baseline (FIXED)
NEG_CELLS = [
    ("random",      "random (P2.1 base)"),
    ("hard_oracle", "hard-oracle (diff TRUE class)"),
    ("hard_proto",  "hard-proto (diff class MEAN)"),
    ("hard_unsup",  "hard-unsup (diff KMeans cluster)"),
]
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


def load_task(name, seed):
    c = CFG[name]
    if name == "synth":
        t = c["task"]
        Xtr, Ytr = make_tierb(c["n_train"], np.random.default_rng(seed + 1), **t)
        Xte, Yte = make_tierb(c["n_test"], np.random.default_rng(seed + 2), **t)
        return Xtr, Ytr, Xte, Yte, int(t["n_class"]), Xtr.shape[1]
    X, Y = load_cifar_local()
    rng = np.random.default_rng(seed); idx = rng.permutation(len(X))
    tr, te = idx[:c["n_train"]], idx[c["n_train"]:c["n_train"] + c["n_test"]]
    return (X[tr].astype(np.float64), Y[tr], X[te].astype(np.float64), Y[te], int(Y.max() + 1), X.shape[1])


# ----------------------------------------------------------------------------- negative-partner samplers
def diff_label_partner(labels, rng):
    """For each i, the index of a random sample with a DIFFERENT label (rejection-sampled, vectorized)."""
    n = len(labels); part = rng.integers(0, n, n); bad = labels[part] == labels
    while bad.any():
        part[bad] = rng.integers(0, n, int(bad.sum())); bad = labels[part] == labels
    return part


def diff_class_ids(labels, classes, rng):
    """For each i, a random class id != labels[i] (for the prototype/mean partner)."""
    out = rng.choice(classes, len(labels)); bad = out == labels
    while bad.any():
        out[bad] = rng.choice(classes, int(bad.sum())); bad = out == labels
    return out


def make_partners(mode, Xtr, Ytr, clabels, cmeans, classes, rng):
    """Return the [n, D] negative-partner array for one epoch (fresh draw). Whole-set pool; only the
    CONSTRAINT differs across modes (clean one-variable comparison)."""
    n = len(Xtr)
    if mode == "random":
        return Xtr[rng.integers(0, n, n)]
    if mode == "hard_oracle":
        return Xtr[diff_label_partner(Ytr, rng)]
    if mode == "hard_unsup":
        return Xtr[diff_label_partner(clabels, rng)]
    if mode == "hard_proto":
        return cmeans[diff_class_ids(Ytr, classes, rng)]
    raise ValueError(mode)


def cluster_purity(clabels, Y):
    """Avg majority-true-class fraction per cluster — how class-aligned the unsupervised clustering is."""
    return float(sum(np.bincount(Y[clabels == c]).max() for c in np.unique(clabels)) / len(Y))


def train_scff_neg(dims, mode, Xtr, Ytr, clabels, cmeans, classes, seed, epochs):
    m = SCFF2(dims, seed=seed, **TRANS)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        partners = make_partners(mode, Xtr, Ytr, clabels, cmeans, classes, rng)   # [n,D] this epoch
        for s in range(0, len(Xtr), BATCH):
            b = idx[s:s + BATCH]
            m.train_step(Xtr[b], rng, neg_partner=partners[b])
    return m


def train_wall_ref(dims, Xtr, seed, epochs):
    """P2.0's exact wall (length+squared, two-sided theta=2.0) — the historical reference line."""
    m = SCFF2(dims, seed=seed, norm="lengthnorm", goodness="squared", objective="two_sided", theta=2.0)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], rng)
    return m


# ----------------------------------------------------------------------------- one seed
def run_seed(name, seed):
    c = CFG[name]
    Xtr, Ytr, Xte, Yte, C, D = load_task(name, seed)
    classes = np.unique(Ytr)
    cmeans = np.stack([Xtr[Ytr == k].mean(0) for k in range(C)])   # class means, indexed by class id (0..C-1)
    km = KMeans(n_clusters=C, n_init=4, random_state=seed).fit(Xtr)
    clabels = km.labels_
    out = {"C": C, "D": D, "purity": cluster_purity(clabels, Ytr)}
    dims = [D] + [WIDTH] * L
    print(f"    [seed {seed}] KMeans done (purity {out['purity']:.2f})", flush=True)   # progress beacon

    for key, _lab in NEG_CELLS:
        m = train_scff_neg(dims, key, Xtr, Ytr, clabels, cmeans, classes, seed, c["scff_ep"])
        for mk, mv in cell_metrics(m, Xtr, Ytr, Xte, Yte, C).items():
            out[f"{mk}_{key}"] = mv
        print(f"    [seed {seed}] cell {key} done", flush=True)   # per-cell progress (stall = visible)

    wref = train_wall_ref(dims, Xtr, seed, c["scff_ep"])
    out["wall_ref_probe"] = probe_per_layer(wref, Xtr, Ytr, Xte, Yte)

    scff_budget = n_w(dims) + (L * WIDTH * C + C)
    w, _ = match_width(scff_budget, D, C, L)
    gd, out["gd_held"] = train_mlp([D] + [w] * L + [C], Xtr, Ytr, Xte, Yte, seed, c["gd_ep"])
    out["gd_perlayer"] = gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte)
    return out


# ----------------------------------------------------------------------------- aggregate + report
def main():
    name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "cifar"
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    t0 = time.time()
    print(f"=== P2.2 [{name}] negative-quality grid on layer-norm+linear+contrast | seeds={seeds} ===", flush=True)
    runs = []
    for s in seeds:
        r = run_seed(name, s); runs.append(r)
        msg = f"  seed {s} (purity {r['purity']:.2f}):"
        for key, _l in NEG_CELLS:
            pr = r[f"probe_{key}"]; msg += f" {key.split('_')[-1][:5]}={pr[0]:.2f}->{pr[-1]:.2f}"
        print(msg + f" | GD {r['gd_held']:.3f}", flush=True)

    def st(k): return np.array([r[k] for r in runs])
    chance = 1.0 / max(int(np.median(st("C"))), 2)

    print(f"\n--- P2.2 [{name}] median, n={len(seeds)} ---  (KMeans cluster purity {np.median(st('purity')):.3f})")
    print(f"  {'negative':30s} {'L1->L8':>14s} {'slope':>9s} {'final[IQR]':>16s} {'dead L8':>8s} {'erank L8':>9s}")
    base_final = np.median(st("probe_random")[:, -1])
    cell_slope = {}
    for key, lab in NEG_CELLS:
        P = st(f"probe_{key}"); med = np.median(P, 0); sl = slope(med); cell_slope[key] = sl
        fin = P[:, -1]
        dead = np.median(st(f"dead_{key}"), 0)[-1]; er = np.median(st(f"erank_{key}"), 0)[-1]
        flag = "  <-- slope>=0" if sl >= 0 else ""
        print(f"  {lab:30s} {med[0]:.3f}->{med[-1]:.3f}  {sl:+.4f}  "
              f"{np.median(fin):.3f}[{np.percentile(fin,25):.3f},{np.percentile(fin,75):.3f}] "
              f"{dead:6.2f}  {er:7.1f}{flag}")
    wref = np.median(st("wall_ref_probe"), 0); gdpl = np.median(st("gd_perlayer"), 0)
    print(f"  {'WALL_REF (P2.0 two-sided)':30s} {wref[0]:.3f}->{wref[-1]:.3f}  {slope(wref):+.4f}")
    print(f"  GD-hidden envelope {np.round(gdpl,3)} (gap vs wall_ref {np.median(gdpl)-np.median(wref):+.3f})")

    # the two gates
    def lift(key):  # final-probe lift over random, with disjoint-IQR test
        a = st(f"probe_{key}")[:, -1]; b = st("probe_random")[:, -1]
        return float(np.median(a) - np.median(b)), float(np.percentile(a, 25) - np.percentile(b, 75))
    print("\n  --- gates ---")
    for key, lab in NEG_CELLS[1:]:
        d, dj = lift(key)
        print(f"  {lab:30s} probe-lift vs random {d:+.3f} (disjoint-IQR margin {dj:+.3f}; >0 = real) | "
              f"slope {cell_slope[key]:+.4f} {'>=0 RISES' if cell_slope[key] >= 0 else 'still declines'}")
    oracle_slope = cell_slope["hard_oracle"]
    oracle_lift, oracle_dj = lift("hard_oracle")
    if oracle_slope >= 0:
        verdict = "OBJECTIVE IS THE LEVER (oracle bends slope>=0) -> test unsup feasibility"
    elif oracle_dj > 0:
        verdict = "objective LIFTS probe (disjoint-IQR) but slope still <0 -> partial; weigh vs P2.5 fallback"
    else:
        verdict = "even ORACLE fails (no lift, slope<0) -> DEPTH IS NOT THE LEVER -> Phase-1 fallback (P2.5)"
    print(f"\n  VERDICT: {verdict}")

    OUT = os.path.join(_HERE, f"figs_exp2_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {}
    for k in runs[0].keys():
        try:
            saved[k] = st(k)
        except Exception:
            pass
    saved["seeds"] = np.array(seeds); saved["L"] = L; saved["width"] = WIDTH
    saved["neg_keys"] = np.array([k for k, _ in NEG_CELLS])
    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in saved.items()})
    manifest = {"experiment": f"exp2-{name}", "git_commit": _git(), "seeds": list(seeds), "task": name,
                "config": CFG[name], "transmission": TRANS, "L": L, "width": WIDTH,
                "neg_cells": [{"key": k, "label": l} for k, l in NEG_CELLS],
                "results_median": {
                    "cluster_purity": float(np.median(st("purity"))),
                    "cell_slopes": {k: cell_slope[k] for k in cell_slope},
                    "cell_final": {k: float(np.median(st(f"probe_{k}")[:, -1])) for k, _ in NEG_CELLS},
                    "oracle_probe_lift": oracle_lift, "oracle_disjoint_iqr": oracle_dj,
                    "verdict": verdict},
                "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_exp2
        plot_exp2.draw_all(np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True), name, OUT)
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {manifest['git_commit'][:8]})")


if __name__ == "__main__":
    main()
