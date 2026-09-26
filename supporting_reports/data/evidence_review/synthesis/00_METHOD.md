# Spacetime engineering textbook — working method

Working space for deciding how the book is set up and what it says. Nothing
here is book text.

## Ground rules (from the user)

- The book is a textbook for the field. The active-rail project supplies
  results and practices; it never supplies the book's shape, a case study or
  a narrative.
- A practice or claim enters the book only after vetting. Quick
  generalizations of how the project happened to work are hypotheses.

## Where candidates come from

Candidates are generated from three sources. Listing the project's current
rules and then looking for support would bias every verdict toward the
project's habits.

1. **Incidents in the project record**: reversals, failures detected late,
   costly detours, and catches where a check changed a decision. Sources:
   git history (commit dates and messages), reports that announce a failure,
   repair or redesign, and the dated plan.md handoffs. For each incident,
   record what was known when, which tool would have caught it, and whether
   that tool existed at the time.
2. **The literature's own practices**, especially the 2022–2026 work on
   verifying warp and wormhole constructions. Examples are Le's five-criterion
   standard, observer-robust energy-condition tests, Warp Factory, and the
   source-consistency critiques. Where the field already codifies a practice,
   the book cites it; where the project's version is weaker, the book teaches
   the stronger one.
3. **Derivations**: statements that follow from the equations, such as
   zero Eulerian momentum ⇒ Type I. These are physics, not practice, and
   belong in the physics chapters.

4. **Design-response maps**: how the physics responds to engineering
   strategy. For each part and knob a design exposes, record which physical
   channels it moves: demand magnitude and location, algebraic type, occupant
   quantities, causal structure and arrival, swept matter, and source-family
   requirements. Mark each response as an identity for its class of metrics or
   a measurement on one design, and record the couplings and the separations
   between knobs. The project's maps (one-space and throat era) are compared
   with the literature's parameter studies and with design-decomposition
   methods from engineering (axiomatic design, sensitivity analysis). The
   identity-backed responses become the book's design-principle chapters.

Evidence inventories live in `inventory/`: project incidents (May–June,
September), knob maps (one-space, throat era), and three literature surveys
(design strategy, foundations and verification, adjacent engineering methods).

## Coverage requirement (from the user)

Everything that the project's work, existing science and engineering research
can justify is covered, including the design-response maps. Coverage is
checked against the inventories before the structure is fixed.

## Vetting rubric (one file per candidate in `vetting/`)

1. **Decompose.** Split the candidate into its separate claims; a single
   slogan usually bundles an ordering claim with several technical ones.
2. **Truism test.** Would any competent practitioner in an adjacent
   engineering field do this without being told? If so, it earns a sentence
   at most. The domain-specific reason it matters may still earn more.
3. **Scope and exceptions.** Does it always hold? Under which source class,
   symmetry, regime or design class? Look actively for counterexamples,
   in the literature and in the project.
4. **Evidence.**
   - Project: the incident, its date, the counterfactual (tool available?
     decision changed?), and n, the number of independent incidents.
   - Literature: fetched and read, with the version pinned (arXiv IDs can
     change content between versions).
   - Derivation: written out.
5. **Better practice elsewhere?** Compare with the literature's method for
   the same problem.
6. **Hazards.** What does following the practice cost or distort?
7. **Verdict**, one of:
   - *Established physics* — cite.
   - *Derived general result* — state with proof.
   - *Evidence-backed practice* — state with evidence and scope.
   - *Observed hazard* — state with mechanism; label the incident count.
   - *Heuristic* — label as such, or drop.
   - *Truism* — one sentence.
   - *Project habit* — drop.
8. **Placement.** Physics chapter or method chapter.

## Book structure

Decided after the candidates are vetted. The skeleton in `01_CANDIDATES.md`
is provisional.

## Open questions for the user

- Reader: GR graduate student, physics-literate engineer, or both with
  layered sections?
- Format: LaTeX in the repo, like the disclosure?
- Existing canon to position against (to verify before relying on it):
  Visser, *Lorentzian Wormholes* (1995); Alcubierre, *Introduction to 3+1
  Numerical Relativity* (2008); Gourgoulhon, *3+1 Formalism in General
  Relativity* (2012); Kontou & Sanders, energy-conditions review (CQG 2020);
  Lobo (ed.), *Wormholes, Warp Drives and Energy Conditions* (2017).
