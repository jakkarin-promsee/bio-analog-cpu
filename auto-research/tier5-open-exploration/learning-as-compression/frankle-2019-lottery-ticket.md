# The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks
- **Authors / Year / Venue:** Jonathan Frankle, Michael Carbin (MIT) / 2019 / ICLR 2019
- **Link:** https://arxiv.org/abs/1803.03635
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐⭐ — the second name for "spare capacity is real"; but its init-dependence is a caveat our stream-grown bulk must answer.

## TL;DR
A dense, randomly-initialized network contains a small **"winning" subnetwork** (often **<10–20%** of the weights) that, trained *in isolation from the same initialization*, matches the full network's accuracy in a similar number of steps. The other 80–90% is slack: it helped *find* the solution but isn't needed to *represent* it.

## The mechanism (how it actually works)
Train the full network. Prune the smallest-magnitude weights. Now **reset the surviving weights to their original init values** (not to fresh random values) and retrain only those. This "iterative magnitude pruning" finds a sparse mask that, combined with the *original* initialization, trains to full accuracy. The critical, counter-intuitive part is the reset: a sparse subnetwork with fresh random init trains *worse*; the same mask with the original init trains *as well as the dense net*. So the winning ticket is a **(structure, initialization) pair** — the dense network is essentially running many lottery tickets in parallel and the good one wins. The implication for capacity: most weights are **overhead for the search**, not for the final function — the represented solution is far smaller (more compressible) than the training-time parameter count.

## Key results / claims
- Winning tickets at **10–20% of weights** match full accuracy on MNIST/CIFAR-10 (FC and conv nets).
- Below that they can train *faster* and reach *higher* accuracy.
- The **original initialization is essential** — the win is not just about the sparse structure.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk (capacity), the spare-capacity hypothesis, sleep/consolidation, P11 substrate-factor scaling.
- **Same as us:** the author's "some neurons aren't used 100%; there's spare space" re-derives the lottery ticket exactly. Suggests a two-phase story that fits our sleep loop: learn **over-provisioned** (use slack to find the solution — double descent says this is safe), then **consolidate toward the winning ticket**, freeing slack for the next task. That is continual learning meeting compression.
- **Different from us:** the winning ticket is *found by pruning a trained dense net with backprop* and depends on a *lucky init*. Our bulk is grown online by a local forward rule, never pruned, and there is no "reset to init" move on a streaming substrate.
- **What we could borrow or test:** measure whether our frozen bulk has a lottery-ticket structure — prune Scaps by magnitude and check whether a small fraction retains the task. If yes, sleep could *physically free* the pruned capacity for future tasks (the shareable-slack claim, made concrete).
- **What contradicts or challenges us:** the init-dependence is a real threat. Lottery tickets say the winning subnetwork is tied to a *specific* initialization found by search; our spare-capacity-shared-across-tasks bet assumes slack is *reusable* across tasks, which the init-lock does not guarantee. If the slack is init-specialized, sharing it across future tasks may not work.

## Follow-on leads
- Frankle et al. "Stabilizing the Lottery Ticket Hypothesis" / "Linear Mode Connectivity" — when tickets transfer.
- "Lottery tickets across tasks / continual pruning" — the exact reuse question our hypothesis needs.
- Structured/movement pruning as a substrate-legal consolidation primitive.
