# P8.5 — The metered 80/20: the first honest split, and OURS vs BP+replay

**Question.** Inheriting the SLDA-committed head (P8.4) and the committed economy (DDM gate + direction trigger + grid-8
sleep): with the gate on, what fraction of total substrate energy is the GD namer (op (c) fire + (d) sleep-solve/write)
vs the unsupervised SCFF (op (a) forward + (b) inference)? Is it ≤ 0.25 — the founding 80/20, now **metered, not
proxied**? And how does OURS's total energy compare to a **BP+replay** model at matched retention on the same substrate
table?

**Setup.** Swept variable = the gate config ∈ {committed (DDM), always-pay (no gate)}. Controls locked (live bulk, SLDA
head, direction trigger, checkpoint sleep, CI+nuisance stream, seeds [42,137,271,314,1729]). GD-share = E[(c)+(d)]/E_total;
the sleep LUT re-forward is unsupervised SCFF forward and is charged to the SCFF share, not the namer. The BP model =
backward pass every step + full-weight writes + a replay mini-batch sized to reach OURS's retention (iso-weight-budget
MLP [40,130,130,130,10]), NOT a naive backward-every-step BP that forgets. Figures: METERED-8020 (+ bp panel), INV.

**Run.** 2 configs × 5 seeds; per-op energy from the fire/sleep trace + the BP+replay energy model. Wall ≈ 4.9 min.

**Result / figures.**
| config | GD-share | SCFF-share | bp_ratio (OURS / BP+replay) | verdict |
| --- | --- | --- | --- | --- |
| **committed (DDM gate on)** | **0.121 [0.121–0.121]** | 0.879 | 0.501 [0.501–0.501] | **80/20 CONFIRMED** |
| always-pay (no gate) | 0.778 [0.778–0.778] | 0.222 | — | no-gate ceiling |

- **METERED-8020** (headline): with the gate on, the GD namer is **12.1%** of total energy — under the 25% line, and the
  first time the "80/20" is a metered number rather than an op-count tag. Turn the gate *off* (always-pay) and the namer
  balloons to **77.8%** — the gate is not a nicety, it is what *creates* the 80/20. The bp panel: OURS draws **0.501×**
  the energy of a BP+replay learner at matched retention on the same substrate table — roughly half.
  - **INV**: meter-proxy + partial-fit-equiv guards green.

**Read (8 slots).**
1. *Claim* — with the committed gate on, the GD namer is ≤ 0.25 of total metered energy (the 80/20 is real, not a
   proxy), and the whole economy costs about half of a fair BP+replay learner at matched retention.
2. *Headline* — committed GD-share 0.121 [0.121–0.121] (vs always-pay ceiling 0.778); bp_ratio 0.501 [0.501–0.501]
   (n=5, live CI+nuisance; behavioral ADC-centred meter).
3. *Figures* — METERED-8020 (GD/SCFF stacked + bp panel), INV (guards green).
4. *Mechanism* — the gate fires the namer on ~0.003 of steps (P8.1), so op (c) is tiny; the only recurring GD cost is the
   periodic sleep-solve (op (d)), and even that re-forward is charged to SCFF (it is an unsupervised forward pass). So the
   namer's energy is a thin 12%. Without the gate, the namer runs `partial_fit` every step — op (c) fires on all 336
   steps — and its share jumps to 78%, confirming the gate is the mechanism, not the head. Against BP+replay: BP pays a
   3× forward + 2× ADC backward pass *every* step plus replay, while OURS pays one forward + a rare solve — hence
   bp_ratio ~0.5 even though the substrate weight-update itself is cheap (a local analog nudge) in *both* models.
5. *Threats* — (a) the meter is behavioral (params + citations logged, P8.4). (b) The BP model is BP+**replay at matched
   retention** on the *same substrate table* — a fair fight on the *energy* axis, not the strawman naive-BP-that-forgets;
   the fair *accuracy* fight (same buffer/compute) is still Phase 9's existential test. (c) GD-share depends on the gate's
   fire-rate, which is drift-rate-conditional (P8.3); a faster drift raises it. (d) bp_ratio's zero IQR reflects the
   deterministic op-count given a fixed schedule, not implausible precision.
6. *Decision* — **discharges the arch-file's "net energy win unquantified" caveat**: the metered 80/20 (GD-share 0.121)
   replaces every "80/20 (proxy)" tag where the meter actually ran (P8.4/P8.5). Sets the headline economy number the
   assembled run (P8.6) reports.
7. *Economy-honesty* — GD-share is E[(c)+(d)]/E_total with the sleep re-forward correctly attributed to SCFF; bp_ratio is
   vs BP+replay at matched retention on the same substrate table (not naive BP); the meter model + params are tagged. The
   always-pay ceiling (0.778) is reported so the gate's contribution is not hidden.
8. *Live-safety / namer* — the 80/20 is realized *by the SLDA head* (the P8.4 commit), confirming the cheaper namer also
   delivers the economy. Live A6 safety of this exact loop is P8.6.
