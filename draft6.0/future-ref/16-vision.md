# 16 — A retina / vision front-end with predictive learning (far-future)

> Your far-future plan: build a **retina + CNN decoder** as the input, and let the model **learn by predicting the image** — because vision is *less abstract than language*, and a creature-like sensory front-end lets you copy real developmental mechanisms (parent-teaching, baby-behavior). You flagged this as "almost the last stage," so this file is **short — the instinct is right, here's the one refinement and where it plugs in.** Not a plan; a compass bearing.

---

## The instinct is sound, on two counts

1. **"Learn by predicting the input" is one of the strongest self-supervised signals there is.** Predicting the next frame / the missing part forces the model to learn the *structure* of the visual world without labels — it's **predictive coding** (`3-recurrence.md`, `4-signal.md`) applied to vision, and it's exactly how the cortex is thought to learn. The video-prediction literature (PredNet; Dense Predictive Coding) confirms it: *future-frame prediction is a complete representation-learning objective.*
2. **Vision-before-language is the right order for a creature.** Language is a compressed, late, abstract layer; grounding a mind in **sensory prediction** first (then letting symbols attach to grounded representations) is the developmental order, and it's what makes "copy parent-teaching / baby-behavior mechanisms" even possible — those mechanisms operate on *grounded sensorimotor experience*, not on tokens. This is the **Perception module** of LeCun's architecture (`6-architectures.md`), feeding the world-model loop.

---

## The one refinement that saves the whole thing: predict the *representation*, not the *pixels*

*Dense Predictive Coding (Han et al., 2019, [arXiv 1909.04656](https://arxiv.org/pdf/1909.04656)); PredNet; and I-JEPA (`7-encoding.md`).*

This is the single most important thing to carry forward, and it's the same lesson as `7-encoding.md`: **don't predict raw pixels — predict the learned representation of the future.** The reason is the **under-determined future problem**: from one frame, *many* next frames are possible (a leaf could blow left or right). If you train the model to predict exact pixels, it's forced to model **unpredictable detail and noise** — and either it blurs everything (averaging the futures) or it memorizes noise (the "lie to itself" failure from `7`). Predicting the *representation* (the embedding) lets the model say "something leaf-shaped moves" without committing to every pixel — it predicts what's *predictable* and ignores what isn't. **Dense Predictive Coding** does exactly this (predict future embeddings, with a curriculum that predicts further ahead with less context); I-JEPA is the still-image version.

**For us:** retina → encode (SCFF/CNN front-end) → **predict the future *encoding*, score by prediction error** (which *is* the correctness/feeling signal, `4-signal.md`) → that error trains the encoder *and* drives the thinking loop. The retina plan and the phase-2 brain are the **same loop** with a camera on the front: perception encodes, the world-model predicts the next encoding, the surprise is the learning-and-feeling signal. You don't build a separate vision system; you point the existing predictive loop at pixels.

---

## The developmental angle (parent-teaching, baby-behavior) — real, and it has a field

Your "push parent-teaching and baby-behavior mechanisms into it" is **developmental robotics / curriculum learning** — a real research tradition (start with simple stimuli, scaffold up; let a "caregiver" shape the reward/attention; learn sensorimotor contingencies before abstractions). It pairs naturally with **curiosity/intrinsic motivation** (`4-signal.md`): a baby explores what's *learnable-but-not-yet-learned* (prediction-error-as-reward), and a parent **shapes the curriculum** by controlling what the baby is exposed to and when. That maps onto your **grounding signal** (the parent is an external corrector) plus **curiosity** (the internal drive). Far-future, but the pieces are the ones you've already gathered.

---

## The shape of the answer (this file)

A retina/vision front-end with predictive learning is a **right and well-supported far-future direction** — predicting the input is a top self-supervised signal, and grounding in vision before language is the correct developmental order. The **one refinement that matters**: predict the **representation of the future, not the pixels** (Dense Predictive Coding / I-JEPA), or the under-determined future forces the model to model noise and lie to itself. Built that way, the **vision front-end isn't a separate system — it's the phase-2 predictive loop with a camera on it**: retina → encode → predict next encoding → surprise = the learning-and-feeling signal. The **parent-teaching / baby-behavior** instinct is *developmental robotics + curriculum + curiosity*, and it sits right on top of the grounding and intrinsic-motivation pieces you already have. Keep it on the horizon; don't build it until the simple loop thinks.
