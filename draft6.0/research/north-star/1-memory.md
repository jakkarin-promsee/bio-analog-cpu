# 1 — The hippocampus / long-term store

> Your question: *"What should the hippocampus look like?"* The field's answer, across forty years: a **fast, sparse, associative, content-addressable** memory kept *separate* from the slow compute — and you already started building it (the sleep + LUT prototype store). This file is the menu of how others built it.

---

## Complementary Learning Systems (CLS) — the theory that says "two memories, on purpose"

*McClelland, McNaughton & O'Reilly, 1995; updated Kumaran, Hassabis & McClelland, 2016 ([Trends in Cognitive Sciences](https://www.cell.com/trends/cognitive-sciences/abstract/S1364-6613(16)30043-2)).*

The founding idea. The brain has **two** learning systems because one can't do both jobs: the **hippocampus** learns *fast*, storing individual episodes as **sparse, pattern-separated, non-overlapping** traces (so new memories don't smear old ones); the **neocortex** learns *slow*, weaving many episodes into **distributed, overlapping** representations that generalize. If you only had the fast one, everything interferes; if you only had the slow one, every new fact would need thousands of repetitions. The resolution: the hippocampus catches experience now and **replays it into the cortex over time** (largely during sleep), interleaving old and new so the cortex integrates without forgetting.

**For us:** this is the *theoretical license* for the exact split you already built — the SCFF/GD body is the slow cortex, the **LUT prototype store is the hippocampus**, and **sleep replay is the consolidation channel between them.** You re-derived CLS from intuition. Phase 2's move is to also let the cortex *query* the hippocampus during thinking, not only during sleep. (Apply-side proof it works: DQN's experience replay buffer is literally a CLS hippocampus bolted onto a slow net.)

---

## Neural Turing Machine (NTM) — a net with RAM

