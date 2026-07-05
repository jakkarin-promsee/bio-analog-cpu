# Phase 11 — the limit map: the frozen recipe on real data and at scale (front door)

> **Status: 🟢 RUN — committed core + all three scaling extensions (2026-07-05).** The phase the red team asked for —
> the P10 instrument taken to **harder data, real-world streams, cross-dataset streams, and scale**, run honestly,
> expecting and welcoming losses. The product is the **LIMIT-MAP**: 8 arenas × 5 capability channels, every cell
> win / tie / loss / FLOOR with its number. The committed object (the P9-frozen two-brain neocortex, `freeze_content`
> bit-exact) was measured untouched (Arm A, the frozen recipe through the 40-D porthole) and re-built to a
> pre-registered scaling rule (Arm B); **nothing was tuned in either arm.** ER-strong was re-tuned per arena on the
> disjoint seed-7 stream — the asymmetry runs *against* the home team.
>
> **What ran:** P11.0 (bench) · P11.1 (decomposition) · P11.2 (MNIST rung) · P11.3 (real streams: gas · HAR ·
> electricity · covertype) · P11.4 (cross-dataset 30-way) · **P11.5 (Fashion/CIFAR rungs + class-count crossover) ·
> P11.6 (capacity scaling) · P11.7 (throughput)** · P11.9 (the LIMIT-MAP + close-out). **What did not:** Yearbook /
> BloodMNIST / CIFAR-100 (openml API down; optional bonuses) and P11.8 (the features arena — no off-box precompute
> window). The map ships the columns that exist.

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
its wins, its losses, and its FLOOR cells. **And it scales (P11.5–P11.7):** the pinned GD-share shape is confirmed
(the economy does not improve with width — the namer solve is the thing that scales worst), the analog substrate
advantage *grows* with width (5.4→7.4×), safety holds at every width/dim, the prototype+Gram namer out-retains a
byte-matched replay buffer by C=20 (replay dilutes, the namer does not), and on gas the frozen recipe
out-throughputs the retention-tuned ER. The honest counterweights — static accuracy trails on recognizable data,
CIFAR-gray floors, the streaming canon floors under label-persistence — ship in the map beside the wins.

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
  · `STREAM_{gas,har,electric,covtype}.png` (now **OURS vs ER-strong** + the no-change floor — on gas OURS is steadier
  at the drift boundaries where ER spikes down; on the floor arenas ER rides just above OURS, both under persistence).
- **P11.4 — the cross-dataset gauntlet (the author's ask).** MNIST→Fashion→CIFAR-gray as one class-IL 30-way stream
  (harder than the field's task-IL), shared source-1 porthole. **All three data types stay alive** (weakest,
  CIFAR-gray, ~4× chance, never collapses); **order-invariant across data types** (|fwd−rev| 0.007/0.004); retention
  **TYPE-SCOPED at the porthole** (Arm A worst-ret 0.415 < ER 0.534) → **TYPE-ROBUST when scaled** (Arm B 0.581 ≥ ER
  0.551). Gram conditioning bounded (~1–2e8, no blow-up). → [`exp4/experiment-4.md`](exp4/experiment-4.md) ·
  `STREAM_xdata.png` (now **OURS vs ER-strong** — ER learns block 1 higher but **catastrophically collapses to ≈0 at
  each data-type switch**, while OURS degrades gracefully and rides above it through the Fashion block).
- **P11.5 — Fashion/CIFAR rungs + the class-count crossover.** Fashion (r2) **BET HOLDS** (safety win, worst-BWT
  −0.021/−0.057 vs ER −0.146/−0.141; static AA trails, Arm B recovers retention); CIFAR-gray (r3) = **FLOOR** (joint
  ceiling 0.199, the honest resolution floor). **The retention crossover is real by C=20** — OURS 0.354/ER 0.423 at
  C=10 flips to OURS 0.233/ER **0.014** at C=20 (the fixed replay buffer dilutes to ≈0; prototype+Gram does not
  dilute per-class). → [`exp5/experiment-5.md`](exp5/experiment-5.md) · `CROSSOVER.png`.
- **P11.6 — capacity scaling.** The bench-**pinned GD-share shape CONFIRMED** (measured [0.17,0.28,0.45] tracks
  pinned [0.21,0.34,0.53] — the economy does *not* improve with width); capacity buys the accuracy gap back
  (0.42→0.50); the **substrate factor RISES** 5.4→7.4× (the analog advantage grows with scale — the chip's best
  sentence); safety holds at every width/dim. → [`exp6/experiment-6.md`](exp6/experiment-6.md) · `SCALING.png`.
- **P11.7 — throughput.** On gas, the retention-tuned ER costs more FLOPs/sample than the frozen recipe → **branch
  (i) the regime win** (ER skips 32%/31%/8% raw/digital/analog at the demo rate; OURS keeps up). Honest caveat: this
  *inverts* P10's synthetic-home FLOP inversion — arena/opponent-dependent, reported as such. →
  [`exp7/experiment-7.md`](exp7/experiment-7.md).
- **P11.9 — the LIMIT-MAP + close-out.** The money figure — 8 arenas × 5 channels, every cell win/tie/loss/FLOOR +
  number ([`exp9/figs_p11_9/LIMIT_MAP.png`](exp9/figs_p11_9/LIMIT_MAP.png)); the owed §7 deltas banked to
  `main.ideas` as **S15**. → [`RESULTS.md`](RESULTS.md) · [`phase11-report.md`](phase11-report.md).

---

## What Phase 11 does NOT claim (written before the map is read)

- **No raw-vision-at-scale claim** (ImageNet/CORe50/CLEAR-raw untouched). **No PVT/analog realism** (behavioral
  meter throughout → the analog-realism layer). **No recurrence / north star.**
- **Honest descopes (named, not faked):** Yearbook / BloodMNIST / CIFAR-100 did not fetch (openml API down);
  **P11.8** (the features arena) had no off-box precompute window; the raw-784 Split-MNIST anchor validation is owed
  (P11.2 ran the anchor at porthole-40, a config note not an ER failure); the D=160 cross-dataset Arm B awaits the F5
  einsum→GEMM apparatus fix (descoped to D=80). **Losses and floors stay in the map** — that is the deliverable.

*Up:* [draft context](../../CLAUDE.md) · *prev:* [Phase 10 — validation](../phase10/README.md) (closed, S14) ·
*spec:* [`design.md`](design.md) · *contract:* [`result-format.md`](result-format.md).
