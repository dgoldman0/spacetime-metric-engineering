## 4. Source-architecture knobs (Sept 9 – 17)

Every report in this family was created Sept 9 – 17, 2026. None computes a
quantum-inequality or ANEC bound, a passenger norm, or a handoff schedule;
handoff appears only as an architectural requirement
(`RAIL_BUILD_TOPOLOGY_DECISION.md:70-77, 101-105`).

**Backgrounds.** The C1 screens (`C1_*`), the cavity screens
(`CAVITY_AND_MAGNETIC_SOURCE_COMPARISON.md`, `NARROW_CURVED_CAVITY_EVALUATION.md`)
and the longitudinal gate (`COUPLED_REORIENTATION_INVESTIGATION.md`) use a
**static, zero-shift surrogate**: the phase-0.745 slice of repaired beta075
(`C1_FINITE_MODULE_PAIR_SCREEN.md:25-29`, `ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:39-42`).
By identities I3 and I22 a static slice has a Type I radial block, so the surrogate
cannot see the Type IV layer; it also discards the shift and current content
[L1, L6]. The storage, capacitor and magnetic-containment reports use
**active beta075 V5 histories** (`ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md:15-17`,
`PRESSURE_LINKED_STORAGE_COMPLETION.md:16-18`, `RAIL_STORAGE_AND_INTERFACE_STATUS.md:18-20`),
whose demanded stress contains the Type IV layer [L1].

**What transfers.** The source laws and their scaling identities are
background-independent. Every demand magnitude, multiplicity, threshold and
supply-to-demand ratio is measured on a throat slice or on beta075 V5.

### S1. Mechanical connectivity (C1 separated modules vs connected control)

- (a) How finite assemblies are joined. C1: structural members carry no
  traction between assemblies; fields, radiation and packet exchange still
  transfer energy, momentum and angular momentum, and recoil and recovery over
  a service/reset cycle are counted (`RAIL_BUILD_TOPOLOGY_DECISION.md:70-77`).
  Families A1/A2, B1–B3, C1–C3 are listed at `RAIL_BUILD_TOPOLOGY_DECISION.md:41-49`.
- (b) C1 narrow pair vs a connected finite control, same total field and
  charge (`C1_FINITE_MODULE_PAIR_SCREEN.md:76-79`).
- (c) Source burden by role: support-material energy 5.492386 (separated)
  vs 3.101704 (connected), +77%; field + support 98.889098 vs 96.498416,
  +2.48%; absolute charge inventory 28.188125 vs 14.094063, ×2
  (`C1_FINITE_MODULE_PAIR_SCREEN.md:143-153`). Remaining signed demand:
  negative radial-null 14.368400 vs 9.649532; negative angular-null
  75.207016 vs 74.193194 (`C1_FINITE_MODULE_PAIR_SCREEN.md:164-168`).
- (d) SINGLE COMPARISON with refinement to 256 cells per unit.
- (e) The charge doubling for neutral modules that share one field is
  general: "The extra opposing charges in the overlap produce real internal
  reaction duties even where the summed charge density vanishes"
  (`C1_FINITE_MODULE_PAIR_SCREEN.md:151-154`). Energies: measured on the surrogate.
- (f) Mechanical independence buys separate module motion for support and
  charge-host inventory.
- (g) "Reassigning the same Maxwell load to a separate support component
  leaves the integrated result unchanged"
  (`CAVITY_AND_MAGNETIC_SOURCE_COMPARISON.md:86-87`).
- (h) Separation adds 2.48% to total energy and 77% to support energy.
- (i) [L6] static surrogate of a throat slice; [L7].

### S2. C1 overlap width and offset

- (a) A smooth step h over [a,b] splits the common radial electric flux
  between modules, Q_L=(1−h)Q, Q_R=hQ (`C1_FINITE_MODULE_PAIR_SCREEN.md:38-47`).
  The field energy is identical in every placement, 93.396712
  (`C1_FINITE_MODULE_PAIR_SCREEN.md:60-61`); the overlap carries the Maxwell
  cross term u_E=(Q_L²+Q_R²)/2R⁴+Q_LQ_R/R⁴ (`C1_FINITE_MODULE_PAIR_SCREEN.md:56-57`).
