# `auto-research/` — the automated literature sweep

> **What this is.** A machine-generated literature library, built by an **orchestrator + one-at-a-time subagents**
> loop. Each subagent takes **one topic**, understands the relevant slice of our project (via the graphify graph +
> one phase README), searches the open literature, writes **full paper summaries + a topic synthesis** here, and
> reports a short digest back. The orchestrator never reads papers into its own context — it reads only the digests,
> updates the queue, and picks the next topic. This runs **topic by topic, sequentially**, so if it stops we know
> **exactly** where.
>
> **This is NOT `draft6.0/research/`.** That folder is hand-curated and wired to real experiments and results — the
> project record. This folder is **automation output**: raw material for the author to read and ratify later. Treat
> everything here as **found, not yet vetted** until a human confirms it. Where a topic overlaps the curated library,
> the sweep goes **broader / newer** (2023–2026) and points back rather than duplicating the hand-written stories.

---

## How to read it (for a human coming back)

0. **[`_SWEEP-SYNTHESIS.md`](_SWEEP-SYNTHESIS.md)** — ★ **START HERE.** The master close-out: the five strategic reframes, the ranked experiment queue, the honest limits, the must-cite anchors. Then the five [`tierN-*/_TIERn-SYNTHESIS.md`](tier1-nearest-neighbors/_TIER1-SYNTHESIS.md) rollups.
1. **[`INDEX.md`](INDEX.md)** — the master table of every paper card: title · tier · topic · one-line relation to us · link. Skim everything found.
2. **[`BACKLOG.md`](BACKLOG.md)** — the topic queue and its status. What's done, what's active, what's next. This is also the **resume point** if the loop was interrupted.
3. **`tierN-*/<topic>/_SYNTHESIS.md`** — per topic: the landscape, **how WE differ**, and the gap. Read this before the individual cards.
4. **`tierN-*/<topic>/<author-year>.md`** — the per-paper cards (mechanism-first, with a "How it relates to us" section).

---

## The five tiers (what goes where)

| Tier | Folder | The question each topic answers | Compare-to-us? |
| ---- | ------ | ------------------------------- | -------------- |
| **1 — Nearest neighbors** | [`tier1-nearest-neighbors/`](tier1-nearest-neighbors/) | *Who else built something like the whole draft-6.0 object (forward-only + local + continual + on-chip), and exactly how are we different?* | **Yes — the point.** Prior art we'd have to cite. |
| **2 — Component optimization** | [`tier2-component-optimization/`](tier2-component-optimization/) | *For one organ we already have (SCFF bulk / closed-form namer / sleep / drift gate / mono-forward), what has the literature tried that we haven't, inside the P1–11 scope?* | **Yes** — against the specific organ. |
| **3 — North star / horizon** | [`tier3-north-star/`](tier3-north-star/) | *What's the buildable path to the horizon (recurrent thinking brain, the hippocampus organ = next build, "correctness is a feeling"), and who's closest?* | Yes — against the stated north star (root README). |
| **4 — Adjacent wildcards** | [`tier4-adjacent-wildcards/`](tier4-adjacent-wildcards/) | *What nearby field (analog in-memory compute, equilibrium propagation, neuromorphic, state-space, associative memory) has a tool that could change our game, even though it's out of the current experiment ladder?* | Light — note the leverage, don't force-fit. |
| **5 — Open exploration** | [`tier5-open-exploration/`](tier5-open-exploration/) | *What's worth knowing that we haven't slotted anywhere?* Free reading, foundational/inspirational. | **No** — capture the material, no forced comparison. |

Priority order for the sweep: **Tier 1 first** (a research-first project's top need is establishing prior art), then 2, then 3, then 4, with Tier 5 as spillover / leads.

---

## The mechanics (for the orchestrator / next session)

- **Loop:** pick the next `pending` topic in [`BACKLOG.md`](BACKLOG.md) → mark it `active` → spawn **one** `general-purpose` subagent with the brief in [`_protocol/subagent-brief-template.md`](_protocol/subagent-brief-template.md) → read only its digest → mark `done`, log outputs → enqueue any follow-on leads → repeat.
- **One subagent at a time.** No parallel fan-out — that's deliberate, so token exhaustion lands on a clean topic boundary.
- **The corpus lives on disk, not in the orchestrator's context.** Full detail is written to files; only a short digest returns. That's what lets the loop run long.
- **Resumable:** [`BACKLOG.md`](BACKLOG.md) is the single source of truth for state. A fresh session reads it and continues from the first non-`done` topic.

*Provenance: every card is machine-drafted from web search. Real links are required; anything unverified is flagged. Ratify before citing.*
