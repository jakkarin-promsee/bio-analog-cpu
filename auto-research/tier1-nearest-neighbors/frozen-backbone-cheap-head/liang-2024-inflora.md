# InfLoRA: Interference-Free Low-Rank Adaptation for Continual Learning
- **Authors / Year / Venue:** Yan-Shuo Liang, Wu-Jun Li / 2024 / CVPR 2024
- **Link:** https://arxiv.org/abs/2404.00228
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐☆☆ — the LoRA-CL representative: instead of "never write," write only in a **subspace constructed to not interfere** with old tasks — the principled middle ground between our hard freeze and full fine-tuning.

## TL;DR
InfLoRA continually fine-tunes a pretrained ViT through low-rank branches (LoRA), but pre-designs each new task's LoRA subspace so that updates within it are (approximately) orthogonal to the gradient/input subspaces that matter for old tasks — eliminating new-on-old interference by construction rather than by penalty or replay. SOTA over prompt- and adapter-based PTM-CL at publication.

## The mechanism (how it actually works)
LoRA fine-tunes W as W + BA (B, A low-rank), which is exactly fine-tuning W *restricted to a subspace*. InfLoRA's move: choose that subspace *before* training each task. The dimensionality-reduction matrix (the input-side projection) is designed so the new task's updates lie in a subspace orthogonal to directions old tasks rely on (estimated from stored old-task input/gradient subspace bases), while still overlapping the new task's own gradient directions (so plasticity survives). Training then proceeds freely inside the safe subspace — stability is geometric, not regularized. Old LoRA branches are kept and merged; the trunk itself is never touched.

## Key results / claims
- Outperforms L2P/DualPrompt/CODA-Prompt-class methods and prior LoRA/adapter CL on multiple CIL benchmarks under matched pretrains.
- The stability–plasticity trade-off is controlled by subspace geometry (principal-subspace overlap), not loss penalties.
- Interference measured directly: constrained updates change old-task features/losses far less than unconstrained LoRA.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P2.5 envelope (read/gate/add-OK, rewrite-forbidden); the bulk write policy; north-star plasticity questions.
- **Same as us:** same enemy (new learning overwriting old function), same instinct that the fix should be **structural/geometric, not a penalty**. Our answer is a 0-dimensional writable subspace (never write); theirs is a carefully-chosen k-dimensional one.
- **Different from us:** they require estimating and storing per-task subspace bases and running SGD within the constraint — machinery (SVDs, stored bases, gradients) that has no cheap analog realization; and it presumes task boundaries. Ours needs no bases because nothing is written.
- **What we could borrow or test:** the *concept* transplants to our one open write-surface — the **SCFF stream itself**: SCFF updates rotate the bulk (P9.0), and the namer must chase the rotation. An InfLoRA-flavored question: could SCFF updates be *projected away from the subspace the deployed reader currently taps* (a fixed cheap projection, not per-task SVD), so unsupervised plasticity continues but reader-relevant directions rotate slower? That would attack the P10 staleness mechanism at the bulk side — flagged there as the "bulk-level component." Even a negative would sharpen why we chose sleep-side repair.
- **What contradicts or challenges us:** InfLoRA (with EASE, SLCA) demonstrates the field extracts real accuracy from *writing carefully* rather than never writing. Our never-write rule is justified by substrate cost and safety, not by accuracy optimality — this family is the standing measurement of the accuracy we leave on the table, and any pitch claiming freeze is *accuracy*-optimal would be wrong against this literature.

## Follow-on leads
- O-LoRA (orthogonal LoRA for LLM CL, 2310.14152) — same geometry in language models.
- GPM — Gradient Projection Memory (2103.09762) — the pre-PTM ancestor: protect old-task gradient subspaces.
- SD-LoRA / LoRA-merging CL lines (2025) — scalable decoupled LoRA without stored bases.
