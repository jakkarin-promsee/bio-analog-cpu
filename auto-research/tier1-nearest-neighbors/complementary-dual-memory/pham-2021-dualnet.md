# DualNet: Continual Learning, Fast and Slow
- **Authors / Year / Venue:** Quang Pham, Chenghao Liu, Steven C. H. Hoi / 2021 / NeurIPS 2021
- **Link:** https://arxiv.org/abs/2110.00175 (fetched)
- **Tier / Topic:** tier1 / t1.4 complementary dual-memory
- **Relevance:** ⭐⭐⭐⭐ — the closest *architectural* fast/slow split in the CL literature: a slow **self-supervised** representation learner + a fast supervised adapter. It is the mainstream version of exactly our "unsupervised bulk + supervised namer" division — and its differences from us are the sharpest way to state what's ours.

## TL;DR
DualNet has two networks. The **slow learner** trains a general representation by a **self-supervised (SSL) objective** (Barlow-Twins-style) on samples drawn from memory — no labels. The **fast learner** is a small per-task network that *adapts* the slow representation for the current labeled task and does the actual prediction. Crucially, the supervised loss backprops through **both** learners, so labels still shape the slow net. It beats prior CL methods "by a large margin" on CORE50 and miniImageNet.

## The mechanism (how it actually works)
Two systems, meant to map onto neocortex (slow) and hippocampus (fast):
- **Slow learner (representation):** a backbone trained continuously with an SSL loss (feature decorrelation / redundancy reduction) over a replay memory. This is label-free and task-agnostic — it just tries to build good general features from whatever streams past, interleaved with buffered old data so the representation doesn't collapse onto the newest task.
- **Fast learner (adaptation):** given labeled data, a lightweight module transforms the slow features (channel-wise modulation / a small adapter) and predicts. It learns fast, per task.

The two are trained together: when a labeled batch arrives, the supervised loss flows through the fast adapter **and into the slow backbone**, while asynchronously the slow net keeps doing SSL on memory. So "slow" and "fast" here are two coupled networks trained by the *same* backprop, differing in objective (SSL vs supervised) and update rate, not in learning algorithm.

## Key results / claims
- Outperforms SOTA (including DER, ER variants) on CORE50 and Split-miniImageNet online CL by a large margin.
- The SSL slow learner is the load-bearing piece: general features learned label-free transfer across tasks and resist forgetting better than a purely supervised backbone.
- Both learners can be trained synchronously; the design is task-boundary-agnostic in the online setting.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk (the slow unsupervised representation) · namer (the fast supervised reader) · the 80/20 split itself.
- **Same as us:** the *division of labor is our division of labor* — a **label-free representation learner does the bulk of the work**, and a **small supervised module puts task labels on top**. DualNet is the mainstream-ML statement of our 80/20 thesis, and it independently confirms that the slow part should be **self-supervised** (their SSL ≈ our SCFF contrastive objective) and that this is what buys continual robustness.
- **Different from us:** three hard differences. (1) **Their slow net still learns from labels** — the supervised loss backprops into the backbone; ours is a **strictly frozen forward-only cortex** that never sees a gradient or a label (SCFF is local + contrastive only). (2) **Their fast learner is a trained network** (an SGD adapter); ours is a **closed-form namer** (no gradient) plus a **non-parametric LUT** that isn't a predictor at all. (3) They train by end-to-end backprop through both systems; our whole point is that no backward pass ever crosses the cortex (the P2.5 forward-leak wall). So DualNet is "two SGD nets, one SSL one supervised"; we are "one frozen local-rule cortex + one analytic head + one exemplar service."
- **What we could borrow or test:** DualNet's **feature-modulation adapter** — the fast learner *modulates* (channel-wise scales) the slow features rather than reading them linearly. Our namer reads taps linearly (per-depth heads); a cheap closed-form *gain* on tap channels (a diagonal re-weighting fit at sleep) is a lightweight analog of their adapter and could recover some of the expressivity we give up by forbidding backprop into the bulk. Also: their result that **SSL-slow > supervised-slow for transfer** is direct external support for keeping the cortex label-free.
- **What contradicts or challenges us:** DualNet gets a real accuracy edge *because* labels reach the backbone (fast+slow co-adapt). That is precisely the channel we forbid. It sets an honest ceiling: a system that lets a little supervision into the representation may out-accuracy us on static difficulty — consistent with our own P4/P10 finding that we trail on static accuracy. It challenges "never write the bulk" as a *free* choice; it's a real accuracy cost we pay for the substrate/safety win.

## Follow-on leads
- Barlow Twins (Zbontar 2021) — the SSL objective DualNet uses; compare to our InfoNCE-contrastive SCFF.
- Fast-and-slow *weights* (Ba et al. 2016, already in north-star/1-memory) — the "fast timescale in the weights" alternative to a second network.
- CLS-ER (carded) — the weight-EMA version of the same fast/slow idea, no second objective.
