# Revisiting Supervision for Continual Representation Learning
- **Authors / Year / Venue:** Daniel Marczak, Sebastian Cygert, Tomasz Trzciński, Bartłomiej Twardowski — 2024 — ECCV 2024
- **Link:** https://arxiv.org/abs/2311.13321 (fetched; code: https://github.com/danielm1405/sl-vs-ssl-cl; ECVA PDF: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/00944.pdf)
- **Tier / Topic:** tier1 / t1.7 SSL backbones for CL
- **Relevance:** ⭐⭐⭐⭐⭐ — **the skeptic.** The SSL-forgets-less advantage may be an *architecture* artifact (the MLP projector), not a *label-freeness* effect — an attribution threat aimed at our founding bet.

## TL;DR
Directly re-runs the supervised-vs-self-supervised continual-representation comparison, but gives the supervised model the same **MLP projector head** that SSL methods always carry. Result: **supervised models with a projector outperform SSL models at continual representation learning.** The transferability magic previously credited to label-freeness largely lives in the projector — a buffer layer that absorbs task-specific pressure so the backbone features stay general.

## The mechanism (how it actually works)
Every joint-embedding SSL pipeline trains through a small MLP projector and then *throws it away*, evaluating the pre-projector backbone features. The projector soaks up the objective-specific distortion (invariances, decorrelation structure), leaving backbone features less specialized — that is the transfer advantage. Classic supervised training has no such buffer: the linear classifier's task pressure lands directly on backbone features, specializing (and, sequentially, overwriting) them. Add the projector to the supervised path — cross-entropy through MLP-then-classifier, evaluate pre-projector — and the supervised backbone now *also* keeps general features, plus it gets the extra semantic signal of labels. In sequential training that combination beats the label-free version of the same architecture.

## Key results / claims
- Supervised + MLP projector > SSL counterparts for continual representation learning across their sequential benchmarks (abstract-level; per-benchmark digits in paper, not pulled here).
- The projector, not the training-signal type, is identified as the primary driver of feature transferability across tasks.
- Reframes prior SSL-forgets-less results (LUMP, Davari-style) as under-controlled comparisons — architecture differed along with supervision.

## How it relates to us
- **Organ / phase touched:** SCFF bulk objective (InfoNCE + w=2 coordination window); the attribution story under the A6 continual win; public-claim hygiene.
- **Same as us:** methodologically kin — it is a one-thing-changed control experiment (our house rule #1) applied to the field's favorite comparison, and it found the confound.
- **Different from us:** operates entirely in offline backprop land; "supervision" there means dense per-sample labels, which our bulk never has by *hardware* design, not by choice of objective fashion.
- **What we could borrow or test:** the attribution control, ported to our substrate: is our bulk's continual robustness due to **label-freeness** or to the **contrastive-objective architecture** (InfoNCE + window acting as our "projector")? Concrete test: a supervised-contrast SCFF variant (labels define InfoNCE positives — still local, still forward-only) vs our label-free cell, everything else locked, measured on BWT/retention. If supervised-contrast matches label-free, our safety story should credit the *objective structure*, not the absence of labels — which would actually *strengthen* the chip story (labels are absent for cost reasons; robustness comes from structure we control).
- **What contradicts or challenges us:** directly undercuts citing LUMP/Cossu-style "SSL forgets less" as support for the bulk being label-free — the comparison behind that claim is confounded. Our public framing must not lean on label-freeness *causing* continual robustness until we run the control.

## Follow-on leads
- The projector/feature-buffer literature (why throwing away the head helps transfer).
- Whether our w=2 coordination window functions as a projector-equivalent (absorbing objective distortion away from tapped features) — measurable via probe-vs-tap gaps we already log.
- Supervised-contrastive local rules (SupCon-style positives) as the label-injected control arm.
