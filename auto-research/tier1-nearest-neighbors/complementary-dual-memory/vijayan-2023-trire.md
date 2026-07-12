# TriRE: A Multi-Mechanism Learning Paradigm for Continual Knowledge Retention and Promotion
- **Authors / Year / Venue:** Preetha Vijayan, Prashant Bhat, Elahe Arani, Bahram Zonooz / 2023 / NeurIPS 2023
- **Link:** https://arxiv.org/abs/2310.08217 (fetched)
- **Tier / Topic:** tier1 / t1.4 complementary dual-memory
- **Relevance:** ⭐⭐⭐ — the "biological kitchen-sink" pole of the dual-memory field: it stacks *many* neurophysiological mechanisms (neurogenesis, active forgetting, metaplasticity, gating, rehearsal) into one method. Useful mainly as the **contrast** to our discipline — it is exactly the "so many papers / add every brain trick" temptation our build rules forbid.

## TL;DR
TriRE fights forgetting with a three-phase per-task loop over the *neurons* of one network: **Retain** the most salient neurons for the task (freeze/protect them), **Revise** by rehearsing and solidifying current+past knowledge, and **Rewind-Relearn** by resetting the *less-active* neurons and re-training them so unused capacity is recycled for future tasks. It leans on task modularity and combines several brain mechanisms at once, beating single-mechanism CL methods.

## The mechanism (how it actually works)
Within a task, TriRE runs three stages:
1. **Retain:** score neurons by salience/activity; keep a sparse set of the most prominent ones as the task's "winning subnetwork" and protect them from future overwriting (a context-dependent gating / metaplasticity move).
2. **Revise & solidify:** with an episodic buffer, rehearse old+new so the extracted knowledge is reinforced and decision boundaries stabilize (standard replay, but scoped to the retained subnetwork).
3. **Rewind-relearn:** take the neurons that were *not* prominent, **rewind** them (reset toward earlier weights) and **relearn** — an "active forgetting + neurogenesis" step that frees and re-initializes capacity so later tasks have room, rather than saturating the net.

The result is a modular network where each task owns a sparse subnetwork, unused neurons are continually recycled, and rehearsal glues it together.

## Key results / claims
- Beats CL methods that use these mechanisms *in isolation* across Seq-CIFAR-10/100 and Seq-TinyImageNet class-incremental settings.
- The gains come from the **combination** — retention (protect) + promotion (recycle) + rehearsal together reduce task interference more than any one alone.
- Emphasizes neuron-level modularity and capacity management as the missing pieces beyond plain replay.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** conceptually the SCFF bulk (neuron allocation) — but mostly a **methodological contrast**, not an organ we'd modify.
- **Same as us:** it's CLS-motivated and rehearsal-based, and its "protect the important directions, recycle the rest" instinct rhymes with our spine story (keep class *directions*, discard the dense mean). Both accept that continual learning needs *some* structural bookkeeping beyond a single loss.
- **Different from us:** TriRE is the **opposite of our discipline.** It reallocates neurons *inside* a backprop-trained net every task (retain/rewind/relearn), which requires per-task boundaries, a trainable plastic backbone, and gradient access to every neuron — *all three of which we forbid.* Our cortex is frozen and unsupervised (no neurons to protect or recycle toward labels), our namer is closed-form (no neurons at all), and we are boundary-free. There is no "rewind-relearn" in an analytic head.
- **What we could borrow or test:** almost nothing structurally — but one *idea* transfers cheaply: **capacity recycling as an eviction/allocation policy in the LUT.** TriRE recycles unused neurons; our LUT already does novelty-allocation + usage-aging of *prototype slots*. Reading TriRE as "usage-scored recycling of a bounded resource" gives an alternative framing for CBRS eviction (evict by staleness/low-usage, not just class balance) — worth noting alongside the ESMER error-based rule, though lower priority.
- **What contradicts or challenges us:** it's the strongest datapoint for "more mechanisms win." TriRE beats single-mechanism methods by stacking five — which could be read as pressure to bolt more machinery onto our loop. Our project rules (walk one spine, keep the north-star menu closed) explicitly resist this; TriRE is the citation for *why that temptation exists* and the reminder that our object's value is **substrate + closed-form simplicity**, not mechanism count.

## Follow-on leads
- Winning-subnetwork / lottery-ticket CL (PackNet, Mallya 2018; SupSup, Wortsman 2020) — the neuron-masking lineage TriRE sits in.
- Active-forgetting / neurogenesis CL (e.g., NISPA, Gurbuz 2022) — the "recycle capacity" branch, if the LUT ever needs a smarter allocation rule.
- Metaplasticity (BGD / synaptic-metaplasticity, Laborieux 2021) — per-weight importance as a register (ties to SI in our phase9 library).
