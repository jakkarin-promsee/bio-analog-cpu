# Phase 6 — Noise-robust SCFF: make the cheap brain survive the world it runs in

> **The front door.** Read this for the verdict; open [`phase6-report.md`](phase6-report.md) for the full story with
> every figure, `RESULTS.md` for the numbers, `expK/experiment-K.md` for a rung's story, `design.md` for the pre-run
> plan. Phase 6 is a **Stage-1 extension** — it hardens the *frozen Phase-5 cell* against noise **before** the GD
> namer (Stage 2), because a frozen head cannot manufacture backbone robustness (LP-FT). Ran 2026-07-01, P6.0→P6.8,
> single-thread, seeds `[42,137,271,314,1729]`, all guards pass.
>
> *↑ In the arc:* **Phase 6** of the ten-phase story ([map](../README.md) · [Stage 1](../stage1-report.md)) — the spine under all of it: [`the-essence2`](../../../docs/essence/the-essence2.md).

---

## The verdict — **Scoped-YES: the dominant channel is (partially) fixable in SCFF, forward-only**

**The cheap brain's eval-time noise-sensitivity (A7) is real, OURS-specific, and directional — and the dominant
(tap) channel is substantially hardened by a single forward-only objective change that keeps the A6 continual win.**
The fix is **generic noise-augmentation**: corrupt one InfoNCE view with broad iid noise at train time. In the
assembled-cell confirmation it lifts the Rasch-dominant tap-directional retention **0.817 → 0.865** (5/5 seeds
paired, real; digits 0.763→0.888, CIFAR-flat 0.697→0.779), *improves* clean accuracy, holds selectivity, and
**passes the continual-safety gate** (BWT −0.022→−0.017, AA 0.937→0.944 — a noise-robust rep is also drift-robust).
**Honest scope:** the lift is **partial — near, not decisively above, the pre-registered 0.90 band** at σ\* (the
per-rung 0.946 sat at the top of a wide IQR; the combined run overrides it at 0.865). The **input-transducer
channel's directional residual is not helped** (0.733→0.696) → both go to Stage-2 read-side as a named brief (**the
"scoped" in Scoped-YES**). **Not NO** — the SCFF objective did not need reopening; a forward-only fix reproducibly
hardens the dominant channel without denting depth, selectivity, or the A6 win.

**Two hypotheses the sims overturned or sharpened (the honest science):**
- **The fix is GENERIC, not directional-specific.** The design predicted a *directional* augmentation would be the
  spine fix. It is not: `iid ≥ random-axis > directional-specific`. You cannot bet the augmentation on one axis for a
  coherent shift whose direction is unknown at train time (and label-free), so **broad smoothing generalizes best**.
- **The spine metric had to be sharpened.** The two noise enemies attack *different geometry*: iid noise **rotates**
  each representation (per-sample `cos` collapses with depth); the directional enemy is a **coherent translation**
  along the class axis — it barely rotates any single rep (`cos` ≈ 0.97) yet moves the whole cloud off the fixed
  readout. So for the directional enemy the direction-preservation read **is retention** (made direction-specific by
  OURS-vs-linear and dir-vs-iid), not per-sample `cos`. density≠class, wearing its 6th coat.

---

## The problem — two doors, one directional crux

| door | the enemy | Phase-6 finding |
| --- | --- | --- |
| **A — the analog substrate** | tap / input / ADC / weight noise; the **directional residual** that survives auto-zero | A7 reproduces; **OURS is ~2× more directionally fragile than a linear readout** (5/5); the per-sample layernorm that won P5 depth *amplifies* a directional shift; common-mode is auto-rejected by that same norm; ADC fine ≥3-bit; weight-noise mild |
| **B — the data stream** (every datum is a noisy real-world sample banked to the LUT) | learn a stable class direction from an all-corrupted stream, no clean truth | the class direction **still forms** from a fully-noisy stream (zero-mean ratio 0.93, directional 1.00); buffer *purity* ≈ naive averaging at this noise level (not needed) |

