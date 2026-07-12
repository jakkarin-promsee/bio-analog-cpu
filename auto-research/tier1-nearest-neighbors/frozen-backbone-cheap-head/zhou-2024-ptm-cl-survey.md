# Continual Learning with Pre-Trained Models: A Survey
- **Authors / Year / Venue:** Da-Wei Zhou, Hai-Long Sun, Jingyi Ning, Han-Jia Ye, De-Chuan Zhan / 2024 / IJCAI 2024 (Survey Track, pp. 8363–8371)
- **Link:** https://arxiv.org/abs/2401.16386
- **Tier / Topic:** tier1 / t1.5 frozen-backbone + cheap-head
- **Relevance:** ⭐⭐⭐☆☆ — the field map: taxonomizes all PTM-CL into three groups and empirically flags that many comparisons are **unfair** (different pretrains, benchmark-pretrain overlap) — the citation for scoping any claim we make against this literature.

## TL;DR
Survey of pretrained-model-based continual learning, categorizing methods into three groups (prompt-based; representation-based, i.e., frozen features + classifier statistics; and model-mixture/ensemble-based — the abstract confirms three groups, the naming here follows the paper's accompanying PILOT toolbox), with a comparative empirical study across SOTA methods. Its running concern is **fairness**: methods differ in pretrained checkpoints, tunable-parameter budgets, and benchmark overlap with the pretrain corpus, so many published deltas do not measure what they claim.

## The mechanism (how it actually works)
As a survey, its "mechanism" is the taxonomy + controlled re-evaluation: hold the pretrained checkpoint and benchmarks fixed, re-run the leading methods from each family (via the LAMDA-PILOT codebase), and compare under a matched protocol. The empirical section repeatedly finds the simple representation-based methods (prototype/statistics heads over frozen features — the SimpleCIL/FSA/RanPAC family) to be far stronger than headline tables implied, and the gaps between elaborate methods to shrink under matched pretrains — echoing Janson-style skepticism from inside the field.

## Key results / claims
- Three-way taxonomy of PTM-CL; representation-based (frozen features + cheap classifier) is established as a co-equal SOTA family, not a baseline.
- Comparisons across papers are frequently confounded by pretrain choice and ImageNet-derived benchmark overlap; matched re-evaluation shrinks or reorders claimed advantages.
- Companion toolbox (LAMDA-PILOT) provides the standardized implementations.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** framing/positioning of the whole draft-6 object against the CL field (the P10/P11 fair-baseline discipline).
- **Same as us:** its fairness program is our P10 methodology (fair, budgeted, tuned baseline; blind verdict shapes) applied field-wide — we can cite it as the norm our validation already follows.
- **Different from us:** everything surveyed presumes the giant pretrain; the survey does not treat the representation's *source* as a variable at all — the axis we live on is absent from the field's own map.
- **What we could borrow or test:** when writing any public comparison, use the survey's taxonomy to place us precisely: we are "representation-based PTM-CL, with the PTM replaced by a stream-grown unsupervised substrate" — one sentence that makes us legible to this audience. Also: benchmark hygiene (their overlap critique) applies to our synthetic home; P11's external arenas are the response to keep front-and-center.
- **What contradicts or challenges us:** the empirical finding that within-family differences shrink under matched conditions warns that our P7 bake-off ordering (RanPAC vs SLDA vs others) may be tighter than it looked — consistent with what we found (3-way tie; SLDA deployed on cost).

## Follow-on leads
- LAMDA-PILOT toolbox (github.com/sun-hailong/LAMDA-PILOT) — if we ever want an external-methods harness for our arenas.
- "Reflecting on the State of Rehearsal-free CL with Pretrained Models" (2406.09384) — the critical-analysis companion.
- "The Future of Continual Learning in the Era of Foundation Models" (2506.03320) — 2025 position paper on where this field goes next.
