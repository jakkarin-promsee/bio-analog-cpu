# Bio-Inspired Analog Neural Compute Architecture

> A continuous-time analog substrate with on-chip hierarchical credit assignment.
> Specification and experimental campaign.

**Status:** Theory locked at draft 5.1. Simulation phase about to begin.

> [!NOTE]
> This is a solo independent research project at the architecture-specification stage. No experimental data exists yet. The repository will grow as the simulation campaign progresses.

---

## What this is

An attempt to design a compute substrate where the kind of computation brains do is the _cheap_ path, instead of an emulation layered on top of von Neumann silicon or a programmed-once inference array.

Concretely: capacitors hold weights as analog charge. SRAM is repurposed from branch prediction into wiring, sign bits, contribution accumulation, and routing. Hardwired op-amps perform add / multiply / ReLU directly on capacitor charges. Learning diffuses through a hierarchy of modules using locally-measured contribution, not per-weight gradient routing.

The four properties this architecture targets:

| Property            | Meaning                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| **Online**          | Weights update during operation, not in batch-offline epochs                                             |
| **Sparse**          | Only paths that carry signal consume energy                                                              |
| **Continuous**      | Weights and signals live in capacitor voltages, not bit patterns                                         |
| **Resident-weight** | Weights never leave the substrate during operation — boot and shutdown are the only serialization events |

The broader field is **compute-in-memory (CIM)**.

## What this isn't

- Not an attempt to build intelligence. "Intelligence" is too fuzzy to optimize against.
- Not a 1:1 copy of biology. Biology is the source of architectural patterns, not a reproduction target.
- Not another digital ML accelerator. Digital neural networks are a metaphor mistaken for the thing.
- Not another inference-only analog array. The architecture's central commitment is **on-chip learning**, not just programmed weights.
- Not approximate backprop. The learning rule is attribution-based, in the three-factor / LRP family (see below).

## The central bet

Every level of the architecture stores **distribution memory** — how much each of its children contributed to its output on the most recent forward pass. When loss arrives from above, the level divides it among its children in proportion to their stored contributions, broadcasts the shares on its local bus, and each child does the same recursively until the share reaches the leaf storage cells.

```
Brainstem computes total loss L
    ↓ broadcasts on global bus
Limbic Loop reads L
    ↓ uses distribution memory → (Cortex's share, Hippocampus's share)
    ↓ broadcasts on Limbic-local bus
Each Lobe reads its share
    ↓ uses distribution memory → (Column shares)
    ↓ broadcasts on Lobe-local bus
Each Column reads its share
    ↓ uses distribution memory → (Ganglion shares + translate ALU shares)
    ↓ broadcasts on Column-local bus
Each Ganglion reads its share
    ↓ uses 29 measurement caps → (per-Scap shares)
    ↓ broadcasts on Ganglion-local bus
Each Scap reads its share, updates weight cap locally via PWM × momentum × direction
```

The whole backward pass takes six clocks regardless of network size — one per hierarchy level plus one for the local Scap update.

**The substrate measures `|a · W|` because that _is_ the forward current through each wire.** No extra computation. The same physical wire that does the forward computation produces the backward routing signal as a byproduct.

This is the project's load-bearing architectural commitment. Whether it converges on substantive tasks is **H1**, the central hypothesis the simulation campaign exists to test.

## Architecture at a glance

Five structural levels plus one controller:

| Level           | Role                                 | Composition                                                         |
| --------------- | ------------------------------------ | ------------------------------------------------------------------- |
| **Scap**        | Atom of storage (one synapse weight) | 1 capacitor + ~30 bits SRAM                                         |
| **Ganglion**    | Atom of computation                  | 29 Scaps wired in 2-3-3-2                                           |
| **Column**      | Sequential signal transformation     | Chain of Ganglia + learnable translate ALUs                         |
| **Lobe**        | Multi-branch DAG composition         | DAG of Columns with skip connections                                |
| **Limbic Loop** | Top-level recurrent system           | Cortex Lobe + Hippocampus Lobe + Commissure, two-timescale learning |
| **Brainstem**   | Central controller                   | Small (~8–15k transistors), sets clocks, broadcasts loss            |

Three cross-cutting mechanisms:

- **Residual connections** at the Ganglion level — primary defense against dead-weight collapse
- **SpecialGeneralist** inside Lobes — gated Ganglion reuse via context masks, higher effective capacity per Scap
- **Analog robustness mechanisms** — Differential Pair op-amps, Dummy Scap calibration, Current Mirror Loss Share, Auto-Zeroing, Range Sensitivity (PGA), optional Ping-Pong substrate

