"""
p9lib — the Phase-9 apparatus: CLOSE & FREEZE the maintenance loop. A CHIP NETLIST, not normal Python: every reuse is
a *tested* primitive carried forward unchanged from p8lib (which re-exports p7/p6/p5…), and every genuinely-new organ
ships with its own equivalence/behaviour guard. Phase 9 tunes the FINE machinery AROUND P8's committed loop (SLDA +
DDM gate on the namer's error-EMA — the class-direction trigger was validated but NOT deployed — + grid-8/full-history
sleep) against INTERNAL signals only, then freezes the object.

The five things P9 closes (design §0.0): (P9.0) the measured bulk-drift rate + the rotation/staleness/DESTRUCTION split;
(P9.1) N2 read-side/rate-only; (P9.2) sleep consolidation DEPTH; (P9.3) bounded-LUT eviction; (P9.4, conditional) the
read-side noise residual; (P9.5) assemble + FREEZE. The envelope is unbroken: GD reads taps, never writes SCFF.

Built on p8lib. Reused, NOT re-implemented:
  p8lib : run_economy (the guard reference for run_economy_p9), make_drift_stream, build_cache, awake_sleep_loop,
          make_stream_head/SLDAHeadStream/RanPACHeadStream (+ partial_fit/sleep_fit), the detectors + triggers,
          hardware_cost_meter/meter_from_trace/bp_replay_energy, class_balanced_reservoir, continual_safety_heads
          (the oracle/block-mode reference), readout_feats/all_tap_feats/trunc_feats, make_committed_cell, and ALL P8
          guards. calibrate_threshold, sig_tap_drift_direction, _l2n, _onehot.
  p6lib (direct — NOT in p8lib.__all__, so sys.path the ../phase6 dir): bulk_drift, NoiseModel, infer_noisy,
          NoiseAugContrast (the LLRDCell base), label_free_axis, class_axis.

NEW here (Phase 9) — design §6:
  make_lifelong_stream : the long/repeating stream (revisit cycles) so drift accumulates past P8's single pass.
  build_cache_p9 : build_cache + per-layer reps_b (batch) & reps_probe (probe) & reps_early (held-out task-0) at grid
      steps -> the probes score at any depth (P9.0) and the depth selector re-slices at sleep (P9.2).
  probe_retention : the THREE-curve P9.0 instrument (rotation cosine / fit-once frozen probe / RE-FIT optimal probe).
  EMAView : the N2 read-side de-drift (a stateful tap-mean EMA subtracted from the taps the namer reads). SCFF untouched.
  LLRDCell(NoiseAugContrast) : the N2 flagged-secondary — scales the LATE-read layers' applied update by rho (rate-only
      IFF the representation guard holds). Its own build_cache per rho.
  run_economy_p9 : run_economy + the N2 view, the sleep-DEPTH selector, the StreamingLUT eviction, and a lifelong
      worst-BWT tracker. All P9 features OFF == run_economy bit-for-bit (n2_readside_guard).
  StreamingLUT(cap, policy) : the accumulating, EVICTING prototype store (P8 had only a fixed balanced probe).
      Policies: cbrs / reservoir / recency / herding(the magnitude null) / dcbrs(hand-rolled, single-threaded).
  sleep_cost_at_depth : the depth-aware sleep re-fit energy (the solve/Gram term at the depth's Fdim — trunc re-slices
      the top of the full forward, so only the Fdim term saves; the SCFF re-forward is unchanged and reported apart).
  proto_reanchor / slda_readside_refit / residual_probe : the P9.4 conditional read-side defenses (Phase-6 NoiseModel).
  guards : n2_readside_guard (N2-off == P8 bit-for-bit; EMA-view: SCFF untouched; LLRD: rho=1 bit-for-bit + early/mid
      taps unmoved), evict_equiv_guard (cap=inf retains all appends; finite-cap recency == exactly the last-k). + all P8.

numpy only. CPU float64 (the bit-exact guards need determinism). OMP_NUM_THREADS=1 set by the run layer. NO sklearn.
"""
from __future__ import annotations
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase8"))                # p8lib
sys.path.insert(0, os.path.join(_HERE, "..", "phase6"))                # p6lib direct (bulk_drift/NoiseModel not in p8 __all__)
import p8lib as P8                                                      # noqa: E402
from p8lib import (run_economy, make_drift_stream, build_cache, awake_sleep_loop,                   # noqa: E402
                   make_stream_head, RanPACHeadStream, SLDAHeadStream,
                   make_detector, calibrate_threshold, sig_tap_drift_direction, sig_tap_drift_magnitude,
                   sig_driftlens, mtd_far, hardware_cost_meter, meter_from_trace, bp_replay_energy,
                   class_balanced_reservoir, continual_safety_heads, readout_feats, all_tap_feats,
                   trunc_feats, make_committed_cell, train_cell, acc_matrix_metrics, CISTREAM_TASKS,
                   synth_stream, load_digits_split, linear_probe, race_bp, normalize, relu, EPS, jsonsafe,
                   nuisance_transform)
from p8lib import _onehot, _l2n                                        # noqa: E402
# all P8 guards (carried; run FIRST every rung)
from p8lib import (partial_fit_equiv_guard, live_path_anchor_guard, scff_static_frozen_guard,        # noqa: E402
                   meter_proxy_guard, detector_far_guard, cache_replay_guard, fd_budget_gate_guard)
from p6lib import (bulk_drift, NoiseModel, infer_noisy, NoiseAugContrast,                            # noqa: E402
                   label_free_axis, class_axis)
from p7lib import AUG, COMMITTED                                        # noqa: E402  (the frozen cell knobs: AUG in p7, COMMITTED in p6)

__all__ = [
    "make_lifelong_stream", "build_cache_p9", "probe_retention",
    "EMAView", "LLRDCell", "make_llrd_cell",
    "run_economy_p9", "StreamingLUT",
    "evict_cbrs", "evict_reservoir", "evict_recency", "evict_herding", "evict_dcbrs",
    "sleep_cost_at_depth", "loop_energy",
    "proto_reanchor", "slda_readside_refit", "residual_probe",
    "n2_readside_guard", "evict_equiv_guard",
    # carried P8 (re-export so run scripts import only p9lib)
    "run_economy", "make_drift_stream", "build_cache", "awake_sleep_loop", "make_stream_head",
    "make_committed_cell", "readout_feats", "all_tap_feats", "trunc_feats", "acc_matrix_metrics",
    "CISTREAM_TASKS", "synth_stream", "load_digits_split", "linear_probe", "race_bp",
    "class_balanced_reservoir", "continual_safety_heads", "calibrate_threshold",
    "sig_tap_drift_direction", "sig_tap_drift_magnitude", "sig_driftlens", "mtd_far", "meter_from_trace",
    "hardware_cost_meter", "bp_replay_energy", "bulk_drift", "NoiseModel", "infer_noisy", "jsonsafe", "EPS",
    "partial_fit_equiv_guard", "live_path_anchor_guard", "scff_static_frozen_guard", "meter_proxy_guard",
    "detector_far_guard", "cache_replay_guard", "fd_budget_gate_guard",
]


