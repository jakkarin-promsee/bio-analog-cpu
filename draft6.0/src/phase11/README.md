# Phase 11 — the limit map: the frozen recipe on real data and at scale (front door)

> **Status: 🟢 COMMITTED CORE RUN (2026-07-05).** The phase the red team asked for — the P10 instrument taken to
> **harder data, real-world streams, cross-dataset streams, and scale**, run honestly, expecting and welcoming
> losses. The product is the **LIMIT-MAP**: arenas × capability channels, every cell win / tie / loss / FLOOR with
> its number. The committed object (the P9-frozen two-brain neocortex, `freeze_content` bit-exact) was measured
> untouched (Arm A, the frozen recipe through the 40-D porthole) and re-built to a pre-registered scaling rule
> (Arm B); **nothing was tuned in either arm.** ER-strong was re-tuned per arena on the disjoint seed-7 stream —
> the asymmetry runs *against* the home team.
>
> **What ran:** P11.0 (bench, all green) · P11.1 (decomposition, the pre-pitch strike) · P11.2 (MNIST rung, both
> arms) · P11.3 (real streams: gas · HAR · electricity · covertype) · P11.4 (cross-dataset MNIST→Fashion→CIFAR-gray,
> class-IL 30-way). **What did not:** Yearbook / BloodMNIST / CIFAR-100 (openml API down on this box; optional
> bonuses, out of the committed core), and P11.5–P11.8 extensions (scaling sweeps / features arena) — descoped for
> the single-session budget, named not faked. The map ships the columns that exist.

---

## The one-paragraph verdict

**The founding two-brain story survives contact with real data — but P11 sharpens *which half of it is which*.**
The decomposition (P11.1) is the headline honesty: the continual **safety** (worst-BWT ≈ 0) is largely the
**closed-form namer + gate + sleep**, not the SCFF bulk — a linear head with the same machinery forgets no more.
The SCFF **bulk** is the **nonlinear feature learner**: on data a linear namer can't crack (the synthetic home:
0.172 → 0.589, Δbulk **+0.417**, and it beats a random 12-layer reservoir → *learned*, not just depth) it is
decisive; on near-linearly-separable data (digits) it is correctly redundant. So "isn't this just SLDA?" has an
honest answer: *the safety largely is — we measured it and say so; the bulk is the nonlinear learner, and where the
data needs one it earns its place.* On real MNIST (P11.2) the frozen recipe wins **continual safety** (≈10× less
forgetting than a tuned ER), **retention on long blocks**, and **order-invariance**, while static accuracy trails
(continual-not-static, P4/P10.5 re-confirmed) — and **Arm B scales** (more input dim recovers porthole loss). On
nature's own drift (P11.3, the real-world headline) and across data *types* (P11.4) the map is drawn honestly with
its wins, its losses, and its FLOOR cells.

---

## The ladder (per-rung front doors: `expK/experiment-K.md`)

- **P11.0 — bench (all green).** 7 arenas load offline; `freeze_content` **bit-exact** (the object measured IS the
  P9-frozen object); noise-σ pinned by P10 equivalence (σ/RMS = 1.239, the F3 direction-killer caught); the
  **GD-share-vs-W shape RISES** (0.21→0.34→0.53 — the SLDA solve ~O((L·W)³); the economy does *not* improve with
  scale, refuting the temp2 guess at the meter source); dominance holds. → [`exp0/experiment-0.md`](exp0/experiment-0.md).
- **P11.1 — the decomposition ("is it just SLDA?", the pre-pitch strike).** Δbulk tracks **arena nonlinearity**:
  synth-home **+0.417**, MNIST-40 +0.008, digits −0.014; the bulk beats a random reservoir (learned structure);
  continual safety is closed-form (proj→namer forgets no more than bulk). **NARROWED-with-mechanism** — the bulk is
  the nonlinear learner, the safety is the namer. → [`exp1/experiment-1.md`](exp1/experiment-1.md) · `DECOMP.png`.
- **P11.2 — the MNIST rung (bet HOLDS).** Native-784 gauntlet, both switch regimes, both arms, vs per-arm-tuned ER.
  Safety WINS every cell (long-regime worst-BWT −0.012/−0.046 vs ER −0.196/−0.162); retention WINS on long blocks;
  order-invariance holds (|fwd−rev| 0.003/0.011); static AA trails; **Arm B (D80) scales** (AA 0.284→0.421,
  retention 0.223→0.314). → [`exp2/experiment-2.md`](exp2/experiment-2.md) · `STREAM_mnist.png`.
- **P11.3 — the real-world streams (the headline).** Prequential balanced accuracy vs the stronger ER + no-change +
  sgd-linear + first-block-frozen. **gas WINS** — OURS-A 0.789 ≥ stronger-ER 0.756, beats persistence 0.605 by
  +0.184 (Arm B 0.856); the frozen recipe is the best online learner on a famous real sensor-drift benchmark.
  **har / electricity / covertype FLOOR** — the ELEC2 label-autocorrelation trap (D2) fires as pre-registered: *no*
  learner beats the no-change baseline (0.950/0.836/0.646), and inside the floor the field leads OURS by ~0.07 (grey
  cells, two-sided). Honest split of drift-difficulty vs data-difficulty. → [`exp3/experiment-3.md`](exp3/experiment-3.md)
  · `STREAM_{gas,har,electric,covtype}.png`.
- **P11.4 — the cross-dataset gauntlet (the author's ask).** MNIST→Fashion→CIFAR-gray as one class-IL 30-way stream
  (harder than the field's task-IL), shared source-1 porthole. **All three data types stay alive** (weakest,
  CIFAR-gray, ~4× chance, never collapses); **order-invariant across data types** (|fwd−rev| 0.007/0.004); retention
  **TYPE-SCOPED at the porthole** (Arm A worst-ret 0.415 < ER 0.534) → **TYPE-ROBUST when scaled** (Arm B 0.581 ≥ ER
  0.551). Gram conditioning bounded (~1–2e8, no blow-up). → [`exp4/experiment-4.md`](exp4/experiment-4.md) ·
  `STREAM_xdata.png`.
- **P11.9 — the LIMIT-MAP + close-out.** _[the money figure + the owed §7 deltas.]_ → [`RESULTS.md`](RESULTS.md).

---

## What Phase 11 does NOT claim (written before the map is read)

- **No raw-vision-at-scale claim** (ImageNet/CORe50/CLEAR-raw untouched). **No PVT/analog realism** (behavioral
  meter throughout → the analog-realism layer). **No recurrence / north star.**
- **Honest descopes (named, not faked):** Yearbook / BloodMNIST / CIFAR-100 did not fetch (openml API down);
  P11.5–P11.8 (capacity/class-count/throughput/features sweeps) were not run this session; the raw-784 Split-MNIST
  anchor validation is owed; the D=160 cross-dataset Arm B awaits the F5 GEMM apparatus fix. **Losses and floors
  stay in the map** — that is the deliverable.

*Up:* [draft context](../../CLAUDE.md) · *prev:* [Phase 10 — validation](../phase10/README.md) (closed, S14) ·
*spec:* [`design.md`](design.md) · *contract:* [`result-format.md`](result-format.md).
