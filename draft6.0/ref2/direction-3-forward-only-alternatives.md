# Direction 3 — keep SCFF up front, use a *different* forward-only learner for the deep part

> Your goal: use SCFF only where it has an edge (cheap, unsupervised, continual-robust early layers), and pick a
> different forward-only / single-pass algorithm for the rest. **Verdict up front: this is the strongest
> *practical* direction, and it forks cleanly into two — a *supervised-local* deep learner (Mono-Forward, the
> safe proven win) and an *unsupervised-local* deep learner (GIM/CLAPP, the on-identity win). The fork is the
> real decision, and it is the same fork as the rest of Phase 3.**

---

## The landscape, sorted by what they cost you

Every method here is forward-only and layer-local (no backprop between layers). They differ on the **one axis
that matters for this project: do they use labels at every layer?** — because that is what decides whether the
"unsupervised 80% / continual win" survives.

### A. Unsupervised / self-supervised (keeps the project's identity)

- **Greedy InfoMax (GIM)** — [1905.11786](https://arxiv.org/abs/1905.11786). *The headline.* InfoNCE per module,
  predicts future/neighbouring representations, info-preserving, **composes with depth**, matches end-to-end CPC.
  Fully covered in [the-objective-reframe](the-objective-reframe.md). This is "SCFF but with a depth-composing
  objective," not a replacement bolted on the back — so it can be the *whole bulk*, not just the deep part.
- **CLAPP** — [2010.08262](https://arxiv.org/abs/2010.08262). GIM made single-sample + Hebbian-plausible (a
  predictive contrastive plasticity rule). The 2026 benchmark's **CLAPP++ matches backprop-SSL on CIFAR-10**
  ([2601.21683](https://arxiv.org/abs/2601.21683)). The most substrate-shaped member of this family.
- **SoftHebb** — [2107.05747](https://arxiv.org/abs/2107.05747) + *Hebbian Deep Learning Without Feedback*
  (Journé et al, ICLR 2023). Unsupervised soft-winner-take-all Hebbian; **no targets, no errors at all**;
  implicitly minimizes cross-entropy; scales to deeper nets; robust to noise / one-pass / adversarial. The
  *purest* local rule (even cheaper than SCFF — no negative needed), but its accuracy ceiling is lower and it is
  WTA-structured (a different cell than ours). Good substrate cousin; weak headline accuracy.
- **LPL (Latent Predictive Learning)** — the non-contrastive predictive cousin tested beside SCFF in
  [2601.21683](https://arxiv.org/abs/2601.21683). Worth knowing as the "no-negatives" predictive option (BYOL-ish).

### B. Supervised-local (label at every layer — depth-capable, but spends the unsupervised property)

- **Mono-Forward** — [2501.09238](https://arxiv.org/abs/2501.09238). *The safe, proven win, and the most
  relevant of all the supervised options because it is **flat-MLP-native** (every other deep-FF success —
  DeeperForward, ASGE, CaFo, BiCovG — is a CNN).* Each layer gets a tiny projection `M_i` (classes × neurons)
  → goodness-as-logits → **local** cross-entropy; no signal crosses layers. **Solves depth** (convergence rate
  flat with depth where backprop degrades), **beats backprop** on MLP CIFAR-10 (82.4 vs 77.8) and CIFAR-100
  (54.8 vs 42.1), ~12× lower memory slope, parallel per-layer. Purely local + forward-only = substrate-faithful.
- **Local Error Signals (predsim)** — [1901.06656](https://arxiv.org/abs/1901.06656). Per-layer **pred** (local
  CE) **+ sim** (similarity-matching) loss; first to show layer-wise training "approaches SOTA"; weights updated
  during the forward pass; MLP **and** CNN. The `sim` half is the non-collapsing, structure-preserving target
  Direction 2 wanted.
- **CaFo / DeeperForward / ASGE / BiCovG** — the per-layer-supervised CNN family
  ([2303.09728](https://arxiv.org/abs/2303.09728) · DeeperForward ICLR'25 · [2509.12394](https://arxiv.org/abs/2509.12394)
  · [2605.04346](https://arxiv.org/abs/2605.04346)). All earn depth with per-layer/per-block CE + forward logit
  fusion. Confirm the pattern; not directly portable (conv machinery), but the *fusion-head* is exactly our
  P2.5 `read`.

### C. Forward credit-assignment (the "cheap direction" wildcard — see also the README's 5th option)

- **Forward gradient / activity perturbation** — Baydin et al *Gradients without Backpropagation*
  ([2202.08587](https://arxiv.org/abs/2202.08587)); Ren et al / Hinton *Scaling Forward Gradient With Local
  Losses* ([2210.03310](https://arxiv.org/abs/2210.03310)). An **unbiased gradient estimate from a single
  forward pass** (directional derivative along a random perturbation). This is *literally the missing "direction"*
  P2.2 named — obtained forward-only. High variance (grows with dimension); Ren's activity-perturbation + local
  losses tame it. A genuinely different fifth option; **bench it, don't lead with it** (variance on 3072-D flat
  input is the risk).
- **PEPITA** — Dellaferrera & Kreiman, ICML 2022 + analysis [2302.05440](https://arxiv.org/abs/2302.05440). Two
  forward passes; the second modulates the input by the first pass's error via a fixed random matrix. Forward
  -only credit assignment, supervised. A neat idea but trails FF-family accuracy; lower priority.

## The fork that actually decides Direction 3

It is **not** "which algorithm is most accurate." It is **do you keep the bulk unsupervised?**

- **If yes (recommended default):** the deep learner must be **GIM/CLAPP-family** (A). Then Direction 3 collapses
  into [the-objective-reframe](the-objective-reframe.md): you're not "replacing SCFF for the deep part," you're
  *upgrading SCFF's objective* so the whole bulk composes with depth, unsupervised. Continual win preserved, no
  batch stats, substrate-native.
- **If you'll spend labels in the bulk:** **Mono-Forward** (B) is the proven, flat-MLP-native, depth-capable,
  beats-backprop choice — and it could even **replace the current GD-block "20%"** with something cheaper and
  per-layer-local, rather than replacing SCFF. But it abandons the unsupervised 80% that Phase 1 proved is the
  *actual win* (the forgetting-robust continual regime). Spending that is a strategic cost, not just an
  accuracy trade.

## Substrate fit (the quick table)

| method | labels? | depth-composes? | substrate fit | continual-safe? |
| --- | --- | --- | --- | --- |
| **GIM / CLAPP** | no | ✅ (proven) | forward-only, per-sample, no batch stats | ✅ (no labels/batch stats) |
| **SoftHebb** | no | ~ (modest) | purest local rule, WTA | ✅ |
| **Mono-Forward** | **yes (every layer)** | ✅ (proven, MLP) | forward-only, tiny per-layer head | ⚠ supervised bulk → re-test forgetting |
| **predsim** | yes | ✅ | forward-only, per-layer head | ⚠ supervised |
| **forward gradient** | (either) | untested here | forward-only, high variance | depends |

## Verdict / how to prioritise

**Highest practical value of the three directions — but route it through the fork.** Default to the
**unsupervised** branch (GIM/CLAPP objective) because it keeps the project's identity *and* has the depth
existence proof; hold **Mono-Forward** as the **de-risked fallback** (if the predictive objective won't compose
on flat-MLP vectors, Mono-Forward is the proven way to get a depth-capable cheap local stack, and it's a
strictly better "GD 20%" than full backprop blocks). Treat **forward gradient** and **PEPITA** as bench options,
not first bets.

## Papers

GIM [1905.11786](https://arxiv.org/abs/1905.11786) · CLAPP [2010.08262](https://arxiv.org/abs/2010.08262) ·
LPL/SCFF benchmark [2601.21683](https://arxiv.org/abs/2601.21683) · SoftHebb
[2107.05747](https://arxiv.org/abs/2107.05747) · Mono-Forward
[2501.09238](https://arxiv.org/abs/2501.09238) · Local Error Signals
[1901.06656](https://arxiv.org/abs/1901.06656) · Forward gradient
[2202.08587](https://arxiv.org/abs/2202.08587) / [2210.03310](https://arxiv.org/abs/2210.03310) · PEPITA
[2302.05440](https://arxiv.org/abs/2302.05440).
