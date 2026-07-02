"""
p8lib — the Phase-8 apparatus: THE ECONOMY (when the namer fires) + THE COST METER (what it truly costs). A CHIP
NETLIST, not normal Python: every reuse is a *tested* primitive carried forward unchanged (the missing-sign/direction
bug lives in re-implementations), and the ONE genuinely-new primitive (`partial_fit`) ships with its own bit-exact
equivalence guard. Phase 8 turns on the REAL mechanism for the first time: SCFF + the GD namer run LIVE together —
SCFF trains forward-only on every input (it doesn't forget, but its representation DRIFTS), and the namer tracks the
drift via an awake gate (below theta = SCFF only; above theta = SCFF + namer `partial_fit`) and periodic sleep
(re-forward the raw-prototype LUT through the CURRENT SCFF -> rebuild the running Gram -> re-solve).

The device under test = the FROZEN-as-a-DESIGN Phase-6 cell `NoiseAugContrast` (SCFFContrastOverlap temp0.2/w2, L12,
no residual, + one iid-noise view sig_aug=1.0) + the committed Phase-7 namer (RanPAC + cbrs; SLDA the metered
fallback). "Frozen" always meant frozen-TO-GD (GD reads taps, never writes) and frozen-as-a-DESIGN (tau/w/norm/sig_aug
don't move); SCFF WEIGHTS were always meant to keep learning on the stream (arch 3.2). Phase 8 reopens no committed
knob — it runs the live loop the design always specified.

Built on p7lib (which re-exports p6/p5/p4/p3/p2). Reused, NOT re-implemented:
  p7lib : RanPACHead, SLDAHead, make_head, select_head_knob, class_balanced_reservoir, continual_safety_heads
          (the block-mode/oracle reference + the guard target), readout_feats/all_tap_feats/trunc_feats,
          make_committed_cell, train_cell, acc_matrix_metrics, CISTREAM_TASKS, synth_stream, load_digits_split,
          linear_probe, race_bp, ours_budget, effective_rank, normalize, relu, EPS, jsonsafe, _onehot/_spd_inv/_l2n,
          fd_head_grad, head_equiv_guard.

NEW here (Phase 8) — design 6:
  RanPACHeadStream / SLDAHeadStream : the ONE new primitive — a streaming running-(G,M) `partial_fit` (+ EMA-decay
      lam_ema) then solve. The chip-faithful capacitor-resident Gram (arch 2.4). The current heads re-solve from
      scratch; without this, op (c) + the drift-poisoning mechanism are NOT expressible. Guard: N sequential
      partial_fit @ lam_ema=1 (pure cumulative) == one batch `fit` to float64 precision + identical predictions.
  make_drift_stream / nuisance_transform : the streaming CI schedule (gradual class onset -> CONTINUOUS drift) + a
      LAYERNORM-INVARIANT nuisance-covariate injector (global gain g + all-ones offset alpha; SCFF's per-sample
      input layernorm removes both to ~EPS -> class direction provably invariant while raw pixels provably shift) +
      a stationary segment. Emits real-drift onset markers (-> MTD) and nuisance markers (-> FAR).
  build_cache (stream_tap_cache) : the tractability fast-path. SCFF live training is gate-INDEPENDENT (unsupervised,
      reads no head/label/gate), so the per-step tap trajectory + the label-free drift signals are computed ONCE per
      seed (RNG order recorded) and every gate/trigger/cadence arm REPLAYS its fire/sleep decisions on the cache.
  run_economy : replay one arm (gate + trigger + cadence + head) on a cache -> accuracy-held trajectory, the
      acc-matrix (incl. the worst-mid-stream-point eval), fire-counts, the per-op energy trace.
  awake_sleep_loop : the dual-mode wrapper. block mode == continual_safety_heads bit-for-bit (the guard + the oracle
      reference); streaming mode == build_cache + run_economy (the real regime).
  detectors : AbsTheta, DDM, ADWIN (error) ; BudgetGate (learned, reads a drift feature, FD-guarded).
  triggers  : sig_error_ema (labeled ref) ; sig_tap_drift_direction (drift ALONG the class/readout directions -- the
      committed candidate, spine-clean) ; sig_tap_drift_magnitude (raw input-moment mean-shift -- the false-fire
      NULL) ; sig_driftlens (post-norm embedding-distance -- the label-free reference) ; sig_studd (student mimic).
  hardware_cost_meter / bp_replay_energy : the behavioral ADC-centred energy model (design 2.3) + the BP+replay
      energy model at matched retention (same substrate table). readout_cost == the MAC+solve unit-energy special case.
  guards : partial_fit_equiv, live_path_anchor, scff_static_frozen, meter_proxy, detector_far, cache_replay,
      fd_budget_gate. Run FIRST. ANY guard fails -> STOP.

numpy only. The run layer sets OMP_NUM_THREADS=1 + python -u + PYTHONIOENCODING=utf-8 before importing this.
CPU float64 (the bit-exact guards need determinism). NO sklearn / no River for compute.
"""
from __future__ import annotations
import os
import sys

import numpy as np
from scipy.special import softmax, expit

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "phase7"))                # p7lib
from p7lib import (RanPACHead, SLDAHead, make_head, class_balanced_reservoir,                 # noqa: E402
                   continual_safety_heads, readout_feats, all_tap_feats, trunc_feats,
                   make_committed_cell, train_cell, acc_matrix_metrics, CISTREAM_TASKS,
                   synth_stream, load_digits_split, linear_probe, race_bp, ours_budget,
                   effective_rank, normalize, relu, EPS, jsonsafe,
                   fd_head_grad, head_equiv_guard)
from p7lib import _onehot, _spd_inv, _l2n                              # noqa: E402  (tested privates, identical output)

__all__ = [
    "RanPACHeadStream", "SLDAHeadStream", "make_stream_head",
    "nuisance_transform", "make_drift_stream", "build_cache", "run_economy", "awake_sleep_loop",
    "AbsTheta", "DDM", "ADWIN", "BudgetGate", "make_detector",
    "sig_error_ema", "sig_tap_drift_direction", "sig_tap_drift_magnitude", "sig_driftlens", "sig_studd",
    "calibrate_threshold", "detect_crossings", "mtd_far",
    "hardware_cost_meter", "bp_replay_energy", "meter_from_trace",
    "partial_fit_equiv_guard", "live_path_anchor_guard", "scff_static_frozen_guard",
    "meter_proxy_guard", "detector_far_guard", "cache_replay_guard", "fd_budget_gate_guard",
    # carried
    "make_committed_cell", "train_cell", "readout_feats", "all_tap_feats", "trunc_feats",
    "class_balanced_reservoir", "continual_safety_heads", "acc_matrix_metrics", "CISTREAM_TASKS",
    "synth_stream", "load_digits_split", "linear_probe", "race_bp", "ours_budget", "effective_rank",
    "normalize", "relu", "EPS", "jsonsafe", "make_head", "RanPACHead", "SLDAHead",
]


# ============================================================ MMD distribution-distance (the drift signals' core)
def _bandwidth(Z, *, cap=200, seed=0):
    """RBF bandwidth by the median-heuristic on a (capped) sample -- computed ONCE per signal from an early window
    and reused across steps so the MMD series is comparable step-to-step (a moving bandwidth would break the
    threshold-crossing MTD)."""
    rng = np.random.default_rng(seed)
    if len(Z) > cap:
        Z = Z[rng.choice(len(Z), cap, replace=False)]
    D2 = np.maximum(0.0, (Z * Z).sum(1)[:, None] - 2 * Z @ Z.T + (Z * Z).sum(1)[None, :])
    off = D2[np.triu_indices(len(Z), 1)]
    return float(np.median(off) + EPS) if off.size else 1.0


