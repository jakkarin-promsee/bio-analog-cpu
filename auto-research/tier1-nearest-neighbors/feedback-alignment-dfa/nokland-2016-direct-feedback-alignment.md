# Direct Feedback Alignment Provides Learning in Deep Neural Networks
- **Authors / Year / Venue:** Arild Nøkland / 2016 / NeurIPS (NIPS) 2016, pp. 1037–1045
- **Link:** https://arxiv.org/abs/1609.01596 (verified via search; arXiv id + venue confirmed. Abstract-page WebFetch timed out, but the record — title, author, mechanism, NIPS 2016 pages — is confirmed across arXiv listing + dblp.)
- **Tier / Topic:** tier1 / t1.6 feedback-alignment / DFA / target-prop
- **Relevance:** ⭐⭐⭐⭐☆ — the DFA anchor: the *parallel* backprop-free rule that most people mean by "the other way to drop backprop." The nearest engineering neighbor to our forward-only choice on the "keep a random backward path" side.

## TL;DR
Go further than FA: don't propagate error backward through the layer chain at all. **Project the single global output error `e` directly into every hidden layer through that layer's own fixed random matrix `B_l`**, in parallel. No sequential backward pass, no transpose, no update-locking between layers.

## The mechanism (how it actually works)
FA (Lillicrap) still routes error *sequentially* backward layer by layer, just with random matrices. DFA cuts the chain entirely. The error at the output, `e = ŷ − y`, is broadcast **straight to each hidden layer** through a fixed random projection:

`δ_l = (B_l · e) ⊙ f'(a_l)` — with a distinct fixed random `B_l` per layer, sized to map the output error into that layer's width.

Every hidden layer computes its update from the *same* global error, independently and simultaneously. There is no `W_{l+1}ᵀ`, no `B_{l+1}`, no waiting for the layer above — the backward "pass" is one parallel fan-out of the output error. The same alignment phenomenon rescues it: forward weights adapt until each `B_l·e` becomes a descent direction for that layer. Because every layer is taught directly from the output, DFA is **fully parallel across depth** and removes *update locking* (the serialization backprop forces).

## Key results / claims
- Trains deep fully-connected nets and (in the paper's own tests) reaches near-zero training error without any backpropagated error.
- Removes both weight transport *and* update locking → the layer updates are embarrassingly parallel.
- Scope / limits: strong on MNIST-class problems; the well-known failure to train convolutional nets and to scale to ImageNet is documented by later work (Bartunov 2018, Refinetti 2021 in this folder). DFA's single random projection of the output error is a *coarse* teaching signal for spatially structured / weight-shared features.

## The mechanism (how it actually works)
(see above — the direct random projection is the whole idea)

## How it relates to us
- **Organ / phase touched:** the credit-assignment structure of the whole model; the "cheap global direction" question of Phase 5 Track C (`research/papers/phase5/track-c-cheap-direction.md`).
- **Same as us:** both drop the transpose and the deep credit chain; both are motivated by "the cross-layer backward machinery is the expensive, un-physical part."
- **Different from us (the core contrast):** DFA keeps a **random *backward* projection** (an output-error broadcast + a per-layer random matrix multiply) and is **supervised** — it *needs* the global label error every step. Our SCFF has **no error broadcast at all**: credit is a local windowed InfoNCE, label-free, derivative-free. On the ledger: DFA pays {one global error + N random projections + the forward pass}; we pay {a local contrast within a `w`-layer window}. DFA is parallel-across-depth *given the error*; we never form a global error.
- **What we could borrow or test:** DFA's direct random broadcast is the ML-native form of the "three-factor / cheap global direction" lever Phase 5 examined and set aside. If the *namer* ever needed a cheap multi-layer direction, DFA-to-the-heads (not to the bulk) is the candidate — but the scaling literature says keep it shallow.
- **What contradicts or challenges us:** DFA is the strongest existence proof that a *random backward path* is enough for easy tasks — which could tempt us back toward a backward path. Its ceiling (next cards) is why we don't.

## Follow-on leads
- Launay 2020 — DFA scaled to transformers / NeRF / recommenders (this folder).
- Refinetti 2021 — the theory of *why* alignment happens and why conv breaks it (this folder).
- Frenkel 2021 (DRTP) — DFA taken all the way to *no backward path* using the label as error-sign proxy (this folder).