- (b) Nine placements plus the connected control (`C1_FINITE_MODULE_PAIR_SCREEN.md:111-122`).

| Overlap [a,b] | Support-material energy |
|---|---:|
| [−0.25,0.25], [−0.5,0.5], [1.25,1.75] | infeasible |
| [−1,1] | 106.712367 |
| [0.5,1] | 5.492905 (lowest) |
| [0.25,1.25] | 8.982077 |
| [−0.25,1.75] | 20.895785 |
| [1,2] | 11.317216 |
| [0.5,2.5] (retained broad bracket) | 8.866203 (8.862800 at 256 cells) |

- (c) Demand location: offset placements beat throat-centred ones
  (`C1_FINITE_MODULE_PAIR_SCREEN.md:7-9`); proper length of [−1,1] is
  162.5864 against 2.8940 for [0.5,1] (`C1_FINITE_MODULE_PAIR_SCREEN.md:116-117`),
  the stretch near the throat dominating. Interaction energy 3.176760 (broad)
  vs 0.225955 (narrow) (`C1_FINITE_MODULE_PAIR_SCREEN.md:154-157`). Causal:
  static light-crossing time 2.301640 (broad) vs 0.277761 (narrow), in
  surrogate coordinate time (`C1_FINITE_MODULE_PAIR_SCREEN.md:129-133`).
  Quantum sector: minimum central-charge sums with independent counts
  16,854,288 (broad) vs 4,279,590 (narrow) (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:208-210`);
  angular target energy 38.057681 vs 35.550566
  (`C1_ANGULAR_SCALAR_INVESTIGATION.md:160-163`).
- (d) SWEEP.
- (e) The cross-term identity is general; everything else is measured.
- (f) The narrow overlap is cheaper in support and quantum inventory; the
  broad one is retained "because the existing handoff work exposes derivative
  costs at transitions" (`RAIL_BUILD_TOPOLOGY_DECISION.md:101-105`).
- (h) The cheapest placement is not the retained bracket; [1.25,1.75] is
  infeasible while [1,2] is feasible.
- (i) [L6] [L7].

### S3. Tension-carrier share and carrier type ("95% backbone")

- (a) Fraction f of the throat radial tension assigned to a standing
  backbone. A string-cloud backbone has (ρ,p_r,p_t)=Φ/R²(1,−1,0)
  (`COUPLED_REORIENTATION_INVESTIGATION.md:37-38`), adds zero radial-null
  stress and positive angular-null stress (`COUPLED_REORIENTATION_INVESTIGATION.md:100-102`),
  and needs a reacted force density −Φ′/R² (`COUPLED_REORIENTATION_INVESTIGATION.md:45-52`).
  C1 fills the role with a radial electric field at 95%
  (`C1_FINITE_MODULE_PAIR_SCREEN.md:31-36`), whose Maxwell tensor is
  ½E²(1,−1,0,+1) (`ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md:51-52`).
- (b) f = 0, 0.5, 0.95 (`COUPLED_REORIENTATION_INVESTIGATION.md:41-43, 91-99`).

| f | Backbone | Condensate | Quantum | Host (DEC) |
|---:|---:|---:|---:|---:|
| 0 | 0 | 2.69006 | −23.38925 | 137.25975 |
| 0.5 | 58.40579 | 2.69006 | −25.13640 | 80.60112 |
| 0.95 | 110.97100 | 2.69006 | −27.78549 | 30.68499 |

- (c) Each row sums to 116.56057. Raising f lowers the host energy and raises
  the quantum magnitude by 18.8%. Carrier type sets the angular duty: the C1
  throat remainder after Maxwell and radial source is
  (0.000477588, −0.000477499, −0.009054029), angular-null −0.00857644
  (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:123-127`). Since the
  demand p_t is +3.26×10⁻⁵ (`COUPLED_SOURCE_ROLE_AUDIT.md:60-62`), almost the
  whole C1 angular signed duty is the electric carrier's own +u angular
  pressure (inference from these two lines; the reports do not state it).