# ============================================================ the LIFELONG stream (P9.0 bench)
def make_lifelong_stream(Xtr, Ytr, Xte, Yte, tasks, seed, cfg, *, quick=False):
    """The long/repeating stream: P8's CI+nuisance schedule THEN `LIFE_CYCLES` re-visit cycles that rotate the batch
    emphasis across all seen classes (no new labels -> pure CONTINUED drift), so the 'does the bulk forget?' question
    is asked on ACCUMULATED drift. Re-uses make_drift_stream's segments, then appends revisit blocks + a denser probe
    grid + monitor eval points (all-task re-evals for the lifelong worst-BWT) + a held-out EARLY-TASK (task-0) eval
    set (the destruction curve's held-out data). Returns the P8 stream dict + {monitor_steps, probe_grid, Xearly,
    Yearly, early_task}."""
    base = make_drift_stream(Xtr, Ytr, Xte, Yte, tasks, seed, cfg, quick=quick)
    rng = np.random.default_rng(seed + 9090)
    C = cfg.NCLASS; B = cfg.BATCH
    q = 0.5 if quick else 1.0
    n_cycles = max(0, int(cfg.LIFE_CYCLES if not quick else 1))
    rev = max(4, int(cfg.LIFE_REVISIT * q))
    by_class = {c: np.where(Ytr == c)[0] for c in range(C)}
    allc = [c for tk in tasks for c in tk]

    def draw(classes, n):
        pool = np.concatenate([by_class[c] for c in classes])
        return rng.choice(pool, n, replace=len(pool) < n)

    # the P8 base runs warmup -> ... -> nuisance -> stat2. Insert the revisit cycles BEFORE the terminal nuisance so
    # the covariate-FAR probe stays at the end (calibration references intact). Rebuild the step list around it.
    steps = list(base["steps"])
    nuis_start = base["nuis_onset"]                                     # first nuisance step index in `steps`
    head_steps = steps[:nuis_start]                                    # everything up to (not incl.) nuisance
    tail_steps = steps[nuis_start:]                                    # nuisance + stat2 (kept terminal)

    # revisit cycles: rotate emphasis task-by-task over ALL classes (bursty, class-imbalanced arrival)
    revisit_steps = []
    monitor_local = []                                                 # positions (within head+revisit) to re-eval all tasks
    T = len(tasks)
    for cyc in range(n_cycles):
        for t in range(T):
            emph = tasks[t]
            for r in range(rev):
                n_emph = int(round(0.5 * B)); n_rest = B - n_emph
                idx = np.concatenate([draw(emph, n_emph), draw(allc, n_rest)])
                revisit_steps.append(dict(idx=idx, seg=f"revisit{cyc}.{t}", nuis=None, seen=T - 1))
            monitor_local.append(len(head_steps) + len(revisit_steps) - 1)   # re-eval all tasks at each block end

    new_steps = head_steps + revisit_steps + tail_steps
    shift = len(revisit_steps)                                         # tail indices shift by the inserted revisits

    # remap the terminal-segment markers (nuisance/stat2/settle interior) by the insert shift
    def _remap(lst):
        return [i + shift if i >= nuis_start else i for i in lst]
    real_onsets = base["real_onsets"]                                 # all before nuis_start -> unchanged
    nuisance_steps = _remap(base["nuisance_steps"])
    stationary_steps = _remap(base["stationary_steps"])
    calib_steps = _remap(base["calib_steps"])
    nuis_onset = base["nuis_onset"] + shift
    checkpoints = [(s, t) for (s, t) in base["checkpoints"]]           # cycle-0 CI boundaries (canonical acc-matrix)

    # held-out EARLY-TASK (task-0) eval for the destruction curve (Davari 2203.13381): never used to fit the bulk.
    early_task = 0
    m0 = np.isin(Yte, tasks[early_task]); ei = np.where(m0)[0]
    if len(ei) > cfg.EARLY_N:
        ei = rng.choice(ei, cfg.EARLY_N, replace=False)
    Xearly, Yearly = Xte[ei], Yte[ei]

    n_steps = len(new_steps)
    probe_grid = sorted(set(range(cfg.LIFE_PROBE_EVERY - 1, n_steps, cfg.LIFE_PROBE_EVERY))
                        | set(s for s, _ in checkpoints) | set(monitor_local))

    out = dict(base)
    out.update(steps=new_steps, n_steps=n_steps, real_onsets=real_onsets, nuis_onset=nuis_onset,
               nuisance_steps=nuisance_steps, stationary_steps=stationary_steps, calib_steps=calib_steps,
               checkpoints=checkpoints, monitor_steps=sorted(monitor_local), probe_grid=probe_grid,
               Xearly=Xearly, Yearly=Yearly, early_task=early_task, C=C, tasks=tasks)
    return out


