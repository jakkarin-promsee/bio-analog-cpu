# Experiment P4.6 — noise robustness (A7): the substrate axis

> **Status: ✅ DONE (2026-06-22) — an HONEST NEGATIVE.** The plan expected OURS to *win* here ("forward-only is
> hardware-noise-robust" — Distance-Forward, the analog-IMC corpus). It doesn't, under this noise model. Method:
> train each racer CLEAN, inject multiplicative Gaussian **weight noise** (`W -> W*(1+σ·N(0,1))` — the analog Scap
> programming/read model) at eval, sweep σ, measure accuracy + RETENTION `acc(σ)/acc(0)`. Task: flat `make_gauss`
> (dim 40, 4-class). 5 seeds, 5 noise draws/cell. Run: `OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u
> run_p4_6.py` (105s). Contract: [`../result-format.md`](../result-format.md).

---

## The 6+2 slot read

**1 · Claim.** **Hypothesis REFUTED (for this noise model): OURS is *not* more weight-noise-robust than tuned BP —
it is the *least* robust of the three.** Under eval-time multiplicative weight noise, **BP retains best** (0.875 at
σ=0.4), Mono second (0.786), **OURS worst (0.754)**. The "forward-only is noise-robust" expectation fails here — a
clean negative the "check everything before going farther" gate was built to catch. **Important scope:** this is
*eval-time* noise on a *clean-trained* model; the literature's robustness claim is about noise **during learning**
(hardware-aware / on-chip), the substrate's *actual* regime — untested here and the proper follow-up.

**2 · Number + IQR** (median over 5 seeds; retention = acc(σ)/acc(0)):

| σ | OURS acc | BP acc | Mono acc | OURS ret | BP ret | Mono ret |
| --- | --- | --- | --- | --- | --- | --- |
| 0.00 | 0.795 | 0.823 | 0.734 | 1.000 | 1.000 | 1.000 |
| 0.10 | 0.783 | 0.814 | 0.733 | 0.987 | 0.992 | 0.989 |
| 0.20 | 0.740 | 0.801 | 0.695 | 0.935 | 0.974 | 0.946 |
| 0.40 | 0.600 | 0.722 | 0.575 | **0.754** | **0.875** | 0.786 |

**BP's retention curve is flattest** (most robust); OURS and Mono (the two forward-only/local methods) degrade more
and similarly. The ordering is consistent across all 5 seeds.

**3 · Figures.** `NOISE_CURVE` (left: accuracy vs σ with seed-IQR bands — BP stays highest, OURS & Mono fall faster;
right: retention — BP's curve flattest, OURS lowest).

**4 · Mechanism (the likely culprit — and a real tradeoff).** OURS's **per-sample layernorm** — the very thing that
gives it nuisance-dimension robustness (A2) — appears to make it **weight-noise-sensitive**: layernorm
re-normalizes after each noisy matmul, so multiplicative noise that perturbs the activation *direction* isn't
damped (only the magnitude is renormalized), and that direction error **compounds through 4 layernormed layers +
the all-tap readout** that reads all of them. BP (plain ReLU MLP, no layernorm) tolerates multiplicative weight
*scaling* better (ReLU is scale-tolerant; softmax is shift-tolerant). So **A2's robustness and A7's fragility share
one cause** — layernorm — a genuine architectural tradeoff, not a bug.

**5 · Threats / scope (load-bearing here).** (a) **Eval-time noise on a clean-trained model is the worst case for
any method and NOT the substrate's regime** — the chip learns *online with the analog noise present*, where models
**adapt** to noise (hardware-aware training); that is where the literature's forward-only robustness claim lives,
and it is **untested here**. So this negative refutes a *narrow* (and somewhat strawman) version of the hypothesis,
**not the substrate thesis.** (b) Multiplicative weight noise only — additive / activation / PVT noise may order
differently. (c) One flat task. (d) OURS retention 0.75 at heavy σ=0.4 is still *graceful* (not catastrophic) — it
loses the *comparison*, not the function.

**6 · Decision.** **A7 = a non-win (mild loss) for OURS under eval-time weight noise — do NOT claim noise-robustness
as a substrate selling point yet.** **Carry forward:** (i) the **layernorm robustness↔noise-sensitivity tradeoff**
is real (A2 win and A7 loss share a cause) — a knob, not a verdict; (ii) the **decisive test is train-with-noise**
(hardware-aware / online-with-noise), which is the substrate's real regime and the literature's actual claim —
**route to Phase 5** (it couples to the analog/PVT realism layer); (iii) this corrects the plan's optimistic
"expected win."

**7 · Cost-honesty.** No cost claim here — this rung is about robustness, not backward work. (The cost story is
P4.0/P4.3's: cheap, depth-gated.)

**8 · Map-contribution → P5.** A7 tile: **eval-time weight-noise robustness is a non-win for OURS (surprising), and
it shares a root cause with the A2 win (layernorm).** Tells Phase 5: (a) **don't market noise-robustness** on this
evidence; (b) run the **train-with-noise / hardware-aware** test — the substrate's real regime — before any analog
claim; (c) treat **layernorm as a tunable tradeoff** (nuisance-robustness vs weight-noise-sensitivity), possibly
regime-dependent. A caught over-optimistic assumption is a successful pre-flight check.

---

## Reproducibility

`figs_p4_6/{manifest.json, arrays.npz, _ckpt.jsonl}`; `python plot_p4_6.py figs_p4_6`. Single-threaded, `python -u`,
`PYTHONIOENCODING=utf-8`, per-seed fsync. Pure numpy (snapshot→perturb→eval→restore weight matrices; multiplicative
σ). New: `exp6/run_p4_6.py` (`noisy_ours`/`noisy_mlp`/`noisy_mono`) + `plot_p4_6.py`.
