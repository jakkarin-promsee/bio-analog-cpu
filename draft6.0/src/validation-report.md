# The validation — the frozen object on trial (Phases 10–11, the report)

> The third volume of the draft-6.0 report set, and the one where **nothing is decided and everything is measured.**
> [Stage 1](stage1-report.md) built the cheap SCFF brain (Phases 1–6); [Stage 2](stage2-report.md) built the
> gradient-free namer and its economy and **froze the complete two-brain object at Phase 9** (commit `59d2720`).
> This volume is the judgment: **Phase 10** races the frozen object — untouched — against a fair, budgeted, tuned
> BP+replay opponent on the home bench and delivers an honest **Pareto** verdict (**S14**); **Phase 11** takes the
> same frozen object off the toy bench onto **eight real arenas and scale** and draws the honest **LIMIT-MAP** —
> every win, tie, loss, and floor (**S15**). Nothing in either phase tunes a learned knob; the only things that move
> are the declared cost axis (the sleep cadence) and a pre-registered scaling rule. The posture, in the author's own
> words: *"if everything fails, let them attack my math, not my missing evidence."*
>
> The two phase reports this volume tells as one arc: [Phase 10](phase10/phase10-report.md) ·
> [Phase 11](phase11/phase11-report.md). Terms and metrics: [`ref-report/`](ref-report/README.md). The object under
> trial, in one self-contained file: [`phase9-final-architecture.md`](phase9-final-architecture.md). The professor
> pack: [`phase10/professor-brief.md`](phase10/professor-brief.md).

---

## 1 · What is on trial, and how the trial is run

**The object.** One analog chip, two brains, frozen. A cheap **SCFF bulk** (~80%) — 12 forward-only self-contrastive
layers (`NoiseAugContrast`, the Stage-1 committed cell) — organizes the world *unsupervised*; a tiny **closed-form
namer** (SLDA, ~20%, no gradient) reads those features and puts our labels on them; a **DDM drift gate** fires the
namer only when the cheap path stalls; a **sleep loop** (grid-4 cadence over a bounded CBRS prototype LUT, with
proto-reanchor) consolidates. Phase 9 tuned this loop against *internal signals only* and locked it. From that moment
the object **touched no knob** — the `freeze_content` guard asserts, on every rung of both phases, that the grid-4
arm reproduces the P9 freeze arrays **bit-for-bit.**

