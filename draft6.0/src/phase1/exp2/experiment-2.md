# Experiment 2 — inside the block: converting SCFF features to labels

> Three internal knobs, one variable per cell, all vs the pure-GD ceiling, judged on held-out.
> Driven by Exp 1's finding: **SCFF features degrade with depth.** Spec: [`../design.md`](../design.md)
> (Exp 2); reporting: [`../result-format.md`](../result-format.md); the *why*: N2 in
> [`../../../idea/main.ideas.v1.md`](../../../idea/main.ideas.v1.md).

## Question

- **2c — the plasticity gradient (committed, N2).** Frozen / slow / fast read-layers in *online
  co-training* (SCFF still learning while GD reads it → taps drift). What slowdown keeps GD tracking
  without choking SCFF? Sets N2's only open knob (front:back plasticity ratio).
- **2a — the SCFF:GD ratio.** At ~fixed weights, slide the split 0% SCFF (= pure GD) → 100% SCFF. **The
  direct test of the depth-degradation finding:** how much cheap SCFF before precision suffers?
- **2b — Interface-GD depth.** Deferred — 2a already sweeps the GD-depth axis at its high-GD end (the GD
  back is `(L-k)` layers); a dedicated 2b adds little until the degradation question is settled.

## Setup

Block = stack of `L=4` width-`H` layers + readout. **2a:** first `k` layers SCFF-trained (local,
unsupervised, frozen — two-phase), the rest GD-trained (backprop); GD reads the **all-layer** tap (Exp 1
fix); sweep `k=0..4`. **2c:** warm up SCFF, then co-train (SCFF front fast, read-layers L3,L4 at rate ρ ∈
{0,0.1,0.3,1.0}; GD readout tracks). digits (dev), MNIST (headline). Seeds `[42,137,271,(314,1729)]`,
median+IQR. Code: [`run_exp2a.py`](run_exp2a.py), [`run_exp2c.py`](run_exp2c.py); figures
[`F9_trade.png`](figs_exp2a_digits/F9_trade.png), [`exp2c_plasticity.png`](figs_exp2c_digits/exp2c_plasticity.png).

## Result / figures

**2c — plasticity gradient (digits, n=3):**

| ρ (read-layer rate) | held-out | gap | end-drift | per-layer separability |
| --- | --- | --- | --- | --- |
| 0.0 frozen | 0.918 | +0.040 | 0.177 | [0.90, 0.86, 0.80, 0.75] |
| 0.1 slow | 0.920 | +0.040 | 0.182 | [0.90, 0.86, 0.81, 0.76] |
| **0.3 slow** | **0.923** | +0.040 | 0.205 | [0.90, 0.86, 0.81, 0.77] |
| 1.0 fast | 0.912 | +0.052 | 0.262 | [0.90, 0.86, 0.80, 0.76] |

Slow read-layers marginally best + lower drift; **drift is mild in finite multi-epoch data** (its real bite
is the continual regime, Exp 4). **Plasticity does NOT fix depth-degradation** — the per-layer profile
`[0.90→0.75]` is identical at every ρ. ([`exp2c_plasticity.png`](figs_exp2c_digits/exp2c_plasticity.png).)

**2a — SCFF:GD ratio (digits, n=5; F9 trade):**

| SCFF fraction k/L | held-out | gap | GD backward FLOPs |
| --- | --- | --- | --- |
| 0.00 (pure GD) | **0.965 [0.960,0.967]** | +0.035 | 75,008 |
| 0.25 | 0.952 [0.938,0.958] | +0.048 | 58,624 |
| 0.50 | 0.947 [0.937,0.952] | +0.052 | 58,624 |
| 0.75 | 0.935 [0.932,0.948] | +0.053 | 58,624 |
| 1.00 (max SCFF) | 0.920 [0.918,0.923] | +0.042 | 34,048 |

**Accuracy declines monotonically with SCFF fraction; the big backward saving (→45%) only arrives at full
SCFF, where accuracy is worst. No free-lunch sweet spot.** ([`F9_trade.png`](figs_exp2a_digits/F9_trade.png).)

**2a — MNIST (n=3) — confirms, with a twist:**

| SCFF fraction | held-out | GD backward FLOPs |
| --- | --- | --- |
| 0.00 (pure GD) | **0.943 [0.940,0.944]** | 615,680 |
| 0.25 | 0.906 [0.901,0.907] | **214,272 (35%)** |
| 0.50 | 0.890 | 214,272 |
| 0.75 | 0.867 | 214,272 |
| 1.00 | 0.837 [0.835,0.838] | 66,816 |

Same monotonic decline, steeper. **The twist:** on high-D input the **first layer (784→128) dominates the
backward cost**, so moving *just it* to SCFF (25%) saves **65%** of the backward pass for a 3.7-pt accuracy
loss. The cost saving concentrates in the *input* layer, not the bulk — so the practical sweet spot is **low
SCFF fraction (the expensive front), not 80%** (on a single block). Whether high-SCFF depth pays off is
exactly the Exp-3 chain question.

## Read (six-slot per `result-format.md` Layer C)

1. **Claim.** Inside one block, **more cheap SCFF buys backward-cost savings only at a roughly proportional
   accuracy cost** (no near-ceiling-cheap sweet spot), because SCFF features degrade with depth; the
   plasticity gradient is a *drift* insurance, not a degradation fix.
2. **Numbers.** 2a: held-out 0.965 (0% SCFF) → 0.920 (100%), backward 75k→34k FLOPs. 2c: ρ=0.3 best
   (0.923) vs fast 0.912; degradation `[0.90→0.75]` invariant to ρ.
3. **Figures.** F9 (the trade curve, 2a), exp2c_plasticity (2c).
4. **Mechanism.** Each SCFF layer re-optimizes *goodness* (density) and sheds class-relevant directions, so
   stacking SCFF loses accuracy that more GD layers recover. Plasticity only changes *how fast the taps
   move*, not *what the SCFF objective preserves* — so it can't touch degradation.
5. **Threats.** digits/MNIST may be too shallow-structured for deep SCFF to ever help; the real depth payoff
   the architecture claims is the **boosting CHAIN (Exp 3)** — shallow SCFF per block + a GD corrector,
   depth from *stacking corrected blocks* on a residual stream — NOT a monolithic deep SCFF stack. 2a tests
   the latter (and it loses); Exp 3 tests the former. GD-coshaping / DF-O (Ch6 optional) is the other
   untested degradation fix.
6. **Decision.** Below.

## Decision

- **2c → N2's knob locked: slow read-layers (ρ ≈ 0.1–0.3).** Marginal-but-free here; the real value is
  continual drift (Exp 4). Frozen is the cheap fallback; "fast" is worst (drift + bigger gap). EMA-view not
  needed yet.
- **2a → keep SCFF SHALLOW inside a block.** Depth degrades it; more GD layers recover accuracy. There is no
  "80% deep SCFF nearly free" regime on these tasks — the 80/20 framing must be re-read as *per-block
  shallow SCFF + GD correction*, with depth coming from the chain.
- **The pivot this sets up: Exp 3 (residual-boosting chain) is now THE critical experiment** — it is the
  architecture's actual mechanism for getting depth-benefit (each block a weak corrector; GD re-corrects
  the residual before the next block, side-stepping monolithic-SCFF degradation). If Exp 3's chain doesn't
  buy depth, the deep-cheap-brain thesis needs rethinking; if it does, the degradation finding is simply
  "don't go deep *within* SCFF — go deep *across* corrected blocks."
- **Default for Exp 3:** shallow SCFF per block (1–2 layers), slow read-layers, all-layer tap, H=64.
