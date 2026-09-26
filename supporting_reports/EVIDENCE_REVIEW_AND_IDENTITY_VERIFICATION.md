# Evidence Review and Independent Identity Verification

Date: 2026-09-26. Context: a session that planned a textbook on spacetime
engineering reviewed the evidence in this repository. It did three things:
- re-derived the identities the reports state, independently;
- surveyed the surrounding literature with every citation pinned to a
  version;
- read the project's record for decisions that later checks overturned.

This report records what the review establishes for the rail. The data, with
every script and draft, is in
[data/evidence_review](data/evidence_review/README.md).

## Result

- **The identities the reports rely on hold.** Four verifications re-derived
  them from scratch in sympy and mpmath, sharing no code with the harness:
  - the flat-slice lapse–shift class (134 checks);
  - spherical warped products (170 checks);
  - moving patterns and their horizons (75 checks);
  - the source-physics formulas (192 checks).

  Every check passes. The complete demanded tensor of the axial class, the
  flat-slice energy density, the pure-lapse identity, the product
  (service-region) identity, the Killing-energy laws, the horizon criterion
  and the spherical identities are all confirmed. A few statements need
  stated hypotheses, listed below.
- **Two statements in the reports are stronger than the evidence.**
  - The first concerns the ANEC exclusion. The [ANEC map](ANEC_MAP_PASS.md)
    and the README say that no semiclassical quantum sector can supply the
    demand at any size. Achronal ANEC is proven in flat space, for a free
    scalar at first order in curvature, and at first order in ħ given the
    generalized second law. It excludes a lead only when the lead persists
    between distant endpoints, and it needs null completeness and the generic
    condition.
  - The second is the lapse envelope α > 2r|β_z|. It is neither sufficient
    nor necessary for Type I: one coupled configuration meets it with a ratio
    of 0.3 and is still Type IV.
- **Bounded designs are globally hyperbolic.** With α > 0 and α + |β|
  bounded, every slice of constant exterior time is a Cauchy surface. That is
  stronger than the global time function the disclosure states. A Killing
  horizon coexists with it.
- **Every non-constant lapse violates the null energy condition somewhere on
  flat slices.** This holds where the shift is uniform across the slice and
  the lapse is bounded, whatever its fall-off. The
  [deficit minimization pass](DEFICIT_MINIMIZATION_PASS.md) found the
  quantitative floor of the same fact: the falls carry an irreducible
  deficit set by the log-lapse drop and the plateau's mean width.
- **The Type I gate may be stricter than the open source family needs.**
  Kinetic-braiding scalars with a timelike gradient can be Type IV where they
  violate the null energy condition (Gergely 2026, arXiv:2608.15228v1,
  accepted in PRD). The standing gate predates the choice of that family by
  about 37 hours, so its criterion has not yet been matched to the family's
  algebraic range.

## Identities: confirmations and stated hypotheses

The verification reports give each statement, its hypotheses, the method and
a derivation sketch. The points that change how the reports read are these.

**Flat-slice class** (`verification/v1_flat_slice_class.md`):
- The energy density ρ = −(β_r/α)²/32π holds with the stretch equal to one,
  and the form written with the stretch, −(Aβ_r/α)²/32π, holds exactly for a
  stretch A(t, z). For a radially varying stretch the density gains
  −Δ⊥A/(8πA) ([lapse and staging pass](LAPSE_AND_STAGING_PASS.md) l.15–16).
- The flux-free conformal rise of the [one-space revision](ONE_SPACE_REVISION.md)
  (l.103–107) needs two conditions: β_r = 0 across the rise, and a rise
  profile fixed in time. The exact flux is
  8πT_n̂r̂ = ∂_z(αAβ_r)/(2α²A) − n(∂_r ln A).
- Speed scaling (α, β) → (cα, cβ) is an exact isometry during a steady lane
  and for static fields. For ramps of fixed duration the verification gives
  the exact correction terms. The [closure pass](GEOMETRY_CLOSURE_PASS.md)
  quotes agreement to 10⁻⁵ (l.130–133), where the test asserts 10⁻³.
- The shear identity 8πT(n±e_z, n±e_z) = −(β_r² ± Δ⊥β) is exact, as the
  [axial track](AXIAL_TRACK.md) states. Opposite signs give Type IV where the
  (n, z) plane is invariant, as for the report's static shift window.
  Elsewhere the full classification decides.
