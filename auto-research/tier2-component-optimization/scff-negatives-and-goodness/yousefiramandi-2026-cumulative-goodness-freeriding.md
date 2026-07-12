# Cumulative-Goodness Free-Riding in Forward-Forward Networks: Real, Repairable, but Not Accuracy-Dominant
- **Authors / Year / Venue:** Amirhossein Yousefiramandi / 2026 / arXiv
- **Link:** https://arxiv.org/abs/2605.06240
- **Tier / Topic:** tier2-component-optimization / t2.1 SCFF negatives & goodness
- **Relevance:** ⭐⭐⭐⭐ — names and formalizes the failure mode our cross-layer coordination window is most exposed to: when layers share/accumulate goodness, later layers can stop learning.

## TL;DR
In cumulative-goodness FF variants (where a block's objective includes goodness accumulated by earlier blocks), later layers **free-ride**: the class-discrimination gradient reaching block *d* **decays exponentially** with the positive margin already accumulated upstream. Three local remedies (per-block, hardness-gated, depth-scaled) restore per-layer separation 4×–45× in deep layers — but accuracy moves <1 point. Verdict: real, repairable, **not** the accuracy bottleneck.

## The mechanism (how it actually works)
The story: under a softplus FF criterion on *cumulative* goodness, once the running sum of margins from earlier blocks is comfortably positive, the softplus saturates — the loss is already "solved" from block *d*'s point of view, so the gradient that would teach block *d* its own separation shrinks like e^(−accumulated margin). Early layers do the work; late layers coast on inherited separation and learn almost nothing task-specific. The remedies are all local re-normalizations of the objective: **per-block** (each block sees only its own margin — drop the accumulation), **hardness-gated** (only samples still hard *at this depth* contribute gradient), and **depth-scaled** (rescale the criterion by depth so saturation is deferred). All three revive deep-layer separation statistics dramatically. The sting in the tail: on CIFAR-10/100 and Tiny ImageNet, reviving deep layers barely changes accuracy — so free-riding is an optimization pathology, not the ceiling.

## Key results / claims
- Formal claim: class-discrimination gradient at block *d* decays exponentially in the upstream accumulated positive margin (softplus FF).
- Remedies recover 4×–45× on layer-separation measures in deeper layers.
- Accuracy change <1 pp for non-degenerate training — free-riding is real but not accuracy-dominant on these benchmarks.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk — specifically the **cross-layer coordination window (w≥2)** adopted in P3 and kept in P5 (w2, temp 0.2).
- **Same as us:** our window makes a layer's objective depend on neighboring layers' representations — the same coupling family in which free-riding lives. Our P3.1 observation that w1 is "myopic" and larger windows help is the *good* face of the same coin.
- **Different from us:** our contrast is InfoNCE over windowed representations, not softplus-on-cumulative-goodness; InfoNCE's log-softmax does not saturate the same way — but a *shared* denominator across a window can still let a layer's gradient shrink when neighbors already separate the batch.
- **What we could borrow or test:** their diagnostic, verbatim: measure **per-layer selectivity gain conditioned on upstream margin** in our w2/w4 stacks — do our deep layers still learn when early layers already separate? We have the probes (P3/P5 per-layer selectivity) but never conditioned them this way. If free-riding shows, the **hardness-gated** remedy is substrate-cheap (a per-sample gate on an already-computed similarity — one comparator).
- **What contradicts or challenges us:** their "repair helps separation but not accuracy" result cautions against spending a phase on this even if we find the signature — the fix may be hygiene, not headline.

## Follow-on leads
- Whether InfoNCE-with-shared-window has a provable analogue of the exponential decay (theory gap — no paper found).
- Connection to DeeperForward / depth-scaling tricks in the FF-scaling literature.
