# Experiment P4.3-decay — WHY does OURS decay with depth? (width is not the lever)

> **Status: ✅ DONE (2026-06-24; figures extended 2026-06-25).** Follow-up to A4: P4.3 showed OURS's last-layer
> accuracy droops past ~L5 even at fixed width (depth-decay, not the iso width-shrink). Two hypotheses — **(H1)
> class-collapse from too-few effective neurons** (shrinking width destroys class structure; even fixed width loses
> to **dead neurons** accruing at depth), tested by **widening each layer with depth**; and **(H2)** how a **mixed
> flat+headroom** task behaves and whether the flat subtask (solved early) is **corrupted** by the deeper layers.
> Width sweep: arms `fix64` / `widen`, depths `[2,3,4,6,8,10,12]`, OURS, per-layer probe/dead/erank. Mixed sweep:
> **iso-budget widths (W109→W30, matching WIDTHxDEPTH)**, same depths, OURS **vs tuned BP** (overall + per subset).
> 5 seeds. Run: `OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_3_decay.py`. Apparatus:
> `run_p4_3_decay.py` + `plot_p4_3_decay.py`, figs in `figs_p4_3_decay/`.

---

## The 6+2 slot read

**1 · Claim.** **Widening does NOT fix the decay — capacity is not the cause (H1 refuted).** `fix64` (W64 constant)
and `widen` (W = 64 + 16·layer → deep layers up to **W240** at L12) **decay to the same accuracy** by L12 (flat
0.647 vs 0.642; headroom 0.449 vs 0.441), both **crossing from above-BP at L2–L6 to below-BP by L8** on headroom.
The per-layer diagnostics kill both capacity sub-hypotheses: **dead-unit fraction ≈ 0.00 at every layer** (not dead
neurons), and **effective rank declines but `widen` carries much higher rank (18.7 vs 12.3 @L12) at identical
accuracy** — so the lost rank is a *symptom*, not the binding constraint, and the dims `widen` adds are **not
class-aligned**. The separability probe **peaks at layer ~4–5 then erodes for both widths**. ⇒ the decay is the
**per-layer local contrast objective drifting the representation off the class manifold past ~layer 5**, independent
of width. **The MIXED task (H2) confirms it operationally:** it is **flat-good / headroom-weaker** (not
both-medium), and the flat subtask, readable by layer 2–3 (probe ~0.67), is **actively corrupted by the deeper
layers** (decays to ~0.51 by L12) — while **tuned BP holds flat across depth** (flat subset steady ~0.75), so the
corruption is OURS-specific, not the task's fault.

**2 · Number** (median, n=5):

*Width sweep — last-layer readout accuracy (representative of the 7-depth sweep; full curve in `WIDEN_ACC`):*
| L | flat fix64 | flat widen | head fix64 | head widen |
| --- | --- | --- | --- | --- |
| 4 | 0.731 | 0.749 | 0.565 | 0.556 |
| 8 | 0.679 | 0.673 | 0.500 | 0.528 |
| 12 | 0.647 | **0.642** | 0.449 | **0.441** |

*Width sweep — L12 mechanism diagnostics (last layer, headroom):*
| arm | dead-frac | effective rank | probe peak → L12 |
| --- | --- | --- | --- |
| fix64 | 0.00 | 12.3 | 0.540 (L5) → 0.435 |
| widen | 0.00 | 18.7 | 0.553 (L5) → 0.443 |

*Mixed task — per-subset accuracy, OURS vs tuned BP (iso-budget):*
| L/W | OURS all | BP all | OURS flat | BP flat | OURS head | BP head |
| --- | --- | --- | --- | --- | --- | --- |
| L2/W109 | 0.591 | 0.605 | 0.712 | 0.731 | 0.471 | 0.464 |
| L4/W64 | 0.607 | 0.627 | 0.709 | 0.757 | 0.505 | 0.499 |
| L8/W40 | 0.509 | 0.613 | 0.585 | 0.752 | 0.404 | 0.473 |
| L12/W30 | **0.445** | 0.608 | **0.507** | 0.751 | **0.343** | 0.464 |

Mixed per-layer probe at L12: flat subset **~0.47 (L1) → 0.67 (L3–4 peak) → 0.51 (L12)**; headroom ~0.38 → 0.47
(L3) → 0.35 (L12). **Both peak ~layer 3–4 then decay; BP holds both subsets flat across depth** (flat ~0.75, head
~0.47) — OURS matches BP at L2–L4 (even edges it on headroom) then falls away as it decays.

