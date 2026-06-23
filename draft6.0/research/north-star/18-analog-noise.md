# 18 — Analog noise, and the temperature problem you couldn't crack

> `17-durability.md` gave the theory; this is the circuit reality — what noise actually hits a capacitor-weight chip, and specifically your **temperature / fast-swing** worry. The single conceptual key you're missing: **match the technique to the noise's *timescale*. Slow noise you SUBTRACT (against a reference); fast noise you AVERAGE (over time or copies).** Once you know a noise's frequency, the technique is almost forced. And the good news: **you already designed most of this in draft-5 (§15) — you just didn't know the theory behind why it works.**

---

## First: name your enemies (the analog noise taxonomy)

A capacitor-weight, crossbar-compute chip faces a specific menu — know which is which, because the *fix depends on the timescale*:

| Noise | Timescale | Source | Killed by |
| --- | --- | --- | --- |
| **kT/C thermal** | **fast** (broadband) | thermal agitation on every cap | bigger caps; averaging |
| **Shot noise** | fast | discrete charge carriers | averaging; bigger signals |
| **1/f (flicker)** | **slow** | device traps | chopper / auto-zero |
| **Offset / mismatch** | **static→slow** | device-to-device variation | differential; auto-zero; calibration |
| **Temperature drift** | **slow** | T changes conductance/threshold | differential; chopper; reference cell |
| **Supply / coupling** | fast→slow | `V` noise, crosstalk | differential (common-mode reject) |
| **Conductance drift** | slow | the stored weight ages | refresh; noise-aware training |

The split that organizes everything: **slow stuff (temperature, 1/f, offset, drift) vs fast stuff (kT/C, shot, coupling).** Two different toolkits.

---

## Your temperature worry: it's SLOW noise — so you *subtract* it

Here's the reframe that cracks your "no idea" problem. **Temperature drift is *slow*** — a chip's temperature changes over milliseconds-to-seconds, not nanoseconds (thermal mass is large). Slow noise has a superpower: **it affects everything almost equally at any instant**, so you can **measure it on a reference and subtract it off**. That's the whole game for drift. Four ways, all of which you can build:

### 1. Differential / common-mode rejection — the big one
Represent every value as a **difference of two lines** (`+` and `−`) instead of one. Temperature (and supply noise, and any drift that hits both lines equally) is **common-mode** — it adds the *same* amount to both, so it **cancels in the difference.** This is *the* classic analog answer to temperature, and your **draft-5 §15 "Differential Pair op-amps" already does exactly this.** Differential signaling is why precision analog survives in a hot, noisy world. Make it pervasive: differential weights, differential activations.

### 2. Chopper stabilization & auto-zeroing — cancel slow drift in time
*Enz & Temes, 1996 (the classic review).* **Chopper:** modulate your signal up to a high frequency *before* it picks up the slow drift/1/f, amplify, then demodulate back down — the drift, which was never modulated, gets filtered away. Result: **1/f noise eliminated, temperature drift greatly reduced.** **Auto-zero:** periodically measure the amplifier's own offset/drift (input grounded) and subtract it on the next cycle — nanovolt offsets, near-zero drift. **Your draft-5 §15 "Auto-Zeroing" is this.** (Chopper for low-frequency/low-power, auto-zero for wideband; combine for both.)

### 3. Dummy / reference cell — subtract a twin that drifts the same way
Keep a **dummy Scap** that sees a *known* input and sits in the *same thermal environment*; its output tells you "this is what drift looks like right now," and you subtract it from the real readings. Because it drifts *with* temperature identically, the subtraction removes the drift. **Your draft-5 §15 "Dummy Scap" is exactly this**, and the **"Current Mirror"** (§22 #13) preserves ratios under drift the same way.

> **So your temperature problem is already three-quarters solved in your own draft-5.** Differential + auto-zero + dummy-reference is *the* standard arsenal against slow drift, and you independently specced all three. The theory above is just *why* they work: slow noise is common-mode and subtractable.

---

## The fast noise (kT/C): you *average* it — and your weights are caps, so this is direct

The noise you *can't* subtract (it's random and different every instant) you **average** instead — and the most fundamental one is **kT/C noise**, which matters to you specifically because **your weights are stored on capacitors.**

