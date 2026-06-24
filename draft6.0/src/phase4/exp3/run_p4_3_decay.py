"""
P4.3 DECAY INVESTIGATION (follow-up to A4) — WHY does OURS decay with depth, and can width fix it?

(A) WIDTH sweep: two arms at depth [4,8,12], OURS only.
      fix64 = W64 constant (the control's schedule)
      widen = W grows with depth (W_l = WBASE + l*WSTEP -> deep layers much wider)
    Hypothesis under test (the author's): the decay is class-collapse from too-few EFFECTIVE neurons — shrinking
    width destroys class structure, and even fixed width loses to DEAD neurons accruing at depth. If so, widening
    the deep layers should kill the dead-fraction rise and flatten the probe decay. Per-layer diagnostics that
    test this directly: linear PROBE (separability), DEAD-fraction (dead units), effective RANK (collapse).

(B) MIXED task: half flat (make_gauss) + half headroom (make_tierb) in ONE 4-class problem (shared dim/labels,
    different cluster structures). Questions: flat-bad/headroom-good, or both-medium? And does the FLAT subset
    (solvable at the front layers) DECAY as it rides through the deeper layers the headroom subset needs?
    Per-subset accuracy (flat / headroom / overall) + per-subset per-layer probe (where each subtask is solved).

CHECKPOINTED. Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_3_decay.py [--quick]
"""
from __future__ import annotations
import json, os, subprocess, sys, time
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))                          # p4lib
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase3"))          # p3lib (SCFFContrastOLU)
sys.path.insert(0, os.path.join(_HERE, "..", "..", "phase2"))          # p2lib (make_tierb, effective_rank)
from p4lib import make_gauss, fit_readout, readout_feats, linear_probe, race_bp, n_w  # noqa: E402
from p3lib import SCFFContrastOLU                                       # noqa: E402
from p2lib import make_tierb, effective_rank                           # noqa: E402

SEEDS = [42, 137, 271, 314, 1729]
WID_DEPTHS = [2, 3, 4, 6, 8, 10, 12]                                   # match WIDTHxDEPTH's scale
WBASE, WSTEP = 64, 16                                                  # widen: W_l = 64,80,96,... (deep = wide)
ARMS = ["fix64", "widen"]
REGIMES = ["flat", "headroom"]
MIX_DEPTHS = [2, 3, 4, 6, 8, 10, 12]                                   # match WIDTHxDEPTH's scale
DIM, NCLASS = 40, 4
NTR, NTE = 4000, 1500
READOUT_LAST_N = 1
B = n_w([DIM] + [64] * 4) + n_w([4 * 64, 32, NCLASS])                  # iso-budget = the canonical L4/W64 cell
OUT = os.path.join(_HERE, "figs_p4_3_decay")


def ours_width_for_budget(D, L, C):
    """Iso-budget bulk width (same schedule as WIDTHxDEPTH): bulk([D]+[W]*L) + all-tap readout([L*W,32,C]) ~= B."""
    best = None
    for W in range(8, 320):
        tot = n_w([D] + [W] * L) + n_w([L * W, 32, C])
        if best is None or abs(tot - B) < abs(best[1] - B):
            best = (W, tot)
    return best


def _git():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=_HERE,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def widths_for(arm, L):
    return [WBASE] * L if arm == "fix64" else [WBASE + l * WSTEP for l in range(L)]


def make_regime(regime, n, seed):
    if regime == "flat":
        X, Y, _ = make_gauss(n, np.random.default_rng(seed), dim=DIM, n_class=NCLASS, n_clusters=16, overlap=0.7)
        return X, Y
    return make_tierb(n, np.random.default_rng(seed), grid=4, n_active=3, dim=DIM, overlap=0.6,
                      label="random", n_class=NCLASS)


def make_mixed(n, seed):
    """Half flat (make_gauss) + half headroom (make_tierb), shared 40-D / 4-class space, different cluster
    structures. Returns X, Y, is_flat (bool mask)."""
    nf = n // 2; nh = n - nf
    Xf, Yf, _ = make_gauss(nf, np.random.default_rng(seed), dim=DIM, n_class=NCLASS, n_clusters=16, overlap=0.7)
    Xh, Yh = make_tierb(nh, np.random.default_rng(seed + 9999), grid=4, n_active=3, dim=DIM, overlap=0.6,
                        label="random", n_class=NCLASS)
    X = np.concatenate([Xf, Xh]); Y = np.concatenate([Yf, Yh])
    isflat = np.concatenate([np.ones(nf, bool), np.zeros(nh, bool)])
    p = np.random.default_rng(seed + 1).permutation(len(X))
    return X[p], Y[p], isflat[p]


