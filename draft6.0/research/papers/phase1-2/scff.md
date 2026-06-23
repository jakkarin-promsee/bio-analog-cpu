# SCFF — Self-Contrastive Forward-Forward

*Nature Communications, 2025 ([arXiv 2409.11593](https://arxiv.org/abs/2409.11593)). The deep technical file is [../../survey/SCFF.detail.md](../../survey/SCFF.detail.md); this is the story.*

---

## The problem it was stuck on

In 2022 Hinton proposed **Forward-Forward (FF)**: throw away backprop, and instead of one forward pass + one backward pass, do *two forward passes*. One on real data ("positive"), one on fake data ("negative"). Train every layer to get **loud** on the real and **quiet** on the fake. No gradient ever travels backward. Beautiful for hardware — no transpose, no stored activations, every layer learns on its own.

But FF had a splinter in its foot that never came out: **where do the fake examples come from?** Hinton's trick was to take a real image and stamp a *wrong label* into its corner pixels. That "fake" works on MNIST and nowhere harder — and worse, it needs labels, so FF wasn't really the label-free learner it promised to be. The negatives were the weak link in the whole idea.

## The one idea that unstuck it

SCFF's move is almost embarrassingly simple: **stop inventing fakes. Make them out of the data you already have, by pairing.**

- A **positive** is a sample paired *with itself* — "this is one coherent thing."
- A **negative** is a sample paired *with a different sample* — "this is a mixture of two things, not one thing."

That's it. The network learns to answer one question at every layer: *"is what I'm looking at a single coherent thing, or a mash-up?"* Real data is coherent; a blend of two random images is not. No labels are touched — the contrast comes purely from the structure of the data. SCFF turned FF's broken supervised crutch into a clean **unsupervised** learner.

"Goodness" — the thing each layer makes high for positives, low for negatives — is just **energy**: the mean of the squared activations, `G = (1/C)·Σ y²`. A loud layer has high energy. Training pushes positive-energy above a threshold and negative-energy below it.

## The subtlety that matters for *us*

Here's where you need to know one thing about your own notes. The **real paper pairs by concatenation**: it literally stacks the two inputs, `[x_k, x_k]` for positive, `[x_k, x_n]` for negative — so the input *doubles* in size, and there are two weight blocks `W₁, W₂`. The paper then *proves* (Appendix A) that those two blocks converge to be equal, `W₁ = W₂`.

Our [SCFF.detail.md](../../survey/SCFF.detail.md) describes it as **summation** with a single weight and no size growth. **That's not a mistake — it's a smart reformulation, and it's exactly equal to the paper** *because* `W₁ = W₂`:

$$W\cdot[x_k, x_k] \;=\; W_1 x_k + W_2 x_k \;=\; W(2x_k)$$

So "concatenate then apply two equal weights" and "sum then apply one weight" are the *same computation*. We chose the sum form on purpose: it **halves the input lines**, stores **one** weight instead of two, and — this is the big one — it's **what makes mono-forward possible** (each world carries one vector through one shared crossbar, not a doubled concatenation). Just remember to *call it our reformulation* in the writeup, so nobody thinks we misread the paper.

## What it achieved

- **MNIST (MLP): 98.7%** — statistically tied with backprop. On an easy task, label-free local learning loses *nothing*.
- **CIFAR-10 (CNN): 80.75%**, STL-10: 77.3%, Tiny ImageNet: lower.
- It even extended FF to **recurrent nets** (audio, 90.3% on spoken digits).

The pattern: SCFF *matches* backprop when the task is simple, and a **gap opens as the task gets harder**. That gap is the price of locality — each layer optimizes its own myopic goodness with no global signal coordinating the layers.

## What it means for us

SCFF is **the cheap brain — the unsupervised 80%** of draft 6.0. It is the only learning rule we surveyed that is local *and* derivative-free *and* forward-only *and* unsupervised, all at once. That combination is why it can live on the substrate at all.

And that "gap as tasks get harder"? **That gap is the entire reason the GD part exists.** SCFF organizes the world cheaply; it can't coordinate across layers toward a label. So we don't ask it to — we bolt the precise GD brain on top to do exactly the coordination SCFF gives up. Knowing *where* SCFF stops is knowing where our 20% has to start.
