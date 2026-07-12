# When, Where and Why to Average Weights?
- **Authors / Year / Venue:** N. Ajroldi, A. Orvieto, J. Geiping / 2025 / arXiv (cs.LG)
- **Link:** https://arxiv.org/abs/2502.06761 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐☆☆ — a 2025 head-to-head of EMA vs SWA vs soups on a standard benchmark; the "how much does averaging actually buy, and when" reality check.

## TL;DR
An extensive, benchmark-driven (AlgoPerf, 7 architectures/datasets) comparison of weight-averaging methods — EMA, SWA, model soups. Finding: averaging **accelerates training** and yields **efficiency gains** at negligible cost, with **modest** (not dramatic) generalization improvement, and it interacts tightly with **learning-rate annealing** (averaging can partly stand in for LR decay).

## The mechanism (how it actually works)
No new method; it stress-tests the family. The unifying view: all three are the same low-pass filter over the iterate distribution, differing only in *which* iterates and *what weighting* — EMA (exponential, online), SWA (uniform, tail of training), soups (uniform, across runs). The paper isolates *when* averaging helps (interaction with the LR schedule, where in training you start averaging) and quantifies the honest size of the win.

## Key results / claims
- Averaging **speeds up training** / gives efficiency gains broadly, low overhead.
- Generalization improvement is **modest** across the board — a calibration against over-claiming.
- Strong **interaction with LR annealing**; averaging and decay are partly substitutes.
- Where/when you average matters (start point in training).

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** namer; sets the *expected magnitude* of any stable-namer win.
- **Same as us:** frames EMA/SWA/soups as one family — helps us place our proposal (an EMA-of-*statistics*) as a member, and warns the win is likely **modest**, not transformative. Good prior for setting the experiment's success bar honestly.
- **Different from us:** stationary, gradient-trained, offline. Our regime (drift, closed-form, online) is where averaging's *tracking-vs-smoothing* tension is sharpest — a regime this benchmark doesn't cover.
- **What we could borrow or test:** the **"when to start averaging"** question maps to *when the stable namer should begin trusting itself* after a drift event — cold-start the anchor at each rotation boundary rather than run it continuously.
- **What contradicts or challenges us:** the "modest gain" verdict tempers expectations — a stable namer may buy a small worst-point improvement, which must be weighed against grid-4 sleep (which already got worst-BWT to −0.028). The lever only earns a phase if it beats *cheaper sleep*, not just no-averaging.

## Follow-on leads
- The averaging × LR-annealing substitution → averaging × sleep-cadence substitution for us. AlgoPerf as a fair-budget protocol idea. Fisher-weighted averaging (statistically weighted soup).
