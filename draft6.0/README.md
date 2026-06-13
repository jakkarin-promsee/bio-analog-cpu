# Draft 6.0

## How did we get here?

TBH, it's my mistake — I didn't check the main formula of draft 5.0 carefully enough. The worst part I missed is **direction**. Back then I was thinking only about how much loss each neuron should receive — the magnitude of the distribution — while the **sign** of the loss distribution was missing completely. That broke the draft 5.0 model apart: nothing converged, and patching direction in properly would break all my essence rules (the local-learning core this whole architecture stands on).

This is the worst scenario you can think of. Every concept I built before is wrong, and I have to rebuild everything from zero.

If you're reading this `draft6.0/`, know that this time I threw all the previous drafts away. They're left as idea references only — don't read them as the concept.

It cost me a burnout of about 3–4 days, but now I can stand again. The whole week I spent down actually made me see my target clearer. Now I'm back with a completely new plan.

## What will I do now?

### Overview

After the long downfall, I went and researched a lot of ideas for what our "backpropagation" should look like. You can see all of them in `./draft6.0/concept`. The final idea, after 4 days of fully thinking, is:

- I will use **SCFF (Self-Contrastive Forward-Forward)** for most of the model (about 80%). This learning type needs no derivative, no summation chain, no order wall (no waiting for other layers to finish first) — each neuron can update itself without knowing anything about the others. It doesn't even need a label. SCFF converges to the place where `x_pos` and `x_neg` separate clearly, making the final layer of this part a near-perfect classifier.

- But SCFF can't fit a real label. It is only an _unsupervised_ classification of the data shape.

- So for the other ~20%, I will use **full gradient descent** to translate that classification into real labels. Why gradient descent? Because eventually every algorithm ends up paying a computation cost close to full gradient descent anyway — no matter what you choose, in the end you get stuck on direction diffusion. So I pick the one that gives the most accuracy per computation cost. (Think at CPU scale: `ldr` data-load cost + computation cost.)

### Full Detail

#### 1. The Middle Layer

From the overview, you see the model has two parts: SCFF and gradient descent. The problem: SCFF has no label and updates with only a Hebbian-style rule. So if the input shape changes even a bit, the output at SCFF's last layer can swing a lot. The classification stays precise — but its _position_ moves. Which makes the gradient descent sitting on top of it outdated, and it breaks.

So I will fix this with **middle layers** that mix SCFF and gradient descent. I'm not sure about the exact formula yet, but the idea is to blend the two updates:

- Layer n: full SCFF
- Layer n+1: 0.9·SCFF + 0.1·gradient descent
- Layer n+2: 0.8·SCFF + 0.2·gradient descent
- …
- Layer n+s: 0.1·SCFF + 0.9·gradient descent
- Layer m: full gradient descent

The middle layers don't aim to converge. They aim to _smooth the connection_ between the two models — so the output at the last layer doesn't swing so much, and gradient descent can follow its shape.

Not sure yet if this is enough, because SCFF and gradient descent won't train at the same time — e.g. train 64 batches on SCFF only, then switch to gradient descent (more detail in §3, The Learning Mechanism).

#### 2. The Block Concept

Topic 1 describes one unit of SCFF and gradient descent working together:

First layers (SCFF) → middle layers (SCFF + gradient descent mix) → last layers (gradient descent)

Call this a **[Block]**. Each block needs only one delta term from outside to drive its gradient descent — ∂L/∂Block_l, passed down to Block_l−1. But computing the whole network backward to get this delta exactly costs too much. So I approximate: `Block_W = Block_out / Block_in` — treat the whole block like a one-layer linear function with a single approximate weight matrix. (It's not linear. It's just an approximation.)

This drops the backward cost from O(len(layers)) to O(len(blocks)). We get:

Block_1 → Block_2 → … → Block_n

Each block has an unsupervised classifier (SCFF) that can learn at any time from input alone, plus gradient descent right before the block sends its output out — and that gradient descent has a _fixed label_. This makes each block discrete: no matter how much the SCFF inside Block 1 swings, gradient descent pulls the output back to the label shape, so Block 2 still receives similar input.

#### 3. The Learning Mechanism

