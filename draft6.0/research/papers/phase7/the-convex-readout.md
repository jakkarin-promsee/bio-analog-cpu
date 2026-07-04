# The convex readout — why the 20% is the *easy* part

*Reservoir Computing (Jaeger's Echo-State Networks 2001; Maass's Liquid State Machines 2002), Extreme Learning Machines
(Huang 2006), and Online Convex Optimization (Hazan's monograph; McMahan's FTRL 2011). Modern survey: "Deep Randomized
Neural Networks" ([arXiv 2002.12287](https://arxiv.org/abs/2002.12287)).*

---

## The problem it answers

Coming off Stage 1, the instinct is to fear the GD side: "now we need backprop, the expensive thing we spent five
phases avoiding." That fear is misplaced, and this whole family of papers is *why*. The question it answers: **when you
freeze a big nonlinear feature machine and train only a readout on top of it, how hard is the learning?**

## The one idea that unstuck it

**Almost nothing.** Reservoir computing's founding move (echo-state networks, liquid state machines) is exactly ours:
take a large, fixed, nonlinear dynamical system — *don't train it* — and train **only a linear read-out** from its
state. Extreme Learning Machines do the feed-forward version: random hidden layer, frozen, train only the output
weights. The payoff is a theorem, not a heuristic:

> Fixing the bulk and training only the readout turns credit assignment into a **single convex problem** — for a linear
> head with a convex loss (squared error, logistic/cross-entropy), there is **one global optimum, no bad local minima**.

**Two honest boundaries on "convex," up front** (the critics pushed hard here, rightly):
- **Convex names the *regression*, not the deployed readout's substrate cost.** "No bad local minima" says nothing
  about the softmax/normalizer (a non-free digital block — arch-file §2.4), the per-depth-head Scap count, or the
  tap-reading cost. The *learning* is easy; the *deployed readout* is not free. That cost is Phase-7's meter to measure.
- **The universal-approximation half does *not* transfer to us.** ELM/reservoir's "good in the wide limit" rests on a
  **random** projection (Johnson–Lindenstrauss-style separability). Our bulk is **unsupervised-trained then frozen** —
  *better* features, but it **voids the random-projection theorem.** We inherit the **readout convexity** (that only
  needs the features fixed); we do **not** inherit the approximation-power guarantee, nor (see below) the reservoir's
  free mismatch-tolerance.

