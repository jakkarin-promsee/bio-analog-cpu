# Synthesis — The self-generated learning / halt signal ("correctness as a feeling")  (Tier 3)
**The question:** What is the buildable, substrate-native form of a self-generated correctness signal — computable from signals we already produce, grounded so it can't collapse, usable as a halt/gate/learn-trigger — and who is closest?
**Already in `draft6.0/research/`:** the north-star dossier `4-signal.md` maps the four frames (Free Energy/Active Inference, curiosity/compression-progress, World Models, the actor-critic) and parks the P8.2 tap-drift seed. The t3.2 sweep added the halt-adjacent engineering (TRM's one-head BCE halt, EBT's energy-as-verifier, Geiping's zero-training convergence halt). This topic fills what neither covers: **what makes a self-signal *trustworthy*** — the 2022–2026 verifier/calibration/collapse literature.

## The landscape (the engineering view)

Strip the biology and the field's answer to "how does a system know it's right without labels?" has exactly **three information sources**, and every working method is one of them:

1. **Agreement under independent perturbation** (dispersion, not magnitude). Sample the system several times with independent noise and measure whether it returns to the *same answer*. Semantic entropy (Farquhar/Kuhn — Nature 2024) is the strongest label-free wrongness detector in the field, and it is nothing but entropy over meaning-equivalence classes of resampled outputs. Plan2Explore uses the same physics at training time: ensemble disagreement isolates *epistemic* (learnable) uncertainty from aleatoric noise, and self-anneals as data arrives. The consistent finding: **the reliable self-signal is a distribution shape over re-runs, not the height of any single-run score.**

2. **A learned judge fed by sparse objective grounding.** The verifier/PRM line: a separate small model scores the process, trained not on introspection but on labels *diffused from a checkable outcome* — Math-Shepherd manufactures dense per-step labels from Monte-Carlo rollouts to a verifiable final answer; Lightman shows dense process supervision is harder to hack than outcome supervision; the 2025 PRM survey documents the whole field converging on this "outcome-anchored automatic supervision" tier and naming the doctrine (RLVR: prefer deterministic checks wherever they exist).

3. **Cheap internal statistics + statistical calibration.** CALM's halt uses signals we already have (top1−top2 margin; hidden-state saturation = a ‖Δz‖ settling signal) but *never trusts them raw*: a distribution-free hypothesis-testing procedure (Learn-then-Test) sets the threshold against grounded calibration data, yielding a certificate. Kadavath's audit gives the boundary condition: trained/self-rated confidence is well-calibrated in-distribution and **silently miscalibrates under distribution shift** — calibration is a perishable good.

And two hard constraints fence the whole space. **The collapse law (Gao):** optimize anything against a learned proxy signal and true performance rises-peaks-falls, smoothly and predictably, in the distance moved from the anchor — so the feeling may *gate*, never be the *training target*, and distance-from-anchor is the honest trust axis. **The null result (Huang):** a self-signal with no information advantage over the forward pass — same weights re-reading the same output — adds nothing and often subtracts. Every legitimate feeling must name its advantage: independent noise draws, a different timescale, different training data, or an asymmetric (cheaper) check.

## How WE differ  ← the money section

We are unusually well-positioned, for a reason the LLM literature would envy: **their perturbation ensembles are bought with compute; ours come from physics.** Temperature sampling costs k full forward passes; the analog substrate produces thermal noise for free and a settle *is* the resample. And their equivalence-classing needs an NLI model; our namer's discrete read *is* the equivalence class. Second, the field's biggest reliability hole — calibration decays under drift, and their systems have no recalibration organ — is a solved problem in our loop: **sleep already re-fits statistics on schedule.** What we lack is what they have: any verifiable outcome denser than our labeled trickle, and any calibration *procedure* (our thresholds are hand-set, not certified). Our existing signals sort cleanly onto their map: the error-EMA is grounding (source 2's anchor, not a feeling); tap-drift direction is a temporal dispersion signal (source 1, information source = time); the settle-‖Δz‖ is CALM's saturation measure (source 3, "decided" ≠ "correct"); the namer margin and SCFF goodness are raw magnitudes — the tier every strand of this literature marks as the hackable one.

## The ranked recommendation — the buildable self-signal

Ranking by (computable-from-what-we-have × grounded-so-it-can't-collapse × halt/gate-usable):

1. **Re-settle agreement (the semantic-entropy analog) — the halt.** Settle k times under the substrate's own noise; the feeling = agreement of the namer's reads (entropy over named outcomes). Computable from planned parts (settle → name → count); grounded in independent physical noise draws (Huang-legal); dispersion-form (spine-legal); anytime (keep settling until agreement crosses θ). Cost is k× settle energy — find the smallest useful k (likely 3–5).
2. **Tap-drift direction (P8.2, already built) — the learn-trigger.** Label-free, leads error by ~8 steps, nuisance-invariant, direction-form. Its information source is time (now vs sleep anchor) — and per Gao, distance-from-anchor is *the* correct trust axis, so this signal doubles as the trust-horizon meter for every other signal.
3. **Settle-‖Δz‖ convergence — the free v0 halt** (comparator only), but it says "decided," not "correct" — deploy only as the inner loop under signal 1.
4. **A closed-form critic head trained at sleep (the Math-Shepherd move) — the eventual feeling organ.** Ridge/prototype from settled state → "was this named correctly," labels harvested free from sleep-graded trajectories; re-anchored every sleep (killing Kadavath's OOD failure mechanically). PonderNet gives the target semantics ("will more thinking change the answer?") and the energy-budget prior (λ_p = step-energy/decision-budget).
5. **Namer margin / SCFF goodness as confidence — rejected as primary.** Magnitude-form, in-distribution-only, and (goodness) identical to the training objective — the exact Goodhart channel.

**The one grounding safeguard it needs:** *the feeling is a gate, never a target, and its threshold is re-certified at every sleep* — a CALM/Learn-then-Test sweep against the grounded window (labeled trickle + error-EMA), with the certificate's validity horizon tied to accumulated tap-drift, not wall-clock. This single rule blocks all three documented collapse routes: proxy optimization (Gao), introspective delusion (Huang), and drift-decayed calibration (Kadavath).

## The gap / what we haven't tried
- **Re-settle agreement** has never been run — it needs only the recurrent loop prototype + noise + the namer. The natural first experiment of the north-star gate, raced against error/confidence halts (the dossier's deferred P8.2 race, now with a third lane).
- **Threshold certification at sleep** (Learn-then-Test over the grounded window) — closed-form, bolt-on to the existing sleep, upgrades every gate we own from hand-set to certified.
- **Epistemic gating:** fire learning on inter-tap/anchor *disagreement* rather than raw error-EMA — the Plan2Explore fix for the "permanent noise = permanent firing" trap; testable on the P6 all-noisy stream.
- **Trajectory-shaped trust (the PRM idea, continuous form):** count namer read-flips along the settle path; flip-free settles get halt priority (Lightman's product-of-steps, physics edition).
- **The measured hump:** reproduce Gao's rise-peak-fall on our object — gate on a learned signal, push cadence, plot task metric vs accumulated drift; would give a *quantitative* re-grounding rule (cadence from trust budget, not grid).

## Papers (table linking the cards)
| Paper | ⭐ | The one thing it gives us |
| ----- | -- | ------------------------- |
| [Schuster 2022 — CALM](schuster-2022-calm.md) | ⭐⭐⭐⭐⭐ | Our two cheap signals (margin, settle-Δ) suffice for a halt — *if* the threshold is statistically certified against grounded data. |
| [Gao 2022 — RM overoptimization](gao-2022-reward-model-overoptimization.md) | ⭐⭐⭐⭐⭐ | The collapse law: gate-never-target; distance-from-anchor (= tap-drift) is the trust axis. |
| [Farquhar 2024 — Semantic entropy](farquhar-2024-semantic-entropy.md) | ⭐⭐⭐⭐⭐ | The buildable feeling: agreement of re-runs in an invariance space — our noise re-settles + namer read, verbatim. |
| [Wang 2023 — Math-Shepherd](wang-2023-math-shepherd.md) | ⭐⭐⭐⭐ | Grow a dense critic from the sparse labeled trickle by sleep-time rollout grading — no humans needed. |
| [Huang 2023 — Cannot self-correct](huang-2023-llms-cannot-self-correct.md) | ⭐⭐⭐⭐ | The acceptance test: every feeling must name its information advantage or it's introspective noise. |
| [Banino 2021 — PonderNet](banino-2021-pondernet.md) | ⭐⭐⭐⭐ | The learned-halt template + the geometric prior as a literal energy budget on thinking time. |
| [Sekar 2020 — Plan2Explore](sekar-2020-plan2explore.md) | ⭐⭐⭐⭐ | Epistemic (disagreement) vs aleatoric (raw error) — the self-annealing learn-trigger that can't hook on noise. |
| [Kadavath 2022 — Know what they know](kadavath-2022-know-what-they-know.md) | ⭐⭐⭐ | Trained self-confidence miscalibrates under shift — our sleep re-anchoring is the mechanical cure; calibration must be a measured invariant. |
| [Lightman 2023 — Verify step by step](lightman-2023-lets-verify-step-by-step.md) | ⭐⭐⭐ | Score the trajectory, not the endpoint — dense signals are harder to hack. |
| [Zheng 2025 — PRM survey](zheng-2025-prm-survey.md) | ⭐⭐⭐ | The field map: everyone converged on outcome-anchored automatic supervision; pure self-consistency of a judge with itself is the flagged hackable tier. |

## Leads spawned
- **Learn-then-Test / conformal risk control under drift** — the calibration machinery as its own topic (Angelopoulos 2021; weighted conformal under covariate shift). The certified-gate enabler.
- **Semantic Entropy Probes (Kossen 2024)** — amortizing an expensive agreement signal into a cheap learned shadow; the k-settle → 1-read compression for our halt.
- **Reward-hacking theory (Skalse 2022)** — formal conditions for unhackable proxies; the theory backing for gate-vs-target.
- **Generation-verification gap** — for which task families is verification cheaper than generation? (decides where a same-substrate verifier is legal).
- **PRM-overoptimization (2024–2025)** — does dense supervision delay Gao's hump, and by how much?
- **Search-pressure hacking of halts** — once the loop keeps the best-feeling settle, the feeling is under optimization; needs its own design rule (flagged by the PRM survey).
