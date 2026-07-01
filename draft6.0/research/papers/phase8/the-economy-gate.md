# The economy — when to pay for direction (the gate)

*Concept-drift detection: DDM (Gama et al. 2004), ADWIN (Bifet & Gavaldà 2007), and unsupervised drift from deep
representations ([2406.17813](https://arxiv.org/abs/2406.17813)). Learned skipping: Skip-RNN
([1708.06834](https://arxiv.org/abs/1708.06834)). Decoupled updates: Synthetic Gradients / DNI
([1608.05343](https://arxiv.org/abs/1608.05343)). Plus our own survey's SGR ε-floor (`survey/SGR.detail.md`).*

---

## The problem it answers

The **Ch7 threshold learning-gate** is the biggest *unbuilt* piece of the architecture: run cheap local SCFF most of
the time, and spend an expensive GD update **only when the cheap path stalls** (`L < θ` → SCFF only; `L ≥ θ` → SCFF + GD).
We even pre-registered the refinement: gate on the **loss-slope / a plateau**, not the absolute loss (a fast loss-EMA
vs a slow one — two capacitors). The open question: *is "when to spend a gradient" a thing we have to invent, or is it
already solved somewhere we weren't looking?* It's solved.

## The one idea that unstuck it

**The data-stream / concept-drift community has been answering "when has the cheap model gone stale, retrain now" for
twenty years — and their detectors *are* our gate.** Two canonical ones, and they map onto our two gate variants
exactly:

- **DDM (Drift Detection Method)** monitors the online **error rate** and its standard deviation and defines **two
  thresholds — a *warning* level and a *drift* level.** Below warning: keep the cheap model. Past warning: start
  buffering. Past drift: **retrain on the buffered-since-warning data.** That is, line for line, our **two-threshold
  gate plus the sleep replay** — the warning level is "start paying attention," the drift level is "spend the
  expensive update," and "retrain on the buffer since warning" is the LUT replay. We described the gate from circuit
  intuition; DDM is the same object with 20 years of analysis behind it.
- **ADWIN (Adaptive Windowing)** keeps a window of recent signal, splits it into an older and a newer sub-window, and
  flags drift when their **means differ significantly** — then drops the stale half. That is **exactly** the
  fast-EMA-vs-slow-EMA plateau detector we sketched, made rigorous (a statistical test instead of a hand-tuned θ). One
  honest correction: it doesn't *remove* the magic number, it **moves** it — to the confidence parameter δ that sets the
  test's sensitivity. The win is that δ is *interpretable* (a false-positive rate), not that it's gone.

Two more pieces fill the corners:
- **Unsupervised drift detection from representations** ([2406.17813](https://arxiv.org/abs/2406.17813)) runs the
  detector on the *feature distribution*, not the error — a **label-free** trigger. Important for us because SCFF drift
  is *unsupervised*; we can fire the gate on the SCFF features moving, before the readout's error even reacts.
- **Skip-RNN** ([1708.06834](https://arxiv.org/abs/1708.06834)) shows you can **learn** a binary "update or skip"
  decision *and* add a **budget loss** (a cost per update, mathematically like weight decay) that tunes how often the
  model pays. That is a learned, differentiable version of the gate with the **80/20 cost target written directly into
  the objective** — a clean way to make "spend ~20% of the time" an outcome instead of a hand-set θ.

And one **cautionary** entry, so we don't chase it: **Synthetic Gradients / Decoupled Neural Interfaces** answer a
*different* "when" — they let a layer update *without waiting* for the backward pass by **predicting** the gradient a
small aux-net thinks is coming. Tempting for decoupling, but the literature is clear it **degrades / diverges on deeper
nets**, and (the deeper reason) a *predicted supervised gradient injected upstream of SCFF is exactly the fast-supervised
poison* the kickoff frame forbids. So DNI is filed as a **don't** — read it to know why we *won't* synthesize gradients
into the stream.

## What it means for us

- **The gate is not ours to invent — it's ours to *choose and tune*.** DDM (two-threshold, error-based) and ADWIN
  (two-window, self-tuning) are the two concrete designs for the Ch7 gate, and Skip-RNN is the "learn the gate with a
  budget loss" upgrade. Phase-6 work is a clean bake-off: **absolute-θ vs DDM-style two-threshold vs ADWIN-style
  two-window vs a learned budget-gate**, scored on (accuracy held) × (fraction of steps that paid for GD) — the 80/20,
  metered.
- **Fire on the features, not just the error — but classic DDM/ADWIN assume a *labeled* error signal.** Because SCFF
  drift is unsupervised and *leads* the readout's error, the best trigger may be a **label-free drift detector on the
  SCFF taps** ([2406.17813]); for that, the **unsupervised ADWIN variant (ADWIN-U)** is the right tool — vanilla
  DDM/ADWIN watch an *error rate* (needs labels). The gate sees the base move and schedules a refit *before* accuracy
  drops. This makes the gate and the sleep-cadence ([`maintenance-and-replay.md`](maintenance-and-replay.md)) **the same
  detector at two timescales** (per-step gate vs periodic sleep).
- **The ε-floor is the *why*, drift-detection is the *how*.** Our justification for gating (the SGR gradient-mismatch
  ε-floor: local learning converges while block-disagreement is small, stalls when it dominates) says *a stall is real
  and worth detecting*; the drift literature says *here is the detector*. Two halves of one gate.
- **Caveat — "solved" overstates it; the failure modes are exactly the ones that burn the 80/20.** Drift detectors are
  *off-the-shelf designs*, not a free answer. Documented failure modes we will hit: **false positives on long streams**
  (every spurious fire spends a GD update we didn't need), a **sensitivity δ that still must be tuned**, and **slow
  detection of *gradual* drift** (which is exactly SCFF's slow representation creep). And firing on the *features* risks
  catching **nuisance / virtual drift that doesn't actually hurt the readout** — burning the budget for nothing. So the
  gate experiment isn't "pick DDM and done"; it is *which signal (loss-EMA vs tap-distribution, both physically present
  as capacitor EMAs) detects the **harmful** stall earliest without false-firing.* That's a real bake-off with a real
  failure axis, not a solved problem we're importing.
