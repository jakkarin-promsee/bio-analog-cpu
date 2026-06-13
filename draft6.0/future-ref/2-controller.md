# 2 — The prefrontal cortex / working memory / coordinator

> Your question: *"What should the prefrontal cortex look like? Which model? How do the parts communicate?"* The convergent answer: **not one big network.** A *small, bandwidth-limited coordinator* that holds a little active, queries the rest from memory, and broadcasts a summary back to the specialists. The scarcity is the point — it forces the parts to specialize and to agree.

---

## Global Workspace Theory (GWT) — the neuroscience of "a little, broadcast widely"

*Baars, 1988; global neuronal workspace: Dehaene & Changeux.*

The dominant cognitive-science theory of what "conscious thought" *does* mechanically. The brain is a crowd of fast, parallel, unconscious **specialists** (vision, audition, memory, motor…). Only a tiny fraction of their content wins entry into a **global workspace** at any moment — and once in, it is **broadcast** back to *all* the specialists, letting them coordinate around it. Consciousness, in this theory, is the **bandwidth-limited broadcast bus**: little gets on it, but what does, everyone hears. Working memory is whatever is currently held in that workspace.

**For us:** this is the model for your prefrontal "thinking mind." It is **not** a big network that knows everything — it is a *small bus* that holds one thought at a time and shares it. That directly matches your intuition ("the brain holds only short-term memory while it calls long-term"). The limited bandwidth isn't a flaw to engineer away; it's the mechanism.

---

## Coordination Among Neural Modules Through a Shared Global Workspace — the buildable version

*Goyal, Didolkar, Lamb, …, Mozer, Blundell, Bengio, ICLR 2022 ([arXiv 2103.01197](https://arxiv.org/abs/2103.01197)).*

GWT turned into a working deep-learning module, and the single most directly useful paper here. Several specialist modules (could be RIMs, could be SCFF blocks) don't talk pairwise (that's `O(n²)` and incoherent); instead they **compete for a limited number of slots in a shared workspace**, the winners are written in, and the workspace contents are **broadcast back to every module**. The bandwidth limit is shown to be *rational*: it forces **specialization and compositionality** and synchronizes otherwise-independent parts.

**For us:** this is the concrete answer to *"how do the two/several brains communicate?"* — **a shared workspace with a hard bandwidth cap and a broadcast.** It's also a gift for analog hardware, where a wide shared bus is *expensive*: GWT says you *want* a narrow bus. The competition-for-slots is a winner-take-all (which you have as a primitive), and the broadcast is one-to-many (cheap). Build the inter-module bus as a small workspace, not a crossbar-to-everything.

---

## Recurrent Independent Mechanisms (RIMs) — modular recurrence that only fires when relevant

*Goyal, Lamb, Hoffmann, Sodhani, Levine, Bengio & Schölkopf, 2019 ([arXiv 1909.10893](https://arxiv.org/abs/1909.10893)).*

The module *design* that pairs with the workspace. Instead of one monolithic RNN, RIMs use **many small recurrent cells with independent dynamics**. At each step, **only the top-k most relevant cells activate** (selected by attention to the input); the rest hold their state untouched. The active cells communicate **sparingly, through attention**. Result: each cell specializes to a "mechanism" of the world, and the system generalizes better when only a few factors change — because only the relevant modules update.

**For us:** RIMs is how you avoid "a full LSTM that knows everything at once" (your exact worry). It's **sparse, modular recurrence** — only the relevant part fires, the rest is dormant — which is *also* your sparsity substrate property and cheap on analog (dormant module = no charge cycles). Pair RIMs (the specialists) with the shared workspace (the bus) and you have a buildable prefrontal system.

---

## The Consciousness Prior — the low-dimensional thought

*Bengio, 2017 ([arXiv 1709.08568](https://arxiv.org/abs/1709.08568)).*

A short, idea-side manifesto. A high-dimensional unconscious state exists, but a **conscious thought** is a *very low-dimensional* projection of it — a handful of variables, expressible almost as a sentence. The "prior" is that the world's useful abstractions can be captured by such sparse, low-dimensional statements (e.g., "if I drop this, it falls"). Learning should bottleneck through that narrowness.

**For us:** this reinforces the workspace's narrowness as a *learning prior*, not just a bandwidth limit — the thing you hold in working memory should be a **few strong variables**, and forcing that narrowness is what makes the abstractions clean. Your SCFF clusters are candidate low-dim variables; the workspace holds a few at a time.

---

## PBWM — gating: what enters working memory, and when to let it go

*O'Reilly & Frank, 2006, Neural Computation ("Prefrontal cortex and Basal-ganglia Working Memory").*

The neuroscience-grounded model of the *gate*. Prefrontal cortex holds working memory, but something must decide **when to update it** (write a new item) versus **maintain it** (protect it from being overwritten) versus **release it**. PBWM gives that job to the **basal ganglia**, trained by **reinforcement (dopamine)** — it learns *when* gating helps. The key insight: robust working memory needs an explicit, *learned* gate, or it's either too sticky (can't update) or too leaky (can't hold).

**For us:** this is the LSTM gate's biological parent, and it answers a concrete design question: the prefrontal loop needs a **learned gate** deciding what to admit to the workspace and what to flush. On your substrate this is a small controller (Brainstem-flavored) trained by the same grounding/feeling signal from `4-signal.md`. The LSTM forget/input gate is the cheap version; PBWM is the principled one.

---

## The shape of the answer (this file)

A prefrontal cortex, for us, is **not a model — it's a coordinator**: a small, bandwidth-limited **workspace** (GWT / Shared-Global-Workspace) that holds a few low-dimensional variables (Consciousness Prior), fed by **sparse, specialized recurrent modules** that only fire when relevant (RIMs), with a **learned gate** controlling what gets in and out (PBWM), and a **broadcast** back to all specialists as the communication channel. The narrow bus is the feature, and it's analog-cheap. Communication = compete-for-slots + broadcast, not all-to-all wiring.
