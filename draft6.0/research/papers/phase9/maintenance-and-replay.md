# Maintenance — sleep, replay, and not rotting

*Experience Replay for Continual Learning (Rolnick et al., [1811.11682](https://arxiv.org/abs/1811.11682)); EWC
(Kirkpatrick PNAS 2017, [1612.00796](https://arxiv.org/abs/1612.00796)); Synaptic Intelligence (Zenke et al.,
[1703.04200](https://arxiv.org/abs/1703.04200)); A-GEM ([1812.00420](https://arxiv.org/abs/1812.00420)); replay×sharpness
MGSER-SAM ([2405.09492](https://arxiv.org/abs/2405.09492)). Background: Complementary Learning Systems.*

---

## The problem it answers

Phase 1 found the architecture's home and its decisive win: in the **continual** regime, online backprop forgets
catastrophically while our cell — with a periodic **sleep** that refits the readout full-batch over a **LUT** of
history — *recovers*. That win is real but two things are owed: (1) the cadence and mechanism are hand-set, and Phase 6
must **tune them against this cell's measured drift**; (2) the baseline it beat is **naive online-BP with no replay**,
which is not a fair fight. So: *what does the continual-learning field say the maintenance loop should be, and what is
the honest baseline?*

## The one idea that unstuck it

The field splits maintenance into two families, and we are squarely — and correctly — in the **replay** one:

- **Replay (rehearsal):** keep some old data (or generate it) and **mix it back in** while learning new things. Its
  explicit inspiration is **memory consolidation during sleep** — replay daytime experience to fix it into long-term
  memory. This *is* our sleep + LUT, named. The evidence is strong that **replay is the most reliable continual method**,
  often beating the regularization family outright.
- **Regularization (EWC, SI, MAS):** don't store data; instead estimate **which weights matter** and penalize moving
  them. EWC uses the Fisher information; **Synaptic Intelligence** accumulates a per-weight importance *online* (a
  running sum of `gradient × step` — note: a per-weight running statistic, i.e. **the same kind of register the Scap
  already holds for momentum / the BCM threshold**). These are the cheaper-memory option but lose to replay when task
  importance is spread evenly across weights.

Four findings sharpen this for us:
- **You don't need much history.** Replay works with a *small* buffer, and our Phase-1 result already saw the LUT
  replay correctly at **a third of full store** — consistent with the literature that a modest, well-chosen rehearsal
  set suffices.
- **REMIND is our sleep/LUT, already published.** REMIND (Hayes et al., ECCV 2020) and ACAE-REMIND
  ([2105.08595](https://arxiv.org/abs/2105.08595)) keep a **frozen backbone** and replay **compressed mid-network
  *features*** (not raw images) into the head — *exactly* our "replay tap-features into the readout at sleep" mechanism,
  from the same group as Deep SLDA. It is the closest published cousin to our sleep loop and the natural reference for
  the LUT-replay design (raw-input vs feature storage is the one knob where we differ — we store raw to dodge feature
  drift; REMIND stores compressed features and accepts some drift).
- **A-GEM** is the *efficient* replay baseline: instead of a full retrain, it just **projects** the new gradient so it
  doesn't increase loss on the replay buffer — one extra inner product. This is the **fair, same-budget BP+replay
  baseline** Phase 4 said we owe: not naive online-BP, but BP that *also* gets a replay buffer. Concretely, our racer is
  **`race_bp` + a replay buffer at matched budget** (`race_bp` = the Bartunov/Spyra tuned-BP apparatus carried from
  Phases 4–5; don't invent a weaker comparator).
- **MGSER-SAM** combines replay with **sharpness-aware** updates (flat minima) — a *hypothesised* seam to the noise
  question ([`noise-and-flatness.md`](../phase6/noise-and-flatness.md)): consolidating into a *flat* readout *might* also be
  consolidating into a *noise-robust* one. Two open problems that *may* share one lever — to test, not assume (MGSER-SAM
  was validated for forgetting, not analog-noise tolerance).

## What it means for us

- **Our sleep is replay, and the cheapness has a precise reason: only the readout is replayed.** The full-network
  continual methods (EWC over a whole net, replay-through-a-deep-backbone) pay to protect/replay *everything*. We don't —
  **the SCFF bulk doesn't forget** (it's unsupervised and drifts slowly), so sleep only re-aims the small convex readout
  over the LUT. That is *why* the recovery is cheap, and it's a genuinely different cost profile than the literature's
  replay (which is the headline of the same-budget comparison: a fair BP+replay must replay gradients through the whole
  net; we replay one forward pass into a small head).
- **The cadence question = the drift detector at a slow timescale.** "When to sleep" is "when has enough SCFF drift
  accumulated that the readout's coverage has decayed" — the *same* signal as the per-step gate
  ([`the-economy-gate.md`](../phase8/the-economy-gate.md)), integrated. So sleep-cadence is not a separate magic number; it's the
  drift detector with a longer window. And it should be **readout-aware**: consolidate the **extractor depth the fixed
  reader actually reads** (shallow on the flat home, deep on compositional tasks), not the whole stack.
- **The fair baseline is A-GEM-style BP+replay, and we should run it.** Phase 4's continual WIN was vs naive online-BP;
  the honest Phase-6 claim needs **OURS vs BP+replay at matched buffer + matched compute.** We may still win (cheaper
  replay, non-forgetting features) — but we have to show it, not assume it.
- **Caveat — replay's quiet costs are real for a chip, and a drift-gated stream makes them worse.** A bounded on-chip
  LUT under a lifelong stream **must evict**, and the continual-safety mechanism leans on negatives/replay drawn from
  *across* tasks — evict wrong and forgetting re-enters through the buffer (the architecture file §2.4 flags this as
  unsolved). Worse: a drift-**gated** stream presents classes in **bursts**, so the buffer is **class-imbalanced** by
  construction — the exact problem the **class-balancing reservoir sampling (CBRS)** / imbalanced-online-CL line
  (Chrysakis & Moens, ICML 2020) exists to fix, and the streaming head needs a **logit-adjustment / balanced-softmax**
  ([2311.06460](https://arxiv.org/abs/2311.06460)) guard so the burst doesn't bias it. Our ART/vigilance prototype
  allocation is *a* "keep it representative" rule, but it isn't class-balanced — **how it interacts with a bounded,
  imbalanced store under lifelong drift is untested**, and is a first-class Phase-8 risk (not a footnote). And the whole
  "only the readout is replayed, the bulk doesn't forget" cheapness rests on the bulk *actually* not drifting — measure
  it (representation drift in SSL-continual is real, [2203.13381](https://arxiv.org/abs/2203.13381)), don't assume it.
