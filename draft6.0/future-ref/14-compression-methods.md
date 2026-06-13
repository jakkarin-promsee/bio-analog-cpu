# 14 — How to actually compress (methods, your two mechanisms, and the on-chip stakes)

> `13-compression.md` said *why* compression is possible (learning **is** compression; the task is tiny; the slack is real and shareable). This file is *how* — the concrete, trustable methods — plus a direct mapping of **your two mechanisms** (the cross-layer "expand range" layer and the "clipping trigger"), and why this is **existential**, not optional, for a resident-weight chip.

---

## The stakes: for you, compression is survival, not optimization

For a GPU model, compression is a nice-to-have (smaller download, faster inference). For **your chip it is the whole game**: resident-weight means **every weight must physically fit on silicon and never leave.** If the model doesn't compress, it doesn't fit, and the architecture doesn't exist. You said it: "now we only do compression in software." The goal is **structural** compression — the network is *born* small because its *form* (sparsity, low-rank, sharing, superposition) is compressive — not a big network squeezed afterward. The methods below are the menu, ordered from "squeeze after" to "born small."

---

## Pruning / Deep Compression — remove the slack (the lottery ticket, harvested)

*Han, Mao & Dally, ICLR 2016 ([arXiv 1510.00149](https://arxiv.org/abs/1510.00149)); origins: LeCun, "Optimal Brain Damage," 1989.*

The classic three-stage pipeline, and the proof that the slack from `13` is real and removable: **(1) prune** the unimportant connections (9–13× fewer), **(2) quantize** the survivors and **share weights** (32-bit → 5-bit), **(3) Huffman-code** the result. Total: **35–49× smaller with no accuracy loss** (AlexNet 240 MB → 6.9 MB). It *harvests* the lottery-ticket slack.

**For us:** the *idea* transfers, the *mechanism* changes. On analog you don't "delete a connection" cleanly, but you have the native equivalents: **pruning = let an unused Scap's weight decay to zero and reclaim its charge-path** (your tunable leak already does this); **quantization/weight-sharing = many Scaps reference one stored value** (your refill-SRAM already shares a reference). So Deep Compression maps onto controls you *already built*. The lesson: build the **prune-and-consolidate** step into sleep — after learning over-provisioned, decay the slack and free it. (Honest caveat: pruning to a fixed sparse mask fights continual learning; pair with `5-continual.md` so freed capacity goes to *new* tasks, not stays dead.)

---

## Knowledge Distillation — compress the *capability*, not the weights

*Hinton, Vinyals & Dean, 2015 ([arXiv 1503.02531](https://arxiv.org/abs/1503.02531)).*

The most conceptually important method here. Instead of shrinking a network's *weights*, train a **small "student"** to mimic a **big "teacher's"** *soft outputs* — and the magic is in the **"dark knowledge"**: the teacher's *wrong* answers (it says "7" but with 8% on "1") encode the **relationships between classes**, which carry far more information than a hard label. The student learns the teacher's *understanding* in a fraction of the parameters.

**For us:** this is the compression of *knowledge*, and you already have its shape. Your **SCFF front is the big teacher** (rich, over-provisioned, unsupervised); your **GD readout is the student** that compresses SCFF's knowledge into a compact, labeled form. The "dark knowledge" idea also sharpens `7-encoding.md`: **the soft, full distribution carries the structure; the hard label throws it away** — which is *why* your model should learn from representation/soft targets, not hard labels (the "don't lie to itself" point, again). Distillation also enables a clean lifelong loop: the chip's slow brain *distills* fast experience into compact resident weights during sleep — teacher (today's activity) → student (consolidated weights).

---

## Low-rank factorization / LoRA — store the small subspace, not the big matrix

*Low-rank NN compression (classic); LoRA: Hu et al., 2021 ([arXiv 2106.09685](https://arxiv.org/abs/2106.09685)).*

The direct exploitation of `13`'s intrinsic-dimension fact. A weight matrix `W` (n×m, expensive) is replaced by a **product of two thin matrices** `W ≈ A·B` with rank `r ≪ n,m` — storing `r·(n+m)` numbers instead of `n·m`. **LoRA** showed weight *updates* have such low intrinsic rank that **rank 1–2 suffices** even for GPT-3-scale matrices (full dim 12,288). The redundancy `13` promised is *literally* the matrix being low-rank.

**For us:** low-rank is **structural** compression and it's analog-friendly: `W ≈ A·B` means a big crossbar becomes **two small crossbars in series** (`n→r` then `r→m`) — `r(n+m)` devices instead of `n·m`, a huge area saving (your `12-dataflow.md` cost). And it connects straight to your `11-connectivity.md` butterfly/Monarch idea: low-rank, butterfly, and grouped are all **structured-matrix** compressions — different shapes of "don't build the dense `n×m`." The unifying move for your chip: **never build a full crossbar; build a structured (low-rank / butterfly / grouped) one.** That's compression as *circuit topology*.

---

## Weight sharing / hashing — many connections, one stored value

*HashedNets: Chen et al., 2015 ([arXiv 1504.04788](https://arxiv.org/abs/1504.04788)); also Deep Compression's quantization stage.*

The most literal version of your "sharing neurons." A hash function maps **many connections to the same small pool of weight values** — the network has the *connectivity* of a big net but the *storage* of a tiny one, because thousands of edges read the same few numbers.

**For us:** this is your "shared neural/layer" intuition as a storage scheme, and on analog it's natural: **many Scaps reference one shared reference cap / SRAM value** (your refill mechanism is already a sharing primitive). It says the chip can have rich *connectivity* without rich *storage* — exactly the resident-weight win. Combine with superposition (`13`): shared *storage* (hashing) + shared *capacity* (superposition) are two axes of the same compression.

---

## Your Mechanism A = DenseNet feature reuse (validated, with the caveat you spotted)

*DenseNet: Huang et al., CVPR 2017 ([arXiv 1608.06993](https://arxiv.org/abs/1608.06993)).*

Your Mechanism A — *let a layer take input from its 2-previous (and feed its 2-next) layers, widening the range so more of each neuron's capacity is allocated* — **is dense connectivity.** DenseNet connects **each layer to *all* previous layers** (not just 2), so every layer reuses all earlier features. The result is *exactly your goal*: **drastic parameter efficiency** — DenseNet matches ResNet accuracy with **~1/3 the parameters** (20M vs 44M), *because* feature reuse means no layer has to re-learn what an earlier one already computed. Reusing capacity = needing less of it = compression.

**For us:** your instinct is right and it's a top efficiency architecture. Cross-layer reuse compresses by **not recomputing** — the slack you wanted to allocate gets filled with *reused* features instead of redundant new ones. **And you also spotted the real failure mode yourself:** you said Mechanism A "may diverge — inputs from each layer can refute each other." That is the genuine risk of dense connectivity (feature *soup*, unstable scales, the same drift problem from `../ref/`'s BYOL/plasticity discussion). Which is precisely why you invented Mechanism B...

---

## Your Mechanism B = the supervised anchor (and it's the right fix)

Your Mechanism B — *a "clipping trigger" that clips the cross-layer mix and **injects the label** to stop divergence* — is the **supervised anchor / normalization checkpoint**, and it's the correct instinct for the exact problem Mechanism A creates. In ML terms it's the same role as your **draft-6.0 GD checkpoint** and **translate clip** (`11-connectivity.md`), and the **BatchNorm/normalization** layers that real DenseNets put between dense blocks to keep the feature soup at a stable scale. Injecting the label periodically is **distillation/grounding** (`13`, `4-signal.md`): the label re-anchors the reused features to reality so they can't drift into an incoherent blend.

**For us:** Mechanisms A+B together are a **dense-reuse block + a normalized, label-anchored clip** — which is *the* validated pattern (DenseNet = dense block + transition layer; your draft-6.0 = SCFF reuse + GD checkpoint). You re-derived both halves: the reuse (compression) *and* its stabilizer (anti-divergence). The refinement from the literature: make the clip a **normalization + small supervised readout** (cheap, `n→m` structured, not a dense `n→1`-per-output), placed *between* reuse blocks, fired on the same threshold gate you already use.

---

## The shape of the answer (this file)

Compression methods, for you, are not a post-hoc squeeze — they're **circuit topology and learning discipline.** **Pruning** (decay the slack, reclaim charge-paths) and **weight sharing** (many Scaps, one reference) map onto controls you already built (leak, refill-SRAM). **Distillation** is what your SCFF→GD split already does (teacher front, student readout) and what sleep should do (distill experience into compact weights). **Low-rank / butterfly / grouped** are the same idea — *never build a dense `n×m` crossbar; build a structured one* — which is compression as **area**. Your **Mechanism A is DenseNet feature reuse** (~1/3 params via not-recomputing), and your **Mechanism B is its mandatory normalized, label-anchored stabilizer** — you re-derived both the compressive move and its safety catch. The through-line with `13`: **a well-chosen *form* (sparse + low-rank + shared + superposed) is born compressed**, so the same structures that fit the chip are the ones that learn well. That is the in-chip compression algorithm you were looking for — it's not one algorithm, it's *building the network out of compressive structure.*
