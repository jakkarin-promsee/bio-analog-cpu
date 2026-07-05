"""P11.7 — throughput / stream-rate (the strike-3 'does it scale?' answer, real-time half). A DERIVATION from the
metered FLOPs/sample (the Ghunaim read — computed, not wall-clock), on the gas stream. R12 pins: price BOTH learners
SAME-substrate (analog a separate labeled row, never mixed); the demonstration rate = the GEOMETRIC MEAN of the two
critical rates (fixed by rule before any read). The honest branch is pre-registered as (iii) THE INVERSION: P10
measured OURS at MORE FLOPs/sample (the 12-layer bulk every step), so on RAW FLOPs OURS's critical rate is LOWER and
it drops first — UNLESS the analog substrate re-prices it (the crossbar MACs near-free). Reads: the critical-rate
table + the branch.
"""
import os, time
import numpy as np
import p11lib as P
import p10cfg as CFG0

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp7", "figs_p11_7")
t0 = time.time()
print("=" * 78, "\nP11.7 THROUGHPUT — the critical-rate derivation (gas), same-substrate + the analog row\n", "=" * 78, flush=True)

# ---- OURS-A on gas (one seed; the FLOPs/sample + energy/sample source) ------------------------------
cfg = P.arm_a_cfg(6)
stream, meta = P.make_real_stream("gas", cfg, 42, arm="A")
cache = P.build_cache_p9(P.make_committed_cell, stream, 42, cfg, store_reps=False)
res = P.run_economy_p9(cache, lambda: P.make_stream_head(P.HEAD, 6, seed=42, **cfg.SLDA_KNOB), cfg, **P.COMMITTED_LOOP_G4)
n_steps = len(cache["steps"]); B = cfg.BATCH
fb_ours = P.P10.fair_budget_meter(cfg, learner="ours", ours_cache=cache, ours_res=res)
m_a = P.meter_from_trace(cfg, P.HEAD, cache, res, substrate="analog")
m_d = P.meter_from_trace(cfg, P.HEAD, cache, res, substrate="digital")
E_ours_a = m_a["total"] / (n_steps * B); E_ours_d = m_d["total"] / (n_steps * B)

# ---- ER-strong on gas (tuned seed-7) ---------------------------------------------------------------
def gas_stream(seed): return P.make_real_stream("gas", P.arm_a_cfg(6), seed, arm="A")[0]
er = P.tune_er_arena(gas_stream, cfg, cfg.DIM, 6, tune_seed=7, lrs=(0.1, 0.03), replays=(2, 4), hidden_mults=(1, 2))
fb_er = P.P10.fair_budget_meter(cfg, learner="er", bp_dims=er["bp_dims"], replay=er["replay"],
                                buffer_cap=er["buffer_cap"], in_dim=cfg.DIM)
er_a = P.P10.bp_stream_energy(cfg, er["bp_dims"], "er", n_steps=n_steps, replay=er["replay"], substrate="analog")
er_d = P.P10.bp_stream_energy(cfg, er["bp_dims"], "er", n_steps=n_steps, replay=er["replay"], substrate="digital")
E_er_a = er_a["total"] / (n_steps * B); E_er_d = er_d["total"] / (n_steps * B)

# ---- the throughput derivation (critical rate proportional to 1/cost; higher cost -> saturates first) ----
F_ours, F_er = fb_ours["flops_per_sample"], fb_er["flops_per_sample"]
tp_flops = P.P10.throughput_meter({"ours_g4": F_ours, "er_strong": F_er}, c_stream_learner="ours_g4")
# critical rate (arbitrary compute-budget units R=1): lam_crit = R / cost ; demo rate = geometric mean (R12)
def crit_table(cost_ours, cost_er, label):
    lam_o, lam_e = 1.0 / cost_ours, 1.0 / cost_er
    lam_demo = float(np.sqrt(lam_o * lam_e))
    skip_o = max(0.0, 1.0 - lam_o / lam_demo); skip_e = max(0.0, 1.0 - lam_e / lam_demo)
    print(f"  [{label}] cost/sample OURS {cost_ours:.3g} vs ER {cost_er:.3g} (ratio {cost_ours/cost_er:.2f}x) | "
          f"crit-rate OURS {lam_o:.3g} vs ER {lam_e:.3g} | demo(geomean) {lam_demo:.3g} -> "
          f"skip@demo OURS {skip_o:.1%} / ER {skip_e:.1%}", flush=True)
    return dict(cost_ours=cost_ours, cost_er=cost_er, ratio=cost_ours / cost_er, lam_ours=lam_o, lam_er=lam_e,
                lam_demo=lam_demo, skip_ours=skip_o, skip_er=skip_e)

print("\n[derivation table — same-substrate rows]", flush=True)
row_flops = crit_table(F_ours, F_er, "RAW FLOPs/sample")
row_dig = crit_table(E_ours_d, E_er_d, "ENERGY/sample DIGITAL")
row_ana = crit_table(E_ours_a, E_er_a, "ENERGY/sample ANALOG (the chip)")

# ---- verdict (the pre-registered branches) ---------------------------------------------------------
inversion = F_ours > F_er
analog_wins = E_ours_a < E_er_a
if inversion and analog_wins:
    verd = ("BRANCH (iii) THE INVERSION, RESOLVED BY SUBSTRATE — on RAW FLOPs OURS costs %.2fx more (the 12-layer "
            "bulk) so it drops FIRST under a fixed-FLOP real-time budget; but on the ANALOG chip OURS's energy/sample "
            "is %.2fx LOWER than ER, so the real-time disadvantage is a DIGITAL artifact — on the substrate the "
            "throughput economy holds." % (F_ours / F_er, E_er_a / E_ours_a))
elif inversion:
    verd = "BRANCH (iii) THE INVERSION — OURS costs more per sample on every substrate row; the economy loses its real-time sentence (reported)."
else:
    verd = "BRANCH (i) THE REGIME WIN — OURS's critical rate exceeds ER's (a rate exists where ER drops and OURS does not)."
print("\n  VERDICT:", verd, flush=True)

arrays = dict(flops_ours=np.array([F_ours]), flops_er=np.array([F_er]),
              e_ours_analog=np.array([E_ours_a]), e_ours_digital=np.array([E_ours_d]),
              e_er_analog=np.array([E_er_a]), e_er_digital=np.array([E_er_d]))
manifest = dict(rung="P11.7", git=P.git_hash(), arena="gas", er_cfg=dict(lr=er["lr"], replay=er["replay"], hidden=er["hidden"]),
                flops_per_sample=dict(ours=F_ours, er=F_er, ratio=F_ours / F_er),
                energy_per_sample=dict(ours_analog=E_ours_a, ours_digital=E_ours_d, er_analog=E_er_a, er_digital=E_er_d),
                rows=dict(raw_flops=row_flops, energy_digital=row_dig, energy_analog=row_ana),
                throughput_flops=tp_flops, verdict=verd,
                note="derivation from metered FLOPs/sample (Ghunaim read); same-substrate rows + the analog row (R12); "
                     "demo rate = geometric mean of the two critical rates. No wall-clock (a numpy artifact).",
                wall_s=round(time.time() - t0, 1))
P.save_run(OUT, arrays, P.jsonsafe(manifest))
print(f"\n  saved -> {OUT}  ({time.time()-t0:.1f}s)", flush=True)
