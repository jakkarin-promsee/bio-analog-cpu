# Green AI
- **Authors / Year / Venue:** Roy Schwartz, Jesse Dodge, Noah A. Smith, Oren Etzioni / 2019 (arXiv) → Communications of the ACM 63(12), 2020
- **Link:** https://arxiv.org/abs/1907.10597 (fetched)
- **Tier / Topic:** tier4-adjacent-wildcards / t4.5 energy-benchmarking-protocol
- **Relevance:** ⭐⭐⭐⭐ — the manifesto that made *efficiency a first-class reported metric*; the norm our whole "why analog" pitch is built to satisfy, and the source of "report FLOPs / a price tag" as baseline hygiene.

## TL;DR
Coins **Red AI** (buy accuracy with ever-more compute — ~300,000× compute growth 2012→2018) vs **Green AI** (treat efficiency as an evaluation criterion *alongside* accuracy). Recommends every paper report the computational/financial cost of getting its result, so efficiency can be compared rather than assumed.

## The mechanism (how it actually works)
Not an algorithm — a reporting norm and a diagnosis. The field rewards a single number (accuracy/SOTA), and compute is an unpriced input, so the equilibrium is a compute arms race. Green AI proposes to internalise that cost: make efficiency a reported outcome. It surveys candidate cost measures — carbon, electricity, elapsed time, parameters, and **FLOPs** — and argues FLOPs is the most hardware-agnostic *first-order* proxy for the work an algorithm does (reproducible, independent of the accelerator), while acknowledging it omits memory and data-movement cost. The deeper recommendation is to report cost *and* accuracy together so readers can locate a method on an accuracy-vs-cost trade-off, i.e. read efficiency at a chosen accuracy.

## Key results / claims
- Documents the compute explosion and its exclusionary effect (only well-funded labs can play).
- Recommends: report FLOPs (hardware-agnostic) and/or a financial "price tag" as standard practice; make efficiency an explicit research goal, "enabling any inspired undergraduate with a laptop."
- Frames efficiency as a *trade-off with accuracy*, not an absolute — the seed of the iso-accuracy idea.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** the project's founding identity (efficient on-chip learning), the P8.7 cost meter, the whole 80/20 pitch.
- **Same as us:** we are the Green-AI thesis taken to the substrate — the entire draft exists to make learning cheaper at a given capability, and we *do* report cost as a first-class result (P8/P10/P11), not an afterthought.
- **Different from us:** Green AI's recommended proxy is FLOPs — and P10 R1 says on FLOPs/sample the algorithm alone *loses* to a small tuned ER. FLOPs is exactly the proxy that misses our win, because our win is **data-movement / substrate** (compute-in-memory), which FLOPs cannot see. So the Green-AI norm is necessary but insufficient for us: we must report FLOPs (to satisfy the norm) *and* a pJ/data-movement measure (to show the real win).
- **What we could borrow or test:** adopt the "price tag" framing literally — report a single headline cost number per method at matched accuracy, plus the FLOPs disclosure. This is the minimum a reviewer now expects; we already exceed it, but should cite Green AI as the standard we meet.
- **What contradicts or challenges us:** Green AI's implicit trust in FLOPs is the trap — a naive Green-AI reviewer might rank us *below* ER on FLOPs and stop. We must actively redirect to the substrate/data-movement axis (Horowitz, Gholami, this folder) where the FLOP proxy breaks.

## Follow-on leads
- Strubell 2019 (this folder) operationalises the "price tag" for training.
- Henderson 2020 (this folder) turns the norm into a measurement tool (experiment-impact-tracker).
