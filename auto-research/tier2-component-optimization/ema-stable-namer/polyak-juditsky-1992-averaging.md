# Acceleration of Stochastic Approximation by Averaging
- **Authors / Year / Venue:** B. T. Polyak, A. B. Juditsky / 1992 / SIAM Journal on Control and Optimization 30(4)
- **Link:** https://epubs.siam.org/doi/10.1137/0330046 (fetched)
- **Tier / Topic:** tier2 / t2.7 EMA "stable namer"
- **Relevance:** ⭐⭐⭐⭐☆ — the theorem that says averaging a noisy running estimate is *asymptotically optimal*; the math floor under any EMA-of-statistics anchor.

## TL;DR
If you run a stochastic-approximation recursion with a *larger-than-optimal* step size and then **average the iterates**, the averaged estimate converges at the best possible rate and attains the **optimal asymptotic covariance** — you get second-order efficiency for free, without tuning a decaying step schedule. This is the theoretical seed of Polyak–Ruppert averaging, and by extension every weight-EMA / mean-teacher / SWA method.

## The mechanism (how it actually works)
Ordinary stochastic approximation (SGD is a special case) needs a carefully decayed step size to converge efficiently; too large and it rattles around the optimum, too small and it crawls. Polyak & Juditsky's move: deliberately use a *robust, larger* step so the raw iterate explores fast (and noisily), then take the **running average** of the whole trajectory as your actual answer. The averaging cancels the excess noise the big step introduced. The punchline theorem: this two-part scheme reaches the Cramér–Rao-style optimal asymptotic variance — the same you'd get from the (impractical) perfectly-tuned schedule — with a step size you barely have to tune. Averaging *is* the variance reduction.

## Key results / claims
- Trajectory averaging + a larger step → **highest possible convergence rate** and **optimal asymptotic covariance** for a broad class of SA problems.
- Convergence with probability one.
- Decouples "explore fast (raw iterate)" from "estimate precisely (the average)" — the two-timescale idea.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the namer (SLDA mean+cov / RanPAC Gram); the maintenance loop's stability-vs-recency knob.
- **Same as us:** our namer already *is* a running estimator (SLDA running class means + tied covariance; RanPAC running Gram). Polyak says: if that estimate is noisy under drift, a slower average of it is the *statistically optimal* smoother — exactly the "stable namer" premise.
- **Different from us:** Polyak averages **first-order** parameter iterates of an optimizer. Our proposal averages **second-order** statistics (a Gram/covariance) — the optimality theorem does *not* transfer verbatim to the SPD cone (see arsigny-2006). For the **mean vector** channel it transfers cleanly.
- **What we could borrow or test:** the two-timescale framing — let the fast namer track drift with a "large step," and keep a slow Polyak-average as the anchor. Predicts a real variance reduction at the worst point.
- **What contradicts or challenges us:** the theorem is *asymptotic and stationary*. Under **non-stationary drift** (our regime) a plain infinite-horizon average is biased toward stale data — you must use a *forgetting* average (finite memory / EMA), which trades optimality for tracking. So "EMA," not "Polyak-mean-of-all-history," is the drift-correct form.

## Follow-on leads
- Ruppert 1988 (the parallel discovery). Forgetting-factor RLS (the drift-correct finite-memory version). Two-timescale stochastic approximation (Borkar).
