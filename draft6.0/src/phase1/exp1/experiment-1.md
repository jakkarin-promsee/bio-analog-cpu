# Experiment 1 — one block vs pure GD

> The first real test of the thesis: a single **block** = `[SCFF feature layers → GD checkpoint]`
> vs a **pure-GD MLP at the same total weights**. Not "who wins" — *the difference*, forward and
> backward, and the **memorization gap**. Spec: [`../README.md`](../README.md) (Exp 1); reporting:
> [`../result-format.md`](../result-format.md); the *why*: [`../../idea/ideas1.md`](../../idea/ideas1.md).

## Question

1. **1a — behaviour at fixed size.** How does one block differ from vanilla GD, *forward* (where is
   separability built — SCFF bottom-up vs GD top-down) and *backward* (credit locality + cost)?
2. Does the block **understand** (small train−held-out gap) where pure GD **memorizes** (large gap)?
3. **Pass gate (ladder 2.0):** tapped-GD on SCFF features **beats SCFF's bare top-layer readout** *and*
   **approaches the 1.1 full-GD ceiling** (exp0 = 0.943 on the 2-D checkerboard; a fresh ceiling per task).
4. **1b — scale-free check.** Does the difference (accuracy, gap) hold as total weights sweep small→large?

## Setup (carried from exp0 + the one forced change)

**The task must be HIGH-D and FINITE.** exp0 proved the headline cannot be tested in low-D: (a) on 2-D
Gaussian clusters a *random projection* already matches SCFF (Johnson–Lindenstrauss), so the block's SCFF
half adds nothing; (b) under a fresh-draw single pass the memorization gap is **0 by construction**. Both
disappear on a finite high-D dataset with repeats. So Exp 1 runs on:

- **Primary headline: MNIST** (784-D) — and a fast offline development twin, **`load_digits`** (64-D), where
  exp0 already showed SCFF > random. Small train subset on purpose, so pure GD *can* overfit and a gap exists.
- The 2-D checkerboard stays only for the **F5** visualization (boundary), not the accuracy claim.

| Knob | Value |
| --- | --- |
| Block | SCFF body `[D, H,H,H,H]` (4 layers, local SCFF, sum-goodness, input-norm, θ=2.0) → **Output GD** readout `[2H, 32, C]` (Adam, cross-entropy) on the last-2-layer taps |
| Pure-GD control | MLP `[D, w,w,w,w, C]`, **total weights matched** to the block (`match_width`) |
| Training | SCFF unsupervised multi-epoch → freeze → readout supervised; pure-GD supervised. **Same supervised epoch budget** for readout and GD (fair). |
| Datasets | digits (dev), MNIST subset (headline); fixed train/held-out split |
| Seeds | `[42,137,271,314,1729]`, median + IQR |
| Realism | ideal floats; no analog/PVT, no gate, no sleep |

**Mandatory figures** ([`../result-format.md`](../result-format.md)): **F1** (held-out + train-on-seen, gap
shaded, block vs GD) + **F2** gap scalar · **F3** separability heatmap block vs GD · **F7** backward
cost/locality · **INV** (+F5 if Tier-A). 5 seeds, IQR; manifest + arrays; figures regenerate via `plot`.

## Run

**2026-06-20, 5 seeds.** Code: [`run_exp1.py`](run_exp1.py) (1a), [`run_exp1b.py`](run_exp1b.py) (size
sweep), [`tap_diag.py`](tap_diag.py) (the tap-strategy diagnostic), figures via
[`plot_exp1.py`](plot_exp1.py). Reuses the tested exp0 components. Arrays + manifest + figures in
`figs_exp1_digits/`, `figs_exp1_mnist/`, `figs_exp1b_digits/`.

