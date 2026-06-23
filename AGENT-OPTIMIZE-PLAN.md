# Agent-Optimize Plan — a 3-layer context hierarchy for AI agents

> **What this is.** A plan for restructuring the project's **AI-facing context** (`CLAUDE.md` + skills) into a
> **3-layer hierarchy** so a fresh agent loads *little* at the top and descends only into the branch it needs.
> **Rev. 2 (2026-06-24): validated against how others do it** — Claude Code's official large-codebase guide,
> Anthropic's context-engineering writeup, the cross-tool `AGENTS.md` standard, and Cursor's rules model. The
> good news up front: **the 3-layer idea is exactly the established pattern.** This rev keeps the structure and
> swaps our hand-rolled conventions for the **native mechanisms** that already implement them, and adds a
> cross-tool layer. Sources at the end.
>
> **Build status (2026-06-24): the core hierarchy is BUILT** — root [`AGENTS.md`](AGENTS.md) + a slimmed root
> [`CLAUDE.md`](CLAUDE.md), [`draft6.0/CLAUDE.md`](draft6.0/CLAUDE.md), thin per-phase signposts
> (`draft6.0/src/phaseN/CLAUDE.md`), and [`draft5.0/CLAUDE.md`](draft5.0/CLAUDE.md). Cross-tool = option **C**
> (self-contained `AGENTS.md`, no `@import` dependency on the always-loaded file). **Still pending (next pass):**
> the skills migration to native `.claude/skills/` + per-draft relocation (§6); the optional settings levers
> (`claudeMdExcludes` / read-deny, §5); hooks (§9.7).

---

## 0. The core move (one paragraph)

The current context is **flat** — one 240-line always-loaded `CLAUDE.md` plus flat `skill/` routers — and it
conflates two axes. **Axis A: stable vs shifting** (rules that never change vs status that changes every phase).
**Axis B: altitude** (*map* → *mental-model* → *detail*). The fix: **stable + map** at the root (always loaded,
tiny), **shifting + mental-model** in each `draftN/`, **raw detail** in each `phaseN/` (loaded only when an agent
is there). Claude Code **auto-loads a subdirectory's `CLAUDE.md` only when the agent touches files in that
subtree** — so deeper context costs *zero tokens until you descend*. Two payoffs: a phase-4 task loads
`root + draft6 + phase4` and **never** phase-2/3, and advancing a phase edits **one** draft-level file, not the root.

This is not a bespoke idea — it is **Claude Code's documented recommendation for large codebases**, and it lines
up with Anthropic's context-engineering principles and the `AGENTS.md` standard 60k+ repos use. §2 is the evidence.

---

## 1. The problems (the analysis — grounded in measurements)

