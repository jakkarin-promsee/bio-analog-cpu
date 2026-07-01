# The forward-only noise toolbox — what the substrate demands, and what we're allowed to use

*Analog HW-aware training: Rasch et al. (Nat. Comm. 2023); AIHWKit ([2104.02184](https://arxiv.org/abs/2104.02184); APL
ML 2023); post-training IMC accuracy ([2401.09859](https://arxiv.org/abs/2401.09859)); **Variance-Aware Noisy Training**
([2503.16183](https://arxiv.org/abs/2503.16183)); **BayesFT / Bayes-optimized noise injection** (Comm. Eng. 2023,
[s44172-023-00074-3](https://www.nature.com/articles/s44172-023-00074-3)); **noise-agnostic explainable regularizers,
correlated vs uncorrelated** ([2409.08633](https://arxiv.org/abs/2409.08633)). Forward-only flatness (the ZO-SAM
*mechanism* — SPSA/ZO-SGD; **MeZO** [2305.17333](https://arxiv.org/abs/2305.17333) scales it; **ZOSA**
[2511.09156](https://arxiv.org/abs/2511.09156) is evidence, LLM-prompt-tuning-scoped); SAM-selects-flat-late
([2410.10373](https://arxiv.org/abs/2410.10373)). In-family precedent: **Distance-Forward**
([2408.14925](https://arxiv.org/abs/2408.14925)); the named blind spot — neuromorphic on-chip local learning.*

---

## The problem it answers

Design §2 set the lens: **the noise fix must be forward-only / local** (SCFF has no backward pass). This file asks the two
questions that lens raises — *what does the hardware say the noise actually is?* and *which robustness tools survive the
forward-only filter?* — so the Phase-6 probe attacks the real enemy with allowed weapons.

## What the hardware says the enemy is (so the numpy probe is honest)

- **Channel:** Rasch — **input / tap / ADC-quantization noise dominates, not weight**, and the readout-input layer is
  precision-critical. (Probe that channel primary.)
- **Structure:** the **correlated vs uncorrelated** split ([2409.08633]) names our circuit framing in ML terms.
  *Correlated* noise = all neurons in a layer share a perturbation (temperature, supply voltage, a shared reference) —
  this is the **common-mode** draft-5's differential / auto-zero already subtracts. What's left is **uncorrelated device
  mismatch + the directional residual** — the actual enemy. The literature and our circuit agree on the target.
- **Practice:** the standard analog defense is **noise-aware training** — inject noise on weights/activations at train
  time to match deployment (AIHWKit, Rasch). The refinements matter for us: **BayesFT** makes the injection a
  *theoretically-guaranteed, Bayes-optimized* distribution (not a guessed σ); **Variance-Aware Noisy Training** trains
  *aware of the noise variance* (analog noise is unstable, not stationary). → **inject a principled, variance-matched,
  structured noise, not fixed-σ i.i.d. Gaussian.**
- **Where post-training fixes live:** calibration / rescaling methods ([2401.09859]) are *read-side* — for us they map to
  the **readout (Stage 2)**, and LP-FT already told us they can't manufacture base robustness. They're a Stage-2
  complement, not the Phase-6 answer.

## The forward-only filter on the toolbox

- **✅ Noise injection (input / tap / weight)** — forward-only-native (just perturb the activation/weight in the local
  update). This is Bishop (input channel) + S-SGD (weight channel), and it's the backbone of the plan.
- **✅ Forward-only *flatness* is reachable — this overturns the concept's "SAM is out."** The **zeroth-order SAM
  mechanism** — estimate the sharp direction from **Rademacher perturbations, no backpropagation** — is real and general
  (the ZO-optimization line: **SPSA / ZO-SGD**; **MeZO** [2305.17333](https://arxiv.org/abs/2305.17333) shows ZO scales
  to large models). **ZOSA** (2511.09156) is *evidence the ZO-SAM mechanism works* — but it is an **LLM prompt-tuning
  paper**, so we lift the *mechanism*, not the paper's result: **S-SGD weight-noise is the reliable lever**, and the ZO
  pass is the sharper option behind an entry gate (design P6.2). **SAM selects flatter minima late in training**
  (2410.10373) grounds applying it **periodically / late** — as a **forward-only pass over the SCFF weights**, *not* the
  readout's GD sleep (the SCFF bulk doesn't sleep; readout-flat-sleep / MGSER-SAM is Stage-2). *Correction to the
  concept: what's out is SAM's **two-pass backprop**, not flatness-seeking.*
- **⚠ Jacobian / Lipschitz regularization (explicit)** needs a backward pass → **not** forward-only. Its forward-only
  surrogate is input-noise injection (Bishop), the mechanism in [`noise-as-augmentation.md`](noise-as-augmentation.md). So
  it stays as the *explanation* of why noise injection works, not as a method we run.
- **In-family precedent — we're not inventing from zero.** **Distance-Forward** (2408.14925), a forward-forward variant
  already in our Phase-1–2 reading, was **explicitly hardened to hardware noise** (device-mismatch via Gaussian on the
  update; shot noise via Poisson on the input) at **<40 % the memory of backprop**. A forward-only learner *can* be made
  analog-noise-robust — there is a worked precedent to stand on.
- **Named blind spot (critic pass) — neuromorphic on-chip noise-robust local learning.** The adjacent body we cite
  *none* of: spiking / memristor local-learning that has fought exactly our fight (local, forward-ish, analog device
  noise on-chip — e.g. Local Tandem Learning, the memristor on-chip-training line). Out of the numpy behavioral scope, so
  *not chased* — but named here so the absence is a choice, not an oversight.

## What it means for us

- **The forward-only-filtered toolbox is:** noise-injection (input/tap/weight, principled & structured) **+** zeroth-order
  flatness (a periodic forward-only pass over SCFF weights — *not* the readout's sleep) **+** replay purity (from
  [`all-data-is-noise.md`](all-data-is-noise.md)).
  Jacobian-reg is the *explanation*, run via its noise surrogate; SAM-proper and post-training calibration are out
  (backprop / read-side).
- **Build an honest numpy noise model** mirroring the AIHWKit structure — a **correlated common-mode** term (that
  auto-zero subtracts, to confirm our circuit does its job) **+ uncorrelated mismatch + ADC quantization**, with the
  *directional residual* as the headline attack. Don't beat a weaker i.i.d. enemy than A7 named.
- **Variance-/Bayes-matched injection** is a refinement worth a rung once the basic noise-as-augmentation lever works.
