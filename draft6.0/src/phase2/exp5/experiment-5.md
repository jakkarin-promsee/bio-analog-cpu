# Experiment P2.5 — multi-block: does GD *between* shallow SCFF earn the depth deep SCFF can't?

> **Status: ✅ RUN COMPLETE (2026-06-21) — verdict: GD-between (READ) earns depth marginally + cheaply; WRITE
> fails; Phase-2 depth arc CLOSED → route P2.6.** P2.1 (transmission) + P2.2 (objective) proved depth is not the
> lever *inside* SCFF. P2.5 tested GD *between* shallow SCFF groups: **`read` (boost the block readouts) beats
> pure-SCFF by a disjoint-IQR margin (+0.010, 5/5) — but marginally and saturating ~2–4 blocks; `write`
> (re-inject the GD rep into the stream) fails decisively (−0.04→−0.09).** The real prize is **cost**: `read`
> reaches ~85% of pure-GD accuracy at ~1/6 of its backward cost (forward-only SCFF bulk + tiny GD readouts). The
> depth question is *answered, not won*: depth comes cheaply from boosted shallow blocks (GD as readout, not
> stream-rewriter), and the architecture's real home stays the *continual* regime (Phase-1). Convention:
> question → setup → run → result → read → decision. Spec: [`../README.md`](../README.md) §P2.5. Reporting:
> [`../result-format.md`](../result-format.md). Re-tests Phase-1 exp3 (the boosting chain) under the substrate
> framing on the CIFAR-flat headline.
>
> **Folder note:** `exp5/` = P2.5 (folder = rung, per exp0=P2.0…exp2=P2.2). There is no `exp3/`/`exp4/` — **P2.3
> (collaboration) and P2.4 (interface) were skipped**, made moot by the P2.1+P2.2 decisive negatives (they refine
> a deep SCFF stack that shouldn't exist). The gap is intentional and documents the skip.

## Question

1. **Does GD-between turn the declining pure-SCFF depth curve into a rising/held one?** At fixed total SCFF
   depth (8 layers), as we insert more GD checkpoints (cadence `k` = SCFF layers per block; `N = 8/k` blocks),
   does final accuracy climb from the pure-SCFF floor (~0.20, the P2.1 wall) toward the GD ceiling (~0.35)?
2. **Read vs write — does the GD checkpoint need to *write* back into the stream?** `read` = GD is a readout
   only (boosting ensemble; the next SCFF block sees raw SCFF features — Phase-1 exp3). `write` = the GD-realign's
   class-aligned hidden representation *feeds the next SCFF block* (re-injecting the label direction SCFF sheds —
   the "class-alignment reset" hypothesis). Does write beat read?
3. **At what backward cost?** Each checkpoint adds GD (backward) weight. The substrate cares: what cadence `k`
   buys how much accuracy, vs pure-GD which pays full backward? (The accuracy/cost Pareto — Phase-1 F7.)

**Pass gate (README §P2.5).** Some cadence `k` **beats pure-deep-SCFF** (disjoint IQR) at the depth-8 budget,
naming the GD-between cadence. (Phase-1 prior: the boosting chain saturates ~2 blocks — so the live question is
*whether write pushes past that*, and how cheaply.)

## Hypothesis (committed)

> **GD-between earns depth where deep SCFF can't — that's the whole point of the 20%.** Even one GD checkpoint
> re-aligns the representation to class; stacking shallow SCFF *between* checkpoints then organizes a
> class-aligned space rather than a density one. So final accuracy should climb with checkpoints toward the GD
> ceiling. **Write should beat read:** read only ensembles myopic SCFF features (Phase-1's ~2-block saturation —
> the blocks are too redundant to ensemble well); write re-injects the class direction *into the stream*, so each
> SCFF block starts class-aligned and the next can build genuinely new features (BoostResNet's diverse weak
> learners). **The honest caveat:** flat-MLP CIFAR has a low GD ceiling (~0.35), so "earns depth" means *climbs
> toward 0.35*, not high absolute accuracy — and Phase-1's saturation prior may cap the gain. If even write
> saturates fast, the verdict is "GD-between recovers the lost depth but doesn't compound it" — still the
> constructive answer (depth = blocks, cheaply), just bounded.

## Setup (LOCKED — methodology rule #3)

**Fixed total SCFF depth = 8 (comparable to P2.1/P2.2). The variable: GD-checkpoint cadence `k` × mode.** Each
SCFF block uses P2.1's validated **healthy shallow cell** (layer-norm + linear + contrast — no death, rank
preserved). Greedy block-wise training (SCFF local, then GD-realign supervised) = the boosting order.

