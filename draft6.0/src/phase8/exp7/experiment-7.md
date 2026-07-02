# P8.7 — The substrate ablation: WHY ANALOG? (OURS-analog vs OURS-digital vs GD-digital)

> **EXTENSION (added 2026-07-02, post-run — author Q-call for the professor brief).** P8.4/P8.5 metered OURS and BP+replay
> on the *same analog table*, so their `bp_ratio` isolates the **algorithm** win. This rung adds the missing axis the
> "why build the analog chip" question needs: the same committed loop and the same fair baseline, re-metered on a **digital
> substrate** — the full 2×2, decomposing the total win into **substrate × algorithm**.

**Question.** Inheriting the committed economy (SLDA + DDM + cbrs + grid-8/full/λ1.0, P8.6's exact live loop) and the fair
BP+replay baseline (P8.5): how much of the energy win is the **analog substrate** (compute-in-memory vs von-Neumann) and
how much is the **80/20 algorithm** (our gated forward-only loop vs real backprop+replay)? Is the analog advantage a
robust *floor* or a knife-edge on one digital-MAC-energy assumption? Does the 80/20 survive the substrate swap?

**Setup.** Swept variable = model × substrate ∈ {OURS, GD+replay} × {analog, digital}. Controls locked (the committed live
economy, CI+nuisance stream, seeds [42,137,271,314,1729]). **Analog** = the §2.3 meter (crossbar MAC `e_MAC` 0.01 pJ +
ADC-dominant `e_ADC(8b)` 1.6 pJ + `e_write` 10 + `e_digital` 5e-4). **Digital** = §2.5, the conventional von-Neumann /
GPU-class baseline on the *same op-counts*: **no ADC** (`e_ADC=0` — the analog tax vanishes, granted fully to digital), a
real digital MAC `E_MAC_DIG=0.2 pJ` (**Horowitz ISSCC'14** 45 nm 8-bit MAC, arithmetic-only — the *most generous* to
digital), SRAM write `E_WRITE_DIG=0.5`, same `e_digital`; **matched 8-bit precision** (the axis under test is the
substrate, not the format). GD+replay = the same P8.5 iso-weight-budget MLP [40,130,130,130,10] at matched retention.
Figures: SUBSTRATE (the 2×2 + the `E_MAC_DIG` memory-wall sweep), INV. Guards re-checked (meter-proxy = the analog path is
unchanged by the digital switch; partial-fit-equiv) — bit-exact.

**Run.** 4 (model×substrate) cells + a 5-point `E_MAC_DIG` sweep × 5 seeds; energy tallied from the committed loop's
fire/sleep trace + the BP+replay energy model on each substrate table. Wall ≈ 1.5 min.

**Result / figures.** *(energy is deterministic given the fixed schedule → zero IQR)*
| model × substrate | E_total (pJ) | vs OURS-analog | verdict |
| --- | --- | --- | --- |
| **OURS · analog** (the chip) | **3.40e7** | (ref) | the proposed substrate |
| OURS · digital | 1.83e8 | 5.37× | our algorithm without CIM |
| GD+replay · analog | 5.37e7 | 1.58× | algorithm-only ablation |
| GD+replay · digital (status quo) | 5.23e8 | 15.37× | conventional GD on a digital accelerator |

- **Win decomposition:** **substrate** (OURS digital/analog) = **5.37×** · **algorithm** (digital GD/OURS) = **2.86×** ·
  **TOTAL** (GD-digital / OURS-analog) = **15.37×**. Identity check: 5.37 × 2.86 = 15.4 ✓ (substrate × algorithm = total).
- **80/20 holds on both substrates:** GD-share analog **0.155** / digital **0.109** — the gate's split is
  substrate-independent (it is a property of the op-schedule, not the physics).
- **`E_MAC_DIG` memory-wall sweep** (substrate win): 0.1→**2.74×** · 0.2→5.37× (Horowitz) · 0.5→13.3× · 1.0→26.5× ·
  2.0→52.9× — analog wins even at the most-generous arithmetic-only digital, so the advantage is a **floor**.
- Cross-check: OURS/GD on analog = **0.63** (P8.5 reported 0.50 — P8.5 used the simpler checkpoint sleep cadence; the
  committed grid-8 sleeps more, so OURS costs a little more, still cheaper than BP+replay). Same direction, reconciled.
- **SUBSTRATE** (headline): the OURS-analog bar (ringed teal, "the chip") is a **sliver** of the GD-digital status-quo bar
  (magenta); the sweep panel shows the two digital costs rising with the memory wall while OURS-analog is a flat reference.
  - **INV**: meter-proxy guard green (analog MAC+solve ≡ `readout_cost` — the digital switch left the default untouched);
    partial-fit-equiv green.

**Read (8 slots).**
1. *Claim* — the chip's energy advantage over the conventional approach (real BP+replay on a digital accelerator) is
   ~15×, and it decomposes cleanly: ~5× is the **analog substrate** (compute-in-memory) and ~3× is the **80/20 algorithm**;
   the substrate advantage is a floor that only grows with the memory wall.
2. *Headline* — TOTAL win 15.37× (GD-digital / OURS-analog) = substrate 5.37× × algorithm 2.86×; substrate win ≥ 2.74×
   across the whole `E_MAC_DIG` sweep (n=5, live CI+nuisance; behavioral meter, params + citations logged).
3. *Figures* — SUBSTRATE (the 2×2 bars + the memory-wall sweep), INV (meter-proxy + partial-fit green).
4. *Mechanism* — the analog win is the **compute-in-memory** thesis, measured: the SCFF forward is ~8×10⁸ MACs, and in the
   crossbar those MACs are near-free (`e_MAC` 0.01 pJ, weights resident) so the **ADC readout dominates** (the analog tax).
   On a digital substrate there is no ADC, but every one of those MACs now costs real energy (`E_MAC_DIG` ≥ 0.2 pJ,
   operands fetched — the memory wall) — and there are ~75× more MACs than ADC conversions, so dropping the ADC saves far
   less than the MACs now cost → digital is 5.37× the analog. The algorithm win is orthogonal: OURS never runs a backward
   pass and fires the namer on ~12–16% of steps (the gate), while BP+replay pays a 3× forward + a replay pass *every* step
   — 2.86× on the same digital substrate. They multiply.
5. *Threats* — (a) the digital model is **behavioral**, and its central `E_MAC_DIG=0.2` is *arithmetic-only* (Horowitz),
   which is the most generous assumption to digital — a real accelerator pays the memory wall (SRAM/DRAM fetch), so the
   sweep shows the true advantage is *larger*; the reported 5.37× is a conservative floor (2.74× even below Horowitz). (b)
   Matched 8-bit precision + matched weight budget + matched retention — the axis under test is the substrate/algorithm,
   not the number format or model size. (c) The analog path is bit-exact unchanged by the digital switch (meter-proxy guard
   green) — the digital branch is additive, not a re-tuning of the analog verdict. (d) Relative-pJ only; no absolute Joule.
6. *Decision* — **completes the cost-meter deliverable**: the "why analog" number for the professor brief. It sets no new
   committed knob (the committed economy is P8.6's); it *decomposes* the already-committed loop's cost onto the substrate
   axis. Records the substrate/algorithm/total split alongside the metered 80/20 (S12).
7. *Economy-honesty* — the meter model + params + citations (analog **and** digital, `METER_CITE` / `METER_CITE_DIG`) are
   in the manifest; the digital MAC energy is anchored (Horowitz) and swept (memory wall); the analog advantage is reported
   as a floor with its sensitivity range, not a single hero number; the identity check (substrate × algorithm = total) is
   the internal-consistency guard.
8. *Live-safety / namer* — no change to the committed head/gate/cadence or to the live A6 safety (P8.6 stands); this rung is
   a cost decomposition of that exact loop. The deployed head remains **SLDA** — the 15× total win is realized *by the
   cheap no-gradient namer* on the analog substrate.
