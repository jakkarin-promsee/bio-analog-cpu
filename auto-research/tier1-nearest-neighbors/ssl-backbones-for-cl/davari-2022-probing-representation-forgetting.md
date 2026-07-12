# Probing Representation Forgetting in Supervised and Unsupervised Continual Learning
- **Authors / Year / Venue:** MohammadReza Davari, Nader Asadi, Sudhir Mudur, Rahaf Aljundi, Eugene Belilovsky — 2022 — CVPR 2022
- **Link:** https://arxiv.org/abs/2203.13381 (fetched; CVPR open-access PDF: https://openaccess.thecvf.com/content/CVPR2022/papers/Davari_Probing_Representation_Forgetting_in_Supervised_and_Unsupervised_Continual_Learning_CVPR_2022_paper.pdf)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐⭐ — the measurement paper: "forgetting" at the classifier is not "forgetting" in the representation — the exact distinction our bulk/namer split is built on.

## TL;DR
Defines **representation forgetting** as the drop in an *optimal linear probe* fit before vs after a new task — separating "the readout went stale" from "the features are gone." Under this lens, plain fine-tuning (no CL machinery) often keeps or even improves prior-task representations, sometimes matching explicit CL methods, especially over long sequences; SSL-trained representations are notably robust.

## The mechanism (how it actually works)
The observed catastrophic-forgetting number conflates two failures: (a) the representation genuinely losing the old structure, and (b) the classifier head drifting out of alignment with a representation that still holds the structure. The probe protocol isolates (a): freeze the representation at checkpoints, fit the *best possible* linear classifier on old-task data before and after new-task training, and difference them. Much of the canonical forgetting turns out to be (b) — the representation "changes without losing knowledge." They exploit this constructively: learn features with supervised-contrastive loss and rebuild old-class predictions from stored prototypes, letting the representation drift while the readout re-anchors.

## Key results / claims
- Representation forgetting is much milder than classifier-level forgetting; naive fine-tuning is a strong representation-level baseline, increasingly so on longer task sequences.
- SSL/unsupervised objectives yield representations more robust under sequential training than supervised ones (probe-level).
- Prototype + supervised-contrastive construction recovers old-task performance without replaying raw data through the loss.

## How it relates to us
- **Organ / phase touched:** the bulk/namer split itself; P9.0 (bulk rotates-not-forgets); P9.4 proto-reanchor; P11 decomposition (safety lives in the namer+gate+sleep).
- **Same as us:** this is the published version of our central architectural diagnosis — the representation drifts benignly, the *readout* is what forgets, so put the repair (re-fit, prototypes, sleep) at the readout. Their prototype re-anchoring is our P9.4 in gradient-world clothes.
- **Different from us:** offline probes fit with full old-task data (an oracle readout, not deployable); backprop representations; no gate, no cost accounting, no online constraint.
- **What we could borrow or test:** report an **optimal-probe forgetting curve** for the SCFF bulk alongside our prequential numbers — it is the field's accepted instrument for "the representation held," and it would let us cite-compare our rotation claim directly.
- **What contradicts or challenges us:** their "fine-tuning is a strong baseline" cuts both ways — if plain backprop representations also barely forget under probes, our bulk's representation-level stability is table stakes, and our differentiators must be safety-at-the-deployed-readout, energy, and order-invariance (which is where P10/P11 put them anyway).

## Follow-on leads
- Optimal-probe (linear evaluation) protocols for continual representations — align our reporting.
- Zhang et al., SLCA and the slow-representation/fast-head family (already carded in t1.5).
- CKA/feature-similarity drift measures as cheap online probes of benign vs destructive drift.
