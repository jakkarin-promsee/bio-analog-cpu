# Slow coordination — what is allowed to live between SCFF layers

*Mean Teacher (Tarvainen & Valpola 2017); momentum encoders — MoCo, BYOL ([2006.07733](https://arxiv.org/abs/2006.07733)),
DINO; "On the Pros and Cons of the Momentum Encoder" ([2208.05744](https://arxiv.org/abs/2208.05744)); stop-gradient
(SimSiam); Lookahead ([1907.08610](https://arxiv.org/abs/1907.08610)). This file also records **why boosting-blocks are
dropped.***

---

## The problem it answers — and the kickoff decision behind it

At Stage-2 kickoff the author made a call that reshapes the whole GD side: **boosting blocks are out.** The reasoning,
in his words: a GD-write step *"moves faster toward a new optimum and destroys the unsupervised SCFF base underneath
it. At batch 1, SCFF gets a first-generation view of the data; then GD destroys the shape of that first generation and
pushes it to a second generation — and even though the input is the same, SCFF now sees it as new, different data."*
The generalization:

> **Anything that sits between or under SCFF must be unsupervised, or a slow model that doesn't shift all the labels at
> once. Fast + supervised + upstream-of-SCFF breaks the base.**

This kills the residual **boosting chain** (the old N3): a chain feeds each block's GD-corrected residual into the
*next* block's SCFF, which is precisely "a fast supervised thing upstream of SCFF." It also retires the **Interface-GD
organ** (no blocks → no per-block-exit tracker) and the **inter-block direction-chaining** (Ch9 delta). The committed
era is **one big SCFF bulk + per-depth GD readout heads, read-only.** So the live question becomes: *if we ever want
something to coordinate across SCFF depth, what is allowed?* The answer is **slow** or **unsupervised** — and the
self-supervised literature has spent years building exactly that.

## The one idea that unstuck it

The whole modern SSL stack is built on **letting a downstream/target signal influence an encoder without destabilizing
it — by making that signal *slow*.** The device is the **EMA (exponential-moving-average) "teacher" / momentum
encoder**: MoCo, BYOL, DINO, Mean Teacher all keep a copy of the network whose weights are a slow EMA of the live
weights, and train against *that* slow copy. Two of its properties are the exact tools we need:

- **Slow = stable = safe to put near the base.** The EMA teacher changes smoothly, so the thing reading it sees a
  stationary-ish target instead of a thrashing one. "On the Pros and Cons of the Momentum Encoder"
  ([2208.05744](https://arxiv.org/abs/2208.05744)) frames the EMA's benefit as **smoother, more consistent targets**,
  not better representations per se — i.e. it buys *stability*, which is the only thing the SCFF base needs from
  anything downstream of it.
- **It matters most at the *late* layers — which is our drift-slowdown flip, confirmed.** The same analysis finds the
  EMA is nearly irrelevant near the input and **significant near the output, where gradients are large and fluctuating
  and cause instability.** Read that against our N2 plasticity-gradient decision: *slow the late SCFF layers that GD
  reads* (the LLRD flip). The momentum-encoder literature independently says **the late, output-side layers are exactly
  the ones that need the slow treatment.** We flipped LLRD's axis from circuit intuition; this is the SSL-side
  confirmation.

And **stop-gradient** (SimSiam, BYOL) is the formal name for our **GD-reads-SCFF-never-writes** relationship: the
downstream learner consumes a stop-gradient copy and cannot push instability back into the encoder. We already cite
BYOL for this; the point here is that stop-gradient is *necessary but not sufficient* — boosting-chain had a
stop-gradient at each readout yet still poisoned the base **through the residual stream**, which carried the supervised
correction forward into the next block's input. Stop-gradient blocks the *backward* leak; the residual stream was a
*forward* leak. That's the subtlety the kickoff decision caught.

The **two-timescale** idea also rescues the one useful thing the dropped "two GD organs" had: a **fast tracker + a slow
consolidator.** **Lookahead** ([1907.08610](https://arxiv.org/abs/1907.08610)) formalizes slow/fast weights (fast
weights explore, slow weights are an EMA that gets periodically synced) — which is precisely **a fast online readout
that tracks drift + a slow sleep-consolidated readout.** So the fast/slow split survives the death of boosting; it just
lives *inside the readout* (and inside the LUT's two-timescale role) instead of *between blocks*.

## What it means for us

- **The boosting chain is correctly dead, and the principle generalizes.** Record it: *no fast supervised signal
  upstream of SCFF, via backward leak (stop-gradient handles this) or forward leak (the residual stream — boosting's
  hidden poison).* Per-depth read-only heads on one bulk are safe because they only ever *read*.
- **If we want cross-depth coordination, it must be EMA-slow or unsupervised.** Two clean options on the table:
  (a) the **coordination window** `w` we already adopted — it's *unsupervised* (forward-only InfoNCE across `w` layers),
  so it's allowed; (b) an **EMA-teacher view** of the SCFF taps for the readout to read (de-risks drift for free, the
  N2 "EMA-view" upgrade) — allowed because it's slow and read-only. Anything *supervised and fast* between layers is
  ruled out, on principle, before we waste an experiment on it.
- **The drift-slowdown is doubly grounded — a strong *proposal*, not yet a settled default.** Slowing the late SCFF
  layers GD reads is supported now by **two** independent lines — LLRD (slow what the downstream reads) and the
  momentum-encoder finding (late layers are where the instability is). That's enough to make it the **default hypothesis
  the sim tests first**, but per the discipline ("architecture changes are decisions backed by a result, not a hunch")
  it stays a proposal until a run confirms it — and the same goes for promoting N2's EMA-view from *de-risked standby*
  (its current decision-record status) to a default. Both are **owed decision-record deltas**, flagged not applied
  (design §5).
- **Caveat — slow is a tax on plasticity.** The EMA buys stability by *lagging*; if the world genuinely shifts, a
  too-slow teacher/late-layer is *late* to follow it. The momentum-encoder papers note the τ (decay) is a real knob with
  a stability↔freshness tradeoff — the same tradeoff as our sleep cadence and gate. So "how slow" is, again, set by the
  measured drift rate, not a constant — the recurring Phase-6 theme.
