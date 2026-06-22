# Experiment P4.3 — width × depth (A4): the Scap-budget Pareto

> **Status: ✅ DONE (2026-06-22).** At a **fixed total weight budget** (the substrate's real constraint — Scaps are
> finite), how should it be spent: wide-shallow or narrow-deep? And does the answer flip by task regime? Iso-budget
> shape sweep (B = the canonical L4/W64 cell ≈ 23.5k weights), depth `[2,3,4,6,8]`, width chosen per depth to hold B.
> Two regimes: **flat** (`make_gauss`, no headroom — Phase-1/2 regime) and **headroom** (`make_tierb`, the P4.2
> config — depth pays). Racers: OURS vs tuned BP (task accuracy + the measured backward-cost Pareto). 5 seeds. Run:
> `OMP_NUM_THREADS=1 PYTHONIOENCODING=utf-8 python -u run_p4_3.py` (2027s). Contract: [`../result-format.md`](../result-format.md).

---

## The 6+2 slot read

**1 · Claim.** **A4 resolves the Scap-collision decisively in OURS's favour — via cost.** At iso-weight budget,
**OURS's backward cost is flat in depth (~41–47k); BP's grows linearly (52k → 124k)** — so **narrow-deep, the
substrate-friendly direction, is nearly *free* for OURS and 2.6× costlier for BP** (the w=2 window bounds credit
distance; BP's full-depth backprop scales with L). And accuracy splits by regime: on **flat**, depth doesn't pay
(OURS gently declines, BP flat — OURS trails on accuracy but is cheaper); on **headroom**, **OURS *climbs* with
depth (0.51 → 0.56 at L6) and overtakes BP from L3 on** (gap IQR-negative at the deep shapes), while BP stays flat.
**Depth is OURS's to spend — cheaply, and accretively where there's headroom; BP can't exploit it.**

**2 · Number + IQR** (median [IQR], n=5):

*flat regime:*
| shape | OURS | BP | gap-to-BP | cost OURS/BP |
| --- | --- | --- | --- | --- |
| L2/W109 | 0.791 | 0.837 | +0.039 | 47k / 52k |
| L3/W79 | 0.799 | 0.830 | +0.033 | 41k / 65k |
| L4/W64 | 0.795 | 0.831 | +0.037 | 47k / 77k |
| L6/W48 | 0.787 | 0.830 | +0.042 | 46k / 99k |
| L8/W40 | 0.782 | 0.841 | +0.059 | 47k / 124k |

*headroom regime:*
| shape | OURS | BP | gap-to-BP | cost OURS/BP |
| --- | --- | --- | --- | --- |
| L2/W109 | 0.511 | 0.528 | +0.012 | 47k / 52k |
| L3/W79 | 0.538 | 0.519 | **−0.014** [−0.021,−0.011] | 41k / 65k |
| L4/W64 | 0.540 | 0.533 | +0.002 | 47k / 77k |
| L6/W48 | **0.560** | 0.536 | **−0.027** [−0.027,−0.012] | 46k / 99k |
| L8/W40 | 0.551 | 0.523 | **−0.028** [−0.032,−0.024] | 47k / 124k |

OURS best shape: **flat L3** (cost-driven), **headroom L6** (0.560, beats BP's best 0.536). **OURS cost flat across
depth; BP cost 2.4× over the sweep.**

**3 · Figures.** `WIDTHxDEPTH` (flat: OURS gently declines, BP flat-above; headroom: OURS *rises* and crosses above
BP from L3, best at L6) · `PARETO` (**the headline** — OURS a tight cheap vertical cluster at ~45k climbing in
accuracy; BP a horizontal fan ballooning 52k→124k for ~no gain) · `INV` (width shrinks as depth grows = iso-budget
✓; gap-to-BP vs shape, per regime).

**4 · Mechanism.** OURS's backward credit-assignment work is **bounded by the coordination window (w=2), not by
depth** — so adding layers costs ~nothing backward. BP's credit distance **= full depth**, so its backward work
grows linearly with L. Meanwhile depth only buys *accuracy* where the task has **headroom** (P4.2): on flat,
deeper layers have nothing to compose (OURS drifts down — the w=2 inverted-U; BP flat); on headroom, OURS composes
(rises to L6) while BP — needing task-gradient-headroom it doesn't have at this budget — stays flat. So the
substrate's native direction (narrow-deep, Scap-cheap) is exactly where OURS is **both cheaper and (on headroom)
more accurate**, and exactly where BP is **both costlier and no better**.

**5 · Threats.** (a) On **flat**, OURS *loses accuracy* to BP at every shape (+0.03–0.06) — this rung's win is
**cost everywhere + accuracy on headroom-at-depth**, not "OURS beats BP." (b) OURS's cost-flatness is **structural**
(the w=2 window bounds credit distance by construction) — the design working as intended, not an emergent surprise.
(c) Headroom absolute accuracy is ~0.5 (near chance for this hard task) — the **shape-dependence** is the result,
not the magnitude. (d) Single budget (~23.5k) and dim (40); shape *accuracies* could shift elsewhere, but the
**cost-scaling argument is general** (BP credit-distance ∝ L always).

**6 · Decision.** **A4 = depth is OURS's lever — cheap and substrate-native.** **Carry forward:** (i) for
depth-needing tasks, **spend Scaps on depth** — it composes (P4.2) at ~flat backward cost (P4.3); (ii) the **80/20
cost advantage is depth-gated** — negligible shallow (P4.0's L4 null), large deep (2.6× at L8) — so it materializes
exactly in the substrate's operating regime; (iii) on **flat** tasks depth is a cost-neutral non-win → don't
over-invest depth without headroom (couples to an adaptive-depth/window knob, with P4.2's w-vs-headroom rule).

**7 · Cost-honesty.** This is the rung where the **80/20 cost advantage becomes clearly visible — as a function of
depth.** OURS backward work is **flat in depth** (~45k; window-2 bounded credit), BP's is **linear** (52k→124k);
2.6× at L8. This **refines P4.0's "not visible per-pass"** — that was at shallow L4 where costs match; the advantage
*grows with depth*. Still **analytic / substrate units, not energy** — and OURS's flatness is by-construction (w=2).

**8 · Map-contribution → P5.** A4 tile: **depth is cheap + accretive for OURS (the substrate's native direction);
BP can't exploit it.** Tells Phase 5: (a) **build deep** (SCFF depth / block-stack) — nearly free backward and it
composes; (b) the **80/20 claim is depth-gated** → P5's cost meter must report **cost-vs-depth**, not a single
number (a single shallow number understates it, a single deep number overstates per-pass); (c) **gate depth on
headroom** — deep where it composes, shallow where it doesn't (the adaptive knob, with P4.2's window rule).

---

## Reproducibility

`figs_p4_3/{manifest.json, arrays.npz, _ckpt.jsonl}`; `python plot_p4_3.py figs_p4_3`. Single-threaded, `python -u`,
`PYTHONIOENCODING=utf-8`, per-cell fsync; verified alive mid-run. Pure numpy (no sklearn — task-accuracy rung, lower
phantom risk). Iso-budget via `ours_width_for_budget` (bulk + all-tap readout = B); BP matched to OURS's actual
total at each shape (`race_bp` with `depths=(L,)`, tuned over lr×wd). New: `exp3/run_p4_3.py` + `plot_p4_3.py`.
