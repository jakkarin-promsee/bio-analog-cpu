---
name: simulator-code
description: Work on the draft-6 numpy simulation code — the per-phase pNlib / run / plot scripts; it is a chip netlist, not normal Python. Use for "edit the sim", "modify p4lib", "what does pNlib do", "add a probe", "the simulation code", "run the 6.0 sim".
---

# The draft-6 simulator

**Where it lives:** `draft6.0/src/phase{1..10}/` — one folder per phase, each with its own apparatus.
- Shared libraries: **`p2lib.py` … `p10lib.py`** (one per phase, Phases 2–10). `p5lib`/`p6lib` carry the frozen cheap brain — per-depth heads, the calibrated-exit gate, a forward-MACs meter, the A6 continual harness, and the `NoiseAugContrast` noise model; `p7lib` … `p10lib` carry the Stage-2 namer — the streaming `partial_fit`, the DDM gate, the CBRS bounded LUT, and the ADC-centred cost meter. **Phase 1 has no `p1lib`** — its code lives in `phase1/exp0/models_extra.py` plus the per-experiment scripts.
- Per phase: `pNlib.py` (apparatus, Phases 2–4) · `run_*.py` (one run script per experiment) · `plot_*.py` (figure script) · `figs_*/` (outputs: `.png` + `arrays.npz` + `manifest.json`).

**It is a behavioral numpy sim (ideal floats, ideal operators) — a *netlist of a chip*, not a model.**
"Optimizing"/vectorizing the Python can quietly make it **unbuildable** in silicon — **correctness over speed.**
Run **single-threaded** (`OMP_NUM_THREADS=1 python -u …`) — there is a known OpenMP hang on this Windows box.

**"Done" for a code change:** it runs; the result is loggable (one variable changed, multi-seed); the exp card is writable from the output.

**Budget:** this skill + the relevant `phaseN/README.md`. Open `pNlib.py` only when modifying it, not for orientation.
