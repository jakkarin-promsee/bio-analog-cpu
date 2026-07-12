# Improved Few-Shot Visual Classification (Simple CNAPS)
- **Authors / Year / Venue:** Peyman Bateni, Raghav Goyal, Vaden Masrani, Frank Wood, Leonid Sigal / 2020 / CVPR 2020
- **Link:** https://arxiv.org/abs/1912.03432 (fetched; CVF: https://openaccess.thecvf.com/content_CVPR_2020/html/Bateni_Improved_Few-Shot_Visual_Classification_CVPR_2020_paper.html; code: https://github.com/peymanbateni/simple-cnaps)
- **Tier / Topic:** tier2 / t2.2 closed-form classifier
- **Relevance:** ⭐⭐⭐⭐ — the deployed recipe for **count-aware covariance blending**: per-class Mahalanobis that automatically degrades to a shared covariance when a class has too few samples — the streaming-safe version of the RDA dial.

## TL;DR
Simple CNAPS replaces the learned/linear classifier of a few-shot pipeline with a **Mahalanobis-distance classifier whose per-class covariance is a hierarchically regularized blend**: each class's covariance is mixed with the *task-level* covariance with a weight that grows with the class's sample count. With ~9.2% *fewer* trainable parameters it beat the then-SOTA by up to 6.1% on Meta-Dataset — the covariance-aware metric, not more architecture, was the lever.

## The mechanism (how it actually works)
The story: in few-shot episodes a class may have 1–5 samples — a per-class covariance is unestimable, but a task-shared one throws away real shape differences for the classes that *do* have samples. The blend resolves it per class, by count:

1. For class c with n_c support samples: **Σ̂_c = λ_c·Σ_c + (1−λ_c)·Σ_task (+ βI for invertibility)**, with the blend weight **λ_c = n_c/(n_c + 1)** — one sample ⇒ half class / half task; many samples ⇒ mostly class. No knob is fit; the count *is* the knob.
2. Σ_task is pooled over all support samples of the episode (the "tied" estimate), Σ_c over the class's own.
3. Classify by softmax over negative squared Mahalanobis distances to class means under Σ̂_c.
4. Everything after the (episodically adapted) feature extractor is closed-form — the classifier itself has no trained parameters at all.

This is Friedman's RDA λ-dial with the dial set by sample count instead of cross-validation — which is what makes it *streaming-deployable*.

## Key results / claims
- **Up to +6.1%** over state-of-the-art on Meta-Dataset (and mini/tiered-ImageNet benchmarks) while **removing ~9.2% of trainable parameters** — the distance metric replaced learned capacity.
- The class-covariance metric is the ablated source of the gain; Euclidean and cosine variants trail.
- Later extended to transductive and continual few-shot settings (WACV 2022, Neural Networks 2022 — same code base).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer — the concrete formula for a per-class covariance our stream can actually afford statistically; interacts with cbrs (which controls the n_c entering the blend).
- **Same as us:** closed-form head on top of features it does not tune per class; the count-honesty instinct (don't fit what the data can't support) is our methodology rule 6 in classifier form.
- **Different from us:** episodic few-shot (a fresh task context per episode) rather than one lifelong stream; their Σ_c is still a **full d×d per class** while the episode is active — fine transiently in software, expensive as *resident* analog state.
- **What we could borrow or test:** the **λ_c = n_c/(n_c+k) blend rule** as the scheduling law for our diagonal-RDA head (Friedman card): per-class *diagonal* variance blended into the tied covariance with count-aware weight, so burst-starved classes automatically collapse to today's SLDA behavior — which is exactly the guard the A6 gate demanded when it struck FeCAM. Substrate cost: +d per class (one extra capacitor row beside each stored mean) + one counter per class (already exists for cbrs).
- **What contradicts or challenges us:** their gain came *with* an episodically adapted extractor (FiLM layers) — on a fully frozen bulk the covariance blend's headroom may be smaller; the FeCAM-diagnostic gap tells us how much is actually on the table.

## Follow-on leads
- Bateni et al., WACV 2022 (arXiv 2006.12245) — the transductive extension of the same head.
- Friedman 1989 RDA (this folder) — the statistical ancestor of the blend.
- Regularized Tyler / robust scatter — if real-stream features are heavy-tailed, the Gaussian blend needs a robust core.
