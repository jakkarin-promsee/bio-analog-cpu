# P11.4 — the cross-dataset gauntlet (the author's aggressive ask): robustness to the TYPE of data

**Question.** The author's ask: not "same data plus a transform" but **different datasets entirely** — MNIST →
Fashion-MNIST → CIFAR-10-gray as ONE class-incremental **30-way** stream (the field's 5-Datasets protocol, Ebrahimi
ECCV'20, at our scale but **class-IL**, harder than their task-IL). Does the LUT/namer keep all three **data types**
alive as they arrive, or does one collapse — and is OURS order-invariant across a change in the *kind* of data?

**Setup.** Sources = [mnist (labels 0–9), fashion (10–19), cifar10gray (20–29)], each ONE contiguous block, single
pass, iid within block, no revisits (R1). CIFAR center-cropped 32→28 to share the 784 native space. **ONE shared
source-1-fit porthole + unit-RMS scaler** (fit on MNIST only, frozen — the honest gain-shock read; future sources
arrive uncalibrated, R7). Both arms (A = D40/W64 frozen; B = D80/W128 recipe), forward + reversed, 5 seeds. ER =
fixed 30-way head, re-tuned on seed-7. Watch: Gram condition number per arm (the conditioning risk, instrumented).
Arm B **descoped from the recipe D=160 to D=80** (commented in the run): D=160→W=256→Fdim=3072 makes SLDA's `_solve`
build a 30·3072·3072·8 ≈ 2.3 GB temp per solve (the F5 einsum→GEMM apparatus fix, deferred) — D=80 is a valid
scaled instance (> Arm A's 40) that shows the scaling read within the overnight budget; the D=160 leg is **owed**.

**Result — TYPE-SCOPED at the porthole (Arm A); TYPE-ROBUST when scaled (Arm B). All three data types stay alive.**

| arm | final-30 | rev | \|Δ\| | worst-ret | ER worst-ret | mnist | fashion | cifar-gray | cond(G) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A (D40) | 0.338 | 0.332 | **0.007** | 0.415 | 0.534 | 0.421 | 0.461 | 0.125 | 1.0e8 | TYPE-SCOPED |
| B (D80) | 0.440 | 0.444 | **0.004** | **0.581** | 0.551 | 0.588 | 0.581 | 0.143 | 1.9e8 | **TYPE-ROBUST** |

- **All three data types stay alive.** No block collapses toward chance (1/30 = 0.033): the weakest, CIFAR-gray, is
  0.125 (A) / 0.143 (B) — ~4× chance and above the collapse cut (chance+2δ = 0.073). The LUT's CBRS eviction keeps
  all three types represented through 30-way growth; the namer's Gram stays conditioned (~1–2e8, high but **bounded,
  no blow-up** — the D-research Q8 risk was instrumented, not assumed).
- **Order-invariance across data TYPES: |AA(fwd)−AA(rev)| = 0.007 (A) / 0.004 (B)** — OURS is essentially
  order-invariant even when the *kind* of data changes (MNIST-first vs CIFAR-first), well inside δ. This is the
  P10.3 order-invariance property surviving the hardest ordering stress in the phase.
- **Retention: the scaling recipe flips the verdict.** Arm A worst-point all-prev retention 0.415 trails ER 0.534
  (TYPE-SCOPED — all alive but retention behind); Arm B **0.581 ≥ ER 0.551** (TYPE-ROBUST — the scaled instance
  recovers and passes the field's retention). The porthole was the binding constraint; native dim buys it back.
- **CIFAR-gray is the hard type** (weakest block both arms) — grayscale-cropped natural images through a 40/80-D
  porthole is near the resolution floor, but it never collapses; the map records it alive-but-weak, not dead.

**Read (8 slots).**
1. *Claim* — the frozen object is robust to the TYPE of data: across a 30-way MNIST→Fashion→CIFAR-gray class-IL
   stream all three types stay alive, OURS is order-invariant, and the scaling recipe (Arm B) matches the field's
   retention.
2. *Headline* — order-invariance |Δ| **0.007/0.004** across data types; Arm B worst-ret **0.581 ≥ ER 0.551**
   (TYPE-ROBUST); no block below 4× chance.
3. *Figures* — `STREAM_xdata.png` (the 30-way prequential trajectory as each new data type arrives, sleep ticks +
   the three dataset onsets).
4. *Mechanism* — the SCFF bulk is a *shared* nonlinear front; the CBRS LUT holds a class-balanced prototype memory
   across all three types, and sleep re-fits the closed-form namer over that memory → no type is evicted to death.
   Order-invariance follows from the namer being closed-form (no gradient path that a data-type ordering could bias)
   and the LUT being balanced. ER's gradient head, by contrast, must re-tune per block and leans on its buffer —
   which the porthole-40 Arm A out-retains only once scaled.
5. *Threats* — (i) **projection loss** dominates absolute 30-way accuracy (Arm B bounds it; the owed D=160 leg would
   bound more); (ii) **conditioning**: Gram cond ~1e8 is high — bounded here but a watch item at larger C/D (banked
   as the conditioning invariant); (iii) the class-IL head convention is fixed 30-way uniformly for the gradient
   learners (R1), so the comparison is well-posed; (iv) CIFAR-gray's weakness is partly a native-resolution floor,
   not purely a continual-learning failure.
6. *Verdict* — **TYPE-SCOPED (Arm A) → TYPE-ROBUST (Arm B):** all types alive + order-invariant in both arms;
   retention trails ER at the frozen porthole and matches/beats it when scaled. Neither type-broken nor
   type-collapse fired.
7. *Recipe-honesty* — Arm A bit-equal committed; Arm B recipe-guard clean ({D,W,cap} only); shared source-1 porthole
   (no future data touches the stream's front — the honest gain-shock read); ER fixed-head re-tuned on seed-7;
   nothing tuned. The D=80 descope is an apparatus budget note (commented in-code), not a science change; the D=160
   leg is owed once the GEMM fix lands.
8. *Where-it-stands* — the **xdata(30-way)** column of the LIMIT-MAP: **order-invariance WIN, retention scoped→robust
   (arm-dependent), all-types-alive.** The type-robustness verdict banks: *the object survives a change in the kind
   of data, and the scaling recipe carries it past the field's retention.*

**Design deviations (commented):** Arm B D=160→D=80 descope (F5 GEMM fix owed); modest ER grid for the overnight
budget (full grid pinned in bench). STREAM-xdata figure (the Arm-A first-seed prequential curve) now overlays
**ER-strong** + the no-change floor — ER collapses to ≈0 at each data-type switch, OURS degrades gracefully.

*Guards: arena-data ✓ · recipe A/B ✓ · porthole ✓ (one shared source-1 projection) · condition-trace ✓ (bounded).
n=5.*
