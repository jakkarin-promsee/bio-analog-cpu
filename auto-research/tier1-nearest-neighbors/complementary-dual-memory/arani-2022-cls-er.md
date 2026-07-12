# Learning Fast, Learning Slow: A General Continual Learning Method based on Complementary Learning System (CLS-ER)
- **Authors / Year / Venue:** Elahe Arani, Fahad Sarfraz, Bahram Zonooz / 2022 / ICLR 2022
- **Link:** https://arxiv.org/abs/2201.12604 (fetched)
- **Tier / Topic:** tier1 / t1.4 complementary dual-memory
- **Relevance:** ⭐⭐⭐⭐⭐ — the canonical *built* CLS in ML: it makes "two semantic memories + episodic buffer" a concrete algorithm, and its consolidation trick (EMA of weights at two rates) is the dual-memory lever we have never tried on our closed-form head.

## TL;DR
CLS-ER runs **three** copies of one network — a **working model** trained by SGD, plus a **stable** and a **plastic** *semantic memory*, each an exponential-moving-average (EMA) of the working weights at a different rate (plastic tracks fast, stable tracks slow). A small **episodic replay buffer** (reservoir) supplies old samples; the replay loss doesn't just fit labels, it also **aligns the working model's logits to the semantic memories'**. At test time the *stable* memory is deployed. It's task-boundary-free ("general continual learning") and hits SOTA on the standard rehearsal benchmarks.

## The mechanism (how it actually works)
Start with one network `θ`. Train it online with SGD on the incoming stream **plus** a reservoir replay batch — normal experience replay so far. The novelty is two extra weight vectors that are never trained by gradient, only *averaged into existence*:
- **Plastic memory `θ_p`:** `θ_p ← α_p·θ_p + (1−α_p)·θ` with a *fast* decay — it's a smoothed recent version of the worker.
- **Stable memory `θ_s`:** the same EMA update but *slow* — a long-horizon consolidation of everything the worker has ever been.

The replay objective has two parts: (1) the usual cross-entropy on buffered samples, and (2) a **consistency pull** — on replayed inputs, the worker is pushed to match the *semantic memory's* soft outputs (whichever of stable/plastic is more confident). So new learning happens in the plastic worker, but it is continually *reined back toward* the slow consolidated view. The EMA is the whole consolidation engine: no separate "sleep phase," no closed-form solve — just two running averages at two timescales. Deploy `θ_s` (the slow one) because it has the flattest minima and least recency bias.

## Key results / claims
- SOTA on Seq-CIFAR-10 / Seq-CIFAR-100 / Seq-TinyImageNet and on the "general CL" (blurry, boundary-free) settings, beating DER++, ER, and the regularization family at matched buffer.
- Converges to **flatter minima**, is **better calibrated**, and **mitigates recency bias** (the stable memory lags the worker's drift toward the newest task).
- Task-boundary-free and buffer-based; the gains scale with buffer size but hold at small buffers.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer (SLDA/RanPAC head) · sleep consolidation · the LUT · the whole two-timescale frame.
- **Same as us:** the *architecture-level thesis* is identical — a fast store + a slowly-consolidated general learner + rehearsal between them, and the deployed model is the **slow** one (we deploy the sleep-consolidated namer, they deploy the slow EMA). Both are boundary-free and lean on a bounded reservoir. Both explicitly cite CLS.
- **Different from us:** their two "memories" are **two EMAs of one backprop-trained classifier** — the slow system is a running weight-average, and *both* semantic memories are themselves classifiers. Ours splits by **role, not by timescale-of-the-same-net**: an unsupervised **frozen forward-only SCFF cortex** (never trained toward labels, no backprop — it drifts/rotates but is not an EMA of anything) organizes features, a **non-parametric LUT** holds exemplars/prototypes as a *service* (it never classifies), and consolidation is a **closed-form analytic re-fit** (SLDA/RanPAC) at a discrete sleep, not a continuous weight EMA. They have no frozen backbone and no closed-form step; we have no second trained network.
- **What we could borrow or test:** **a slow-EMA "stable namer."** CLS-ER's core trick — keep a second, slowly-EMA'd copy of the classifier as a stability anchor — is *closed-form-compatible* for us: our namer's state is running statistics (SLDA class means + tied covariance; RanPAC Gram matrix), and an EMA of those statistics is well-defined and cheap. A `Σ_stable ← α·Σ_stable + (1−α)·Σ_fast` pair could give us a two-timescale namer with an anti-recency, flatter-minima stability anchor **without any gradient** — a genuinely untried lever that fits our constraints. Also test their **logit-consistency pull** as a sleep regularizer.
- **What contradicts or challenges us:** CLS-ER gets its continual-safety *for free from the EMA*, with **no explicit sleep cadence and no eviction policy tuning** — which raises the question of whether our grid-4 cadence + CBRS machinery is buying safety that a running average would supply more cheaply. Their deployed-slow-model beats recency bias structurally; we fight recency with cadence. Worth a head-to-head: EMA-of-statistics vs periodic closed-form re-fit.

## Follow-on leads
- ESMER (Sarfraz 2023, same lab) — adds error-sensitivity + error-based buffering on top of this dual-memory frame (carded).
- DER / DER++ (Buzzega 2020) — the logit-distillation replay baseline CLS-ER builds on; the "store logits not just labels" idea.
- Mean-teacher / EMA-teacher literature (Tarvainen & Valpola 2017) — the semi-supervised origin of the EMA-as-consolidation trick, worth a t4 wildcard.
