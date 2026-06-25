# Result format — the Stage-1 reporting standard (the house style)

> The standing **house style** for every draft-6.0 run, all phases. A phase's `design.md` says *what to test*; this
> file says *what a result looks like* so that every run — by you or by a handed-off agent — comes out
> **comparable, non-toy, and deep enough to cite.** Each `experiment-N.md` and each phase's thin
> `phaseN/result-format.md` delta links here instead of re-describing the basics.
>
> It fixes the three things that make results "feel like a toy": **(1)** no variance shown (single-seed pretty
> lines), **(2)** inconsistent encoding (block is teal here, green there; axes rescale every plot), **(3)**
> summaries that report the number but not the mechanism, the confound, or the decision.
>
> Grounded in how the neighbouring fields actually report: FF goodness/per-layer figures (Hinton; *Characterizing
> FF Training Behavior*, arXiv 2504.11229), linear-probe layer heatmaps (Alain & Bengio 2016), online/anytime
> accuracy + AAA (online-CL eval, arXiv 2308.10328), BoostResNet training-error-vs-modules with the theory bound
> overlaid (Huang et al. 2018), and the median+IQR / one-variable-per-row / error-bars discipline of the ML
> reproducibility checklists (Pineau; AAAI-25).
>
> This is the **floor**. Adapt upward per experiment; never drop below it. **Per-phase figure additions**
> (depth curves, CKA, gap surfaces, the capability map …) live in each phase's thin
> `phaseN/result-format.md`, which inherits everything here and adds only what that phase needed.

---

## Layer A — House style (the consistency contract)

The enforcement mechanism is **one plotting module per phase, with one function per catalog figure (Layer
B).** Every experiment, and every agent we hand an experiment to, calls the *same function* — so plots
**cannot** drift in look. Lock these once:

| Rule | Locked to |
| --- | --- |
| **Method encoding** | Each method gets ONE colour + linestyle, forever. `Block/OURS = solid teal` · `Pure-GD/BP = dashed orange` · `SCFF-only = dotted teal`. World colours fixed: `pos = blue`, `neg = red`. Never reassigned per-plot. |
| **Variance** | Every headline curve = **median line + IQR shaded band** across the 5 seeds `[42,137,271,314,1729]`. Single-seed lines only in an explicit per-seed diagnostic, never in a headline. |
| **Reference lines** | Accuracy plots always draw **chance** (dashed grey) + the **ceiling** (full-GD / tuned-BP / Bayes, per phase). Boosting plots always draw the **theoretical `e^{-½Tγ²}` bound**. A number with no reference line is a toy. |
| **Axes** | Samples-seen on **log-x**; accuracy on **fixed y = [chance, 1.0]** so plots compare across experiments. Difficulty axes labelled with the *dial value AND its meaning* ("length-scale 0.3 = high-freq boundary"; "overlap 0.95 = Bayes 0.24"). |
| **Caption** | Every caption ends with **the one-sentence takeaway**, not a description. Append `(n=5 seeds, task, weight budget)`. e.g. *"Block holds GD accuracy at ¼ the backward cost (n=5, spiral σ=0.1, 16.6k wts)."* |
| **Format** | **Fixed dpi · fixed `figsize` · fixed font, identical every plot** — *that* is the contract. **300-dpi PNG is the default** (our spec→A4 path is pandoc→docx via [`tools/mkdocx.py`](../../tools/mkdocx.py), where high-dpi PNG survives and SVG/EMF is finicky); vector (PDF/SVG) is nice-to-have, not required. Transparent bg. |

---

## Layer A2 — Reproducibility (every run is regenerable)

The house style governs how a figure *looks*; this governs whether it's *real*. **A figure you can't redraw
from saved data + the exact config is still a toy — just a prettier one.** This is the half of the
reproducibility checklists that median+IQR doesn't cover.

- **Every run writes a `manifest.json` next to its figures:** git commit hash, the full *resolved* config, the
  seed list, library versions, wall-clock, and the task-generator parameters.
- **Every run persists its raw logged arrays** (`.npz`/`.parquet`): the curves, per-layer probe accuracies,
  goodness values, op-counts — the numbers *behind* every figure.
- **Figures regenerate from saved data by one script — never from a live training run.** `plot.py <run-dir>`
  redraws every figure from the arrays. This is what lets you (or an agent) re-draw F3 six months later
  without re-running 50k samples — and it's what makes a result *citable*.
