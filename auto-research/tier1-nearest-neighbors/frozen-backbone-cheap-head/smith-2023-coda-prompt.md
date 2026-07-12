# CODA-Prompt: COntinual Decomposed Attention-based Prompting for Rehearsal-Free Continual Learning
- **Authors / Year / Venue:** James Seale Smith, Leonid Karlinsky, Vyshnavi Gutta, et al. (9 authors, Georgia Tech + MIT-IBM) / 2023 / CVPR 2023
- **Link:** https://arxiv.org/abs/2211.13218
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐☆☆ — the prompt-side SOTA refinement; shows the paradigm's internal fix was *more capacity + end-to-end training*, i.e., leaning harder on gradient machinery we deliberately avoid.

## TL;DR
CODA-Prompt replaces L2P's discrete hard prompt selection with a **soft, weighted assembly of decomposed prompt components**, making the whole prompting mechanism differentiable end-to-end. It beat DualPrompt by up to ~4.5% average final accuracy on rehearsal-free benchmarks. The backbone stays fully frozen; all the innovation is in *how* the small writable module is composed.

## The mechanism (how it actually works)
Instead of retrieving top-N prompts from a pool (a non-differentiable argmax that trains prompts and keys under two separate objectives), CODA keeps a bank of **prompt components** and builds each input's effective prompt as a **weighted sum**: weights come from an attention operation between the input's frozen-backbone query and each component's learnable key (with a learnable feature-selection mask). Because the assembly is a soft sum, gradients flow through selection and content jointly — one optimization, not two. New tasks add components (orthogonality-initialized against old ones) while old components' keys/masks are frozen — capacity expands, prior routing is preserved. Prompting capacity can be scaled arbitrarily (more components) without changing inference cost much.

## Key results / claims
- ImageNet-R, CIFAR-100 (class-incremental, rehearsal-free): new SOTA at publication, up to **+4.5%** average final accuracy over DualPrompt; up to **+4.4%** on a dual class+domain-shift benchmark.
- Establishes that L2P/DualPrompt's bottleneck was the non-differentiable selection, not the frozen-trunk premise.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer-side (P7) — the "what should the small writable module be" question.
- **Same as us:** frozen trunk, tiny writable surface, rehearsal-free by architecture rather than by buffer.
- **Different from us:** the field's improvement direction here is *more gradient*, not less — end-to-end differentiability through the selection mechanism is the whole contribution. Our P7 bake-off went the exact opposite way: the closed-form no-gradient head tied/beat the gradient MLP head. Also their writable module steers the trunk's computation (prompts enter attention); ours never does.
- **What we could borrow or test:** the **soft-composition-over-components** idea maps onto prototype mixing: a namer that classifies against a *weighted blend* of stored prototypes (attention over the hippocampus LUT) rather than nearest-single-prototype — a closed-form-compatible upgrade worth a P-future rung.
- **What contradicts or challenges us:** nothing structural — but it is evidence that when accuracy on hard static benchmarks is the goal, the winning move was richer trainable routing. If we ever chase static accuracy, "our head is closed-form" becomes a ceiling, not a feature; our defense stays what P4/P10 measured — we sell continual safety + substrate economics, not static SOTA.

## Follow-on leads
- DualPrompt (2204.04799) — the G-prompt/E-prompt split CODA supersedes.
- HiDe-Prompt (NeurIPS 2023) — hierarchical decomposition of the prompt-CL objective.
- Mixture-of-experts readings of prompt-CL (arXiv 2405.14124) — prompt pools as MoE; connects routing to gating literature (our DDM gate is a 1-bit cousin).
