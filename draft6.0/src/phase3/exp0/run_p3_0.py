"""
Experiment P3.0 — the objective swap: does an info-preserving objective stop the depth wall?

Per seed, per task, over the depth stack L=1..8 (width 64), per-layer linear probe (the PRIMARY metric):
  (1) ENERGY-WALL  — p2lib.SCFF2, the P2.1 healthy cell (layer-norm + linear + contrast). The baseline-to-beat
                     (P2.1: slope ~ -0.020 on CIFAR-flat).
  (2) MASKED-RECON — p3lib.SCFFRecon, per-layer masked denoising-AE (the hero). + recon_error (INFOPRESERVE).
  (3) GD-CEILING   — pure-GD MLP, matched depth+budget: per-layer hidden probe (the flat-high envelope).
  (4) RANDOM-FLOOR — an UNTRAINED SCFFRecon (identical arch + layer-norm): the selectivity floor.
SCORECARD per cell: slope, peak-layer, center-of-mass, decline-area, tail-retention, N_eff.
SELECT = masked-recon probe - random-floor probe (does TRAINING add readable info, or is the probe doing it?).

5 seeds [42,137,271,314,1729], median + IQR. Reuses p2lib + p3lib + phase1 models_extra. Saves arrays.npz +
manifest.json; plot.py regenerates every figure.

Run (single-threaded -- OpenMP phantom guard on this machine):
  OMP_NUM_THREADS=1 python -u run_p3_0.py synth        (fast code sanity; synth has NO wall)
  OMP_NUM_THREADS=1 python -u run_p3_0.py cifar         (the headline wall)
  add --quick for 2 seeds.
"""
from __future__ import annotations
import gzip, json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                                              # plot
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p3lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))          # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p2lib import SCFF2, probe_per_layer, probe_one, effective_rank, make_tierb  # noqa: E402
from p3lib import SCFFRecon, SCFFContrast                                        # noqa: E402
from models_extra import MLP, match_width                                        # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
L, WIDTH, BATCH = 8, 64, 32
ENERGY_WALL = dict(norm="layernorm", goodness="linear", objective="contrast")    # the P2.1 healthy cell

CFG = {
    "synth": dict(n_train=6000, n_test=2000, ep=30, gd_ep=60,
                  task=dict(dim=20, grid=4, n_active=2, overlap=0.30, label="random", n_class=2)),
    "cifar": dict(n_train=5000, n_test=2000, ep=20, gd_ep=40, task=None),
    # depth-headroom task (P3.2 scan winner): GD-hidden RISES +0.021 (0.374->0.481) -> depth genuinely helps.
    "headroom": dict(n_train=5000, n_test=1500, ep=30, gd_ep=60,
                     task=dict(grid=4, n_active=3, overlap=0.6, dim=40, label="random", n_class=4)),
}


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# ----------------------------------------------------------------------------- data (port of P2.0)
_CIFAR_CACHE = None
_CIFAR_GZ = os.path.expanduser(
    "~/scikit_learn_data/openml/openml.org/data/v1/download/16797613/CIFAR_10.arff.gz")


def load_cifar_local(path=_CIFAR_GZ):
    global _CIFAR_CACHE
    if _CIFAR_CACHE is not None:
        return _CIFAR_CACHE
    if not os.path.exists(path):
        raise FileNotFoundError(f"CIFAR cache missing at {path} (see P2.0 load_cifar_local note).")
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


def load_task(name, seed):
    c = CFG[name]
    if name != "cifar":                                   # any make_tierb task (synth / headroom / ...)
        t = c["task"]
        Xtr, Ytr = make_tierb(c["n_train"], np.random.default_rng(seed + 1), **t)
        Xte, Yte = make_tierb(c["n_test"], np.random.default_rng(seed + 2), **t)
        return Xtr, Ytr, Xte, Yte, int(t["n_class"]), Xtr.shape[1]
    X, Y = load_cifar_local()
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(X)); tr, te = idx[:c["n_train"]], idx[c["n_train"]:c["n_train"] + c["n_test"]]
    return (X[tr].astype(np.float64), Y[tr], X[te].astype(np.float64), Y[te], int(Y.max() + 1), X.shape[1])


def n_w(dims):
    return sum((dims[i] + 1) * dims[i + 1] for i in range(len(dims) - 1))


# ----------------------------------------------------------------------------- training
def train_energy(dims, Xtr, seed, epochs):
    m = SCFF2(dims, seed=seed, **ENERGY_WALL)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], rng)
    return m


def train_recon(dims, Xtr, seed, epochs):
    m = SCFFRecon(dims, seed=seed, mask_ratio=0.5, norm="layernorm")
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], rng)
    return m


def train_contrast(dims, Xtr, seed, epochs):
    m = SCFFContrast(dims, seed=seed, mask_ratio=0.5, temp=0.5, norm="layernorm")
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:                                  # InfoNCE needs in-batch negatives
                m.train_step(xb, rng)
    return m


