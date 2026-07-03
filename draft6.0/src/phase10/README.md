# Phase 10 — Validation / showcase: the frozen object vs a fair BP+replay (the front door)

> **✅ COMPLETE (ran 2026-07-03, P10.0→P10.6, all 14 guards bit-exact; grid-4 reproduced bit-for-bit vs the P9
> freeze).** The **fourth and last Stage-2 phase** (P7 readout ✓ · P8 economy ✓ · P9 close/freeze ✓ · **P10
> validate**). Phase 10 **measured** the frozen two-brain object against a **fair, budgeted, tuned** BP+replay
> baseline across the continual gauntlet — it tuned nothing (the object was locked in P9; the only dial that moved was
> the declared cadence cost axis). The verdict shapes were pinned **BLIND** before any baseline number was seen.
> **+ §10 post-close extension (four rounds, author-directed; measurement-only, every carried array bit-exact):**
> the cadence break fully localized — a **plateau + two cliffs** (the safety plunge at cadence **6→7**; the accuracy
> cliff at **15→16**, where equal-count sleeps turn *timing*-sensitive) via grid-12 + the probes {7,13,14,15}; the
> per-batch **GAUNTLET-STREAM** view forward *and reversed* (ER is **order-sensitive** — reversed final AA 0.343 vs
> forward 0.504 — while OURS is order-invariant, 0.494 vs 0.490); every measured cadence point on the verdict Pareto
> (numbered-point encoding). **Round 3 — the ALIGNMENT-BREAK test (E8/E8b):** the committed gauntlet's block (24)
> equalled the grid-4 sleep period exactly (every sleep landed on a domain's last step); re-run with long randomized
> non-multiple blocks (sleeps mid-domain) + an aligned-72 control → **alignment is a NON-FACTOR for OURS** (paired gap
> +0.002; its retention *rises*, 0.490→0.533) — but ER strengthens on long stationary blocks (0.504→0.675), so **the
> gauntlet retention win is switch-frequency-scoped** (a stated money-figure scope line, not a defeat). **Round 4 —
> the staircase-mechanism test (E10, reversed-long):** the REV staircase's sag is the GD-readout frame going stale
> between sleeps (the bulk rotates every batch; only sleep re-anchors) — mid-domain sleeps demonstrably **rescue** it
> (jumps +0.052, 5/5; floors rise; OURS order-invariant at length, 0.527 vs 0.533) but the pre-registered confirming
> cut was mis-specified, so the mechanism is banked **supported-not-confirmed** (bulk-level component flagged, not
> excluded); ER stays order-sensitive even at length (0.580 rev-long vs 0.675 fwd-long). (A grid-5 fight point was
> added then withdrawn — within noise.)
> Read this for the verdict; numbers in [`RESULTS.md`](RESULTS.md); per-rung stories in [`expK/experiment-K.md`](exp0/experiment-0.md); the
> spec in [`design.md`](design.md) (§10 = the extension's pre-run record); the contract in [`result-format.md`](result-format.md).

---

## The verdict — an honest Pareto close-out (the founding bet's two halves, banked separately)

The frozen object is a **competitive, decisively safer, and far more noise-robust continual learner whose energy
advantage over conventional GD is substrate-realized** — a *substrate-native continual learner*, not a static-accuracy
or same-substrate-energy point-winner. Precisely the identity Phase 4 named. Against a **tuned, budget-matched
experience replay** (the honest opponent — Prabhu CVPR'23: ER is strong under a matched FLOPs+bytes budget), measured
across 5 seeds on the continual home + a 5-domain gauntlet + a held-out noise battery + natural digits:

- **ACCURACY half — *competitive on the continual home; trails a tuned ER on static natural data; WINS on continual
  safety*.** On the hard synthetic continual home OURS **ties** ER-strong (0.494 vs 0.498, within δ, P10.1); on
  recognizable **natural digits** a tuned ER **beats** OURS by **+0.071** (0.950 vs 0.879, P10.5) — OURS is not a
  static-accuracy competitor (P4, confirmed). But on the honest **worst-pre-sleep continual read** OURS is the
  **safest of the field**: worst-BWT **−0.028 vs ER's −0.272** (P10.1), worst-point all-prev retention **0.490 vs
  0.350** with higher anytime-accuracy (AAA 0.519 vs 0.433) across 5 domains (P10.3). *The "beats backprop accuracy"
  claim is not supported on final/static accuracy; OURS's accuracy edge is continual **stability**, and it is real.*
- **ECONOMICS half — *substrate-realized* (the honest R1 outcome).** On the **same digital substrate**, OURS's
  12-layer unsupervised bulk costs **1.5× more** than a small tuned ER (P10.1/P10.3) — the algorithm alone does **not**
  win the energy race against a small efficient net. The chip (**OURS-analog**) is **3.4–3.5× cheaper** than that same
  GD model on a conventional digital accelerator — but that advantage is the **analog crossbar** (a meter-structural
  floor), **not** the algorithm. "Less energy than modern GD" holds **for the chip**, honestly scoped as
  substrate-driven. On a same-substrate (accuracy × energy) Pareto, a small tuned ER **dominates** OURS (P10.6) — OURS's
  wins live on the axes that Pareto omits: **safety, noise-robustness, and the substrate**.
- **NOISE — a clean win over the fair opponent.** OURS-hardened **≫ BP+replay on every held-out channel** (iid 1.095
  vs 0.608, directional 0.978 vs 0.225, adc3b 0.923 vs 0.300, nuisance 1.000 vs 0.469; P10.4). A small directional/ADC
  residual (~0.02–0.08 > δ) is **named → the analog-realism layer** (the Phase-6 "scoped-YES" cashed on the whole
  object, honestly).

**Why this is a success, not a failure:** the founding claim was tested honestly against the strongest fair opponent
and *refined*, not inflated. OURS is what the project always said it was — a **continual** substrate whose value is
lifelong stability + noise-survival + the analog energy floor, not a static-accuracy or same-substrate-FLOP win. The
"why analog" is now **load-bearing and measured**, not incidental.

---

## The ladder (one line each; the number that carries it)

| rung | what it measured | the read |
| --- | --- | --- |
| **P10.0** bench + 6 new guards | is the racer fair + the object provably frozen? | 14/14 green; grid-4 **bit-exact**; ER-strong tuned on seed-7; full roster real code. Pre-registered: OURS uses *more* FLOPs than ER. |
| **P10.1** existential fight | OURS(g4) vs tuned ER + field, continual home | accuracy **tie** (0.494 vs 0.498); worst-BWT **−0.028 vs −0.272** (safety win); same-substrate energy 1.54× more; substrate total 3.35×. |
| **P10.2** cadence frontier | the family {4,5,6,8,12,16} + §10 probes {7,13,14,15} | grid-4 headline (bit-exact); **grid-5 = Tier-1 rep**; grid-6 = the safety δ-edge (−0.087), **grid-7 = the plunge** (−0.322); final AA plateaus to g15 and cliffs **at 15→16** (0.495→0.458 at the SAME energy/nsleep — timing-sensitive, not count-limited); energy monotone 6.7e7→4.0e7. |
| **P10.3** gauntlet (money figure) | 5 domain-IL worlds, all grids vs ER | worst-point all-prev **0.490 vs 0.350**, AAA **0.519 vs 0.433** (steadier); final 0.490 vs 0.504 (within δ); 1.47× / 3.5× energy. §10 **GAUNTLET-STREAM** (fwd+rev+long): ER saw-tooths per batch (live 0.273, ~0.1 at onsets) while OURS rides flat (0.469) — reversed (noised first) **ER collapses to 0.343 vs its forward 0.504** while OURS holds 0.494 — and the E8 alignment-break clears the flat line (**alignment a non-factor**, E8b gap +0.002) while scoping the win: on long stationary blocks ER re-converges per checkpoint (0.675 vs 0.533) → **the retention win is switch-frequency-scoped**. |
| **P10.4** noise showcase (held-out) | directional retention OURS vs BP vs naive | OURS **≫ BP+replay on every channel**; residual (dir 0.978 / adc3b 0.923) **named → analog layer**. |
| **P10.5** A5 natural (digits) | the fight a professor recognizes | ER-strong **beats OURS by +0.071** (0.950 vs 0.879) — synthetic masked ER's static-accuracy edge; OURS is a continual, not static, learner. |
| **P10.6** Pareto verdict | assemble the frontier + the map | same-substrate Pareto frontier = **{er_strong, gdumb}** (OURS dominated on acc×energy); OURS's wins are off-Pareto (safety/noise/substrate). §10: **every measured cadence point** (family + probes, 10 grids) drawn as the money line (~0.49-AA plateau, 6.7e7→4.0e7 pJ, the accuracy cliff visible on-line); frontier membership unchanged. |

---

## What OURS wins / ties / loses (the honest map)

| axis | OURS | best fair opponent | verdict |
| --- | --- | --- | --- |
| final accuracy (continual synthetic home) | 0.494 | ER-strong 0.498 | **tie** (within δ) |
| final accuracy (natural digits, static-ish) | 0.879 | ER-strong 0.950 | **loss** (−0.071 — not a static competitor) |
| worst-pre-sleep BWT (lifelong) | **−0.028** | ER-strong −0.272 | **win** (≈10× safer) |
| worst-point all-prev retention (gauntlet) | **0.490** | ER-strong 0.350 | **win** (steadier) + AAA 0.519 vs 0.433 — rapid-switch regime (§10 E8 scope; alignment a non-factor, E8b) |
| noise robustness (held-out, vs BP) | 0.92–1.10 | BP+replay 0.23–0.61 | **win** on every channel |
| energy — same substrate (algorithm) | 3.46e8 | ER-strong 2.25e8 | **loss** (1.54× — the deep bulk) |
| energy — chip vs conventional GD (total) | 6.70e7 (analog) | ER-digital 2.25e8 | **win** (3.4×, substrate-realized floor) |

---

## The disciplines that make it honest

- **Freeze in P9, judge in P10.** The object was locked *before* any baseline number existed (freeze-content guard:
  content manifest + grid-4 bit-exact; `59d2720` a provenance label). The only dial moved is the declared cadence cost
  axis. The verdict shapes were pinned BLIND in `design.md` §2.3.
- **The fair racer.** ER byte-matched to OURS's LUT + tuned on a **disjoint** seed (7 ∉ raced set); ER-budget (same
  FLOPs) + ER-strong (own config) both built; A-GEM / DER++ real code (grad-handle + logit distillation); GDumb the
  cost-pathological accuracy-axis control; naive-BP the floor. **The racer's shape is its own best choice, uncapped** —
  which is *why* the same-substrate energy cut goes against OURS (threat h, reported not hidden).
- **The load-bearing energy cut is same-substrate** (`E(OURS-digital)` vs `E(ER-digital)`); the analog factor is a
  meter-structural floor, never the contestable claim (R1). The meter is behavioral (ADC-centred, NOT SPICE).
- **The spine.** Every noise read is a **direction** (retention under a coherent shift), never a per-sample magnitude.

## Hand-offs (what P10 names / defers)

- **→ the analog-realism layer (SPICE/PVT):** the small directional/ADC residual P10.4 shows the read-side defense
  cannot fully reach; the absolute-Joule / PVT layer the behavioral meter cannot give.
- **→ a future draft (flagged, not executed):** the static-accuracy gap on natural data (P10.5) — a *convolutional* or
  larger bulk would lift it, but that is a Stage-1 re-open, not a P10 re-run; a pretrained-backbone comparison (out of
  scope — OURS *replaces* the pretrained backbone).
- **→ the decision record ([`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md)):** the S14 close-out delta
  (the founding bet's two halves banked separately; the cadence cost-frontier; the noise arc cashed + residual named).

---

*Deep story + every figure:* [`phase10-report.md`](phase10-report.md). *Numbers:* [`RESULTS.md`](RESULTS.md). *The
professor pack:* [`professor-brief.md`](professor-brief.md). *Up:* [Stage-2 map](../stage2-design.md) · *prev:*
[Phase 9 — freeze](../phase9/README.md) · *next:* the Stage-2 close-out ([`../stage2-report.md`](../stage2-report.md)) →
the analog-realism layer, and beyond the numbered phases, the north star.
