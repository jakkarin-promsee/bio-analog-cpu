# North-star bridges — what the GD side hands to the thinking brain

*PonderNet (Banino et al. 2021, [2107.05407](https://arxiv.org/abs/2107.05407)); Adaptive Computation Time (Graves
2016); TENT — fully test-time adaptation by entropy minimization ([2006.10726](https://arxiv.org/abs/2006.10726));
plus Active Inference / Free Energy as the home of "correctness is a feeling." **A deliberately light pass** — enough
to know what promotes vs conflicts with the north star, for a clean Phase-6 → Phase-7 hand-off, no more.*

---

## The problem it answers

The north star (held closed, by the author's choice) is a **recurrent, lifelong "thinking" brain where correctness is a
self-generated feeling** — the organs re-wired to run recurrently at inference, *thinking until the feeling crosses θ*.
Stage 2 is *not* that — but the GD side is where two of its seeds physically live (the **gate** = the halt; the
**readout's confidence** = a candidate feeling). So the only question this file answers: **which GD choices we make in
Phase 6 will the north star later thank us for, and which would it have to undo?** We want the Stage-2 report to *hand
off clean*.

## The one idea that unstuck it

The "learned halting" literature is the north star's gate, prototyped on feed-forward nets:

- **PonderNet / ACT** make a network **decide when to stop** — a halting unit emits, at each step, the probability of
  halting *given it hasn't yet*, and the net learns to spend more steps on harder inputs. Map onto us: the **threshold
  gate** ("keep computing cheaply until a signal crosses θ") is the *static, one-shot* version of PonderNet's *recurrent*
  halt. **Build the gate well now and it is the seed of "think until the feeling settles" later** — same object, looped.
- **TENT** adapts a model at test time by **minimizing prediction entropy** — "make myself more confident." It's the
  closest existing thing to "tune toward the feeling of being sure," and it's a *promote*: a readout that can adapt
  online to its own confidence is a step toward a self-grounding loop.

**But here the spine fires a warning, and it is the single most important thing this file says:** PonderNet's halt and
TENT's objective both read **confidence / entropy — which is a *magnitude*.** Phase 5 already struck the confidence-gated
adaptive exit for exactly this reason (confidence is a poor, over-magnitude selector; deeper layers are *more*
overconfident, and early layers are confident-when-wrong). So the naive north-star bridge — *"halt when confident"* —
**conflicts with the spine.** The promote/conflict split:

- **Conflicts:** a halt signal built on softmax confidence / entropy (magnitude). The feeling-as-confidence shortcut is
  the same density≠class trap, one level up. Active-inference's own failure mode is identical — an ungrounded "feeling"
  collapses to *"everything is correct"* (the BYOL-collapse / winner-take-all failure), which is why the north-star
  notes insist the feeling must be **grounded** by prediction-error and occasional real labels.
- **Promotes:** a halt / "where-to-read" signal built on a genuinely **direction** quantity — the **cosine margin**
  (angle to the nearest vs runner-up class) of the direction-readouts ([`direction-readouts.md`](direction-readouts.md)),
  or the **drift detector's** "has the base settled" signal ([`the-economy-gate.md`](the-economy-gate.md)). *(Be careful:
  a Mahalanobis/NCM **distance** is a magnitude, not a direction — the very slip the direction-readouts file corrected;
  so the spine-clean "feeling" candidate is the **cosine margin**, not the prototype distance the first draft named.)*
  These are the *right* seed to plant in Phase 6.

## What it means for us

- **Build the gate as PonderNet's ancestor, but ground it on direction, not confidence.** When Phase 6 picks the gate
  signal, prefer a **direction/drift** signal over a **confidence/entropy** one — not only because it gates better
  *now* (Phase 5 showed confidence is a weak selector), but because it is the signal the north-star loop will want to
  *reuse* as "the feeling." A confidence-based gate would have to be torn out later; a direction-based one is the seed.
- **The parked P5 "better-than-confidence selector" comes home here — and `direction-readouts.md` just handed it a
  candidate.** The oracle per-sample selector reached far above the deployed reader; the spine says the path to it is a
  *direction* signal, not a sharper confidence threshold. That is a north-star problem, correctly parked — but Phase 6
  should leave a clean note: *the selector wants a direction signal.*
- **Keep it closed, but keep the door labeled.** No recurrence, no active-inference machinery in Stage 2 — *simple
  intelligence first.* The deliverable is one paragraph in the Stage-2 report: **"the gate and the readout-confidence
  are the halt and the feeling; we built them on direction signals so the recurrent brain can reuse them; here is what
  would have conflicted."** That's the whole hand-off.
- **The missing third leg: calibration under shift.** *Any* signal we read for halting/exiting — confidence *or* a
  cosine margin — assumes the head's outputs are **calibrated**, and frozen-backbone heads are **systematically
  mis-calibrated under distribution shift** (the calibration-under-shift / TENT line). So even a direction-grounded
  "feeling" needs a calibration check before it's trusted as a gate — a temperature-scaling-style calibration of the
  margin, re-estimated at sleep. This is the literature leg the first draft missed, and it sits between the gate
  ([`the-economy-gate.md`](the-economy-gate.md)) and this file.
- **Caveat — don't over-fit Stage 2 to a north star that isn't specced.** The author chose to hold the thinking brain
  as direction only. So this is a *bias in tie-breaks* (prefer direction-grounded, calibrated gate signals), **not** a
  reason to add scope. If a confidence-based gate decisively wins the Phase-6 economy on its own merits, that's data — we
  note the north-star tension and still report the result honestly.
