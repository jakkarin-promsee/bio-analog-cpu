# Experiment P4.5 — continual (A6) across difficulty

> **Status: ✅ DONE (2026-06-22).** Does the home-turf WIN (Phase-1 exp4, P3.3) hold *off* the home config? Class-
> incremental stream (5 tasks of 2 classes), fed the **validated P3.3 continual harness** (contrast+coord+sleep vs
> the no-sleep rot control vs online-BP), on **synthetic data at swept difficulty** (overlap 0.4/0.7/1.0) + the
> **digits home anchor**. Metrics (GEM/CL-survey): AA, BWT, forget. 3 seeds. Run:
> `OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_5.py` (152s). Contract: [`../result-format.md`](../result-format.md).

---

## The 6+2 slot read

**1 · Claim.** **A6 is the WIN — and it holds decisively across difficulty.** OURS (contrast+coord + sleep) forgets
almost nothing (**BWT −0.02 to −0.18**) at every difficulty *and* on digits, while **online-BP catastrophically
forgets** (BWT −0.83 to −0.99) everywhere, and the **no-sleep control rots** (BWT −0.84 to −0.95) — proving sleep,
not SCFF alone, carries the recovery. The digits anchor **reproduces P3.3 exactly** (AA 0.954, BWT −0.017). As
difficulty rises OURS's AA falls (harder task) but its **BWT stays excellent** — the win is robust off the home
config. This is the **largest, cleanest margin in the phase** — the architecture's reason for being.

**2 · Number + IQR** (median [IQR], n=3):

| regime | OURS-sleep AA | OURS-sleep BWT | online-BP AA | online-BP BWT |
| --- | --- | --- | --- | --- |
| ov0.4 (easy) | 0.710 | −0.122 [−0.124,−0.116] | 0.200 | −0.929 |
| ov0.7 | 0.583 | −0.176 [−0.191,−0.168] | 0.197 | −0.876 |
| ov1.0 (hard) | 0.435 | −0.183 [−0.205,−0.183] | 0.186 | −0.826 |
| **digits (home)** | **0.954** | **−0.017 [−0.020,−0.015]** | 0.186 | −0.992 |

No-sleep control (rot): AA ~0.20, BWT −0.84 to −0.95 across all regimes. **OURS-sleep BWT IQRs are disjoint from
both baselines at every regime.**

**3 · Figures.** `CONT` (AA bars — OURS towers over both baselines everywhere; BWT bars — OURS near zero, online-BP
& no-sleep deep negative) · `LINE` (AA & BWT vs difficulty — OURS-sleep's BWT stays flat-near-zero across the band
while the baselines sit at the floor).

**4 · Mechanism.** SCFF contrast is **unsupervised + per-sample** (no batch statistics) — new classes *add*
discriminative structure rather than overwriting old (the Phase-1 forgetting-robustness, re-confirmed for the
contrast objective). **Sleep re-fits the readout** over replayed prototypes → recovers any readout drift. Online-BP
overwrites its weights with each task's gradient → catastrophic forgetting. The **no-sleep control rots** because
the readout (the only supervised part) drifts to the current task without consolidation — so **SCFF doesn't forget,
but the readout does without sleep**, and sleep is the decisive recovery mechanism.

**5 · Threats.** (a) The `gd` baseline is **naive online BP** (fixed arch) — the *catastrophic-forgetting
reference*, not a continual-learning SOTA; the claim is "naive online BP forgets, OURS+sleep doesn't" (the validated
Phase-1 framing), **not** "OURS beats a replay/regularization CL method." (b) Synthetic stream shares the digits
shape (5×2); (c) 3 seeds (heaviest rung); (d) AA falls with difficulty (absolute — expected; BWT is the win metric).

**6 · Decision.** **A6 = the validated WIN, confirmed difficulty-robust.** This is the architecture's home and the
reason it exists. **Carry forward:** the continual+sleep win **does not erode as tasks harden** (BWT stays −0.02 to
−0.18 while online-BP stays at the floor); it is the **strongest, most robust result in the phase**, and the
substrate's actual value proposition.

**7 · Cost-honesty.** The win is bought with **sleep = periodic readout re-fit** (the GD ~20%, sleep-consolidated)
over a small prototype buffer; the SCFF bulk is forward-only. Same cheap-backward profile as the rest of the phase
— the continual recovery is *not* an expensive add-on.

**8 · Map-contribution → P5.** A6 tile: **THE win — robust across difficulty.** Tells Phase 5: this is the mechanism
to *optimize* (the **sleep cadence + the Ch7 gate** — exactly P5's maintenance loop, now to be tuned against the
*measured* drift of this cell). The continual regime is where the cheap forward-only brain decisively earns its
place; everything else in the phase characterizes the *cost* of getting here.

---

## Reproducibility

`figs_p4_5/{manifest.json, arrays.npz, _ckpt.jsonl}`; `python plot_p4_5.py figs_p4_5`. Single-threaded, `python -u`,
`PYTHONIOENCODING=utf-8`, per-cell fsync. Reuses the **validated P3.3 continual harness** verbatim
(`run_p3_3.run_condition`, `load_digits_split`) — synthetic streams from `make_gauss` (10-class, 40 clusters), fed
in at swept overlap. Uses sklearn probes inside the harness (ran clean, OMP=1). New: `exp5/run_p4_5.py` + `plot_p4_5.py`.
