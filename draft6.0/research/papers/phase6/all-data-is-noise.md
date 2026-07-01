# All data is noise — can the cheap brain learn when it never sees clean truth?

*Noise2Noise (Lehtinen et al., ICML 2018, [1803.04189](https://arxiv.org/abs/1803.04189)); **Self-Purified Replay**
(Kim et al., ICCV 2021, [2110.07735](https://arxiv.org/abs/2110.07735)); CNLL ([2204.09881](https://arxiv.org/abs/2204.09881));
Co-learning with self-supervision ([2108.04063](https://arxiv.org/abs/2108.04063)); contaminated/blurry stream
([2203.15355](https://arxiv.org/abs/2203.15355)).*

---

## The problem it answers — the author's Phase-6 insight (Door B)

Our model is **online and lifelong**: every datum is a single noisy real-world sample the hippocampus banks into the LUT
to replay at sleep. **It never sees a clean, curated "truth" set — its entire world is noisy samples**, one at a time,
out of distribution, never i.i.d. So the existential question isn't only "tolerate a noisy *weight*" (Door A) — it's:
**is a stable class direction even *learnable* from a stream where every single example is corrupted and the clean signal
is never shown?**

## The one idea that unstuck it

**Noise2Noise.** You can learn the clean signal from **only pairs of independently-corrupted observations — no clean
ground truth at all** — provided the noise is **zero-mean / unbiased**: the minimizer of a regression loss against a
*noisy* target converges, in expectation, to the *same* estimator as clean-target supervision. The network "cannot learn
the random noise, so falls back to the underlying clean structure." **Two honest qualifiers the critic pass forced:**
(i) the condition is *equal conditional expectation*, which is **zero-mean only for an L2 loss** (for L1 it's the median,
L0 the mode); (ii) our InfoNCE is **not** an L2-to-a-target regression, so **the contrastive transfer is a suggestive
analogy — a hypothesis P6.4 tests, not Lehtinen's theorem.** With those held: **for zero-mean corruption, clean is
recoverable-in-principle from only-noisy** — the cheap brain is not doomed by never seeing truth, and P6.4 measures how
much survives at finite stream length.

The recurring caveat returns, a fourth face of the same enemy: **zero-mean only.** Structured / directional (biased)
noise does *not* average out and does *not* vanish under Noise2Noise. So the hard residual of Door B is identical to the
hard residual of Door A — **one enemy (directional mismatch), three faces** (survives auto-zero, survives replay
averaging, survives N2N). That convergence is reassuring: Phase 6 has *one* crux to beat, not three.

Two mechanisms we **already have** push toward the zero-mean-recoverable side for free:
- **Replay aggregation** (design §3.4): the LUT prototype is a *mean* over many noisy samples → √N suppression of
  zero-mean noise.
- **Contrastive Noise2Noise** ([`noise-as-augmentation.md`](noise-as-augmentation.md)): pulling two *noisy* views
  together is N2N in representation space — robustness without any clean reference.

## The correction the research forced — averaging is not enough; you need *purity*

Design §3.4 said "the LUT mean denoises Door B." **Self-Purified Replay (2110.07735) shows that's incomplete:** *"the
purity of the replay buffer is crucial."* A naive buffer accumulates corrupted/mislabeled samples and the mean is pulled
off; their **Self-Centered Filter** (centrality-based) keeps a *pure* buffer, and — the gift to us — *"forgetting can be
mitigated even with noisy labels via self-supervised learning."* That is our exact loop (SCFF = self-supervised; LUT =
the buffer; sleep = replay) validated under noise. The small-loss / co-teaching / **co-learning** ([2108.04063]) line says
the same from another angle: the **self-supervised (feature) signal is the noise-robust half**, the supervised (label)
signal the fragile one — keep the base unsupervised.

## What it means for us

- **Door B is learnable for the zero-mean part — and partly for free** (replay mean + contrastive N2N). The cheap brain
  *can* learn from an all-noisy stream; this is not the wall it first looked like.
- **Add buffer *purity* to the LUT design** — a Self-Centered / small-loss filter on what the hippocampus keeps, not just
  aggregation. This is a **Phase-6 ↔ Phase-9 seam**: noise-robustness and maintenance share the same buffer-hygiene knob.
- **The hard residual is again structured/directional noise** (non-zero-mean) — the same crux as Door A, so Phase 6's
  directional probe tests *both doors at once.*
- **Confirms design §1:** SCFF being unsupervised removes the *label*-noise door entirely for the base; the live doors
  are input corruption, stream ordering, and buffer purity — all of which the existing architecture is half-built to
  handle.