**3 · Figures.** `WIDEN_ACC` (fix64 ≈ widen at all 7 depths, both decay below the flat BP line by L8 — widening
doesn't help) · `WIDEN_DIAG` (the mechanism: probe peaks L4–5 then decays for both; **dead-fraction flat at ~0**;
erank declines but widen's higher rank buys no accuracy) · `MIXED` (OURS vs BP per-subset: BP holds flat with
depth, OURS decays; per-subset probe shows the flat subtask peak ~L3–4 then **decay through the deep layers**).

**4 · Mechanism.** Every layer applies its own local InfoNCE; with no signal to **preserve** already-class-relevant
structure, repeated local transforms steer the representation toward *some* informative-but-not-class-aligned code,
so class separability peaks (~L5, where the window's coordination still helps) then erodes. Width is irrelevant
because the problem is **direction of the representation, not its dimensionality** — `widen` has more live, higher-
rank units that don't carry more *class* information. The mixed task makes the corruption visible against a
non-decaying ceiling: BP keeps the easy flat subtask at ~0.75 across depth, while OURS's deep layers, applying the
local objective, overwrite the flat subtask's early-solved code.

**5 · Threats.** (a) **Under-training still untested** — all depths share `ep=25, lr=0.03`; a depth-scaled lr /
more passes *could* push the peak deeper. But the **peak-at-~5-then-decay shape is identical across both widths,
both regimes, and both mixed subtasks**, which argues objective-drift over an optimization shortfall (a
depth-scaled-training control is the clean P5 check). (b) One widen schedule (linear +16/layer) and one budget. (c)
`widen` at L12 reaches W240 — far past any plausible Scap budget — and *still* doesn't help, so the negative is
robust to "not wide enough." (d) erank is on a centered activation matrix (the standard read).

**6 · Decision.** **Width is NOT the depth lever — do not widen to fix depth (it costs more for nothing).** The
decay is intrinsic to stacking the local objective, so the fix is **preservation, not capacity:** (i) the deployed
**all-tap / boosting readout is the right answer** (reads the ~L5 peak instead of the decayed top — doubly
vindicated, here and in A4); (ii) **residual / skip connections** are the clean P5 architectural candidate (let deep
layers *add to* rather than *overwrite* the representation); (iii) **useful composition depth ≈ 5 layers** for this
cell — "how deep can we use it" has a number; (iv) run the **depth-scaled-training control** before declaring the
~5-layer ceiling fully intrinsic.

**7 · Cost-honesty.** Width arms are OURS-only diagnostics; the mixed task adds a **genuinely-tuned BP** reference
(same grid/budget as the A4 racers) — and BP **holds flat with depth** while OURS decays, so the gap is real, not a
weak baseline. `widen` strictly *increases* weight/compute cost (W up to 240) for **no accuracy gain** → widening is
a cost-benefit loss, reported as a refuted fix, not a config.

**8 · Map-contribution → P5.** The A4 depth-decay has a **named cause (local-objective drift) and a named non-fix
(width)**. Tells P5: (a) **add a preservation path** — residual/skip and/or keep all-tap/boosting (not a deeper
single stack, not a wider one); (b) **target ~5 composing layers**, stack shallow blocks for more depth (the
boosting design); (c) **test depth-scaled training** to bound how much of the ~5-layer ceiling is optimization vs
objective. The mixed-task corruption — deep layers overwrite early-solved structure while BP doesn't — also flags a
**continual-learning risk**: the sleep/replay mechanism (A6) must protect early-solved representations.

---

## Reproducibility

`figs_p4_3_decay/{manifest.json, arrays.npz, _ckpt.jsonl, run_full.log}`; `python plot_p4_3_decay.py
figs_p4_3_decay`. Single-threaded, `python -u`, `PYTHONIOENCODING=utf-8`, per-cell fsync; verified alive mid-run.
Pure numpy hot path (numpy linear probe + `effective_rank`; no sklearn → no OpenMP phantom). OURS trained inline
(`SCFFContrastOLU`, w=2); diagnostics = per-layer linear probe, `dead_fraction`, `effective_rank`; mixed BP via
`race_bp(..., te_masks=...)` (per-subset). Checkpoint keyed by `(part, …)`: `part="width"` (arm·regime·L·seed) +
`part="mixed"` (L·seed). New files: `exp3/run_p4_3_decay.py`, `exp3/plot_p4_3_decay.py`.
