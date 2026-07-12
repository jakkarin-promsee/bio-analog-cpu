# Inducing Neural Collapse in Imbalanced Learning: Do We Really Need a Learnable Classifier at the End of Deep Neural Network?
- **Authors / Year / Venue:** Yibo Yang, Shixiang Chen, Xiangtai Li, Liang Xie, Zhouchen Lin, Dacheng Tao / 2022 / NeurIPS 2022
- **Link:** https://arxiv.org/abs/2203.09081 (fetched; also https://papers.nips.cc/paper_files/paper/2022/hash/f7f5f501282771c96bb3fedcc96bedfe-Abstract-Conference.html)
- **Tier / Topic:** tier2 / t2.2 closed-form classifier
- **Relevance:** ⭐⭐⭐⭐ — the root paper of the "no-fit classifier geometry" escape: if the optimal classifier shape is known a priori (a simplex ETF), stop estimating it — a zero-storage, zero-covariance anisotropy dodge.

## TL;DR
Neural collapse says that at the end of training on balanced data, class-mean features and classifier vectors converge to a **simplex equiangular tight frame** (ETF) — C unit vectors in d ≥ C−1 dimensions with maximal, equal pairwise angles. This paper inverts the observation: **fix the classifier as a random ETF from step zero and never train it**. Features learn to meet it; the collapse state is reached even under class imbalance (where a *learned* classifier degenerates), and cross-entropy can be swapped for a simpler squared "dot-regression" loss with the same global optimum and faster convergence.

## The mechanism (how it actually works)
The story: a trained classifier is an *estimate* of class geometry, and estimates inherit the data's pathologies — imbalance shrinks minority classifier vectors (the recency/magnitude bias our P7 bake-off measured as argmax-flips). But the *optimal* geometry under balanced conditions is known in advance: maximally-separated equiangular directions. So:

1. Draw a random orthogonal-ish ETF: W = √(C/(C−1))·U·(I − (1/C)·11ᵀ), U any rotation — C fixed unit vectors, pairwise cosine −1/(C−1).
2. Assign each class a vertex. The classifier is now a **constant**.
3. Train only the features, with a **dot-regression (squared) loss** pulling each sample's feature toward its vertex; the paper proves this shares the CE global optimum and avoids CE's imbalance-driven gradient distortion.
4. Because the classifier can't shrink or inflate per class, the magnitude channel through which imbalance and recency express themselves is *structurally absent*.

## Key results / claims
- Fixed-ETF + dot-regression reaches neural collapse **even on imbalanced data**, where learnable classifiers provably distort.
- Consistent gains and faster convergence on imbalanced benchmarks; no accuracy cost on balanced ones.
- The philosophical claim: the classifier's optimum is geometry, not statistics — so don't spend parameters (or forgetting-surface) estimating it.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer (classifier geometry); the spine (direction-purity) — an ETF head is all-direction, no learned magnitudes.
- **Same as us:** the instinct that magnitude estimated from a stream is the failure channel (our P7.4 recency strikes; the cbrs guard) — ETF deletes that channel by construction.
- **Different from us:** the ETF papers **train the backbone toward the fixed targets** — our bulk is frozen and label-free (SCFF), so we cannot move features to vertices. The transferable piece is not "train features to an ETF" but "**use ETF vertices as the regression targets of the closed-form solve**."
- **What we could borrow or test:** the **ETF-target ridge**: our RanPAC/SLDA solve currently regresses onto one-hot targets; swap the targets for ETF vertices (a C×(C−1) fixed matrix in the LUT — zero resident-weight growth, the identical Gram algebra). Hypothesis: equalized inter-class angles reduce the anisotropy-driven *asymmetric* confusions that a one-hot solve tolerates. Cheap, honest tag: **unproven for frozen-feature closed-form heads** — the collapse theory assumes trainable features.
- **What contradicts or challenges us:** if features can't move (frozen bulk), the ETF's optimality theorem doesn't apply — the test could be a clean null. But the cost of finding out is one target-matrix swap.

## Follow-on leads
- Papyan, Han & Donoho 2020 — the original neural-collapse measurement (PNAS).
- NC-FSCIL (Yang et al., ICLR 2023, arXiv 2302.03004) — pre-assigning ETF over future classes for few-shot CIL.
- Neural Collapse Terminus (this folder) — the whole-label-space CIL extension.
- "Guiding Neural Collapse" (NeurIPS 2024, arXiv 2411.01248) — optimizing *toward the nearest* ETF instead of a random one.
