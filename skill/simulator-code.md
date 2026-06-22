# `skill/simulator-code.md` — editing the simulator: mental-model map

> ## ⚠️ HISTORICAL — the attribution-era `src/` simulator (draft 5.1)
> **This map describes the *old* simulator, built for the attribution chip — kept as a guideline for how
> the previous build worked, not as the current task.** Draft 6.0 (June 2026) set the circuit/ALU/memory
> aside to **stabilize the core math first**. **Update (2026-06-23):** the draft-6.0 behavioral sim has since
> been written and run across `draft6.0/src/phase{1,2,3,4}/` (numpy SCFF + GD + probes; `p4lib.py` + per-phase
> run/plot scripts) — Stage 1 (Phases 1–4) is complete. A fresh draft-6.0 code map is still TODO; until it
> exists, read this only to understand the historical `src/` (the Ganglion, broadcast + momentum, the lean
> baseline). The live plan is [`draft6.0/`](../draft6.0/idea/ideas1.md).
>
> ---
>
> *(Original 5.1-era content below, unchanged.)*
>
> **Use this when** you're about to change `src/library/*` (wires, capacitor, pwm, scap, banks, alu,
> control) or `src/example/*` (the builds, brainstem, run_xor).
>
> This is a **router**, not a procedure — it tells you which docs to load and the mindset to hold; read
> the docs it points to. `CLAUDE.md` is already in context; this adds the code layer.
> **New here? Read `skill/project-explore.md` first** — the concept entry point.

## The one thing to internalize first

This Python **looks like software but is a chip.** Every clean line hides silicon (a bus, a mux, a
MAR/MDR inter-processor transfer). Trust the *shapes*; distrust the *ease*.

## Read these first, in order — only the parts named

1. **`src/docs/core_logic.md` — every time, before touching code.** The Python↔hardware decoder. Burn in
   **§6: moving a value across a scope wall is a bus transaction — never "just pass the object."**
2. **`src/docs/code_concept.md`** — the class shapes you're editing. Match what's there.
3. **`src/docs/context.md` §4** (decision log — what we chose *and reverted*) and **§6** (the traps).
4. **`src/docs/question.md`** — skim when a construct confuses you ("why io_id? why is run() blocking?").

Don't re-read the whole spec for a code change — pull only the section a doc points you to.

## The mindset (load-bearing)

- **Three live classes only:** `Scap`, `ALU`, `ControlUnit`. ColumnGroup / Lobe / Brainstem are all the
  same `ControlUnit`. Everything else is a wire, a cap, or data.
- **The wiring rule:** pass a `SignalWire` into a class and let it `append_trigger(self.handler)` in
  `__init__` (self-registration). Don't move registration out to the build.
- **Credit = momentum.** Backward is a broadcast pulse × per-Scap momentum. No gradient, no per-weight
  error routing, no Current Mirror in the baseline.
- **Topology is data.** The instruction list is the wiring; rewiring = editing data, never modules.

## Constraints you cannot violate

- **§22 (the protected list)** in `draft5.1-1.md` — locked architecture decisions. Don't reopen.
- **The recorded deviations** (`src/docs/context.md §5`): the lean broadcast+momentum baseline and the
  shallower credit hierarchy are *deliberate*. Don't "fix" them back without phase data.
- **ids on wires are ints** (`group_id`, `weight_model_id`, `target_group`); `alu_id` is a `str` dict key.
- **Don't import ML/backprop instincts.** No gradient routing, no weight transport. A Scap is a wire.

## Where the build is now (2026-06)

- **SLICE-1 (one Ganglion) is built and runs** end-to-end: boundary bridge, crossbar, Ganglion ALU,
  EMA momentum, backward broadcast, basic supply-rail saturation (`W_RAIL`). `python -m src.example.run_xor`.
- **Stable.** The lean baseline has no hidden-layer credit *by construction* (broadcast + single global
  feedback). The author is exploring `run_xor` pre-Phase-2 on **linearized** data (range / activation
  probes) — intentional play, not an H1 verdict; there is no clean XOR result on the current code.
- The boundary flag (#2) is resolved as **CU-mediated copy** (boundary caps on the local bus, bridged by
  indexed parent access in `control.py`). `code_concept.md §3` still describes the older variant —
  reconcile if you touch the bridge.
- Many algorithms are first-pass `[ALGO]` fills (forward math, momentum EMA, update equation, loss).

## Traps (these cost real time — `context.md §6`)

- Re-adding the Current Mirror / measurement caps / distribution memory — they're spec, not baseline.
- Making registration external again — we tried; self-register won.
- Treating ColumnGroup as a learning level — it's ALU-cost packaging.
- Letting the Scap compute its own `forward_sign` — it can't; the ALU does.
- Passing cap objects across a scope wall instead of the start-pointer bridge.

## Done means

- It runs (`run_xor` at minimum, or a targeted probe of what you changed).
- You didn't violate §22 or silently undo a recorded deviation.
- If you added a **cross-scope data path**, you re-read `core_logic.md §6` and used the bridge.
- If you changed a **design decision**, you updated `context.md §4` so the next mind doesn't re-derive it.
