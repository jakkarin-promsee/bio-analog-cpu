# Phase 8 — RESULTS (the scalar ledger)

> One section per rung, the fixed §D row schema (no prose). Controls locked unless swept. Device under test = the
> frozen-as-a-DESIGN `NoiseAugContrast` cell (SCFFContrastOverlap temp0.2/w2, L12, +iid-noise view σ_aug=1.0) + the
> committed Phase-7 namer (RanPAC + cbrs; SLDA the metered fallback), run **LIVE** (SCFF trains forward-only on every
> input; the namer tracks the drift via the awake gate + periodic sleep). Seeds `[42,137,271,314,1729]`. Median
> `[q25–q75]`. The cost meter is a **behavioral ADC-centred model** (params + citations in each manifest), NOT SPICE.

Full ladder ran 2026-07-02 (seeds `[42,137,271,314,1729]`, `--quick` off, git `e6993d5`, numpy 2.3.5, single-thread
CPU/float64). Wall: P8.0 850s · P8.1 1511s · P8.2 1207s · P8.3 1206s · P8.4 157s · P8.5 291s · P8.6 398s (≈94 min total).
All seven guards bit-exact every rung. Cell = `NoiseAugContrast(iid,σ_aug=1.0)+SCFFContrastOverlap temp0.2/w2/L12`.
**P8.7 (substrate ablation — EXTENSION) ran 2026-07-02, 91s** (5 seeds; meter-proxy + partial-fit guards re-checked
bit-exact — the analog path is unchanged by the digital switch).

---

## P8.0 — bench + guards + live drift + drift-visibility

*Controls: live bulk, RanPAC+cbrs, CI+nuisance stream (n_steps 336, onsets [40,88,136,184], nuis 272), 5 seeds.*

| control / guard | value | vs reference | pass? | verdict |
| --- | --- | --- | --- | --- |
| partial_fit_equiv (ranpac/slda) | 4.11e-15 / 2.22e-16, miss 0 | ≡ batch fit | ✓ | primitive faithful |
| fd_budget_gate | 3.47e-08 | ≡ analytic grad | ✓ | gate grad correct |
| meter_proxy | fwd-MAC 1 556 000 ≡ readout_cost | exact | ✓ | meter reduces to proxy |
| detector_far floor | {abs 0.0, ddm 0.0, adwin 0.0} | stationary | ✓ | floors clean |
| scff_static_frozen | 0.00e+00 (static acc 0.566) | ≡ P7 static | ✓ | frozen ≡ P7 |
| live_path_anchor | 0.00e+00 (AA 0.3602=0.3602) | ≡ continual_safety_heads | ✓ | live path faithful |
| cache_replay | 0.00e+00, fire-diff 0 | deterministic | ✓ | replay exact |
| bulk_drift (min..max) | 0.627 .. 1.000 | > 0 everywhere | ✓ | bulk doesn't forget |
| drift-vis real-onset [dir/mag/err] | 1.38 / 1.30 / 1.02 | ×calib | — | direction rises, error lags |
| drift-vis nuisance [dir/mag/err] | 0.84 / 10.00 / 0.83 | ×calib | — | direction invariant, magnitude ×10 |
| always-pay ceiling | AA 0.448, f 1.00, FAR 1.00 | — | — | cost ceiling |
| oracle-cadence ref | AA 0.448, f 0.286, FAR 0.00 | — | — | achievable reference |

---

## P8.1 — gate bake-off *(swept: gate; sleep=checkpoint, trigger=error-EMA)*

| gate | accuracy-held | GD-fire-fraction | FAR | MTD | worst-BWT | vs-oracle | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| always-pay (ceiling) | 0.448 [0.445–0.471] | 1.000 | 1.000 | 0 | −0.295 | +0.000 | cost ceiling |
| oracle-cadence (ref) | 0.448 [0.445–0.471] | 0.286 | 0.000 | 0 | −0.208 | (ref) | achievable reference |
| absolute-θ | 0.448 [0.445–0.471] | 0.027 | 0.042 | 19 | −0.167 | +0.000 | held-not-clean (false-fires) |
| DDM | 0.448 [0.445–0.471] | 0.003 | 0.000 | 40 | −0.439 | +0.000 | **committed-eligible** |
| ADWIN | 0.448 [0.445–0.471] | 0.003 | 0.000 | 40 | −0.439 | +0.000 | committed-eligible |
| budget-gate | 0.448 [0.445–0.471] | 0.000 | 0.000 | 40 | −0.444 | +0.000 | committed-eligible (spine-flagged) |

