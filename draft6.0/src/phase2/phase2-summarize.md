# Phase 2 — what we discovered (the synthesis)

> The depth phase of draft 6.0, run 2026-06-21 (P2.0 → P2.6). The *story of the findings* — what we asked, what
> the sims said (mostly **no**, decisively), and the honest verdict. Per-rung detail in each
> `expN/experiment-N.md`; the scalar ledger is [`RESULTS.md`](RESULTS.md); the reporting standard is
> [`result-format.md`](result-format.md); the plan was [`README.md`](README.md). Stack: numpy-only SCFF (local
> closed-form gradient) + sklearn probes + matplotlib; tasks = CIFAR-10-flat (the depth probe), synth Tier-B
> (the dial), digits (the continual veto); 5 seeds (3 for continual).

---

## The one-paragraph verdict

**Depth is not SCFF's game — and proving that, decisively, *is* Phase 2's result.** Phase 2 existed to resolve
one hardware collision (README §0): SCFF's strength is *width*, but the Scap substrate's cheap axis is *depth* —
can we move SCFF's success onto depth? **No.** A deep SCFF stack cannot earn depth, and we closed every escape
hatch: it is not a **transmission** problem (P2.1 — no normalization × goodness bends the per-layer probe up,
though the right cell fixes the *mechanism*: no deactivation, rank preserved), and it is not an **objective**
problem (P2.2 — *even a perfect label-oracle* class-aware negative changes the slope by nothing). The depth wall
is **intrinsic to SCFF's forward-only locality**: composing class features across depth needs cross-layer
coordination that local learning structurally cannot supply — exactly what the GD 20% exists to provide. So depth
comes the *other* way: **boosted ensembles of *shallow* SCFF blocks with tiny GD readouts** (P2.5 — earns depth
cheaply but modestly, ~85% of GD accuracy at ~1/6 of GD's backward cost; `read`/ensemble works, `write`/re-inject
fails), and that recipe **preserves the Phase-1 continual win and is continual-safe by construction** (P2.6 — no
batch statistics to rot). Phase 2 did not make SCFF deep; it proved SCFF *shouldn't be* deep, and named the cheap
substrate-native way to get depth anyway — vindicating the cheap-brain 80/20 design rather than overturning it.

---

## The arc, rung by rung

