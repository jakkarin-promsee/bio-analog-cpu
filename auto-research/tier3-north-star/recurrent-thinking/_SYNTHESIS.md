# Synthesis — Recurrent "think until it settles" compute  (Tier 3)
**The question:** what is the buildable, analog-native path to "the brain thinks many times until it settles," and who is closest? Rank by (analog-native-ness of the settle × principled learned halt × composes with frozen SCFF + closed-form namer + the planned delta-rule memory).
**Already in `draft6.0/research/`:** the north-star dossier `3-recurrence.md` maps the classics — DEQ (settle = infinite depth), EqProp (the settle also yields the gradient), predictive coding (iterative error minimization), ACT/PonderNet (learned halting), Universal Transformer (looped attention + ACT), LSTM/GRU (keep the gate, not the throne). This folder extends it with the 2020–2025 engineering layer: convergence *guarantees*, the LLM-scale latent-reasoning wave, energy-verifier halting, tiny-scale recursion, hardware EqProp, and the gated-delta recurrent state.

## The landscape (the engineering view, not the neuroscience one)

Four camps now exist, and they answer different halves of our question.

**Camp 1 — implicit / equilibrium models (the settle as math).** DEQ said "the answer is the fixed point"; monDEQ (Winston & Kolter 2020) said the part we actually need: *constrain the operator so the fixed point provably exists and iteration provably converges* — dissipativity as an architecture constraint, not a hope. This camp treats convergence as a certificate you buy in parameter space. It is the direct math of an analog relaxation, and it is the only camp that guarantees the loop settles at all.

**Camp 2 — the latent-reasoning / test-time-compute wave (2024–2025, the scaling evidence).** Geiping et al. iterate one recurrent block inside a 3.5B LLM and buy reasoning with iterations instead of parameters; Saunshi et al. prove the economics (reasoning needs depth, not parameters — k layers looped L times ≈ kL layers); Coconut shows the thought should stay a continuous vector fed back on itself (the token projection destroys the superposed alternatives); TRM shows the whole recipe works at 7M params/2 layers with a one-head learned halt, beating LLMs on ARC. Two findings matter most for us: (a) Geiping's **zero-shot halt** — stop when the KL between successive states falls below threshold; *convergence itself is the halting signal, no training needed*; (b) Geiping's **orbits** — free trained recurrence learns rotating, non-converging latent dynamics for hard tokens. The field's own loops do not always settle; ours physically must (or must be constrained to).

**Camp 3 — energy-based iterative inference (the halt as a learned scalar).** EBT trains a transformer *as an energy function* and thinks by descending it until it bottoms out — verification and generation become the same object, and the energy value is a continuous, self-generated confidence: "correctness as a feeling," shipped as engineering. IRED adds the annealing schedule — a sequence of smoothed-to-sharp landscapes, so descent doesn't stick — and gets test-time generalization to *harder* problems by spending more steps. This camp owns the principled halt (energy plateau) but pays for it with the most off-substrate training (backprop through optimization).

**Camp 4 — physical settle machines + local learning (the analog natives).** Laydevant et al. train a real D-Wave Ising machine with EqProp: the anneal is the inference, and a second nudged anneal plus a *local correlation difference* is the weight update. No backward pass exists in the building. This is the only camp where both the thinking and the learning are executed by physics — with honest taxes: two settles per update, symmetric couplings, heavy embedding overhead. Adjacent, Gated DeltaNet is not a settle at all but the substrate-legal *cross-time state*: gate (decay) + delta rule (error-correcting overwrite) on a fast-weight matrix — every operation crossbar-native, and the modern confirmation of the dossier's "keep the LSTM gate, not the throne."

## How WE differ

Nobody in this literature has our starting position: a **frozen, label-free bulk + a closed-form namer** that already works on streams. Every camp trains its loop end-to-end with gradients through time (truncated BPTT, backprop-through-optimization, or deep supervision); we cannot and — the P7 lesson — may not need to. Conversely, we have nothing they have: P1–11 is entirely feed-forward; we own no loop, no halt, no measurement of iteration-vs-difficulty. What is genuinely ours to claim: the substrate makes Camp 1's expensive root-find and Camp 3's descent loop *free physics*, and our namer margin is a *fit-free* halt signal no one else gets for free. What is a re-invention risk: "correctness-as-feeling" is EBT's energy and TRM's BCE halt head — prior art exists; our novelty must be the closed-form/analog execution, not the idea.

## The buildable path (the ranked recommendation)

**Build first — the certified settle with a convergence halt (monDEQ × Geiping).** One weight-tied block over frozen SCFF features, `z ← f(z, x)`, with a contractive/monotone constraint imposed by construction; iterate to the fixed point; namer reads z*. Halt v0 = ‖Δz‖ (or namer-output KL) below threshold — Geiping proved the convergence-halt works *untrained*, and in analog it is a comparator on "currents stopped changing." This is rank 1 because it needs **zero new learned machinery**: no trained loop weights required for v0 (even a random contractive block + LUT pull answers the first question), no trained halt, and it composes with every frozen organ. The three measurements: accuracy vs iteration budget; iterations-to-settle vs input difficulty (does ponder time track hardness for free?); what constraint strength costs (the orbit tension).

