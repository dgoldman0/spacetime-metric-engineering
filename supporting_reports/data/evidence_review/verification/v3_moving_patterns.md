# V3. Moving patterns: pattern-frame kinematics (I12–I17, I19, I20)

Verification record for the textbook, 2026-09-26.

- Script: `v3_moving_patterns.py` (sympy derivations plus scipy geodesic integration).
- Numbers: `v3_moving_patterns_results.json`; run log: `v3_run.log`.
- Run: `nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 v3_moving_patterns.py`
  (one process, about 20 s). Two consecutive runs give a bit-identical JSON file.
- Outcome: 75 of 75 checks pass. Check labels (S = symbolic, N = numerical) are quoted
  below; each appears verbatim in the log.

The script is written from scratch. The repository reports were read only for the exact
wording of the statements (FRONT_LIGHT_SURFACE_PASS.md "Why the front gathers what it
overtakes" and "The two front elements"; CONE_TIP_FIELD_PASS.md "Horizons of the moving
pattern"; QUANTUM_ESTIMATES_PASS.md "Rear horizon"; GEOMETRY_CLOSURE_PASS.md "The cone at
speed" and the cavity paragraph; CHOREOGRAPHY_PASS.md lines 152–191; COMPARTMENT_PASS.md
"Placement"). Literature statements come from the saved texts in `lit_pdfs/`.

---

## 0. Setting, conventions and the pattern-frame mapping

**Book convention (05_STRUCTURE.md).** The lab metric of class C0 is

  ds² = −α² dσ² + (dz + β dσ)² + dx² + dy²  (equivalently dr² + r² dφ² transversely).

The Eulerian observer n = (∂_σ − β∂_z)/α moves at dz/dσ = −β, so a carriage moving at +v has
β = −v.

**Steady lane.** α and β depend on σ only through ζ = z − vσ, with v constant. Since
dz + β dσ = dζ + (β + v) dσ, the pattern-frame metric is

  ds² = −α² dσ² + (dζ + b dσ)² + dx² + dy²,  b = β + v.

The report's b = β + v is therefore the book's convention, with no sign change. The mapping is:

| Region | lab shift β | pattern-frame shift b |
|---|---|---|
| carried region (the packet rests on the Eulerian observers) | −v | 0 |
| shift-free regions: exterior, lapse falls, front elements | 0 | v |

σ is the same coordinate in both frames: the proper time of static exterior observers
(α = 1, β = 0). The slices σ = const, the Eulerian observers n and the extrinsic curvature
K_ij are the same in both frames. The pattern frame's time translation

  ξ = ∂_σ|_ζ = ∂_σ|_z + v ∂_z

is a Killing vector (S1.1). Its norm is g(ξ,ξ) = b² − α², so ξ is timelike only where α > |b|.
For v > 1 it is spacelike throughout the exterior. The reports call the pattern-frame metric
"stationary" in the sense of ξ-invariance; Natário 2002 §3 reserves the word for a timelike
Killing vector ("such spacetime can only be stationary if |v_s| < 1").

**Definition of k.** k is the spatial part of the 4-momentum on the σ-slices,
k_i = γ_i^μ p_μ = p_i: the momentum measured by the Eulerian observers. With flat slices in
Cartesian coordinates k^i = k_i. Their measured energy is E_n = −n·p = √(m² + |k|²), and
k_ζ = p_ζ = p_z.

**Numerical method.**
- Test patterns are defined in the lab frame with fields depending on z − vσ. Every step
  function is C^∞ with compact support, so "exterior" means α = 1 and β = 0 exactly.
- Geodesics are integrated in Eulerian variables (x^i, k_i) with E_n = √(m² + |k|²):
  dx^i/dσ = αk^i/E_n − β^i and dk_i/dσ = k_z ∂_iβ − E_n ∂_iα. S1.3 derives these equations
  symbolically from H = ½ g^{μν}p_μp_ν.
- Integrator: DOP853 at rtol 1e-11 to 1e-13, with the step capped at 0.05 (0.02 for the tip
  and rear-horizon runs).

Two practices for the book's verification chapter came out of building the engine:

1. In the phase-space form (p_σ, p_i), the Killing energy E = −p_σ − v p_z is a linear
   invariant of the equations. Every Runge–Kutta step preserves linear invariants exactly, so
   E-conservation in that form tests nothing. In Eulerian variables E = αE_n − b k_z is
   nonlinear in the state, and its conservation measures accuracy. An early version conserved
   E to rounding while violating the null condition by order one.
2. Across the exactly flat exterior the error estimate is zero, so an uncapped step grows until
   it jumps over a thin layer. A step cap below the layer width removes the problem.

**Test patterns.**

