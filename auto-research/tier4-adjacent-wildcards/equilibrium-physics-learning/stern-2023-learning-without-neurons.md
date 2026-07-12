# Learning Without Neurons in Physical Systems
- **Authors / Year / Venue:** Menachem Stern, Arvind Murugan / 2023 / Annual Review of Condensed Matter Physics 14, 417–441
- **Link:** https://arxiv.org/abs/2206.05831 (journal: https://www.annualreviews.org/doi/10.1146/annurev-conmatphys-040821-113439)
- **Tier / Topic:** tier4 / t4.2 equilibrium & physics-based learning
- **Relevance:** ⭐⭐⭐ — the field map of "physical learning": what it means for matter itself to learn by local rules, and why model-free adaptation is the payoff.

## TL;DR
The review that names the field. Large classes of physical systems — flow networks, mechanical/elastic materials, molecular self-assembly — can *physically learn*: their microscopic parameters (pipe conductances, spring stiffnesses, binding energies) adapt autonomously under local rules in response to examples of use, with no processor, no model, and no neurons. Learning becomes a driven physical process rather than an optimization performed *on* the system.

## The mechanism (how it actually works)
The recurring skeleton across substrates: (1) the system's response to inputs is a **physical equilibrium** (minimum of energy or dissipation); (2) a desired behavior is imposed as a **boundary condition or drive** (a clamped output, an applied strain, a chemical bath); (3) each microscopic element follows a **local rule** that moves its parameter in the direction that reduces the discrepancy it can sense locally — typically a contrast between the free response and the driven response (coupled learning / EqProp are the sharpened versions of this), or aging/creep dynamics that naturally relax toward the driven configuration ("directed aging": material plasticity itself is the learning rule). The deep point: local rules exist whose *collective* effect is descent on a *global* objective the elements never see — the physics assembles the credit assignment.

## Key results / claims
- Unifies experiments and theory across flow networks (allostery-like function), elastic networks (auxetic and shape-shifting materials), and self-assembly (molecular recognition as learned classification).
- Physical learners are **model-free**: no accurate system model is needed, so fabrication variation and drift are absorbed rather than fought.
- They **re-adapt autonomously** to changing conditions — continual adaptation is native, not bolted on.
- Frames physical constraints (locality, symmetry of interactions, available measurements) as the axes that reshape abstract learning theory.

## How it relates to us
- **Organ / phase touched:** the project identity itself (the substrate premise); the analog-realism pass; the continual-learning claim.
- **Same as us:** their two headline selling points — model-free tolerance to device imperfection, and native continual re-adaptation — are exactly the two capabilities our P6–P11 validation banked (noise robustness, drift-following). Independent convergence from condensed-matter physics onto our value proposition.
- **Different from us:** the systems reviewed learn *functions*, not representations; most are supervised (target = clamped boundary); none have a memory/namer/gate economy; scales are tiny (tens of elements).
- **What we could borrow or test:** the vocabulary. "Physical learning," "coupled learning," "directed aging" are the condensed-matter names for our design space — citing this review places our math model in a recognized field rather than a private analogy. Their taxonomy of what each element can locally sense is a ready-made audit frame for the realism pass.
- **What contradicts or challenges us:** the field's honest scaling status — no physical learner reviewed here exceeds toy scale — is also *our* status at the circuit level; the review denies everyone (including us) the claim that local physical learning is proven at scale.

## Follow-on leads
- Stern et al., "Physical learning beyond the quasistatic limit" — dynamics-rate effects on coupled learning, ⚠ not fetched here.
- Metamaterials that learn to change shape (arXiv:2501.11958), self-learning magnetic Hopfield network with intrinsic gradient descent (arXiv:2501.01853) — newer substrate entries, ⚠ not fetched here.
- The Restricted Kirchhoff Machine (arXiv:2509.15842) — the unsupervised turn of this field, ⚠ not fetched here.
