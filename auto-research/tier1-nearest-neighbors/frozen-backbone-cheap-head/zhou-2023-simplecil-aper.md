# Revisiting Class-Incremental Learning with Pre-Trained Models: Generalizability and Adaptivity are All You Need (SimpleCIL + ADAM/APER)
- **Authors / Year / Venue:** Da-Wei Zhou, Zi-Wen Cai, Han-Jia Ye, De-Chuan Zhan, Ziwei Liu / 2023 (arXiv), IJCV 2024
- **Link:** https://arxiv.org/abs/2303.07338
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐⭐⭐ — SimpleCIL is the field's canonical "prototype head on a frozen trunk beats the prompt methods" result, and APER is the published version of "adapt once, then freeze forever."

## TL;DR
Two findings. **SimpleCIL:** set each class's classifier weight to its prototype (mean frozen-PTM feature) — no training at all — and you beat L2P/DualPrompt-era SOTA on standard splits. **ADAM (renamed APER, AdaPt-and-mERge):** do one parameter-efficient adaptation on the *first* task only to bridge the domain gap, then freeze; concatenate frozen + adapted embeddings and run the same prototype classifier. Also flags that ImageNet-pretrained backbones make ImageNet-derived CL benchmarks meaningless (data overlap) and proposes four harder benchmarks.

## The mechanism (how it actually works)
CIL needs two things that live at different timescales: **generalizability** (features that transfer to classes never trained on) and **adaptivity** (closing the gap between pretrain domain and the incoming stream). The pretrain already supplies the first — so SimpleCIL just extracts each new class's mean embedding and uses it as that class's linear-classifier weight (a cosine/prototype head; streaming, no gradient, no exemplars). For the second, APER runs **one** PEFT pass (adapter / VPT / SSF / full FT — any of them) on session-1 data only. Further sessions never touch the body: new classes are represented by prototypes in the concatenated [frozen ‖ adapted] feature space. Merging protects against the adaptation having overfit session 1 — the raw pretrain view is always retained.

## Key results / claims
- SimpleCIL beats contemporaneous SOTA PTM-CL methods on CIFAR-100/CUB/ImageNet-R style splits **with zero training on the downstream task**.
- APER adds a consistent margin over SimpleCIL; the framework is PEFT-agnostic.
- New benchmarks (ImageNet-A, ObjectNet, OmniBenchmark, VTAB) chosen for large pretrain-to-stream gap — where naive frozen-PTM methods degrade and the single adaptation matters most.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the two-brain split itself (80/20), the P9 freeze, the namer (P7).
- **Same as us:** the architecture is a near-isomorph of ours: a representation fixed after an initial formation period + a streaming prototype head that grows classes without gradients. Their generalizability/adaptivity decomposition is our 80/20 told in PTM vocabulary: pay for representation once, name cheaply forever.
- **Different from us:** (1) their "formation period" is an internet-scale pretrain plus one supervised PEFT session; ours is unsupervised SCFF on the stream itself — no labels, no offline corpus, no session-1 privilege. (2) Their adaptivity is a one-shot event; our bulk keeps SCFF-adapting continuously (drift-tracking, which their frozen trunk cannot do — our P11 gas-sensor win lives exactly there). (3) Their prototype head is cosine-on-concatenated-features; ours passed through a P7 bake-off that also priced covariance (SLDA) and spine-cleanliness.
- **What we could borrow or test:** the **merge trick** — read the namer from [early-formation-snapshot ‖ current] bulk taps, insuring against SCFF drift corrupting a class direction the way APER insures against session-1 overfit. Cheap: one extra stored tap view at sleep time.
- **What contradicts or challenges us:** their benchmark critique cuts our way too — any evaluation where the representation "already knows" the stream inflates the freeze-plus-prototype recipe. Our synthetic home is built by us, so the P11 real-arena map is the required counterpart; the honest question their VTAB-style gap benchmarks pose: how does our object behave when the stream's structure is far from anything SCFF saw during formation? (Our alignment-break and cross-dataset P11 rungs partially answer; a deliberate formation-vs-deployment mismatch rung does not exist yet.)

## Follow-on leads
- EASE (2403.12030 — carded here) — same group's next step: per-task adapters instead of one-shot.
- The LAMDA-PILOT toolbox (github.com/sun-hailong/LAMDA-PILOT) — the reproducibility hub for this family.
- "Adapt before Continual Learning" (2506.03956) — 2025 follow-on making the pre-CL adaptation phase itself the object of study.
