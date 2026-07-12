# Larimar: Large Language Models with Episodic Memory Control

- **Authors / Year / Venue:** Payel Das, Subhajit Chaudhury, Elliot Nelson, Igor Melnyk, Sarath Swaminathan, Sihui Dai, Aurélie Lozano, Georgios Kollias, Vijil Chenthamarakshan, et al. (IBM Research) / 2024 / ICML 2024 (arXiv 2403.11901)
- **Link:** https://arxiv.org/abs/2403.11901 — fetched
- **Tier / Topic:** tier3 / t3.1 hippocampus organ
- **Relevance:** ⭐⭐⭐⭐ — The **one-shot, closed-form, editable** episodic memory: write a fact in a single pass, edit it, and *selectively forget* it — the write/forget primitives our passive LUT is missing, done without gradient re-training.
- **Already in `north-star/1-memory.md`:** Kanerva/associative-memory ideas are implicit; Larimar is the modern editable-episodic instantiation the dossier lacks.

## TL;DR
Larimar bolts a **Kanerva-style linear associative memory** onto a frozen LLM: an encoder turns an episode into an address/key, the memory `M` is written by a **one-shot least-squares update** (no gradient descent), and reading conditions the decoder. Because the write is closed-form, you can add, overwrite, or *erase* a specific memory in one shot — fact-editing at 8–10× the speed of gradient-based editors, with selective forgetting and leakage control for free.

## The mechanism (how it actually works)
The memory is a matrix `M` (a fixed number of memory rows) implementing an associative store in the Kanerva "distributed memory" tradition. To **write** a set of episodes: encode them to key vectors `K` and value/latent vectors `Z`, and solve for the memory that best maps addresses to contents — a **linear least-squares** update `M = solve(K, Z)`, computed in one pass (a pseudo-inverse / ridge solve), not by backprop through the LLM. To **read**: encode the query to an address, retrieve the associated latent from `M`, and feed it to the decoder as conditioning. **Editing** a fact = re-solving the one row's contribution; **forgetting** = subtracting an episode's outer-product term from `M` (the write is algebraic, so it's reversible). The base LLM's weights never move — all knowledge lives in the fast, rewritable memory matrix.

## Key results / claims
- One-shot knowledge editing accuracy comparable to the strongest gradient-based editors, with **8–10× speed-ups**, and robustness in **sequential** editing where retrain-based editors degrade.
- Built-in **selective forgetting** and information-leakage prevention (delete an episode's term → it's gone), plus input-context-length generalization — all from the algebraic memory, no fine-tuning.
- LLM-agnostic: the memory is a general module you attach, not a bespoke architecture.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** hippocampus-LUT (write + forget primitives) · sleep/consolidation (the re-solve is our sleep re-fit) · closed-form namer (same algebra family).
- **Same as us:** the memory write is a **closed-form least-squares / outer-product** update — *the same math as our RanPAC/SLDA namer and our sleep re-fit.* Larimar is proof that a **gradient-free, one-shot, editable** associative memory works, attached to a frozen body — which is exactly our frozen-SCFF + closed-form-namer + LUT posture. It also gives us the **forgetting** operation our store lacks: subtract the outer-product term.
- **Different from us:** Larimar's memory holds *episodes for a decoder to condition on* (generation), where our LUT holds *prototypes/negatives for classification and replay*. And its addresses come from a trained encoder; ours come from the frozen SCFF bulk (cheaper, but we don't control the key geometry).
- **What we could borrow or test:** adopt Larimar's **write = one-shot ridge solve** and **forget = outer-product subtraction** directly as the LUT's learning operations — they are already in our algebraic wheelhouse and need no new organ. This turns the passive store into a *writable, editable, forgettable* memory while keeping everything closed-form. Concretely: on novelty, write the episode into `M` by the Kanerva solve instead of just snapshotting; on eviction (our CBRS), *subtract* the term instead of dropping a slot. Test selective-forgetting against our P9 eviction and the P10 REV-staircase stale-namer sag (a targeted forget may beat a blunt cap).
- **What contradicts or challenges us:** the Kanerva memory has a fixed capacity and the least-squares solve conditioning degrades as it fills (the same ill-conditioning LoRanPAC flags for our namer) — so it doesn't remove the need for consolidation/eviction, and on an analog crossbar the pseudo-inverse is the hard part (our sleep does it offline, which is the natural home).

## Follow-on leads
- Kanerva 1988 "Sparse Distributed Memory" — the root of the address-based associative store.
- Pham et al. 2021 "Generative Pseudo-Inverse Memory" — the closed-form memory-write lineage.
- Model-editing benchmarks (ZsRE, CounterFact) — the eval suite for a write/edit/forget memory, if we ever test targeted forgetting.
