# Layer-wise Learning Rate Decay (the "slowdown")

*Not one paper but a practice — crystallized as **discriminative fine-tuning** in ULMFiT (Howard & Ruder, 2018) and now standard in BERT/transformer fine-tuning. Plain-English explainer: [the LLRD writeup](https://mbrenndoerfer.com/writing/fine-tuning-learning-rates-llrd-warmup-decay-transformers).*

---

## The problem it was stuck on

You have a big pretrained network that already learned good general features. Now you want to fine-tune it on your specific task. The naive move — hit *every* layer with the same learning rate — quietly wrecks things: the fast updates **smash the general features** the early layers had carefully learned, and you end up worse than if you'd been gentler. The pretraining knowledge evaporates under a uniform learning rate.

## The one idea that unstuck it

**Don't move every layer at the same speed.** Give each layer (or group of layers) its *own* learning rate — "discriminative" or "layer-wise" rates. Then the layers that hold precious, general, widely-depended-on features learn **slowly**, while the layers doing task-specific work learn **fast**.

The intuition the papers use is worth quoting almost directly, because it's *our problem in someone else's words*:

> *If a layer that everything downstream depends on shifts sharply, all the layers above it must relearn how to interpret it — cascading disruption through the whole network.*

So the rule is: **slow down whatever a lot of other things are reading.** Pin the foundation; let the surface adapt. In the standard fine-tuning setting that means a smooth ramp — tiny learning rate at the embedding/early layers, growing toward the task head (often a factor like ×10 per level of depth).

## What it means for us

This is the precedent we were hoping existed for our **middle-layer slowdown / plasticity gradient** — and it does, it's mainstream, and it's used for *exactly* the reason we want it: stop a downstream consumer from breaking when the thing it reads moves too fast.

**But mind the mirror.** Standard LLRD slows the *early* layers, because in fine-tuning the downstream consumer (the task head) sits on *top* and depends on the stable *bottom*. In **our** design the downstream consumer is **GD**, and GD reads the **top of SCFF** (the last `n` layers, via the taps). So we apply the **same principle with the depth axis flipped**: slow the **late** SCFF layers — the interface GD reads — and let the **front** SCFF layers stay fast and plastic to keep discovering structure.

> Same rule — *"slow what the downstream learner reads."* Different geometry — their downstream reads the bottom, ours reads the top.

That's the whole idea, and it lands cleanly on the substrate: "slow learning rate on a layer" is physically just **weaker update coupling / a bigger smoothing capacitor** on those Scaps. **Zero extra state** — no second weight, no copy. Just a slower clock on the layers facing GD.

Two honest notes:

- **It's a heuristic, not a theorem.** The *schedule* (how slow, how steep the ramp) is tuned, not derived. For us that's fine — it's literally the "frozen vs slow vs fast read-layers" experiment cell that sets the number.
- **It's the cheap cousin of [byol.md](byol.md)'s EMA-view.** Both say "let the downstream learner see a slow version of the encoder." LLRD does it by *braking the layer itself* (cheapest, zero extra state). BYOL does it by *holding a separate slow copy* (costs extra capacitors, but lets the live layer stay fast). Start with the brake; reach for the copy only if braking the read-layers slows SCFF's learning too much.
