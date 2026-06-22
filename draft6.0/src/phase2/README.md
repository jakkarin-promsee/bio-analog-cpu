# Phase 2 — Make cheap SCFF earn *depth* (and the GD interface that reads it)

> **Status: ✅ COMPLETE (2026-06-21, P2.0 → P2.6).** This README is the original **plan** (kept as the record of
> what was proposed); the **results + verdict** live in [`phase2-summarize.md`](phase2-summarize.md) (the
> synthesis), the `expN/experiment-N.md` cards, and [`RESULTS.md`](RESULTS.md) (ledger). **Verdict in one line:
> depth is not SCFF's lever** (deep SCFF can't earn depth — P2.1 transmission + P2.2 objective, oracle-proof);
> depth comes cheaply from **boosted shallow blocks + small GD readouts** (P2.5, `read` not `write`), and that
> recipe **preserves the continual win** (P2.6 veto). **P2.3/P2.4 were skipped** (moot — no `exp3/`/`exp4/`).
> Read the plan below for the *aims*; read the summary for *what happened*. Builds on the Phase-1 verdict in
> [`../phase1/phase1-summarize.md`](../phase1/phase1-summarize.md).
>
> **Reporting is decided up front:** [`result-format.md`](result-format.md) — pinned metrics (probe · CKA ·
> effective rank · Fisher/NCC · drift · continual ACC+BWT), the figure catalog (depth curve, width×depth,
> REPR, DECIDE, BLOCK, continual-veto…), and the 6+2-slot summary. Every run follows it as the baseline;
> override only when the data demands.
>
> **Phase numbering (re-renumbered 2026-06-21, see §8):** Phase 1 = structure + sleep (**done**). **Phase 2 =
> *this*, depth round 1 — the *energy-goodness can't* negative (**done**).** **Phase 3 = depth round 2 — the
> objective reframe** (`../phase3/`, active). **Phase 4** = online maintenance (the Ch7 gate + sleep-cadence —
> *was* "Phase 3"). The recurrent lifelong brain is the **north star**, beyond the numbered phases.

---

## 0. Why Phase 2 exists — *despite* Phase 1 saying depth isn't our game

Read this first, because it is the only justification for the whole phase. **Phase 1's verdict was emphatic:
the home is the *continual* regime, not static depth** — "shallow-is-better, depth saturates… *not* a deep
static-accuracy competitor, and that's the point." So why spend six rungs fighting the depth wall?

**Because of a hardware collision, and nothing else:**

> **SCFF's strength is *width*; the Scap substrate's cheap axis is *depth*.** The algorithm succeeds on the
> exact axis the hardware most wants to avoid — width is free on a GPU but expensive in Scaps; depth is the
> chip's cheap direction but where SCFF degrades. Phase 2 exists *only* to resolve that collision: **can we
> move SCFF's success onto the substrate's cheap axis?** We are not chasing static accuracy for its own sake
> — the moment a depth-fix costs the Phase-1 continual win, it is rejected (the **continual veto**, P2.6).

That is the front door. Everything below serves it.

**The one question, and the frame (stated once — referenced, not repeated, below):**

> **Can a *stackable, cheap* SCFF±GD unit be made to *gain* accuracy with depth — narrow-and-deep matching
> wide-and-shallow — while staying single-sample-online and continual-robust?**

There is **one object**: a stackable unit `[ SCFF feature layers → (optional GD checkpoint) ]`. "Deep SCFF"
and "multi-block" are the **same axis**, differing only in whether GD checkpoints sit *between* SCFF groups.
Two sub-aims fall out — **(A)** fix the SCFF layer so depth *adds* class structure instead of homogenizing
it; **(B)** fix the GD input interface so it reads the deeper representation efficiently.

