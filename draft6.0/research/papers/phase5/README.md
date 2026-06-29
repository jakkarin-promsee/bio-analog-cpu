# `phase5/` — the depth-readout reframe (Phase 5 papers)

The literature pass behind the Phase-5 question: *the cheap brain composes class structure for ~5 layers, then the
representation drifts off the class manifold — how do we make a forward-only, unsupervised stack keep useful depth,
and read it cheaply?* Phase 3 settled the *objective* (contrast composes where energy can't); Phase 5 attacks what
contrast **still** leaves — the decay past the coordination window's reach, and the **placement** problem (the
useful layer is at a task-dependent depth, and all-tap reads everything, burning the 80/20).

> **Provenance.** These four files are the literature dossier from the **2026-06-28/29 depth-readout research
> session** (the rough-idea pass that scoped Phase 5). They keep their literature value verbatim. The *decisions*
> derived from this reading — what's adopted, demoted, cut — are **not** here; they live in the Phase-5 design
> ([`../../../src/phase5/design.md`](../../../src/phase5/design.md)), which is authoritative on any conflict. Each
> file is a **story, not a spec**, with a **"For us"** read and three flags on every mechanism: **cost-on-chip**,
> **SCFF-flow-safe?** (does it rewrite the stream — forbidden), and published depth-recovery evidence.

---

## §1 · The shape the decay takes — the extractor / tunnel analogy

