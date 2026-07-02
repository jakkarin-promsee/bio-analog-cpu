"""
P9.1 — N2: the drift-slowdown bake-off (read-side / rate-only) (design.md §3 P9.1). Swept variable = the N2 mechanism
∈ {no-N2 (the P8 loop) · EMA-view (namer reads a tap-EMA — the doubly-grounded, truly-read-side default) · LLRD-rate
(a LLRDCell subclass slowing the late-read layers — the flagged secondary, guarded representation-level)}. Score
drift-reduction × sleep-frequency-at-held-accuracy × worst-point A6-BWT × plasticity (new-task acc). Read: an arm ↓
drift -> sparser sleep at held A6 without a plasticity tax -> N2 standby->DEFAULT (commit the cheaper eligible) / no
arm clears the bar -> N2 STRUCK / LLRD moves the early/mid taps -> Stage-1-reopen FLAG. Inherits the ROTATION-ONLY
drift from P9.0 (the bulk doesn't forget; N2's job is to make the namer chase the rotation less often).

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p9_1.py [--quick]
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))
import p9lib as P                                                      # noqa: E402
import p9cfg as CFG                                                    # noqa: E402
import p9run as R                                                      # noqa: E402
import plot_p9                                                         # noqa: E402

QUICK = "--quick" in sys.argv
OUT = os.path.join(_HERE, "figs_p9_1" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
CADENCES = [8, 16, 24]                                                # committed grid-8 + 2x/3x-sparser (the N2 lever)
ARMS = [("no-N2", "base", None), ("ema-0.3", "ema", 0.3), ("ema-0.1", "ema", 0.1),
        ("llrd-0.5", "llrd", 0.5)]


def n2_of(kind, param):
    return P.EMAView(param) if kind == "ema" else None


def main():
    t0 = time.time()
    print(f"P9.1 — N2 bake-off (read-side/rate-only)  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    g, n2d = R.run_all_guards(verbose=True)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)
    stage1_reopen = not n2d["early_clean"]                            # LLRD honesty: early/mid taps must be unmoved
    print(f"  -> all guards PASS  (LLRD early/mid taps {'CLEAN (rate-only)' if not stage1_reopen else 'MOVE -> Stage-1-reopen FLAG'})", flush=True)

    per = {a[0]: dict(acc=[], bwt=[], plast=[], drift_red=[], sleepfreq=[], f=[]) for a in ARMS}
    for s in SEEDS:
        _, base_cache = R.build_life_cache(s, quick=QUICK, store_reps=False)
        drift_base = P.read_drift(base_cache, n2_beta=None)
        llrd_cache = None
        hf = R.committed_hf(s)
        # no-N2 grid-8 worst_bwt = the A6 reference every arm's sparser-hold is judged against
        ref = P.run_economy_p9(base_cache, hf, CFG, **{**R.COMMITTED_LOOP, "cadence_every": 8})
        ref_bwt = ref["worst_bwt"]
        for name, kind, param in ARMS:
            if kind == "llrd":
                if llrd_cache is None:
                    _, llrd_cache = R.build_life_cache(
                        s, quick=QUICK, store_reps=False,
                        cell_factory=lambda dims, ss, p=param: P.make_llrd_cell(dims, ss, rho=p, late=CFG.N2_LATE_LAYERS))
                cache = llrd_cache; drift_arm = P.read_drift(cache, n2_beta=None)
            else:
                cache = base_cache; drift_arm = P.read_drift(cache, n2_beta=param)
            # committed cadence (grid-8): the primary accuracy/BWT/plasticity read
            r8 = P.run_economy_p9(cache, hf, CFG, **{**R.COMMITTED_LOOP, "cadence_every": 8, "n2_view": n2_of(kind, param)})
            # sparser-hold: the sparsest cadence still within delta_acc of the no-N2 grid-8 worst_bwt
            held_cad, held_nsleep = 8, r8["nsleep"]
            for cad in CADENCES:
                rc = P.run_economy_p9(cache, hf, CFG, **{**R.COMMITTED_LOOP, "cadence_every": cad,
                                                         "n2_view": n2_of(kind, param)})
                if rc["worst_bwt"] >= ref_bwt - CFG.DELTA_ACC and cad >= held_cad:
                    held_cad, held_nsleep = cad, rc["nsleep"]
            per[name]["acc"].append(r8["aa"]); per[name]["bwt"].append(r8["worst_bwt"])
            per[name]["plast"].append(r8["plasticity"]); per[name]["f"].append(r8["firefrac"])
            per[name]["drift_red"].append(drift_base - drift_arm)
            per[name]["sleepfreq"].append(held_nsleep / cache["stream"]["n_steps"])
        print(f"  seed {s}: " + " | ".join(
            f"{a[0]} AA={per[a[0]]['acc'][-1]:.3f} wBWT={per[a[0]]['bwt'][-1]:+.3f} "
            f"drift_red={per[a[0]]['drift_red'][-1]:+.4f} sf={per[a[0]]['sleepfreq'][-1]:.3f}" for a in ARMS), flush=True)
        del base_cache, llrd_cache

    # verdict (STRICT lever — a real IMPROVEMENT, not mere non-inferiority): adopt-eligible iff acc held (within delta
    # of no-N2) AND worst-BWT not worse (within delta) AND plasticity not down > delta AND the LEVER fires — the arm
    # holds A6 at a STRICTLY sparser cadence than no-N2 (real-diff on sleep-freq) OR its worst-BWT is STRICTLY better
    # (real-diff). drift_red is a reported DIAGNOSTIC only (the cosine centroid measure is unreliable for a view that
    # re-centres the cloud). Commit the cheaper eligible; else struck.
    base_acc = per["no-N2"]["acc"]; base_bwt = per["no-N2"]["bwt"]; base_plast = per["no-N2"]["plast"]
    base_sf = per["no-N2"]["sleepfreq"]
    elig = {}
    for name, kind, param in ARMS:
        if name == "no-N2":
            continue
        d = per[name]
        acc_ok = R.med(d["acc"]) >= R.med(base_acc) - CFG.DELTA_ACC
        bwt_ok = R.med(d["bwt"]) >= R.med(base_bwt) - CFG.DELTA_ACC
        plast_ok = R.med(d["plast"]) >= R.med(base_plast) - CFG.DELTA_ACC
        sparser = R.real_diff(base_sf, d["sleepfreq"])[0] and R.med(d["sleepfreq"]) < R.med(base_sf)
        better_bwt = R.real_diff(d["bwt"], base_bwt)[0] and R.med(d["bwt"]) > R.med(base_bwt)
        lever_ok = bool(sparser or better_bwt)
        reopen = stage1_reopen and kind == "llrd"
        elig[name] = dict(acc_ok=acc_ok, bwt_ok=bwt_ok, plast_ok=plast_ok, lever_ok=lever_ok,
                          sparser=bool(sparser), better_bwt=bool(better_bwt), reopen=reopen,
                          eligible=bool(acc_ok and bwt_ok and plast_ok and lever_ok and not reopen))
    winners = [n for n, e in elig.items() if e["eligible"]]
    committed = (sorted(winners, key=lambda n: (0 if n.startswith("ema") else 1))[0] if winners else "struck")
    verdict = (f"N2 standby->DEFAULT: {committed}" if winners else "N2 STRUCK (no arm clears the bar)")

    A = dict(seeds=np.array(SEEDS), n2_arms=np.array([a[0] for a in ARMS]), **R.inv_arrays(g),
             inv_firefrac=np.array([R.med(per["no-N2"]["f"])]))
    for name, *_ in ARMS:
        d = per[name]
        A[f"accheld_{name}"] = np.array(d["acc"]); A[f"bwt_worst_{name}"] = np.array(d["bwt"])
        A[f"plasticity_{name}"] = np.array(d["plast"]); A[f"drift_red_{name}"] = np.array(d["drift_red"])
        A[f"sleepfreq_{name}"] = np.array(d["sleepfreq"])
    man = R.base_manifest("P9.1", _HERE, SEEDS, QUICK, guards=g, n2_detail=n2d, wall_s=round(time.time() - t0, 1),
                          eligibility=elig, committed_n2=committed, stage1_reopen=stage1_reopen,
                          summary={name: dict(acc=R.fmt(per[name]["acc"]), wbwt=R.fmt(per[name]["bwt"]),
                                              plast=R.fmt(per[name]["plast"]), drift_red=R.fmt(per[name]["drift_red"]),
                                              sleepfreq=R.fmt(per[name]["sleepfreq"])) for name, *_ in ARMS} | {"verdict": verdict})
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p9.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P9.1 SUMMARY (wall {man['wall_s']}s) ==", flush=True)
    for name, *_ in ARMS:
        d = per[name]
        print(f"  {name:9s}: AA {R.fmt(d['acc'])} wBWT {R.fmt(d['bwt'])} plast {R.fmt(d['plast'])} "
              f"drift_red {R.fmt(d['drift_red'])} sleepfreq {R.fmt(d['sleepfreq'])}", flush=True)
    for name, e in elig.items():
        print(f"  eligible[{name}] = {e['eligible']}  ({e})", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)


if __name__ == "__main__":
    main()
