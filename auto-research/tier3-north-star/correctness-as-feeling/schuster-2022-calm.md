# Confident Adaptive Language Modeling (CALM)
- **Authors / Year / Venue:** Tal Schuster, Adam Fisch, Jai Gupta, Mostafa Dehghani, Dara Bahri, Vinh Q. Tran, Yi Tay, Donald Metzler — 2022, NeurIPS (oral)
- **Link:** https://arxiv.org/abs/2207.07061
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐⭐⭐ — the engineering-complete halt: a cheap internal confidence measure + a *statistical calibration procedure* that turns it into a guaranteed gate. The missing half of every naive confidence signal.

## TL;DR
CALM lets a language model exit early (skip remaining layers) per token when an internal confidence measure crosses a threshold — and, crucially, it does not *trust* the confidence measure: it **calibrates the threshold with a distribution-free hypothesis-testing procedure** (Learn-then-Test) so the early-exit output provably stays within a user-chosen tolerance of the full model's output. Up to 3× speedup at guaranteed consistency.

## The mechanism (how it actually works)
Three candidate confidence signals per layer, cheapest first:
1. **Softmax response** — the gap between the top-1 and top-2 output probabilities (our namer's margin, exactly).
2. **Hidden-state saturation** — cosine similarity between the hidden state at layer L and layer L−1. If the state has stopped moving, more layers won't change the answer. *This is a ‖Δz‖ settling signal — "the state has settled" used as "the answer is decided."*
3. **A tiny trained classifier** on the hidden state predicting "will the full model agree with the current prediction."

The halt itself is trivial (threshold comparator). The load-bearing part is **calibration**: candidate thresholds are treated as hypotheses; each is tested on a held-out calibration set for "risk (disagreement with the full model) ≤ δ"; a fixed-sequence multiple-testing procedure (Learn-then-Test / conformal-style) picks the lowest threshold that passes at confidence 1−ε. The guarantee is distribution-free — no assumption that the confidence signal is "well calibrated," only that calibration data matches deployment.

Two engineering details: per-token exits must respect sequence-level quality (they aggregate token risk into a sequence constraint), and skipped layers leave missing hidden states for future tokens' attention (they copy the exited state upward — a state-reuse hack).

## Key results / claims
- Up to **×3 decoding speedup** on three generation tasks (CNN/DM summarization, WMT translation, SQuAD QA) with provable consistency to the full model.
- The trained classifier and saturation measures work at different cost/quality points; softmax response is strong but expensive at large vocab (irrelevant for us — our namer's output is tiny).
- The guarantee holds only against the *full model's* output (self-consistency), not against ground truth — an honest scoping: it's a compute gate, not a correctness oracle.

## How it relates to us
- **Organ / phase touched:** the recurrent halt (north star §3/§4); the namer's margin; the settling loop's ‖Δz‖; the sleep calibration slot.
- **Same as us:** its two cheap signals are *literally our two planned signals* — the namer margin (top1−top2) and the settled-state Δ (hidden-state saturation ≈ ‖z_t − z_{t−1}‖). CALM is the published proof they suffice for a halt.
- **Different from us:** CALM halts a feed-forward depth sweep; we halt a physical settling loop. Their guarantee target is "agrees with the full model"; our analog is "agrees with the settled fixed point" — cheaper for us since the substrate reaches the fixed point physically.
- **What we could borrow or test:** the **calibration ritual**. Do not hand-pick θ_halt. At every sleep, run the Learn-then-Test sweep over candidate thresholds against the grounded window (LUT + labeled trickle + error-EMA) and ship the threshold that passes at (δ, ε). Sleep already exists; this adds one closed-form pass. It converts "a feeling" into "a feeling with a certificate," and — because it re-runs every sleep — the certificate **tracks drift**, answering Kadavath's OOD-miscalibration failure.
- **What contradicts or challenges us:** their guarantee needs calibration data ≈ deployment data. Under drift that premise decays *between* sleeps — the certificate has a staleness clock, same shape as our stale-namer REV-staircase sag. The gate's trust horizon should be tied to the drift meter (tap-drift), not to wall-clock.

## Follow-on leads
- Angelopoulos et al., "Learn then Test" (arXiv:2110.01052) — the calibration framework itself, worth a dedicated read for the sleep-calibration design.
- Conformal risk control under distribution shift (weighted conformal prediction) — calibration that survives drift.
- BranchyNet / Shallow-Deep Networks — the early-exit ancestors (already named in the north-star dossier graph).
