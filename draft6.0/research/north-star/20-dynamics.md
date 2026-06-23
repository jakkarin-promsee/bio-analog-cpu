# 20 — Dynamics & stability: will your analog system *settle*?

> Your chip does not "execute layers" — it is a **physical dynamical system that evolves charge over time and settles.** That changes the foundational question from "is the math correct?" to **"will the dynamics converge, or oscillate, or blow up?"** This is the theory of *physical* computation, and it's load-bearing for *every* analog and recurrent part of the project (the equilibrium loop, liquid atoms, the Limbic recurrence, even a single Ganglion settling). It was scattered across `3`/`8`/`17`; this file is the spine.

---

## The reframe: computation as a dynamical system

A feed-forward digital net is a *function*. Your analog network is a **dynamical system**: state `x` evolves by `dx/dt = f(x, input)` (a capacitor network relaxing), and the "answer" is **where it settles** — its equilibrium / fixed point. This is the view behind Neural ODEs (`8`), Deep Equilibrium Models (`3`), Hopfield memory (`1`), and your own "settle once" Ganglion. The whole question of correctness becomes a question of **stability**: does `x` reach a unique, meaningful resting state?

Three things can happen as the dynamics run: it **converges** (settles — good), it **oscillates** (limit cycle — sometimes useful, often not), or it **diverges** (blows up — fatal). Which one happens is decided by the math below, and you can *design* for convergence.

---

## Lyapunov stability — the energy-that-decreases proof of settling

*Lyapunov, 1892; ubiquitous in control theory.*

The classical, exact tool. To prove a system settles, find a **Lyapunov function** `V(x)` — a scalar that is **bounded below and always decreases** as the dynamics run (`dV/dt < 0`). If such a `V` exists, the system *must* roll downhill to an equilibrium and stay there — settling is **guaranteed**, no simulation needed. A Lyapunov function is, literally, an **energy** the system dissipates (which is why this file is the twin of `21-energy.md`).

**For us:** this is how you *certify* that an analog block will converge instead of ringing. If your Ganglion/loop has an energy that its physics always lowers — and a dissipative analog circuit (with leak/loss) *does* — then it provably settles. Hopfield's genius was exactly this: he *gave* his network an energy function so recall = guaranteed downhill settle. Design your dynamics so a Lyapunov/energy function exists (symmetric-ish couplings, dissipation, bounded gain), and you've **proven stability by construction.**

---

## Contraction theory — the strong, designable condition

*Lohmiller & Slotine, 1998; ML applications: contraction for RNNs/Neural-ODEs/implicit nets ([review](https://arxiv.org/abs/2110.00207)).*

The modern, *constructive* version, and the most useful for you. A system is **contracting** if **any two trajectories converge toward each other exponentially**, regardless of where they started. Contraction guarantees, all at once: a **unique** equilibrium, **global exponential** convergence to it, **initial conditions forgotten** exponentially fast, and **no chaos.** It's checkable from a condition on the Jacobian (negative "contraction metric"), and it's *designable* — you can constrain a network to be contracting.

**For us:** contraction is the gold standard "it will settle" guarantee, and it connects three things you already have:
- **Bounded gain / Lipschitz (`17`/`19`):** a contracting system has bounded gain — the *same* spectral-norm/saturation ceiling that bounds noise amplification *also* guarantees settling. One constraint, three payoffs (stability + durability + generalization).
- **The reservoir's "echo state property" (`8`/`10`)** is exactly a contraction condition (fading memory — old inputs forgotten). It's why a random reservoir is *stable* despite being untrained.
- **Liquid atoms / leak:** dissipation (your capacitor leak) is what makes the dynamics contracting rather than conservative (which would oscillate forever). Your leak isn't just for forgetting — it's what *guarantees the system settles.*

So "will my analog circuit converge?" has a real, designable answer: **make the dynamics contracting** (bounded gain + dissipation), and convergence is *proven*, exponential, and noise-forgetting.

---

## The edge of chaos — the dial between order and chaos

*(The dynamical-systems reading of `17`'s deep-information-propagation.)*

`17` introduced the edge of chaos for signal propagation; here is its dynamical meaning, via **Lyapunov exponents** (the rate at which nearby trajectories separate). Negative exponent → **contracting/ordered** (perturbations die, but too far in = signal vanishes, frozen). Positive exponent → **chaotic** (perturbations explode, sensitive, unstable). **Zero → the edge**, the critical line where the system is maximally expressive *and* still stable — the richest dynamics that don't blow up.

**For us:** this is the *dynamical* statement of your residual/variance instinct. You want your recurrent/analog dynamics tuned **near the edge** — contracting *enough* to settle and forget noise (`17`/`18`), but not so contracting that all structure collapses. The knob is gain vs dissipation (weight scale vs leak). Too much gain → chaos/oscillation/noise-explosion; too much leak → everything decays to zero. The sweet spot is the edge, and your physical parameters (cap leak rate, op-amp gain, saturation) are exactly the dials.

---

## Attractors *are* computation (settling is the answer, and the cleanup)

*Hopfield, 1982 (`1-memory.md`); attractor dynamics.*

The payoff of all the above: in a stable dynamical system, the **equilibria are computational results.** A memory recall is "settle to the nearest stored attractor"; a decision is "settle to the winning attractor"; your thinking loop (`3`) is "settle to the consistent interpretation." And because settling is *downhill into a basin*, it **cleans up noise for free** — a perturbed state rolls back to the clean attractor (the `17` "restoring organ," now formalized: the basin of attraction *is* the error-correcting region).

**For us:** this is why building computation *as a settling dynamical system* is the right move for an analog chip, not a constraint to fight: stability theory gives you **convergence guarantees, noise-cleanup, and memory all from one mechanism** (a well-shaped energy landscape with deep basins). The depth and width of the basins = how much noise you can absorb = your durability margin, now a *dynamical* quantity you can design.

---

## The shape of the answer (this file)

Your chip computes by **physically settling**, so "is it correct?" becomes **"does it settle?"** — a stability question with real, *designable* answers. **Lyapunov:** if an energy function exists that the dynamics always lower (a dissipative circuit has one), settling is *proven* — Hopfield built memory this way. **Contraction:** bounded gain + dissipation ⇒ a *unique* equilibrium, *global exponential* convergence, noise forgotten, no chaos — and it's the *same* bounded-gain constraint that gives durability (`17`) and generalization (`19`), and it's why your *leak guarantees settling* (not just forgetting). **Edge of chaos:** tune gain-vs-leak to the critical line — maximally expressive but still stable (the dynamical form of your residual/variance instinct). **Attractors:** equilibria *are* results, and basins *are* error-correction — convergence, memory, and noise-cleanup from one shaped landscape. The through-line: **design your analog dynamics to be contracting near the edge of chaos, and settling, stability, durability, and memory all come together** — which is the literal energy-descent picture of `21-energy.md`.
