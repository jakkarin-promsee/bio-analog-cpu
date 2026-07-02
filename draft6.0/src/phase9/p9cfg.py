"""
p9cfg — the PINNED Phase-9 run config. INHERITS every pinned P8 constant (the committed cell/head, the streaming
schedule, the meter's per-op energy params + citations, the seeds) via `from p8cfg import *`, then ADDS only the
P9-new knobs (the lifelong stream, the N2 arms, the consolidation-depth set, the bounded-LUT eviction caps, the
read-side residual channel). Change one and every drift/N2/depth/eviction/residual number downstream is inconsistent.

The discipline P9 rides on: these knobs are tuned against INTERNAL signals only (measured drift, BWT vs the
frozen/oracle reference, metered energy) — never the P10 BP+replay baseline (freeze in P9, judge in P10).
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "phase8"))
from p8cfg import *                                                    # noqa: F401,F403  (inherit ALL pinned P8 constants)

# ============================================================ the LIFELONG stream (P9.0 — drift must accumulate)
# P8's schedule is a single pass (warmup -> 4 gradual onsets -> settle -> nuisance). A lifelong stream RE-VISITS the
# tasks for several cycles so the SCFF representation keeps drifting past the single-pass regime -> the 'does the bulk
# forget?' question is asked on accumulated, not one-shot, drift. The revisit block rotates the batch emphasis across
# all seen classes (each task re-emphasized in turn), all classes present, no new labels -> pure continued drift.
LIFE_CYCLES = 2             # number of RE-VISIT cycles after the initial CI introduction (0 == the P8 single pass)
LIFE_REVISIT = 20          # steps per re-visited task inside a revisit cycle (emphasis rotates task-by-task)
LIFE_PROBE_EVERY = 6       # grid stride for the drift-probe instrument (reps_probe stored here; coarser = less RAM)
EARLY_N = 200              # held-out EARLY-TASK (task-0) eval size for the destruction curve (Davari 2203.13381)
PROBE_FIT_RIDGE = 1e-1     # ridge for the re-fit / frozen linear probes in probe_retention (well-conditioned 768-D)

# ============================================================ N2 (P9.1 — the last open decision-record knob)
# EMA-view: the namer reads a per-tap EMA of the features (read-side, SCFF untouched — the doubly-grounded default).
# LLRD-rate: a LLRDCell subclass slows the LATE-read layers' SCFF update (rate-only IFF the representation guard holds).
N2_EMA_BETAS = [0.3, 0.1]  # EMA-view smoothing (lower = slower view); raced to find the drift-reducing setting
N2_LLRD_RHOS = [0.5, 0.25]  # LLRD late-layer learning-rate multipliers (rho<1 slows the late-read layers)
N2_LATE_LAYERS = 4         # how many FINAL layers LLRD slows / EMA smooths (the 'read' band, matches the trunc reader)

# ============================================================ consolidation depth (P9.2 — latent-replay layer)
# The sleep re-fit re-forwards the LUT and rebuilds the Gram at a chosen feature DEPTH. all-tap = P8 (all L reps);
# trunc-K = the deployed short reader (last K); per-depth = a single sharp layer.
SLEEP_DEPTHS = ["alltap", "truncK", "perdepth"]
SLEEP_TRUNC_K = 3          # the trunc-K depth (== the P5 fixed-reader / p8cfg.TRUNC_K)
SLEEP_PERDEPTH_K = 3       # the single sharp layer for the per-depth arm (last K==this reduces to one slice band)

# ============================================================ bounded-LUT eviction (P9.3 — the new StreamingLUT)
# P8's streaming sleep re-solves over a FIXED balanced probe (no growing history). A lifelong stream forces a BOUNDED,
# EVICTING store. The cap is pinned at a PRESSURE POINT (C7): small enough that the bound bites (few exemplars/class).
EVICT_POLICIES = ["oracle", "cbrs", "reservoir", "recency", "herding"]
EVICT_CAP = 120            # bounded-LUT cap at the pressure point (~12 exemplars/class over 10 classes)
EVICT_CAP_SCALING = [40, 80, 120, 200, 400]   # cap x #classes scaling sub-sweep (separate sub-table)
EVICT_APPEND_EVERY = 2     # append a prototype batch to the streaming LUT every k steps (the growing history)

# ============================================================ read-side noise residual (P9.4 — conditional)
# The Phase-6 residual = the INPUT-TRANSDUCER directional channel + ADC<3-bit (the channel SCFF's per-sample norm
# CANNOT remove forward-only) — injected with p6lib.NoiseModel, NOT p8's layernorm-invariant nuisance (which SCFF
# removes by construction -> a vacuous probe). Earn-its-place gate: does it dent the committed SLDA loop by > delta_acc?
RESID_INPUT_RMS = 1.5      # input-transducer directional RMS (projected-RMS on the class axis)
RESID_ADC_BITS = 2         # sub-3-bit ADC on the read (the Phase-6 named residual)
RESID_COMMON_MODE = 0.0    # common-mode is handled by the differential front end; residual is the directional part

# ============================================================ verdict constants (PINNED BLIND)
DELTA_ACC = 0.02           # the house bar (paired, IQR-disjoint + >=4/5 sign)
GD_SHARE_CAP = 0.25        # the metered economy the P9 tuning must not inflate
SLEEP_COST_ERATIO = 1.5    # P9.2 adopts trunc-depth only at >= this sleep-cost saving (frontier-knee, not hard-binary)