| Knob | Value | Why |
| --- | --- | --- |
| **Headline task** | **CIFAR-10-flat** — same `load_cifar_local` as P2.0–P2.2 | directly comparable to the P2.1/P2.2 wall curves; the documented thin regime (GD ceiling ~0.35). |
| **Per-block SCFF** | `k` layers, width 64, **layer-norm + linear + contrast** (P2.1 healthy cell) | the validated shallow front (no deactivation, rank preserved). |
| **GD-realign** | MLP `[blk-alltap → 64 → C]`, Adam + cross-entropy, supervised; hidden (64-D) is the class-aligned rep | the coordinating 20%; `read` uses its logits, `write` feeds its hidden forward. |
| **Cadence grid** | `N ∈ {1, 2, 4, 8}` blocks, `k = 8/N` (so total SCFF depth = 8 always). N=1 (k=8) = **pure-SCFF baseline** (≡ P2.1 wall + readout) | one axis: # GD checkpoints in a depth-8 stack; equal SCFF depth, varying GD cadence. |
| **Mode** | `read` (ensemble of block readouts — boosting) vs `write` (GD hidden feeds next block — class-realign reset). N=1 identical for both. | the decisive read/write fork (the new lever vs Phase-1 exp3). |
| **Final prediction** | read: sum of all block logits (boosting ensemble); write: last block's logits (the class-aligned final rep) | each mode's natural readout. |
| **References** | **pure-GD ceiling** (full backprop, matched total weights) + the **pure-SCFF** point (N=1) | the envelopes: does GD-between climb from pure-SCFF toward GD? |
| **Cost** | backward weights = Σ GD-realign weights (per config), vs pure-GD's full backward | the substrate Pareto (accuracy / backward-cost). |
| **Probe / seeds / realism** | per-block all-tap linear probe C=1.0 · seeds `[42,137,271,314,1729]` median+IQR · ideal floats, single-threaded (OpenMP phantom guard) | pinned metrics; one axis at a time. |

**Must emit** (`result-format` map for P2.5): **BLOCK** (final accuracy vs #blocks N / cadence k, read & write,
+ pure-SCFF & GD-ceiling envelopes — the headline), **F3⁺** (per-block all-tap probe trajectory — does the
stream stay/again-become class-separable in write vs degrade in read/pure?), **F7 BACKWARD** (accuracy vs
backward-cost Pareto), **INV**. *(CONT-veto deferred to P2.6 unless a config clearly wins.)*

## Run

*Pending — build: (1) `Block` = k-layer SCFF (healthy cell) + GD-realign (MLP w/ hidden accessor); greedy
sequential train; read/write stream wiring. (2) `run_exp5.py` (cadence × mode grid + GD ceiling + cost). (3)
`plot_exp5.py` (BLOCK/F3⁺/F7/INV). (4) smoke (synth, 2 seeds) → CIFAR 5-seed, single-threaded.*

## Result / figures

**Run 2026-06-21**, 5 seeds, CIFAR-10-flat, single-threaded. Figures in [`figs_exp5_cifar/`](figs_exp5_cifar):
[BLOCK](figs_exp5_cifar/BLOCK.png) (the headline) · [F3⁺](figs_exp5_cifar/F3plus_perblock.png) (per-block probe) ·
[F7](figs_exp5_cifar/F7_backward.png) (accuracy/backward Pareto). `arrays.npz` + `manifest.json` saved.

