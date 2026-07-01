# Noise as a contrastive augmentation — building robustness *into* the SCFF objective

*Robust / consistency contrastive learning (Manifold-Aware Diffusion-Augmented Contrastive,
[2509.20048](https://arxiv.org/abs/2509.20048); the consistency-loss family); **"Ditch the Denoiser: Emergence of
Noise Robustness in SSL from a Data Curriculum"** (Lu et al., NeurIPS 2025, [2505.12191](https://arxiv.org/abs/2505.12191));
**"Why Contrastive Learning Benefits Robustness Against Label Noise"** ([2201.12498](https://arxiv.org/abs/2201.12498));
Jacobian regularization (Hoffman, Roberts & Yaida 2019, [1908.02729](https://arxiv.org/abs/1908.02729); Jakubovitz &
Giryes, ECCV 2018); **RINCE — Robust InfoNCE against noisy views** (Chuang et al., CVPR 2022,
[2201.04309](https://arxiv.org/abs/2201.04309)); the capacity-ceiling caveat — **Noisy Machines**
([2001.04974](https://arxiv.org/abs/2001.04974)); a second theory leg — **contrastive ≈ implicit Lipschitz / spectral
robustness** ([2405.17181](https://arxiv.org/abs/2405.17181)); the forward-only bridge — Bishop 1995 (input-noise =
Tikhonov, a classic).*

---

## The problem it answers

Phase 6's headline bet (design §3.1). A7 says the noise-sensitivity is **in the SCFF representation**, and LP-FT says the
20% readout can't manufacture robustness the base lacks — so the fix must be an **SCFF-objective** change, and (design §2)
it must be **forward-only.** The precise question: *what objective change makes the class **direction** invariant to
device noise, using only a local forward update?*

## The one idea that unstuck it

**Contrastive learning is invariance-injection.** Pulling two views of the same sample together makes the representation
invariant to *whatever differs between the views*. SCFF's InfoNCE already does this with the coordination window. So the
move is almost embarrassingly direct: **make the difference be the device noise.** One view clean, the other
tap/ADC/charge-corrupted → the objective trains "**same class direction under noise.**" The robust-contrastive literature
is exactly this — an unsupervised consistency loss forcing perturbed inputs to similar *normalized* embeddings.

Three things make it *fit us* specifically, not just "a robustness trick":

- **It's spine-clean by construction.** The consistency is on the *normalized* embedding — an **angle** constraint, not a
  magnitude. It hardens precisely the *direction* axis A7 attacks. (Contrast with a denoising-reconstruction objective,
  which would preserve *magnitude/density* — the density≠class trap that P3 already struck.)
- **The "why it's allowed forward-only" is a real theorem.** The *explicit* way to buy noise robustness is **Jacobian /
  Lipschitz regularization** — penalize the Frobenius norm of the input→output Jacobian → local smoothness → tolerance to
  input perturbation. But that needs a backward pass (a gradient w.r.t. the input). **Bishop 1995 proves that injecting
  small input noise during training adds, to first order, the *same* Tikhonov/Jacobian penalty — without ever computing
  the Jacobian.** So **noise-as-augmentation is the forward-only surrogate for Jacobian regularization.** That is the
  clean reason this fits a forward-only learner: we get the Lipschitz smoothness the explicit method buys, paid for with
  sampling instead of backprop.
- **It can be *pretrained in* and the crutch discarded.** "Ditch the Denoiser" (2505.12191) shows SSL develops genuine
  noise robustness from a clean→noisy *curriculum* + a teacher anchor, and the **denoiser is discardable at deployment**
  (+4.8% linear-probe on σ=255 ImageNet over DINOv2). Robustness lives in the *features*, not a runtime filter — exactly
  what an analog chip needs (no denoiser in the loop). *(Honest caveat: their curriculum uses denoised — i.e. cleaner —
  samples early on, so a clean-ish reference exists during pretraining. Whether **we** have any clean reference is Door
  B's question — see [`all-data-is-noise.md`](all-data-is-noise.md).)*

And a bonus that closes a loop: **a linear head on contrastive features is provably robust to label noise**
([2201.12498]). That *validates design §1's subtlety* — the unsupervised base is the label-noise-robust half; only the
readout sees labels, and we defend that separately (Phase 9 buffer hygiene).

## What it means for us

- **3.1 is confirmed as the primary fix, and it now has a name and a theory.** Adopt a **noise-corrupted positive view
  in the InfoNCE** as the headline Phase-6 objective change. It's the forward-only surrogate for Jacobian/Lipschitz
  smoothness; it hardens the direction axis; it composes with the window we already adopted.
- **Sweep the noise strength.** Too weak → no robustness; too strong → the positive pair collapses (BYOL-style) or the
  task gets so hard selectivity drops. There is a sweet spot, and finding it is a rung (P6.1).
- **Attack the right axis.** The corrupting view must be **structured & directional** (the residual after auto-zero), not
  only i.i.d. Gaussian — or we harden against the easy enemy and leave A7's real one standing.
- **Measure spine-cleanliness directly:** does robustness show up as *angle* invariance (direction) and survive
  feature-norm rescaling? If a "robustness" gain is really a magnitude artifact, the spine test catches it.
- **The critic pass added two levers and a second theory leg.** (1) **RINCE** ([2201.04309]) is a *loss-level* robust
  contrastive objective — a drop-in InfoNCE replacement provably robust to corrupted positive views; it hardens the
  *loss* where augmentation hardens the *inputs*, so P6.1 tests both (compose, or RINCE-alone). (2) **A capacity ceiling
  below collapse:** noise-injection *reduces representational capacity* (**Noisy Machines**, [2001.04974]), so clean
  selectivity can sag with `σ_aug` *before* any BYOL collapse — P6.1 pre-registers a capacity-knee probe, not just the
  collapse guard (the documented remedy if it bites is distillation, a Stage-2 note). (3) The Bishop bridge isn't the
  only theory: **contrastive objectives are implicitly Lipschitz / spectrally-bounded** ([2405.17181]), so the *base*
  SCFF objective already buys some of the smoothness we want — a second, contrastive-native leg that sharpens the
  YES-branch prior.
