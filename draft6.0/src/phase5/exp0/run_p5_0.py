"""
P5.0 — the bench + the decay reproduction + the guards (design.md §3 P5.0).

The question: does the Phase-5 apparatus reproduce the P4.3 depth-decay (per-layer probe peak ~L5 -> tail-L12
slide ~0.43) at full protocol, and pass its sign-bug guards, BEFORE any cell is trusted? No trusted bench, no
results. This rung establishes:
  * the decay reproduces on HEADROOM (the headline) and FLAT (easier -> peaks earlier), under the adopted w2 cell;
  * the w12 cell composes the WHOLE stack with NO decay  -> w12 = the objective-capability ceiling (the decay is
    objective-locality, not an intrinsic Tunnel; the P4.3 finding, re-confirmed);
  * tuned-BP (race_bp) = the old-world ACHIEVABLE reference (a second, deployable ceiling beside w12);
  * the MIXED (disjoint-label) corruption detector: do the deep layers the headroom subtask needs CORRUPT the
    early-solved flat subtask? (the cleanest decay tell);
  * the GUARDS pass: overlap == OLU bit-for-bit (equivalence), FD-gradient < 1e-5 (the InfoNCE window backward),
    dead-frac ~ 0. ANY guard fails -> STOP.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_0.py [--quick]
"""
from __future__ import annotations
import os
# --- thread caps BEFORE numpy import (the OpenMP-phantom guard) ---
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p5lib
from p5lib import (SCFFContrastOverlap, cost_overlap, ours_budget,        # noqa: E402
                   make_headroom, make_flat, make_mixed,
                   equivalence_guard, fd_gradient_check, mean_infonce_loss,
                   fit_readout, readout_feats, linear_probe, race_bp, bayes_error, effective_rank)

# ---- locked config (matches the P4.3 / T3 bench so the decay is directly comparable) ----
SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH = 25, 32
PROBE_EP = 120                                                         # full protocol (T3 used 60)
CELLS = {"w2": dict(window=2, stride=2), "w12": dict(window=12, stride=12)}
OUT = os.path.join(_HERE, "figs_p5_0")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


# ============================================================ training (with the INV loss trace)
def train_overlap(Xtr, cell, seed):
    m = SCFFContrastOverlap([DIM] + [W] * L, lr=0.03, seed=seed,
                            window=cell["window"], stride=cell["stride"], mask_ratio=0.5, temp=0.5)
    rng = np.random.default_rng(seed)
    Xheld = Xtr[:256]; lrng = np.random.default_rng(seed + 555)
    trace = []
    for _ in range(EP):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
        trace.append(mean_infonce_loss(m, Xheld, lrng))
    return m, trace


# ============================================================ cells
def run_standard(task, cellname, seed):
    if task == "headroom":
        Xtr, Ytr = make_headroom(NTR, seed + 1); Xte, Yte = make_headroom(NTE, seed + 2)
    else:                                                              # flat
        Xtr, Ytr, _ = make_flat(NTR, seed + 1); Xte, Yte, _ = make_flat(NTE, seed + 2)
    m, trace = train_overlap(Xtr, CELLS[cellname], seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    probe = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed, epochs=PROBE_EP) for rt, re in zip(reps_tr, reps_te)]
    Ftr, Fte = readout_feats(reps_tr, 1), readout_feats(reps_te, 1)
    ro = fit_readout(Ftr, Ytr, NCLASS, seed)
    return dict(task=task, cell=cellname, seed=seed, probe=[float(p) for p in probe],
                dead=[float(x) for x in m.dead_fraction(Xte)],
                erank=[float(effective_rank(r)) for r in reps_te],
                readout=float((ro.predict(Fte) == Yte).mean()), losstrace=[float(t) for t in trace],
                nan=bool(np.any(~np.isfinite(probe))))


