# P6.2 — flatness (S-SGD + zeroth-order sharpness) — **SKIP-CARD**

*Inheriting from P6.0 (tap ≫ weight: weight-channel retention 0.895 @σ=0.4 is far milder than the tap-directional
0.586 @rms 4.0) and P6.1 (the iid noise-augmentation brings the **tap** curve into band: tap-directional retention
0.841→0.946).*

**Pre-registered skip (design §3 P6.2).** P6.2 was conditional: *"run iff the weight channel is dominant AND P6.1
leaves a weight-channel gap; if P6.0 confirms tap ≫ weight and P6.1 brings the tap curve into band, P6.2 is a
one-line skip-card — flatness would improve a non-dominant channel, not worth continual-scale compute."* Both
antecedents hold:

- **tap ≫ weight** (P6.0): the weight channel (multiplicative, old-A7) retains 0.895 @σ=0.4 — the *mildest* channel;
  tap/input directional are the dominant enemies (retention ~0.59 @rms 4.0), and the norm-amplified tap channel is
  where the fragility lives. ADC is fine ≥3-bit; common-mode is auto-rejected by the layernorm.
- **P6.1 substantially closes the tap gap** (0.817→0.865 combined; per-rung to 0.946) via generic iid augmentation —
  no weight-channel gap remains that a flatness lever would be needed to close (and flatness targets the *weight*
  channel, not the tap residual regardless).

**Verdict: SKIPPED.** Flatness (S-SGD weight-noise + the zeroth-order sharpness pass) would harden the
*non-dominant* weight channel; the compute (a continual-scale periodic forward-only pass over the SCFF weights) is
not justified by the verdict. The apparatus (`p6lib.flatness_probe`, `weight_noise_update`, `zosa_sharpness`) is
built and guard-checked, available if a later weight-channel gap surfaces (e.g. under PVT realism, a deferred phase).
Nothing banked. Continual-safety: n/a (no change).
