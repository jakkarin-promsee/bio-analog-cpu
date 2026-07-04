# `ref-report/` — the glossary the phase reports link to

> **What this is.** A thin, report-altitude reference so the phase reports stay lean: every method,
> metric, and paper the reports cite gets a short entry here, and the reports link to it
> (`[term](../ref-report/<file>.md#anchor)`). Each entry points **onward** to the deep file
> (`research/papers/`, `research/survey/`) for the full story, and **back** to the phase reports where it's used.
>
> **What this is NOT.** Not a re-telling of the paper stories (those live in [`../../research/papers/`](../../research/papers/README.md))
> and not the algorithm detail (that's [`../../research/survey/`](../../research/survey/README.md)). If an entry grows past ~3 sentences, it belongs in one of those
> and this entry should just link to it. Keep it DRY.

---

## The three files

| File | Holds | Reports lean on it for |
| --- | --- | --- |
| [`methods.md`](methods.md) | the mechanisms — SCFF, mono-forward, contrast, sleep, the namer (RanPAC / SLDA), the gate, … (grouped in **5 bands**: cheap brain / objective family / chain+maintenance / racers / **the closed object** = the Stage-1 close-out + Stage 2) | "what *is* this part" without re-explaining it each phase |
| [`metrics.md`](metrics.md) | the measurement dictionary — AAA, gap, selectivity, BWT, worst-pre-sleep BWT, GD-share, argmax-flip, … | one **pinned** definition per metric (consolidated here from the `result-format.md` files) |
| [`papers.md`](papers.md) | the citation table — paper, people, arXiv, one-line why, link to the `research/papers/` story | naming the source without a paragraph |

## Convention for every entry

```
### <term>   (the header doubles as a one-line gloss, so the set is reviewable at a glance)
<short definition — 1–3 sentences; if it grows past that, move it to research/papers/ or research/survey/ and just link>
- **Onward:** <link to the deep story in research/papers/ or research/survey/, and papers.md for a paper>
- **Used in:** <which phase reports lean on it>
```

## Growth note

This scaffold now covers **Phases 1–10** — the Stage-1 cheap-brain vocabulary (methods Bands 1–4; the metrics
through Phase 4) **plus** the depth close-out and Stage-2 terms (methods **Band 5 — the closed object**; metrics
**Depth close-out & Stage 2**: composing-depth, the w12 ceiling, the truncation floor, forward-MACs, argmax-flip,
worst-pre-sleep BWT, GD-share, MTD/FAR, destruction). When a later write introduces a term not listed here, **add the
entry, don't inline the definition** — that's the whole point of this folder.