def train_mlp(dims, Xtr, Ytr, Xte, Yte, seed, epochs, lr=1e-3):
    m = MLP(dims, seed, lr=lr)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            m.train_step(Xtr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    return m, float(m.accuracy(Xte, Yte))


def gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte):
    gd.forward(Xtr); htr = [a.copy() for a in gd.cache[1:]]
    gd.forward(Xte); hte = [a.copy() for a in gd.cache[1:]]
    return [probe_one(a, Ytr, b, Yte) for a, b in zip(htr, hte)]


# ----------------------------------------------------------------------------- scorecard
def scorecard(probe, chance):
    p = np.asarray(probe, float); Ln = len(p); layers = np.arange(1, Ln + 1)
    slope = float(np.polyfit(layers, p, 1)[0])
    pk = int(np.argmax(p))
    w = np.clip(p - chance, 0.0, None)
    com = float((layers * w).sum() / (w.sum() + 1e-12))
    decline = float(np.clip(p[pk] - p[pk:], 0.0, None).sum() / Ln)          # post-peak degradation, norm by L
    tail_k = max(1, Ln // 4); tail_ret = float(p[-tail_k:].mean() / (p[pk] + 1e-12))
    ww = w / (w.sum() + 1e-12); H = -(ww * np.log(ww + 1e-12)).sum(); neff = float(np.exp(H))
    return dict(slope=slope, peak_l=float(pk + 1), peak=float(p[pk]), com=com,
                decline=decline, tail_ret=tail_ret, neff=neff)


# ----------------------------------------------------------------------------- one seed
def run_seed(name, seed):
    c = CFG[name]
    Xtr, Ytr, Xte, Yte, C, D = load_task(name, seed)
    dims = [D] + [WIDTH] * L
    out = {"C": C, "D": D, "chance": 1.0 / C}

    # (1) ENERGY-WALL
    en = train_energy(dims, Xtr, seed, c["ep"])
    out["energy_probe"] = probe_per_layer(en, Xtr, Ytr, Xte, Yte)
    out["energy_dead"] = en.dead_fraction(Xte).tolist()
    out["energy_erank"] = [effective_rank(a) for a in en.infer(Xte)]

    # (2) MASKED-RECON (the hero)
    rc = train_recon(dims, Xtr, seed, c["ep"])
    out["recon_probe"] = probe_per_layer(rc, Xtr, Ytr, Xte, Yte)
    out["recon_dead"] = rc.dead_fraction(Xte).tolist()
    out["recon_erank"] = [effective_rank(a) for a in rc.infer(Xte)]
    out["recon_err"] = rc.recon_error(Xte).tolist()                          # INFOPRESERVE

    # (2b) CONTRAST (InfoNCE / CLAPP — the discriminative-preservation hero, the P3.0 route)
    ct = train_contrast(dims, Xtr, seed, c["ep"])
    out["contrast_probe"] = probe_per_layer(ct, Xtr, Ytr, Xte, Yte)
    out["contrast_dead"] = ct.dead_fraction(Xte).tolist()
    out["contrast_erank"] = [effective_rank(a) for a in ct.infer(Xte)]

    # (3) GD-CEILING (matched depth + budget) -> per-layer hidden probe (flat-high envelope)
    scff_budget = n_w(dims) + (L * WIDTH * C + C)
    w, _ = match_width(scff_budget, D, C, L)
    gd, out["gd_held"] = train_mlp([D] + [w] * L + [C], Xtr, Ytr, Xte, Yte, seed, c["gd_ep"])
    out["gd_perlayer"] = gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte)

    # (4) RANDOM-FLOOR — untrained SCFFRecon (identical arch + layer-norm): the selectivity floor
    rand = SCFFRecon(dims, seed=seed, norm="layernorm")                      # no training
    out["rand_probe"] = probe_per_layer(rand, Xtr, Ytr, Xte, Yte)

    # selectivity = (objective probe) - random, per layer  -- does TRAINING add class-readable info?
    out["select"] = (np.array(out["recon_probe"]) - np.array(out["rand_probe"])).tolist()       # recon
    out["select_ct"] = (np.array(out["contrast_probe"]) - np.array(out["rand_probe"])).tolist()  # contrast
    return out


