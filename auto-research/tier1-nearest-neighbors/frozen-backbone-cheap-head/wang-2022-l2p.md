# Learning to Prompt for Continual Learning (L2P)
- **Authors / Year / Venue:** Zifeng Wang, Zizhao Zhang, Chen-Yu Lee, Han Zhang, Ruoxi Sun, Xiaoqi Ren, Guolong Su, Vincent Perot, Jennifer Dy, Tomas Pfister / 2022 / CVPR 2022
- **Link:** https://arxiv.org/abs/2112.08654
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐☆☆ — the paradigm anchor: the paper that made "freeze the backbone, adapt a tiny module" the mainstream CL recipe.

## TL;DR
L2P freezes a large pretrained ViT entirely and learns only a small **pool of prompt vectors** — extra input tokens prepended to the transformer. At test time an input's frozen-feature query retrieves the best-matching prompts from the pool (key-query cosine matching), so the model needs **no task identity and no rehearsal buffer**. It launched the pretrained-model-based CL (PTM-CL) subfield.

## The mechanism (how it actually works)
The backbone (ViT-B/16, supervised ImageNet-21k pretrain) never receives a gradient. Learning lives in a **prompt pool**: ~10–30 short learnable token sequences, each paired with a learnable **key** vector. For each input, the frozen backbone's [CLS] feature acts as a **query**; the top-N keys by cosine similarity are selected, their prompts are prepended to the input token sequence, and only those prompts (plus keys and a linear classifier) are trained with the task loss. Because different tasks tend to pull different prompts, task-specific knowledge lands in different (small) parameter subsets — instance-wise routing replaces task labels. Forgetting is small because the shared trunk is immutable and the writable surface is tiny.

## Key results / claims
- Split-CIFAR-100, 5-datasets, Gaussian-schedule CORe50: beats then-SOTA regularization and architecture CL methods, and is **competitive with rehearsal-based methods without any buffer**.
- Works task-agnostic (no task id at test time) — the key-query routing does the inference-time selection.
- The writable parameter count is a fraction of a percent of the backbone.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the frozen SCFF bulk + the namer (P5 per-depth read-only heads; P7 closed-form namer).
- **Same as us:** identical topology commitment — an immutable representation trunk, all continual adaptation confined to a small module that **reads, never writes** the trunk. Same bet that forgetting is defeated by making the writable surface small.
- **Different from us:** (1) **Representation source** — their trunk's quality is bought with an internet-scale *supervised* pretrain; ours is grown unsupervised, forward-only, from the deployment stream itself, on-substrate. (2) Their adaptation module is still **gradient-trained** (prompts + head via SGD); ours is closed-form. (3) Their prompts modulate the trunk's *computation* (inserted tokens change every attention layer); our heads strictly post-read tap activations — the bulk's function is never input-conditionally steered. (4) Their trunk is frozen *forever*; our bulk stays SCFF-plastic (frozen only to supervised writes).
- **What we could borrow or test:** the **key-query routing idea** as an analog-cheap context bias — a small LUT of per-context input offsets retrieved by nearest-prototype matching (the hippocampus LUT already does nearest-prototype work). Could give domain-conditioning without writing weights.
- **What contradicts or challenges us:** their absolute numbers ride on a backbone we cannot have on-chip; L2P is the cleanest demonstration that when the frozen representation is *strong enough*, the continual problem nearly disappears. Our claim must not silently borrow that intuition — our bulk is small and self-grown, so "freeze + cheap head" is only as good as what SCFF actually built (this is exactly what P11.0's Δbulk decomposition measured).

## Follow-on leads
- DualPrompt (ECCV 2022, arXiv 2204.04799) — splits prompts into general vs expert; same team, same frozen-trunk assumption.
- The "does the pool actually get used?" critiques inside CODA-Prompt and the PTM-CL survey — prompt-selection collapse.
- Key-query retrieval over a prototype LUT as a north-star "context" mechanism.
