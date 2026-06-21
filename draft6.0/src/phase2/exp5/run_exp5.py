"""
Experiment P2.5 — multi-block: does GD *between* shallow SCFF earn the depth deep SCFF can't?

P2.1 (transmission) + P2.2 (objective) proved depth is not the lever INSIDE SCFF — composing class features
across depth needs cross-layer coordination forward-only locality can't give. P2.5 tests the architecture's
actual depth mechanism: insert a GD checkpoint BETWEEN shallow SCFF groups -> [SCFF×k -> GD-realign]×N -> does
the total stack climb from the pure-SCFF floor (~0.20, the P2.1 wall) toward the GD ceiling (~0.35)?

Fixed total SCFF depth = 8. Vary the GD-checkpoint cadence k (N = 8/k blocks) x mode:
  pure  (N=1, k=8) — one block = deep SCFF + 1 readout (the P2.1 baseline)
  read  — GD is a readout only; next block sees raw SCFF features; final = ensemble of block logits (boosting)
  write — GD-realign's class-aligned HIDDEN feeds the next block (the "class-alignment reset"); final = last logits
Greedy block-wise training (SCFF local/unsupervised, then GD-realign supervised) = the boosting order.
Per-block SCFF = P2.1's healthy cell (layer-norm + linear + contrast: no death, rank preserved).

Pass gate: some cadence beats pure-SCFF (disjoint IQR) -> the GD-between cadence. (Phase-1 prior: chain
saturates ~2 blocks; the live Q is whether WRITE pushes past that, and how cheaply — the accuracy/backward Pareto.)

5 seeds, median + IQR. Single-threaded (OpenMP phantom guard). Saves arrays.npz + manifest.json.
Run:  OMP_NUM_THREADS=1 python -u run_exp5.py cifar     (headline)
      OMP_NUM_THREADS=1 python -u run_exp5.py synth      (sanity)   add --quick for 2 seeds.
"""
from __future__ import annotations
import json, os, subprocess, sys, time, warnings
import numpy as np
warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
sys.path.insert(0, os.path.join(_HERE, "..", "exp1"))                  # load_cifar_local, n_w
from p2lib import SCFF2, probe_one, make_tierb                          # noqa: E402
from models_extra import MLP, match_width                              # noqa: E402
from run_exp1 import load_cifar_local, n_w                             # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
WIDTH, BATCH, TOTAL_DEPTH = 64, 32, 8
CELL = dict(norm="layernorm", goodness="linear", objective="contrast")   # P2.1 healthy shallow cell
# configs: (mode, N).  N=1 = pure-SCFF baseline (read==write).  N in {2,4,8} x {read, write}.
CONFIGS = [("pure", 1)] + [(m, N) for N in (2, 4, 8) for m in ("read", "write")]
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


def train_scff_block(stream, k, seed, epochs):
    """k-layer SCFF block (healthy cell), trained locally on the incoming stream (random negatives)."""
    m = SCFF2([stream.shape[1]] + [WIDTH] * k, seed=seed, **CELL)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(stream))
        for s in range(0, len(stream), BATCH):
            m.train_step(stream[idx[s:s + BATCH]], rng)
    return m