The single organizing find: a deep net splits into an **extractor** (early layers — build the linearly-separable
representation; length set by *task complexity*) and a **tunnel** (later layers — compress/drift, add ~nothing).
The **Tunnel Effect** ([2305.19753](https://arxiv.org/abs/2305.19753), NeurIPS 2023) names it from the supervised
side; it is the author's *"easy task → read early, hard task → read late"* in the literature's own variables. Two
caveats keep it honest (it is a **loose analogy for the shape**, not a load-bearing theory — see the design's
decision record): it's **capacity-relative** and measured on **supervised** nets, and a *supervised* tunnel
**preserves** in-distribution accuracy whereas **SCFF's tunnel is worse — it actively overwrites** the extractor's
work (the mixed-task corruption, P4.3). The part that bites hardest: **a long tunnel raises catastrophic forgetting**
— so the readout/depth work is a *defense of the continual win*, not a side-quest.

## §2 · The two tracks — two ends of one axis

```
   input → [ EXTRACTOR (builds, ~L1..Lk) ] → [ TUNNEL (drifts/overwrites, Lk..Ln) ] → out
                         ▲                                   ▲
            read HERE (the sweet spot)            all-tap reads everything (burns the 80/20)
       ┌─────────────────┴───────────────┐
   TRACK A: make the tunnel harmless     TRACK B: find the extractor's end, read it cheaply
   (preserve early features forward)     (deep-supervision heads + a calibrated confidence exit)
                  TRACK C: the cheap global direction (only if locality forces it)
```

If preservation (A) carries the extractor to the top, "read the top" *is* "read the extractor" and placement
dissolves. If it only partly preserves, adaptive readout (B) finds the (now-deeper) end cheaply. **C** — a bounded,
flow-safe global signal — enters only if the depth ceiling proves *locality*-bound and A/B underdeliver.

> **The spine (every file obeys it):** preserve/read the class **DIRECTION** (the manifold), never a **magnitude**
> (rank, variance, contrast-loudness, goodness/energy are symptoms). **The hard rule:** read / gate / add-to-the-
> objective is allowed; **rewriting the SCFF stream is forbidden** (P2.5 `write` kills SCFF) — which is why FTP and
> PEPITA are out *even though they work*.

---

## The files

| File | What it covers |
| ---- | -------------- |
| [lit-cheap-credit.md](lit-cheap-credit.md) | **Read first for "earn the depth."** The deep survey of the cheapest *global-credit* mechanism that recovers composing depth without a deep backprop chain or a stream rewrite — the 3 flow-safe shapes, the ranked shortlist (objective-side first), FTP/PEPITA ruled out, all arXiv IDs verified. Supersedes track-c's survey-level treatment. |
| [track-a-preservation.md](track-a-preservation.md) | **Preservation** — the near-identity residual (ReZero/Fixup/LayerScale), dense reuse, and the honest "residuals are not a free win" warning. *(Post-review: α defaults **frozen**; preserve **class direction**; whitening rejected-as-lever.)* |
| [track-b-adaptive-readout.md](track-b-adaptive-readout.md) | **Adaptive readout** — deep-supervision heads (Mono-Forward-style), early-exit + confidence (BranchyNet/SDN/CALM), halting, MoE/SSM, the per-task profiler. *(Post-review: learned halting **CUT** → calibrated threshold; placement = head-confidence, not goodness.)* |
| [track-c-cheap-direction.md](track-c-cheap-direction.md) | **Cheap global direction** — DFA/EBD, top-down broadcast, Forward Target Propagation (✗ rewrites the stream), three-factor/dopamine. The "eventually backward, forward-cheap" menu, third lever. |

### Master paper list (Phase-5 additions, beyond the Phase 1–3 set)

| paper | id | track | flow-safe? | depth-evidence | note |
| --- | --- | --- | --- | --- | --- |
| Tunnel Effect | [2305.19753](https://arxiv.org/abs/2305.19753) | shape | — | — | the extractor/tunnel analogy (demoted to analogy) |
| ReZero | [2003.04887](https://arxiv.org/abs/2003.04887) | A | ✅ | ✅ 1000s of layers | `y=x+α·f(x)`, α init 0 = the author's Sol-2, named |
| Fixup | [1901.09321](https://arxiv.org/abs/1901.09321) | A | ✅ | ✅ 10k layers, no norm | init-based; **frozen-α default** (no batch stats) |
| LayerScale / Hyper-Connections | (CaiT 2021) · [2409.19606](https://arxiv.org/abs/2409.19606) | A | ✅ | ✅ | per-channel / learnable preserve↔transform upgrade |
| Residuals harm SSL repr. | [2404.10947](https://arxiv.org/abs/2404.10947) | A | — | ⚠ caution | the bypass-cheat warning → the α→0 ablation guard |
| DenseNet / MSDNet | (Huang 2017/2018) | A/B | ✅ | ✅ | preserve-by-concat; MSDNet = preserve **+** early-exit |
| Deeply-Supervised Nets | (Lee 2015) · [1505.02496](https://arxiv.org/abs/1505.02496) | B | ✅ | ✅ | a readout head at every depth (the base) |
| Mono-Forward | [2501.09238](https://arxiv.org/abs/2501.09238) *(repo)* | B | ✅ | ✅ | the **forward-only** deep-supervision head we deploy |
| BranchyNet / SDN | [1709.01686](https://arxiv.org/abs/1709.01686) · (Kaya 2019) | B | ✅ | ✅ | confidence early-exit; "over-thinking" = thinking-harder≠better |
| CALM | (Schuster 2022) | B | ✅ | ✅ | **calibrated** exit with a guarantee (the gate we use) |
| ACT / PonderNet / AdaPonderLM | (Graves 2016) · [2107.05407](https://arxiv.org/abs/2107.05407) · [2603.01914](https://arxiv.org/abs/2603.01914) | B | ✅ | ✅ | learned halting — **CUT from Stage 1**, held as the north-star "I-get-it" seed |
| Intermediate-Layers-Matter SSL | (NeurIPS 2021) | B | ✅ | ✅ | best layer ≠ last in contrastive SSL → the profiler |
| Can Local Learning Match SSL-BP? | [2601.21683](https://arxiv.org/abs/2601.21683) | C | ✅ | ✅ parity | reaches BP-SSL parity by fixing the **local update geometry** — not a wire |
| InfoPro / DGL / ContSup | [2101.10832](https://arxiv.org/abs/2101.10832) · [1901.08164](https://arxiv.org/abs/1901.08164) · [2312.07636](https://arxiv.org/abs/2312.07636) | C | ✅✅ | ✅ | "greedy local discards downstream-useful info" = our drift, published; fix = add a preserve term (class direction, **not** reconstruction) |
| DFA / EBD | (Nøkland 2016) · [2504.11558](https://arxiv.org/abs/2504.11558) | C | ✅ (update form) | ⚠ degrades on deep/conv | the cheapest global *wire*; needs a contrastive error; gated behind A/B |
| Layer Collaboration | [2305.12393](https://arxiv.org/abs/2305.12393) | C | ✅ | ~ | scalar broadcast (goodness = magnitude → prefer a direction reference) |
| Forward Target Propagation | [2506.11030](https://arxiv.org/abs/2506.11030) | C | ❌ | ✅ | **OUT** — drives activations to targets = stream rewrite |
| PEPITA + top-down | [2302.05440](https://arxiv.org/abs/2302.05440) | C | ❌ | ⚠ caps ~5 | **OUT** — input-modulation = activation rewrite; caps at our exact ceiling (negative control) |
| e-prop / three-factor | (Bellec 2020; Frémaux & Gerstner) | C | ✅ | — | eligibility trace × broadcast = the half-local/half-global/dopamine intuition |

> Cross-references: the adopted Phase 1–3 design papers are in [`../phase1-2/`](../phase1-2/README.md) and
> [`../phase3/`](../phase3/README.md); the Phase-5 plan these feed is
> [`../../../src/phase5/design.md`](../../../src/phase5/design.md); the learning-rule survey is
> [`../../survey/summary.detail.md`](../../survey/summary.detail.md).
