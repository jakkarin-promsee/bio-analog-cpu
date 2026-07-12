# RanDumb: Random Representations Outperform Online Continually Learned Representations
- **Authors / Year / Venue:** Ameya Prabhu, Shiven Sinha, Ponnurangam Kumaraguru, Philip H.S. Torr, Ozan Sener, Puneet K. Dokania / 2024 / NeurIPS 2024
- **Link:** https://arxiv.org/abs/2402.08823
- **Tier / Topic:** tier1-nearest-neighbors / t1.2 analytic continual learning
- **Relevance:** ⭐⭐⭐⭐ — the field's sharpest skeptic control — and the namesake of our own P7.0 "RanDumb control" that our bulk had to beat before the bake-off counted.

## TL;DR
RanDumb embeds raw pixels with a *fixed random transform* (random Fourier features approximating an RBF kernel, fixed before any data is seen), then trains only a streaming linear/LDA-style classifier on top — one pass, no exemplars, no representation learning at all. It beats state-of-the-art online continually-*learned* representations across standard OCL benchmarks. The claim: online continual representation learning, as practiced, is worse than not learning the representation.

## The mechanism (how it actually works)
1. **Random kernel embedding:** raw input → random Fourier feature map (Rahimi–Recht machinery) ≈ RBF kernel lift, sampled once at t=0, never trained.
2. **Decorrelated linear head:** a simple streaming classifier (LDA-flavored, with feature decorrelation) fit online, sample-at-a-time, exemplar-free.
3. **The experiment:** swap the learned encoder of SOTA online-CL methods for this random lift; keep everything else. The random lift wins — consistently — in low-exemplar and online regimes. With pretrained models, a frozen-feature linear probe similarly beats continual fine-tuning/prompt-tuning.

The mechanism *is* the control condition: it exists to expose that the hard part (representation) was not being learned productively under online-CL constraints.

## Key results / claims
- Outperforms continually learned representations across standard online-CL benchmarks; the gap is systematic, not marginal.
- In pretrained settings, frozen features + linear probe > most continual fine-tuning and prompt-tuning strategies.
- Implication claimed: representation learning is the bottleneck-shaped illusion of online CL; the classifier-on-frozen-lift is the honest baseline every method must beat.

## How it relates to us
- **Organ / phase touched:** P7.0's bench guard (our control is named after this paper) — and, by extension, the legitimacy of the whole SCFF bulk.
- **Same as us:** the architecture is literally our namer minus the bulk: random lift + streaming closed-form head (RanPAC's projection is the same move one level up).
- **Different from us:** RanDumb is an *indictment* of learned online representations; our P7.0 result is our *acquittal* — the trained SCFF bulk **beats a random projection of raw pixels for every head** (earning its keep), while honestly *tying* a random expansion of its own taps for a plain linear namer (the expected ELM effect) and winning it for the ridge head. P11.0 extends the acquittal at depth: Δbulk +0.417 on the synthetic home vs. a random 12-layer reservoir — the bulk is learned, not lucky.
- **What we could borrow or test:** their decorrelation detail on the streaming head is worth one bench cell; their benchmark suite is the external stage where our "bulk beats RanDumb" claim would carry old-world weight.
- **What contradicts or challenges us:** the paper's thesis is aimed at exactly our class of claim ("my continually-learned representation helps"). It is the strongest published prior *against* us, which is why keeping the control in every future bench (and citing it) is cheap insurance — our evidence answers it on our arenas, not universally.

## Follow-on leads
- Rahimi & Recht 2007 — random features for kernel machines (the lift's theory).
- LoRanPAC (arXiv 2410.00645) — the theory-side reconciliation: *why* random lifts + ridge work in CL.
- The "linear probes beat prompt tuning" thread in pretrained-model CL (RanPAC's own ablations continue it).