### P2.0 — re-establish the wall + the decisive fork (lost vs entangled)
**Result.** On CIFAR-flat the deep-SCFF wall reproduces cleanly (per-layer probe **0.23 → 0.117**, slope
**−0.018**, all 5 seeds); the **selectivity control** (vs an untrained random projection) returns **LOST**, not
entangled — deep SCFF features fall *below* random (selectivity −0.005). Cause = *both* axes (dead-units 0→0.47
*and* rank-collapse 39→11). **Set:** the wall curve every later rung must bend up; the selectivity control
(kept permanently — it caught a mis-route); synth has *no* wall (it's the dial, not the headline).

### P2.1 — the normalization × goodness grid (the make-or-break gate)
**Result.** **GATE FAILED — 0/7 learning cells reach slope ≥ 0.** Every learning cell declines; the
DeeperForward-style heroes (layer-norm+linear, online-BN+linear) decline *faster* than the wall (better shallow
features, lost by L8). The transmission fix **works at the mechanism level** (linear goodness → dead 0.25→**0.00**,
rank 19→**46–50**, L1 probe 0.29→**0.33**) but that never becomes depth-rising *class* separability — the
bottleneck is the objective (density ≠ class). **New:** squared goodness + mean-zero norm = total unit death (the
wall survives *only because* length-norm keeps the mean). **Side-win:** the threshold-free contrast loss ~doubles
the deep probe vs two-sided θ=2.0. **Set:** transmission is necessary (linear + per-sample, no death) but not
sufficient; **carry the healthy cell** (layer-norm + linear + contrast). STOP/rethink → promote P2.2.

### P2.2 — the objective: class-aware (hard) negatives (the decisive rung)
**Result.** **DECISIVE NEGATIVE — even a perfect ORACLE fails.** With the healthy transmission fixed, making the
negative class-aware (oracle, true labels; prototype; or unsupervised KMeans) changes the depth-slope by nothing
(all −0.022 to −0.015, ≈ random); no real probe lift (oracle +0.003, disjoint-IQR −0.010 ✗). Synth control: the
oracle *does* lift where classes exist (+0.027, real) → the CIFAR negative is real, not a bug. **Verdict: depth
is not the lever** — transmission *and* objective both fail ⇒ the wall is intrinsic to locality. **Skip P2.3
(collaboration) + P2.4 (interface)** — moot (they refine a deep stack that shouldn't exist). Route → P2.5.

### P2.5 — multi-block: GD *between* shallow SCFF (the constructive answer)
**Result.** **GD-between earns depth — cheaply, not greatly.** `read` (boost the per-block GD readouts) beats
pure-SCFF by a disjoint-IQR margin (N8 0.292→**0.302**, +0.010) where deep SCFF *can't* — but **saturates ~2–4
blocks** (Phase-1 reconfirmed). **`write` (re-inject the GD rep into the SCFF stream) FAILS monotonically**
(−0.04→−0.09) — class-collapsed reps destroy the rich features. **The real prize is cost:** `read` reaches **~85%
of pure-GD accuracy at ~17% of its backward cost** (the SCFF bulk is forward-only; only tiny readouts pay
backward). **Set:** depth = cheap boosted *shallow* blocks, GD as **readout** not stream-rewriter; few blocks
suffice.

### P2.6 — the substrate filter + the continual veto (the real deliverable; closes Phase 2)
**Result.** **VETO PASSED.** The boosted-read recipe, run continually + sleep-consolidated, recovers to **0.932**
(BWT **−0.034**) ≈ single-block (0.938 / −0.026), ≫ online-rot (0.33) / GD-online (0.19); **SCFF probe flat**
(doesn't forget); sleep decisive. It is **continual-safe by construction** — per-sample norm carries no batch
statistics, so the Continual-Normalization rot worry never applies. Honest caveat: boosted BWT a hair worse than
single-block (−0.008, disjoint-IQR but negligible — multi-block drift compounds slightly). **Set:** the recipe is
the surviving deliverable; **drift measured** for the Phase-3 gate; **few blocks suffice** (now confirmed from
*both* the static and continual sides).

---

## The cross-cutting discoveries (what the sims forced)

1. **Depth is intrinsically not SCFF's lever.** Not transmission (P2.1), not objective (P2.2 — even an oracle).
   Forward-only locality cannot coordinate features across layers; that's structural, not a tuning gap.
2. **The literature's depth fix is the right mechanism for the wrong problem.** DeeperForward/ASGE's
   linear/mean-goodness *does* cure deactivation and rank-collapse on our substrate — but on *unsupervised
   flat-MLP* SCFF that cures the symptom, not the disease (density ≠ class). *(They earn depth with **supervised**
   per-layer CE on **CNNs** — a different regime; the FF survey confirms our regime was unaddressed.)*
3. **Squared goodness + mean-zero norm = catastrophic death;** the FF "layer norm" (length-norm) survives *only*
   because it does **not** remove the mean. Any mean-zero cell must use linear goodness.
4. **Contrast (threshold-free) > two-sided θ** for deep SCFF (~2× the deep-layer probe) — the loss matters, the
   threshold is a liability across scales.
5. **Depth is bought by *blocks*, not SCFF layers — and only by *reading* (boosting), never *writing*.**
   Re-injecting a class-collapsed GD rep into the SCFF stream destroys the rich features.
6. **The cheap-brain shape is real and continual-safe:** forward-only single-sample SCFF bulk (0 backward) + tiny
   sleep-consolidated GD heads (~17% backward), no batch statistics anywhere.

---

## What's validated vs not

| | status |
| --- | --- |
| Deep SCFF can earn depth (transmission or objective fix) | ❌ **decisively** (P2.1 + P2.2, oracle-proof) |
| The transmission fix (linear + per-sample norm) cures deactivation/rank-collapse | ✅ (mechanism only — doesn't earn depth) |
| GD-*between* shallow blocks (read/boosting) earns depth | ✅ **cheaply & modestly** (saturates ~2–4 blocks) |
| `write` (re-inject GD into the SCFF stream) | ❌ (loses accuracy, rejected) |
| The depth recipe is cheap (vs full GD) | ✅ ~85% of GD acc at ~1/6 backward |
| The depth recipe preserves the continual win (ACC+BWT) | ✅ (P2.6 veto; continual-safe by construction) |

---

## Open knobs (set) and remaining follow-ups

**Set by Phase 2:** the surviving recipe = `[SCFF×k → GD-readout]×N`, **read** (not write), per-block SCFF =
**layer-norm + linear + contrast** (the healthy cell), sleep-consolidated; **few blocks suffice** (cheapest k);
GD is a **readout**, not a stream-rewriter.

**Remaining (Phase 3 / later):**
- **Ch7 threshold gate** — when to pay for the GD readout / sleep (tuned against the drift Phase 2 *measured*).
- **Sleep-cadence + LUT-vigilance** — how *little* maintenance suffices (LUT ⅓-store compression, exp4).
- **Analog / PVT / SPICE realism** — the deferred substrate layer (still out of behavioral scope).
- **The recurrent lifelong brain** — the north star, beyond the numbered phases.

---

## The bridge to Phase 3 (and the north star)

Phase 1 found *where* this architecture wins (the continual regime). Phase 2 found *what depth costs and how to
buy it cheaply* — and confirmed the win survives. The picture is now complete enough to stop characterizing the
static substrate and start building the **temporal** machinery: a brain that decides *when* to learn cheaply vs
pay for coordination (the gate), and *when* to consolidate (sleep cadence). That is Phase 3 — and the step toward
the project's real target, the recurrent prefrontal↔hippocampus loop where "correctness is a self-generated
feeling." Phase 2's gift to it: **a depth-capable, continual-robust, substrate-native cheap brain, with its drift
measured and its cost known.**

---

## Reproducibility

Every rung writes `figs_*/manifest.json` (git commit + config + medians) + `figs_*/arrays.npz`; figures regenerate
with no retraining (`python expN/plot_expN.py <dir>`). Runs are seeded/deterministic. **Run heavy jobs
single-threaded** (`OMP_NUM_THREADS=1` + `python -u`) — sklearn/OpenMP phantom-hangs in a backgrounded process on
this machine. Entry points: `exp0/run_exp0.py` (wall+DECIDE), `exp1/run_exp1.py` (norm×goodness),
`exp2/run_exp2.py` (negatives), `exp5/run_exp5.py` (GD-between), `exp6/run_exp6.py` (continual veto). *(No
exp3/exp4: P2.3/P2.4 skipped, moot per P2.1+P2.2.)*
