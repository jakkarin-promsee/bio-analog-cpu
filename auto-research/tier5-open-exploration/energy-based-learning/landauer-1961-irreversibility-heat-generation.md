# Irreversibility and Heat Generation in the Computing Process
- **Authors / Year / Venue:** Rolf Landauer / 1961 / IBM Journal of Research and Development 5(3): 183–191
- **Link:** https://en.wikipedia.org/wiki/Landauer%27s_principle (fetched; DOI 10.1147/rd.53.0183)
- **Tier / Topic:** tier5-open-exploration / t5.1 (energy-based learning — the thermodynamic floor)
- **Relevance:** ⭐⭐⭐⭐⭐ — the physical floor under our *entire* efficiency thesis. It says the real cost of computing is **erasing and moving bits**, not computing — which is exactly the cost our resident-weight, settle-don't-erase substrate sidesteps.

## TL;DR
**Erasing one bit of information has a fundamental minimum energy cost of `k_B·T·ln 2`** (≈ 2.9×10⁻²¹ J at room temperature). The reason is thermodynamic: erasure is **logically irreversible** — it merges two possible states into one, destroying information — and destroying information must dump at least that much heat to the environment. Operations that *don't* destroy information can, in principle, be made thermodynamically **free**.

## The mechanism (how it actually works)
A bit is a physical system with two distinguishable states — think two wells of a potential separated by a barrier, one microstate carrying "0", the other "1". **Erasing** (RESET-to-0 regardless of the prior value) forces both wells into one. Phase-space volume that was spread over two states is compressed into one — an entropy decrease of `k_B·ln 2` *in the memory*. The second law forbids destroying entropy, so that `k_B·ln 2` must appear as entropy `+` heat `≥ k_B·T·ln 2` **in the surroundings**. The dissipation is tied to the **logical irreversibility** of the operation, not to any particular technology: any map that is not one-to-one (AND, ERASE, OVERWRITE) has this floor; a **one-to-one** (reversible) map does not. Bennett (1973, 2003) completed the argument by showing any computation *can* be rearranged to be logically reversible, so the only unavoidable cost is the erasures you actually perform.

## Key results / claims
- The `k_B·T·ln 2` per-bit-erased limit — the most-cited number in the physics of computation.
- Dissipation follows **irreversibility**, not switching per se: reversible logic has no floor; only information destruction does.
- Today's digital chips burn roughly a **billion times** this limit per operation — almost all of it in moving and erasing bits, not in the logic itself.

## How it relates to us (light — why worth knowing)
- **Organ / phase touched:** the whole "copy the brain's function, cheat the implementation" efficiency thesis; the P8.7 substrate-factor and the north-star `21-energy.md`.
- This grounds our efficiency story **in thermodynamics, not slogan.** Where digital pays Landauer over and over — every register overwrite, every load/store, the von-Neumann shuttle *destroys and moves* bits — our **weights are never erased or moved**: they persist as analog charge, and the multiply happens where the weight lives (compute-in-memory). We sidestep the dominant cost by *not erasing*.
- **Settling is near-reversible.** An analog network relaxing to equilibrium dissipates energy gradually along a continuous landscape; it is not doing irreversible bit-erasure at every step. "Settle-don't-erase" is, precisely, "stay near the reversible side of Landauer's line."
- Keep the sentence: **the cost of computing is erasing — so a machine that descends and persists instead of erasing and moving is on the cheap side of physics.**

## Follow-on leads
Bennett's reversible computing (1973/2003); experimental verification of the Landauer bound (Bérut et al. 2012, single-particle erasure); thermodynamics of computation reviews; the thermodynamic-computing hardware that *uses* fluctuations as a resource (Coles 2023, Aifer 2023, Melanson 2025).
