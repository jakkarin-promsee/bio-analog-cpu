# Draft 6.0 — the depth-decay problem (warm-up before the research session)

> **What this is.** The problem statement we go into research with — not the fix. A reconstruction of *what
> breaks*, *where the data says it breaks*, and *why*, built from the Phase 1→4 reports (the live diagnosis is
> [`src/phase4/exp3/experiment-3-decay.md`](../src/phase4/exp3/experiment-3-decay.md) +
> [`experiment-3.md`](../src/phase4/exp3/experiment-3.md)). It also reconciles your Phase-4 reflection
> ([`phase4-opinion.md`](phase4-opinion.md)) against what the sims actually measured —
> because two of your guesses are confirmed by the data and one is *refuted by your own experiment*, and we
> shouldn't carry a dead mechanism into the reading.

---

## 1 · The problem, in one line

**Contrast (InfoNCE, two-mask) + coordination w=2 made depth *compose* — but it didn't make it *keep* composing.**
The SCFF bulk builds useful (class-relevant) structure for the first ~5 layers, plateaus, and then the
representation **decays** — class separability erodes layer after layer past ~L7. Your "context decay with depth"
is real, it is the live ceiling on the 80%-of-the-brain part, and it is the thing the research session has to
attack.

This is **not** the Phase-2 wall returning. The old wall (energy `Σh²`) never composed at all — it rotted from
layer 1. Contrast genuinely climbed for ~5 layers; the problem now is that the climb turns into a slow slide. Two
different failures, and the difference is the whole point (§4).

---

## 2 · The exact shape of the decay (what the data shows)

From **P4.3** and its decay follow-up (n=5, iso-budget and fixed-width controls, headroom + flat synth tasks):

- **Builds → plateaus → decays.** Per-layer probe on the adopted cell (w=2, headroom, fixed W64):
  **peak ~0.54 at L5 → 0.435 at L12.** It composes to layer ~4–5 (the cross-layer window really is sharing context
  forward), holds briefly, then erodes after ~L7.
- **It is depth, not the iso-budget width-shrink.** At **constant width W64** (so deep layers aren't starved of
  neurons), OURS *still* droops: headroom **0.557 → 0.449** over L4→L12, flat **0.731 → 0.647**. The width-shrink
  in the iso-budget sweep only adds ~0.02–0.03 on top. The decay survives holding width fixed.
