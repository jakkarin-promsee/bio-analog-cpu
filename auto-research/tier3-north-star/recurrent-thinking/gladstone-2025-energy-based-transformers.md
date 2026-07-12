# Energy-Based Transformers are Scalable Learners and Thinkers (EBT)
- **Authors / Year / Venue:** Alexi Gladstone, Ganesh Nanduru, Md Mofijul Islam, Peixuan Han, Hyeonjeong Ha, Aman Chadha, Yilun Du, Heng Ji, Jundong Li, Tariq Iqbal / 2025 / arXiv Jul 2025
- **Link:** https://arxiv.org/abs/2507.02092
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles"
- **Relevance:** ⭐⭐⭐⭐⭐ — a **learned scalar energy as the verifier** = "correctness is a feeling," implemented; thinking = descend the energy until it bottoms out.

## TL;DR
Train the transformer not as a predictor but as an **energy function** E(context, candidate): a scalar compatibility score between an input and a candidate prediction. Inference is optimization — start from a guess and run gradient descent *on the candidate* until the energy converges. "Thinking longer" = more descent steps; "self-verification" = score candidates and keep the lowest-energy one. Claims better training-scaling than standard transformers and inference-time gains that grow on out-of-distribution data.

## The mechanism (how it actually works)
Classic nets map x → y in one pass; the compute per answer is fixed. EBT learns the *landscape* instead: a scalar E over (x, y) pairs, low where y fits x. Prediction becomes: initialize y (noise or a cheap guess), then iterate y ← y − η∇_y E(x, y) until the energy stops falling. This unbundles three things System-2 needs: (1) **dynamic compute** — descent steps are spent per-problem, not fixed by architecture; (2) **uncertainty** — the energy value itself says how well the current answer fits, continuously, even in continuous state spaces; (3) **verification** — generation and checking are the same object, so the model can propose many candidates and *pick* by energy. Works across modalities (text, video) without extra supervision. Trained by making the descent process itself differentiable (backprop through the optimization), which is the expensive part.

## Key results / claims
- Scaling during pretraining: up to ~35% higher scaling rate than the Transformer++ recipe w.r.t. data, batch, params, depth, compute (their headline claim).
- Inference-time "thinking" improves language-task performance by ~29% more than standard transformers given equal extra compute; energy-verified generation beats diffusion transformers on image denoising with ~99% fewer forward passes.
- Thinking gains are *larger out-of-distribution* — iterative verification generalizes where one-pass prediction degrades.

## How it relates to us
- **Organ / phase touched:** north-star loop + the halt signal + correctness-as-feeling; North-star 21 (the energy view).
- **Same as us:** the north-star sentence "correctness is a self-generated feeling" is here as engineering: the feeling = a learned scalar energy, low when the answer fits. The halt has a principled trigger — **stop when E stops falling** — and the same scalar prices confidence for free. And gradient *flow* on an energy is what analog circuits do natively (a resistive network relaxing IS descending its co-content/energy function); their digital descent loop is our physics.
- **Different from us:** the energy is a full transformer trained by backprop-through-optimization — far off-substrate; our energy would have to be structurally cheap (quadratic/prototype-shaped: distance-to-LUT-attractor, namer margin), not a learned deep landscape.
- **What we could borrow or test:** (1) halt v1: monitor a scalar readout (namer top1−top2 margin, or distance-to-nearest-prototype) along the settle and stop when it plateaus — an EBT-shaped halt with zero new training; (2) the verification asymmetry — generate cheap candidate states, score with the closed-form namer, keep the best — verification is closed-form even when generation isn't; (3) their OOD result predicts our loop should help most on the noisy/shifted streams where P6/P11 found the floors.
- **What contradicts or challenges us:** EBT's power comes from *learning* the landscape end-to-end; a fixed/closed-form energy (prototype distance) may make the settle trivial (one basin per class, no multi-step reasoning). The open question: how much thinking can a *structured* energy support?

## Follow-on leads
- Du & Mordatch — energy-based models as compositional reasoners (the lineage).
- Hopfield-network energy = our LUT recall energy (bridge to t3.1).
- LeCun's JEPA/EBM position papers — the "inference as optimization" world-model frame.
