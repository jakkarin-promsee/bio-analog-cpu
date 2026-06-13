# 19 — Why learning converges *and* generalizes (the optimization foundation)

> The whole project bets that a network *will* train to a good solution *and* that the solution will work on data it hasn't seen. That bet rests on optimization & generalization theory — foundational, and (until now) only touched in pieces (your double descent, `13`). This file is the floor under "it learns." The punchline that ties it to the rest: **the thing that makes a solution generalize is the same thing that makes it survive analog noise — flatness.**

---

## Will it converge? Over-parameterization makes optimization easy (NTK)

*Neural Tangent Kernel: Jacot, Gabriel & Hongler, 2018 ([arXiv 1806.07572](https://arxiv.org/abs/1806.07572)).*

The surprising answer to "won't a big non-convex network get stuck?" In the **wide (over-parameterized) limit**, a network at initialization behaves like a **Gaussian process**, and *training by gradient descent becomes equivalent to kernel regression* with a fixed kernel (the NTK) — which is a **convex** problem. The consequence: **in the wide limit, gradient descent provably converges** to a global solution, and the dynamics are nearly linear. Width *buys* trainability.

**For us:** this is half the license for your "don't fear extra Scaps" rule (`13`, double descent is the other half). **Over-provisioning doesn't just avoid overfitting — it makes the optimization itself well-behaved.** A wide, over-parameterized analog network is *easier* to train to convergence than a tight one, not harder. So the resident-weight area you spend on extra capacity pays back twice: compressible (so it still fits) and convergent (so it trains).

---

## Won't it get stuck in a bad local minimum? No — the enemy is saddles, not minima

*Dauphin, Pascanu, Gulcehre, Cho, Ganguli & Bengio, 2014 ([arXiv 1406.2572](https://arxiv.org/abs/1406.2572)).*

The result that dissolved the "local minima" fear. Using random-matrix theory, they showed that in **high dimensions, critical points are exponentially more likely to be *saddle points* than bad local minima** — and the few local minima that exist are nearly all close to the *global* optimum in value. So you almost never get *trapped* in a bad minimum; you get *slowed* on the plateaus around saddles. And escaping saddles is exactly what **noise** does (a noisy step rolls off the saddle's unstable direction).

**For us:** two design implications. (1) **You don't need to find *the* optimum — almost any minimum you reach is good** (most are near-global). That's a relief for a noisy analog learner that will never land precisely. (2) **Noise is the saddle-escape mechanism** — your analog noise, far from blocking convergence, *helps* the optimizer slide off the plateaus that would stall a perfectly deterministic chip. (Connects straight to `17`'s "noise is an asset.")

---

## Will it generalize? Flat minima — and this is the unification with durability

*Flat minima: Hochreiter & Schmidhuber, 1997; Keskar et al., 2017 ([arXiv 1609.04836](https://arxiv.org/abs/1609.04836)); SAM: Foret et al., 2020. Implicit regularization of SGD: Smith et al., 2021.*

Here is the keystone, and it's the most beautiful connection in the whole dossier for your project. Among all the minima that fit the training data, some are **sharp** (the loss spikes up if you nudge the weights a little) and some are **flat** (the loss barely moves under a nudge). **Flat minima generalize better** — and **SGD's noise automatically prefers them**: the randomness in stochastic gradients is an *implicit regularizer* that escapes sharp basins and settles into flat ones (which is why large-batch training, with less noise, generalizes worse — it lands in sharp minima).

Now look at what "flat" *means*: **a flat minimum is one where perturbing the weights barely changes the loss.** That is *exactly the definition of weight-noise robustness.* So:

> **Flat minimum = generalizes well = survives weight perturbation = survives analog noise.** They are the *same property.*

**For us — this fuses `17`/`18` (durability) with this file (generalization) into one target.** You don't optimize for generalization and *separately* for noise-robustness — **you optimize for flatness and get both.** And the tools all point the same way: SGD noise finds flat minima (implicit), Bishop's noise-injection finds flat minima (explicit, `17`), SAM finds flat minima (directly), and *your analog noise during training* finds flat minima (free). Your chip's imperfection, trained against, pushes you toward the minima that are *simultaneously* the most generalizable and the most durable. This single fact justifies the entire "noise is an asset" stance — flatness is the unifying objective.

---

## You *must* choose an inductive bias — which makes your bio bet honest (No Free Lunch)

*Wolpert & Macready, 1997 ([No Free Lunch Theorems for Optimization](https://ieeexplore.ieee.org/document/585893)); Wolpert, 1996 (supervised).*

The theorem that frames every architectural choice you've made. **Averaged over *all possible* problems, no learning algorithm beats any other** — every gain on one class of problems is paid for by a loss on another. The consequence is not nihilism; it's the opposite: **to generalize at all, you *must* build in assumptions about the structure of your data (an inductive bias), and no single bias is universally best.** Convolution assumes spatial locality (`15`); residuals assume identity-near maps; your sparse/local/brain-like substrate assumes the world has the structure brains evolved for.

**For us:** this is the *vindication and the honest framing* of the whole project's premise. You can't escape choosing a bias, so the only question is *which* — and your bet is **"the inductive biases of biological computation (sparsity, locality, prediction, energy-descent) match the structure of the natural world a creature lives in."** No Free Lunch says that bet is not arbitrary *and* not universally safe — it's a real, falsifiable wager that your chip will excel on brain-like problems and (correctly) not on arbitrary ones. That's exactly the scope you already committed to ("not external-benchmark-chasing"). The theorem tells you to **own your inductive bias as the bet it is** — which is what you've been doing.

---

## The shape of the answer (this file)

The optimization floor under "it learns": **(1) wide/over-parameterized nets provably converge** (NTK) — extra Scaps make training *easier*, not just safe; **(2) you won't get trapped** — high-dim critical points are saddles not bad minima, almost any minimum is near-global, and **noise escapes the saddles** (your analog noise helps); **(3) generalization = flatness, and flatness = noise-robustness** — SGD noise / Bishop noise / your analog noise all push toward flat minima that *simultaneously* generalize and survive perturbation, fusing this file with durability (`17`/`18`) into one objective; **(4) No Free Lunch** says you *must* pick an inductive bias, which makes your brain-like substrate a real, honest, scoped bet rather than a universal claim. Your double descent (`13`) is the fifth piece. Together: over-provision freely, let noise find flat minima, own your bias.