**The crux both share:** a **directional, non-zero-mean** perturbation aligned with the class axis. One enemy, three
faces (Door A residual · Door B residual · the spine's enemy).

---

## The ladder (what ran, what each decided)

| rung | question | verdict |
| --- | --- | --- |
| **P6.0** `exp0` | reproduce A7 on the frozen cell with an honest noise model; which channel; directional? | **BENCH TRUSTED** — A7 OURS-specific & directional (0.60 vs linear 0.96, 5/5); σ*=2.0 pinned; 7/7 guards |
| **P6.1** `exp1` | does a noise-augmented contrastive view fix it, spine-clean, no collapse? *(STOP ①)* | **substantially, on the dominant tap channel** — adopt **iid σ_aug=1.0** (0.82→0.87 combined; per-rung 0.95); the fix is **generic** (overturns H-aug-directional) |
| **P6.2** `exp2` | forward-only flatness for the weight channel? | **SKIP** — tap ≫ weight, tap already fixed |
| **P6.3** `exp3` | re-tune the per-sample norm (the A7 root)? *(STOP ②)* | **SKIP** — leave the load-bearing norm; harden around it |
| **P6.4** `exp4` | can the direction form from an all-noisy stream; does purity beat averaging? | **YES it forms** (zero-mean 0.93, directional 1.00); purity ≈ averaging (not needed) |
| **P6.6** `exp6` | does the fix keep the A6 continual win? *(the gate, 5 seeds + paired veto)* | **PASS — banked** (BWT −0.022→−0.017, AA ↑; 1/5 negative) |
| **P6.7** `exp7` | does A7 + the fix hold on natural flat data (digits, CIFAR-flat)? | **YES both** (digits 0.76→0.89, CIFAR 0.70→0.78; not a synthetic artifact) |
| **P6.8** `exp8` | assembled-cell confirmation + the arc verdict | **Scoped-YES** (partial tap lift 0.82→0.87 + named residual) |

---

## The noise-hardened cell (handed to Stage 2)

**`NoiseAugContrast` = the frozen Phase-5 cell (`SCFFContrastOverlap` temp0.2 / w2, L12, no residual) + one
iid-noise-augmented InfoNCE view at σ_aug = 1.0.** Forward-only, local, no backward pass through the bulk, no stream
rewrite — the P2.5 envelope held. Clean accuracy, selectivity, depth, and the A6 continual win are **preserved or
improved**; the dominant tap-directional channel is noise-robust.

**The Stage-2 brief (what the namer can assume vs must defend):**
- **Assume handled:** the dominant **tap-directional** channel (the Rasch-dominant analog read path) is noise-robust
  in the base representation; the **common-mode** channel is auto-rejected by the layernorm; the **A6 continual win**
  survives the fix.
- **Must still defend (read-side, Stage 2):** the **input-transducer directional residual** (calibration under shift)
  and any **ADC-quantization** below ~3-bit — the named residuals of the Scoped-YES.
- **Owed to Phase 9 (maintenance):** the buffer-purity filter (P6.4) — measured, **not needed** at this noise level
  (≈ naive averaging); an *available* knob for higher-noise regimes, not a required one.

---

## The decision-record delta (to bank at phase close)

*SCFF carries a noise-aware objective — one contrastive view is corrupted by broad (iid) noise at train time;
robustness is built into the base representation, not bolted onto the readout.* This revises the implicit "the SCFF
objective is noiseless" and is the Phase-6 supporting decision for `idea/main.ideas.v1.md`.

## Read next

| For | Go to |
| --- | --- |
| **The full story, every figure, the per-rung reads** | [`phase6-report.md`](phase6-report.md) |
| The scalar ledger (per-rung numbers + the scorecard) | [`RESULTS.md`](RESULTS.md) |
| The pre-run design (the ladder, the build plan, the two-door framing) | [`design.md`](design.md) |
| The binding reporting contract (figures · tables · the 8-slot summary) | [`result-format.md`](result-format.md) |
| The run-cards | `exp0`…`exp8/` `experiment-*.md` (P6.0–P6.8; exp2/exp3 = the documented skips) |
| The literature behind every mechanism | [`../../research/papers/phase6/`](../../research/papers/phase6/README.md) |
| The Stage-1 arc (Phase 6 is its noise-hardening extension) | [`../stage1-report.md`](../stage1-report.md) |

*Prev:* [Phase 5](../phase5/README.md) · *Next:* [Phase 7 — the GD namer](../phase7/README.md) (Stage 2 begins).
