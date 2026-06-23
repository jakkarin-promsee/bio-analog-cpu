# Criticize

Let me read the middle of the document that was truncated to make sure I'm covering everything.I've read enough. Let me also check §6.1-§6.2 briefly to make sure I have everything.OK I have the full picture now. Let me think hard about this.

Let me reason through the architecture systematically — section by section, looking for internal inconsistencies, logical gaps, and unstated assumptions. I'll do this as a real analysis pass, not a summary.

---

**Pass 1: Internal consistency check across sections**

Going through each module to see if its claims match other modules' claims:

§4 Brainstem says it "Reads predictions from the system's output capacitors (via an ADC)." But §8.4 says distribution memory is SRAM "after passing through ADCs at the Brainstem interface." Wait — does each level have its own ADC, or is there just one ADC at the Brainstem? Re-reading §8.4: "the signals at higher levels are already discretized after passing through ADCs at the Brainstem interface." This is confusing — distribution memory exists at every hierarchy level, but only the Brainstem has an ADC? How does the Limbic Loop's distribution memory get populated then? It must require ADCs at every level too, or analog SRAM storage at each level. **This is unclear and probably wrong.**

§5.7 says distribution memory at higher levels is 16/12/10-bit SRAM. SRAM requires an ADC to fill from analog. So either (a) each level has its own ADC, or (b) the distribution measurement at higher levels is done by the ALU at _that_ level using its own time-to-threshold circuit. Option (b) is much cleaner and consistent with §5.8 "Forward pass measurement." But it's never said explicitly. **Hole in spec.**

