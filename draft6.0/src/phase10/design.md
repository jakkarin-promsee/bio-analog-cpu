# Phase 10 — The validation: race the whole object across the lifelong gauntlet (the showcase plan)

> **Status: 🌱 ROUGH / IDEAS-FIRST (sketched 2026-07-02, nothing run, nothing committed).** The *first map* of Phase 10 —
> the Stage-2 close-out, where the **frozen** two-brain object (handed over by Phase 9) is raced against a **fair** BP
> baseline across the full continual gauntlet: a multi-domain adaptive sequence, the noise environments, and the honest
> cost fight. This is **the document the professor reads** — so its job is not to *tune* anything (the object is locked)
> but to *show, honestly, where the complete architecture wins, ties, and loses.* When the rungs firm up (research
> session), this hardens into the normal per-phase `design.md` + `expK/` ladder + a `research/papers/phase10/` folder.
>
> The frozen object it races: [`../phase9/design.md`](../phase9/design.md) → the P9 freeze commit. The founding claim it
> tests: [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) (the 80/20 continual bet). The economy + meter it
> carries: [`../phase8/README.md`](../phase8/README.md). The Stage-2 map: [`../stage2-design.md`](../stage2-design.md) §4.
> House style: [`../result-format.md`](../result-format.md).
>
> **Phase 10 = the fourth and last Stage-2 phase** (P7 readout ✓ · P8 economy ✓ · P9 close ✓ · **P10 validation /
> showcase**). Bar set with the author: **professor-convinced / showcase** — one fair baseline *family*, a legible
> gauntlet, an honest Pareto verdict. **Not** a SOTA-benchmark chase (the project is explicitly *not a benchmark-beat*).

---

## 0 · Why Phase 10 exists — the one existential hole, and the showcase that fills it

### 0.0 The arc — everything is built; nothing is yet *validated as one object* against a fair opponent

Seven phases characterized *pieces*. The founding claim is a whole-system bet: **"an 80/20 forward-only continual learner
that beats backprop's economics *and* accuracy."** Phase 8 settled the **economics** (OURS ≈ half the energy of BP+replay;
15× vs GD-on-digital). But every continual **accuracy** win to date — Phase 1, Phase 4, the P8 live-safety check — was
measured against **naive online-BP with no replay.** That is a strawman, and it is the *first* thing an outside reviewer
attacks: *"of course you beat BP-with-no-memory; race a real continual learner."* Until the frozen object races **BP + a
replay buffer at matched budget** on **accuracy**, the headline is *supported, not validated.*

So Phase 10 is not a victory lap — it is the **thesis defense**, and it has three jobs:

1. **The existential fight** — OURS vs a *fair* BP+replay baseline, on **accuracy × energy**, continual. Load-bearing.
2. **The adaptive showcase** — the multi-domain lifelong gauntlet: *watch it learn five different worlds in a row, not
   forget the old ones, and do it cheaper than BP.* The money figure — the whole thesis in one animation.
3. **The noise showcase** — the gauntlet under analog/eval noise (the A7 → Phase-6 arc, now on the assembled object):
   *where a naive learner degrades, the noise-hardened cell holds.* The Phase-6 investment, cashed in publicly.

### 0.1 The one discipline — the object is FROZEN (inherited from P9 §0.1)

Phase 10 **measures; it does not tune.** The loop was locked at the P9 freeze commit *before* any baseline number was
seen. Touching a single knob here (a cadence, an N2 rate, an eviction bound) to improve a comparison invalidates the
fight — it is *tuning-to-win*. The verdict cuts are **pinned BLIND** before the racer runs. This is what lets the
close-out answer *"did you tune against the baseline?"* with the commit hash.

### 0.2 What Phase 10 is NOT — the scope guard

- **NOT tuning.** The object is frozen. Any knob-touch → the fight is void.
- **NOT a benchmark-beat / SOTA chase.** Professor-convinced bar: **one fair baseline family** (BP+replay — ER as the
  honest same-budget racer; A-GEM as the efficient variant; DER++ optional as a stronger-modern control), a **legible
  gauntlet** (≈5 domains, drop-in input shape), an **honest Pareto** verdict. Not ImageNet, not a 20-baseline table.
- **NOT re-opening SCFF or the Namer.** Both committed and frozen (Stage 1 / P7–P8).
- **NOT SPICE / device physics.** Behavioral ADC-centred meter, carried from P8 (analog + digital substrate axes).
- **The fight can LOSE — and that is a valid result.** BP+replay may edge us on raw accuracy. If so, the deliverable is
  the **Pareto story** (half the energy, 15× vs digital-GD, at competitive-not-superior accuracy is still a strong chip
  claim). We pin the verdict to report *either way* — that willingness is what makes the win credible.

---

## 1 · The spine and the envelope (unchanged)