- In the plane-invariant case the exact Type I condition behind the envelope
  is |a_r/r − K| > 2|β_z a_r|/α, with a = ln α. In general the discriminant
  of the (n, z, r) block decides. Even without convexity, the shift alone
  makes K = (β_z/α)² > 0.
- The lapse-only lemma has a short proof. The identity
  8πT(n+e, n+e) = Δ_{e⊥}α/α shows that a null-energy-respecting plane makes α
  subharmonic, and the 2D Liouville theorem then makes it constant. The
  proof also yields a localized form: a lapse contrast outside the convex
  hull of the shift's support costs null-energy violation there.

**Moving patterns** (`verification/v3_moving_patterns.md`):
- The Killing energy is conserved to 10⁻¹¹.
- The rate law d ln|k|/dσ = −k̂·∇α holds wherever the shift is locally uniform,
  and the general law carries a shift-gradient term. The kept-gain formula is
  exact only for paths that stay where the lab shift vanishes.
- The exit-angle law measures θ_f with static exterior observers, and exits
  lie within arccos(1/v) of the track.
- The shelf law needs three conditions: reflection, an axial exit and a
  terminal that is static while it is crossed.
- The surface α² = b² is null exactly where its transverse gradient vanishes.
  The signed surface gravity is κ = ∂_ζ(α − |b|).
- Light comes to rest in the pattern frame only at the null points of that
  surface, which is where Natário's Mach cone meets it.
- The tip's linearized escape rate λ is exact. The rate 2(κ − λ) for field
  energy density holds in geometric optics within a paraxial window, and its
  extension to quantum stress is an estimate.
- The lapse cavity reflects totally only from low to high lapse, and only
  where the pattern frame is static (b = 0).

**Spherical warped products** (`verification/v2_spherical_class.md`):
- The flare-out bound of at least one per end needs the lapse normalized to
  one at that end (in general the bound is 1/N∞), no horizon, and R′ → 1.
- Its time-dependent form, 4π∫R T(k,k) dλ = −Δ(dR/dλ) along any affine
  radial null geodesic, holds to 2×10⁻¹³.
- A d^p cusp raises the stress as d^{p−2} only where the affected second
  derivative appears in the Einstein tensor. The stress is integrable across
  a join if and only if p > 1.

**Source physics** (`verification/v4_source_physics.md`):
- The field-count requirement N ≥ 64π² d τ₀⁴ (L/ℓ_P)² of the
  [source scaling test](SOURCE_SCALING_TEST.md) is exact algebra.
  - It counts free, massless, minimally coupled scalars.
  - d is the deficit averaged over the sampling window, and τ₀ is the
    standard deviation of g².
  - Carrying the flat-space bound into curved spacetime is Ford and Roman's
    argued premise, not a theorem.
  - The faint-tail row cannot be reproduced from its pointwise inputs.
- The Casimir deficit π²ħc/(180a⁴) is the electromagnetic value; a
  conformally coupled scalar gives half of it. The matching gap is
  0.5814 √(ℓ_P L).
- The trace-anomaly coefficients were recomputed spectrally for scalars, Weyl
  fermions and Maxwell fields.
- The curvature-coupling bound F″ ≤ 8πT(k,k)F follows from the field
  equations. Its conclusion that F vanishes by ψ's first zero holds for rays
  that enter from a flat past.

## Statements to reword

| Location | Statement | Supported form |
|---|---|---|
| `README.md` l.91–92; [ANEC map](ANEC_MAP_PASS.md) l.47 | No semiclassical quantum sector supplies the demand at any size | Excluded for a lead that persists between distant endpoints, under null completeness and the generic condition, within the semiclassical regime. The complete first ray still needs to be shown achronal, and the negative-ANEC bundle's width measured. The theorem chain is Gao–Wald Thm 1 in Galloway's null-line form with Graham–Olum Lemma 1. |
| [Choreography pass](CHOREOGRAPHY_PASS.md) l.118–119 | "The envelope is the sufficient estimate" | A leading-order estimate; the classifier decides |
| [Lapse and staging pass](LAPSE_AND_STAGING_PASS.md) l.15–16 | ρ = −(Aβ_r/α)²/32π with A = 1 | Exact for A(t, z); a radially varying stretch adds −Δ⊥A/(8πA) |
| [One-space revision](ONE_SPACE_REVISION.md) l.103–107 | A conformal rise is flux-free | Where β_r = 0 across the rise and the rise profile is fixed in time |
| [Closure pass](GEOMETRY_CLOSURE_PASS.md) l.130–133 | Agreement to 10⁻⁵ | The test asserts 10⁻³; the isometry is exact in a steady lane |
| Gate handoff l.172; [coupled reset attempt](LE_COUPLED_RESET_SOURCE_ATTEMPT.md) l.307 | arXiv:2606.22531 as "Steering a warp drive without exotic matter" | Retitled and revised in v4 (13 Sep); cite v3 for that content |

