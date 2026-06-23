# Distance-Forward Learning (DF)

*"Enhancing the Forward-Forward Algorithm Towards High-Performance On-Chip Learning," 2024 ([arXiv 2408.14925](https://arxiv.org/html/2408.14925)).*

---

## The problem it was stuck on

Forward-Forward and SCFF are lovely for hardware, but two things nag. First, the **accuracy gap** — on anything past MNIST, FF-family methods trail backprop by a lot. Second, FF was designed as an *algorithm*, not as a thing that has to survive on a **real noisy analog/neuromorphic chip** with 4-bit weights and device mismatch. Nobody had asked: what does FF look like when you actually mean to fab it?

Distance-Forward is the paper that asks exactly that. (Notice the subtitle — *"Towards High-Performance On-Chip Learning."* This is the FF paper written for *our* problem.)

## The one idea that unstuck it

DF starts by re-asking a question everyone else glossed: **what *is* goodness, really?** FF says "energy, `‖h‖²`," and leaves it there. DF answers it geometrically: **goodness is a distance.** Each class gets an *anchor* point in representation space, and a layer's job is to pull a sample's projection *close* to its correct anchor and *far* from wrong ones. FF becomes **distance metric learning** — the same family as face-recognition embeddings, where you train "same person → close, different person → far."

Once you see goodness as distance, three upgrades fall out naturally:

1. **A margin loss instead of FF's log-loss.** Borrowed straight from contrastive/triplet learning: `L = max(m + g_neg − g_pos, 0) + λ·g_neg`. In words: *"don't just separate positive from negative — separate them by at least a margin `m`, then stop pushing."* A margin gives cleaner, better-conditioned separation than the soft log-loss, and it stops the network wasting effort over-separating things that are already far apart.

2. **N-pair negatives.** Instead of contrasting against *one* negative at a time, contrast against *many* at once — which keeps the classes balanced and the signal richer (especially when there are lots of classes).

3. **Letting neighbors talk (DF-O and DF-R).** Pure FF forbids any cross-layer communication, and that myopia is part of the accuracy gap. DF offers two softeners: **DF-O** groups *two adjacent layers* and lets the gradient flow *across the pair* before detaching — a tiny, controlled window of coordination. **DF-R** adds fixed *random feedback* connections (feedback-alignment flavor) so layers can update more in parallel.

## What it achieved

- **MNIST: 99.7%**, **CIFAR-10: 88.2%** — that CIFAR number is a big jump over SCFF's 80.75%, genuinely closing on backprop.
- **Less than 40% of backprop's memory.**
- Explicitly robust to **device noise** (mismatch, photon shot noise, impulse sensor noise) and runs at **4-bit quantization** — i.e. it was stress-tested for silicon, not just for a GPU.

## What it means for us

DF is the closest thing in the literature to *"FF, but you actually intend to build it."* So it's a goldmine — but with **one wire you must not cross.**

**The catch:** DF is **supervised.** Those class anchors *are labels*. DF measures distance-to-the-right-label, so it cannot be our unsupervised cheap brain. If we swapped SCFF for DF wholesale, we'd lose the entire "learns the world for free, no labels" property that the 80/20 split is built on. **Don't replace SCFF with DF.**

**What we raid instead:**

- **The margin loss** — keep it on the bench. If SCFF's log-loss turns out mushy or slow in simulation, the margin form is a drop-in, better-conditioned objective. It pairs especially well with our differential-charging story, where the contrast is the natural quantity.
- **DF-O overlapping blocks** — this is a *second, independent* answer to our "middle layer" question. Where the plasticity-gradient slowdown gives us *stability*, DF-O gives us *coordination*: a published, minimal way to let two layers at a boundary share a gradient without opening a full backward pass. Our middle layer can be exactly this — a two-layer overlap window — rather than a vague blend.
- **The noise-robustness + 4-bit results** are a quiet reassurance: an FF-family method has *already* been shown to survive the kind of analog ugliness Phase 8 will throw at us.