| # | Problem | Evidence (measured) |
| - | ------- | ------------------- |
| **P1** | **Always-on bloat.** Root `CLAUDE.md` loads on *every* session — even a `docs/` typo fix pays for the whole draft-6 status. | `CLAUDE.md` = **240 lines** (Anthropic's guidance: keep CLAUDE.md **under ~200**, the denser the better). |
| **P2** | **Over-reading on complex tasks.** "Research material for phase 4" sends the agent into the *full* phase-2/3 trees + code, because nothing says a prior phase's gist is in **one** file. | `draft6.0/src/` = **6,662 lines** of markdown + code; each phase ~450–590. Two prior phases ≈ 1,000+ lines for a one-line fact. |
| **P3** | **Shifting churn — backwards.** Every phase you rewrite the root `CLAUDE.md` (status, verdicts). The *most volatile* content sits in the *always-loaded* file. | It changed again this session. |
| **P4** | **Imprecise routing.** `skill/` maps point at *folders*, not the **minimal file set + a stop-here budget**, so the agent reads broadly "to be safe." | `skill/` = **920 lines** across 6 maps; all folder-level routers. |
| **P5** | **Built for one draft.** One root file + flat skills can't localize per-draft/phase, so everything lives high and central. | No nested `CLAUDE.md`; no `.claude/skills/`; the tree is one level deep. |

**The deeper "why" (from the research): context rot.** It isn't only token cost. Studies show model accuracy
*decreases* as the token count grows — an LLM has a finite "attention budget," and irrelevant context is *noise
that degrades output*. So a smaller, sharper context isn't just cheaper, it's **more correct**. That reframes the
whole exercise: we're not saving money, we're making the agent *better*.

---

## 2. How others do this (the evidence — so we're not inventing)

Four independent sources, one consensus: **layer context by directory, keep the top tiny, load the rest on demand.**

- **Claude Code — official large-codebase guide.** Recommends *exactly* this: per-directory `CLAUDE.md`, where the
  root holds repo-wide rules and each subdirectory adds its own; **loaded lazily** (root + ancestors at launch,
  a subdir's file only when Claude reads there; **siblings never cross-load**). It ships native levers we should
  use instead of hand-rolling: `claudeMdExcludes`, path-scoped `.claude/rules/`, per-directory `.claude/skills/`,
  `permissions.deny` for file reads, and **starting Claude from a subdirectory** to scope a session. (§5.)
- **Anthropic — context engineering.** The principle behind the plan: prefer **just-in-time** loading (keep
  lightweight identifiers — paths — and fetch on demand) over upfront; **progressive disclosure** (assemble
  understanding layer by layer, keep only what's necessary); **sub-agent isolation** (a subagent burns 10k+ tokens
  and returns a 1–2k summary, keeping the detail out of the main thread); and write each prompt at the **"right
  altitude"** — specific enough to guide, not a brittle wall of rules.
- **`AGENTS.md` — the cross-tool standard.** A README-for-agents that **30+ tools read** (Cursor, Copilot, Codex,
  Jules, Devin, Aider, Zed, Warp…), **60k+ repos**, now under the Linux Foundation. Same nesting model (nearest
  wins). Claude Code reads `CLAUDE.md`, *not* `AGENTS.md` — but bridges to it cleanly (§7). Relevant because your
  repo is going to professors who may use *any* tool. (§7 is the decision.)
- **Cursor — rules model.** Gives a clean vocabulary for *when* context loads, which we adopt as our load-tier
  language (§3): **Always / Auto-attached (glob) / Agent-requested (description) / Manual.**

**Verdict: keep the plan; upgrade the mechanism.** Our 3 layers = the official pattern (we just go one level
deeper, root → draft → phase, which the depth of this project earns). The revisions below are (a) use the native
features, (b) add the `AGENTS.md` portability layer, (c) name the load-tiers.

---

## 3. The principles (what the new shape optimizes for)

1. **Stable ≠ shifting.** Root = stable only (identity, collaboration rules, methodology, naming, the router).
   Anything dated/verdict-bearing moves **down**.
2. **Right altitude per level.** *Map* (where things are) → *mental-model* (how this draft thinks) → *detail*
   (results/code). Declare your tier and **stop**.
3. **Four load-modes (the Cursor vocabulary), mapped to Claude Code:**
   | Mode | Loads when | Claude Code mechanism | Use for |
   | --- | --- | --- | --- |
   | **Always** | every request | root `CLAUDE.md` (+ ancestors) | identity + rules only — keep **< ~200 lines** |
   | **Auto (path)** | editing files under a path | nested `CLAUDE.md` / `.claude/rules/` `paths:` glob | per-draft, per-phase conventions |
   | **Agent-requested** | the task matches a description | `.claude/skills/<name>/SKILL.md` | "find a paper", "run a phase" |
   | **Manual** | explicitly invoked | `/command` or `@file` | the `/orient`-family moves |
4. **Light top, deep on demand.** Every level is an **index that lets the agent decide what to load without
   loading it.** Traverse small indices, read one or two leaves.
5. **Summaries stand in for raw reads.** A phase's `summarize`/`RESULTS` must be complete enough that an agent
   *never needs the raw code or a re-run* — your words: *"get context without reading code or running commands."*
6. **The context wall (heavy-read escape).** For read-heavy work (understand a prior phase, hunt a paper),
   **dispatch a subagent** — it reads in its own window and returns a ~1–2k-token conclusion. Officially endorsed
   ("run exploration in a subagent so file reads stay out of the main conversation").

---

## 4. The 3-layer hierarchy — what each file holds  ★

```
LOAD PATH for "work on phase 4"            what loads        tier / mode
────────────────────────────────────────   ──────────────    ─────────────────
root/CLAUDE.md            (always)          < ~120 lines      MAP + rules   (Always)
  └─ draft6.0/CLAUDE.md   (auto, in-draft)  < ~120 lines      MENTAL MODEL  (Auto/path)
       └─ phase4/CLAUDE.md (auto, in-phase) ~20–30 lines      SIGNPOST      (Auto/path)
            └─ phase4-summarize.md / RESULTS.md / expK/   (read on demand)  DETAIL
phase2/, phase3/  ← NOT loaded. Need their gist? read ONE phaseN-summarize.md, or send a subagent.
```
*(Pro lever, from the official guide: for a phase-scoped task, **start Claude *in* `draft6.0/src/phase4/`** — it
then loads that file + every ancestor and nothing sideways. Starting at the repo root keeps everything reachable
but lazy.)*

### Layer 1 — root (the map; always loaded; **stable only**; target < ~120 lines)
- **`CLAUDE.md`** holds only cross-draft invariants: one-paragraph "what this is"; the **collaboration rules**;
  the **methodology rules**; the **naming discipline**; the **router** ("draft 6 → `draft6.0/CLAUDE.md`; history →
  `draft5.0/`; the journey → `draft-journey/`; cross-draft moves → `skill/`"); and the **reading-budget rule**
  ("load your tier and stop; heavy cross-phase reads → dispatch a subagent"). **Removed:** per-phase verdicts,
  draft-6 architecture, the draft-6 file tree, the draft-6 routing table → all to Layer 2.
- **`skill/`** keeps only **cross-draft** moves (`workflows.md`) + a one-line pointer to each draft's skills.
- **`.claude/`**: `commands/` stay; add `claudeMdExcludes` + `permissions.deny` (§5); optionally `skills/`.

### Layer 2 — `draftN/` (mental model + status; auto-loads in-draft; **shifting lives here**)
- **`draftN/CLAUDE.md`** (NEW) — *the file you edit when a phase advances, never the root:* architecture-in-one-
  breath; the **status ladder** (one line per phase + a pointer to each `phaseN-summarize.md`); the file map; the
  routing table (results → `src/stage1-report.md`; a paper → `research/papers/{phase1-2,phase3}/`; decisions →
  `idea/main.ideas.v1.md`; deep dump → `context.md`).
- **`draftN/context.md`** — the rich cold-start narrative (already exists). `CLAUDE.md` *points to* it.
- **`draftN/.claude/skills/`** — this draft's task skills (§6).

### Layer 3 — `phaseN/` (detail; auto-loads in-phase)
- **`phaseN/CLAUDE.md`** (NEW; thin, ~20–30 lines) — a **signpost**: one-line identity + verdict; "authoritative
  record = `phaseN-summarize.md` + `RESULTS.md`; cards = `expK/`; apparatus = `pNlib.py`; figs = `figs_*/`"; and
  the **read-budget**: *"to use this phase from elsewhere, read `phaseN-summarize.md` only."*
- **The existing `*-summarize.md` / `RESULTS.md` / `*-report.md` / `expK/`** = the detail tier, unchanged.

> Net: a phase-4 task loads ~**220 lines** of layered signposts and *chooses* to open one summary. Today the same
> task can pull 1,000+ lines of phase-2/3 it never needed.

---

## 5. The native mechanisms (use these instead of hand-rolling)

All are Claude Code features confirmed in the official large-codebase guide:

| Mechanism | What it does | Use here for |
| --- | --- | --- |
| **Per-directory `CLAUDE.md`** | lazy-loads with its subtree | the Layer-2 / Layer-3 files above |
| **`claudeMdExcludes`** (settings, glob) | never-load specific `CLAUDE.md` | drop `draft5.0/` (fossil) + `draft-journey/` + sibling drafts from load |
| **Path-scoped `.claude/rules/`** (`paths:` glob) | central rule that loads when a matching file is touched | an alternative to nested `CLAUDE.md` when a rule spans scattered paths (e.g. all `expK/experiment-*.md`) |
| **`.claude/skills/<name>/SKILL.md`** (`description`, optional `paths:`) | model **auto-loads** the skill when the task matches; only the chosen skill's body enters context | the task-scoped skills in §6 (the real "loads only when relevant") |
| **`permissions.deny` → `Read(...)`** | blocks reading paths | the figure binaries (`**/figs_*/arrays.npz`), any generated output |
| **Start Claude from a subdirectory** | loads only that dir + ancestors | scope a session to one phase/draft (biggest cheap win) |
| **Subagents for investigation** | reads in an isolated window, returns a summary | the context wall (§3.6) |
| **`SessionStart` hook** (optional) | prints a recommendation at launch | "you're in phase 4 — load the `run-phase` skill" |

**Important format note:** Claude Code "skills" are `.claude/skills/<name>/SKILL.md` with a `description` the model
matches on — *different* from our current `skill/*.md` reference docs + `.claude/commands/` slash-triggers. The
auto-load-by-relevance behavior you want comes from the **`.claude/skills/` form**, so the migration in §6 is the
part that actually fixes P4. **Descriptions get truncated when many skills exist → keep them short and lead with
the words a request would contain** ("find the paper behind…", "run a phase-N experiment").

---

## 6. Skills — audit (migrate to the native form) + read-budgets

**Move draft-specific maps down, convert them to `.claude/skills/`, give each a stop-here budget.**

| Current `skill/*.md` | Action | New home (native form) |
| --- | --- | --- |
| `workflows.md` | keep (cross-draft) | root `.claude/skills/workflows/SKILL.md` (or keep as `/commands`) |
| `project-explore.md` | move + convert | `draft6.0/.claude/skills/explore/SKILL.md` |
| `architecture-research.md` | move + convert | `draft6.0/.claude/skills/architecture/SKILL.md` |
| `simulation-experiments.md` | move + convert | `draft6.0/.claude/skills/run-experiment/SKILL.md` |
| `sureSkill.md` | move + convert | `draft6.0/.claude/skills/confidence-log/SKILL.md` |
| `simulator-code.md` | move (historical) | `draft5.0/.claude/skills/` |

**Add — task-scoped skills with explicit budgets (the P2/P4 fix):**
- **`find-paper`** — loads **only** the two `research/papers/{phase1-2,phase3}/README.md` + `research/survey/summary.detail.md`; returns the path. *Budget: ≤3 index files; never open a story to find one.* (`paths:` could auto-attach it under `research/`.)
- **`run-phase-experiment`** — loads the target `phaseN/README.md` + `result-format.md` + the one `expK` card. *Budget: that phase only; prior-phase context comes from its `summarize`, not its code.*
- **`read-results`** — answer-about-results without editing → best as a **subagent** (own window, returns prose). Encode the rule; don't build a fleet yet.

**The budget line every skill carries:** *"Load the files named above and stop. To pull in another phase/draft,
read its one `…-summarize.md` (or its Layer-2 `CLAUDE.md`); anything heavier → dispatch a subagent."*

---

## 7. `AGENTS.md` — the cross-tool layer (a new decision)

The thing the plan missed: **`AGENTS.md` is the portable standard** every non-Claude tool reads. Your repo is
headed to two professors (who may use Cursor / Copilot / Codex) and you want it broadly agent-friendly — so a
Claude-only `CLAUDE.md` leaves that audience with nothing. But **Claude Code does not read `AGENTS.md` natively.**
The clean bridge (works on Windows, which matters here):

- **Canonical content in `AGENTS.md`** at each level; a one-line **`CLAUDE.md` containing `@AGENTS.md`** beside it.
  Claude Code's `@import` pulls the AGENTS.md in (recursive, up to 4 hops, Windows-safe); every other tool reads
  `AGENTS.md` directly. *Write once, read everywhere.* (Symlinking `CLAUDE.md → AGENTS.md` also works but needs
  Admin/Developer-Mode on Windows — avoid; use `@import`.)

`⟦DECISION⟧` Three options, pick one:
- **(A) `CLAUDE.md`-only (simplest).** Claude Code is your tool; least moving parts. Lose cross-tool portability.
- **(B) `AGENTS.md` canonical + `CLAUDE.md` `@import` shim at each level (recommended).** Portable + Claude-native;
  cost = one extra one-line file per layer (~6–10 tiny shims).
- **(C) Root `AGENTS.md` only** (cross-tool entry at the top), nested layers stay `CLAUDE.md`. A middle ground:
  other tools get the map, Claude Code gets the full hierarchy.

My lean: **(B)** if you want this to be a model professional repo (it's cheap and future-proofs); **(C)** if you
want 80 % of the benefit with almost no extra files. Avoid (A) only because the publish/multi-tool goal is real.

---

## 8. The churn fix — "never rewrite the root again" (solves P3)

The root holds nothing dated. Edit surface shrinks to the lowest level that changed:
- **Finish a phase** → write `phaseN/` (summarize/RESULTS exist) + add thin `phaseN/CLAUDE.md` + bump **one line**
  in `draft6.0/CLAUDE.md`'s ladder. **Root: untouched.**
- **Start draft 7** → create `draft7.0/` with its own `CLAUDE.md` + `.claude/skills/` (copy the draft-6 skeleton)
  + add **one router line** to the root. The "candidate all the time" shape, now cheap.
- **Change a collaboration/methodology rule** → edit the root (rare, correctly central).

---

## 9. Rough rollout (order; each step reversible + testable)

1. **`draft6.0/CLAUDE.md`** — move architecture + status ladder + file map + routing *out of root* into here. *(Biggest win; do first.)*
2. **Shrink root `CLAUDE.md`** to the stable skeleton + router (< ~120 lines).
3. **Add `claudeMdExcludes`** (drop `draft5.0/`, `draft-journey/`) + **`permissions.deny`** for figure binaries — instant load savings, zero content moves.
4. **Add thin `phaseN/CLAUDE.md` signposts** — write one template, copy ×4.
5. **Migrate skills to `.claude/skills/`** (per-draft) + write `find-paper` / `run-phase-experiment` with budgets.
6. **Decide §7 (AGENTS.md)**; if (B)/(C), add the `AGENTS.md` + `@import` shim(s).
7. *(Optional)* `SessionStart` hook to recommend the area's skill; a reader subagent if over-reading persists.

**Test the way it's used:** open a fresh session (or start *in* `phase4/`), run `/memory` to see what loaded —
it should be root + draft6 + phase4 signposts, nothing from phase2/3. The official debugging tip: if a rule is
ignored, it's likely in a nested file that hasn't loaded yet — `/memory` shows it.

---

## 10. Open decisions (your call before I build it)

1. **`AGENTS.md` adoption — §7 (A) / (B) / (C)?** Rec: **(B)** for a model repo, **(C)** for near-zero extra files.
2. **`phaseN` file: real `CLAUDE.md` (auto-loads) vs just `README.md`?** Rec: thin `phaseN/CLAUDE.md` — *after* a 2-minute test that nested lazy-load works in your version (`/memory`).
3. **Per-phase `CLAUDE.md` vs central `.claude/rules/` with a `paths:` glob?** Rec: per-phase `CLAUDE.md` (versioned beside the phase); use `.claude/rules/` only if a rule spans scattered paths.
4. **How thin is the root?** Rec: **< ~120 lines** (Anthropic says < ~200; we can beat it).
5. **Apply to `draft5.0/` (fossil)?** Rec: a thin `draft5.0/CLAUDE.md` ("superseded; here's its map") + `claudeMdExcludes` it from default load. No per-phase work on a fossil.
6. **Subagents now or just the built-in explorer?** Rec: built-in now; bespoke fleet only if 1–5 don't kill the over-reading.

---

## Sources

- Claude Code — [Set up Claude Code in a monorepo or large codebase](https://code.claude.com/docs/en/large-codebases) (nested CLAUDE.md, lazy load, `claudeMdExcludes`, `.claude/rules/`, per-directory skills, `permissions.deny`, start-from-subdir, subagents).
- Anthropic — [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (just-in-time loading, progressive disclosure, sub-agent isolation, context rot, right altitude).
- [AGENTS.md](https://agents.md/) — the cross-tool standard (nesting, tool support); [Codex AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md).
- Claude Code ↔ AGENTS.md bridge — [@import / symlink methods](https://gist.github.com/yurukusa/d36197848911f025add142abefcde685) and [ClaudeLog](https://claudelog.com/faqs/claude-md-agents-md-symlink/).
- Cursor — [Rules](https://cursor.com/docs/rules) (Always / Auto-attached-glob / Agent-requested / Manual modes; keep always-rules small).
- Anthropic — [Claude Code best practices](https://code.claude.com/docs/en/best-practices) (subagents for investigation; CLAUDE.md size/compression).
