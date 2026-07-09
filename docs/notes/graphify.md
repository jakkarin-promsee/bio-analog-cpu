# graphify — how to use the research map

> Beginner guide for this repo's knowledge graph. Built 2026-07-09; covers the full Bio-AnalogCPU corpus
> (draft-journey → draft5 collapse → draft6 phases 1–11, code, north-star papers). **Quality over quantity:**
> the map tracks *thought → experiment → result → interpretation → new decision*, not every file equally.

---

## What this is (in one paragraph)

**graphify** turns the repo into a **queryable graph**: nodes = concepts, experiments, code symbols, documents;
edges = citations, rationale, imports, inferred links. You get three things in `graphify-out/`:

| File | What it is | When you use it |
| --- | --- | --- |
| **`graph.html`** | Interactive map (community view) | Browse visually — double-click communities, search |
| **`graph.json`** | Raw graph data | Agent queries, future tools |
| **`GRAPH_REPORT.md`** | Audit report — god nodes, surprising bridges, suggested questions | Read once to see what the graph *noticed* |

Current scale (first full build): **~6,600 nodes · ~9,100 edges · 524 communities**. Markdown + code are complete;
experiment PNG figures are partially wired (Phase 1–2 done; other phases queued).

---

## Open the map (30 seconds)

1. In File Explorer, go to the repo root → `graphify-out/`
2. Double-click **`graph.html`** (opens in Chrome/Edge/Firefox)
3. You see **community bubbles** — each cluster is a topic (e.g. "Phase 6 Noise Hardening", "Project Soul & History")
4. Click a bubble to zoom; use the search box to find a name like `SCFF`, `depth decay`, `missing sign`

That's it for browsing. No install needed for the HTML view.

---

## Ask questions (CLI)

graphify is installed on this machine via `uv tool install graphifyy`. From the **repo root** in PowerShell:

```powershell
cd C:\Users\BTCOM\Desktop\0_Project\Bio-AnalogCPU

# Broad context — "how does X connect to the project?"
graphify query "Why did draft5 collapse and what replaced it?"

# Shortest path between two ideas
graphify path "missing sign" "SCFFContrastOLU"

# Plain-language explanation of one node
graphify explain "NoiseAugContrast"
```

**Tip:** phrase questions with **words that appear in your docs** (`SCFF`, `Phase 5`, `depth decay`, `attribution`).
The query tool expands against the graph's vocabulary.

**Easier for beginners:** ask your AI agent in Cursor — *"Use graphify to trace how Phase 5 fixed depth decay."*
Agents should query the graph instead of reading 50 markdown files.

---

## What's inside the graph (what got extracted)

| Layer | Source | What it captures |
| --- | --- | --- |
| **Semantic (docs)** | All `.md` in scope | Concepts, decisions, experiment verdicts, `rationale` on *why* |
| **AST (code)** | `.py` under the repo | Imports, calls, class/function structure |
| **Images (partial)** | `.png` experiment figures | Chart metrics + links back to experiment cards |

**Excluded from scan** (on purpose — not research record):

- `.obsidian/` — personal vault sync
- `post/` — social post drafts
- `temp/`, `temp2/` — scratch

---

## When to update the graph

Update after **substantial** corpus changes — not every typo fix.

| You did… | Action |
| --- | --- |
| Finished a new phase (new `RESULTS.md`, experiment cards, report) | Incremental update (below) |
| Wrote a big decision doc (`main.ideas.v1.md`, north-star note) | Incremental update |
| Added many experiment figures you care about | Ask agent to extract image chunks + merge |
| Only changed Python internals, no new docs | Optional — AST refresh on full rebuild |
| Renamed/moved many files | Full rebuild (paths affect node IDs) |

---

## How to update (incremental — the normal path)