**The spine — read the class DIRECTION, never a MAGNITUDE.** In Phase 10 it lives in the **noise showcase**: the
dangerous analog enemy is a *coherent directional shift* along the class axis (Phase 6), so the retention read (not
per-sample cosine) is the direction measurement, and the noise-hardened cell's advantage is *directional* by
construction. density ≠ class, cashed in on the assembled object.

**The envelope — GD reads taps, never writes SCFF.** Unbroken; the frozen object already obeys it.

**Guards first.** The fair-baseline racer (`race_bp` + replay) ships with its own equivalence/budget guard (matched
buffer, matched compute, same per-op energy table — no strawman by construction). **Any guard fails → STOP.**

---

## 2 · The three showcases (the deliverables)

### 2.1 Deliverable A — the existential fight (the load-bearing number)

**OURS (frozen) vs `race_bp` + replay at matched buffer + matched compute**, on **accuracy AND energy**, continual
regime. The honest baseline is **BP+replay** (ER / A-GEM — replay *gradients through the whole net*; we replay *one
forward pass into a small head*), metered on the **identical per-op energy table** as P8. We may still win — only the
readout replays and the bulk doesn't forget — but we **show** it. The primary read is the **Pareto point**: (accuracy,
energy) for OURS vs BP+replay. Pinned cut BLIND: `δ_acc = 0.02`, paired by seed, the P8 house bar.

### 2.2 Deliverable B — the multi-domain adaptive gauntlet (the money figure)