- (d) SWEEP (3 shares); tensor algebra is IDENTITY.
- (e) The algebra is general: a (1,−1,0) carrier removes tension without
  touching ρ+p_r, and a conserved static one scales as R⁻²
  (`COUPLED_SOURCE_ROLE_AUDIT.md:70-73`). A Maxwell carrier adds +u to p_t.
  Magnitudes are throat-specific.
- (f) Host energy against quantum magnitude; electric carrier against
  angular duty.
- (i) [L6]; the string-cloud source family was replaced
  (`THROAT_GEOMETRY_CLARIFICATION.md:248`) [L7].

### S4. Radial cavity length and subdivision (compartment count, count distribution)

- (a) Number of equal-optical-length reflecting compartments per module, and
  whether each compartment carries its own channel count.
- (b) 1, 2, 4, 8, 16, 32 compartments; uniform or independent counts
  (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:193-199`).
- (c) 1–16 compartments fail even with the angular target relaxed; 32 pass
  the sampled bulk inequalities (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:201-203, 281-284`).

| Overlap | Counts | Σc | Radial E | Largest reflector force |
|---|---|---:|---:|---:|
| Broad | Uniform | 283,517,387 | −870.800464 | 526.613099 |
| Broad | Independent | 16,854,288 | −31.417409 | 9.030015 |
| Narrow | Uniform | 78,411,043 | −423.962896 | 229.318500 |
| Narrow | Independent | 4,279,590 | −25.091154 | 7.453737 |

  (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:207-210`). Outer end loads grow as the
  square of the compartment count; equal compartments balance internally
  (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:115-117`).
- (d) SWEEP (80 radial-only + 72 layout cases); the scaling is DERIVATION.
- (e) The Casimir 1/L² law, the reflector jump F=−4πR²[p_r] and the internal
  balance are general (identities Q1–Q3). The 32-compartment threshold is
  measured.
- (f) More compartments give more negative radial-null stress and larger end
  loads; independent counts cut Σc about 17× and reflector force 30–60×.
- (g) Shortening moves only the Casimir part; ρ−p_r is fixed by the anomaly
  (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:128-134`). A conformal radial channel
  therefore cannot change the sign of ρ−p_r where the geometry asks for the
  other sign; a separate sector is required there.
- (i) [L6] [L7].

### S5. Population grouping

- (a) How radial central charges are allocated among cells: retained,
  two module scale factors, independent cells, five or six uniform groups
  (`C1_JOINT_SOURCE_MESH_SCREEN.md:104-118`, `C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:40`).
- (c) At ℓ₀=1 only independent cells and five groups admit allocations; at
  ℓ₀=4 every grouping fails (`C1_JOINT_SOURCE_MESH_SCREEN.md:187-191`).
  Inventory 8.0898×10⁸ grouped vs 1.1664×10⁸ independent
  (`C1_JOINT_SOURCE_MESH_SCREEN.md:198-203`). Radial wall traction 9.0300 →
  26.4514 (`C1_JOINT_SOURCE_MESH_SCREEN.md:156-158`). Grouping can empty the
  active radial overlap (left population ends at 0.5178507, right begins at
  0.55) and leaves a ρ−p_r duty of −0.333 to −0.387 near x≈0.518
  (`C1_JOINT_SOURCE_MESH_SCREEN.md:206-210, 222-225`).
- (d) SWEEP (72 + 24 cases with dual certificates).
- (e) Measured. (f) "Population grouping reduces the number of adjustable
  settings while increasing some inventory and interface demands"
  (`C1_JOINT_SOURCE_MESH_SCREEN.md:13-15`).
- (h) Source overlap becomes a property of the population, distinct from the
  hardware overlap (`C1_JOINT_SOURCE_MESH_SCREEN.md:37-40`).
- (i) [L6].

### S6. Local subdivision at a population boundary

- (a) Split the two cells adjoining x=0.518 into 2, 4 or 8 equal-optical
  cavities; alternatively add a wall at 0.35 or 0.4
  (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:133-138, 93-99`).
