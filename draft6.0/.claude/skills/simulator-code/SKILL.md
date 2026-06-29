---
name: simulator-code
description: Work on the draft-6 numpy simulation code — the per-phase pNlib / run / plot scripts; it is a chip netlist, not normal Python. Use for "edit the sim", "modify p4lib", "what does pNlib do", "add a probe", "the simulation code", "run the 6.0 sim".
---

# The draft-6 simulator

**Where it lives:** `draft6.0/src/phase{1..5}/` — one folder per phase, each with its own apparatus.
- Shared libraries: **`p2lib.py`, `p3lib.py`, `p4lib.py`, `p5lib.py`** (`p4lib`/`p5lib` are the most feature-complete; `p5lib` adds per-depth heads, the calibrated-exit gate, a forward-MACs meter, and the A6 continual harness). **Phase 1 has no `p1lib`** — its code lives in `phase1/exp0/models_extra.py` plus the per-experiment scripts.
- Per phase: `pNlib.py` (apparatus, Phases 2–4) · `run_*.py` (one run script per experiment) · `plot_*.py` (figure script) · `figs_*/` (outputs: `.png` + `arrays.npz` + `manifest.json`).

**It is a behavioral numpy sim (ideal floats, ideal operators) — a *netlist of a chip*, not a model.**
"Optimizing"/vectorizing the Python can quietly make it **unbuildable** in silicon — **correctness over speed.**
Run **single-threaded** (`OMP_NUM_THREADS=1 python -u …`) — there is a known OpenMP hang on this Windows box.

**"Done" for a code change:** it runs; the result is loggable (one variable changed, multi-seed); the exp card is writable from the output.

**Budget:** this skill + the active `phaseN/README.md`. Open `pNlib.py` only when modifying it, not for orientation.
