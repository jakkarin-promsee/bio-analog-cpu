# Direction 1 — cross-layer goodness (your "A1-from-layer-2" idea)

> Your proposal: compute a layer-1 neuron's goodness from **layer 2's combined output**, not its own —
> `goodness(A1) = f( A1 · (B1+B2+B3+B4) + bias )` — so A1 learns to help the *next* layer's goodness, not its
> own. **This is a real, named idea with published results.** It is the cheapest thing to test, and it stays
> unsupervised. Verdict up front: **worth running as the cheap first probe — but the published gain is modest;
> the powerful version of "cross-layer coordination" is the predictive objective in
> [the-objective-reframe](the-objective-reframe.md), not goodness-coupling alone.**

---

## Your idea already has a name: Overlapping Local Updates (OLU)

From **The Trifecta** (Lorberbom et al, [arXiv 2311.18130](https://arxiv.org/abs/2311.18130)) — the paper
already in our `ref/`:

> OLU trains layers in **overlapping pairs**. Each layer is optimized with two alternating objectives: when it
> is the *last* layer of a pair it maximizes its **own** goodness; when it is the *first* layer of a pair it is
> updated **to help the next layer maximize *its* goodness.** The former promotes local understanding; the
> latter "prompts the layer to increase the **usefulness of its representations for the next layer.**"

That second objective — *update A so that layer-B's goodness goes up* — is **exactly your `A1·(ΣB)` proposal.**
You re-derived OLU from the goodness side. Mechanically, "increase `A1·(B1+B2+B3+B4)`" pushes A1 along
`∂(ΣB)/∂A1 = Σ_j w_j1` (over active B units) — i.e. A1 moves in the direction the *layer-2 weights* say is
useful. That is a genuine, forward-computed, cross-layer signal: it carries one layer of "what the next layer
wants" without any backward pass. (It's a one-step forward lookahead — the same shape as **DF-O**, below.)

## The same idea from three other angles

- **DF-O (Distance-Forward overlapping)** — already in our `ref/distance-forward.md` and named in decision **N2**
  as our "coordination" lever. DF-O groups two adjacent layers and lets the gradient flow *across the pair*
  before detaching — a "tiny, controlled window of coordination." OLU and DF-O are the same family: a 2-layer
  coordination window. **N2 committed to this and Phase 2 never tested it** (P2.3 was skipped). Direction 1 is
  the rung that finally runs it.
- **Layer Collaboration in FF** (Lorberbom et al, AAAI 2024, [arXiv 2305.12393](https://arxiv.org/abs/2305.12393))
  — the *broadcast* version: each layer's loss adds the **detached total goodness of all other layers** (a
  single scalar Γ). Stays local (Γ is detached → no gradient), one broadcast wire ≈ a neuromodulator. Weaker
  than OLU (a scalar, not a directional coupling) but cheaper.
- **Direct feedback** (from [2601.21683](https://arxiv.org/abs/2601.21683)) — the *top-down* version: use the
  **top layer's** activations as a reference for *all* lower layers. Stronger coordination than a 2-layer window
  (it's global), still forward-only (a top-down broadcast, not a backward gradient). Cousin of **DFA** (Direct
  Feedback Alignment) — fixed random feedback, no weight transport.
- **The diagnosis everyone shares** (Parallel Training with Local Updates,
  [2012.03837](https://arxiv.org/abs/2012.03837); Interlocking Backprop,
  [2010.04116](https://arxiv.org/abs/2010.04116)): *"local algorithms fail because there is no mechanism for
  higher layers to communicate with lower layers — lower layers learn representations that aren't productive for
  the higher layers."* That sentence **is** the Phase-2 wall, in the wider local-learning literature's own words.

## How to read the evidence — the honest part

- **OLU's gain is real but modest.** In The Trifecta, OLU is **one of three** techniques; the heavy lifting on
  the depth curve is done by **batch-norm**, with SymBa and OLU as smaller add-ons. So "goodness-coupling alone
  bends the wall up a lot" is **not** what the paper shows. Expect OLU to *help*, not to *unlock* depth by
  itself.
- **A one-layer lookahead may be too short.** P2.2's wall is about *global* composition across 8 layers; a
  2-layer window passes a little coordination locally but doesn't guarantee it accumulates. Direct feedback
  (top-down, global) is the stronger bet if the 2-layer window underdelivers — at the cost of one top-down wire.
- **It does not change the *objective family*.** OLU still optimizes *energy*-goodness, just coupled across two
  layers. The reframe in [the-objective-reframe](the-objective-reframe.md) argues the deeper fix is changing
  *what* goodness measures (energy → prediction/info-preservation). Direction 1 is the cheap coordination patch;
  the reframe is the structural cure. They stack: a **predictive objective + a coordination window** is the
  GIM-with-LoCo recipe, which closes most of the gap to end-to-end.

## Substrate fit

Excellent for the 2-layer window (OLU/DF-O): it needs only *two layers' activations live at once* — the chip
already holds the LocalCapacitor buffers for the dual-rail forward. No labels, no batch stats, no backward pass.
Direct-feedback / top-down adds **one broadcast wire** (top activations → all layers) — feasible (it's the same
class of object as the γ broadcast, and the north-star brain is explicitly top-down), but it is *added wiring*,
so price it.

## Verdict / how to prioritise

**Run it — as the cheap, fast, unsupervised first probe, because it is nearly free** (the dual-rail forward
already computes everything; OLU is a few lines on top of `train_step`). But set expectations from the
literature: goodness-coupling alone is a *modest* lever. The high-value experiment is to test it **together with
the objective reframe** (does a predictive/info-preserving objective *plus* a 2-layer coordination window earn
depth on flat-MLP?), and to test **direct-feedback (top-down)** as the stronger coordination if the 2-layer
window stalls.

**Cheapest informative experiment:** add an OLU "help-the-next-layer" term to the P2.1 healthy cell (layer-norm
+ linear + contrast), re-run the P2.1/P2.2 depth-slope on CIFAR-flat. If the slope moves from −0.02 toward 0,
that is the first crack in the wall and routes the bigger objective work. If it doesn't, it's a clean negative
that says "coordination-window alone is insufficient → the fix must be the objective," which is exactly the
fork you want resolved.

## Papers

- **The Trifecta (OLU)** — [2311.18130](https://arxiv.org/abs/2311.18130) (also `ref/` — the Phase-2 rival).
- **Distance-Forward (DF-O)** — [2408.14925](https://arxiv.org/abs/2408.14925) (also `ref/distance-forward.md`).
- **Layer Collaboration (γ broadcast)** — [2305.12393](https://arxiv.org/abs/2305.12393).
- **Direct feedback / constant-width** — [2601.21683](https://arxiv.org/abs/2601.21683).
- **Diagnosis of the myopia problem** — [2012.03837](https://arxiv.org/abs/2012.03837),
  [2010.04116](https://arxiv.org/abs/2010.04116).