The technical disclosure carries several of the same points:
- quantum fields supplying the rail below 0.45 mm (l.401, l.468, l.573), which
  the ANEC result supersedes;
- the lapse envelope as a held condition (l.114, l.267, l.277, l.482, l.533);
- the global time function, where global hyperbolicity is available;
- `\bibitem{Le2026}` (l.605–608), which cites arXiv:2605.25417 without a
  version. That identifier is Le's boundary-cost paper only in v1 and v2; v3
  (17 Sep) is a different paper.

The disclosure is updated when its author asks for it.

## Literature that bears on the rail

- **The lapse lever is published.** Shoshany and Snodgrass (2024, §4.2)
  describe a large lapse where the shift gradient is large as a way to shrink
  the Eulerian energy, at a time-stretch of the source matter of order the
  lapse.
- **Barzegar, Buchert and Vigneron (2026, Thm IV.7)** state that a switched-on
  superluminal model cannot be globally hyperbolic. That conflicts with the
  bounded-field result above, and the verifier traces the proof to the
  premise that global hyperbolicity excludes horizons, which the Kruskal
  extension contradicts. The theorem is recorded as disputed until its
  definitions are read in full.
- **Version hazards:**
  - arXiv:2605.25417 changed paper in v3;
  - arXiv:2606.22531 was retitled in v4;
  - arXiv:2603.21352 replaced its warp claim in v3.

  The bibliography in the data folder pins every arXiv entry to a version
  and records these notes.
- **A coefficient conflict.** Graham and Olum (2007) give 1/(2880π²) for the
  anomalous-scaling coefficient, and Kontou gives 1/(1920π²). The
  first-principles value c/16π² equals 1/(1920π²).

## Process observations

- **The first gate verdict was bypassed.** The 8 September verdict, internal
  closure failure, was the handoff's condition for redesign. The source
  inversion ran eleven hours later, and 183 commits followed through 17
  September, most of them source work on a static slice of the failed
  geometry. The rule sat in a user-supplied
  handoff that entered the repository only on 16 September.
- **The same verdict left the disclosure within hours.** Commit `921e560`
  wrote it into the disclosure at 16:59 on 9 September, and `734156c`
  ("Remove source-trial narratives") replaced it with a conditional
  requirement at 20:31. `plan.md` first records Type IV on 23 September.
- **A negative-results ledger kept beside the disclosure would preserve such
  verdicts.** It would record failed necessary conditions and every relaxed
  criterion, while the disclosure keeps holding only locked design elements.
- **One solver setting was never tested.** The HiGHS runs in
  `graded_electrothermal.py` keep the default small-coefficient threshold
  of 10⁻⁹, and the earlier GRADED runs were not repeated at 10⁻¹².

## Open items

- **Untested design responses:**
  - the quantum-inequality source test on the compartment, cone, trimmed,
    speed-scaled and deficit-minimized designs;
  - passenger temperature at clock rates other than 1;
  - the shift-transition radius in flat-slice designs.
- **The Type I gate against the algebraic range of kinetic-braiding scalars.**
- **The harness's smeared-null floor.** It may be 8π looser than the
  published form, per a throat-era reading that has not been verified.
- **The packet-safety cliffs of the May throat-era freeze** (w_th 0.569/0.570
  and V ≈ 10.01) sit at single mask-edge grid nodes. This is a
  reconstruction in the inventory, outside any report.

## Reproduction

```bash
cd supporting_reports/data/evidence_review/verification
python3 v1_flat_slice_class.py
python3 v2_spherical_class.py
python3 v3_moving_patterns.py
python3 v4_source_physics.py
```

The scripts need sympy and mpmath, and each run's log sits beside its script.