def train_ours(Xtr, dims, seed, ep=25, batch=32):
    m = SCFFContrastOLU(dims, seed=seed, window=2, mask_ratio=0.5, temp=0.5)
    rng = np.random.default_rng(seed)
    for _ in range(ep):
        idx = rng.permutation(len(Xtr))
        for s in range(0, len(Xtr), batch):
            xb = Xtr[idx[s:s + batch]]
            if len(xb) >= 4:
                m.train_step(xb, rng)
    return m


def run_width_cell(arm, regime, L, seed):
    Xtr, Ytr = make_regime(regime, NTR, seed + 1)
    Xte, Yte = make_regime(regime, NTE, seed + 2)
    dims = [DIM] + widths_for(arm, L)
    m = train_ours(Xtr, dims, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    Ftr, Fte = readout_feats(reps_tr, READOUT_LAST_N), readout_feats(reps_te, READOUT_LAST_N)
    ro = fit_readout(Ftr, Ytr, NCLASS, seed)
    probe = [linear_probe(rt, Ytr, re, Yte, NCLASS, seed) for rt, re in zip(reps_tr, reps_te)]
    dead = [float(x) for x in m.dead_fraction(Xte)]
    erank = [float(effective_rank(r)) for r in reps_te]
    return dict(part="width", arm=arm, regime=regime, L=L, seed=seed, widths=widths_for(arm, L),
                acc_te=float((ro.predict(Fte) == Yte).mean()), probe=probe, dead=dead, erank=erank)


def run_mixed_cell(L, seed):
    Xtr, Ytr, ftr = make_mixed(NTR, seed + 1)
    Xte, Yte, fte = make_mixed(NTE, seed + 2)
    W, ours_total = ours_width_for_budget(DIM, L, NCLASS)              # iso-budget width (matches WIDTHxDEPTH)
    m = train_ours(Xtr, [DIM] + [W] * L, seed)
    reps_tr, reps_te = m.infer(Xtr), m.infer(Xte)
    Ftr, Fte = readout_feats(reps_tr, READOUT_LAST_N), readout_feats(reps_te, READOUT_LAST_N)
    ro = fit_readout(Ftr, Ytr, NCLASS, seed); pred = ro.predict(Fte)
    b = race_bp(Xtr, Ytr, Xte, Yte, NCLASS, total=ours_total, in_dim=DIM, depths=(L,), seed=seed,
                te_masks={"flat": fte, "head": ~fte})                 # tuned-BP reference, per subset
    # per-subset per-layer probe: a SEPARATE probe per subset = each subset's intrinsic separability at layer l
    pf = [linear_probe(rt[ftr], Ytr[ftr], re[fte], Yte[fte], NCLASS, seed) for rt, re in zip(reps_tr, reps_te)]
    ph = [linear_probe(rt[~ftr], Ytr[~ftr], re[~fte], Yte[~fte], NCLASS, seed) for rt, re in zip(reps_tr, reps_te)]
    return dict(part="mixed", L=L, seed=seed, width=int(W),
                acc_all=float((pred == Yte).mean()),
                acc_flat=float((pred[fte] == Yte[fte]).mean()),
                acc_head=float((pred[~fte] == Yte[~fte]).mean()),
                bp_all=b["acc_te"], bp_flat=b["acc_flat"], bp_head=b["acc_head"],
                probe_flat=pf, probe_head=ph)


def rkey(r):
    return (r["part"], r["arm"], r["regime"], r["L"], r["seed"]) if r["part"] == "width" \
        else (r["part"], r["L"], r["seed"])


def load_ckpt(path):
    done = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                r = json.loads(line); done[rkey(r)] = r
    return done


def _med_profile(rows, key):
    return np.median(np.array([r[key] for r in rows]), axis=0)


def main():
    seeds = SEEDS[:2] if "--quick" in sys.argv else SEEDS
    wid_depths = WID_DEPTHS[:1] if "--quick" in sys.argv else WID_DEPTHS
    mix_depths = MIX_DEPTHS[:1] if "--quick" in sys.argv else MIX_DEPTHS
    os.makedirs(OUT, exist_ok=True)
    ckpt = os.path.join(OUT, "_ckpt.jsonl"); done = load_ckpt(ckpt)
    t0 = time.time()
    print(f"=== P4.3 DECAY | width-arms {ARMS} L{wid_depths} | mixed L{mix_depths} | regimes {REGIMES} | "
          f"seeds {seeds} | {len(done)} cached ===", flush=True)
    fck = open(ckpt, "a")
    for arm in ARMS:                                                   # (A) width sweep
        for regime in REGIMES:
            for L in wid_depths:
                for s in seeds:
                    if ("width", arm, regime, L, s) in done:
                        continue
                    r = run_width_cell(arm, regime, L, s); done[rkey(r)] = r
                    fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
                    print(f"  width {arm:5s} {regime:8s} L{L:>2} seed {s}: acc {r['acc_te']:.3f}  "
                          f"pL {r['probe'][-1]:.3f}  dead_last {r['dead'][-1]:.2f}", flush=True)
    for L in mix_depths:                                              # (B) mixed task
        for s in seeds:
            if ("mixed", L, s) in done:
                continue
            r = run_mixed_cell(L, s); done[rkey(r)] = r
            fck.write(json.dumps(r) + "\n"); fck.flush(); os.fsync(fck.fileno())
            print(f"  mixed L{L:>2} seed {s}: all {r['acc_all']:.3f}  flat {r['acc_flat']:.3f}  "
                  f"head {r['acc_head']:.3f}", flush=True)
    fck.close()

    rows = list(done.values())
    wrows = [r for r in rows if r["part"] == "width"]
    mrows = [r for r in rows if r["part"] == "mixed"]
    wid_present = sorted({r["L"] for r in wrows}) or wid_depths
    mix_present = sorted({r["L"] for r in mrows}) or mix_depths
    wid_deep = max(wid_present); mix_deep = max(mix_present)
    save = {"wid_depths": np.array(wid_present), "mix_depths": np.array(mix_present),
            "wid_deep": wid_deep, "mix_deep": mix_deep, "wbase": WBASE, "wstep": WSTEP, "seeds": np.array(seeds)}

    # (A) width: acc vs depth per (arm,regime) + per-layer probe/dead/erank profiles at the deepest depth
    print(f"\n--- P4.3 WIDTH sweep, n={len(seeds)} (fix64 vs widen; pL/deadL/erankL = last layer) ---")
    for arm in ARMS:
        for rg in REGIMES:
            save[f"wid_{arm}_{rg}_acc"] = np.array(
                [float(np.median([r["acc_te"] for r in wrows
                                  if r["arm"] == arm and r["regime"] == rg and r["L"] == L])) for L in wid_present])
            deep = [r for r in wrows if r["arm"] == arm and r["regime"] == rg and r["L"] == wid_deep]
            if deep:
                for k in ("probe", "dead", "erank"):
                    save[f"wid_{arm}_{rg}_{k}"] = _med_profile(deep, k)
                print(f"  {arm:5s} {rg:8s}: acc@L{wid_deep} {np.median([r['acc_te'] for r in deep]):.3f}  "
                      f"pL {save[f'wid_{arm}_{rg}_probe'][-1]:.3f}  deadL "
                      f"{save[f'wid_{arm}_{rg}_dead'][-1]:.2f}  erankL {save[f'wid_{arm}_{rg}_erank'][-1]:.1f}")

    # (B) mixed: acc (all/flat/head) for OURS + tuned BP, vs depth (iso-budget) + per-subset per-layer probe
    print(f"\n--- P4.3 MIXED task, n={len(seeds)} (flat+headroom in one 4-class problem; +tuned BP) ---")
    save["mix_widths"] = np.array([next(r["width"] for r in mrows if r["L"] == L) for L in mix_present])
    for k in ("acc_all", "acc_flat", "acc_head", "bp_all", "bp_flat", "bp_head"):
        save[f"mix_{k}"] = np.array([float(np.median([r[k] for r in mrows if r["L"] == L])) for L in mix_present])
    mdeep = [r for r in mrows if r["L"] == mix_deep]
    if mdeep:
        save["mix_probe_flat"] = _med_profile(mdeep, "probe_flat")
        save["mix_probe_head"] = _med_profile(mdeep, "probe_head")
    for L in mix_present:
        rs = [r for r in mrows if r["L"] == L]
        print(f"  L{L:>2} W{rs[0]['width']:>3}: all {np.median([r['acc_all'] for r in rs]):.3f} "
              f"(BP {np.median([r['bp_all'] for r in rs]):.3f})  "
              f"flat {np.median([r['acc_flat'] for r in rs]):.3f} (BP {np.median([r['bp_flat'] for r in rs]):.3f})  "
              f"head {np.median([r['acc_head'] for r in rs]):.3f} (BP {np.median([r['bp_head'] for r in rs]):.3f})")

    np.savez(os.path.join(OUT, "arrays.npz"), **save)
    json.dump({"experiment": "p4_3_decay", "git_commit": _git(), "seeds": list(seeds), "wid_depths": wid_depths,
               "arms": ARMS, "wbase": WBASE, "wstep": WSTEP, "mix_depths": mix_depths, "regimes": REGIMES,
               "dim": DIM, "n_class": NCLASS, "numpy": np.__version__, "wall_clock_s": round(time.time() - t0, 1)},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=2)
    try:
        import plot_p4_3_decay as plot
        plot.draw_all(np.load(os.path.join(OUT, "arrays.npz")), OUT)
    except Exception as e:
        print(f"  [plot skipped: {e}]")
    print(f"  ({time.time()-t0:.0f}s) -> {OUT}  (git {_git()[:8]})")


if __name__ == "__main__":
    main()
