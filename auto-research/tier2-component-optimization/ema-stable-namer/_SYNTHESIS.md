# Synthesis — EMA "stable namer" (temporal averaging of closed-form statistics)  (Tier 2, t2.7)

**The question:** Is a slow **"stable namer"** — built by EMA-ing the *closed-form namer's own running statistics* (`Σ_stable ← α·Σ_stable + (1−α)·Σ_fast` over the SLDA mean+covariance / RanPAC Gram) — **sound and worth building**? Is averaging *second-order* statistics principled (an SPD EMA stays SPD, but is the *implied classifier* well-behaved)? Rank concrete variants by stability-benefit × substrate-fit (the Scap is already an EMA register).

**Already in `draft6.0/research/` and prior cards:** `survey/momentum.detail.md` (Polyak/heavy-ball EMA + the Scap-as-EMA-momentum register); CLS-ER (Arani 2022) & ESMER (Sarfraz 2023) as t1.4 — the *built* slow-EMA "stable memory" for CL — **referenced, not re-carded**. Ledoit-Wolf 2004 & Chen 2010 OAS shrinkage sit under `closed-form-classifier` (a *spatial* covariance regularizer, complementary to a *temporal* one). This card set adds the **engineering-native averaging theory** (Polyak, SWA, soups, Mean-Teacher, Lookahead, EMA-scaling/dynamics, the 2025 averaging benchmark) and — the load-bearing addition — the **SPD/covariance-averaging soundness literature** (log-Euclidean swelling; Riemannian geometric-mean classifiers).

## The landscape (the field)

**1. Temporal parameter averaging is one of ML's most reliable free lunches.** Polyak–Ruppert (1992) proved that averaging noisy stochastic-approximation iterates attains the *optimal* asymptotic covariance — averaging *is* variance reduction. SWA (Izmailov 2018) and model soups (Wortsman 2022) cash this out as flatter, better-generalizing solutions at zero inference cost. Mean-Teacher (Tarvainen 2017) turns the same EMA into a **slow "teacher" anchor** — the exact "stable memory" CLS-ER/ESMER rebuild for continual learning. Lookahead (Zhang 2019) is the cleanest **two-timescale** schematic: fast weights explore, slow weights `slow ← slow + α(fast − slow)` (an EMA) and periodically pull the fast state back. Modern work sharpens the knob: "How to Scale Your EMA" (Busbridge 2023) treats the momentum as a **timescale** (horizon ≈ 1/(1−α) updates) that must be scaled to the fast track's rate; the TMLR study (Morales-Brotons 2024) catalogues what weight-EMA actually buys — **noisy-label robustness, prediction consistency, calibration, transfer, and reduced LR-decay need**; and the 2025 AlgoPerf comparison (Ajroldi) reality-checks the size of the win as **real but modest** and tightly coupled to the LR schedule.

**2. Averaging *second-order* statistics is where it gets subtle — and the field has a clear verdict.** Covariances / Gram matrices are **symmetric positive-definite (SPD)** — points on a curved cone, not a flat vector space. Two facts settle the soundness question. **(a) Validity:** the SPD cone is *convex*, so any convex combination `α·A + (1−α)·B` of SPD matrices is SPD. An arithmetic EMA of covariances therefore **always stays a valid covariance** — the head never breaks. **(b) Statistical bias:** the *arithmetic* mean of SPD matrices exhibits the **swelling effect** (Arsigny 2006) — the determinant of the mean can exceed that of the inputs, artificially inflating variance/volume. The principled fix is the **geometric mean** (affine-invariant, or the cheap **log-Euclidean** `exp(mean(log Σ))`), which is swelling-free. Real closed-form classifiers are built on exactly this geometric mean of covariances — the Riemannian MDM BCI decoder (Congedo 2013) uses running geometric-mean-covariance prototypes and is prized for **drift/session robustness** — the property we want.

## How WE differ  ← the money section

**What is genuinely ours (a composition, not a published result):** the specific idea of EMA-ing a **closed-form continual namer's sufficient statistics** to get a zero-gradient "stable namer" — a *closed-form* CLS-ER. Nobody in these papers does closed-form-CLS-with-a-statistic-EMA; CLS-ER/ESMER EMA *network weights* with a gradient loss.