A sequence of **≈5 distinct datasets / domains** presented in phases (the author's "5 phases of different datasets"),
same input shape so it is a drop-in flat-vector stream in the numpy sim (no convolution). At each phase, measure — the
author's four asks, mapped to the standard continual-learning metrics (GEM / Lopez-Paz & Ranzato ACC/BWT/FWT):

| the author's ask | the CL metric | what it shows |
| --- | --- | --- |
| accuracy on the **new** dataset | **plasticity** (acc on task *t* right after learning *t*) | can it still *learn* after many tasks? |
| accuracy on **1 previous** dataset | **1-back retention** (acc on *t−1* after learning *t*) | immediate forgetting |
| accuracy on **all previous** datasets | **Average Accuracy (ACC)** + **Forgetting / BWT** over all seen tasks | the lifelong retention curve — the headline |
| **compute cost** OURS vs BP | **cumulative energy** (the P8 meter, integrated over the stream) | the 80/20, cashed over a lifetime |

**The money figure:** the all-previous retention curve *and* the cumulative-cost curve, OURS vs BP+replay, across the 5
domains — the thesis in one picture. **Candidate gauntlets (research session picks / combines):** a **domain-incremental**
grayscale-28×28 sequence (MNIST → Fashion-MNIST → KMNIST → notMNIST → EMNIST-letters — genuinely different worlds, same
shape → the strongest "watch it adapt" story) and/or **Split-MNIST** class-incremental (5 tasks × 2 classes — the clean
CL-protocol variant). This rung also reports **how the SCFF:Namer energy ratio moves across the gauntlet** (does the
namer's GD-share grow on harder / multi-domain streams, or hold near the P8 0.12?) — the "final ratio," characterized
rather than assumed.

### 2.3 Deliverable C — the noise showcase (the Phase-6 arc, cashed in)

Run the gauntlet under a taxonomy of **environments** (carry Phase 6's behavioral analog-noise model + Phase 9's
read-side calibration): **clean · iid weight/tap noise · directional coherent shift (the lethal one) · ADC quantization
(< 3-bit) · high nuisance-dim.** Three learners on each: **OURS-hardened** (`NoiseAugContrast` + P9.4 read-side) vs
**BP+replay** vs **naive-online** (the forgetting floor). The read: the noise-hardened cell holds retention where the
others degrade — *and* the advantage is directional (the substrate's dominant mismatch is directional too), so the
showcase demonstrates the design protecting the very class-direction it exists to protect.

### 2.4 The verdict — the Pareto frontier + the assembled-object figure

Not a single win/lose scalar — the **Pareto frontier** across (accuracy, energy, retention, noise-robustness), OURS vs
the field, on the frozen object. Where we win (continual retention, cost, nuisance-dim, noise-directional), where we tie
(static accuracy on kind data), where we lose (raw static difficulty, many classes — stated plainly). This is the
close-out a professor reads.

---

## 3 · The ladder — P10.0 → P10.5 (rough; each states its read-including-failure)

| rung | question | rough read (incl. failure) — *pinned BLIND in the research session* |
| --- | --- | --- |
| **P10.0** — bench: the **fair racer** + the gauntlet harness | Is the BP+replay baseline genuinely fair, and is the object genuinely frozen? | Build `race_bp`+replay (ER/A-GEM, matched buffer+compute, same energy table) + the multi-domain harness. **Freeze-check:** assert the P9 commit hash. *Read:* racer passes the budget guard (fair) / the harness or freeze is wrong → STOP. |
| **P10.1** — **the existential fight** | Does OURS match/beat BP+replay on accuracy at its metered energy? | OURS vs BP+replay, accuracy × energy, continual home, 5 seeds. *Read:* OURS on/above the Pareto frontier (the headline win) / OURS below on accuracy but far cheaper (the honest Pareto — report it) / OURS dominated (the founding bet fails — the headline, reported). |
| **P10.2** — **the multi-domain gauntlet** (money figure) | Does it learn 5 worlds without forgetting, cheaper than BP? | new / 1-back / all-prev accuracy + cumulative cost, OURS vs BP+replay, across ≈5 domains. + the SCFF:Namer ratio across difficulty. *Read:* flat retention at low cost (the showcase) / retention decays with #domains (the scaling limit, stated) / cost creeps toward BP on hard domains (the ratio isn't scale-free — flag). |
| **P10.3** — **the noise showcase** | Does the noise-hardened cell hold where naive/BP degrade? | The gauntlet under {clean, iid, directional, ADC<3b, nuisance-dim}; OURS-hardened vs BP+replay vs naive. *Read:* OURS holds retention under the directional enemy (the Phase-6 payoff) / the read-side residual bites (named, → analog layer). |
| **P10.4** — **A5 natural multi-class** | Does the fight hold on real data, not just synthetic? | The existential fight + gauntlet on natural datasets (the synthetic overstates gaps both ways). May fold into P10.2's real-domain gauntlet. *Read:* the win/tie/loss on data a professor recognizes. |
| **P10.5** — **the Pareto verdict + the Stage-2 close-out** | Where does the whole object stand vs the field? | Assemble the frontier + the assembled-object figure; rewrite [`../stage2-report.md`](../stage2-report.md) as the **Stage-2 close-out** (the way `stage1-report.md` closed Stage 1). *Read:* the honest map — win / tie / loss, stated. |

*(The object is frozen; these rungs *measure*. Verdict cuts pinned BLIND. Heavy live cells checkpoint + single-thread +
verify PID. Seeds `[42,137,271,314,1729]`, median + IQR, paired-sign veto on retention.)*

---

## 4 · Metrics (rough — pinned in the research session)

Carry the P8 ledger; add the gauntlet + noise reads. All median + IQR, 5 seeds, reference lines (chance, ceiling,
BP+replay), captions ending in the takeaway.

| metric | rough definition | why |
| --- | --- | --- |
| **ACC / Average Accuracy** | mean acc over all seen tasks at stream end (GEM convention) | the lifelong retention headline |
| **BWT / Forgetting** | backward transfer (GEM) — retention over history | the continual win, fairly measured |
| **FWT** (bonus) | forward transfer — does old learning help new tasks? | the "adaptive" story's upside |
| **plasticity / 1-back** | acc on task *t* at *t*; acc on *t−1* at *t* | the author's new/1-previous asks |
| **cumulative energy** | the P8 ADC-centred meter integrated over the stream, OURS vs BP+replay | the 80/20 over a lifetime |
| **SCFF:Namer ratio across difficulty** | GD-share vs domain hardness | the "final ratio," characterized not assumed |
| **noise-retention** | retention vs noise level per environment, OURS vs BP vs naive | the Phase-6 payoff |

---

## 5 · What the research session must add (this file is rough on purpose)

- Create `research/papers/phase10/` — the validation slice: the fair-baseline lineage (ER Rolnick, A-GEM, DER++, GDumb;
  the ACC/BWT/FWT metric provenance — GEM/Lopez-Paz & Ranzato), the multi-domain / domain-incremental CL protocols, and
  the online-CL eval conventions (anytime accuracy / AAA) the gauntlet should report against.
- **Decide the gauntlet composition** — domain-incremental grayscale-28×28 sequence vs Split-MNIST class-incremental vs
  both; the same-input-shape constraint (numpy, flat vectors, no conv); how many domains before it stops being legible.
- **Decide the baseline set** — ER (honest same-budget) is mandatory; A-GEM (efficient) and DER++ (stronger-modern) as
  controls — how many, and the matched-budget guard that keeps each fair.
- Pin the **numeric verdict cuts BLIND** (the P8 discipline) — the Pareto acceptance shapes, `δ_acc`, the noise bands.
- Write `phase10/result-format.md` (the delta — the retention-curve + cost-curve + Pareto-frontier figures).
- Spell the `p10lib.py`-on-`p9lib` build list + guards (import, don't retype — the netlist rule), esp. the BP+replay
  racer's budget guard (the anti-strawman).

> The **floor**, per [`../result-format.md`](../result-format.md): median + IQR, 5 seeds, reference lines including the
> BP+replay racer, a caption that ends in the takeaway, a manifest that regenerates every figure. The object is frozen;
> we measure it honestly and report the frontier — win, tie, or loss.

*Up:* [Stage-2 map](../stage2-design.md) · *prev:* [Phase 9 — close & freeze](../phase9/design.md) · *next:* the Stage-2
close-out → the analog-realism layer (SPICE / PVT), and beyond the numbered phases, the north star.
