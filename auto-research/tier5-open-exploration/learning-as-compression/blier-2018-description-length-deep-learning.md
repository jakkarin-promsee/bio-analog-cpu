# The Description Length of Deep Learning Models
- **Authors / Year / Venue:** Léonard Blier, Yann Ollivier / 2018 / NeurIPS 2018
- **Link:** https://arxiv.org/abs/1802.07044
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐⭐ — makes "learning IS compression" *operational*: an actual codelength you can measure, via the prequential (online) code — which is the shape our streaming setup already computes.

## TL;DR
Turns MDL from slogan into measurement. A deep net's **description length of the data** is measured by the **prequential (online) code**: predict each label from all previous ones, and sum the negative log-likelihoods. Under this code, deep nets **losslessly compress** the training labels *even after paying to encode the parameters* — empirically confirming they find real structure, not noise. And the "obvious" way to measure it (variational / two-part codes) gives **surprisingly poor** bounds.

## The mechanism (how it actually works)
MDL says the best model minimizes `L(model) + L(data | model)` in bits. The naive **two-part code** encodes the weights explicitly then the residuals — but for a huge net the weight term is enormous, so this badly overstates the codelength. The fix is the **prequential (predictive) code**: never encode the weights at all. Instead, process the data as a stream — at step `t`, use the model trained on the first `t−1` points to predict point `t`, and charge `−log p(y_t | x_t, model_{t−1})` bits; sum over the stream. This is a *valid, self-delimiting* code (the receiver retrains the same way, so no parameters need transmitting) and it automatically accounts for model complexity through early-stream prediction cost. Measured this way, an MNIST classifier compresses the labels to a tiny fraction of the raw `log(10)`-bits-per-label — i.e. it **found the regularity**. The paper also shows variational codes, though built to minimize a bound, compress *worse* than this simple online scheme.

## Key results / claims
- Deep nets achieve **lossless compression** of labels including parameter cost — MDL/Occam confirmed for over-parameterized nets.
- **Prequential coding** gives the best (smallest) codelengths; **variational** codes are surprisingly loose.
- Codelength is a **generalization signal**: better compression tracks better test performance.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the whole learning-is-compression frame, the SCFF bulk + namer as a joint code, streaming evaluation, P11 prequential metric.
- **Same as us:** the prequential code is **exactly our streaming setup** — P11 already reports *prequential accuracy* on gas/real streams. Blier & Ollivier say: the same online loss, in bits, **is** the description length. So we can report our object's *compression* almost for free, and "fits on-chip" and "learns the real shape" become one measured quantity.
- **Different from us:** they train a full net by backprop over the stream and read its predictive loss; our bulk is frozen-unsupervised and only the namer predicts labels. The codelength we could report is the *namer-on-frozen-bulk* code, not an end-to-end trained one.
- **What we could borrow or test:** **report our streams' prequential codelength (bits), not just accuracy.** This is the direct measurement of "how compressible is this task on our substrate" — and it upper-bounds the storage the task needs, which is the on-chip-fit argument in its native currency. A frozen-bulk that gives a short code on a stream is *literally* a good compressor for it.
- **What contradicts or challenges us:** the prequential code *rewards early-stream prediction*; our namer is cold at stream start (few prototypes) and drift-gated, so our early-stream bits are expensive — our codelength may look worse than a fully-online backprop net even where our *safety/energy* wins. Compression is not the axis we win on; be honest about that.

## Follow-on leads
- Hinton & van Camp 1993 / Rissanen MDL (in dossier) — the theory roots.
- Prequential MDL as a continual-learning metric — "compression per task" as a retention measure.
- Grünwald "The Minimum Description Length Principle" — the reference text for the coding machinery.
