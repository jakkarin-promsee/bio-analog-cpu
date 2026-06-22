"""
Experiment P4.2 — depth headroom (A3) × difficulty. Does Phase-3's depth-composition (P3.2: contrast + coordination
w>=2 makes the per-layer probe RISE with depth on a headroom task) GENERALIZE across difficulty, or was it one
config? P3.2 warned headroom is fragile ("no config gives both GD-rises AND energy-declines"), so this is the rung
most likely to come back PARTIAL — which is itself a result.

INSTRUMENT SWITCH (vs P4.0/P4.1): depth-composition is a REPRESENTATION property, invisible to task accuracy (the
all-tap readout masks it). So we use the Phase-3-validated PER-LAYER PROBE SLOPE. Three curves across the difficulty
dial (overlap on the make_tierb headroom family, 64 clusters):
  OURS w=2 (adopted, coordination)  ·  OURS w=1 (no-coordination control, the P3.2 contrast)  ·  GD-hidden (ceiling;
  its slope tells us WHERE depth headroom even exists). The sharp question: does w2's rising slope hold across the
  difficulty band where the ceiling has headroom?

Reuses the Phase-3 bench (make_tierb, probe_per_layer, gd_hidden_probe, train_mlp) -> no new generator, no new bugs.
NOTE: probe_per_layer uses sklearn LogisticRegression -> the phantom-hang risk. OMP_NUM_THREADS=1, python -u,
per-cell fsync checkpoint. CHECKPOINTED per (overlap, seed). Run: OMP_NUM_THREADS=1 python -u run_p4_2.py [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase1", "exp0"))  # models_extra
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))          # p2lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase3"))          # p3lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase3", "exp0"))  # run_p3_0 helpers
from p2lib import make_tierb, probe_per_layer                          # noqa: E402
from p3lib import SCFFContrastOLU                                      # noqa: E402
from models_extra import match_width                                   # noqa: E402
from run_p3_0 import train_mlp, gd_hidden_probe, n_w, BATCH            # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
OVERLAPS = [0.4, 0.6, 0.8, 1.0, 1.2]                                   # difficulty dial on the headroom task
TASK = dict(grid=4, n_active=3, dim=40, label="random", n_class=4)     # 64 clusters — the P3.2 headroom family
L, WIDTH = 8, 64                                                       # depth headroom (8 layers) for composition to show
WIN = 2                                                                # the adopted coordination window
EP_OURS, EP_GD = 30, 60
OUT = os.path.join(_HERE, "figs_p4_2")


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


def train_olu(dims, Xtr, seed, epochs, window):
    m = SCFFContrastOLU(dims, seed=seed, window=window, mask_ratio=0.5, temp=0.5)
    rng = np.random.default_rng(seed)
    for _ in range(epochs):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


def slope(p):
    return float(np.polyfit(np.arange(1, len(p) + 1), p, 1)[0])


def run_cell(overlap, seed):
    t = dict(TASK, overlap=overlap)
    Xtr, Ytr = make_tierb(NTR_NTE[0], np.random.default_rng(seed + 1), **t)
    Xte, Yte = make_tierb(NTR_NTE[1], np.random.default_rng(seed + 2), **t)
    D = Xtr.shape[1]; C = int(t["n_class"]); dims = [D] + [WIDTH] * L
    m2 = train_olu(dims, Xtr, seed, EP_OURS, WIN); o2 = probe_per_layer(m2, Xtr, Ytr, Xte, Yte)
    m1 = train_olu(dims, Xtr, seed, EP_OURS, 1);   o1 = probe_per_layer(m1, Xtr, Ytr, Xte, Yte)
    budget = n_w(dims) + (L * WIDTH * C + C)                           # GD ceiling at the matched-ish budget
    w, _ = match_width(budget, D, C, L)
    gd, _ = train_mlp([D] + [w] * L + [C], Xtr, Ytr, Xte, Yte, seed, EP_GD); gp = gd_hidden_probe(gd, Xtr, Ytr, Xte, Yte)
    return dict(overlap=overlap, seed=seed, chance=1.0 / C,
                ours2_probe=o2, ours1_probe=o1, gd_probe=gp,
                ours2_slope=slope(o2), ours1_slope=slope(o1), gd_slope=slope(gp),
                ours2_top=float(o2[-1]), ours1_top=float(o1[-1]), gd_top=float(gp[-1]),
                headroom=bool(slope(gp) > 0.004))                      # ceiling has depth headroom here?


NTR_NTE = (5000, 1500)


def main():
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    overlaps = OVERLAPS[:2] if "--quick" in sys.argv else OVERLAPS
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.2 depth-headroom x difficulty | L={L} w={WIN} | overlaps={overlaps} | seeds={seeds} | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for ov in overlaps:
        for s in seeds:
            if (ov, s) in done:
                continue
            r = run_cell(ov, s); done[(ov, s)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  ov {ov:.2f} seed {s}: slope OURSw2 {r['ours2_slope']:+.4f}  OURSw1 {r['ours1_slope']:+.4f}  "
                  f"GD {r['gd_slope']:+.4f} | top w2 {r['ours2_top']:.3f} GD {r['gd_top']:.3f} | "
                  f"{'HEADROOM' if r['headroom'] else 'flat'}", flush=True)
    fck.close()

    rows = list(done.values())
    print(f"\n--- P4.2 median over seeds, n={len(seeds)} ---")
    print(f"{'overlap':>7} {'GDslp':>7} {'w2slp':>7} {'w1slp':>7} {'w2top':>6} {'GDtop':>6}  headroom?")
    agg = []
    for ov in overlaps:
        rs = [r for r in rows if abs(r["overlap"] - ov) < 1e-9]
        if not rs:
            continue
        def md(k): return float(np.median([r[k] for r in rs]))
        def prof(k): return np.median(np.array([r[k] for r in rs]), axis=0)   # [L] median per-layer
        agg.append(dict(overlap=ov, gd_slope=md("gd_slope"), ours2_slope=md("ours2_slope"),
                        ours1_slope=md("ours1_slope"), ours2_top=md("ours2_top"), gd_top=md("gd_top"),
                        ours2_prof=prof("ours2_probe"), ours1_prof=prof("ours1_probe"), gd_prof=prof("gd_probe"),
                        headroom=bool(md("gd_slope") > 0.004)))
        a = agg[-1]
        print(f"{ov:7.2f} {a['gd_slope']:+7.4f} {a['ours2_slope']:+7.4f} {a['ours1_slope']:+7.4f} "
              f"{a['ours2_top']:6.3f} {a['gd_top']:6.3f}  {'YES' if a['headroom'] else 'flat'}")

    np.savez(os.path.join(OUT, "arrays.npz"),
             overlap=np.array([a["overlap"] for a in agg]),
             gd_slope=np.array([a["gd_slope"] for a in agg]),
             ours2_slope=np.array([a["ours2_slope"] for a in agg]),
             ours1_slope=np.array([a["ours1_slope"] for a in agg]),
             ours2_top=np.array([a["ours2_top"] for a in agg]), gd_top=np.array([a["gd_top"] for a in agg]),
             ours2_prof=np.array([a["ours2_prof"] for a in agg]), ours1_prof=np.array([a["ours1_prof"] for a in agg]),
             gd_prof=np.array([a["gd_prof"] for a in agg]),
             chance=1.0 / int(TASK["n_class"]), L=L, seeds=np.array(seeds))
    json.dump({"experiment": "p4_2", "git_commit": _git(), "seeds": list(seeds), "overlaps": overlaps,
               "task": TASK, "L": L, "window": WIN, "numpy": np.__version__,
               "wall_clock_s": round(time.time() - t0, 1)}, open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_2 as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
