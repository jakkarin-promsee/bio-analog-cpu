# 12 — The ALU wall: spatial vs temporal compute, and where your crossbar sits

> Your framing: a normal CPU does **one task at a time**; on your analog substrate "one task = one charging time," and charging needs a routed analog path — *expensive* if used like a CPU. Your draft-5 breakthrough was to **wire a whole Ganglion as a static circuit** (29 weights, input cap + output cap, the 3-layer net acts like a fixed wire) so the *whole block* computes in essentially one settle. This file is the names and theory behind that move — what the "ALU wall" actually is, the fundamental tradeoff you're navigating, and how the rest of the world organizes compute to dodge it.

---

## The "ALU wall" has a name: the von Neumann / memory wall

*Backes & Wulf, 1995 (the original "memory wall"); modern surveys on compute-in-memory.*

What you're feeling is the field's oldest hardware problem. A normal computer **separates memory from the ALU**, so every operation must **move data** from memory to the compute unit and back. As compute got fast, the *movement* became the bottleneck — and the energy numbers are brutal: **a DRAM access costs ~200× more energy than the multiply-accumulate it feeds** (200 pJ vs ~0.075 pJ). For a neural net, which is mostly multiply-accumulates over millions of weights, **moving the weights dominates everything** — latency *and* energy. That is the wall.

**For us:** this is the entire justification for your project, stated in the field's own words. **Compute-in-memory** — your capacitors that *are* the weights and *also* do the multiply — is the textbook answer to the memory wall: if the weight never moves (resident-weight), you never pay the 200×. Your "ALU wall" worry is real, but your architecture is *already the recognized solution to it.* The remaining question isn't "how to beat the wall" (CIM does that) — it's "how to organize the in-memory compute," which is the spatial-vs-temporal tradeoff below.

---

## The fundamental tradeoff: spatial vs temporal (and you're choosing spatial)

Every accelerator lives on one axis: **reuse hardware over time, or unroll it into space.**

- **Temporal (like a CPU / one ALU):** one multiply unit, used over and over. *Cheap area, many time-steps.* This is your "one task = one charging time, used like a CPU" — and it's exactly the expensive-in-time case you're avoiding.
- **Spatial (unroll the computation into dedicated hardware):** a multiplier for *every* weight, all firing at once. *Big area, few time-steps (ideally one).* This is your "**wire the whole Ganglion as a static circuit**" — the entire block computes in one settle because every weight has its own physical path.

There is no free lunch: spatial trades **area** for **time**. Your draft-5 insight — "don't time-multiplex one ALU across 29 weights; lay all 29 down as a fixed circuit and let it settle once" — is the **spatial** choice, and it's the *right* one for analog, because in analog the "multiplier" is nearly free (a resistor/capacitor) so spreading out in space is cheap, while time (charge cycles) is your scarce resource.

**For us:** name your draft-5 breakthrough precisely — it's **spatial dataflow / full unrolling of a block.** The cost you pay is **area** (one path per weight), and that is *exactly* why `11-connectivity.md` matters: **block-local connectivity is how you keep the spatial cheapness while controlling the area** — smaller crossbars (`n·m/g` paths instead of `n·m`), mixed cheaply by shuffles.

---

## Analog crossbar MVM — the purest spatial primitive (this is your Ganglion)

*Memristor/cap crossbars for in-memory MVM. ([Review: Ohm's + Kirchhoff's law MVM in one step](https://pmc.ncbi.nlm.nih.gov/articles/PMC9756267/)).*

The physics that makes your static-wire idea work, formalized. Arrange weights as conductances in a **crossbar** grid; apply the input vector as voltages on the rows; **Ohm's law** makes each device output a current proportional to `weight × input` (the multiply), and **Kirchhoff's law** sums all currents on each column (the accumulate). The result is a **full matrix-vector multiply — an entire layer — in ONE analog step**, at femtojoule energy. No clock stepping through weights; the physics does the whole layer at once.

**For us:** this *is* your "Ganglion as a static wire, input cap → output cap, one charging time." A full layer = one crossbar = one settle. The crossbar literature is your closest engineering kin — read it for the *non-idealities* you'll hit (device variation, IR drop along wires, ADC cost at the edges, limited precision), which are exactly your PVT concerns. **The crucial number:** a crossbar's cost is its **area = (rows × columns) devices.** So "how big can one block be" is an area question, and **grouping/block-diagonal (`11-connectivity.md`) is the lever that keeps each crossbar small enough to build** while butterfly-mixing reconnects them. Spatial compute + block-local connectivity are the *same* design conversation.

---

## Systolic arrays (TPU) — the digital middle ground, worth knowing

*Kung & Leiserson, 1978; Google TPU, Jouppi et al., 2017.*

How the digital world gets *most* of the spatial win without one-multiplier-per-weight. A **systolic array** is a grid of tiny multiply-accumulate cells; **weights sit still** ("weight-stationary"), and **data flows through** the grid in a wave, each cell doing one MAC and passing partial sums to its neighbor. The TPU v1 is a **256×256** such grid doing 92 trillion ops/sec at ~40 W — fast *because* data marches through a fixed spatial structure instead of bouncing to memory and back.

**For us:** the systolic array is the **time-multiplexed cousin** of your full crossbar — it reuses each cell across many data items (more temporal) but keeps weights stationary (the key CIM-like idea: *don't move the weights*). It's worth knowing as the proven large-scale point between "one ALU" (fully temporal) and "one device per weight" (fully spatial, your crossbar). If a single analog crossbar ever gets too big/imprecise, **tiling** it (systolic-style: stream activations through smaller crossbar tiles) is the known scaling path — and it pairs naturally with your block-local Ganglia (each tile = a group).

---

## The synthesis (this file)

The "ALU wall" is the **von Neumann/memory wall** — moving weights costs ~200× the compute — and your **compute-in-memory** substrate (resident weights that *are* the multiplier) is the field's recognized answer, so you're already past the wall the question worries about. Your draft-5 "Ganglion as a static wire" is **spatial dataflow / full unrolling**, realized as an **analog crossbar MVM** (a whole layer in one settle via Ohm + Kirchhoff). Its one cost is **area** (one path per weight) — and that is exactly the cost **block-local connectivity** (`11-connectivity.md`) controls: smaller crossbars, reconnected by cheap shuffles/butterfly mixing. If one block ever gets too big, **systolic-style tiling** is the proven way to stream through smaller crossbars. So the whole worry resolves into one clean design rule: **stay spatial (let each block settle once), keep each crossbar small via grouping, and reconnect groups with log-depth/permutation mixing — not a dense ALU and not a dense clip.** That is your draft-5 instinct and the modern hardware playbook, converged.
