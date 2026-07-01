"""
p7cfg — the PINNED Phase-7 run config (the no-baseline-drift rule made mechanical). Every rung imports these
constants; none redefines them. Pinned at P7.0 and FROZEN for all later rungs (feature source, PROBE_EP, seeds,
the continual home, the RanDumb expansion). Change one → the whole ladder is inconsistent.
"""
from p7lib import CISTREAM_TASKS

# --- seeds (methodology §5) ---
SEEDS = [42, 137, 271, 314, 1729]                                      # the standard 5
SEEDS9 = SEEDS + [1009, 2027, 9091, 7]                                 # +4 for the <=0.02 spine-tension gap

# --- readout-fit budgets (PINNED at P7.0, frozen for all rungs) ---
PROBE_EP = 120                                                         # gradient-head static readout-fit budget
SLEEP_EP = 60                                                          # continual sleep-refit (consolidation) budget
SCFF_EP = 8                                                            # per-task forward-only bulk training (A6)
STATIC_EP = 25                                                         # static bulk pre-training (the pinned feature bulk)

# --- the continual home (synthetic class-incremental stream; P4.5/P6 shape) ---
DIM, NCLASS, NCLUST = 40, 10, 40
NTR, NTE = 4000, 1500
OVERLAP = 0.6
TASKS = CISTREAM_TASKS                                                 # 10 classes -> 5 tasks of 2
FEAT = "alltap"                                                        # the canonical feature source (P5 peak-acc tap)
TRUNC_K = 3                                                            # the short fixed-reader truncation (secondary)

# --- the RanDumb control (fair expansion, not a matched-64 strawman) ---
RANDPROJ_DIM = 2000

# --- the committed-cell dims are [dim] + [64]*12 (L12, W64) ---
WIDTH, DEPTH = 64, 12
