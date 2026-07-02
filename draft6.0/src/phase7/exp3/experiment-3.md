# P7.3 — the bursty-stream imbalance guard

**Inheriting** the committed namer **RanPAC** (+ SLDA, the trained comparators) from P7.1/P7.4 and the pinned bulk from
P7.0. **Question.** A drift-gated stream presents classes in bursts → the head is chronically class-imbalanced. Does a
trained-softmax head develop the documented recency/magnitude bias that a no-gradient head dodges — and what is the
family-matched guard for the head we keep?

**Setup (one variable = the imbalance guard).** Our A6 mechanism normally consolidates on a **balanced** replay
buffer (no imbalance), so imbalance is **induced**: a bounded (`cap=800`) **recency-skewed reservoir** — every class
present, but per-class count ∝ task recency `(t+1)²` (recent tasks over-represented; *not* the degenerate total-absence
of a raw last-cap cut). Guards, family-matched: trained heads → {none, logit-adjust, balanced-softmax, class-balanced
reservoir}; analytic heads → {none, **AIR**, class-balanced reservoir}. Measure per-class accuracy split (old tasks vs
recent tasks) at stream end = the task-recency-bias read. Seeds ×5, median. Wall 47s.

**Result / figures.** *(synthetic CI home, n=5, median; old = tasks 0–1, recent = tasks 3–4)*

| head (family) | guard | old-class acc | recent-class acc | recency-gap | reading |
| --- | --- | --- | --- | --- | --- |
| **RanPAC** (analytic, committed) | none | 0.179 | 0.674 | **+0.495** | biased under strong skew |
| | AIR | 0.506 | 0.412 | −0.094 | **over-corrects** (blunt) |
| | **cbrs** | **0.562** | 0.575 | **+0.013** | **near-eliminates the gap + lifts old** |
| SLDA (analytic) | none | 0.287 | 0.648 | +0.361 | less biased (no trained weights) |
| | AIR | 0.315 | 0.000 | −0.315 | **badly over-corrects** (recent→0) |
| | cbrs | 0.529 | 0.583 | +0.055 | clean fix |
| cosine-softmax (trained) | none | 0.024 | 0.683 | **+0.659** | **worst recency bias (trained-softmax)** |
| | logit-adjust | 0.352 | 0.567 | +0.214 | helps |
| | balanced-softmax | 0.000 | 0.586 | +0.587 | barely helps |
| | cbrs | 0.392 | 0.587 | +0.195 | helps most among trained-head options |
| MLP (trained) | none | 0.175 | 0.674 | +0.498 | biased |
| | logit-adjust | 0.347 | 0.601 | +0.254 | helps |
| | cbrs | 0.475 | 0.569 | +0.094 | best |

- **IMBALANCE** (headline): with no guard, every head over-predicts recent classes; the **trained cosine-softmax is
  worst (+0.659)**, the no-gradient analytic heads less so (RanPAC +0.495, SLDA +0.361). **cbrs** (buffer-side) is the
  reliable fix across all families (RanPAC → +0.013); **AIR** (analytic head-side) reduces the gap only by
  over-correcting. - **INV**: feat-pinned ✓.

**Read (8 slots).**
1. **Claim** — under a bursty recency-skewed buffer every head develops a recency gap; the **trained-softmax head is
   worst** (+0.659) and the no-gradient committed RanPAC less so (+0.495), but it still needs a guard. **The reliable
   guard is class-balanced reservoir sampling (cbrs, buffer-side)** — it drops RanPAC's gap to +0.013 while lifting
   old-class accuracy; **AIR (the analytic head-side guard) over-corrects** and is not shipped.
2. **Headline** — RanPAC recency-gap **+0.495 (no guard) → +0.013 (cbrs)** with old-class acc 0.179→0.562; cosine-softmax
   +0.659 (worst, no guard); AIR over-corrects RanPAC to −0.094 and SLDA to −0.315 (recent→0) (n=5, synthetic CI home).
3. **Figures** — IMBALANCE (old vs recent, guard on/off, per head), INV. Regen from `arrays.npz`.
4. **Mechanism** — the trained cosine-softmax's +0.659 gap is the classic magnitude/recency bias (BiC/WA/SCR): its
   trained weights inflate toward the over-represented recent classes. The no-gradient RanPAC is less biased (its ridge
   prototype still weights by frequency, hence +0.495, but there are no trained softmax weights compounding it). **cbrs
   fixes the root cause** — it re-balances the *buffer* so the analytic fit sees equal classes → an unbiased solution
   by construction, family-agnostic. **AIR mis-fires** because it inverse-frequency-reweights the fitted head's columns
   post-hoc; on a strongly-skewed fit that inversion over-shoots (SLDA's recent classes collapse to 0). Re-balancing the
   input (cbrs) is safer than re-weighting the output (AIR).
5. **Threats** — (a) the buffer-skew being a synthetic artifact → it models the real drift-gated bursty regime; the
   *balanced*-buffer A6 case (P7.4) shows no such gap, so this is the bounded-buffer stress, correctly isolated; (b) AIR
   under-tuned → AIR has no free knob (a closed-form inverse-frequency rule); its over-correction is intrinsic, not a
   tuning miss; (c) cbrs flattering by discarding data → cbrs keeps `cap/C` per class within the same `cap` budget, a
   fair buffer-management choice, not extra data.
6. **Decision** — the imbalance guard shipped with the committed RanPAC is **class-balanced reservoir sampling (cbrs)**
   on the replay buffer (buffer-side, family-agnostic). **AIR is available but not shipped** (over-corrects). This
   **overturns the design's expectation** that AIR is the no-gradient family's guard — the sims show a buffer-side
   balance is the reliable fix. Carried to P7.6 assembled-head confirmation + the Phase-9 maintenance brief.
7. **Spine-honesty** — the recency bias is a **magnitude** phenomenon (over-large logits/prototypes for recent classes);
   it is measured directly (old-vs-recent split under the *actual* skewed buffer, not a synthetic norm-inflation). The
   committed no-gradient head is *less* magnitude-biased than the trained one but not immune — named honestly, and the
   fix is a buffer balance, not a magnitude trick. Cost not a factor here.
8. **Namer-verdict / continual-safety** — RanPAC + **cbrs** is the committed head + guard. This is consistent with the
   P7.4 gate (the trained-softmax dented A6; here it also carries the worst recency bias) and the P7.1
   magnitude-wins-spine-bends verdict (the no-gradient winner is recency-robust-*ish*, and cbrs closes the residual).

**Pre-submit checklist.**
- [x] Median for every headline number (n=5).
- [x] The **family-matched** guard tested per head (trained: logit-adj/bal-softmax/cbrs; analytic: AIR/cbrs).
- [x] Whether the no-gradient head needed a guard recorded (yes under strong skew; cbrs fixes it; AIR over-corrects).
- [x] Feature source loaded from the pinned P7.0 config; feat-pinned INV green.
- [x] Every figure by a `plot_p7.fig_*` function; regen from `arrays.npz`.
- [x] All 8 slots; formal voice; opens by naming the inherited knob (committed RanPAC).
- [x] `manifest.json` + `arrays.npz` written.
- [x] Single-threaded; no sklearn for compute.
- [x] `RESULTS.md` row added; the over-correcting AIR logged with its mechanistic reason.
