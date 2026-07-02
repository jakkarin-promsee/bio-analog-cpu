"""
p8cfg — the PINNED Phase-8 run config (the no-baseline-drift rule made mechanical). Every rung imports these
constants; none redefines them. Pinned at P8.0 and FROZEN for all later rungs (the committed cell/head, the
continual home, the streaming schedule, the meter's per-op energy params + citations, the seeds). Change one and
every MTD/FAR/cadence/energy number downstream is inconsistent.
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "phase7"))
from p7lib import CISTREAM_TASKS

# --- seeds (methodology §5) ---
SEEDS = [42, 137, 271, 314, 1729]                                      # the standard 5
SEEDS9 = SEEDS + [1009, 2027, 9091, 7]                                 # +4 for <=0.02 decisive gaps

# --- the committed cell + head (frozen-as-a-DESIGN; Phase 8 turns on the LIVE loop, reopens no knob) ---
DIM, NCLASS, NCLUST = 40, 10, 40
NTR, NTE = 4000, 1500
OVERLAP = 0.6
TASKS = CISTREAM_TASKS                                                 # 10 classes -> 5 tasks of 2
WIDTH, DEPTH = 64, 12                                                  # dims = [DIM] + [64]*12
FEAT = "alltap"                                                        # the canonical readout feature source
TRUNC_K = 3

# committed namer (P7): RanPAC + cbrs; SLDA = the metered cost fallback (P8.4 decides).
COMMITTED_HEAD = "ranpac"
COST_FALLBACK_HEAD = "slda"
RANPAC_KNOB = {"proj_dim": 2000, "ridge_lambda": 1.0}                  # the P7.1-selected knob
SLDA_KNOB = {"shrinkage": 1e-3}
CBRS_CAP = 800                                                        # class-balanced-reservoir buffer cap (P7.3)

# --- readout/consolidation budgets (carried from P7; frozen) ---
SCFF_EP = 8                                                          # per-task forward-only bulk training (block mode / A6)
STATIC_EP = 25                                                       # static bulk pre-train (the frozen-guard path)
SLEEP_EP = 60                                                        # gradient-head sleep-refit budget (MLP only)

# ============================================================ the STREAMING schedule (P8.0 pins + justifies it)
# The reframe's "every input, forward-only" regime: SCFF trains on each mini-batch; class onset is GRADUAL (a mix
# ramp), so representation drift is CONTINUOUS, not the stepwise per-task-block boundary the inherited harness had.
BATCH = 32
WARMUP_STEPS = 40           # SCFF pre-stream warmup on task-0 classes (unscored) so the stationary floor is meaningful
STAT_STEPS = 40             # stationary segment length (classes fixed, no nuisance) -> the FAR / MTFA floor
ONSET_RAMP = 24             # gradual class-onset ramp length (mix prob 0 -> ONSET_MIX over these steps)
PLATEAU = 24                # steady segment after each onset
ONSET_MIX = 0.5             # steady-state fraction of the batch drawn from the newest task at plateau
SETTLE_STEPS = 40           # all-class no-nuisance segment BEFORE nuisance; its interior = the clean FAR/MTFA floor
NUIS_STEPS = 48             # nuisance-covariate segment length (all classes seen; boundary intact)
STAT2_STEPS = 16            # short post-nuisance recovery (bulk_drift viz only; NOT a calibration reference)
NUIS_GAIN = 3.0             # covariate ramp: input gain g (layernorm removes it -> class direction invariant)
NUIS_OFFSET = 4.0           # covariate ramp: all-ones offset alpha (layernorm removes it -> class direction invariant)
PROBE_N = 600               # fixed probe set size for bulk_drift + the tap-drift detectors
EVAL_N = 900                # fixed eval subset (per checkpoint accuracy-held / the acc-matrix)

# --- default awake-gate / sleep knobs (the sweep ranges live in the run scripts) ---
ABS_THETA = 0.55            # absolute-theta gate default (error-rate threshold on the batch)
DDM_WARN, DDM_DRIFT = 2.0, 3.0     # DDM sigma multipliers (warning / drift)
ADWIN_DELTA = 0.05          # ADWIN confidence delta
EMA_BETA = 0.3              # error-EMA smoothing
DRIFT_WIN = 8               # reference window (steps) for the tap-drift / DriftLens detectors
WIN_W = 4                   # MMD current-window width (mini-batches) for the trigger signals
WIN_LAG = 8                 # MMD lagged-reference offset (steps) -- makes each signal a CHANGE detector
SLEEP_EVERY = 2             # default detector-driven sleep cadence proxy (sleeps per real onset) -- swept in P8.3
LUT_FRAC = 1.0              # fraction of replay history re-forwarded at sleep -- swept in P8.3
LAM_EMA = 1.0               # running-Gram EMA decay (1.0 = pure cumulative) -- swept in P8.3

# ============================================================ the behavioral ADC-centred cost meter (§2.3)
# Literature-calibrated RELATIVE per-op energies (NeuroSim / ISAAC / PUMA level; tagged BEHAVIORAL, sensitivity-swept).
# Anchors (cite in manifest): SAR-ADC ~0.2 pJ/conversion-step, energy ~x2 per effective bit; crossbar 8-bit MAC <100 fJ;
# ADCs 5-50x crossbar area + ~half tile energy (ISAAC); weight write large but rare (write-verify).
ADC_BITS = 8
E_ADC_STEP = 0.2            # pJ per SAR conversion-step  -> e_ADC(b) = E_ADC_STEP * b
E_MAC = 0.01               # pJ per scalar analog crossbar MAC (8-bit MAC << 100 fJ; ADC >> MAC per op)
E_WRITE = 10.0             # pJ per weight write (capacitor/RRAM program w/ write-verify; large, rare)
E_DIGITAL = 5e-4           # pJ per digital FLOP (the ridge/tied-cov solve = the non-free digital block)
METER_CITE = {
    "sar_adc_pJ_per_step": E_ADC_STEP, "adc_energy_x2_per_bit": True,
    "crossbar_8b_mac_fJ": "<100", "adc_area_vs_crossbar": "5-50x", "isaac_adc_share": "~half tile energy",
    "refs": ["DNN+NeuroSim", "ISAAC ISCA'16", "PUMA ASPLOS'19", "AIHWKit", "SAR-ADC Walden FoM"],
    "scope": "behavioral macro-model, relative-energy pJ, NOT SPICE",
}
