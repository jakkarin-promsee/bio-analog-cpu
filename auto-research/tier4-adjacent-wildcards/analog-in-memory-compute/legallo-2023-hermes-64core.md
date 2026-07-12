# A 64-core mixed-signal in-memory compute chip based on phase-change memory for deep neural network inference (IBM HERMES)
- **Authors / Year / Venue:** Manuel Le Gallo, Riduan Khaddam-Aljameh, Milos Stanisavljevic, … Abu Sebastian (IBM) / 2023 / Nature Electronics 6:680–693
- **Link:** https://www.nature.com/articles/s41928-023-01010-1
- **Tier / Topic:** tier4 / t4.1 analog in-memory compute for learning
- **Relevance:** ⭐⭐⭐⭐ — the hardest silicon evidence for our crossbar-MVM floor: a fully integrated 64-core analog chip with measured TOPS/W — and the honest scale of the ADC/precision tax at chip level.

## TL;DR
The IBM HERMES chip: 64 analog PCM crossbar cores + on-chip network, 14 nm CMOS with backend-integrated PCM, all weight-layer computation and activation functions on-chip. Near-software-equivalent inference on ResNet and LSTM. Measured: 16.1 TOPS at 2.48 TOPS/W (high-precision 4-phase readout) or 63.1 TOPS at 9.76 TOPS/W (low-precision 1-phase) for 8-bit-I/O MVMs. Weights resident in an 8T4R unit cell (eight transistors, four PCM devices).

## The mechanism (how it actually works)
Each core is a crossbar of PCM unit cells holding weights as conductances; input activations become pulse-modulated voltages; column currents integrate the MVM in one analog step; on-chip ADCs digitize the result; digital nearest-neighbor links carry activations between cores so the whole network stays resident. Two operating modes expose the analog precision economy directly: spending 4 readout phases buys precision (2.48 TOPS/W); accepting 1 phase quadruples throughput and ~4×es efficiency (9.76 TOPS/W) at accuracy cost — the ADC/readout is *the* metered bottleneck, the MACs themselves are nearly free. The unit cell is 8T4R: four PCM devices per weight (differential pairs + significance), a redundancy that buys signed weights, drift averaging, and conductance headroom — the real price of "one weight = one device" idealizations.

## Key results / claims
- Fully integrated 64-core AIMC chip, 14 nm CMOS + backend PCM.
- Near-software-equivalent accuracy on ResNet-class CNNs and LSTMs with all weight-layer compute on-chip.
- 8-bit MVM: 16.1 TOPS @ 2.48 TOPS/W (high-precision mode) / 63.1 TOPS @ 9.76 TOPS/W (low-precision mode).
- Inference-only: weights are programmed once (write-verify), then read; training happens off-chip.

## How it relates to us
- **Organ / phase touched:** P8.7's substrate meter (crossbar MAC ~free, ADC taxed) — the claims this chip grounds; P11's substrate-factor scaling.
- **Same as us:** resident-weight compute-in-memory at real chip scale, with the same internal economy our behavioral meter assumes: the MVM is cheap, the read-out/conversion is where energy goes. Our "ADC-centred meter" is the right shape — this is the fabricated version of the NeuroSim/ISAAC-level model we cite.
- **Different from us:** inference-only — the chip's weights are programmed with careful write-verify then left alone. The entire on-array *update* problem (our topic's hard part) is deliberately out of scope for this flagship. Also 8T4R: four devices + eight transistors per weight, vs our one-Scap-per-weight picture.
- **What we could borrow or test:** the two readout modes are a ready-made knob for our meter's sensitivity analysis — our ADC-bits sweep (P8.4) mirrors their 4-phase/1-phase trade, and their measured 2.48–9.76 TOPS/W brackets give real-silicon anchor points for the meter's absolute scale.
- **What contradicts or challenges us:** the overhead multiplier. Where our math model counts one capacitor per weight, the shipped analog chip spends 8 transistors + 4 devices per weight plus per-core ADCs — the substrate factor survives (the chip still wins on efficiency), but area/complexity per weight is ~an order above the naive picture, and drift management (PCM conductance decays in time) needs compensation machinery even for *frozen* weights. Any analog LUT we build inherits that drift tax on stored prototypes.

## Follow-on leads
- Ambrogio et al. 2023 (Nature) "An analog-AI chip for energy-efficient speech recognition and transcription" — the 34-tile sibling, larger networks.
- "The design of analogue in-memory computing tiles" (Nature Electronics 2025) — the tile-engineering follow-on.
- PCM conductance-drift compensation literature — directly relevant to analog prototype/LUT storage.
- Comparing 8T4R-style significance/differential weight encodings against our sign-bit + magnitude Scap scheme.