**The claim on trial.** The founding bet is a whole-system claim: *"an 80/20 forward-only continual learner that
beats backprop's economics **and** accuracy."* Every continual accuracy win through Phase 9 was measured against
**naive online backprop with no replay** — a strawman, and the first thing an outside reviewer attacks. The trial
therefore runs against the opponent the literature demands: under a matched FLOPs/sample + memory-bytes budget, a
well-tuned **experience replay (ER)** is the strong baseline that beats the fancy CL methods (Prabhu CVPR'23; Ghunaim
CVPR'23).

**The two trials.**

- **Phase 10 — the honest race (§2).** The frozen object vs the tuned, budgeted ER field on the home bench: the
  existential accuracy fight, the cadence cost-frontier, the five-world gauntlet, the held-out noise battery, natural
  digits, and the Pareto verdict. *Does the founding bet survive a fair opponent?* → **S14.**
- **Phase 11 — the limit map (§4).** The same frozen object on real data (MNIST/Fashion/CIFAR-gray, four real drift
  streams, a 30-way cross-dataset stream) and scale (width/depth/input-dim/class-count). *Does anything survive
  contact with the real world — and where exactly does it stop?* → **S15.**

**The disciplines shared by both** (what makes a showcase a *validation*):

1. **Freeze first, judge second.** The object was locked before any baseline number existed; verdict shapes were
   pinned **BLIND** in each phase's `design.md` before the racer ran. Touching a learned knob to improve a comparison
   would invalidate the fight.
2. **A steel-manned opponent.** ER is byte-matched to OURS's LUT and tuned on a **disjoint seed** (7, never raced) —
   in Phase 11, re-tuned **per arena** while OURS stays frozen. The asymmetry runs *against* the home team on
   purpose: when the frozen recipe still wins, it counts.
3. **The load-bearing energy cut is same-substrate.** `E(OURS-analog) < E(GD-digital)` is near-guaranteed by the CIM
   meter before any run; the *contestable* cut is `E(OURS-digital)` vs `E(ER-digital)` — the algorithm alone, on the
   same digital substrate. The analog factor is a **meter-structural floor** overlay, never the claim. The meter is
   behavioral (relative-pJ, ADC-centred), **not SPICE.**
4. **Losses ship.** A loss is reported with the same rigor as a win; an uninformative cell is marked FLOOR, not
   spun. The map, not the highlight reel, is the deliverable.

---

## 2 · Trial one — the honest race (Phase 10, S14)

*Ran 2026-07-03, P10.0→P10.6 + a four-round §10 extension; 5 seeds `[42,137,271,314,1729]`; all 14 guards bit-exact.*

**The reframe that opens the phase: the frozen object is presented as a cadence cost-frontier *family*.** Rather than
racing a single point, the object is shown along its one runtime cost dial — the **sleep cadence** (`grid-N` = sleep
every N segments), `grid ∈ {4,5,6,8,16}` plus the §10 probes {7,12,13,14,15}. Every *learned* part is frozen; only
the sleep interval changes. **grid-4 is the committed headline and is never swapped** — the family is a declared,
transparent cost axis (the x of every Pareto plot), not a knob turned to beat the baseline.

### 2.0 The bench (P10.0) — the fair racer, built for real

The rung is a build: the `ContinualBP` learners (ER / A-GEM / DER++ / GDumb / naive, all real code — the time-boxed
descope came back False), the fair-budget meter (bytes + per-sample FLOPs), the native domain-IL gauntlet stream, the
cadence-family runner, the held-out noise battery, and the joint-BP ceiling. ER-strong tuned on the disjoint seed 7
(`dims [40,49,49,49,10] / lr 1e-3 / replay 64`); its buffer byte-matched to OURS's LUT (196 800 B). The bench came
back **all-green (14/14)** and surfaced the one honest tension the whole phase then measures, **pre-registered**:
OURS's FLOPs/sample (96 938) is *higher* than ER-strong's (65 268) — OURS forwards a 12-layer unsupervised bulk on
every step, so the same-substrate energy cut is genuinely contestable.

### 2.1 The existential fight (P10.1) — accuracy TIE · continual-safety WIN · energy substrate-realized 🔥

The load-bearing rung: OURS(grid-4) vs the tuned ER-strong + the full field on the lifelong synthetic home.

![P10.1 — the existential fight](phase10/exp1/figs_p10_1/FIGHT.png)
*The fight. **Left** — accuracy: OURS(grid-4) **0.494** and ER-strong **0.498** sit inside the δ=0.02 band (a tie;
OURS wins 3/5 seeds), both far above the field (ER-budget 0.376, A-GEM 0.320, DER++ 0.360, naive 0.308) and well
below the offline joint-BP ceiling (0.870). **Right** — energy per substrate: OURS's 12-layer bulk costs more than
the small tuned ER on the digital substrate, and the gap collapses on the analog substrate — the whole "why analog"
in one pair of bars. (n=5; behavioral ADC-centred meter.)*

The raw accuracy read is a **tie within δ** — exactly the live accuracy-loss branch the plan pre-registered. But the
**worst-pre-sleep BWT reveals the real story**, which the final-BWT had masked (replay recovers by stream-end): on
the honest worst-mid-stream read, applied to *every* learner, **OURS forgets ~10× less than the tuned ER** —
worst-BWT **−0.028 vs −0.272.** The energy is the honest R1 outcome: same-substrate (digital) OURS is **1.54× more
expensive** (3.46e8 vs 2.25e8 — the 12-layer bulk is not free even forward-only); the win is **substrate-realized**
(OURS-analog 6.70e7 is **3.35× cheaper** than ER-on-digital). AAA favors ER (0.503 vs 0.392 — the sleep-cadence
anytime tax, reported beside AA). From here the bet's two halves are banked separately.

### 2.2 The cadence frontier (P10.2) — a plateau + two localized cliffs

![P10.2 — the cadence cost-frontier family](phase10/exp2/figs_p10_2/CADENCE_FRONTIER.png)
*Ten operating points on (accuracy × energy), worst-BWT in the right panel. **grid-4** (⭐, committed headline)
anchors the safe/dense end (worst-BWT −0.028, 6.70e7 pJ); **grid-5** is the only δ-eligible cheaper rep (−0.039,
IQR-disjointly cheaper at 5.99e7); **grid-6** fails the δ-BWT gate (−0.087 — the safety edge); **grid-7** is the
plunge (−0.322); the sparse arms stay safety-broken (−0.32…−0.44) while final AA plateaus at 0.494–0.496 through
grid-15 and cliffs only at 15→16 (0.458). GD-share falls 0.178 → 0.107. (n=5.)*

The §10 probes gave the break its true shape — **not a smooth decay but a plateau with two localized cliffs.** The
*safety* axis breaks in two steps: a δ-edge at grid-6, then the plunge at grid-7, where the mid-interval pre-sleep
troughs outrun the consolidations. The *accuracy* axis plateaus through grid-15 and cliffs exactly at 15→16 — and
the mechanism read is the sweep's sharpest: **grid-15 and grid-16 sleep the same number of times at the same
energy — only the positions differ** — so at ~6 sleeps the outcome stops being count-limited and becomes
**timing-sensitive.** The frontier's honest shape: **worst-case safety degrades a full tier before average accuracy
does** — precisely why the freeze committed grid-4 on the worst-point read, not the final-AA read. (This closes the
"cadence-swap loophole": a cheaper grid must *earn* δ-eligibility; no per-dataset best grid is ever passed off as
"OURS.")

### 2.3 The multi-domain gauntlet (P10.3) — the money figure, and the mechanism batch-by-batch

Five native domain-IL digit worlds — identity, permuted, rotated, covariate (`3x+4`), noised (σ=0.6 iid on a [0,1]
signal) — one shared 40-D projection, one shared head, every learner consuming the bit-identical stream. **Forward**
is the merciful curriculum (clean world first); **reversed** is the cruel one (the first representation must form
inside the noise). The tuning asymmetry is stated blind: OURS runs a frozen config; ER gets its own best.

![P10.3 — the gauntlet money figure](phase10/exp3/figs_p10_3/GAUNTLET.png)
*The money figure. **Top** — worst-pre-sleep all-prev retention across the 5-domain stream: OURS(grid-4) holds
**0.490** at its worst point while ER-strong dips to **0.350** mid-stream; sleep ticks and domain boundaries
overlaid. **Bottom** — cumulative energy: OURS runs above ER on the digital substrate (the deep bulk) and below it
on analog. (n=5; worst-pre-sleep read, ER at the same convention.)*

The honest continual read favors OURS decisively — worst-point retention **0.490 vs 0.350**, steadier anytime
accuracy (**AAA 0.519 vs 0.433**) — at competitive final AA (0.490 vs 0.504, within δ). The §10 extension then made
the *mechanism* visible and stress-tested it, four rounds:

![P10.3 §10 — the per-batch stream view](phase10/exp3/figs_p10_3/GAUNTLET_STREAM.png)
*The mechanism. ER's seen-so-far line **crashes at every domain onset and re-climbs** — the saw-tooth of an
end-to-end learner re-fitting its representation to each new world (live-batch mean 0.273) — while OURS rides
near-flat (0.469): the forward-only bulk + sleep loop holds both the live and the remembered read steady. ER buys
its marginally higher final AA with a crash-and-relearn cycle at every switch. (n=5, median; triple-guarded replay
of the committed run.)*

- **Reversed order (E6): the steadiness is curriculum-robust, and ER's is not.** Noised-first, **ER never recovers**
  — reversed final AA **0.343 vs its forward 0.504** (the net and its reservoir are shaped by noise early, and every
  later world is learned on that damaged base) — while **OURS lands at the same endpoint either way** (0.494 vs
  0.490): the unsupervised bulk extracts structure even from the all-noisy opener (Phase-6's Door-B result, visible
  live). The committed forward gauntlet was ER's *favorable* ordering — and a lifelong learner does not get to
  choose the order the world arrives in.
- **The staircase read (D1).** Reversed, OURS's line is a rising staircase whose treads sag: the SCFF bulk rotates
  on every batch (P9.0) while the SLDA namer is re-anchored only at sleeps — between sleeps the namer's frame goes
  stale and the averaged-over-old-worlds read sags, then each sleep snaps it back to a *higher* floor
  (0.17 → 0.42 → 0.44 → 0.46 → 0.49). Staleness, not loss: the endpoint equals the forward endpoint, and the live
  line never crashes. The sag bottoms are the worst-pre-sleep points in the flesh — the same mechanism that opens
  the P10.2 safety cliff when the cadence stretches.
- **The alignment-break (E8/E8b): the flat line is not a scheduling coincidence.** The author caught that the
  committed 24-step blocks equal the grid-4 sleep period exactly (every sleep sat on a domain's last step). Re-run
  with randomized non-multiple blocks `[68,63,56,57,68]` — 2–3 sleeps landing *inside* every domain — OURS is
  unchanged-to-better (worst-point 0.533; the aligned-72 control ties it, **paired gap +0.002 → alignment is a
  NON-FACTOR**). What moves is the opponent: given ~68 steps per world ER fully re-converges before every checkpoint
  (0.675). The honest scope line this buys: **the retention win over a tuned ER belongs to the rapid-switch regime**
  — where switches outpace the plastic learner's re-convergence. OURS itself is order-invariant,
  alignment-invariant, and length-stable in every layout tested; the *ranking* depends on how fast the world moves.
- **The reversed-long (E10): do the sleeps actually cure the sag?** Mid-domain sleeps demonstrably rescue it
  (median seen-jump **+0.052 across sleeps, 5/5**; the curve saw-tooths around a rising level; OURS order-invariant
  at length, 0.527 vs 0.533; ER still order-sensitive, 0.580 vs 0.675). Banked exactly as the pre-registered verdict
  fired — **supported, not confirmed** (the sag-shallower cut was mis-specified: equal inter-sleep segments measure
  rotation *rate*, not cumulative run-down); a small bulk-level decay component stays formally flagged.

### 2.4 The noise showcase (P10.4) — OURS ≫ BP+replay on every held-out channel

The Phase-6 noise arc, cashed on the assembled object under a **margin-disjoint held-out battery** (directional RMS
2.5, ADC 3-bit, + a nuisance channel). The read is directional retention — a direction, never a magnitude (the
spine, cashed one last time).

![P10.4 — the noise showcase](phase10/exp4/figs_p10_4/NOISE_SHOWCASE.png)
*OURS holds **0.92–1.10 on every channel** while BP+replay collapses (iid 0.61, directional 0.22, adc3b 0.30,
nuisance 0.47); OURS is invariant to the layernorm-removable covariate (1.000) and *improves* under iid noise
(1.095 — the noise-augmented training objective). (n=5, held-out, margin-disjoint.)*

Honestly scoped: the battery is re-parameterized, not structurally novel, so the claim is **"confirms P9.4 at new
levels,"** not a fresh payoff. A small **directional/ADC residual** persists (0.978 / 0.923, just > δ) → **named →
the analog-realism (SPICE/PVT) layer** — the Phase-6 hand-off cashed on the whole object, its remainder named rather
than papered over.

### 2.5 Natural digits (P10.5) — the honest static loss

On recognizable 8×8 digits (class-IL), ER-strong **beats OURS by +0.071** (0.950 vs 0.879, 5/5) with slightly less
forgetting (−0.019 vs −0.051; a short easy stream doesn't stress forgetting — there is nothing for the sleep loop to
out-protect). This is the honest *direction* of the synthetic-overstatement threat: the hard synthetic home
**understated** ER's edge. So "beats backprop accuracy" is **not supported** on static accuracy; OURS's accuracy
value is **continual stability on hard/long/multi-domain streams** — exactly the Phase-4 identity, re-confirmed. The
static gap is flagged to a future draft (a convolutional / larger bulk — a Stage-1 re-open, never a P10 re-run).

### 2.6 The Pareto verdict (P10.6) — the wins live off the (accuracy × energy) axis

![P10.6 — the Pareto verdict](phase10/exp6/figs_p10_6/PARETO.png)
*The verdict. On (final AA × analog energy) the non-dominated staircase is **{er_strong, gdumb}** — OURS(grid-4,
hero-ringed) is **dominated**: a small tuned ER has higher accuracy *and* lower energy (and GDumb anchors the cheap
corner cost-pathologically — it retrains from scratch at eval, annotated, never used to inflate the frontier). The
§10 all-grid money line sweeps the model's whole operating range in one stroke, cliff edges visible. OURS's genuine
wins are on the axes this scatter does not have: worst-case continual safety, noise robustness, and the substrate
floor. (n=5.)*

### The honest map (Phase 10's verdict table)

| axis | OURS | best fair opponent | verdict | number |
| --- | --- | --- | --- | --- |
| final accuracy (continual synthetic home) | 0.494 | ER-strong 0.498 | **tie** | +0.004 (< δ) |
| final accuracy (natural digits, static-ish) | 0.879 | ER-strong 0.950 | **loss** | −0.071 (not a static competitor) |
| worst-pre-sleep BWT (lifelong) | **−0.028** | ER-strong −0.272 | **win** | ≈10× safer |
| worst-point all-prev retention (gauntlet) | **0.490** | ER-strong 0.350 | **win** | +0.140 (AAA 0.519 vs 0.433); rapid-switch regime — the E8 scope |
| noise robustness (held-out, vs BP) | 0.92–1.10 | BP+replay 0.23–0.61 | **win** | every channel |
| energy — algorithm (same digital substrate) | 3.46e8 | ER-strong 2.25e8 | **loss** | 1.54× (the deep bulk) |
| energy — chip vs conventional GD (total) | 6.70e7 (analog) | ER-digital 2.25e8 | **win** | 3.4× (substrate-realized floor) |

**The founding bet, banked as two halves (S14).** **Economics — substrate-realized:** the 80/20 *algorithm* alone
does not win the same-substrate energy race (1.5× more than a small tuned ER); the **chip** is 3.4–3.5× cheaper than
the same GD model on a conventional digital accelerator — "less energy than modern GD" holds *for the chip*, and the
win is the substrate, reported plainly. **Accuracy — competitive on the home, a static trail, a continual-stability
WIN:** ties the tuned ER on the hard home, trails on easy static digits, and is the **safest of the whole field** on
the honest worst-case read (~10× less worst-point forgetting; steadier retention across five shifting worlds; ≫ BP
on every noise channel). The founding bet is **refined, not inflated** — the honest-science outcome the project's
whole method is built to produce. The frozen object is a **substrate-native continual learner** — precisely the
identity Phase 4 named, now tested against the strongest fair opponent.

---

## 3 · Between the trials — the strike Phase 10 could not answer

Phase 10 closed Stage 2, and the author's own red team then named the one gap that mattered: **"the wins live on toy
data."** Every arena so far — the synthetic home, the transformed-digit gauntlet, 8×8 digits — is small, and partly
built by us. Three reviewer strikes crystallized: **(1)** *"isn't this just SLDA?"* — the namer is off-the-shelf
literature, so is the architecture doing anything? **(2)** *"show me real data"* — real drift, real streams,
cross-dataset streams; **(3)** *"does it scale?"* — one width, one depth, one input dim, one class count is not a
scaling story. Phase 11 is the answer, run under the same disciplines with one addition: **welcoming losses.** The
deliverable is not a win — it is the **map**.

---

## 4 · Trial two — the limit map (Phase 11, S15)

*Ran 2026-07-05, P11.0→P11.9; committed core + all three scaling extensions; verdict shapes pinned BLIND.*

**The instruments.** **Arm A — the frozen recipe:** the committed object, bit-for-bit, forced through a
**40-dimensional random porthole** so every arena — an 8-D power stream or a 784-D image — enters at the same input
width the object was frozen at. Arm A answers: *does the thing we actually committed survive contact with real
data?* **Arm B — the scaling rule:** the same architecture rebuilt to a **pre-registered** size law (D = min(native,
160), W = ⌈1.6·D⌉, depth 12) — declared before any run, tuned to nothing. Arm B answers: *how much of the porthole
loss comes back at native scale?* The opponent (ER-strong) is re-tuned **per arena** on the disjoint seed-7 stream;
OURS is never touched. Five channels score every arena: **AA / prequential accuracy** (balanced, test-then-train),
**worst-BWT** (safety — the object's signature channel), **worst-point retention**, **order-invariance**
(|AA(fwd) − AA(rev)|), and **beats-persistence** (the no-change baseline — brutal on autocorrelated streams). Every
cell is **win / tie / loss / FLOOR**; a FLOOR is *uninformative* — the ceiling sits at the data's resolution or
persistence limit, so nobody separates from it there. **Grey is honesty, not defeat.**

### 4.0 The bench (P11.0) — three load-bearing facts before any run

Seven real arenas loaded offline (MNIST/Fashion/CIFAR-gray at 784-D, gas 128-D sensor drift, HAR 561-D, electricity
8-D chronological, covertype 54-D; balanced accuracy mandatory where imbalance hits 10:1). Three bench facts carry
everything after: **(1)** `freeze_content` is bit-exact — the object under test *is* the P9 freeze, not a
re-implementation that drifted. **(2)** The noise-σ direction-killer, caught at the source: P10's noised domain is
σ/RMS = 1.239, and the naive "0.6 × RMS" shorthand would have made MNIST's noised domain ~2× milder — confounding
the exact channel that drives the retention differentiator (this project's recurring silent killer is a wrong
direction/scale on one variable; pinned by equivalence on every arena). **(3)** A pre-registered guess refuted at
the meter source: **the economy does NOT improve with scale** — GD-share rises {0.21, 0.34, 0.53} for W ∈ {64, 128,
256}, because the SLDA solve term scales ~O((L·W)³).

### 4.1 The decomposition (P11.1) — "isn't this just SLDA?" → which half does which job, measured

Δbulk = (bulk→namer) − (projection→namer): how much the *learned* SCFF bulk adds over feeding the same closed-form
namer a plain random projection — swept from linear-easy to nonlinear-hard arenas, with a random-frozen 12-layer
reservoir as the "is it just depth?" control. (A pre-run diagnostic reframed the rung: digits are near-linearly
separable — raw-SLDA 0.950 — so a digits-only Δbulk would have banked a misleading "the bulk is worthless.")

![P11.1 decomposition — the strike-1 answer](phase11/exp1/figs_p11_1/DECOMP.png)
*Two panels. **Left** — Δbulk tracks arena nonlinearity: where a linear head is at chance the learned bulk lifts it
**+0.417** and clears the random reservoir (0.389 → 0.589) by a wide margin — **learned SCFF structure, not merely
depth**; on near-linear digits the bulk is correctly redundant (−0.014). **Right** — the safety channel: a
projection→namer with no bulk at all forgets no more than the full object — so the continual safety lives in the
**closed-form namer + gate + sleep**, not the bulk.*

The honest answer is a *decomposition of attribution*, sharper than a defensive "no": the SCFF **bulk is the
nonlinear feature learner** (decisive where a linear head can't crack the data, correctly out of the way where one
can, and it beats a random reservoir — the lift is *learned*); the continual **safety is the namer + gate + sleep**
— we measured which half of the machine does which job, and we say so. On iid noise at matched clean accuracy the
bulk wins +0.086 (digits) / +0.215 (synth) — the Phase-6 noise-augmentation earning its keep, a channel the
projection can't reach forward-only.

### 4.2 The MNIST rung (P11.2) — the signature survives real data, and the recipe scales

The P10.3 gauntlet rebuilt in native MNIST-784 → porthole, both switch regimes, both arms, vs a per-arm-tuned ER:

| arm | regime | OURS AA | ER AA | OURS worst-BWT | ER worst-BWT | OURS ret | ER ret |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A (D40) | rapid | 0.258 | 0.448 | −0.080 | −0.143 | 0.216 | 0.221 |
| A (D40) | **long** | 0.284 | 0.427 | **−0.012** | −0.196 | **0.223** | 0.102 |
| B (D80) | rapid | 0.390 | 0.541 | −0.011 | −0.113 | 0.298 | 0.210 |
| B (D80) | **long** | 0.421 | 0.514 | **−0.046** | −0.162 | **0.314** | 0.105 |

![P11.2 MNIST rung — the sleep loop batch-by-batch](phase11/exp2/figs_p11_2/STREAM_mnist.png)
*The STREAM view with the best tuned BP overlaid. **ER (orange) rides higher within each stationary domain** —
climbing to 0.8–1.0 — but **crashes at every domain switch** toward ~0.1, the sawtooth of forget-and-relearn; **OURS
(teal) rides lower but far flatter** and never collapses at a switch. ER wins raw accuracy inside a domain; OURS
wins **stability across the switches** (long-regime worst-BWT −0.046 vs −0.162). A continual-stability trace, not a
static-accuracy one.*

The bet **holds on real data**: OURS wins continual safety in every cell (forgetting ~4–16× less than a
per-arena-tuned ER), wins retention on long blocks, and is order-invariant (|Δ| 0.003 / 0.011). Static accuracy
trails — the porthole discards most of MNIST's spatial structure, and the object was never a static competitor. And
**Arm B scales**: D40→D80 lifts AA 0.284→0.421 and retention 0.223→0.314 with the safety intact. (One honest
asterisk, owed: the Split-MNIST *anchor* ran at porthole-40, not the literature's raw-784 — a config note, not an
ER-implementation failure.)

### 4.3 The real-world streams (P11.3) — nature's own drift, and the two kinds of hard

Four real time-ordered streams where the drift is the world's, not ours: gas-sensor aging, human-activity by
subject, electricity price, forest cover. Pinned channel: prequential balanced accuracy, every learner including the
no-change persistence baseline.

| stream | OURS-A | OURS-B | stronger-ER | no-change | verdict |
| --- | --- | --- | --- | --- | --- |
| **gas** (6-cls, sensor drift) | **0.789** | **0.856** | 0.756 | 0.605 | **WIN** |
| har (6-cls, by-subject) | 0.686 | 0.820 | 0.754 | 0.950 | FLOOR (field +0.07) |
| electricity (2-cls, chrono) | 0.606 | 0.596 | 0.687 | 0.836 | FLOOR (field +0.08) |
| covertype (7-cls, file order) | 0.471 | 0.472 | 0.542 | 0.646 | FLOOR (field +0.07) |

![P11.3 gas — the real-world headline win](phase11/exp3/figs_p11_3/STREAM_gas.png)
*The headline (rolling mean ±1σ — the swings are the data's; ER's band swings just as wide). Both learners ride far
above persistence — this is real, information-bearing drift — and **OURS pulls clearly ahead in the late stream,
where the sensors have aged most**, taking the aggregate: prequential **0.789 ≥ the per-arena-tuned ER 0.756**,
+0.184 over persistence; Arm B lifts it to **0.856**. Sensor aging is a coherent covariate shift — exactly the drift
the SCFF bulk + sleep re-anchoring was built to ride while the closed-form namer never catastrophically forgets.*

![P11.3 HAR — an honest FLOOR](phase11/exp3/figs_p11_3/STREAM_har.png)
*The counter-case, shown just as plainly. On HAR the no-change baseline (dash-dot, **0.95**) sits above every
learner — the ELEC2 label-autocorrelation trap, where "predict the previous label" is near-unbeatable by any model
that reads the features. Inside that floor the field leads OURS by ~0.07; the cell is grey and two-sided, and both
sides are visible. HAR, electricity, and covertype all live in this regime.*

The measurement cleanly separates **drift-difficulty** from **data-difficulty**: when the drift is a genuine
covariate shift (gas), the object's whole design pays off — the untouched frozen recipe is the strongest online
learner in the room. When the labels autocorrelate (HAR/electricity/covertype), *no learner beats persistence* — a
known property of those streams (Souza 2020), not of our object — and we floor honestly, reporting that inside the
floor the field is ~0.07 ahead (the anti-hype guard is not an anti-loss shield). One honest limit stays in the open:
the near-zero worst-BWT of the synthetic gauntlet **does not carry to real continuous drift** (gas −0.333, har
−0.233 — the SLDA frame going stale between sleeps as nature drifts continuously, not in discrete steps); on gas
that read is also under-powered (late batches < 100 eval samples), which is exactly why prequential accuracy is the
pinned headline channel there.

### 4.4 The cross-dataset gauntlet (P11.4) — robustness to the *type* of data

The most aggressive ask: MNIST → Fashion → CIFAR-gray as ONE class-IL **30-way** stream (the field's 5-Datasets
protocol, but class-IL — harder), through a single porthole fit only on source 1: the object never re-fits its front
end when the *kind* of data changes.

| arm | final-30 | order \|Δ\| | worst-ret | ER worst-ret | mnist / fashion / cifar-gray | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| A (D40) | 0.338 | 0.007 | 0.415 | 0.534 | 0.421 / 0.461 / 0.125 | TYPE-SCOPED |
| B (D80) | 0.440 | 0.004 | **0.581** | 0.551 | 0.588 / 0.581 / 0.143 | **TYPE-ROBUST** |

![P11.4 cross-dataset — 30-way across three data types](phase11/exp4/figs_p11_4/STREAM_xdata.png)
*The phase in miniature. ER learns block 1 (MNIST, alone) higher than OURS — then **catastrophically collapses to
≈0 at each data-type switch** (its fixed 30-way replay head has never seen the new classes); OURS **degrades
gracefully** and rides above ER through the entire Fashion block. No block dies — even CIFAR-gray holds ~4× chance;
the CBRS prototype LUT keeps every type represented through the growth to 30-way.*

Three findings: all three data types stay **alive**; **order-invariance survives even a change in data type**
(|Δ| = 0.007 / 0.004 — a direct consequence of the closed-form namer: there is no gradient path an ordering can
bias); and **the scaling recipe flips the retention verdict** — Arm A trails ER on worst-point retention (0.415 vs
0.534, TYPE-SCOPED), Arm B recovers it (0.581 ≥ 0.551, **TYPE-ROBUST**), with the namer's Gram condition number
instrumented and bounded. (The owed leg is honest: Arm B ran at D=80, descoped from the full D=160 for the overnight
budget.)

### 4.5 Does it scale? (P11.5–P11.7) — the strike-3 trilogy

- **Accuracy & hardness.** **Fashion holds the safety bet** on a harder recognizable dataset — OURS worst-BWT
  −0.021/−0.057 vs ER −0.146/−0.141 (≈2–7× less forgetting), ER leads absolute accuracy (the continual-not-static
  identity again), Arm B recovers retention (0.401 > 0.380). **CIFAR-gray is the honest FLOOR** — the joint-BP
  ceiling itself is 0.199: grayscale-cropped CIFAR through a porthole sits at the resolution floor and every channel
  there is grey, not a parity claim.
- **Memory — the cleanest scaling result in the phase.**

  ![P11.5 crossover — the class-count memory read](phase11/exp5/figs_p11_5/CROSSOVER.png)
  *Two honest halves. **Left** — on raw bytes the prototype+Gram namer carries a large fixed O(C·F + F²) cost and
  never crosses below a fixed-rate replay buffer — no memory-byte crossover, and we say so. **Right** — but on
  worst-point retention it crosses hard: at C=10 the byte-matched replay out-retains OURS (0.423 vs 0.354); at
  **C=20 the replay buffer dilutes to ≈0 retention (0.014) while the prototype+Gram namer holds (0.233)** — a +0.219
  flip. Per-class fidelity is C-independent for an exact mean + shared covariance; a fixed buffer splits its budget
  O(1/C) and collapses as classes accumulate.*

- **Economy & substrate.**

  ![P11.6 scaling — capacity vs the economy and the substrate](phase11/exp6/figs_p11_6/SCALING.png)
  *Three reads. **Left** — the bench-pinned GD-share shape is **CONFIRMED at the run**: measured [0.17, 0.28, 0.45]
  tracking the meter-derived [0.21, 0.34, 0.53] as W ∈ {64, 128, 256} — the economy does *not* improve with width
  (the SLDA solve scales worst); a pre-run guess refuted, kept refuted. **Middle** — capacity buys the accuracy gap
  back (0.42→0.50 over W, 0.39→0.51 over D). **Right** — the chip's best sentence: the **analog substrate advantage
  GROWS with width** — E(digital)/E(analog) = 5.39 → 6.89 → 7.25 (7.37× at D=160). The crossbar prices the extra
  bulk MACs near-free, so the compute-in-memory edge widens exactly where the digital substrate pays most.*

- **Real-time throughput.** On the gas stream the retention-tuned ER-strong costs more FLOPs/sample than the frozen
  D40 recipe, so at a shared compute budget **ER must drop 32% / 31% / 8% of the stream** (raw-FLOP / digital /
  analog) while OURS keeps up — a regime win, honestly caveated: it **inverts** P10's synthetic-home measurement, so
  the real-time economy is **arena- and opponent-dependent, not universal** — and the map says so.

### 4.6 The LIMIT-MAP (P11.9) — the deliverable

![P11.9 LIMIT-MAP — the committed object across real arenas and scale](phase11/exp9/figs_p11_9/LIMIT_MAP.png)
*The money figure: 8 arenas × 5 capability channels, every cell win (teal) / tie (light) / loss (pink) / FLOOR (grey
hatch), with its number. Read down the channels and the object's identity is unmistakable and honestly bounded.*

- **Wins (teal):** continual **safety** on every non-floor gauntlet arena; **retention** on mnist-long;
  **order-invariance** everywhere measured (|Δ| ≤ 0.043, even across data *types*); **gas accuracy** — the
  real-world headline, the frozen recipe beating a per-arena-tuned ER *and* persistence on a famous sensor-drift
  benchmark; and every **scaling read** (the pinned economy shape confirmed, the growing substrate factor, the C=20
  retention crossover, the gas throughput regime win).
- **Losses (pink):** static **accuracy** on mnist and fashion (continual-not-static, re-confirmed at scale);
  **retention** on fashion-A and the 30-way stream (both recovered by Arm B). The object is not a static-accuracy
  competitor and the map never pretends otherwise.
- **Floors (grey):** CIFAR-gray (native-resolution floor); HAR / electricity / covertype (the ELEC2
  label-autocorrelation trap — the field floors alongside OURS but leads ~0.07). The far and autocorrelated edges of
  the map are grey, **and grey is not parity.**

The **Δbulk overlay** keys the map to a mechanism: the bulk earns its place where the data is nonlinear; the safety
is the namer + gate + sleep. **S15 banked.**

---

## 5 · The combined verdict — what the two trials establish

One sentence, earned twice — once against the strongest fair opponent on the home bench, once across the real world:

> **A substrate-native continual learner that wins continual safety (~10× less worst-point forgetting),
> noise-robustness (every held-out channel), order-invariance (even across data types), real information-bearing
> drift (gas — the frozen recipe beats a per-arena-tuned ER and persistence), and every scaling read of the
> economy/substrate (the analog advantage grows 5.4→7.4× with width; the namer out-retains replay by C=20) — while
> trailing on static accuracy, paying a same-substrate algorithm-energy premium for its deep bulk, and flooring
> where the data hits its resolution or persistence limit.**

The wins are real; the losses and floors are **mapped, not hidden.** The founding bet survives both trials *refined*:
the economics win belongs to the **chip** (the analog crossbar — a meter-structural floor that widens with scale),
and the accuracy win is **lifelong stability**, not static accuracy — exactly the identity Phase 4 named on the
capability map, now validated against the strongest fair opponent (S14) and bounded on the real world (S15).

---

## 6 · Honest scope + threats-to-validity (both trials)

- **The meter is behavioral** (relative-pJ, ADC-centred macro-model, Horowitz-anchored, params + citations logged),
  **not SPICE.** The analog factor is meter-structural — never the contestable claim; the load-bearing energy cut is
  same-substrate. Absolute Joules and device physics are the analog-realism layer's.
- **The fair fight depends on the ER budget + tuning** — so ER was FLOPs+byte-matched *and* tuned strong on a
  disjoint seed (per arena in P11), and both budget and strong points are reported. The racer's shape is its own
  uncapped best choice — which is *why* the same-substrate energy cut goes against OURS, reported not hidden.
- **The gauntlet retention win is switch-frequency-scoped** (the E8 alignment-break): on long stationary blocks a
  tuned ER re-converges and overtakes the checkpoint read. OURS itself is order-, alignment-, and length-invariant
  in every layout tested — the scope belongs to the comparison, not the object.
- **Synthetic overstates static gaps** — the natural reads (P10.5, P11.2/11.5) are the honest ones, and they
  *reveal* the ER static edge the hard synthetic home masked.
- **Projection loss dominates absolute accuracy in P11's Arm A** — the →40 porthole discards structure; Arm B bounds
  how much comes back per arena; the static losses are partly a porthole artifact, not a pure capability gap.
- **Real-drift worst-BWT is genuinely negative** — the synthetic near-zero-forgetting does not transfer to
  continuous natural drift; reported, not hidden (and under-powered on gas's small late batches, which is why
  prequential accuracy is the pinned channel there).
- **Descopes named, not faked:** Yearbook / BloodMNIST / CIFAR-100 (openml API down), the P11.8 features arena, the
  D=160 cross-dataset Arm B (ran at D=80), the raw-784 Split-MNIST anchor validation.
- **Behavioral simulation throughout** — numpy ideal floats + the Phase-6 behavioral analog-noise model; no SPICE,
  no device physics, no fabrication.

---

## 7 · Hand-offs — what the trials name and defer

- **→ the analog-realism layer (SPICE / PVT):** the small directional/ADC residual the read-side defense cannot
  fully reach (P10.4); the absolute-Joule + device-physics layer the behavioral meter cannot give; inheriting P11's
  real-data envelope as the deployment spec.
- **→ the noise-first representation limit (named by the §10 reversed runs):** order-invariant at the endpoint, but
  a representation whose first structure forms inside noise runs thin-margined between sleeps. The named capability
  target: a bulk that recovers the clean structure *itself* from an all-noisy stream — a deployed chip does not get
  a merciful curriculum.
- **→ a future draft (flagged, not executed):** the static-accuracy gap on natural data — a convolutional or larger
  bulk would lift it (P11.6's capacity read supports this), but that is a Stage-1 re-open.
- **→ the professor pack:** [`phase10/professor-brief.md`](phase10/professor-brief.md) — the object in a paragraph,
  the money figures, the two-halves verdict, and the two honesty lines a reviewer tests first.
- **→ the decision record:** **S14** (the P10 close-out) + **S15** (the P11 limit map), banked to
  [`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md).
- **→ the north star (deliberately not specced):** no recurrence was added; the spine-clean cosine direction and the
  drift-gate halt survive as tie-break biases only. Simple intelligence first.

---

## Reading guide

**For the whole model in one file:** [`phase9-final-architecture.md`](phase9-final-architecture.md) (v2.0.0 — both
brains + the maintenance loop, self-contained). **For how the object was built:** [`stage1-report.md`](stage1-report.md)
(the cheap brain, P1–6) → [`stage2-report.md`](stage2-report.md) (the namer + the economy + the freeze, P7–9).
**For this volume's depth:** the two phase front doors — [Phase 10](phase10/README.md) ·
[Phase 11](phase11/README.md) — then the deep stories ([`phase10-report.md`](phase10/phase10-report.md) ·
[`phase11-report.md`](phase11/phase11-report.md)), the scalar ledgers (`phaseN/RESULTS.md`), and the
`expK/experiment-K.md` cards. **For the professor meeting:** [`phase10/professor-brief.md`](phase10/professor-brief.md).
Terms, metrics, and papers: [`ref-report/`](ref-report/README.md); the committed decisions (through S15):
[`../idea/main.ideas.v1.md`](../idea/main.ideas.v1.md).

*Prev:* [Stage 2 — the namer (P7–9)](stage2-report.md) · *Up:* [draft 6.0 context](../CLAUDE.md) · *Next:* the
analog-realism layer (SPICE / PVT), and beyond the numbered phases, the recurrent lifelong brain — the north star.
