# Findings for the active-rail project (outside the book)

Surfaced while vetting; corrected against `audit_synthesis.md` §2
(2026-09-26). Nothing has been changed in the repo.

## Claims that need rewording

1. **ANEC exclusion** (`ANEC_MAP_PASS.md` l.47; `README.md` l.91–92, which
   also states flatly "Achronal ANEC holds for quantum fields"). The claim
   "No semiclassical quantum sector can supply the demand at any size" holds
   only under three conditions:
   - for a lead that persists between distant endpoints;
   - with null completeness and the generic condition;
   - within the semiclassical regime.

   Achronal ANEC is proven in flat space (Faulkner et al. 2016; Hartman et
   al. 2017), for a free scalar at first order in curvature on NEC
   backgrounds (Kontou–Olum 2015), and at first order in ħ given the
   generalized second law (Wall 2010). Its self-consistent form is
   Graham–Olum's conjecture, and test-field versions fail (Urban–Olum 2010).

   Two further steps are needed:
   - show that the complete ray is achronal, not only the segment from
     departure;
   - measure the transverse width of the negative-ANEC bundle.

   The theorem chain to cite is Gao–Wald Theorem 1 in Galloway's null-line
   form, with Graham–Olum Lemma 1 (`lit_design_strategy.md` C.7). ANEC
   magnitudes carry the affine normalization; only their signs are
   invariant.
2. **Disclosure, quantum sources.** The disclosure still says quantum fields
   supply the rail below 0.45 mm (tex l.401 and the acceptance table at l.468),
   and says it again at l.573. The QI magnitude result and the ANEC exclusion
   answer different questions, and the disclosure should carry the exclusion
   with its scope. Updating the disclosure needs your explicit go-ahead.
3. **Citations.** The disclosure's `\bibitem{Le2026}` (tex l.605–608) cites
   arXiv:2605.25417 without a version. That identifier is Le's boundary-cost
   paper only in v1 and v2; v3 (17 Sep) is a different paper, so pin v2.
   Separately, arXiv:2606.22531 is cited in the gate handoff (l.172) and in
   `LE_COUPLED_RESET_SOURCE_ATTEMPT.md` (l.307) as "Steering a warp drive
   without exotic matter". It was retitled and substantially revised in v4
   (13 Sep); pin v3 where the old content is meant.
4. **Time function and global hyperbolicity.** The disclosure states that σ
   is a global time function (l.315), which gives stable causality. A stronger
   statement is available: with α > 0 and α + |β| bounded, every σ-slice is a
   Cauchy surface, so a bounded single-rail design is globally hyperbolic
   (`verification/v3_moving_patterns.md`, I19; non-imprisonment argument). This
   conflicts with Barzegar–Buchert–Vigneron 2026 Thm IV.7, which is recorded as
   disputed (`inventory/lit_design_strategy.md` F.1.11). No claim of global
   hyperbolicity appears anywhere in the repo.
5. **Lapse envelope.** α > 2r|β_z| is a leading-order heuristic; Type I occurs
   at ratios up to 1.59 (`AMPLITUDE_PASS.md` l.111–113). The reports call it
   "the sufficient estimate, and the classifier decides", though its
   sufficiency is not established either. The disclosure uses it as a held
   condition: glossary l.114, pass criteria l.267 and l.277, packet clock
   l.482 and claim text l.533.
6. **Energy formula with a stretch factor.** `LAPSE_AND_STAGING_PASS.md`
   l.15–16 writes ρ = −(Aβ_r/α)²/32π while stating A = 1. The formula holds
   for any constant A, which is a rescaling of z, and fails for a varying A.
   Dropping the A removes the ambiguity. The symbolic verification
   (`verification/v1_flat_slice_class.md`) settles the general form.
7. **Conformal flux-free result** (`ONE_SPACE_REVISION.md` l.103–107). It
   holds where the shift has no radial gradient across the rise. That
   condition is inferred; the report states no shear condition, the
   stretched (A ≠ 1) tensor was never derived, and the test places the shift
   layer outside the rise (`tests/test_axial_track.py` l.519–526).
8. **Speed-scaling agreement.** The report quotes 10⁻⁵, while the HEAD test
   asserts agreement within 10⁻³ of the tensor scale at one time and four
   offsets. The identity is exact only in a steady lane.

## Design questions raised

9. **Type I gate against the open source family.** Kinetic-braiding scalars
   with a timelike gradient can be Type IV only where the NEC fails (Gergely
   2026, arXiv:2608.15228v1, accepted in PRD).
   - The standing Type I gate was reinstated on 23 Sep at `9be57e0` (11:50).
   - About 37 hours later, the higher-derivative scalars were named the open
     family in `SOURCE_SCALING_TEST.md` (`d128547`, 25 Sep 00:40).

   The gate criterion has not been matched to that family's algebraic range.
10. **Lapse-only NEC lemma.** On flat slices every non-constant lapse violates
    the NEC somewhere, given zero or uniform shift wherever the lapse varies
    and α → 1 outside. Speed as a lapse contrast therefore places its contrast
    in NEC-violating falls. This is consistent with the outer falls carrying
    most of the null content in the flat-slice designs: 456 of 799 in the
    staged-lapse design and 1,334 of 2,286 in the compartment design. Curved
    slices escape the lemma; a static clock maximum then needs only
    ρ + p_r + 2p_t < 0.
11. **Untested design responses:**
    - the QI source test on the compartment, cone, trimmed and speed-scaled
      designs;
    - passenger temperature at clock rates other than 1;
    - the shift-transition radius in flat-slice designs.

## Process observations

12. **The stopping rule was bypassed.** The gate verdict landed at `ed67c3d`
    (8 Sep 09:38). The Comer inversion followed 11 h 08 min later
    (`cc5e253`), and 195 commits came after it through `42e6688` (17 Sep),
    183 of them dated 9–17 Sep. The rule sat in a user-supplied handoff that
    entered the repo only on 16 Sep, as "separate research context"
    (`e7a9951`).
13. **The Type IV verdict left the disclosure the day it entered.**
    - Commit `921e560` (9 Sep 16:59) wrote the Type IV verdict into the
      disclosure.
    - `734156c` (20:31 the same day), "Remove source-trial narratives from the
      technical disclosure", replaced it with a conditional requirement.
    - `plan.md` first records Type IV on 23 Sep.

    The affirmative-language and no-running-log rules entered AGENTS.md on
    16 Sep, seven days later. The removal fits their intent, as its commit
    message shows, but a causal link to written rules is an inference. A
    negative-results ledger kept apart from the disclosure would serve both
    rules.
14. **HiGHS settings.** `graded_electrothermal.py` l.142–145 passes a time
    limit and 1e-9 primal and dual feasibility tolerances. It leaves the
    small-coefficient threshold at its 1e-9 default, which deletes
    coefficients at or below that size. The earlier GRADED runs were not
    repeated with a 1e-12 threshold.
15. **Uncommitted work by another session** (snapshot 26 Sep, about 11:40).
    The other session is still writing: `data/deficit_minimization_pass/`
    changed at 11:38. Its uncommitted changes:
    - modified: `compartment_service.py`, `front_surface.py` and
      `tests/test_speed_scaling.py` (a `sys.path` line only; the tolerance is
      unchanged);
    - untracked: `run_deficit_minimization_pass.py`,
      `test_shaped_pattern.py`, `tests/test_deficit_minimization.py` and
      `data/deficit_minimization_pass/`.
