# main.ideas.v1 — Draft 6.0, the approved design

**Snapshot v1 · 2026-06-12.** This is the *decision record* — what we've committed to and why, one line each. The full story behind each call is in [ideas1.md](ideas1.md); the outside papers are in [../ref/](../ref/README.md). Where this disagrees with the draft-5.1 "locked decisions" in the top-level `CLAUDE.md`, **this wins for draft-6.0 work** — 5.1 is the pre-pivot world.

---

## The whole thing in one breath

Two brains. A cheap, unsupervised **SCFF** front (~80%) that organizes the world for free, and a small, precise **gradient-descent** back (~20%) that puts real labels on it — because direction is the one expensive thing in learning, so we pay for it *once*, where it counts. The two are chained as **residual boosting blocks**: each block a weak corrector, SCFF doing feature work inside the residual stream, a GD checkpoint at each block's exit. Learning is **threshold-gated** (cheap local SCFF most of the time; expensive direction only when the cheap path stalls) and **sleep-consolidated** (periodic full-batch GD over a prototype memory, so nothing rots).

---

## The net — the three approved calls

**N1 · SCFF stays the cheap brain.** Vanilla, unsupervised — the only rule that is local + derivative-free + forward-only + unsupervised at once. Relabel our **summation** form as *our* reformulation of the paper's concatenation (exact because `W₁=W₂`; first-layer-only; it's what makes mono-forward possible). Keep Distance-Forward's **margin loss on standby** for if the log-loss is mushy. → [scff.md](../ref/scff.md), [distance-forward.md](../ref/distance-forward.md)

**N2 · The middle layer = stability + coordination, split apart.** Don't blend two objectives on one layer — they fight. Instead: **plasticity-gradient slowdown** (mirror LLRD — slow the *late* SCFF layers GD reads) for stability, plus **DF-O overlapping blocks** for coordination. **EMA-view** (BYOL momentum encoder) is the de-risked upgrade if the cheap slowdown pinches SCFF's learning. → [llrd.md](../ref/llrd.md), [distance-forward.md](../ref/distance-forward.md), [byol.md](../ref/byol.md)

**N3 · GD = residual boosting blocks.** Each GD checkpoint fits the *residual* the previous one left (boosting telescoping sum — BoostResNet); SCFF does feature work inside the residual stream. The boosting guarantee lives on the labels → in the GD checkpoints, not the unsupervised SCFF stages. → [boostresnet.md](../ref/boostresnet.md)

---

## Supporting structure (committed)

**S1 · Path diversity comes from depth, not input-width.** Concatenation's only edge over summation was path diversity (training-time over-parameterization) — and it's *redundant* diversity that collapses to `W₁=W₂`. Depth buys it better: non-redundant capacity, uniform width-`d` rails, and it matches our own locked "path-diversity-per-scap" topology. Depth's cost is coordination debt — which N2 + N3 already exist to pay down.

**S2 · Mono-forward, dual-rail.** One forward sweep, two worlds (positive + negative) side by side through the *shared* weight crossbar. Doubles only the **LocalCapacitor** activation buffers (RAM-like temp `a` values), **not** the Scaps. Trades cheap buffer area for one charge cycle instead of two. Both goodnesses stay explicit → full two-sided loss, no scale runaway.

**S3 · GD reads via taps.** GD reads the last `n` SCFF layers (richer than one thin top layer; precedented by SCFF's own all-layer readout). GD reads, never writes into SCFF → no shared weights, and a built-in stop-gradient (BYOL's anti-collapse condition, for free).

**S4 · Two GD organs.** *Interface GD* (small, per-block exit, tracking job, SGD+momentum, squared error) vs *Output GD* (the brain, final, 2–3 layer residual MLP, Adam-class online / full-batch at sleep, cross-entropy).

**S5 · Inter-layer normalization, mandatory.** Required by FF for correctness (the next layer can't just recycle the previous layer's goodness) — and now load-bearing twice, because it's also the guard against the residual shortcut (a block inflating `‖h‖²` just by passing its input through).

**S6 · Threshold-gated learning.** Loss < θ → SCFF only (cheap, local). Loss ≥ θ → SCFF + chained GD delta. Justified by the gradient-mismatch ε-floor: local learning converges while block disagreement is small, stalls when it dominates. Candidate refinement: gate on loss-*slope* (plateau detection), not absolute loss.

**S7 · Sleep consolidation.** Periodic full-batch GD over history, re-covering the whole data range against the *current* SCFF map. Cheap by construction (GD ≈ 20% of weights, SCFF body frozen). Robustness from tap-normalization + drift-spanning replay + free analog noise augmentation.

**S8 · LUT prototype memory.** Deduplicated raw-input prototypes (winner-take-all novelty allocation). One store, three customers: SCFF negatives, sleep replay, and the seed of the future "memory model" (the hippocampus track). Experiment 3.2 becomes the prototype-history cell.

---

## The drift fix (resolved)

GD breaks if SCFF drifts faster than GD can re-track. This is **not** a contested-weight problem — taps mean SCFF and GD never share a weight. So we bound drift cheaply with the **plasticity gradient** (N2). The budget rule: lower the read-layer learning rate (free) rather than fire GD more often (burns the 80/20). Permutation / re-clustering events are the one thing slow-LR only *delays* → guard with BCM homeostasis (on the existing momentum register) + the multi-layer tap as redundancy.

---

## Open knobs — the sims decide, not us

