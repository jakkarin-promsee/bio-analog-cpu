# First Session Adaptation: A Strong Replay-Free Baseline for Class-Incremental Learning (FSA)
- **Authors / Year / Venue:** Aristeidis Panos, Yuriko Kobe, Daniel Olmeda Reino, Rahaf Aljundi, Richard E. Turner / 2023 / ICCV 2023
- **Link:** https://arxiv.org/abs/2303.13199
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐⭐⭐ — the closest published twin of our deployed object: body adapted once then frozen, an LDA head with **exact** incremental updates on top, and the explicit finding that *continuing* to adapt the body is counterproductive.

## TL;DR
FSA adapts the pretrained body **only on the first session's data**, freezes it, and puts a linear-discriminant-analysis head on top whose sufficient statistics (class means + shared covariance) update exactly and incrementally with no stored examples. Across 22 datasets it beat SOTA in 15 of 16 settings. The head is our SLDA; the philosophy is our freeze; the difference is where the body came from.

## The mechanism (how it actually works)
The insight is a clean division of labor. **Body:** the pretrain-to-target domain gap is best closed *once*, while the classes available (session 1) still represent the domain; lightweight FiLM-style adapters (feature-wise scale/shift) suffice, and stopping there avoids the drift/forgetting that continuous fine-tuning causes. **Head:** on a *fixed* feature map, LDA is exactly incrementally updatable — running class means and a shared covariance are sufficient statistics, so every new session's update is algebra, not optimization, and is identical to having seen all data jointly (the same joint-equivalence property as the analytic-CL family). No replay is needed because nothing that could forget is ever re-trained.

## Key results / claims
- 22 image datasets, high-shot and few-shot CIL: **beats SOTA in 15 of 16 settings**.
- FiLM adapters are especially effective few-shot (very few writable parameters resist overfitting).
- Explicit takeaway: sophisticated *continuous* body-adaptation schemes (prompts included) are often outperformed by adapt-once-then-freeze + an exact head — continuous adaptation buys interference, not accuracy.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P9 freeze decision, the SLDA namer (P7/P8), the bulk's plasticity policy.
- **Same as us:** the deployed pipeline is nearly ours line-for-line: fix the representation, then a Gaussian-statistics head (means + shared covariance ≡ SLDA) that updates in closed form, exactly, forever, replay-free. Their "continuous adaptation is counterproductive" is the PTM-world echo of our P8 finding that firing the namer more forgets more, and of the P9 freeze.
- **Different from us:** (1) their body starts from a strong pretrain and the first-session adaptation is *supervised*; our bulk starts from nothing and grows *unsupervised*. (2) Their body is frozen absolutely after session 1; our bulk continues label-free SCFF updates for the life of the device — our design bets that unsupervised plasticity is the *safe* kind (it cannot chase labels off a cliff), theirs bets that no plasticity is safest. This is a directly testable disagreement.
- **What we could borrow or test:** **the FSA control, verbatim** — run our system with SCFF halted after a warmup window (bulk truly frozen) vs. continuous SCFF, on (a) the stationary home and (b) the P11 drift arenas. If frozen-after-warmup ties on stationary but loses on gas-style drift, we have the cleanest possible statement of what continuous self-grown plasticity buys — and the anti-FSA scoping of when their advice is wrong.
- **What contradicts or challenges us:** on stationary streams their result predicts our continuous SCFF earns nothing after formation (P9.0's rotates-not-forgets already hints the updates are partly churn). If the FSA control ties everywhere including drift, our "always-on cheap brain" halves into "warmup phase + dead weight," and the energy story changes (though SCFF forward cost is paid for inference anyway — only the update circuitry is at stake).

## Follow-on leads
- FeCAM (2309.14062 — carded t1.2 side) — the per-class-covariance upgrade of the same head family.
- "Exemplar-free Continual Representation Learning" (2407.08536) — when the representation itself must keep learning, the FSA question inverted.
- Turner-group follow-ups on efficient transfer (FiLM adapters in few-shot: TravMD et al. lineage) — the minimal-writable-surface toolkit.