The most distinctive defense in the whole architecture: **Physical Saturation** as primary bound on winner-take-all dynamics. The weight capacitor's hard supply-rail ceiling self-limits as `dV/dt → 0` near the rail. This is L2 regularization implemented in physics — no explicit `λ · ‖W‖²` term, free.

## How this differs from existing CIM / neuromorphic work

| Project                        | Substrate                         | On-chip learning    | Learning mechanism                                                     |
| ------------------------------ | --------------------------------- | ------------------- | ---------------------------------------------------------------------- |
| **Mythic AI**                  | Analog flash transistors          | No (inference only) | —                                                                      |
| **Intel Loihi**                | Digital neuromorphic, spike-based | Yes (STDP-flavored) | Local-Hebbian                                                          |
| **IBM analog AI / NorthPole**  | Analog matrix-vector              | Some research       | Gradient-descent variants (weight transport)                           |
| **BrainChip Akida, SpiNNaker** | Mostly spike-based                | Varies              | Spike-timing rules                                                     |
| **This project**               | Continuous analog currents        | Yes                 | Attribution-based hierarchical credit assignment (three-factor family) |

The distinguishing claim is the _combination_: continuous analog compute + on-chip credit assignment + multi-level hierarchy + locally-measured contribution instead of routed gradients. That combination is what the rest of the specification describes.

## Project structure

```
.
├── README.md                          # This file
├── draft5.1-1.md                      # Canonical spec, Part 1: architecture, mechanism,
│                                      #   hypotheses, math, open questions, protected list,
│                                      #   glossary (§0–§19, §22–§23)
├── draft5.1-2.md                      # Canonical spec, Part 2: simulation campaign and
│                                      #   future tracks (§20–§21)
├── docs/
│   └── draft/
│       ├── draft.heirachy.md          # Map of every draft and how each evolved
│       ├── project-history.md         # AI handoff: how the architecture evolved
│       └── project-personal.md        # AI handoff: who I am, how I work
├── draft/                             # Historical drafts (1.0 through 5.0) + the unsplit
│   │                                  #   draft5.1-full.md kept for reference
│   ├── draft1.0.md … draft1.5.md
│   ├── draft2.0.md … draft2.3.x2.md
│   ├── draft3.0.md … draft3.3.r1.md
│   ├── draft4.0.md … draft4.1.x1.md
│   ├── draft5.0.md, draft5.0.x1.md
│   └── draft5.1-full.md               # Unsplit version of the canonical spec, kept for
│                                      #   reference; split into draft5.1-{1,2}.md at root
├── src/                               # Python simulator (to be created)
├── tests/                             # pytest unit tests (to be created)
├── reports/                           # Phase reports as experiments run (to be created)
└── notes/                             # Working notes, ad-hoc analyses (to be created)
```

The canonical spec was split into two files (`draft5.1-1.md` and `draft5.1-2.md`) only because the markdown-to-PDF tool fails on the unsplit length; there is no content difference. Section numbers are continuous across both parts. The unsplit version lives at `draft/draft5.1-full.md` for reference.

**Reading order if you've just arrived:**

1. This README (you are here).
2. `draft5.1-1.md` — start with its §0 Reading Guide. If you only read three sections of the spec, read §2 (the mechanism), §3 (a concrete example), and §20.1 in `draft5.1-2.md` (the one-hour test that could falsify the central claim).
3. `docs/draft/project-history.md` — for the _why_ behind each architectural decision.
4. `docs/draft/project-personal.md` — only relevant if you're picking up the project in a new context.

## Status

**Phase: theoretical specification complete. Simulation about to begin.**

What exists:

- Architecture specification: locked at `draft5.1-1.md` + `draft5.1-2.md` (~2,230 lines total, split for PDF export only)
- Eleven testable hypotheses (H1–H11) with concrete pass criteria
- Ten-phase simulation campaign with hard exit gates, ablation matrices, and effort estimates
- Continuous-invariant monitors specified (loss conservation, dead-weight fraction, ceiling saturation, T_max clip rate)
- Negative-result protocols for each phase failure mode
- Reproducibility infrastructure (locked seed list, configuration hashing, phase reports)

What does not yet exist:

- Python simulator
- Phase 1 operator unit tests
- The **Minimum Viable Falsification** test (§20.1 in the spec) — a 1-hour single-Ganglion XOR run that would catch infrastructure bugs before investing weeks in Phase 2
- Any experimental data
- Any results

