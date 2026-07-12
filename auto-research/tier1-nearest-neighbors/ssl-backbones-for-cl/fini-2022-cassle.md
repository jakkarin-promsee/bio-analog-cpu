# Self-Supervised Models are Continual Learners (CaSSLe)
- **Authors / Year / Venue:** Enrico Fini, Victor G. Turrisi da Costa, Xavier Alameda-Pineda, Elisa Ricci, Karteek Alahari, Julien Mairal — 2022 — CVPR 2022
- **Link:** https://arxiv.org/abs/2112.04215 (fetched; CVPR open-access: https://openaccess.thecvf.com/content/CVPR2022/html/Fini_Self-Supervised_Models_Are_Continual_Learners_CVPR_2022_paper.html)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐⭐⭐ — the anchor of continual *self-supervised* learning: what it takes for a label-free representation to survive a sequential stream.

## TL;DR
The title is half the claim: SSL representations, unlike supervised ones, are *almost* continual learners already — but plain sequential SSL still degrades ("efficacy catastrophically reduced" in the CL scenario). CaSSLe closes the gap with one generic move: turn the SSL loss itself into a distillation loss via a small predictor network that maps current features onto the frozen past model's features. No replay of raw data, no labels, little tuning.

## The mechanism (how it actually works)
Keep a frozen snapshot of the backbone from the end of the previous task. During the new task, alongside the normal SSL loss, feed each input to both networks; a small trainable predictor `g` takes the *current* representation and tries to predict the *frozen past* representation — and the loss used for that prediction is **the same SSL objective** (SimCLR stays SimCLR, Barlow Twins stays Barlow Twins). The trick is that every SSL loss is already a "make these two views agree" machine, so "current-vs-past" can be dropped in where "view-1-vs-view-2" was. The predictor gives the new model room to improve (it can drift as long as the drift is *invertible* by `g`) while anchoring the old structure. Works across six popular SSL objectives with the same recipe.

## Key results / claims
- Plain sequential SSL fine-tuning loses representation quality; CaSSLe "significantly improves the quality of the learned representations" across class-, data-, and domain-incremental settings (fetched abstract; per-benchmark digits not pulled — see paper Tables 1–3).
- Compatible with several state-of-the-art SSL objectives with little to no hyperparameter tuning; trained six popular SSL models under CL.
- No replay buffer, no labels, no task boundaries needed at *inference* (they are used to snapshot).

## How it relates to us
- **Organ / phase touched:** SCFF bulk (the label-free representation under drift); the P9.0 rotation finding; sleep.
- **Same as us:** the bet that a label-free objective is the right thing to keep running on a stream; no labels touch the representation; no raw-data replay into the representation objective.
- **Different from us:** CaSSLe is backprop-through-the-SSL-loss, offline multi-epoch per task, with task-boundary snapshots and a second full copy of the network (the frozen past model) — none of which exists on our substrate. Their default (no machinery) *degrades*; our P9.0 measured the bulk "rotates but does not forget" without any distillation anchor — but at toy scale.
- **What we could borrow or test:** a *cheap* analog of the predictor trick — at sleep, fit a closed-form linear map from current-bulk features to LUT-stored past features and count the residual as a drift meter (a functional version of our tap-drift gate signal, banked in P8.2).
- **What contradicts or challenges us:** at their scale, unaided sequential SSL *does* forget; our rotation-not-forgetting result may be scale- or task-gated. The honest read: label-free helps, but is not sufficient alone at scale.

## Follow-on leads
- The CSSL benchmark suite it spawned (class-/data-/domain-incremental SSL) — evaluation protocol alignment for any public claim we make.
- Gomez-Villa et al., projected functional regularization (arXiv 2112.15022) — the sibling approach.
- POCON (WACV 2024) — the successor that attacks CaSSLe's many-task degradation.
