# Deep Double Descent: Where Bigger Models and More Data Hurt
- **Authors / Year / Venue:** Preetum Nakkiran, Gal Kaplun, Yamini Bansal, Tristan Yang, Boaz Barak, Ilya Sutskever / 2019 / arXiv (ICLR 2020)
- **Link:** https://arxiv.org/abs/1912.02292
- **Tier / Topic:** tier5 / t5.2 learning-as-compression
- **Relevance:** ⭐⭐⭐⭐ — deep double descent in real nets, extended to epochs and sample count; grounds the author's "over-provisioning is safe" beyond Belkin's kernel setting.

## TL;DR
Double descent is not a curve you see only in width — it appears along **model size, training epochs, and even dataset size**, all unified by one axis: **effective model complexity (EMC)**. Test error peaks when EMC ≈ the number of training samples (the interpolation threshold) and descends on both sides. Crucially, near that threshold, **more data or more training can *hurt***.

## The mechanism (how it actually works)
Define **effective model complexity** as the largest sample count on which the training procedure still reaches ~zero training error. Plot test error against EMC: in the **under-parameterized** regime the classic bias-variance U-curve holds; at the **interpolation threshold** (EMC ≈ n samples) the model can *just barely* fit the data, so it fits it in a brittle, high-variance way and test error **peaks**; in the **over-parameterized** regime (EMC ≫ n) there are many zero-training-error solutions and SGD's implicit bias selects a smooth, low-norm — i.e. **compressible** — one, so test error descends again. Because EMC grows with *epochs* too, the same peak appears mid-training (**epoch-wise double descent**): a model can get worse before it gets better. And because the threshold is at EMC ≈ n, adding samples can *move you onto the peak* (**sample-wise double descent**), the "more data hurts" regime. Label noise sharpens all of it.

## Key results / claims
- One phenomenon, three axes (width, epochs, samples), unified by EMC.
- The peak sits at the interpolation threshold; over-parameterization is the *good* side.
- Regimes where **more data or longer training hurts** near the threshold — a real, reproducible effect in ResNets/CNNs/Transformers.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** SCFF bulk sizing, the double-descent intuition, the sleep/consolidation cadence, P11 scaling.
- **Same as us:** confirms in real nets what the author re-derived — **over-provisioning capacity is safe and helpful** because the learner prefers the compressible fit. Extra Scaps do not cause overfitting on the over-parameterized side. Our analog substrate's natural smoothing (saturation, leak, noise) is exactly such a low-norm bias.
- **Different from us:** their axes are dataset-static (epochs, fixed n, fixed width); our bulk is frozen and streamed. The relevant warning for us is **epoch-wise / sample-wise**: our *namer re-fit cadence* (grid-4) and the growing stream length are EMC-like axes where a threshold peak could hide.
- **What we could borrow or test:** watch for a **cadence-wise or stream-length double descent** — is there a sleep frequency or class-count where OURS gets transiently *worse* before recovering (the P10 §10 cliffs at 6→7 and 15→16 smell like threshold effects)? EMC gives a language for those cliffs.
- **What contradicts or challenges us:** "more data hurts near the threshold" is a caution against assuming monotone improvement with stream length — our capacity/cadence sits somewhere on this curve, and we have not located the peak.

## Follow-on leads
- Belkin et al. 2019 (the kernel-regime origin, already in our dossier) — the theory companion.
- Epoch-wise double descent × continual re-fit cadence — a testable interaction for our sleep loop.
- "Norm-based capacity control" (φ-curve) papers — capacity measured by norm, not parameter count.
