# DeeperForward — keep layer-norm, fix the *goodness*

*ICLR 2025 ([proceedings](https://proceedings.iclr.cc/paper_files/paper/2025/file/7dd309df03d37643b96f5048b44da798-Paper-Conference.pdf), [code](https://github.com/tobysunsun/deeperforward)). Added 2026-06-21, at the top of Phase 2. The story; the deep notes live in [`../../../src/phase2/exp0/experiment-0.md`](../../../src/phase2/exp0/experiment-0.md).*

---

## The problem it was stuck on

Forward-Forward and its children (SCFF included) are **shallow**. Pile up layers and accuracy *falls* — the
opposite of what depth is supposed to buy you. That is our Phase-1 finding in one sentence ("SCFF features
degrade with depth"), and it is the entire reason Phase 2 exists. The field had a leading answer already — **The
Trifecta** (2023): *layer-norm is the depth-killer; rip it out, put batch-norm in.* DeeperForward looked at that
answer and said: not so fast.

## The one idea that unstuck it

The Trifecta blames the **normalization**. DeeperForward blames the **goodness**.

Their reading: FF's goodness is **squared** — `G = Σ hᵢ²`, the energy. Two things go wrong with that as you go
deep:

- **Squared energy is outlier-dominated.** A few loud units carry the whole goodness, the rest get pushed
  toward zero — and a **dead unit stops learning entirely**, because the weight update `ΔW ∝ hⱼ · ∂L/∂G`
  carries a factor of its own activation `hⱼ`. Zero activation, zero gradient, dead forever. Layer by layer the
  living-unit budget shrinks and features are lost. *(This is our Phase-1 "dead-unit fraction" climbing with
  depth, seen from the objective side.)*
- The batch-norm "fix" has its own leak: batch statistics **carry goodness forward into the next layer**, so
  deep layers re-use the previous layer's separation instead of building new features — it *looks* like it
  scales, then **overfits** as you stack.

Their fix is the elegant part: **keep layer-norm, but make goodness the *mean*, not the energy** — `G = mean(h)`
(first moment, linear), instead of `Σh²` (second moment, squared). Why that one swap fixes both failures:

- **Linear goodness doesn't deactivate neurons.** Its update `ΔW ∝ xᵢ · ∂L/∂G` has **no `hⱼ` factor** — a quiet
  unit still gets a gradient and can come back to life. The dead-unit cascade stops.
- **Layer-norm already removes the mean.** So if goodness *is* the mean, then the representation passed
  forward — the mean-zero, unit-std normalized vector — is **automatically goodness-free**: decoupled, for free,
  with **no batch statistics required.** That is what lets each layer build genuinely new features without the
  batch-norm leak.

With that, they train FF on a **17-layer** CNN — CIFAR-10 4-layer **79.5% → 17-layer 86.2%** (rising with
depth), where the batch-norm route (CwComp) *falls* 78.1% → 75.3%.

## How they measure it — same picture we draw

Their headline depth read (Fig 5d) is **per-layer accuracy vs layer index** — a rising curve is the win — and
they overlay **residual-shortcut on vs off** (Fig 5c). That is *exactly* our F3⁺ and exactly Phase-1 exp3's
pivot figure. The field's way of asking "does depth help in FF" and ours are the same plot; good. They also add
a **Signal-Integrating-and-Pruning (SIP)** module that picks the best **contiguous layer range** to read out
(and finds easy tasks keep fewer layers — depth adapts to difficulty) — which is real guidance for our P2.4 "GD
interface / which layers to tap" question.

## What it means for us

It puts a **second, more recent, contradicting hypothesis on P2.1's table — and the more substrate-friendly one.**

- The Trifecta says the cure is **batch-norm**. But batch-norm is GPU-native; our chip is **online,
  single-sample**, so P2.1/P2.6 have to sweat whether the *online* version keeps the gain and whether its stats
  **rot under task shift** (the continual veto). **Layer-norm is per-sample — it needs no batch at all.**
- DeeperForward shows layer-norm **can** scale (to 17 layers) *if* you fix the goodness instead. So the cheapest
  depth-fix for *us* might not be "import batch-norm and fight to make it online" — it might be **"keep the
  per-sample norm we already have, switch goodness squared → linear."** Intrinsically single-sample,
  intrinsically continual-safe.

That is why Phase 2's P2.1 was widened from a pure normalization sweep to a **`{squared, linear} goodness ×
{layer-norm, batch-norm, online-BN}` grid** — the two axes are coupled (linear goodness only decouples *because*
layer-norm is mean-zero), and the corner the Trifecta never tests, **layer-norm + linear goodness**, is the one
our substrate would most like to win. P2.0 logs the dead-unit and rank-collapse diagnostics precisely so the
lost/entangled verdict tells us *which* corner to trust first.

*Caveat to carry: DeeperForward's 17-layer result is a **CNN** with a channel-wise-competitive conv and a
pruning head — architecture does real work there. We are flat-MLP. So we adopt the **goodness diagnosis** (the
portable, substrate-relevant idea), not the conv machinery — and we test whether mean-goodness alone earns depth
in our setting, which is an open question, not a settled import.*
