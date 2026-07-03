# Phase 10 — the validation / showcase: racing the frozen object against a fair BP+replay (the deep story)

> The full narrative of the **fourth and last Stage-2 phase** (P7 readout · P8 economy+cost · P9 close/freeze · **P10
> validate/showcase**). Phase 9 locked the complete two-brain neocortex object; **Phase 10 raced it — untouched — against
> a fair, budgeted, tuned experience-replay backprop learner** across the continual gauntlet, and delivered an honest
> **Pareto** close-out. It *measured*; it tuned nothing. The one discipline the whole phase's honesty rides on:
> **freeze in P9, judge in P10** — the object was locked *before any baseline number existed*, and the verdict shapes were
> pinned **BLIND** (`design.md` §2.3) before the racer ran. Ran 2026-07-03, P10.0→P10.6, 5 seeds `[42,137,271,314,1729]`,
> all 14 guards bit-exact; the frozen grid-4 object reproduced the P9 freeze arrays bit-for-bit.
>
> Front door: [`README.md`](README.md). Numbers: [`RESULTS.md`](RESULTS.md). Per-rung cards:
> [`expK/experiment-K.md`](exp0/experiment-0.md). Spec: [`design.md`](design.md); contract: [`result-format.md`](result-format.md).
> The professor pack: [`professor-brief.md`](professor-brief.md). The object it races: [`../phase9/README.md`](../phase9/README.md).

---

## 1 · What Phase 10 was — the thesis defense

Seven phases characterized *pieces*. Phase 1 found a forgetting-robust continual learner; Phase 4 mapped it as a
substrate-native continual learner, not a static-accuracy competitor; Phases 5–6 finished and noise-hardened the cheap
SCFF brain; Phases 7–8 built the gradient-free namer and metered the two-brain economy; Phase 9 tuned the lifelong
maintenance loop against *internal signals only* and **froze the whole object** at a commit hash. What was never done —
the debt Phases 4, 8, and 9 each flagged and passed forward — is the **existential test**: every continual *accuracy*
win to date was measured against **naive online backprop with no replay.** That is a strawman, and it is the first thing
an outside reviewer attacks.

The founding bet is a whole-system claim: *"an 80/20 forward-only continual learner that beats backprop's economics **and**
accuracy."* Phase 8 settled the **economics** half (OURS ≈ half the energy of BP+replay on the same substrate; 15× vs
GD-on-digital). Phase 10 is the phase that races the **accuracy** half — and it does so against the *strong* opponent the
literature demands: under a matched **FLOPs/sample + memory-bytes** budget, a well-tuned **experience replay (ER)** is the
baseline that beats the fancy CL methods (Prabhu CVPR'23; Ghunaim CVPR'23). Until the frozen object races a **strong,
budgeted ER** on accuracy, the headline is *supported, not validated.* Phase 10 measures it — and reports whatever the
numbers say, **win or lose.**

**The reframe (the kickoff decision): present the frozen object as a cadence cost-frontier *family*.** Rather than
racing a single point, the object is shown as a family of operating points along its one runtime cost dial — the **sleep
cadence** (`grid-N` = sleep every N segments), `grid ∈ {4,5,6,8,16}` (+ **grid-12**, added post-close by the §10
extension to make the Tier-2 break's shape legible). **Every *learned* part is frozen** (the SCFF bulk, the SLDA namer,
the DDM gate, the CBRS eviction, the proto-reanchor defense); only the sleep *interval* changes. **grid-4 is the
committed frozen headline and is never swapped** — the family is a *declared, transparent cost axis* (the x of every
Pareto plot), not a knob turned to beat the baseline. This matters beyond P10: the cadence *is* the sleep mechanism, so
how the family scores shapes the future of the sleep design.

---

## 2 · The disciplines that make it honest

Phase 9's rule was *internal-signals-only* — never look at the P10 baseline while tuning. Phase 10 is the phase that
*does* consult the external baseline; that is its whole job. So the honesty inverts and moves to a different cut, and four
disciplines carry it:

1. **Freeze in P9, judge in P10.** The object was locked before any baseline number existed. The `freeze_content_guard`
   asserts the frozen-knob **content manifest** (`COMMITTED_LOOP` + `cadence_every=4` + `HEAD="slda"` + the SLDA/cell
   config) **and** that the grid-4 arm reproduces the P9 freeze arrays **bit-for-bit** (`59d2720` is a provenance label,
   not a runtime git check). Touching a single *learned* knob to improve a comparison would invalidate the fight; the only
   dial that moves is the declared cadence cost axis.
