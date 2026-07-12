# Online Training Through Time for Spiking Neural Networks (OTTT)
- **Authors / Year / Venue:** Mingqing Xiao, Qingyan Meng, Zongpeng Zhang, Di He, Zhouchen Lin / 2022 / NeurIPS 2022
- **Link:** https://arxiv.org/abs/2210.04195
- **Tier / Topic:** tier4 / t4.3 neuromorphic-spiking online learning
- **Relevance:** ⭐⭐⭐⭐ — the "make surrogate-gradient SNN training online" workhorse; derives a **three-factor Hebbian** update from BPTT with **constant memory** — the engineering-native version of e-prop for deep feed-forward SNNs.

## TL;DR
OTTT trains deep SNNs with surrogate gradients but **forward-in-time**: instead of storing every time-step to backprop through them, it tracks a running presynaptic-activity trace and applies an instantaneous-loss gradient at each step. Memory is **constant in the number of time steps** (vs BPTT's linear blow-up), and the resulting update has three-factor Hebbian form → hardware-friendly.

## The mechanism (how it actually works)
BPTT for an SNN unrolls the net across T time steps and backprops through all of them — memory grows with T, and you need the whole sequence before you can learn. OTTT observes that if you accumulate a **presynaptic activity trace** `â` (a leaky sum of past presynaptic spikes) and use the *instantaneous* loss at each step, the online update at step t approximates the BPTT gradient:

`ΔW ∝ (instantaneous output error) · (surrogate-derivative of postsynaptic spike) · (presynaptic trace â)`

That's a **three-factor product**: error (broadcast) × post-activation gate × pre-trace. Only `â` must be carried forward (one number per presynaptic unit), so memory is O(1) in T. Two variants: OTTTₐ (tracks a spatial gradient) and OTTTₒ (fully online, matches the tracked gradient direction to BPTT). It provably tracks the descent direction under mild conditions.

## Key results / claims
- Benchmarks: CIFAR-10, CIFAR-100, ImageNet, CIFAR10-DVS — competitive accuracy at **small time steps** (T=6).
- **Constant training memory** w.r.t. time steps (the headline win over BPTT).
- Update is explicitly three-factor-Hebbian → the paper markets it for neuromorphic on-chip training.

## How it relates to us
- **Organ / phase touched:** north-star temporal loop; the pre-activity trace = our leaky-cap primitive again.
- **Same as us:** the *pre-synaptic trace* is another leaky-capacitor / EMA register — the substrate atom we already have. The three-factor "error × gate × trace" form is the same skeleton as our "namer error × bulk activation".
- **Different from us:** OTTT is still **surrogate gradient descent** — its whole contribution is *keeping* the gradient while making it online and memory-cheap. Our P7 result is that the namer needs *no* gradient. OTTT is the spiking world's answer to "cheap online gradient"; we answered the same online-learning problem by dropping gradient (closed-form) instead of streamlining it. Also spiking + explicit time axis, which our current object lacks.
- **What we could borrow or test:** if a future rung *does* want an online gradient on a temporal stream, OTTT's "carry one pre-trace, use instantaneous loss" is the minimal recipe and maps onto our registers directly. It's the concrete template for "online GD on the substrate" if we ever need one.
- **What contradicts or challenges us:** OTTT shows online surrogate-gradient training is now cheap and works to ImageNet — it weakens any claim that "online gradient on a temporal net is impractical". Our differentiator has to stay the *closed-form / no-direction-per-weight* thesis, not "gradients are too expensive online".

## Follow-on leads
- Meng et al. 2023 SLTT (sibling card) — same authors, pushes the "temporal backprop barely matters" idea further.
- Yin, Corradi & Bohté 2021/2023 "Accurate online training via Forward Propagation Through Time (FPTT)" — the receptance/liquid-state online-training cousin.
- Kag & Saligrama 2021 — FPTT for general RNNs (the non-spiking parent).