*Committed awake gate = **DDM**. absolute-θ struck: FAR 0.042 > stationary floor (magnitude leak on nuisance).*

---

## P8.2 — trigger bake-off *(swept: trigger signal)*

| trigger | MTD | FAR (nuisance) | excess-FAR | accuracy-held | lead? / verdict |
| --- | --- | --- | --- | --- | --- |
| error-EMA (labeled ref) | 14.000 [10.00–40.00] | 0.000 [0.00–0.00] | 0.000 | (at oracle) | reference |
| **tap-drift-direction** | **6.000 [5.00–11.00]** | 0.021 [0.00–0.042] | **0.000** | (at oracle) | **earns-early** |
| tap-drift-magnitude (null) | 6.500 [5.00–6.50] | 0.938 [0.938–0.938] | 0.906 | — | false-fires (spine null) |
| DriftLens (label-free ref) | 6.000 [5.00–11.00] | 0.021 [0.00–0.042] | 0.000 | — | matches tap-dir |
| STUDD (conservative) | 0.000 [0.00–0.00] | 0.896 [0.854–0.917] | 0.896 | — | degenerate (always-fires) |

*Deployed trigger = the namer's **error-EMA** (DDM's input). A **class-direction tap-drift** signal was *validated* here
(MTD 6 < error 14, excess-FAR 0.000) but **not shipped** — the north-star gate upgrade. Magnitude null FAR 0.938 = the
spine demonstration.*

---

## P8.3 — sleep cadence *(swept: frequency × history; awake=DDM)*

*Accuracy-held (ref [oracle-boundary, full] = 0.448):*

| cadence \ history | full/λ1.0 | half/λ1.0 | qtr/λ1.0 | full/λ0.9 |
| --- | --- | --- | --- | --- |
| oracle-boundary | 0.448 | 0.416 | 0.356 | 0.448 |
| grid-2 | 0.448 | 0.416 | 0.356 | 0.448 |
| grid-4 | 0.446 | 0.406 | 0.350 | 0.446 |
| **grid-8** | **0.446** | 0.406 | 0.350 | 0.446 |

*Worst-point BWT:*

| cadence \ history | full/λ1.0 | half/λ1.0 | qtr/λ1.0 | full/λ0.9 |
| --- | --- | --- | --- | --- |
| oracle-boundary | −0.439 | −0.356 | −0.333 | −0.439 |
| grid-2 | 0.000 | −0.015 | −0.017 | 0.000 |
| grid-4 | 0.000 | −0.015 | −0.061 | 0.000 |
| **grid-8** | **0.000** | −0.058 | 0.000 | **0.000** |

*Committed cadence = **grid-8, full history, λ_ema 1.0** (AA 0.446, worst-BWT 0.000, sleep-cost 10.0 — cheapest holding
A6). Flagged drift-rate-conditional. Full history load-bearing; regular cadence beats boundary-aligned; EMA-decay no
benefit.*

---

## P8.4 — cost meter *(swept: head; behavioral ADC-centred meter, pJ)*

| head | E_total | E_adc | E_solve | AA (live) | E-ratio (namer) | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| RanPAC | 2.488e8 | 5.15e7 | 2.21e7 | 0.448 [0.445–0.471] | (subject A) | — |
| **SLDA** | **2.687e7** | 1.71e7 | 1.80e6 | 0.463 [0.445–0.469] | **69.1× cheaper** | **commit SLDA** |

*E-ratio namer 69.1× · total 9.26× · ΔAA −0.015 (SLDA higher). ADC-bits sensitivity 61.0–66.1× (4→10b). Both cut
conditions met (≥2× ∧ |ΔAA| ≤ 0.02). Resolves S11.*

---

## P8.5 — metered 80/20 *(swept: gate config; head=SLDA)*