- (c) Two subdivisions fail; four and eight pass only with the angular
  division at 0.30 (16 of 72) (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:140-148`).
  Added walls: all 84 fail. Σc 1.885×10⁶ → 2.276×10⁶ (4) → 1.521×10⁶ (8);
  E_K −63.49 → −108.24 → −108.69 (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:183-185`).
  New walls carry zero net traction but face loads up to 2.420
  (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:193-198`).
- (d) SWEEP; "fourfold shortening multiplies the local Casimir part by 16" and
  Σc_jL_j is invariant under repartitioning — IDENTITY
  (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:162-166`).
- (g) Equal populations in equal-optical cavities cancel net wall traction.
- (i) [L6].

### S7. Angular division coordinate

- (a) Where the left angular population ends: 0.10 or 0.30.
- (c) 0.10 fails; 0.30 passes with 4 or 8 radial subdivisions
  (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:97-99, 140-144`). A resolved
  residual ρ+p_t = −0.00796195 remains just beyond the new end at x=0.300001
  (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:211-213`). A local certificate
  F(T)=(ρ−p_t)+0.4029(ρ−p_r) has F(demand)=−0.01571; scalar populations add
  +5.3×10⁻¹⁰ per field, the wrong sign
  (`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:103-117`).
- (d) SWEEP with certificates. (e) Measured. (h) Each new endpoint relocates
  residual demand to itself. (i) [L6].

### S8. Angular reflector pattern / reflector transparency

- (a) Where the angular (4D conformal, ξ=1/6) scalar sees Dirichlet walls:
  whole module (transparent to radial walls) or 4, 8, 32 compartments.
- (c) Spectrum: all 574 cases positive; lowest ω² 2.588779 (whole module);
  it selects neither count nor overlap (`C1_ANGULAR_SCALAR_INVESTIGATION.md:7-9, 112-122`).
  Added throat angular-null per field −3.447×10⁻¹¹ (1→8) and −3.467×10⁻¹¹
  (1→32), broad pair: 8→32 gains 0.6%
  (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:165-173`). In the overlap
  the increment has the wrong sign (+5.3×10⁻⁸ per field per module)
  (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:179-192`). End loads at
  logarithm-1 multiplicity: retained radial force 9.03 against ≈2,741 (8
  compartments) and ≈1.51×10⁶ (32) (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:213-216`).
  Transparent walls remove the reflection increments and keep the bulk
  contribution (`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:298-302`).
- (d) SWEEP (66 comparisons) plus exact cylinder control. Dirichlet-end
  response (Δρ,Δp_r,Δp_t)=Δb(1/6,1/2,−1/6) and the held-interaction bound
  d|F|/|E| = 1 + zK₀(z)/K₁(z) > 1 are IDENTITIES
  (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:199-201, 253-268`).
- (e) Response formula and bound general; magnitudes measured.
- (f) Reflection gives a useful local sign and a confinement load orders of
  magnitude larger. (h) Most of the throat benefit comes from one nearby
  reflector. (i) [L6].

### S9. Curvature-coupling logarithm ℓ₀ = log(R₀/a₀)

- (a) A fixed global finite curvature-squared coupling of the conformal
  scalar's effective action; a₀ ≈ 1.2371, 0.7503, 0.2760, 0.03736
  (`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:130-136`).
