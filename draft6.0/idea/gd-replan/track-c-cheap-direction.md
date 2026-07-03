# Track C — the cheap global direction ("eventually we want backward somewhere")

> **The job:** the author's answer 2 — *"SCFF runs forward great, but eventually we want backward somewhere; real
> neurons are half-local, half-global, dopamine-modulated; nobody knows exactly how."* This track is the menu of
> ways to inject a **global** coordinating signal **cheaply and forward-ish**, to *bend the tunnel* (give deep
> layers a reason to keep serving the class) — under the **hard rule: never rewrite the SCFF stream** (P2.5).
> Most of this is **already in the repo**; the new pieces are one 2025 paper and the framing.

---

## C0 · The principle (why a little global is allowed, and where it goes)

The Tunnel Effect and the myopia diagnosis both say the same thing: deep layers drift because **nothing tells them
what the whole network wants.** A *bounded* global signal fixes that. The author already accepts it for the GD side;
the question is the *cheapest* global signal that (a) doesn't need a backward pass through the SCFF bulk, (b) doesn't
need weight transport (symmetric backward weights — biologically and physically implausible), and (c) **reads/gates,
never overwrites** the SCFF activations.

Two shapes qualify, and they map to biology:
- **Top-down broadcast** — the top (or a global scalar) is *broadcast down* as a *reference/modulator*. One wire,
  detached. (≈ a neuromodulator / attention bias.)
- **Three-factor local update** — each synapse keeps a local **eligibility trace** (which it already has: a leaky
  cap), and a **global signal** (one broadcast number, ≈ dopamine) gates *when/how much* it learns. Local mechanics,
  global timing. **This is the author's "half-local, half-global, dopamine" intuition, exactly.**

## C1 · Feedback Alignment / DFA — global error without a real backward pass