§5.6 "The division problem" says we solve it by pre-normalization at each level. But pre-normalization requires either (a) one division per module per forward pass (which is what's claimed) or (b) storing pre-normalized values. The spec doesn't explain how that division is done physically. It says "the cost is per-module, not per-weight" — but per-module division still needs an analog divider or an ADC + digital divide. **Not addressed.**

§5.4 mentions "If a substantial fraction of scaps collapse, that is the signal to (a) add a tiny random noise floor to weight updates, or (b) move to path 2." But §5.4 lists three paths and (a) is not one of them — the noise floor is informal. Also the relationship between "floor at 1" (momentum SRAM) and "noise floor" (weight update) needs disambiguation. **Confusing.**

§6.5 backward update formula:

```
weight_cap += pulse_width × momentum × direction
```

But where does `share` come into this? The §5.1 description says scaps receive a share via the Ganglion-local bus and apply PWM update. So which is it — does `pulse_width` already encode the share, or is `share` a separate quantity multiplied by `momentum`?

Reading more carefully: §6.5 says "The PWM-encoded share from the Ganglion's local bus (pulse width = magnitude of share)." So the pulse-width _is_ the share. But then why multiply by momentum? The share already came from the share calculation which already used the measurement (which is proportional to `|a·W|`). Multiplying again by momentum (which is an EMA of the same measurement) is **double-counting**. The scap's importance is being multiplied in _twice_ — once in routing the share through the Ganglion's distribution memory, and once locally as `momentum`.

**This is a real bug in the spec.** Let me verify by tracing the math:

Imagine 2 scaps in a Ganglion. Scap A has measurement 10, Scap B has measurement 1. Loss share arrives at Ganglion = `L`.

Ganglion distributes: `share_A = L × 10/11`, `share_B = L × 1/11`. These are broadcast as pulse widths on the Ganglion-local bus.

Then scap update per §6.5: `ΔW = pulse_width × momentum × direction`.

If momentum_A = 10 (matches measurement) and momentum_B = 1:

- `ΔW_A = L × (10/11) × 10 = 100L/11`
- `ΔW_B = L × (1/11) × 1 = L/11`

That's 100× difference between A and B for a 10× difference in contribution. **Quadratic, not linear.** Maybe that's intentional? But it's not stated as such. And it amplifies the dead-weight problem (weak scaps now get updates scaled by `share × momentum`, both small, → multiplicatively tiny).

Actually wait — maybe momentum is the _cross-batch_ accumulation (EMA), and the measurement that feeds the share is _the current batch_. In that case, the share is `L × measurement / total_measurement` (current batch) and the local multiplier is `momentum` (history). Those are different quantities.

But §7.4 step 6 says measurement values are "Used immediately for the Ganglion's contribution to its parent block (sum, for §5 distribution). Combined via EMA into the corresponding scap's momentum SRAM (§6.3)." So the measurement feeds both the parent's distribution memory (for next pass?) and the scap's momentum.

Now, when does the share get computed? §5.9 says backward pass is 6 clocks, where clock 4 is "Ganglia read, compute per-scap shares using measurement caps." So shares are computed from the most recent measurement caps. And scap local update at clock 5 uses... `pulse_width × momentum × direction`.

Two possibilities:

- (A) `pulse_width` = share computed from measurement (current batch), `momentum` = EMA of measurements (history). The combined update favors scaps that _both_ contributed now AND have a history of contributing. Acceptable but it's quadratic in contribution and never stated as such.
- (B) Author intended these to be one and the same — the scap reads its share via pulse_width and momentum should not appear. The §6.5 formula is overspecified.

**This needs explicit resolution in draft4.** It's currently ambiguous and the wrong reading is buggy.

OK, more issues:

§7.5 "Forward-pass timing risk" mitigation 1 says "Cap the measurement time. If a scap doesn't cross threshold within T_max clocks, store T_max in its temp SRAM." But wait — _T_max is the longest time, which means weakest contribution_. So storing T_max for too-slow scaps puts them at "max weakness" which is correct. But then time-to-threshold has inverted semantics — _shorter_ time = stronger contribution. So `1/T` not `T` is the measurement. Let me check §5.8 and §7.4:

§7.4 step 4: "Steeper rise = stronger contribution = shorter time." OK so shorter time = stronger. But in §7.5 mitigation 1, weak scap defaults to T_max (longest time = weakest contribution). That's correct.

But then if measurement is `time-to-threshold`, the scap with highest contribution has the smallest stored value. Then how does the Ganglion's distribution sum work? Distribution share should give _more_ weight to stronger contributors. So if we naively sum `T` and normalize, we'd give shares inversely proportional to contribution. We'd need to store `1/T` somewhere, or do the inversion at distribution time.

**This is another unstated detail.** Either the stored measurement is `1/T` (so a divider is needed somewhere), or the distribution math takes the inverse. Neither is specified.

§5.9 backward pass timing claims 6 clocks regardless of network size. But the actual diffusion takes 5 levels × 1 clock per level = 5 clocks of routing + 1 clock for scap update = 6 clocks. But each Ganglion's per-scap share computation has its own internal latency — the 29 measurement caps × 16-bit temp SRAM. Even if done in parallel, there's a real circuit delay. Calling this "one clock" hides real complexity. Should probably say "6 clock-edges" with explicit acknowledgment that each clock takes finite time.

§4.4 mentions §13 (Future Tracks) but §13 is actually "Hypotheses." Future Tracks is §14. **Cross-reference error.**

§14 contains "Future Mechanisms" (5.5–5.6 are about _current_ mechanisms but with §14 entries pointing back). Actually wait — let me check the section numbering globally.Good. So §13 is Hypotheses, §14 is Future Tracks. §4.4 references §13 saying "Future Tracks" — that's wrong, should be §14.

Reading guide says "consequences ripple to §13 (hypotheses), §15 (math), §18 (protected list)" — correct.

But §4.4 says "If a future breakthrough lets us distribute the loss compute itself... That is a §13 (Future Tracks) item, not a blocker." Wrong — should be §14.5 (which exists, "Distributed loss compute"). Cross-reference error.

Let me continue the deeper analysis on substance.

---

**Pass 2: The Cortex / Hippocampus structural identicality**

§10.2 commits to "same structure, different learning rates." That's a clean decision. But §10.3 has:

- Cortex: high-quality input + Hippocampus output (Commissure)
- Hippocampus: low-quality input + Cortex output (Commissure)

And §10.4 has Cortex with **two output heads** (one for prediction, one for Commissure). §10.5 says Hippocampus has one output to Commissure.

So they aren't actually structurally identical. Cortex has dual-head output, Hippocampus single-head. That's a real structural difference, not just a timescale difference. **§10.2 overclaims.**

Either:

- (a) Hippocampus also has dual heads (one for its own prediction loss, one for Commissure). Then "predict input" claim is symmetric.
- (b) The structural difference is acknowledged but kept small.

Reading more carefully: §10.5 says "Hippocampus also predicts input (same loss target as Cortex)." If both predict input, both need a prediction head. So Hippocampus must have head A (predict input) and head B (to Commissure). That makes the structures identical.

But §10.5 doesn't explicitly say Hippocampus has two heads. It implies it. **Should be made explicit in §10.5.**

Also: what does "head" mean structurally? Is it two separate output Ganglia? Two output capacitors from the same Ganglion? The output of an entire G-S block? This is undefined.

---

**Pass 3: The label flow**

The Brainstem "Receives or holds the label signal." But where do labels come from? In a Limbic Loop that's _self-supervised_ (predicting next input), the label is the _future input_ — which arrives after a delay. The Brainstem must hold the prediction made at time T, wait for input at T+1, then compute the loss. This implies the Brainstem has a 1-step memory buffer. That's an additional Brainstem responsibility not listed in §4.2.

For Hippocampus consolidation: Hippocampus predicts the "stable consistent pattern" of input. The label for _that_ is... what? The current input? The recent-history average? Unspecified. This is the predictive-coding theory direction §10.2 hints at, but the actual loss for Hippocampus is undefined.

**The loss function for each Column is missing.** Open question 11 mentions "Loss function: MSE? Cross-entropy?" but doesn't address that _what's being predicted_ and _what the supervision signal is_ differ between Cortex and Hippocampus.

---

**Pass 4: Loss conservation and routing math**

§5.5 invariant: `Σ children_shares = parent_loss`. This is enforced by pre-normalization (§5.6): `share = loss × normalized_contribution_i` where `Σ normalized_contribution = 1`.

But §5.6 says pre-normalization happens at the _module_ level, "once per pass." So each module pre-normalizes its distribution memory once per forward pass.

Question: when a child receives its share and recurses, does it also pre-normalize _its_ distribution memory? If so, the child's pre-normalization is independent of the parent's. The numbers don't have to match. The cascade works if each level normalizes locally.

But there's a subtle issue: distribution memory at the Ganglion level is measurement caps, not SRAM. How do you "pre-normalize" a set of 29 analog caps? You'd need a 29-input analog normalizer (each output = input / sum). That's hard.

§5.8 says "Higher-level measurement is cheaper because it operates on fewer, larger signals." So at higher levels, the sums are over fewer children (4 G/S blocks per Column, ~3 Columns in Limbic). Pre-normalizing 4 SRAM values is just digital division — easy. Pre-normalizing 29 analog caps is hard.

**Hidden cost: the per-Ganglion division for normalization is non-trivial.** Not discussed.

Alternative: skip the pre-normalization at the Ganglion level. Just multiply: `share_k = loss × measurement_k`. But then the _total_ of shares at the Ganglion is `loss × Σ measurements`, which is not equal to `loss`. **Loss conservation breaks at the Ganglion level if normalization is skipped.**

So either you eat the per-Ganglion divide, or you violate loss conservation, or you handle it some clever way. None of these is in the spec.

---

**Pass 5: The Hippocampus update math**

§10.7 says backward flow is the same hierarchical diffusion. But Hippocampus is gated — its `update_signal` only fires every k clocks. So when Hippocampus's update fires, what loss does it backprop?

Two interpretations:

- (a) The accumulated loss over the last k clocks (sum of momentum). But the Brainstem broadcasts current loss each clock. Where is the accumulation done?
- (b) Only the loss from the k-th clock. But then Hippocampus learns from a sample of timesteps, not all of them.

(a) is more biologically faithful (sleep consolidation does aggregate). But it requires Hippocampus to _aggregate_ loss between consolidations. Where does that aggregation happen? The momentum SRAM aggregates _measurements_ (forward signals), not losses.

So either Hippocampus's loss is also aggregated somewhere (new state), or it learns from punctual samples (which is statistically biased — k-th sample isn't representative).