- (b) ℓ₀ = 0.5, 1, 2, 4.
- (c) Throat multiplicity 174.8M, 58.28M, 24.98M, 11.66M; outcomes: overlap
  wrong sign (0.5); throat works, overlap fails (1); neighbour allowed 0–8.9M
  (2); both bulk witnesses pass (4) (`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:259-264`).
  ℓ₀=4 then fails once transition probes are added
  (`C1_JOINT_SOURCE_MESH_SCREEN.md:132-133, 191`).
- (d) The shift T(ℓ₀)=T(1)−2(ℓ₀−1)H is IDENTITY
  (`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:125`); outcomes SWEEP.
- (e) Identity general. "a change of subtraction convention is accompanied by
  a compensating change of α,β. The total balance is invariant … changing a
  subtraction label alone supplies no additional stress. A material mechanism
  for adjusting the couplings has yet to be established"
  (`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:143-151`).
- (h) Non-monotone in coverage: ℓ₀=4 passes two probe points and fails at
  four and six.
- (i) [L6].

### S10. Longitudinal channel strength, interval and clock freedom

- (a) Central charge through k=ηc/(12π), the interval every channel covers,
  and an allowed clock band (1±d)A₀ (`COUPLED_REORIENTATION_INVESTIGATION.md:184-236`).
- (c) At k/R₀²=0.01 (c≈64,997): supply/demand 0.00463 on [−7,7] (0.0417
  with the 50–150% clock box) and 0.000175 on [−40,40]; 78 of 88 cases
  excluded (`COUPLED_REORIENTATION_INVESTIGATION.md:242-258`). Thirteen
  archived geometry transfers change the ratio by −8.45% to +0.315%
  (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:132-143`); see G1 and G13.
  In the C1 pair the 50% clock box supplies 17.10%, 7.45%, 4.15% of the
  balance on [−3,3], [−5,5], [−7,7] (`C1_FINITE_MODULE_PAIR_SCREEN.md:174-176`).
- (d) Integral identity (Q4) DERIVATION; AdS₂ positive control gives exactly
  4 (`COUPLED_REORIENTATION_INVESTIGATION.md:304-307`); outcomes SWEEP.
- (e) Identity general for the stated 1+1 law with non-negative remainder.
  "A global rescaling of time leaves the source and the bound unchanged"
  (`COUPLED_REORIENTATION_INVESTIGATION.md:260-262`).
- (i) [L6]; the gate holds R(l) fixed (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:128-129`).

### S11. Cavity gap and mirror profile (scalar-mirror proximity cavity)

- (a) Gap a, relative mirror thickness s=d/a, optical strength q=gv²a²,
  portal coupling g (`NARROW_CURVED_CAVITY_EVALUATION.md:63-67`).
- (c) Planar selected case: h_I=1.0984×10⁻⁴ against mirror load 1.9096/g,
  crossing coupling g*=17,385 (`NARROW_CURVED_CAVITY_EVALUATION.md:119-125`).
  Curved (R=3, 4.2, 6.8): g* 24,191 → 17,438; best net opening −0.2015 at
  g=10 against a requirement ≈2 (`NARROW_CURVED_CAVITY_EVALUATION.md:131-147`).
  At fixed mirror height and thickness a 16× gap reduction raises h_I only
  1.67× (`NARROW_CURVED_CAVITY_EVALUATION.md:156-162`).
- (d) "h_I and h_χ both ∝ η/a³" at fixed optical strength and relative
  thickness — DERIVATION (`NARROW_CURVED_CAVITY_EVALUATION.md:82-87`); rest SWEEP.
- (e) Planar threshold and co-scaling are background-independent within the
  canonical scalar-mirror model; curved values are throat-specific.
- (f) Interaction and mirror cost scale "at nearly the same rate"
  (`CAVITY_AND_MAGNETIC_SOURCE_COMPARISON.md:48-50`).
- (h) Finite transparency caps the gain at fixed material. (i) [L6].

### S12. Short magnetic-circuit geometry (summary level)

