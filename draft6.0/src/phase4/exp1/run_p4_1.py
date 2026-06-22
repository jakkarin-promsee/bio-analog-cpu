"""
Experiment P4.1 — ambient-dim tolerance (A2). Hold difficulty FIXED (overlap 0.7 -> Bayes ~0.108, dim-invariant
because the signal lives in a 2-D subspace and the rest is pure nuisance) and sweep the ambient input dimension.
The sharp question: does OURS's contrast objective filter irrelevant/nuisance dimensions as well as a genuinely-
tuned backprop? (Phase-1 exp0: random ties SCFF in low-D — here we map the high-D edge.)

Because Bayes (the achievable ceiling) is FIXED across dim, gap-to-BP is a clean read here (no shrinking-window
confound, unlike P4.0). Racers (matched weight budget PER dim): OURS · BP-ceiling (tuned) · Mono-Forward.
Headline: gap-to-BP vs ambient dim. INV confirms Bayes stays flat (the apparatus claim).

CHECKPOINTED per (dim, seed). Run:  OMP_NUM_THREADS=1 python -u run_p4_1.py   [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra (match_width)
from p4lib import (make_gauss, bayes_error, race_ours, race_bp, race_mono, n_w)   # noqa: E402
from models_extra import match_width                                   # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
DIMS = [8, 16, 40, 100, 250, 500]                                     # ambient-dim dial (nuisance grows; signal 2-D)
OVERLAP = 0.7                                                          # FIXED difficulty -> Bayes ~0.108 (dim-invar)
NCL, NCLUST, NCLASS = 4, 16, 4
NTR, NTE = 4000, 1500
L, WD, WIN = 4, 64, 2
OUT = os.path.join(_HERE, "figs_p4_1")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                r = json.loads(line); done[(r["dim"], r["seed"])] = r
    return done


def run_cell(dim, seed):
    rng = np.random.default_rng(seed)
    Xtr, Ytr, params = make_gauss(NTR, rng, dim=dim, n_class=NCLASS, n_clusters=NCLUST, overlap=OVERLAP)
    Xte, Yte, _ = make_gauss(NTE, np.random.default_rng(seed + 7), dim=dim, n_class=NCLASS,
                             n_clusters=NCLUST, overlap=OVERLAP)
    bayes = bayes_error(params, np.random.default_rng(seed + 99), n=15000)
    bulk = [dim] + [WD] * L
    total = n_w(bulk) + n_w([L * WD, 32, NCLASS])
    bw, _ = match_width(total, dim, NCLASS, L)
    mono_dims = [dim] + [bw] * L + [NCLASS]
    o = race_ours(Xtr, Ytr, Xte, Yte, NCLASS, L=L, Wd=WD, w=WIN, seed=seed)
    b = race_bp(Xtr, Ytr, Xte, Yte, NCLASS, total=total, in_dim=dim, seed=seed)
    mo = race_mono(Xtr, Ytr, Xte, Yte, NCLASS, dims=mono_dims, seed=seed)
    return dict(dim=dim, seed=seed, bayes=bayes, chance=1.0 / NCLASS,
                ours_te=o["acc_te"], ours_tr=o["acc_tr"], ours_bwd=o["bwd"],
                bp_te=b["acc_te"], bp_tr=b["acc_tr"], bp_bwd=b["bwd"],
                bp_lr=b["lr"], bp_wd=b["wd"], bp_depth=b["depth"], bp_width=b["width"],
                mono_te=mo["acc_te"], mono_tr=mo["acc_tr"], mono_bwd=mo["bwd"],
                gap=float(b["acc_te"] - o["acc_te"]),
                capture=float((o["acc_te"] - 1.0 / NCLASS) / max(1e-6, (1 - bayes) - 1.0 / NCLASS)))


def main():
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    dims = DIMS[:2] if "--quick" in sys.argv else DIMS
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.1 ambient-dim axis | overlap {OVERLAP} | dims={dims} | seeds={seeds} | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for d in dims:
        for s in seeds:
            if (d, s) in done:
                continue
            r = run_cell(d, s); done[(d, s)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  dim {d:5d} seed {s}: bayes {r['bayes']:.3f} | OURS {r['ours_te']:.3f}  "
                  f"BP {r['bp_te']:.3f}  Mono {r['mono_te']:.3f}  | gap {r['gap']:+.3f}  "
                  f"capture {r['capture']:.2f}  [BP d{r['bp_depth']}w{r['bp_width']} "
                  f"lr{r['bp_lr']:g} wd{r['bp_wd']:g}]", flush=True)
    fck.close()

    rows = list(done.values())
    print(f"\n--- P4.1 median over seeds, n={len(seeds)} ---")
    print(f"{'dim':>6} {'bayes':>6} {'OURS':>6} {'BP':>6} {'Mono':>6} {'gap':>7} {'capture':>7}")
    agg = []
    for d in dims:
        rs = [r for r in rows if r["dim"] == d]
        if not rs:
            continue
        def md(k): return float(np.median([r[k] for r in rs]))
        agg.append(dict(dim=d, bayes=md("bayes"), ours=md("ours_te"), bp=md("bp_te"), mono=md("mono_te"),
                        ours_tr=md("ours_tr"), bp_tr=md("bp_tr"), mono_tr=md("mono_tr"),
                        gap=md("gap"), capture=md("capture"),
                        ours_bwd=rs[0]["ours_bwd"], bp_bwd=rs[0]["bp_bwd"], mono_bwd=rs[0]["mono_bwd"]))
        a = agg[-1]
        print(f"{d:6d} {a['bayes']:6.3f} {a['ours']:6.3f} {a['bp']:6.3f} {a['mono']:6.3f} "
              f"{a['gap']:+7.3f} {a['capture']:7.2f}")
    gaps = [a["gap"] for a in agg]
    print(f"\n  gap-to-BP {gaps[0]:+.3f} (dim {dims[0]}) -> {gaps[-1]:+.3f} (dim {dims[-1]}); "
          f"Bayes {agg[0]['bayes']:.3f}->{agg[-1]['bayes']:.3f} (flat = apparatus OK)", flush=True)

    np.savez(os.path.join(OUT, "arrays.npz"),
             **{k: np.array([a[k] for a in agg]) for k in ("dim", "bayes", "ours", "bp", "mono",
                                                           "ours_tr", "bp_tr", "mono_tr", "gap",
                                                           "capture", "ours_bwd", "bp_bwd", "mono_bwd")},
             chance=1.0 / NCLASS, seeds=np.array(seeds))
    json.dump({"experiment": "p4_1", "git_commit": _git(), "seeds": list(seeds), "dims": dims,
               "overlap": OVERLAP, "n_class": NCLASS, "n_clusters": NCLUST, "cell": dict(L=L, Wd=WD, w=WIN),
               "gap_lo_hi": [gaps[0], gaps[-1]], "numpy": np.__version__,
               "wall_clock_s": round(time.time() - t0, 1)}, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_1 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
