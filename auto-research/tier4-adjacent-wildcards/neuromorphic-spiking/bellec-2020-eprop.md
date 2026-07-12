# A solution to the learning dilemma for recurrent networks of spiking neurons (e-prop)
- **Authors / Year / Venue:** Guillaume Bellec, Franz Scherr, Anand Subramoney, Elias Hajek, Darjan Salaj, Robert Legenstein, Wolfgang Maass / 2020 / Nature Communications 11:3625
- **Link:** https://www.nature.com/articles/s41467-020-17236-y (open mirror: https://pmc.ncbi.nlm.nih.gov/articles/PMC7367848/)
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐⭐⭐ — the anchor. The gradient factorizes into "local forward trace × broadcast signal", which is structurally *our* architecture with a time axis added; the eligibility trace is literally a leaky capacitor.

## TL;DR
e-prop makes recurrent spiking nets learn online, forward-in-time, with no backward pass and no stored history, by factorizing the exact BPTT gradient into two pieces that are both available in real time: a per-synapse **eligibility trace** (local, computed forward) times a top-down **learning signal** (can be a broadcast). It learns slower than BPTT but approaches its accuracy, and is explicitly pitched as the on-chip learning rule for neuromorphic hardware.

## The mechanism (how it actually works)
Start from the true gradient of a loss over a recurrent net unrolled in time (BPTT). Bellec et al. re-derive it and show it splits *exactly* into a sum over time of two factors per synapse:

`ΔW_ji ∝ − Σ_t L_j^t · e_ji^t`

- **Eligibility trace `e_ji^t`** — a *forward-computed, local* quantity: a fading memory of the recent pre×post coincidence at synapse i→j, carried in the neuron's slow hidden variables (e.g. spike-frequency-adaptation threshold, membrane). It says "this synapse just did something that *might* matter." It is a leaky accumulator — an exponentially-decaying register per synapse. This is the "highway into the future": it holds what the synapse did until the verdict arrives.
- **Learning signal `L_j^t`** — a top-down "how wrong is neuron j right now", routed through per-neuron feedback weights. In the tractable form it can even be a single **broadcast** error signal shared across neurons (symmetric or random feedback).

The trick: BPTT's backward-through-time term is replaced by the *forward* eligibility trace, so credit assignment happens **forward and locally** — no unrolling, no future needed, O(#synapses) memory. The slow neuron variables make the trace span hundreds of ms, so a *late* error signal still lands on the *right* synapses (temporal credit assignment without going back in time).

## Key results / claims
- **TIMIT** phoneme recognition with LSNNs: e-prop approaches BPTT accuracy in a sparse ~12 Hz firing regime.
- **Evidence-integration** task with a 2.25 s delay before the learning signal: e-prop succeeds where plain RSNNs fail.
- **Reward-based e-prop** (three-factor form): an LSNN learns Atari (Pong, Fishing Derby) online, single-agent, **no experience replay**.
- Complexity O(S) (S = synapses), online → "a qualitative jump in on-chip learning capabilities" for SpiNNaker / Loihi.

## How it relates to us
- **Organ / phase touched:** the **north-star recurrent temporal loop** (primary); secondarily the leaky-cap / EMA primitive and the broadcast-correction shape of the namer.
- **Same as us:** the *shape* is our architecture — "local forward computation + a broadcast top-down correction". The eligibility trace = a **leaky capacitor per synapse = the EMA register we already have** (error-EMA gate, momentum). "Local trace × global teaching signal" is our "SCFF bulk + namer correction", now with a temporal justification.
- **Different from us:** e-prop is (a) **spiking + recurrent over an explicit time axis**; our current object is rate-based, feed-forward, i.i.d. sample-at-a-time — *there is no time axis for the trace to integrate*. (b) e-prop is still **gradient descent** (an online BPTT approximation, learns *slower* than BPTT); our committed namer is **closed-form, no gradient at all** (P7). So e-prop solves a problem our current object does not have, with a method our current object deliberately dropped.
- **What we could borrow or test:** the moment the north-star loop has temporal structure, e-prop is the canonical learning rule and *we already own its hardware primitive*. A concrete sim rung: "SCFF-in-time" — add one eligibility register per weight (the leaky cap we have) and a broadcast learning signal, and see whether the recurrent loop learns forward-only.
- **What contradicts or challenges us:** e-prop "learns slower than BPTT" — a reminder that keeping gradients (even online, local ones) still pays a slow-convergence tax. Our closed-form namer bet is precisely that you can *skip* that tax where direction is cheap. e-prop is the neighbor that keeps gradient; we should be able to say why we don't.

## Follow-on leads
- Frémaux & Gerstner 2016 — the three-factor theory e-prop's reward form instantiates (see sibling card).
- Menick et al. 2021 "Practical real-time RTRL" and Zucchet & Orvieto 2023 (RTRL survey) — the exact-gradient parent of e-prop.
- SpiNNaker-2 e-prop (Rostami et al. / Frontiers 2022) — e-prop actually running on neuromorphic silicon.