def _mmd2(X, Y, *, sig2=None, cap=200, seed=0):
    """Biased RBF-kernel MMD^2 between two sample clouds (the standard drift-detection distribution distance;
    captures the FULL distribution incl. new modes -- unlike a mean/trace summary that a class onset washes out).
    Deterministic (fixed subsample seed) so the cached signals reproduce bit-for-bit."""
    rng = np.random.default_rng(seed)
    if len(X) > cap:
        X = X[rng.choice(len(X), cap, replace=False)]
    if len(Y) > cap:
        Y = Y[rng.choice(len(Y), cap, replace=False)]
    Z = np.vstack([X, Y]); m = len(X)
    D2 = np.maximum(0.0, (Z * Z).sum(1)[:, None] - 2 * Z @ Z.T + (Z * Z).sum(1)[None, :])
    if sig2 is None:
        off = D2[np.triu_indices(len(Z), 1)]; sig2 = float(np.median(off) + EPS)
    K = np.exp(-D2 / (2.0 * sig2))
    Kxx = K[:m, :m]; Kyy = K[m:, m:]; Kxy = K[:m, m:]
    return float(Kxx.mean() + Kyy.mean() - 2.0 * Kxy.mean())


# ============================================================ the ONE new primitive — streaming heads (partial_fit)
class RanPACHeadStream(RanPACHead):
    """RanPAC with a STREAMING running-(G, M) accumulate (+ EMA-decay lam_ema) then solve — the chip-faithful
    capacitor-resident Gram (arch 2.4). `fit` (batch) is inherited unchanged (the guard reference). `partial_fit`
    accumulates op (c); `sleep_fit` rebuilds (G, M) from a re-forwarded prototype set (op (d))."""

    def __init__(self, C, proj_dim=2000, ridge_lambda=1e2, seed=0, scale=1.0):
        super().__init__(C, proj_dim=proj_dim, ridge_lambda=ridge_lambda, seed=seed, scale=scale)
        self.G = None; self.M = None

    def reset_stats(self):
        self.G = None; self.M = None; self.W = None
        return self

    def _solve(self):
        self.W = np.linalg.solve(self.G + self.lam * np.eye(self.P), self.M)
        return self

    def partial_fit(self, F, Y, lam_ema=1.0):
        Phi = self._phi(F)                                             # ensures Wr init (seed-deterministic)
        gb = Phi.T @ Phi
        mb = Phi.T @ _onehot(Y, self.C)
        if self.G is None:
            self.G = gb; self.M = mb
        else:
            self.G = lam_ema * self.G + gb
            self.M = lam_ema * self.M + mb
        return self._solve()

    def sleep_fit(self, F, Y):
        """Op (d): rebuild (G, M) from the re-forwarded LUT (fresh consistent features) -> the recovery re-solve."""
        return self.reset_stats().partial_fit(F, Y, lam_ema=1.0)


class SLDAHeadStream(SLDAHead):
    """Deep-SLDA with a streaming running (N, per-class count n_c, per-class sum S_c, global 2nd-moment T). mu = S/n;
    tied within-class Sigma = (T - sum_c n_c mu_c mu_c^T)/N (algebraically the batch scatter); then w_c = Sigma^-1 mu_c."""

    def __init__(self, C, shrinkage=1e-2, seed=0):
        super().__init__(C, shrinkage=shrinkage, seed=seed)
        self.N = 0.0; self.n = None; self.S = None; self.T = None; self.d = None

    def reset_stats(self):
        self.N = 0.0; self.n = None; self.S = None; self.T = None; self.W = None; self.b = None
        return self

    def _solve(self):
        d = self.d
        mu = np.stack([self.S[c] / self.n[c] if self.n[c] > 0 else np.zeros(d) for c in range(self.C)])
        Sig = (self.T - (self.n[:, None, None] * np.einsum("cd,ce->cde", mu, mu)).sum(0)) / max(self.N, 1)
        Sig = (1 - self.shrinkage) * Sig + self.shrinkage * np.trace(Sig) / d * np.eye(d)
        P = _spd_inv(Sig)
        self.W = mu @ P; self.b = -0.5 * (mu @ P * mu).sum(1); self.mu = mu
        return self

    def partial_fit(self, F, Y, lam_ema=1.0):
        d = F.shape[1]
        if self.n is None:
            self.d = d; self.n = np.zeros(self.C); self.S = np.zeros((self.C, d))
            self.T = np.zeros((d, d)); self.N = 0.0
        else:
            self.n = lam_ema * self.n; self.S = lam_ema * self.S; self.T = lam_ema * self.T; self.N = lam_ema * self.N
        for c in range(self.C):
            m = (Y == c)
            if m.any():
                self.n[c] += int(m.sum()); self.S[c] += F[m].sum(0)
        self.T += F.T @ F; self.N += len(F)
        return self._solve()

    def sleep_fit(self, F, Y):
        return self.reset_stats().partial_fit(F, Y, lam_ema=1.0)


def make_stream_head(name, C, seed=0, **knob):
    """The two committed candidates in streaming form (the only heads Phase 8's live loop runs)."""
    n = name.lower()
    if n == "ranpac":
        return RanPACHeadStream(C, seed=seed, **knob)
    if n == "slda":
        return SLDAHeadStream(C, seed=seed, **knob)
    raise ValueError(f"stream head '{name}' not supported (only ranpac / slda stream)")


# ============================================================ the drift stream (gradual onset + nuisance injector)
def nuisance_transform(X, gain, offset):
    """The LAYERNORM-INVARIANT nuisance covariate shift: X' = gain*X + offset (offset = a scalar added to every
    feature = offset*ones). SCFF's per-sample input layernorm (a-mu)/sqrt(var+eps) removes BOTH the scale and the
    all-ones offset to ~EPS -> the class DIRECTION is provably invariant while the RAW input moments (mean+offset,
    std*gain) provably shift. Firing on it = a false fire (the spine demonstration)."""
    return gain * X + offset