- **Heavy/continual cells checkpoint per cell** (`_ckpt.jsonl`, fsync'd) so an overnight death is resumable
  (the P3.1 lesson). Run single-threaded (`OMP_NUM_THREADS=1` + `python -u`), `PYTHONIOENCODING=utf-8` (the
  cp874 console gotcha) — the phantom-hang guard.

---

## Layer B — Base figure catalog (the "what is each result" backbone)

A small fixed set, **shared across all phases**. An experiment does not invent figures — it **declares which
catalog entries it emits.** (Phase-specific additions — depth curves, CKA, gap surfaces, the capability map —
are catalogued in each `phaseN/result-format.md`.)

| # | Figure | Axes / form | Diagnostic — the failure it catches |
| --- | --- | --- | --- |
| **F1** | **Learning panel** (HEADLINE) | per method, two curves on shared log-x axes — **held-out** acc + **train-on-seen** acc — with the **memorization gap shaded between each method's pair**; chance + ceiling refs, IQR bands | who *understands* vs *memorizes*; convergence speed. The gap is the *visual*, not a second chart |
| **F1′** | Adaptation curve (secondary) | prequential (predict-before-update) acc vs samples-seen | **tracking speed only** — a *distinct* measurement, **not** the gap (see the gap note below) |
| **F2** | **Memorization gap** | the **shaded region in F1** + a **scalar** in the table — **not** a standalone chart | structure vs rote, in one band + one number |
| **F3** | **Layer × time separability heatmap** | rows = layers, cols = log-checkpoints, colour = **linear**-probe acc; block vs GD pair, shared colourbar | *where & when* separability is built (bottom-up vs top-down) |
| **F4** | **Goodness separation** | per-layer `G_pos` vs `G_neg` (paired) + pos/neg goodness histograms | does SCFF separate at all — the exp0 gate |
| **F5** | **Boundary plot** (Tier-A only) | the 2-D decision boundary, actually drawn | sanity — *look at what it learned* |
| **F6** | **Reachability surface** (co-headline — the *shape read*) | final held-out acc as heatmap/surface over (difficulty × size), fixed budget; **block−GD difference map** | the scale-free shape read — *the read we trust most*; a **coarse grid can ride along in any sweep** |
| **F7** | **Backward cost / locality** | **measured** backward op-counts (block vs GD), **annotated** with the structural credit-distance (SCFF = 0, GD = full depth) | *the* structural claim — local & cheap vs global & expensive. Draw the *measured* cost; the distance is a labelled constant |
| **F8** | **Boosting shape** | training error vs #blocks + **theory bound overlay**; companion per-block γ bars | error falls as predicted; **dead-block** watch (γ≈0) |
| **F9** | **Trade curve** | held-out acc + backward cost vs SCFF fraction | the 80/20 sweet spot |
| **INV** | **Invariant strip** (every run) | small-multiples: loss-slope · dead-unit % · ceiling-saturation · (chains) inter-block drift | health at a glance — same strip every run |

**Gap definition (F1/F2) — don't let this one rot silently.** `train-on-seen accuracy` = re-evaluation
(*no update*) on a buffer of **already-trained-on** samples — **not** the prequential adaptation curve (F1′).
The distinction is load-bearing: under a **fresh-draw generator, single pass, `prequential ≈ held-out`, so the
gap is ~0 by construction** — there is nothing to memorize. The memorization gap only *means* something when
data repeats (a finite / looped pool) **or** when train-on-seen is measured by re-eval on a seen buffer.
**Default:** re-eval on a rolling buffer of the last `K = held-out size` trained-on samples, no update. *(Open
knob: buffer size / strategy — record it in the manifest.)* Loose definitions are this project's classic silent
killer; this one is pinned on purpose.

**Probe discipline (F3) — pinned, identical for every layer and method:** **logistic regression**, fixed **L2**
(record the value), a **frozen 2k/2k train/test split** of activations, trained **to convergence**. Linear so
the result is attributable to the *representation*, not the classifier (Alain & Bengio); *pinned* so "don't let
the probe get cleverer to rescue a layer" is actually enforceable, not a slogan.

**The scalar for tables.** Every run emits **two comparable numbers**: the **AAA** and the **final held-out
median ± IQR**. **AAA is pinned:** *trapezoidal area under held-out-acc vs `log₁₀(samples-seen)`, divided by the
log-span* → a single number in [chance, 1] (a convergence-speed-weighted average; log-x because the checkpoints
are log-spaced). Ablations are **tables, one variable per row, delta vs the baseline, IQR in every cell** —
never a bare mean.

---

## Calling a difference real (n = 5)

Five seeds is too few for honest p-values — so don't fake them, and don't let an agent over-claim from one
swung seed:

> A difference counts as **real** only if the **IQR bands are disjoint at the final checkpoint** *and* the
> **sign is consistent in ≥ 4 / 5 seeds, paired by seed** (same seed = same stream + same held-out, so the
> pairing is legitimate). Everything else is reported as **"within noise."**

One rule, load-bearing for the honesty of every comparison in Stage 1.

---

## Layer C — Summary template (the depth contract)

A shallow summary reports the number; a research summary reports **claim → number-with-uncertainty → mechanism →
confound → decision.** Every `experiment-N.md` *Read* section fills these six slots — **no slot may be empty**
(if one is "n/a", say *why*; an empty Threats section is a red flag, not a clean result):

1. **Claim** — one falsifiable sentence ("the block keeps a smaller memorization gap than same-budget GD").
2. **Headline number** — median + IQR across the 5 seeds, *against its reference* (ceiling / chance / theory
   bound). Never a bare number.
3. **Figures** — the catalog refs, each with a one-line read. Name the headline figure(s) explicitly.
4. **Mechanism** — *why* the number is what it is, tied to the substrate / algorithm reason. This is the part
   that makes it research, not a benchmark — and it's how the result re-loads later.
5. **Threats to validity** — what *else* could explain this (is the smaller gap real structure, or the block
   just under-using capacity?). This is methodology rule #1 — "is it the variable or an artifact?" — written in.
6. **Decision** — which open knob this *sets*, and what the next rung inherits. A result that changes no
   downstream decision didn't need running.

**Purpose of the summary.** It exists so that **future-you, or another agent, can act on the result without
re-running it** — make the next decision, catch a wrong conclusion via the stated confound, inherit the set
knob. It is *not* there to look impressive.

**Negative-result rule.** A failed rung still fills all six slots — slot 4 becomes "leading hypothesis for *why*
it failed" — and we do **not** tune-to-pass (methodology rule #5). A configuration that fails to converge is a
result; log it and move on.

---

## How this links into each experiment

Keep the existing `experiment-N.md` spine — **question → setup → run → result → read → decision** — but now:

- **Result / figures** = the catalog refs from Layer B (the mandatory set for that experiment + the phase's own
  additions in `phaseN/result-format.md`), all drawn through the phase's `plot_*.py` in the Layer-A house style.
- **Read** = the six-slot template from Layer C.
