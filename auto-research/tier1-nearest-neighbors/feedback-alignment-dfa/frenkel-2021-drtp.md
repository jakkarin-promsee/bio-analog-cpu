# Learning Without Feedback: Fixed Random Learning Signals Allow for Feedforward Training of Deep Neural Networks (DRTP)
- **Authors / Year / Venue:** Charlotte Frenkel, Martin Lefebvre, David Bol / 2021 / Frontiers in Neuroscience 15:629892 (earlier arXiv 1909.01311)
- **Link:** https://www.frontiersin.org/articles/10.3389/fnins.2021.629892 (verified via search; arXiv 1909.01311 + PMC7902857 mirror confirmed)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐⭐☆ — the **bridge between DFA and us**: it removes the backward path *entirely* (like us) while staying in the FA family. The nearest thing to "forward-only DFA," and its accuracy cost is the honest price of that removal.

## TL;DR
Direct Random Target Projection (DRTP) notices that in supervised classification the **one-hot label is already a proxy for the sign of the output error**. So you don't need to wait for the forward pass to finish and compute `e = ŷ − y` — you can project the **label itself** through fixed random matrices directly into each hidden layer, *before* the output is known. This makes training **fully feedforward**: it solves weight transport **and update locking**, with no backward pass at all.

## The mechanism (how it actually works)
DFA still needs the *actual* output error `e = ŷ − y`, which means it must finish the forward pass, read the prediction, and broadcast the error back — a (short) backward step and an update-lock. DRTP's insight: the modulatory signal DFA broadcasts is dominated by its **sign**, and for one-hot targets the label `y` already carries that sign. So replace the broadcast error `e` with the **fixed target `y`**:

`δ_l = (B_l · y) ⊙ f'(a_l)` — projected through a fixed random `B_l`, available *as soon as the label is*, i.e. concurrently with the forward pass.

There is now **no backward pass and no update locking**: each layer's teaching signal is a fixed random projection of the label, computed feedforward. This is the maximal simplification of the FA family — it trades the (already-random) backward path for *no path*, at the cost of a coarser signal (it uses the target, not the residual, so it can't tell "how wrong" as precisely).

## Key results / claims
- Solves **both** weight transport and update locking → a genuinely feedforward training rule.
- Sharply relaxes compute/memory requirements — pitched explicitly for **low-cost adaptive edge sensors**.
- Accuracy cost: DRTP is weaker than DFA/BP (using the target instead of the error is a coarser signal); it is a *simplicity/hardware* win, not an accuracy win. Demonstrated on MNIST-class problems.

## How it relates to us
- **Organ / phase touched:** the credit-assignment core; the "how little backward machinery can you get away with" axis that our forward-only choice sits at the extreme of.
- **Same as us:** DRTP and SCFF are the two "**no backward pass at all**" points. Both are motivated by edge/hardware locality; both refuse update-locking and weight transport.
- **Different from us (the sharp line):** DRTP is still **supervised** — it needs the **label at every layer, every step**, projected in. Our SCFF is **label-free**: the whole 80% bulk learns with *no targets*, and labels enter only at the tiny closed-form namer. So DRTP removes the backward *path* but keeps the *supervision*; we remove **both** from the bulk. DRTP is "feedforward *supervised* learning"; SCFF is "feedforward *unsupervised* representation learning + a cheap named head."
- **What we could borrow or test:** DRTP is arguably the right template for **our namer**, not our bulk — a feedforward, fixed-random-projection supervised head is exactly the kind of cheap direction the 20% could use. Worth a note against RanPAC/SLDA: DRTP is the *gradient-free-ish, projection-based* supervised head from the FA lineage; our closed-form namer is the analytic-CL lineage's answer to the same need. A head-level bake-off (DRTP-style vs SLDA) is a concrete untested comparison.
- **What contradicts or challenges us:** DRTP shows removing the backward path is cheap *if you keep supervision*. It quietly reframes our contribution: the hard, novel part is not "no backward path" (DRTP has that too) — it is **"no backward path AND no supervision in the bulk."** State the claim that precisely.

## Follow-on leads
- Frenkel's hardware work (ODIN / ReckOn spiking chips) — DRTP-adjacent on-chip learning silicon.
- PEPITA / SigProp (already in `forward-only-family/`) — other "forward-only supervised" points; DRTP is the FA-family member of that cluster.
- Head-level comparison: DRTP-style random-projection head vs our closed-form SLDA/RanPAC namer (a testable P7-adjacent probe).
