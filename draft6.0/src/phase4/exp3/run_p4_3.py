"""
Experiment P4.3 — width x depth (A4): the Scap-budget Pareto. At a FIXED total weight budget (the substrate's real
constraint — Scaps are finite), how should you spend it: wide-shallow or narrow-deep? And does the answer differ by
TASK REGIME? This ties P4.2 (depth pays on a headroom task) to Phase-1/2 (wide-shallow wins on a flat task).

Design: iso-budget shape sweep. Fix total weights B (= the canonical L4/W64 cell). For each depth L in [2,3,4,6,8]
pick the OURS bulk width that hits B (so every shape spends ~the same Scaps), and match the BP ceiling to OURS's
actual total at that shape. Walk wide-shallow (L2) -> narrow-deep (L8). Two regimes:
  flat     = make_gauss (overlap 0.7, Bayes ~0.108) — no depth headroom (Phase-1/2 regime)
  headroom = make_tierb (the P4.2 headroom config)  — depth pays (P4.2 regime)
Racers: OURS vs tuned BP (Mono dropped — the budget-allocation question is OURS-vs-ceiling; Mono is the cautionary
racer, not central here). Headline: accuracy vs depth-at-fixed-budget per regime + the cost Pareto.

CHECKPOINTED per (regime, L, seed). Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_3.py [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))          # p2lib (make_tierb)
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
from p4lib import make_gauss, race_ours, race_bp, n_w                  # noqa: E402
from p2lib import make_tierb                                           # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
DEPTHS = [2, 3, 4, 6, 8]                                               # wide-shallow -> narrow-deep (iso-budget)
REGIMES = ["flat", "headroom"]
DIM, NCLASS = 40, 4
NTR, NTE = 4000, 1500
B = n_w([DIM] + [64] * 4) + n_w([4 * 64, 32, NCLASS])                  # iso-budget = the canonical L4/W64 cell
OUT = os.path.join(_HERE, "figs_p4_3")


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
                r = json.loads(line); done[(r["regime"], r["L"], r["seed"])] = r
    return done


def ours_width_for_budget(B, D, L, C):
    """Pick the OURS bulk width so bulk([D]+[W]*L) + all-tap readout([L*W,32,C]) ~= B (iso total weights)."""
    best = None
    for W in range(8, 320):
        tot = n_w([D] + [W] * L) + n_w([L * W, 32, C])
        if best is None or abs(tot - B) < abs(best[1] - B):
            best = (W, tot)
    return best


def make_regime(regime, n, seed):
    if regime == "flat":
        X, Y, _ = make_gauss(n, np.random.default_rng(seed), dim=DIM, n_class=NCLASS, n_clusters=16, overlap=0.7)
        return X, Y
    return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=DIM, overlap=0.6,
                      label="random", n_class=NCLASS)


def run_cell(regime, L, seed):
    Xtr, Ytr = make_regime(regime, NTR, seed + 1)
    Xte, Yte = make_regime(regime, NTE, seed + 2)
    W, ours_total = ours_width_for_budget(B, DIM, L, NCLASS)
    o = race_ours(Xtr, Ytr, Xte, Yte, NCLASS, L=L, Wd=W, w=2, seed=seed)
    b = race_bp(Xtr, Ytr, Xte, Yte, NCLASS, total=ours_total, in_dim=DIM, depths=(L,), seed=seed)
    return dict(regime=regime, L=L, width=int(W), ours_total=int(ours_total), seed=seed,
                ours_te=o["acc_te"], ours_tr=o["acc_tr"], ours_bwd=o["bwd"],
                bp_te=b["acc_te"], bp_tr=b["acc_tr"], bp_bwd=b["bwd"], bp_width=b["width"],
                gap=float(b["acc_te"] - o["acc_te"]))


def main():
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    depths = DEPTHS[:2] if "--quick" in sys.argv else DEPTHS
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.3 width x depth (iso-budget B={B}) | depths={depths} | regimes={REGIMES} | seeds={seeds} | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for regime in REGIMES:
        for L in depths:
            for s in seeds:
                if (regime, L, s) in done:
                    continue
                r = run_cell(regime, L, s); done[(regime, L, s)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
                print(f"  {regime:8s} L{L} W{r['width']:>3} seed {s}: OURS {r['ours_te']:.3f}  "
                      f"BP {r['bp_te']:.3f}  gap {r['gap']:+.3f}  (tot~{r['ours_total']/1000:.0f}k)", flush=True)
    fck.close()

    rows = list(done.values())
    agg = {}
    print(f"\n--- P4.3 median over seeds, n={len(seeds)} ---")
    for regime in REGIMES:
        print(f"[{regime}]  {'L':>2} {'W':>4} {'OURS':>6} {'BP':>6} {'gap':>7} {'OURSbwd':>8} {'BPbwd':>8}")
        a = []
        for L in depths:
            rs = [r for r in rows if r["regime"] == regime and r["L"] == L]
            if not rs:
                continue
            def md(k): return float(np.median([r[k] for r in rs]))
            a.append(dict(L=L, width=rs[0]["width"], ours=md("ours_te"), bp=md("bp_te"), gap=md("gap"),
                          ours_bwd=md("ours_bwd"), bp_bwd=md("bp_bwd")))
            x = a[-1]
            print(f"        {L:>2} {x['width']:>4} {x['ours']:6.3f} {x['bp']:6.3f} {x['gap']:+7.3f} "
                  f"{x['ours_bwd']/1000:7.0f}k {x['bp_bwd']/1000:7.0f}k")
        agg[regime] = a
        best_ours = max(a, key=lambda z: z["ours"]); best_bp = max(a, key=lambda z: z["bp"])
        print(f"   -> OURS best shape L{best_ours['L']}/W{best_ours['width']} ({best_ours['ours']:.3f}); "
              f"BP best L{best_bp['L']}/W{best_bp['width']} ({best_bp['bp']:.3f})", flush=True)

    np.savez(os.path.join(OUT, "arrays.npz"),
             depths=np.array(depths), widths=np.array([z["width"] for z in agg[REGIMES[0]]]),
             **{f"{rg}_{k}": np.array([z[k] for z in agg[rg]])
                for rg in REGIMES for k in ("ours", "bp", "gap", "ours_bwd", "bp_bwd")},
             B=B, seeds=np.array(seeds))
    json.dump({"experiment": "p4_3", "git_commit": _git(), "seeds": list(seeds), "depths": depths,
               "regimes": REGIMES, "budget_weights": int(B), "dim": DIM, "n_class": NCLASS,
               "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_3 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