And because our chip learns **online** (per-sample, streaming), the right lens is **Online Convex Optimization (OCO)**:
the readout sees a stream of (feature, label) pairs and must keep a low *regret* versus the best fixed readout in
hindsight. The classic algorithms — Online Gradient Descent, **Follow-The-Regularized-Leader (FTRL)**,
Passive-Aggressive, online logistic regression — give **regret bounds**. But read the rate honestly, in two ways the
first draft blurred:
- **Reaching the optimum vs the regret rate are different claims.** Plain OGD on the logistic/CE loss gets only
  $R_T \le \mathcal{O}(\sqrt{T})$; the fast $\mathcal{O}(\log T)$ rate needs **exp-concavity** via **Online Newton Step**
  — which carries a **quadratic register + a per-step linear solve**, i.e. *exactly* the heavy optimizer the "no
  exotic optimizer" line says we avoid. (Parameter-free logarithmic-regret online logistic regression,
  [1902.09803](https://arxiv.org/abs/1902.09803), is the honest version of this story.) So "any simple optimizer
  *converges*" is true; "the optimizer doesn't matter at all" is not.
- **The comparator *moves*.** Across the stream SCFF drifts, so the readout chases a **drifting** optimum — this is OCO
  with a *non-stationary comparator*, whose regret scales with the **path length / drift rate**, not $\sqrt{T}$. The
  "easy" framing holds only if the drift is small — which is exactly what the sleep loop and the late-layer slowdown
  ([`slow-coordination.md`](../phase9/slow-coordination.md)) exist to keep small. **Tracking the drift, not solving the
  regression, is the real cost.**

The mechanics that matter for hardware:

- **The optimizer barely matters.** On a convex problem there is no saddle-point / sharp-minimum drama for momentum or
  Adam to rescue you from. SGD + a little momentum is enough; Adam/AdamW's per-parameter rate is a convenience, not a
  necessity. (Empirically: on **small** heads like ours, AdamW tends to edge out the memory-light **Lion** optimizer —
  Lion ([2302.06675](https://arxiv.org/abs/2302.06675)) trades Adam's second-moment register for a sign update and
  shines on *large* models, not small ones.) This frees the **Scap budget**: the per-weight registers a momentum + a
  second moment would need (which the substrate happens to already have — the momentum register and the BCM
  $\langle a^2\rangle$ threshold) are a *nicety*, not a load-bearing requirement.
- **It can be even cheaper than SGD — and there's a published, substrate-native recipe.** Because the problem is convex,
  closed-form streaming estimators work, and **RanPAC** ([2307.02251](https://arxiv.org/abs/2307.02251)) is the modern
  near-twin of our setup: frozen features → a frozen nonlinear projection → a **ridge-regularized class-prototype** head
  updated by a **running mean + a running Gram (second-moment) matrix** — rehearsal-free, SOTA on class-incremental
  benchmarks, **no gradient at all.** A running mean is a capacitor EMA and a Gram matrix is a running second moment, so
  this is the most substrate-native readout on the table — *provided* the `Σ⁻¹`/ridge solve (a non-free digital block) is
  affordable. RanPAC's own result that the **ridge term beats plain NCM** is the warning against "just use the mean":
  the second moment earns its keep. (Details + the spine caveat: [`direction-readouts.md`](direction-readouts.md).)

## What it means for us

We already had this in the dossier and didn't connect it: **reservoir computing is north-star file 8 ("the atom") —
"don't train the recurrent core, only the readout."** The draft-6 architecture is **reservoir-*like*** in the readout
sense — a frozen bulk + a trained head — **but not a reservoir proper:** a true reservoir/ELM is a *random, untrained*
core, and ours is **unsupervised-trained then frozen.** That difference cuts two ways. It is *better* (the bulk composes
class-relevant depth instead of a random projection), but it **does not inherit the reservoir's free
device-mismatch-tolerance** (file 8's "tolerates mismatch by design" assumes the random core) — which is *exactly why A7
is an open risk and not auto-solved* ([`noise-and-flatness.md`](../phase6/noise-and-flatness.md)). Keep the reservoir framing for
the *readout-convexity* intuition only; don't let it wave away the noise problem. With that boundary drawn:

- **The 20% is the tractable half, not the scary half — *in the learning*, with the cost caveat held.** Frozen-to-GD
  features make the *regression* a convex online problem. We do **not** need the heavy optimizer zoo (second-order,
  K-FAC, Shampoo, LARS/LAMB — those are for the hard non-convex bulk, which we don't train with GD). The survey's
  optimizer detail files (`survey/adam.detail.md`, `momentum.detail.md`, `second-order-methods.detail.md`) are
  *reference*, not a menu to shop — "the simplest thing converges here." But "tractable learning" ≠ "free readout":
  the deployed-readout substrate cost (the two boundaries above) is what Phase 7's meter still has to answer.
- **It reframes "pay for direction once."** The expensive thing about backprop was the **cross-layer credit chain**.
  A readout has **no chain** — it is one layer (or a tiny stack) reading fixed features. So the direction we pay for is
  cheap *by construction*, not by cleverness. The 80/20 isn't "80% cheap magic + 20% expensive necessity"; it's "80%
  unsupervised structure + 20% **convex** naming" — with the honest asterisk that the 80/20 is, ultimately, a **cost**
  claim, and the cost meter is deferred to Phase 7 (don't quote the ratio as settled before then).
- **The remaining boundary: a deeper head.** Convexity is exact only for a **linear/logistic** readout; a 2–3-layer MLP
  head (the old "Output GD" organ) is non-convex again — mild over good features, but real — and the multimodality
  fallback (a *mixture* of per-class prototypes, [`direction-readouts.md`](direction-readouts.md)) is non-convex too.
  So the clean convex story holds for the *simplest* readouts and degrades gracefully toward the realistic ones. **Convex
  *per step* for a linear head, tracking a drifting comparator *across* steps, non-free to *deploy* — the honest version
  of "the cleanest part of the GD job."