| Label | Pattern | Used for |
|---|---|---|
| P1 | flat front, v = 2: shift-free, ln α = ln 4 · W(ζ) · W(r); front fall centred at ζ = 3 and rear fall at ζ = −6, both flat for r ≤ 4.9, κ = ln 2 at both | κ, horizons (N4, N5.4) |
| P2 | cone of half-angle 15°, shift-free: tip rounded over 0.5, layer half-width 1, base at ζ = 0; interior log-lapse L_c = 1.5 + ln(v/2.1) (the reports' speed scaling); v = 2.1, 3, 5 | exit-angle law, flank, tip (N2, N4.4, N5) |
| P3 | static shelf α_s = e for z < 78.5, falling to 1 across 78.5–81.5 (a resting lapse step); a shift-free bump α_s e^{W} moves through it at v = 2.1 | shelf law (N3) |
| P4 | static optics: planar step α 1 → 5; spherical walls at R = 3 of half-width 1 and 2 | cavity (N7) |
| P5 | carried pattern, v = 2.1: β = −v in a core (flat for \|ζ\| ≤ 0.5, r ≤ 0.89; support \|ζ\| < 2.5, r < 2.68) inside a lapse plateau α = 3 (flat for \|ζ\| ≤ 2.5, r ≤ 3.07), falling to 1 by \|ζ\| = 5.5, r = 5.57; also a non-steady variant with the plateau height ramped in σ | Killing energy, gain laws, ordering (N1, N8) |
| — | planar lapse layer at 15° moving at v along z (α from 1 to 10) | flank criterion (N6) |

---

## 1. I12 part one: Killing energy, Eulerian rate law, kept gain

### Statements with hypotheses

**(a) Killing energy.** During a steady lane, every geodesic (light m = 0, matter m > 0)
conserves

  E = −p·ξ = α √(m² + |k|²) − b k_ζ,  b = β + v,

with k the Eulerian spatial momentum defined in §0.

**(b) Eulerian rate law.** On flat static slices, along any geodesic, for any time dependence of
α and β:

  dE_n/dσ = k_z (k·∇β)/E_n − k·∇α.

For light (E_n = |k|) this reads d ln|k|/dσ = k̂_z (k̂·∇β) − k̂·∇α. Wherever the shift is locally
uniform (in particular where the lab shift vanishes), d ln|k|/dσ = −k̂·∇α.

**(c) Lapse-weighted energy.** Along any geodesic,

  d ln(α E_n)/dσ = (∂_σ − β∂_z) ln α + k_z (k·∇β)/E_n².

In a steady lane, (∂_σ − β∂_z) ln α = −b ∂_ζ ln α. Where the lab shift vanishes, b = v and the
shear term drops. On a path lying entirely in that region,

  α_f|k_f| / (α_i|k_i|) = exp( v ∫ (−∂_ζ ln α) dσ ),

which is the kept gain for light that starts and ends in the exterior (α = 1 at both ends).

### Method

- Symbolic:
  - S1.1: the Lie derivative of the lab metric along ξ = ∂_σ + v∂_z vanishes for
    α(z − vσ, x, y), β(z − vσ, x, y).
  - S1.2, S1.2b: E = αE_n − b k_z, and dE/dσ = 0 along Hamilton's equations.
  - S1.3–S1.6: the rate law and the αE_n identity, for arbitrary α(σ, x, y, z),
    β(σ, x, y, z).
- Numerical (N1):
  - Seven geodesics on P5: light forward, backward and oblique; matter at rest; on and off the
    axis.
  - Three geodesics on the non-steady variant of P5.

### RESULT: VERIFIED WITH ADDED HYPOTHESES

**(a) VERIFIED.** The largest drift of E on the seven geodesics is 1.3e-11 relative to αE_n.
Forward light and matter held at the front's null disk for 14 time units gain factors of 1.6e4
and 8.7e4, and E drifts there by at most 6.4e-13.

**(b) VERIFIED, in a wider form.** The pure-lapse law needs only k̂_z (k̂·∇β) = 0 along the ray,
which holds for any locally uniform shift. In particular it holds in the carried region as well
as where the lab shift vanishes.

**(c) Kept gain: exact on shift-free paths, with an added hypothesis.**
- On paths that stay where the lab shift vanishes, the formula is exact:
  - forward light at r = 4.3: gain 3.4239, formula error 1e-12;
  - backward light at r = 4.3: gain 1.4670, formula error 2e-12;
  - all 36 cone exits of §2 (P2 is shift-free), with |ln G − v∫(−∂_ζ ln α)dσ| ≤ 1.2e-10.
- Counterexample: an oblique ray through the shift core (|β| up to 0.82) misses the pure formula
  by 6.1%. The full identity with the shear term holds on it to 2.7e-12. The head-on axial ray
  through the core satisfies the pure formula only because P5 is front–back symmetric.
- On the non-steady variant the general identity (c) holds to 1.1e-12, while E changes by 17%
  to 400%.

Corrected statement of the kept gain:

> For light whose whole path lies where the lab shift vanishes during a steady lane, α|k| changes
> by exp(v∫(−∂_ζ ln α)dσ). For light that starts and ends in the exterior this factor is the kept
> gain. On any other path, ln(α|k|) changes by ∫[−b ∂_ζ ln α + k̂_z (k̂·∇β)] dσ in a steady
> lane, and by ∫[(∂_σ − β∂_z) ln α + k̂_z (k̂·∇β)] dσ in general.

### Derivation sketch (book proof)

1. **Conservation.** The pattern-frame components do not depend on σ, so ξ = ∂_σ|_ζ is Killing.
   Along a geodesic, d(p·ξ)/dλ = p^μ p^ν ∇_μ ξ_ν = 0 by Killing's equation.
2. **3+1 form of E.** In pattern coordinates αn = ∂_σ − b∂_ζ, so ξ = αn + b∂_ζ. Hence
   −p·ξ = α(−n·p) − b p_ζ = αE_n − b k_ζ.
3. **Rate law.** For the Eulerian congruence, ∇_μ n_ν = −K_μν − n_μ a_ν, with a = D ln α and
   K_ij = (∂_iβ_j + ∂_jβ_i)/2α on static flat slices. Along a geodesic,
   dE_n/dλ = −p^μ p^ν ∇_μ n_ν = k^i k^j K_ij − E_n k^i ∂_i ln α. With dσ/dλ = E_n/α this gives (b).
4. **Lapse-weighted energy.** Along the geodesic, dα/dσ = ∂_σα + (αk^i/E_n − β^i) ∂_iα. Adding
   d ln E_n/dσ cancels the k·∇α terms and leaves (c).
5. **Steady lane.** ∂_σα = −v ∂_ζα turns (∂_σ − β∂_z) ln α into −b ∂_ζ ln α. Where β ≡ 0 this
   is −v ∂_ζ ln α and the shear term vanishes.

### Literature

(a) with α = 1 is established physics, in three unit-lapse forms:
- Natário 2002 §3: E(1 + X·n) = E₀ for the Eulerian energy E, with X = −b the flow.
- Clark, Hiscock & Larson 1999 eqs. (24)–(26): conserved p_t, and E₀/E_∞ = 1 ± v for axial
  photons at the bridge.
- McMonigal, Lewis & O'Byrne 2012 eq. (15): b = 1 − v_s v_p.

Three pieces generalize these results to a lapse: the α√(m² + k²) term, the rate law (b) with its
shear term, and the lapse-weighted identity (c). None of them appears in the papers read.

---

## 2. I12 part two: exit-angle law and shelf law

### 2a. Exit-angle law

**Statement (precise).** Take a steady lane with v > 1 and light that:
- starts in the flat exterior moving along the pattern's direction of motion (+z);
- is overtaken by the pattern;
- returns to the flat exterior before the lane ends.

It leaves with

  |k_f| / |k_i| = (v − 1)/(v cos θ_f − 1).

θ_f is the angle between the light's final direction of propagation and +z, measured by static
exterior observers (in the exterior, k̂ is the lab-frame direction of motion). For an arbitrary
initial direction the law is (1 − v cos θ_i)/(1 − v cos θ_f).

Since E = |k_i|(1 − v) < 0, the exit direction lies in the cone cos θ_f > 1/v. The gain is at
least 1, equals 1 only at θ_f = 0, and grows without bound as θ_f → arccos(1/v).

**Lemma (overtaken light and the carried region).** Where α > |b|, ξ is future-directed timelike,
and every future-directed momentum has E = αE_n − b k_ζ ≥ (α − |b|) E_n > 0. Light the pattern
overtakes has E < 0, so it never enters a region where α > |b|. The carried region (b = 0)
belongs to that set.

**Method.** S2.1 (symbolic). N2: 36 overtaken rays on the cone P2 at v = 2.1, 3 and 5, launched
on 12 radii from 0.02 to 7. N1 adds four exterior-to-exterior rays on P5.

**RESULT: VERIFIED WITH ADDED HYPOTHESIS.** The exit, and the overtaking with it, must fall within
the steady lane; the light starts in the flat exterior moving along +z; θ_f is as defined above.

- The residual |G(v cos θ_f − 1) − (v − 1)|/(Gv) is at most 1.3e-11 on all 36 exits.
- Exit angles stay inside the bound arccos(1/v):

| v | exit angle range | bound arccos(1/v) |
|---|---|---|
| 2.1 | 31.3°–56.0° | 61.56° |
| 3 | 48.1°–68.6° | 70.53° |
| 5 | 46.6°–78.46296° | 78.46304° |

- The gain itself is ill-conditioned near cos θ_f = 1/v, since d ln G/dθ_f = vG sin θ_f/(v − 1).
  At gains of 6e5, reconstructing G from θ_f loses 4e-7 relative accuracy, while the residual
  stays at 1e-11. The residual form is the right numerical test.

**Derivation sketch.** Conserve E between two exterior states, where α = 1, b = v and
E = |k|(1 − v cos θ). For the lemma, use |k_ζ| ≤ E_n.

**Literature.**
- The bound cos θ_f = 1/v is the edge of the rear cap of Clark, Hiscock & Larson 1999: a conical
  region behind the ship "from within which no signal can reach the starship", forming at v = 1
  and widening toward 90° as v grows. The lemma explains the edge: those sources send light with
  negative Killing energy, which never reaches a region where ξ is timelike.
- arccos(1/v) is the direction normal to the Mach cone sin θ_M = 1/v of Natário 2002 §3. Light
  propagating along that normal keeps pace with the cone, which is why the gain diverges there.
- McMonigal et al.'s "time locked" particles overtaken from ahead (region P+) sit on the axis of a
  front with a null light surface. On a cone the same class exits with the finite gain above.

### 2b. Shelf law

**Statement (with added hypotheses).**
- *Setting.* A region ahead of the pattern holds a uniform lapse α_s > v with zero lab shift (the
  forward shelf). Along the particle's path, the pattern's lapse rises to at least √(α_s² + v²)
  where the lab shift vanishes. This condition suffices for reflection.
- *Reflection.* Matter at rest in the shelf (E = α_s m) turns in the pattern frame where
  α = √(α_s² + v²). It leaves forward along the axis with Lorentz factor, relative to the shelf's
  static observers,

  γ′ = (α_s² + v²)/(α_s² − v²).

  Leaving at angle θ′ to the axis inside the shelf, it has
  γ′ = (α_s² + v² cos²θ′)/(α_s² − v² cos²θ′), which is smaller.
- *Terminal.* If the particle then crosses a lapse step from α_s to 1 that is static while it is
  crossed (a resting terminal), it enters the flat exterior with γ = α_s γ′.

**Method.** S2.2–S2.6 (symbolic). N3: a one-dimensional run through the moving bump in P3,
followed by the resting terminal.

**RESULT: VERIFIED WITH ADDED HYPOTHESES** (reflection condition, axial exit, static terminal).

| Quantity | measured | law |
|---|---|---|
| γ′ in the shelf | 3.9606693218 | 3.9606693218 |
| lapse at the turning point | 3.43498 | √(e² + 2.1²) = 3.43498 |
| γ after the terminal | 10.766215446 | α_s γ′ = 10.766215446 |

- The bump's front edge stays at z ≤ 69.52 while the particle crosses the terminal (78.5–81.5), so
  the terminal is static during the crossing.
- The report's numbers are reproduced: 3.96 and 10.77. So is the running leading edge's light gain
  (u − 1)/(u − α_s) = 3.198 at u = 3.5 (S2.6).

**Derivation sketch.**
1. *Moving-mirror reading.* In the shelf the metric −α_s² dσ² + dz² is flat with light speed α_s.
   With t′ = α_s σ, the pattern is a reflector moving at u = v/α_s < 1.
2. *Reflection.* E-conservation gives α_s γ′ − v √(γ′² − 1) = α_s, with roots 1 and
   (α_s² + v²)/(α_s² − v²). The second is the relativistic mirror formula (1 + u²)/(1 − u²)
   (S2.4).
3. *Turning point.* At pattern-frame rest the Eulerian velocity is v/α, so E = m √(α² − v²).
4. *Terminal.* In a static, shift-free region identity (c) gives d ln(αE_n)/dσ = ∂_σ ln α = 0.
   Hence αE_n is conserved and γ_f = α_s γ′.

**Literature.** None of the papers read contains a lapse version of this law. Its content is the
reflection law of a mirror moving at v/α_s, derived here from E-conservation.

---

## 3. I13: light surface, Killing horizon, surface gravity

### Statement (corrected)

**Setting.** The pattern-frame metric is ξ-invariant, with α(ζ, r, φ) and b(ζ, r, φ), and the
shift points along ζ. On S = {α² = b²} the Killing vector ξ is null. With F = α² − b²,

  g^{μν} ∂_μF ∂_νF = (1 − b²/α²) F_ζ² + F_r² + F_φ²/r²,

which on S reduces to F_r² + F_φ²/r².

**Causal character.** At each point of S with dF ≠ 0, S is null if and only if its transverse
gradient (F_r, F_φ) vanishes there, and timelike (crossable in both directions) otherwise.

**Killing horizon.** On an open portion of S where the transverse gradient vanishes identically
(a disk), ξ is null, tangent and normal to S, so that portion is a Killing horizon of ξ. Its
surface gravity, from ξ^ν ∇_ν ξ^μ = κ ξ^μ, is

  κ = ∂_ζ(α − |b|) on S (signed);  |κ| = |∂_ζ(α − |b|)|.

- Where the lab shift vanishes (b = v) this reduces to κ = ∂_ζα.
- The sign distinguishes the two types:

| Horizon type | lapse along +ζ | sign of κ |
|---|---|---|
| white-hole | falls through v | negative |
| black-hole | rises through v | positive |

**Normalization.** κ is defined with ξ = ∂_σ|_ζ, where σ is the proper time of static exterior
observers. Since ξ is spacelike in the exterior when v > 1, the usual normalization to unit norm
at infinity is unavailable, and the exterior-time normalization is the natural one. Rescaling
ξ → cξ gives κ → cκ.

**Isolated null points.** Where the transverse gradient vanishes at an isolated point, such as the
tip of a lapse cone on the axis, S is null at that point only and carries no Killing horizon.
These points are the rest points of the ray flow (step 5 below).

### Method

- Symbolic:
  - S3.0–S3.2: inverse metric; norm of dF on S; ξ normal to S exactly when F_⊥ = 0.
  - S3.3–S3.6: κ from the Christoffel symbols (ξ^ν∇_νξ^μ = κξ^μ with a^ζ = 0 on S) and from
    κ² = −½ (∇ξ)².
  - S3.7: the unified null-surface criterion.
  - S3.8–S3.9: rest points of the pattern-frame ray flow.
- Numerical (N4 on P1 and P2; N5.4).

### RESULT: VERIFIED WITH CORRECTED HYPOTHESES

The Killing horizon occupies only open null portions of S. For a general b, κ = ∂_ζ(α − |b|), with
ξ normalized to exterior time.

- **Flat front P1** (κ = |∂_ζα| = ln 2 = 0.693147):
  - *Held light.* Forward light on the disk, launched from behind at r = 0, 2 and 4 and overtaken
    from ahead at r = 2, is held at S. It gains at 0.693147 over the last 4 time units and
    approaches S at 0.69315. Rates measured in lab time equal κ, which confirms the
    normalization.
  - *Beyond the disk.* At r = 5.8, outside the flat disk, S is timelike and the ray leaves with a
    finite gain of 3.16.
  - *Rear fall (black-hole type).* Light started 1e-7 ahead of or behind S leaves it at
    0.69316 / 0.69314 and redshifts at −0.69317 / −0.69313.
- **Cone P2 at v = 2.1.** On S, the ratio |∂_rα|/|∂_ζα| is 0 on the axis, 1.67 at r = 0.25,
  2.64 at 0.5 and 3.34 at 1, rising to 3.71 at r = 5 (cot 15° = 3.73). S is null only on the axis.
- **Energy density at the flat front.** A geometric-optics bundle held there grows in energy
  density at 1.38648, against 2κ = 1.38629 (N5.4).

### Derivation sketch (book proof)

1. **Normal norm.** The pattern-frame inverse metric has g^{σσ} = −1/α², g^{σζ} = b/α²,
   g^{ζζ} = 1 − b²/α², and unit transverse components. For a σ-independent F,
   g^{μν}F_μF_ν = |∇F|² − (b·∇F)²/α². On S, (b·∇F)² = α²F_ζ², which leaves F_r² + F_φ²/r².
2. **Killing normal.** ξ_μ = g_{μσ} = (b² − α², b, 0, 0), which becomes (0, b, 0, 0) on S. This is
   proportional to dF exactly when F_r = F_φ = 0.
3. **Surface gravity.** For a Killing vector, ξ^ν ∇_ν ξ_μ = −½ ∂_μ(ξ·ξ) = ½ ∂_μF. On the null
   portion dF = F_ζ dζ and ξ_μ = b dζ, so ξ^ν∇_νξ_μ = (F_ζ/2b) ξ_μ. Hence κ = F_ζ/2b
   = (αα_ζ − bb_ζ)/b = ∂_ζ(α − b) at α = b > 0.
4. **Stationary null-surface criterion (S3.7).** A σ-independent surface with unit normal N in the
   flat slice is null iff |b·N| = α, timelike iff |b·N| < α, and spacelike iff |b·N| > α. I13,
   Natário's horizon and the flank criterion I15 (§5) are three uses of this one criterion.
5. **Rest-point lemma (S3.8–S3.9).** A light ray is at rest in the pattern frame exactly when it
   sits on S moving along b. Its direction stays fixed only where ∂_⊥(α − |b|) = 0, that is, at the
   null points of S. There its momentum changes at the rate −κ_signed: the blueshift at a
   white-hole point, the redshift at a black-hole point.

### Literature

**Natário 2002 §3.** For a stationary bubble with v_s > 1, the surface through the axis point
where ‖X‖ = 1 "whose angle α with X is given by sin α = 1/‖X‖ is a horizon, in the sense that
events inside the warp bubble cannot causally influence events on the other side of this surface".
Far from the bubble, sin α = 1/v_s is "the familiar expression for the Mach cone angle".
- With unit lapse and b = |X|, sin α = 1/|X| is exactly |b·N| = α. Natário's horizon is the
  stationary null surface (a causal boundary) that step 4 builds through the axis point where S is
  null.
- Away from that point it lies where |b| > α and ξ is spacelike. In the flat exterior it becomes
  the Mach cone.
- S itself (|X| = 1) is timelike away from the axis.

**Natário and I13 are different statements with a common root.** I13 concerns the Killing surface
S and where it is null. Natário concerns the causal horizon of the bubble's interior. The two
surfaces meet at the null points of S.

**Barceló et al. 2022 §III B** (unit lapse, 2+1, stationary): "the only points on the boundary of
the bubble v = 1 which have the possibility of generating Cauchy horizons are the ones where
∂_y v = ζ = 0". Their ζ is the label for ∂_y v at the point, unrelated to the pattern coordinate
used here.
- Their boundary v = 1 is S at α = 1, and ∂_y v = 0 is the vanishing of the transverse gradient
  of F = 1 − v². **The two criteria select the same points.**
- The claims differ in kind. Barceló et al. derive, from the geodesic equations and analyticity,
  where infinite blueshift can occur. I13 states the causal character of S, for any lapse.
- The rest-point lemma links them: in a stationary pattern, a light ray can come to rest in
  position and direction only at the null points of S. Their flat-front case (a finite region with
  ∂_y v = 0, eq. (17)) is I13's Killing-horizon disk.

**Finazzi, Liberati & Barceló 2009.**
- *Surface gravity (eq. (13)).* The signed surface gravity is κ_{1,2} = dv/dr at the horizons of
  −c²dt² + [dr − v̄ dt]², with t the exterior time: positive at the black horizon, negative at the
  white one. This is κ = ∂_ζ(α − |b|) at α = 1, with the same normalization and sign.
- *White-horizon growth (eqs. (83)–(87)).* The renormalized stress grows near the white horizon as
  e^{2κt}. The e^{2κt} consequence quoted under I13 in the inventory is this 1+1 result. N5.4
  reproduces the 2κ exponent for classical geometric-optics packets.

---

## 4. I14: tip shedding rate

### Statement

**Setting.** A shift-free (b = v), axisymmetric front whose light surface S reaches the axis at a
tip where:
- α = v and ∂_ζα = −κ < 0;
- α_r = 0 on the axis;
- A ≡ −∂_r²α > 0 at the tip.

**Linearized dynamics.** For rays near the axial ray, to linear order (and the same in y):

  δζ̇ = −κ δζ,  ẋ = v u_x,  u̇_x = A x − κ u_x.

- The axial ray converges to the tip at rate κ, and its energy per quantum grows at κ.
- Off-axis displacements grow at

  λ = ½ (√(κ² + 4vA) − κ).

  The other root, −½(√(κ² + 4vA) + κ), is the separatrix into the tip.

**Density law.** A geometric-optics wave packet riding the axial ray changes its energy density
(Eulerian energy per quantum divided by the ray-bundle volume, photon number conserved) at

  2(κ − λ).

The rate collects three pieces:
- +κ from the blueshift;
- +κ from compression along the axis;
- −2λ from transverse spreading in two directions.

On a flat front (A = 0) the rate is 2κ.

### Method

- Symbolic (S4.1–S4.5):
  - the reduced ray equations, derived from the pattern-frame Hamiltonian;
  - the Jacobian at the fixed point and its characteristic polynomial,
    −(κ + λ)(vA − κλ − λ²)²;
  - the dictionary with Barceló et al.
- Numerical (N5):
  - P2 at v = 2.1, whose tip has κ = 0.407734, A = 3.04337, λ = 2.332397;
  - ray pairs displaced by 1e-7 and a four-ray bundle, fitted over σ ∈ [2.2, 5.2];
  - the same bundle on the flat front P1 (N5.4).

### RESULT

**λ: VERIFIED (derived).** λ is the paraxial ray exponent, exact for the linearized ray flow.
- Transverse growth measures 2.3374 against 2.3324 (0.2%).
- Energy growth and axial convergence both measure 0.40860 against 0.40773 (0.2%).
- The report's numbers are reproduced: λ(κ = 0.563, A = 4.20, v = 2.1) = 2.702 and
  2(κ − λ) = −4.277, against the stated 2.70 and −4.3.

**Density law 2(κ − λ): ESTIMATE.**
- *Exact within geometric optics.* For the ray bundle the law holds: −3.8577 measured against
  −3.8493 (0.2%); on the flat front 1.38648 against 2κ = 1.38629.
- *Estimate for fields.* As a statement about field-mode energy density, and about renormalized
  quantum stress, it is an estimate. It is valid under these conditions:

1. **Geometric optics.** The wavelength must be much smaller than the tip scale (here the
   rounding ε). The condition improves as the packet blueshifts, provided the packet's transverse
   width stays much larger than its wavelength.
2. **Paraxial window.** The rays must stay where α is quadratic in r (roughly within the tip
   rounding). This holds for σ ≲ λ⁻¹ ln(ℓ_⊥/w₀), with w₀ the initial packet width and ℓ_⊥ that
   transverse scale.
3. **Transients.** The rate applies after about 1/|λ₋| (0.36 here), once the separatrix mode has
   decayed.
4. **Setting.** The lane must be steady, the lab shift zero near the tip, and the lapse a regular
   maximum on the axis (∂_r²α < 0). For a lapse minimum on the axis (∂_r²α > 0) the transverse
   modes decay and the exponent exceeds 2κ, matching Barceló et al.'s remark that a concave peak
   makes the instability greater.
5. **Scope of the quantity.** Photon number is conserved (the adiabatic invariant of geometric
   optics), and density is measured by Eulerian observers for classical packets. The step to the
   vacuum stress of a quantum field (a sum over all modes, renormalized) is heuristic.

### Derivation sketch

1. **Hamiltonian.** In the pattern frame, H = ½[−(E + v p_ζ)²/α² + |p|²].
2. **Ray equations.** In σ, with u = p/|p|:
   - dx^i/dσ = α u^i − v δ^i_ζ;
   - du/dσ = −∇α + u(u·∇α);
   - d ln|p|/dσ = −u·∇α.
3. **Paraxial model.** Insert α ≈ v − κ δζ − ½A(x² + y²). The mixed derivative ∂_r∂_ζα vanishes
   on the axis by symmetry.
4. **Linearize** at (δζ, x, y, u_x, u_y) = 0. Each transverse direction gives the block
   [[0, v], [A, −κ]], and the ζ direction gives −κ.
5. **Eigenvalues.** They solve λ² + κλ − vA = 0.

### Literature

**Barceló et al. 2022 eqs. (11), (14), (18)–(19).** With v(x, y) ≈ 1 + κ(x − x₁) + ξy²,
transverse deviations obey y″ + κy′ − 2ξy = 0 and grow at η₋ = (κ/2)(√(1 + 8ξ/κ²) − 1).
- With ξ = vA/2 this is λ (S4.5).
- In units where the tip's light speed is one (σ′ = vσ), the lapse front's b/α
  ≈ 1 + (κ/v)δζ + (A/2v) r² plays the role of their v(x, y). Converting back to σ multiplies the
  rates by v and gives λ.

**The density rate is new with the project.** Barceló et al. estimate the vacuum-energy profile
near the tip from the deflection time t_def = η₋⁻¹ log(y_def/y₀), a logarithmic profile. The
2(κ − λ) exponent is the project's own geometric-optics estimate; their paper does not contain it.

---

## 5. I15: flank criterion

### Statement (with added hypotheses)

**Setting.** A lapse layer moves with the pattern at v through a region where the lab shift
vanishes. The normal N of its level surfaces makes angle θ_c with the radius (N·e_z = sin θ_c).

**Null level.** Each level surface moves along its normal at v sin θ_c. The level α = a is:
- null exactly when a = v sin θ_c;
- timelike when a > v sin θ_c;
- spacelike when a < v sin θ_c.

**Held light.** Suppose the layer holds every lapse from 1 to α_in, with 1 < v sin θ_c < α_in.
- Light moving along the normal is then held at the level α = v sin θ_c and blueshifts there at
  |∂_nα|.
- For a planar layer this level is exactly a Killing horizon of the layer's normal Killing field.

**Escaping light.** If v sin θ_c < 1, no level is null, and light moving along the normal leaves
the layer with a finite gain.

**Scope.** For a curved flank (a cone) the statement is local. It holds where the flank's
curvature radius and the along-flank variation of the lapse are large compared with the layer
width. At the cone's tip the normal is the axis, and I14 applies.

**Mach cone.** v sin θ_c = 1 is θ_c = arcsin(1/v) = θ_M. The criterion v sin θ_c < 1 says that
the front's flank lies inside the Mach cone of its own speed.

### Method

- Symbolic: S5.1–S5.3.
- N6: a planar layer at 15°, α from 1 to 10, at v = 5 and 2.1.
- N2: the cone P2 at v = 2.1, 3 and 5, which brackets the threshold 1/sin 15° = 3.864.

### RESULT: VERIFIED WITH ADDED HYPOTHESES

The hypotheses: a shift-free layer, α_in > v sin θ_c, exact for planar layers, local for curved
ones.

**Planar layer.**
- At v = 5, light launched along N inside the layer is held at α = 1.2940952255, which equals
  v sin θ_c to 2e-12. It gains at 2.2481191, which equals |∂_nα| there to 4e-10.
- At v = 2.1, light along the normal leaves with gains 12.360273 and 3.611808. These equal
  (α₀ − u)/(1 − u) with u = v sin θ_c = 0.5435.

**Cone.**

| v | v sin θ_c | largest gain |
|---|---|---|
| 2.1 | 0.54 | 6.29 |
| 3 | 0.78 | 21.0 |
| 5 | 1.29 | 5.8e5 |

The rays above the threshold (v = 5) ride the flank:
- Before reaching the base they settle at α = 1.2983 (v sin θ_c = 1.2941), moving at 74.95° to
  the axis (the flank normal is at 75°), with pattern-frame normal speed 0.0042.
- They blueshift at 2.31 per unit time while riding.
- They exit at 78.463° = arccos(1/5), the Mach-cone normal, which is the direction where the
  exit-angle law diverges.

### Derivation sketch

1. **Planar reduction.** A planar layer α(N·x − vσN_z) is the same metric as a layer moving along
   N at u = v sin θ_c, because tangential translations are symmetries.
2. **Null level.** In the frame moving along N, the metric is Killing-invariant with shift u. By
   the null-surface criterion (§3, step 4), the level α = u is null.
3. **Held light.** For light moving along N, the pattern-frame normal velocity is α − u. It
   vanishes at the level α = u, is positive inside (α > u) and negative outside. The level
   therefore attracts normal light (white-hole type).
4. **Blueshift.** There d ln|k|/dσ = −N·∇α = |∂_nα|.

### Literature

- Natário 2002 §3: in the exterior the horizon is the Mach cone sin α = 1/v_s.
- Clark, Hiscock & Larson 1999: conical horizon-like regions "somewhat analogous to the Mach cones
  associated with supersonic fluid flow".
- In these terms, the flank criterion keeps a lapse front inside the Mach cone of its own speed,
  which keeps its flank timelike in the exterior.

---

## 6. I16: lapse cavity

### Statement (corrected)

**Setting.** The region is static in the pattern frame, which requires the pattern-frame shift
b = 0 (the lab shift equals −v; a merely uniform lab shift does not suffice). The slices are flat.

**Optics.** Light rays there are geodesics of the optical metric δ_ij/α², so the refractive index
is 1/α, and E = α|k| is conserved. Light passing from lapse α_in into α_out obeys Snell's law,

  sin ψ_out = (α_out/α_in) sin ψ_in.

**Total reflection.** The direction matters:
- For α_in < α_out, the light is totally reflected when sin ψ_in > α_in/α_out; it escapes only
  within arcsin(α_in/α_out) of the normal.
- For α_in ≥ α_out it is always transmitted.

**Exactly when.** The arcsin rule is exact in these cases:
- *Planar layers of any monotone profile.* For a non-monotone layer, replace α_out by the largest
  lapse on the path.
- *A z-independent cylindrical boundary crossed by rays that meet its axis.* k_z is conserved,
  and the light escapes within arcsin(α_in/α_out) of the transverse plane.

For a spherical boundary the exact condition is L/E ≤ min r/α(r) over the outward path, with L the
conserved angular momentum. This reduces to the arcsin rule only for a wall that is thin compared
with its radius.

### Method

- Symbolic: S6.1–S6.3.
- N7:
  - a planar step 1 → 5, in both directions;
  - spherical walls of half-width 1 and 2 at R = 3.

### RESULT: VERIFIED WITH CORRECTED HYPOTHESES

The hypotheses: b = 0; α_in < α_out for total reflection; exact scope as stated above.

**Planar step (threshold 11.537°).**
- Rays at 11.0° and 11.4° are transmitted; rays at 11.7°, 12.5° and 30° are reflected.
- Transmitted angles follow Snell's law to within 2e-9 degrees.
- In the reverse direction (5 → 1), rays at 30°, 60° and 85° are all transmitted.

**Spherical wall, half-width 1.** The exact threshold is L* = 0.767, against 0.6 from the
thin-wall rule.
- A ray with L = 0.744 escapes, although the thin-wall rule predicts trapping.
- A ray with L = 0.790 is trapped.

**Spherical wall, half-width 2.** r/α(r) never falls below its starting value, so the wall traps
nothing: rays launched at 30°–89° from r = 0.9 all escape, although α_in/α_out = 1/5.

### Derivation sketch

1. **Optical metric.** With b = 0 the metric is static. The null condition α²dσ² = |dx|² gives
   Fermat's arrival-time functional ∫|dx|/α, whose extremals are the geodesics of the optical
   metric δ/α².
2. **Conserved quantities.** E = α|k| (from the Killing vector), together with the momentum along
   the boundary's symmetry: k_∥ for a plane, k_z for a cylinder, L for a sphere.
3. **Reachability.** The normal momentum satisfies k_⊥² = E²/α² − k_∥² (planar) or
   k_r² = E²/α² − L²/r² (spherical). A ray reaches a point iff the right-hand side stays
   non-negative along the way.
4. **Uniform b ≠ 0 (S6.3).** Removing a uniform b by ζ′ = ζ + bσ makes α time dependent, so the
   region is static only when b = 0. Where the lab shift vanishes (b = v), the E law of §1 applies
   in place of the static optics.

### Literature

- Natário 2002 §3, footnote 2, computes refraction at a thin moving (shift) wall from Fermat's
  principle: sin r = sin i/(1 + v_s cos(i − θ)). The lapse cavity is the static (b = 0)
  counterpart, with index 1/α.
- The report applies the rule to a carried region of lapse 1 inside a lapse of 55 at v = 2.1:
  escape within 1.04°, and a share of 1/55 for light emitted evenly at the centre. For light
  leaving through the radial wall this is the cylinder/axis case, exact when the radial rise does
  not depend on z. For a closed boundary, and for emitters off the axis, the exact condition
  follows from the conserved quantities of the actual symmetry, as in the spherical case above.

---

## 7. I17: Tolman reading of the horizon flux

### Statement

**Input.** The rear light surface is a black-hole-type Killing horizon of ξ, with κ normalized by
ξ = ∂_σ|_ζ. It emits a flux thermal in the Killing frequency ω = −p·ξ at T = κ/2π; this is the
1+1 result.

**Reading.** An observer at rest in the pattern frame, with 4-velocity u = ξ/N (possible where
α > |b|), measures each mode at ω/N. It therefore reads

  T_loc = κ/(2πN),  N = √(−ξ·ξ) = √(α² − b²).

**Passengers.** In a carried region (b = 0, clock rate α_c), N = α_c and T = κ/(2πα_c). At the unit
clock this is κ/2π.

### Method

- Symbolic: S7.1–S7.3.
- N4.2: rates measured in lab time equal κ.
- The thermal input comes from Finazzi, Liberati & Barceló 2009.

### RESULT: VERIFIED (normalizations)

- κ/N is invariant under ξ → cξ.
- N = 1 at the unit clock (α_c = 1, b = 0) holds.
- The thermal input at κ/2π in Killing frequency is the 1+1 result of Finazzi, Liberati &
  Barceló 2009. For a finite disk in 3+1, greybody factors and the disk's size shape the spectrum,
  and κ varies across the disk (the report finds 7.55–8.3). That part stays an estimate, as the
  report itself states.

### Derivation

1. **Local frequency.** For every mode, −p·u = −p·ξ/N = ω/N.
2. **Temperature.** A Planck distribution in ω at temperature T becomes one in ω/N at T/N;
   occupation numbers are invariant.
3. **Rescaling.** Under ξ → cξ, κ → cκ (from ξ^ν∇_νξ^μ = κξ^μ) and N → cN.

### Literature

Finazzi, Liberati & Barceló 2009:
- κ = dv̄/dr at the black horizon, with exterior-time normalization.
- An observer at rest at the bubble centre (where N = 1) measures ρ = (π/12)T_H², with
  T_H = κ/2π (eqs. (77)–(78)).

I17 is this result for a general N.

---

## 8. I19 and I20: time function, light speeds, static observers

### 8a. Time function and causality (I19)

**Statement (corrected).**
- *Time function.* For every C0 (and C0A) metric with α > 0, g^{σσ} = −1/α² < 0. So σ is a time
  function: it increases strictly along every future-directed causal curve.
- *Stable causality.* This gives stable causality on one rail, and with it the absence of closed
  causal curves.
- *No global hyperbolicity from the time function alone.* The C0 metric
  −(1 + z²)² dσ² + dz² + dx² + dy² has the time function σ, yet the light ray z = tan σ leaves
  every compact set at σ = π/2. So no σ-slice is a Cauchy surface; the (σ, z) part is conformal to
  a strip of Minkowski space.

**Added theorem.** Suppose in addition that α + |β| is bounded on every finite slab
[σ₁, σ₂] × R³. This holds for every design with a flat exterior and bounded fields; the reports'
lapses stay below about 1.7e3. Then every σ-slice is a Cauchy surface and the spacetime is
globally hyperbolic, including superluminal carriage and light surfaces.

**Proof sketch.**
1. **Stable causality.** The widened metric g_c = g − c dσ² (c > 0) has strictly wider light cones,
   and g_c^{σσ} = g^{σσ}/(1 + c/α²) < 0 (S8.3). σ is therefore also a time function for g_c, so g_c
   has no closed causal curves. This is the widening definition of stable causality quoted in
   Visser, Bassett & Liberati 2000 ("possesses a widening … that satisfies the chronology
   condition").
2. **Speed bound.** Parametrize a causal curve by σ. Then |dx/dσ + β| ≤ α, so |dx/dσ| ≤ α + |β|
   ≤ C on a slab.
3. **No escape in finite σ.** Suppose σ stayed below some σ₊ < ∞ on a future-inextendible causal
   curve. Then x(σ) would be Lipschitz and would converge, giving an endpoint (σ₊, x₊). That
   contradicts inextendibility.
4. **Cauchy slices.** So σ runs over all of ℝ on every inextendible causal curve, and every slice
   is met exactly once (σ is strictly increasing). Each slice is then a Cauchy surface: global
   hyperbolicity in the sense of Definition IV.1 of Barzegar, Buchert & Vigneron 2026.
5. **The counterexample.** α = 1 + z² violates the bound, and the ray z = tan σ escapes at
   σ = π/2.

**RESULT: VERIFIED WITH CORRECTED STATEMENT.** The time function gives stable causality. The time
function together with bounded α + |β| gives global hyperbolicity.

**Literature (F.1.11 of lit_design_strategy.md).**
- *Alcubierre.* His claim that a positive-definite γ_ij alone gives global hyperbolicity
  (Barzegar, Buchert & Vigneron 2026, Error 1) fails. The α = 1 + z² example is a lapse-only
  counterexample.
- *Natário 2002.* Definition 1.1 assumes bounded shift functions and unit lapse, and calls the
  spacetime globally hyperbolic. The proof above confirms that.

**Conflict with Barzegar, Buchert & Vigneron 2026, Theorem IV.7.** The theorem states "It is
impossible to construct a superluminal R-Warp model that is globally hyperbolic". This conflicts
with the added theorem for bounded fields.
- *The proof's steps.* The proof reads the condition "time-oriented by increasing t" of their
  Theorem IV.3 as |shift| < lapse (their Remark IV.4). It then uses "globally hyperbolic ⇒ no
  horizons".
- *The failing step.* The flat-front pattern P1 has bounded fields and a Killing-horizon disk, and
  the proof above shows it is globally hyperbolic. So the second step fails.
- *Where the Cauchy horizons lie.* The Cauchy horizons of Finazzi et al. 2009 are defined relative
  to data on past null infinity. Those of Barceló et al. 2022 (Fig. 1) are reached as t → ±∞ at
  finite affine parameter (their eq. (9)). Both lie on the boundary of the chart and concern
  extensions of the prescribed spacetime.
- *Recommendation.* F.1.11 should record this conflict. The book can state global hyperbolicity of
  bounded-field C0 designs as a theorem, with the geodesic incompleteness of steady light surfaces
  stated beside it.

**Outside this verification.** I19's second sentence, that two rails in relative motion can close
causal curves, needs a spacetime that no single C0 chart covers. Everett & Roman 1997 §6 note that
"the t = const slices of the Krasnikov spacetime are not everywhere spacelike".

### 8b. Null speeds and ordering of rays (I20)

**Statement.** For a two-dimensional block −α²dσ² + γ_ℓℓ(dℓ + β^ℓ dσ)², null curves obey

  dℓ/dσ = −β^ℓ ± α/√γ_ℓℓ.

- *Ordering.* Rays of one family are integral curves of one Lipschitz direction field, so by
  uniqueness they never cross and stay ordered.
- *Scope.* This holds for rays confined to a two-dimensional totally geodesic surface: the symmetry
  axis of an axisymmetric pattern (the fixed set of the rotations), or radial lines under spherical
  symmetry. Off such surfaces in 3+1, rays of one family can cross at caustics.
- *Standing geometry.* Along-track light in a static stretch region (C0A, β = 0) moves at α/A.

**Method.**
- S8.5 (symbolic).
- N8.1: axis rays in P5, both families, including passage through the white disk.
- N8.2: parallel rays through a static lapse dip.

**RESULT: VERIFIED WITH ADDED HYPOTHESIS** (a two-dimensional reduction).
- On the axis, order is preserved in both families. The smallest separation is 2.2e-5 for the
  forward family, which converges on the white disk.
- Through the lapse dip, rays starting at x = 0.3, 0.6, 0.9 and 1.2 end at 0.12, −20.5, −32.1 and
  −31.0: they cross.
- The report's own fan grazing the cone tip (GEOMETRY_CLOSURE_PASS.md, a fold caustic with 14
  crossings) is another three-dimensional case of rays of one family crossing.

**Literature.** Finazzi, Liberati & Barceló 2009, eqs. (7)–(8), define the null coordinates of
−c²dt² + (dr − v̄ dt)² through exactly these speeds.

### 8c. Static observers (I20)

**Statement.** Observers at fixed (z, x, y) exist iff g_σσ < 0, which means:
- α > |β| in C0;
- α > A|β| in C0A.

Observers at rest in the pattern frame exist iff α > |b|.

**RESULT: VERIFIED** (S8.6).

---

## Summary table

| Item | Claim | Verdict | Evidence |
|---|---|---|---|
| I12a | Killing energy E = α√(m² + k²) − b k_ζ conserved in a steady lane | VERIFIED | S1.1–S1.2b; drift ≤ 1.3e-11 on 7 geodesics (N1.1) |
| I12a | d ln\|k\|/dσ = −k̂·∇α where the lab shift vanishes | VERIFIED (holds wherever the shift is locally uniform; general form adds k̂_z k̂·∇β) | S1.4 |
| I12a | kept gain exp(v∫(−∂_ζ ln α)dσ) | VERIFIED WITH ADDED HYPOTHESIS: whole path where the lab shift vanishes, steady lane; general identity otherwise | S1.5–S1.6; N1.2–N1.4, N1.6, N2.6; 6.1% counterexample through the shift |
| I12b | exit-angle law (v − 1)/(v cos θ_f − 1) | VERIFIED WITH ADDED HYPOTHESIS: exit within the steady lane; θ_f = exterior propagation angle to +z; exits lie in cos θ_f > 1/v | S2.1; 36 exits, residual ≤ 1.3e-11 (N2.2–N2.3) |
| I12b | shelf law γ′ = (α_s² + v²)/(α_s² − v²); terminal α_s γ′ | VERIFIED WITH ADDED HYPOTHESES: reflection (lapse reaches √(α_s² + v²)), axial exit, static terminal | S2.2–S2.5; N3 to 1e-12 |
| I13 | S null exactly where its transverse gradient vanishes, timelike elsewhere; Killing horizon there | VERIFIED WITH CORRECTED HYPOTHESES: Killing horizon on open null portions only; isolated null points (cone tip) are rest points of the ray flow | S3.1–S3.2, S3.8–S3.9; N4.3–N4.4 |
| I13 | κ = \|∂_ζα\| where the lab shift vanishes | VERIFIED: κ = ∂_ζ(α − \|b\|) in general, signed (negative white, positive black), ξ normalized to exterior time | S3.3–S3.6; N4.1–N4.2, N4.5 |
| I13 vs Natário | same statement? | Different statements with a common criterion \|b·N\| = α; the surfaces meet at the null points of S | S3.7 |
| I13 vs Barceló et al. 2022 | same statement? | Same location criterion; I13 gives the causal character, Barceló et al. the blueshift; the rest-point lemma links them | S3.8–S3.9 |
| I14 | λ = ½(√(κ² + 4v(−∂_r²α)) − κ) | VERIFIED (derived): exact paraxial ray exponent; equals Barceló et al.'s η₋ with ξ = vA/2 | S4.2, S4.5; N5.1–N5.2 (0.2%) |
| I14 | mode energy density changes at 2(κ − λ) | ESTIMATE: exact for geometric-optics ray bundles; conditions 1–5 of §4 for fields and quantum stress | S4.4; N5.3–N5.4 |
| I15 | flank moves at v sin θ_c along its normal; light rides once v sin θ_c > 1 | VERIFIED WITH ADDED HYPOTHESES: shift-free layer, α_in > v sin θ_c, exact for planar, local for curved; threshold = Mach angle | S5.1–S5.3; N6, N2.4–N2.5 |
| I16 | total reflection unless within arcsin(α_in/α_out) of the normal | VERIFIED WITH CORRECTED HYPOTHESES: b = 0 (lab shift −v); α_in < α_out; exact for planar layers and axis-crossing rays in cylinders; spherical walls need L/E ≤ min r/α | S6.1–S6.3; N7.1–N7.4 |
| I17 | occupants read κ/(2πN), N = √(α² − b²) | VERIFIED (normalizations; κ/N invariant; N = α_c); thermal input is the 1+1 result | S7.1–S7.3 |
| I19 | g^{σσ} = −1/α² makes σ a time function | VERIFIED WITH CORRECTED STATEMENT: gives stable causality, and not global hyperbolicity by itself (counterexample α = 1 + z²); with bounded α + \|β\| every slice is Cauchy (conflicts with BBV 2026 Thm IV.7) | S8.1–S8.4 |
| I20 | null speeds dℓ/dσ = −β ± α/√γ_ℓℓ | VERIFIED | S8.5 |
| I20 | rays of a family stay ordered | VERIFIED WITH ADDED HYPOTHESIS: two-dimensional reductions (axis, radial); 3D rays cross | N8.1–N8.2 |
| I20 | static observers iff α > \|β\| | VERIFIED (C0A: α > A\|β\|; pattern-static: α > \|b\|) | S8.6 |
