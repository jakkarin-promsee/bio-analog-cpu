# Bio-Inspired Analog Neural Compute Architecture

> A continuous-time analog substrate with on-chip, online learning.
> Architecture spec + behavioral-simulation plan.

**Status:** Rebuilt at **draft 6.0** (June 2026) after the previous learning rule collapsed. The substrate vision is intact; the learning rule was rebuilt from zero as a **SCFF + gradient-descent hybrid.** The design spine is committed; **Phase 1** (the behavioral-simulation ladder) is specified but has **not run yet** — numbers pending.

> [!NOTE]
> Solo independent research project, evenings/weekends. The live plan lives in [`draft6.0/`](draft6.0/). Drafts 1 → 5.1 (the *attribution era*) are kept as reference for how the project worked before the pivot — see [Project history](#project-history--the-attribution-era-draft-1--51) below.

---

## What this is

An attempt to design a compute substrate where the kind of computation brains do is the **cheap path**, instead of an emulation layered on von Neumann silicon or a programmed-once inference array.

Concretely: capacitors hold weights as continuous analog charge; SRAM holds wiring and sign bits; hardwired op-amps do add / multiply / ReLU directly on the charges; the chip **learns on-chip, online, with the weights never leaving it.** The broader field is **compute-in-memory (CIM)**.

The four committed substrate properties (these survived every pivot, unchanged):

| Property            | Meaning                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| **Online**          | Weights update during operation, not in batch-offline epochs                                             |
| **Sparse**          | Only paths that carry signal consume energy                                                              |
| **Continuous**      | Weights and signals live in capacitor voltages, not bit patterns                                         |
| **Resident-weight** | Weights never leave the substrate during operation — only inputs/labels enter, only predictions leave    |

The guiding method, in the author's words: **copy the brain's *function*, cheat the *implementation*.** You can't copy 3D-moving synapses, growing axons, or multi-hormone wires — so you reproduce what the brain *does* and pay for each principle with whatever is cheap on this substrate (analog physics where physics is cheaper, modern DL math where math is cheaper). Modern ML doesn't brute-force biology; it projects it into a dimension we can compute. That projection is the only honest road to it.

## What this isn't

- Not an attempt to build intelligence. "Intelligence" is too fuzzy to optimize against.
- Not a 1:1 copy of biology. Biology is the source of architectural patterns, not a reproduction target.
- Not another digital ML accelerator.
- Not another inference-only analog array. The central commitment is **on-chip learning**, not just programmed weights.

## Draft 6.0 in one breath

**Two brains.** A cheap, unsupervised **SCFF** front (~80% of the network — Self-Contrastive Forward-Forward: label-free, forward-only, local) that organizes the world for free, and a small, precise **gradient-descent** back (~20%) that maps those features onto real labels.

The organizing principle: **direction is the one expensive thing in learning.** Magnitude is cheap — the substrate measures `|a·W|` for free. Direction is what costs a backward pass, a transpose, a chain of dependencies. So draft 6.0 **pays for direction once, in one place (GD), and keeps everything else cheap (SCFF).**

The pieces:

- **Residual boosting blocks** — the two brains chain as blocks, each a weak corrector on a residual stream (BoostResNet), SCFF doing feature work inside, a GD checkpoint at each exit.
- **Threshold-gated learning** — cheap local SCFF most steps; expensive GD only when the cheap path stalls.
- **Sleep + memory** — periodic full-batch GD over a **hippocampus LUT** (deduplicated raw-input prototypes) re-covers the whole data range so nothing rots.
- **Mono-forward** (the substrate move) — one forward sweep carries a positive and a negative world side by side through the **shared** weight crossbar; only the cheap activation buffers double, not the weight capacitors.

The full story is in [`draft6.0/idea/ideas1.md`](draft6.0/idea/ideas1.md); the committed decisions in [`draft6.0/idea/main.ideas.v1.md`](draft6.0/idea/main.ideas.v1.md); the pivot story in [`draft6.0/README.md`](draft6.0/README.md).

## The substrate

The atom of storage is the **Scap** (SRAM + Capacitor) — the only original name that survived from draft 1: magnitude as analog charge on a capacitor, sign as a digital SRAM bit. **A Scap is a wire, not a neuron.** Compute happens in the wires: a **crossbar** of Scaps does the multiply-accumulate as physical current, and hardwired op-amps do add / multiply / ReLU directly on the charges. There is no ALU shuffling data — computation is where the weights physically are.

Under-refilling the weight capacitor below its natural decay gives **free L2-style weight decay in physics** (no `λ‖W‖²` term anywhere). The same physical realism that brings noise becomes free regularization when trained against.

## Phase 1 — the build plan

Phase 1 is the behavioral simulation: classification / statistics tasks, **ideal operators first** (analog/PVT realism added only after the ideal converges), one variable changed per run, multi-seed (`[42, 137, 271, 314, 1729]`), median + IQR.

The discipline: **walk one spine — the neocortex (SCFF + GD)** — straight down the ladder. The **hippocampus LUT is a service, not a parallel brain**: it feeds SCFF its negatives (stubbed early) and holds replay history for sleep (where it becomes a real organ). You test **convergence, not theory.**

The experiment ladder (full detail in [`draft6.0/idea/ideas1.md`](draft6.0/idea/ideas1.md)):

1. **1.x — the atoms.** 1.0 full SCFF (mono-forward, mandatory inter-layer norm); 1.1 full GD (the precision ceiling).
2. **2.x — putting them together.** SCFF + GD via taps; then the plasticity-gradient middle layer.
3. **3.x — staying alive (sleep).** No-sleep (watch it rot) → full-batch history → prototype-LUT history → learned memory.
4. **4.x — scaling out.** Chain blocks, gated on a stable single block.

## How this differs from existing CIM / neuromorphic work

| Project                        | Substrate                         | On-chip learning    | Learning mechanism                                                  |
| ------------------------------ | --------------------------------- | ------------------- | ------------------------------------------------------------------- |
| **Mythic AI**                  | Analog flash transistors          | No (inference only) | —                                                                   |
| **Intel Loihi**                | Digital neuromorphic, spike-based | Yes (STDP-flavored) | Local-Hebbian                                                       |
| **IBM analog AI / NorthPole**  | Analog matrix-vector              | Some research       | Gradient-descent variants (weight transport)                        |
| **BrainChip Akida, SpiNNaker** | Mostly spike-based                | Varies              | Spike-timing rules                                                  |
| **This project**               | Continuous analog currents        | Yes (online, local) | **SCFF + gradient-descent hybrid** (cheap local front, precise back) |

The distinguishing claim is the *combination*: continuous analog compute + on-chip online learning + a label-free local front that pays for direction only where it must.

## Project structure

```
.
├── README.md                  # This file (public overview)
├── CLAUDE.md                  # Always-loaded project context for AI collaboration
├── draft6.0/                  # ★ THE LIVE PLAN (draft 6.0 — SCFF + GD)
│   ├── README.md              #   the pivot story (why 5.x died, what 6.0 is)
│   ├── context.md             #   full context dump — the whole picture (cold-start here)
│   ├── idea/
│   │   ├── main.ideas.v1.md   #   the decision record (N1–N3 + S1–S8)
│   │   └── ideas1.md          #   the full derivation + the Phase-1 build plan
│   ├── concept/               #   learning-rule survey (the options considered)
│   ├── ref/                   #   paper stories behind 6.0 (SCFF, Distance-Forward, BoostResNet, BYOL, LLRD)
│   └── future-ref/            #   north-star research dossier (21 files, beyond the numbered phases) — compass, not the live line
├── docs/
│   ├── essence/the-essence.md # the project's soul (origin → collapse → return)
│   └── draft/                 # collaboration handoff + the draft 1→5.1 history
├── skill/                     # task skill-maps for AI collaboration
├── report/                    # spec → A4 Word toolchain
│
│   # ── HISTORICAL (the attribution era — kept as reference) ──
├── draft5.1-1.md / draft5.1-2.md   # the old canonical spec (attribution architecture)
├── draft/                     # historical drafts 1.0 → 5.1
└── src/                       # the old behavioral simulator (built for attribution)
```

**Reading order if you've just arrived:** this README → [`draft6.0/README.md`](draft6.0/README.md) (the pivot) → [`draft6.0/idea/main.ideas.v1.md`](draft6.0/idea/main.ideas.v1.md) (the decisions) → [`docs/essence/the-essence.md`](docs/essence/the-essence.md) (the why). For the whole picture in one file: [`draft6.0/context.md`](draft6.0/context.md).

## Project history — the attribution era (draft 1 → 5.1)

The project began as a different learning rule. From draft 1 to draft 5.1 (~the first year), the architecture was a five-level hierarchy (Scap → Ganglion → Column → Lobe → Limbic Loop, plus a Brainstem controller) learning by **attribution-based hierarchical diffusion** — loss broadcast from the top and split at each level in proportion to locally-measured `|a·W|` contribution, with no per-weight gradient routing.

In June 2026 that rule collapsed on a single flaw: the diffusion carried loss **magnitude** but never **direction** (the sign). Magnitude without direction cannot descend anything, and routing the sign back would have broken the locality the whole chip stands on. The architecture was rebuilt around SCFF + GD — **the substrate survived; only the learning rule was reborn.**

That era is kept intact as reference — *how the project worked before the pivot*:

- [`draft5.1-1.md`](draft5.1-1.md) / [`draft5.1-2.md`](draft5.1-2.md) — the old canonical spec.
- [`docs/draft/project-history.md`](docs/draft/project-history.md) — the narrative arc, why each pivot happened.
- [`docs/draft/draft.heirachy.md`](docs/draft/draft.heirachy.md) — the file-by-file map of every draft.
- [`src/`](src/) — the behavioral simulator built for the attribution chip.

What carried forward in *spirit*: residual connections (now confirmed by boosting theory), the two-timescale Cortex/Hippocampus (now sleep + the LUT), and resident-weight / sign-as-digital / the Scap (substrate-level, unchanged).

## Methodology note

Built from intuition first; literature comparison reserved for after the design stabilizes. *"The fast answer will destroy your creativity."* The risk is reinventing wheels; the benefit is reaching design decisions the literature wouldn't have suggested — and in practice the project keeps re-deriving published results from the circuit side before learning their names. The papers behind each draft-6.0 decision are told as stories in [`draft6.0/ref/`](draft6.0/ref/).

## Honest framing

This project does **not** claim to: build intelligence; invent SCFF (it's reformulated for the substrate); inherit gradient descent's convergence guarantees; or replicate biological brain function with high fidelity.

This project **does** claim to: be a coherent design for a continuous analog substrate with on-chip *online* learning; pay for direction once (in GD) and keep the rest cheap (SCFF); be physically realizable with standard analog IC techniques; and have a concrete, falsifiable Phase-1 ladder. **Convergence is empirical** — nothing in draft 6.0 has been simulated yet. The spine is committed; the numbers are what the experiments exist to find.

## Background

The author is a Year-2 undergraduate. A prior project — **ChronoForge** — was a pure-hardware 2D game engine on a Xilinx Basys3 FPGA: 640×480 at 60 Hz, no CPU, no OS, ~18k LUTs, three independent hardware timelines in parallel. That hardware-design experience informs the substrate-level thinking here.

## Contributing

Not yet — solo, at the design + pre-simulation stage. If the architecture interests you, opening an issue to discuss is welcome; please read [`draft6.0/README.md`](draft6.0/README.md) first so we can talk specifics.

## License

To be determined. Until a LICENSE file appears, content is © the author, all rights reserved.

## Acknowledgments

Developed iteratively with AI assistance for critique, structural review, and naming. Literature anchors are cross-validation references — the architecture was designed before the work was surveyed. Any errors of attribution or framing are the author's.

---

_Rebuilt at draft 6.0 (SCFF + GD). The attribution-era spec (draft 5.1) is kept as historical reference. Phase 1 — the behavioral-simulation ladder — is specified; the numbers are next._