| config (n=5 median) | final acc [IQR] | vs pure-SCFF | backward weights |
| --- | --- | --- | --- |
| **pure-SCFF** (N=1, k=8) | 0.292 [0.283,0.293] | — (the P2.1 wall + readout) | 33.5k |
| `read` N=2 | 0.283 [0.279,0.288] | −0.009 | 34.2k |
| `read` N=4 | 0.300 [0.297,0.319] | **+0.008 ✓ (disjoint)** | 35.6k |
| **`read` N=8** | **0.302** [0.300,0.307] | **+0.010 ✓ (disjoint)** | 38.5k |
| `write` N=2 | 0.251 | −0.041 | 34.2k |
| `write` N=4 | 0.234 | −0.059 | 35.6k |
| `write` N=8 | 0.205 | −0.087 | 38.5k |
| **pure-GD ceiling** | **0.354** | +0.062 | **230k** |

**Pass gate MET (technically):** `read` N=4 and N=8 beat pure-SCFF by a disjoint-IQR margin (5/5 seeds) — so
GD-between (read / boosting) **does** earn depth. But the gain is **small and saturating** (+0.010, closes only
~16% of the pure→GD gap), and **`write` fails decisively** (monotone −0.04 → −0.09).

## Read (eight-slot)

1. **Claim.** **Depth comes from *ensembling* shallow SCFF blocks (read), not from re-injecting GD into the
   stream (write) — and the real prize is cost, not accuracy.** Inserting cheap GD readouts between shallow SCFF
   groups and boosting them (`read`) marginally beats a monolithic deep SCFF stack (+0.010, disjoint-IQR) where
   P2.1 proved deep SCFF *can't* improve at all. But feeding the GD-realign's class-aligned hidden *back into* the
   SCFF stream (`write`) is actively harmful and gets worse with every checkpoint. The headline is the
   **substrate Pareto**: `read` N=8 reaches **85% of pure-GD's accuracy (0.302/0.354) at ~17% of its backward
   cost (38k/230k)** — because the expensive 3072-D front is learned forward-only by SCFF; only tiny per-block
   readouts pay backward.
2. **Number + IQR.** `read` N=8 0.302 [0.300,0.307] vs pure-SCFF 0.292 [0.283,0.293] (+0.010, disjoint, 5/5);
   `write` N=8 0.205 (−0.087, monotone over N). GD ceiling 0.354. Backward: read/write 34–38k vs pure-GD 230k
   (**~6× cheaper**). n=5.
3. **Figures.** [BLOCK](figs_exp5_cifar/BLOCK.png) (read flat-rising past pure; write collapsing) ·
   [F7](figs_exp5_cifar/F7_backward.png) (the cost Pareto — read sits near GD accuracy at a fraction of backward
   cost) · [F3⁺](figs_exp5_cifar/F3plus_perblock.png) (per-block probe).
4. **Mechanism.** **Read works (a little)** because boosting ensembles *diverse* shallow weak learners
   (BoostResNet; Phase-1 exp3) — but the blocks are myopic and redundant, so it **saturates ~2–4 blocks** (the
   Phase-1 finding, reconfirmed). **Write fails** because the GD-realign's hidden is *class-collapsed* (trained
   to predict 10 logits); running SCFF on it forces the next block to re-cluster a low-information, already-
   collapsed representation — it throws away the rich raw features and the loss compounds with depth. The stream
   must carry the **rich SCFF features (read)**, never the **class-collapsed GD rep (write)**. The read/write
   fork resolves firmly to **read**.
5. **Threats.** (a) The accuracy gain is *small* (flat-MLP CIFAR is thin; GD itself only reaches 0.354) — the
   load-bearing results are the **direction** (read > pure > write, all disjoint) and the **cost ratio**, not the
   magnitude. (b) `read`'s ensemble is a simple logit-sum; a tuned gradient-boost (Phase-1 exp3) might squeeze a
   little more, but the saturation is robust. (c) Single-seed `read` N=2 dips below pure — the gain is real only
   by N≥4 and is genuinely marginal.
