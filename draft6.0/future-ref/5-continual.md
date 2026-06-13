# 5 — Never freeze / lifelong learning

> Your committed goal: *a model that doesn't stop learning in real use — its own essence across its life, not born to finish a prompt and die.* That is **continual / lifelong learning**, and it has one central enemy — **catastrophic forgetting** — and a small set of trustable defenses. The deepest one is the same CLS sleep you already built.

---

## The stability–plasticity dilemma — the problem named

The framing the whole field hangs on. A network that **never stops learning** faces a trap: too **plastic** and new learning overwrites old (catastrophic forgetting — the new task smashes the old weights); too **stable** and it can't learn anything new. *Every* continual-learning method is a way to be plastic where it's safe and stable where it matters. Frozen models (GPT/Claude) dodge the dilemma by *not learning at all after deploy* — which is exactly the thing you refuse to accept.

**For us:** this is the tax on "never freeze." The moment the chip keeps learning in real use, forgetting becomes the central risk, not an edge case. The good news: you already have the two strongest structural answers (slow/fast weight split, and sleep replay). The papers below sharpen them.

---

## Elastic Weight Consolidation (EWC) — slow the weights that matter

*Kirkpatrick et al., 2017, PNAS 114:3521 ([paper](https://www.pnas.org/doi/10.1073/pnas.1611835114)).*

The most-cited weight-based defense, and it's *literally synaptic consolidation in math*. After learning a task, estimate how **important** each weight was (via the Fisher information — roughly, how much the loss cares about that weight). When learning the next task, add a **quadratic penalty** that **slows changes to the important weights** while letting unimportant ones move freely. The network stays plastic overall but **rigid exactly where forgetting would hurt.** It learned a sequence of Atari games without erasing the earlier ones.

**For us:** EWC is the principled version of your **plasticity gradient** — instead of "slow the late SCFF layers by depth," it's "slow each weight by *measured importance*." Same physics on your substrate (importance → a per-Scap leak/coupling rate), finer grain. Hold it as: when forgetting shows up in phase 2, EWC is the first, cheapest weight-side patch. (Honest caveat: importance estimates drift over many tasks; EWC alone isn't enough for *very* long lives — which is why replay matters.)

---

## Synaptic Intelligence & Memory-Aware Synapses — importance, measured online

*Zenke, Poole & Ganguli, 2017 ([SI](https://arxiv.org/abs/1703.04200)); Aljundi et al., 2018 (MAS).*

EWC's importance is measured *after* a task in a batch step. **Synaptic Intelligence** measures each weight's importance **online, as it trains** (accumulating how much each weight contributed to reducing the loss). **MAS** measures it in an *unsupervised* way (sensitivity of the output to each weight), so it works without task labels.

**For us:** these are the *online, label-free* versions — which is the only kind your always-on, often-unlabeled chip can actually use. SI's "accumulate importance while running" is a per-Scap statistic, exactly the kind your momentum register already holds. If EWC is the idea, SI/MAS are the forms that fit a substrate with no clean task boundaries.

---

## Deep Generative Replay — sleep, but the hippocampus *dreams the old data*

*Shin, Lee, Kim & Kim, 2017 ([arXiv 1705.08690](https://arxiv.org/abs/1705.08690)).*

The replay-based defense, and the most CLS-faithful. Keep a **generator** ("scholar") that learns to *produce* samples resembling past data; when learning something new, **interleave generated pseudo-samples of the old** so the main net ("solver") never drifts away from them. No need to store the raw old data — the generator *re-dreams* it. This is McClelland's hippocampal replay, built.

**For us:** this is **the upgrade path for your sleep mechanism + LUT.** Right now sleep replays stored prototypes (a buffer). Generative replay says: eventually, replace the buffer with a *learned generator that dreams the distribution* — which is precisely your "memory model / real hippocampus" idea (the 3.3 cell). It also connects to World Models (`4-signal.md`): the same M that predicts-forward can *generate* replay. One organ, two uses.

---

## Progressive Neural Networks — grow, don't overwrite

*Rusu et al., 2016 ([arXiv 1606.04671](https://arxiv.org/abs/1606.04671)).*

The architecture-side answer: when a new task arrives, **freeze the old network and grow a new "column"** beside it, with lateral connections so the new column can *reuse* old features but can't *damage* them. Zero forgetting by construction — you never touch the old weights — at the cost of growing the model.

**For us:** mostly a *contrast* case (unbounded growth fights resident-weight + fixed silicon), but the *idea* is relevant: **reserve capacity.** Your chip has fixed Scaps, but "grow a column" maps to "allocate fresh, unused Scaps/blocks to a new skill while protecting committed ones" — which dovetails with the LUT's novelty-allocation and with keeping some blocks plastic and others consolidated. Don't copy it; borrow "protect the committed, learn in the spare."

---

## The shape of the answer (this file)

Never-freezing, for us, is a **two-front defense you already half-built**: (1) **weight-side** — slow the important/committed weights (EWC's idea = your plasticity gradient, made importance-weighted; SI/MAS for the online label-free form your chip needs); (2) **memory-side** — **sleep replay** that interleaves old and new (CLS), upgrading from a stored-prototype buffer toward a **generative replay / world-model that dreams the past** (= your "memory model" / hippocampus track). The stability-plasticity dilemma is the tax for the thing that makes your chip *not* a frozen LLM; these are how you pay it without going bankrupt on forgetting.
