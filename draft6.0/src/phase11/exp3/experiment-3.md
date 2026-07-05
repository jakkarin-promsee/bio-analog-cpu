# P11.3 — the real-world streams (the phase HEADLINE): does the frozen recipe survive nature's own drift?

**Question.** Every P1–P10 number lived behind a synthetic porthole. Take the P9-frozen object to **four real-world
streams** — gas sensor drift (nature's own gauntlet, Vergara 2012), HAR by-subject, electricity + covertype (the
streaming canon) — and read the pinned channel: **prequential balanced accuracy** (pre-update, every learner incl.
no-change; R2), vs the **stronger** of two per-arena-tuned ER points (byte-matched + bigbuf; R3), with the mandatory
**no-change** persistence baseline (the ELEC2 autocorrelation trap; D2) and the sgd-linear + first-block-frozen
controls (R11/R5). Does OURS win where drift is real — or does nature erase the synthetic-gauntlet differentiator?

**Setup.** Roster per stream = {OURS-A (porthole-40), OURS-B (recipe native-D), ER-matched (byte-matched buffer),
ER-bigbuf (cap min(10%,5000)), sgd-linear (native, lr tuned seed-7), first-block-frozen, no-change}. Scaler fit on
the **first natural block only**, frozen; every learner sees the same projected stream. Accuracy channel =
prequential balanced accuracy over the full stream (covertype: balanced, its 10:1 imbalance mandates it). gas
reversed-order committed (nature fixed the order → seeds vary init+projection only). 5 seeds (covtype 3, declared
heavy: native-54, 40k slice). STREAM-{gas,har,electric,covtype} + the fight tables.

**Result — gas WINS; the streaming canon FLOORs under persistence (honestly, as pre-registered).**

| stream | C / native | OURS-A | OURS-B | stronger-ER | sgd-lin | frozen | no-change | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **gas** | 6 / 128 | **0.789** [.78–.82] | **0.856** [.85–.88] | 0.756 | 0.518 | 0.213 | 0.605 | **WIN** |
| har | 6 / 561 | 0.686 [.68–.70] | 0.820 [.82–.82] | 0.754 | 0.429 | 0.707 | **0.950** | FLOOR |
| electric | 2 / 8 | 0.606 [.61–.61] | 0.596 [.59–.60] | 0.687 | 0.594 | 0.544 | **0.836** | FLOOR |
| covtype | 7 / 54 | 0.471 [.47–.48] | 0.472 [.46–.48] | 0.542 | 0.504 | 0.591 | **0.646** | FLOOR |

- **gas — the headline WIN.** OURS-A 0.789 ≥ stronger-ER 0.756 (Δ +0.033, real-difference bar) at prequential
  balanced accuracy, and **beats persistence by +0.184** (no-change 0.605 → the cells are informative, not a
  floor). Arm B (native-128) lifts it further to **0.856** — the porthole was costing ~0.07, the scaling recipe
  recovers it. On nature's own sensor-aging drift, the frozen recipe is the strongest online learner in the room.
- **har / electric / covtype — FLOOR (field leads +0.07).** On these three, **no raced learner beats the no-change
  baseline** (persistence 0.950 / 0.836 / 0.646) — the ELEC2 label-autocorrelation trap (Souza 2020, D2) fires
  exactly as pre-registered: the streams are so autocorrelated that "predict the previous label" is near-unbeatable
  by any online model, ours or ER. The cell is grey — **two-sided**: inside the floor, the stronger ER leads OURS by
  har +0.068 / electric +0.081 / covtype +0.071 (the anti-hype guard is not an anti-loss shield — the field is
  ahead on these, and the map says so). OURS-B closes most of the har gap (0.820) but the persistence wall stands.
- **worst-point BWT on real drift is genuinely negative** (OURS-A gas −0.333, har −0.233, electric −0.149, covtype
  −0.097) — **the near-zero worst-BWT was a synthetic-gauntlet property; on nature's drift the SLDA frame goes stale
  between sleeps and retention dips.** Reported, not hidden. (Power caveat, R8: gas batches 4/5 carry ~32–40 eval
  samples < 100, so the gas worst-BWT is dominated by the smallest blocks and is under-powered; the **prequential
  accuracy is the pinned headline read**, not the worst-BWT.)
