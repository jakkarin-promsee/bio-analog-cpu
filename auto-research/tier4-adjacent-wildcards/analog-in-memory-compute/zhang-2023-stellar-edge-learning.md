# Edge learning using a fully integrated neuro-inspired memristor chip (STELLAR)
- **Authors / Year / Venue:** Wenbin Zhang, Peng Yao, Bin Gao, … Huaqiang Wu (Tsinghua) / 2023 / Science 381:1205–1211
- **Link:** https://www.science.org/doi/10.1126/science.ade3483 (abstract verified via https://pubmed.ncbi.nlm.nih.gov/37708281/)
- **Tier / Topic:** tier4 / t4.1 analog in-memory compute for learning
- **Relevance:** ⭐⭐⭐⭐ — the existence proof: a *fully integrated* memristor chip that learns on-chip — and it gets there by simplifying the learning rule to what analog devices survive, the same move our architecture makes.

## TL;DR
A complete, single-chip demonstration of on-chip learning with memristor crossbars — no external computer in the training loop. The STELLAR architecture makes learning device-tolerant by simplifying what each update asks of the hardware (sign/threshold-style learning with a parallel conductance-tuning scheme), and demonstrates adaptation tasks — motion control, image classification, speech recognition — at low energy cost, positioned for edge devices that must adapt to new scenes/users after deployment.

## The mechanism (how it actually works)
The recurring lesson of every fabricated learning chip: full-precision backprop updates do not survive real analog devices, so *reduce the information content of the update until they do*. STELLAR's ingredients: (1) a learning scheme that leans on **signs and thresholds** rather than precise gradient magnitudes — a device only needs to move in the right *direction* past a threshold, not by an exact amount; (2) a **parallel conductance-tuning** scheme so updates land on many cross-points at once (keeping the update O(1)-ish rather than cell-serial); (3) a 2T2R differential cell arrangement that mitigates IR-drop (line-resistance) distortion across the array. The demonstrated setting is *adaptation*: a deployed model tuned on-chip to a new user/scene — i.e., incremental learning near a good starting point, not from-scratch training.

## Key results / claims
- Fully integrated chip (crossbar + drivers + tuning + control on one die) executing the improved learning ability at low energy cost.
- Three demonstrated on-chip learning tasks: motion control, image classification, speech recognition.
- The STELLAR schemes are presented as general across memristor device types.

## How it relates to us
- **Organ / phase touched:** the whole-chip credibility of "learns on-chip, online, without a backward pass leaving the chip"; the sign-bit substrate primitive.
- **Same as us:** the strategy. Our committed chip also refuses precise gradient magnitudes on the analog substrate — SCFF asks for local contrastive nudges; the direction/sign is carried digitally (SRAM sign bits); the precise fit is closed-form elsewhere. STELLAR is independent, fabricated evidence that *rule-simplified, sign-leaning, adaptation-scoped* on-chip learning is the version of analog learning that actually ships.
- **Different from us:** STELLAR still distills a supervised gradient signal (simplified backprop-style adaptation); our bulk is label-free and our namer avoids gradients entirely. Their plasticity is episodic (adapt to a new scene); ours is continuous (every step, forever) — continuous plasticity re-raises endurance/drift questions their setting can duck.
- **What we could borrow or test:** the 2T2R differential cell + IR-drop discipline is a concrete array-level constraint our math model ignores — array width in our P11 scaling story should be sanity-checked against line-resistance limits. Also: their "adaptation, not from-scratch" scoping is a fair frame for what our namer does at each gated fire.
- **What contradicts or challenges us:** "fully integrated" is the bar. Our numbers live in a behavioral simulator; this paper is what closing the gap costs — years of device-circuit co-design even for a simplified rule. It also quietly confirms that nobody fabricates *continuous every-step* analog learning: the field's demos are episodic adaptation, which flags our always-plastic SCFF bulk as beyond current demonstrated practice (endurance on filamentary devices; our capacitor choice dodges endurance but inherits volatility).

## Follow-on leads
- Yao et al. 2020 (Nature) "Fully hardware-implemented memristor CNN" — the inference-side predecessor from the same group.
- The NeuRRAM chip (Wan et al. 2022, Nature) — multi-task RRAM CIM with on-chip flexibility.
- "A Fully-Integrated Memristor Chip for Edge Learning" (Nano-Micro Letters 2024 highlight) — commentary/context on STELLAR.
- Sign-based / SignSGD-family learning rules as the analog-native gradient dialect — worth a dedicated backlog topic.
