# Synthetic Benchmarks Overstate Forward-Forward Scaling: Real-Data Limits of Layer-Local Training
- **Authors / Year / Venue:** Yucheng Chen / 2026 / arXiv:2606.06539 (preprint)
- **Link:** https://arxiv.org/pdf/2606.06539 (fetched; title/id/core-claim confirmed from PDF metadata — full abstract & numbers ⚠ UNVERIFIED)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐⭐ — external, independent statement of *exactly* the risk our Phase 11 limit-map was built to answer; both validates and challenges our methodology.

## TL;DR
Layer-local / Forward-Forward methods look far better on **synthetic or curated benchmarks** than they do on **real data** — the scaling gains reported on artificial tasks shrink or vanish under realistic data distributions. A caution against generalizing FF-family results from synthetic microscopes to deployment.

## The mechanism (how it actually works)
An evaluation/critique paper: it contrasts FF-family performance on synthetic/structured benchmarks against performance on real datasets, and reports a systematic gap — the layer-local objective's apparent depth/scaling benefits are partly an artifact of the benchmark's structure, not a property that transfers to messy real data.

## Key results / claims
Central thesis: **synthetic benchmarks overstate FF scaling**; real-data performance is the honest test and it is weaker. (Specific datasets and numbers did not extract from the PDF — flagged UNVERIFIED; title, arXiv id, and thesis confirmed.)

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** Phase 4/5's **synthetic headroom microscope** and Phase 11's **real-data limit map** — the exact tension this paper names.
- **Same as us:** we *independently reached the same conclusion* and acted on it — Phase 11 took the object off the synthetic bench onto 8 real arenas precisely because the headroom task is a constructed microscope, not a benchmark. Our own docs flag the depth result as a "representation claim on a task we constructed."
- **Different from us:** we did the real-data pass and reported the **floors honestly** (autocorrelated streams HAR/electric/covtype floor; the ELEC2 persistence trap), plus a real *win* (gas-sensor drift beats tuned ER). So this paper's warning is one we have already partly discharged — but it is external confirmation the warning is real for the family at large.
- **What we could borrow or test:** if it names *which* real-data properties break FF scaling (autocorrelation, low intrinsic dimension, distribution shift), those are ready-made axes to extend our limit map's channel set.
- **What contradicts or challenges us:** it directly challenges any claim resting on the synthetic headroom result (the `0.550 > 0.531` depth win). Our defense must always pair that synthetic result with the Phase-11 real-data map — this paper is the reason that pairing is non-negotiable.

## Follow-on leads
Real-data evaluation protocols for local learning; which data properties (autocorrelation, intrinsic dim, shift) break layer-local scaling; synthetic-vs-real generalization gap for continual learners; benchmark-design honesty for forward-only methods.