# ----------------------------------------------------------------------------- aggregate
def main():
    name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "synth"
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    t0 = time.time()
    print(f"=== P3.0 [{name}] objective swap: energy-wall vs masked-recon | seeds={seeds} ===", flush=True)
    runs = []
    for s in seeds:
        r = run_seed(name, s)
        runs.append(r)
        ep, rp, cp = r["energy_probe"], r["recon_probe"], r["contrast_probe"]
        print(f"  seed {s}: ENERGY {ep[0]:.3f}->{ep[-1]:.3f} | RECON {rp[0]:.3f}->{rp[-1]:.3f}"
              f" (sel {np.mean(r['select']):+.3f}) | CONTRAST {cp[0]:.3f}->{cp[-1]:.3f}"
              f" (sel {np.mean(r['select_ct']):+.3f}) | GD {r['gd_held']:.3f}", flush=True)

    def st(k): return np.array([r[k] for r in runs])
    runs_keys = [k for k in runs[0].keys()]
    chance = float(np.median(st("chance")))

    en_p, rc_p = np.median(st("energy_probe"), 0), np.median(st("recon_probe"), 0)
    ct_p = np.median(st("contrast_probe"), 0)
    gd_p, rd_p = np.median(st("gd_perlayer"), 0), np.median(st("rand_probe"), 0)
    sc_en, sc_rc, sc_ct = scorecard(en_p, chance), scorecard(rc_p, chance), scorecard(ct_p, chance)
    sel, sel_ct = np.median(st("select"), 0), np.median(st("select_ct"), 0)
    env_gap = float(np.median(gd_p) - np.median(en_p))

    print(f"\n--- P3.0 [{name}] median, n={len(seeds)} ---")
    print(f"  ENERGY-WALL  : {np.round(en_p,3)}  slope {sc_en['slope']:+.4f}  decl {sc_en['decline']:.3f}"
          f"  tail {sc_en['tail_ret']:.2f}")
    print(f"  MASKED-RECON : {np.round(rc_p,3)}  slope {sc_rc['slope']:+.4f}  decl {sc_rc['decline']:.3f}"
          f"  tail {sc_rc['tail_ret']:.2f}  sel(mean) {sel.mean():+.3f}")
    print(f"  CONTRAST     : {np.round(ct_p,3)}  slope {sc_ct['slope']:+.4f}  decl {sc_ct['decline']:.3f}"
          f"  tail {sc_ct['tail_ret']:.2f}  peakL {sc_ct['peak_l']:.0f}  CoM {sc_ct['com']:.2f}"
          f"  Neff {sc_ct['neff']:.2f}  sel(mean) {sel_ct.mean():+.3f}")
    print(f"  GD ceiling   : {np.round(gd_p,3)}  (env gap vs wall {env_gap:+.3f})")
    print(f"  RANDOM floor : {np.round(rd_p,3)}")
    print(f"  SELECT recon : {np.round(sel,3)}")
    print(f"  SELECT contr : {np.round(sel_ct,3)}  (peak {sel_ct.max():+.3f}, mean {sel_ct.mean():+.3f})")
    # The HERO is now CONTRAST (the P3.0 route after masked-recon's density fail). Honest two-condition gate:
    # slope must move toward 0 AND the preserved info must be CLASS-relevant (selectivity meaningfully > 0).
    slope_gate = sc_ct["slope"] >= -0.005
    sel_gate = float(sel_ct.mean()) > 0.01
    if slope_gate and sel_gate:
        verdict = "PASS - CONTRASTIVE preservation earns depth (slope flat, selectivity>0) -> route P3.1"
    elif sel_gate and not slope_gate:
        verdict = "PARTIAL - selectivity>0 (class info preserved) but still declining -> coordination (P3.1)"
    elif slope_gate and not sel_gate:
        verdict = "PARTIAL - flat but selectivity<0 (still density) -> rethink the views / Mono-Forward (P3.2)"
    else:
        verdict = "FAIL - contrastive doesn't compose on flat-MLP -> Mono-Forward fallback (P3.2)"
    print(f"  RECON gate (density fail, for the record): slope {sc_rc['slope']:+.4f}, sel {sel.mean():+.3f}")
    print(f"  CONTRAST GATE (the hero): slope {sc_ct['slope']:+.4f} (flat? {slope_gate}) | sel mean "
          f"{sel_ct.mean():+.3f} (class-info? {sel_gate})\n  => {verdict}", flush=True)

    OUT = os.path.join(_HERE, f"figs_p3_0_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {k: st(k) for k in runs_keys}
    saved.update(seeds=np.array(seeds), L=L, width=WIDTH, chance=chance)
    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in saved.items()})
    manifest = {"experiment": f"p3_0-{name}", "git_commit": _git(), "seeds": list(seeds), "task": name,
                "config": {k: v for k, v in CFG[name].items()}, "energy_cell": ENERGY_WALL,
                "L": L, "width": WIDTH, "batch": BATCH, "mask_ratio": 0.5,
                "results_median": {"energy": sc_en, "recon": sc_rc, "contrast": sc_ct, "env_gap": env_gap,
                                   "select_recon_mean": float(sel.mean()),
                                   "select_contrast_mean": float(sel_ct.mean()),
                                   "select_contrast_peak": float(sel_ct.max()),
                                   "gd_held": float(np.median(st("gd_held"))),
                                   "slope_gate": bool(slope_gate), "select_gate": bool(sel_gate),
                                   "verdict": verdict},
                "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p3_0 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), name, OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {manifest['git_commit'][:8]})")


if __name__ == "__main__":
    main()
