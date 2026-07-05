# Phase 9 — Close & *freeze* the maintenance loop: the lifelong neocortex, tuned then locked

> **The front door.** Read this for the verdict; open [`phase9-report.md`](phase9-report.md) for the full story with every
> figure, [`RESULTS.md`](RESULTS.md) for the numbers, [`expK/experiment-K.md`](exp0/experiment-0.md) for a rung's story,
> [`design.md`](design.md) for the pre-run plan, [`result-format.md`](result-format.md) for the reporting contract. Phase 9 is
> **Stage 2's third GD phase** (P7 readout · P8 economy+cost · **P9 maintenance/close** · P10 validate/showcase). Phase 8
> turned both brains on and metered the economy; **Phase 9 tunes the five still-open knobs of the lifelong maintenance loop
> against *internal* signals, then LOCKS the object** for Phase 10 to race. Ran 2026-07-02, P9.0→P9.5, single-thread
> CPU/float64, seeds `[42,137,271,314,1729]`, all nine guards bit-exact. Discipline: **freeze in P9, judge in P10.**
>
> *↑ In the arc:* **Phase 9** of the eleven-phase story ([map](../README.md) · [Stage 2](../stage2-report.md)) — the spine under all of it: [`the-essence2`](../../../docs/essence/the-essence2.md).

---

## The verdict — **the maintenance loop is frozen, and the freeze made it safer than what P8 shipped** 🔥

The chip runs forever: the SCFF cortex learns forward-only on **every** input (it never forgets, but its feature map
**drifts**), and the namer must keep its labels tracking that drift cheaply. Phase 8 built and metered that loop; Phase 9
asked whether the *loop around the frozen head* is actually tuned for a **lifelong** stream — one that revisits its tasks for
many cycles, so drift accumulates past P8's single pass — then locked it. The result is not "polish"; it discharged the
founding assumption and caught one real gap.

- **The founding assumption is measured, not assumed: the bulk ROTATES, it does not FORGET.** On the lifelong stream an
  optimal probe **re-fit** on the current bulk holds ≥ its birth score on held-out early-task data throughout (destruction
  final 2.2×, min 0.966), while a *fixed* head fit at birth rots to ~0.07. The "SCFF doesn't forget → sleep is cheap" story
  that the whole architecture rests on is now a **measurement** (Davari 2203.13381 protocol, rotation factored out), not a
  caveat. So N2 (a drift-slowdown) is *not mandatory*.
- **Four of five open knobs resolved to *keep* the committed loop** — N2 **struck**, consolidation depth **all-tap**, eviction
  **CBRS** (already the P8 guard), read-side residual **defended by the sleep mechanism itself**. The precise brain P8 shipped
  needed almost nothing added.
- **The freeze itself caught the one real gap — and closed it.** The first assemble (the inherited P8 grid-8 cadence, which is
  the P8.6 shipped object bit-for-bit) **failed the worst-point oracle-veto 2/5** on the lifelong stream: sparse sleep let the
  pre-sleep state fall into deep troughs between sleeps on high-variance seeds (worst-BWT −0.517). The freeze-driven **cadence
  re-confirm** — the P8 "cadence is drift-rate-conditional" debt, now owed — found the fix is denser sleep: at **grid-4** the
  worst-point BWT collapses to **−0.028** and exactly matches the boundary oracle (0/5 regress), at GD-share **0.178 ≤ 0.25**.
- **The frozen loop is an order of magnitude safer at the worst point than the shipped loop, on a true lifelong stream** —
  worst-BWT **−0.028** (frozen, grid-4) vs **−0.317** (shipped, grid-8), at the same accuracy (AA 0.494). The P8 cadence,
  tuned on a single pass, silently under-consolidated under revisits; P9 restored the near-flat continual-safety.

**Two guesses the sims overturned (the honest science):**
- **The worst-point gap looked like the committed gate's *fire-timing* — unfixable in P9 (the gate is committed).** The sims
  overturned it: the oracle and the loop sleep on the *same* cadence, so denser **sleep** (a P9-legal knob) closed the gap
  entirely — frequent consolidation makes the DDM-vs-onset fire-timing difference irrelevant. The lever was frequency, not the
  gate.
- **The read-side defense was planned around an SLDA *covariance* re-estimate (feature-level).** The sims overturned it:
  **prototype re-anchoring** — re-forwarding the raw LUT through the current bulk under the shift, the plan's *own sleep
  mechanism*, no covariance estimate — fully recovers the residual (retention 0.787 → **0.986**). The fallback was never needed.

**The spine, 9th coat.** Eviction keeps the class *directions* (CBRS balances classes) not the dense *mean* (herding, the
magnitude null); the read-side calibration re-anchors a *direction*, never an entropy/confidence *magnitude*. Where herding
tied CBRS it was a **buffer-spine null** (density ≈ class at the buffer on this task), reported as a null, not a spine win.

---

## The frozen object (what Phase 9 locks — the loop Phase 10 races)

