# P5.8 — natural-data confirmation: the decay is real; the temp-fix holds where depth composes

*The whole Phase-5 diagnosis is synthetic. The strongest validity flag: maybe the decay — or the temp0.2 fix — is a
synthetic artifact. So a first-class gate: run the SAME per-layer DEPTH-PROFILE on the in-scope real flat anchors,
digits (64-D) and CIFAR-flat (3072-D, the Phase-2/3 wall), for the decay baseline (temp0.5) vs the adopted fix
(temp0.2). The decay reproduces on both; the temp-fix reproduces on digits and is null on the no-headroom wall.*

**Question.** Does the per-layer decay reproduce on real flat input, and does the temp0.2 fix lift the tail there
(not just on synthetic data)?

**Setup.** Committed cell (L12/w2), static all-class, per-layer linear probe (PROBE_EP=120). digits (64-D, 5 seeds) +
CIFAR-flat (3072-D, 3 seeds — the heavier anchor, the Phase-2/3 "wall"). temp ∈ {0.5 (decay baseline), 0.2 (adopted
fix)}. Guards passed.

**Run.** 2 datasets × 2 temps × seeds, checkpointed; wall ≈ 13 min (CIFAR 3072-D dominates).

**Result / figures.** *(median, n=5 digits / n=3 CIFAR)*
| anchor · temp | peak | top | tail-L12 | **decay (top−tail)** | readout |
| --- | --- | --- | --- | --- | --- |
| **digits** temp0.5 | L1 | 0.946 | 0.687 | **+0.260** | 0.951 |
| **digits** temp0.2 | L1 | 0.958 | **0.839** | +0.119 | 0.950 |
| **CIFAR-flat** temp0.5 | L1 | 0.332 | 0.238 | **+0.094** | 0.311 |
| **CIFAR-flat** temp0.2 | L1 | 0.348 | 0.244 | +0.104 | 0.293 |

- **NAT-ANCHOR-digits**: clean separation — temp0.5 decays 0.95→0.69, temp0.2 holds 0.96→0.84 (**fix +0.152 tail**). -
  **NAT-ANCHOR-cifar**: the two curves **overlap** within IQR, both decay 0.33→0.24 (**fix +0.006, null**). - **INV**:
  dead-unit ≈ 0, rank decays, guards PASS.

**Read (6 + 2 slots).**

1. **Claim** — The decay is **real, not a synthetic artifact** (reproduces on both anchors — strongly on digits +0.260,
   modestly on CIFAR +0.094). The temp0.2 fix **reproduces where there is depth to compose** (digits +0.152) and is
   **null on the no-headroom wall** (CIFAR-flat +0.006). **Commit the fix** — it helps where it can, is neutral/safe
   where it can't, and (P5.7) is continual-safe.
2. **Headline** — digits: temp0.5 tail 0.687 → temp0.2 **0.839** (+0.152, the fix holds on real data). CIFAR-flat: tail
   0.238 → 0.244 (+0.006, within noise). Decay on both (digits +0.260, CIFAR +0.094). (n=5 / n=3.)
3. **Figures** — NAT-ANCHOR-{digits, cifar}, INV. Regen from `arrays.npz`.
4. **Mechanism** — The temp lever **extends composing depth** (P5.1/P5.2): it keeps each per-layer update on the class
   manifold, so deep layers compose instead of overwrite — but *only if there is compositional structure to compose*.
   **digits** has accessible depth (peak L1 but the tail is recoverable — temp0.2 keeps it ~0.84 vs 0.69), so the fix
   bites. **CIFAR-flat** is the established **no-headroom wall** (Phase 2/3: GD-hidden is itself flat ~0.36 — raw
   3072-D pixels carry no depth-composable class structure to a *flat* method; it needs convolution). The temp lever
   has nothing to extend there, so it's null — *exactly* as scoped (design §0.4: conv/image is out of Phase-5 scope,
   north-star territory). The decay still appears on CIFAR (deep layers drift off even the weak L1 signal), confirming
   the decay is intrinsic to the cell, not the task — but the *fix* needs depth headroom to act on.
5. **Threats** — (a) CIFAR n=3 (the heavy anchor; P4.4 used n=1) — the temp-null is small (+0.006) and within IQR, so
   "null" is the honest call, but a depth-composable real task (not flat-CIFAR) is owed for a *positive* large-D
   confirmation (deferred — needs conv or a structured real task, north-star). (b) digits peak L1 (near-linearly
   separable) — the "read shallow" deployment (P5.5 truncation) is *also* confirmed here (everything past L1 is tunnel
   that temp0.2 merely makes less destructive); the temp-fix value on digits is **tail-preservation**, not a deeper
   peak. (c) the CIFAR readout dips slightly under temp0.2 (0.311→0.293, within noise) — not a real regression, but
   temp0.2 buys nothing on the wall (and costs nothing — P5.7 safe).
6. **Decision** — **COMMIT the temp0.2 fix.** The decay diagnosis and the fix both survive the synthetic-artifact gate
   *where the fix is meant to act* (depth-composable data: digits, synth headroom). The CIFAR-flat null is an **honest
   scope line**, not a refutation — flat-CIFAR is the no-headroom wall the whole project brackets out (needs conv). The
   synthetic story is **real**; the Phase-5 cell holds on natural flat input.
7. **Cost-honesty** — no deployment cost; this is a validity gate. It strengthens the "read shallow" story (digits peak
   L1 → the truncation/short-read deployment of P5.5 is the right call on easy real data too) and bounds the claim
   honestly (large-D *flat* real data with no composable depth gets no temp benefit — and shouldn't, by design).
8. **SCFF-completion** — the natural-data gate is **cleared (scoped)**: decay real on both anchors; temp-fix confirmed
   on digits, null-but-safe on the CIFAR wall. Combined with P5.7 (continual-safe), the committed cell (temp0.2/w2)
   is validated on real flat input. **Remaining: P5.9** — assemble the verdict (the per-rung wins all used this one
   committed cell, so the assembled-cell confirmation is the rung-by-rung evidence; the public README/report is
   deferred to the author's return per the session directive).

**Pre-submit checklist.** [x] Median [IQR via arrays], n=5 digits / n=3 CIFAR. [x] "Real" rule (digits fix +0.152
clean-separated; CIFAR fix +0.006 within-noise = null). [x] Same per-layer probe protocol as P5.0/P5.1 (PROBE_EP=120).
[x] Both anchors (64-D + 3072-D). [x] decay baseline vs fix isolated (temp the only variable). [x] Figures via
`plot_p5.fig_nat_anchor`; regen redraws. [x] manifest+arrays to schema. [x] Guards logged (FD 2.1e-8). [x]
Single-threaded, checkpointed. [x] Spine: the fix acts on composing-depth (direction), null where no depth composes —
not a magnitude story. [x] CIFAR-flat null scoped honestly (the no-headroom wall, needs conv). [x] `RESULTS.md` row.
