# Continual Pre-Training Mitigates Forgetting in Language and Vision
- **Authors / Year / Venue:** Andrea Cossu, Tinne Tuytelaars, Antonio Carta, Lucia Passaro, Vincenzo Lomonaco, Davide Bacciu — 2022 (arXiv) / 2024 (Neural Networks, vol. 179) 
- **Link:** https://arxiv.org/abs/2205.09357 (fetched; journal: https://www.sciencedirect.com/science/article/pii/S0893608024004167; code: https://github.com/AndreaCossu/continual-pretraining-nlp-vision)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐⭐ — the factor analysis: of modality, architecture, and pretraining protocol, **the protocol (self-supervised vs supervised) matters most for forgetting** — and SSL wins.

## TL;DR
Formalizes *continual pre-training*: a model keeps pre-training on a stream of incoming data and is only later fine-tuned to downstream tasks — the closest mainstream scenario to a representation that lives on the stream. Across language and vision, **self-supervised continual pre-training mitigates forgetting without any CL strategy at all**, and a factor decomposition (modality × architecture × protocol) finds the pre-training protocol is the dominant factor: SSL retains prior knowledge far better than supervised protocols.

## The mechanism (how it actually works)
Split the lifelong problem into two loops: an inner, never-ending *pre-training* loop that only ever optimizes a label-free objective on whatever data arrives, and an outer, occasional *fine-tuning* loop that adapts snapshots to tasks. Forgetting is then measured where it matters — in the downstream usefulness of the continually-pre-trained representation, not in any classifier head. Because the label-free objective never encodes task boundaries or class boundaries, sequential pre-training updates move the representation *along* directions that preserve generic structure; supervised continual pre-training, by contrast, keeps re-aiming features at each round's label set, and that is where the knowledge loss concentrates. The striking part is the "no CL strategy" clause: no replay, no distillation, no regularizer — the objective's own geometry is the protection.

## Key results / claims
- Self-supervised continual pre-training suffices to mitigate forgetting in both NLP and vision — without replay/distillation/regularization.
- Factor analysis over modality (NLP/Vision), architecture (Transformer/ResNet), protocol (supervised/self-supervised): **protocol is the most important factor accounting for forgetting**; SSL retains best.
- Robustness holds across the tested downstream suites (journal version, Neural Networks 2024).

## How it relates to us
- **Organ / phase touched:** the always-plastic SCFF bulk (P8 live loop; P9.0 rotates-not-forgets); the two-loop split mirrors bulk-learning vs sleep-refit.
- **Same as us:** the strongest mainstream echo of our operating regime — a label-free representation that *keeps training forever* and stays safe without CL machinery. Their "no CL strategy needed" is our P9.0 measured at scale, in backprop-world.
- **Different from us:** their continual pre-training is chunked (large data increments, multi-epoch, backprop, IID within chunks), not one-pass temporally-correlated streaming; downstream evaluation is fine-tuning, not a live closed-form namer; no cost model.
- **What we could borrow or test:** their factor-decomposition design (modality × architecture × protocol) is the template for the public version of our attribution question — ours would be objective (label-free vs label-injected) × plasticity (frozen vs live) × substrate (analog vs digital), which P8.7/P11 partially fill; one missing cell (label-injected live bulk) is the Marczak control.
- **What contradicts or challenges us:** the Marczak caveat applies here too — their supervised-vs-SSL protocols differ in more than labels; and their gentler chunked-IID streaming means they never face the autocorrelation floor that breaks us (and Purushwalkam's SSL) on real streams.

## Follow-on leads
- Continual pre-training at LLM scale ("Simple and Scalable Strategies to Continually Pre-train LLMs", arXiv 2403.08763) — the scaling side of the same claim.
- "The Future of Continual Learning in the Era of Foundation Models" (arXiv 2506.03320) — positions continual SSL pre-training as a key direction; context for where the field is heading.
- Chunked-IID vs truly-streaming continual pre-training — the gap between their setting and ours.
