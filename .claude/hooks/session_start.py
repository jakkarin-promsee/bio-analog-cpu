#!/usr/bin/env python3
"""SessionStart hook -- prints a short orientation banner into context at launch,
so every session starts knowing the layered context + the skills and reaches for
the cheap path. Kept ASCII-only (this Windows console is cp874). Maintained per
AGENT-OPTIMIZE-GUIDE.md (the SessionStart-hook lever)."""
print(r"""[repo orientation -- Bio-Analog CPU]
Context is layered; load your tier and STOP:
  root CLAUDE.md (loaded) -> draftN/CLAUDE.md (auto in-draft) -> phaseN/CLAUDE.md (signpost) -> phaseN/README.md (front-door synthesis)
Live line = draft6.0/ (P1-P10 DONE, both stages; neocortex validated, S14; next = analog-realism).  History = draft5.0/.  Idea journey = draft-journey/.
Skills auto-load by task: project-frame, explore, folder-structure, writing-report;
  draft-6 (work in draft6.0/): status, run-experiment, find-paper, simulator-code.
Heavy lookup? read ONE phaseN/README.md, or dispatch the Explore subagent.
Tip: start Claude IN the subdir you're working in -- it loads only that chain.
Keeping the repo lean for agents: AGENT-OPTIMIZE-GUIDE.md
""")