# ============================================================ the P9 cache (reps_b/reps_probe/reps_early at grid)
def build_cache_p9(cell_factory, stream, seed, cfg, *, sleep_every=None, store_reps=True, quick=False):
    """build_cache extended for Phase 9. Runs the frozen-to-GD SCFF bulk forward-only through the stream ONCE
    (gate-independent) and caches, per step: the batch taps + labels (op(c) input) + the cumulative bulk_drift; and
    at PROBE-GRID steps: the per-layer PROBE reps (`reps_probe`, float32 -> P9.2 depth + P9.0 curves) + the per-layer
    EARLY-TASK reps (`reps_early`) + the all-tap phi_probe (P8-compatible sleep set). Optionally the per-layer BATCH
    reps (`reps_b`) so the awake read can be re-sliced at a deployed depth (P9.2). Returns the P8-cache fields + grid/
    monitor. Memory: reps stored float32, one seed at a time (the run layer never holds >1 cache)."""
    rng = np.random.default_rng(seed)
    dims = [cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH
    cell = cell_factory(dims, seed)
    Xtr, Ytr = stream["Xtr"], stream["Ytr"]
    Xpr, Ypr = stream["Xpr"], stream["Ypr"]
    Xearly, Yearly = stream.get("Xearly"), stream.get("Yearly")

    wu = stream["warmup_idx"]
    for s in range(0, len(wu), cfg.BATCH):
        xb = Xtr[wu[s:s + cfg.BATCH]]
        if len(xb) >= 4:
            cell.train_step(xb, rng)

    grid = set(stream.get("probe_grid") or [])
    if not grid:                                                       # fall back to the P8 sleep grid if no probe grid
        every = sleep_every or 4
        grid = set(P8._sleep_grid(stream["n_steps"], stream["checkpoints"], every))
    ckpt_steps = {s: t for s, t in stream["checkpoints"]}
    monitor = set(stream.get("monitor_steps") or [])

    def reps(X):
        return cell.infer(X)

    def alltap_from(R):
        return readout_feats(R, None)

    cache = dict(steps=[], sig=dict(), grid=sorted(grid), ckpt=ckpt_steps, monitor=sorted(monitor),
                 rng_fingerprint=[])
    ref_reps = cell.infer(Xpr)                                        # birth reference (cumulative bulk_drift)
    x_buf = []
    all_tasks_eval = {k: (alltap_from(reps(Xte_k)), Yte_k)            # for monitor all-task re-eval (built lazily below)
                      for k, (Xte_k, Yte_k) in stream["eval_by_task"].items()} if False else None

    for si, st in enumerate(stream["steps"]):
        xb = Xtr[st["idx"]].copy(); yb = Ytr[st["idx"]].copy()
        if st["nuis"] is not None:
            g, a = st["nuis"]; xb = nuisance_transform(xb, g, a)
        rb = None
        if len(xb) >= 4:
            rb = reps(xb)                                             # per-layer batch reps (pre-update read == op(c) input)
            cell.train_step(xb, rng)
        else:
            rb = reps(xb)
        cache["rng_fingerprint"].append(float(rng.random()))
        phi_b = alltap_from(rb)
        rec = dict(phi_b=phi_b, y_b=yb, seg=st["seg"]); x_buf.append(xb)
        if store_reps:
            rec["reps_b"] = [r.astype(np.float32) for r in rb]
        # the probe re-forward (bulk_drift + reps_probe) is only needed at GRID steps (the committed loop gates on
        # the head error-EMA, not the tap signal; the rotation curve reads grid reps) -> ~5x cheaper cache build.
        rec["_bd"] = np.nan
        if si in grid:
            reps_pr = cell.infer(Xpr)
            rec["_bd"] = float(bulk_drift(reps_pr, ref_reps).mean())
            rec["phi_probe"] = alltap_from(reps_pr); rec["y_probe"] = Ypr
            if store_reps:
                rec["reps_probe"] = [r.astype(np.float32) for r in reps_pr]
                if Xearly is not None:
                    rec["reps_early"] = [r.astype(np.float32) for r in cell.infer(Xearly)]
        if (si in ckpt_steps) or (si in monitor):
            tmax = ckpt_steps.get(si, len(stream["tasks"]) - 1)
            ev = {}; evr = {}
            for k, (Xk, Yk) in stream["eval_by_task"].items():
                if k <= tmax:
                    Rk = reps(Xk); ev[k] = (alltap_from(Rk), Yk)
                    if store_reps:
                        evr[k] = ([r.astype(np.float32) for r in Rk], Yk)
            rec["eval"] = ev
            if store_reps:
                rec["eval_reps"] = evr
            rec["eval_task"] = tmax
        cache["steps"].append(rec)

    # the trigger signals (identical construction to p8.build_cache) — MMD change-detector on post-norm taps
    n = len(cache["steps"]); W = max(2, int(cfg.WIN_W)); Dlag = max(2, int(cfg.WIN_LAG))
    PHI = [r["phi_b"] for r in cache["steps"]]; PHIN = [_l2n(p) for p in PHI]

    def _window(buf, si):
        return np.concatenate(buf[max(0, si - W + 1):si + 1], 0)
    cidx = stream.get("calib_steps") or list(range(W - 1, n))
    b_dir = P8._bandwidth(np.concatenate([PHIN[i] for i in cidx], 0))
    b_dl = P8._bandwidth(np.concatenate([PHI[i] for i in cidx], 0))
    b_mag = P8._bandwidth(np.concatenate([x_buf[i] for i in cidx], 0))
    tap_dir = np.zeros(n); driftlens = np.zeros(n); tap_mag = np.zeros(n)
    for si in range(n):
        j = max(W - 1, si - Dlag)
        tap_dir[si] = P8._mmd2(_window(PHIN, si), _window(PHIN, j), sig2=b_dir)
        driftlens[si] = P8._mmd2(_window(PHI, si), _window(PHI, j), sig2=b_dl)
        tap_mag[si] = P8._mmd2(_window(x_buf, si), _window(x_buf, j), sig2=b_mag)
    bd_series = np.array([r["_bd"] for r in cache["steps"]])          # NaN off-grid -> forward-fill for the viz curve
    last = 1.0
    for i in range(len(bd_series)):
        if np.isnan(bd_series[i]):
            bd_series[i] = last
        else:
            last = bd_series[i]
    cache["sig"] = dict(tap_dir=tap_dir, driftlens=driftlens, tap_mag=tap_mag, bulkdrift=bd_series)
    for r in cache["steps"]:
        r.pop("_bd", None)
    cache["stream"] = stream
    return cache


# ============================================================ P9.0 — the three-curve probe instrument
def _fit_ridge_W(F, Y, C, lam):
    """Fit a linear classifier by ridge (closed-form) and RETURN the weight matrix W [d+1, C] (linear_probe returns
    only accuracy, so it can't be frozen-then-reapplied — the B1 fix). Bias via an appended ones column."""
    Fb = np.hstack([F, np.ones((len(F), 1))])
    G = Fb.T @ Fb + lam * np.eye(Fb.shape[1])
    W = np.linalg.solve(G, Fb.T @ _onehot(Y, C))
    return W


def _score_W(W, F, Y):
    Fb = np.hstack([F, np.ones((len(F), 1))])
    return float((np.argmax(Fb @ W, 1) == Y).mean())


def probe_retention(cache, cfg, *, depth=None):
    """The THREE-curve P9.0 instrument (design §2.3, keyed on curve 3). Over the probe grid:
      (1) ROTATION  = mean-layer cos(reps_probe_t, reps_probe_birth) (== bulk_drift; basis-free).
      (2) STALENESS = a linear probe FIT ONCE at birth on the probe reps, re-applied to the current EARLY-TASK reps,
          scored on held-out task-0 data / its birth score (what a FIXED head loses -> what sleep exists to fix).
      (3) DESTRUCTION = an OPTIMAL linear probe RE-FIT on the CURRENT probe reps, scored on the SAME held-out task-0
          data / its birth score (rotation factored out -> the TRUE forgetting measure; 2203.13381). THE VERDICT CURVE.
    `depth`: None=all-tap, int k = trunc-K (score the curves at the deployed read depth). Returns dict of [K] arrays."""
    grid = [si for si in cache["grid"] if "reps_probe" in cache["steps"][si] and "reps_early" in cache["steps"][si]]
    C = cache["stream"]["C"]; Ypr = cache["steps"][grid[0]]["y_probe"]; Yearly = cache["stream"]["Yearly"]
    lam = cfg.PROBE_FIT_RIDGE

    def feats(reps):
        return readout_feats([r.astype(np.float64) for r in reps], depth)

    # birth references (first grid step)
    R0p = cache["steps"][grid[0]]["reps_probe"]; R0e = cache["steps"][grid[0]]["reps_early"]
    W_frozen = _fit_ridge_W(feats(R0p), Ypr, C, lam)                  # the fit-once probe (staleness)
    stale0 = _score_W(W_frozen, feats(R0e), Yearly)
    W_refit0 = _fit_ridge_W(feats(R0p), Ypr, C, lam)                  # the birth re-fit (destruction denom)
    destroy0 = _score_W(W_refit0, feats(R0e), Yearly)

    rot, stale, destroy, steps = [], [], [], []
    for si in grid:
        rec = cache["steps"][si]
        Rp = rec["reps_probe"]; Re = rec["reps_early"]
        rot.append(float(bulk_drift([r.astype(np.float64) for r in Rp],
                                    [r.astype(np.float64) for r in R0p]).mean()))
        stale.append(_score_W(W_frozen, feats(Re), Yearly) / (stale0 + EPS))
        W_t = _fit_ridge_W(feats(Rp), Ypr, C, lam)                    # RE-FIT on the current bulk
        destroy.append(_score_W(W_t, feats(Re), Yearly) / (destroy0 + EPS))
        steps.append(si)
    return dict(steps=np.array(steps), rotation=np.array(rot), staleness=np.array(stale),
                destruction=np.array(destroy), stale0=stale0, destroy0=destroy0)


# ============================================================ N2 arm 1 — EMA-view (read-side de-drift; the default)
class EMAView:
    """The N2 read-side view: a stateful EMA of the per-tap feature MEAN, subtracted (relative to birth) from the
    taps the NAMER reads. It removes the slow COHERENT translation of the tap cloud (the P6 directional enemy is a
    coherent translation) WITHOUT rotating class directions -> spine-clean (a magnitude/translation is removed, the
    class DIRECTION is preserved). SCFF is untouched (read-side). beta smaller = slower view. Off (beta None) ==
    identity -> the namer reads the raw taps == P8 bit-for-bit."""

    def __init__(self, beta=None):
        self.beta = beta; self.m = None; self.m0 = None

    def update(self, phi):
        if self.beta is None:
            return
        mu = phi.mean(0)
        if self.m is None:
            self.m = mu.copy(); self.m0 = mu.copy()
        else:
            self.m = (1.0 - self.beta) * self.m + self.beta * mu

    def transform(self, phi):
        if self.beta is None or self.m is None:
            return phi
        return phi - (self.m - self.m0)


# ============================================================ N2 arm 2 — LLRD-rate (flagged secondary)
class LLRDCell(NoiseAugContrast):
    """Layerwise-LR-decay cell: identical objective (masking, InfoNCE, tau/w/norm/sig_aug byte-identical), but the
    APPLIED update of the LATE-read layers is scaled by rho<1 (slows their training dynamics — 'rate-only' IFF the
    representation guard holds; if it moves the EARLY/MID taps it is a Stage-1 reopen). rho_l=1 for early/mid, rho for
    the last `late` layers. rho=1 everywhere == NoiseAugContrast bit-for-bit (the guard's first arm)."""

    def __init__(self, dims, *, rho=1.0, late=4, **kw):
        super().__init__(dims, **kw)
        self.rho_vec = np.ones(self.L)
        if late > 0 and rho != 1.0:
            self.rho_vec[self.L - late:] = float(rho)

    def train_step(self, Xb, rng, neg_partner=None):
        Wb = [W.copy() for W in self.W]; bb = [b.copy() for b in self.b]
        super().train_step(Xb, rng, neg_partner)                      # consumes rng identically to the base
        for l in range(self.L):
            self.W[l] = Wb[l] + self.rho_vec[l] * (self.W[l] - Wb[l])
            self.b[l] = bb[l] + self.rho_vec[l] * (self.b[l] - bb[l])


def make_llrd_cell(dims, seed, *, rho=1.0, late=4):
    return LLRDCell(dims, seed=seed, rho=rho, late=late, **AUG, **COMMITTED)


def read_drift(cache, *, n2_beta=None):
    """The scalar drift of the features the NAMER reads across the stream: mean over grid steps of
    1 - cos(probe-centroid_t, probe-centroid_{t+1}). With an EMA-view (n2_beta) the de-drifted probe centroid moves
    less -> lower drift -> the N2 lever's effect. On an LLRD cache (its own slower SCFF trajectory) the drift is
    lower with n2_beta=None. The P9.1 drift-reduction axis."""
    view = EMAView(n2_beta)
    cents = []
    for si, rec in enumerate(cache["steps"]):
        view.update(rec["phi_b"])
        if si in cache["grid"] and "phi_probe" in rec:
            cents.append(view.transform(rec["phi_probe"]).mean(0))
    cents = np.array(cents)
    d = [1.0 - float((cents[i] @ cents[i + 1]) / (np.linalg.norm(cents[i]) * np.linalg.norm(cents[i + 1]) + EPS))
         for i in range(len(cents) - 1)]
    return float(np.mean(d)) if d else 0.0


# ============================================================ P9.3 — the accumulating, evicting StreamingLUT
def evict_reservoir(store, cap, rng):
    """iid reservoir: keep a uniform random `cap` sample of the appended history."""
    if len(store["idx"]) <= cap:
        return store
    keep = rng.choice(len(store["idx"]), cap, replace=False)
    return _subset(store, keep)


def evict_recency(store, cap, rng):
    """FIFO/recency: keep exactly the last `cap` appended (the naive eviction; the finite-cap guard target)."""
    if len(store["idx"]) <= cap:
        return store
    keep = np.arange(len(store["idx"]) - cap, len(store["idx"]))
    return _subset(store, keep)


def evict_cbrs(store, cap, rng, C):
    """Class-balanced reservoir (Chrysakis & Moens ICML'20): keep prototypes balanced across classes -> spans the
    class DIRECTIONS, not the densest region (the committed policy — the spine at the buffer)."""
    F = store["feat"]; Y = store["lab"]
    if len(Y) <= cap:
        return store
    Fk, Yk, keep = _cbrs_indices(F, Y, C, cap, rng)
    return _subset(store, keep)


def evict_herding(store, cap, rng, C):
    """Herding (iCaRL): keep, per class, the prototypes NEAREST the class feature-MEAN — a MAGNITUDE/mean null. It
    keeps the dense center and drops the tails -> the class direction NARROWS (expected to re-import forgetting IFF
    the raw dense-center diverges from the direction span; else 'buffer-spine null here')."""
    F = store["feat"]; Y = store["lab"]
    if len(Y) <= cap:
        return store
    per = max(1, cap // max(1, C))
    keep = []
    for c in np.unique(Y):
        ci = np.where(Y == c)[0]
        mu = F[ci].mean(0)
        d = np.linalg.norm(F[ci] - mu, axis=1)
        keep.extend(ci[np.argsort(d)[:per]].tolist())
    keep = np.array(keep[:cap], int)
    return _subset(store, keep)


def evict_dcbrs(store, cap, rng, C):
    """D-CBRS (diversity refinement, 2207.05897): class-balanced, and WITHIN each class keep the most DIVERSE
    prototypes via a hand-rolled single-threaded farthest-point scorer (NOT sklearn K-means — the OpenMP phantom-hang
    on this box). Conditional (only if CBRS loses intra-class diversity)."""
    F = store["feat"]; Y = store["lab"]
    if len(Y) <= cap:
        return store
    per = max(1, cap // max(1, C))
    keep = []
    for c in np.unique(Y):
        ci = np.where(Y == c)[0]
        if len(ci) <= per:
            keep.extend(ci.tolist()); continue
        sel = [int(ci[0])]                                            # farthest-point sampling (single-threaded)
        cand = list(ci[1:])
        while len(sel) < per and cand:
            selF = F[sel]
            d = np.array([np.min(np.linalg.norm(selF - F[j], axis=1)) for j in cand])
            nxt = cand[int(np.argmax(d))]; sel.append(nxt); cand.remove(nxt)
        keep.extend(sel)
    keep = np.array(keep[:cap], int)
    return _subset(store, keep)


def _cbrs_indices(F, Y, C, cap, rng):
    """class_balanced_reservoir returns (F,Y) not indices; re-derive the kept indices by class-balanced subsampling
    (per-class cap/C, uniform within class) so the StreamingLUT can subset ALL its parallel arrays consistently."""
    per = max(1, cap // max(1, C)); keep = []
    for c in np.unique(Y):
        ci = np.where(Y == c)[0]
        if len(ci) <= per:
            keep.extend(ci.tolist())
        else:
            keep.extend(ci[rng.choice(len(ci), per, replace=False)].tolist())
    keep = np.array(keep, int)
    if len(keep) > cap:
        keep = keep[rng.choice(len(keep), cap, replace=False)]
    return F[keep], Y[keep], keep


def _subset(store, keep):
    return dict(idx=store["idx"][keep], lab=store["lab"][keep], feat=store["feat"][keep],
                pid=store["pid"][keep])


class StreamingLUT:
    """The bounded, EVICTING prototype store P9.3 forces (P8 had only a fixed balanced probe — no growing history to
    bound). It APPENDS prototypes (raw-probe indices + their birth features + labels) as the stream runs (bursty,
    class-imbalanced arrival matched to the stream's class mix) and evicts by `policy` at the cap. At sleep it returns
    the kept prototypes' CURRENT (re-forwarded) features by indexing the current step's `phi_probe`. cap=inf ('oracle')
    keeps everything (the unbounded reference)."""

    def __init__(self, cap, policy, C, seed):
        self.cap = cap; self.policy = policy; self.C = C
        self.rng = np.random.default_rng(seed + 55)
        self.store = dict(idx=np.empty(0, int), lab=np.empty(0, int), feat=np.empty((0, 0)), pid=np.empty(0, int))
        self.n_appended = 0

    def append(self, probe_idx, feats, labels):
        """Append a batch of prototypes (probe_idx into Xpr, their current features, labels)."""
        if self.store["feat"].shape[1] == 0:
            self.store["feat"] = np.empty((0, feats.shape[1]))
        self.store["idx"] = np.concatenate([self.store["idx"], probe_idx])
        self.store["lab"] = np.concatenate([self.store["lab"], labels])
        self.store["feat"] = np.vstack([self.store["feat"], feats]) if len(self.store["feat"]) else feats.copy()
        self.store["pid"] = np.concatenate([self.store["pid"], probe_idx])
        self.n_appended += len(probe_idx)
        self._evict()

    def _evict(self):
        if np.isinf(self.cap) or len(self.store["idx"]) <= self.cap:
            return
        cap = int(self.cap); pol = self.policy
        if pol == "reservoir":
            self.store = evict_reservoir(self.store, cap, self.rng)
        elif pol == "recency":
            self.store = evict_recency(self.store, cap, self.rng)
        elif pol == "cbrs":
            self.store = evict_cbrs(self.store, cap, self.rng, self.C)
        elif pol == "herding":
            self.store = evict_herding(self.store, cap, self.rng, self.C)
        elif pol == "dcbrs":
            self.store = evict_dcbrs(self.store, cap, self.rng, self.C)
        else:                                                          # 'oracle' / unbounded
            return

    def sleep_set(self, phi_probe_now):
        """The kept prototypes' CURRENT features (re-forwarded) — index the current step's phi_probe by kept probe id."""
        pid = self.store["pid"]
        return phi_probe_now[pid], self.store["lab"]

    def __len__(self):
        return len(self.store["idx"])


# ============================================================ P9.2 — depth-aware sleep energy
def sleep_cost_at_depth(cfg, head_name, depth, n_sleep, probe_n, scff_dims):
    """The P9.2 sleep-cost axis = the namer's sleep RE-FIT energy that scales with the read depth's Fdim (the
    solve/Gram + write term). trunc re-slices the TOP of the full forward, so the SCFF re-forward MACs are UNCHANGED
    (reported apart, `reforward_e`); only the Fdim-scaled solve/Gram/write term saves (design C6). Returns dict."""
    L = len(scff_dims) - 1; W = scff_dims[1]
    Fdim = {"alltap": L * W, "truncK": cfg.SLEEP_TRUNC_K * W, "perdepth": W}[depth]   # perdepth = a SINGLE layer
    if head_name == "ranpac":
        Pp = cfg.RANPAC_KNOB["proj_dim"]
        solve_flop = (2.0 / 3.0) * Pp ** 3; gram_flop = probe_n * Pp * Pp; nwrite = Pp * cfg.NCLASS
        proj_mac = probe_n * (Fdim * Pp)                              # the projection depends on Fdim (P8.4 cost caveat)
    else:  # slda
        solve_flop = (2.0 / 3.0) * Fdim ** 3; gram_flop = probe_n * Fdim * Fdim; nwrite = Fdim * cfg.NCLASS
        proj_mac = 0.0
    e_solve = n_sleep * (solve_flop + gram_flop) * cfg.E_DIGITAL
    e_write = n_sleep * nwrite * cfg.E_WRITE
    e_proj = n_sleep * proj_mac * cfg.E_MAC
    # the SCFF re-forward at sleep (FULL depth — trunc re-slices the top, so this is unchanged across depths)
    layer_macs = scff_dims[0] * scff_dims[1] + sum(scff_dims[i] * scff_dims[i + 1] for i in range(1, L))
    layer_acts = sum(scff_dims[1:])
    reforward_e = n_sleep * probe_n * (layer_macs * cfg.E_MAC + layer_acts * cfg.E_ADC_STEP * cfg.ADC_BITS)
    refit_e = e_solve + e_write + e_proj
    return dict(Fdim=Fdim, refit_e=float(refit_e), reforward_e=float(reforward_e),
                sleep_cost=float(refit_e), full_sleep_e=float(refit_e + reforward_e))


def loop_energy(cfg, head_name, res, cache, *, substrate="analog"):
    """Full-loop metered energy for a run_economy_p9 result (reuses the P8 ADC-centred meter on the actual fire/sleep
    counts). Returns the meter dict incl. gdshare (the economy the P9 tuning must not inflate, <= 0.25)."""
    return meter_from_trace(cfg, head_name, cache, res, substrate=substrate)


# ============================================================ the P9 economy replay (P8 run_economy + the P9 hooks)
def run_economy_p9(cache, head_factory, cfg, *, gate="oracle", trigger="error", sleep_policy="checkpoint",
                   cadence_every=1, lam_ema=1.0, cbrs=False, detector_kw=None, ema_beta=None, sig_override=None,
                   n2_view=None, sleep_depth="alltap", lut=None, reanchor_fn=None):
    """run_economy + the Phase-9 hooks. ALL hooks off (n2_view None, sleep_depth 'alltap', lut None, reanchor None)
    == p8.run_economy bit-for-bit on a P8 cache (n2_readside_guard). Hooks:
      * n2_view (EMAView): the read-side de-drift applied to EVERY feature the head reads (awake phi, sleep set, eval).
      * sleep_depth: 'alltap' (P8) / 'truncK' / 'perdepth' — the DEPLOYED read depth (awake + sleep both re-slice
        reps_b/reps_probe; requires a build_cache_p9 cache).
      * lut (StreamingLUT): replaces the fixed-probe sleep set with a bounded, evicting store (P9.3).
      * reanchor_fn(rec): returns (F_sleep, Y_sleep) for the read-side residual defense (P9.4) — overrides the sleep set.
    Adds a LIFELONG worst-BWT tracker (min over ALL eval/monitor points of acc_now[k]-first_learned_acc[k])."""
    steps = cache["steps"]; stream = cache["stream"]; C = stream["C"]; T = len(stream["tasks"])
    ema_beta = cfg.EMA_BETA if ema_beta is None else ema_beta
    head = head_factory()
    fires = np.zeros(len(steps), bool); sleeps = np.zeros(len(steps), bool)
    energy_trace = []
    det = make_detector(gate, cfg, **(detector_kw or {})) if gate in ("abs", "ddm", "adwin") else None
    sig = sig_override
    thr = calibrate_threshold(sig, stream["stationary_steps"]) if sig is not None else None
    ckpt = cache["ckpt"]; monitor = set(cache.get("monitor", []))
    checkpoint_steps = set(s for s, _ in stream["checkpoints"])
    oracle_fire = set(i for i, st in enumerate(stream["steps"]) if st["seg"].startswith("onset"))
    grid_seen = 0
    is_alltap = (sleep_depth == "alltap")

    def _slice(reps):
        """The DEPLOYED read depth applied to a per-layer rep list: all-tap (all L) / trunc-K (last K) / per-depth
        (a SINGLE layer — the last one; distinct from trunc-K)."""
        R64 = [r.astype(np.float64) for r in reps]
        if sleep_depth == "truncK":
            return readout_feats(R64, cfg.SLEEP_TRUNC_K)
        if sleep_depth == "perdepth":
            return readout_feats([R64[-1]], None)
        return readout_feats(R64, None)

    amat = [[0.0] * T for _ in range(T)]
    worst_bwt = 0.0; first_acc = {}                                   # lifelong per-task first-learned baseline
    last_eval = {}                                                    # per-task acc at the final eval (lifelong AA)
    err_ema = 0.0; fitted = False; err_trace = []

    def _eval_feats(rec):
        """The per-task eval features at the DEPLOYED read depth: all-tap uses the cached float64 eval (P8 bit-for-bit
        on the guard); a truncated depth re-slices the cached per-layer eval_reps."""
        if is_alltap:
            return rec["eval"]
        return {k: (_slice(Rk), Yk) for k, (Rk, Yk) in rec["eval_reps"].items()}

    def _phi_read(rec):
        """The features the namer READS (awake fit/predict) at the deployed depth. all-tap prefers the cached
        float64 phi_b (so the N2-off path is P8 bit-for-bit); a truncated depth re-slices the per-layer reps_b."""
        if is_alltap:
            return rec["phi_b"] if "phi_b" in rec else _slice(rec["reps_b"])
        return _slice(rec["reps_b"])

    def _phi_eval(F):
        return n2_view.transform(F) if n2_view is not None else F

    def _sleep_set(rec, si, phi_probe_now):
        if reanchor_fn is not None:
            Fp, Yp = reanchor_fn(rec)
        elif lut is not None:
            Fp, Yp = lut.sleep_set(phi_probe_now)
        else:
            Fp, Yp = phi_probe_now, rec["y_probe"]
            if cbrs:
                Fp, Yp = class_balanced_reservoir(Fp, Yp, C, cfg.CBRS_CAP, np.random.default_rng(2000 + si))
        if n2_view is not None:
            Fp = n2_view.transform(Fp)
        return Fp, Yp

    def _probe_now(rec):
        if is_alltap:
            return rec["phi_probe"] if "phi_probe" in rec and "reps_probe" not in rec else (
                _slice(rec["reps_probe"]) if "reps_probe" in rec else rec.get("phi_probe"))
        return _slice(rec["reps_probe"])

    for si, rec in enumerate(steps):
        phi_raw = _phi_read(rec); y_b = rec["y_b"]
        if n2_view is not None:
            n2_view.update(phi_raw)
        phi_b = _phi_eval(phi_raw)
        e_op = dict(step=si, fire=False, sleep=False, Fdim=phi_b.shape[1], B=len(phi_b),
                    probe_n=(rec["phi_probe"].shape[0] if "phi_probe" in rec else 0))
        err_trace.append(1.0 - float((head.predict(phi_b) == y_b).mean()) if head.W is not None else np.nan)

        # append to the streaming LUT (P9.3): the batch's prototypes arrive as the stream runs (bursty/imbalanced).
        if lut is not None and "phi_probe" in rec:
            _lut_append(lut, rec, si, _probe_now(rec))

        # op(c): the awake fire
        if gate == "always":
            fire = True
        elif gate == "oracle":
            fire = si in oracle_fire
        elif not fitted:
            fire = True
        elif det is not None:
            err = 1.0 - float((head.predict(phi_b) == y_b).mean())
            if trigger == "error_ema":
                err_ema = (1 - ema_beta) * err_ema + ema_beta * err; fire = det.update(err_ema)
            else:
                fire = det.update(err)
        elif sig is not None:
            fire = bool(sig[si] > thr)
        else:
            fire = False
        if fire:
            head.partial_fit(phi_b, y_b, lam_ema=lam_ema); fitted = True
            fires[si] = True; e_op["fire"] = True

        is_grid = si in cache["grid"]
        if is_grid:
            grid_seen += 1
        will_sleep = (si in checkpoint_steps) if sleep_policy == "checkpoint" else (
            is_grid and (grid_seen % max(1, cadence_every) == 0))

        do_eval = ("eval" in rec)
        if do_eval:
            t_row = min(ckpt.get(si, rec.get("eval_task", T - 1)), T - 1)
            if not fitted:
                head.partial_fit(phi_b, y_b, lam_ema=lam_ema); fitted = True
            efeats = _eval_feats(rec)
            for k, (Fk, Yk) in efeats.items():                       # PRE-sleep: the awake gate's worst point
                acc = float((head.predict(_phi_eval(Fk)) == Yk).mean())
                if k not in first_acc:
                    first_acc[k] = acc
                worst_bwt = min(worst_bwt, acc - first_acc[k])

        if will_sleep and "phi_probe" in rec:
            Fp, Yp = _sleep_set(rec, si, _probe_now(rec))
            if len(Fp) >= C:
                head.sleep_fit(Fp, Yp); sleeps[si] = True; e_op["sleep"] = True; fitted = True

        if do_eval:                                                   # POST-sleep canonical matrix (AA) + lifelong AA
            efeats = _eval_feats(rec)
            for k, (Fk, Yk) in efeats.items():
                a_post = float((head.predict(_phi_eval(Fk)) == Yk).mean()) if head.W is not None else 0.0
                amat[t_row][k] = a_post; last_eval[k] = a_post
        energy_trace.append(e_op)

    aa_canon, bwt, forget = acc_matrix_metrics(amat)
    aa_life = float(np.mean(list(last_eval.values()))) if last_eval else aa_canon
    aa = aa_life if monitor else aa_canon
    # plasticity = mean first-learned acc over the LATER tasks (1..T-1) — the newest-task acc right after arrival
    plast = float(np.mean([first_acc[k] for k in first_acc if k >= 1])) if any(k >= 1 for k in first_acc) else \
        (float(np.mean(list(first_acc.values()))) if first_acc else 0.0)
    return dict(aa=aa, aa_canon=aa_canon, aa_life=aa_life, bwt=bwt, forget=forget, matrix=amat,
                worst_bwt=float(worst_bwt), plasticity=plast, first_acc=first_acc,
                fires=fires, sleeps=sleeps, firefrac=float(fires.mean()), nsleep=int(sleeps.sum()),
                energy_trace=energy_trace, err_trace=np.array(err_trace, float),
                lut_size=(len(lut) if lut is not None else 0),
                lut_appended=(lut.n_appended if lut is not None else 0))


def _lut_append(lut, rec, si, phi_probe):
    """Append the CURRENT step's prototypes to the streaming LUT: sample probe indices matching the batch's class mix
    (bursty arrival), with their current re-forwarded features (phi_probe at this grid step, already at the read depth)."""
    y_b = rec["y_b"]; y_probe = rec["y_probe"]
    rng = np.random.default_rng(3000 + si)
    take = []
    for c in np.unique(y_b):                                          # arrival mirrors the batch's classes (bursty)
        pc = np.where(y_probe == c)[0]
        if len(pc):
            take.extend(rng.choice(pc, min(len(pc), int((y_b == c).sum())), replace=False).tolist())
    if not take:
        return
    take = np.array(take, int)
    lut.append(take, phi_probe[take], y_probe[take])


# ============================================================ P9.4 — read-side residual (conditional)
def residual_probe(cell, cache_stream, cfg, seed, *, defended=None):
    """The earn-its-place gate + the read-side defense (design §2.3 P9.4). Injects the Phase-6 INPUT-TRANSDUCER
    DIRECTIONAL residual + sub-3-bit ADC (p6lib.NoiseModel — the channel SCFF's per-sample norm CANNOT remove
    forward-only; NOT p8's layernorm-invariant nuisance). Measures the committed SLDA loop's directional retention:
    undefended vs `defended` ∈ {None, 'proto_reanchor', 'slda_refit'}. Returns retention ratios."""
    # (implemented in the P9.4 run script against the built cell — this stub documents the contract; the run script
    #  builds the residual eval directly via infer_noisy on the committed cell.)
    raise NotImplementedError("residual_probe is realized inline in run_p9_4.py (needs the live cell + NoiseModel)")


def proto_reanchor(cell, Xpr, Ypr, channel, nm, rng, *, input_axis=None, depth=None):
    """P9.4 PRIMARY defense: re-forward the raw LUT prototypes through the CURRENT bulk UNDER THE SHIFT -> drift-free,
    shift-CONSISTENT prototypes (the plan's own sleep mechanism = test-time prototype shift, 2403.12952; no covariance
    estimate). Returns (F_sleep, Y_sleep) at the read depth, consistent with the shifted eval reads."""
    reps = infer_noisy(cell, Xpr, channel, nm, rng, input_axis=input_axis)
    return readout_feats(reps, depth), Ypr


def slda_readside_refit(head, F_shift, Y, *, shrinkage=None):
    """P9.4 FALLBACK defense: re-estimate the SLDA class means / shared covariance on the SHIFTED read (feature-level,
    scalar TS is ineffective under shift — D4). Shrinkage/min-count guarded (SLDA covariance is unstable under bursty
    few-shot classes — A2)."""
    head.reset_stats().partial_fit(F_shift, Y, lam_ema=1.0)
    return head


# ============================================================ guards (run FIRST — any fails -> STOP)
def n2_readside_guard(cfg, *, seed=42, verbose=True):
    """The N2 organ's guard (design §6 / red-team B2):
      (a) run_economy_p9 with ALL hooks OFF == p8.run_economy bit-for-bit on a P8 cache (the new organ reduces to the
          tested primitive);
      (b) EMA-view leaves the SCFF cell untouched (read-side — asserted by construction: EMAView never touches cell.W);
      (c) LLRD-rate rho=1 == NoiseAugContrast bit-for-bit, AND at rho<1 the EARLY/MID-layer taps are UNMOVED (only the
          late-read layers slowed) — else a Stage-1-reopen FLAG (not a silent adopt)."""
    Xtr, Ytr, Xte, Yte = synth_stream(1500, 700, cfg.OVERLAP, seed, dim=cfg.DIM, n_class=cfg.NCLASS, n_clusters=cfg.NCLUST)
    stream = make_drift_stream(Xtr, Ytr, Xte, Yte, cfg.TASKS, seed, cfg, quick=True)
    cache = build_cache(make_committed_cell, stream, seed, cfg, quick=True)                # a P8 cache (no reps_b)
    hf = lambda: make_stream_head("slda", cfg.NCLASS, seed=seed, **cfg.SLDA_KNOB)
    r_p8 = run_economy(cache, hf, cfg, gate="ddm", trigger="error_ema", sleep_policy="grid", cadence_every=2)
    r_p9 = run_economy_p9(cache, hf, cfg, gate="ddm", trigger="error_ema", sleep_policy="grid", cadence_every=2)
    dmat = max(abs(r_p8["matrix"][i][k] - r_p9["matrix"][i][k]) for i in range(len(cfg.TASKS)) for k in range(len(cfg.TASKS)))
    dfire = int(np.abs(r_p8["fires"].astype(int) - r_p9["fires"].astype(int)).sum())
    a_ok = (dmat < 1e-12) and (dfire == 0)

    # LLRD representation check: rho=1 bit-for-bit; rho<1 -> early/mid taps unmoved, late taps moved
    dims = [cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH
    rng = np.random.default_rng(seed)
    Xb = Xtr[:64]
    c_ref = make_committed_cell(dims, seed); c_r1 = make_llrd_cell(dims, seed, rho=1.0, late=cfg.N2_LATE_LAYERS)
    for _ in range(6):
        rr = np.random.default_rng(seed + 100); c_ref.train_step(Xb, np.random.default_rng(seed + 100))
    # re-run deterministically in lockstep
    c_ref = make_committed_cell(dims, seed); c_r1 = make_llrd_cell(dims, seed, rho=1.0, late=cfg.N2_LATE_LAYERS)
    c_rlo = make_llrd_cell(dims, seed, rho=cfg.N2_LLRD_RHOS[0], late=cfg.N2_LATE_LAYERS)
    for _ in range(8):
        c_ref.train_step(Xb, np.random.default_rng(seed + 7))
        c_r1.train_step(Xb, np.random.default_rng(seed + 7))
        c_rlo.train_step(Xb, np.random.default_rng(seed + 7))
    d_rho1 = max(float(np.abs(c_ref.W[l] - c_r1.W[l]).max()) for l in range(c_ref.L))
    late0 = c_ref.L - cfg.N2_LATE_LAYERS
    early_move = max(float(np.abs(c_ref.W[l] - c_rlo.W[l]).max()) for l in range(late0))
    late_move = max(float(np.abs(c_ref.W[l] - c_rlo.W[l]).max()) for l in range(late0, c_ref.L))
    b_ok = d_rho1 < 1e-12
    early_clean = early_move < 1e-9                                   # early/mid taps unmoved -> rate-only honest
    if verbose:
        print(f"  [n2_readside] (a) p9==p8 max|dmat|={dmat:.2e} fire-diff={dfire}  "
              f"{'OK' if a_ok else '!! N2-OFF DIVERGES FROM P8'}", flush=True)
        print(f"  [n2_readside] (c) LLRD rho=1 max|dW|={d_rho1:.2e} {'OK' if b_ok else '!! rho=1 NOT bit-for-bit'} | "
              f"rho<1 early/mid move={early_move:.2e} late move={late_move:.2e}  "
              f"{'early CLEAN (rate-only)' if early_clean else 'EARLY TAPS MOVE -> Stage-1-reopen FLAG'}", flush=True)
    return (a_ok and b_ok), dict(dmat=dmat, dfire=dfire, d_rho1=d_rho1, early_move=early_move,
                                 late_move=late_move, early_clean=bool(early_clean))


def evict_equiv_guard(cfg, *, seed=0, verbose=True):
    """The StreamingLUT organ's guard (design §6 / red-team B3+C5). The design's 'cap=inf == block-mode full-history
    bit-for-bit' is INFEASIBLE in the cache-replay paradigm (block-mode buffers Xtr samples; the streaming LUT indexes
    the Xpr probe pool — different sample pools), so the machinery is pinned by TWO EXACT invariants instead:
      (a) cap=inf retains EVERY appended prototype (no eviction — the unbounded reference is faithful);
      (b) StreamingLUT(cap=k, policy=recency) holds EXACTLY the last-k appended (a deterministic FIFO-contents check ->
          the eviction machinery is verified live, not only at the degenerate cap=inf)."""
    C = cfg.NCLASS; rng = np.random.default_rng(seed)
    d = 32; nap = 20; bs = 7
    lut_inf = StreamingLUT(np.inf, "oracle", C, seed)
    lut_k = StreamingLUT(30, "recency", C, seed)
    log_idx = []
    for a in range(nap):
        pid = rng.integers(0, 600, bs); feats = rng.standard_normal((bs, d)); lab = rng.integers(0, C, bs)
        lut_inf.append(pid, feats, lab); lut_k.append(pid, feats, lab)
        log_idx.extend(pid.tolist())
    a_ok = (len(lut_inf) == nap * bs) and (lut_inf.n_appended == nap * bs)
    last_k = np.array(log_idx[-30:])
    b_ok = (len(lut_k) == 30) and bool(np.array_equal(lut_k.store["pid"], last_k))
    if verbose:
        print(f"  [evict_equiv] (a) cap=inf kept={len(lut_inf)}/{nap*bs} appended={lut_inf.n_appended}  "
              f"{'OK' if a_ok else '!! cap=inf EVICTS'}", flush=True)
        print(f"  [evict_equiv] (b) cap=30 recency == last-30 FIFO contents  "
              f"{'OK' if b_ok else '!! FIFO CONTENTS WRONG'}", flush=True)
    return (a_ok and b_ok), dict(inf_kept=len(lut_inf), k_kept=len(lut_k))