6. **Decision.** **Phase 2's depth question is CLOSED. The depth recipe = cheap boosted ensembles of shallow
   SCFF blocks (read), GD as a *readout* not a stream-rewriter.** Modest accuracy gain, ~6× backward saving — the
   "cheap brain" thesis, exactly. → Route to **P2.6 (substrate filter + continual veto)** as the final Phase-2
   deliverable: confirm this recipe is single-sample-online-feasible and **preserves the Phase-1 continual win**
   (ACC+BWT). *(Full in ## Decision.)*
7. **Substrate-feasibility (slot 7).** Strong: the whole SCFF body is forward-only/local (0 backward); only the
   per-block readouts are GD, totalling ~17% of full-backprop weight. `read` N=8 = 8 forward-only SCFF layers +
   8 tiny backward readouts. This is the substrate's native shape (cheap forward bulk + small backward heads).
   `write` is rejected — it needs the GD rep to flow *into* the next SCFF block (extra coupling) *and* it loses
   accuracy. **online-single-sample feasibility of the readouts → P2.6.**
8. **Continual-preservation (slot 8).** Deferred to P2.6 (no continual run this rung). The boosted-read recipe is
   structurally Phase-1's validated block/chain, which exp4 already showed is forgetting-robust under sleep — so
   the prior is favourable, but the veto (ACC+BWT with this exact recipe) is P2.6's job.

## Decision

**Phase 2's depth arc is CLOSED — and the answer is constructive, if modest.** Across P2.1 (transmission), P2.2
(objective), and P2.5 (multi-block), the complete picture:

- **Deep SCFF cannot earn depth** (P2.1 + P2.2, decisive — even a perfect oracle fails).
- **GD-*between* shallow SCFF earns depth (read/boosting), but marginally and saturating** (~2–4 blocks, +0.010;
  Phase-1 exp3 reconfirmed on the substrate task). It does **not** reach the GD ceiling.
- **The win is cost, not accuracy:** the read recipe gets ~85% of GD's accuracy at ~1/6 of GD's backward cost —
  the cheap-forward-bulk + small-backward-head shape the chip is built for.
- **`write` (re-inject GD into the stream) is rejected** — class-collapsed reps destroy the rich features;
  GD must *read* the SCFF stream, not *overwrite* it. (A clean negative for the "class-alignment reset" idea.)

**This is not a depth victory; it is the depth question *answered*.** The README §0 substrate-collision resolves
exactly as Phase-1 predicted: SCFF is the cheap shallow front, depth is bought *cheaply* by stacking boosted
blocks with small GD readouts — accepting that static-accuracy depth gain is modest, because **the architecture's
real home is the *continual* regime, not static depth** (Phase-1's verdict, never overturned).

- **Route → P2.6 (substrate filter + the continual veto).** The final Phase-2 deliverable: re-run the boosted-read
  recipe through the online / single-sample filter and the exp4 continual stream (ACC + BWT). Does the depth
  recipe preserve the Phase-1 continual win? That is the question that actually matters for this architecture.
- **Carry forward:** `read` (boosting), **not** `write`; per-block SCFF = the healthy P2.1 cell; cadence k is a
  cost knob (more blocks ≈ flat accuracy past ~4, so few blocks suffice — cheapest is best).

## References (P2.5-specific)

- **Phase-1 exp3** ([`../../phase1/exp3/run_exp3.py`](../../phase1/exp3/run_exp3.py)) — the residual boosting
  chain; found chain > single block but **saturates ~2 blocks**. P2.5 re-tests under the substrate framing + adds
  the write mode.
- **BoostResNet** ([`../../ref/boostresnet.md`](../../ref/boostresnet.md)) — boosting wants *diverse* weak
  learners; full residual ε=1 (Phase-1 confirmed). The write mode's rationale.
- **P2.1/P2.2** — the decisive negatives that route here; the healthy shallow-SCFF cell carried as the per-block
  front.
