# Continual Learning on Noisy Data Streams via Self-Purified Replay (SPR)
- **Authors / Year / Venue:** Chris Dongjoo Kim, Jinseo Jeong, Sangwoo Moon, Gunhee Kim / 2021 / ICCV 2021
- **Link:** https://arxiv.org/abs/2110.07735
- **Tier / Topic:** tier2-component-optimization / t2.5 noise-robust representation (the label-noise-robust-CL slot; ESMER itself is already carded in t1.4)
- **Relevance:** ⭐⭐⭐☆☆ — the published, heavier-artillery version of our P6.4 PurityFilter: keep the replay buffer clean when the *stream's labels* are noisy, via self-supervision + graph centrality. The reference point for the noise level at which purity machinery starts paying.

## TL;DR
SPR tackles continual learning when the incoming stream has wrong labels — the regime where replay is poisoned by its own memory. Two mechanisms: *Self-Replay* trains the representation with self-supervised learning (label-free, so mislabeled samples can't inject wrong signal into the features), and a *Self-Centered filter* admits into the replay buffer only samples that are central in a stochastic similarity-graph ensemble — structurally "typical" examples, which are overwhelmingly the correctly-labeled ones.

## The mechanism (how it actually works)
The story: a wrong label can only hurt you through the loss that consumes it — so (1) push representation learning onto a self-supervised objective that never reads labels (the noise becomes inert for the features), and (2) before a sample earns a buffer slot, test not its *label* but its *geometry*: build kNN similarity graphs over candidate features under stochastic perturbations (an ensemble of graphs), score each sample's centrality, and keep the consistently-central ones. Mislabeled samples sit off their claimed cluster's core, so centrality filters them without ever checking the label directly. The purified buffer then supports supervised consolidation.

## Key results / claims
On MNIST/CIFAR-10/CIFAR-100 with symmetric/asymmetric synthetic noise and WebVision's real crowd-noise, SPR substantially beats stacked SOTA combinations of continual-learning + noisy-label methods; the buffer stays highly pure even from heavily corrupted streams. First framework to address forgetting + label noise jointly (2021); ESMER (ICLR 2023, carded in t1.4) is the lighter error-EMA descendant.

## How it relates to us
- **Organ / phase touched:** the hippocampus LUT / CBRS buffer (P9.3); Door B (all-data-is-noise, P6.4); the P8 error-EMA gate.
- **Same as us:** the architecture is spookily parallel — a label-free representation learner (their SSL ≈ our SCFF: both make features label-noise-inert by construction) + a curated episodic memory feeding consolidation (their purified buffer ≈ our LUT feeding sleep). Their premise "wrong labels only hurt through the consumer" is why our bulk is already immune and only the namer/LUT path is exposed.
- **Different from us:** P6.4 measured purity machinery at our noise level and found it ≈ naive averaging — *not needed*; SPR operates at much harsher noise (real web labels, high symmetric rates) where it pays. Their centrality ensemble is far heavier than our purity filter (graph ensembles vs a distance test). Also their noise is on *labels*; P6's was on *inputs* — the LUT admission problem is the shared surface.
- **What we could borrow or test:** the cheap ESMER-flavored middle before full SPR: admission to the LUT weighted by the error-EMA the gate already maintains (low-surprise samples admitted, high-surprise quarantined until confirmed) — closed-form, no extra pass, reuses existing state. Mark SPR's centrality filter as the named escalation if a future arena (web-labeled streams) pushes noise past where P6.4's null holds.
- **What contradicts or challenges us:** SPR implies our P6.4 "purity not needed" is a *regime statement*, not a theorem — the honest scope line for any claim about Door B: at WebVision-grade label noise, untreated admission would poison the LUT and sleep would consolidate the poison.

## Follow-on leads
- ESMER (t1.4 card) — error-EMA modulation + error-sensitive reservoir; the lightweight sibling that plugs into our gate directly.
- CNLL / noisy-label online CL follow-ups (2022–2024) — cheaper purity scores for streaming admission.
- Centrality-as-admission for prototype memories (graph test before a LUT write) — scaled-down candidate if a real arena demands it.