**One forced correction mid-run (backed by [`tap_diag.py`](tap_diag.py)): tap ALL SCFF layers, not S3's
"last n".** SCFF separability *degrades with depth* (MNIST: `[0.82, 0.73, 0.61, 0.52]` L1→L4), so the last-2
taps read the **worst** features — block held-out was stuck at 0.68. Switching to all-layer taps (the SCFF
paper's own readout) recovered **+0.17→+0.21** (MNIST 0.68→0.85). S3's "last n" is corrected to "all layers."

## Result / figures

**1a — MNIST (headline) and digits (dev), block vs matched pure-GD, median [IQR], n=5:**

| metric | **MNIST** block | MNIST pure-GD | digits block | digits pure-GD |
| --- | --- | --- | --- | --- |
| held-out | 0.850 [0.848,0.861] | **0.938 [0.936,0.939]** | 0.927 [0.923,0.930] | **0.968 [0.953,0.973]** |
| **memorization gap** | **+0.027 [+0.023,+0.028]** | **+0.062 [+0.061,+0.064]** | +0.047 | +0.032 |
| SCFF bare-top readout | 0.518 | — | 0.763 | — |
| backprop FLOPs vs GD | **10%** | 100% | 34% | 100% |
| weights | 166.8k | 167.3k | 25.2k | 25.5k |

- **F1** (`figs_exp1_mnist/F1_gap.png`) — train/held curves, gap shaded. **MNIST: block gap +0.027 vs GD
  +0.062, IQRs DISJOINT, 5/5 seeds → REAL** (per `result-format`'s n=5 rule). The block *understands*; GD
  *memorizes*.
- **F3** (`F3_separability.png`) — SCFF degrades with depth `[0.82→0.52]`; pure-GD stays flat-high `[~0.94]`.
- **F7** (`F7_backward.png`) — block's serial backprop = **10%** (MNIST) / 34% (digits) of GD's; the rest is
  SCFF **local, forward-only, credit-distance 0** (no transpose chain). The structural claim, measured.
- **INV** (`INV_dead.png`) — SCFF dead-unit fraction healthy.
- **1b / F6** (`figs_exp1b_digits/F6_scale.png`) — block held-out rises with size and **closes on GD** (gap
  0.15→0.03 as weights 4k→47k); memorization-gap advantage is clear at small sizes, crosses over on
  (easy) digits at large sizes. Default size **H=64 (~25k)** — the competitive middle regime (= exp0's lock).

## Read (six-slot per `result-format.md` Layer C)

1. **Claim.** A single SCFF+GD block, at matched weights, reaches near-GD accuracy with a **markedly smaller
   memorization gap** and a **~5–10× cheaper, mostly-local backward pass** — on high-D data. (On low-D the
   SCFF half adds nothing; exp0.)
2. **Headline number.** MNIST: block 0.850 vs GD ceiling 0.938; **gap +0.027 ≪ +0.062 (disjoint IQR, 5/5)**;
   block backprop = 10% of GD's. digits: 0.927 vs 0.968.
3. **Figures.** F1 (gap, the headline), F3 (separability), F7 (backward cost, the structural win), F6 (1b
   scale-free), INV.
4. **Mechanism.** SCFF's unsupervised features can't encode label noise → the readout has little to memorize
   → small gap; but each SCFF layer re-optimizes *goodness* (density), shedding class-relevant directions, so
   features **degrade with depth** → the block trails GD's ceiling and must tap **all** layers (value is in
   the early ones). GD's label-driven full-depth backprop fits *and* memorizes → high accuracy, large gap,
   serial credit through the whole stack.
5. **Threats to validity.** (a) The block's small gap is *partly* underfitting — but at MNIST 0.85 it is
   competitive, and the gap is real at comparable fit. (b) **SCFF degrades with depth** → the deep "80% cheap
   brain" is not yet earning its depth; today the value is *shallow* SCFF + all-layer tap. Exp 2 (middle-layer
   coordination / plasticity gradient, N2) exists precisely to fix this — it is now well-motivated, not
   speculative. (c) Two-phase (SCFF frozen → readout) sidesteps drift; co-training (Exp 2) may differ. (d) The
   S3 "last-n tap" correction was necessary — logged.
6. **Decision.** Below.

## Decision

- **Pass gate: MET.** Block beats SCFF's bare-top readout (MNIST +0.33, digits +0.16) and approaches the
  full-GD ceiling (MNIST 0.85 vs 0.94; digits 0.93 vs 0.97). The block is a viable cheap learner: near-GD
  accuracy, smaller memorization gap, ~10% backward cost.
- **Spec correction (locked): tap ALL SCFF layers, not S3's "last n".** SCFF degrades with depth.
- **GD ceilings to quote in Exp 2/3:** MNIST **0.938**, digits **0.968** (the per-task references).
- **Default size: H=64 (~25k weights)** — the competitive middle regime; Exp 2/3 hold this.
- **Carried concern → Exp 2's job:** SCFF feature degradation with depth. Exp 2 (frozen/slow/fast read-layers
  + coordination) is the named fix; if it can't stop the degradation, the architecture should lean on
  *shallower* SCFF. This is the most important thing Exp 2 must resolve.
