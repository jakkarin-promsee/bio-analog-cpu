# Budgeted Online Continual Learning by Adaptive Layer Freezing and Frequency-based Sampling
- **Authors / Year / Venue:** Minhyuk Seo, Hyunseo Koh, Jonghyun Choi / 2024 (rev. 2025) / ICLR 2025 (Spotlight)
- **Link:** https://arxiv.org/abs/2410.15143
- **Tier / Topic:** tier1-nearest-neighbors / t1.3 on-device online learning
- **Relevance:** ⭐⭐⭐⭐ — the current (2025) state of budget-honest online CL: a *total-budget* accounting (FLOPs + bytes) and an information-per-cost rule for when NOT to learn.

## TL;DR
Argues online-CL comparisons are unfair unless **total** compute (FLOPs) and **total** memory (bytes — buffer AND model AND optimizer state) are equalized, then wins under that accounting with two levers: **adaptive layer freezing** (don't backprop into lower layers for uninformative batches) and **frequency-based sampling** (retrieve under-seen samples so each gradient step carries more new information). SOTA at matched total budget on CIFAR-10/100, CLEAR-10/100, ImageNet-1K.

## The mechanism (how it actually works)
Budget accounting first: methods that look cheap by "buffer size" often hide cost in model copies, teacher networks, or extra passes — counting bytes and FLOPs *totally* removes the hiding places. Then the levers. (1) Adaptive layer freezing: for each incoming batch, estimate how informative it is (Fisher-information-flavored signal vs cost); for low-information batches, freeze the lower layers and update only the top — the per-batch version of "pay for direction only when the data deserves it." (2) Frequency-based sampling: track how often each stored sample has been rehearsed; preferentially retrieve rarely-seen ones, so the same knowledge is learned in fewer iterations than uniform retrieval. Both levers spend a fixed budget where the information return is highest.

## Key results / claims
- Beats SOTA online-CL methods **within the same total (FLOPs + bytes) budget** on CIFAR-10/100, CLEAR-10/100, ImageNet-1K.
- Shows several published methods lose their edge once their true total cost is counted — the accounting *is* a result.
- Layer freezing driven by batch informativeness retains accuracy while cutting backward FLOPs substantially.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the P8 meter + the gate; the P10 fair-race accounting.
- **Same as us:** the philosophy is the metered 80/20 in digital clothes — an explicit total budget, and a *conditional* refusal to compute gradients when the input isn't worth it (their per-batch freezing ≈ our per-step drift gate; both are "learning is a purchase, not a reflex").
- **Different from us:** their gate is per-batch informativeness inside an always-training loop, ours is a stream-level drift event over a *closed-form* learner; their budget is FLOPs+bytes on digital hardware, no energy or substrate axis; the representation is still trained by backprop.
- **What we could borrow or test:** (1) publish our costs in their currency — a FLOPs+bytes table for OURS vs tuned-ER alongside our pJ meter would let the budgeted-CL community place us without trusting our analog model; (2) frequency-based retrieval for our **sleep** — cbrs balances classes but ignores rehearsal frequency; a seen-count-weighted consolidation over the LUT is a direct, cheap import; (3) their informativeness signal as a second gate input (fire on drift AND expected information).
- **What contradicts or challenges us:** their success shows a *graded*, per-batch economy inside gradient learning can be very strong — our binary fire/no-fire gate is coarse by comparison, and a reviewer can ask why the namer shouldn't have a graded budget too.

## Follow-on leads
- Koh et al. — earlier "i-Blurry" online-CL setup from the same group (task-free streams).
- CLEAR benchmark (Lin et al. 2021) — natural temporal distribution shift; a candidate real-stream arena we haven't used.
- Harun & Kanan — "Overcoming the Stability Gap in Continual Learning" — the transient-forgetting-at-update phenomenon relevant to our worst-point BWT metric.
