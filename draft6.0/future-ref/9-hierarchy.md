# 9 — The hierarchy: how others compose the levels

> Your words: *"the brain hierarchy — the way others do it."* Your draft-5 hierarchy (Scap→Ganglion→Column→Lobe→Limbic) "looked good but wasn't complete." This file is how *other* people structure the levels — and the key realization across all of them: **the hierarchy is not just a stack; it's a loop** (top-down predictions meet bottom-up evidence) with **dynamic, per-input structure**, not a fixed pyramid.

---

## Hierarchical Predictive Coding — the hierarchy is a two-way street

*Rao & Ballard, 1999; framework: Friston. (See also `4-signal.md`, `../concept/predictive-coding.detail.md`.)*

The most influential model of the *cortical* hierarchy, and the correction to "stack of feature detectors." Each level **predicts the activity of the level below** and sends that prediction *down*; the level below sends only the **prediction error** *up*. Perception is the hierarchy **settling** so that errors are minimized at every level. So the hierarchy is **bidirectional**: bottom-up isn't features-getting-fancier, it's *error*; top-down isn't just attention, it's *prediction*.

**For us:** your draft-5 hierarchy was (like most first drafts) **bottom-up only** — signal flows up, loss diffuses down. Predictive coding says the *real* cortical hierarchy is a **prediction-error loop at every level**. For phase 2 this is the structural template: each level predicts the one below, passes error up, and the whole thing **settles** (`3-recurrence.md`). It also tells you *what flows between levels*: **predictions down, errors up** — not raw activations. That's the "completeness" your draft-5 hierarchy was missing.

---

## GLOM — the hierarchy is *dynamic*, built from agreement

*Hinton, 2021 ([arXiv 2102.12627](https://arxiv.org/abs/2102.12627)).*

Hinton's answer to "how does a *fixed* network parse each input into a *different* part-whole tree?" Picture a **column at every location**, each holding embeddings at **multiple levels** (sub-part, part, object, scene). The embeddings get updated by bottom-up (from below), top-down (from above), and **lateral agreement** (nearby columns at the same level pulling toward each other). The parse tree appears as **"islands of agreement"** — regions where many columns settle on the *same* vector represent the same object/part. The hierarchy isn't wired in; it **emerges as agreement, fresh for each input.**

**For us:** this is the answer to "my hierarchy isn't complete" — because the missing piece is usually that the hierarchy should be **dynamic and consensus-based, not a fixed pyramid.** GLOM's "islands of agreement" is a **voting/settling** mechanism (which your analog substrate does natively, and which Thousand-Brains in `6-architectures.md` echoes). It also unifies your levels: every level is the *same* kind of column running the *same* process — which is your self-similar-hierarchy instinct from draft 5, done right (process, not just structure, repeats).

---

## Hierarchical Temporal Memory (HTM) — every region runs the *same* algorithm on sparse codes

*Hawkins / Numenta. ([SDR properties](https://arxiv.org/pdf/1503.07469)).*

The most explicit "repeat one process at every level" hierarchy, and the most biologically constrained. Two repeating modules: a **Spatial Pooler** (turns input into a fixed-sparsity **SDR** — see `7-encoding.md`) and a **Temporal Memory** (learns *sequences* of SDRs and makes **context-sensitive predictions** of what comes next). Every region in the hierarchy runs the *identical* SP+TM process on its own input; higher regions see slower, more abstract patterns.

**For us:** HTM is the clean template for a **self-similar, time-aware hierarchy** — exactly your draft-5 instinct ("each level does the same thing to its children") but with the **temporal** dimension built in, which phase 2 needs. The Temporal Memory's "predict the next pattern in context" is your phase-2 prediction loop at every level. And it's all on **SDRs** (sparse, analog-friendly, `7-encoding.md`). Read HTM as "draft-5 self-similarity + sequence prediction + sparse codes."

---

## Slot Attention & object-centric learning — composition into *things*

*Locatello et al., 2020 ([arXiv 2006.15055](https://arxiv.org/abs/2006.15055)).*

A different cut: instead of levels, **slots**. A fixed set of "slots" **compete** (via iterative attention) to each bind to one *object* in the input, decomposing a scene into a set of independent entities — with no labels telling it what the objects are. The hierarchy is "input → a handful of object-slots," each a reusable, composable unit.

**For us:** relevant to "what should flow between blocks" and to the workspace (`2-controller.md`). Slot attention is **how you get discrete, composable *things* out of continuous input** without labels — and the iterative *competition* for slots is a winner-take-all settling (analog-native). If phase-2 thinking operates over *entities* ("the car," "orange") rather than raw features, slot-style binding is how those entities get carved out. It pairs with the workspace (slots compete for the bus).

---

## Mixture-of-Experts routing — sparse, learned hierarchy

*Shazeer et al., 2017 (sparse MoE); Switch Transformer, Fedus et al., 2021.*

The scaling-world's modular hierarchy: many "expert" sub-networks, and a **router** that sends each input to only the **top-k** relevant experts. Most of the network is *dormant* for any given input — conditional computation. It's how you get a huge model whose *active* cost per input stays small.

**For us:** MoE is the same idea as RIMs (`2-controller.md`) at the hierarchy level — **sparse, conditional routing** so only the relevant part fires. That's your **sparse** substrate property as an architectural principle: a big hierarchy where each input lights up a small path (few charge cycles). The router is a small learned gate (cheap). Hold it as: the hierarchy can be *wide and mostly-dormant*, not deep-and-all-active.

---

## Greedy layer-wise growth — build the hierarchy one level at a time

*Deep Belief Nets: Hinton, Osindero & Teh, 2006; and the Forward-Forward / local-learning lineage (`../concept/`).*

The historical-but-relevant idea: you don't have to train a deep hierarchy *end-to-end*. Train level 1 to encode the input, **freeze it**, train level 2 on level-1's output, and so on — **growing the hierarchy bottom-up**, each level local. This is what made deep learning work *before* end-to-end backprop got good, and it's exactly the spirit of **SCFF stacking** and **BoostResNet** (`../ref/boostresnet.md`).

**For us:** this is the construction *method* for your hierarchy, and you're already using it (SCFF is greedy-layerwise; blocks chain by boosting). The lesson for phase 2: **grow the thinking hierarchy level by level**, each trained locally/online, rather than designing the whole tower and training it at once. It matches your "simple first, then climb" discipline and your local-learning substrate.

---

## The shape of the answer (this file)

The hierarchy, for us, is *more than a stack*. The completeness your draft-5 was missing: (1) it's a **bidirectional loop** — predictions flow **down**, errors flow **up**, and the levels **settle** (predictive coding); (2) the structure is **dynamic and consensus-based** — parse trees emerge as **islands of agreement / voting**, fresh per input (GLOM, Thousand-Brains), not a fixed pyramid; (3) **every level runs the same process** on **sparse codes**, with **time** built in (HTM) — your self-similarity instinct, completed with sequence prediction; (4) it can be **wide and mostly-dormant** with sparse routing (MoE/RIMs), lighting a small path per input; and (5) you **grow it greedily, level by level, locally** (Forward-Forward / boosting) — which you already do. Draft-5's skeleton was right; what it lacked was the **top-down prediction loop, the dynamic agreement, and time.**
