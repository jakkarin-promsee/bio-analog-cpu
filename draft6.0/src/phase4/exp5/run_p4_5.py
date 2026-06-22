"""
Experiment P4.5 — continual (A6) across difficulty: does the home-turf WIN hold off the home config? Phase-1 exp4
and P3.3 proved it on class-incremental DIGITS: online BP catastrophically forgets; OURS (contrast+coordination +
sleep-consolidated readout) does not — sleep recovers it. P4.5 asks: does that survive as the task gets HARDER?

We feed SYNTHETIC class-incremental data (make_gauss, 10 classes / 40 clusters, split into 5 tasks of 2 — the same
stream shape as digits) at a swept difficulty (overlap), straight into the VALIDATED P3.3 continual harness
(run_condition: contrast+coord+sleep vs the rot control vs online-BP). Plus the digits home config as an anchor.

Metrics (GEM/CL-survey): AA (final all-task acc), BWT (forgetting), forget. The win = OURS-sleep keeps AA up and
BWT near zero while online-BP's BWT craters, across the whole difficulty band.

Uses sklearn probes inside the harness -> phantom risk. 3 seeds (heaviest rung). CHECKPOINTED per (task,key,seed).
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_5.py [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time, warnings
import numpy as np
warnings.filterwarnings("ignore")

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase3", "exp3"))  # run_p3_3 (the continual harness)
from p4lib import make_gauss                                          # noqa: E402
from run_p3_3 import run_condition, load_digits_split, LAB            # noqa: E402

SEEDS = [42, 137, 271]
OVERLAPS = [0.4, 0.7, 1.0]                                            # difficulty dial on the synthetic stream
CONDS = ["gd", "contrast_sleep", "contrast_nosleep"]                  # forget baseline / OURS / rot control
NCLUST, DIM, NCLASS = 40, 40, 10                                      # 10 classes -> 5 tasks of 2 (matches digits)
NTR, NTE = 4000, 1500
OUT = os.path.join(_HERE, "figs_p4_5")


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
                r = json.loads(line); done[(r["key"], r["cond"], r["seed"])] = r
    return done


def synth_stream(overlap, seed):
    Xtr, Ytr, _ = make_gauss(NTR, np.random.default_rng(seed), dim=DIM, n_class=NCLASS,
                             n_clusters=NCLUST, overlap=overlap)
    Xte, Yte, _ = make_gauss(NTE, np.random.default_rng(seed + 7), dim=DIM, n_class=NCLASS,
                             n_clusters=NCLUST, overlap=overlap)
    return Xtr, Ytr, Xte, Yte


def main():
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    overlaps = OVERLAPS[:1] if quick else OVERLAPS
    do_digits = not quick
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.5 continual x difficulty | overlaps={overlaps} | conds={CONDS} | seeds={seeds} | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")

    def do(key, Xtr, Ytr, Xte, Yte, seed):
        for c in CONDS:
            if (key, c, seed) in done:
                continue
            r = run_condition(c, Xtr, Ytr, Xte, Yte, seed)
            rec = dict(key=key, cond=c, seed=seed, final=r["final"], bwt=r["bwt"], forget=r["forget"])
            done[(key, c, seed)] = rec
            fck.write(json.dumps(rec) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  {key:>7} {c:18s} seed {seed}: AA {r['final']:.3f}  BWT {r['bwt']:+.3f}  "
                  f"forget {r['forget']:.3f}", flush=True)

    for ov in overlaps:
        key = f"ov{ov:.1f}"
        for s in seeds:
            Xtr, Ytr, Xte, Yte = synth_stream(ov, s)
            do(key, Xtr, Ytr, Xte, Yte, s)
    if do_digits:
        for s in seeds:
            Xtr, Ytr, Xte, Yte = load_digits_split(s)
            do("digits", Xtr, Ytr, Xte, Yte, s)
    fck.close()

    rows = list(done.values())
    keys = [f"ov{ov:.1f}" for ov in overlaps] + (["digits"] if do_digits else [])
    print(f"\n--- P4.5 median over seeds, n={len(seeds)} ---")
    agg = {}
    for key in keys:
        agg[key] = {}
        for c in CONDS:
            rs = [r for r in rows if r["key"] == key and r["cond"] == c]
            if not rs:
                continue
            def md(k): return float(np.median([r[k] for r in rs]))
            agg[key][c] = dict(final=md("final"), bwt=md("bwt"), forget=md("forget"))
        line = "  ".join(f"{c.split('_')[0]}:AA{agg[key][c]['final']:.2f}/BWT{agg[key][c]['bwt']:+.2f}"
                         for c in CONDS if c in agg[key])
        print(f"  [{key}] {line}", flush=True)

    np.savez(os.path.join(OUT, "arrays.npz"),
             keys=np.array(keys),
             overlaps=np.array(overlaps),
             **{f"{key}_{c}_{m}": np.array(agg[key][c][m])
                for key in keys for c in CONDS if c in agg[key] for m in ("final", "bwt", "forget")},
             seeds=np.array(seeds))
    json.dump({"experiment": "p4_5", "git_commit": _git(), "seeds": list(seeds), "overlaps": overlaps,
               "conds": CONDS, "n_class": NCLASS, "n_clusters": NCLUST, "dim": DIM, "digits": do_digits,
               "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_5 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz"), allow_pickle=True), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