*kT/C noise:* the thermal noise voltage on a sampled capacitor is **`√(kT/C)`** — set by temperature `T` and capacitance `C`. The lever is blunt and powerful: **every 10× increase in `C` cuts the noise by ~10 dB.** Capacitance *is* your noise knob.

**For us — the core analog tradeoff, made concrete:**
- **Bigger weight caps = quieter weights** (`√(kT/C)`), but bigger area and slower charging (your `12-dataflow.md` area cost, your charge-time cost). So **cap sizing is a direct noise-vs-area-vs-speed dial** — precision-critical weights get big caps, others stay small.
- **Average over time** — integrate longer / low-pass-filter the output. Fast random noise averages toward zero; the more settling time, the less noise (at the cost of speed). Your settle-to-equilibrium (`3`, `17`) *is* this averaging.
- **Average over copies** — `N` redundant noisy Scaps, averaged, cut noise by **`√N`** (population coding / von Neumann multiplexing, `17`). Redundancy buys precision you can't get per-device.

So fast noise has three knobs — **bigger caps, longer integration, more copies** — and they trade against area, speed, and count respectively. Pick per-weight by how much that weight's precision matters (most don't — see compression, `13`).

---

## The software side: noise-aware training (and it's your "fix in software" idea)

*Variation-aware / noise-aware training for analog in-memory computing (memristor/crossbar literature).*

The most important *modern* tool, and it ties straight to Bishop (`17`). Instead of fighting every non-ideality in silicon, **train the model with the hardware's noise model injected** — add the real device variation, drift, and kT/C noise to weights/activations *during training*. The network **learns weights that are robust to exactly the noise it will face.** The numbers are encouraging: injecting **<15% noise during training yields models that hold ~97% accuracy despite real device variation.**

**For us — this is the cleanest expression of "fix it in software, keep the hardware clean and fast."** You don't need to make the analog perfect (perfect analog is impossible and expensive); you make it **fast and rough**, then **train against its measured noise** so the *weights absorb the imperfection.* Bishop (`17`) proves this is also free regularization. So the division of labor is: **circuit techniques kill the *slow* drift (differential/auto-zero/dummy — cheap, your draft-5 has them), cap-sizing + averaging tame the *fast* kT/C where it matters, and noise-aware training mops up the rest in the weights.** Three layers, and the hardware gets to stay simple.

---

## The shape of the answer (this file)

The conceptual key you were missing: **classify the noise by timescale, then the fix is forced.** **Slow noise (temperature, 1/f, offset, drift) you SUBTRACT** against a reference — *differential / common-mode rejection* (temperature is common-mode → cancels in a difference), *chopper / auto-zero* (modulate past the drift, or measure-and-subtract it), *dummy/reference cell* (a twin that drifts identically). **Your temperature problem is this, and your draft-5 §15 already specced all three mechanisms** — you'd designed the solution before you knew the theory. **Fast noise (kT/C thermal — and your weights are caps, so this is your noise floor) you AVERAGE** — *bigger caps* (`√(kT/C)`, the direct dial vs area/speed), *longer integration* (your settling does this), *redundant copies* (`√N`, von Neumann multiplexing). And the modern glue is **noise-aware training**: train with the device noise injected so the weights are born robust — your "fix in software, keep hardware fast and clean," vindicated and made precise. Durability ends up at three levels — **circuit (subtract slow / average fast), architecture (residual variance-control + redundancy + attractor restoring, `17`), and training (noise-aware = free Tikhonov)** — and you already hold the circuit layer.
