# Phase 10 papers — the validation / showcase slice (the fair fight + the gauntlet + the Pareto)

> The literature Phase 10 stands on: the **fair same-budget** continual baseline (and why it is *hard*), the **CL metric**
> provenance, the **three-scenario** framing for the multi-domain gauntlet, the **online / anytime** eval convention, and
> the **accuracy-vs-energy Pareto** presentation. Phase 10 races the frozen object (`59d2720`, grid-4) — it builds *no new
> model*, so this slice is thinner than P7–P9's: it is about **how to judge fairly**, not what to build. Written as the
> deep-research delta answering the author's question: **"did our earlier rough plan cover all of Phase 10, and is there a
> better choice?"** (2026-07-03.)

---

## 0 · The headline the research changed — the fair baseline is *strong*, and the budget is FLOPs + bytes

The rough plan said "race BP+replay (ER / A-GEM / DER++), matched buffer + compute." The research **sharpened the
methodology and raised the bar**:

- **Computationally Budgeted Continual Learning** (Prabhu et al., CVPR 2023 — [2303.11165](https://arxiv.org/abs/2303.11165)):
  the budget must be **FLOPs-per-sample (compute) + total memory in Bytes (storage)**, matched across methods; and under
  that budget, **a naive experience-replay (ER) baseline outperforms the fancy CL methods.** So our opponent is **not** a
  weak strawman to beat easily — a *well-tuned ER at matched budget* is the strong baseline. The anti-strawman guard must
  match **FLOPs/sample + bytes**, not "buffer size" alone.
- **Real-Time Evaluation in Online CL: A New Hope** (Ghunaim et al., CVPR 2023 — [2302.01047](https://arxiv.org/abs/2302.01047)):
  in a **real-time** stream that *does not wait for the model to finish training*, a simple ER baseline again beats SOTA —
  because expensive per-step training **falls behind the stream.** This is the regime our gated, backward-pass-free economy
  is *built for*: a cheap learner keeps up where per-step BP cannot. It is the motivating frame for the money figure — and,
  after the lab-manager review (B3), **throughput / steps-behind is adopted as a *measured* read** in the gauntlet, not just
  cited (cash the motivation, don't only reference it).
- **Budgeted Online CL** (ICLR 2025 — [2410.15143](https://arxiv.org/abs/2410.15143)): confirms the FLOPs+bytes budget
  framing; adaptive layer-freezing / frequency-based sampling as the budgeted-OCL SOTA (a stronger control if wanted).

**Verdict:** the rough plan *undersold the opponent.* The fight is honest only if ER is (a) budgeted in FLOPs/sample +
bytes and (b) tuned, not crippled. This is now the load-bearing spec of the racer's guard.

---

## 1 · The baseline family (what to race, and why each earns a slot)

| baseline | ref | role in P10 | budget note |
| --- | --- | --- | --- |
| **ER** (experience replay, reservoir) | Rolnick et al. [1811.11682](https://arxiv.org/abs/1811.11682) | **the honest same-budget racer** — the strong one (Prabhu) | matched FLOPs/sample + bytes; **mandatory** |
| **A-GEM** | Chaudhry et al. [1812.00420](https://arxiv.org/abs/1812.00420) | the **compute-efficient** replay variant (one extra grad projection) | cheaper per step than ER — a different point on the cost axis |
| **DER++** | Buzzega et al., NeurIPS 2020 [2004.07211](https://arxiv.org/abs/2004.07211) | the **stronger-modern** replay control (logit distillation) | stores logits too — bytes budget must count them (Prabhu's warning); **its distillation adds a forward → higher FLOPs/sample** (A5 — the FLOPs axis is not equal across the roster) |
| **GDumb** | Prabhu, Torr & Dokania, ECCV 2020 | the **"questions our progress" sanity control** — greedy-balanced buffer + train-from-scratch-at-eval | memory-matched; **cost-pathological at eval** → reported on the **accuracy axis** (its intended role), energy-annotated *not an energy competitor* (A3 — never used to inflate the Pareto) |
| **naive online-BP** (no replay) | — | the **forgetting floor** (Phase 4's old opponent — kept only as the floor, never the headline) | — |

The existential headline = **OURS(grid-4) vs ER at matched FLOPs/sample + bytes.** A-GEM / DER++ / GDumb populate the
Pareto field; naive-BP is the floor line. GSS and other gradient-buffer methods are out (need gradients our namer lacks —
and they lose under budget anyway, Prabhu).

---

## 2 · The metric provenance (we are reporting the field's standard)

- **ACC / AA · BWT · FWT** — Lopez-Paz & Ranzato, **GEM** (NeurIPS 2017 — [1706.08840](https://arxiv.org/abs/1706.08840)):
  the acc-matrix conventions the repo already implements (`acc_matrix_metrics`). BWT < 0 = forgetting; FWT = does old
  learning help new tasks.
- **Forgetting Measure** — Chaudhry et al. (Riemannian Walk, ECCV 2018 — [1801.10112](https://arxiv.org/abs/1801.10112)):
  per-task max-minus-final; the "1-back" and "all-prev" reads map here.
- **Average Anytime Accuracy (AAA / AAP)** — the online-CL convention (avg accuracy after *each* minibatch, not just at
  stream end). **Origin: OSAKA** (Caccia et al., NeurIPS 2020 — [2003.05856](https://arxiv.org/abs/2003.05856), which
  introduced measuring performance *cumulatively during* the introduction of new tasks, not only after exposure);
  the reporting-convention anchor is "A Comprehensive Empirical Evaluation on Online CL" ([2308.10328](https://arxiv.org/abs/2308.10328))
  (A1 — the origin was previously misattributed to [2308.10328]). **Add AAA beside final AA** — the online read the rough plan
  under-specified. Pinned formula (result-format §B): AAA = mean over stream-checkpoints of AA(t), AA(t) = mean acc over
  tasks-seen-so-far at checkpoint t.
- **"More than forgetting"** — Díaz-Rodríguez et al. [1810.13166](https://arxiv.org/abs/1810.13166): the reminder to report
  plasticity / transfer / efficiency, not forgetting alone — exactly the author's new/1-back/all-prev + cost quartet.

**Verdict:** the rough plan's metric list (ACC/BWT/FWT + plasticity + cost) is correct and standard; the one addition is
**AAA (anytime)** alongside final AA.

---

## 3 · The gauntlet — the scenario name, and the honest construction

- **The three scenarios** — van de Ven, Tuytelaars & Tolias, "Three types of incremental learning" (Nature Machine
  Intelligence 2022; [1904.07734](https://arxiv.org/abs/1904.07734)): **task-IL / domain-IL / class-IL.** Our multi-domain
  gauntlet (5 datasets, *same* 10-way structure, changing input distribution, **shared single head**) is **domain-IL** —
  name it precisely. A **Split-X class-IL** run (grow the label set) is the complementary clean protocol.
- **Same input shape is mandatory** (a single frozen-config bulk has a fixed input dim = **40**): every domain must be
  projected to the shared **40-D** bulk input (seed-frozen random projection / PCA-to-40) — the "28×28 MNIST-family" framing
  is therefore partly cosmetic; the bulk never sees 784-D. **The PRIMARY protocol is native and offline-guaranteed** (review
  B2 — MNIST-family is *not* offline-loadable on this box: only MNIST is cached; no Fashion/KMNIST/notMNIST/EMNIST, no
  torchvision, network unreliable → do **not** gate P10.0 on a fetch): **Permuted-/Rotated-digits + CIFAR-flat-gray→40 + a
  synthetic Gaussian domain.** MNIST-784→40 is an **optional legibility bonus** (the one cached set), never load-bearing. The
  shared-head/shared-index construction reuses label indices with *shifting semantics* per domain (harder than
  permutation-style domain-IL — state it).

**Verdict:** the rough gauntlet is right in spirit; the research + review add the precise **domain-IL** label
(shifting-semantics noted), the shared-head / shared **40-D** constraint, and — after the review — **native domain-IL as the
PRIMARY protocol** (MNIST-family a legibility bonus, not the runnable path).

---

## 4 · The Pareto / cost-aware presentation

- Accuracy-vs-compute/energy **bi-objective Pareto** is the standard way to present a cost-aware learner; the efficiency
  read is the **normalized distance to the ideal (max-acc, min-energy) corner.** (Efficient-ML / budgeted-CL surveys;
  compute-accuracy Pareto is now routine.) Our money figure = the retention curve + the cumulative-energy curve, with the
  **{OURS-analog, OURS-digital} vs {GD-digital, GD-analog}** substrate split from P8.7 re-metered across the stream.
  **The load-bearing, honestly-contestable energy comparison is same-substrate** (`E(OURS-digital)` vs `E(ER-digital)` = the
  *algorithm* win; review R1) — because the analog substrate prices crossbar MACs near-zero *by construction of the meter*, so
  `E(OURS-analog) < E(GD-digital)` is largely guaranteed before the run and is reported as a **meter-structural floor** overlay
  (the "money" total = substrate × algorithm), never as the contestable claim.
- **Energy anchors** (carried from P8, unchanged — behavioral, not SPICE): Horowitz (ISSCC 2014) for digital MAC/memory;
  DNN+NeuroSim, ISAAC (ISCA'16), PUMA (ASPLOS'19), AIHWKit for the analog CIM meter. No newer anchor needed — the P8.7
  accounting stands across a lifelong stream (energy is per-op and additive; integrate over the stream).

---

## 5 · What the research did NOT change (checked, kept)

- The **frozen object** and the **freeze discipline** (freeze in P9, judge in P10) — standard train/val hygiene, unchanged.
- The **substrate 2×2** accounting (P8.7) — still the right frame; just re-metered per-domain / cumulative.
- The **spine** in the noise showcase (directional retention, not per-sample cosine) — Phase-6 result, unchanged.
- **REMIND** (replay into a frozen backbone) stays the **anti-pattern** our split is defined against (our backbone is
  unsupervised and *rotates-not-forgets*, so only the tiny readout replays) — [1910.02509](https://arxiv.org/abs/1910.02509).

---

## 6 · The five deltas folded into `../../src/phase10/design.md`

| # | the rough-plan guess | what the research changed |
| --- | --- | --- |
| D1 | "race BP+replay, matched buffer + compute" | budget = **FLOPs/sample + bytes**; ER is the **strong** baseline (Prabhu); the guard matches FLOPs+bytes, ER is **tuned** |
| D2 | "ER / A-GEM / DER++" | add **GDumb** (the progress-questioning sanity control) + **naive-BP floor**; DER++ bytes must count stored logits |
| D3 | "ACC/BWT/FWT + plasticity" | add **AAA (anytime accuracy)** beside final AA — the online-CL standard |
| D4 | "5-domain 28×28 sequence" | name it **domain-IL** (van de Ven); shared-head + shared **40-D** constraint; **native domain-IL is the PRIMARY protocol** (MNIST-family a legibility bonus — data risk) |
| D5 | "cumulative cost curve" | frame as an **accuracy-vs-energy Pareto** (normalized-distance efficiency); the real-time-eval (Ghunaim) motivation for why a cheap learner wins the stream |

> **Post-research refinement (the 3-agent lab-manager review, folded 2026-07-03 — full ledger in [`../../../src/phase10/design.md`](../../../src/phase10/design.md) §8).**
> The review stress-tested this delta from three cold-start lenses (repo-fit · red-team · literature) and sharpened five
> things it touches: (R1) the load-bearing energy cut is **same-substrate** (analog is a meter-structural floor); (A1) AAA
> **origin = OSAKA** (§2, fixed above); (B2) **native domain-IL is the PRIMARY protocol**, all domains projected to the shared
> **40-D** bulk input (§3, fixed above); (B3) **throughput / steps-behind is a measured read** (§0, above); (A3/A5) **GDumb is
> an accuracy-axis control** (cost-pathological) and **DER++ carries a higher FLOPs/sample** (§1, above). This paper is the
> research record; `design.md` §8 is the binding decision ledger.

---

*Sources:* [Prabhu 2023 budgeted-CL](https://arxiv.org/abs/2303.11165) · [Ghunaim 2023 real-time-eval](https://arxiv.org/abs/2302.01047)
· [Budgeted OCL ICLR'25](https://arxiv.org/abs/2410.15143) · [van de Ven three scenarios](https://arxiv.org/abs/1904.07734)
· [GEM / Lopez-Paz & Ranzato](https://arxiv.org/abs/1706.08840) · [A-GEM / Chaudhry](https://arxiv.org/abs/1812.00420)
· [DER++ / Buzzega](https://arxiv.org/abs/2004.07211) · GDumb / Prabhu (ECCV 2020)
· [ER / Rolnick](https://arxiv.org/abs/1811.11682) · [Online-CL eval / AAA](https://arxiv.org/abs/2308.10328)
· [More-than-forgetting](https://arxiv.org/abs/1810.13166) · [REMIND anti-pattern](https://arxiv.org/abs/1910.02509).
Energy anchors (carried from P8): Horowitz ISSCC'14 · NeuroSim · ISAAC ISCA'16 · PUMA ASPLOS'19 · AIHWKit.
