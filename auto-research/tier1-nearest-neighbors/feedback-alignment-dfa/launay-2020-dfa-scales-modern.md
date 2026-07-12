# Direct Feedback Alignment Scales to Modern Deep Learning Tasks and Architectures
- **Authors / Year / Venue:** Julien Launay, Iacopo Poli, François Boniface, Florent Krzakala / 2020 / NeurIPS 2020, pp. 9346–9360
- **Link:** https://arxiv.org/abs/2006.12878 (fetched)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐⭐☆ — the counter-narrative to Bartunov: DFA *does* scale — but only to architectures **without weight sharing**. The nuance that decides whether a random backward path is worth it depends entirely on architecture, which is directly informative for our flat-vector substrate.

## TL;DR
DFA is shown to train a broad range of *modern, non-conv* architectures at performance "close to fine-tuned backpropagation": NeRF neural view synthesis, recommender-system embeddings, graph/geometric learning, and Transformers/NLP. The message: the FA family's failure is **not** universal — it is specifically the **convolutional / weight-shared** case that breaks, and much of modern deep learning is not that.

## The mechanism (how it actually works)
Same DFA rule as Nøkland — the output error is projected directly into each layer through a fixed random matrix — but applied at scale to architectures the original papers never touched. The engineering contribution is showing DFA can be dropped into fully-connected blocks, attention, embedding tables, and implicit-representation MLPs, and still align. Transformers are the hard case: DFA trains them, but with a **larger gap** to backprop than the other families, which the authors attribute to needing to *rethink standard practices* (init, normalization, learning-rate schedules) for large complex architectures rather than a fundamental block.

The quiet but crucial implication (made explicit in the follow-on theory, Refinetti 2021): DFA scales exactly where there is **no weight sharing**. Fully-connected / attention / embedding layers align fine; convolution's shared kernels are what poisons the alignment.

## Key results / claims
- DFA successfully trains SOTA architectures across four modern domains (view synthesis, recommenders, geometric learning, NLP) "close to fine-tuned backpropagation."
- Transformers: trainable with DFA, but the DFA↔BP gap is largest here → an open practices problem, not a wall.
- Reframes the family's reputation: "fails to scale" (Bartunov) is really "fails on conv"; on non-conv modern nets DFA is viable.
- Companion hardware angle (same group, LightOn): DFA's direct random projection is attractive because it can be computed *in one shot* on analog optical hardware.

## How it relates to us
- **Organ / phase touched:** the SCFF bulk's architecture class (flat-vector, no weight sharing) and the north-star question of whether a cheap non-exact rule can ever carry a big model.
- **Same as us:** our substrate is **flat-vector — no weight sharing**, which is precisely the regime where DFA *does* align. So the strongest "backprop-free rules can't scale" objection (Bartunov's conv result) targets a structure we don't have. This is a genuine point in our favor worth stating carefully.
- **Different from us:** DFA still needs the global label error and a random backward broadcast; we are forward-only + unsupervised. And DFA's "scales" is on *supervised* end-to-end training; our scaling story (P11) is *continual/streaming*, a different axis.
- **What we could borrow or test:** if a future north-star build wants attention/recurrence, this says a DFA-style random broadcast to those (non-conv) blocks is a live option — a cheaper credit path than backprop for the parts SCFF's local contrast can't reach.
- **What contradicts or challenges us:** it weakens any claim that "forward-only is the *only* way to avoid the transpose at scale" — DFA gets much of the way there while keeping supervision. Our differentiator has to be the *unsupervised + zero-backward-path + continual* combination, not merely "no transpose."

## Follow-on leads
- Refinetti 2021 — the theory that formalizes "scales iff no weight sharing."
- Filipovich 2022 / reservoir-DFA 2024 / PNAS-2025 optical DFA — the analog hardware realizations this work's group and others pursued.
- Sign-symmetry (Xiao 2018) — the partial-transport alternative for the conv case DFA can't reach.
