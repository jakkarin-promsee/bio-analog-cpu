# Recurrent Memory Transformer (RMT)
- **Authors / Year / Venue:** Bulatov, Kuratov, Burtsev / 2022 / NeurIPS 2022
- **Link:** https://arxiv.org/abs/2207.06881 (fetched)
- **Tier / Topic:** tier3 / t3.4 prefrontal-controller
- **Relevance:** ⭐⭐⭐ — a **few memory tokens** carried across time as the entire shared state; the minimal "bandwidth-limited register that persists" pattern.

## TL;DR
Add a handful of special **memory tokens** to a plain Transformer's input. After processing a segment, the memory tokens' output states are **carried to the next segment** as its memory input — a small recurrent state threaded through an otherwise stateless model. Read and write to memory are just ordinary self-attention; no architecture change. Matches Transformer-XL with a smaller memory budget and beats it on long-range tasks.

## The mechanism (how it actually works)
Prepend M memory tokens (M small, e.g. 10) to segment t's tokens. Self-attention lets the real tokens **read from** memory and, at the segment's end, lets the memory slots **write** a summary of the segment. Those M output vectors become the memory input for segment t+1. The model learns, by ordinary BPTT over segments, to compress what the next segment will need into M vectors — a **fixed-width bottleneck through time**. The recurrence is entirely in that tiny carried state; everything else is a standard forward pass.

## Key results / claims
On language modeling RMT reaches Transformer-XL quality with less stored context; on tasks needing long-range/algorithmic memory it exceeds Transformer-XL, and memory tokens even help when added on top of XL. The compact recurrent state is enough to carry global information across many segments.

## How it relates to us  ← the load-bearing section
- **Organ / phase touched:** north-star coordinator + the settle loop (a persistent working register between settles).
- **Same as us:** a **few slots that survive across time steps** is the working-memory register the "prefrontal" loop needs — hold a little, carry it forward, re-read next step. Fixed width regardless of stream length matches a bounded analog register.
- **Different from us:** the memory read/write are learned attention trained by **BPTT through segments** — the exact backward-through-time our substrate forbids; and RMT's memory summarizes *its own* token stream, not a set of external organs.
- **What we could borrow or test:** the **minimal design** — a small carried register that the settle loop reads at the start and writes at the end of each "thought" — with the write governed by our gate rather than learned attention.
- **What contradicts or challenges us:** RMT's memory only becomes useful because BPTT teaches it *what to store*; a gate-written register with no learned compression may carry the wrong summary — the open question for a gradient-free recurrent state.

## Follow-on leads
- Block-Recurrent Transformers (Hutchins 2022); Memorizing Transformers (Wu 2022, kNN memory); Fast-Weight Programmers (Schlag 2021, already in t3.1 hippocampus).
