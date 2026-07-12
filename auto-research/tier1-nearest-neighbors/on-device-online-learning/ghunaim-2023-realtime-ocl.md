# Real-Time Evaluation in Online Continual Learning: A New Hope
- **Authors / Year / Venue:** Yasir Ghunaim, Adel Bibi, Kumail Alhamoud, Motasem Alfarra, Hasan Abed Al Kader Hammoud, Ameya Prabhu, Philip H.S. Torr, Bernard Ghanem / 2023 / CVPR 2023 (Highlight)
- **Link:** https://arxiv.org/abs/2302.01047
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐ — the evaluation protocol we have NOT run: the stream does not wait for the learner; slow learners miss data. Our sleep has a latency we never priced in stream-time.

## TL;DR
Proposes **real-time evaluation** for online CL: the stream keeps emitting samples while the model trains; a method that takes k stream-steps of compute per update simply *does not see* (or predicts stale on) the data arriving meanwhile. Under this clock, a simple baseline (small replay + cheap updates) beats every state-of-the-art online CL method tested.

## The mechanism (how it actually works)
Each method is charged in *stream time*: its per-update compute is expressed as a multiple of the baseline's, and while it is busy, the stream advances — new samples get predictions from the stale model and training opportunities are skipped. A method twice as slow trains on half the stream. This converts computational complexity into an *accuracy* penalty endogenously, with no artificial FLOP cap: slow-but-clever loses to fast-and-simple because cleverness costs coverage. The motivating scale: a Twitter-like stream at 350K items/minute — no learner is entitled to pause the world.

## Key results / claims
- Under real-time evaluation, **a minimal baseline outperforms all evaluated SOTA online-CL methods** — the methods' published wins existed only because the stream politely waited.
- The gap grows with the method's compute multiplier; delay is the dominant term, not update quality.
- Framed by the authors as a required paradigm shift for deployable online CL.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the whole live loop of P8.6/P9 — the gate cadence, and especially **sleep**, whose wall-clock latency we have never charged against a moving stream.
- **Same as us:** the design philosophy conclusion is ours — the always-on path must be near-free and the expensive step rare; our SCFF-every-step + rare gated namer is exactly the shape that survives their clock.
- **Different from us:** our evaluations are prequential (P11 gas) or block-mode, but the stream *pauses* during sleep in every phase we ran; energy is metered, **time is not**. They price time and ignore energy; we price energy and ignore time.
- **What we could borrow or test:** **run the frozen object under their protocol** — let the stream flow during sleep consolidation and during gated namer fires; measure how much stream the economy misses at realistic sleep latencies, and whether the drift gate's rarity (f ≈ 0.003) makes us nearly delay-free where BP+replay pays every step. Given our fire fraction, this is likely a *strong win* we have not banked — and the missing piece of the P10 fair race (ER's per-step gradient cost would hurt it badly on this clock).
- **What contradicts or challenges us:** if our sleep re-fit over full LUT history is slow in stream-time, grid-4 cadence could look worse here than the energy meter suggests — the full-history commitment (P8.3) has an unpriced latency cost.

## Follow-on leads
- Prabhu et al. 2023 — the budgeted twin (carded here).
- "A Comprehensive Empirical Evaluation on Online Continual Learning" (arXiv:2308.10328) — the survey-scale replication.
- Delay-aware streaming-ML literature (prequential evaluation with verification latency) — older data-stream-mining framing of the same clock.
