# Experiment P2.1 — the normalization × goodness grid (the make-or-break gate)

> **Status: ✅ RUN COMPLETE (2026-06-21) — verdict GATE FAILED → STOP/rethink → route P2.2 (objective).** The
> make-or-break rung of Phase 2: P2.0 reproduced the wall and routed us here (verdict **LOST**, cause = *both*
> axes). P2.1 asked the one question the whole phase hangs on — **can a different normalization and/or goodness
> make SCFF separability *rise* with depth?** Answer on CIFAR-flat: **no.** 0/7 learning cells reach slope ≥ 0;
> the literature's transmission fix (linear goodness + per-sample norm) works at the *mechanism* level (kills
> deactivation, preserves rank, lifts shallow features) but does **not** create depth-rising class separability —
> the bottleneck is the *objective* (density ≠ class), not transmission. Per README §5 this is the STOP/rethink
> branch; the rethink routes to **P2.2 (class-aware objective)**, not the transmission-adjacent rungs. Convention:
> question → setup → run → result → read → decision. Spec: [`../README.md`](../README.md) §P2.1. Reporting:
> [`../result-format.md`](../result-format.md). Builds on [`../exp0/experiment-0.md`](../exp0/experiment-0.md)
> (the wall + the grid-widening decision). The two papers it leans on:
> [`../../../research/papers/phase1-2/deeperforward.md`](../../../research/papers/phase1-2/deeperforward.md) (keep per-sample norm, fix the goodness) and
> the Trifecta ([2311.18130](https://arxiv.org/abs/2311.18130), batch-norm route — the rival, drawn as the GPU
> reference).

## Question

1. **Does separability rise with depth under a different norm and/or goodness?** The wall (length-norm +
   squared) declines at **−0.018/layer** (P2.0, CIFAR-flat). Does any grid cell take the **depth-slope from
   `< 0` to `≥ 0`** — separability non-declining with depth? This is the entire Phase-2 thesis in one slope sign.
2. **Does the substrate-feasible version keep it? (the hero test).** Per-sample norms (layer-norm, group-norm)
   need no batch; batch-norm does. Of the cells that bend the curve up, is the **online / per-sample** one within
   `0.03` of the GPU batch-norm reference — i.e. does going single-sample-online *forfeit* the gain?
3. **Which axis earns the depth — norm, goodness, or the coupling?** P2.0 named *both* causes (deactivation +
   rank-collapse). The grid decomposes them: is it the norm swap, the goodness swap, or only the
   **layer-norm + linear** corner where they combine (the corner two recent papers validate, the Trifecta never
   tests)?
4. **Light continual preview (the early veto sniff).** On the *winning* cell only, a quick continual sanity —
   does the depth-fix obviously *cost* the Phase-1 continual win? Full ACC+BWT veto across surviving levers stays
   **P2.6**; this is the cheap early catch the Continual-Normalization prediction motivates (see Hypothesis).

**Pass gate (README §P2.1, make-or-break).** At least one variant reaches **depth-slope `≥ 0`** AND the
**online-BN final-layer probe is within `0.03` of batch-BN**. **If no variant reaches slope `≥ 0`, STOP and
rethink before P2.2+.**

## Hypothesis (committed, with the research behind it)

> **The winner is the per-sample corner — `layer-norm + linear goodness` — and it is *also* the substrate-native
> and continual-safe one.** Two of the three most recent FF-depth papers earn depth by *fixing the goodness while
> keeping a per-sample norm*, never batch-norm: **DeeperForward** (ICLR 2025 — mean/linear goodness, layer-norm
> kept, 17 layers) and **ASGE** (Sept 2025 — spatial-mean goodness, layer-norm kept, reverses degradation, scales
> to ImageNet). The mechanism is the one P2.0 measured: linear goodness has **no `h`-factor** in the update
> (`dG/dz = gs·1[z>0]`) so quiet units keep learning (kills the dead-unit cascade, P2.0 dead 0.02→0.47), and
> because layer-norm is **mean-zero**, goodness-as-mean **decouples from the forward rep for free, with no batch
> statistics** — the most substrate-native fix possible.
>
> **Batch-norm is doubly disfavoured and is included only as the GPU reference.** It is not per-sample (the
> online version must prove it doesn't forfeit the gain — Q2), *and* **Continual Normalization (ICLR 2022)**
> predicts it **rots under task shift** (the *cross-task normalization effect*: running moments bias to the
> current task, old tasks get normalized by current-task stats → forgetting). So even if batch-norm wins the
> static depth curve, the per-sample corner is what the chip carries forward. The light continual preview (Q4) is
> the first cheap test of that prediction.

## Setup (LOCKED — methodology rule #3)

**The grid = the P2.0 wall config, with norm and goodness made switches, under the threshold-free contrast
loss.** One cell at a time; depth is the curve axis; CIFAR-flat is the headline (the only surface with a real
wall — P2.0 proved synth is flat), synth is the dial + code sanity.

### The focused grid (decided 2026-06-21 — focused, not full 12-cell factorial)

Drop the cells the research already predicts dead; keep every cell that carries information. **9 cells:**

| # | norm | goodness | role | encoding (`result-format` Layer A) |
| --- | --- | --- | --- | --- |
| 1 | length-norm | squared | **the wall** (P2.0 baseline, the line to beat) | dashed grey |
| 2 | length-norm | linear | isolate goodness swap *alone* (norm held = wall) | dashed grey, thin |
| 3 | **layer-norm** | **linear** | **the hero — substrate-native, the predicted winner** | **bold** (per-sample) |
| 4 | layer-norm | squared | isolate norm swap *alone* (goodness held = wall) | per-sample |
| 5 | group-norm | linear | per-sample, finer-grained than layer-norm (G groups) | dotted purple |
| 6 | **online-BN** | **linear** | **the substrate hero candidate (running-stats, batch-1)** | **solid teal, bold** |
| 7 | batch-norm | linear | **GPU reference** for cell 6 (the online-vs-batch gap) | solid blue, thin |
| 8 | batch-norm | squared | the **Trifecta** route (batch-norm + squared) — GPU ref | solid blue, thin |
| 9 | no-norm | linear | cheat/fail control (should blow up / collapse) | thin red |

*(Dropped as degenerate: `no-norm + squared` — unbounded goodness, blows up; `length-norm + linear` is kept as
#2 only because it cleanly isolates the goodness axis. `group-norm + squared`, `online-BN + squared` dropped —
the squared axis is fully characterized by cells 1/4/8; the live question is whether *linear* goodness rescues
each norm.)*

### Locked knobs

| Knob | Value | Why |
| --- | --- | --- |
| **Headline task** | **CIFAR-10-flat** (3072-D, 10-class, no conv) — same `load_cifar_local` as P2.0 | the only surface with a real wall (P2.0: synth slope ≈ 0); the documented FF depth task. A *probe*, not a benchmark claim (README §2). |
| **Dial / sanity task** | **synth Tier-B** (`make_tierb`, same config as P2.0) | fast code sanity + the F6⁺ dial; **not** the headline (no wall). |
| **Loss** | **threshold-free contrast** (`objective="contrast"`, SymBa-signed `log(1+exp(G_neg−G_pos))`) — **NOT a shared θ** | each cell's goodness scale differs (linear sits at G≈35 → θ=2.0 saturates to a dead loss; experiment-0.md). Scale-invariant contrast is **required**, not cosmetic. Sign pinned from `p2lib` (`s=expit(Gn−Gp); dGp,dGn=−s,s`), never from the Trifecta summary (sign-flipped there). |
| **SCFF stack** | `L = 1…8`, **width 64**, ReLU, mono-forward dual-rail | depth is the axis; width fixed (one axis at a time). |
| **Goodness scale** | **sum** (`gs=1`, width-independent) — Phase-1 locked | linear-sum = `Σh`; squared-sum = `Σh²`. (DeeperForward uses mean; sum is the Phase-1 substrate-faithful choice and contrast is scale-invariant anyway.) |
| **Input norm** | on (`normalize_input=True`) — Phase-1 ratified | uniform goodness scale, zero L1 unit-death. |
| **Tap** | all-layer — Phase-1 corrected | S3 "last-n" reads the worst layers. |
| **online-BN spec** | **forward EMA only**: `μ_j←(1−ρ)μ_j+ρ·h_j`, `σ²_j←(1−ρ)σ²_j+ρ(h_j−μ_j)²`, normalize each sample by the running stat; **train updates stats, eval freezes them**. ρ swept lightly `{0.01, 0.05, 0.1}` if the default lags. | SCFF is *local* — no gradient flows back through the inter-layer norm — so Online-Norm's (Chiley 2019) backward *control process* is **moot**; only the forward EMA remains. The running `σ²_j` **is** the chip's `⟨a²⟩` register. |
| **batch-norm spec** | per-feature over the mini-batch at train (`μ_j,σ²_j` of the batch), running stats at eval | the GPU reference; `result-format` draws it thin (we choose what survives on the chip, not on a GPU). |
| **group-norm spec** | per-sample, features split into **G groups** (sweep `G∈{2,4,8}`), normalize within group; G=1 ≡ layer-norm | a per-sample, batch-free family between layer-norm (G=1) and finer granularity. |
| **Probe (PRIMARY)** | logistic, fixed L2 **C=1.0**, frozen **2k/2k** split, to convergence — **per layer** | the pinned ground-truth metric (`result-format` Layer B). |
| **Continual preview** | **winning cell only**: short class-incremental stream (exp4 setup, reduced), report ACC + a BWT sniff vs the length-norm wall | the cheap early veto catch; **full ACC+BWT veto across surviving levers = P2.6**. |
| **Seeds** | `[42, 137, 271, 314, 1729]`, median + IQR | methodology rule #2. |
| **Realism** | ideal floats; **online single-sample claimed only where a cell asserts it** (cells 3,5,6); no analog/PVT | substrate-feasibility is *tested* (Q2/the hero line), full PVT later. |

**Must emit** (`result-format` map for P2.1): **F3⁺** (the 9 cells overlaid, hero lines bold, +GD-hidden &
length-norm-wall reference envelopes, caption states the envelope gap **and** the winning slope), **REPR**
(CKA + effective-rank + Fisher/NCC vs depth — *why* the slope moved: does linear goodness lift erank off the
P2.0 floor of 11?), **INV** (loss-slope · **dead-unit %** · goodness-gap · erank-floor — dead-units is the
causal read: linear should hold ~0.05 where squared hit 0.47), and the **light CONT preview** (winner only).
DRIFT and the full CONT-veto are emitted at **P2.6** (deferred per the veto-scope decision).

## Run

**Built 2026-06-21** (autonomous build). [`../p2lib.py`](../p2lib.py) extended with the stateful norm modes
(`batchnorm` / `online_bn` / `groupnorm`); [`run_exp1.py`](run_exp1.py) (9-cell grid + WALL_REF + GD envelope +
REPR metrics + light continual preview) + [`plot_exp1.py`](plot_exp1.py) (F3⁺ · SLOPE · REPR · REPR_CKA · INV ·
CONT). `arrays.npz` + `manifest.json` saved; regenerate with `python plot_exp1.py figs_exp1_<task>`.

**Design decisions made during the build (recorded — methodology rule #8):**

1. **All 9 cells run under the threshold-free contrast loss; the P2.0 wall is added back as `WALL_REF`.** Cell 1
   (length+squared, **contrast**) is the in-grid wall baseline (apples-to-apples under the common loss). Because
   P2.0's canonical wall used **two-sided θ=2.0**, I also train `WALL_REF` = length+squared+**two-sided θ=2.0**
   once per seed — both the **regression guard** (it must reproduce P2.0's decline on CIFAR, slope ≈ −0.016) and
   the historical reference line in F3⁺. (Loss should not move the wall; this verifies it.)
2. **Stateful-BN dual-rail rule: stats from the positive (real) rail, applied to both rails, one EMA update per
   site/step.** The chip's `⟨a²⟩` register tracks *real-data* statistics, so `infer()` (real rail only) stays
   consistent. `batchnorm`@train normalizes by the batch stat (the GPU leak); `online_bn`@train normalizes by
   the running EMA (the substrate lag — the Q2 gap); both use frozen running stats at eval. Norm **sites**:
   0 = input, 1…L = inter-layer. `groups=8`, `bn_rho=0.05` (EMA rate).
3. **online-BN = forward EMA only.** SCFF is locally trained — no gradient flows back through the inter-layer
   norm — so Online-Norm's (Chiley 2019) backward control process is moot; only the forward running-stat
   normalization remains. (The substrate already holds the register; this is the cheap, faithful version.)
4. **Continual preview = digits, class-incremental** (`load_digits`, the exp4 5-task setup, L=4, 3 seeds),
   measuring the **SCFF all-class linear-probe trajectory** over tasks for {wall, winner, online-BN} — the BWT
   sniff (does the norm's SCFF forget as the stream shifts?). Light by design; full ACC+BWT veto = P2.6.

**Smoke (synth, 2 seeds, 178s) — code de-risked, harness clean.** All 6 norms run NaN-free; the F3⁺/SLOPE/REPR/
INV/CONT figures + pass-gate + winner logic all work. On the wall-free synth (P2.0: no wall, slope ≈ 0) the
`layer+lin` hero is already the only fix-cell with slope ≥ 0 (+0.003) and the top final probe (0.714) — the
hypothesis direction, but synth is not decisive (no wall to bend). **The headline verdict rests on CIFAR-flat.**

**CIFAR 5-seed run complete (2026-06-21, 1387s, `git 3c7cbd0`).** One bug caught + fixed mid-run (recorded —
methodology rule #5): the `none` cheat-control overflows to NaN on CIFAR's 3072-D input (unbounded activations
across 8 unnormalized layers) — now caught by a finite-check and recorded at chance rather than crashing the
grid; and the pass-gate auto-"winner" initially mis-fired on a *collapsed* cell (squared+mean-zero died to
chance, flat slope read as a degenerate "pass") — fixed to exclude collapsed cells before any conclusion was
drawn. Result / Read / Decision below.

## Result / figures

**Run 2026-06-21**, 5 seeds `[42,137,271,314,1729]`, median + IQR, CIFAR-10-flat (headline). Figures per
`result-format` in [`figs_exp1_cifar/`](figs_exp1_cifar): [F3⁺](figs_exp1_cifar/F3plus_grid.png) (9-cell depth
curve) · [SLOPE](figs_exp1_cifar/SLOPE.png) (the make-or-break bar) · [REPR](figs_exp1_cifar/REPR.png) +
[CKA](figs_exp1_cifar/REPR_CKA.png) · [INV](figs_exp1_cifar/INV.png) · [CONT](figs_exp1_cifar/CONT_preview.png).
`arrays.npz` + `manifest.json` saved; regenerate with `python plot_exp1.py figs_exp1_cifar` (no retrain).

**Regression guard PASSED — exact.** `WALL_REF` (length+squared, two-sided θ=2.0 — *exactly* P2.0's wall)
reproduces P2.0 to the digit: `0.230 → 0.116`, slope **−0.0157** (P2.0 was −0.0157). The code is verified; the
grid is built on the same wall.

| cell (n=5 median) | L1 → L8 probe | slope/layer | final [IQR] | dead L8 | erank L8 | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `len+sq` (wall, contrast) | 0.292 → 0.221 | **−0.010** | 0.221 [0.221,0.225] | 0.25 | 19 | declines |
| `len+lin` | 0.316 → 0.175 | −0.019 | 0.175 | 0.22 | 16 | declines |
| **`layer+lin` (HERO)** | **0.333** → 0.197 | **−0.020** | 0.197 [0.167,0.201] | **0.00** | **46** | declines |
| `layer+sq` | 0.10 → 0.10 | (flat) | 0.100 | **1.00** | **0** | **COLLAPSED** |
| `group+lin` | 0.261 → 0.133 | −0.017 | 0.133 | 0.00 | 50 | declines |
| **`online-BN+lin` (HERO)** | **0.329** → 0.191 | **−0.021** | 0.191 [0.174,0.194] | **0.00** | **50** | declines |
| `batch-BN+lin` (ref) | 0.340 → 0.167 | −0.026 | 0.167 | 0.00 | 33 | declines |
| `batch-BN+sq` (Trifecta) | 0.10 → 0.10 | (flat) | 0.100 | **1.00** | **0** | **COLLAPSED** |
| `none+lin` (cheat) | 0.181 → 0.175 | −0.001 | 0.175 | 0.41 | 8 | near-chance fail |
| **GD-hidden envelope** | flat ~0.36 | — | 0.354 ceiling | — | — | gap vs wall **+0.187** |

**THE GATE FAILED: 0 / 7 learning cells reach depth-slope ≥ 0.** Every cell that *learns* declines; the only
two cells with slope ≥ 0 (`layer+sq`, `batch-BN+sq`) **collapsed to chance** (every unit dead, erank 0) — their
flat slope is degenerate, not a pass (the pass-gate excludes them).

## Read (eight-slot)

**Pass gate (README §P2.1, make-or-break): FAILED.** No normalization × goodness variant takes the depth-slope
from `< 0` to `≥ 0` while learning. Per README §5 this is the explicit **STOP-and-rethink** branch.

1. **Claim.** On unsupervised flat-MLP SCFF (CIFAR-flat), **the depth wall is not a transmission problem.** No
   norm × goodness cell makes per-layer separability *rise* with depth: every learning cell declines (−0.010 to
   −0.026/layer), and the DeeperForward-style heroes (`layer+lin`, `online-BN+lin`) decline **as fast or faster**
   than the wall — they start higher (better *shallow* features) but lose it all by L8. The literature's lever
   (fix the goodness, keep a per-sample norm) **does exactly what it claims at the mechanism level** — kills the
   deactivation cascade (dead 0.25→**0.00**), preserves rank (erank 19→**46–50**), lifts the L1 probe
   (0.29→**0.33**) — **yet none of that becomes depth-rising class-separability.** The bottleneck is the
   *objective*, not the transmission.
2. **Number + IQR.** Heroes: `layer+lin` 0.333→0.197 (slope −0.020 [−0.022,−0.020]); `online-BN+lin` 0.329→0.191
   (−0.021). Wall (contrast) 0.292→0.221 (−0.010); WALL_REF (two-sided, =P2.0) 0.230→0.116 (−0.0157). Collapsed:
   `layer+sq`, `batch-BN+sq` → 0.100, dead 1.00, erank 0. GD ceiling 0.354, envelope gap **+0.187** (headroom
   present — gate is falsifiable, same as P2.0). n=5, all-seed-consistent (every learning slope < 0 in 5/5).
3. **Figures.** [SLOPE](figs_exp1_cifar/SLOPE.png) (0/7 learning cells ≥ 0 — the headline) ·
   [F3⁺](figs_exp1_cifar/F3plus_grid.png) (all decline toward chance) · [INV](figs_exp1_cifar/INV.png)
   (linear→dead 0.00; squared+mean-zero→dead 1.00; wall→0.25) · [REPR](figs_exp1_cifar/REPR.png) (erank preserved
   by linear, collapses for wall; **probe & NCC decline regardless**).
4. **Mechanism.** Two mechanisms, cleanly separated. **(a) Transmission fix works but is insufficient.** Linear
   goodness removes the `h`-factor → quiet units keep learning → no deactivation (dead 0.00) and rank holds
   (erank ~50). But keeping units alive and rank high only preserves **density** structure — and (Phase-1) SCFF
   *clusters by density, not class*; on flat CIFAR pixel-density ≠ class, so depth compounds density, not class.
   The fix gives more/healthier features that still aren't class-aligned → probe still falls. **(b) Squared
   goodness + mean-zero norm = catastrophic death.** `layer+sq`/`batch-BN+sq` die completely (dead 1.00) — a
   *new* finding: mean-zero centering makes ~half the units negative→ReLU-dead, and squared goodness's `h`-factor
   then kills the rest; the **wall survives *only because* length-norm does NOT remove the mean** (keeps the rep
   positive, units barely alive at dead 0.25). DeeperForward's deactivation thesis, confirmed and *sharpened*.
5. **Threats.** (a) **Flat-MLP, unsupervised SCFF** — DeeperForward/ASGE earn depth with *supervised* per-layer
   CE on *CNNs*; our negative result is specific to the unsupervised, fully-connected substrate regime (which
   the FF survey confirms is *unaddressed* — no prior answer to import). The *shape* (all learning cells decline,
   heroes ≤ wall by L8, mean-zero+squared death) is load-bearing; absolute magnitudes are low (flat CIFAR is
   thin). (b) **The continual preview is inconclusive** — digits' task-shift is too mild/easy (all configs flat
   ~0.90–0.93, no visible BN rot), so the Continual-Norm prediction is *untested here*; it needs a harder
   continual task at P2.6. (c) The gate's "winner" auto-label initially mis-fired on a collapsed cell; fixed
   (collapsed cells excluded) before any conclusion — the verdict rests on the corrected logic.
6. **Decision.** **GATE FAILED → STOP/rethink (README §5).** The fix must not be sought on the *transmission*
   axis. Route the rethink to **P2.2 (the objective: class-aware / hard negatives)** as the decisive next test —
   it attacks the actual bottleneck (density ≠ class) that no norm/goodness can touch. **P2.3 (collaboration) and
   P2.4 (interface) are deprioritized** — there is no depth-rising transmission signal for them to refine. If
   P2.2's class-aware objective *also* fails to bend the slope, depth is confirmed **not the lever** and the
   substrate-collision (README §0) is resolved by Phase-1's answer — *stay shallow, get depth from boosted blocks*
   (P2.5), not from a deep SCFF stack. *(Full in ## Decision.)*
7. **Substrate-feasibility (slot 7).** Moot but logged: `online-BN+lin` lands within **+0.024** of `batch-BN+lin`
   (Q2 pass, |gap| ≤ 0.03) — going single-sample-online does *not* forfeit batch-BN's behaviour. But there is **no
   gain to keep** (both decline), so the hero-line test is vacuous this rung. The substrate-native per-sample
   cells (`layer+lin`, `group+lin`) are the cheapest *if* a later rung makes any cell win.
8. **Continual-preservation (slot 8, preview).** Inconclusive (see threat b): on digits, wall / `layer+sq` /
   `online-BN+lin` all hold flat (~0.90–0.93, BWT ≈ 0) — the task is too easy to surface the predicted BN rot.
   The full ACC+BWT veto (and a harder continual task) is **P2.6**; nothing here contradicts the Phase-1 win.

## Decision

**GATE FAILED — the make-or-break STOP, taken honestly (README §5).** The normalization × goodness grid does
**not** bend the depth wall up for unsupervised flat-MLP SCFF. This is a real result, not a tuning failure
(WALL_REF reproduces P2.0 exactly; 5/5 seeds agree; headroom present at +0.187).

- **The transmission fix is the right mechanism for the wrong problem.** It works precisely as the literature
  says — DeeperForward's deactivation cure (linear goodness → dead 0.00, erank preserved, shallow probe up) is
  *confirmed on our substrate*. It just doesn't produce depth-rising **class** separability, because our
  bottleneck is the **unsupervised objective** (density ≠ class, Phase-1), which lives on a different axis.
- **Route the rethink → P2.2 (objective: class-aware / hard negatives from the LUT), not P2.3/P2.4.** P2.2 is the
  one lever that attacks density ≠ class directly. It is now *promoted ahead of* the transmission-adjacent rungs.
  **Carry forward into P2.2:** (i) the **threshold-free contrast loss** (a genuine positive — it ~doubled the
  deep-layer probe vs two-sided: 0.221 vs 0.116 final; keep it as the P2.2+ default loss); (ii) a **per-sample
  norm** (`layer-norm` or `length-norm`) with **linear goodness** as the transmission baseline (no deactivation,
  rank preserved, substrate-native) — so P2.2 varies *only* the objective on a healthy transmission substrate.
- **If P2.2 also fails to bend the slope → depth is not the lever.** Then the README §0 substrate-collision is
  answered by Phase-1: *stay shallow, get depth from boosted blocks (P2.5)*, and the deep-SCFF stack is abandoned
  as a static-accuracy path. This is the pre-registered fallback, not a new hypothesis.
- **New finding to record (spec-relevant):** **squared goodness + mean-zero normalization is catastrophic**
  (total unit death) — the wall survives *only because length-norm preserves the mean*. Any future mean-zero
  cell **must** pair with linear goodness. And **contrast > two-sided** for deep SCFF (the loss matters).
- **References for later rungs.** The CIFAR grid (every learning slope ∈ [−0.026, −0.010], all < 0; heroes ≤ wall
  by L8; GD gap +0.187) is the baseline P2.2's F3⁺ must beat. The transmission question is **closed** for the
  flat-MLP unsupervised regime: it is necessary (use linear+per-sample) but not sufficient.

## References (P2.1-specific, full list in README §10)

- **DeeperForward** (ICLR 2025) — keep per-sample norm, fix goodness squared→mean/linear; the predicted-winner
  corner. Story: [`../../../research/papers/phase1-2/deeperforward.md`](../../../research/papers/phase1-2/deeperforward.md).
- **The Trifecta** ([2311.18130](https://arxiv.org/abs/2311.18130)) — batch-norm route (the rival / GPU
  reference); 6-layer 2048-wide FCN on CIFAR-10 (our headline precedent); BN placement *normalize→linear→ReLU*.
- **ASGE** ([2509.12394](https://arxiv.org/abs/2509.12394)) — spatial-mean goodness, layer-norm kept, reverses
  degradation; the second paper backing the goodness lever over batch-norm.
- **Online Normalization** (Chiley 2019) — batch-1 normalization via forward EMA; the backward control process
  is moot under SCFF locality (we keep only the forward EMA). **Batch Renorm** (Ioffe 2017) — the documented
  train/eval stat mismatch that Q2 measures.
- **Continual Normalization** (ICLR 2022) — the cross-task normalization effect; the prediction that batch/online
  -BN rot under task shift while per-sample norms survive (motivates the light preview, sets up the P2.6 veto).
- **2025 FF survey** ([2504.21662](https://arxiv.org/abs/2504.21662)) — confirms continual/online/single-sample
  FF is *unaddressed* (the substrate regime is novel; the sim is the only oracle).
