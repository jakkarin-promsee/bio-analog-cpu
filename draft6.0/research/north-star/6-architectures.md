# 6 — The whole mind / "is 2 brains enough?"

> Your question: *"Is two brains enough? Should we get more?"* The honest answer from every serious attempt at a *complete* cognitive architecture: **no, two is the starting cell, not the organism — think ~4–6 roles.** But also: **you grow into them.** Don't start with six modules; start with the smallest loop that thinks and let failures name the next one. This file is the menu of "whole mind" blueprints.

---

## LeCun — "A Path Towards Autonomous Machine Intelligence" (the most complete answer)

*LeCun, 2022, v0.9.2 ([OpenReview](https://openreview.net/pdf?id=BZ5a1r-kVsf)).*

The single most relevant paper to your question, because it is *exactly* "how many brains, and which ones," from someone who thought hard about it. LeCun proposes **six modules** in one loop:

1. **Configurator** — the executive; sets up and modulates all the others for the current task (your Brainstem, grown up).
2. **Perception** — encodes the world into a state (your SCFF front).
3. **World Model** — predicts missing info + future states, **in abstract representation space, not pixels** (the prefrontal↔hippocampus prediction loop). LeCun calls this *"the most complex piece."*
4. **Cost** — an **intrinsic** part (hardwired drives) + a **trainable critic** (learned value). *This is your "correctness/feeling," split into innate + learned — exactly your "I learned correct from my parents."*
5. **Short-Term Memory** — holds state/cost history (working memory + hippocampus).
6. **Actor** — proposes and optimizes action sequences (reactive, or by *planning* through the world model).

The learning engine is **JEPA** (Joint-Embedding Predictive Architecture): predict in **representation space**, trained energy-based, with anti-collapse regularization (the BYOL/VICReg lineage you already met in `../papers/phase1-2/byol.md`).

**For us:** read this as the **target organ chart**, and notice the overlap is staggering — you already have or have named *five of the six*: SCFF=Perception, the loop=World Model, the feeling=Cost (intrinsic+critic), the LUT/workspace=Short-Term Memory, the Brainstem=Configurator. The one you *don't* have is the **Actor** (acting on the world) — which is fine, because phase 2 is *thinking*, not *acting*, and you can add the Actor later when the loop needs to do epistemic action (`4-signal.md`). **So: two brains is not enough — but you're already closer to six than you think.** JEPA also validates your whole direction: predict in representation space, energy-based, anti-collapse — that's SCFF+grounding.

---

## System 1 / System 2 — fast intuition + slow deliberation

*Kahneman, "Thinking, Fast and Slow," 2011; Bengio & Goyal, "Inductive Biases for Deep Learning of Higher-Level Cognition," 2021 ([arXiv 2011.15091](https://arxiv.org/abs/2011.15091)).*

The cleanest two-system frame, and it maps onto your design almost perfectly. **System 1** is fast, automatic, intuitive, parallel, sensory — *current deep learning, and your SCFF front.* **System 2** is slow, sequential, conscious, logical, compositional, effortful — *the recurrent thinking loop you're trying to build.* Bengio's program is precisely "what *inductive biases* (modularity, sparse attention, causal structure, a workspace) does deep learning need to get System 2?" — and his answers are the workspace + RIMs of `2-controller.md`.

**For us:** this says your two-brain split is the *right first cut* — but it's **fast-vs-slow**, not just unsupervised-vs-supervised. SCFF is System 1 (cheap, parallel, intuitive); the **settling loop + feeling + memory is System 2** (slow, deliberate, sequential). Phase 1 built a System 1. Phase 2 is building System 2 *on top of it*. That's the cleanest one-sentence statement of your roadmap.

---

## Thousand Brains Theory — maybe it's *thousands*, voting

*Hawkins / Numenta, 2019 ([Frontiers](https://www.numenta.com/neuroscience-research/research-publications/papers/thousand-brains-theory-of-intelligence/)); book "A Thousand Brains," 2021.*

The radical answer to "how many brains." Hawkins argues the neocortex is **~150,000 near-identical cortical columns**, and *each one builds a complete model of the whole world* using **reference frames** (coordinate systems attached to objects/concepts). Perception is not a hierarchy funneling to one decision — it's **thousands of parallel models voting** to a consensus. Intelligence emerges from the *agreement of many small, complete modelers.*

**For us:** the provocative reframe — maybe the unit isn't "two brains" but "**many copies of one small complete brain, voting.**" Your **Ganglion / SCFF block is a candidate column**; a Lobe of them voting is a candidate cortex. This is ideas-side (no turnkey method), but it's a permission slip: scaling might mean **replicate-and-vote**, not "add bigger modules." Voting = a consensus/winner-take-all over many cheap models, which is analog-friendly. Hold it as the "what if more than two" answer: *more, but identical and voting*, not *more and each bespoke.*

---

## SOAR & ACT-R — the classical cognitive architectures (don't skip the old masters)

*SOAR: Laird, Newell & Rosenbloom, 1987→; ACT-R: Anderson, 1993→.*

The 40-year-old answers, from before deep learning, and still the most *complete* working models of a whole mind. Both are built on a **prefrontal-loop-plus-memory** skeleton that will look familiar: a **working memory** (the current state), a **procedural memory** of *production rules* ("if state matches X, do Y"), a **declarative/long-term memory** of facts, and a **decision cycle** that repeatedly matches → selects → acts → updates working memory until a goal is met. ACT-R even splits memory into modules with a central **buffer** (a workspace!) and models *retrieval time* and *forgetting*.

**For us:** these are the original *"prefrontal loop calls memory, repeat until done"* — your exact phase-2 picture, built and tested for decades (they model human reaction times to the millisecond). Ideas-side, they tell you the **minimum role set** a thinking loop has historically needed: working memory + long(declarative) + procedural + a match-select-act cycle. The lesson for a hardware person: the symbolic versions are brittle, but the **decomposition** is sound — your job is to rebuild that decomposition in continuous analog + learned (not hand-written) rules.

---

## The shape of the answer (this file)

Is two brains enough? **No — but you're closer to "enough" than you think, and you grow into the rest.** Every complete blueprint has **more than two roles**: LeCun's six (perception, world-model, cost, memory, configurator, actor — you have ~five), Kahneman/Bengio's fast-System-1 + slow-System-2 (you've built System 1, phase 2 is System 2), the classical SOAR/ACT-R quartet (working + declarative + procedural memory + a decision cycle), and Hawkins' radical *thousands, voting*. The convergent minimum for a *thinking* loop: **a fast perception front, a slow recurrent world-model loop, an addressable memory, a self-generated cost/feeling, and a small configurator** — and eventually an **actor** when it must act to learn. Start with the smallest loop that thinks (front + loop + memory + feeling), ground it, and add a role only when a concrete failure demands it. That is the discipline; this file is just the map of where the road can go.