**This is a real gap.** Hippocampus needs a per-Hippocampus-scap eligibility-trace-style accumulator for _backward signal_, separate from forward momentum.

Or — and this is interesting — perhaps the momentum SRAM _is_ the eligibility trace, and the consolidation pulse acts on it. In that reading, momentum is updated every clock (forward measurements arrive every clock), but weight is only updated when consolidation fires. The pulse-width broadcast on consolidation can encode aggregated loss, and the local momentum (now larger because it's accumulated over k clocks) does the rest.

But that requires the Brainstem to send an aggregated loss on consolidation clocks. That's another Brainstem responsibility not listed.

---

**Pass 6: SpecialGeneralist mask coverage**

§9 has G receiving a context mask M_i from Specialist S_i. The mask gates G's neurons. But:

- What's the mask width? If G has 32 neurons (hidden), the mask is at least 32 bits — but that's per-clock per Specialist. Where do these bits live? §9.4 says "G has an active-mask register (small SRAM)" — so G has one mask register and it gets overwritten each call. Fine.

- Are the masks hardcoded mutually exclusive (M1, M2, M3 cover disjoint G-neurons) or overlapping? Hardcoded mode (§9.5 option 1) is undefined on this point. Mutually exclusive is the simplest, but it means G's effective capacity is partitioned three ways (each S only sees 1/3 of G). That's not Lottery-Ticket-style reuse anymore, that's just three sub-networks under one address.

If overlapping, the gradient collision problem returns _within the overlap region_. The whole point of gating was to avoid collision.

**§9 doesn't address whether masks should overlap.** This is structural.

- More importantly: SpecialGeneralist's whole value proposition is that G _learns multiple functions_. If masks are mutually exclusive and hardcoded, G isn't learning multiple functions — it's three independent sub-networks. The "G learns multiple functions" claim only works if masks have _enough overlap to learn shared structure but enough separation to avoid collision_. That's a delicate balance. Not addressed.

---

**Pass 7: The two-timescale interpretation**

§10.2 says Hippocampus updates every k clocks "with a large pulse when it fires." The intuition is: same per-batch impact, fewer batches.

But this isn't quite right. If Cortex updates every clock with pulse-width `L` (loss), Hippocampus updates every k clocks with pulse-width `k·L`? Or `L` (same)? Or some accumulated quantity?

The bullet says "Slow effective; large pulse when it fires." So pulse is large at Hippocampus update time. But where does that come from? The Brainstem must know it's a Hippocampus update clock and adjust the broadcast pulse width accordingly.

But broadcast is global — Cortex scaps and Hippocampus scaps both see the same broadcast bus. If the Brainstem sends `k·L` on a Hippocampus update clock, Cortex scaps also see `k·L` and update too aggressively.

So either:

- (a) There are separate broadcast buses for Cortex and Hippocampus. Probably yes, since they're separate Columns with separate Column-local buses.
- (b) The gating logic is at the receive side: Hippocampus scaps multiply incoming pulse by k internally.

(a) is the cleaner reading and matches the existing hierarchy (each level has its own bus). So Cortex Column has its own bus carrying `L` every clock; Hippocampus Column has its own bus carrying `0` k-1 clocks and a larger pulse on the k-th. Fine.

But that means the per-Column bus carries different temporal signals. The hierarchy is asymmetric in time.

**Should be made explicit.**

---

**Pass 8: Initialization and how H7 actually plays out**

§16 open question 9: "Small uniform magnitudes + random signs + zero momentum (baseline)." But the momentum needs to be non-zero for any update to happen (`ΔW = pulse × momentum × direction`, if momentum = 0, ΔW = 0).

So at boot, all weights have zero momentum → no updates can happen → no learning.

Wait — momentum is filled by the _forward pass measurements_ (§7.4 step 6). So momentum becomes non-zero after first forward pass. Then learning can happen on the backward pass.

But §6.3 "floor at 1" only kicks in _after_ momentum decays toward zero. At boot, momentum starts at 0 and is raised by EMA from measurements. As long as some measurements exist, momentum becomes non-zero.

So this works _if_ measurements are non-zero. But measurements are `|a · W|`. If weights are uniformly small but non-zero, and inputs are non-zero, measurements are non-zero. OK.

But for scaps where the input `a` is zero (e.g. ReLU has cut off the upstream neuron, or the input pattern just has zeros), measurement is zero. If a scap consistently sees `a = 0`, its momentum stays at 0 (or hits the floor at 1).

Then when it's _not_ in a dead pattern but starts contributing, its momentum is still near floor. Updates are tiny. **This is the dead-weight collapse problem.** §5.4 already names it. But it's not just about weight magnitude collapsing — it's also about whether momentum has a chance to grow.

The floor at 1 helps. But "1 out of 65,536" levels of momentum is tiny. Maybe the floor should be higher (1024? a percentile of the distribution?). This is testable.

---

**Pass 9: The "no LDR/STR" claim**

H5 says weights never leave the substrate during operation. Let me sanity-check.

Weight is in capacitor. Refill comes from 8-bit SRAM (which holds the reference level). The refill operation reads SRAM and refreshes the capacitor — that's a load/store internally, but neither leaves the chip. OK.

Boot: weights serialized in. Shutdown: weights serialized out. Both outside "operation." OK.

But: the Brainstem reads predictions via ADC. Those predictions came from output capacitors. Is the ADC inside the chip or outside? If inside, no boundary crossed. The Brainstem is on-chip (it's a chip module). Predictions go from output caps to ADC to Brainstem, all on-chip. Loss computed on-chip. Broadcasts go out via on-chip buses. OK.

The Brainstem's community SRAM map — is that part of the weight state? It's set at boot and never changes during operation. It's structural, not learned. So it doesn't count as "weight" that needs no LDR/STR. OK.

What about labels? Labels come _from outside_ the chip. They enter every clock. They aren't weights, they're inputs. So H5 holds.

**H5 stands.**

---

**Pass 10: What's the "task" really?**

§17 Phase 2 tasks: XOR, sine regression, two-moons classification. Reasonable starting points.

Phase 4 task: "recall task." Undefined. Recall _what_? Memorize a sequence, then recall a partial cue? Memorize a static set, recognize members? Big difference.

For a recurrent predictor (Limbic Loop), the natural task is **sequence prediction**. Feed a sequence, ask the system to predict the next element. "Recall from partial cue" then becomes: feed a prefix of a learned sequence, see if the network completes it.

But this requires the network to _memorize specific sequences_, which is what Hippocampus is supposed to do. And it requires evaluation infrastructure (was the completion correct?).

**Phase 4 needs a concrete task definition.** Right now it's hand-wavy.

---

**Pass 11: The reading of `|a · W|` as a "natural measurement"**

§5.2 says: "The forward-pass current through a scap is `a · W`." But is this actually what the substrate measures?

The current through a single scap is its input voltage (representing `a`) divided by its effective resistance (representing `W`, or rather `1/W`). So the current is `a · W` if the scap's circuit is configured to multiply, but it's `a / W` if configured to divide.

Practically, in an op-amp-based multiplier with a capacitor weight, the current through the scap is proportional to `a × W` _only with the right circuit topology_. The architecture handwaves this — §3.x doesn't specify the multiplier topology in detail.

This is fine for a Python sim (we choose `a · W` by definition). But the "substrate measures it for free" claim is contingent on circuit choices that haven't been spelled out.

Also: §7.4 measures "the current that scap delivers" via time-to-threshold on a measurement cap. Time-to-threshold is `1/current`. So actually the _measurement_ is `1/(a·W)`, not `a·W`. To get attribution proportional to `a·W`, the distribution math has to invert.

Going back to my Pass 1 worry: **what's stored is `1/(a·W)` (or `T = time-to-threshold`), but what's needed for attribution is `a·W` (or `1/T`).** The inversion is unaddressed.

A reasonable fix: instead of measuring `T = time-to-threshold`, you could measure `voltage-after-fixed-time` (charge accumulated in a fixed window). That's linear in current. But the spec says time-to-threshold. Either change to voltage-after-time, or add an inversion step.

**This is a real concrete gap.**

---

**Pass 12: The relationship between H1, H2, H3 — are they independent?**

H1: attribution learning converges (testable on single Ganglion).
H2: SpecialGeneralist > plain G-reuse (testable on a Column).
H3: Limbic Loop converges (testable on full hierarchy).

Each builds on the previous. If H1 fails, the others are moot. Phase 2 → 3 → 4 in §17 mirrors this. Good logical structure.

But notice: H2's test ("does SpecialGeneralist beat plain G-reuse?") in Phase 3 implicitly assumes H1 has succeeded enough that you can measure relative convergence. If H1 barely works, H2 might fail simply because nothing converges well enough to compare. The exit criterion of Phase 2 (within an order of magnitude of SGD) is the right kind of bound.

**Logically sound.**

---

**Pass 13: H6 — loss conservation as a real test**

H6 says simulation verifies `Σ children_shares = parent_loss`. This is testable in software trivially. But in hardware it's bounded by analog precision — the sum will never exactly equal the parent because of finite precision at each level. The hypothesis should be "conservation holds within ε for measurable ε," not "holds exactly."

§13 doesn't acknowledge this. **Should bound the tolerance.**

---

**Pass 14: Phase ordering and the Brainstem**

The Brainstem is the central controller, doing label management, loss compute, clock generation, ADC reading. None of the simulation phases explicitly build or test the Brainstem. Phase 1 is operators, Phase 2 is single Ganglion (where there is no hierarchy and the Brainstem degenerates to "compute loss, send pulse"). Phase 4 is Limbic Loop, where the Brainstem must orchestrate properly.

The Brainstem's specification is incomplete and there's no phase to validate it as a unit. **This is a hole.**

---

OK that's plenty for the substantive critique. Let me write this up.

---

Here's what I found. I'll order by severity: critical issues first (could derail the project if unaddressed), then significant ones (need fixing before draft4), then nits.

## Critical Issues — these could break the architecture

### C1. The scap update formula appears to double-count contribution

§6.5 says `weight_cap += pulse_width × momentum × direction`. §5.1 says the scap receives a _share_ via pulse width on the Ganglion-local bus. The share was computed by the Ganglion from each scap's measurement (which is proportional to current, which is proportional to `|a·W|`). The momentum SRAM is the EMA of those same measurements.

So both `pulse_width` (share = `loss × normalized_measurement`) and `momentum` (EMA of measurement) carry the same information — _how much this scap contributed_. Multiplying them together makes the update **quadratic in contribution**, not linear.

That might be intentional (Hebbian-style positive feedback amplification), but draft3.2 doesn't say so. The naive reading is a bug. **Resolve before draft4.**

If intentional: state "this is quadratic in contribution by design, because we want strongly-contributing scaps to amplify their dominance." Then justify why dead-weight collapse won't make this catastrophic.

If unintentional: pick one or the other. Either `pulse_width` carries the share and momentum scales nothing, or momentum is the local scaling and pulse_width is just a loss-magnitude broadcast.

### C2. Time-to-threshold measures `1/contribution`, not `contribution`

§7.4 measures time for measurement cap to cross A%→B%. Shorter time = stronger current = stronger contribution. So the stored value is **inversely** proportional to contribution.

When the Ganglion computes shares from these stored values, it needs to invert: a smaller stored T should give a _larger_ share. Either (a) the measurement is converted (stored as `T_max - T` or `1/T`) before being used, or (b) the share math uses the inverse.

Neither is in the spec. Without fixing this, the architecture would give the largest shares to the _weakest_ contributors. Sign error at the heart of the system.

**Fix:** specify that either the time-measure circuit outputs `1/T` (via a current-source-and-count scheme), or the stored value is converted to `voltage-after-fixed-time` instead of `time-to-threshold`. The latter is cleaner — store the analog voltage on the measurement cap after a fixed time window. That voltage is linear in contribution, no inversion needed.

### C3. Loss conservation requires per-Ganglion normalization of 29 analog measurements

§5.6 says shares are pre-normalized at each level. At the Ganglion level, that means dividing each of 29 analog measurement values by their sum. This requires an analog divider (hard) or an ADC + digital divider (expensive).

The architecture handwaves this with "the cost is per-module, not per-weight." Per-module is still 256 divisions per region per forward pass. That's real circuit area / time.

**Three options:**

- Build the analog divider (specify how).
- ADC at the Ganglion output of the measurement bank, do the divide digitally, store as SRAM (also specify how).
- Skip normalization at the Ganglion level, accept that loss conservation breaks below the Ganglion (just at the bottom level). This is probably acceptable — local conservation violation is bounded by Ganglion size and the system still works in expectation. **But you have to acknowledge it.**

This needs a concrete decision before draft4.

### C4. Hippocampus consolidation is undefined

Hippocampus updates every k clocks. But what loss does it backprop on the k-th clock?

- If it's the loss at the k-th clock only, Hippocampus learns from punctual samples — statistically biased.
- If it's the accumulated loss over the k-clock window, the architecture needs an accumulator somewhere (Brainstem? Per-Hippocampus-scap eligibility trace?).
- If it's "use momentum as eligibility trace, large pulse on consolidation does the rest" — that's a plausible reading, but it requires the Brainstem to send a _larger_ pulse on consolidation clocks.

§4 lists Brainstem responsibilities but doesn't include "send aggregated/amplified loss on consolidation clocks." This is missing infrastructure.

**Fix:** specify what Hippocampus actually trains on. The eligibility-trace reading (momentum accumulates losses too, big pulse releases them) is biologically plausible and architecturally clean. State it explicitly.

## Significant Issues — fix in draft4

### S1. ADC location ambiguity

§4 says Brainstem has an ADC for reading predictions. §8.4 says distribution memory at higher levels is SRAM "after ADCs at the Brainstem interface." This implies _one_ ADC at the Brainstem.

But distribution measurement happens at every level (§5.8). Distribution memory is SRAM (16/12/10 bit). To fill SRAM from analog signals, every level needs its own measurement circuit or its own ADC.

The cleaner story: each level has its own ALU/measurement circuit (the Ganglion's measurement caps generalize upward as the "translate ALU" performs measurement of its inputs). State this explicitly.

### S2. Cortex/Hippocampus structural symmetry overclaimed

§10.2 commits to "same structure." But §10.4 gives Cortex two output heads (prediction + Commissure) and §10.5 implies Hippocampus also has both. The structure is identical only if you specify it that way. State explicitly that both Columns have two output heads.

Also: define what a "head" is — separate output Ganglia? Different output capacitors of the same Ganglion? Different output dimensions of the top-level Cortex Column?

### S3. Mask overlap policy in SpecialGeneralist

§9 doesn't say whether masks M₁, M₂, M₃ overlap or are mutually exclusive. The architecture's value depends critically on this:

- **Mutually exclusive masks** → G is just three independent sub-networks under one address space. No shared learning. SpecialGeneralist becomes just "partitioned G" — not really "learning multiple functions on the same hardware."
- **Overlapping masks** → real reuse, but gradient collision returns in the overlap. Need a strategy for the overlap region.
- **Partially overlapping with controlled overlap fraction** → goldilocks zone, but undefined.

Decide and state. Probably start with mutually exclusive for first sim (cleanest), then test overlap variants as optimization.

### S4. Hippocampus consolidation pulse must be per-Column

§10 has Hippocampus update every k clocks. If broadcasts are global, Cortex and Hippocampus see the same pulse, breaking the asymmetry. The architecture must have **per-Column buses** with independent timing.

The hierarchy in §3.3 implies this (each Column has its own bus). But §4.2 lists the Brainstem broadcasting `update_signal` on the global bus, singular. Need to be explicit: the Brainstem manages **separate update_signal buses per Column**, gated independently.

### S5. Brainstem responsibilities are incomplete

Listed in §4.2: read predictions, compute loss, broadcast, manage clocks. Missing:

- Holding the previous prediction for autoregressive loss computation (need 1-step memory of predictions vs incoming input as label).
- Per-Column update gating (different cadences for Cortex / Hippocampus / Commissure).
- Sending different pulse magnitudes per Column if consolidation uses amplified pulses (C4 fix).

The Brainstem is starting to be a real microcontroller, not "one MAC per inference." Should restate its budget honestly.

### S6. Phase 4 task is undefined

"Recall task" is too vague to test against. Define one of:

- Sequence prediction with partial-cue completion (memorize sequence A→B→C→D, given A→B, complete with C→D).
- Static pattern recognition with noisy input (memorize K patterns, present a noisy version of one, ask which K it is).

Sequence prediction matches the predictive-coding framing better and uses the autoregressive setup naturally.

## Smaller issues

### N1. Cross-reference error

§4.4 references "§13 (Future Tracks)" — should be §14.

### N2. H6 should bound the tolerance

`Σ children_shares = parent_loss` won't hold exactly in finite precision. State the bound (e.g. "within ε of measurable precision per level").

### N3. The "noise floor" in §5.4 isn't in the three paths

§5.4 mentions "(a) add a tiny random noise floor to weight updates" but this isn't part of the three paths listed below. Either add it as Path 0 (cheapest first remediation) or remove the mention.

### N4. Initialization needs concrete numbers

§16 says "small uniform magnitudes." How small? 10% of capacitor range? 1%? Initialization is mentioned as a known failure mode for attribution-based methods (§5.4 point 4) — it deserves a starting concrete value, not just "small."

### N5. Where is the Brainstem in the simulation phases?

None of the six phases in §17 explicitly builds or tests the Brainstem. Phase 4 implicitly does. Add a note in Phase 4 that this is when Brainstem behavior gets validated, or add a Phase 4.5 specifically for it.

## The single most important question

If I had to pick one thing for you to resolve before writing draft4, it's **C1 — the double-counting in the scap update formula.** That's the heart of the learning algorithm. If `momentum × pulse_width` is wrong, every other simulation result is suspect.

Sit with it. Either:

- The architecture is "share computes the gradient direction, momentum is the local sensitivity" — two different roles, and the multiplication is intentional. Then the project is doing a kind of _adaptive_ attribution where strongly-contributing scaps are amplified. This is novel and worth saying explicitly.
- The architecture is "pulse_width carries the share, momentum was supposed to be the previous batch's record so we have temporal smoothing." Then `pulse_width × momentum / total_momentum_at_Ganglion` might be the right formula, with momentum acting as a filter rather than a multiplier.
- The architecture is "momentum is for the next forward pass's normalization but doesn't enter the backward update." Then drop it from the §6.5 formula.

These are three substantively different learning rules. The current spec is consistent with all three. Pick one, write it out with a worked example on a 2-scap Ganglion, and check the math.

---

Everything else flows from that decision. Once C1 is fixed, the other issues are mechanical cleanup. If C1 turns out to mean the architecture is doing something genuinely novel (option 1), that becomes a real research contribution — and it should be H8 or so, with its own justification.

Want me to write out the three candidate update rules in detail with worked examples so you can pick? Or do you already have an intuition for which one you meant?

---

---

# My Opinion

C1. The scap update formula appears to double-count contribution
: Yeach, pulse_width seem being duplicate, but it act more like lr or a master control of this update. First we can use only duplicate = loss, all layer act at same lr. But you miss a bit, the weight_update_cap (the real capacitor that keep all mometum and change weight) = summation (a·W), we sum this momentum while run each batch. While real pulse_width we use only when update time. Making real weight_cap -= pulse_width \* weight_update_cap. It's on different duty, I determine.

C2. Time-to-threshold measures `1/contribution`, not `contribution`
: Yeah, good catch. Actualy we have to use 1/contribute. But I assume that in weight_update_cap will be already transform or compute to ready for update, it will keep only meaning of "how this weight contribute the output"

C3. Loss conservation requires per-Ganglion normalization of 29 analog measurements
: Yeah, it's so intricate about normalization compute, but it's so important. Our capacitor have limit range. But I think I will fix it since opamp ALU, not in binary. I think it may more easy. But eventually the thing that keep in each scap have to be final compute, ready to use.

The full image will be:

- Forward: many size of ALU go to compile Limbic Loop, column, ganglion, etc. Using global capacitor to hold temp value. While each ALU move to compute the prediction, that time it will record how each scap distribute with parallel.
- Backpropagation: Then the Brainstem chain the loss throught the brain level, each level size chian loss to child. Making all scap update with decentralize.

S4. Hippocampus consolidation pulse must be per-Column
: Correct, brain stem is just a global in local... 🤔🤣🤣 I mean that brain stem is just a main control of some group.

S5. Brainstem responsibilities are incomplete
: Yeah so right. But I don't think deep till those brain part yet. Because it's too deep and too much. But list those question challege in the draft will be good.

S6. Phase 4 task is undefined
: This part too, My model still not stable now. But list this question to remind me will be good.

Then for Smaller issues, Those vairant I didn't write it yet. But I have my mental model now. Just let for futhur.

So now can you update draft3.2 to draft3.3 to placehold those missing or error content?
