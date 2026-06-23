# BYOL — Bootstrap Your Own Latent

*Grill et al., DeepMind, 2020 ([arXiv 2006.07733](https://arxiv.org/pdf/2006.07733)).*

---

## The problem it was stuck on

By 2020, self-supervised learning (learning good features with *no labels*) had a winning recipe: **contrastive learning** (SimCLR, MoCo). Pull two views of the same image together, push views of *different* images apart. It worked — but it lived in fear of one thing and depended on another:

- It **needed lots of negatives** — big batches or big memory banks full of "other images" to push away from. Expensive.
- It was haunted by **collapse**: the trivial cheat where the network maps *everything* to the same constant vector. "Same → close" is trivially satisfied if *everything* is close. The negatives were the guard rail stopping that collapse.

So the field "knew" you needed negatives, both for signal and for safety.

## The one idea that unstuck it

BYOL made a claim that sounded impossible: **learn great features with no negatives at all.** Just "pull same-views together," and somehow *don't* collapse.

The trick is an **asymmetry between a student and a slow teacher:**

- An **online network** (the *student*) — it has an extra little **predictor** head on top.
- A **target network** (the *teacher*) — a *copy* of the student that the student never trains directly. Instead, the teacher's weights are a **slow moving average (EMA)** of the student's: `θ_teacher ← τ·θ_teacher + (1−τ)·θ_student`, with `τ` near 1, so the teacher drifts *slowly* behind.

The student looks at one augmented view and tries to **predict the teacher's representation** of another view. Crucially, **stop-gradient**: no gradient flows into the teacher. The teacher is a slowly-moving target the student chases but can never instantly become.

Why doesn't it collapse? Because of the asymmetry. The student has to *predict* the teacher through an extra head, and the teacher is always a *lagged* version of the student — so "just output a constant" is never the easy equilibrium the way it is in a symmetric setup. The **slow target is the thing that makes a negative-free method stable.** (The exact "why no collapse" is still partly empirical — but it works, robustly, and kicked off a whole family of methods.)

## What it means for us

This is the precedent for our **EMA-view** — the upgrade we keep in our back pocket for when SCFF drifts too fast under GD.

Remember the worry: SCFF never stops learning, so the features GD reads keep *moving*, and GD breaks if they move faster than it can re-track. One fix is the cheap plasticity-gradient (slow the read-layers). The *stronger* fix, if that pinches, is **BYOL's exact move**: let SCFF learn as fast as it wants, but have **GD read a slow EMA copy** of the SCFF read-layers. GD trains against a smoothed, slow-moving target instead of the twitchy live one — and you run inference on that same slow copy, so it stays consistent.

And here's the gift: **our architecture already has BYOL's two anti-collapse ingredients, for free.**

- BYOL needs **asymmetry** → we have it: GD and SCFF are *different modules* with different jobs, not a symmetric siamese pair.
- BYOL needs **stop-gradient** → we have it: GD *reads* SCFF and never writes back into it. That read-only tap *is* a stop-gradient.

So the EMA-view isn't a hopeful guess we'd be inventing — it's a published, battle-tested technique, and we're already standing in the exact structural setup (asymmetric + stop-grad) where it's known to be stable. The only new cost is holding a slow copy of the `n` read-layers (extra capacitors), which is why it stays the *upgrade*, not the default. The one knob that matters is the EMA rate `τ` — too fast and you haven't gained stability; too slow and GD is training on stale features. That `τ` is the same physical "slow clock" idea as the plasticity gradient, just implemented as a copy instead of a brake.
