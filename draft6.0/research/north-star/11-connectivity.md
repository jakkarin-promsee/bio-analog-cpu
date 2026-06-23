# 11 — Local input + mixing: "can each block see only a slice?"

> Your worry, restated: each Ganglion sees a *slice* of the input (dims 0–20, 20–40, …), produces a slice, and a "translate clip" periodically **sums everything back** so information can cross blocks. Three questions: **is it efficient? does it break gradient descent? is there a better way than the dense mixing clip?** The answers, in order: **yes (hugely), no (it gets easier), and yes (much better).** Because what you described is one of the most successful patterns in deep learning, and it has names.

---

## Your scheme has a name: grouped / depthwise-separable convolution

*Group conv: Krizhevsky (AlexNet), 2012; ResNeXt, Xie et al., 2017. Depthwise-separable: Chollet (Xception), 2017; Howard et al. (MobileNet), 2017.*

This is the keystone — read it twice. A **grouped convolution** does *exactly* your scheme: split the input channels into `g` groups, give each group its **own** block of weights that sees **only** that group, and process them independently. Your "input 100 → 5 Ganglia of 20 → 5 outputs of 20" **is a grouped layer with g=5.** A **depthwise-separable convolution** is the extreme case (each group = 1 channel) plus your translate clip: it splits one normal layer into

- a **depthwise** step — local processing, each channel/group on its own (your **Ganglion**), then
- a **pointwise (1×1)** step — a small layer that **mixes across all channels** (your **translate clip**).

So your "Ganglion ALU (n→m, l layers, local) + translate clip (n→1, mixing)" is **literally depthwise-separable convolution.** This is not a fringe idea — it is the core of **MobileNet** and **Xception**, the architectures that made deep learning run on phones. You arrived at the single most important efficiency primitive in modern vision from pure circuit reasoning. 🗿

**For us:** your instinct is not only valid, it's *state-of-the-art-efficient*. The mapping is exact: local block = depthwise/grouped, translate clip = pointwise mix. Everything below is "how to do the mix cheaply" and "what it costs."

---

## How much does it help? (a lot) — the efficiency math

A normal dense layer connecting `n` inputs to `m` outputs costs `n·m` weights (and that many multiplies). Split into `g` groups and each group is `(n/g)·(m/g)`, times `g` groups = **`n·m/g`** — a **g× reduction** in weights and compute for that layer. With `g=5`, that's 5× cheaper. Depthwise-separable does even better: the depthwise part is almost free (local), and only the small pointwise mix costs `n·m`, so the *spatial* work is decoupled from the *mixing* work. MobileNet uses this to cut compute ~**8–9×** versus a normal CNN for only **~1%** accuracy loss.

