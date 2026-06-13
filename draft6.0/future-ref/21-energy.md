# 21 — The energy view: the one principle under half this dossier

> This is the **capstone** — not new mechanisms, but the single idea that *unifies* a startling number of the files you've already read, and ties them to the physics of your chip. The principle: **define a scalar "energy" that is low for good configurations and high for bad ones; then inference is rolling downhill, and learning is reshaping the hills.** Once you see it, SCFF, Hopfield memory, equilibrium propagation, predictive coding, the correctness-feeling, attractor cleanup, and analog stability are all *the same thing wearing different clothes.* And at the bottom sits Landauer's principle — the thermodynamic floor that says your settle-don't-erase substrate is physically the cheap path.

---

## The frame: energy = compatibility; inference = descend; learning = reshape

*Energy-Based Learning: LeCun, Chopra, Hadsell, Ranzato & Huang, 2006 ([tutorial](http://yann.lecun.com/exdb/publis/pdf/lecun-06.pdf)).*

LeCun's unifying frame. An **energy function** `E(x, y)` assigns a scalar — a measure of *incompatibility* — to each configuration. Two operations:

- **Inference:** given input `x`, find the `y` that **minimizes** energy — the most compatible answer. (Settle downhill.)
- **Learning:** shape the landscape so that **correct** `(x, y)` pairs sit in **low-energy valleys** and wrong ones sit on **high-energy hills.**

The deep advantage (and why it's the right frame for analog): **no normalization required.** Probabilistic models must compute an intractable normalizing constant (the partition function); energy-based models don't — you only need *relative* energies, *valleys vs hills.* That flexibility is exactly what a physical, non-probabilistic substrate wants — your chip doesn't compute probabilities, it **rolls downhill.**

---

## The unification: everything you've read is energy descent

Watch how many files collapse into this one principle:

- **SCFF "goodness" (`../ref/scff.md`)** — goodness *is* (negative) energy. "High goodness on positives, low on negatives" = "low energy on real data, high on fake." Training SCFF *is* shaping an energy landscape with valleys at coherent inputs. Your whole cheap brain is an energy-based learner.
- **Hopfield associative memory (`1`)** — defined by an explicit energy function; recall = settle to the nearest energy minimum. Modern Hopfield = attention = your LUT. **Memory is energy descent.**
- **Equilibrium Propagation (`3`)** — the network *is* an energy function; it settles to an energy minimum, and the learning rule is the difference between two energy-minimized states. **Learning from energy, locally.**
- **Predictive coding & the free-energy principle (`3`, `4`)** — the brain minimizes "free energy" = prediction-error energy. Perception = settle the energy; the **"I get it" feeling = the energy hitting bottom.** Your correctness-signal *is* an energy reaching its floor.
- **Attractor cleanup / durability (`17`, `20`)** — a Lyapunov function *is* an energy the dynamics dissipate; basins of attraction are energy valleys; noise-cleanup = rolling back down. **Stability is energy descent.**
- **Diffusion / score models (modern generative)** — generate by descending a learned energy/score landscape from noise to data. Same principle, run in reverse.

So **six+ files are one idea.** Inference is "let the physics find the bottom of the valley"; learning is "carve the valleys in the right places." This is the **single mental model** that makes the whole dossier cohere — and it's the one your substrate is *built* to run, because an analog network settling to equilibrium **is** energy minimization in hardware. You are not implementing energy descent on a digital machine; your capacitors *do it physically.*

**For us:** if you keep one unifying picture from all of this, keep **this**: your chip is an **energy-shaping machine.** SCFF, the GD readout, the memory, the thinking loop, the feeling, the noise-cleanup — all of them are "shape a landscape so good things are low, then roll downhill." That single sentence is your architecture's soul in physics terms.

---

## The thermodynamic floor: Landauer, and why brain-like is the cheap path

*Landauer, 1961 ([Landauer's principle](https://en.wikipedia.org/wiki/Landauer's_principle)); reversible computing: Bennett, 1973.*

The other meaning of "energy," and the physics under your whole efficiency thesis. **Landauer's principle:** erasing one bit of information has a *fundamental* minimum energy cost of **`kT·ln2`** (≈ 2.9×10⁻²¹ J at room temperature) — because erasure is **logically irreversible**, and irreversibility dissipates heat. Reversible operations can, in principle, be thermodynamically *free*; only **destroying information** must cost energy. Today's digital chips burn ~a *billion* times the Landauer limit per operation — almost all of it in moving and erasing bits.

**For us — this grounds "copy the brain's function, cheat the implementation" in thermodynamics.** Look at where digital computers waste energy and where yours doesn't:
- **Digital erases constantly** (every register overwrite, every load/store destroys the old value) → pays Landauer over and over. **Your resident weights are never erased or moved** — they *persist* as charge. You sidestep the dominant cost.
- **Digital separates memory and compute** (the von-Neumann shuttle, `12`) → energy in *moving* bits. **Your compute-in-memory does the multiply where the weight lives** — no shuttle, no erasure.
- **Settling is near-reversible** — an analog network relaxing to equilibrium *dissipates* energy gradually (the Lyapunov energy, above), but it isn't doing irreversible bit-erasure at every step; it's flowing downhill in a continuous landscape.

So the claim "brain-like computation is the cheap path in silicon" isn't a slogan — **it's a statement about Landauer's floor.** The brain runs on ~20 W because it computes by *continuous settling and resident memory*, not by erasing and shuttling discrete bits. Your substrate makes the same bet at the same physical level. The two meanings of "energy" meet here: the **energy landscape you descend** (learning/inference) is shaped on a substrate whose **thermodynamic energy cost** (Landauer) is low *precisely because* it descends and persists instead of erasing and moving.

---

## The shape of the answer (this file)

One principle unifies the dossier: **energy.** Define a scalar that's low for good configurations and high for bad; **inference = roll downhill, learning = carve the valleys** (LeCun's energy-based learning — and it needs *no* normalization, which is why it fits a physical, non-probabilistic chip). Through that lens, **SCFF goodness, Hopfield memory, equilibrium propagation, predictive coding, the correctness-feeling, attractor cleanup, and analog stability are all the same thing** — energy descent — and your analog substrate runs it *physically* (settling = minimization in hardware). Beneath the *learning* energy sits the *thermodynamic* one: **Landauer's `kT·ln2`** says the real cost of computing is **erasing and moving bits** — which digital does constantly and your **resident-weight, compute-in-memory, settle-don't-erase** substrate largely avoids. That is the physics under "brain-like is the cheap path." Keep one sentence from all 21 files: **your chip is an energy-shaping machine that computes by descending landscapes it never has to erase.**