- (c) 303 of 440 paths give helpful quantum opening; all 23,760 combinations
  fail; best load-to-vacuum ratio ≈355; the required N_fe²/(16π²)=17.971
  exceeds the perturbative limit 0.1 (`CAVITY_AND_MAGNETIC_SOURCE_COMPARISON.md:46, 57-64`).
  "adding flux, shrinking capsules, or allowing their fields to spread is
  insufficient" (`CAVITY_AND_MAGNETIC_SOURCE_COMPARISON.md:83-85`).
- (d) SWEEP (source report `SHORT_MAGNETIC_CIRCUIT_EVALUATION.md` outside this
  inventory's reading list). (e) Measured on the static slice. (i) [L6].

### S13. Planar EM Casimir cell realization and holding

- (a) Two orientations of ideal planar cells, target
  (ρ,p_r,p_t)_Q=(−C_r−2C_t, −3C_r+2C_t, C_r−2C_t)
  (`COUPLED_REORIENTATION_INVESTIGATION.md:59-63`).
- (c) C=ηπ²/(720d⁴) maps targets to d≈0.992 at the throat and ≈0.0565 near
  |x|=2.5 (`COUPLED_REORIENTATION_INVESTIGATION.md:129-133`). Independently
  held cells need holder energy ≥3(C_r+2C_t), complete cells ≥2(C_r+2C_t),
  leaving a local deficit up to 0.139277 (`COUPLED_REORIENTATION_INVESTIGATION.md:141-145`).
- (d) IDENTITY for d⁻⁴ and the holder bounds; application measured.
- (e) General: a directly held static negative-energy cell costs more positive
  holding energy than it supplies.

### S14. Magnetic containment loop geometry and sleeve strength

- (a) Aspect ratio a/L and pitch of a capsule flux tube confining an
  ultrarelativistic gas; sleeve strength k = allowable stress / proper energy
  density (`MAGNETIC_LOAD_BALANCING_TEST.md:24-38`, `MAGNETIC_CONTAINMENT_MATERIAL_SEARCH.md:19-21`).
- (c) At the second location a/L=0.005–0.025 pass and 0.05–0.2 fail
  (`MAGNETIC_LOAD_BALANCING_TEST.md:148-153`); minimum k 0.7386 and 0.9505
  (`MAGNETIC_LOAD_BALANCING_TEST.md:135-136`). Demonstrated materials:
  graphene k≈6.15×10⁻¹⁰, carbon nanolattices ≈4×10⁻¹¹
  (`MAGNETIC_CONTAINMENT_MATERIAL_SEARCH.md:65-76`).
- (d) SWEEP; the virial bound E_sleeve ≥ 2E/(3k(1+πa/L)) is DERIVATION
  (`MAGNETIC_GEOMETRY_COMPARISON.md:182-183`).
- (e) Confinement B²/8π > P and the virial bound are general; thresholds rest
  on beta075 V5 histories [L1].

### S15. Magnetic jacket (internal/annular field ratio, radius ratio)

- (a) Internal and annular magnetic pressures bp, ep and radius ratio η;
  53 geometries (`MAGNETIC_GEOMETRY_COMPARISON.md:46-47, 123-127`).
- (c) Required sleeve k (first/second location): original loop
  0.81147/0.99520; common jacket (b=0.1, e=1.1, η=1.01) 0.80655/0.65421;
  zero-field wall control 0.59383/0.52680 (`MAGNETIC_GEOMETRY_COMPARISON.md:135-140`).
  The common jacket cuts loop field energy to 12.2% and hoop load to 56.1%,
  raises sheet current 1.79× (`MAGNETIC_GEOMETRY_COMPARISON.md:148-153`).
  Every geometry fails at k=0.5 (`MAGNETIC_GEOMETRY_COMPARISON.md:145-146`).
- (d) SWEEP plus derived pressure relations Δp_i=p(1+b−e), Δp_o=ep
  (`MAGNETIC_GEOMETRY_COMPARISON.md:49-63`).
- (f) Lower field energy against higher sheet current. (h) A strong inward
  bend load appears under compression (bend pressure ratio −11.8 to −13.8,
  `MAGNETIC_GEOMETRY_COMPARISON.md:218-223`). (i) [L1].

### S16. Containment ensemble composition and orientation

- (a) Longitudinal sheet, hoop strings, transverse sheet, hoop-directed
  Maxwell field, pressureless host (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:47-53`).
- (c) Replacing the hoop field by a normal field or by axial photons fails;
  the hoop field passes (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:108-112`).
  Reserves 0.0047–0.0157 (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:124-127`).
- (d) SWEEP / LP; projector algebra IDENTITY (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:63-66`).
- (h) The averaged tensor (1,1,0) hides the mechanical difference between a
  transverse field and axial photons (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:38-42`).
- (e) Orientation lesson general; reserves measured on beta075 [L1].

### S17. Storage medium and converter directionality (capacitor vs pressure-linked vs elastic vs EM)

- (a) The store that supplies endpoint work and heat: pressure-linked thermal
  fluid with radial E-field; longitudinal thermoelastic body; net-neutral
  radial-E store; charged capacitor.
- (c) Pressure-linked: a continuous column costs 221,216.7 peak pressure and
  3.09×10⁷ slice energy at startup against 158.34 for isolated pieces
  (`PRESSURE_LINKED_STORAGE_COMPLETION.md:119-124`); unrestricted passive
  discharge leaves a null burden 7.115; bidirectional stores give 0.0937
  against a fade requirement 0.104; a single-port heat engine 5.61
  (`PRESSURE_LINKED_STORAGE_COMPLETION.md:178-179, 250-251`). Balanced ends
  are infeasible, integrated witness I=−2.1947 (`PRESSURE_LINKED_STORAGE_COMPLETION.md:161-167`).
  Elastic: every prepared case stops at local heat depletion, s=0.266–0.379
  (`ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md:188-193`). EM store: moving field
  energy into material heat clears s=0.5 at +20.5% energy
  (`ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md:154-157`). Capacitor:
  best field/wall ratio 0.048 (b/a=1.05) → 3.27 (b/a=30)
  (`CHARGED_CAPACITOR_CONSTRUCTION.md:100-108`); fade requirement 0.254 before
  work transport, 8.6–43.5 once joint transport is counted
  (`CHARGED_CAPACITOR_CONSTRUCTION.md:203-206, 235-238`).
- (d) Single comparisons and small sweeps; constitutive laws and the shell
  bound U_E/(M_in+M_out) ≤ 2(b−a)/(b+a) are IDENTITIES
  (`CHARGED_CAPACITOR_CONSTRUCTION.md:116-121`).
- (e) Laws general; every number rests on beta075 V5 [L1].
- (h) Pressure-column self-weight accumulates across the clock gradient
  (`PRESSURE_LINKED_STORAGE_COMPLETION.md:123-125`); an apparent heat-engine
  infeasibility came from the LP solver deleting coefficients ≤1e−9
  (`PRESSURE_LINKED_STORAGE_COMPLETION.md:230-237`); the capacitor's
  instantaneous tensor looks favourable until work transport is counted.
- (g) "Additional divisions of the same fluid and field leave the summed force
  balance intact" (`PRESSURE_LINKED_STORAGE_COMPLETION.md:171-172`).

### S18. Physical scale L (homothetic enlargement)

- (c) E_peak=(5.86×10²⁶ V)/L; the Schwinger field is reached at L≈4.43×10⁸ m
  (`CHARGED_CAPACITOR_CONSTRUCTION.md:269-272`). "Increasing L lowers the
  electric field without improving the dimensionless material-energy ratio"
  (`CHARGED_CAPACITOR_CONSTRUCTION.md:295-296`). C_J/δ_s ∝ c⁵/G independent of
  L_g, C_Jδ_s/ħ ∝ (L_g/ℓ_P)² (`RAIL_STORAGE_AND_INTERFACE_STATUS.md:111-133`).
- (d) IDENTITY. (e) General for any geometry-scaled design.