**For us, on analog:** the win is *physical*. A full dense crossbar for `n→m` needs `n·m` devices/charge-paths (the area you're worried about, `12-dataflow.md`). A grouped crossbar needs `n·m/g` — **g× smaller crossbar, g× fewer charge paths.** Your block-local scheme is *the* way to shrink the crossbar without going fully time-multiplexed. The locality you proposed for circuit reasons is exactly the locality that buys efficiency in ML.

---

## Does it break gradient descent? No — it makes credit *local* (easier for you)

This is the question that should reassure you most. A grouped/block-diagonal layer is **still just a linear map with a sparse (block-diagonal) weight matrix.** Backprop through it is completely standard — the gradient is *also* block-diagonal: each block's gradient depends **only on its own slice** of input and output. Nothing about learning gets harder; you simply don't compute the cross-block terms that are zero anyway.

**For us this is a gift, not a cost.** Your whole substrate problem is that global credit assignment is expensive (the draft-5 wall). **Block-local connectivity makes credit assignment block-local** — each Ganglion's update needs only its own slice, computed in parallel, no cross-block routing. The *only* place cross-block credit must flow is **through the translate clip**, which is small. So locality doesn't fight your learning rule (SCFF/GD) — it *aligns* with it: local compute, local credit, with mixing as the one place global information passes. This is why local connectivity is *friendlier* to on-chip learning than a dense layer, not harder.

---

## The one rule you must not break: you MUST mix

*This is the theoretical catch, and it's important.* If the groups **never** mix, your 5 Ganglia are **5 completely independent networks** — input dim 7 can *never* influence output dim 80. The network factorizes, and it provably **cannot learn any function that couples across groups** (most real functions). So the translate clip is **not optional decoration — it's mandatory**, and *how often* and *how cheaply* you mix is the central design knob. ShuffleNet's authors put it bluntly: "pure group convolution blocks information flow between groups." Everything below is how to pay for the mixing without it dominating.

---

## The "better way" you were hoping for — yes, and it's beautiful

You guessed the translate clip might be a dense `n→1`-per-output mix (expensive: `n` charge-times per output, `n²` total). **There are three much cheaper ways to mix, in increasing cleverness:**

### 1. Channel shuffle — mix by *permutation*, nearly free
*ShuffleNet: Zhang et al., 2017 ([arXiv 1707.01083](https://arxiv.org/abs/1707.01083)).*

Instead of a dense mixing layer, just **rearrange (permute) the channels** between grouped layers — send output-channel 1 of every group into group 1 of the next layer, channel 2 into group 2, etc. (round-robin). A permutation is **free** (it's just wiring — and on your chip, *literally just routing*, no compute). After a couple of grouped layers + shuffles, information has **diffused across all groups** even though no single layer ever did a dense mix. Mixing emerges from *cheap routing + depth*, not from an expensive layer.

**For us:** this is the cheapest possible translate clip — **a fixed permutation of wires.** On analog hardware a permutation is *free routing* (no charging, no ALU). Stack a few grouped Ganglia with shuffles between them and information crosses the whole input over 2–3 layers, at the cost of *zero* extra compute. This is almost certainly your best first answer: **don't build a dense mixing clip; shuffle and stack.**

### 2. Butterfly / Monarch matrices — global mixing in log(n) stages (the FFT trick)
*Butterfly: Dao et al., 2019; Monarch: Dao et al., ICML 2022 ([arXiv 2204.00595](https://arxiv.org/abs/2204.00595)).*

The deep answer. The Fast Fourier Transform mixes `n` inputs all-to-all not in one `n²` step but in **`log₂(n)` stages of tiny 2-input mixes** — `O(n log n)` total. **Butterfly matrices** generalize this: any "fast transform" (and, it turns out, a huge class of useful dense matrices) factorizes into `log(n)` **sparse** stages. **Monarch matrices** make it hardware-practical: a dense matrix ≈ **(block-diagonal) × (permutation) × (block-diagonal)** — which is *your exact scheme* (local blocks + a shuffle), applied **recursively**. So the efficient mixing layer is *itself* built from small local blocks and permutations.

**For us:** this is the rigorous "better way." Instead of one `100→100` dense translate clip (`100²` charge-paths), use a **butterfly of ~`log₂(100)≈7` stages of tiny 2-wide mixes + shuffles** — reaching true all-to-all mixing at `O(n log n)≈700` instead of `O(n²)=10,000`, a **~14× saving** that grows with `n`. And Monarch tells you the structure to build: *your Ganglion-block + shuffle, stacked log(n) deep, is provably near-dense in expressivity.* Your intuition and the optimal structure are the same shape — you just stack it `log(n)` deep instead of doing one big mix.

### 3. Mixture-of-Experts routing — only mix the *relevant* blocks
*Switch Transformer: Fedus et al., 2021 ([arXiv 2101.03961](https://arxiv.org/abs/2101.03961)).*

The conditional answer. A small **router** decides which few blocks (experts) each input should go to, and only those fire. Capacity grows with the number of experts, but **compute stays fixed** because only `k` of them activate per input.

**For us:** this is your **sparse** substrate property as a connectivity strategy — most Ganglia dormant (no charge cycles), a cheap router lighting only the relevant few. It composes with grouping: route to a few groups, mix those. Hold it for when the model is big and most blocks are irrelevant per input.

---

## And the validation that "mix one way, then the other" is a whole architecture

*MLP-Mixer: Tolstikhin et al., 2021 ([arXiv 2105.01601](https://arxiv.org/abs/2105.01601)).*

A reassurance that your *pattern* — alternate "process within a slice" and "mix across slices" — is sufficient on its own. MLP-Mixer drops convolution and attention entirely and just **interleaves a token-mixing MLP (mix across positions) and a channel-mixing MLP (mix across features)**. Two kinds of mixing, alternated, is a *complete* architecture, competitive with the fancy stuff, at **linear** cost.

**For us:** your "Ganglion (process slice) → clip (mix slices) → Ganglion → clip …" is exactly the Mixer pattern. It says the structure you proposed is not a compromise — *alternating local-process and cross-mix is a known-sufficient way to build a whole network.* You're not giving anything up.

---

## The shape of the answer (this file)

Your block-local scheme is **grouped / depthwise-separable convolution** — the foundation of efficient deep learning, not a student's hack. **Efficiency:** a `g×` reduction in weights/compute *and* crossbar area; ~1% accuracy cost *if you mix*. **Gradient descent:** not broken — block-diagonal gradients are *block-local*, which makes on-chip credit assignment **easier**, with the translate clip as the one place cross-block credit flows. **The mandatory rule:** you *must* mix or the blocks become independent networks. **The better way you wanted:** don't build a dense `n→1`-per-output clip (`O(n²)`); instead **shuffle wires (free) + stack** (ShuffleNet), or mix in **log(n) butterfly/Monarch stages** (`O(n log n)`, and Monarch = your block+shuffle made optimal), or **route to only the relevant blocks** (MoE). Your intuition and the state of the art are the same shape; the refinement is *mix shallowly and often via cheap routing, not deeply and densely all at once.*