def train_realign(Ftr, Ytr, C, seed, epochs):
    """The GD-realign: MLP [alltap -> WIDTH -> C], supervised cross-entropy. Hidden (WIDTH) = the
    class-aligned representation the write mode feeds forward."""
    m = MLP([Ftr.shape[1], WIDTH, C], seed, lr=1e-3)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Ftr))
        for s in range(0, len(Ftr), BATCH):
            m.train_step(Ftr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    return m


def hidden(mlp, X):
    mlp.forward(X)
    return mlp.cache[1].copy()                # first hidden (WIDTH-D), class-aligned


def run_config(mode, N, Xtr, Ytr, Xte, Yte, C, seed, scff_ep, gd_ep):
    k = TOTAL_DEPTH // N
    s_tr, s_te = Xtr, Xte
    logits_tr, logits_te, perblk_probe = [], [], []
    gd_w = 0
    for blk in range(N):
        scff = train_scff_block(s_tr, k, seed + blk, scff_ep)
        atr = np.concatenate(scff.infer(s_tr), 1); ate = np.concatenate(scff.infer(s_te), 1)
        last_tr, last_te = scff.infer(s_tr)[-1], scff.infer(s_te)[-1]
        re = train_realign(atr, Ytr, C, seed + blk, gd_ep)
        gd_w += re.n_weights()
        logits_tr.append(re.forward(atr)); logits_te.append(re.forward(ate))
        perblk_probe.append(probe_one(atr, Ytr, ate, Yte))
        if mode == "write":
            s_tr, s_te = hidden(re, atr), hidden(re, ate)   # class-aligned rep feeds the next block
        else:                                               # read / pure: SCFF stream continues
            s_tr, s_te = last_tr, last_te
    if mode == "read":
        Lte = np.sum(logits_te, 0)                          # boosting ensemble of block readouts
    else:                                                   # write / pure: the last (most-realigned) readout
        Lte = logits_te[-1]
    return dict(final_acc=float((Lte.argmax(1) == Yte).mean()), perblk_probe=perblk_probe, gd_w=gd_w)


def run_seed(name, seed):
    c = CFG[name]
    Xtr, Ytr, Xte, Yte, C, D = load_task(name, seed)
    out = {"C": C, "D": D}
    for mode, N in CONFIGS:
        r = run_config(mode, N, Xtr, Ytr, Xte, Yte, C, seed, c["scff_ep"], c["gd_ep"])
        key = f"{mode}_N{N}"
        out[f"acc_{key}"] = r["final_acc"]
        out[f"probe_{key}"] = r["perblk_probe"]
        out[f"gdw_{key}"] = r["gd_w"]
        print(f"    [seed {seed}] {key:10s} acc {r['final_acc']:.3f}  gd_w {r['gd_w']}", flush=True)
    # pure-GD ceiling at matched total weights (SCFF depth-8 stack + a readout) — the same envelope as P2.1
    budget = n_w([D] + [WIDTH] * TOTAL_DEPTH) + (TOTAL_DEPTH * WIDTH * C + C)
    w, _ = match_width(budget, D, C, TOTAL_DEPTH)
    gd = MLP([D] + [w] * TOTAL_DEPTH + [C], seed, lr=1e-3); rng = np.random.default_rng(seed)
    for _ in range(c["gd_ep"]):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            gd.train_step(Xtr[idx[s:s + BATCH]], Ytr[idx[s:s + BATCH]])
    out["gd_held"] = float(gd.accuracy(Xte, Yte)); out["gd_w_full"] = gd.n_weights()
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "cifar"
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    t0 = time.time()
    print(f"=== P2.5 [{name}] GD-between blocks (total SCFF depth {TOTAL_DEPTH}) | seeds={seeds} ===", flush=True)
    runs = []
    for s in seeds:
        runs.append(run_seed(name, s))
        print(f"  seed {s} done", flush=True)

    def st(k): return np.array([r[k] for r in runs])
    chance = 1.0 / max(int(np.median(st("C"))), 2)
    pure = np.median(st("acc_pure_N1"))
    gd = np.median(st("gd_held"))
    print(f"\n--- P2.5 [{name}] median, n={len(seeds)} ---  (chance {chance:.2f})")
    print(f"  pure-SCFF (N=1, k=8): {pure:.3f}   |   pure-GD ceiling: {gd:.3f}   (gap {gd-pure:+.3f})")
    print(f"  {'config':12s} {'final acc[IQR]':>20s} {'vs pure':>9s} {'gd_w(backward)':>15s}")
    best = ("pure_N1", pure)
    for mode, N in CONFIGS:
        key = f"{mode}_N{N}"; a = st(f"acc_{key}")
        med = np.median(a); dj = float(np.percentile(a, 25) - np.percentile(st("acc_pure_N1"), 75))
        gw = int(np.median(st(f"gdw_{key}")))
        if med > best[1]:
            best = (key, med)
        flag = "  <-- beats pure (disjoint)" if dj > 0 and key != "pure_N1" else ""
        print(f"  {key:12s} {med:.3f}[{np.percentile(a,25):.3f},{np.percentile(a,75):.3f}] "
              f"{med-pure:+.3f}  {gw:13d}{flag}")
    gd_w_full = int(np.median(st("gd_w_full")))
    print(f"  pure-GD backward weights: {gd_w_full}  (full backprop through the whole net)")
    # verdict
    winners = [f"{m}_N{N}" for m, N in CONFIGS if m != "pure"
               and float(np.percentile(st(f"acc_{m}_N{N}"), 25) - np.percentile(st("acc_pure_N1"), 75)) > 0]
    print(f"\n  PASS GATE: configs beating pure-SCFF (disjoint IQR): {winners or 'NONE'}")
    print(f"  -> best = {best[0]} ({best[1]:.3f}); "
          f"{'GD-between EARNS depth' if best[0] != 'pure_N1' else 'no GD-between gain over pure'}")

    OUT = os.path.join(_HERE, f"figs_exp5_{name}"); os.makedirs(OUT, exist_ok=True)
    saved = {}
    for k in runs[0].keys():
        try:
            saved[k] = st(k)
        except Exception:
            pass
    saved["seeds"] = np.array(seeds); saved["total_depth"] = TOTAL_DEPTH
    saved["configs"] = np.array([f"{m}_N{N}" for m, N in CONFIGS])
    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v, dtype=object) if k == "configs"
                                                 else np.array(v) for k, v in saved.items()})
    manifest = {"experiment": f"exp5-{name}", "git_commit": _git(), "seeds": list(seeds), "task": name,
                "config": CFG[name], "cell": CELL, "total_depth": TOTAL_DEPTH,
                "configs": [f"{m}_N{N}" for m, N in CONFIGS],
                "results_median": {"pure_scff": float(pure), "gd_ceiling": float(gd),
                                   "best": best[0], "best_acc": float(best[1]),
                                   "acc": {f"{m}_N{N}": float(np.median(st(f"acc_{m}_N{N}"))) for m, N in CONFIGS},
                                   "winners_vs_pure": winners},
                "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)}
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_exp5
        plot_exp5.draw_all(np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True), name, OUT)
    except Exception as e:
        import traceback; traceback.print_exc(); print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {manifest['git_commit'][:8]})")


if __name__ == "__main__":
    main()
