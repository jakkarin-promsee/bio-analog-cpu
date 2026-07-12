# Scalable Class-Incremental Learning Based on Parametric Neural Collapse (SCL-PNC)
- **Authors / Year / Venue:** Chuangxin Zhang, Guangfeng Lin, Enhui Zhao, Kaiyang Liao, Yajun Chen / 2025 (submitted Dec 2025; Pattern Recognition journal submission)
- **Link:** https://arxiv.org/abs/2512.21845 (fetched)
- **Tier / Topic:** tier2 / t2.2 closed-form classifier
- **Relevance:** ⭐⭐ — the newest word on the ETF-for-CIL line: static ETF geometry is *too* rigid under shifting distributions; they make it parametric. Mostly a boundary marker for us.

## TL;DR
SCL-PNC accepts the neural-collapse/ETF program for class-incremental learning but attacks its two rigidities: a fixed backbone can't absorb genuinely new domains, and a **static ETF misaligns** when class counts grow and distributions shift. It grows the backbone with minimal "adapt-layers" on demand, converts the static ETF into a **dynamic parametric ETF** that adapts as classes arrive, and keeps expanded modules consistent with parallel-expansion knowledge distillation.

## The mechanism (how it actually works)
Three coupled moves:

1. **Demand-driven backbone expansion:** small adapt-layers are added only when new data warrants it — capacity grows sub-linearly with tasks, existing parameters are not retrained (the parameter-isolation family, done cheaply).
2. **Parametric ETF:** instead of one frozen simplex over the whole label space (the Terminus approach, this folder), the ETF's parameterization is allowed to adjust as new classes arrive — repairing the misalignment between pre-assigned vertices and the actual shifted feature distribution, while keeping the equiangular structure as the organizing prior.
3. **Parallel expansion + distillation:** expanded modules learn alongside (not stacked after) existing ones, with distillation keeping feature spaces aligned — countering the drift that serial expansion accumulates.

## Key results / claims
- Claims effectiveness on standard CIL benchmarks with growing category counts; positions itself as the *scalable* member of the neural-collapse CIL family. (Journal-submission stage; treat headline numbers as not yet peer-anchored.)

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer's target geometry; tangentially the bulk (their expansion story is the road we deliberately did not take — our bulk is frozen, single, and never grows).
- **Same as us:** recognizes that pre-committed geometry (static ETF) and a shifting world disagree — the same tension our sleep re-fit resolves on the statistics side.
- **Different from us:** solves it by *training* — adapt-layers, distillation, a parametric learnable geometry. Every ingredient is gradient-paid and backbone-touching; none of it is closed-form.
- **What we could borrow or test:** the negative result implied by their motivation — **static whole-label-space ETF degrades under distribution shift and growing class counts**. If we test ETF-target ridge solves (Yang 2022 card), this paper predicts the failure mode to watch: vertex assignments going stale as the stream drifts. Our sleep already re-fits statistics; an ETF-target variant would need vertex re-anchoring at sleep, which is a closed-form Procrustes-style step — worth noting, not yet worth building.
- **What contradicts or challenges us:** if even the geometry-purist camp concedes the fixed simplex must become adaptive, the "no-fit anisotropy escape" is weaker than it first looks — geometry alone doesn't dodge drift; something must still track the world (for us, the covariance statistics do).

## Follow-on leads
- Neural Collapse Terminus (this folder) — the static-ETF position this paper argues against.
- Progressive Neural Collapse (arXiv 2505.24254) — a parallel "un-fix the terminus" argument.
- Guiding Neural Collapse (NeurIPS 2024, arXiv 2411.01248) — nearest-ETF optimization, the third position.
