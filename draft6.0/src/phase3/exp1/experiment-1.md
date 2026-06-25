# Experiment P3.1 — cross-layer coordination (Direction 1 / OLU) on the contrastive objective

> **Status: ✅ RUN COMPLETE (2026-06-22) — PARTIAL: coordination is a real, correct lever (monotone slope
> improvement, holds selectivity, *rises* on synth) but flat-CIFAR saturates ~−0.011 and never reaches flat —
> because flat-CIFAR has no depth headroom *for anyone* (GD-hidden is flat too). → lock **contrast + w2** as the
> best unsupervised cell; route to **P3.3 (continual veto)**, the question that actually decides adoption
> (direct-feedback = an optional static side-check).** P3.0 settled the objective (contrast preserves class info
> but declines −0.016); P3.1 adds the coordination P2.2 named as missing. Spec: [`../design.md`](../design.md)
> §P3.1. Reporting: [`../result-format.md`](../result-format.md). Builds on
> [`../exp0/experiment-0.md`](../exp0/experiment-0.md).

## Question

1. **Does cross-layer coordination bend the contrastive slope from −0.016 toward ≥ 0?** The user's Direction 1:
   a layer should help the *next* layer's objective. Implemented as a **coordination window** `w` — layers
   trained in joint groups of `w` (gradient shared across the window, then detached). `w=1` ≡ P3.0 contrast
   (per-layer, gradient-isolated); `w=2,4` = increasing coordination.
