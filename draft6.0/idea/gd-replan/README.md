# Research session — the depth-readout problem: the map, the literature, the re-plan

> **What this is.** The output of the research session you asked for (2026-06-28): find the work / papers / research
> for the depth problem, and re-plan the project around it. The warm-up doc
> ([`../phase4-problem.md`](../phase4-problem.md)) framed the *problem*; this folder is the
> *answer search*. Five files: this synthesis + three track dossiers + the re-plan. Written mechanism-first (the
> way the repo's `research/` dossiers are), with a **For us** line on everything, a **cost-on-chip** read, and an
> **SCFF-flow-safe?** flag (does it rewrite the SCFF stream — the P2.5 `write`-kills-SCFF rule).
>
> **Status: research notes, not decisions.** Architecture changes are decisions backed by a result, not a hunch —
> so this proposes the *ladder of experiments*, it doesn't commit the architecture. The author decides where to
> step on.
>
> ## ⚠ POST-REVIEW (2026-06-28) — read this first
> Four **Opus 4.8** subagents rechecked the plan (cold outsider · red-team · insider auditor · substrate checker).
> The plan was **revised**. The authoritative post-review decisions are in
> **[`review-and-revisions.md`](review-and-revisions.md)**, and **[`replan.md`](replan.md) is now v2.** Headline
> changes: the Tunnel Effect is **demoted** to an analogy; ReZero defaults to **frozen** α (no valid training signal
> otherwise); **learned halting/PonderNet is CUT** (over-engineering → calibrated threshold); T0 gains a decisive
> **locality control** + probe-capacity + natural-data controls; T1 must beat a **truncation baseline** on the
> **continual** workload; the **native goodness signal is rejected for placement** (density≠class) and settling-time
> is parked for the north star. The spine of every change: **preserve/read the class DIRECTION, never a magnitude.**
> The track files below keep their literature value; on any conflict, `review-and-revisions.md` wins.
>
> ## ✅ T0 RAN (2026-06-28) — the depth ceiling is LOCALITY-bound
> The two pre-decision controls executed (results: **[`t0-results.md`](t0-results.md)**, figure
> `t0/figs_t0/T0_RESULTS.png`, script `t0/run_t0.py`). **(T0.1)** the decay is *not* lr/passes under-training — but
> **sharper InfoNCE temperature (0.5→0.2) is a free lever** (peak L4→L7, tail +0.12). **(T0.2)** full end-to-end
> backprop on the *same* InfoNCE composes all 12 layers, while local windows cap ~5 → **the ~5 ceiling is LOCALITY,
> not the objective** → **native depth is CURABLE via global credit**, so the cheap-credit ladder (temp → w4 →
> cheap global signal) is now **mandatory, not optional**. [`replan.md`](replan.md) is updated to **v2.1**.
>
> ## ✅ T3 RAN (2026-06-29) — the cheap-credit lever is OBJECTIVE SHARPNESS, not credit machinery
> The cheap-credit ladder + a deep-lit pass ran (results: **[`t3-results.md`](t3-results.md)**, figure
> `t3/figs_t3/T3_RESULTS.png`; survey: **[`lit-cheap-credit.md`](lit-cheap-credit.md)**; scripts `t3/run_t3.py`,
> `t3/run_topdown.py`). **Surprise verdict: sharpening the InfoNCE objective (`temp 0.5→0.2`) at the cheap depth-2
> window nearly matches full-backprop composition (tail 0.539 ≈ 0.549) at ~1/6 the cost — a FREE fix.** Two candidate
> "cheap global credit" mechanisms were guard-checked and **failed**: overlapping windows *hurt* (credit-chain length
> composes depth, not path multiplicity), and a naive detached top-down loss term *hurt* (imports the decayed top's
> badness — FD-gradient-verified). FTP/PEPITA ruled out (they rewrite the stream). The decay is, to first order, an
> **objective-sharpness problem with a free fix**; genuine global-credit machinery is deferred and may be unneeded.
> [`replan.md`](replan.md) is updated to **v2.2**.

---

## 0 · The reframe (what we actually learned this session)

Going in, "the problem" was *"SCFF decays with depth."* The author sharpened it mid-session and the literature
confirmed the sharpening is **exactly right**:

> **The problem is not "stop the decay." It is "we don't know *where to read*."** The composer gives us any depth;
> the useful representation lives at a **task-dependent sweet spot** (easy task → early layer, hard task → late
> layer); reading every layer (all-tap) **burns the 80/20 cost win** that justifies SCFF being 80% of the brain.
> SCFF "isn't done" until we can place the GD readout *cheaply and correctly* without reading everything.

And the decay itself we already nailed in the warm-up: not dead neurons (dead-frac ≈ 0), not capacity (W240
doesn't help) — **the local objective drifts the representation off the class manifold once a layer's class-relevant
abstraction saturates** (the *trigger × multiplier* synthesis, [problem doc §3a](../phase4-problem.md)).

## 1 · The keystone: the author re-derived the **Tunnel Effect** (again)

The single most important find of the session. **The Tunnel Effect**
([arXiv 2305.19753](https://arxiv.org/abs/2305.19753), Masarczyk, Ostaszewski, Imani, Pascanu, Miłoś, Trzciński,
**NeurIPS 2023**) is the author's reframe, already published — from the *supervised* side:

- A deep net splits into an **extractor** (early layers — builds linearly-separable representations, reaches >99%
  of final accuracy) and a **tunnel** (later layers — compress the representation, drop its rank, contribute almost
  nothing to accuracy).
- **Increasing depth only lengthens the tunnel.** The extractor length stays fixed; deeper networks just grow more
  useless tunnel. *"Overparameterized nets allocate a fixed capacity for a given task independent of total
  capacity."*
- **Extractor length is set by task complexity.** More classes / harder task → **longer extractor, shorter
  tunnel.** This **is** the author's "easy task → read early layer, hard task → read late layer," in the
  literature's own variables.
- **The tunnel degrades OOD generalization and — the part that matters most for us — continual learning.** The
  tunnel is *task-agnostic* and **causes higher catastrophic forgetting**; the published advice is literally
  *"regularize the extractor, skip feature-replay in the deep layers, or use a compact model without a tunnel."*

Three consequences land hard on this project:

1. **"Native deep SCFF" is the wrong goal.** You can't make a stack *useful*-deeper by stacking — the extractor is
   as long as the task needs and no longer; the rest is tunnel. The prize is to **find where the extractor ends and
   read there**, and get more capacity from boosting/width, not tunnel-length. (This *vindicates* the Phase-2
   boosting verdict and the all-tap readout — they read the extractor, not the tunnel.)
2. **The decay is the tunnel, sharpened.** Supervised tunnels at least *preserve* in-distribution accuracy (a global
   label pins the output); SCFF's tunnel is **worse** — with no global signal, the local objective *actively drifts*
   and the deep layers **overwrite** the extractor's work (the mixed-task corruption). So the SCFF tunnel is a
   *harmful* tunnel, not a benign one.
3. **The tunnel is a direct threat to our home turf (continual).** A long SCFF tunnel would erode the A6 win. This
   makes the readout/extractor work not a side-quest but a *defense of the core result*.

## 2 · The unifying picture — two tracks, two ends of one axis

```
            the representation
   input → [ EXTRACTOR (builds, ~L1..Lk) ] → [ TUNNEL (drifts/overwrites, Lk..Ln) ] → out
                         ▲                                   ▲
            read HERE (the sweet spot)            all-tap currently reads everything
                         │                          (works, but burns the 80/20)
       ┌─────────────────┴───────────────┐
   TRACK A: make the tunnel harmless     TRACK B: find the extractor's end
   (preserve early features forward,     (read at the right depth cheaply —
    so reading the TOP == reading the      multi-head + confidence, learned halt)
    extractor → placement dissolves)
```

- **If Track A wins** (preservation: a near-identity residual carries the extractor's features to the top), then
  "read the top" *is* "read the extractor" and the placement problem **dissolves**.
- **If Track A only partially wins** (the extractor still ends somewhere), then **Track B finds that end cheaply**
  (deep-supervision heads + a confidence/halting gate = the author's "decider GD").
- They **compose**: preservation lengthens the useful part; adaptive readout reads the (now-deeper) end. And both
  are *cheaper* than all-tap, which is the whole point.

## 3 · The constraint envelope (the author's answer 2, made into a rule)

Everything below is graded against this:

- **Forward-forward is the default** (it's what's cheap on the analog substrate). Prefer forward-only, local,
  per-sample.
- **A bounded amount of global / "backward" is licensed** — the author accepts it ("eventually we want backward
  somewhere; real neurons are half-local, half-global, dopamine-modulated"). It's allowed **in the GD-side modules
  (readout, decider) and as a top-down broadcast** that *reads/gates*, never as a full backprop through the SCFF
  bulk.
- **The hard rule: never place a signal between SCFF layers that REWRITES the stream.** This is P2.5 (`write` kills
  SCFF) restated by the author ("some backpropagation model can destroy SCFF if placed between"). Read-only heads,
  detached top-down broadcasts, eligibility-trace×neuromodulator updates = OK. Backprop that overwrites SCFF
  activations mid-stack = forbidden.

So every paper below carries an **SCFF-flow-safe?** flag.

## 4 · What was already in the repo vs what's new

The repo's `research/papers/phase3/` already maps the **forward-only depth-composing** family deeply — GIM, CLAPP,
CLAPP++, SoftHebb, Mono-Forward, predsim, the OLU/DF-O coordination window, Direct-Feedback/DFA, the
"higher-layers-can't-talk-to-lower" diagnosis (2012.03837 / 2010.04116), forward-gradient, PEPITA. **We do not
re-derive that** — the track files point back to it. The session's *new* contributions:

- **The Tunnel Effect** as the unifying diagnosis (the readout-placement problem has a name and a theory) — §1.
- **The preservation-via-near-identity-init family** (ReZero / Fixup / LayerScale / Hyper-Connections) as the
  named, proven, substrate-cheap version of the author's residual idea — [Track A](track-a-preservation.md).
- **The adaptive-readout / early-exit / learned-halting family** (deep supervision, BranchyNet/MSDNet/SDN/CALM,
  ACT/PonderNet, MoE/SSM) as the engineering answer to "where to read" and the author's decider-GD —
  [Track B](track-b-adaptive-readout.md).
- **The cheap-global-direction family** (DFA, top-down broadcast, Forward Target Propagation) as the
  constraint-respecting "eventually backward" — [Track C](track-c-cheap-direction.md).

## 5 · The files

| File | What's in it |
| --- | --- |
| **[`t3-results.md`](t3-results.md)** ★ NEWEST | **The T3 cheap-credit ladder results (2026-06-29) — the latest empirical word.** Objective sharpness (temp) is the decisive free lever ≈ e2e ceiling; overlap + naive top-down STRUCK (guard-checked negatives); the reordered ladder. Scripts in `t3/`. |
| **[`lit-cheap-credit.md`](lit-cheap-credit.md)** ★ | **The deep literature survey (2026-06-29):** the 3 flow-safe global-credit shapes, ranked candidates, FTP/PEPITA ruled out, all arXiv IDs verified. Supersedes track-c's survey-level treatment. |
| **[`t0-results.md`](t0-results.md)** | **The T0 experiment results (2026-06-28).** Both controls ran: decay is locality-bound (not under-training), temperature is a free lever, native depth is curable via global credit. |
| **[`review-and-revisions.md`](review-and-revisions.md)** ★ | **The post-review decision record (authoritative for the plan logic).** The 4-agent recheck, the meta-insight (direction not magnitude), the KEEP/CHANGE/CUT ledger, and where the leader overrules a reviewer. |
| [`replan.md`](replan.md) **(v2.2)** | The re-planned ladder, **post-review + post-T0 + post-T3**: T0/T3 ✅done → T1 (MVP, cost) → T2 (frozen residual) → T3 (the cheap-credit ladder — **temperature is the primary free lever**; overlap + naive top-down struck; global-credit deferred) → T4 continual → T5 north star. The actionable plan. |
| [`track-a-preservation.md`](track-a-preservation.md) | Preservation literature — near-identity residual (ReZero/Fixup), dense reuse, the residual caveat. *(Post-review: α defaults to **frozen**; preserve **class direction**; whitening rejected-as-lever — see review-and-revisions.md.)* |
| [`track-b-adaptive-readout.md`](track-b-adaptive-readout.md) | Adaptive-readout literature — deep supervision (multi-head), early-exit + confidence, halting, MoE/SSM. *(Post-review: learned halting **CUT** → calibrated threshold; placement = head-confidence not goodness.)* |
| [`track-c-cheap-direction.md`](track-c-cheap-direction.md) | Global-coordination literature — DFA, top-down broadcast, Forward Target Propagation, three-factor/dopamine. *(Post-review: promoted to **conditional T3**, mandatory iff the locality control says so.)* |

## 6 · The one-paragraph verdict (for future-me, cold)

The depth problem is the **Tunnel Effect**: the useful representation is the *extractor* (length set by task
complexity), the rest is a *tunnel* that — in SCFF's unsupervised case — actively drifts and overwrites the good
features, and (the killer) **a long tunnel causes catastrophic forgetting**, threatening the project's continual
win. So the goal is **not** native-deep SCFF; it's **(A) carry the extractor's features forward so the tunnel can't
overwrite them** (ReZero-style near-identity residual — one scalar per block, substrate-cheap, the author's own
idea, proven to train 1000-layer nets) **and/or (B) read at the extractor's end cheaply** (deep-supervision heads +
a confidence/learned-halt gate = the author's decider GD, which is also the seed of the north star's "I get it"
feeling). The constraint: forward-first, bounded global OK, **never rewrite the SCFF stream**. The ladder in
[`replan.md`](replan.md) starts with three cheap tests in the 40-min budget (settle the under-training confound,
try the ReZero gate, build the per-task extractor-length profiler) and climbs to the recurrent thinking brain.
