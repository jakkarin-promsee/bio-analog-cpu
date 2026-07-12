# Let's Verify Step by Step
- **Authors / Year / Venue:** Hunter Lightman, Vineet Kosaraju, Yura Burda, Harri Edwards, Bowen Baker, Teddy Lee, Jan Leike, John Schulman, Ilya Sutskever, Karl Cobbe — 2023 (OpenAI; ICLR 2024), arXiv:2305.20050
- **Link:** https://arxiv.org/abs/2305.20050
- **Tier / Topic:** tier3 / t3.3 correctness-as-feeling
- **Relevance:** ⭐⭐⭐ — the anchor of the verifier line: a *separate trained judge* scoring the reasoning **process**, not just the outcome — dense supervision beats sparse, measured cleanly.

## TL;DR
Train a **process reward model (PRM)** on 800K human labels grading every *step* of model-generated math solutions, and compare against an outcome reward model (ORM) trained only on final answers. Process supervision wins decisively: best-of-N reranking with the PRM solves **78.2%** of a MATH test subset, and the gap over the ORM *grows* with N. Released PRM800K.

## The mechanism (how it actually works)
- **The two supervision shapes:** ORM sees (solution, final-answer-correct?) — one sparse grounded bit; the credit for *where* it went wrong is unassigned. PRM sees per-step labels (positive/neutral/negative) — the error is localized to the step that made it.
- **Training:** the PRM predicts each step's label from the prefix; a solution's score = the probability all steps are correct (product of per-step scores). Reranking: sample N solutions, answer with the top-scored one.
- **Why the PRM wins as N grows:** the ORM rewards *lucky right answers from wrong reasoning* (false positives that reranking amplifies); the PRM's step-level checks are much harder to satisfy by luck. Dense supervision isn't just more signal — it's **harder-to-hack** signal, the Goodhart-resistance argument in supervised form.
- **Active learning:** label the samples where the current PRM most disagrees with the outcome check — 2.6× label efficiency.

## Key results / claims
- 78.2% on MATH-500 subset via best-of-1860 reranking vs ORM and majority-vote baselines below it; gap widens with N.
- Process supervision's advantage holds for smaller models supervised by machine labels (a scale-down check).
- The price is the elephant: 800K *human* step labels — the expensive-grounding ceiling (Math-Shepherd's automation answers this).

## How it relates to us
- **Organ / phase touched:** the future critic head; the settling loop's trajectory (our "process"); the gate's judged quantity.
- **Same as us:** the architectural claim — the judge is a **separate small model beside the producer**, trained by grounding — is the dossier's learned-critic picture, validated at frontier scale.
- **Different from us:** their process is a discrete token trajectory with human-readable steps; ours is a continuous settle path (states z_0 → z_T) and tap trajectory. "Step labels" for us are machine-harvestable (did the namer's read change? did drift move along the class axis?) rather than human-annotated — we live on the Math-Shepherd side of this pair by necessity.
- **What we could borrow or test:** the **shape of the halt score**: score the *trajectory*, not the endpoint. A settle that arrives at its fixed point through a monotone, direction-consistent path deserves more trust than one that wandered — a per-step feeling aggregated by product/min (their aggregation) is a stronger halt than endpoint confidence alone. Cheap version: count sign-flips of the namer's read along the settle; flip-free settles are the "all steps correct" analog. (Consistent with our own P10 finding that OURS rides flat while ER saw-tooths — path shape carries information.)
- **What contradicts or challenges us:** dense human grounding is what makes their signal trustworthy, and we have none of it. Everything we build in this direction must borrow trust from automation (rollouts, checks) or physics (agreement under noise) — the two neighboring cards.

## Follow-on leads
- Math-Shepherd (this folder) — the same PRM without human labels.
- Zheng et al. 2025 PRM survey (this folder) — where the line went after this.
- "Process Reward Models That Think" (arXiv:2504.16828) — the 2025 turn: the verifier itself reasons before judging.
