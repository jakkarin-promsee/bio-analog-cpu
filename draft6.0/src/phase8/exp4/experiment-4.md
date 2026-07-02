# P8.4 — The cost meter: is "no-gradient" actually cheap, and does SLDA displace RanPAC?

**Question.** Inheriting the committed gate/trigger/cadence: on the behavioral ADC-centred substrate meter, what does the
namer actually cost — and does the ~200× RanPAC/SLDA proxy gap from Phase 7 survive a real meter, with **both AA freshly
measured on the live loop** (not P7's frozen tie)? Commit SLDA iff E(RanPAC)/E(SLDA) ≥ 2 **and** |ΔAA| ≤ 0.02 live.

**Setup.** Swept variable = the deployed head ∈ {RanPAC (proj 2000, ridge 1.0), SLDA (shrinkage 1e-3)}. Controls locked
(live bulk, DDM awake gate + direction trigger + grid-8 sleep, CI+nuisance stream, seeds [42,137,271,314,1729]). Meter =
behavioral macro-model (NOT SPICE): E = n_MAC·e_MAC + n_ADC·e_ADC(bits) + n_write·e_write + n_solve·e_digital; params
e_MAC 0.01, e_ADC(8b) 0.2/step, e_write 10.0, e_digital 5e-4 pJ; citations DNN+NeuroSim, ISAAC, PUMA, AIHWKit, SAR-ADC
Walden FoM (logged in manifest). Figures: COST-METER (per-op bars), INV.

**Run.** 2 heads × 5 seeds; per-op energy tallied from the fire/sleep trace + an ADC-bits sensitivity sweep. Wall ≈ 2.6 min.

**Result / figures.**
| head | E_total (pJ) | E_gd namer (pJ) | E_adc | E_solve | AA (live) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| RanPAC | 2.488e8 | 2.251e8 | 5.15e7 | 2.21e7 | 0.448 [0.445–0.471] | — |
| **SLDA** | **2.687e7** | **3.259e6** | 1.71e7 | 1.80e6 | **0.463 [0.445–0.469]** | **committed** |

- namer E-ratio RanPAC/SLDA = **69.1×** · total E-ratio = **9.26×** · ΔAA = **−0.015** (SLDA slightly *higher* live).
- ADC-bits sensitivity (namer ratio): 4b→61.0×, 6b→62.7×, 8b→64.4×, 10b→66.1× — the RanPAC penalty is robust to the ADC
  precision assumption.
- **COST-METER** (headline): stacked per-op bars — RanPAC's namer energy is dominated by its 2000-dim random projection
  (the ADC + solve terms on a wide feature vector); SLDA's tied-covariance solve on the raw 64-dim taps is ~69× cheaper
  per name. The ADC term is the largest single component within each head.
  - **INV**: meter-proxy guard green (MAC+solve ≡ readout_cost under unit energies), all guards green.

**Read (8 slots).**
1. *Claim* — the Phase-7 cost caveat holds under a real meter: SLDA names the world ~69× cheaper than RanPAC on the
   substrate, and (freshly measured live) it ties or beats RanPAC on accuracy — so SLDA displaces RanPAC as the deployed
   head.
2. *Headline* — E-ratio 69.1× (namer) / 9.26× (total), ΔAA −0.015 [both within δ_acc]; SLDA E_total 2.69e7 vs RanPAC
   2.49e8 pJ (n=5, live CI+nuisance; behavioral ADC-centred meter).
3. *Figures* — COST-METER (per-op breakdown, RanPAC vs SLDA), INV (meter-proxy + guards green).
4. *Mechanism* — the ADC dominates, exactly as the CIM literature predicts, and RanPAC's cost is *self-inflicted by its
   own width*: a random ReLU projection to 2000 dims means every name reads out a 2000-long vector through the ADC and
   solves a 2000² Gram, whereas SLDA works in the native 64-dim tap space. On the frozen bulk (P7) their accuracies tied;
   run live, SLDA's tied-covariance prototype is marginally *more* robust to the drift (ΔAA −0.015 in SLDA's favor) — the
   projection bought nothing here. The cut's two conditions (E-ratio ≥ 2, |ΔAA| ≤ 0.02) are both met with margin.
5. *Threats* — (a) the meter is a **behavioral** model — per-op params + citations are logged in the manifest, and the
   ADC-dominance assumption is sensitivity-checked (ratio 61–66× across 4–10 bits), so the verdict does not hinge on one
   ADC number. (b) The MAC+solve sub-terms are guarded to reduce to `readout_cost` under unit energies (green); ADC/write
   are net-new terms, not reduction targets. (c) No absolute Joule is claimed — relative-pJ only.
6. *Decision* — **resolves S11's cost caveat**: commit **SLDA** as the deployed namer (RanPAC remains the P7 accuracy
   reference and the spine-cleaner option, kept in the family, not deployed). P8.5 and P8.6 run on SLDA.
7. *Economy-honesty* — the meter model + params + citations are stated (not a bare Joule); the ADC-dominance assumption
   is sensitivity-checked; the verdict is the E-ratio cut, not a hand-wave. This is the first hardware-meaningful namer
   cost the project has computed.
8. *Live-safety / namer* — **namer verdict: SLDA committed** (cheaper namer, AA ties/beats live). This is the concrete
   discharge of Phase 7's flagged fallback. A6 live-safety with SLDA is adjudicated in P8.6.