*Graves, Wayne & Danihelka, 2014 ([arXiv 1410.5401](https://arxiv.org/pdf/1410.5401)).*

The first clean "controller + external memory" architecture. A neural **controller** (LSTM or MLP) reads and writes an external **memory matrix** through differentiable **read/write heads**. Two addressing modes, used together: **content-based** (find the row most similar to a query — associative recall) and **location-based** (shift to the next address — iteration). Because the reads/writes are "blurry" (soft attention over all rows), the whole thing trains end-to-end by gradient descent. It learns algorithms — copy, sort, recall — that a plain RNN can't, because it has somewhere to *put* variables.

**For us:** the NTM is the cleanest schematic of your phase-2 loop — **the prefrontal controller is the network; the hippocampus is the memory matrix; the read head is content-addressable recall** (= your LUT dot-product match). Note the split: compute and memory are *different organs* wired by an attention bus. That separation is the whole point.

---

## Differentiable Neural Computer (DNC) — NTM, grown up

*Graves et al., 2016, Nature 538:471–476 ([DeepMind](https://github.com/google-deepmind/dnc)).*

The NTM's successor, and the one that actually scaled to structured reasoning (it solved shortest-path on the London Underground and family-tree inference). It adds three things the NTM lacked: **dynamic memory allocation** (a "free list" so the controller can grab and release memory cells like `malloc`/`free`), a **temporal link matrix** (remembers the *order* writes happened, so it can replay a sequence), and **usage tracking** (so rarely-used cells get recycled). It's a neural network that has, in effect, a tiny operating system for its own memory.

**For us:** DNC is the answer to "what does the hippocampus need *beyond* a lookup table." Two features are directly relevant: **allocation/recycling** (your LUT's novelty-allocation + usage-aging is exactly this), and the **temporal link** (phase 2 is time-series — you'll want to recall not just "what" but "what came next," and the link matrix is how). Read DNC as the spec sheet for a grown-up LUT.

---

## Memory Networks — explicit slots, multi-hop reads

*Weston, Chopra & Bordes, 2014; End-to-End Memory Networks, Sukhbaatar et al., 2015 ([arXiv 1503.08895](https://arxiv.org/abs/1503.08895)).*

A simpler, very influential cousin: store facts as memory slots, answer a query by **softmax-attending** over them, and — crucially — do it in **multiple hops** (read, update the query with what you found, read again). That iterative read-refine-read loop is exactly your orange-car search: *"found apple, no, search again, found orange, almost…"*

**For us:** the **multi-hop read** is the concrete mechanism for your retrieve-compare-retrieve loop. Each hop is one "settle and check the feeling"; the number of hops is the thinking depth (which `3-recurrence.md`'s halting papers make *learned*).

---

## Modern Hopfield Networks — "retrieval *is* attention"

*Ramsauer et al. (Hochreiter group), 2020, "Hopfield Networks is All You Need" ([arXiv 2008.02217](https://arxiv.org/abs/2008.02217)); capacity from Demircigil et al. 2017.*

The deep unifier. Classic Hopfield nets (1982) store patterns as energy minima but choke at ~0.14N memories. **Modern** Hopfield nets use a sharper energy that gives **exponential capacity** (store ~`exp(N)` patterns) and **retrieve in a single step** — and that single-step update turns out to be *mathematically identical to transformer self-attention*. So "associative memory" and "attention" are the same operation viewed from two sides: a query pulls the nearest stored pattern out of an energy landscape.

**For us:** this is the most important entry in the file for your hardware, because **your LUT crossbar already computes the core operation** (dot-product similarity → retrieve). It says: you don't need to choose between "a Hopfield memory," "an attention layer," and "a content-addressable LUT" — *they are the same thing*, and your analog crossbar is a native implementation. It also says the recall is **one settling step** of an energy network — which `3-recurrence.md` says analog physics does for free.

---

## Retrieval-augmented models (kNN-LM, RETRO) — memory you don't have to train into weights

*kNN-LM: Khandelwal et al., 2019 ([arXiv 1911.00172](https://arxiv.org/pdf/1911.00172)); RETRO: Borgeaud et al., 2021 ([Improving LMs by retrieving from trillions of tokens](https://proceedings.mlr.press/v162/borgeaud22a/borgeaud22a.pdf)).*

The modern apply-side of "keep knowledge *outside* the network." **kNN-LM** stores every (context → next-token) pair in a giant key-value datastore and, at inference, retrieves the nearest neighbors (via FAISS) and blends them with the model's own prediction — improving the model **with zero extra training**. **RETRO** scales this to *trillions* of tokens, chunking text and cross-attending to retrieved neighbors, letting a small model punch far above its weight by *looking things up*.

**For us:** the lesson is **resident facts ≠ resident weights.** A growing memory store can carry knowledge the slow brain never has to absorb into its weights — which is *exactly* your resident-weight chip plus an addressable LUT. It also reframes "lifelong learning": some of it is *weight* learning (slow, `5-continual.md`), but a lot of it can be *memory* writing (fast, cheap, non-destructive). The honest caveat from this literature ("Great Memory, Shallow Reasoning"): retrieval gives knowledge, **not** reasoning — the reasoning still has to live in the loop.

---

## Fast Weights — a third, faster timescale

*Ba, Hinton, Mnih, Leibo & Ionescu, 2016 ("Using Fast Weights to Attend to the Recent Past", [arXiv 1610.06258](https://arxiv.org/abs/1610.06258)).*

A short-term memory that lives *in the weights*, not in a separate matrix. Alongside the slow weights, each connection has a **fast weight** that updates Hebbianly and **decays quickly** — a transient associative memory of the last few moments, used to "attend to the recent past" without a separate read head.

**For us:** this is a *third timescale* between activations and slow weights, and it's analog-native (a leaky capacitor with a fast RC *is* a fast weight — and you already proposed leaky-fast caps for the SCFF read-layers). Worth holding as: working memory might not need an external matrix at all for the *recent* past — a fast-decaying cap can hold it. Reserve the LUT for the *distant* past.

---

## The shape of the answer (this file)

A hippocampus, for us, is: **a content-addressable associative store (= LUT crossbar = modern Hopfield = attention), kept separate from the slow compute, with allocation/recycling and a temporal link, written fast and cheap, read by similarity during thinking and replayed during sleep.** CLS says *why* it must be separate and fast; NTM/DNC say *how* to wire it to the controller; Hopfield says *it's the operation your crossbar already does*; retrieval says *keep knowledge in it, not in the weights*; fast weights say *the recent past can live in a leaky cap instead.*
