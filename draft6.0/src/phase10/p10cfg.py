"""
p10cfg — the PINNED Phase-10 run config. INHERITS every pinned P9 constant (which inherits P8: the committed
cell/head, the streaming schedule, the meter's per-op energy params + citations, the seeds, the lifelong stream,
the frozen-object knobs) via `from p9cfg import *`, then ADDS only the P10-new knobs (the fair BP+replay racer
budget + tuning protocol, the multi-domain gauntlet, the held-out noise battery, the eval-checkpoint grid).

Phase 10 is VALIDATION, not tuning: these knobs configure the *measurement apparatus* (the racer field, the
gauntlet, the noise battery) — none touches a LEARNED knob of the frozen object. The only object dial that moves
is the declared cadence cost axis (grid ∈ {4,5,6,8,16}); grid-4 is the committed frozen headline (design §0.1).

Discipline: the verdict SHAPES are pinned BLIND (design §2.3); ER-strong is tuned only on a DISJOINT tuning stream
(seed ∉ the raced set) — the raced seeds are never consumed during tuning (K2).
"""
import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "phase9"))
from p9cfg import *                                                    # noqa: F401,F403  (inherit ALL pinned P9/P8 constants)

# ============================================================ the cadence cost-frontier family (the declared axis)
# The frozen object is grid-4 (COMMITTED_LOOP + cadence_every=4); the family varies ONLY the sleep interval. Tier-1
# {4,5,6} = the sweet spot; Tier-2 {8,16} = the degradation arms (grid-8 fails the P9 veto, grid-16 fails AA-held).
# grid-2 is omitted as the dense end past the knee (design §0.1) — addable if the frontier wants extending.
CAD_FAMILY = [4, 5, 6, 8, 16]
CAD_TIER1 = [4, 5, 6]
CAD_TIER2 = [8, 16]
CAD_HEADLINE = 4                                                       # the committed frozen headline — NEVER swapped

# ============================================================ the fair BP+replay racer (P10.0/P10.1 — the anti-strawman)
# The load-bearing opponent is a BUDGETED, TUNED experience-replay (Prabhu CVPR'23: ER is strong under a matched
# FLOPs/sample + memory-bytes budget). OURS's hippocampus LUT = the fixed raw-prototype probe (PROBE_N raw samples);
# byte-matching (both store raw DIM-D samples + a label) => the ER-budget buffer cap == PROBE_N samples.
BP_TUNE_SEED = 7                                                      # the DISJOINT tuning stream seed (∉ SEEDS) — K2
BP_TUNE_LRS = [1e-2, 3e-3, 1e-3, 3e-4]                                # the ER-strong lr search grid
BP_TUNE_REPLAY = [16, 32, 64]                                        # replay minibatch-size search (ER-strong)
BP_DEPTHS = [2, 3]                                                    # race_bp shape search (matched-weight MLP)
BP_EP_TUNE = 40                                                       # offline tuning-stream epochs for shape/lr search
ER_BUDGET_REPLAY = 8                                                 # ER-budget: throttled replay (matched to OURS's FLOPs)
ER_BUDGET_BUFFER = None                                              # None => byte-match to OURS's LUT (PROBE_N raw samples)
DERPP_ALPHA = 0.5                                                    # DER++ logit-distillation weight (Buzzega NeurIPS'20)
DERPP_BETA = 0.5                                                     # DER++ replay-CE weight
JOINT_BP_EPOCHS = 60                                                # the offline joint-BP CEILING (pooled data, multi-epoch)

# ============================================================ the multi-domain gauntlet (P10.3 — the money figure)
# Domain-IL (van de Ven): the SAME 10 classes across domains, a domain-specific INPUT transformation; a SHARED head.
# Base = 8x8 digits (recognizable, offline via sklearn.datasets.load_digits — DATA-only, no OpenMP). ONE pinned
# projection mechanism (seed-frozen random Gaussian, native-dim -> DIM=40, matched to how the synth home is 40-D)
# applied identically to every domain; every learner consumes the BIT-IDENTICAL projected 40-D stream (K5).
GAUNTLET_DOMAINS = ["identity", "permuted", "rotated", "covariate", "noised"]   # the 5 native domain-IL worlds
GAUNTLET_PROJ = "gauss"                                              # the ONE pinned ->40 mechanism (seed-frozen random Gaussian)
GAUNTLET_DIM = 40                                                    # the shared bulk input dim (== DIM; frozen bulk needs it)
GAUNTLET_NTR = 1200                                                 # per-domain train pool (digits has ~1797 total)
GAUNTLET_NTE = 500                                                  # per-domain held-out eval pool
GAUNTLET_COV_GAIN = 3.0                                              # 'covariate' domain: layernorm-invariant gain (nuisance-style)
GAUNTLET_COV_OFFSET = 4.0                                            # 'covariate' domain: all-ones offset
GAUNTLET_NOISE_RMS = 0.6                                             # 'noised' domain: iid Gaussian input RMS
GAUNTLET_ROT_DEG = 90                                               # 'rotated' domain: fixed image rotation (8x8 grid)

# ============================================================ the held-out noise battery (P10.4 — margin-disjoint)
# The showcase battery is a MARGIN-DISJOINT operating point of p6lib.NoiseModel vs P9.4's home residual
# (RESID_INPUT_RMS=1.5, RESID_ADC_BITS=2). Disjoint => a higher directional RMS + a distinct structure, so a
# "payoff" claim is honest (genuinely-novel) vs a "confirms P9.4" downgrade (re-parameterized) — design §2.3-P10.4.
NOISE_ENVS = ["clean", "iid", "directional", "adc3b", "nuisance"]    # the 5 held-out environments
NOISE_HOLDOUT_INPUT_RMS = 2.5                                        # directional RMS (disjoint > P9.4's 1.5 + a margin)
NOISE_HOLDOUT_ADC_BITS = 3                                           # sub-3-bit-ish ADC arm (adc3b; disjoint from P9.4's 2)
NOISE_IID_RMS = 1.0                                                 # the iid channel RMS
NOISE_NUISANCE_GAIN = 3.0                                            # the nuisance-dim channel (layernorm-invariant covariate)

# ============================================================ the eval-checkpoint grid (K12 — learner-independent)
# A fixed, learner-independent eval-checkpoint grid: OURS's sleep-interval / task boundaries applied to EVERY learner
# so the worst-pre-sleep read is symmetric (no asymmetric read can be invented). The canonical checkpoints (task
# boundaries) are the pinned grid; the lifelong monitor points extend it.
EVAL_ON_CHECKPOINTS = True                                          # eval every learner on the stream's canonical checkpoints

# ============================================================ verdict constants (PINNED BLIND — carried; restated)
# DELTA_ACC = 0.02 and GD_SHARE_CAP = 0.25 inherited from p9cfg. The paired-sign veto + IQR-disjoint real-difference
# rule live in p9run (real_diff / paired_sign_neg). Decisive gaps <= DELTA_ACC escalate to SEEDS9 (9 seeds).
