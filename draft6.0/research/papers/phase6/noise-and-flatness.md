# Noise and flatness — where does robustness live? (the existential one)

*Training with Noise = Tikhonov (Bishop, Neural Computation 1995 — **input** noise); SAM (Foret et al. 2020,
[2010.01412](https://arxiv.org/abs/2010.01412)); S-SGD symmetric **weight**-noise → flat minima
([2009.02479](https://arxiv.org/abs/2009.02479)); replay×sharpness MGSER-SAM ([2405.09492](https://arxiv.org/abs/2405.09492)).
The part the literature already answers: analog in-memory HW-aware training (Rasch et al., Nat. Comm. 2023,
[link](https://www.nature.com/articles/s41467-023-40770-4)); a frozen head **preserves but can't create** backbone
robustness — LP-FT (Kumar et al., [2202.10054](https://arxiv.org/abs/2202.10054)) and backbone-robustness
([2305.17438](https://arxiv.org/abs/2305.17438)); representation drift is real — Probing Representation Forgetting
([2203.13381](https://arxiv.org/abs/2203.13381)).*

> **Correction note (post critic-pass).** Two attribution slips fixed below: **Bishop's theorem is about *input* noise,
> not weight noise**; and the substrate's directional mismatch was wrongly grounded in north-star file 18 (which says
> the *slow/common-mode* part is the **subtractable** enemy). More importantly, the critics showed the existential
> question is **partly pre-answered by literature this file already cites — and it leans toward the arc-rethink
> branch.** This version says so honestly.

---

## The problem it answers — and why it is *primary*, not deferred

The kickoff rule is "we live in numpy; analog/hardware-aware training is **secondary**." **One thing breaks that rule
and the author flagged it himself:** Phase 4's **A7** — the cell is **sensitive to eval-time weight noise** (the
per-sample L2 norm that makes it nuisance-robust is *also* what makes it noise-sensitive), and on an analog substrate
the dominant mismatch is **directional**, attacking the very class-direction the design exists to preserve. The
architecture file calls this **"the sharpest open silicon risk."** The author's reasoning for why it can't wait:

> Train-with-noise is primary too — eventually we have to know **where** we fix this noise problem. If the 20% GD
> *also* can't take it… that means we have to rethink at whole-arc scale again. 💀

So the existential question: **noise-robustness has to be absorbed *somewhere*. SCFF's per-sample-norm machinery is the
*source* of the sensitivity, so it probably can't self-heal. Can the GD readout absorb it — and if not, what does that
tell us about the arc?**

## The one idea that unstuck it (with the two noise channels kept separate)

The literature gives a clean answer to *what robustness is*, and it unifies generalization with noise-tolerance — but
**the mechanism depends on which noise channel you mean,** and the first draft blurred them:

- **Input/activation noise → Bishop's Tikhonov result.** Bishop 1995 proves that injecting **small-variance input
  noise** during training adds, to first order, a **Jacobian-smoothness (Tikhonov) penalty** (derived for a
  sum-of-squares loss). This is the channel for **noise on the *features* the readout reads** — the SCFF taps, and any
  ADC quantization on them. Bishop is the right citation *here* and only here.
- **Weight noise → flat minima (a *different* mechanism).** Robustness to perturbing the **weights** (= noisy analog
  charge) is the **flat-minimum** story: a flat minimum is one where moving the weights barely changes the loss, which
  is *simultaneously* "generalizes well" and "survives weight perturbation." **SAM** ([2010.01412]) targets flatness
  directly; **S-SGD** ([2009.02479]) reaches it by **injecting symmetric weight noise** during training — *this* is our
  noisy-charge case, **not** Bishop. So the unification is real — generalization = flatness = perturbation-robustness —
  but it is reached by **two different levers for two different channels**: inject input noise (Bishop) *or* injure the
  weights toward flatness (S-SGD/SAM).
- **The seam to maintenance — as a hypothesis, not an identity.** **MGSER-SAM** ([2405.09492]) is replay + sharpness-aware
  updates, i.e. sleep-consolidating toward a *flat* readout. It is *suggestive* that our sleep loop and our noise problem
  could be one update — but MGSER-SAM was validated for **forgetting**, not for **analog weight-noise tolerance**, so we
  carry it as **a hypothesis to test at sleep**, not a near-identity.

## The part the literature already settles — and why it points to the harder branch

This is the finding that reshapes Phase 9. **Two results the package already cites jointly predict the *NO* branch:**

1. **A frozen backbone caps the head's robustness.** The linear-probe-robustness line — **LP-FT** ([2202.10054]) and
   "backbone matters for adversarial robustness" ([2305.17438]) — shows a **trained head *preserves* but cannot
   *manufacture*** robustness the features lack. If A7's sensitivity originates **in SCFF's representation** (and the
   per-sample norm strongly suggests it does), then **training the readout with noise *cannot* fix it** — the fix would
   have to be upstream, in the SCFF objective.
2. **We may be probing the wrong noise channel.** Rasch 2023 (our own analog cite) finds that in analog in-memory
   compute, **input/output and ADC-quantization noise dominate the accuracy loss — not weight noise — and the
   *output/readout* layer is the precision-critical one.** A7 was framed as **weight** noise; the hardware says the
   **activation/tap/ADC** channel is the bigger threat. If Phase 9 stress-tests only weight noise, it could **declare
   victory against the weaker enemy.**

So the honest prior going *into* Phase 9 is: **the hoped-for "the readout absorbs it" is the *less* likely branch, and
the channel that matters most is the one the readout *reads* (its input taps), not its own weights.** That doesn't make
Phase 9 unnecessary — it makes it sharper and falsifiable, with the expectation set correctly instead of optimistically.

## What it means for us

- **Phase 9 is an arc-diagnosis, and the literature has set the odds.** Run train-with-noise on the **right channels**
  (input/tap/ADC quantization via Bishop; weight noise via S-SGD; ideally both) + a flatness probe, and watch where
  robustness has to come from:
  1. **YES (the readout absorbs A7):** robustness lives in the 20%, the cheap brain stays, the fix is *how we consolidate*
     (MGSER-SAM-style flat sleep). The literature says **don't bet on this** for sensitivity that originates upstream —
     but a clean YES would be a real, surprising result.
  2. **NO (sensitivity is upstream in SCFF):** the per-sample-norm objective has to change (a **noise-aware SCFF
     objective**), which reopens Stage 1. **The literature *favors this branch* — so we should pre-budget for it**, not
     treat it as the unlikely tail. We want to find it out now, cheaply, in numpy, before silicon.
- **Test the channel the hardware says matters.** Make **input/tap/ADC-quantization noise primary** in the probe (Rasch),
  with weight noise secondary — the inverse of the first draft. The cheap **P0 de-risk probe** (design §4) should already
  inject *tap* noise, not just weight noise.
- **Directional, structured, slow — re-grounded correctly.** A7's enemy is **directional** noise aligned with the class
  axis. Per the architecture file's A7 (§2.3) — *not* north-star file 18 — the slow/common-mode part of analog drift is
  the part draft-5's differential/auto-zero circuitry **already subtracts** (that's file 18's actual claim); what Phase 9
  must test is the **residual directional mismatch that survives auto-zero**, which *sharpens* (does not weaken) the
  existential question. Generic i.i.d. Gaussian noise is the easy version; the honest test is **structured directional**
  noise.
- **Flatness is the unifying target, and we may be half-built for it.** SGD noise, the chip's own analog noise, and (at
  sleep) S-SGD/SAM all push toward flat minima — which are *also* the generalization the continual home wants. The
  capacitor-leak "free L2" (designed, untested) and the per-sample norm are weak flatness pressures already present. So
  the experiment is "**measure the flatness we have, pull it with the cheapest lever (noise injection at sleep), and see
  if the tap-channel robustness reaches the readout.**"
- **Caveat — and watch the bulk, too.** "Only the readout is replayed; the bulk doesn't forget" assumes the frozen-to-GD
  bulk doesn't drift. SCFF is unsupervised and *still updating*, and representation drift in self-supervised continual
  learning is a measured phenomenon ([2203.13381](https://arxiv.org/abs/2203.13381)). If the bulk drifts, stored
  tap-features go stale — which is *both* a maintenance issue and a noise-like perturbation the readout must tolerate.
  Measure the bulk-drift rate; don't assume it's zero.
