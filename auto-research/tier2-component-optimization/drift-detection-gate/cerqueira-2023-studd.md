# STUDD: a student–teacher method for unsupervised concept drift detection
- **Authors / Year / Venue:** Vitor Cerqueira, Heitor Murilo Gomes, Albert Bifet, Luis Torgo / 2023 / Machine Learning 112:4351–4378 (arXiv 2103.00903)
- **Link:** https://arxiv.org/abs/2103.00903 (journal: https://link.springer.com/article/10.1007/s10994-022-06188-7)
- **Tier / Topic:** tier2 / t2.4 drift-detection gate
- **Relevance:** ⭐⭐⭐⭐⭐ — the trick that makes a **label-free signal wear the error-rate shape DDM already consumes**: no detector swap needed to ship a label-free gate.

## TL;DR
Train a small **student** model to mimic the deployed **teacher's predictions** (not the true labels). At runtime, the student's *disagreement with the teacher* is a label-free "error rate"; feed that meta-error to any standard detector (DDM, Page-Hinkley, ADWIN) and you get unsupervised drift detection with the supervised machinery unchanged. Competitive across 19 data streams.

## The mechanism (how it actually works)
The insight is a signal-shape adapter. Supervised detectors like DDM want a Bernoulli error stream — right/wrong per step — which normally requires true labels. STUDD manufactures one: at training time, fit a student on `(x, teacher(x))` pairs, so the student learns the teacher's *function*. In stream, both predict; `student(x) ≠ teacher(x)` is a 0/1 event whose rate is stable while the input distribution stays in the region where mimicry was learned, and rises when inputs move somewhere the student's copy of the teacher no longer matches. The mimicking error is a proxy for "the world moved under the model," available every step, no labels. When the detector trips, the system retrains (there, with newly-requested labels).

## Key results / claims
- On 19 real/synthetic streams, STUDD is competitive with supervised detection at a fraction of the label cost, and beats input-distribution-only unsupervised baselines that false-fire on benign input shifts.
- Explicitly framed as a **meta-detector**: any off-the-shelf detector consumes the mimicking error.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the awake gate (the committed DDM, P8.1); the trigger bake-off (P8.2).
- **Same as us:** shares our conclusion that the detector layer (DDM) is fine and the *signal* is the design choice; shares the model-conditioned (not raw-input) philosophy that our nuisance test rewards.
- **Different from us:** STUDD trains a second learner with GD. We would not — but we have something better: a **frozen snapshot of the closed-form namer from the last sleep**. Live-SLDA vs snapshot-SLDA disagreement is exactly a student-teacher pair with zero training: the "student" is manufactured by our sleep cycle for free.
- **What we could borrow or test:** the **self-disagreement trigger** — keep the previous sleep's namer weights (one C×d matrix, resident in the crossbar), compare argmaxes each step, feed the 0/1 disagreement to the *unmodified committed DDM*. Label-free, error-rate-shaped, and directional in our sense: disagreement rises only when features move across the *decision structure*, not on nuisance magnitude shifts that both heads ignore identically. Test in the P8.2 harness against MTD 6 (tap-drift) and MTD 14 (labeled error).
- **What contradicts or challenges us:** disagreement measures movement relative to the *old* decision boundary — after several sleeps of benign rotation (P9.0), the snapshot must be refreshed at each sleep or it drifts into permanent disagreement (the same re-anchoring bill DriftLens pays).

## Follow-on leads
- "Unsupervised Concept Drift Detection Using a Student–Teacher Approach" (DS 2020) — the earlier conference version.
- Model-disagreement ensembles for drift (query-by-committee streams).
- Label-scarcity drift detection surveys (verification latency literature).