| config | GD-share | SCFF-share | bp_ratio (OURS / BP+replay) | verdict |
| --- | --- | --- | --- | --- |
| **committed (DDM on)** | **0.121 [0.121–0.121]** | 0.879 | 0.501 [0.501–0.501] | **80/20 CONFIRMED** |
| always-pay (no gate) | 0.778 [0.778–0.778] | 0.222 | — | no-gate ceiling |

*First metered (non-proxy) 80/20: GD-share 0.121 ≤ 0.25. OURS ≈ half the energy of BP+replay at matched retention on the
same substrate table. The gate creates the 80/20 (off → 0.778).*

---

## P8.6 — assembled + LIVE A6 gate *(committed vs oracle vs always-pay; head=SLDA, 5 seeds)*

| mechanism | AA (live) | worst-BWT (pre-sleep, +paired-sign) | forget | GD-share | vs-baseline | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| frozen promise (block-mode) | 0.614 [0.606–0.622] | — | — | — | (offline ref) | — |
| **committed** (DDM+cbrs+grid-8) | **0.447 [0.426–0.448]** | **0.000 [0.000–0.000]** (0/5 neg) | 0.000 | 0.155 | = oracle | **LIVE-SAFE** |
| oracle-cadence | 0.447 [0.426–0.448] | 0.000 [0.000–0.000] | 0.000 | 0.492 | (ref) | reference |
| always-pay (no gate) | 0.474 [0.474–0.485] | −0.137 [−0.153,−0.135] | — | 0.747 | forgets | cost+forgetting ceiling |

*Paired veto 0/5 more-negative than oracle → PASS; AA-match OK → **LIVE-SAFE**. The disciplined economy is cheaper
(GD-share 0.155 vs 0.747) **and** safer (worst-BWT 0.000 vs −0.137) than firing always. Live-vs-frozen AA gap (0.447 vs
0.614) = task difficulty (harder live stream), not forgetting (worst-BWT 0.000).*

---

## P8.7 — substrate ablation: WHY ANALOG? *(EXTENSION; swept: model × substrate; committed economy = SLDA+DDM+cbrs+grid-8)*

*The full 2×2 — the exact committed live loop (P8.6) and the fair BP+replay baseline, re-metered on the analog crossbar
and the digital (von-Neumann / GPU-class) substrate. Digital = §2.5 (no ADC, `E_MAC_DIG=0.2` pJ Horowitz-anchored, SRAM
write, matched 8-bit). Behavioral, relative-pJ. Energy is deterministic given the fixed schedule → zero IQR.*

| model × substrate | E_total (pJ) | vs OURS-analog | verdict |
| --- | --- | --- | --- |
| **OURS · analog** (the chip) | **3.40e7** | (ref) | the proposed substrate |
| OURS · digital | 1.83e8 | 5.37× | our algorithm without CIM |
| GD+replay · analog | 5.37e7 | 1.58× | algorithm-only ablation (OURS/GD = 0.63, cf. P8.5 checkpoint 0.50) |
| GD+replay · digital (status quo) | 5.23e8 | 15.37× | conventional GD on a digital accelerator |

*Win decomposition (median [IQR], deterministic):*

| win | ratio | meaning |
| --- | --- | --- |
| **substrate** (OURS digital/analog) | **5.37×** | CIM vs von-Neumann, same algorithm — *why analog* |
| **algorithm** (digital GD/OURS) | **2.86×** | our 80/20 vs real backprop+replay, same digital substrate |
| **TOTAL** (GD-digital / OURS-analog) | **15.37×** | what the chip buys = substrate × algorithm (5.37 × 2.86 = 15.4 ✓ identity) |

*80/20 holds on both substrates: GD-share analog 0.155 / digital 0.109 (the gate's split is substrate-independent).
`E_MAC_DIG` memory-wall sweep (substrate win): 0.1→2.74× · 0.2→5.37× (Horowitz) · 0.5→13.3× · 1.0→26.5× · 2.0→52.9× —
analog wins even at the most-generous arithmetic-only digital (2.74× ≫ 1), so the reported advantage is a **floor**, not
a knife-edge. Committed reading: **the analog substrate is ~5× of the total ~15× win; the 80/20 algorithm is the other
~3×.***

