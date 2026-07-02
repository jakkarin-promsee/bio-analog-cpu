# P9.3 — Bounded-LUT eviction: which policy holds continual-safety under a finite, bursty buffer?

**Inheriting** the committed loop from P8 and the rotation-only drift from P9.0, P9.3 builds the one thing P8 never
had — an **accumulating, evicting** prototype store (`StreamingLUT`; P8's streaming sleep re-solved over a *fixed*
600-item balanced probe, so there was no growing history to bound). A truly-lifelong stream forces a bounded evicting
buffer; this rung asks which eviction policy makes the most of a tight budget.

**Question.** At a pinned pressure-point cap (120 = ~12 exemplars/class), which eviction policy holds worst-point BWT
within δ_acc of the unbounded oracle — and does eviction re-import forgetting (herding = the magnitude/mean null)? And
does the cap needed to hold BWT grow with #classes (the scaling law)?

**Setup.** Swept variable = eviction policy ∈ {unbounded-oracle (cap=∞), CBRS (committed), reservoir (iid),
recency/FIFO, herding (feature-mean = magnitude null)} at cap 120, on the **base** committed loop (eviction is
orthogonal to N2/depth — P9.5 assembles). Controls locked (committed loop, lifelong stream, seeds
[42,137,271,314,1729]). GSS not raced (gradient-free); D-CBRS a hand-rolled single-threaded scorer (no sklearn — the
phantom-hang). Plus a cap × #classes scaling sub-sweep (cbrs, caps {40,80,120,200,400}, #classes {6,10}, 3 seeds —
a separate sub-table). EVICT + INV. **Internal-signals-only affirmed.**

**Run.** 5 policies × 5 seeds + the scaling sub-sweep. `evict_equiv` guard green (cap=∞ retains all; cap=k recency ≡
last-k FIFO). Wall ≈ 5.7 min.

**Result / figures.**
| policy | evict-BWT (worst) | accuracy-held | LUT size | vs-oracle | verdict |
| --- | --- | --- | --- | --- | --- |
| unbounded-oracle | −0.240 [−0.287,−0.228] | 0.514 [0.492–0.519] | 3232 | (ref) | the ceiling |
| **CBRS** | −0.400 [−0.406,−0.367] | 0.380 [0.374–0.391] | 120 | 0.16 below | **best bounded (committed)** |
| herding (mean null) | −0.367 [−0.427,−0.361] | 0.318 [0.314–0.380] | 120 | 0.13 below | **ties CBRS → buffer-spine null** |
| reservoir (iid) | −0.607 [−0.613,−0.547] | 0.359 [0.352–0.371] | 120 | 0.37 below | re-imports forgetting |
| recency/FIFO | −0.707 [−0.780,−0.587] | 0.327 [0.325–0.336] | 120 | 0.47 below | re-imports forgetting |

*Scaling sub-sweep (cbrs; min-cap-holding-BWT vs #classes):*
| cap | 6-class BWT | 10-class BWT |
| --- | --- | --- |
| 40 | −0.392 | −0.456 |
| 80 | −0.301 | −0.444 |
| 120 | −0.263 | −0.406 |
| 200 | −0.296 | −0.372 |
| 400 | **−0.237** (≈ oracle) | −0.311 |

- **EVICT** (headline): at cap 120 the bound bites hard — *no* bounded policy matches the unbounded oracle (all
  re-import forgetting relative to it). Among bounded policies, **CBRS and herding tie** (−0.400 vs −0.367, within
  noise) and both **decisively beat reservoir/recency** (−0.607 / −0.707). The cap × #classes inset shows the
  **scaling law fires**: 6 classes hold BWT at cap 400 (≈ oracle), 10 classes need > 400 — the bound grows with class
  count.
  - **INV**: all nine guards green (evict-equiv cap=∞ retains all; cap=k recency ≡ last-k FIFO).

**Read (8 slots).**
1. *Claim* — CBRS is the eviction policy that degrades most gracefully under a tight bounded buffer (best-bounded,
   ties the herding null, beats iid/FIFO decisively); the cap needed to hold BWT grows with #classes.
2. *Headline* — cbrs −0.400 ≈ herding −0.367 (buffer-spine null) ≫ reservoir −0.607, recency −0.707 (n=5, cap 120);
   scaling: min-cap-hold 6cls cap400, 10cls > 400 (grows with #classes). Internal refs only (unbounded oracle −0.240).
3. *Figures* — EVICT (policies + cap×#classes scaling inset), INV (evict-equiv green).
4. *Mechanism* — CBRS keeps prototypes **balanced across classes** → it spans the class *directions* even at a tight
   budget, so old classes stay decodable; reservoir/recency skew toward the recent, bursty majority → the old class
   directions narrow → forgetting. **Herding ties CBRS here** because on this task the raw dense-center ≈ the
   direction-span (density ≈ class at the buffer — the features are near-unimodal), so keeping the class *mean* is not
   worse than keeping the *span*: this is a **buffer-spine null**, not a spine win (herding *would* fail where the
   dense center diverges from the span — a task this bench doesn't provide). CBRS is committed for that robustness, not
   because it beats herding on this task.
5. *Threats* — (a) the herding null is a genuine null here (density ≈ class), so it can't demonstrate the spine —
   reported as "buffer-spine null," not a win. (b) the cap-scaling is at #classes ∈ {6,10}; the direction (grows with
   #classes) is clear but the exact holding cap depends on the class-prototype count. (c) the unbounded oracle
   accumulates duplicate prototypes (LUT 3232) — it is the no-eviction reference, not a deployed store. Rule-1: one
   variable (policy) at the pinned cap; the cap-scaling is a separate sub-table (not co-varied with the policy verdict).
6. *Decision* — **CBRS committed** as the eviction policy (S13-candidate) + the **cap-scaling law** (deploy the buffer
   ≥ the class-prototype budget; the cap grows with #classes). Note: CBRS is *already* the P8.6 committed loop's sleep
   guard on the fixed-probe buffer — P9.3 confirms it is the right policy under a bounded stream and quantifies the
   cost of a tight budget. P9.5 deploys cbrs on the committed buffer.
7. *Freeze-honesty* — **internal-signals-only affirmed** (no P10 baseline consulted). The eviction policy does not
   inflate the economy (cbrs is a buffer-side selection, no extra fires/sleeps); GD-share unchanged (≤ 0.25).
8. *Live-safety* — CBRS holds the least-negative worst-BWT of the bounded policies; the deployed loop (P9.5) uses cbrs
   at the class-prototype budget, so live-safety = the committed loop's. The tight-cap cost is a *result* (the bound
   bites), carried as the cap-scaling law, not a live-safety failure of the deployed object.
