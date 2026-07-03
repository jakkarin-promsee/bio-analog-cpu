**Recap:**

Phase 1 tested the SCFF hypothesis, and it worked well — SCFF can enhance the GD flow. Its only problem: a Phase-1 SCFF layer can't pass its work on to the next layer. So the deeper we stack, the less accuracy we get.

Phase 2 was about finding where that problem comes from. The answer: it's SCFF itself.

Phase 3, we tried a lot of things and landed on the final answer: **contrast (InfoNCE, two-mask) + coordination w=2** for the SCFF bulk, plus an all-tap, sleep-consolidated readout.

Phase 4, we tested the hypothesis again, and the result was great. Contrast (InfoNCE, two-mask) *can* pass its work to the next layer — because at w=2, each SCFF neuron also computes goodness for the next layer.

---

**Problem:**

But the problem is still there. Contrast (InfoNCE, two-mask) can stack abstraction layer by layer — yet if the network gets too deep, dead neurons and context decay still show up. In Experiment 3 we found that on the headroom dataset, contrast (InfoNCE, two-mask) keeps stacking abstraction up to layer 4 (depth raises accuracy). After that, more depth *lowers* accuracy.

I'm not sure where this problem comes from. My guess: each SCFF layer is only good for *complex* classification. If the task is too easy, too few neurons fire, so the weights collapse on themselves and lose wiring ("fire together, wire together").

You can see it on the flat dataset — it's designed for a flat task, where 1–2 layers are enough. So SCFF stays active only in the front layers and leaves the later ones dead. The deeper the SCFF stack, the more the context decays.

Back to the headroom dataset: its complexity needs many layers working together, so SCFF can keep stacking accuracy up to layer 4. After that, the task stops flowing forward, and the last layers go dead again.

So the new contrast (InfoNCE, two-mask) solves the *abstraction-passing* problem between layers — but it doesn't solve SCFF *depth decay* yet.

---

**One more detail:**

SCFF → GD write → SCFF → GD write → SCFF

This GD-write step breaks SCFF, because GD moves faster toward a new optimum and destroys the unsupervised SCFF base underneath it. Picture it like this: at batch 1, SCFF gets a "first-generation" view of the data for the label. Then GD destroys the shape of that first generation and pushes it to a second generation — and even though the input is the same, SCFF now sees it as new, different data.

This tells me that whatever sits *between* SCFF layers should also be unsupervised — or at least a slow model that doesn't shift all the labels at once.

---

**Solution:**

Honestly, I don't know what the fix is either. The ideas below are just my own thoughts — no math, no paper references yet.

**1. (Minor) Bypass gate.** Let the first layer's output bypass straight to a deeper layer — e.g. L1 bypasses to L4, L2 bypasses to L5 — while L1 still feeds L2 and L4 still feeds L5. This gives the deep layers enough data to strengthen their wiring. But I don't think it's very sustainable; it's a way to optimize neural activity, not to solve the whole problem.

**2. (Minor) Residual.** Each layer's output becomes a residual between its input and its SCFF output — either `input − SCFF output` or `input + SCFF output`. I haven't done the math to know which one is right yet 😂. We train SCFF only to increase goodness. The core problem is that context can't chain to deep layers, and since `y = f(aw + b)`, a messy late layer destroys the whole input. So the idea is to initialize the SCFF output near zero and let it change the output only when it's confident. That way the input survives to the last layer (`residual ≈ input`), and we don't lose the accuracy we already had.

**3. (Main 1) Change the wiring architecture.** Right now we use a simple linear relation — plain L1 → L2 → L3 → L4, just multiply and pass. That breaks real neural behavior: we have real neural *learning*, but we're missing real *wiring* — so we only get half of Hebbian learning. My idea: each SCFF layer sends its error to a "decider" GD, which decides whether to forward that SCFF's output to the next SCFF layer or not.

This gives us a "lazy" ability — compute as little as we can. How deep we activate depends on the task.

The hard part is building the decider GD. My idea is to split the architecture into: **SCFF brain + per-layer decoder GD + one universal final GD.**

- The SCFF brain has n layers, stacked normally.
- Each per-layer decoder GD wires its SCFF layer to the universal final GD.
- The universal final GD is shared across all SCFF layers.

Workflow:

1. SCFF activates one layer, then the decider GD decides whether to forward to the next layer.
2. Loop that decision until the decider GD says "don't forward."
3. SCFF exits, sends its output to the decoder GD, then on to the universal final GD.
4. If the final output has too much error (above threshold), the decider GD runs a **check loop**: it compares the accuracy of the previous layer and the next layer against the current one, to see whether the current layer is actually the peak. If a neighbour does better, update the decider GD so next time it stops (or forwards) at the better depth. If the current layer is already the highest, do nothing — this SCFF depth is already optimal. This check is the expensive step, so the threshold is really a knob on *how often the model bothers to run it.*
5. Each decoder GD is trained on its specific SCFF layer. We freeze SCFF and the universal final GD, and tune only the middle part per task.
6. The universal final GD is trained while SCFF and the decoder GDs are frozen.
7. **The threshold = average error.** I mashed two cores together before, so here they are split out:

    - **Core 1 — the global threshold decays over training, and it's the model's effort knob.** It starts high and shrinks step by step. The threshold gates the check loop from step 4, so it controls *how much work the model does*: a high threshold rarely fires the check, so SCFF is cheap and free to form itself first; a low threshold fires it often, so the model checks carefully and gets precise at each layer boundary (more compute). As training goes on the avg error falls, the threshold falls with it, and the model shifts from "form freely" to "check carefully." (That's why I picked avg error as the threshold: it drops naturally as the model improves.)
    - **Core 2 — the "danger" signal is how far the error overshoots the threshold.** When a sample's error blows past the threshold by a lot, that's the danger feeling: the bigger the overshoot, the harder the model should learn from that sample. When the error sits near or under the threshold, we're "comfortable" → stay lazy. The concept comes from how humans handle danger: hit real danger and we remember it hard; stay comfortable and we get lazy. 😂😂😂💀

    One risk with Core 1: a little oscillation when the model hits the data limit — accuracy can't improve any further, but the threshold keeps dropping below what's actually reachable.
8. We might also use neuron-activity percentage to decide. E.g. if layer 1's output makes 30% of layer 2 go dead, we stop forwarding layer 1's output to layer 2. Something like that — just an idea to bring in a real neural mechanism. 😂😂😂💀💀

**4. (Main 2) The Hippocampus idea (from the essence).** Maybe the current contrast (InfoNCE, two-mask) SCFF is already right — it's just missing the Hippocampus part. What we're missing now is *loop thinking*, the same concept as in `docs/essence/the-essence.md`:

```
One question, the one I sat with from 1 a.m. to 8 a.m. on milk and no sleep: _how do I think?_

Not "how does a network classify." How do **I** know I'm right? When I work out how much money I owe, when I land the answer in calculus, when I'm sure 1+1=2 — nobody hands me a label. There's a _feeling_. An "I get it." It sits in the same place as tired, or sad. And I wasn't born with it; I learned what correct feels like from my mother and father, the way I learned hot soup is hot. Correctness is a feeling, and the feeling is taught.

So a mind isn't a lookup. It's a loop: hold a little in front of you, call the rest from memory, compare, reject, search again — until the feeling says stop. That's the thing I'm building toward. Something that keeps that loop running its whole life. That keeps learning while it's being used. That carries an essence across its life instead of being born to answer one prompt and end.

IF the question is "This car color is orange or not", the first thing I think isn't any calculation. At first, I try look at the car and think "what is this car color look like?"

- If the apple image appear in my thought first, then I compare the apple color (in my thought) to the car color (in my eyes). And yeah, it's not. So then, next time I think "what is this car color look like?, plus it's not a tone of red apple"
- I loop many memory until I found "Orange fruit" in my thought. That time I get that the car color is so like orange. But the feeling is just "similar", not "sure". So then I can answer it's orange color by cursory, but it more like "Neon Orange" if your ask specifically (I loop thought myself again).

For the math or physic formular too. I think q = mc∆t is right, not because it's a truth. But because my all memory said, this law is correct. it's "make sense".
```

Maybe the threshold I'm looking for is hiding in the Hippocampus part — an "I get it" threshold instead of an average-of-error threshold.

---

**Summary:**

So, as you can see, context decay with depth is the real problem we have to solve. But solving it takes a lot — and I don't know which part to attack first. Until this problem is fixed, we can't optimize anything else yet.

---

**Yapping:** *(just me thinking out loud about the project concept)*

A real neural cell works by spikes. Many synapses wire into the next axon.

The axon acts like a capacitor, waiting for the signal to reach a threshold (with both up-spikes and down-spikes). And there's a distance between each synapse and the axon.

So the axon's received charge = Σ synapseᵢ × distanceᵢ.

If the axon's charge < threshold, it does nothing — `relu(x) = 0` for `x < 0`.
When the axon's charge > threshold, it spikes to the next neuron — `relu(x) = x` for `x ≥ 0`.

But a real neuron uses pulses over many time steps: the axon-capacitor decays, and each synapse has a delay. So the new formula becomes:

axon charge (avg/time) = Σ synapseᵢ(avg/time) × distanceᵢ − decay(avg/time).

It's the same formula as above. The idea: for the same task, the whole network eventually converges. All the pulses and delays average out to a single scale for that task — so a simple, straight formula can stand in for all that pulse activity.

That's why `y = ax + b` with `a = relu(y)` makes sense now.

---

**Yapping (2):** *(more thinking out loud)*

I think this phase is missing something too. Same as Solution 3 — I think our model still lacks the "lazy" part.

The problem is that thinking harder doesn't mean thinking better. It's like designing a house with general relativity: sure, it's more precise, but it's overkill and easy to hallucinate with. Newton's laws — or even just momentum — are enough. 😂😂

But I don't know how to do it yet. I just have some ideas from State Space Models (SSMs) and Mixture of Experts (MoE) — open up SCFF only for the part we actually use. 😂😂
