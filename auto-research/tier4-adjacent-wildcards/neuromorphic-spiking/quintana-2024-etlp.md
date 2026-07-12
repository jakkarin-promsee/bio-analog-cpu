# ETLP: Event-based Three-factor Local Plasticity for online learning with neuromorphic hardware
- **Authors / Year / Venue:** Fernando M. Quintana, Fernando Perez-Peña, Pedro L. Galindo, Emre O. Neftci, Elisabetta Chicca, Lyes Khacef / 2023 (arXiv) → 2024 / Neuromorphic Computing and Engineering (IOP), DOI 10.1088/2634-4386/ad6733
- **Link:** https://arxiv.org/abs/2301.08281
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐⭐ — the closest spiking neighbor to *our* philosophy: its third factor is a **projected label with NO error calculation** — i.e. it drops the gradient/error, exactly like our closed-form no-GD namer. This is the bridge between the spiking-online world and our "direction is bought once, cheaply" thesis.

## TL;DR
ETLP is a **local three-factor rule for on-chip learning** whose weight update uses (1) a presynaptic spike trace, (2) postsynaptic membrane voltage, and (3) a **third factor = a fixed random projection of the label — no error, no backprop**. It matches BPTT/e-prop reasonably on event-based visual and auditory tasks at far lower computational complexity, and is demonstrated as an FPGA proof-of-concept for low-energy real-time learning.

## The mechanism (how it actually works)
Most three-factor rules use `error` as the third factor (requires computing a loss gradient and routing it back). ETLP replaces that with a **target-projection** signal: the label is pushed through a *fixed random projection* to each neuron and used directly as the modulator — structurally **Direct Feedback Alignment / Direct Random Target Projection**, spiking-ized. So the update is: pre-trace × post-membrane-voltage × (random-projected label). No backward pass, no error subtraction, no symmetric weights — every factor is locally available at the synapse the instant a label arrives. That is the minimal computational primitive: three local multiplies. The trade is that a random label projection is a *cruder* teaching signal than a real error gradient (accuracy gap on harder tasks), but it is dramatically cheaper and hardware-trivial.

## Key results / claims
- Third factor is **projected labels, no error calculation** — the defining move.
- Compared against BPTT and e-prop on event-based visual + auditory recognition: **competitive accuracy, clear computational-complexity advantage.**
- **FPGA proof-of-concept** hardware implementation → low-energy, real-time on-chip learning.

## How it relates to us
- **Organ / phase touched:** the **namer** (closed-form, no-GD) and the north-star loop's learning signal.
- **Same as us:** ETLP and our namer make the *same bet* — **you don't need a real gradient/error to teach the readout; a cheap fixed projection of the label is enough.** ETLP = random-projection-target three-factor; our RanPAC = random-projection + closed-form ridge. Both refuse to backprop an error. This is the single most philosophically aligned spiking paper in the set.
- **Different from us:** ETLP still updates *per-synapse online* with a plasticity rule and runs on spikes over a time axis; our namer is a *batched closed-form solve* (SLDA/RanPAC), not per-spike plasticity, and our bulk is unsupervised (no label touches it). ETLP labels every neuron; we label only the ~20% namer.
- **What we could borrow or test:** ETLP is a *ready-made temporal analogue of our namer*. If the north-star loop needs an online (per-step) namer instead of a batched closed-form one, ETLP's "random-projected-label third factor" is the drop-in rule that preserves our no-gradient commitment. Concrete rung: replace the closed-form re-fit with an ETLP-style projected-label trace update and see if it holds our BWT/safety.
- **What contradicts or challenges us:** ETLP reports an accuracy gap vs real-error rules on harder tasks — the same "random projection is cheaper but weaker" trade our RanPAC-vs-gradient comparison showed. It's confirmation that the no-error shortcut has a ceiling; we should keep quoting *where* it holds (structured bulk) and where it doesn't.

## Follow-on leads
- Frenkel, Lefebvre & Bol 2021 "Direct Random Target Projection (DRTP)" — the non-spiking parent of ETLP's third factor; near-identical to our RanPAC intuition.
- Neftci et al. 2017 "Event-driven random backpropagation" — the earlier spiking feedback-alignment line.
- Chicca & Indiveri group — mixed-signal neuromorphic substrates that would host a rule like this (nearest hardware neighbor to our analog substrate).