- **It happens in both regimes.** Headroom (depth *should* pay) and flat (depth shouldn't) both decay — flat just
  starts higher. So it isn't "the task ran out of headroom"; even the flat task, solvable in 1–2 layers, gets
  *worse* with more depth.
- **The mixed-task tell (the cruelest read).** On a task that is half flat-subtask / half headroom-subtask, the
  flat subtask is **readable by layer 2–3 (probe ~0.67) and then actively corrupted by the deeper layers
  (down to ~0.51 by L12)** — while a tuned BP holds that same subtask flat at ~0.75 across all depths. The deep
  layers don't just fail to help; they **overwrite structure the early layers already solved.** The corruption is
  OURS-specific, not the task's fault.

> Crossover vs BP (headroom, iso-budget): OURS **beats** tuned BP at L2–L6 (best −0.039 at L3), then **loses**
> L8–L12 (+0.094 at L12). The decay is exactly the part that hands the lead back to BP.

---

## 3 · The cause, nailed by three controls

The decay follow-up was built to kill the obvious capacity explanations, and it killed all of them. The cause is
**not** a resource shortage — it is a **direction** problem.

| Hypothesis (capacity-flavoured) | Control run | Verdict |
| --- | --- | --- |
| Deep layers go **dead** (too few neurons fire → wiring collapses) | per-layer dead-unit fraction | **REFUTED — dead-fraction ≈ 0.00 at every layer.** Nothing is dying. |
| Deep layers are **too narrow** (need more neurons) | widen each layer with depth, up to **W240** at L12 | **REFUTED — widening doesn't help.** W64 and W240 decay to the *same* accuracy. |
| The lost **effective rank** is the binding constraint | erank vs accuracy, both widths | **REFUTED — rank is a symptom.** `widen` carries much higher rank (18.7 vs 12.3 @L12) at *identical* accuracy; the extra dimensions it adds are **not class-aligned.** |

What's left, and what the diagnosis names explicitly:

> **The cause is the per-layer local contrast objective drifting the representation off the class manifold past
> ~layer 5 — independent of width.** It is the *direction* of the representation that rots, not its dimensionality
> or its liveness.

The mechanism in plain words: **every layer applies its own local InfoNCE, and nothing tells a layer to *preserve*
the class structure the layer below already found.** So each layer is free to re-discriminate the input *its own
way* — toward *some* code that is informative about the input but not aligned with the *class* axis the readout
needs. For ~5 layers the w=2 coordination window keeps neighbours roughly pulling the same direction, so it climbs.
Past the window's reach, with no global "keep what's already class-relevant" signal, the independent local
objectives walk the representation off the class manifold. Alive, full-rank, informative — and pointed the wrong
way. (This is, once again, a **direction** failure — the same family of bug that ate draft 5 and the XOR sign. The
project's recurring silent killer shows up here as "informative but mis-aimed," not "missing.")

Contrast with the **old energy wall** so the two don't blur together:

| | Energy `Σh²` (Phase 2 wall) | Contrast + w=2 (the current decay) |
| --- | --- | --- |
| What each layer asks | "am I *loud* on coherent input?" (a **density** question) | "can I *tell the views apart*?" (a **class** question) |
| Depth behaviour | rots **from layer 1**, composes *zero* | climbs to **~L5**, then decays |
| Dead units | **accrue** (0 → 0.47 by deep layers) | **none** (≈ 0.00) |
| Effective rank | **collapses** (39 → 11) | declines but **not binding** (symptom) |
| Failure type | features homogenize / die (density ≠ class) | features drift off the class manifold (preserved-but-mis-aimed) |

The through-line from Phase 1 (**density ≠ class**) turned once in Phase 3 — contrast preserves *class*, so it
composes — but it didn't fully resolve: contrast preserves the right *kind* of information for ~5 layers, then
**stops preserving the *specific* class structure** because no signal makes it.

### 3a · The trigger × multiplier synthesis (reconciling the author's "abstraction-dead")

The author's reflection had this right under a different name — and the reconciliation is the cleanest statement of
the cause, so it's worth pinning. His "dead neurons" never meant ReLU-dead (zero activation); it meant
**abstraction-dead**: a task carries a finite amount of *class-relevant abstraction*, and once a layer has extracted
all of it, there's nothing real left to chain forward. That predicts exactly what the data shows — **the composing
peak tracks task complexity** (flat saturates by ~L1–2 and decays early; headroom saturates ~L4–5 then decays) —
and it's the *cause* behind the project's own standing rule "depth only pays with headroom" (A3/P4.2).

One correction makes it exact, and it's load-bearing: **the saturated layers are not idle.** The mixed task proves
it — there the deep layers *still have the headroom subtask to learn from* (real signal, plenty of work) yet they
*still* corrupt the already-solved flat subtask (0.67 → 0.51) while tuned BP holds it at ~0.75. So the damage is not
"no signal → wander into noise"; it is "the layer is **actively optimizing something else** and **nothing forces it
to keep** what it already solved." Rename it **abstraction-*saturated*** (the useful class signal dies; the activity
doesn't) and it reconciles both facts at once: **dead-fraction ≈ 0** (alive, busy) *and* the author's intuition
(no useful abstraction left to chain) are simultaneously true.

> **Decay = trigger × multiplier.**
> - **Trigger (the author's):** the task's class-abstraction *saturates* at some depth — sooner on flat, later on
>   headroom. This sets *when* drift begins and *how deep is useful per task*.
> - **Multiplier (the data's):** the local objective carries no **preservation** term, so a post-saturation layer
>   (now feeding on non-class / nuisance structure) **overwrites** the good representation instead of leaving it
>   alone.
>
> The fix targets the **multiplier** (preservation); the **trigger** is what tells us how deep we even need to go.
> Same picture from two ends.

---

## 4 · Why the coordination window only delays it

The window (`w`) is the lever that *bought* depth in Phase 3 — and it's worth being precise about what it does and
doesn't do, because it's the obvious "just turn it up" reflex:

- **It pushes the peak deeper, at a cost.** w=2 composes ~5 layers; w=4 reached **L8 monotone** on the Phase-3
  headroom task (0.41 → 0.569, slope +0.022). Bigger window = composition reaches further before the slide.
- **But it's a *local* lever.** A window of `w` only lets a layer see `w` neighbours; it shares context across a
  few layers, then detaches. It is not a global "preserve the class manifold across the whole stack" signal. So
  raising `w` *delays* the drift (and costs more coordination every layer); it doesn't remove the thing that causes
  it. Outrun the window and the decay returns.

So "crank `w`" is a knob, not the fix. The fix the data points at is **preservation** — a way to carry already-found
class structure *forward unchanged* so deep layers can only *add to* it, not *overwrite* it (§6).

---

## 5 · Your reflection vs the data (what to carry, what to drop)

You said the solutions in your opinion file are rough guesses with no refs yet — fair. But some of them you can
already grade against your *own* experiments before we read a single paper:

**✅ CONFIRMED by the data — carry these in:**

- **"GD-write breaks SCFF" (your "one more detail").** Dead on. Phase 2 P2.5 already found `write` (re-inject the
  GD-corrected representation back into the stream) **fails** — a class-collapsed rep destroys the rich features —
  while `read` (GD reads the stream, never rewrites it) works. The mixed-task corruption in P4.3 is the same
  phenomenon from the SCFF side. **Your conclusion — "whatever sits between SCFF layers should be unsupervised, or
  at least slow and not shift all the labels at once" — is exactly what the data says.** The GD readout must *read*,
  not *overwrite*.
- **Residual (your Solution 2) is the data's own lead candidate.** The decay card names **"residual / skip
  connections"** as *"the clean P5 architectural candidate — let deep layers add to rather than overwrite the
  representation."* That is your residual idea, almost verbatim. And your instinct on the form — *initialize the
  SCFF output near zero, let it change the output only when confident, so `residual ≈ input` survives to the last
  layer* — is the right shape (additive, near-identity init). It's `input + SCFF(input)`, not `input − SCFF`: the
  point is to **preserve** the input and let SCFF *contribute* a correction, which is addition from a near-zero
  start, not subtraction. (We'll pin the exact math in the research session — but you're on the additive side.)

**🔎 RIGHT INSTINCT, WRONG NAME — re-aim, don't drop (the "dead neurons" clarification):**

- **"Abstraction-dead" (Solutions 1, 3, point 8) — NOT ReLU-dead.** The author's "dead neurons" never meant
  zero-activation death (that *is* refuted — dead-fraction ≈ 0.00 at every layer, W240 doesn't help). It meant
  **abstraction-saturated** — see §3a: a layer with no class-relevant abstraction left to chain keeps optimizing on
  non-class structure and overwrites the good rep. That framing is **supported** (the peak tracks task complexity)
  and is the *trigger* half of the cause. The one thing to drop is any **gate criterion built on activation-death**
  (e.g. "stop forwarding when 30% of layer-2 goes dead") — there is no activation-death to detect; a saturation gate
  would have to read *class-signal exhaustion* (e.g. probe/selectivity stalling), not dead-unit count.
- **The bypass gate (Solution 1)** is a hand-wired, weaker form of the residual/skip idea (#2) — same instinct
  (get early structure to deep layers), less principled. If residual is the structural answer, bypass folds into it.

**🔭 DIFFERENT PROBLEM (real, but not *this* one) — park for later:**

- **The decider-GD / "lazy depth" idea (Solution 3) and the SSM/MoE "open SCFF only where used" (Yapping 2).**
  These are about **adaptive computation depth** — *how deep should this sample compute* — which is a genuine and
  interesting direction (it's the territory of early-exit / PonderNet-style halting / conditional compute). But it
  **routes around** the decay (use only the good early layers) rather than **fixing** it (make deep layers stop
  drifting). Worth its own track; not the lever for "why does the representation rot." Note its gate would read
  **class-signal exhaustion** (probe/selectivity stalling), not activation-death (§5, the saturation clarification).
- **The Hippocampus loop (Solution 4) / "I get it" threshold.** That's the north star — the recurrent
  correctness-as-feeling brain — deliberately beyond the numbered phases. Real, yours, and *not* what unblocks
  depth-decay. Hold it.

---

## 6 · The fix direction the data already points at (the on-ramp to research — not conclusions)

We are **not** picking the fix yet — that's the research session. But the experiments don't leave us empty-handed;
they hand the reading three concrete leads, all under one word: **preservation.**

1. **Preservation paths — residual / skip.** Let deep layers *add to* a carried-forward representation instead of
   *re-deriving* it, so already-found class structure can't be overwritten. (The decay card's named candidate;
   your Solution 2.) The research question: what's the right forward-only, local way to do this under SCFF +
   contrast — and does it interact with the mandatory inter-layer norm?
2. **The all-tap / boosting readout is already the *workaround* and it's load-bearing.** It reads the ~L5 peak
   instead of the decayed top, and stacking *shallow* blocks (boosting) gets depth without deep-SCFF decay. So even
   un-fixed, the architecture has a route to depth — which matters for the "is this blocking?" question (§7).
3. **The one honest confound to settle *first*: depth-scaled training.** Every depth in P4.3 used the *same*
   `ep=25, lr=0.03`. Deeper stacks may simply be **under-trained** — a depth-scaled learning rate or more passes
   could push the peak deeper. The decay's *shape* (peak-at-~5-then-slide, identical across both widths, both
   regimes, both mixed subtasks) argues it's objective-drift rather than an optimization shortfall — but until the
   **depth-scaled-training control** is run, "~5 useful layers" is "~5 under *this* fixed online budget," not a
   proven intrinsic ceiling. This control should be the *first* thing the research session frames a test around, so
   we don't go architecture-hunting for a problem that's partly a tuning artifact.

---

## 7 · The stakes — is this actually blocking Phase 5?

Your reflection says *"until this problem is fixed, we can't optimize anything else."* That's true for the **vision**
but not strictly for the **mechanics**, and the distinction matters for the phase-5-vs-fix-first call you're sitting
with:

- **Mechanically, Phase 5 can run without solving native depth-decay.** Phase 5's core is the *continual*
  maintenance loop (sleep cadence + the Ch7 gate) — the validated A6 win — and depth is *already* handled by the
  boosting design (shallow blocks + all-tap readout). The decay doesn't block that.
- **But for the architecture's *identity*, it's a real cap.** SCFF is ~80% of the brain and the whole "cheap deep
  analog substrate" pitch. If native SCFF can only stack ~5 composing layers before drifting, then "deep SCFF" is
  leaning permanently on the GD-readout/boosting crutch. Solving native depth-decay is what would let the cheap
  brain actually *be* the deep substrate — which is why it feels like the savior problem. It is the difference
  between "we route around it" and "we earned it."

So the real fork isn't "phase 5 *or* fix this" — it's **"do we let Phase 5's continual optimization proceed on the
boosting workaround while we research the native-depth fix in parallel, or do we hold Phase 5 and make depth the
next first-class research phase?"** That's the decision the research session should inform — and it's a decision
(architecture is a decision, not an experiment), so it waits for the reading. We don't have to answer it in this
warm-up.

---

## 8 · One-paragraph carry into the research session

The cheap brain composes depth for ~5 layers and then its representation **drifts off the class manifold** — not
because neurons die (they don't; dead-fraction ≈ 0) and not because layers are too narrow (W240 doesn't help), but
because each layer's *independent local contrast objective re-aims the representation with no signal to preserve the
class structure the layer below already found.* The coordination window delays this locally and at a cost; it
doesn't cure it. The data's own pointer is **preservation** (residual/skip, the load-bearing all-tap/boosting
readout), and the first control to settle is **depth-scaled training** (to bound how much of the ~5-layer ceiling is
objective-drift vs under-training). The research session goes looking for the forward-only, local, biologically
plausible way to make a deep stack *preserve and add* instead of *overwrite* — that's the search.
