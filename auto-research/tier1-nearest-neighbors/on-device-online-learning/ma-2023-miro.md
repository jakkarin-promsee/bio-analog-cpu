# Cost-effective On-device Continual Learning over Memory Hierarchy with Miro
- **Authors / Year / Venue:** Xinyue Ma, Suyeon Jeong, Minjia Zhang, Di Wang, Jonghyun Choi, Myeongjae Jeon / 2023 / ACM MobiCom 2023
- **Link:** https://arxiv.org/abs/2308.06053 (DOI: 10.1145/3570361.3613297; code: github.com/omnia-unist/Miro)
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐ — the only paper in this set whose objective function is literally ours: accuracy per joule for on-device CL — and its answer is a runtime that *re-tunes the knobs online*.

## TL;DR
A system runtime for replay-based CL on energy-sensitive edge devices. Old samples live across a **memory hierarchy** (fast/expensive on-device RAM vs slow/cheap secondary storage); Miro profiles the accuracy-energy trade-off of the CL configuration **online** and dynamically re-configures (buffer placement/size, training amount) for best cost-effectiveness. 7–66% less energy at 1.35–15.37% higher accuracy vs baseline systems across memory budgets.

## The mechanism (how it actually works)
The insight: a CL system has knobs — episodic-memory size and placement (RAM vs flash/cloud tiers), how much to replay, how much to train per task — and each knob has a *measurable* accuracy-per-joule slope that shifts with resource state and workload. Miro first maps this design space offline (which knobs have clean trade-offs), then at runtime does cheap online profiling on exactly those knobs and moves the configuration to the current optimum. The learner itself is ordinary replay+backprop; all the intelligence is in the *meta-controller* that decides what the learner may spend. Hierarchical memory means the buffer is no longer a single budget number but a placement problem: hot samples near, cold samples far.

## Key results / claims
- **7–66% energy reduction with 1.35–15.37% accuracy gain** over baseline hierarchical-replay systems, across various memory budgets (Jetson-class edge hardware).
- First systematic design-space exploration of hierarchical-memory replay CL for cost-effectiveness.
- Online profiling overhead is low enough to pay for itself.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P8/P9 economy knobs (cadence, LUT history, gate thresholds) + the P8.4 meter; the LUT as a memory system.
- **Same as us:** the target metric is identical — accuracy per unit energy for a learner that must keep learning on-device — and it treats the *memory of the past* as the central budget object, as our LUT is.
- **Different from us:** their learner is backprop+replay (the thing we removed); energy is measured at the device level (no substrate decomposition); no drift gate — training is task-arrival-driven; and crucially their knobs are **adaptive at runtime** while ours were tuned once and frozen (grid-4, full history, DDM thresholds — locked in P9).
- **What we could borrow or test:** the Miro move applied to us: our committed cadence is *drift-rate-conditional* (P8 honest scope says re-tune if drift slows) — a tiny meta-controller that profiles error-EMA drift rate online and adapts sleep cadence between grid-4/8/16 would make that conditionality self-managing instead of a footnote. Also the memory-hierarchy idea maps to the LUT: hot prototypes resident (analog/SRAM), cold class history in cheap dense storage, paged in at sleep.
- **What contradicts or challenges us:** their gains show static configurations leave 7–66% energy on the table — our frozen knob set is plausibly leaving similar margin; "committed and frozen" is a scientific virtue but an engineering cost.

## Follow-on leads
- Chameleon (DATE 2023 / TCAD 2024) — dual replay buffers split across on-chip/off-chip memory.
- Ekya / RECL (NSDI 2022/2023) — the same meta-controller idea at the edge-server scale (Ekya carded here).
- DaCapo (arXiv:2403.14353) — continuous-learning accelerator with spatial resource allocation between training/inference/labeling.
