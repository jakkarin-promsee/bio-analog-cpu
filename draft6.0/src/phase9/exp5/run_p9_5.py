"""
P9.5 — assemble + FREEZE (the integration + the lock) (design.md §3 P9.5). Every committed knob live at once —
NoiseAugContrast bulk + SLDA + DDM/error-EMA gate + cbrs + the P9-tuned cadence/depth + the committed eviction policy
(+ N2 if P9.1 adopted, + read-side if P9.4 earned). Re-run the P8.6 live-safety gate on the FULLY-TUNED loop, 5 seeds,
paired-sign veto, worst-BWT at the worst mid-stream point (pre-sleep). Read: the assembled loop holds A6 + accuracy at
the metered economy -> COMMIT + FREEZE (the hash P10 races) / a knob interaction breaks it -> fix inside P9 + re-freeze.
Freeze cuts (all vs INTERNAL references, NEVER the P10 baseline):
  (1) worst-point A6-BWT not more-negative than the oracle in >= 4/5 (the paired-sign veto);
  (2) accuracy-held within delta_acc of the BASE committed loop on the SAME lifelong stream (the pinned reference —
      'P9 tuning did not cost accuracy vs the shipped object'); P8.6's CI-stream AA reported for context;
  (3) the metered GD-share stays <= 0.25.

Run: OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p9_5.py [--quick]
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
OUT = os.path.join(_HERE, "figs_p9_5" + ("_quick" if QUICK else ""))
SEEDS = CFG.SEEDS[:2] if QUICK else CFG.SEEDS
P86_CI_AA = 0.447                                                     # P8.6 committed live AA (CI stream) — context ref
# The FREEZE-DRIVEN cadence re-confirm (run_p9_5_cadence.py). The first assemble at the inherited P8 grid-8 cadence
# FAILED the worst-point oracle-veto on the lifelong REVISIT stream (2/5 seeds' pre-sleep worst-BWT materially
# more-negative than the boundary oracle — deep troughs between sparse sleeps on high-variance seeds). The cadence
# re-confirm (the P8 'cadence is drift-rate-conditional' debt, owed by the freeze) found ANY denser cadence clears the
# veto at held AA + GD-share <= 0.25; grid-4 is the KNEE (worst-BWT saturates at ~-0.03 = grid-2's, cheaper than grid-2,
# safer than grid-6's -0.087). So the FROZEN lifelong loop deploys grid-4 (the base/shipped AA ref stays P8.6 grid-8).
LIFELONG_CADENCE = 4


def main():
    t0 = time.time()
    committed_n2 = R.load_prior("exp1", "committed_n2", "struck")
    committed_depth = R.load_prior("exp2", "committed_depth", "alltap")
    committed_evict = R.load_prior("exp3", "committed_eviction", "cbrs")
    resid = R.load_prior("exp4", "gate_fired", False)
    n2_fac, needs_llrd, rho = R.n2_view_for(committed_n2)
    # The committed eviction POLICY (P9.3) is cbrs — but cbrs is ALREADY the P8.6 committed loop's sleep guard on the
    # class-prototype buffer (the fixed balanced probe = the deployment budget). P9.3's tight-cap StreamingLUT is a
    # STRESS APPARATUS (the cap-scaling law), not the deployed budget: at cap >= the class-prototype count it does not
    # evict, and a tight cap costs AA/BWT (the bound bites). So the FROZEN loop deploys cbrs on the committed buffer
    # (use_lut=False -> the P8.6 fixed-probe+cbrs sleep) — the object P9 confirmed nothing needs to change from.
    use_lut = False
    print(f"P9.5 — assemble + FREEZE  (QUICK={QUICK}, seeds={SEEDS})", flush=True)
    print(f"  committed knobs: N2={committed_n2} depth={committed_depth} eviction={committed_evict}(cap {CFG.EVICT_CAP}) "
          f"read-side-residual={'earned' if resid else 'skipped'}", flush=True)
    g, _ = R.run_all_guards(verbose=True)
    if not all(g.values()):
        print(f"!! GUARD FAILURE {g} — STOP", flush=True); sys.exit(1)

    asm = dict(bwt=[], aa=[], gd=[]); base = dict(bwt=[], aa=[]); orc = dict(bwt=[], aa=[])
    for s in SEEDS:
        cf = (lambda dims, ss: P.make_llrd_cell(dims, ss, rho=rho, late=CFG.N2_LATE_LAYERS)) if needs_llrd else None
        store = committed_depth != "alltap"
        _, cache = R.build_life_cache(s, quick=QUICK, store_reps=store, cell_factory=cf)
        hf = R.committed_hf(s)

        def assembled(gate):
            lut = P.StreamingLUT(CFG.EVICT_CAP, committed_evict, cache["stream"]["C"], s) if use_lut else None
            return P.run_economy_p9(cache, hf, CFG, **{**R.COMMITTED_LOOP, "gate": gate,
                                                       "cadence_every": LIFELONG_CADENCE,  # grid-4 (freeze re-confirm)
                                                       "sleep_depth": committed_depth, "n2_view": n2_fac(),
                                                       "lut": lut, "cbrs": (not use_lut)})
        r_asm = assembled("ddm")
        r_orc = assembled("oracle")
        r_base = P.run_economy_p9(cache, hf, CFG, **R.COMMITTED_LOOP)   # the shipped loop on the same stream (AA ref)
        met = P.loop_energy(CFG, R.HEAD, r_asm, cache)
        asm["bwt"].append(r_asm["worst_bwt"]); asm["aa"].append(r_asm["aa"]); asm["gd"].append(met["gdshare"])
        base["bwt"].append(r_base["worst_bwt"]); base["aa"].append(r_base["aa"])
        orc["bwt"].append(r_orc["worst_bwt"]); orc["aa"].append(r_orc["aa"])
        print(f"  seed {s}: assembled AA={r_asm['aa']:.3f} wBWT={r_asm['worst_bwt']:+.3f} gd={met['gdshare']:.3f} | "
              f"base AA={r_base['aa']:.3f} wBWT={r_base['worst_bwt']:+.3f} | oracle wBWT={r_orc['worst_bwt']:+.3f}", flush=True)
        del cache

    # freeze cuts — the paired-sign veto tolerates a sub-delta_acc gap (a difference within delta_acc is 'not real' per
    # the house bar), so it fires only on a seed materially worse than the oracle.
    neg = R.paired_sign_neg(asm["bwt"], orc["bwt"], tol=CFG.DELTA_ACC)  # #seeds assembled worse-than-oracle by > delta
    veto_ok = neg <= len(SEEDS) - 4                                    # not materially-worse in >=4/5
    aa_ok = R.med(asm["aa"]) >= R.med(base["aa"]) - CFG.DELTA_ACC
    gd_ok = R.med(asm["gd"]) <= CFG.GD_SHARE_CAP
    frozen = bool(veto_ok and aa_ok and gd_ok)
    ghash = R.git_hash(_HERE)
    verdict = (f"FREEZE — assembled loop holds A6 (veto {neg}/{len(SEEDS)} more-neg), AA held, GD-share "
               f"{R.med(asm['gd']):.3f} <= {CFG.GD_SHARE_CAP}; lock at commit" if frozen else
               f"NOT frozen (veto {veto_ok}/acc {aa_ok}/gd {gd_ok}) -> fix inside P9 + re-freeze")

    A = dict(seeds=np.array(SEEDS), safety_cfgs=np.array(["assembled", "oracle", "base"]),
             freeze_bwt_worst=np.array(asm["bwt"]), freeze_accheld=np.array(asm["aa"]), freeze_gdshare=np.array(asm["gd"]),
             freeze_oracle_bwt=np.array(orc["bwt"]), freeze_hash=np.array([ghash]),
             aa_assembled=np.array(asm["aa"]), bwt_worst_assembled=np.array(asm["bwt"]),
             aa_oracle=np.array(orc["aa"]), bwt_worst_oracle=np.array(orc["bwt"]),
             aa_base=np.array(base["aa"]), bwt_worst_base=np.array(base["bwt"]),
             **R.inv_arrays(g), inv_firefrac=np.array([R.med(asm["gd"])]))
    man = R.base_manifest("P9.5", _HERE, SEEDS, QUICK, guards=g, wall_s=round(time.time() - t0, 1),
                          committed_knobs=dict(N2=committed_n2, depth=committed_depth, eviction=committed_evict,
                                               evict_cap=CFG.EVICT_CAP, read_side_residual=("earned" if resid else "skipped (gate not fired)"),
                                               sleep_cadence=f"grid-{LIFELONG_CADENCE} (freeze re-confirm; P8 grid-8 was single-pass)",
                                               bulk="NoiseAugContrast σ_aug=1.0", head="SLDA", gate="DDM/error-EMA", cbrs=True),
                          freeze=dict(frozen=frozen, veto_more_neg=neg, veto_ok=bool(veto_ok), aa_ok=bool(aa_ok),
                                      gd_ok=bool(gd_ok), git_hash_prefreeze=ghash),
                          summary=dict(assembled_aa=R.fmt(asm["aa"]), assembled_wbwt=R.fmt(asm["bwt"]),
                                       assembled_gdshare=R.fmt(asm["gd"]), base_aa=R.fmt(base["aa"]),
                                       base_wbwt=R.fmt(base["bwt"]), oracle_wbwt=R.fmt(orc["bwt"]),
                                       p86_ci_aa=P86_CI_AA, verdict=verdict))
    R.save_run(OUT, A, man)
    print("== figures ==", flush=True)
    for p in plot_p9.regen(OUT):
        print("  " + os.path.basename(p), flush=True)
    print(f"\n== P9.5 SUMMARY (wall {man['wall_s']}s) ==", flush=True)
    print(f"  assembled: AA {R.fmt(asm['aa'])} wBWT {R.fmt(asm['bwt'])} GD-share {R.fmt(asm['gd'])}", flush=True)
    print(f"  base (shipped, same stream): AA {R.fmt(base['aa'])} wBWT {R.fmt(base['bwt'])}", flush=True)
    print(f"  oracle: wBWT {R.fmt(orc['bwt'])}  | veto {neg}/{len(SEEDS)} more-neg (ok={veto_ok})", flush=True)
    print(f"  AA-held={aa_ok} GD<=0.25={gd_ok}  git(pre-freeze)={ghash[:10]}", flush=True)
    print(f"  VERDICT: {verdict}", flush=True)


if __name__ == "__main__":
    main()
