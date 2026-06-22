"""
Experiment P4.0 — the bench + the difficulty axis (A1). The locked first run: validate the whole apparatus
(controlled generator, EXACT Bayes error, the three racers, the gap + cost meters) and reproduce a clean
gap-to-backprop that OPENS as difficulty (Bayes error) rises.

Racers (matched weight budget): OURS (contrast+coord+readout) · BP-ceiling (tuned MLP) · Mono-Forward (sup-local).
Dial: cluster overlap -> EXACT Bayes error. Headline: gap-to-BP vs Bayes error. + the cost Pareto.

CHECKPOINTED: each (overlap, seed) result is appended to figs_*/_ckpt.jsonl the instant it finishes and SKIPPED
on restart -> an overnight laptop-sleep loses one cell, not the run (the P3.1 lesson).

Run (single-threaded -- phantom guard):  OMP_NUM_THREADS=1 python -u run_p4_0.py   [--quick]
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
# difficulty dial -> EXACT Bayes error, chosen to span the INFORMATIVE band ~0.02..0.37 (even spread; the
# trivial sub-0.01 end where everyone hits ~100% is dropped -- it wastes seeds and says nothing). See README §5.
OVERLAPS = [0.50, 0.65, 0.80, 0.95, 1.10, 1.25]
DIM, NCL, NCLUST, NCLASS = 40, 4, 16, 4
NTR, NTE = 4000, 1500
L, WD, WIN = 4, 64, 2
OUT = os.path.join(_HERE, "figs_p4_0")


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
                r = json.loads(line); done[(r["overlap"], r["seed"])] = r
    return done


def run_cell(overlap, seed):
    rng = np.random.default_rng(seed)
    Xtr, Ytr, params = make_gauss(NTR, rng, dim=DIM, n_class=NCLASS, n_clusters=NCLUST, overlap=overlap)
    Xte, Yte, _ = make_gauss(NTE, np.random.default_rng(seed + 7), dim=DIM, n_class=NCLASS,
                             n_clusters=NCLUST, overlap=overlap)
    bayes = bayes_error(params, np.random.default_rng(seed + 99))
    # matched weight budget = OURS (bulk + all-tap readout); BP searches shapes at THIS budget, Mono uses a
    # representative matched shape at OURS's depth.
    bulk = [DIM] + [WD] * L
    total = n_w(bulk) + n_w([L * WD, 32, NCLASS])
    bw, _ = match_width(total, DIM, NCLASS, L)
    mono_dims = [DIM] + [bw] * L + [NCLASS]
    o = race_ours(Xtr, Ytr, Xte, Yte, NCLASS, L=L, Wd=WD, w=WIN, seed=seed)
    b = race_bp(Xtr, Ytr, Xte, Yte, NCLASS, total=total, in_dim=DIM, seed=seed)   # genuinely-tuned ceiling
    mo = race_mono(Xtr, Ytr, Xte, Yte, NCLASS, dims=mono_dims, seed=seed)
    return dict(overlap=overlap, seed=seed, bayes=bayes, chance=1.0 / NCLASS,
                ours_te=o["acc_te"], ours_tr=o["acc_tr"], ours_bwd=o["bwd"],
                bp_te=b["acc_te"], bp_tr=b["acc_tr"], bp_bwd=b["bwd"],
                bp_lr=b["lr"], bp_wd=b["wd"], bp_depth=b["depth"], bp_width=b["width"],
                mono_te=mo["acc_te"], mono_tr=mo["acc_tr"], mono_bwd=mo["bwd"],
                gap=float(b["acc_te"] - o["acc_te"]),
                capture=float((o["acc_te"] - 1.0 / NCLASS) / max(1e-6, (1 - bayes) - 1.0 / NCLASS)))


def main():
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    overlaps = OVERLAPS[:2] if "--quick" in sys.argv else OVERLAPS
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.0 difficulty axis | overlaps={overlaps} | seeds={seeds} | {len(done)} cells cached ===",
          flush=True)
    fck = open(ckpt, "a")
    for ov in overlaps:
        for s in seeds:
            if (ov, s) in done:
                continue
            r = run_cell(ov, s); done[(ov, s)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  ov {ov:.2f} seed {s}: bayes {r['bayes']:.3f} | OURS {r['ours_te']:.3f}  "
                  f"BP {r['bp_te']:.3f}  Mono {r['mono_te']:.3f}  | gap {r['gap']:+.3f}  "
                  f"capture {r['capture']:.2f}  [BP d{r['bp_depth']}w{r['bp_width']} "
                  f"lr{r['bp_lr']:g} wd{r['bp_wd']:g}]", flush=True)
    fck.close()

    # aggregate (median over seeds per overlap)
    rows = list(done.values())
    print(f"\n--- P4.0 median over seeds, n={len(seeds)} ---")
    print(f"{'overlap':>7} {'bayes':>6} {'OURS':>6} {'BP':>6} {'Mono':>6} {'gap':>7} {'capture':>7}")
    agg = []
    for ov in overlaps:
        rs = [r for r in rows if abs(r["overlap"] - ov) < 1e-9]
        if not rs:
            continue
        def md(k): return float(np.median([r[k] for r in rs]))
        agg.append(dict(overlap=ov, bayes=md("bayes"), ours=md("ours_te"), bp=md("bp_te"),
                        mono=md("mono_te"), ours_tr=md("ours_tr"), bp_tr=md("bp_tr"), mono_tr=md("mono_tr"),
                        gap=md("gap"), capture=md("capture"),
                        ours_bwd=rs[0]["ours_bwd"], bp_bwd=rs[0]["bp_bwd"], mono_bwd=rs[0]["mono_bwd"]))
        a = agg[-1]
        print(f"{ov:7.2f} {a['bayes']:6.3f} {a['ours']:6.3f} {a['bp']:6.3f} {a['mono']:6.3f} "
              f"{a['gap']:+7.3f} {a['capture']:7.2f}")
    gaps = [a["gap"] for a in agg]
    print(f"\n  gap-to-BP opens {gaps[0]:+.3f} (easy) -> {gaps[-1]:+.3f} (hard); "
          f"cost OURS/BP/Mono backward = {agg[0]['ours_bwd']/1000:.0f}k / {agg[0]['bp_bwd']/1000:.0f}k / "
          f"{agg[0]['mono_bwd']/1000:.0f}k", flush=True)

    np.savez(os.path.join(OUT, "arrays.npz"),
             **{k: np.array([a[k] for a in agg]) for k in ("overlap", "bayes", "ours", "bp", "mono",
                                                            "ours_tr", "bp_tr", "mono_tr", "gap",
                                                            "capture", "ours_bwd", "bp_bwd", "mono_bwd")},
             chance=1.0 / NCLASS, seeds=np.array(seeds))
    json.dump({"experiment": "p4_0", "git_commit": _git(), "seeds": list(seeds), "overlaps": overlaps,
               "dim": DIM, "n_class": NCLASS, "n_clusters": NCLUST, "cell": dict(L=L, Wd=WD, w=WIN),
               "gap_easy_hard": [gaps[0], gaps[-1]], "numpy": np.__version__,
               "wall_clock_s": round(time.time() - t0, 1)}, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_0 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
