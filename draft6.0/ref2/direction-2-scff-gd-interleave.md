# Direction 2 — make SCFF interleave with GD layers

> Your goal: let GD-trained layers sit *between* SCFF layers, instead of SCFF always feeding SCFF. **Verdict up
> front: Phase 2 already half-answered this, and the answer is mostly "don't." The useful residue is one narrow
> seam — a GD layer with a *non-collapsing* objective — and it is lower-priority than Directions 1/3.**

---

## What P2.5 already settled (don't re-litigate it)

P2.5 tested exactly this under the names **read** vs **write**:

- **`read`** = the GD layer is a *readout only*; the next SCFF block still sees the **raw SCFF features**. This
  **works** (boosting ensemble, +0.010, ~85% of GD accuracy at ~1/6 backward) and is the surviving recipe.
- **`write`** = the GD layer's class-aligned hidden rep is **fed forward into the next SCFF block** — i.e. a GD
  layer literally interleaved into the stream. This is **your Direction 2, and it failed decisively**
  (−0.04 → −0.09, monotone worse with more checkpoints).

**Why write fails (the mechanism, worth internalising):** a GD layer trained to predict 10 logits produces a
**class-collapsed** representation — it throws away everything *except* the 10-way class direction. Running SCFF
on top of a 10-dimensional-ish collapsed rep forces the next block to re-cluster an information-starved input.
The rich raw features are gone. So the stream must carry **rich SCFF features (read)**, never a **class-collapsed
GD rep (write)**.

This is the same conclusion the wider local-learning literature reaches: you combine blocks by **fusing their
readouts at the end** (a shared head over per-block logits), not by **piping one block's class-collapsed output
into the next**. ASGE's "Fusion-Pred", BiCovG's "Logistic Fusion", CaFo's ensembled predictors — all *read*,
none *write*.

## The one seam that's still open: a non-collapsing intermediate objective

`write` failed because the GD layer's objective was **classification** (collapses to the label manifold). The
untested variant: a GD (or local-supervised) layer trained on an objective that **preserves information** while
still injecting *some* class/direction structure — so the next SCFF block receives a *re-aligned but still rich*
representation. Candidates from the literature:

- **Block-local learning with auxiliary non-classification losses** (Block-Local Learning,
  [2305.14974](https://arxiv.org/abs/2305.14974); Nøkland & Eidnes "predsim" = **pred** CE **+ sim**
  similarity-matching, [1901.06656](https://arxiv.org/abs/1901.06656)). The *sim* (similarity-matching) loss
  keeps a high-dimensional structure-preserving target instead of collapsing to logits — exactly the property
  `write` lacked. A "predsim-write" might interleave where a "CE-write" can't.
- **Interlocking Backpropagation** ([2010.04116](https://arxiv.org/abs/2010.04116)) — overlapping blocks share a
  *local* gradient through the boundary, so the upper block's needs shape the lower block's output *without* a
  global pass. This is the principled "interleave" — but note it is **gradient sharing across the boundary**
  (a small backward window), i.e. it is really Direction 1's coordination window wearing different clothes.
- **"Local Back-Propagation for Forward-Forward Networks"** (MDPI Appl. Sci. 2025) — explicitly studies
  independent unsupervised layer-wise training mixed with local backprop in an FF stack. Closest published
  thing to "SCFF and GD in the same stack." Worth a read before committing.

## Substrate fit

`read` (the survivor) is the substrate's native shape — forward-only SCFF bulk + tiny backward heads, fuse the
logits. A genuinely *interleaved* GD layer means a backward-trained layer sitting mid-stream whose output the
*forward* SCFF body then consumes — extra coupling, extra backward sites deeper in the stack, and the
class-collapse failure mode. The non-collapsing-objective variant keeps the coupling but removes the collapse;
it is feasible but buys back complexity the `read` recipe was designed to avoid.

## Verdict / how to prioritise

**Lowest of the three.** The headline question ("can GD sit between SCFF?") is *answered*: as a class-collapsing
classifier, **no** (P2.5 write); as an end-of-stack readout you fuse, **yes** (P2.5 read, already the recipe).
The only thing worth one experiment is the **non-collapsing intermediate objective** (predsim-style or a
structure-preserving transform as the "GD layer") — and even that is better framed as part of Direction 1
(coordination) or Direction 3 (a better deep local learner) than as its own track. Don't open a third front
here; fold the live seam into whichever of 1/3 you run.

## Papers

- **P2.5** (`../src/phase2/exp5/experiment-5.md`) — the read/write result that already answers this.
- **Local Error Signals / predsim** — [1901.06656](https://arxiv.org/abs/1901.06656) (the non-collapsing `sim`
  loss).
- **Block-Local Learning** — [2305.14974](https://arxiv.org/abs/2305.14974).
- **Interlocking Backpropagation** — [2010.04116](https://arxiv.org/abs/2010.04116).
- **Local Back-Propagation for Forward-Forward Networks** — MDPI Appl. Sci. 15(15):8207, 2025.
