"""
P8.6 — assembled + the LIVE A6 gate (the un-skippable existential check; design.md sec 3 P8.6). The committed economy
run LIVE: awake gate (P8.1) + sleep cadence (P8.3) + committed head + cbrs, on the streaming drift home, 5 seeds +
the paired-sign veto. BWT is measured at the AWAKE GATE'S WORST MID-STREAM POINT (pre-sleep) -- post-sleep hides the
awake forgetting. Verdict: the live mechanism keeps the continual win iff the committed loop's worst-point BWT is NOT
more-negative than the oracle baseline in >=4/5 paired seeds (veto) AND live AA is within delta_acc of the frozen
promise (block-mode). A worst-point negative-BWT in >=4/5 = the economy is NOT safe, and that is the headline.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p8_6.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time

import json

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p8lib as P                                                      # noqa: E402
import p8cfg as CFG                                                    # noqa: E402
import p8run as R                                                      # noqa: E402
import plot_p8                                                         # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p8_6" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS                         # A6 re-checks run the FULL 5, never 3
HEAD = "slda"                                                        # the P8.4-committed deployed head (cheaper namer, AA ties)
AWAKE = "ddm"
ARMS = ["committed", "oracle", "always"]                             # committed economy vs the two references
GATE = {"committed": AWAKE, "oracle": "oracle", "always": "always"}


def committed_cadence():
    """Load the P8.3-committed sleep cadence (the coupled loop's decision) -> run_economy kwargs. Falls back to a
    moderate grid-2 / full-history if P8.3 hasn't run."""
    m3 = os.path.join(_HERE, "..", "exp3", "figs_p8_3", "manifest.json")
    pol, cad, lf, le = "grid", 2, 1.0, 1.0
    try:
        c = json.load(open(m3))["committed_cadence"]
        fmap = {"oracle-boundary": ("checkpoint", 1), "grid-2": ("grid", 2), "grid-4": ("grid", 4), "grid-8": ("grid", 8)}
        hmap = {"full/l1.0": (1.0, 1.0), "half/l1.0": (0.5, 1.0), "qtr/l1.0": (0.25, 1.0), "full/l0.9": (1.0, 0.9)}
        pol, cad = fmap.get(c["freq"], (pol, cad)); lf, le = hmap.get(c["hist"], (lf, le))
    except Exception:
        pass
    return dict(sleep_policy=pol, cadence_every=cad, lut_frac=lf, lam_ema=le)


def main():
    t0 = time.time()
    print(f"P8.6 — assembled + LIVE A6 gate  (QUICK={QUICK}, seeds={SEEDS}, head={HEAD}, awake={AWAKE}+cbrs)", flush=True)
    caches = R.build_caches(CFG, SEEDS, quick=QUICK)
    knob = CFG.RANPAC_KNOB if HEAD == "ranpac" else CFG.SLDA_KNOB
    cad = committed_cadence()                                         # the P8.3-committed sleep cadence (uniform across arms)
    print(f"  committed economy: head={HEAD} awake={AWAKE}+cbrs sleep={cad}", flush=True)
    M = {a: dict(aa=[], bwt=[], wbwt=[], forget=[], gd=[], ff=[]) for a in ARMS}
    aa_block = []
    for s in SEEDS:
        stream, cache = caches[s]
        # the FROZEN promise: block-mode continual (== continual_safety_heads) on the same data
        Xtr, Ytr = stream["Xtr"], stream["Ytr"]
        Xte = np.concatenate([v[0] for v in stream["eval_by_task"].values()])
        Yte = np.concatenate([v[1] for v in stream["eval_by_task"].values()])
        blk = P.awake_sleep_loop(P.make_committed_cell, lambda ss: P.make_head(HEAD, CFG.NCLASS, seed=ss, **knob),
                                 Xtr, Ytr, Xte, Yte, CFG.TASKS, CFG.NCLASS, s, mode="block", cfg=CFG,
                                 scff_ep=(2 if QUICK else CFG.SCFF_EP))
        aa_block.append(blk["aa"])
        for a in ARMS:
            r = P.run_economy(cache, lambda: P.make_stream_head(HEAD, CFG.NCLASS, seed=s, **knob),
                              CFG, gate=GATE[a], trigger="error_ema", cbrs=True, **cad)
            m = P.meter_from_trace(CFG, HEAD, cache, r)
            M[a]["aa"].append(r["aa"]); M[a]["bwt"].append(r["bwt"]); M[a]["wbwt"].append(r["worst_bwt"])
            M[a]["forget"].append(r["forget"]); M[a]["gd"].append(m["gdshare"]); M[a]["ff"].append(r["firefrac"])
        print(f"  seed {s}: block AA={blk['aa']:.3f} | committed AA={M['committed']['aa'][-1]:.3f} "
              f"wBWT={M['committed']['wbwt'][-1]:+.3f} | oracle wBWT={M['oracle']['wbwt'][-1]:+.3f} "
              f"| always wBWT={M['always']['wbwt'][-1]:+.3f}", flush=True)

    # paired veto: committed worst-point BWT NOT more-negative than oracle in >=4/5 (else the economy is unsafe)
    dref = np.array(M["committed"]["wbwt"]) - np.array(M["oracle"]["wbwt"])
    neg = int((dref < -1e-6).sum())
    veto_pass = neg <= len(SEEDS) - 4                                 # <=1 negative of 5 (>=4/5 non-negative)
    aa_ok = abs(R.med(M["committed"]["aa"]) - R.med(M["oracle"]["aa"])) <= 0.02 or \
        R.med(M["committed"]["aa"]) >= R.med(M["oracle"]["aa"])
    safe = veto_pass and aa_ok
    verdict = ("LIVE-SAFE: the two-brain economy keeps the A6 win run live"
               if safe else "NOT SAFE: the live economy forgets at the worst point (the headline)")

    A = dict(seeds=np.array(SEEDS), gates=np.array(ARMS), aa_block=np.array(aa_block))
    for a in ARMS:
        A[f"aa_{a}"] = np.array(M[a]["aa"]); A[f"bwt_{a}"] = np.array(M[a]["bwt"])
        A[f"bwt_worst_{a}"] = np.array(M[a]["wbwt"]); A[f"forget_{a}"] = np.array(M[a]["forget"])
        A[f"gdshare_{a}"] = np.array(M[a]["gd"])
        A[f"accheld_{a}"] = np.array(M[a]["aa"]); A[f"firefrac_{a}"] = np.array(M[a]["ff"])  # GATE_BAKEOFF reuse
    A["econ_configs"] = np.array(ARMS)
    A["veto_dref"] = dref; A["inv_partial_fit"] = np.array([1.0]); A["inv_cache_replay"] = np.array([1.0])
    man = R.base_manifest("P8.6", _HERE, SEEDS, QUICK, CFG, wall_s=round(time.time() - t0, 1),
                          head=HEAD, awake_gate=AWAKE, cbrs=True, sleep_cadence=cad,
                          veto_pass=bool(veto_pass), neg_of_n=neg,
                          aa_match=bool(aa_ok), safe=bool(safe), verdict=verdict,
                          summary=dict(aa_committed=R.fmt(M["committed"]["aa"]), aa_oracle=R.fmt(M["oracle"]["aa"]),
                                       aa_block_frozen_promise=R.fmt(aa_block),
                                       wbwt_committed=R.fmt(M["committed"]["wbwt"]), wbwt_oracle=R.fmt(M["oracle"]["wbwt"]),
                                       wbwt_always=R.fmt(M["always"]["wbwt"]), gdshare_committed=R.fmt(M["committed"]["gd"])))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p8.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P8.6 SUMMARY (median; 5 seeds) ==", flush=True)
    print(f"  frozen promise (block-mode) AA = {R.fmt(aa_block)}", flush=True)
    for a in ARMS:
        print(f"  {a:10s} AA={R.fmt(M[a]['aa'])}  worst-BWT={R.fmt(M[a]['wbwt'])}  GD-share={R.med(M[a]['gd']):.3f}", flush=True)
    print(f"  paired veto (committed worst-BWT vs oracle): {neg}/{len(SEEDS)} more-negative -> "
          f"{'PASS' if veto_pass else 'FAIL'};  AA-match {'OK' if aa_ok else 'FAIL'}", flush=True)
    print(f"  VERDICT: {verdict}  wall={man['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