- **order-invariance (gas): |AA(fwd)−AA(rev)| = 0.043** — OURS is near order-invariant even on nature's real drift
  (forward 0.789 / reversed 0.832; the reversed order is slightly *easier*, not a symmetry break).

**Read (8 slots).**
1. *Claim* — on real-world streams the frozen recipe wins where drift is genuine and information-bearing (gas), and
   FLOORs (with the field ahead) where the stream is dominated by label persistence (har/electric/covtype). The map
   ships both.
2. *Headline* — gas OURS-A **0.789** ≥ stronger-ER **0.756**, no-change 0.605 (WIN, +0.184 over persistence);
   OURS-B **0.856**. Three streams FLOOR under no-change {0.950, 0.836, 0.646}, field ahead by ~0.07.
3. *Figures* — `STREAM_gas.png` (the headline — OURS vs ER-strong riding above persistence, OURS steadier where ER
   spikes down at drift boundaries), `STREAM_har.png`, `STREAM_electric.png`, `STREAM_covtype.png` (OURS vs ER-strong,
   both under the persistence wall, ER just ahead — the two-sided floor visible batch-by-batch).
4. *Mechanism* — gas drift is a **coherent covariate shift** (sensors age): the SCFF bulk + sleep re-anchoring
   tracks the manifold while the closed-form namer never catastrophically forgets → OURS rides the drift. On HAR/
   ELEC2/covtype the *label* is autocorrelated (long runs of one class), so persistence — which the streaming field
   flags as a trap — beats every model that actually looks at the features; drift-difficulty and data-difficulty are
   different axes and this rung separates them by measurement.
5. *Threats* — (i) **projection loss**: the →40 porthole discards native structure (Arm B's native-D bounds it —
   gas +0.067, har +0.134); (ii) **R8 power**: gas small batches make its worst-BWT under-powered (prequential is
   the headline); (iii) **stream-order provenance**: covertype has no timestamp (file-order convention stated);
   (iv) the gas dataset's published limitations (Dennler 2022) — balanced accuracy + the composition table respond
   to it; (v) real streams have one natural order (seeds vary init/projection only; McNemar-on-prequential is the
   per-stream significance read where seeds cannot resample).
6. *Verdict* — **gas WIN** (deployment story complete on nature's drift); **har/electric/covtype FLOOR (field leads
   +0.07)** — the honest ELEC2 outcome, banked as a grey column with its two-sided delta, never as parity.
7. *Recipe-honesty* — Arm A bit-equal committed (recipe-guard clean); Arm B recipe-guard clean ({D,W,cap} only); ER
   re-tuned per arena on the disjoint seed-7 stream (the asymmetry against the home team); no-change + sgd-linear +
   first-block-frozen present (stream-controls guard); the accuracy channel is prequential (R2), pinned, no post-hoc
   choice; nothing tuned in either arm.
8. *Where-it-stands* — the real-world columns of the LIMIT-MAP: **gas = WIN (teal)**; **har/electric/covtype =
   FLOOR (grey, field +0.07)**. The real-world verdict banks **"wins on real information-bearing drift; floors under
   label-persistence, where the field also floors but leads."** Gas is the professor-pitch headline: *the frozen
   recipe, untouched, is the best online learner on a famous real sensor-drift benchmark.*

**Design deviations (commented, per the author's leave to change the plan on the result):** ER tuning used a modest
grid (lr {0.1,0.03} × replay {2,4} × hidden {1,2}) for the overnight budget (full grid pinned in the bench
manifest); covtype ran 3 seeds / 40k-slice (declared heavy). No iid-shuffled OURS control this pass (optional, §2.4)
— owed if the drift-vs-data separation wants a per-stream measurement beyond the mechanism argument above.

*Guards: arena-data ✓ (stream order asserted) · recipe A/B ✓ · stream-controls ✓ (no-change + sgd + frozen present)
· budget-report ✓ · floor-criterion ✓. n=5 (covtype 3, declared).*
