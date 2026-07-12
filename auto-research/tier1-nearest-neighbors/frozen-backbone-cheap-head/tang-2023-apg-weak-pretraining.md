# When Prompt-based Incremental Learning Does Not Meet Strong Pretraining (APG)
- **Authors / Year / Venue:** Yu-Ming Tang, Yi-Xing Peng, Wei-Shi Zheng / 2023 / ICCV 2023
- **Link:** https://arxiv.org/abs/2308.10445
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐⭐⭐ — the direct published answer to our central question: **yes, prompt-CL's success depends on the strong pretrain**, and it degrades when the frozen representation doesn't match the stream.

## TL;DR
The authors show that L2P-style prompt methods **heavily rely on strong pretraining** (ImageNet-21k): when the gap between the pretraining distribution and the incoming tasks is large — or when the backbone is weakly pretrained — the frozen-backbone-plus-prompts recipe gets "trapped." Their fix (Adaptive Prompt Generator, APG) makes the prompting machinery itself learnable end-to-end so it can *compensate* for the weak representation, significantly outperforming prompt methods in exemplar-free IL **without** strong pretraining while staying comparable with it.

## The mechanism (how it actually works)
Diagnosis first: prompt pools assume the frozen features already separate future classes well enough that (a) key-query retrieval routes correctly and (b) small prompt nudges suffice. With a weak or mismatched backbone both assumptions fail — queries are uninformative, and no small nudge fixes a representation that never contained the needed structure. APG's repair: replace discrete retrieval with a **learnable prompt generator** (a small cross-attention module that maps an image's intermediate features directly to its prompt), trained jointly with the stream; a **knowledge pool** of per-class feature statistics regularizes the generator so new-task training doesn't erase old prompt-generation behavior. In effect, the writable module grows from "lookup table of nudges" to "small network that manufactures the nudge" — more capacity where the backbone offers less.

## Key results / claims
- Under weak/absent strong pretraining, existing prompt-based models collapse below classic exemplar-free IL methods; APG significantly outperforms both in that regime.
- Under strong pretraining, APG is comparable to existing prompt models — the compensation costs nothing when it isn't needed.
- Net message: reported PTM-CL gains are **conditional on the pretrain-stream match**, which standard benchmarks (ImageNet-pretrain → ImageNet-derived splits) quietly maximize.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the representation-source question itself — the bulk (P1–6) vs the field's pretrain.
- **Same as us:** shares our skepticism that the PTM-CL literature's wins transfer to settings without a giant matched pretrain — which is exactly our setting (on-chip, no pretrain possible).
- **Different from us:** their response to "the frozen representation is weak" is to *strengthen the gradient-trained head-side machinery*. Ours is to *grow the representation from the stream itself* (SCFF), keeping the head minimal. Two opposite escapes from the same trap.
- **What we could borrow or test:** their weak-pretrain benchmark protocol — evaluate the frozen-trunk recipe as a function of representation quality. For us: sweep bulk formation budget (steps/width) and plot namer accuracy vs it, giving our own "how much representation does the cheap head need" curve; it would locate our object on the same axis this paper put the field on.
- **What contradicts or challenges us:** cuts both ways. It *validates* our core differentiator — a representation grown from the deployment stream cannot have a pretrain-stream gap, since the "pretrain" IS the stream (our P11 gas win is the existence proof). But it also warns: where our stream is too thin/noisy for SCFF to build structure (the P11 autocorrelated floors, the noise-first thin-margin limit), we are in their "weak pretrain" regime, and their data says a minimal head will not save us there — capacity has to come from somewhere.

## Follow-on leads
- "Reflecting on the State of Rehearsal-free CL with Pretrained Models" (2406.09384) — 2024 systematized critique incl. first-task-adaptation analyses.
- Self-supervised-pretrained (vs supervised) backbones for CL — how much does *label-free* pretraining change the picture (bridges toward our unsupervised bulk).
- Domain-incremental deployments with genuine pretrain-stream gaps (medical/remote-sensing CL) — the field's natural experiments on this axis.
