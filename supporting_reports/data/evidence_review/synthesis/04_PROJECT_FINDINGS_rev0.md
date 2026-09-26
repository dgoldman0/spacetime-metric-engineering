# Findings for the active-rail project (outside the book)

Surfaced while vetting. Nothing has been changed in the repo.

## Claims that need rewording

1. **ANEC exclusion** (`ANEC_MAP_PASS.md`, README). "No semiclassical quantum
   sector can supply the demand at any size" holds only:
   - for a lead that persists between distant endpoints;
   - with null completeness and the generic condition;
   - within the semiclassical regime.

   The quantum exclusion is proven perturbatively and conjectured in
   general. Two further steps are needed: show that the complete ray is
   achronal, not only the segment from departure; and measure the transverse
   width of the negative-ANEC bundle. The theorem chain to cite is Gao–Wald
   Theorem 1 in Galloway's null-line form, with Graham–Olum Lemma 1
   (`lit_design_strategy.md` C.7).
2. **Disclosure, quantum sources.** It still says quantum fields supply the
   rail below 0.45 mm (tex l.401 and the acceptance table at l.468), which
   contradicts the ANEC map.
   Updating the disclosure needs your explicit go-ahead.
3. **Disclosure citation.** arXiv:2605.25417 is Le's boundary-cost paper only
   in v1 and v2. v3 (17 Sep) is a different paper, so pin `v2`. Also,
   2606.22531 was retitled and substantially revised in v4.
4. **Time function.** σ as a global time function gives stable causality,
   not global hyperbolicity; say which.
5. **Lapse envelope.** α > 2r|β_z| is a leading-order heuristic; Type I
   occurs at ratios up to 1.59.
6. **Energy formula with a stretch factor.** The energy formula is written
   with a stretch factor A but holds only for A = 1
   (`LAPSE_AND_STAGING_PASS.md` l.16).
7. **Conformal flux-free result.** It requires β_r = 0 across the rise,
   which is not stated.
8. **Speed-scaling agreement.** The report quotes 10⁻⁵ where the test
   tolerance is 10⁻³, and the identity is exact only in the steady lane.

## Design questions raised

9. **Type I gate against the open source family.** Kinetic-braiding
   scalars reach Type IV exactly where the NEC fails (Gergely 2026). The
   Type I criterion was adopted a day before this family was identified, and
   has not been matched to its algebraic range.
10. **Lapse-only NEC lemma.** On flat slices every non-constant lapse
    violates the NEC somewhere. Speed as a lapse contrast therefore places
    its contrast in NEC-violating falls. This is consistent with the census.
    It is a structural cost of flat slices, and curved slices escape it.
11. **Untested design responses:**
    - the QI source test on the compartment, cone, trimmed and speed-scaled
      designs;
    - passenger temperature at clock rates other than 1;
    - the shift-transition radius in flat-slice designs.

## Process observations

12. **The stopping rule was bypassed.** The gate handoff said to redesign
    before the Comer inversion. The inversion ran 11 hours after the failed
    gate, and 183 commits followed.
13. **A style rule erased a verdict.** Under the affirmative-language and
    no-running-log rules, commit `734156c` removed the Type IV verdict from
    the disclosure, and `plan.md` never recorded it. A negative-results
    ledger kept separate from the disclosure would preserve both rules.
14. **HiGHS default settings.** `graded_electrothermal.py` l.142–145 runs
    HiGHS with default settings, which drop small coefficients.
15. **Uncommitted work by another session.** The working tree has these
    uncommitted changes, and the process behind them was running during this
    session:
    - modified: `compartment_service.py`, `front_surface.py` and
      `tests/test_speed_scaling.py`;
    - untracked: `run_deficit_minimization_pass.py`, `test_shaped_pattern.py`
      and `data/deficit_minimization_pass/`.

    Item 8 cites `test_speed_scaling.py` at HEAD.
