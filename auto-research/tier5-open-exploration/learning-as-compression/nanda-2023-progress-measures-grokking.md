# Progress Measures for Grokking via Mechanistic Interpretability
- **Authors / Year / Venue:** Neel Nanda, Lawrence Chan, Tom Lieberum, Jess Smith, Jacob Steinhardt / 2023 / ICLR 2023
- **Link:** https://arxiv.org/abs/2301.05217
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐⭐ — makes grokking-as-compression rigorous: memorize → build a compact circuit → **delete the memorized scaffold**; and gives *progress measures* that see the compression the loss hides.

## TL;DR
By fully reverse-engineering a transformer that learned modular addition, the authors split training into **three continuous phases — memorization, circuit formation, cleanup** — and show grokking is not a sudden event but the **gradual amplification of a compact algorithm followed by the removal of the memorized solution**. New *progress measures* (restricted loss, excluded loss) reveal the compression happening underneath a flat test loss.

## The mechanism (how it actually works)
The grokked network computes `a + b mod p` by a beautiful trick: embed each input on a circle (a **discrete Fourier basis**), rotate by addition using **trig identities**, and read off the angle — a genuine algorithm, not a table. Tracking this circuit over training gives three phases. **Memorization**: the net fits training data with a dense, non-generalizing solution. **Circuit formation**: the Fourier algorithm gradually *forms and strengthens* in the weights while the memorized solution is still present (test loss still flat). **Cleanup**: weight decay *removes* the now-redundant memorized components, the network's norm drops, and test accuracy snaps up — that snap is what we call grokking. The key instruments: **restricted loss** (ablate everything but the key Fourier frequencies — falls early, showing the circuit forms *before* generalization is visible) and **excluded loss** (remove those frequencies — rises, showing reliance shifting onto the circuit). Compression is literally the cleanup phase: the model **discards** the part that was memorization.

## Key results / claims
- Three phases: **memorization → circuit formation → cleanup**; grokking = cleanup completing.
- **Progress measures** derived from the reverse-engineered circuit track generalization *before* it shows in test loss.
- Grokking is "the gradual amplification of structured mechanisms … followed by the removal of memorizing components" — a compression process, not a phase transition out of nowhere.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk (structure formation), sleep/consolidation (the cleanup analog), convergence invariants, the double-descent frame.
- **Same as us:** the **cleanup phase is the mechanistic twin of our sleep/consolidation** — a periodic move that *removes the memorized scaffold and keeps the compact structure*. Our founding "rotates-not-forgets" bulk + closed-form re-fit is a cleanup-style compression, done by architecture instead of weight decay.
- **Different from us:** their cleanup is driven by weight decay on a static task with backprop; ours is a closed-form namer re-fit over a prototype LUT on a stream. Same *shape* (discard scaffold, keep structure), different *engine*.
- **What we could borrow or test:** **progress measures.** Nanda's lesson is that test loss/accuracy is blind to compression in progress; a *circuit/probe-based* measure sees it. For us: define a "structure-formed" progress measure on the frozen bulk (e.g. probe-accuracy or a restricted-tap loss) so we can tell *when the bulk has actually organized a task* vs merely stopped moving — a sharper convergence invariant than loss-slope.
- **What contradicts or challenges us:** cleanup needs a pressure that *removes* the redundant memorized part. Our forward-only bulk has no explicit such pressure; if the scaffold is never cleaned, the "spare capacity" is occupied by dead memorized directions, not shareable slack — the pessimistic reading of P11's half-confirmation.

## Follow-on leads
- Power et al. 2022 (the phenomenon this explains).
- Restricted/excluded-loss-style **progress measures** as a new convergence invariant for the SCFF bulk.
- "Grokking as compression / L2-norm dynamics" and interpretability-of-continual-learning threads.