- Front:back plasticity ratio — exp 2.1 (frozen vs slow vs fast read-layers).
- Gate threshold — absolute vs plateau-slope.
- Sleep cadence — couples to cluster-churn rate, and to EMA τ if the EMA-view is used.
- How little history sleep needs (3.x); LUT vigilance threshold.
- Margin loss vs log-loss; two-sided vs pure-contrast objective.
- How many chained blocks before direction-chaining strains.
- Tied-from-start vs converge-to-tied first layer — does forcing summation cost any training ease?

---

## Status

**✅ Phase 1 ran and is complete (2026-06-20, exp0 → exp4).** Spine confirmed; numbers found. Full synthesis: [`../src/phase1/phase1-summarize.md`](../src/phase1/phase1-summarize.md) + ledger [`../src/phase1/RESULTS.md`](../src/phase1/RESULTS.md). **Verdict:** a cheap, *forgetting-robust* **continual** learner — one block generalizes better than backprop (smaller memorization gap) at ~10% backward cost, and in the continual regime sleep recovers what online backprop catastrophically forgets; it is **not** a deep static-accuracy competitor (SCFF is weak, shallow-is-better, depth saturates). **Knobs the sims set:** goodness = **sum ‖h‖²**, θ=2.0, input-norm, **tap all SCFF layers** (S3 "last n" corrected), two-sided loss, **full residual ε=1** (N3 boosting; Ch9 delta off), **slow read-layers** (N2 ρ≈0.3), default **H=64**. **✅ Phase 2 (depth) also ran and is complete (2026-06-21, P2.0 → P2.6).** Synthesis: [`../src/phase2/phase2-summarize.md`](../src/phase2/phase2-summarize.md) + ledger [`../src/phase2/RESULTS.md`](../src/phase2/RESULTS.md). **Verdict: depth is not SCFF's lever** — a deep SCFF stack cannot earn depth on *either* axis: not **transmission** (P2.1 — norm × goodness fixes the mechanism but not the depth curve) and not **objective** (P2.2 — *even a perfect label-oracle* hard negative doesn't bend the slope). The wall is **intrinsic to forward-only locality** (no cross-layer coordination — what GD exists to supply). Depth instead comes from **boosted ensembles of *shallow* SCFF blocks with tiny GD readouts** (P2.5 — `read`/ensemble earns it cheaply: ~85% of GD accuracy at ~1/6 backward; `write`/re-inject **fails**), and the recipe **preserves the continual win + is continual-safe by construction** (P2.6 veto). So the *SCFF-likes-width / Scap-likes-depth* collision resolves by the **other horn — depth = block-count, not SCFF-layer-count**. **Tools' fates:** online batch-norm/SymBa/hard-negatives = *don't earn depth* (mechanism-only); the γ scalar + deep supervision (P2.3/P2.4) = *skipped, moot*; **GD-between blocks = the survivor**. **Spec set:** recipe `[SCFF×k → GD-readout]×N` (**read**, healthy *layer-norm + linear + contrast* cell, sleep-consolidated, few blocks); **contrast > two-sided θ**. **What's next → Phase 3 = depth, round 2 — the objective reframe.** Energy-goodness SCFF can't earn depth (Phase 2's decisive negative), so Phase 3 tests the one lever Phase 2 never touched: a different *objective family*. The Phase-3 literature pass (`../ref2/`) found the wall is **intrinsic to the energy objective `G=Σh²`, not to forward-only locality** — Greedy InfoMax / CLAPP (and greedy layer-wise autoencoder pretraining, Hinton'06/Bengio'07) are forward-only, unsupervised, *and depth-composing* because their objective is **information-preserving / predictive**. So Phase 3 swaps the per-layer goodness energy → **masked-feature reconstruction** (decided primary: single-sample, info-preserving), with sibling-contrastive (CLAPP) as control, OLU cross-layer coordination as a booster, Mono-Forward as the supervised-local fallback; the continual veto is unchanged (the new objective must *re-earn* the Phase-1 win). Plan: [`../src/phase3/README.md`](../src/phase3/README.md); survey: [`../ref2/README.md`](../ref2/README.md). **Phase 4** = online maintenance — the **Ch7 gate** + **sleep-*cadence*** / LUT-vigilance sweep (sleep **already built**, exp4) + GD-coshaping, tuned against the drift Phase 2 *measured* (*this was "Phase 3" — renumbered 2026-06-21*). The **recurrent lifelong brain is the north star**, beyond the numbered phases. Analog/PVT realism runs in parallel once a phase's ideal converges.

_Original next-action (now done):_ the experiment ladder in [ideas1.md](ideas1.md) (§ "The experiment ladder"), starting at **1.0 — full SCFF**, with mono-forward dual-rail and mandatory inter-layer normalization in from the first run.

The codeable Phase-1 spec is [`../src/phase1/README.md`](../src/phase1/README.md) (0th probe → Exp 1–3, with Exp 4 = gate + sleep). **Note the reorder:** Phase 1 runs chaining (Exp 3 ≈ ladder 4.x) *before* the maintenance layer (Exp 4 ≈ ladder 3.x sleep + Ch 7 gate) — structure first, maintenance once Exp-3 drift shows how much is needed. **Resolution (Ch 9 vs N3):** Exp 3 makes **N3 residual boosting** the primary chaining mechanism; the Ch 9 linear inter-block delta is demoted to an optional, off-by-default top-up. **Phase-1 pass metric:** held-out generalization is the headline; the **train−held-out memorization gap** is the block-vs-GD comparison (not the online curve, not a single scalar).
