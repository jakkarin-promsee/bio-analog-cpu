# Online Coreset Selection for Rehearsal-based Continual Learning (OCS)
- **Authors / Year / Venue:** Jaehong Yoon, Divyam Madaan, Eunho Yang, Sung Ju Hwang / 2022 / ICLR 2022
- **Link:** https://arxiv.org/abs/2106.01085 (fetched)
- **Tier / Topic:** tier2 / t2.3 replay selection & consolidation schedule
- **Relevance:** ⭐⭐⭐⭐ — the tri-criterion refinement of GSS (representativeness + diversity + past-task affinity); the criteria are conceptually what we want at eviction, but all three are computed in **gradient space** — substrate-forbidden as written.

## TL;DR
At every minibatch, score each sample by three gradient-space quantities and keep the coreset that is simultaneously **representative** of the current batch, **diverse** within itself, and **high-affinity** to past tasks. Selecting for past-task affinity directly suppresses forgetting; unlike GSS/bilevel it does not collapse onto dominant classes.

## The mechanism (how it actually works)
Each candidate sample is reduced to its **loss-gradient vector**. Three cosine-similarity scores are formed: (1) **minibatch similarity** — how aligned a sample's gradient is with the mean gradient of its minibatch (representativeness); (2) **sample diversity** — negative average pairwise gradient similarity to other kept samples (spread); (3) **coreset affinity** — gradient similarity to a held-out set of previous-task samples (does keeping this help the past). A weighted sum ranks candidates; the top-k per iteration are stored and replayed. The whole selection lives in gradient space and needs **per-sample gradients**. Borsos et al.'s bilevel coreset is cited as the accurate-but-unscalable alternative OCS replaces with cheap online scoring.

## Key results / claims
Outperforms GSS, reservoir, and bilevel coreset on balanced, **imbalanced**, and **noisy** class-incremental / task-free streams; the diversity + affinity terms are what beat GSS (which over-picks dominant classes). Especially strong when the stream is corrupted or imbalanced — the regime our drift-gated bursty stream lives in.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** bounded-LUT eviction (P9.3 CBRS), the read-side residual / imbalance guard, C=20 (P11).
- **Same as us:** "affinity to past tasks" is exactly the property our sleep needs — keep the samples that most protect old classes. And OCS explicitly targets the **imbalanced** stream, which is our drift-gated bursty regime (why we needed CBRS in the first place).
- **Different from us:** all three criteria are **gradient cosines** → per-sample backprop → off-substrate. Our closed-form namer never computes a sample gradient.
- **What we could borrow or test:** re-express the three criteria in a **gradient-free** surrogate our substrate already has — feature-space representativeness (distance to class prototype, which we store), feature diversity (Mahalanobis spread under the namer covariance), and "affinity" ≈ namer margin/error on the sample (the gate signal). A prototype/feature-space OCS would be a legitimately substrate-native eviction upgrade over pure class-count balancing.
- **What contradicts or challenges us:** its ablation shows plain class-balance (≈CBRS) is beaten by informativeness-aware selection on hard streams — a hint that our CBRS leaves retention on the table at tight caps.

## Follow-on leads
- Borsos et al. 2020 bilevel coreset (the accurate ceiling OCS approximates).
- Feature-space (gradient-free) coreset / k-center greedy (Sener & Savarese 2018) as the substrate-legal cousin.