2. **The fair racer.** ER is byte-matched to OURS's LUT (196 800 B) and **tuned on a disjoint seed** (7 ∉ the raced set)
   with its own val split — so the raced seeds are never consumed during tuning. Both an **ER-budget** (throttled to
   OURS's FLOPs) and an **ER-strong** (its own best config) are built; A-GEM (real one-projection grad-handle), DER++
   (logit buffer + distillation), GDumb (from-scratch retrain at eval, the cost-pathological control), and naive-BP (the
   floor) populate the field. **The racer's shape is its own uncapped best choice** — which is precisely why the
   same-substrate energy cut goes *against* OURS (threat h, reported not hidden).
3. **The load-bearing energy cut is same-substrate.** `E(OURS-analog) < E(GD-digital)` is ~guaranteed by the CIM meter
   *before any run* (the crossbar prices in-memory MACs near-zero by construction). So the *contestable* cut is
   **`E(OURS-digital)` vs `E(ER-digital)`** — the algorithm win, on the same digital substrate. The analog factor is a
   **meter-structural floor** overlay, never the claim. The meter is **behavioral** (relative-pJ, ADC-centred, NOT SPICE).
4. **The spine.** Every noise read is a **direction** (retention under a coherent class-axis shift), never a per-sample
   magnitude. density ≠ class — the recurring fault, cashed one last time on the assembled object.

All 14 guards (8 carried from P8/P9 + `fair_budget` · `freeze_content` · `cadence_family` · `gauntlet_data` ·
`noise_holdout` · `substrate_identity`) were green on every rung.

---

## 3 · Phase by phase — the seven rungs

### P10.0 — the bench: the fair racer + the gauntlet + the six guards *(no verdict — a build)*

The bulk of P10.0 was **real new code**, not carries: the `ContinualBP` learners (ER/A-GEM/DER++/GDumb/naive on the
gradient MLP, made online with a replay buffer), the `fair_budget_meter` (a byte counter + a per-sample FLOPs counter
exposing the MAC counts inside the energy meter), the native domain-IL `make_gauntlet_stream`, the `cadence_family_runner`,
the `held_out_noise_battery`, and `joint_bp_ceiling`. The A-GEM/DER++ descope was decided at P10.0 (time-boxed) and came
back **False** — the full roster is real code.

The bench came back **all-green (14/14)**, and it surfaced the one honest tension the whole phase then measured: OURS's
**FLOPs/sample (96 938) is *higher* than ER-strong's (65 268)** — OURS forwards a 12-layer unsupervised bulk on every
step. This was **pre-registered**: it means the same-substrate (digital) energy cut is genuinely contestable — the analog
crossbar is exactly what prices those bulk MACs near-zero (R1's point). ER-strong tuned on the disjoint seed 7 to
`dims [40,49,49,49,10] / lr 1e-3 / replay 64` (tune-AA 0.540); its replay buffer byte-matched OURS's LUT exactly. Bench
green → proceed. *(A broken bench poisons every verdict — this is the STOP gate, and it passed.)*

### P10.1 — the existential fight → *accuracy TIE, a decisive continual-safety WIN, energy substrate-realized* 🔥

The load-bearing rung: OURS(grid-4) vs the tuned ER-strong + the full field, on the lifelong synthetic home (the class-IL
leg — the Split-X complement the research names, so the gauntlet stays purely domain-IL).

![P10.1 — the existential fight](exp1/figs_p10_1/FIGHT.png)
*The fight. **Left** — accuracy: OURS(grid-4) **0.494** and ER-strong **0.498** sit inside the δ=0.02 band (a tie; OURS
wins 3/5 seeds), both far above the field (ER-budget 0.376, A-GEM 0.320, DER++ 0.360, naive 0.308) and well below the
offline joint-BP ceiling (0.870, dash-dot); the §10 **OURS grid-5** bar beside the headline shows the family's cheaper
Tier-1 point riding δ-equal (0.495). **Right** — energy per substrate: OURS's 12-layer bulk costs more than the small
tuned ER on the digital substrate (grid-5 trims ~11% off grid-4), and the gap collapses on the analog substrate — the
whole "why analog" in one pair of bars. (n=5, continual home; behavioral ADC-centred meter.)*

The raw accuracy read is a **tie within δ** — exactly the *live accuracy-loss branch* the plan pre-registered ("on a
~0.49-AA synthetic home a budgeted ER may well edge us"). But the **corrected worst-pre-sleep BWT reveals the real
story.** The final-BWT had masked it — replay recovers by stream-end — but on the honest worst-mid-stream read (the P9
convention, applied to *every* learner, R6), **OURS forgets ~10× less than the tuned ER**: worst-BWT **−0.028 vs ER's
−0.272.** That is the substrate-native continual edge, visible even on the home the raw AA called a tie.

The energy is the honest **R1** outcome. Same-substrate (digital) algorithm cut: `E(OURS-digital)` 3.46e8 vs
`E(ER-digital)` 2.25e8 → OURS is **1.54× more expensive.** The 12-layer bulk is not free even forward-only against a
small tuned ER. The energy win is **substrate-realized**: OURS-analog 6.70e7 is **3.35× cheaper** than ER-on-digital
2.25e8 — the analog crossbar, not the algorithm. So P10.1 banks as: **accuracy competitive (tie)**, **continual-safety
win (10× safer)**, **algorithm-energy not a same-substrate win**, **total energy substrate-realized.** AAA favors ER
(0.503 vs 0.392) — the sleep-cadence anytime tax, reported beside AA. The two halves are banked separately from here on.

### P10.2 — the cadence frontier → *grid-4 the headline, grid-5 the cheaper rep, the Tier-2 break has TWO cliffs*

The frozen object as a cost-frontier family (six points after the §10 extension added grid-12) — only the sleep interval
varies; grid-4 reproduces the P9 freeze bit-for-bit (the guard's core check).

![P10.2 — the cadence cost-frontier family](exp2/figs_p10_2/CADENCE_FRONTIER.png)
*The frontier. Six operating points on (accuracy × energy), worst-BWT the marker read. **grid-4** (⭐, committed
headline) anchors the safe/dense end (worst-BWT −0.028, energy 6.70e7); **grid-5** is the δ-eligible Tier-1 showcase rep
(−0.039, within δ of grid-4, IQR-disjointly cheaper at 5.99e7); **grid-6** fails the δ-BWT gate (−0.087); the Tier-2 arms
(orange) make the scaling break legible — **grid-8** forgets (−0.317, fails the veto), **grid-12** (§10) still forgets
(−0.339) yet *holds* final AA (0.496 at 4.28e7), and **grid-16** drops accuracy (0.458, over-sparse). Energy is monotone
with cadence density (6.70e7 → 3.99e7); GD-share falls 0.178 → 0.107. (n=5.)*

grid-4 is the committed headline, **never swapped, always plotted.** The Tier-1 *showcase rep* (for the 3-line
visualization only) is **grid-5** — the only δ-worst-BWT-eligible candidate; grid-6's −0.087 is > δ worse than grid-4's
−0.028, so it fails the gate (this closes the R2 "cadence-swap loophole" — a cheaper grid must earn its place, it is not
free). The Tier-2 break is confirmed on **both** axes: grid-8 fails the *veto* (forgetting), grid-16 fails *AA-held*
(over-consolidation gap). The family is a declared cost axis — no per-dataset best grid is ever passed off as "OURS."

**The §10 grid-12 finding — the break is a plateau + cliff, not a smooth decay.** The author read the AA-vs-energy trend
as roughly exponential and asked for the missing 8→16 point; grid-12 (never run before, not even in P9.5) shows the
opposite shape. **Final AA stays flat all the way down to grid-12** (0.496 — statistically grid-4's 0.494) because even 8
sleeps still cover the stream's revisits on *average*; it **cliffs only at grid-16** (0.458, 6 sleeps). Meanwhile the
**safety axis broke a full tier earlier** — the worst pre-sleep trough plunges at 6→8 (−0.087 → −0.317) and stays broken
at grid-12 (−0.339, where even the same-cadence oracle sits at −0.461, so it is pure sparsity, not gate timing). The
frontier's honest shape: **worst-case safety degrades a full tier before average accuracy does** — which is exactly why
the freeze committed the knee at grid-4 on the worst-point read, not the final-AA read.

### P10.3 — the multi-domain gauntlet → *the money figure: steadier retention across 5 worlds at substrate-realized cost*

Five native domain-IL digit worlds — identity, permuted, rotated, covariate, noised — all projected to the shared 40-D
bulk input with the one pinned projection, one shared head, every learner consuming the bit-identical stream. A
construction note worth stating: the frozen loop's replay probe had to be made **cross-domain** (matching ER's
cross-domain reservoir) for a *fair* domain-IL test — the domain-0-only probe was an artifact that starved the namer of
the shifted domains. With both learners' replay spanning domains, the fight is honest.

![P10.3 — the gauntlet money figure](exp3/figs_p10_3/GAUNTLET.png)
*The money figure (twin panel). **Top** — worst-pre-sleep all-prev retention across the 5-domain stream: OURS(grid-4)
holds **0.490** at its worst point while ER-strong dips to **0.350** mid-stream (then recovers by the end); sleep-position
ticks and domain-boundary lines overlaid. **Bottom** — cumulative energy: OURS's line runs above ER's on the digital
substrate (the deep bulk) and below it on analog. The Tier-2 arms (grid-8/16) trade retention for energy. (n=5, native
domain-IL digits; worst-pre-sleep read, ER at the same convention.)*

The honest continual read — **worst-point all-prev retention** — favors OURS decisively: **0.490 vs ER's 0.350**, with a
steadier anytime accuracy (**AAA 0.519 vs 0.433**). At the *final* checkpoint the two are within δ (OURS 0.490 vs ER
0.504, ER edging 4/5 — the sleep loop's worst point is mid-stream, ER's is smoothed by stream-end), and the result is
**order-robust** (reversed-order AA Δ −0.014). The energy is again substrate-realized: same-substrate 1.47× more, chip vs
conventional GD 3.5× cheaper. The SUBSTRATE 2×2 decomposes it:

![P10.3 — the substrate 2×2, re-metered over the gauntlet](exp3/figs_p10_3/SUBSTRATE.png)
*Why analog, re-metered across the gauntlet. The 2×2 {OURS,GD}×{analog,digital}: the chip (OURS-analog, hero-ringed) runs
~3.5× under conventional GD-on-digital, and the win factors into a substrate term (the analog crossbar) × an algorithm
term (the 80/20). The algorithm term does **not** favor OURS same-substrate — the substrate carries the total. (Behavioral
meter, params in the manifest.)*

The gauntlet's **tuning asymmetry is stated blind**: OURS runs a *frozen-config* backbone (its claim is generality), ER
gets its *own best per-domain config* (steel-manned). So OURS's retention win is *despite* the handicap — a frozen
substrate holding steadier than a tuned end-to-end learner across 5 shifting worlds. This is the showcase's continual
core: **plasticity across domains without catastrophic forgetting, at substrate-realized cost.**

**The §10 GAUNTLET-STREAM view — the mechanism, batch by batch.** The per-domain money figure reads at checkpoints; the
extension adds the training-curve view the author asked for — every batch, two measurements per model (the **live-batch**
prequential accuracy and the **seen-so-far** all-domain accuracy) plus the **exact** prefix-priced cumulative energy. It
is a *guarded replay* of the committed run, not a new arm (cell pass bit-exact vs the cache; head states bit-exact vs the
committed error trace; energy endpoint equal to the committed meter total — any divergence aborts).

![P10.3 §10 — the per-batch stream view](exp3/figs_p10_3/GAUNTLET_STREAM.png)
*The in-domain vs domain-switch activity. **Top** — ER's seen-so-far line (thick magenta) **crashes at every domain onset
and re-climbs** — the saw-tooth of an end-to-end learner re-fitting its representation to each new world — while
OURS's (thick teal) rides near-flat ~0.5 across all five; the thin live-batch lines show it directly: ER dives to ~0.1 on
arrival batches (live mean 0.273) while OURS barely moves (0.469). **Bottom** — cumulative energy at batch resolution:
OURS is a sleep **staircase** (each consolidation a visible jump), ER a smooth every-step ramp; OURS stays the pricier
same-substrate line (the 1.47×), now exact per batch. (n=5, median; IQR band on the seen-so-far lines.)*

The stream view is the money figure's mechanism made visible: **ER buys its marginally higher final AA with a
crash-and-relearn cycle at every domain switch; OURS's forward-only bulk + sleep loop holds both the live and the
remembered read near-flat.** The steadiness is the product.

### P10.4 — the noise showcase → *OURS ≫ BP+replay on every held-out channel; a small residual named*

The Phase-6 noise arc, cashed on the assembled object under a **margin-disjoint held-out battery** (directional RMS 2.5
vs P9.4's 1.5; ADC 3-bit vs 2-bit; + a nuisance-dim channel) — a genuinely *disjoint* operating point of the transducer
model. The read is **directional retention** (accuracy under the channel / clean) — a direction, the spine.

![P10.4 — the noise showcase](exp4/figs_p10_4/NOISE_SHOWCASE.png)
*The noise showcase. Directional retention per held-out environment, OURS-hardened vs BP+replay vs naive. OURS holds
**0.92–1.10 on every channel** while BP+replay collapses (iid 0.61, directional 0.22, adc3b 0.30, nuisance 0.47); OURS is
invariant to the layernorm-removable nuisance covariate (1.000) and *improves* under iid noise (1.095, from the
noise-augmented training objective). naive incidentally ties OURS on directional/adc3b (a shallow raw-input classifier)
but collapses on nuisance — the load-bearing comparison is vs the fair continual opponent, BP+replay. (n=5, held-out,
margin-disjoint; the read is a direction, not a magnitude.)*

The verdict is a **clean win over the fair opponent** — OURS-hardened ≫ BP+replay on **every** held-out channel — honestly
scoped: because the battery is *re-parameterized*, not structurally novel, the claim is the honest **"confirms P9.4 at new
levels,"** not a fresh "payoff." A small **directional/ADC residual** persists (0.978 / 0.923, just > δ) → **named → the
analog-realism (SPICE/PVT) layer**, exactly the Phase-6 "scoped-YES → Stage-2 read-side" handoff, now cashed on the whole
object and its remainder named rather than papered over.

### P10.5 — A5 natural multi-class → *a tuned ER beats OURS on static digits; OURS is a continual, not static, learner*

The recognizable-data confirm: 8×8 digits projected to the shared 40-D input, class-incremental, against the same field.

![P10.5 — the fight on natural digits](exp5/figs_p10_5/FIGHT.png)
*The natural confirm. On recognizable digits ER-strong **beats OURS by +0.071** (0.950 vs 0.879, > δ, 5/5) and forgets
slightly less (worst-BWT −0.019 vs −0.051); OURS beats naive (0.866) and trails ER-budget (0.922). The joint ceiling
(0.982) is near-saturated — digits are easy. (n=5, natural class-IL.)*

This is the honest *direction* of the synthetic-overstatement threat: the hard synthetic home **understated** ER's edge
(both sat near-Bayes-hard at ~0.49), while on easy natural data ER's flexible MLP capacity + replay pull ahead. Crucially,
**OURS's continual-safety edge — decisive on the lifelong P10.1 stream and the 5-domain gauntlet — does NOT appear here**,
because a short easy CI stream does not stress forgetting (ER's own worst-BWT is only −0.019 — there is nothing for the
sleep loop to out-protect). So the "beats backprop *accuracy*" claim is **not supported** on final/static accuracy; OURS's
accuracy value is **continual stability on hard/long/multi-domain streams** — exactly the P4 identity. The static gap is
flagged to a future draft (a convolutional / larger bulk would lift it — a Stage-1 re-open, not a P10 re-run).

### P10.6 — the Pareto verdict + the close-out → *an honest Pareto; the wins live off the acc×energy axis*

The integration rung: assemble the (accuracy × energy) frontier across the OURS-family + the field, and bank the two
halves separately.

![P10.6 — the Pareto verdict](exp6/figs_p10_6/PARETO.png)
*The verdict. On (final AA × analog energy) the non-dominated staircase is **{er_strong, gdumb}** — OURS(grid-4,
hero-ringed) is **dominated** (a small tuned ER has higher accuracy *and* lower energy, and GDumb anchors the cheap
corner, cost-pathologically). The §10 **full-family money line** {g4 ⭐, g5, g6, g8, g12, g16} sweeps the top of the
scatter — a near-flat ~0.49-AA line from 6.7e7 down to 4.3e7 pJ, with the single g16 accuracy-cliff outlier — the model's
whole operating range in one stroke; what the scatter cannot show (g8/g12's broken worst-case safety) is why grid-4 is
the headline and not the cheapest point. OURS's genuine wins are on the axes this scatter does not have: worst-case
continual safety, noise robustness, and the substrate floor. (n=5; GDumb annotated — it retrains from scratch at eval,
not an energy competitor.)*

On the (accuracy × energy) Pareto a small tuned ER **dominates** OURS — because OURS pays for a 12-layer unsupervised bulk
every step, and that bulk is affordable only on the analog crossbar (near-free MACs), which is the whole "why analog."
OURS's genuine wins come from the sleep-consolidated loop (steady worst-case retention) and the noise-augmented + layernorm
+ proto-reanchor stack (noise survival) — capabilities the acc×energy Pareto simply does not have an axis for. The
close-out banks the two halves separately: **economics = substrate-realized** (validated as a *chip* claim, not an
algorithm claim); **accuracy = competitive-on-home / trails-on-static / wins-on-continual-safety.**

---

## 4 · The honest map — where OURS wins, ties, loses

| axis | OURS | best fair opponent | verdict | number |
| --- | --- | --- | --- | --- |
| final accuracy (continual synthetic home) | 0.494 | ER-strong 0.498 | **tie** | +0.004 (< δ) |
| final accuracy (natural digits, static-ish) | 0.879 | ER-strong 0.950 | **loss** | −0.071 (not a static competitor) |
| worst-pre-sleep BWT (lifelong) | **−0.028** | ER-strong −0.272 | **win** | ≈10× safer |
| worst-point all-prev retention (gauntlet) | **0.490** | ER-strong 0.350 | **win** | +0.140 (AAA 0.519 vs 0.433) |
| noise robustness (held-out, vs BP) | 0.92–1.10 | BP+replay 0.23–0.61 | **win** | every channel |
| energy — algorithm (same digital substrate) | 3.46e8 | ER-strong 2.25e8 | **loss** | 1.54× (the deep bulk) |
| energy — chip vs conventional GD (total) | 6.70e7 (analog) | ER-digital 2.25e8 | **win** | 3.4× (substrate-realized floor) |

The frozen object is a **competitive, decisively safer, and far more noise-robust continual learner whose energy advantage
over conventional GD is substrate-realized** — a *substrate-native continual learner*, not a static-accuracy or
same-substrate-energy point-winner. Precisely the identity Phase 4 named, now tested against the strongest fair opponent
and refined, not inflated.

---

## 5 · The founding bet, banked as two halves (S14)

> **Bet:** *"an 80/20 forward-only continual learner that beats backprop's economics **and** accuracy."*

- **ECONOMICS — substrate-realized (the honest R1 outcome).** On the same digital substrate the 80/20 algorithm is **1.5×
  *more*** than a small tuned ER — the algorithm alone does not win the energy race against an efficient discriminative
  net. The **chip (analog crossbar) is 3.4–3.5× cheaper** than that same GD model on a conventional digital accelerator.
  "Less energy than modern GD" holds **for the chip**, and the win is the **substrate** (a meter-structural floor, reported
  plainly, never rested on as the contestable claim).
- **ACCURACY — competitive on the home, a static trail, a continual-stability WIN.** OURS ties the tuned ER on the hard
  continual home (0.494 vs 0.498) and trails on easy static digits (0.879 vs 0.950). But on the honest worst-case
  continual read it is the **safest of the whole field** — ~10× less worst-point forgetting (BWT −0.028 vs −0.272),
  steadier worst-point retention across 5 domains (0.490 vs 0.350). The "beats backprop accuracy" claim is **not
  supported** on static accuracy; OURS's edge is *lifelong stability*, and it is real.
- **NOISE — a clean win.** Under the held-out battery OURS holds 0.92–1.10 on every channel while BP+replay collapses to
  0.23–0.61. A small directional/ADC residual is **named → the device-physics layer.**

**New supporting decisions banked:** the cadence cost-frontier `{4,5,6,8,12,16}` (grid-4 headline, no swap; grid-5 the
δ-eligible rep; the §10 grid-12 point gives the Tier-2 break its **two-cliff shape** — safety falls at 6→8, final AA only
at 12→16) and the characterized SCFF:Namer ratio (GD-share 0.107–0.178 ≤ 0.25). The founding bet is **refined, not
inflated** — the honest-science outcome the project's whole method is built to produce.

---

## 6 · Hand-offs — what Phase 10 names and defers

- **→ the analog-realism layer (SPICE / PVT), named:** the small directional/ADC residual P10.4 shows the read-side
  defense cannot fully reach; the absolute-Joule and PVT layer the behavioral meter cannot give.
- **→ a future draft (flagged, not executed):** the static-accuracy gap on natural data (P10.5) — a *convolutional* or
  larger bulk would lift it, but that is a Stage-1 re-open, not a P10 re-run; a pretrained-backbone comparison is out of
  scope (OURS *replaces* the off-chip pretrained backbone — the fair comparator is BP-from-scratch + replay, which is
  exactly what was raced).
- **→ the professor pack ([`professor-brief.md`](professor-brief.md)):** the one-page brief for the author's meeting — the
  object in a paragraph, the GAUNTLET / PARETO / SUBSTRATE figures, the two-halves verdict, and the two honesty lines a
  reviewer tests first (*the analog factor is a meter-structural floor; the load-bearing energy win is same-substrate*).
- **→ the decision record ([`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md)):** the **S14** close-out delta,
  banked the way S10–S13 were.
- **→ the Stage-2 close-out ([`../stage2-report.md`](../stage2-report.md)):** rewritten from "living / in-progress" to a
  closed Stage-2 arc.
- **→ the north star (deliberately not specced):** the cosine spine-pure head (P7) and the better-than-confidence exit
  (P5) survive as a *tie-break bias* only; P10 adds no recurrence. Simple intelligence first.

---

## 7 · Honest scope + threats-to-validity

- **The meter is behavioral** (ADC-centred macro-model, relative-pJ, NeuroSim/ISAAC/PUMA-level, params + citations
  logged), **not SPICE.** The **analog energy factor is meter-structural** — never the contestable claim; the load-bearing
  energy cut is same-substrate.
- **The fair fight depends on the ER budget + tuning.** A crippled ER makes the win vacuous — so ER was FLOPs+byte-matched
  *and* tuned strong on a disjoint seed; both budget and strong points are reported. The racer's shape is its own uncapped
  best choice (threat h) — which is *why* the same-substrate energy cut goes against OURS, reported not hidden.
- **The gauntlet depends on the domain set + order + the frozen-config-vs-per-domain-tuning asymmetry.** All three are
  stated; the reversed-order control (grid-4 + ER-strong, 5 seeds) was run and is order-robust (AA Δ −0.014).
- **Synthetic overstates static gaps** — the natural digits (P10.5) are the honest read, and they *reveal* ER's
  static-accuracy edge the hard synthetic home masked.
- **The noise battery is a margin-disjoint operating point of the same transducer model** — a genuinely-novel channel
  earns "payoff," a re-parameterized one earns "confirms"; the read is a **direction**, not a magnitude.
- **Accuracy is substrate-independent** (guarded `pred_analog == pred_digital` bit-for-bit on every NoiseModel-off cell —
  P10.4's noise arms the declared exception) — the substrate axis lives only in energy, never double-counted in accuracy.
- **GDumb is cost-pathological** (retrains from scratch at eval) — reported on the accuracy axis, annotated on the energy
  axis, never used to inflate the Pareto.
- **Behavioral simulation only** — numpy ideal floats + Phase-6's behavioral analog-noise model; small, partly synthetic
  tasks (the continual home, digits, the transformed-digit gauntlet). No SPICE, no device physics, no fabrication.

---

## Reading guide

**For the verdict:** [`README.md`](README.md) (the front door). **For the numbers:** [`RESULTS.md`](RESULTS.md) (the
scalar ledger). **For the professor meeting:** [`professor-brief.md`](professor-brief.md). **For each rung's full story:**
the [`expK/experiment-K.md`](exp0/experiment-0.md) cards. **For the plan and the contract:** [`design.md`](design.md) +
[`result-format.md`](result-format.md). **For the object it races:** [`../phase9/README.md`](../phase9/README.md) and the
whole model in one file, [`../phase9-final-architecture.md`](../phase9-final-architecture.md). Every figure regenerates
from saved data: `python plot_p10.py <run-dir>` reads `arrays.npz` and redraws — a figure you can't regenerate is a
screenshot, not a result.

*Up:* [the Stage-2 arc](../stage2-report.md) · *prev:* [Phase 9 — close & freeze](../phase9/README.md) · *next:* the
analog-realism (SPICE / PVT) layer, and beyond the numbered phases, the recurrent lifelong brain — the north star.