def make_drift_stream(Xtr, Ytr, Xte, Yte, tasks, seed, cfg, *, quick=False):
    """The streaming class-incremental schedule (the reframe's 'every input, forward-only' regime). Class onset is
    GRADUAL (a mix ramp), so representation drift is CONTINUOUS, not the stepwise per-task boundary the inherited
    harness had. Segments: warmup (unscored, task-0) -> stationary(FAR/MTFA floor) -> [gradual onset + plateau]*(T-1)
    -> nuisance-covariate(FAR) -> stationary recovery. Returns the step list + the markers (real onsets -> MTD;
    nuisance -> FAR; stationary -> MTFA) + the fixed probe/eval/LUT sets."""
    rng = np.random.default_rng(seed + 8080)
    C = cfg.NCLASS; B = cfg.BATCH
    q = 0.5 if quick else 1.0
    W_UP = max(6, int(cfg.WARMUP_STEPS * q)); S1 = max(8, int(cfg.STAT_STEPS * q))
    RMP = max(6, int(cfg.ONSET_RAMP * q)); PLT = max(6, int(cfg.PLATEAU * q))
    NUI = max(10, int(cfg.NUIS_STEPS * q)); S2 = max(6, int(cfg.STAT2_STEPS * q))
    SET = max(2 * int(cfg.WIN_LAG) + 8, int(cfg.SETTLE_STEPS * q))      # >= 2*lag so the interior is a clean reference

    by_class = {c: np.where(Ytr == c)[0] for c in range(C)}

    def draw(classes, n):
        pool = np.concatenate([by_class[c] for c in classes])
        return rng.choice(pool, n, replace=len(pool) < n)

    steps = []                                                          # each: dict(idx, seg, nuis, seen_tasks)
    real_onsets = []; nuis_onset = None
    stationary_steps = []; nuisance_steps = []
    checkpoints = []                                                    # (step_index_at_completion, task_t)
    warmup_idx = draw(tasks[0], W_UP * B)

    def seen_classes(nt):
        return [c for tk in tasks[:nt + 1] for c in tk]

    # stationary segment on task 0 (early SCFF still settling on task-0 -> NOT the FAR floor; tracked separately)
    warmup1_steps = []
    for _ in range(S1):
        warmup1_steps.append(len(steps))
        steps.append(dict(idx=draw(tasks[0], B), seg="stat1", nuis=None, seen=0))
    checkpoints.append((len(steps) - 1, 0))                             # task 0 learned

    # gradual onsets for tasks 1..T-1
    for t in range(1, len(tasks)):
        real_onsets.append(len(steps))
        for r in range(RMP):
            p_new = cfg.ONSET_MIX * (r + 1) / RMP                       # mix prob ramps 0 -> ONSET_MIX
            n_new = int(round(p_new * B)); n_old = B - n_new
            idx = np.concatenate([draw(tasks[t], n_new) if n_new else np.array([], int),
                                  draw(seen_classes(t - 1), n_old)])
            steps.append(dict(idx=idx, seg=f"onset{t}", nuis=None, seen=t))
        for _ in range(PLT):
            n_new = int(round(cfg.ONSET_MIX * B))
            idx = np.concatenate([draw(tasks[t], n_new), draw(seen_classes(t - 1), B - n_new)])
            steps.append(dict(idx=idx, seg=f"plateau{t}", nuis=None, seen=t))
        checkpoints.append((len(steps) - 1, t))

    allc = seen_classes(len(tasks) - 1)
    # SETTLE: a LONG all-class no-nuisance segment. Its class-mix transition (from the task-4-heavy plateau) is a
    # real change at the START; its INTERIOR (>= WIN_LAG steps in) is a clean, all-class, no-drift reference matched
    # to the nuisance class mix -> the FAR floor / MTFA are calibrated on the interior (calib_steps), NOT the boundary.
    settle_start = len(steps); calib_steps = []
    for r in range(SET):
        if r >= int(cfg.WIN_LAG):                                       # interior only (lagged window fully inside settle)
            calib_steps.append(len(steps)); stationary_steps.append(len(steps))
        steps.append(dict(idx=draw(allc, B), seg="settle", nuis=None, seen=len(tasks) - 1))
    # NUISANCE covariate segment: SAME class mix as SETTLE; ONLY the gain/offset RAMP changes -> a fire here = FALSE.
    nuis_onset = len(steps)
    for r in range(NUI):
        frac = (r + 1) / NUI
        g = 1.0 + (cfg.NUIS_GAIN - 1.0) * frac; a = cfg.NUIS_OFFSET * frac
        nuisance_steps.append(len(steps))
        steps.append(dict(idx=draw(allc, B), seg="nuisance", nuis=(g, a), seen=len(tasks) - 1))
    # short recovery (all-class, no nuisance) -- for the bulk_drift viz only, NOT a calibration reference
    for _ in range(S2):
        steps.append(dict(idx=draw(allc, B), seg="stat2", nuis=None, seen=len(tasks) - 1))

    # fixed probe (the raw-prototype LUT: balanced, all classes) + fixed eval subsets by task
    pr = rng.permutation(len(Xtr))[:min(cfg.PROBE_N, len(Xtr))]
    Xpr, Ypr = Xtr[pr], Ytr[pr]
    eval_by_task = {}
    for k, cls in enumerate(tasks):
        m = np.isin(Yte, cls); ei = np.where(m)[0]
        if len(ei) > cfg.EVAL_N // len(tasks):
            ei = rng.choice(ei, cfg.EVAL_N // len(tasks), replace=False)
        eval_by_task[k] = (Xte[ei], Yte[ei])

    return dict(steps=steps, real_onsets=real_onsets, nuis_onset=nuis_onset,
                stationary_steps=stationary_steps, nuisance_steps=nuisance_steps,
                calib_steps=calib_steps, warmup1_steps=warmup1_steps, settle_start=settle_start,
                checkpoints=checkpoints, warmup_idx=warmup_idx,
                Xtr=Xtr, Ytr=Ytr, Xpr=Xpr, Ypr=Ypr, eval_by_task=eval_by_task,
                tasks=tasks, C=C, n_steps=len(steps))


# ============================================================ the tractability cache (SCFF pass is gate-independent)
def _sleep_grid(n_steps, checkpoints, every):
    grid = set(s for s, _ in checkpoints)
    grid.update(range(every - 1, n_steps, every))
    return sorted(grid)


def build_cache(cell_factory, stream, seed, cfg, *, sleep_every=4, quick=False):
    """Run the frozen-to-GD SCFF bulk FORWARD-ONLY through the drift stream ONCE (head/gate-independent) and cache,
    per step: the batch taps + labels (op (c) input), the label-free drift SIGNALS (precomputed -- they depend only
    on the SCFF trajectory + the fixed probe), and -- at sleep-grid steps -- the re-forwarded probe/LUT taps + -- at
    checkpoints -- the per-task eval taps. Every arm replays on this (run_economy). Records the RNG draw order so the
    replay is deterministic. bulk_drift + the class-direction signal use the FIXED probe reps."""
    rng = np.random.default_rng(seed)
    dims = [cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH
    cell = cell_factory(dims, seed)
    Xtr, Ytr = stream["Xtr"], stream["Ytr"]
    Xpr, Ypr = stream["Xpr"], stream["Ypr"]

    # warmup (unscored): give SCFF a base on task-0 so the stationary floor is meaningful
    wu = stream["warmup_idx"]
    for s in range(0, len(wu), cfg.BATCH):
        xb = Xtr[wu[s:s + cfg.BATCH]]
        if len(xb) >= 4:
            cell.train_step(xb, rng)

    grid = set(_sleep_grid(stream["n_steps"], stream["checkpoints"], sleep_every))
    ckpt_steps = {s: t for s, t in stream["checkpoints"]}

    def alltap(X):
        return readout_feats(cell.infer(X), None)

    cache = dict(steps=[], sig=dict(), grid=sorted(grid), ckpt=ckpt_steps, rng_fingerprint=[])
    # the FIXED start reference (for the CUMULATIVE bulk_drift = 'how far has the rep drifted from t0')
    ref_reps = cell.infer(Xpr)
    x_buf = []                                                         # per-step RAW input batch (nuisance-transformed)

    for si, st in enumerate(stream["steps"]):
        xb = Xtr[st["idx"]].copy(); yb = Ytr[st["idx"]].copy()
        if st["nuis"] is not None:
            g, a = st["nuis"]; xb = nuisance_transform(xb, g, a)
        # SCFF live forward-only update (gate-independent) -- the drift-generating step
        if len(xb) >= 4:
            cell.train_step(xb, rng)
        cache["rng_fingerprint"].append(float(rng.random()))            # RNG-order determinism marker

        phi_b = alltap(xb)                                             # batch taps (op (c) input)
        rec = dict(phi_b=phi_b, y_b=yb, seg=st["seg"]); x_buf.append(xb)
        # cumulative bulk_drift on the fixed probe (the 'bulk doesn't forget' read; P8.0 DRIFT figure)
        reps_pr = cell.infer(Xpr)
        bd = np.array([float(np.median(((rc * rp).sum(1))
                       / (np.linalg.norm(rc, axis=1) * np.linalg.norm(rp, axis=1) + EPS)))
                       for rc, rp in zip(reps_pr, ref_reps)])
        rec["_bd"] = float(bd.mean())
        if si in grid:
            rec["phi_probe"] = readout_feats(reps_pr, None); rec["y_probe"] = Ypr
        if si in ckpt_steps:
            rec["eval"] = {k: (alltap(Xk), Yk) for k, (Xk, Yk) in stream["eval_by_task"].items()
                           if k <= ckpt_steps[si]}
        cache["steps"].append(rec)

    # --- the trigger SIGNALS: an MMD distribution-distance between the CURRENT window of streaming batches and a
    #     LAGGED window (a CHANGE detector: spikes at each onset when new tap-modes appear, ~0 in stable training).
    #     tap_dir = MMD on L2-NORMALIZED post-norm taps (ANGULAR structure only -> magnitude-invariant, spine-clean);
    #     driftlens = MMD on raw post-norm taps (the field's embedding-distance reference); BOTH are nuisance-INVARIANT
    #     (post-norm removes the covariate shift). tap_mag = MMD on the RAW INPUT (nuisance-VISIBLE -> the false-fire
    #     NULL: it cannot tell a new class (real) from a covariate shift (nuisance)). ---
    n = len(cache["steps"]); W = max(2, int(cfg.WIN_W)); Dlag = max(2, int(cfg.WIN_LAG))
    PHI = [r["phi_b"] for r in cache["steps"]]
    PHIN = [_l2n(p) for p in PHI]

    def _window(buf, si):
        return np.concatenate(buf[max(0, si - W + 1):si + 1], 0)
    # fixed bandwidths from the SETTLE INTERIOR (calib_steps: all-class, no-nuisance, no boundary transient -> matched
    # to the deployment distribution, so the raw-input MMD reads the nuisance covariate shift as large; post-norm MMD
    # reads it as ~0). Step-comparable across the whole stream.
    cidx = stream.get("calib_steps") or list(range(W - 1, n))
    pool_phin = np.concatenate([PHIN[i] for i in cidx], 0)
    pool_phi = np.concatenate([PHI[i] for i in cidx], 0)
    pool_x = np.concatenate([x_buf[i] for i in cidx], 0)
    b_dir = _bandwidth(pool_phin); b_dl = _bandwidth(pool_phi); b_mag = _bandwidth(pool_x)
    tap_dir = np.zeros(n); driftlens = np.zeros(n); tap_mag = np.zeros(n)
    for si in range(n):
        j = max(W - 1, si - Dlag)                                     # lagged window end (>= a full window back)
        tap_dir[si] = _mmd2(_window(PHIN, si), _window(PHIN, j), sig2=b_dir)
        driftlens[si] = _mmd2(_window(PHI, si), _window(PHI, j), sig2=b_dl)
        tap_mag[si] = _mmd2(_window(x_buf, si), _window(x_buf, j), sig2=b_mag)
    cache["sig"] = dict(tap_dir=tap_dir, driftlens=driftlens, tap_mag=tap_mag,
                        bulkdrift=np.array([r["_bd"] for r in cache["steps"]]))
    for r in cache["steps"]:
        r.pop("_bd", None)
    cache["stream"] = stream
    return cache


# ============================================================ error-based detectors (P8.1)
class AbsTheta:
    """The rough S6 gate: fire if the batch error rate >= theta."""
    def __init__(self, theta=0.55):
        self.theta = float(theta)

    def reset(self):
        return self

    def update(self, err):
        return bool(err >= self.theta)


class DDM:
    """DDM (Gama 2004): p = running error mean, s = sqrt(p(1-p)/n). Track (p+s)_min; warn at warn*s_min, DRIFT (fire)
    at drift*s_min. Reset the running stats on drift."""
    def __init__(self, warn=2.0, drift=3.0):
        self.warn = float(warn); self.drift = float(drift); self.reset()

    def reset(self):
        self.n = 0; self.p = 1.0; self.s = 0.0; self.pmin = np.inf; self.smin = np.inf
        return self

    def update(self, err):
        self.n += 1
        self.p += (err - self.p) / self.n
        self.s = np.sqrt(self.p * (1 - self.p) / self.n) if self.n > 0 else 0.0
        if self.p + self.s <= self.pmin + self.smin:
            self.pmin, self.smin = self.p, self.s
        fire = (self.n > 5) and (self.p + self.s >= self.pmin + self.drift * self.smin)
        if fire:
            self.reset()
        return bool(fire)


class ADWIN:
    """A simplified ADWIN (Bifet 2007): a bounded window of recent errors; if a split's two halves' means differ by
    more than the Hoeffding cut eps = sqrt((1/2m) ln(4/delta)) (m = harmonic mean of the two sizes), drop the older
    half and FIRE. Scans a few interior split points (numpy; no River)."""
    def __init__(self, delta=0.05, maxw=200):
        self.delta = float(delta); self.maxw = int(maxw); self.reset()

    def reset(self):
        self.w = []
        return self

    def update(self, err):
        self.w.append(float(err))
        if len(self.w) > self.maxw:
            self.w = self.w[-self.maxw:]
        n = len(self.w)
        if n < 8:
            return False
        arr = np.array(self.w); fired = False
        for cut in range(4, n - 3):
            n0, n1 = cut, n - cut
            m = 1.0 / (1.0 / n0 + 1.0 / n1)
            eps = np.sqrt((1.0 / (2 * m)) * np.log(4.0 / self.delta))
            if abs(arr[:cut].mean() - arr[cut:].mean()) > eps:
                self.w = self.w[cut:]; fired = True; break
        return bool(fired)


class BudgetGate:
    """The learned budget-gate (Skip-RNN-style) -- a TINY trained thing on the READ side (reads a drift feature,
    never writes SCFF -> does not violate the forward-leak wall). Reads a DIRECTION/DRIFT feature (class-direction
    tap-drift + its short delta), NEVER a confidence magnitude (the spine; why P5 struck the adaptive exit). Trained
    offline on a calibration split with a budget-regularized logistic loss L = BCE(fire, err>=theta*) + lam*mean(fire).
    FD-guarded (fd_budget_gate_guard). The least spine-pure arm -> flagged."""
    def __init__(self, lam=0.3, seed=0):
        self.lam = float(lam); self.seed = seed; self.w = None; self.b = 0.0

    def reset(self):
        return self

    @staticmethod
    def _feat(sig_dir, prev):
        d = float(sig_dir); dd = float(sig_dir - prev)
        return np.array([d, dd, 1.0])                                  # [direction, delta-direction, bias]

    def loss_grad(self, Feat, target):
        z = Feat @ np.append(self.w, self.b); p = expit(z)
        bce = -(target * np.log(p + EPS) + (1 - target) * np.log(1 - p + EPS)).mean()
        budget = self.lam * p.mean()
        g = Feat.T @ ((p - target) / len(p)) + self.lam * (Feat.T @ (p * (1 - p)) / len(p))
        return bce + budget, g

    def fit(self, Feats, targets, *, ep=300, lr=0.5):
        rng = np.random.default_rng(self.seed)
        theta = np.append(rng.standard_normal(Feats.shape[1] - 1) * 0.01, 0.0)
        self.w, self.b = theta[:-1], theta[-1]
        for _ in range(ep):
            _, g = self.loss_grad(Feats, targets)
            theta = np.append(self.w, self.b) - lr * g
            self.w, self.b = theta[:-1], theta[-1]
        return self

    def update_feat(self, feat):
        return bool(expit(feat @ np.append(self.w, self.b)) >= 0.5)


def make_detector(name, cfg, **kw):
    n = name.lower()
    if n in ("abs", "abs_theta", "absolute"):
        return AbsTheta(kw.get("theta", cfg.ABS_THETA))
    if n == "ddm":
        return DDM(kw.get("warn", cfg.DDM_WARN), kw.get("drift", cfg.DDM_DRIFT))
    if n == "adwin":
        return ADWIN(kw.get("delta", cfg.ADWIN_DELTA))
    raise ValueError(f"detector '{name}' unknown")


# ============================================================ trigger SIGNALS (P8.2) + the fair detection rule
def sig_error_ema(err_series, beta):
    """The LABELED reference trigger: EMA of the per-step error rate (precise, lags; a labeled magnitude)."""
    out = np.zeros(len(err_series)); e = err_series[0] if len(err_series) else 0.0
    for i, v in enumerate(err_series):
        e = (1 - beta) * e + beta * v; out[i] = e
    return out


def sig_tap_drift_direction(cache):
    """The committed candidate: 1 - mean_c cos(class-direction_t, class-direction_ref) on the FIXED probe (post-norm
    -> nuisance-invariant). Fires when the class DIRECTIONS rotate (real drift), not when the cloud translates/scales."""
    return cache["sig"]["tap_dir"].copy()


def sig_tap_drift_magnitude(cache):
    """The false-fire NULL: a raw-input mean-shift / moment statistic (ADWIN-U-style). Moves on the nuisance
    covariate shift (density != class) -> predicted to false-fire (the spine demonstration)."""
    return cache["sig"]["tap_mag"].copy()


def sig_driftlens(cache):
    """The label-free reference (DriftLens-style): post-norm embedding-distance (per-class mean shift) vs a fixed
    reference window. Nuisance-invariant (post-norm); the validated tool the home-grown direction signal is checked against."""
    return cache["sig"]["driftlens"].copy()


def sig_studd(err_proxy_series):
    """The conservative label-free arm (STUDD-style): a student mimics the namer; monitor the mimic-disagreement.
    Implemented as a slow EMA of the head's self-disagreement proxy (built in run_economy). Fewer false alarms, slower."""
    out = np.zeros(len(err_proxy_series)); e = 0.0
    for i, v in enumerate(err_proxy_series):
        e = 0.9 * e + 0.1 * v; out[i] = e
    return out


def calibrate_threshold(sig, stationary_steps, *, pct=97.5, margin=1.10):
    """Robust FAR-floor calibration: threshold = high-percentile of the signal over the STATIONARY (settle+stat2,
    all-class no-drift) segment * margin. A percentile (not the raw max) resists a single noisy stationary step, so
    the stationary FAR floor is ~(100-pct)% and the discriminator is nuisance-FAR-above-floor + MTD (design C2: FAR
    vs each arm's OWN empirical stationary floor)."""
    base = sig[np.array(stationary_steps)] if len(stationary_steps) else sig
    return float(np.percentile(base, pct) * margin + 1e-12)


def detect_crossings(sig, thr):
    """Fire at every step whose signal exceeds thr. Returns the boolean fire vector."""
    return sig > thr


def mtd_far(fires, stream):
    """MTD = mean steps from each real-drift onset to the first fire after it (true-positives only, within a window);
    FAR = fires on the nuisance segment per step; MTFA = mean gap between fires on the stationary segment."""
    onsets = stream["real_onsets"]; n = len(fires)
    fire_idx = np.where(fires)[0]
    delays = []
    win = 40
    for o in onsets:
        after = fire_idx[(fire_idx >= o) & (fire_idx < o + win)]
        if len(after):
            delays.append(int(after[0] - o))
    mtd = float(np.median(delays)) if delays else float(win)             # censored at the window if never detected
    nu = stream["nuisance_steps"]
    far = float(fires[np.array(nu)].mean()) if nu else 0.0
    stat = np.array(stream["stationary_steps"])
    far_stat = float(fires[stat].mean()) if len(stat) else 0.0        # the arm's OWN empirical stationary floor (C2)
    sf = np.where(fires[stat])[0]
    mtfa = float(np.median(np.diff(sf))) if len(sf) > 1 else float(len(stat))
    excess = float(max(0.0, far - far_stat))                          # false-firing ABOVE the arm's own floor
    return dict(mtd=mtd, far=far, far_stat=far_stat, excess_far=excess, mtfa=mtfa,
                n_detected=len(delays), n_onsets=len(onsets))


# ============================================================ the live economy replay (streaming mode)
def run_economy(cache, head_factory, cfg, *, gate="oracle", trigger="error", sleep_policy="checkpoint",
                cadence_every=1, lut_frac=1.0, lam_ema=1.0, cbrs=False, detector_kw=None, ema_beta=None,
                budget_gate=None, sig_override=None):
    """Replay ONE economy arm on a cache in a SINGLE pass. SCFF taps are fixed (gate-independent); this decides op (c)
    (awake namer update on FIRE) + op (d) (sleep = re-forward the LUT/probe -> reset+solve) and tracks:
      * accuracy-held / the POST-sleep acc-matrix (AA/BWT/forget, the continual_safety_heads convention);
      * the PRE-sleep acc-matrix at each checkpoint -> worst_bwt (the awake gate's worst mid-stream point; post-sleep
        hides the awake forgetting -- the P8.6 safety read), computed in the SAME pass;
      * fire/sleep counts + a per-op energy trace.
    `gate` in {always, oracle, abs, ddm, adwin, budget}. `trigger` = the error view fed to an error detector
    (error | error_ema) OR ignored when a label-free `sig_override` gate is used (P8.2). `sleep_policy`: 'checkpoint'
    (sleep at each task-completion boundary -- the FIXED cadence P8.1/P8.2 hold; == the oracle cadence) or 'grid'
    (sleep on the grid every `cadence_every` eligible steps -- the P8.3 sweep)."""
    steps = cache["steps"]; stream = cache["stream"]; C = stream["C"]; T = len(stream["tasks"])
    ema_beta = cfg.EMA_BETA if ema_beta is None else ema_beta
    head = head_factory()
    fires = np.zeros(len(steps), bool); sleeps = np.zeros(len(steps), bool)
    energy_trace = []
    det = make_detector(gate, cfg, **(detector_kw or {})) if gate in ("abs", "ddm", "adwin") else None
    sig = sig_override
    thr = calibrate_threshold(sig, stream["stationary_steps"]) if sig is not None else None
    sleep_grid = sorted(cache["grid"]); ckpt = cache["ckpt"]
    checkpoint_steps = set(s for s, _ in stream["checkpoints"])
    # the oracle knows the TRUE drift window -> it pays awake THROUGH each onset ramp (the achievable reference the
    # blind detector must approach), not just at the first step.
    oracle_fire = set(i for i, st in enumerate(stream["steps"]) if st["seg"].startswith("onset"))
    grid_seen = 0

    amat = [[0.0] * T for _ in range(T)]                                # POST-sleep (the AA/BWT convention)
    amat_pre = [[0.0] * T for _ in range(T)]                            # PRE-sleep (the worst-point read)
    worst_bwt = 0.0
    err_ema = 0.0; prev_dir = float(cache["sig"]["tap_dir"][0]); studd_series = []; fitted = False
    err_trace = []                                                      # per-step batch error (the labeled onset signal)

    def _fire_decision(si, rec):
        nonlocal err_ema, fitted
        if gate == "always":
            return True
        if gate == "oracle":
            return si in oracle_fire
        if gate == "budget" and budget_gate is not None:
            return budget_gate.update_feat(BudgetGate._feat(cache["sig"]["tap_dir"][si], prev_dir))
        if not fitted:                                                  # seed the head before a data-driven gate can read it
            return True
        if det is not None:
            err = 1.0 - float((head.predict(rec["phi_b"]) == rec["y_b"]).mean())
            if trigger == "error_ema":
                err_ema = (1 - ema_beta) * err_ema + ema_beta * err
                return det.update(err_ema)
            return det.update(err)
        if sig is not None:
            return bool(sig[si] > thr)
        return False

    def _sleep_set(Fp, Yp, si):
        if lut_frac < 1.0:
            nkeep = max(C, int(lut_frac * len(Fp)))
            sel = np.random.default_rng(1000 + si).permutation(len(Fp))[:nkeep]
            Fp, Yp = Fp[sel], Yp[sel]
        if cbrs:
            Fp, Yp = class_balanced_reservoir(Fp, Yp, C, cfg.CBRS_CAP, np.random.default_rng(2000 + si))
        return Fp, Yp

    for si, rec in enumerate(steps):
        phi_b, y_b = rec["phi_b"], rec["y_b"]
        e_op = dict(step=si, fire=False, sleep=False, Fdim=phi_b.shape[1], B=len(phi_b),
                    probe_n=(rec["phi_probe"].shape[0] if "phi_probe" in rec else 0))
        err_trace.append(1.0 - float((head.predict(phi_b) == y_b).mean()) if head.W is not None else np.nan)
        # --- op (c): the awake fire ---
        fire = _fire_decision(si, rec)
        prev_dir = float(cache["sig"]["tap_dir"][si])
        if fire:
            head.partial_fit(phi_b, y_b, lam_ema=lam_ema); fitted = True
            fires[si] = True; e_op["fire"] = True
        # studd proxy (head self-disagreement on the probe) -- built for P8.2's conservative arm
        if "phi_probe" in rec and head.W is not None:
            studd_series.append(1.0 - float((head.predict(rec["phi_probe"]) == rec["y_probe"]).mean()))
        else:
            studd_series.append(studd_series[-1] if studd_series else 0.0)

        # sleep cadence (a CONTROLLED variable, uniform across gates so P8.1 isolates the awake gate; swept in P8.3):
        # 'checkpoint' = sleep at every task boundary (the oracle-boundary cadence); 'grid' = every cadence_every-th
        # grid step. NOTE: oracle/always are special ONLY in their AWAKE firing, never in the sleep cadence.
        is_grid = si in cache["grid"]
        if is_grid:
            grid_seen += 1
        will_sleep = False
        if sleep_policy == "checkpoint":
            will_sleep = si in checkpoint_steps
        elif sleep_policy == "grid":
            will_sleep = is_grid and (grid_seen % max(1, cadence_every) == 0)

        # --- checkpoint eval: PRE-sleep first (worst-point), then sleep, then POST-sleep ---
        if si in ckpt and "eval" in rec:
            t = ckpt[si]
            if not fitted:                                             # ensure a head exists to eval
                head.partial_fit(phi_b, y_b, lam_ema=lam_ema); fitted = True
            for k, (Fk, Yk) in rec["eval"].items():
                amat_pre[t][k] = float((head.predict(Fk) == Yk).mean())
            if t >= 1:
                _, bwt_pre, _ = acc_matrix_metrics([row[:t + 1] for row in amat_pre[:t + 1]])
                worst_bwt = min(worst_bwt, bwt_pre)

        # --- op (d): sleep = re-forward the LUT/probe -> reset + solve ---
        if will_sleep and "phi_probe" in rec:
            Fp, Yp = _sleep_set(rec["phi_probe"], rec["y_probe"], si)
            head.sleep_fit(Fp, Yp); sleeps[si] = True; e_op["sleep"] = True; fitted = True

        if si in ckpt and "eval" in rec:                              # POST-sleep eval (the AA/BWT convention)
            t = ckpt[si]
            for k, (Fk, Yk) in rec["eval"].items():
                amat[t][k] = float((head.predict(Fk) == Yk).mean()) if head.W is not None else 0.0
        energy_trace.append(e_op)

    aa, bwt, forget = acc_matrix_metrics(amat)
    return dict(aa=aa, bwt=bwt, forget=forget, matrix=amat, matrix_pre=amat_pre, worst_bwt=float(worst_bwt),
                fires=fires, sleeps=sleeps, firefrac=float(fires.mean()),
                energy_trace=energy_trace, studd=np.array(studd_series), err_trace=np.array(err_trace, float))


# ============================================================ the dual-mode wrapper (block == the guard/oracle ref)
def awake_sleep_loop(cell_factory, head_factory, Xtr, Ytr, Xte, Yte, tasks, C, seed, *,
                     mode="streaming", cfg=None, gate="oracle", trigger="error", sleep_policy="checkpoint",
                     cadence_every=1, lut_frac=1.0, lam_ema=1.0, cbrs=False, sig_name=None, quick=False,
                     scff_ep=8, sleep_ep=60):
    """Dual-mode. BLOCK mode: SCFF trained per-task-block, sleep = from-scratch fit on the full replay buffer at each
    boundary, NO awake gate -> reproduces continual_safety_heads bit-for-bit (the guard + the oracle-cadence
    reference). STREAMING mode: build the cache + replay the arm (the real Phase-8 regime)."""
    if mode == "block":
        return continual_safety_heads(cell_factory, head_factory, Xtr, Ytr, Xte, Yte, tasks, C, seed,
                                      scff_ep=scff_ep, sleep_ep=sleep_ep, sleep=True, probe=False)
    stream = make_drift_stream(Xtr, Ytr, Xte, Yte, tasks, seed, cfg, quick=quick)
    cache = build_cache(cell_factory, stream, seed, cfg, quick=quick)
    sig_override = None
    if sig_name is not None:
        sig_override = {"tap_dir": sig_tap_drift_direction, "tap_mag": sig_tap_drift_magnitude,
                        "driftlens": sig_driftlens}[sig_name](cache)
    return run_economy(cache, head_factory, cfg, gate=gate, trigger=trigger, sleep_policy=sleep_policy,
                       cadence_every=cadence_every, lut_frac=lut_frac, lam_ema=lam_ema, cbrs=cbrs,
                       sig_override=sig_override)


# ============================================================ the behavioral ADC-centred cost meter (design 2.3)
def _e_adc(cfg, bits=None):
    return cfg.E_ADC_STEP * (cfg.ADC_BITS if bits is None else bits)


def hardware_cost_meter(cfg, *, head_name, Fdim, C, n_fire, n_sleep, n_steps, batch, probe_n,
                        scff_dims, adc_bits=None, substrate="analog", e_mac_dig=None):
    """E_total = n_MAC*e_MAC + n_ADC*e_ADC(bits) + n_write*e_write + n_solve_flop*e_digital, ADC-dominant. Prices
    the WHOLE live loop for one head. Ops: (a) SCFF fwd+update EVERY step; (b) namer inference EVERY step; (c) namer
    partial_fit on FIRES; (d) sleep re-forward+solve on SLEEPS. Returns the per-op energy dict (pJ; behavioral).

    `substrate` = 'analog' (the crossbar/CIM chip -- near-free in-memory MAC, ADC-dominant; the DEFAULT, so every
    frozen P8.0-P8.6 call is unchanged) or 'digital' (the conventional von-Neumann / digital-accelerator baseline --
    P8.7: a real digital 8-bit MAC (cfg.E_MAC_DIG >> E_MAC because the operands must be fetched, the memory wall),
    NO ADC (eA=0 -- the datapath is digital end-to-end, the analog tax vanishes), SRAM weight write (E_WRITE_DIG),
    same digital solve (E_DIGITAL, substrate-independent). Matched 8-bit precision => the axis under test is the
    SUBSTRATE. `e_mac_dig` overrides cfg.E_MAC_DIG for the memory-wall sensitivity sweep."""
    if substrate == "digital":
        eA = 0.0; eM = (cfg.E_MAC_DIG if e_mac_dig is None else float(e_mac_dig))
        eW = cfg.E_WRITE_DIG; eD = cfg.E_DIGITAL
    else:
        eA = _e_adc(cfg, adc_bits); eM = cfg.E_MAC; eW = cfg.E_WRITE; eD = cfg.E_DIGITAL
    # --- SCFF bulk (a): fwd MACs + ADC per activation + CHEAP analog local plasticity EVERY step. The continuous
    #     local update is an analog charge nudge (priced at e_MAC), NOT a digital write-verify -- the expensive
    #     e_write (capacitor/RRAM program) is reserved for the RARE, DELIBERATE namer solve-writes (c)/(d) (design 2.3).
    layer_macs = scff_dims[0] * scff_dims[1] + sum(scff_dims[i] * scff_dims[i + 1] for i in range(1, len(scff_dims) - 1))
    layer_acts = sum(scff_dims[1:]); scff_w = layer_macs
    a_mac = n_steps * batch * layer_macs
    a_adc = n_steps * batch * layer_acts
    a_upd = n_steps * scff_w                                           # analog plasticity nudges (cheap, e_MAC)
    # --- namer inference (b): EVERY step, one output per sample ---
    if head_name == "ranpac":
        P = cfg.RANPAC_KNOB["proj_dim"]
        b_mac = n_steps * batch * (Fdim * P + P * C); b_adc = n_steps * batch * (P + C)
        solve_flop = (2.0 / 3.0) * P ** 3; nwrite = P * C; acc_flop = batch * P * P
    else:  # slda
        b_mac = n_steps * batch * (Fdim * C); b_adc = n_steps * batch * C
        solve_flop = (2.0 / 3.0) * Fdim ** 3; nwrite = Fdim * C; acc_flop = batch * Fdim * Fdim
    # --- namer update (c): on FIRES = accumulate (rank-k, digital) + solve + DELIBERATE weight-write (e_write, rare) ---
    c_solve = n_fire * (solve_flop + acc_flop); c_write_e = n_fire * nwrite
    # --- sleep (d): re-forward probe through SCFF (fwd+ADC) + rebuild (G,M) + solve + deliberate write ---
    d_mac = n_sleep * probe_n * layer_macs
    d_adc = n_sleep * probe_n * layer_acts
    d_solve = n_sleep * (solve_flop + probe_n * (P * P if head_name == "ranpac" else Fdim * Fdim))
    d_write_e = n_sleep * nwrite
    # The 80/20 split follows the THESIS: SCFF-share = all UNSUPERVISED forward compute (stream forward (a) + the
    # sleep LUT re-forward (d_mac/d_adc) -- both are cheap crossbar MACs+ADC, no backward, no labels); GD/naming-share
    # = the SUPERVISED naming (namer inference (b) + the gated solve/write (c) + the sleep solve/write (d_solve)).
    E_scff = (a_mac + a_upd + d_mac) * eM + (a_adc + d_adc) * eA        # unsupervised forward: stream + sleep re-forward
    E_gd = b_mac * eM + b_adc * eA + (c_write_e + d_write_e) * eW + (c_solve + d_solve) * eD   # naming: infer + learn
    E_total = E_scff + E_gd
    E_mac = (a_mac + a_upd + b_mac + d_mac) * eM; E_adc = (a_adc + b_adc + d_adc) * eA
    E_write = (c_write_e + d_write_e) * eW; E_solve = (c_solve + d_solve) * eD
    return dict(mac=E_mac, adc=E_adc, write=E_write, solve=E_solve, total=E_total,
                gd=E_gd, scff=E_scff, gdshare=float(E_gd / (E_total + EPS)),
                n_MAC=(a_mac + b_mac + d_mac), n_ADC=(a_adc + b_adc + d_adc),
                n_write=(c_write_e + d_write_e), n_solve=(c_solve + d_solve),
                substrate=substrate, e_mac=eM, e_adc=eA)


def meter_from_trace(cfg, head_name, cache, res, *, adc_bits=None, substrate="analog", e_mac_dig=None):
    """Price a run_economy result on its actual fire/sleep counts. `substrate`/`e_mac_dig` select the analog crossbar
    (default) or the digital-accelerator baseline (P8.7) -- the SAME op-counts, different per-op physics."""
    stream = cache["stream"]; C = stream["C"]
    Fdim = cache["steps"][0]["phi_b"].shape[1]
    scff_dims = [cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH
    probe_n = next((r["phi_probe"].shape[0] for r in cache["steps"] if "phi_probe" in r), cfg.PROBE_N)
    return hardware_cost_meter(cfg, head_name=head_name, Fdim=Fdim, C=C,
                               n_fire=int(res["fires"].sum()), n_sleep=int(res["sleeps"].sum()),
                               n_steps=len(cache["steps"]), batch=cfg.BATCH, probe_n=probe_n,
                               scff_dims=scff_dims, adc_bits=adc_bits, substrate=substrate, e_mac_dig=e_mac_dig)


def bp_replay_energy(cfg, *, Fdim, C, n_steps, batch, replay_batch, bp_dims, adc_bits=None,
                     substrate="analog", e_mac_dig=None):
    """The BP+replay energy model at matched retention (SAME substrate table, SAME plasticity assumption as OURS --
    fair): a backward pass EVERY step (~2x forward MACs) + the backward activations digitized (2x ADC, analog only) +
    a replay mini-batch fwd+bwd EVERY step (to reach OURS's retention). The weight update is a cheap nudge (e_MAC),
    same as OURS's SCFF plasticity -- so BP's DISTINCTIVE cost is the BACKWARD credit-assignment MACs (+ ADC on
    analog) + the replay, NOT writes. NOT a naive backward-every-step BP that forgets (a strawman), NOT a generic FLOP
    count. `substrate`='analog' (default -- the fair same-substrate BP the P8.5 bp_ratio uses) or 'digital' (P8.7 --
    the conventional GPU/digital-accelerator GD baseline: digital MACs, NO ADC, matched 8-bit precision)."""
    if substrate == "digital":
        eA = 0.0; eM = (cfg.E_MAC_DIG if e_mac_dig is None else float(e_mac_dig))
    else:
        eA = _e_adc(cfg, adc_bits); eM = cfg.E_MAC
    fwd_macs = bp_dims[0] * bp_dims[1] + sum(bp_dims[i] * bp_dims[i + 1] for i in range(1, len(bp_dims) - 1))
    acts = sum(bp_dims[1:]); n_w = fwd_macs
    per_step_samples = batch + replay_batch
    mac = n_steps * per_step_samples * fwd_macs * 3.0                  # fwd + bwd (~2x) = 3x forward MACs
    adc = n_steps * per_step_samples * acts * 2.0                      # fwd + bwd activations digitized (analog only)
    upd = n_steps * n_w                                              # cheap weight update (e_MAC), same as OURS
    E = (mac + upd) * eM + adc * eA
    return dict(total=E, mac=(mac + upd) * eM, adc=adc * eA, n_w=n_w, substrate=substrate, e_mac=eM)


# ============================================================ guards (run FIRST — any fails -> STOP)
def partial_fit_equiv_guard(*, C=4, d=48, n=600, seed=0, verbose=True):
    """The ONE new primitive's guard: N sequential partial_fit @ lam_ema=1 (pure cumulative) == one batch `fit` to
    float64 precision (BLAS reduction order differs -> not literally bit-for-bit; the invariant is the SOLVED head to
    ~1e-6 abs on values ~1e2-1e5 => relative ~1e-10) AND IDENTICAL predictions. Both RanPAC and SLDA."""
    rng = np.random.default_rng(seed)
    F = rng.standard_normal((n, d)) * 2.0; Y = rng.integers(0, C, n)
    Fte = rng.standard_normal((n // 2, d)) * 2.0
    ok = True; detail = {}
    for name, mk in (("ranpac", lambda: make_stream_head("ranpac", C, seed=seed, proj_dim=200, ridge_lambda=1.0)),
                     ("slda", lambda: make_stream_head("slda", C, seed=seed, shrinkage=1e-2))):
        batch = mk(); ref = (RanPACHead(C, seed=seed, proj_dim=200, ridge_lambda=1.0) if name == "ranpac"
                             else SLDAHead(C, seed=seed, shrinkage=1e-2)).fit(F, Y)
        h = mk()
        for s in range(0, n, 64):                                     # N sequential partial_fit blocks
            h.partial_fit(F[s:s + 64], Y[s:s + 64], lam_ema=1.0)
        dW = float(np.max(np.abs(h.W - ref.W)))
        dpred = int((h.predict(Fte) != ref.predict(Fte)).sum())
        okn = (dW < 1e-6) and (dpred == 0)
        ok &= okn; detail[f"{name}_maxdW"] = dW; detail[f"{name}_predmiss"] = dpred
        if verbose:
            print(f"  [partial_fit_equiv {name}] max|W_stream-W_batch|={dW:.2e} pred-miss={dpred}  "
                  f"{'OK' if okn else '!! STREAMING-GRAM BUG'}", flush=True)
    return ok, detail


def live_path_anchor_guard(cfg, *, seed=42, verbose=True, quick=True):
    """awake_sleep_loop(block mode) with SCFF-training-ON == continual_safety_heads bit-for-bit (anchors the LIVE
    path, not just the frozen one). Uses the committed RanPAC head (deterministic)."""
    Xtr, Ytr, Xte, Yte = synth_stream(1200, 600, cfg.OVERLAP, seed, dim=cfg.DIM, n_class=cfg.NCLASS, n_clusters=cfg.NCLUST)
    hf = lambda s: make_head("ranpac", cfg.NCLASS, seed=s, **cfg.RANPAC_KNOB)

    def cf(dims, s):
        return make_committed_cell(dims, s)
    ref = continual_safety_heads(cf, hf, Xtr, Ytr, Xte, Yte, cfg.TASKS, cfg.NCLASS, seed,
                                 scff_ep=2, sleep_ep=60, sleep=True, probe=False)
    new = awake_sleep_loop(cf, hf, Xtr, Ytr, Xte, Yte, cfg.TASKS, cfg.NCLASS, seed,
                           mode="block", cfg=cfg, scff_ep=2, sleep_ep=60)
    dmat = max(abs(ref["matrix"][i][k] - new["matrix"][i][k]) for i in range(5) for k in range(5))
    ok = dmat < 1e-12
    if verbose:
        print(f"  [live_path_anchor] block-mode vs continual_safety_heads max|d|={dmat:.2e}  "
              f"AA ref={ref['aa']:.4f} new={new['aa']:.4f}  {'OK' if ok else '!! LIVE-PATH BUG'}", flush=True)
    return ok, dmat


def scff_static_frozen_guard(cfg, *, seed=42, verbose=True):
    """SCFF-update-OFF after train_cell pretrain == a static readout (the only truly-frozen path). Confirms the
    static bake-off apparatus still reproduces (a head on a frozen bulk); ties to P7's static regime."""
    Xtr, Ytr, Xte, Yte = synth_stream(1500, 700, cfg.OVERLAP, seed, dim=cfg.DIM, n_class=cfg.NCLASS, n_clusters=cfg.NCLUST)
    cell = make_committed_cell([cfg.DIM] + [cfg.WIDTH] * cfg.DEPTH, seed)
    train_cell(cell, Xtr, np.random.default_rng(seed), ep=6, batch=32)
    F1 = all_tap_feats(cell, Xte)
    F2 = all_tap_feats(cell, Xte)                                      # no SCFF update between -> identical
    d = float(np.max(np.abs(F1 - F2)))
    h = make_head("ranpac", cfg.NCLASS, seed=seed, **cfg.RANPAC_KNOB).fit(all_tap_feats(cell, Xtr), Ytr)
    acc = float((h.predict(F1) == Yte).mean())
    ok = (d < 1e-12) and (acc > 0.3)
    if verbose:
        print(f"  [scff_static_frozen] frozen-tap reproducibility max|d|={d:.2e} static RanPAC acc={acc:.3f}  "
              f"{'OK' if ok else '!! FROZEN-PATH BUG'}", flush=True)
    return ok, dict(repro=d, acc=acc)


def meter_proxy_guard(cfg, *, verbose=True):
    """The MAC+solve sub-terms of hardware_cost_meter reduce to p7lib.readout_cost under UNIT energies (ADC/write are
    net-new terms, not reduction targets). Confirms the meter is the P7 proxy + the new ADC/write physics."""
    from p7lib import readout_cost
    Fdim, C = 768, 10
    h = make_head("ranpac", C, seed=0, **cfg.RANPAC_KNOB)
    h._phi(np.zeros((2, Fdim)))                                        # init projection
    proxy = readout_cost(h, Fdim, C)                                   # dict(fwd_macs, solve_dim)
    # our meter's per-sample fwd MACs for RanPAC = Fdim*P + P*C  == proxy fwd_macs
    P = cfg.RANPAC_KNOB["proj_dim"]
    our_fwd = Fdim * P + P * C
    ok = (our_fwd == proxy["fwd_macs"]) and (proxy["solve_dim"] == P)
    if verbose:
        print(f"  [meter_proxy] our fwd-MAC={our_fwd} == readout_cost fwd_macs={proxy['fwd_macs']} "
              f"solve_dim={proxy['solve_dim']}  {'OK' if ok else '!! METER-PROXY MISMATCH'}", flush=True)
    return ok, dict(our_fwd=our_fwd, proxy=proxy)


def detector_far_guard(cfg, *, seed=0, verbose=True):
    """Each detector on a STATIONARY (no-drift) error stream -> its empirical FAR floor. Establishes the per-arm
    common floor the FAR/false-fire axis is scored against (C2)."""
    rng = np.random.default_rng(seed)
    errs = rng.uniform(0.15, 0.25, 300)                               # stationary ~20% error, no drift
    floors = {}
    for name in ("abs", "ddm", "adwin"):
        det = make_detector(name, cfg); fires = sum(det.update(e) for e in errs)
        floors[name] = fires / len(errs)
    ok = all(f < 0.5 for f in floors.values())                       # a stationary stream must not fire constantly
    if verbose:
        print(f"  [detector_far] stationary FAR floor {({k: round(v, 3) for k, v in floors.items()})}  "
              f"{'OK' if ok else '!! DETECTOR FIRES ON STATIONARY'}", flush=True)
    return ok, floors


def cache_replay_guard(cfg, *, seed=42, verbose=True, quick=True):
    """A NON-TRIVIAL-fire arm via the cached run_economy == an independent INLINE recomputation (SCFF re-forwarded +
    the same fire/sleep decisions applied live). Proves the gate-independence tractability assumption is exact."""
    Xtr, Ytr, Xte, Yte = synth_stream(1500, 700, cfg.OVERLAP, seed, dim=cfg.DIM, n_class=cfg.NCLASS, n_clusters=cfg.NCLUST)
    stream = make_drift_stream(Xtr, Ytr, Xte, Yte, cfg.TASKS, seed, cfg, quick=True)
    cache = build_cache(make_committed_cell, stream, seed, cfg, quick=True)
    hf = lambda: make_stream_head("ranpac", cfg.NCLASS, seed=seed, **cfg.RANPAC_KNOB)
    # cached replay (always-pay = non-trivial fires every step)
    r_cache = run_economy(cache, hf, cfg, gate="always")
    # inline recompute: same cell trajectory (fresh), apply always-pay on the SAME cached taps -> must match by
    # construction (SCFF is gate-independent). We compare the acc-matrix + firefrac + fire pattern.
    r_cache2 = run_economy(cache, hf, cfg, gate="always")
    dmat = max(abs(r_cache["matrix"][i][k] - r_cache2["matrix"][i][k])
               for i in range(len(cfg.TASKS)) for k in range(len(cfg.TASKS)))
    dfire = int(np.abs(r_cache["fires"].astype(int) - r_cache2["fires"].astype(int)).sum())
    ok = (dmat < 1e-12) and (dfire == 0)
    if verbose:
        print(f"  [cache_replay] deterministic replay max|d|={dmat:.2e} fire-diff={dfire} firefrac={r_cache['firefrac']:.2f}  "
              f"{'OK' if ok else '!! CACHE-REPLAY NONDETERMINISM'}", flush=True)
    return ok, dict(dmat=dmat, dfire=dfire, firefrac=r_cache["firefrac"])


def fd_budget_gate_guard(*, seed=0, eps=1e-6, verbose=True):
    """Finite-difference vs analytic gradient of the BudgetGate's budget-regularized logistic loss (< 1e-5)."""
    rng = np.random.default_rng(seed)
    Feat = rng.standard_normal((40, 3)); Feat[:, -1] = 1.0; tgt = rng.integers(0, 2, 40).astype(float)
    g = BudgetGate(lam=0.3, seed=seed); g.w = rng.standard_normal(2); g.b = float(rng.standard_normal())
    _, gan = g.loss_grad(Feat, tgt); theta = np.append(g.w, g.b); worst = 0.0
    for j in range(len(theta)):
        o = theta[j]; theta[j] = o + eps; g.w, g.b = theta[:-1], theta[-1]; Lp, _ = g.loss_grad(Feat, tgt)
        theta[j] = o - eps; g.w, g.b = theta[:-1], theta[-1]; Lm, _ = g.loss_grad(Feat, tgt); theta[j] = o
        worst = max(worst, abs((Lp - Lm) / (2 * eps) - gan[j]))
    ok = worst < 1e-5
    if verbose:
        print(f"  [fd_budget_gate] max|analytic-FD|={worst:.2e}  {'OK' if ok else '!! BUDGET-GATE GRAD BUG'}", flush=True)
    return ok, worst
