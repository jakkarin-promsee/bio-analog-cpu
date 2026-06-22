# ref2 — Phase-3 research: how to break the SCFF depth wall

> The literature pass behind the Phase-3 "make SCFF earn depth" question (2026-06-21). Phase 2 *closed* the
> deep-**energy-goodness**-SCFF path (P2.1 transmission + P2.2 objective, oracle-proof) and shipped the cheap
> survivor (boosted-`read` shallow blocks). This folder asks the next question — *is there a way to make the
> cheap forward-only bulk actually go deep?* — and surveys every candidate, including the three you proposed.
>
> Companion to [`../ref/`](../ref/README.md) (the Phase-1/2 paper stories). Same house style: plain-language,
> "what it means for us," substrate-first. **Start with [the-objective-reframe](the-objective-reframe.md)** —
> it changes the framing everything else hangs on.

---

## The one finding that reframes the whole question

Phase 2 concluded the depth wall is *"intrinsic to SCFF's forward-only locality."* **The literature says that's
too strong — the wall is intrinsic to the *energy-goodness objective* (`Σh²`), not to locality.**

- **Greedy InfoMax** ([1905.11786](https://arxiv.org/abs/1905.11786)) is an existence proof: forward-only,
  gradient-isolated, **unsupervised** local learning where each module *measurably improves on the previous one*
  — depth composes — because its objective is **info-preserving / predictive** (InfoNCE), not energy.
- A Jan-2026 paper tests **SCFF by name** and shows the predictive local-SSL family (**CLAPP++**) **matches
  end-to-end backprop-SSL** on CIFAR-10 (80.51 vs 80.49), using cheap forward-only coordination
  ([2601.21683](https://arxiv.org/abs/2601.21683)).

So P2.2 was right that *no negative-selection* saves energy-goodness — and *also* there is a different objective
family, untested in Phase 2, with a depth existence proof that keeps everything the project values (unsupervised,
forward-only, no batch stats, continual-safe). That family is the highest-value Phase-3 lever.

## Your three directions, placed

| your direction | what it is | published as | verdict | priority |
| --- | --- | --- | --- | --- |
| **1 · cross-layer goodness** (A1-from-layer-2) | A1 learns to raise *layer-2's* goodness, not its own | **OLU** (The Trifecta), **DF-O** (Distance-Forward), Layer Collaboration γ | real & unsupervised & ~free to test, but **published gain is modest**; a 2-layer window may be too short | **cheap first probe** |
| **2 · interleave SCFF↔GD** | put GD layers *between* SCFF layers | = P2.5 `write` (already failed); block-local / interlocking BP | **mostly answered: don't** (`write` collapses features; `read`+fuse is the recipe). One seam: a *non-collapsing* objective | **lowest** |
| **3 · different forward-only learner for the deep part** | SCFF up front, something else deep | GIM/CLAPP (unsup) · Mono-Forward (sup) · SoftHebb · predsim · forward-gradient | **strongest practical direction** — forks into unsup (GIM/CLAPP) vs sup (Mono-Forward) | **highest** |

## The 5th direction you didn't list — and why it's actually #1

**Change SCFF's objective from energy to predictive/info-preserving** (the GIM/CLAPP idea). It is not really
"replace SCFF for the deep part" (Direction 3) nor "couple goodness across layers" (Direction 1) — it is
*upgrading what every SCFF layer optimizes* so the **whole unsupervised bulk composes with depth.** It subsumes
the good half of Directions 1 and 3, keeps the project's identity, and is the only path with a published depth
+ matches-backprop result in our exact constraint set (forward-only, local, unsupervised). Detail:
[the-objective-reframe](the-objective-reframe.md).

The one honest caveat: GIM/CLAPP earn depth on **spatial/temporal** data (predict the next patch/timestep). Our
headline is **flat-MLP vectors**, which have no sequence to predict — so the real research question is *"what
does a flat-MLP layer predict?"* (sibling-sample rep / masked-feature reconstruction / the next layer's state).
That is the experiment, and it is genuinely open.

## Recommended priority order (my position)

1. **The objective reframe — predictive / info-preserving goodness, unsupervised** (the 5th direction). Highest
   value: depth existence proof, keeps the continual win, substrate-native. *First experiment:* swap the P2.1
   healthy cell's contrast loss for a predictive/info-preserving local objective on a task with predictable
   structure, and re-run the depth-slope. The open sub-question is the flat-MLP "what to predict."
2. **Direction 1 (OLU coordination window) — as the cheap probe that routes #1.** Nearly free (the dual-rail
   forward already computes it). *First experiment:* add OLU's "help-the-next-layer" term to the healthy cell,
   re-run depth-slope. If it cracks the wall a little → coordination matters → invest in #1's stronger forms
   (direct-feedback / top-down). If flat → the fix must be the objective, confirming #1-the-reframe is the road.
3. **Mono-Forward — the de-risked fallback** (Direction 3, supervised branch). If the unsupervised objective
   won't compose on flat vectors, Mono-Forward is the *proven*, flat-MLP-native, depth-capable, beats-backprop
   local learner — and a strictly cheaper "GD 20%" than full backprop blocks. Keep it staged, not led-with,
   because it spends the unsupervised property Phase 1 proved is the actual win.
4. **Direction 2 — fold in, don't open.** The live seam (non-collapsing intermediate objective) rides along with
   #1 or #3; it doesn't merit its own track.
5. **Bench, don't bet:** forward-gradient (the literal forward-only "direction" signal — high variance on 3072-D)
   and PEPITA.

## How this sits against Phase 2 (so nobody thinks we're re-opening a closed case)

Phase 2's energy-goodness results **all stand** — we are not re-running P2.1/P2.2. We are testing a lever
Phase 2 *never touched*: a different objective *family*. The clean way to say it: *Phase 2 proved you can't tune
energy-goodness into depth; Phase 3 asks whether a predictive/info-preserving objective composes where energy
can't — with OLU-style coordination as the cheap probe and Mono-Forward as the proven fallback.*

## Files

- [the-objective-reframe.md](the-objective-reframe.md) — **read first.** Energy vs predictive goodness; GIM/CLAPP
  existence proof; P2.2 narrowed; the flat-MLP "what to predict" question.
- [direction-1-cross-layer-goodness.md](direction-1-cross-layer-goodness.md) — your A1-from-layer-2 idea = OLU /
  DF-O / direct-feedback; cheap probe; modest published gain.
- [direction-2-scff-gd-interleave.md](direction-2-scff-gd-interleave.md) — = P2.5 `write` (failed); the
  non-collapsing-objective seam; lowest priority.
- [direction-3-forward-only-alternatives.md](direction-3-forward-only-alternatives.md) — the algorithm zoo
  (GIM/CLAPP/SoftHebb/Mono-Forward/predsim/forward-gradient/PEPITA) and the unsup-vs-sup fork.

## Master paper list (Phase-3 additions, beyond `ref/`)

| paper | id | direction | sup? | depth | substrate note |
| --- | --- | --- | --- | --- | --- |
| Greedy InfoMax | [1905.11786](https://arxiv.org/abs/1905.11786) | reframe/3A | no | ✅ | the existence proof |
| CLAPP | [2010.08262](https://arxiv.org/abs/2010.08262) | reframe/3A | no | ✅ | single-sample, Hebbian-plausible |
| Can Local Learning Match SSL-BP? | [2601.21683](https://arxiv.org/abs/2601.21683) | reframe | no | ✅ | tests SCFF; CLAPP++ = BP; direct-feedback + constant width |
| LoCo | [2008.01342](https://arxiv.org/abs/2008.01342) | 1/reframe | no | ✅ | GIM + adjacent-block coupling |
| Mono-Forward | [2501.09238](https://arxiv.org/abs/2501.09238) | 3B | yes | ✅ | **flat-MLP-native**, beats BP, the fallback |
| Local Error Signals (predsim) | [1901.06656](https://arxiv.org/abs/1901.06656) | 2/3B | yes | ✅ | non-collapsing `sim` loss |
| SoftHebb | [2107.05747](https://arxiv.org/abs/2107.05747) | 3A | no | ~ | purest local rule; low ceiling |
| OLU / The Trifecta | [2311.18130](https://arxiv.org/abs/2311.18130) | 1 | (either) | ~ | = your idea; modest alone |
| Layer Collaboration (γ) | [2305.12393](https://arxiv.org/abs/2305.12393) | 1 | (either) | ~ | one broadcast wire |
| Forward gradient | [2202.08587](https://arxiv.org/abs/2202.08587) · [2210.03310](https://arxiv.org/abs/2210.03310) | 5 | either | ? | forward-only "direction"; high variance |
| PEPITA / top-down feedback | [2302.05440](https://arxiv.org/abs/2302.05440) | 5 | yes | ~ | 2-pass input modulation |
| Predictive Forward-Forward | [2301.01452](https://arxiv.org/abs/2301.01452) | 1/5 | no | ~ | top-down generative + predictive coding |
| Block-Local Learning | [2305.14974](https://arxiv.org/abs/2305.14974) | 2 | yes | ✅ | block auxiliary losses |
| Interlocking Backprop | [2010.04116](https://arxiv.org/abs/2010.04116) | 1/2 | yes | ✅ | overlapping-pair gradient sharing |
| Mono-Forward eval (3 methods) | [2511.01061](https://arxiv.org/abs/2511.01061) | 3 | — | — | energy/memory parity protocol |
| CaFo / ASGE / BiCovG | [2303.09728](https://arxiv.org/abs/2303.09728) · [2509.12394](https://arxiv.org/abs/2509.12394) · [2605.04346](https://arxiv.org/abs/2605.04346) | 3B | yes | ✅ | per-layer-CE CNNs; confirm the pattern |
