# Expandable Subspace Ensemble for Pre-Trained Model-Based Class-Incremental Learning (EASE)
- **Authors / Year / Venue:** Da-Wei Zhou, Hai-Long Sun, Han-Jia Ye, De-Chuan Zhan / 2024 / CVPR 2024
- **Link:** https://arxiv.org/abs/2403.12030
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐☆☆ — the expansion pole of the paradigm (one adapter per task), and its prototype-complement trick is a published cousin of our P9.4 proto-reanchor.

## TL;DR
EASE never writes the pretrained trunk *or* old adapters: each new task gets its own lightweight adapter, spanning a new task-specific feature subspace; classification happens jointly across all subspaces. The catch — old classes have no features in new subspaces — is solved by a **semantic-guided prototype complement**: old-class prototypes are *reconstructed* in new subspaces from class-similarity structure, with no old instances stored. SOTA on seven benchmarks at publication.

## The mechanism (how it actually works)
Freeze the PTM. For task t, train adapter A_t (bottleneck modules on the frozen trunk) on task-t data only — old adapters and trunk untouched, so nothing can forget. Inference concatenates features from all adapters (an ensemble of subspaces) and scores classes by prototypes. The hole: class c from task 1 has a prototype in subspace 1, but none in subspace t>1. Repair by algebra, not replay: in any subspace both old and new classes can be *related* via the class-similarity matrix computed where they co-exist; reconstruct the missing old-class prototype in the new subspace as a similarity-weighted combination of new-class prototypes there (semantic guidance: classes similar in one space stay similar in another). A reweighting step then balances subspace contributions.

## Key results / claims
- SOTA over prior PTM-CL (including APER, CODA-Prompt) on seven CIL benchmarks (CIFAR-100, ImageNet-R/A, ObjectNet, OmniBenchmark, VTAB…).
- Constant per-task cost (one small adapter), no exemplars, no trunk writes.
- Demonstrates prototype *reconstruction across representation changes* works via similarity structure alone.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** P9.4 proto-reanchor (sleep recovering stale prototypes); hippocampus-LUT geometry; the namer.
- **Same as us:** the write-protection philosophy taken to its limit — *nothing* trained is ever revisited; growth happens by adding, classification by prototypes. Their core problem (prototypes go stale when the feature space moves) is literally our P9 problem (bulk rotates → namer frame stales), and both of us repaired it read-side without replaying raw data.
- **Different from us:** their representation *fragments* — one subspace per task, cost growing linearly in tasks (hardware-hostile: each adapter is new silicon/weights); our bulk is a single shared substrate that rotates in place. Their reconstruction leans on rich semantic similarity from the pretrain; our proto-reanchor re-derives prototypes from the live stream + LUT at sleep.
- **What we could borrow or test:** the **similarity-weighted prototype reconstruction** — at sleep, classes absent from the recent stream currently keep stale prototypes; reconstructing them from their old-frame similarity to *recently re-anchored* classes (one matrix multiply, closed-form) could patch exactly the P10 REV-staircase staleness mechanism (the namer frame going stale between sleeps for unseen-lately classes). This is the most concrete borrowable mechanism in this topic.
- **What contradicts or challenges us:** the linear-growth design is the anti-thesis of a fixed-silicon substrate — if the field's best PTM-CL accuracy requires capacity that grows with tasks, a fixed-capacity chip must show its accuracy *plateau* degrades gracefully with task count instead (our C=20 retention crossover result is the start of that answer; a task-count-scaling rung would finish it).

## Follow-on leads
- MOS (Zhou group, 2024/25) — model-surgery successor merging adapters.
- "Semantically-Shifted Incremental Adapter-Tuning" (2403.19979) — adapter-CL with shift compensation.
- Drift-compensation line for exemplar-free CIL (feature-drift estimation → prototype correction) — the gradient-world mirror of proto-reanchor.
