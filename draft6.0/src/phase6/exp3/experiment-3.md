# P6.3 — the per-sample-norm root re-examination — **SKIP-CARD** (STOPPING MARK ②)

*Inheriting from P6.1: the dominant tap-directional channel is substantially hardened by generic iid augmentation
(retention 0.817→0.865 combined, a partial band crossing), clean acc improved, selectivity held. The only residual
is the input-transducer channel (0.812→0.822, marginal).*

**Pre-registered skip (design §3 P6.3 + STOPPING MARK ②).** P6.3 was conditional — *"run iff P6.1+P6.2 leave a
gap"* — and its default outcome was pre-declared: *"leave the norm alone, harden around it; touching the root is
licensed only by a result that pays for itself on **both** the A7 and the P5-depth axes."* The conditions to open it
are **not** met, and the reasons to leave it are load-bearing:

- **The dominant gap is closed around the norm, not by changing it.** P6.1's augmentation hardened the tap channel
  *while keeping the per-sample layernorm intact* — the "harden around it" path succeeded, so the dangerous root
  surgery is unnecessary for the dominant channel.
- **The only residual is a non-dominant, better-handled-elsewhere channel.** The input-transducer directional residual
  is a **Scoped-YES** item for Stage-2 read-side defence (calibration under shift), not a reason to touch a component
  that is load-bearing for **four** P5/P4 properties (tail-L12 depth, BWT, readout-vs-tuned-BP, A2 nuisance-robustness).
- **The norm is the depth lever.** P6.0 made the tradeoff precise: the per-sample layernorm that *amplifies* the
  directional shift is the same normalization that *won* P5 depth and A2 nuisance-robustness. A "noise-robust norm"
  risks trading A7 for A2/depth — exactly the failure the STOP-② guard fences against. No result on the table pays on
  *both* axes, so the licence to touch the root is not granted.

**Verdict: SKIPPED — leave the P5 norm, harden around it.** The apparatus (`p6lib` norm-variant hooks + the full
P5+P4 abort panel) is available if a future result forces the root open. Nothing banked. Continual-safety: n/a.