**The wall, with the right numbers** (Phase 1, cited precisely — *plain* deep SCFF stack, not the
residual-dilution variant): per-layer linear-probe **degrades `[0.90→0.59]` over 6 layers** (digits, exp3
skip-OFF) and **`[0.82→0.52]` over 4** (MNIST, exp1). *(The `0.46` figure floating around is the ε=1
residual-skip case where the mandatory norm dilutes — a different effect; don't cite it for "the stack
degrades.")* Pure-GD hidden layers stay flat-high (`~0.94`) — that gap is what Phase 2 must close.

---

## 1. The diagnosis + the levers (from Phase 1 + the lit search)

**Diagnosis.** Each SCFF layer optimizes *goodness* (`G=‖h‖²`, real-loud / blend-quiet) — a **density**
objective, class-agnostic. The **mandatory layer-norm** `ĥ=h/‖h‖` is the *transmission line of the damage*:
it strips magnitude (one info channel gone) and forces every layer to **re-separate from scratch on the unit
sphere**, so the homogenization compounds with depth. Not our quirk — *The Trifecta* says it outright:
layer-norm "prohibits the network from creating incrementally useful and specific features… a collection of
single-layer classifiers with shallow insight… high instability at later layers."

**The levers** (full source attribution in §10; this table is the working map):

| lever | source | what it changes | substrate note |
| --- | --- | --- | --- |
| **layer-norm → batch-norm** | Trifecta | per-*feature* (across batch) not per-*sample* length → preserves magnitude structure → incremental features → **depth helps** | needs a *batch* the chip lacks → use **online/streaming BN** (running EMA stats) |
| **θ-loss → SymBa / pure-contrast** | Trifecta, SymBa | optimize the *gap* `g_pos−g_neg`, no threshold | = our Phase-1 0a; cheap |
| **shared goodness γ** | Layer Collaboration | each layer's loss adds the *detached* total goodness of others → collaborate, stay local | **one broadcast scalar = a neuromodulator wire** |
| **overlapping local updates (OLU/DF-O)** | Trifecta, Distance-Forward | a layer also helps its *successor's* goodness | needs 2 layers' state |
| **class-aware (hard) negatives** | Phase-1 §, SCFF Ch4 | `x_neg = x_k + prototype-from-a-*different*-cluster` → "blend = between-*class*" → class-aligned, unsupervised | uses the LUT we already built |
| **deep supervision (per-layer readout)** | Deeply-Supervised Nets | a small companion classifier per layer → weak label into SCFF *and* a clean GD entry | the GD-interface lever |

**The substrate filter** (what makes this *our* problem). Batch-norm is GPU-native; the chip is **online,
single-sample, streaming, analog**. So under every lever the headline question is: *does the online /
running-statistics version keep the benefit?* The chip already holds the registers — the **BCM `⟨a²⟩`** is a
running per-unit second moment, the Scap momentum caps are running first moments — so online/streaming
normalization at batch size 1 is hardware-plausible.

---

## 2. The task, and the locked setup (so the headline figure can *exist*)

**"Does separability rise with depth?" is only measurable on a task with depth *headroom*.** If the task is
easy (raw input already linearly separable — flat-MLP MNIST/digits, where pixels probe ~0.92), even the
shallow/GD-hidden reference is flat-high and there is *nothing for depth to climb*. P2.1's effect would be
invisible. So the depth curves need a task where **shallow features are insufficient and the GD-hidden
reference sits well above the layer-norm baseline** (measurable headroom).

| Knob | Locked to | Note |
| --- | --- | --- |
| **Depth-curve task** | **Tier-B compositional** (many overlapping clusters, XOR-like label, tunable difficulty — Phase-1 §1.5) **+ a real-data confirm: CIFAR-10 as flat-MLP** (the Trifecta's own depth-needing task) | difficulty dialed so GD-hidden ≫ layer-norm baseline = headroom; *not* flat MNIST. **CIFAR here is a flat-MLP depth *probe*, not a benchmark claim** — no conv front-end, no leaderboard chasing; it sits in Phase-1's "one small real probe" carve-out, *not* the "external benchmark as the claim" prohibition (CLAUDE.md scope). |
| **Continual-veto task** | **class-incremental** (digits/MNIST waves, exact exp4 setup) | the veto must test the regime where the Phase-1 win lives |
| Depth sweep | `L = 1…8` SCFF layers, **width fixed** for the depth curve; a separate **width×depth** grid for F6⁺ | one axis at a time |
| Seeds | `[42, 137, 271, 314, 1729]`, median + IQR | per Phase-1 methodology |
| Probe | logistic, fixed L2 `C=1.0`, frozen 2k/2k split, to convergence (per `result-format.md`) | the pinned ground-truth metric |
| Realism | ideal floats; online single-sample where a lever claims it; **no** analog/PVT yet | substrate-feasibility is *tested* (P2.6), realism added later |

---

## 3. The experiment ladder (aims + numeric pass gates)

Each rung: **question → hypothesis → varied → mechanism (math kept) → why → pass gate.** Control in every
rung = the Phase-1 layer-norm degradation curve + the pure-GD ceiling. Pass-gate numbers are *provisional*
(the first runs set the exact bars), but the *shape* of the bar is fixed now.

### P2.0 — Re-establish the wall + the decisive test *(the locked first run)*
- **Question.** (a) Reproduce the degradation cleanly as the curve every lever must bend up. (b) Is class
  info **lost** or merely **entangled**? (c) How big is the narrow-deep vs wide-shallow gap?
- **Locked config.** Tier-B task (above); SCFF `L=1…8`, width 64, sum-goodness, layer-norm, two-sided θ=2.0,
  all-layer tap; seeds `[42,137,271,314,1729]`.
- **Decisive test (DECIDE).** Train a **max-power readout** (deep MLP, to convergence) on **frozen deep SCFF
  features** vs **pure-GD**. < GD by > 0.05 → **lost** (fixes must *preserve*: norm). ≈ GD → **entangled**
  (fixes must *disentangle*: interface). This **routes the whole phase.**
- **Width×depth control (F6⁺).** (width × depth) at fixed budget: wide-shallow (≈2000×2) vs narrow-deep
  (≈64×6). The gap = the Phase-2 target.
- **Pass gate.** Wall reproduced (depth-slope `< 0` under layer-norm); DECIDE returns an unambiguous
  lost/entangled verdict; the width×depth gap is a single number to close.

### P2.1 — The normalization × goodness grid *(the make-or-break, sub-aim A)*
- **Question.** Does per-layer separability **rise** with depth under a different normalization **and/or
  goodness form** — and does the **online / per-sample (substrate-feasible)** version keep it? *(Widened from a
  pure-norm sweep 2026-06-21: DeeperForward shows the norm and the goodness form are coupled — see
  [`exp0/experiment-0.md`](exp0/experiment-0.md) + [`../../ref/deeperforward.md`](../../ref/deeperforward.md).)*
- **Varied — the grid `{ goodness } × { norm }`, one cell at a time.** *Goodness:* `squared Σh²` (baseline) ·
  **`linear Σh`** (DeeperForward — no `h`-factor in the update, so quiet units keep learning). *Norm:*
  `length-norm h/‖h‖` (baseline wall) · **`layer-norm (h−μ)/σ`** (per-sample, **mean-zero** → linear goodness
  decouples for free, **no batch stats** — the substrate-native cell) · `batch-norm` · **`online/streaming-BN`**
  · `group-norm` · `no-norm` (cheat control — should fail). The two corners that matter: **length-norm+squared**
  (the wall) vs **layer-norm+linear** (the substrate-native DeeperForward fix).
- **Mechanism / math.** length-norm: `ĥ=h/‖h‖`. layer-norm: `ĥ_j=(h_j−μ)/√(σ²+ε)` per **sample** (mean-zero).
  BN: `ĥ_j=(h_j−μ_j)/√(σ_j²+ε)` per **feature** over the batch. **Online-BN:** `μ_j←(1−ρ)μ_j+ρh_j`,
  `σ_j²←(1−ρ)σ_j²+ρ(h_j−μ_j)²` (running stats — the chip's `⟨a²⟩` register *is* `σ_j²`). **Goodness:** squared
  `dG/dz=2·gs·h` (the `h`-factor → deactivation cascade with depth) vs linear `dG/dz=gs·1[z>0]` (mask → no
  deactivation). *(Smoke-confirmed 2026-06-21: squared → dead-units 0→0.39 over 8 layers; linear → ~0.05.)*
- **Why.** The headline. If online-BN bends the curve up, the cheap-depth-on-chip thesis is alive.
- **Pass gate (numeric, make-or-break).** At least one variant takes the **depth-slope from `< 0` (layer-norm)
  to `≥ 0`** (separability non-declining with depth), and the **substrate-feasible online-BN's final-layer
  probe is within `0.03` of batch-BN** (i.e. the online version doesn't forfeit the gain). **If no variant
  reaches slope `≥ 0`, STOP** and rethink before P2.2+.

### P2.2 — The objective: loss form *and* negative quality *(sub-aim A, the root)*
- **Question.** Past the transmission fix, can we make the SCFF *objective* class-aligned?
- **Varied.** (i) `two-sided θ` → `SymBa / pure-contrast`. (ii) negatives: `random-batch` → **`hard / class-
  aware`** (`x_neg=x_k+prototype-from-a-different-LUT-cluster`).
- **Mechanism / math.** SymBa: `L=log(1+exp(−(g_pos−g_neg)))`. Hard-neg makes "blend=low goodness" mean
  "**between-class region = low goodness**" → goodness separates *classes*.
- **Why.** P2.1 stops depth *erasing* class info; P2.2 makes SCFF *build* it — orthogonal, probably multiply.
- **Pass gate.** Either lever lifts the final-layer probe over P2.1 by **more than the IQR** (a real gain),
  *or* it's logged as "no effect beyond the norm fix" (a real result for the substrate budget).

### P2.3 — Cross-layer collaboration *(the "connect a bit", A↔B bridge)*
- **Question.** Do layers build **redundant** features? Does letting them see each other make them
  **complementary** so GD reads better?
- **Varied.** `independent` · **shared-goodness γ** · **OLU** · both.
- **Mechanism / math.** γ: `p_i(pos)=σ(‖f_{1:i}‖²+Γ−θ)`, `Γ=Σ_{t≠i}‖f_{1:t}‖²` **detached** (stays local).
  OLU: layer alternates own-goodness / successor-goodness.
- **Why.** γ is one broadcast scalar (a hormone) — the cheapest "global awareness."
- **Pass gate.** Inter-layer **CKA redundancy drops** *and* the tapped-readout improves (disjoint IQR vs P2.1).

### P2.4 — The GD input interface *(sub-aim B)*
- **Question.** Given a depth-fixed SCFF, what is the **cheapest GD entry** that reads it well?
- **Varied.** `all-layer tap` · `learned tap-weighting` (`read=Σ_l α_l ĥ_l`) · **`deep supervision`**
  (per-layer `o_l=W_l ĥ_l`, `Σ_l λ_l·CE(o_l,y)`) · `single deep-layer read`.
- **Why.** Deep supervision is the elegant case — it gives SCFF a class-force (A) *and* GD a clean per-layer
  entry (B) at once.
- **Pass gate.** An interface reaches **within `0.02` of all-tap at lower read cost**, *or* deep-supervision
  **beats** all-tap (disjoint IQR) — naming the cheapest sufficient entry.

### P2.5 — Multi-block = SCFF with GD *between*
- **Question.** Does a GD checkpoint **between** SCFF groups let the stack go *deeper* than pure SCFF — by
  periodically **re-aligning features to class** (a "class-alignment reset")?
- **Hypothesis.** `[SCFF×k → GD-realign → SCFF×k → …]`: each reset re-injects the label direction SCFF sheds,
  so the next group starts class-aligned → depth compounds.
- **Varied.** block size `k` · #blocks · GD-realign *reads* vs *writes* (stop-grad tap vs coshape). Vs
  pure-deep-SCFF (P2.1–3) at **equal cost**.
- **Why.** This *is* multi-block efficiency — the same axis as SCFF depth, now a concrete knob `k`. Connects
  to Phase-1 exp3 but asks **depth-gain**, not just ensemble.
- **Pass gate.** Some `k` beats pure-deep-SCFF at equal weight budget (disjoint IQR), giving the **GD-between
  cadence**.

### P2.6 — The substrate filter + the veto *(the real deliverable)*
- **Question.** Which winning levers **survive single-sample-online + analog**, at what cost — and do they
  **preserve the Phase-1 continual win**?
- **Checks.** online-BN (running stats on `⟨a²⟩`/momentum) · γ (one wire) · OLU (2-layer state) · hard-negs
  (LUT, built) · deep-supervision (readout area). Each surviving lever → SUBSTRATE table (Scaps / registers /
  wires / online? / continual-safe?).
- **The veto (non-negotiable).** Re-run exp4 (continual + sleep) **with the depth-fix in**; report **ACC +
  BWT**. **A lever that lifts static depth but worsens BWT is rejected** (see *Continual Normalization* — BN
  stats rot under task shift). **Do not trade the continual win for static depth.**
- **Hand-off to Phase 3 — *measure* drift, don't *build* the gate.** Log each algorithm's drift (feature
  movement/step + re-track cost) — the raw material the **Phase-3 gate** is tuned against. We measure here;
  Phase 3 builds.
- **Pass gate.** At least one **fully-online** lever-set holds **depth-slope `≥ 0` AND `BWT ≥` the Phase-1
  baseline** — that set is what carries to Phase 3.

---

## 4. The success criterion

> **Narrow-deep** SCFF (substrate regime) + the surviving fixes **≥ wide-shallow** SCFF (paper regime) at
> equal weight budget, *with depth genuinely helping* (probe slope `≥ 0`), *while staying single-sample-online
> and continual-robust (BWT preserved).*

If P2.1 (online-BN) alone bends the curve up, that's the result; P2.2–2.5 are how much further; P2.6 is what
survives on the chip.

## 5. Order to build (cheapest-information-first)

P2.0 (wall + DECIDE) → **P2.1 (online-BN — the make-or-break gate)** → P2.2 (objective) → P2.3 (γ/OLU) →
P2.4 (interface) → P2.5 (GD-between) → P2.6 (substrate + veto). **P2.1 is the gate: if no normalization
variant reaches depth-slope `≥ 0`, stop and rethink before building the rest.**

## 6. What to build (component checklist)

New primitives this phase introduces (so an agent can pick it up cold):

- **Online/streaming batch-norm** — per-feature running `μ_j,σ_j²` (EMA), normalize at batch size 1; the
  `⟨a²⟩` register reuse. *(P2.1, the core.)*
- **Normalization bench** — LN / BN / online-BN / group-norm / no-norm behind one switch, so the depth curve
  swaps cleanly.
- **SymBa / pure-contrast loss** + the **hard-negative LUT sampler** — the first real use of the LUT for
  *negatives* (Phase 1 stubbed it; Ch4 intends cross-cluster mixing). *(P2.2.)*
- **γ broadcast scalar** (detached total goodness) and **OLU pairing** (overlapping local updates). *(P2.3.)*
- **GD interface bench** — all-tap / learned-α / deep-supervision (per-layer readouts) / single-read. *(P2.4.)*
- **GD-between block harness** — `[SCFF×k → GD-realign]×N` on a stream, read-vs-write switch. *(P2.5.)*
- **Metrics + harness** — depth-curve probe, CKA/effective-rank/Fisher/NCC, the drift logger, continual
  ACC/BWT, the width×depth grid — all per `result-format.md`; figures via a `plot.py` from saved arrays.

## 7. Where to record results

One folder per experiment under `draft6.0/src/phase2/` (`exp0/`, `exp1/`, …), each an `experiment-N.md` with
the spine **question → setup → run → result → read → decision** (the *read* uses `result-format.md`'s
6+2-slot template). The phase-wide synthesis lives in a **`RESULTS.md` ledger** (one row per rung: scalar →
lever set → decision fed), filled the moment a rung's decision is made — exactly the Phase-1 discipline.

## 8. The phase map (renumbered) + what's out

**The renumber (2026-06-20).** "Phase 2" previously meant the recurrent brain in `CLAUDE.md` / `main.ideas`;
that collided with this folder. Resolved across every **live** doc — CLAUDE.md (routing + scope),
`main.ideas.v1.md`, `context.md`, the `skill/` maps, and memory (historical `draft/` & `project-history.md`
keep their period usage on purpose):

| phase | scope | status |
| --- | --- | --- |
| **Phase 1** | structure: SCFF, block, chain, **+ sleep** (the continual win) | **done** (exp0–exp4) |
| **Phase 2** | *this* — depth round 1: can a deep *energy-goodness* SCFF stack earn depth? (no) | **done** (P2.0/1/2/5/6; P2.3/4 skipped) — see [`phase2-summarize.md`](phase2-summarize.md) |
| **Phase 3** | depth round 2 — **the objective reframe** (energy → masked-feature reconstruction; the wall is intrinsic to the *energy objective*, not locality) | **active** — see [`../phase3/README.md`](../phase3/README.md) + [`../../ref2/`](../../ref2/README.md) |
| **Phase 4** | **online maintenance** — the **Ch7 gate** (in-time GD trigger) + **sleep-*cadence* refinement** + the lifelong loop (*was "Phase 3"*) | future |
| **north star** | the recurrent lifelong-learning brain (prefrontal↔hippocampus) | beyond the numbers; deliberately unspecced |

**Sleep is already built and validated (Phase-1 exp4) — it is *not* maintenance-phase work.** The maintenance
phase (now **Phase 4**) *refines its cadence* (how little/often) and *adds the gate*; it does not invent sleep.
The gate is deferred to Phase 4 because it is a *temporal* mechanism whose tuning depends on the drift each
depth-phase algorithm produces — Phase 2 only **measures** that drift (P2.6).

**Out of Phase 2:** the Ch7 gate (→ Phase 3) · final architecture decisions (options-open research) ·
analog/PVT/SPICE realism (after the ideal depth-fix converges).

## 9. Open questions seeded for the runs

- **Lost or entangled?** (P2.0 DECIDE → which lever family to trust.)
- Does **online** BN keep batch-BN's gain, or does the running-stats lag kill it?
- Do **hard negatives** alone (no norm change) already realign deep features — objective vs transmission? (P2.1×P2.2.)
- How often must **GD sit between** SCFF (`k`), and is a *reading* GD enough or must it *write*? (P2.5.)
- Does any depth-fix **cost the continual win**? (P2.6 veto.)

## 10. References (the canonical list)

- **The Trifecta: three simple techniques for deeper FF** — [arXiv 2311.18130](https://arxiv.org/abs/2311.18130). BatchNorm + SymBa + OLU; layer-norm is the depth-killer. *The central paper.*
- **DeeperForward: Enhanced Forward-Forward** — [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/7dd309df03d37643b96f5048b44da798-Paper-Conference.pdf). *Counter-finding:* the depth-killer is **squared goodness** (deactivates neurons), not layer-norm — keep the per-sample norm, switch goodness squared→linear → 17-layer FF. The substrate-native route. Story: [`../../ref/deeperforward.md`](../../ref/deeperforward.md). **Co-central for Phase 2.**
- **Layer Collaboration in the Forward-Forward Algorithm** — [arXiv 2305.12393](https://arxiv.org/abs/2305.12393) (AAAI 2024). Shared detached goodness γ.
- **SymBa** (Lee & Song, 2023) — symmetric/separation loss = pure-contrast.
- **Streaming Normalization** — [CBMM-057](https://cbmm.mit.edu/sites/default/files/publications/CBMM-Memo-057.pdf); **Online Normalization** (Chiley 2019); **Batch Renormalization** (Ioffe 2017) — running-stats norm at batch 1.
- **Continual Normalization** (ICLR 2022) — norm under task shift; the veto check.
- **Deeply-Supervised Nets** (Lee 2015) — per-layer auxiliary readouts (the GD interface).
- *Carry-over:* Distance-Forward (DF-O) · BoostResNet · the SCFF paper · Phase-1 exp0–exp4.
