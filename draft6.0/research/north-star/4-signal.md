# 4 — The learning signal / "correctness as a feeling"

> Your deepest idea: *correctness is a self-generated, learned feeling, not an external label.* The field has a name for almost exactly this — **prediction-error / surprise minimization** — and a master frame (**Active Inference**) that *also* explains the hardest part of your vision: **self-verification** (the mind inventing its own test cases). This is the file where your intuition meets a real research program.

---

## The Free Energy Principle & Active Inference — the master frame

*Friston, 2006–present. Overviews: [Free energy principle (Wikipedia)](https://en.wikipedia.org/wiki/Free_energy_principle); [FEP for perception and action: a deep-learning perspective](https://pmc.ncbi.nlm.nih.gov/articles/PMC8871280/).*

The single closest theory to "correctness is a feeling." An agent has an internal model of the world; the gap between what it predicts and what it senses is **surprise** (formally, *variational free energy*). The principle: **everything the brain does minimizes that surprise.** And there are exactly **two ways** to minimize it:

1. **Perception** — change your *beliefs* to match the world (update the model). 
2. **Action** — change the *world* to match your beliefs (act so your predictions come true).

The "I get it" feeling **is** free energy collapsing — surprise dropping to near zero. And *learning* is the slow version of perception: re-shaping the model so the world stops surprising you.

**For us, two huge things:**
- **The feeling is computable and grounded.** "Correctness" = low free energy = small prediction error against reality. This is exactly the *grounded* version we discussed — the feeling can't lie for long because surprise is measured against actual sensory input.
- **It explains your derivative example — the self-verification.** Active inference includes **epistemic action**: an agent *acts to reduce its own uncertainty*. When you weren't sure "2x is the slope of x²," you **generated test points** (x=2,3,4,5) — that is epistemic action, choosing experiments that most reduce your uncertainty. Active inference is the existing theory of *the mind running its own experiments.* It's the formal home of the hardest part of your vision. (Caveat: full active inference is heavy math and not yet a clean hardware recipe — take the *frame*, not a turnkey method.)

---

## Curiosity & compression progress — prediction error *as the reward*

*Pathak, Agrawal, Efros & Darrell, 2017 ([ICM, PMLR](https://proceedings.mlr.press/v70/pathak17a/pathak17a.pdf)); Schmidhuber, 1991–2010 (compression progress / "formal theory of creativity").*

The apply-side of the feeling. **Pathak's Intrinsic Curiosity Module** gives an agent a *self-generated reward* equal to its **prediction error** — it seeks out states it can't yet predict, and the error shrinks as it learns them (so the reward is "learning progress"). **Schmidhuber** generalizes this: *interesting* = compressible-but-not-yet-compressed; the drive is **compression progress**, and he argues this one principle explains curiosity, novelty, surprise, beauty, humor, even art and science. Crucially, the reward is **error in a *learned feature space***, not raw pixels — so it ignores noise it can't control.

**For us:** this is the **engine** for a model that *wants* to keep learning — the "never freeze" drive made concrete. The correctness-feeling has a twin: a **curiosity-feeling** (high prediction error = "interesting, go learn it") that *seeks* the exact data the model is missing. Together they're a self-supervising loop: curiosity points at what you don't know, correctness confirms when you've got it. Note the "learned feature space" detail — it's why grounding must be against *features*, not raw input, and your SCFF gives you exactly that feature space.

---

## World Models — give the mind a simulator to verify *inside*

*Ha & Schmidhuber, 2018 ([arXiv 1803.10122](https://arxiv.org/pdf/1803.10122)); Dreamer lineage: Hafner et al., 2020–2023.*

The substrate for self-verification. Learn a compact internal model of the world in three parts: **V** (a vision encoder compressing input to a small latent), **M** (a recurrent net predicting the *next* latent — the "what happens next" engine), and **C** (a tiny controller acting on V+M). The headline result: the agent can be **trained entirely inside its own "dream"** — M run as a simulated environment — and then deployed in reality (CarRacing solved; later **DreamerV2** beat humans on Atari, **DreamerV3** generalized across domains with no tuning).

**For us:** "thinking" in your derivative example *was running an internal simulation* (compute x² at points, watch the trend). A **world model is that internal simulator** — the place a mind tests "what if" without touching reality. This is the apply-side of your self-verification phase: V is your SCFF encoder, **M is exactly the prefrontal↔hippocampus prediction loop**, and "dreaming" is sleep doing more than replay — it's *imagining*. It also says: the recurrent M and the sleep mechanism are the same organ used two ways (predict-forward while awake, replay/imagine while asleep).

---

## The learned critic — the feeling is a trainable model, not a fixed rule

*Actor-Critic: Sutton & Barto; Barto et al., 1983 onward.*

The plain-ML mirror of your "I learned what correct feels like from my parents." In actor-critic RL, the **critic** is a *separate learned network* that estimates how good a state/action is; it's trained by **prediction error** (TD error) against actual outcomes, and it teaches the actor. The "value" is not a built-in truth — it's **learned from experience and corrected by reality.**

**For us:** this nails the structural point — the correctness-feeling should be its **own small learnable model** (a critic), trained by grounding events, not a hand-coded threshold. It can be wrong (you can feel sure and err), it improves with feedback (you get better at knowing when you're right), and it sits *beside* the main brain, not inside it. That is exactly your "feeling is taught, and fallible."

---

## The shape of the answer (this file)

The correctness-feeling, for us, is: **the collapse of prediction error / free energy** when the loop settles (Active Inference) — *grounded*, because it's measured against real sensory input, so it can't lie for long. Its twin is a **curiosity signal** (high prediction error = "go learn this") that drives the never-freeze hunger (Pathak/Schmidhuber). It is implemented as a **small learned critic** trained by grounding (actor-critic), not a fixed rule — so it's taught and fallible, exactly as you said. And the **self-verification** you described (inventing test cases) is **epistemic action over a world model**: a learned internal simulator the mind runs experiments inside. Active inference is the one frame that ties all of this together — read it as the theory your shower-thoughts were re-deriving.
