# Ganglion Architecture — Dynamic Role Switching & Virtual Synapse Mapping

> **Status: design rationale + a future-track candidate. NOT promoted to the locked spec.** Captured
> 2026-05-31 from the author's own framing — a rationale he had designed earlier and wanted on record
> before it was lost again ("my genius is a curse; I forgot the best part because it makes sense to me but
> not to others"). This file is a faithful capture, not a spec edit.
>
> **Triage (per the §22 discipline / §20.17 promotion path):**
>
> - **§1–§2 below (Virtual Synapse Mapping; Region-vs-Amplification roles)** = *functional rationale for the
>   already-locked 2-3-3-2 topology.* It explains the **why** behind a locked decision (`§7.2`); it does
>   **not** change it. A candidate enrichment to `§7.2` if the author later wants it in the spec proper.
> - **§3 (Dynamic Role Switching)** = a **new training mechanism** (alternating *which layers learn*). It is
>   **not** in the baseline today (every Scap updates on every backward pass). → a **§21 Future Track**, with
>   a **§20** test hook. Do not fold it into the locked §1–§16 without the §20.17 promotion process.
> - **Connects to:** the open **L3/L4 activation experiment** (the author's "let L3/L4 have no violent
>   activation" probe), and the recent **paraboloid result** (one Ganglion cutting `0.1·(x₁+x₂)²` loss ~20×
>   under ±0.02 noise — see `skill/project-explore.md` §2). This note is the candidate *explanation* for
>   that result.

---

## 1. Virtual Synapse Mapping — the "synapse-less distance" bet

Real dendrites attenuate / gain a signal by **distance to the soma**, and biology's richness comes from
dense multi-synapse connectivity and dendritic geometry. Modelling that explicitly (a geometric variable
*d* per synapse, dense connections) is heavy in compute and silicon.

**The bet:** *project* that spatial/structural behaviour onto the constrained 2-3-3-2 layer mapping instead
of modelling it. Dendritic distance → attenuation/gain is captured **without** an explicit geometric
variable, by assigning **operational bounds across the cascade L2 → L3 → L4**. The whole 2-3-3-2 acts as
**one functional Axon unit** — complex multi-synapse behaviour mapped into localized analog primitives.

→ This is the *functional* companion to `§7.2`'s "path-diversity-per-scap" justification — another answer to
*why 2-3-3-2 is enough.*

## 2. Operational pipeline — Region Segmentation vs Signal Amplification

The Ganglion deliberately does **not** learn many high-level features at once. It splits the job into
localized per-layer roles:

- **L2 — Region Segmentation.** L2 carries the explicit activation (ReLU). Its job is *bounded region
  segmentation*: carving the input space into distinct boundary zones (up to **3 structural regions**, one
  per L2 neuron's hyperplane). It segments space; it does **not** track fine 1:1 shape geometry.
- **L3 & L4 — Cascading Gain (Signal Amplification).** A single layer lacks the raw differential drive to
  enforce *sharp* boundaries under analog noise. L3/L4 act as a **multi-stage analog amplifier cascade**
  (series-connected op-amps): they take L2's raw localized differential signals and drive them to **hard
  physical saturation** (`§6.6`), buying stability and noise immunity.

This is the functional reason behind the open **L3/L4 activation** question: L2 needs the segmenting
nonlinearity (ReLU); L3/L4 want amplification-to-saturation, not a ReLU clip.

## 3. Dynamic Role Switching (the leverage)

The architectural leverage: **dynamically alternate operational modes during runtime / learning** — unit
blocks alternate between **Region-Optimization** mode and **Gain-Amplification** mode across iterations.

- In Region-Optimization, attribution learning settles **boundary coordinates on the L2 Scaps**.
- In Gain-Amplification, **L3/L4 adaptively lock the amplification weights**.
- Alternating the two yields **piecewise-linear tracking** — enough to fit highly nonlinear surfaces (e.g.
  paraboloids) under active noise (±0.02), **without gradient math.**

In code terms this is a concrete proposal: an **alternating, block-wise attribution update** (close kin to
alternating / coordinate optimization), versus today's "every Scap updates every backward pass." It is the
candidate explanation for the paraboloid result.

## 4. Open questions for the §20 hook (if/when promoted)

- Does explicit mode-alternation beat the current all-at-once update on the paraboloid / nonlinear tasks?
  (One-thing-changed: role-switching vs the lean baseline, same task/seeds.)
- What sets the alternation cadence — every *k* steps? loss-triggered? — a tuning parameter, kin to the
  Limbic two-timescale *k*.
- Does it cooperate with Physical Saturation (L3/L4 → rail) cleanly, or fight it?
- Does the "≤3 regions per Ganglion" segmentation bound line up with the paths-per-scap story (`§7.2`)?

---

_Capture only — no spec section was edited. To promote §3 into the spec, add a §21 future-track entry and
follow §20.17 (a phase report citing data). §1–§2 may instead enrich §7.2 directly, at the author's call._
