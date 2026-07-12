# Unsupervised Concept Drift Detection from Deep Learning Representations in Real-time (DriftLens)
- **Authors / Year / Venue:** Salvatore Greco, Bartolomeo Vacchetti, Daniele Apiletti, Tania Cerquitelli / 2024 (rev. 2025) / IEEE TKDE (arXiv 2406.17813)
- **Link:** https://arxiv.org/abs/2406.17813
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐⭐⭐⭐ — the purpose-built label-free representation-drift detector that **landed exactly on our validated tap-drift direction signal in P8.2**; also ships the drift-*magnitude* curve we don't have.

## TL;DR
DriftLens detects concept drift **without labels** by monitoring distribution distances between a model's internal embeddings and per-label reference distributions estimated offline. It runs in real time (5×+ faster than prior detectors), wins 15/17 detection use cases, and produces a continuous **drift curve** (correlation ≥ 0.85 with true drift) plus representative drifted samples as explanations.

## The mechanism (how it actually works)
Two phases. **Offline:** take the historical (training) set, extract the classifier's embeddings, reduce with PCA, and fit **one multivariate Gaussian per predicted label** plus a global one — means and covariances become the *reference distributions*; threshold values are calibrated on held-out reference windows. **Online:** for each incoming window, extract embeddings, fit the same per-label Gaussians on the window, and compute a distribution distance (Frechet-style, from the means and covariances) against the reference — per label and overall. The per-label breakdown says *which class's region of feature space moved*; the running distance over windows is the **drift curve** (a magnitude signal, not just a binary trip); crossing the calibrated threshold is the detection event. No labels are consumed anywhere — the model's own predicted labels partition the space.

## Key results / claims
- Beats prior drift detectors in **15/17** use cases across text/image/speech deep classifiers.
- **≥5× faster** than competing detectors — designed for real-time windows.
- Drift curves track injected drift with **correlation ≥ 0.85**; also selects representative drift samples as explanations.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the awake gate (P8.1/P8.2); the parked class-direction tap-drift trigger; sleep sizing (P8.3/P9).
- **Same as us:** P8.2 ran DriftLens as the external reference and it **confirmed our direction signal** (the card's words: "DriftLens lands exactly on it"). Its per-label distances are the published, engineering-native version of our class-direction tap statistic: both partition feature drift by class instead of pooling it into one magnitude (our magnitude null false-fires on 94% of nuisance steps; their per-label design exists for the same reason).
- **Different from us:** DriftLens needs PCA + per-label covariance distances per window (matrix work per check); our tap statistic is a projection onto class directions the SLDA namer already maintains — cheaper. DriftLens's references are fixed offline; our bulk drifts *by design*, so references must re-anchor at sleep or false-fire on benign rotation (P9.0: the bulk rotates without forgetting).
- **What we could borrow or test:** (1) the **drift curve as a magnitude signal** — size the sleep response (how much LUT to re-fit, λ_ema) by measured drift rather than fixed grid-4; (2) the **offline threshold-calibration recipe** (calibrate trip level on reference windows → an interpretable FAR knob, replacing DDM's Bernoulli thresholds when the input is a continuous distance); (3) re-anchor references at each sleep, which our sleep already schedules for free.
- **What contradicts or challenges us:** nothing head-on — but it shows the "validated but unshipped" trigger has a published, deployable form; the excuse that "DDM consumes an error rate" does not survive this paper (threshold the distance directly).

## Follow-on leads
- Frechet-distance drift scores for embeddings (FID-family) as a general magnitude meter.
- Per-label drift localization → class-conditional *partial* sleep (re-fit only moved classes).
- The authors' earlier "Drift Lens" demo paper (2021) for the streaming-windows engineering details.
