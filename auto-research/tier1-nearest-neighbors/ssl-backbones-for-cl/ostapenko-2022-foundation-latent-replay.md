# Continual Learning with Foundation Models: An Empirical Study of Latent Replay
- **Authors / Year / Venue:** Oleksiy Ostapenko, Timothée Lesort, Pau Rodríguez, Md Rifat Arefin, Arthur Douillard, Irina Rish, Laurent Charlin — 2022 — CoLLAs 2022 (PMLR v199)
- **Link:** https://arxiv.org/abs/2205.00329 (fetched; proceedings: https://proceedings.mlr.press/v199/ostapenko22a.html)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐⭐ — the systematic sweep of "which frozen encoder makes the best CL substrate," with the SSL-specific finding: label-free pretraining wins **out-of-distribution**.

## TL;DR
Freeze a zoo of pretrained encoders (varying architecture, pretraining algorithm — supervised vs SSL — and pretraining data), do continual learning in their latent space with latent replay, and ask what property of the encoder predicts downstream CL. Findings: a **non-parametric classifier on frozen latents already gives reasonable CL at negligible compute**; broader pretraining data beats narrower at every replay size; and **SSL pretraining is the better substrate specifically when the downstream domain is out-of-distribution** w.r.t. pretraining.

## The mechanism (how it actually works)
Latent replay stores features, not images, so the whole CL problem reduces to: how linearly-tractable and how *transferable* is the frozen latent geometry? Supervised pretraining organizes latents around the pretraining label set — excellent when downstream classes are in-distribution relatives, brittle when they are not. SSL objectives, trained to preserve input structure rather than label boundaries, leave more of the input manifold intact in the latents, which is exactly what a downstream OOD task needs to find *its* boundaries. The non-parametric-head finding is the same logic at the readout: if the geometry is good, prototype/nearest-mean reading is nearly free and nearly enough.

## Key results / claims
- Reasonable CL performance from a non-parametric classifier on frozen pretrained latents at negligible compute.
- Broader pretraining data → better downstream CL across replay budgets.
- SSL pretraining > supervised pretraining for OOD downstream domains; the reverse can hold in-distribution.
- Transfer/forgetting depend strongly on input-data characteristics, not just the CL algorithm.

## How it relates to us
- **Organ / phase touched:** namer family choice (P7 — closed-form prototype heads); the bulk-as-substrate question (P11 decomposition).
- **Same as us:** validates both our head economics (cheap non-parametric/closed-form reading of a frozen-ish representation is competitive) and our substrate bet in the regime we actually occupy — a stream that is, by construction, "out-of-distribution" relative to any offline pretrain (there is no pretrain; everything is OOD until seen).
- **Different from us:** encoders are large, offline-pretrained, fully frozen; CL happens only in the head + replay; no online growth, no energy account, no forward-only constraint.
- **What we could borrow or test:** their axis decomposition (architecture × pretraining signal × pretraining data → CL outcome) is the clean experimental grammar for a question we half-answered in P11 ("is it just SLDA?"): sweep *bulk variants* (random frozen / SCFF-frozen / SCFF-live) × fixed namer, on fixed arenas — we ran pieces of this; their framing would make the public version legible.
- **What contradicts or challenges us:** "broader pretraining data wins" is the scale argument against small stream-grown substrates: a big offline SSL encoder may simply dominate our bulk on any static axis. Our answer must stay where P10/P11 put it — the live-stream, energy, and safety axes — not representation quality per se.

## Follow-on leads
- Non-parametric heads on frozen latents (ties to Janson 2022 NCM card, t1.5).
- "In-distribution supervised vs OOD self-supervised" as a testable boundary for when label-free substrates win.
- Lesort's follow-up line on scaling and forgetting in large pretrained models.