def run_mixed(cellname, seed):
    Xtr, Ytr, mtr = make_mixed(NTR, seed + 1); Xte, Yte, mte = make_mixed(NTE, seed + 2)
    ftr, fte = mtr["flat"], mte["flat"]; htr, hte = mtr["head"], mte["head"]
    m, trace = train_overlap(Xtr, CELLS[cellname], seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    # subset-only per-layer probe, labels remapped to 0..C-1 (comparable to P4.3's per-subtask probe)
    pf = [linear_probe(rt[ftr], Ytr[ftr], re[fte], Yte[fte], NCLASS, seed, epochs=PROBE_EP)
          for rt, re in zip(reps_tr, reps_te)]
    ph = [linear_probe(rt[htr], Ytr[htr] - NCLASS, re[hte], Yte[hte] - NCLASS, NCLASS, seed, epochs=PROBE_EP)
          for rt, re in zip(reps_tr, reps_te)]
    Ftr, Fte = readout_feats(reps_tr, 1), readout_feats(reps_te, 1)
    ro = fit_readout(Ftr, Ytr, 2 * NCLASS, seed); pred = ro.predict(Fte)   # the single 2C-class readout
    return dict(task="mixed", cell=cellname, seed=seed,
                probe_flat=[float(p) for p in pf], probe_head=[float(p) for p in ph],
                dead=[float(x) for x in m.dead_fraction(Xte)],
                erank=[float(effective_rank(r)) for r in reps_te],
                readout_flat=float((pred[fte] == Yte[fte]).mean()),
                readout_head=float((pred[hte] == Yte[hte]).mean()), losstrace=[float(t) for t in trace],
                nan=bool(np.any(~np.isfinite(pf + ph))))


# ============================================================ references (old-world achievable ceilings)
def run_bp_headroom(seed):
    Xtr, Ytr = make_headroom(NTR, seed + 1); Xte, Yte = make_headroom(NTE, seed + 2)
    b = race_bp(Xtr, Ytr, Xte, Yte, NCLASS, total=ours_budget(DIM, W, L, NCLASS, 1),
                in_dim=DIM, depths=(2, 3, 4), seed=seed)
    return dict(task="bp_headroom", seed=seed, acc=float(b["acc_te"]), depth=int(b["depth"]), width=int(b["width"]))


def run_bp_mixed(seed):
    Xtr, Ytr, mtr = make_mixed(NTR, seed + 1); Xte, Yte, mte = make_mixed(NTE, seed + 2)
    b = race_bp(Xtr, Ytr, Xte, Yte, 2 * NCLASS, total=ours_budget(DIM, W, L, 2 * NCLASS, 1),
                in_dim=DIM, depths=(2, 3, 4), seed=seed, te_masks={"flat": mte["flat"], "head": mte["head"]})
    return dict(task="bp_mixed", seed=seed, acc=float(b["acc_te"]),
                acc_flat=float(b["acc_flat"]), acc_head=float(b["acc_head"]))


def run_bayes_flat(seed):
    _, _, params = make_flat(NTE, seed + 2)
    return dict(task="bayes_flat", seed=seed, bayes=float(bayes_error(params, np.random.default_rng(seed + 3))))


# ============================================================ checkpoint plumbing
def rkey(r):
    return (r["task"], r.get("cell", "-"), r["seed"])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                rr = json.loads(line); done[rkey(rr)] = rr
    return done


def main():
    global PROBE_EP, OUT
    quick = "--quick" in sys.argv
    seeds = SEEDS[:1] if quick else SEEDS
    cellnames = ["w2"] if quick else list(CELLS)
    probe_ep = 40 if quick else PROBE_EP
    PROBE_EP = probe_ep
    OUT = os.path.join(_HERE, "figs_p5_0_quick" if quick else "figs_p5_0")   # isolate quick (PROBE_EP not in ckpt key)
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    # ---- GUARDS FIRST (any fail -> STOP; a sign/direction bug must not masquerade as a finding) ----
    print("=== P5.0 guards (pre-cell) ===", flush=True)
    eq_ok, eq_d = equivalence_guard(dim=DIM, width=W, L=L, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check(dim=DIM)
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP. No cell runs until the apparatus is bit-exact and gradient-correct.",
              flush=True)
        sys.exit(1)
    # cost-meter sanity (monotone in window)
    cost_w = [1, 2, 4, 12]; cost_work = [cost_overlap(DIM, W, L, w, w, NCLASS, 1)[0] for w in cost_w]
    cost_mono = all(cost_work[i] < cost_work[i + 1] for i in range(len(cost_work) - 1))
    print(f"  [cost guard] work(w={cost_w}) = {cost_work}  {'monotone OK' if cost_mono else '!! NON-MONOTONE'}",
          flush=True)

    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P5.0 cells | tasks [headroom,flat,mixed] x {cellnames} | seeds {seeds} | "
          f"PROBE_EP={probe_ep} | {len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")

    def do(key, fn, *a):
        if key in done:
            return done[key]
        r = fn(*a); done[rkey(r)] = r
        fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
        return r

    for cn in cellnames:
        for s in seeds:
            r = do(("headroom", cn, s), run_standard, "headroom", cn, s)
            print(f"  headroom {cn:3s} seed {s}: peak@L{int(np.argmax(r['probe']))+1:>2} "
                  f"({max(r['probe']):.3f})  tailL12 {r['probe'][-1]:.3f}  acc {r['readout']:.3f}"
                  f"{'  [NAN]' if r['nan'] else ''}", flush=True)
            r = do(("flat", cn, s), run_standard, "flat", cn, s)
            print(f"  flat     {cn:3s} seed {s}: peak@L{int(np.argmax(r['probe']))+1:>2} "
                  f"({max(r['probe']):.3f})  tailL12 {r['probe'][-1]:.3f}  acc {r['readout']:.3f}", flush=True)
            r = do(("mixed", cn, s), run_mixed, cn, s)
            print(f"  mixed    {cn:3s} seed {s}: flatL12 {r['probe_flat'][-1]:.3f} "
                  f"(peak {max(r['probe_flat']):.3f}@L{int(np.argmax(r['probe_flat']))+1})  "
                  f"headL12 {r['probe_head'][-1]:.3f}", flush=True)
    for s in seeds:
        rb = do(("bp_headroom", "-", s), run_bp_headroom, s)
        do(("bp_mixed", "-", s), run_bp_mixed, s)
        do(("bayes_flat", "-", s), run_bayes_flat, s)
        print(f"  refs       seed {s}: bp_headroom {rb['acc']:.3f} (d{rb['depth']}/w{rb['width']})", flush=True)
    fck.close()

    # ============================================================ aggregate -> arrays.npz
    def gather(task, cell, key):
        return np.array([done[(task, cell, s)][key] for s in seeds], float)

    def gref(task, key):
        return np.array([done[(task, "-", s)][key] for s in seeds], float)

    save = dict(seeds=np.array(seeds), L=L, W=W, n_class=NCLASS, probe_ep=probe_ep,
                inv_fdguard=fd_d, inv_equiv=eq_d,
                inv_costsane_w=np.array(cost_w), inv_costsane_work=np.array(cost_work),
                inv_deadfrac=gather("headroom", "w2", "dead"),
                inv_erank=gather("headroom", "w2", "erank"),
                inv_losstrace=gather("headroom", "w2", "losstrace"),
                hr_probe_w2=gather("headroom", "w2", "probe"),
                hr_ro_w2=gather("headroom", "w2", "readout"), hr_bp=gref("bp_headroom", "acc"),
                fl_probe_w2=gather("flat", "w2", "probe"),
                fl_ro_w2=gather("flat", "w2", "readout"), fl_bayes=gref("bayes_flat", "bayes"),
                mx_probe_flat_w2=gather("mixed", "w2", "probe_flat"),
                mx_probe_head_w2=gather("mixed", "w2", "probe_head"),
                mx_ro_flat_w2=gather("mixed", "w2", "readout_flat"),
                mx_ro_head_w2=gather("mixed", "w2", "readout_head"),
                mx_bp_flat=gref("bp_mixed", "acc_flat"), mx_bp_head=gref("bp_mixed", "acc_head"))
    if "w12" in cellnames:
        save.update(hr_probe_w12=gather("headroom", "w12", "probe"), hr_ro_w12=gather("headroom", "w12", "readout"),
                    fl_probe_w12=gather("flat", "w12", "probe"), fl_ro_w12=gather("flat", "w12", "readout"),
                    mx_probe_flat_w12=gather("mixed", "w12", "probe_flat"),
                    mx_probe_head_w12=gather("mixed", "w12", "probe_head"))
    np.savez(os.path.join(OUT, "arrays.npz"), **save)
    json.dump(dict(experiment="p5_0_bench", git_commit=_git(), seeds=list(seeds), L=L, W=W, dim=DIM,
                   n_class=NCLASS, probe_ep=probe_ep, cells=cellnames, ntr=NTR, nte=NTE, ep=EP,
                   guards=dict(equiv=eq_d, fd=fd_d, cost_monotone=cost_mono),
                   numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

    # ============================================================ the Reads (design.md P5.0)
    hr = np.median(save["hr_probe_w2"], 0)
    peak = int(np.argmax(hr)) + 1; tail = float(hr[-1])
    print(f"\n--- P5.0 READS (n={len(seeds)}) ---")
    print(f"  HEADROOM w2: peak@L{peak} ({hr[peak-1]:.3f})  tail-L12 {tail:.3f}")
    peak_ok = abs(peak - 5) <= 1; tail_ok = 0.38 <= tail <= 0.49
    print(f"     decay reproduced? peak within +/-1 of L5: {'YES' if peak_ok else 'NO'} | "
          f"tail in ~0.43 band [0.38,0.49]: {'YES' if tail_ok else 'NO'}  "
          f"-> {'BENCH TRUSTED' if (peak_ok and tail_ok) else 'INVESTIGATE (port bug vs probe-protocol effect)'}")
    if "w12" in cellnames:
        w12 = np.median(save["hr_probe_w12"], 0)
        print(f"  HEADROOM w12 (objective-capability ceiling): peak@L{int(np.argmax(w12))+1} "
              f"tail-L12 {w12[-1]:.3f}  (NO-decay expected -> the decay is objective-locality, not a Tunnel)")
    mf = np.median(save["mx_probe_flat_w2"], 0)
    print(f"  MIXED flat subtask w2: peak {mf.max():.3f}@L{int(np.argmax(mf))+1} -> tail-L12 {mf[-1]:.3f} "
          f"(corruption = peak well above tail; BP-flat {np.median(save['mx_bp_flat']):.3f} holds it)")

    try:
        import plot_p5
        print("\n  figures:", [os.path.basename(p) for p in plot_p5.regen(OUT)])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
