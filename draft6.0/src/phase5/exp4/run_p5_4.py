"""
P5.4 — the readout MVP: per-depth heads vs all-tap (design.md §3 P5.4).

Inheriting the committed cell (temp0.2/w2) and P5.3's placement story (read the extractor's end; truncation floor
0.564), this rung asks the accuracy half of the readout redesign: do per-depth deep-supervision heads MATCH all-tap
accuracy at lower (forward) cost?

  * per-depth heads — a tiny readout at EACH SCFF depth, pure `read`: LINEAR (Mono-Forward projection→CE, cheapest)
    and a capacity-matched MLP [W,32,C] head. Per-head acc must reproduce the P5.3 profiler; heads-best = the
    placement-optimal head (oracle depth — the actual selection is P5.5's calibrated exit).
  * all-tap baseline — the deployed readout on the L·W concatenation (the thing heads replace). Matched total
    readout params (L MLP-heads ≈ all-tap by construction), so a heads-vs-all-tap gap is STRUCTURE, not capacity.
  * forward-MACs — read-the-best-head (forward to that depth + 1 head) vs all-tap (forward all L + the big head).

Decision: heads-at-each-depth as the readout base IFF heads-best matches all-tap at lower cost. Guards first.
Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p5_4.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import json
import subprocess
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
from p5lib import (SCFFContrastOverlap, make_headroom, make_flat, make_mixed,    # noqa: E402
                   equivalence_guard, fd_gradient_check, fit_readout, readout_feats, linear_probe,
                   forward_cost_head, forward_cost_alltap, effective_rank, n_w)

SEEDS = [42, 137, 271, 314, 1729]
L, W, DIM, NCLASS = 12, 64, 40, 4
NTR, NTE = 4000, 1500
EP, BATCH, TEMP, WIN = 25, 32, 0.2, 2
PROBE_EP = 120
TASKS = ["headroom", "flat", "mixed"]
OUT = os.path.join(_HERE, "figs_p5_4")
P53 = os.path.join(_HERE, "..", "exp3", "figs_p5_3", "arrays.npz")


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _make(task, n, seed):
    if task == "headroom":
        X, Y = make_headroom(n, seed); return X, Y, NCLASS
    if task == "flat":
        X, Y, _ = make_flat(n, seed); return X, Y, NCLASS
    X, Y, _ = make_mixed(n, seed); return X, Y, 2 * NCLASS


def train(Xtr, seed):
    m = SCFFContrastOverlap([DIM] + [W] * L, lr=0.03, seed=seed, window=WIN, stride=WIN, mask_ratio=0.5, temp=TEMP)
    rng = np.random.default_rng(seed)
    for _ in range(EP):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), BATCH):
            xb = Xtr[idx[s:s + BATCH]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


def run_cell(task, seed):
    Xtr, Ytr, Cout = _make(task, NTR, seed + 1); Xte, Yte, _ = _make(task, NTE, seed + 2)
    m = train(Xtr, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    head_lin = [linear_probe(a, Ytr, b, Yte, Cout, seed, epochs=PROBE_EP) for a, b in zip(reps_tr, reps_te)]
    head_mlp = [float((fit_readout(a, Ytr, Cout, seed).predict(b) == Yte).mean()) for a, b in zip(reps_tr, reps_te)]
    Ftr, Fte = readout_feats(reps_tr, None), readout_feats(reps_te, None)   # all-tap = concat ALL layers
    alltap = float((fit_readout(Ftr, Ytr, Cout, seed).predict(Fte) == Yte).mean())
    best_d = int(np.argmax(head_mlp)) + 1
    return dict(task=task, seed=seed, Cout=Cout, head_lin=[float(x) for x in head_lin],
                head_mlp=[float(x) for x in head_mlp], alltap=alltap, best_d=best_d,
                head_best=float(np.max(head_mlp)), head_lin_best=float(np.max(head_lin)),
                cost_head=int(forward_cost_head(DIM, W, best_d, Cout)),
                cost_alltap=int(forward_cost_alltap(DIM, W, L, Cout)),
                params_heads=int(L * (n_w([W, 32, Cout]))), params_alltap=int(n_w([L * W, 32, Cout])))


def rkey(r):
    return (r["task"], r["seed"])


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
    PROBE_EP = 40 if quick else 120
    OUT = os.path.join(_HERE, "figs_p5_4_quick" if quick else "figs_p5_4")
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()

    print("=== P5.4 guards ===", flush=True)
    eq_ok, eq_d = equivalence_guard(dim=DIM, width=W, L=L, batch=BATCH)
    fd_ok, fd_d = fd_gradient_check(dim=DIM)
    if not (eq_ok and fd_ok):
        print("!! GUARD FAILED — STOP.", flush=True); sys.exit(1)

    tasks = ["headroom"] if quick else TASKS
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    print(f"\n=== P5.4 heads-vs-all-tap | {tasks} | seeds {seeds} | PROBE_EP={PROBE_EP} | {len(done)} cached ===",
          flush=True)
    fck = open(ckpt, "a")
    for task in tasks:
        for s in seeds:
            if (task, s) in done:
                continue
            r = run_cell(task, s); done[rkey(r)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  {task:8s} seed {s}: head-best {r['head_best']:.3f}@L{r['best_d']} (lin {r['head_lin_best']:.3f}) "
                  f"all-tap {r['alltap']:.3f}  cost head/alltap {r['cost_head']}/{r['cost_alltap']} "
                  f"({r['cost_head']/r['cost_alltap']:.2f}×)", flush=True)
    fck.close()

    def prof(task, key):
        return np.array([done[(task, s)][key] for s in seeds])

    save = dict(seeds=np.array(seeds), L=L, W=W, n_class=NCLASS, probe_ep=PROBE_EP, temp=TEMP, window=WIN,
                inv_fdguard=fd_d, inv_equiv=eq_d,
                inv_deadfrac=np.zeros((len(seeds), L)), inv_erank=np.zeros((len(seeds), L)))
    for task in tasks:
        save[f"{task}_head_mlp"] = prof(task, "head_mlp")
        save[f"{task}_head_lin"] = prof(task, "head_lin")
        save[f"{task}_alltap"] = prof(task, "alltap")
        save[f"{task}_head_best"] = prof(task, "head_best")
        save[f"{task}_head_lin_best"] = prof(task, "head_lin_best")
        save[f"{task}_best_d"] = prof(task, "best_d")
        save[f"{task}_cost_head"] = prof(task, "cost_head")
        save[f"{task}_cost_alltap"] = prof(task, "cost_alltap")
    if os.path.exists(P53):                                            # carry the P5.3 truncation floor
        p = dict(np.load(P53))
        if "trunc_L7_owntuned" in p:
            save["trunc_floor"] = float(np.median(p["trunc_L7_owntuned"]))
    save["params_heads"] = int(done[(tasks[0], seeds[0])]["params_heads"])
    save["params_alltap"] = int(done[(tasks[0], seeds[0])]["params_alltap"])
    np.savez(os.path.join(OUT, "arrays.npz"), **save)
    json.dump(dict(experiment="p5_4_heads", git_commit=_git(), seeds=list(seeds), L=L, W=W, temp=TEMP, window=WIN,
                   probe_ep=PROBE_EP, params_heads=save["params_heads"], params_alltap=save["params_alltap"],
                   guards=dict(equiv=eq_d, fd=fd_d), numpy=np.__version__, wall_clock_s=round(time.time() - t0, 1)),
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)

    print(f"\n--- P5.4 READS (n={len(seeds)}) — heads(MLP)-best vs all-tap, matched params "
          f"({save['params_heads']} vs {save['params_alltap']}) ---")
    for task in tasks:
        hb = np.median(save[f"{task}_head_best"]); at = np.median(save[f"{task}_alltap"])
        hl = np.median(save[f"{task}_head_lin_best"])
        ch = np.median(save[f"{task}_cost_head"]); ca = np.median(save[f"{task}_cost_alltap"])
        sgn = int((save[f"{task}_head_best"] >= save[f"{task}_alltap"] - 0.005).sum())
        print(f"  {task:8s}: head-best {hb:.3f} (lin {hl:.3f}) vs all-tap {at:.3f}  Δ{hb-at:+.3f} ({sgn}/{len(seeds)} "
              f"head≥alltap)  read-cost {ch/ca:.2f}× all-tap  -> "
              f"{'HEADS MATCH (cheaper)' if hb >= at - 0.01 else 'heads trail'}")
    if "trunc_floor" in save:
        print(f"  truncation floor (P5.3): {save['trunc_floor']:.3f}")

    try:
        import plot_p5
        figs = [plot_p5.fig_heads(OUT, t) for t in tasks] + [plot_p5.fig_inv(OUT)]
        print("\n  figures:", [os.path.basename(f) for f in figs if f])
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"\n  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})", flush=True)


if __name__ == "__main__":
    main()
