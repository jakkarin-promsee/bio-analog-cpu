"""P11.1 — the decomposition (strike 1: "is it just SLDA?"). Δbulk = (bulk->namer) - (proj->namer) per capability
channel. Run BEFORE the professor pitch — either Δbulk outcome you want in hand.

DESIGN DEVIATION (commented, per author's "change the plan on the result you get"): the spec pinned P11.1 to the
digits home + P10.3 gauntlet. A pre-run diagnostic showed DIGITS ARE NEARLY LINEARLY SEPARABLE (raw-SLDA 0.95),
so a linear namer already saturates and the bulk *cannot* add there (Δbulk<=0) — the digits-only read would bank a
MISLEADING "the bulk is worthless". The honest measurement sweeps arenas of INCREASING nonlinearity
{synth-home (the P7/P10-validated arena) -> mnist-40 -> digits}, so Δbulk is reported as a FUNCTION of how much
nonlinear structure the arena has. This is the strike-1 answer with its mechanism, not a flat number.
"""
import os, time
import numpy as np
import p11lib as P
import p10cfg as CFG0
from p6lib import train_cell
from p5lib import synth_stream

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exp1", "figs_p11_1")
SEEDS = P.SEEDS
t0 = time.time()
cfg = P.arm_a_cfg(10)
dims = [cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH
NZ_IID, NZ_DIR = 1.0, 1.0                                               # moderate rms so the noise channel is INFORMATIVE (not floored)

print("=" * 78, "\nP11.1 DECOMPOSITION — Δbulk vs arena nonlinearity (the strike-1 answer)\n", "=" * 78, flush=True)


def slda(Ftr, Ytr, Fte, Yte, C, seed):
    h = P.make_stream_head(P.HEAD, C, seed=seed, **cfg.SLDA_KNOB); h.sleep_fit(Ftr, Ytr)
    return float((h.predict(Fte) == Yte).mean())


def home_split(arena, seed):
    """Clean home (train,test) projected to cfg.DIM. synth = the P7/P10 nonlinear home; digits/mnist projected."""
    if arena == "synth":
        Xtr, Ytr, Xte, Yte = synth_stream(CFG0.NTR, CFG0.NTE, CFG0.OVERLAP, seed, dim=CFG0.DIM,
                                          n_class=CFG0.NCLASS, n_clusters=CFG0.NCLUST)
        return Xtr, Ytr, Xte, Yte
    Xtr_i, Ytr, Xte_i, Yte, _ = P.load_image_split(arena, seed, 3000 if arena == "mnist" else CFG0.GAUNTLET_NTR,
                                                   1000 if arena == "mnist" else CFG0.GAUNTLET_NTE)
    Pj = P.porthole(Xtr_i.shape[1], cfg.DIM, pseed=7000 + seed)
    return Xtr_i @ Pj, Ytr, Xte_i @ Pj, Yte


# ---- home-AA channel (the strike) + noise channel, across arena nonlinearity ----
home = {a: {} for a in ["synth", "mnist", "digits"]}                   # arena -> chan -> cell -> [seeds]
def hpush(a, chan, cell, v): home[a].setdefault(chan, {}).setdefault(cell, []).append(v)

for seed in SEEDS:
    for arena in ["synth", "mnist", "digits"]:
        Xtr, Ytr, Xte, Yte = home_split(arena, seed)
        rng = np.random.default_rng(seed + 55)
        cells = dict(bulk=P.make_committed_cell(dims, seed), proj=P.identity_cell(dims, seed),
                     reservoir=P.random_frozen_cell(dims, seed))
        train_cell(cells["bulk"], Xtr, rng, ep=CFG0.STATIC_EP, batch=cfg.BATCH)
        for cn, cell in cells.items():
            Ftr, Fte = P.all_tap_feats(cell, Xtr), P.all_tap_feats(cell, Xte)
            hpush(arena, "homeAA", cn, slda(Ftr, Ytr, Fte, Yte, 10, seed))
            nz = P.cell_noise_retention(cell, Xtr, Ytr, Xte, Yte, cfg, 10, seed, channels=("iid", "directional"))
            hpush(arena, "iid", cn, nz["iid"]); hpush(arena, "directional", cn, nz["directional"])
    print(f"  home/noise seed {seed} ({time.time()-t0:.1f}s)", flush=True)

# ---- continual channels (safety worst-BWT, retention) from the live gauntlet: digits + mnist ----
gaunt = {a: {} for a in ["digits", "mnist"]}
def gpush(a, chan, cell, v): gaunt[a].setdefault(chan, {}).setdefault(cell, []).append(v)
for seed in SEEDS:
    for arena in ["digits", "mnist"]:
        stream = P.make_arena_gauntlet_stream(arena, cfg, seed, ntr=CFG0.GAUNTLET_NTR, nte=CFG0.GAUNTLET_NTE,
                                              block=24, regime="rapid")
        hf = lambda: P.make_stream_head(P.HEAD, cfg.NCLASS, seed=seed, **cfg.SLDA_KNOB)
        for cn, cf in [("bulk", P.make_committed_cell), ("proj", P.identity_cell)]:
            cache = P.build_cache_p9(cf, stream, seed, cfg, store_reps=False)
            res = P.run_economy_p9(cache, hf, cfg, **P.COMMITTED_LOOP_G4)
            ret = P.allprev_retention(res["matrix"]); m = P.meter_from_trace(cfg, P.HEAD, cache, res)
            gpush(arena, "gauntletAA", cn, res["aa"]); gpush(arena, "worst_bwt", cn, res["worst_bwt"])
            gpush(arena, "ret_worst", cn, ret["worst"])
            gpush(arena, "energy", cn, float(m["gd"] if cn == "proj" else m["total"]))
    print(f"  gauntlet seed {seed} ({time.time()-t0:.1f}s)", flush=True)

# ---- report --------------------------------------------------------------------------------------
med = lambda x: float(np.median(x))
print("\n  [home-AA + noise, Δbulk = bulk - proj, median over 5 seeds]", flush=True)
print(f"  {'arena':8s} {'homeAA bulk/proj':20s} {'Δbulk':8s}  {'iid-ret Δ':10s} {'dir-ret Δ':10s}", flush=True)
arena_dbulk = {}
for a in ["synth", "mnist", "digits"]:
    b = med(home[a]["homeAA"]["bulk"]); p = med(home[a]["homeAA"]["proj"])
    ib = med(home[a]["iid"]["bulk"]) - med(home[a]["iid"]["proj"])
    db = med(home[a]["directional"]["bulk"]) - med(home[a]["directional"]["proj"])
    arena_dbulk[a] = dict(homeAA_bulk=b, homeAA_proj=p, dbulk_homeAA=b - p, dbulk_iid=ib, dbulk_dir=db)
    print(f"  {a:8s} {b:.3f} / {p:.3f}       {b-p:+.3f}    {ib:+.3f}     {db:+.3f}", flush=True)
print("\n  [gauntlet live-loop channels, median over 5 seeds]", flush=True)
print(f"  {'arena':8s} {'gauntletAA b/p':16s} {'worstBWT b/p':16s} {'ret-worst b/p':16s} {'energy b/p':16s}", flush=True)
for a in ["digits", "mnist"]:
    ab, ap = med(gaunt[a]["gauntletAA"]["bulk"]), med(gaunt[a]["gauntletAA"]["proj"])
    wb, wp = med(gaunt[a]["worst_bwt"]["bulk"]), med(gaunt[a]["worst_bwt"]["proj"])
    rb, rp = med(gaunt[a]["ret_worst"]["bulk"]), med(gaunt[a]["ret_worst"]["proj"])
    eb, ep = med(gaunt[a]["energy"]["bulk"]), med(gaunt[a]["energy"]["proj"])
    arena_dbulk[a].update(gauntletAA_b=ab, gauntletAA_p=ap, worstbwt_b=wb, worstbwt_p=wp, energy_b=eb, energy_p=ep)
    print(f"  {a:8s} {ab:.3f}/{ap:.3f}     {wb:+.3f}/{wp:+.3f}    {rb:.3f}/{rp:.3f}     {eb:.2e}/{ep:.2e}", flush=True)

# ---- verdict (design §2.4-P11.1, arena-conditioned) ----------------------------------------------
syn = arena_dbulk["synth"]["dbulk_homeAA"]; dig = arena_dbulk["digits"]["dbulk_homeAA"]
iid_wins = any(arena_dbulk[a]["dbulk_iid"] > 0.02 for a in ["synth", "mnist", "digits"])
if syn > 0.1 and iid_wins:
    verdict = ("NARROWED-WITH-MECHANISM — the architecture is MORE than its closed-form namer where the data is "
               "NONLINEAR (synth home Δbulk +%.3f; iid-noise Δbulk>0), and correctly NULL where a linear namer "
               "already saturates (digits Δbulk %.3f). 'Is it just SLDA?' -> No on the data that needs a bulk; "
               "effectively yes where a linear head suffices. The bulk's value is arena-nonlinearity, mapped." %
               (syn, dig))
elif syn > 0.1:
    verdict = "CONFIRMED on nonlinear data (synth Δbulk +%.3f) — the bulk is the learner, the namer only names." % syn
else:
    verdict = "BROKEN — Δbulk<=0 even on nonlinear data (kill criterion (i)): the story is gate+sleep+closed-form namer."
print(f"\n  VERDICT: {verdict}", flush=True)
res_rf = med(home["synth"]["homeAA"]["reservoir"])
print(f"  reservoir control on synth: random-frozen-bulk homeAA {res_rf:.3f} vs bulk "
      f"{arena_dbulk['synth']['homeAA_bulk']:.3f} -> "
      f"{'SCFF LEARNING matters (not just 12 layers)' if arena_dbulk['synth']['homeAA_bulk']>res_rf+0.02 else 'reservoir ties -> the nonlinearity is the reservoir, not learning'}", flush=True)

# ---- save ----------------------------------------------------------------------------------------
arrays = {}
for a in home:
    for ch in home[a]:
        for cn, v in home[a][ch].items():
            arrays[f"home_{a}_{ch}_{cn}"] = np.array(v, float)
for a in gaunt:
    for ch in gaunt[a]:
        for cn, v in gaunt[a][ch].items():
            arrays[f"gaunt_{a}_{ch}_{cn}"] = np.array(v, float)
for a in arena_dbulk:
    arrays[f"dbulk_homeAA_{a}"] = np.array([arena_dbulk[a]["dbulk_homeAA"]])
manifest = dict(rung="P11.1", git=P.git_hash(), seeds=SEEDS, cfg="armA committed D40/W64/L12/C10",
                arenas_home=["synth", "mnist", "digits"], arenas_gauntlet=["digits", "mnist"],
                noise_rms=dict(iid=NZ_IID, directional=NZ_DIR), verdict=verdict, arena_dbulk=arena_dbulk,
                note="proj=identity cell (no SCFF, namer reads raw ->D input); reservoir=random-frozen bulk; "
                     "DESIGN DEVIATION: swept arena nonlinearity because digits alone (near-linear) understate Δbulk.",
                wall_s=round(time.time() - t0, 1))
P.save_run(OUT, arrays, P.jsonsafe(manifest))
print(f"\n  saved -> {OUT}  ({time.time()-t0:.1f}s)", flush=True)
