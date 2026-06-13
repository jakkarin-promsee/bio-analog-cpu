# 3 — The loop / "think many times until it settles"

> Your question: *"Should it be a full LSTM? How recurrent?"* My argued answer: **not LSTM-as-the-core.** The brain (and your orange-car example) runs the loop *many times on one input* until it stops changing — that's **fixed-point / equilibrium** computation, which **analog hardware does for free** and which LSTM (one step per input) and transformer (no depth-recurrence) both miss. Keep an LSTM-style *gate* for cross-time memory; don't make it the thinker.

---

## Deep Equilibrium Models (DEQ) — solve for the fixed point directly

*Bai, Kolter & Koltun, 2019, NeurIPS ([arXiv 1909.01377](https://arxiv.org/abs/1909.01377)).*

The apply-side keystone for "settle to equilibrium." Observation: a deep weight-tied network's hidden state tends toward a **fixed point** `z* = f(z*, x)` as you stack more layers. DEQ skips the stacking entirely and **solves for `z*` directly** with a root-finder — equivalent to an *infinite-depth* network — then back-propagates through the fixed point analytically (implicit differentiation), so it needs **constant memory regardless of "depth."** "Thinking" becomes *find the equilibrium*, and how many iterations that takes is adaptive.

**For us:** this is the formal version of "run the loop until it settles = I get it." And here is the punchline your whole project rests on: **an analog circuit finds a fixed point by physically relaxing to it.** A DEQ's expensive root-find is your substrate's *free* settling. So phase-2 thinking isn't a digital recurrence you simulate step-by-step — it's a network you let *physically equilibrate*. DEQ is the math that licenses reading your analog settle as computation.

---

## Equilibrium Propagation (EqProp) — and the settle *also* gives you the gradient

*Scellier & Bengio, 2017 ([Frontiers](https://www.frontiersin.org/articles/10.3389/fncom.2017.00024/full)). (Also in `../concept/equilibrium-propagation.detail.md`.)*

An energy-based network settles to a free equilibrium; then you **nudge** the output slightly toward the target and let it settle again; the **difference between the two equilibria, measured locally at each synapse**, *is* the gradient (exactly, in the small-nudge limit). No backward pass — two relaxations and a local subtraction.

**For us:** EqProp is the leading "exact gradient from local analog physics" candidate, and it stacks perfectly with DEQ: the *same* settling that does your thinking can *also* produce a learning signal, locally, with no backprop. For a phase-2 loop that must learn online while it thinks, this is the natural learning rule for the recurrent core — it's literally physics doing both jobs. (It does need a settling phase and roughly symmetric feedback — the costs to watch.)

---

## Predictive coding — iterative inference as the brain's default

*Rao & Ballard, 1999; as a backprop-approximation: Whittington & Bogacz, 2017. (Also in `../concept/predictive-coding.detail.md`.)*

The brain as a stack of layers each **predicting the layer below** and passing **only the prediction error** upward. "Perceiving" is an *iterative* process: the network relaxes its internal estimates until prediction error is minimized across all layers. It provably approximates backprop, but the mechanism is **local error + iterative settling**, not a global backward sweep.

**For us:** predictive coding is the bridge between "settle to equilibrium" (this file) and "correctness is a feeling" (`4-signal.md`): the thing being minimized *is* prediction error, and when it bottoms out, that's the "I get it." It's also the most biologically literal model of the prefrontal↔sensory loop you're after — top-down prediction, bottom-up error, settle.

---

## Adaptive Computation Time & PonderNet — *learn* when to stop

*ACT: Graves, 2016 ([arXiv 1603.08983](https://arxiv.org/abs/1603.08983)); PonderNet: Banino, Balaguer & Blundell, 2021 ([arXiv 2107.05407](https://arxiv.org/abs/2107.05407)).*

The halting mechanism. **ACT** lets a recurrent net take a *variable* number of compute steps per input, learning to "ponder" longer on harder inputs. **PonderNet** makes this clean: it treats halting as a **probabilistic latent variable** (a learned per-step "should I stop now?"), giving stable, unbiased training and strong generalization on algorithmic reasoning — spend more steps when the problem is hard, stop early when it's easy.

**For us:** this is **the "stop when the feeling fires" mechanism, made learnable.** Your loop settles (DEQ) and a learned halting head decides *enough* — and crucially, PonderNet shows you can *train* that stopping signal end-to-end. Map: the halting probability **is** the correctness-feeling crossing threshold. Variable ponder-time = your "we could stop at step 8 but I kept going." This is the most direct apply-side handle on your halting idea.

---

## Universal Transformer — recurrence in *depth*, with halting

*Dehghani, Gouws, Vinyals, Uszkoreit & Kaiser, 2018 ([arXiv 1807.03819](https://arxiv.org/abs/1807.03819)).*

A transformer made **recurrent in depth**: apply the *same* block over and over to refine the representation, with **ACT** deciding per-token how many refinement steps to take. It's "transformer" and "iterative settling" combined — and it shows the attention machinery you already have (the LUT/Hopfield recall) composes naturally with a settle-until-done loop.

**For us:** evidence that you don't have to *choose* attention-vs-recurrence — you **iterate** an attention-based block until it settles. Your LUT recall + a repeated refine step + a halt = a Universal-Transformer-shaped thinker, but with the iteration done by analog relaxation instead of repeated digital passes.

---

## LSTM / GRU — keep the gate, not the throne

*Hochreiter & Schmidhuber, 1997; GRU: Cho et al., 2014.*

The classic gated recurrent nets. Their genuine invention is the **gate** — a learned "remember this / forget that" valve that lets information survive across many timesteps without vanishing. But, as you said yourself, an LSTM does **one gated step per input** and folds memory and computation into the *same* state — it does not *iterate to a fixed point* on a single input the way thinking does.

**For us:** your instinct is right. **Demote LSTM from the core to a component.** Take its **gate** for cross-time memory control (it's the cheap PBWM, `2-controller.md`) and let the *thinking* be equilibrium settling (DEQ/EqProp/predictive coding) instead. LSTM is a *projection* of the recurrent brain onto one step; phase 2 wants the full settle.

---

## The shape of the answer (this file)

Recurrence, for us, is **not "use an LSTM."** It is: **iterate the loop until it settles to a fixed point** (DEQ) — which your analog substrate does as free physical relaxation — using **local prediction-error / energy settling** that *also* yields the learning signal (EqProp, predictive coding), with a **learned halt** that fires when the error bottoms out (PonderNet) — *that halt is the correctness-feeling.* Keep the **LSTM gate** only for carrying memory across time. The inner loop is analog physics; the outer loop is feeling-gated search.