**But the mechanism is mostly re-invention — and that's reassuring, not disqualifying, and it splits by channel:**
- **The mean-vector channel (SLDA class means): a plain Polyak/Mean-Teacher average.** Means are ordinary Euclidean quantities → arithmetic EMA is *exactly right*, fully principled, textbook. ✅
- **The Gram channel (RanPAC running `XᵀX`): this is Recursive Least Squares with a forgetting factor.** An EMA of the Gram = RLS-with-λ. That is textbook adaptive filtering, *not* our invention — and we **already have `RLSHead` in `p7lib.py`**. So "stable namer via Gram-EMA" largely reduces to *deploying a slow-forgetting RLS namer*. Principled, but not new. ✅ (valid) / ⚠ (novelty)
- **The covariance channel (SLDA tied covariance): valid but it *swells*.** Arithmetic EMA stays SPD (never breaks) but biases the implied Gaussian/LDA toward an **over-inflated, softened** decision boundary (Arsigny). The clean fix — log-Euclidean / geometric EMA — costs a `logm`/`expm`, feasible **at sleep** but **not** substrate-native per-step. ⚠

**The substrate-fit asymmetry that decides the ranking:** the Scap **already is a 16-bit EMA register** — so a slow *arithmetic* EMA of means/Gram is *nearly free* to add (a second register at a slower α). The **geometric** mean is *not* substrate-native. So the deployable form is the arithmetic EMA, with the geometric mean available only as a sleep-time correction or a diagnostic ceiling.

**The honest challenge from our own P9:** grid-4 sleep already drove worst-BWT to **−0.028** (ties the oracle), and P9.1 found an **EMA-view *worsened* worst-BWT** because averaging across a bulk *rotation* averages incompatible frames (the SWA/soup "shared-basin" precondition, violated by rotation). So a stable namer only earns a phase if it beats **cheaper/denser sleep** — its real target is the **inter-sleep worst-point trough** (De Lange stability-gap, already carded t2.3): can a slow statistic-EMA flatten the trough *between* sleeps without a LUT re-fit?

## The gap / what we haven't tried (concrete, testable)

**The single lever:** a **two-timescale namer** = fast SLDA/RanPAC (tracks drift, deployed) **+** a slow **stable namer** = EMA of its statistics at large α, used *between sleeps* as an inference anchor (ensemble the two, or interpolate the fast head toward the slow one, Lookahead-style). **Success bar (honest, per Ajroldi):** it must **flatten the inter-sleep worst-point BWT trough at equal-or-lower sleep cost than grid-4** — i.e. buy stability *between* sleeps, not just duplicate sleep.

Ranked variants by (stability benefit × substrate-fit):
1. **EMA-of-Gram (= slow-forgetting RLS), reusing `RLSHead`.** Best fit: SPD-valid, Scap-native, no swelling concern for a *ridge solve* (the Gram feeds an inverse, and RLS-with-forgetting is the principled object). Cheapest to test — largely a config of existing code. **Build first.**
2. **EMA-of-class-means (Polyak/Mean-Teacher on the SLDA means).** Fully sound, Scap-native, one register. Pair with #1.
3. **Arithmetic EMA-of-tied-covariance.** Valid but swells; test *with a swelling check* on the implied boundary. If it degrades → escalate to #4.
4. **Log-Euclidean (geometric) EMA of the covariance, at sleep only.** The principled fix; one `logm`/`expm` per sleep. The ceiling / fallback, not the daily driver.
5. **α scaled to the measured drift rate** (Busbridge horizon rule + Webb-2016 drift vocabulary) so the anchor spans ~one rotation epoch — makes the knob self-tuning instead of a fixed guess; guards against the P9.1 "averaged across a rotation" failure.

**Do-first micro-check (no full experiment):** numerically confirm whether swelling actually moves an **LDA decision boundary** (vs a generative density) on our features — if the swelling bias is negligible for a *tied* covariance at our α, the whole geometric-mean escalation is unnecessary and #1–#3 arithmetic EMAs are the complete answer.