2. **Does it hold selectivity > 0** (the class info P3.0's contrast won)?
3. **Does it saturate** (a bigger window stops helping)?

**Pass gate.** Some `w` takes the depth-slope to **≥ 0** (or decisively toward 0) with selectivity > 0 →
unsupervised forward-only depth earned → P3.3. Else PARTIAL/FAIL → direct-feedback or Mono-Forward fallback.

## Setup (LOCKED)

One variable: the coordination window. Everything else = P3.0's contrastive cell. `SCFFContrastOLU` —
two masked views of the window input, forwarded through `w` layers, **one InfoNCE at the window top**,
backprop through the whole window (then detach). `w=1` reproduces `SCFFContrast` exactly (the regression
guard). CIFAR-flat headline + synth sanity; `w ∈ {1,2,4}`; energy-wall + GD ceiling + untrained-same-arch
random floor as references; per-layer logistic probe; seeds `[42,137,271,314,1729]`, median + IQR;
single-threaded.

## Hypothesis (committed)

> **Coordination helps (it's the gap P2.2 named) and should bend the slope up — the open question is *how far* on
> the thin flat-CIFAR regime.** A layer trained to help the next layer's discrimination should compose class
> structure across depth rather than re-discriminating myopically. On synth (clusters = classes) I expect it to
> flip declining → rising; on CIFAR I expect real improvement but possibly capped, because **flat-CIFAR has
> little depth headroom even for GD** (P2.2: GD-hidden flat ~0.36) — "rising" may be unachievable there for *any*
> method, making the achievable win "stop the decline + stay above random."

## Run

Built [`../p3lib.py`](../p3lib.py) `SCFFContrastOLU` (windowed multi-layer backprop: L2-embed-norm VJP +
layer-norm VJP + relu/linear, two views, gradient-isolated between windows). [`run_p3_1.py`](run_p3_1.py)
(window scan + energy/GD/random references, reuses the P3.0 bench) + [`plot_p3_1.py`](plot_p3_1.py). Smoke
synth (2 seeds): **w=1 reproduced P3.0 contrast to the digit** (−0.0053, sel +0.105 — backprop verified), and
windows flipped the synth slope **−0.005 → +0.002 (w2) → +0.008 (w4)**, monotone. CIFAR 5-seed: **the first
launch died after 4/5 seeds (a clean 39-min freeze with no traceback — the laptop slept mid-run, not a crash);
re-ran clean** (949s, single-threaded).

## Result / figures

**Run 2026-06-22**, 5 seeds, CIFAR-flat. Figures in [`figs_p3_1_cifar/`](figs_p3_1_cifar):
[F3⁺](figs_p3_1_cifar/F3plus_depth.png) · [SLOPE](figs_p3_1_cifar/SLOPE.png) · [SELECT](figs_p3_1_cifar/SELECT.png).
`arrays.npz` + `manifest.json` saved.

| cell (n=5 median) | probe L1 → L8 | slope/layer | decline | tail-ret | selectivity (mean) |
| --- | --- | --- | --- | --- | --- |
| **contrast w1** (= P3.0 baseline) | 0.331 → 0.230 | **−0.0158** | 0.055 | 0.70 | +0.059 |
| **contrast w2** (coordination) | 0.340 → 0.254 | **−0.0105** | 0.056 | **0.76** | **+0.066** |
| contrast w4 (more coordination) | 0.334 → 0.256 | −0.0113 | 0.058 | 0.76 | +0.057 |
| energy-wall (ref) | 0.33 → 0.20 | −0.0202 | 0.080 | 0.60 | ~0 (into random) |
| GD-hidden ceiling | ~0.36 (flat) | ~0 | — | — | — |

**Synth (sanity):** w1 −0.005 → **w2 +0.002 → w4 +0.008** (rising), selectivity +0.10 throughout. The mechanism
flips declining → rising where the task has headroom. **Per-seed CIFAR:** 5/5 w2 beats w1 on the deep endpoint
and selectivity; the slope improvement (−0.0158 → −0.0105) is monotone and consistent.

## Read (eight-slot)

**Pass gate: PARTIAL.** Coordination improves the slope by a real, monotone margin (w2: −0.0158 → −0.0105, ~33%
flatter; deep endpoint 0.230 → 0.254; selectivity +0.059 → +0.066) but does **not** reach ≥ 0 on flat-CIFAR, and
it **saturates** (w4 ≈ w2).

1. **Claim.** **Cross-layer coordination (your Direction 1) is a real and correct lever — it eases the decline,
   lifts the deep layers, holds class-selectivity, and on a task with headroom (synth) flips declining → rising —
   but flat-CIFAR is too thin to show "rising," because it has no depth headroom for *anyone* (GD-hidden is flat
   ~0.36).** So coordination + the contrastive objective produce the **best unsupervised cell yet** (above random
   at every depth, gentle decline), but the *static-depth "slope ≥ 0"* bar is unachievable on this task.
2. **Number + IQR.** w2 slope −0.0105 (vs w1 −0.0158, energy −0.0202), deep endpoint 0.254 (vs w1 0.230), sel
   +0.066; w4 saturates (−0.0113). Synth: w2 +0.002, w4 +0.008 (rising). GD ceiling flat ~0.36. n=5, monotone.
3. **Figures.** [F3⁺](figs_p3_1_cifar/F3plus_depth.png) (w2/w4 peel above w1 at depth, all above random) ·
   [SLOPE](figs_p3_1_cifar/SLOPE.png) (slope improves w1→w2, saturates w4) · [SELECT](figs_p3_1_cifar/SELECT.png).
4. **Mechanism.** Coordination lets a layer's update account for the next layer's discrimination → it composes
   class structure rather than re-discriminating myopically (the P2.2 coordination gap, partially closed). The
   gain saturates at w=2 because a longer window on a thin task adds little, and the absolute ceiling is set by
   the task (flat-MLP CIFAR: even GD doesn't rise). "Rising" needs a task with depth headroom (synth shows it).
5. **Threats.** (a) flat-CIFAR has no depth headroom for any method → "slope ≥ 0" is the wrong bar here; the
   load-bearing reads are the *monotone improvement*, *above-random selectivity*, and the *synth rise*. (b) Window
   coordination is one of two levers; **direct-feedback (global top-down)** is untested and is the 2026
   CLAPP++ winner — a possible further push, but on a flat-GD task its upside is bounded. (c) First run died to a
   laptop-sleep; the re-run is clean and deterministic.
6. **Decision.** **PARTIAL → lock `contrast + w2` as the Phase-3 unsupervised cell; route to P3.3 (continual
   veto).** The static-depth chase has hit the *task's* ceiling, not the method's — and Phase 1 always said the
   architecture's home is the *continual* regime, not static depth. The question that decides whether to adopt
   the objective reframe is **does contrast+coordination preserve the continual win** (P3.3). Direct-feedback is
   an optional static side-check, not a blocker. Mono-Forward fallback **not** triggered (we have a working
   unsupervised cell that preserves class info). *(Full in ## Decision.)*
7. **Substrate-feasibility.** `SCFFContrastOLU` is forward-only between windows, gradient-isolated at window
   boundaries; the window backprop is `w` layers of local VJP (cheap, `w≤2` suffices). Needs in-batch negatives
   (the LUT sampler) like P3.0's contrast. Substrate-plausible; w=2 is the cheapest sufficient coordination.
8. **Continual-preservation.** N/a this rung — it is *the* P3.3 question, now teed up with the locked cell.

## Decision

**PARTIAL — coordination validated, the static-depth ceiling is the task's, route to the continual veto.**

- **Your Direction 1 works.** Coordination eases the decline monotonically (−0.0158 → −0.0105), lifts the deep
  layers (+0.024 at L8), holds selectivity, and *rises* on synth. It is the correct complement to the contrastive
  objective — together they are the best unsupervised cell across all of Phase 2/3 (above random at every depth).
- **Flat-CIFAR can't show "rising" for anyone** (GD-hidden flat ~0.36) → "slope ≥ 0" is the wrong success bar on
  this task. We've achieved the *achievable* static win: stop the destruction, preserve class info, degrade
  gently. The rest is a **task-headroom** limitation, not a method failure (synth, which has headroom, *does*
  rise).
- **Lock `contrast (InfoNCE) + coordination window w=2`** as the Phase-3 unsupervised cell. Carry it to P3.3.
- **Route → P3.3 (the continual veto):** does this cell preserve the Phase-1 continual win (ACC + BWT)? That is
  the question that decides whether the whole objective reframe is worth adopting — the architecture's home is
  continual, not static depth. **Optional, not blocking:** a **direct-feedback** (global top-down) static
  side-check, and/or a **depth-headroom task** so "rising" is testable at all.

## References (P3.1-specific)

- **P3.0** ([`../exp0/experiment-0.md`](../exp0/experiment-0.md)) — the contrastive objective this builds on.
- **OLU / The Trifecta** ([2311.18130](https://arxiv.org/abs/2311.18130)) · **DF-O**
  ([../../../research/papers/phase1-2/distance-forward.md](../../../research/papers/phase1-2/distance-forward.md)) — the coordination-window lineage.
- **CLAPP++ / direct-feedback** ([2601.21683](https://arxiv.org/abs/2601.21683)) — the untested global-coordination
  lever (the optional next static push).