| knob | committed | resolved by | why |
| --- | --- | --- | --- |
| **bulk** | `NoiseAugContrast` σ_aug=1.0 (SCFFContrastOverlap temp0.2/w2, L12) | P5/P6 (inherited) | the frozen cheap brain |
| **namer** | **SLDA** (tied-covariance analytic; RanPAC the reference) | P7/P8 (inherited) | 69× cheaper, ties live |
| **awake gate / trigger** | **DDM** on the **class-direction tap-drift** | P8 (inherited, not reopened) | spine-clean drift detection |
| **N2** (drift-slowdown) | **struck** | P9.1 | drift is rotation-only → no lever to grip |
| **consolidation depth** | **all-tap** | P9.2 | truncated readers forget more under lifelong drift |
| **bounded-LUT eviction** | **CBRS** | P9.3 | best-bounded; spans class directions; cap scales with #classes |
| **read-side residual** | **proto-reanchor** (earned) | P9.4 | the sleep mechanism recovers the input-transducer channel |
| **sleep cadence** | **grid-4** (was grid-8) | P9.5 | the lifelong revisit stream needs denser sleep than P8's single pass |
| **envelope** | GD reads taps, never writes SCFF | unchanged | the P2.5 forward-leak wall |

**Freeze:** worst-point BWT −0.028 [−0.039,−0.022] (ties oracle, 0/5 regress) · AA 0.494 [0.478–0.502] (= P8.6 shipped) ·
GD-share 0.178 [0.178–0.178] ≤ 0.25. Locked by the P9.5 commit (manifest `exp5/figs_p9_5/manifest.json`, pre-freeze parent
`1fb11b3`); every knob enumerated in the committed-knob block. **Phase 10 touches no knob.**

---

## The ladder (P9.0 → P9.5)

| rung | question | verdict |
| --- | --- | --- |
| **P9.0** risk gate | does the bulk rotate (sleep fixes it) or forget (assumption breaks)? | **rotation-only** — re-fit destruction ≥ birth (final 2.2×, min 0.966); the cheapness holds, N2 not mandatory |
| **P9.1** N2 | does a read-side/rate-only drift-slowdown earn its place? | **struck** — no arm sleeps sparser or improves BWT; EMA-view worsens it; LLRD honestly rate-only |
| **P9.2** depth | can sleep consolidate at a shorter read depth and hold A6? | **keep all-tap** — trunc 12–52× cheaper refit but forgets more (A6 beyond δ_acc) |
| **P9.3** eviction | which bounded-LUT policy holds continual-safety at a tight cap? | **CBRS committed** (S13) — best-bounded, ties herding null, beats iid/FIFO; cap grows with #classes |
| **P9.4** residual | does the Phase-6 read-side residual need a defense, and can sleep supply it? | **proto-reanchor adopted** — gate fires (dent +0.115); retention 0.787 → 0.986; residual resolved read-side |
| **P9.5** freeze | does the assembled loop hold A6 at the economy, and lock? | **FROZEN** at grid-4 (worst-BWT −0.028 = oracle, AA 0.494, GD 0.178); the freeze re-confirmed the cadence |

---

## Honest scope — what Phase 9 does NOT settle (owed → Phase 10)

Phase 9 froze the object against **internal** references only; **no verdict consulted the P10 BP+replay number** (the freeze
discipline). Still owed, unchanged by the freeze:

- **The existential fight:** the fair same-budget **BP+replay *accuracy*** baseline (P8 settled *energy*; the accuracy half is
  P10's). We may still win — only the readout replays, and the bulk doesn't forget (P9.0) — but it must be *shown*.
- **Natural multi-class A5**, the **multi-domain adaptive gauntlet**, and the **noise showcase** — the last on a **held-out**
  noise battery (P9.4 tuned only on the *home* residual; the showcase must not reuse it).
- **Caveats:** the cadence knee (grid-4) is drift-rate-conditional (it depends on the revisit density of the stream); the
  meter is **behavioral** (relative-pJ, ADC-centred, NOT SPICE); absolute live AA on the synthetic home is modest (0.494 — task
  difficulty, not forgetting: worst-BWT −0.028).

---

## Decision-record delta (banked to [`../../idea/main.ideas.v1.md`](../../idea/main.ideas.v1.md) as **S13**)

N2 **resolved** (struck) · S7 **extended** (all-tap depth + grid-4 lifelong cadence) · the bulk-drift assumption **measured**
(rotation-only, the founding caveat discharged) · **eviction = CBRS** (new supporting decision) · the read-side residual
**resolved** (proto-reanchor) · the **frozen object** = the complete committed neocortex loop, locked at a commit hash — the
Stage-2 maintenance close-out.

*Up:* draft context → [`../../CLAUDE.md`](../../CLAUDE.md) · *prev:* [Phase 8 — the economy](../phase8/README.md) · *next:*
[Phase 10 — the validation / the showcase](../phase10/README.md) (races this frozen object).
