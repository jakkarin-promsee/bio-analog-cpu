"""
T0 controls (Phase-5 pre-decision) on the P4.3 apparatus — the two experiments the multi-agent review demanded
before any architecture work. Both at L=12, W=64, headroom task (make_tierb), per-layer linear-probe to L12.

  T0.1  DEPTH-SCALED-TRAINING GRID (the under-training confound).  Is the ~5-layer composing ceiling intrinsic,
        or just under-training at the fixed ep=25/lr=0.03?  Vary (lr x passes) + a contrast-strength control.
        Decision rule (pre-registered): the ~5 ceiling is "intrinsic to the budget" only if the per-layer probe
        PEAK DEPTH is stable across the whole grid. If the peak marches deeper as lr/passes grow -> the ceiling
        was under-training (the problem shrinks).

  T0.2  LOCALITY CONTROL (objective-bound vs locality-bound).  The cell's coordination `window` IS the
        local<->global axis: window=1 = pure forward-only-local (per-layer InfoNCE, gradient-isolated);
        window=2 = the adopted cell; window=L = ONE InfoNCE at the top of the full stack, gradient backprops
        through ALL layers = end-to-end-backprop on the SAME objective. Same cell, same InfoNCE, only the credit
        reach changes.
        Decision rule: if window=L ALSO saturates/decays ~5 -> the bound is the OBJECTIVE/task (locality
        exonerated -> Track C/global-coordination is OPTIONAL). If window=L composes monotonically past ~5 while
        window=1/2 decay -> the bound is LOCALITY (-> Track C is MANDATORY, A/B are palliative).

CHECKPOINTED + safe-launch (the OpenMP-phantom box): thread caps set BEFORE numpy import, python -u, per-cell
fsync beacons. Pure-numpy hot path (numpy linear probe + numpy effective_rank; NO sklearn).
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_t0.py [--quick]
"""
from __future__ import annotations
import os
# --- thread caps BEFORE numpy import (the phantom-hang guard) ---
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "..", "..", "draft6.0", "src")
sys.path.insert(0, os.path.join(_SRC, "phase4"))                       # p4lib
sys.path.insert(0, os.path.join(_SRC, "phase3"))                       # p3lib (SCFFContrastOLU)
sys.path.insert(0, os.path.join(_SRC, "phase2"))                       # p2lib (make_tierb, effective_rank)
from p4lib import fit_readout, readout_feats, linear_probe             # noqa: E402
from p3lib import SCFFContrastOLU                                      # noqa: E402
from p2lib import make_tierb, effective_rank                          # noqa: E402

SEEDS = [42, 137, 271]                                                 # 3 seeds for budget (extendable; ckpt-resumable)
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
PROBE_EP = 60                                                          # linear probe epochs (reduced from 120 for budget)
OUT = os.path.join(_HERE, "figs_t0")

# T0.1 grid: (lr x passes) + contrast-strength controls, all at the adopted window=2.
GRID = [
    dict(tag="base_lr03_ep25",   lr=0.03, ep=25,  window=2, temp=0.5, mask=0.5),   # == the P4.3 cell (anchor)
    dict(tag="lr03_ep75",        lr=0.03, ep=75,  window=2, temp=0.5, mask=0.5),
    dict(tag="lr03_ep150",       lr=0.03, ep=150, window=2, temp=0.5, mask=0.5),
    dict(tag="lr01_ep25",        lr=0.01, ep=25,  window=2, temp=0.5, mask=0.5),
    dict(tag="lr10_ep25",        lr=0.10, ep=25,  window=2, temp=0.5, mask=0.5),
    dict(tag="lr10_ep150",       lr=0.10, ep=150, window=2, temp=0.5, mask=0.5),   # most training
    dict(tag="temp02_ep75",      lr=0.03, ep=75,  window=2, temp=0.2, mask=0.5),   # sharper contrast
    dict(tag="mask03_ep75",      lr=0.03, ep=75,  window=2, temp=0.5, mask=0.3),   # weaker masking
]
# T0.2 locality: window sweep on the same InfoNCE cell (1=pure-local, 2=adopted, 4=wider, 12=full e2e backprop).
LOC = [
    dict(tag="w1_local",   lr=0.03, ep=25, window=1,  temp=0.5, mask=0.5),
    dict(tag="w2_adopted", lr=0.03, ep=25, window=2,  temp=0.5, mask=0.5),
    dict(tag="w4",         lr=0.03, ep=25, window=4,  temp=0.5, mask=0.5),
    dict(tag="w12_e2e",    lr=0.03, ep=25, window=12, temp=0.5, mask=0.5),         # full end-to-end backprop
    dict(tag="w12_e2e_lr01", lr=0.01, ep=25, window=12, temp=0.5, mask=0.5),       # e2e a fairer (lower) lr
]


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def make_headroom(n, seed):
    return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=DIM, overlap=0.6,
                      label="random", n_class=NCLASS)


