# Gated Delta Networks: Improving Mamba2 with Delta Rule (Gated DeltaNet)
- **Authors / Year / Venue:** Songlin Yang, Jan Kautz, Ali Hatamizadeh / 2024 / ICLR 2025
- **Link:** https://arxiv.org/abs/2412.06464
- **Tier / Topic:** tier3 / t3.2 recurrent "think until it settles" (the *cross-time memory core*, from t3.1)
- **Relevance:** ⭐⭐⭐⭐ — the substrate-legal recurrent state: **gate (decay) + delta rule (targeted overwrite)** on a fast-weight matrix — our planned delta-rule memory with the missing forget knob.

## TL;DR
Linear transformers keep a matrix-valued state updated per token — a recurrence over fast weights instead of tokens. Mamba2's trick is a *gate* (scalar decay that can flush the whole memory fast); DeltaNet's trick is the *delta rule* (error-correcting overwrite of the value stored at a key). This paper shows they are complementary and combines them into one **gated delta rule**, with a hardware-efficient parallel training algorithm; the result beats both parents across language modeling, retrieval, length extrapolation, and long-context benchmarks.

## The mechanism (how it actually works)
The state is a matrix S (an associative memory: keys → values). Per input token with key k, value v:
`S_t = α_t (I − β_t k_t k_tᵀ) S_{t−1} + β_t v_t k_tᵀ`
Read right-to-left: write the new association as an outer product (v kᵀ); before writing, *erase what the memory currently returns for this key* (the (I − β k kᵀ) term — the delta rule: update by the error between stored and desired value, not blind accumulation); and scale everything by a learned gate α_t ∈ (0,1) that can decay or flush the entire memory when context changes. Gating handles "this is now irrelevant" globally and fast; the delta rule handles "this particular fact changed" surgically. Reading is a matvec: out = S q. Training is parallelized with a chunkwise WY-representation algorithm so it runs at Mamba2-like speed on GPUs.

## Key results / claims
- Consistently outperforms Mamba2 and DeltaNet on language modeling, common-sense reasoning, in-context retrieval, length extrapolation, long-context understanding.
- Hybrids (Gated DeltaNet + sliding-window attention or Mamba2 layers) push further — the linear-recurrent core carries most of the load, attention patches the rest.
- The gate and the delta rule are *separately* insufficient: erasure without precision (Mamba2) fails retrieval; precision without erasure (DeltaNet) fails long-context drift.

## How it relates to us
- **Organ / phase touched:** the hippocampus organ (t3.1 — Schlag's fast weights was already carded) + the north-star loop's *cross-time* state; the "keep the LSTM gate, not the throne" advice from the dossier, modernized.
- **Same as us:** every operation is crossbar-native — outer-product write, rank-1 error-correcting update, matvec read, scalar decay. This is the closed-form learning memory we planned (delta rule), now with the field's verdict that it *needs a forgetting gate* to survive long streams — which is our P8/P9 lesson (firing more forgets more; maintenance needs explicit forgetting control) in the fast-weight world.
- **Different from us:** the gate α and write strength β are *learned functions of the input* trained by backprop; the whole thing is a sequence-model layer, not a settle — it advances one step per input (the LSTM limitation, deliberately).
- **What we could borrow or test:** (1) build the hippocampus write rule as the gated delta rule with **closed-form** α/β: α from the drift-gate signal we already compute (drift high → decay faster), β from namer error (surprise-gated write — Titans' skeleton on closed-form parts); (2) inside the settling loop, this is the natural *state carrier between thoughts*: the loop settles within a thought, the gated delta memory carries across thoughts; (3) their retrieval benchmarks are the test for whether our LUT-as-delta-memory actually recalls under drift.
- **What contradicts or challenges us:** their ablations say precision retrieval wants *some* attention (the hybrid wins) — a pure fast-weight memory has a capacity/interference ceiling; our LUT may hit the same wall and need the CAM-style exact match (t3.1 Li 2020) as the "attention" half.

## Follow-on leads
- Schlag et al. 2021 (already carded, t3.1) — the delta-rule fast-weight root.
- Behrouz et al. 2025 Titans (already carded, t3.1) — surprise-gated writes; this paper is its linear-algebra sibling.
- Yang et al., parallelizing DeltaNet with WY representations (arXiv 2406.06484) — the training algorithm.
- RWKV-7 / Mamba2 — the wider gated linear-recurrence family.
