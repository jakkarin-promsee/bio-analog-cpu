# Signal Propagation (SigProp): A Framework for Learning and Inference In a Forward Pass
- **Authors / Year / Venue:** Adam Kohan, Edward A. Rietman, Hava T. Siegelmann / 2022 / arXiv:2204.01723 (cs.LG)
- **Link:** https://arxiv.org/abs/2204.01723 (fetched)
- **Tier / Topic:** tier1-nearest-neighbors / t1.1 (forward-only family)
- **Relevance:** ⭐⭐⭐ — a third forward-only paradigm (carry the *target* forward alongside the input); useful as a family boundary marker, less directly borrowable.

## TL;DR
Feed the **learning signal (the target) into the same forward path as the input**, as if it were another input, and let it propagate layer-by-layer. Each layer aligns its input-driven activity with the target-driven activity locally. Result: global supervised learning with **only a forward path** — no feedback connectivity, no weight transport, no backward pass.

## The mechanism (how it actually works)
Where backprop sends the target error *backward*, SigProp sends the target *forward* through the network as a parallel stream. At each layer you have two forward-propagated quantities: the representation of the input and the representation of the target/context. The local update pulls the input representation toward the target representation (a local alignment loss) at that layer. Because the target rides the same forward machinery, no separate feedback pathway or transposed weights are needed; layers can even be updated in parallel. It generalizes to spiking nets and continuous-time Hebbian updates.

## Key results / claims
Matches or approaches backprop on standard vision benchmarks in the paper's setting while using less time and memory (no activation tape, no backward pass). Framed for **neuromorphic hardware** (learning without backward connectivity) and biology (neurons without feedback connections still getting a global signal).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the *paradigm boundary* around our SCFF bulk; the mono-forward dual-rail idea (two things riding one forward path).
- **Same as us:** two quantities carried through **one shared forward path** — mechanically the same shape as our dual-rail (two views / two worlds, one crossbar).
- **Different from us:** SigProp's two streams are **input vs supervised target**; ours are **two label-free augmented views**. SigProp is **globally supervised**; our bulk is unsupervised. SigProp aligns input to target (a supervised regression per layer); we contrast (InfoNCE) with no target.
- **What we could borrow or test:** the "carry the second stream as an input" framing is the clean abstraction of our dual-rail — worth citing when justifying that mono-forward is a known, sound primitive, not an ad-hoc trick.
- **What contradicts or challenges us:** like PEPITA, it shows forward-only can be *fully supervised and global*; reinforces that our label-freedom is a design choice for continual-safety, not forced by the substrate.

## Follow-on leads
Neuromorphic forward-only learning; parallel/pipelined layer training (no update-locking); Hebbian + spiking realizations of forward learning.