def train_cell(Xtr, cfg, seed, batch=32):
    m = SCFFContrastOLU([DIM] + [W] * L, lr=cfg["lr"], seed=seed, window=cfg["window"],
                        mask_ratio=cfg["mask"], temp=cfg["temp"])
    rng = np.random.default_rng(seed)
    for _ in range(cfg["ep"]):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            xb = Xtr[idx[s:s + batch]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


def run_cell(part, cfg, seed):
    Xtr, Ytr = make_headroom(NTR, seed + 1)
    Xte, Yte = make_headroom(NTE, seed + 2)
    m = train_cell(Xtr, cfg, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    probe = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed, epochs=PROBE_EP)
             for rt, re in zip(reps_tr, reps_te)]
    dead = [float(x) for x in m.dead_fraction(Xte)]
    erank = [float(effective_rank(r)) for r in reps_te]
    # realistic single-head readout at the LAST layer (the P4.3 readout position)
    Ftr, Fte = readout_feats(reps_tr, 1), readout_feats(reps_te, 1)
    ro = fit_readout(Ftr, Ytr, NCLASS, seed)
    acc_last = float((ro.predict(Fte) == Yte).mean())
    nan = bool(np.any(~np.isfinite(probe)))
    return dict(part=part, tag=cfg["tag"], lr=cfg["lr"], ep=cfg["ep"], window=cfg["window"],
                temp=cfg["temp"], mask=cfg["mask"], seed=seed,
                probe=[float(p) for p in probe], dead=dead, erank=erank,
                acc_last=acc_last, nan=nan)


def rkey(r):
    return (r["part"], r["tag"], r["seed"])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                r = json.loads(line); done[rkey(r)] = r
    return done


def _med(rows, key):
    return np.median(np.array([r[key] for r in rows]), axis=0)


def _peak_depth(probe):                                                # 1-indexed layer of the probe peak
    return int(np.argmax(probe)) + 1


def main():
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    grid = GRID[:1] if quick else GRID
    loc = LOC[:2] if quick else LOC
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== T0 | grid {len(grid)} cfgs | loc {len(loc)} cfgs | seeds {seeds} | L{L} W{W} | "
          f"{len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for part, cfgs in (("grid", grid), ("loc", loc)):
        for cfg in cfgs:
            for s in seeds:
                if (part, cfg["tag"], s) in done:
                    continue
                r = run_cell(part, cfg, s); done[rkey(r)] = r
                fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
                pk = _peak_depth(r["probe"])
                print(f"  {part:4s} {cfg['tag']:16s} seed {s}: peak@L{pk:>2} ({max(r['probe']):.3f})  "
                      f"tail-L12 {r['probe'][-1]:.3f}  acc_last {r['acc_last']:.3f}"
                      f"{'  [NAN]' if r['nan'] else ''}", flush=True)
    fck.close()

    rows = list(done.values())
    save = {"seeds": np.array(seeds), "L": L, "W": W}
    # ---- T0.1 grid summary ----
    print(f"\n--- T0.1 DEPTH-SCALED GRID (median over n={len(seeds)}; peak depth + tail-L12) ---")
    print(f"  {'cfg':16s} {'peak@L':>7} {'peak':>6} {'tail-L12':>9} {'acc_last':>9}")
    gtags = []
    for cfg in grid:
        rs = [r for r in rows if r["part"] == "grid" and r["tag"] == cfg["tag"]]
        if not rs:
            continue
        pr = _med(rs, "probe"); pk = _peak_depth(pr); gtags.append(cfg["tag"])
        save[f"grid_{cfg['tag']}_probe"] = pr
        save[f"grid_{cfg['tag']}_peak"] = pk
        print(f"  {cfg['tag']:16s} {pk:>7} {float(np.max(pr)):>6.3f} {float(pr[-1]):>9.3f} "
              f"{float(np.median([r['acc_last'] for r in rs])):>9.3f}")
    peaks = [save[f"grid_{t}_peak"] for t in gtags]
    if peaks:
        print(f"  >> peak-depth range across grid: {min(peaks)}..{max(peaks)}  "
              f"(stable ~5 => ceiling intrinsic to budget; marches deeper => was under-training)")
        save["grid_peak_min"] = min(peaks); save["grid_peak_max"] = max(peaks)
    # ---- T0.2 locality summary ----
    print(f"\n--- T0.2 LOCALITY CONTROL (window sweep; same InfoNCE) ---")
    print(f"  {'cfg':16s} {'window':>6} {'peak@L':>7} {'peak':>6} {'tail-L12':>9} {'slope1-12':>9} {'acc_last':>9}")
    for cfg in loc:
        rs = [r for r in rows if r["part"] == "loc" and r["tag"] == cfg["tag"]]
        if not rs:
            continue
        pr = _med(rs, "probe"); pk = _peak_depth(pr)
        slope = float((pr[-1] - pr[0]) / (len(pr) - 1))
        save[f"loc_{cfg['tag']}_probe"] = pr; save[f"loc_{cfg['tag']}_peak"] = pk
        print(f"  {cfg['tag']:16s} {cfg['window']:>6} {pk:>7} {float(np.max(pr)):>6.3f} {float(pr[-1]):>9.3f} "
              f"{slope:>+9.4f} {float(np.median([r['acc_last'] for r in rs])):>9.3f}")
    print(f"  >> if w12(e2e) peak marches past ~5 while w1/w2 stall ~5 => LOCALITY-bound (Track C mandatory);\n"
          f"     if w12 ALSO peaks ~5 => OBJECTIVE/TASK-bound (Track C optional).")

    np.savez(os.path.join(OUT, "arrays.npz"), **{k: np.array(v) for k, v in save.items()})
    json.dump({"experiment": "t0_depthscale_locality", "git_commit": _git(), "seeds": list(seeds),
               "L": L, "W": W, "dim": DIM, "n_class": NCLASS, "probe_ep": PROBE_EP,
               "grid": [c["tag"] for c in grid], "loc": [c["tag"] for c in loc],
               "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