**Verdict:** **Sound, and worth a small phase-experiment — but scoped and de-hyped.** The averaging is principled (SPD-valid always; mean/Gram channels are textbook Polyak/RLS; only the covariance channel swells, with a known cheap fix). Substrate fit is excellent for the arithmetic form (the Scap IS an EMA). The literature predicts a **real but modest** stability/consistency/calibration gain — so the bar is beating *cheaper sleep* on the inter-sleep trough, not beating "no averaging." Flag clearly: **the "closed-form CLS-ER" framing is ours; the Gram-EMA mechanism is RLS-with-forgetting (we already have `RLSHead`), and the covariance-swelling caveat is a published result (Arsigny 2006), with the geometric mean (Congedo-style) as the principled — but non-substrate-native — ceiling.**

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Polyak & Juditsky 1992 — Averaging](polyak-juditsky-1992-averaging.md) | ⭐⭐⭐⭐ | Averaging noisy estimates is *asymptotically optimal* — the theorem under the mean-channel EMA (but stationary → we need forgetting). |
| [Izmailov 2018 — SWA](izmailov-2018-swa.md) | ⭐⭐⭐ | Averaging finds flatter, more general solutions — *if* iterates share a basin (violated by bulk rotation). |
| [Wortsman 2022 — Model Soups](wortsman-2022-model-soups.md) | ⭐⭐ | Averaging even independent models helps; the shared-basin precondition + greedy accept-only-if-it-helps guard. |
| [Tarvainen & Valpola 2017 — Mean Teacher](tarvainen-2017-mean-teacher.md) | ⭐⭐⭐⭐ | The literal slow-EMA stability anchor (parent of CLS-ER); ρ≈0.99–0.999 regime. |
| [Zhang 2019 — Lookahead](zhang-2019-lookahead.md) | ⭐⭐⭐ | The two-timescale fast/slow template + "1 step back" = interpolate-at-sleep instead of re-fit. |
| [Busbridge 2023 — How to Scale Your EMA](busbridge-2023-how-to-scale-your-ema.md) | ⭐⭐⭐⭐ | α is a *timescale* (horizon ≈ 1/(1−α)); scale it to the drift rate, don't fix it. |
| [Morales-Brotons 2024 — EMA Dynamics & Benefits](morales-brotons-2024-ema-dynamics.md) | ⭐⭐⭐⭐ | The benefit catalogue (noisy-label robustness, consistency, calibration) = our stability wishlist; averaging can substitute for re-fit frequency. |
| [Ajroldi 2025 — When/Where/Why to Average](ajroldi-2025-when-where-why-average.md) | ⭐⭐⭐ | The honest size of the win: real but **modest** → set the success bar as "beats cheaper sleep." |
| [Arsigny 2006 — Log-Euclidean](arsigny-2006-log-euclidean.md) | ⭐⭐⭐⭐⭐ | **The soundness verdict:** arithmetic covariance EMA is SPD-valid but **swells**; log-Euclidean (`exp(mean(log Σ))`) is the cheap swelling-free fix. |
| [Congedo 2013 — Riemannian BCI (MDM)](congedo-2013-riemannian-bci.md) | ⭐⭐⭐⭐ | A working closed-form namer built on **geometric-mean covariance** prototypes — drift/session-robust; the principled ceiling for a covariance stable-namer. |

## Leads spawned
- **RLS-with-forgetting-factor as a namer** (t2.x) — formalize that EMA-of-Gram = forgetting-RLS; benchmark `RLSHead` in slow-forget mode as the stable namer directly.
- **Fisher-weighted / statistically-weighted averaging** (Matena & Raffel 2022) — a *precision-weighted* soup; the closed-form analog of trusting low-variance statistics more.
- **Tangent-space (log-Euclidean) linear classifier over log-covariances** — a flat, swelling-free covariance namer; bridges Arsigny↔Congedo↔SLDA.
- **Does swelling move an LDA boundary?** — a numeric soundness probe (generative density vs discriminative boundary sensitivity to determinant inflation).
- **Two-timescale SA (Borkar)** — the convergence theory for a coupled fast-namer / slow-anchor system under drift.
- **Averaging × sleep-cadence substitution** — the analog of Ajroldi's averaging×LR-annealing: can a slow anchor let us sleep *less often*?
