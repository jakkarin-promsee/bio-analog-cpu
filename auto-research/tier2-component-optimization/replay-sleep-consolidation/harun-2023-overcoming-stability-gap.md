# Overcoming the Stability Gap in Continual Learning
- **Authors / Year / Venue:** Md Yousuf Harun, Christopher Kanan / 2023 (arXiv) → TMLR 2024
- **Link:** https://arxiv.org/abs/2306.01904 (fetched; html v3 read for mechanism)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule (the *schedule/how-much* side)
- **Relevance:** ⭐⭐⭐⭐⭐ — the consolidation-schedule paper whose fix mechanisms **already exist inside our namer**: class-mean weight init and frozen old-class outputs — plus a 16.7× fewer-updates result that reframes "how much to consolidate."

## TL;DR
The stability gap is caused by two things: randomly-initialized outputs for new classes producing huge onset loss, and excessive plasticity letting small new batches perturb old representations. Fix both — **Stability Gap Mitigation (SGM)** — and the gap nearly vanishes **and** you need far fewer network updates for the same accuracy. Consolidation gets both safer and cheaper at once.

## The mechanism (how it actually works)
SGM stacks four moves, all aimed at shrinking the onset shock: (1) **data-driven weight init** — a new class's output vector is initialized to the **mean of unit-length embeddings** of that class, not random noise (kills the initial loss spike); (2) **dynamic soft targets** that preserve the old class distribution instead of hard one-hot; (3) **LoRA** low-rank hidden updates to cap how much the trunk can move; (4) **freeze old-class output weights** during rehearsal. Because the onset shock is removed, the model needs **far fewer gradient updates** to re-stabilize — the schedule can be much sparser without losing accuracy.

## Key results / claims
On ImageNet-1K-pretrained ConvNeXtV2 + Places365-LT (5 rehearsal sessions): the stability-gap metric drops **~50×** (0.006 vs 0.300), ImageNet-1K retention 77.64% vs a 77.58% joint upper bound, 70.30% over all 1365 classes — while delivering **16.7× fewer network updates**, **31.9× fewer TFLOPs**, and **18× less training time** than joint retraining. Safer *and* an order of magnitude cheaper.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer (SLDA/RanPAC prototypes), sleep cadence (grid-4), new-class onset.
- **Same as us:** two of the four SGM moves are **things our architecture already is**. "Init the new-class output to the class-mean embedding" = a **prototype**, which is exactly what our namer stores and re-anchors at sleep (P9.4 proto-reanchor). "Freeze old-class outputs during rehearsal" = our closed-form namer never overwrites old-class structure by construction. We got the onset-shock fix *for free* from being prototype-based and closed-form.
- **Different from us:** the LoRA/soft-target parts are gradient-world patches we don't need. Their **compute win comes from needing fewer *gradient* updates**; ours would come from needing **fewer *sleeps*** (a sparser cadence than grid-4).
- **What we could borrow or test:** the transferable claim is *"remove the onset shock and you can consolidate less often."* Because our namer already has the shock-removers baked in, the untested hypothesis is that a **prototype-warm-started new class needs a sparser sleep cadence than grid-4** — i.e. our grid-4 may be conservative *because* we already dodge the stability gap. A cadence sweep conditioned on new-class onset (dense only at a genuinely new class, sparse otherwise) could beat fixed grid-4 on cost at equal safety.
- **What contradicts or challenges us:** it says the stability gap is real for replay too, so we must *verify* (via min-ACC, De Lange) that our prototype init actually flattens the inter-sleep trough before claiming grid-4 can be relaxed.

## Follow-on leads
- Van de Ven's "two complementary perspectives" (arXiv 2311.04898) — what-vs-how of the gap.
- Noradrenergic gain-modulation for the stability gap (arXiv 2507.14056) — a plasticity-schedule knob.