**Second — the learned halt (TRM-shaped).** Upgrade the halt from "state stopped moving" to "I judge my answer correct": TRM's recipe is one head + BCE on correctness, and our closed-form namer already emits margin/confidence — so v1 can be *fit-free* (halt on margin plateau, EBT-shaped) before any trained head. This is where correctness-as-feeling becomes a component.

**Third — the memory spine (Gated DeltaNet, closed-form).** The loop settles *within* a thought; a gated-delta fast-weight memory carries state *across* thoughts — with α (decay) driven by our existing drift-gate signal and β (write strength) by namer error. This is the hippocampus-organ build (t3.1) meeting the loop, all crossbar-native.

**Fourth — learning through the settle (EqProp, Laydevant's protocol).** When the loop must learn, EqProp is the only substrate-native candidate: two relaxations + local correlation diff, with reverse-anneal-style nudging from the free equilibrium. Proven on physical hardware; taxes known (2× settle time, reciprocal couplings).

**Fifth — the annealed settle (IRED-shaped).** Inject decaying noise into the relaxation (analog temperature as the schedule) to escape bad basins — physically free for us, and continuous with the P6 noise-helps finding.

Honest counters, stated once: (1) the orbit problem — forcing every trajectory to converge may forbid the dynamics that make hard reasoning work; measure the cost early. (2) The task gap — every reasoning win here is on algorithmic/puzzle structure; nothing yet shows a settle loop helps a drifting sensor stream. The first experiment needs one task where thinking *can* help (Saunshi's synthetic suite is the ready source). (3) All Camp-2/3 training is substrate-illegal; TRM's no-BPTT schedule (free-run cycles, learn on the last) is the least illegal sim-side stand-in until EqProp is wired.

## The gap / what we haven't tried
- Any recurrence at all (P1–11 is feed-forward) — the v0 loop above is one pNlib file.
- The Δstate-convergence halt; the namer-margin-plateau halt; iteration-count-vs-difficulty curves.
- A contraction-constrained crossbar (monDEQ parameterization) and its expressivity price.
- EqProp on our own bulk (two-settle local update in sim).
- Noise-scheduled settling (analog annealing) as basin-escape.
- The parameter-matched depth test: small block iterated 12× vs the L12 bulk (Saunshi's transplant).

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Winston & Kolter 2020 — monDEQ](winston-2020-monotone-equilibrium.md) | ⭐⭐⭐⭐⭐ | Convergence as a parameterization constraint — the settle certificate. |
| [Geiping et al. 2025 — recurrent depth](geiping-2025-recurrent-depth.md) | ⭐⭐⭐⭐⭐ | Latent iteration scales + the zero-training convergence halt (and the orbit warning). |
| [Laydevant et al. 2024 — Ising EqProp](laydevant-2024-ising-eqprop.md) | ⭐⭐⭐⭐⭐ | Physics does both inference and learning — hardware-proven, with the nudge protocol. |
| [Jolicoeur-Martineau 2025 — TRM](jolicoeur-martineau-2025-tiny-recursion.md) | ⭐⭐⭐⭐⭐ | The chip-sized recursion recipe + the one-head BCE halt (self-judged correctness). |
| [Gladstone et al. 2025 — EBT](gladstone-2025-energy-based-transformers.md) | ⭐⭐⭐⭐⭐ | Correctness-as-feeling as a learned energy; halt = the energy bottoms out. |
| [Du et al. 2024 — IRED](du-2024-ired-energy-diffusion.md) | ⭐⭐⭐⭐ | Annealed landscapes: noise as the settle schedule; more steps solves harder instances. |
| [Yang et al. 2024 — Gated DeltaNet](yang-2024-gated-deltanet.md) | ⭐⭐⭐⭐ | The crossbar-native cross-time state: gate + delta rule on fast weights. |
| [Saunshi et al. 2025 — looped transformers](saunshi-2025-looped-transformers.md) | ⭐⭐⭐⭐ | The theorem for our economics: reasoning needs depth-from-time, not parameters. |
| [Hao et al. 2024 — Coconut](hao-2024-coconut.md) | ⭐⭐⭐ | Keep the thought continuous; don't name between think-steps (the argmax destroys superposition). |

## Leads spawned
- **Kendall et al. 2020, end-to-end analog EqProp (SPICE resistive networks)** — the closest-to-substrate training paper; deserves its own card when the loop experiment starts.
- **Path independence / stability of equilibrium models** (Anil et al.) — when the settled answer doesn't depend on the initial state — the reliability question for a physical loop.
- **Mixture-of-Recursions (2025)** — trained per-token recursion-depth routers — the trained-halt counterpart to Geiping's zero-shot exit.
- **Oscillator Ising machines + EqProp (arXiv 2505.02103)** — the non-quantum physical-settle hardware family.
- **Hopfield/CAM attractors as the loop's memory pull** — bridge t3.1's Li 2020 analog CAM into the settle dynamics (recall = a basin).
- **Reasoning-by-superposition theory (2025)** — why continuous latent search beats committed token search — the theory of Coconut's BFS effect.