This README will be updated as each phase completes. Phase reports will appear in `reports/`.

## The central hypothesis

> **H1.** Attribution-based hierarchical diffusion converges on substantive tasks within 10× the step count of vanilla SGD on the same topology, with dead-weight fraction bounded below 5%.

Tested in Phase 2 of the simulation campaign. Pass criterion: converges on at least 2 of 3 tasks (analog XOR, sine regression, two-moons classification), median final loss within 10× of SGD baseline, dead-weight fraction < 5%, with Physical Saturation reaching 50% of Scaps between 20% and 50% of training duration.

If H1 fails after the documented remediation paths (Path 0: noise floor → Path 1: strip multiplier → Path 2: separate input sensor), the architecture's central learning commitment needs revisiting. This is the project's single biggest risk.

H2 through H11 only matter conditionally on H1.

## Methodology note

This project is built from intuition first, with literature comparison reserved for after architectural stability. The author developed the attribution-based hierarchical diffusion mechanism without first surveying the related literature — and then, after the architecture stabilized, identified its place in the three-factor synaptic learning family:

- **Three-factor learning rules** (Frémaux & Gerstner 2016) — pre × post × neuromodulator
- **Equilibrium Propagation** (Scellier & Bengio 2017) — local updates that compute gradient in the small-perturbation limit
- **Feedback Alignment** (Lillicrap et al. 2016) — random fixed feedback matrices still let networks learn
- **Layer-wise Relevance Propagation** (Bach et al. 2015) — attribution using exactly `|a · W|` as relevance score
- **Predictive coding** (Rao & Ballard; Friston) — local error minimization at each layer
- **e-prop** (Bellec et al. 2020) — eligibility traces in spiking RNNs

These are cross-validation anchors, not design influences. The mechanism was committed to before this literature was surveyed. The risk of this approach is reinventing wheels; the benefit is reaching architectural decisions the existing literature wouldn't have suggested because it pre-commits to digital or spiking framings.

> _"The fast answer will destroy your creativity."_ — author's working motto

## Honest framing

This project does **not** claim to:

- Build intelligence
- Implement the chain rule (exactly or approximately)
- Compute ∂L/∂W rigorously
- Inherit gradient descent's convergence guarantees
- Replicate biological brain function with high fidelity

This project **does** claim to:

- Be a coherent specification for a continuous analog compute substrate with on-chip learning
- Use locally-measured contribution as the attribution signal for hierarchical credit assignment
- Be physically realizable with standard analog IC techniques (Differential Pair op-amps, Current Mirror, capacitor storage with cascode refill)
- Have testable hypotheses with concrete pass criteria
- Have documented failure modes and remediation paths

Convergence is empirical, not theoretical. The simulation campaign in `draft5.1-2.md` §20 exists precisely to determine whether the architecture works in practice.

## Background

The author is a Year 2 undergraduate student. A prior project — **ChronoForge** — was a pure-hardware 2D game engine built on the Xilinx Basys3 FPGA: 640×480 at 60 Hz, no CPU, no OS, no instruction set, 18k LUTs, three independent hardware timelines processing game objects in parallel. The hardware-design experience from that project informed the substrate-level thinking in this one.

The architecture in `draft5.1-1.md` / `draft5.1-2.md` was developed over approximately seven months of solo intuition-building, then condensed and refined through a series of drafts (numbered 1 through 5.1) with AI-assisted critique and structural review. `docs/draft/project-history.md` documents the evolution from the initial brain dump through the final locked specification, and `docs/draft/draft.heirachy.md` is the file-by-file map of every draft.

## Contributing

Not yet. The project is solo at the specification stage. Once simulation is underway and Phase 2 has produced data, this section will be updated.

If you find the architecture interesting and want to discuss, opening an issue is fine — but please read at least the §0 Reading Guide and §2 of `draft5.1-1.md` first so we can talk about specifics.

## License

To be determined. Until a LICENSE file appears in this repository, content is © the author, all rights reserved.

## Acknowledgments

The architectural specification was developed iteratively with AI assistance for critique, structural review, and naming. Where literature anchors are cited, they are cross-validation references — the architecture was designed before this work was surveyed. Any errors of attribution or framing are the author's, not the cited authors'.

---

_Specification locked at draft 5.1 (split into Part 1 / Part 2 for layout, no content change). The Python phase begins next._