**Option A — ask the agent (recommended while you're learning):**

> "graphify `--update` on this repo — I added Phase 12 docs"  
> or  
> "Rebuild graphify for the new experiment cards in `draft6.0/src/phaseN/`"

The agent runs detect → re-extract **only changed/new files** → merge → refresh `graph.html`.

**Option B — yourself (once comfortable):**

```powershell
cd C:\Users\BTCOM\Desktop\0_Project\Bio-AnalogCPU

# 1. Ensure graphify is available
graphify --help

# 2. Incremental update (uses graphify-out/manifest.json to find what changed)
#    In Cursor, invoke the graphify skill with --update, or ask the agent to run Step 1–9 with --update.
```

The skill lives at the global Cursor skill `graphify`; the repo remembers scan root in
`graphify-out/.graphify_root`.

**Deep mode** (`--mode deep`): richer inferred edges between docs — use for a major rebuild, not daily edits.

---

## Full rebuild (rare)

Only when:

- First time on a new machine (clone already has `graph.json` — you usually **don't** need this)
- You intentionally want to re-extract everything with new settings
- Incremental update looks wrong after big moves/renames

Ask the agent: *"Full graphify rebuild on `.` with exclusions `.obsidian post temp temp2`, deep mode."*
Expect **time + subagents** — semantic extraction over ~300 markdown files is the expensive step.

---

## Files in `graphify-out/` (what to commit vs ignore)

**Tracked in git (the durable map):**

- `graph.json`, `graph.html`, `GRAPH_REPORT.md` — the product
- `manifest.json` — file fingerprints for `--update`
- `.graphify_labels.json`, `.graphify_root`, `.graphify_python` — metadata
- `cost.json` — token cost log (mostly zeros for subagent extraction)
- `cache/semantic/` — cached doc extractions (speeds up incremental)

**Ignored (rebuild intermediates — regenerated automatically):**

- `.graphify_ast.json`, `.graphify_extract.json`, `.graphify_semantic.json`
- `.graphify_chunk_*.json`, `.graphify_detect.json`, etc.
- `cache/ast/` — code AST cache (large, reproducible)

See root `.gitignore` for the exact list.

---

## Reading `GRAPH_REPORT.md`

Worth skimming once. Key sections:

1. **God nodes** — most connected concepts (`SCFF`, `MLP`, `main.ideas.v1`, …)
2. **Surprising connections** — cross-era bridges the extractor inferred (e.g. draft5 attribution ↔ draft6 "direction is expensive")
3. **Hyperedges** — groups that belong together (hierarchical diffusion chain, frozen neocortex cell, Phase 5 ladder)
4. **Suggested questions** — good prompts for `graphify query`

Edge tags: **EXTRACTED** = explicit in source; **INFERRED** = model-linked (check if critical); **AMBIGUOUS** = low confidence.

---

## Example workflows

### "Why did we pick RanPAC over SLDA?"

```powershell
graphify query "Why RanPAC over SLDA readout Phase 7 Phase 8"
```

Or open `graph.html`, search `RanPAC`.

### "Trace the draft5 → draft6 pivot"

```powershell
graphify query "missing sign attribution collapse SCFF GD rebuild"
graphify path "Missing-Sign" "SCFF"
```

### "What calls `readout_feats`?"

```powershell
graphify explain "readout_feats()"
```

(AST/code edges — complements reading `p7lib.py`).

### After you finish Phase 12

1. Write `RESULTS.md` + experiment cards as usual
2. Tell agent: *"graphify update — merge Phase 12 docs"*
3. Open refreshed `graph.html`, search your new verdict tag

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `graphify: command not found` | `uv tool install graphifyy` or ask agent to re-resolve `graphify-out/.graphify_python` |
| Query returns noise | Narrow the question; use exact terms from `RESULTS.md` / `design.md` |
| Graph feels stale | Run incremental update after your last doc commit |
| `graph.html` empty / broken | Regenerate: `graphify export html` from repo root |
| Huge git diff after rebuild | Only commit `graph.json`, `graph.html`, `GRAPH_REPORT.md`, `manifest.json`, semantic cache — not `.graphify_ast.json` |

---

## For agents (short)

If `graphify-out/graph.json` exists and the user asks about architecture, history, experiments, or cross-phase
wiring → **`graphify query` first**, then read specific files only where the graph points. Router:
[`CLAUDE.md`](../../CLAUDE.md) § Research knowledge graph. Skill: global `graphify` skill.

---

## What's not done yet

- **~250 experiment PNGs** (phases 3–11, draft5) — not all linked as image nodes yet; verdicts already live in
  markdown. Ask for *"graphify image extraction phase N figures"* to add a batch.
- **1 PDF** in corpus — minor; papers are mostly `.md` summaries.

When those land, incremental update merges them without redoing the whole corpus.
