---
name: project-frame
description: Understand what this project IS before touching it — a chip (analog compute substrate), not an ML model; the SCFF+GD hybrid; the reflexes that are wrong here. Use for "what is this project", "is this ML", "explain the architecture", "what does this chip do", "what is SCFF".
---

# The frame — read before you touch anything

**This is a chip, not a model.** A bio-inspired analog compute substrate whose bet is that brain-like
computation can be the *cheap path in silicon*. Weights are analog charge on capacitors; compute is current in
a crossbar of them; it **learns on-chip, online**. The four committed properties — **online, sparse,
continuous, resident-weight** — are substrate facts, not training tricks. Method: **copy the brain's *function*,
cheat the *implementation*** (analog physics where physics is cheaper, modern DL math where math is cheaper).

**The two-brain hybrid in one breath:** a cheap unsupervised **SCFF** front (~80%, label-free, forward-only)
organizes the world for free; a small precise **gradient-descent** back (~20%) maps features to real labels —
*direction is the one expensive thing in learning, so pay for it once.* The two chain as **residual boosting
blocks**, threshold-gated, sleep-consolidated over a hippocampus LUT.

**Reflexes that are WRONG here — learn the reason, not the rule:**
- *"It's just Forward-Forward / just SCFF."* SCFF is only the cheap 80%; the whole is a hybrid, and our SCFF is reformulated (summation not concat, mono-forward dual-rail) for the substrate.
- *"Why not backprop everything?"* Backprop-everything is exactly what the substrate can't afford — the 80/20 split exists to avoid it.
- *"Make it biologically faithful."* Faithfulness is not the goal; cheap reproduction of the *function* is.
- *"Optimize / vectorize the Python."* The simulator is a **chip netlist**; "optimizing" can quietly design something unbuildable. Correctness over speed.
- *"Tune it until it converges."* A failed run is **data** — characterize and report it.
- *"Rename the bio-names to be rigorous."* They're a structural semantic system; considered and rejected.

**Budget:** read this skill. Architecture detail → load `draft6.0/CLAUDE.md`; the full story → `draft6.0/context.md`; the why and the person → `docs/essence/the-essence.md`.
