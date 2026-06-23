# Experiment P2.2 — the objective: can class-aware negatives build depth where transmission couldn't?

> **Status: ✅ RUN COMPLETE (2026-06-21) — verdict DEPTH IS NOT THE LEVER → close deep-SCFF path → route P2.5.**
> P2.1 closed the *transmission* axis (norm × goodness can't bend the wall up); P2.2 closes the *objective* axis
> with an airtight upper bound — **even a perfect label-based oracle negative changes the depth-slope by nothing**
> (all cells −0.022 to −0.015/layer, identical to random; no real probe lift). The two decisive levers both fail,
> so the depth wall is **intrinsic to SCFF's forward-only locality**: composing class features across depth needs
> cross-layer coordination that only GD supplies. The deep-SCFF static-accuracy path is closed; depth comes from
> **GD-corrected boosted blocks (P2.5)**, not a deep SCFF stack. P2.3/P2.4 are now moot. Convention: question →
> setup → run → result → read → decision. Spec: [`../README.md`](../README.md) §P2.2. Reporting:
> [`../result-format.md`](../result-format.md). Builds on [`../exp1/experiment-1.md`](../exp1/experiment-1.md)
> (gate failed → here) and
> [`../../../research/papers/phase1-2/scff.md`](../../../research/papers/phase1-2/scff.md) (the negative = "mixture of two things"; make it a *between-class*
> mixture).

## Question

1. **Does a class-aware objective bend the depth-slope to ≥ 0 — the thing transmission couldn't? (DECISIVE.)**
   SCFF's negative is "real sample + a *different* sample = a low-goodness mixture." With **random** partners the
   mixture is class-agnostic, so goodness learns *density* (P2.1's wall). With **class-aware** partners (mixture =
   a *different-class* blend), "low goodness = between-class region" → goodness should separate **classes** — and
   class structure, unlike density, is what *should* compound with depth. Does it?
2. **Does it lift the final-layer probe over the random-negative baseline by > IQR? (the README §P2.2 gate.)**
3. **Can the class-awareness come *unsupervised* — the substrate question.** Oracle negatives use true labels
   (the mechanism upper-bound). The substrate has no labels: do **unsupervised** cluster-based negatives (a
   different KMeans/LUT cluster) retain the gain, or do they fail because the clustering itself is density-based
   (the same density ≠ class trap, one level up)?

**Pass gate (two, per the reframed phase).**
- **DECISIVE (slope):** does **hard-oracle** reach depth-slope **≥ 0** (or move it decisively toward 0 vs the
  random baseline's −0.020)? This routes the whole depth question.
- **README §P2.2 (probe):** does a hard-negative lever lift the **final-layer probe** over random by **> the
  IQR**, *or* is it logged as "no effect beyond the transmission fix" (a real result for the substrate budget)?

## Hypothesis (committed)

> **Hard-ORACLE is the mechanism test and I expect it to help — the open question is by how much, and whether
> the slope actually turns non-negative.** Making the negative a between-class blend is the one thing that turns
> goodness from a density detector into a class detector, and class structure is what depth is *supposed* to
> accumulate. So oracle should lift the probe (probe-gate likely passes) and, if depth is genuinely the lever,
> bend the slope toward 0.
>
> **Hard-UNSUP (KMeans/LUT) is the doubtful one — and that doubt is itself the finding.** On flat CIFAR the
> unsupervised clustering is *pixel-density* clustering (the exact density ≠ class problem, re-incurred when
> *picking the negative*). So unsup cross-cluster negatives may be barely more class-aware than random. If oracle
> works but unsup doesn't, the verdict is sharp: **the objective IS the lever, but class-aware negatives are not
> obtainable unsupervised on this representation** → the open problem moves to *getting* class structure (later
> phases / a better front-end), not to depth per se.
>
> **The decisive negative:** if **even hard-oracle** (perfect class-aware negatives) **cannot** bend the slope,
> then **depth is not the lever, full stop** → close the deep-SCFF static path and fall back to Phase-1's answer
> (shallow + boosted blocks, **P2.5**). This is the pre-registered fallback from the P2.1 decision.

## Setup (LOCKED — methodology rule #3)

**One variable: the negative partner. Everything else = P2.1's healthy transmission baseline.** P2.1 settled the
*loss* (threshold-free contrast) and the *transmission* (`layer-norm + linear`, the only non-collapsing,
rank-preserving, deactivation-free per-sample cell). P2.2 holds both fixed and varies **only** how the negative's
partner is chosen — so any change in the depth curve is attributable to the objective, nothing else.

| Knob | Value | Why |
| --- | --- | --- |
| **Headline task** | **CIFAR-10-flat** (3072-D, 10-class) — same `load_cifar_local` as P2.0/P2.1 | the only surface with a real wall (synth is flat); the documented FF depth task. |
| **Dial / sanity** | **synth Tier-B** (`make_tierb`) — cluster→class map is fixed, so oracle negatives are well-defined | fast code sanity; not the headline (no wall). |
| **Transmission (FIXED)** | **`layer-norm` + `linear` goodness + threshold-free `contrast` loss** | P2.1's healthy substrate: no deactivation (dead 0.00), rank preserved (erank ~50), per-sample / substrate-native, contrast ~2× the deep probe of two-sided. |
| **Varied — the negative partner** | the grid (whole-training-set partner pool; only the *constraint* differs): `random` (any sample — the P2.1≈baseline) · **`hard-oracle`** (a different **true-class** sample — the mechanism upper-bound) · `hard-oracle-proto` (a different-class **mean** — clean prototype vs noisy sample) · **`hard-unsup`** (a different **KMeans cluster**, k=10 — the substrate version; LUT is the online variant) | one variable; oracle separates "does class-aware help" from "can we get it unsupervised" — P2.0-selectivity-control-style rigor. |
| **SCFF stack** | `L = 1…8`, width 64, ReLU, mono-forward dual-rail | depth is the axis (the slope is the headline). |
| **Negative construction** | `x_pos = 2·x_k` ; `x_neg = x_k + partner` (the SCFF rule, [`scff.md`](../../../research/papers/phase1-2/scff.md)); only `partner` selection varies | the mechanism is unchanged from P2.1 — only *which* sample is blended in. |
| **Unsup clusterer** | **KMeans, k = n_classes (10)** on raw input, once per seed (report cluster→class purity) | the clean unsupervised proxy; the **LUT** (cosine-vigilance WTA) is the *online* substrate version, deferred to P2.6/Phase-3. |
| **Probe / seeds / realism** | logistic C=1.0, frozen 2k/2k, per layer · seeds `[42,137,271,314,1729]` median+IQR · ideal floats | pinned metrics; one axis at a time. |

**Must emit** (`result-format` map for P2.2 + the reframe): **F3⁺** (negatives overlaid, + WALL_REF & GD-hidden
envelopes), **SLOPE** (the decisive slope bar — does oracle reach ≥ 0?), **REPR** (does hard-neg raise
Fisher/NCC *with depth*? — the class-structure read), **INV** (dead/gap), and the **ablation table**
(negative-quality → final-probe lift + slope, IQR in every cell). Plus a **cluster-purity** number for hard-unsup
(how class-aligned is the KMeans clustering — the diagnostic for why unsup may fail).

## Run

*Pending — build order: (1) `train_scff_neg` (pluggable negative partner; `SCFF2.train_step` gains an optional
`neg_partner=` — random in-batch when None, exact P2.1 behaviour). (2) `run_exp2.py` (4-cell negatives grid +
WALL_REF + GD envelope + REPR + cluster purity). (3) `plot_exp2.py` (F3⁺/SLOPE/REPR/INV + ablation). (4) smoke
(synth, 2 seeds) → CIFAR 5-seed.*

## Result / figures

**Run 2026-06-21**, 5 seeds, CIFAR-10-flat (headline). Single-threaded relaunch (`OMP_NUM_THREADS=1` + `-u`)
after the first attempt **phantom-hung** at the KMeans step — sklearn/OpenMP deadlocks in a backgrounded process
on this machine (logged: [[background-run-openmp-phantom]]). Figures in [`figs_exp2_cifar/`](figs_exp2_cifar):
[F3⁺](figs_exp2_cifar/F3plus_negatives.png) · [SLOPE](figs_exp2_cifar/SLOPE.png) ·
[REPR](figs_exp2_cifar/REPR.png) · [INV](figs_exp2_cifar/INV.png) ·
[ABLATION](figs_exp2_cifar/ABLATION.png). `arrays.npz` + `manifest.json` saved.

| negative (n=5 median) | L1 → L8 probe | slope/layer | final [IQR] | lift vs random (disjoint-IQR) | dead L8 | erank L8 |
| --- | --- | --- | --- | --- | --- | --- |
| `random` (P2.1 base) | 0.321 → 0.179 | −0.020 | 0.179 [0.173,0.186] | — | 0.00 | 39 |
| **`hard-oracle`** (diff TRUE class) | 0.330 → 0.181 | **−0.022** | 0.181 [0.176,0.181] | **+0.003 (−0.010 ✗)** | 0.00 | 42 |
| `hard-proto` (diff class mean) | 0.294 → 0.195 | −0.015 | 0.195 [0.172,0.210] | +0.016 (−0.014 ✗) | 0.00 | 46 |
| `hard-unsup` (diff KMeans cluster) | 0.330 → 0.184 | −0.022 | 0.184 [0.179,0.186] | +0.005 (−0.008 ✗) | 0.00 | 39 |
| WALL_REF (P2.0 two-sided) | 0.230 → 0.117 | −0.0157 | — | regression guard ✓ (=P2.0) | — | — |
| GD-hidden envelope | **flat ~0.36** | ~0 | 0.354 ceiling | gap vs wall +0.187 | — | — |

**KMeans cluster purity = 0.226** (chance 0.10) — the unsupervised clustering is barely class-aligned (it
clusters by pixel-appearance, the density ≠ class trap re-incurred at negative-selection).

**Synth sanity (the code-is-correct control):** on synth (where clusters ≈ classes) `hard-oracle` *does* lift
the probe (+0.027, disjoint-IQR **+0.013 = real**) and slopes go positive — the mechanism works **where class
structure exists**. So the CIFAR negative is real, not a bug.

## Read (eight-slot)

**Both gates FAILED — and this is the *decisive* one (README §5).** No negative — not even the perfect
label-based **oracle** — bends the depth-slope toward 0 (all ∈ [−0.022, −0.015], same as random) or lifts the
final probe by a real (disjoint-IQR) margin.

1. **Claim.** **The objective is not the depth lever either — so depth is not the lever, full stop.** With
   P2.1's healthy transmission held fixed, making the SCFF negative *perfectly class-aware* (oracle, true labels)
   changes the depth curve **not at all**: it declines at −0.022/layer, identical to random negatives. Even the
   clean class-prototype negative (the gentlest, −0.015) still declines and its lift is within the IQR. The two
   decisive levers — **transmission (P2.1)** and **objective (P2.2)** — both fail to make deep SCFF compose class
   structure. The deep-SCFF-earns-depth question is **closed, negative.**
2. **Number + IQR.** `hard-oracle` 0.330→0.181 (slope −0.022 [−0.022,−0.022]); lift over random **+0.003,
   disjoint-IQR margin −0.010** (not real). `hard-proto` lift +0.016 (disjoint −0.014, not real). `hard-unsup`
   +0.005 (disjoint −0.008). WALL_REF reproduces P2.0 exactly (−0.0157). GD envelope **flat ~0.36** (gap +0.187).
   n=5, all 5 seeds decline for every cell. KMeans purity 0.226.
3. **Figures.** [F3⁺](figs_exp2_cifar/F3plus_negatives.png) (oracle sits *on top of* random — zero separation) ·
   [SLOPE](figs_exp2_cifar/SLOPE.png) (0/4 reach ≥ 0) · [ABLATION](figs_exp2_cifar/ABLATION.png) (no real lift) ·
   [REPR](figs_exp2_cifar/REPR.png) (rank healthy ~40, NCC/Fisher don't rise).
4. **Mechanism.** The class signal *is* read at L1 (oracle 0.330 > random 0.321 — a hair) but it **does not
   accumulate with depth — it dilutes**, exactly like density did. The deep reason is the one
   [`scff.md`](../../../research/papers/phase1-2/scff.md) names: *"each layer optimizes its own myopic goodness with no global signal
   coordinating the layers."* **Composing class features across depth requires cross-layer coordination, which
   forward-only locality structurally cannot provide** — no choice of *objective* or *normalization* can
   manufacture it, because the missing thing isn't *what* each layer optimizes, it's the *coordination between*
   layers. That coordination is precisely what GD (the 20%) exists to supply. So the "SCFF gap as tasks get
   harder" *is* the depth gap, and it is unfixable inside SCFF.
5. **Threats.** (a) **Flat-MLP CIFAR is a thin regime** — even GD's hidden layers are flat at ~0.36 (depth adds
   nothing for *anyone* here), so the result is "deep SCFF *actively destroys* class info (0.33→0.18) while GD
   *preserves* it (flat 0.36)," not "depth fails to add." The destruction, and its imperviousness to the
   oracle, is the load-bearing finding. (b) The oracle is the strongest possible negative-quality lever; a
   weaker real lever cannot exceed it, so the negative generalizes. (c) Synth shows the mechanism *works where
   classes exist* — ruling out a code error.
6. **Decision.** **DEPTH IS NOT THE LEVER → close the deep-SCFF static path → Phase-1 fallback (P2.5).** Two
   decisive rungs (transmission + objective) now agree. Route to **P2.5 (multi-block = SCFF with GD *between*)**
   — get depth from GD-corrected boosted blocks, the architecture's actual depth mechanism (Phase-1 exp3).
   **P2.3 (collaboration) and P2.4 (interface) are now moot** — they refine a deep SCFF stack that this rung
   proves should not exist; the GD interface question collapses to "read the *shallow* SCFF" (Phase-1 answered:
   tap all, stay shallow). *(Full in ## Decision.)*
7. **Substrate-feasibility (slot 7).** The unsupervised question is settled the hard way: KMeans purity 0.226 →
   `hard-unsup` ≈ random (lift +0.005, not real). But it is **moot**, because even the *oracle* (the upper bound
   it would approximate) fails. There is no class-aware-negative gain to make substrate-feasible.
8. **Continual-preservation (slot 8).** N/a this rung — no winning lever to veto-test; the continual question
   moves with the surviving architecture (boosted blocks) to P2.5/P2.6. Nothing here touches the Phase-1 win.

## Decision

**DEPTH IS NOT THE LEVER — the deep-SCFF static-accuracy path is closed (the pre-registered decisive negative).**
P2.1 ruled out the *transmission* axis; P2.2 rules out the *objective* axis with an airtight upper bound (a
perfect label-based oracle changes the slope by nothing). Together they prove the depth wall is **intrinsic to
SCFF's forward-only locality**, not a fixable property of normalization or negatives.

- **This is a confirmation of the architecture's own design logic, not a defeat.** Draft 6.0 always said SCFF is
  the cheap *shallow* 80% and GD is the coordinating 20%; [`scff.md`](../../../research/papers/phase1-2/scff.md) predicted "that gap
  is the entire reason the GD part exists." Phase 2 turned that prediction into a measured fact: **depth
  composition is the coordination SCFF gives up, and only GD restores it.**
- **Route → P2.5 (multi-block: `[SCFF×k → GD-realign]×N`).** This is now *the* Phase-2 depth question — does a
  GD checkpoint *between* shallow SCFF groups let the stack earn depth where a monolithic SCFF stack cannot? It
  re-tests Phase-1 exp3's boosting chain under the substrate framing (the GD-between *cadence* `k`).
- **Skip P2.3 + P2.4.** Both presuppose a deep SCFF stack worth refining; P2.1+P2.2 show there isn't one. The
  interface question reduces to Phase-1's settled answer (tap all, shallow).
- **The README §0 substrate-collision is resolved — by the other horn.** We cannot move SCFF's success onto the
  chip's cheap depth axis (proven). So depth must come from the cheap axis a *different* way: **stacked cheap
  shallow blocks with periodic GD coordination** (P2.5), not a deep SCFF stack. The Scap-cheap-depth axis is
  used by *block count*, not by *SCFF layer count*.
- **Carry forward (validated this phase):** threshold-free contrast loss + `layer-norm`/`length-norm` + linear
  goodness = the healthy shallow-SCFF cell (no death, rank preserved). Use it as the per-block SCFF front in P2.5.

## References (P2.2-specific)

- **SCFF** ([`scff.md`](../../../research/papers/phase1-2/scff.md)) — negative = "a mixture of two things, not one"; Ch4 intends
  cross-cluster mixing (the hard negative). The base rule we keep; only the partner changes.
- **P2.1** ([`../exp1/experiment-1.md`](../exp1/experiment-1.md)) — closed the transmission axis; set the healthy
  baseline (layer-norm + linear + contrast) and the deferred slope question.
- **The Trifecta SymBa sign trap** (recorded in [`../exp0/experiment-0.md`](../exp0/experiment-0.md)) — the
  contrast loss is already correctly signed in `p2lib` (`s=expit(Gn−Gp)`); P2.2 keeps it, varies only negatives.
- *Carry-over:* the LUT / hippocampus prototype store (Phase-1 exp4) — the *online* hard-negative sampler for
  P2.6; here we use static KMeans as the clean offline proxy.