Now it's time for the real biology-inspired part — the math ends here. From all my research, I think everything above will be able to converge. The worst case is simply: connect all the SCFF together and keep only one gradient descent at the very end (for the case where gradient-descent delay makes the model swing and explode).

The concept I picked: use **local learning (pure SCFF) until the error builds up and hits a threshold, then bring in gradient descent** — the way real brain nerves do it (per research info in 2025).

- If loss < threshold: update **only SCFF** — the unsupervised classification brain. The model keeps getting more precise at classification, and its output keeps swinging and shifting away from the point gradient descent last saw.
- If loss > threshold: update SCFF as normal **+ update gradient descent**, so the gradient-descent part can follow SCFF's output again.

Why gate it like this? Because gradient descent is slow and huge. It costs a lot to compute: a full forward, the half backward (block-approximated), matrix computation, and the weight approximation. SCFF uses only `x_pos` and `x_neg` in a single forward pass (both computed at the same time). At circuit level, SCFF is more efficient in every way.

And the biggest reason: **SCFF is unsupervised** — it tries to recognize _everything_ about the input. The more data it gets, the more classification it can do. Even while the last output is getting worse loss, the inside of the model still holds the data shape it learned. (The only bad case is overfitting, where it learns to recognize all the noise too XD.)

But this gives us a new problem: gradient descent gets **shifted over time**. The single update when loss > threshold helps a bit — but it only reconnects the last-seen data, while the rest of the output range breaks. Example: SCFF keeps shifting over time, and only 10% of the data hits the threshold — so gradient descent now covers only 10% of the new input map (from SCFF).

So my idea is a **"sleep-like mechanism"**: a phase where we train gradient descent full-batch again on the new SCFF map — making gradient descent cover the whole data range, from the past until now, again.

And this creates a new problem too: where do we keep the full batch for the sleep phase? TBH, I don't know either. But I have 2 rough ideas:

- Use SRAM to keep the input/label history like an array list.
- Use another model whose only job is to remember the full history… yeah, it's a real hippocampus. I don't know yet whether it can work, because this model would be used to train the whole prediction model.

## What will we do next?

First, I will use only classification / statistics tasks.

- 1.0. Simulate full SCFF
- 1.1. Simulate full gradient descent

- 2.0. Simulate SCFF + gradient descent
- 2.1. Simulate SCFF + middle layers + gradient descent

- 3.0. Simulate no sleep update
- 3.1. Simulate sleep update with full-batch history (array history)
- 3.2. Simulate sleep update with 20%-batch history (array history)
- 3.3. Simulate sleep update with another model that keeps the history

Then, once the steps above give us a stable init, I will try the **block concept**:

[SCFF + middle + GD] → [SCFF + middle + GD] → [SCFF + middle + GD] → …

Why do I want this? Because gradient descent is **100% direction-distribution compute** — distributing direction is the entire thing it does. Most Hebbian models break on complex tasks exactly because they can't send direction clearly. Putting a GD checkpoint between every block gives us two things:

1. **A fixed-range translation layer at every boundary.** No matter how Block 1 shifts, its output stays in the same range and shape — so the whole model doesn't swing when the first block updates. The only thing that changes is the _precision_ of the output.
2. **Direction chains through the whole model.** The gradient-descent stages connect to each other, so direction information links end-to-end — even though most of the layers are SCFF.

But I'm not sure yet whether these in-between GD stages will hold or break. So: stable init first from the steps above, then we try this.

---

## Where things live in this folder

| Path | What it is |
| ---- | ---------- |
| [`context.md`](context.md) | **the full context dump** — the whole picture (what / why / how / the person). Start here if you're cold. |
| [`idea/main.ideas.v1.md`](idea/main.ideas.v1.md) | **the decision record** — N1–N3 + S1–S8, the live plan (spine committed, numbers pending). |
| [`idea/ideas1.md`](idea/ideas1.md) | the full derivation, told as a story (every part + *why*). |
| [`concept/`](concept/README.md) | survey of learning algorithms — the *options* considered (attribution here is draft-5.1 history). |
| [`ref/`](ref/README.md) | plain-language stories of the papers **behind** the 6.0 design (SCFF, Distance-Forward, BoostResNet, BYOL, LLRD). |
| [`future-ref/`](future-ref/README.md) | the **phase-2** research dossier (21 files) — free-time reading, *not* the line to walk now. |