- **Feedback Alignment (FA)** (Lillicrap et al 2016) and **Direct Feedback Alignment (DFA)** (Nøkland 2016) — replace
  the transposed-weight backward pass with **fixed random feedback weights**; the network *learns to align* with
  them. DFA sends the **output error directly to every layer** through its own random matrix — **no weight
  transport, no layer-by-layer chain.** *(In the repo's `research/survey/feedback-alignment.detail.md`.)*
- **For us:** DFA is the canonical "cheap direction": a **global error broadcast to all SCFF layers at once**, one
  random projection per layer (a fixed crossbar — substrate-cheap). It would give deep layers the *"what the output
  wants"* signal the tunnel lacks. **But:** DFA is *supervised* (needs the output error) and historically **doesn't
  scale to hard tasks / conv** — so it's a *coordination* signal, not a replacement for SCFF.
- **SCFF-flow-safe?** ⚠ **only if it updates weights via a local rule, not by rewriting activations.** DFA computes a
  per-layer update from `(random-projected error × local activation)` — that's a *weight update*, the stream itself
  isn't overwritten. ✅ in that form. Forbidden if used to *replace* the forward activations.

> **⚠ CORRECTION (2026-06-29, post deep-lit pass — authoritative file: [`lit-cheap-credit.md`](lit-cheap-credit.md)).**
> Two errors below are fixed inline: **(1)** `2601.21683` was mis-labelled "Direct feedback / top-down" — its real
> title is **"Can Local Learning Match Self-Supervised Backpropagation?"** (Gerstner/Bellec, ICML 2026), and it
> reaches BP-SSL parity by **fixing the local objective/update**, NOT by a top-down wire — so it argues *against* C2
> being first and *for* the objective-side fix. **(2)** FTP (C3) was tagged "likely flow-safe"; it is **NOT** — target
> propagation drives activations to targets = the forbidden stream-rewrite. **Net re-ordering:** the cheapest
> global-credit lever is **objective-side** (a detached top-down *consistency term in the local InfoNCE*, preserving
> class direction — see `lit-cheap-credit.md` §D/§F and `replan.md` T3.2), with C2's broadcast wire and DFA *below* it.

## C2 · Top-down broadcast — the global version of the coordination window

- **[corrected]** The objective-side cousin — **"Can Local Learning Match Self-Supervised Backprop?"**
  ([2601.21683](https://arxiv.org/abs/2601.21683), ICML 2026) — does *not* add a top-down wire; it makes the **local
  update align with the global BP-SSL update** and hits parity. The genuine top-down-*broadcast* idea (top layer's
  activations as a detached reference for all lower layers) is still valid and forward-only, but the 2026 evidence
  says try the **objective-side** form first. **Layer Collaboration** ([2305.12393](https://arxiv.org/abs/2305.12393))
  is the scalar-broadcast version (each layer's loss adds the detached total goodness of all others — one wire ≈ a
  neuromodulator; note: goodness = a *magnitude*, so prefer a class-direction reference over a goodness scalar).
- **For us:** this is the **natural upgrade to the w=2 coordination window** if the window proves too short to bend
  the tunnel (the repo's own "if the 2-layer window underdelivers, direct-feedback/top-down is the stronger bet, at
  the cost of one top-down wire"). It's also **exactly the north-star's top-down loop** — so building it here is
  forward progress toward the recurrent brain, not a detour.
- **Cost-on-chip:** one broadcast wire / fixed projection. **SCFF-flow-safe?** ✅ (detached reference/modulator; no
  rewrite).

## C3 · Forward Target Propagation — forward-only *global* credit (new this session)

- **Forward Target Propagation (FTP)** — *A Forward-Only Approach to Global Error Credit Assignment via Local
  Losses* ([2506.11030](https://arxiv.org/abs/2506.11030), June 2025). Gets a **global error signal** to every layer
  using **only forward passes + local losses** — no backward pass at all. The most on-target recent paper for the
  author's exact want ("eventually backward, but forward-cheap").
- **For us — VERIFIED, and it's a ✗.** Read confirmed: target propagation's core move is *"drive each layer's
  activation toward a top-down-derived target"* — that **is** the forbidden stream-rewrite, by construction (not
  incidental). **SCFF-flow-safe? ❌.** Keep FTP only as a *conceptual* proof that forward-only global credit is
  achievable; it is **not implementable as-is** under the never-rewrite rule. (Also: all published FTP is supervised;
  no contrastive/SSL variant exists.) See [`lit-cheap-credit.md`](lit-cheap-credit.md) §C.

## C4 · Three-factor / e-prop / dopamine — the biology the author is describing

- **e-prop** (Bellec et al 2020) — online learning as **eligibility trace × broadcast learning signal**; the trace
  is a leaky integrator the author already has (a cap). **Already in north-star `10-realtime.md`.**
- **Three-factor Hebbian / neuromodulated plasticity** (Frémaux & Gerstner; dopamine-STDP) — local pre×post
  eligibility, gated by a global reward/error chemical. **This is the author's "half-local, half-global,
  activation history in synapse space, dopamine to update," verbatim** — and it's the real-brain mechanism the
  forward-only-with-a-global-gate scheme *approximates*.
- **For us:** the **theoretical home** of the whole constraint envelope. It says: keep SCFF's local trace (free on
  the cap), add **one global gate signal** (the early-exit confidence? the halting head? a DFA error? the loss-slope
  gate?) to decide *when the local update fires* — which is **also the Ch7 threshold gate Phase 5 already owes.**
  So Track C, the gate, and the decider GD (Track B) may all be **the same global scalar** wearing three hats.
- **SCFF-flow-safe?** ✅ by construction (local update, global timing).

## C5 · Already-mapped cousins (pointers)

- **Forward gradient** (Baydin 2022 / Ren-Hinton 2022) — unbiased gradient from one forward pass; high variance.
  Repo `direction-3`.
- **Predictive coding** (local approx of backprop; error-up/predict-down) — repo `survey/predictive-coding.detail.md`
  and north-star `9-hierarchy.md`. The top-down loop is native here.
- **Equilibrium Propagation** — repo `survey/equilibrium-propagation.detail.md`; energy-based, analog-native, but
  needs a settle phase.

## C6 · Verdict / how to prioritise

- **Track C is the *third* lever, not the first.** Try [Track A](track-a-preservation.md) (preserve) and
  [Track B](track-b-adaptive-readout.md) (read smart) first — they're cheaper and don't add global wiring. Reach for
  C **if** the tunnel still drifts *and* we've decided the deep layers must be *actively coordinated*, not just read
  around.
- **When we do reach for it, the order is:** (1) **top-down broadcast** (C2 — the cheap upgrade to the window, and
  north-star-aligned), then (2) **DFA / Forward Target Propagation** (C1/C3 — a global error, forward-only) if a
  reference broadcast isn't enough.
- **The unifying bet:** the **global gate scalar** is probably *one object* — the same signal that (Ch7) decides
  when to spend a GD update, (Track B) decides when to halt, and (Track C) gates the local plasticity. Designing it
  once, as a *neuromodulator-style broadcast*, is the elegant move and the north-star's "feeling."
- **The hard rule, restated:** all of these must **read/gate**, never **rewrite** the SCFF stream. Top-down
  references, error broadcasts that drive *weight updates*, and trace-gating are in-bounds; replacing SCFF
  activations with a globally-computed value is the forbidden `write`.

## Papers (this track)

FA (Lillicrap 2016) / DFA (Nøkland 2016) *(repo survey)* · **Can Local Learning Match Self-Supervised Backprop?**
[2601.21683](https://arxiv.org/abs/2601.21683) *(ICML 2026 — objective-side, not a wire)* · Layer Collaboration
[2305.12393](https://arxiv.org/abs/2305.12393) · Forward Target Propagation
[2506.11030](https://arxiv.org/abs/2506.11030) *(✗ rewrites the stream)* · CLAPP [2010.08262](https://arxiv.org/abs/2010.08262) ·
InfoPro [2101.10832](https://arxiv.org/abs/2101.10832) · ContSup [2312.07636](https://arxiv.org/abs/2312.07636) ·
EBD [2504.11558](https://arxiv.org/abs/2504.11558) · PEPITA+top-down [2302.05440](https://arxiv.org/abs/2302.05440) ·
e-prop (Bellec 2020) *(north-star)* · three-factor / dopamine-STDP (Frémaux & Gerstner) · forward-gradient [2202.08587](https://arxiv.org/abs/2202.08587) /
[2210.03310](https://arxiv.org/abs/2210.03310) · predictive coding / EqProp *(repo survey)*.
