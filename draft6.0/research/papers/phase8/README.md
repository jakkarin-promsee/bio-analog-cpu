# `phase8/` — the economy: *when* do we pay for direction (the gate) + the cost meter

> **Stage-2, the second GD phase.** The readout (Phase 7) is the cheap-most-steps / expensive-when-it-matters bargain;
> **this folder is the trigger** — the unbuilt Ch7 learning-gate that decides *when* the cheap path has stalled and the
> precise GD pass is worth its charge. The good news: it's a **20-year-old solved streaming problem** (concept-drift
> detection). The honest caveat: the *failure modes* (false-fires) are what burn the 80/20, so it's a problem to *tune*,
> not a free answer. This phase also builds the **hardware-meaningful cost meter** Stage 1 explicitly punted here.
>
> Context: feeds [`../../../src/stage2-design.md`](../../../src/stage2-design.md) §3.2 + Phase 8.

---

## The frame

The gate is not ours to invent — it's ours to **choose and tune.** **DDM** (error-rate, two thresholds: warning →
buffer, drift → spend GD → replay-since-warning) *is* our two-threshold gate + sleep. **ADWIN** (two-window mean test)
*is* our fast-EMA-vs-slow-EMA plateau detector — it doesn't *remove* the magic number, it moves it to an interpretable
false-positive rate δ. **Skip-RNN** adds a **budget loss** that writes the 80/20 target directly into the objective. The
exciting bit: fire the gate on the SCFF **features** (a label-free drift detector — ADWIN-U — on the taps), not on the
error, because SCFF drift *leads* the readout's error — schedule a refit *before* accuracy drops. The gate and the
sleep-cadence are the **same detector at two timescales.**

**Don't call it "solved":** drift detectors false-fire on long streams and on *nuisance* drift that doesn't hurt the
readout — and every false fire **burns the 80/20.** So the bake-off has a real failure axis: *which signal detects the
**harmful** stall earliest without false-firing.* And **synthetic gradients / DNI** are the cautionary *don't* — a
*predicted supervised gradient* upstream of SCFF is exactly the §1.1 forward-leak poison.

**The cost meter** is a required deliverable, not a research goal: charge cycles / ADC conversions / write energy,
replacing the op-count proxy — because every "cheaper-than-backprop / 80–20" claim is ultimately a cost claim the proxy
can't settle.

---

## The files

| File | What it covers | The one idea |
| ---- | -------------- | ------------ |
| [the-economy-gate.md](the-economy-gate.md) | Concept-drift detection (DDM, ADWIN, ADWIN-U), plateau / loss-slope detection, Skip-RNN budget loss, synthetic gradients / DNI (the *don't*), the SGR ε-floor. | **"Spend GD only when the cheap path stalls" is a 20-year-old solved streaming problem — but false-fires burn the 80/20.** |

## Papers (the economy slice)

| paper | id / venue | the one-line reason it's here |
| --- | --- | --- |
| DDM (Gama 2004) · ADWIN (Bifet & Gavaldà 2007) | classics | error-rate two-threshold / two-window drift trigger = **the Ch7 gate** |
| Unsupervised drift detection from deep representations · ADWIN-U | [2406.17813](https://arxiv.org/abs/2406.17813) | detect drift in feature space — **label-free** gate trigger (classic DDM/ADWIN need a labeled error) |
| Skip-RNN | [1708.06834](https://arxiv.org/abs/1708.06834) | *learn* when to skip a state/weight update + a **budget loss** (the 80/20 in the objective) |
| Decoupled Neural Interfaces / Synthetic Gradients | [1608.05343](https://arxiv.org/abs/1608.05343) | decoupled local updates — degrades on depth, and a predicted gradient upstream of SCFF is the forward-leak poison (a *don't*) |
