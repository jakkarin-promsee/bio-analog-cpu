# Integrating Present and Past in Unsupervised Continual Learning (Osiris)
- **Authors / Year / Venue:** Yipeng Zhang, Laurent Charlin, Richard Zemel, Mengye Ren — 2024 — CoLLAs 2024 (Oral)
- **Link:** https://arxiv.org/abs/2404.19132 (fetched; project: https://mengyeren.com/research/2024/integrating-present-and-past-in-unsupervised-continual-learning/)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐ — the 2024 formalization of what UCL should optimize (stability + plasticity + **cross-task consolidation**), plus evidence that *structured* (realistic) streams make UCL easier — our coherent-drift intuition, published.

## TL;DR
A unifying framework for unsupervised CL identifying three objectives — plasticity (learn the present), stability (keep the past), and **cross-task consolidation** (relate present to past) — and arguing prior UCL methods squeeze all three into one shared embedding space, hurting each. Osiris optimizes them in **separate embedding spaces** (via distinct heads/losses) and wins on standard and two new *structure-aware* benchmarks, where task sequences follow semantic/environmental structure (as real experience does). Preliminary finding: models can do *better* on such structured streams than on shuffled ones.

## The mechanism (how it actually works)
In shared-space UCL, the stability loss (match old features) and the plasticity loss (fit new data) literally pull the same coordinates in opposite directions, and nothing asks the model to notice how new concepts relate to old ones. Osiris hangs three lightweight projection heads off one backbone: one space where the current-task SSL loss runs free, one where features are held to the past model (stability), and one where **current and buffered past samples are contrasted against each other** — the consolidation space, forcing cross-task discrimination structure that neither of the other losses provides. The backbone integrates all three pressures without any single space having to satisfy them simultaneously. Their new benchmarks order tasks by semantic structure (e.g., environment-coherent sequences) rather than random class splits — and the structured order *helps*, suggesting temporal coherence is a resource, not only a nuisance.

## Key results / claims
- Osiris matches or beats prior UCL methods across benchmarks, including two novel structured-sequence benchmarks mirroring real visual experience.
- Ablation-level claim: cross-task consolidation is the missing objective in prior UCL (CaSSLe-style = stability-only bias).
- Preliminary evidence that semantically-structured task orders improve continual learners vs unstructured orders.

## How it relates to us
- **Organ / phase touched:** SCFF objective structure (InfoNCE positives/negatives across time); LUT negatives; P10 order-invariance results; P11 coherent-drift arenas.
- **Same as us:** two deep echoes. (1) Our LUT negatives already make the bulk's InfoNCE contrast current samples against *stored past* samples — mechanically, an accidental version of their consolidation space. (2) Their structured-streams-help finding is the field catching up to our result that coherent drift is the substrate's home turf (gas-sensor win) while shuffled/adversarial orders are everyone's enemy.
- **Different from us:** separate projection spaces per objective (three heads, backprop); an explicit raw-sample buffer; task-boundary snapshots for the stability loss; evaluation by probes, not prequential.
- **What we could borrow or test:** make the accidental deliberate — split our contrast into *within-recent* negatives (plasticity) vs *LUT-past* negatives (consolidation) with separately-tunable weights; one knob, testable on the P11 arenas. If the consolidation share has an optimum, that is the Osiris claim landing in our substrate.
- **What contradicts or challenges us:** their framework implies stability alone (which our frozen-cell + rotation story mostly leans on) is insufficient for representations that must *relate* old and new concepts — relevant the day the north-star recurrent brain needs cross-episode structure, less so for the current classification benches.

## Follow-on leads
- Structured/environment-coherent stream benchmarks — candidate arenas beyond P11's eight.
- The ratio of past-vs-present negatives in contrastive CL — a cheap, unexplored knob in our LUT service.
- Ren-group follow-ups on naturalistic continual learning streams (egocentric video).
