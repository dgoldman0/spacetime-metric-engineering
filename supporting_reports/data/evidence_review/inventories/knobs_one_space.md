# Part-and-knob → physics response map: the one-space era (23–25 September 2026)

> **Errata (audit 2026-09-26, `../audit_synthesis.md` §5).**
> - I6 (shear identity): the identity 8πT(n±e_z, n±e_z) = −(β_r² ± Δ⊥β) is exact, but it gives opposite-sign null energies along n ± e_z, not Type IV in general. Type IV follows where the (n, e_z) block decouples (T_n̂r̂ = T_ẑr̂ = 0, e.g. a steady shift window uniform along the track); elsewhere the type needs the full classification (audit §1.2 R8, with a Type I counterexample).


Compiled from the read-only repository `/media/projectspace/active-rail-refined-design-base` at HEAD `19a367a`.
Purpose: inventory for a general textbook on metric engineering. Every response is tagged by evidence type and by
how far it generalizes. Nothing here is new physics except the items explicitly tagged **ID-c** (compiler-verified
derivations; see §3.2), which were checked symbolically and are consistent with the report formulas wherever they overlap.

---

## 0. Scope, conventions, legend

### 0.1 Metric classes

| Tag | Line element | Where used |
|---|---|---|
| **C0** (target class) | ds² = −α²dσ² + (dz+β dσ)² + dr² + r²dφ², with α(σ,z,r), β(σ,z,r); flat spatial slices | lapse-and-staging pass onward (LAPSE_AND_STAGING, SOURCE_SCALING, COMPARTMENT, FRONT_LIGHT_SURFACE, CONE_TIP, GEOMETRY_CLOSURE, ANEC_MAP, QUANTUM_ESTIMATES); disclosure `active_rail_technical_disclosure.tex:128-144` |
| **C0A** (with stretch) | ds² = −α²dσ² + A²(dz+β dσ)² + dr² + C(r)²dφ² | AXIAL_TRACK, ONE_SPACE_REVISION, CHOREOGRAPHY_PASS, DEMAND_CENSUS, AMPLITUDE_PASS; code `adm_harness/axial_track.py:1-21` |
| **CS** (spherical, pre-one-space) | 2D (σ,ℓ) service metric × sphere of areal radius R | CONSTANT_RADIUS_TRACK, RESET_SCHEDULE_OPTIONS; `adm_harness/constant_radius_track.py:1-14` |

Units: G = c = 1; lengths in the rail unit L. Stresses scale as 1/L², integrated energies and contents as L
(dimensional identity; DEMAND_CENSUS.md:223-227, tex:355-357). "Content" = null deficit integrated over volume
(coordinate measure 2πr dr dz, or proper measure A r dr dz dφ; DEMAND_CENSUS.md:71-81); "peak negative energy" in the
compartment-era tables is the instantaneous volume integral of the Eulerian T_n̂n̂ < 0 (`scripts/run_compartment_pass.py:166,312-332`,
`scripts/run_geometry_closure_pass.py:117,174`), not a pointwise density. "Type IV band" = interval between samples
where the certified classifier returns a complex eigenpair, found by root-finding at flux-carrying null-sum crossings.

### 0.2 Tags

Evidence (field d):
- **ID**: identity or derivation stated in a report (formula quoted, file:line given).
- **ID-t**: identity checked exactly in a unit test.
- **ID-c**: compiler-verified symbolic derivation, not stated in the reports (script: `scratchpad/textbook/verify_identities.py`, `verify_compact.py`).
- **EST**: estimate or heuristic criterion in a report, not an exact identity.
- **SW**: sweep of three or more values.
- **SC**: single comparison (two values or two designs).

Generality (field e):
- **GEN-any**: holds in any spacetime (or any 3+1 slicing) under the stated conditions.
- **GEN-C0**: holds for every metric of the stated class under the stated conditions.
- **GEN-sub**: holds for a stated sub-class (e.g. static, zero shift, stationary pattern frame).
- **DES**: measured on one design lineage only; no identity backs the trend.

### 0.3 Design lineage (where each measurement lives)

| Label | Design | Class | Report |
|---|---|---|---|
| D-sph | constant-radius spherical track carrying the C∞ beta075 service (support stretch ≈600, decompression) | CS | CONSTANT_RADIUS_TRACK, RESET_SCHEDULE_OPTIONS |
| D-ax0 | same service transplanted into an axial core, single transverse boundary layer | C0A | AXIAL_TRACK |
| D-1S | one-space revision: held support, live-scheduled lapse envelope, staged stack (conformal e⁸ + sheath e⁸) | C0A | ONE_SPACE_REVISION |
| D-ch | choreography: static support (stretch 630), path-matched shift, lanes 1.5/1.8/2.1c, wide stack | C0A | CHOREOGRAPHY_PASS |
| D-cen | D-ch at 2.1c (census design) | C0A | DEMAND_CENSUS |
| D-amp | flat support (C0=B0=1), support lapse 6, conformal pre-sheath e⁷ | C0A | AMPLITUDE_PASS |
| D-lap | A ≡ 1: convex plateau e⁴, gated windows, sheath e¹, static or time-staged sheath (the disclosure's embodiment) | C0 | LAPSE_AND_STAGING_PASS; SOURCE_SCALING_TEST (staged); tex |
| D-cmp | flat compartment, rest-to-rest 2.1c path, plateau e⁴, convex rise 0.5, staged sheath e¹, outer fall 9.25–13.25 | C0 | COMPARTMENT_PASS |
| D-fr | D-cmp + front element (current / running shelf / static shelf / 15° cone) | C0 | FRONT_LIGHT_SURFACE_PASS, CONE_TIP_FIELD_PASS |
| D-trim | trimmed reference: plateau e³, shift edge 1, outer fall 8.75–10.75, cone base 14; speed-scaled variants 1.5–20 | C0 | GEOMETRY_CLOSURE_PASS, ANEC_MAP_PASS, QUANTUM_ESTIMATES_PASS |

The technical disclosure (`active_rail_technical_disclosure.tex`) describes D-lap only; the compartment, fronts and
trimming postdate it.

### 0.4 Physics channels (columns of the coupling matrix, §4)

E = energy of each sign / energy density · N = null deficit (minimum null energy, negative-null content) ·
S = peak stress component · Loc = demand location · Ty = Hawking–Ellis type and bands ·
Oc = occupant clock / packet timelike margin · Ot = tides and proper acceleration · Oθ = temperature, radiation, cavity, view ·
Ar = arrival and lead over light · Sw = swept matter, light surfaces, horizons · Src = source-family requirement.

---

## 1. Parts

| # | Part (code name) | Geometric function, general terms | General or design-specific | Key refs |
|---|---|---|---|---|
| P1 | **Service region** (`core`, r ≤ r_c = 1.75) | Holds the 2D service metric of lapse and shift along the track as an exact product with a flat transverse plane. Its demand is a pure transverse pressure p_r = p_φ = −K/8π (K = Gaussian curvature of the service metric) with zero energy density and zero along-track pressure; along-track null energies vanish identically. | Function GEN-C0A (product identity I4). Radius and choice to keep fields r-independent inside are design choices. | AXIAL_TRACK.md:125-134; tex:146-152 |
| P2 | **Carry shift** (β along z; packet bump; along-track shift edges) | Moves the packet: the packet's coordinate speed equals −β at its centre (or the path speed). On flat slices it is the *only* source of energy density (ρ = −β_r²/32πα²) and the source of every momentum flux (linear in β). | Carrying role and energy/flux structure GEN-C0 (I1, I5). Bump shape, edge width design-specific. | LAPSE_AND_STAGING_PASS.md:56-73; CHOREOGRAPHY_PASS.md:55-59 |
| P3 | **Shift transition** (radial; `shift_layer`, 4.25 ≤ r ≤ 6.25) | Returns β to zero across the transverse plane. Hosts all energy density (negative, α⁻²-suppressed) and the shear flux that produces Type IV unless a high, radially rising lapse surrounds it. | Mechanism GEN-C0 (I1, I5, I6); placement DES. | AXIAL_TRACK.md:191-204; ONE_SPACE_REVISION.md:97-110 |
| P4 | **Packet lapse plateau** (packet lapse window / `plateau_log`) | Raises the lapse where the shift varies, suppressing flux ∝ 1/α and energy ∝ 1/α²; sets the local along-track light speed α/A; in D-lap it also sets the packet clock (e⁴ = 55). | Suppression scalings GEN-C0 (I1, I5). Required height DES. | LAPSE_AND_STAGING_PASS.md:85-101; COMPARTMENT_PASS.md:113-117 |
| P5 | **Convexity / convex rise** (`lapse_convexity`; compartment `slope`) | Makes log-lapse convex along the track where the shift varies, holding the service curvature K negative so the radial pressure p_r = −K/8π stays positive from the service region outward. | Sign relation GEN-C0A (I4; K formula ID-c I4c). Required value DES. | LAPSE_AND_STAGING_PASS.md:85-89; COMPARTMENT_PASS.md:114-115 |
| P6 | **Plateau edge and service cutoff** (flat-top length, edge width, `service_inner`/`track_half_length`) | Brings the plateau back down along the track; a steep edge or a cutoff step compresses the lapse gradient and concentrates stress. | DES. | LAPSE_AND_STAGING_PASS.md:123-139 |
| P7 | **Lapse sheath** (`sheath_log_lapse`, rise/fall radii) | A radial lapse rise held across the shift transition. Supplies positive transverse Laplacian of α in the (n,z) block, which dominates the shift's linear flux; carries stress with zero energy. A standing strong sheath is a lapse maximum: Shapiro advance, fast clocks, a standing superluminal light channel; free particles fall away from it. | Zero energy/zero flux GEN-C0 (I2); why a rising lapse helps ID-c (I5c). Amplitude thresholds DES. | LAPSE_AND_STAGING_PASS.md:99-101; ONE_SPACE_REVISION.md:127-131; CHOREOGRAPHY_PASS.md:160-191 |
| P8 | **Conformal pre-sheath** (`conformal_log_scale`) | Raises ln α and ln A together across a radial layer. Carries no flux even under a moving shift; rescales service curvature by e^(−2φ); its stretch carries energy growing as e^φ. | Flux-free and curvature scaling GEN-C0A (I9); energy scaling GEN-sub (I10). Threshold DES. | ONE_SPACE_REVISION.md:103-107; DEMAND_CENSUS.md:151-178 |
| P9 | **Standing support** (C0, B0 stretch ≈630; support lapse λC0; weight w_support) | beta075 heritage: a stretched, lapse-raised region that compresses the coordinate carry speed (U/B). Carried 99.6% of the census energy; removable. | DES (heritage). | `adm_harness/constant_radius_track.py:441-443`; AMPLITUDE_PASS.md:11-34 |
| P10 | **Carve** (packet-local exclusion of the support weight) | Moves a stretch window with the packet; carried the speed advantage in held-support designs; source of residual moving Type IV bands. | DES. | ONE_SPACE_REVISION.md:29-38,154-155 |
| P11 | **Stretch A** (generic) | Carries all static energy density (ρ√γ = −∂_r(r∂_rA)/8π); when it varies in time it splits the two radial null Hessians and opens Type IV bands. | GEN-sub (I7, I10). | AXIAL_TRACK.md:206-225; DEMAND_CENSUS.md:126-149 |
| P12 | **Live windows** (`live_start`, `lapse_lead`, `lapse_release_lag`) | Time-orders the service so the lapse covers the shift for the shift's entire life: lapse on before the shift, off after the release; the along-track lapse structure meets the shift only on the plateau. | Envelope heuristic EST (I8); timing DES. | LAPSE_AND_STAGING_PASS.md:95-98; ONE_SPACE_REVISION.md:87-95 |
| P13 | **Time staging** (`sheath_follow`, `sheath_schedule`) | Makes the sheath ride with the packet and switch with the transit, so the standing geometry is flat space and all demand is local in space and time. | Admissibility GEN-C0 (I2); schedule DES. | LAPSE_AND_STAGING_PASS.md:34-36,69-73; tex:202-208 |
| P14 | **Flat compartment** (hole; `clock_log`) | Region where α and β are uniform in space at each instant: spacetime there is Minkowski; normal observers are free-falling; the packet rests on them; its clock runs at the compartment lapse. | GEN-C0 (I3). | COMPARTMENT_PASS.md:54-68 |
| P15 | **Hole boundary** (`hole_edge`, `hole_radius`) | Lapse rise from the clock value to the plateau, placed where the shift is still uniform, so it is pure lapse (Type I for any profile). Optically a lapse cavity (index 1/α): total internal reflection outside a narrow escape cone. Trace-anomaly peak sits here. | Type I and cavity optics GEN-C0 (I2, I16). | COMPARTMENT_PASS.md:64-69; GEOMETRY_CLOSURE_PASS.md:205-224; QUANTUM_ESTIMATES_PASS.md:21-23 |
| P16 | **Outer lapse falls** (`lapse_layer`, `sheath_fall`) | Returns the lapse to one. Pure lapse, so any profile is Type I; for radial light the null energy is ∝ α_r/(rα) < 0 on every fall, so the falls hold most of the null deficit; the classical F(φ)R obstruction sits here. Their outer radius sets where α > v and hence the cone base. | Sign GEN-C0 (I18); placement freedom GEN-C0 (I2); magnitudes DES. | SOURCE_SCALING_TEST.md:289-292; GEOMETRY_CLOSURE_PASS.md:86-90 |
| P17 | **Rear lapse fall** | Where the lapse falls through the carry speed behind the pattern: a black-hole-type Killing horizon disk with κ = |∂_ζα|, emitting a Hawking-like flux forward. | Criterion GEN-sub (stationary pattern frame; I13). | CONE_TIP_FIELD_PASS.md:61-71; QUANTUM_ESTIMATES_PASS.md:109-142 |
| P18 | **Front fall ("current front")** | Where the lapse ahead falls through v with no transverse gradient: a white-hole Killing horizon disk; gathers forward light and matter at rest and blueshifts them as exp(κt) for the lane's duration. | GEN-sub (I12, I13). | FRONT_LIGHT_SURFACE_PASS.md:62-100; CONE_TIP_FIELD_PASS.md:16-21 |
| P19 | **Forward shelf** (`ForwardShelf`) | Holds the lapse at α_s > v ahead of the pattern so the front light surface disappears; swept matter leaves at a fixed γ'; signals from the packet run ahead inside the shelf. Cost proportional to route length. | Swept-γ law GEN-sub (I12); costs DES. | FRONT_LIGHT_SURFACE_PASS.md:120-131,215-223 |
| P20 | **Conical front** (`ConeFront`) | Slender cone of raised lapse ahead, peaked on the axis. Its α = v surface is timelike except on the axis (transverse/along-track gradient ratio ≈ cot θ_c), so overtaken objects slide off in bounded time. Its flank must advance along its normal slower than light (v sin θ_c < 1). | Criteria GEN-sub (I13, I15); numbers DES. | FRONT_LIGHT_SURFACE_PASS.md:133-149; GEOMETRY_CLOSURE_PASS.md:136-147 |
| P21 | **Cone tip** (`rounding`) | The only null point of the cone's light surface. Transverse lapse curvature pushes modes off axis at rate λ faster than they blueshift at κ; rounding sets that curvature. A fan grazing the tip forms a fold caustic. | λ formula EST (I14); DES numbers. | CONE_TIP_FIELD_PASS.md:92-104; GEOMETRY_CLOSURE_PASS.md:254-258 |
| P22 | **Track cutoff / sheath taper along z** | Confines the service fields and the sheath to the track; beyond it the metric is exactly Minkowski. | DES. | DEMAND_CENSUS.md:41-46 |
| P23 | **Packet path** (`packet_path`) | Prescribed worldline v(σ) (entry, acceleration, lane, catch, coast; or rest to rest); every packet-centred field is centred on it, and the carry shift equals the path speed at the centre. | Construct general; lead DES. | CHOREOGRAPHY_PASS.md:45-73; tex:168-189 |
| P24 | **Spherical-track parts** (CS): constant-radius track, static end transitions, string cloud; axial string cushion | Constant areal radius makes the radial block an exact string cloud and moves all dynamics into p_Ω = −K/8π; widening into asymptotic ends needs an integrated radial deficit ≥ 1 per end. String cushion (axial) adds K_Σ at the cost of a deficit angle. | GEN-sub for CS (I24). | CONSTANT_RADIUS_TRACK.md:33-95,320-334; AXIAL_TRACK.md:136-140 |
| P25 | **Support decompression / reset** (q(σ), reset fronts) | Scheduled relaxation of the standing stretch; the dominant source of angular deficit (CS) and of boundary-layer Type IV (C0A). | Mechanism GEN-sub (I7, I24); DES numbers. | CONSTANT_RADIUS_TRACK.md:51-71; RESET_SCHEDULE_OPTIONS.md |

---

## 2. Knobs

Format per knob: (a) definition, (b) values tested, (c) responses by channel, (d) evidence, (e) generality,
(f) couplings / trade-offs, (g) separations, (h) surprises.

### K1. Lane speed, choreography era (static support, D-ch)

- (a) v_lane: constant coordinate speed of the packet path through the support; carry field U = v·B at the path centre so the packet's coordinate speed equals the path speed (CHOREOGRAPHY_PASS.md:47-59; `adm_harness/constant_radius_track.py:178-182,438-440`).
- (b) Search: 1.2, 1.5, 1.8, 2.1c (144 choreographies). Gate: 1.5, 1.8, 2.1c.
- (c)
  - Ar: mean lead over flat-space light 0.05 / 0.55 / 0.89 / 1.13 (CHOREOGRAPHY_PASS.md:85-91); chosen lanes lead 1.00 / 1.38 / 1.66, end-to-end 1.35c at 2.1c (:17-20).
  - Ty: Type I at all 2.37 M boundary-layer points for each lane; refined 2.1c 4.79 M; no bands (:98-107).
  - N: boundary-layer costs unchanged by the path (−2.65, 490/σ) (:195-202). Service-region minimum −1.30 (1.5c) vs −1.16 (2.1c), on the leading flank of the packet lapse window (:199-207).
  - Oc: packet timelike; worst normalized norm −0.95 live, −0.0975 coasting (:21-23).
  - Requirement: faster lanes need packet lapse-window gain 3 to satisfy the envelope α > 2r|β_z| (:70-73).
- (d) SW (lead), SC (service-region minimum at two lanes reported).
- (e) DES.
- (f) Lane speed ↔ lapse envelope (higher β_z at entry needs larger window lapse).
- (g) Path choice leaves the boundary-layer cost unchanged (:201-202).
- (h) The slowest lane has the deepest service-region minimum; the window's depth and flank, not the lane speed, set it (:204-207).

### K2. Carry speed with speed-scaled lapse (D-trim, closure scan)

- (a) Lane speed v of the compartment path, with the plateau and cone log-lapse raised by ln(v/2.1) and the compartment lapse held fixed (`scripts/run_geometry_closure_pass.py:69-85`); cone half-angle either fixed at 15° or scaled as sin θ_c = 0.54/v (`:43-44`).
- (b) v = 1.5, 2.1, 3, 5, 10, 20 (both cone rules); ANEC, quantum and 3D audits at 2.1 and 10.
- (c) (scaled cone unless stated; GEOMETRY_CLOSURE_PASS.md:159-166)
  - Ty: Type I at every speed; no bands.
  - E: peak negative energy 0.009015 at every speed; worst envelope ratio 0.504 at every speed (data: `supporting_reports/data/geometry_closure_pass/speed_scan_scaled.csv`, not in report text).
  - S: 1.54, 1.82, 2.18, 2.75, 3.65, 4.77 (≈ ln v).
  - N: peak content 211, 252, 311, 442, 787, 1,529; over-σ content 2,040 → 11,260, of which in the cone 214 → 8,486 (cone dominates above v ≈ 3). Pattern minimum null −0.74 → −1.33 (data CSV).
  - Loc: demand migrates into the cone: 16% of demanded content at 2.1, 60% at 10 (QUANTUM_ESTIMATES_PASS.md:70-81).
  - Oc: passenger at clock 1 ages 244, 174, 122, 73, 37, 18 days per light-year of lane.
  - Oθ: escape cone of the compartment 1.05° (2.1) → 0.22° (10), share 2% → 0.4% (GEOMETRY_CLOSURE_PASS.md:49-56,216-218); rear horizon κ 7.55 → 57.2 on axis, passenger temperature 2.75 mK → 20.8 mK at L = 1 m (QUANTUM_ESTIMATES_PASS.md:119-149); photon trace-anomaly peak 1.33 → 6.01 ħc/L⁴ (:70-81).
  - Ar: lead over light on the test trip 1.5, 5.1, 10.5, 22.5, 52.5, 112.5.
  - Sw: swept matter γ (lanes ending σ = 6/9) 6.6/3.9 → 92.4/93.8; light gain 8.9 → 95.9, ≈ 5v. Tip κ 0.44 → 1.18, λ 1.64 → 41.0, λ/κ 3.7 → 34.9. With the fixed 15° cone: gains 6.0, 11.8, 36, 3.7×10⁶, 7.9×10¹¹, 5.1×10¹⁴ — the flank trap opens above v = 1/sin 15° = 3.9 (:151-155).
  - Src: first-light ANEC −0.0012 (2.1) and −0.0007 (10) on the test trip; −202 and −2.2×10⁴ on long lanes (ANEC_MAP_PASS.md:18-23). Trace/demand ratio 0.74 → 1.64 × (ℓ_P/L)². QI requirement not re-evaluated vs speed.
- (d) ID (speed scaling I11; aging I26; escape cone I16; flank criterion I15), SW (6 speeds).
- (e) Invariance of the shift-region tensor: GEN-C0 (exact isometry during a steady lane). Constancy of peak negative energy and envelope ratio: direct consequences of I11 + I1. ln v stress growth, cone-dominated content, ~5v gains: DES.
- (f) Faster needs a higher plateau (ln v) with a fixed compartment lapse → deeper hole → higher peak stress (same mechanism as K16); a narrower cone (sin θ = 0.54/v) → cone length ∝ v → content ∝ v; higher rear κ.
- (g) Geometry around the shift unchanged up to a time rescaling; only the pure-lapse parts (hole, outer falls, cone) change (GEOMETRY_CLOSURE_PASS.md:121-134; `tests/test_speed_scaling.py:10-20`).
- (h) Peak stress grows only logarithmically; passenger aging per distance falls; the tip grows safer with speed (λ/κ 3.7 → 35); the cost moves into the front element's length.

### K3. Choreography timing: entry, coast and catch speeds, ramps, catch exit

- (a) v(σ) = v_in + (v_lane − v_in)ψ((σ−a)/τ_a) − (v_lane − v_out)ψ((σ−d)/τ_d) (CHOREOGRAPHY_PASS.md:50-53; tex:170-173; `adm_harness/constant_radius_track.py:178-182`). Catch exit = where deceleration ends.
- (b) τ_a 0.3/0.6; τ_d 0.4/0.8; coast v_out 0.8/0.9/0.95c; catch exit ℓ = 1.8/2.1/2.4; entry 0.9c (CHOREOGRAPHY_PASS.md:77-96). Compartment era: rest to rest (v_in = v_out = 0), ramps 1.5 (COMPARTMENT_PASS.md:86-89).
- (c) Ar: mean lead by coast 0.32/0.74/0.92; by exit 0.50/0.66/0.81; by τ_a 0.69/0.62; by τ_d 0.70/0.61; 131 of 144 ahead of light. Oc: all timelike (worst −0.945). Rest-to-rest in a flat compartment: coordinate speed 0 → 2.1c → 0 at zero proper acceleration (COMPARTMENT_PASS.md:56-62).
- (d) SW (lead only); gate not run per timing.
- (e) Lead trend is kinematic (arrival = ∫dz/v); values DES.
- (f) Later catch lengthens the lane (more lead) but moves the release toward the support edge, where the lapse envelope binds.
- (g) Demand not measured against timing.
- (h) Ramp times barely matter; coast speed matters most after lane speed.

### K4. Trip / lane length

- (a) Duration of the steady lane (route length at fixed v).
- (b) Trips 12.6 / 25.2 / 37.8 (FRONT_LIGHT_SURFACE_PASS.md:155-181); lanes ending σ = 6/9 (closure); long lane ending σ = 30 (ANEC).
- (c)
  - Sw: current front: matter γ 1.0×10²² / 1.3×10⁴⁷ / 1.7×10⁷², light 9.9×10⁴ / 1.3×10³⁰ / 1.7×10⁵⁵ (exponential at 9.6 e-folds/σ); shelves 10.8 fixed; cone: overtaken ≤ 5.8, pre-existing interior population levels at 14.7–14.9 (:159-181). Light-surface frequency shift over one D-lap transit 4.5×10⁹ (SOURCE_SCALING_TEST.md:179-195).
  - N: pattern demand is set by the packet's neighbourhood and independent of route length (LAPSE_AND_STAGING_PASS.md:240-243); shelf demand grows 1.58 per unit length (FRONT:215-223).
  - Src: first-light ANEC −0.0012 (12.6 trip) → −202 (long lane, first light rides the cone tip) (ANEC_MAP_PASS.md:18-26).
  - Oc: passenger time ∝ length at fixed clock (I26).
- (d) ID (horizon growth e^{κt}, I12/I13), SW (3 trips).
- (e) Exponential growth at a horizon: GEN-sub. Boundedness for cone and shelf: DES (checked on 3 lengths plus a doubled carry for the cone interior).
- (f) Front choice decides whether swept energy grows with route (current), stays fixed (shelf, cone); shelf trades that for route-proportional demand.
- (h) A structure that outruns light with a front horizon releases arbitrarily energetic matter; ANEC along first light grows by 5 orders once the lane is long enough for first light to reach the cone tip.

### K5. Plateau height (packet lapse log gain; `plateau_log`)

- (a) Log-lapse of the plateau covering the shift: D-lap `standing_support_packet_lapse_log_gain` in exp((g + ½c(ℓ−ℓ_p)²)·window) (`adm_harness/constant_radius_track.py:492-493`); compartment `plateau_log` L_p (`adm_harness/compartment_service.py` HEAD :42,94-100).
- (b) D-1S window gain 2; D-ch gain 3; D-lap e³ vs e⁴, flat plateau e¹⁰ (+sheath e⁸); D-cmp e², e³, e⁴; D-trim e³ vs e⁴, e^2.5; speed scaling +ln(v/2.1).
- (c)
  - Ty: D-lap e³ → 232 Type IV nodes, e⁴ → 0 (LAPSE_AND_STAGING_PASS.md:103-114); D-cmp e² → 22,348, e³ and e⁴ → 0 (COMPARTMENT_PASS.md:97-107); D-trim e^2.5 → 620 (GEOMETRY_CLOSURE_PASS.md:83). Worst envelope ratio 0.08 (e⁴) → 0.50 (e³) (:92-94).
  - S: e⁴ 2.91 → e³ 1.82 (−38%) → e^2.5 1.43, because the compartment hole is shallower (:90-92).
  - E: peak negative energy 0.0013 → 0.0096 (e³) → 0.0245 (e^2.5 with edge 1). The e⁴ → e³ ratio is e² = 7.39, exactly the α⁻² law of I1.
  - N: peak content 198 → 176 (e³), 138 (e^2.5).
  - Oc: D-lap packet clock = plateau lapse: e⁴ = 55; packet proper time 294 vs exterior 11.34 (LAPSE_AND_STAGING_PASS.md:178-192). In D-cmp the clock is decoupled (K16).
  - Ot: D-lap body curvature 0.31/L², normal-observer acceleration up to 0.1c²/L, 3×10¹⁶ m/s² per metre at L = 1 m (COMPARTMENT_PASS.md:4-8); single value.
  - Oθ: escape cone half-angle = arcsin(α_c/α_plateau) (I16); rear horizon κ 9.1 (pre-trim) → 7.55 (trim) (QUANTUM_ESTIMATES_PASS.md:136-137).
  - Sw: radius where the pattern lapse exceeds v: 12.2 → 12.1 (e³) (GEOMETRY_CLOSURE_PASS.md:71-74).
- (d) ID (I1 for E; I16 for cavity), SW (few values per design).
- (e) α⁻² energy scaling GEN-C0. Admissibility thresholds DES (differ by design: e⁴ needed in D-lap, e³ suffices in D-cmp/D-trim with sheath e¹).
- (f) Height vs convexity (flat plateau needs ≥e¹⁰ and still bands; convex 0.3 clears at e⁴); vs sheath (at e³ the e^0.5 sheath fails, K8); vs shift edge (envelope margin); vs clock rate (hole depth L_p − L_c sets peak stress); vs speed (must rise by ln v).
- (g) The compartment decouples passenger clock from plateau height.
- (h) Lowering the plateau lowers peak stress and content while raising the negative energy 7×; shape (convexity) substitutes for six e-folds of height.

### K6. Convexity (along-track convexity of log-lapse)

- (a) D-lap: adds ½c(ℓ−ℓ_p)² to log α inside the lapse window (`adm_harness/constant_radius_track.py:492-493`). D-cmp: convex rise of slope k over `slope_ramp` across the shift's along-track edges (`adm_harness/compartment_service.py` HEAD :94-100).
- (b) c = 0, 0.05, 0.3 (D-lap); k = 0 vs 0.5 (D-cmp).
- (c) Ty: flat 7,495 Type IV nodes and 24 banded crossings ≥2×10⁻³; 0.05 → 412; 0.3 → 0 (LAPSE_AND_STAGING_PASS.md:103-114). D-cmp no convex rise → 218 Type IV and 24 bands 2×10⁻³ (COMPARTMENT_PASS.md:105). Oc: changes the lapse near the packet by < 2% (LAPSE:88-89). S: with a wide plateau the convexity raises the edge log-lapse to ~5.8 and peak stress to 37.8 (LAPSE:136-139).
- (d) SW (3), SC (compartment).
- (e) Mechanism: p_r = −K/8π (I4) and K = −α_zz/α − n(β_z/α) + (β_z/α)² (ID-c, I4c), so convex α along z drives K negative. Threshold value DES.
- (f) Convexity × plateau width sets the edge log-lapse and hence stress (K7).
- (h) A 0.3 convexity replaces ≥6 e-folds of plateau height.

### K7. Plateau shape and service-domain cutoff

- (a) Flat-top half-length, edge width (`standing_support_packet_lapse_radius_multiplier`, `..._width_multiplier`) and the service cutoff (`service_inner`, `track_half_length`) (`scripts/run_lapse_staging_pass.py:50-85`).
- (b) Three designs: top 3.2/edge 0.6/cutoff 4–5; top 1.6/edge 1.9/cutoff 4–5; top 1.6/edge 1.9/cutoff 7.5–8.5.
- (c) S: peak 37.8 / 16.6 / 2.6; median per-σ peak 17.9 / 2.9 / 1.5 (LAPSE_AND_STAGING_PASS.md:130-139).
- (d) SC ×3. (e) DES. (f) Coupled to convexity (edge height) and cutoff (step compression).
- (h) Most of a 15× stress reduction comes from moving the cutoff away from the plateau edge.

### K8. Lapse sheath: amplitude, rise width, envelope strength

- (a) ln α += h(σ,z)E(r), E rising across `sheath_rise`, falling across `sheath_fall` (`adm_harness/axial_track.py:188-252`; tex:135-142).
- (b) D-ax0 probes: envelope log α = 2 vs 4 (AXIAL_TRACK.md:239-250). D-1S/D-ch/D-cen/D-amp: sheath e⁸ (lapse up to e¹⁶ with pre-sheath). D-lap: 0, e^0.5, e¹, e⁴ (and e⁸ with flat e¹⁰ plateau). D-cmp: 0, e^0.5, e¹. D-trim: e^0.5 vs e¹; rise width 5, 4.5, 4, 3.
- (c)
  - Ty: no sheath → 92,247 (D-lap) / 101,638 (D-cmp) Type IV; e^0.5, e¹, e⁴ pass in D-lap; e^0.5 and e¹ pass in D-cmp (plateau e⁴); e^0.5 fails in D-trim (plateau e³; 3,610) (GEOMETRY_CLOSURE_PASS.md:84). Rise compressed to 4 or 3 → 242 / 262 Type IV; the rise must span the whole shift transition (:86-90). Envelope log α = 2 → 751 Type IV; 4 → 0 (AXIAL:249-250). Bands narrow exponentially with sheath lapse (ONE_SPACE_REVISION.md:35-36).
  - E: zero (sheath adds 6,230 → 6,230; DEMAND_CENSUS.md:156-157).
  - N/Loc: standing e¹ sheath floor 53 (LAPSE:169-170); sheath rise holds 255 of 799 staged transit content (LAPSE:171-173) and 621 of 2,286 in D-cmp (COMPARTMENT:171-173). Census: sheath rise 73% NEC-respecting, pressures positive on the rise, p_z, p_φ negative on the shoulder (DEMAND_CENSUS.md:106-109).
  - Oc (not passenger): clocks inside a standing e¹⁶ sheath run 9×10⁶ × exterior (ONE_SPACE:127-129).
  - Ar (light channel): standing e⁸ sheath with e⁸ pre-sheath: along-track light α/A ≈ e⁸ ≈ 2,981, up to 1.9×10⁴; light from entry reaches ℓ = 5 at σ = 0.85 vs packet 3.34 (CHOREOGRAPHY_PASS.md:160-191). Standing e¹ sheath: local light speed 2.7 but no net lead (radial crossing costs it) (LAPSE:219-225).
  - Src: static e¹ sheath raises the QI requirement to Q = 0.60 vs 0.047 for the staged one (SOURCE_SCALING_TEST.md:344-348).
- (d) ID (zero energy I2/I10), SW (amplitude, rise width), SC (envelope 2 vs 4).
- (e) Zero energy GEN-C0. Why a *rising* lapse is needed: exact (n,z)-block terms 8π(ρ+p_z) = Δ⊥α/α − (β_r/α)², 8πT_n̂ẑ = −(1/2r)∂_r(rβ_r/α) (ID-c, I5c): a radially rising, convex-in-r lapse supplies positive Δ⊥α/α that is scale-free in α while the flux falls as 1/α. Thresholds DES.
- (f) Sheath × plateau (lower plateau needs a stronger sheath); sheath rise must cover the shift transition; standing sheath → superluminal channel and QI penalty; staging removes both (K14).
- (g) Adds stress without energy.
- (h) Above threshold the amplitude hardly matters (e^0.5–e⁴ all pass in D-lap); a standing strong sheath makes the rail a superluminal signal channel independent of the packet (lead 4.15 vs packet 1.66).

### K9. Conformal pre-sheath scale φ

- (a) ln α and ln A both += φE_c(r) (`adm_harness/axial_track.py:255-257,385-400`).
- (b) D-cen: none, e², e⁴, e⁶, e⁸ (with support stretch 630); D-amp: e³, e⁴, e⁵, e⁶, e^6.5, e⁷, e⁸ at support lapses 1/6/60/600; D-1S: e⁴ (first draft) vs e⁸.
- (c)
  - E: energy of each sign ∝ e^φ (×8 per step of 2) (DEMAND_CENSUS.md:167-169): D-cen 6.1×10⁴ (e²) → 3.39×10⁷ (e⁸); D-amp 929 (e³) → 2.2×10⁵ (e⁸) (AMPLITUDE_PASS.md:50-58). Gμ/c² along track 25 → 1.97×10⁴ (census), i.e. 13 M_⊙/m at e⁸ with support stretch, 4.4 M_⊙/m at e⁷ flat.
  - Ty: transit Type IV nodes 835 / 388 / 3 / 0 / 0 for none / e² / e⁴ / e⁶ / e⁸ (DEMAND_CENSUS.md:158-161). Resolved band widths ≥2×10⁻³ (e³), 1.4×10⁻³ (e⁴), 2.4×10⁻⁴, 5.0×10⁻⁵, 1.9×10⁻⁵, 0 (e⁷): ≈ e^(−1.5) per unit φ; nodes are Type I from e⁵ upward while bands persist to e^6.5 (AMPLITUDE:50-77).
  - N: coordinate content 179 → 239, proper 1.4×10³ → 2.3×10⁵ (D-amp).
  - Loc: 99.98% of standing energy in the pre-sheath (D-cen) (DEMAND_CENSUS.md:22-24).
  - Service curvature scaled by e^(−2φ) (ONE_SPACE:106-107).
- (d) ID (I9 flux-free; I10 energy linear in A), SW.
- (e) Energy ∝ stretch amplitude GEN-sub (static, zero shift); flux-free rise GEN-C0A; band-free threshold DES.
- (f) The central trade-off of the stretch era: admissibility (bands shrink e^(−1.5φ)) vs energy (grows e^φ). Removed by K13.
- (h) A node-level screen misses the bands (e⁵–e^6.5 all Type I at nodes).

### K10. Support stretch (C0, B0)

- (a) a_spatial = exp(q w ln C0); B = 1 + (B0 − 1) w q (`adm_harness/constant_radius_track.py:441-443`).
- (b) 630 (census) vs 1 (flat), single comparison (D-cen vs D-amp; also pre-sheath changes e⁸ → e⁷).
- (c) E 3.39×10⁷ → 7.5×10⁴; proper content 4.47×10⁷ → 8.3×10⁴; coordinate 572 → 226; share of energy beside the support 99.6% → 43%; static-frame speed 0.28 → 0.095; source speed rel. static 0.32 → 0.11; light channel arrival 0.85 → 1.23; arrival 3.34 unchanged (AMPLITUDE_PASS.md:84-109). Packet proper time 11,927 → 351, peak clock rate 9,069 → 140 (LAPSE_AND_STAGING_PASS.md:184-188). Peak stress 19.9 → 9.0 (LAPSE:166).
- (d) SC + ID (I10). (e) Energy follows the largest stretch GEN-sub; other numbers DES.
- (f) Support stretch multiplies the pre-sheath stretch.
- (h) The heritage support stretch did no work for arrival: removing it changed the lead by nothing.

### K11. Support lapse (λC0)

- (a) t_lapse = exp(q w ln(λC0)) (`adm_harness/constant_radius_track.py:442`); a standing lapse hill over the support.
- (b) 1, 6, 60, 600 on the flat support (`scripts/run_amplitude_pass.py:46-49`).
- (c) E identical for 6/60/600 (AMPLITUDE_PASS.md:79-82); N coordinate content +2–7% from 6 to 600; Ty band-free threshold e⁷ for 6/60/600, e⁸ for 1 (:63-67).
- (d) ID (energy independent of lapse, I10) + SW. (e) Energy independence GEN-sub (static, zero shift); threshold DES.
- (g) Lapse knob leaves energy unchanged (identity confirmed on data).
- (h) Any lapse hill helps admissibility (1 → 6 lowers the threshold), but 6, 60 and 600 are indistinguishable.

### K12. Stretch vs lapse (A ≡ 1 design fork)

- (a) Remove the stretch everywhere (support and pre-sheath) and give its job to lapse elements (K5, K6, K13, K8).
- (b) D-amp vs D-lap (static and staged).
- (c) E standing 7.5×10⁴ → 0; positive energy vanishes everywhere; transit peak negative energy 1.9×10⁻⁴. N standing proper content 8.3×10⁴ → 53 (static sheath) → 0 (staged). S 9.0 → 2.5 / 2.9. Src: source speed rel. static 0.11 → 0.23. Oc packet proper time 351 → 294, peak clock 140 → 55. Ar: arrival unchanged; standing-geometry light 1.23 → 5.0 (no lead). No point satisfies DEC. (LAPSE_AND_STAGING_PASS.md:157-192,219-225)
- (d) SC + ID (I1: on flat slices ρ = −β_r²/32πα² ≤ 0 everywhere).
- (e) ρ ≤ 0 everywhere and zero standing energy: GEN-C0. Demand numbers DES.
- (f) Needs four lapse elements to replace the conformal rise's flux-free property (LAPSE:75-101).
- (h) The admissibility that cost 13 M_⊙/m of standing energy via stretch costs zero standing energy via lapse.

### K13. Time staging of the sheath (static vs staged)

- (a) `sheath_follow` = (half-length 2.5, edge 1), `sheath_schedule` = on over [−4,−3], off over [1.5,2.5] (`scripts/run_lapse_staging_pass.py:60`; tex:204-208; `adm_harness/axial_track.py:214-252`).
- (b) D-lap static vs staged; all compartment-era designs staged.
- (c) Ty both Type I (3.94 M / 0.91 M points; refined 7.89 M / 1.82 M). N standing 53 → 0; transit over σ 1,616 → 799; peak instantaneous 175 → 141; minimum null −0.26/−0.48 vs −0.26/−0.47. S 2.5 → 2.9. Loc demand only σ ∈ [−3.9, 2.8], near the packet. Ar standing geometry becomes flat space. Src Q 0.60 → 0.047. (LAPSE_AND_STAGING_PASS.md:141-176; SOURCE_SCALING_TEST.md:344-348)
- (d) ID (I2: wherever the shift vanishes, a lapse that moves or switches is Type I and carries no energy) + SC.
- (e) Admissibility of staging GEN-C0; demand numbers DES.
- (h) Staging halves the transit content as well as removing the standing floor; it lowers the quantum-inequality requirement 13×, because QIs weigh long, weak deficits heavily.

### K14. Live-window gating, lapse lead and lag, packet lapse window schedule

- (a) `live_start` (shift and window switch-on), `lapse_lead` (lapse earlier), `lapse_release_lag` (lapse later) (`adm_harness/constant_radius_track.py:34-56,478-487`).
- (b) D-1S: lapse window on the live schedule (gain 2, radius 0.875) vs not; D-lap: gated (−2.4, lead 1, lag 1.5) vs open from start.
- (c) Ty: D-1S single layer 18,931 → 2,972 Type IV with the live-scheduled window; envelope violations 10 of 1,445 shift-carrying samples (ratios up to 4.1, all at packet entry where the trailing rematch shift reached the support edge before the lapse) → 0 (max ratio 0.94) (ONE_SPACE_REVISION.md:65-66,87-95). D-lap ungated: 26,895 Type IV, 20 banded crossings ≥2×10⁻³ (LAPSE_AND_STAGING_PASS.md:107). N/Loc: approach minimum −3.19 on the leading flank of the window as it switches on at σ ≈ −7 (DEMAND_CENSUS.md:32-36,196-199; AMPLITUDE:106-109).
- (d) SC; EST (envelope).
- (e) Principle (lapse must cover the shift for its whole life) supported by the envelope estimate I8; timings DES.
- (f) Window switch-on time sets the sheathed length along the track (AMPLITUDE:149-155; switching at entry would roughly halve energy — proposed, untested).
- (h) Ordering in time matters as much as amplitude: the same geometry fails by 26,895 nodes when the windows are simply left open.

### K15. Shift-transition placement, layer ordering, and shift edge width

- (a) Radial `shift_layer` (start, width) relative to lapse and stretch layers (`adm_harness/axial_track.py:56-58,114-118`); along-track `shift_width` in D-cmp (`adm_harness/compartment_service.py` HEAD :49,108-110).
- (b) D-ax0 staged probes (AXIAL_TRACK.md:239-250): shift co-located with lapse; inside lapse envelope; stretch co-located; shift before stretch; stretch before shift (static and moving, and with the stretch decaying at rate 0.3). D-1S: shift layer (3,1) vs (4.25,2). D-trim: along-track edge 2, 1, 0.75.
- (c) Ty: shift before stretch 525 Type IV; stretch before shift 0 (min null −6.30); shift inside envelope 0 (−0.09); stretch co-located 1 (−2.71); stretch decaying → band 1.3×10⁻⁵. Edge 1: content 198 → 180, stress unchanged 2.91; edge 0.75 (in trim combination): 149 → 136, envelope ratio 0.66 (GEOMETRY_CLOSURE_PASS.md:75,81-82,94-95). E: shift transition hosts the only energy density; census transit −782 there; stress flows at up to 0.32c relative to static sources (DEMAND_CENSUS.md:186,205-207).
- (d) ID (I1, I6), SC (probes), SW (edge).
- (e) Why: shear identity GEN-C0 (α = A = 1) and proper-shear statement (derivation missing for A ≠ 1, §3.3). Ordering rules DES (probes).
- (f) Shorter edge raises β_z, raising the envelope ratio (α > 2r|β_z|) and needing plateau margin.
- (h) Where the shift varies matters more than how large it is: it must vary where the lapse is high and still rising, after any stretch has returned to one.

### K16. Compartment clock rate α_c

- (a) `clock_log` L_c: log-lapse inside |ζ| ≤ 1, r ≤ 1.75; hole depth L_p − L_c (`adm_harness/compartment_service.py` HEAD :41,102-106,116-118).
- (b) Screen 0.05, 0.2, 1, 55; full gate 0.2, 1, 55 (COMPARTMENT_PASS.md:97-131); sweep 0.1, 0.2, 0.3, 0.5, 0.7, 1, 1.5, 2, 3, 5 at σ-spacing 0.2 (FRONT_LIGHT_SURFACE_PASS.md:261-281).
- (c)
  - Ty: all Type I (1,615,638 points in sweep); gate unchanged.
  - Oc: passenger proper time = α_c × 7.5 on the 12.6 trip (0.75 … 37.5); per light-year at 2.1c: 17 days (0.1) … 5.7 months (1) … 2.38 years (5).
  - Ot: speed relative to local free fall 0, acceleration 0, largest compartment Riemann component 4.4×10⁻¹⁶ at every rate (COMPARTMENT:139-144).
  - S: 6.75 (0.1), 5.41, 4.69, 3.85, 3.36, 2.91 (1), 2.44, 2.12, 1.75 (3), 1.75 (5); gate designs 5.4 (0.2), 2.9 (1), 1.75 (55).
  - N: peak content 195–201 across the sweep; minimum null −1.45 (0.1) → −0.61 (5).
  - E: peak negative energy 1.3×10⁻³ at 0.2, 1, 55 (COMPARTMENT:164).
  - Loc/placement: radius without static frames 2.45 (0.1) → 0 from 3 upward (static frames exist where α > |β|); static units can sit wherever the deficit lies (COMPARTMENT:181-192).
  - Oθ: measured at clock 1 only (2.75 mK at L = 1 m). Tolman gives T = κ/(2πN) with N = α_c (QUANTUM_ESTIMATES_PASS.md:139-142), so the read temperature scales as 1/α_c — inferred, not computed. Escape cone arcsin(α_c/α_plateau) — inferred for α_c ≠ 1.
  - Ar: unchanged (lead 5.1).
- (d) ID (I3, I2, I26) + SW.
- (e) Clock, tides, acceleration, gate invariance: GEN-C0. Stress trend and saturation at 1.75: DES.
- (f) Hole depth couples clock rate to plateau height (and so to speed, K2).
- (g) Clock rate leaves the gate and the NEC content (±3%) unchanged.
- (h) A 50-fold clock change moves peak stress 4× and content 3%; very slow clocks (deep holes) cost stress, fast clocks saturate at the surroundings' floor.

### K17. Hole boundary sharpness and radius

- (a) `hole_edge` (along track), `hole_radius` (radial start, width).
- (b) Along-track edge 1 vs 0.5 (screen only).
- (c) Ty: both pass (COMPARTMENT_PASS.md:104). Loc: hole boundary holds 157 of 2,286 content at clock 1 (:171-174). Oθ: photon trace-anomaly peak on the axis at the hole boundary, 0.375 beyond the flat interior; vanishes inside (<10⁻²⁷) (QUANTUM_ESTIMATES_PASS.md:21-23,86-89).
- (d) ID (I2) + SC. (e) Gate invariance GEN-C0.
- (h) The passengers' nearest curvature and the largest vacuum-polarization stress sit at the compartment's own wall.

### K18. Outer fall placement and sheath rise width (trimming)

- (a) `lapse_layer` / `sheath_fall` start and width; `sheath_rise` width.
- (b) Outer fall from 9.25 (width 4) → 8.75 (width 2); rise 5 / 4.5 / 4 / 3 with fall from 8.25 / 7.75 / 7.25 (`scripts/run_geometry_closure_pass.py:41-59`).
- (c) Ty: pull-in to 8.75 passes; rise ≤ 4 fails (242, 262). N: content 198 → 190 (8.75); 179 / 168 / 155 for the three compressed variants. Sw: radius where α > v 12.2 → 10.2 → 9.7 / 9.2 / 9.1 → cone base 16 → 14, cone length 66.5 → 58.0 (GEOMETRY_CLOSURE_PASS.md:71-95,112). Loc: outer falls hold most content: 1,334 of 2,286 (D-cmp), 456 of 799 (D-lap staged), 491 of 572 coordinate (D-cen); governing QI points and the F(φ)R zero at r ≈ 10.65 lie there (SOURCE_SCALING_TEST.md:114-142,289-294).
- (d) ID (I2: pure lapse where shift vanishes; I18 sign) + SW.
- (e) Freedom to move the fall GEN-C0; magnitudes DES.
- (f) Fall radius ↔ cone base ↔ cone length ↔ cone content; rise width ↔ shift-transition coverage.

### K19. Front element: current front, forward shelf, conical front

- (a) Log-lapse term added only ahead of the shift's front edge (`adm_harness/front_surface.py` HEAD :63-170).
- (b) Current, running shelf (edge 3.5c), static shelf (edge ∞), 15° cone; trips 12.6/25.2/37.8.
- (c) (FRONT_LIGHT_SURFACE_PASS.md:159-249)
  - Sw: see K4. Horizons: current front is a white-hole disk, κ 9.1–9.7, null within 1.2% to r = 8; cone surface timelike wherever r > 0 (ratio 2.64 at r = 0.5, 3.3–4.3 beyond) (CONE_TIP_FIELD_PASS.md:16-24,73-83). Both keep a rear black-hole disk.
  - N: peak content 198 / 248 / 251 / 333; over σ 2,295 / 2,747 / 2,783 / 3,114; beyond ζ = 8.25: 0 / 383 / 419 / 518. Shelf 1.58 per unit route length (2.1×10²⁷ kg/m; 10¹³ M_⊙/ly).
  - S: 2.91 for all four. Ty: all Type I; front-element minimum null −0.11 (shelves), −0.16 (cone).
  - Ar/causal: shelf lets packet signals reach 18 of 19 route points before the pattern, lead growing 0.109 per unit distance; cone signals travel inside it (leads to 9) and stop at its surface; current front none.
  - Oc/Ot: compartment unchanged (`tests/test_front_surface.py:52`).
  - Src: tip field evolution: modes rise ≤1.6× and leave; flat front with same axial lapse grows at 2κ (CONE_TIP:26-40).
- (d) SC per element; ID for gain laws (I12) and horizon criterion (I13).
- (e) Gathering mechanism and its two cures (lapse ahead > v everywhere; or a tilted surface) GEN-sub; costs DES.
- (f) Shelf: causal control and no light surface vs route-proportional demand. Cone: fixed +68% peak content vs a surviving (axis-only) light surface.
- (g) Front elements leave the fields around the compartment and shift unchanged.

### K20. Cone half-angle, layer, tip rounding, base, lapse

- (a) θ_c, `layer`, `rounding`, `base_radius`, `log_lapse` (`adm_harness/front_surface.py` HEAD :121-170).
- (b) Stationary screen at 2.1c: 15°, 22°, 30°, 45°; layers 5 and 2; rounding 0.5 and 2 (`scripts/run_cone_front_checks.py`). Reference 15°/layer 3/rounding 0.5/lapse 1.5/base 16 → 14. Speed rules: fixed 15°; sin θ_c = 0.54/v (K2).
- (c) Sw: largest near-axis gain 1.0–4.9 (15°), 10–20 (22°), 500–10⁵ (30°), 10⁶–10¹⁵ (45°); rounding 2 raises 15° gains to 10–42 (FRONT_LIGHT_SURFACE_PASS.md:139-149). Tip κ = 0.563, −∂²_rα = 4.20, λ = 2.70 (CONE_TIP:92-104). N: cone length = base/tan θ_c; +68% peak content vs current front (FRONT:215-216). Src: on the axis T(k,k) = α_rr/(4πα) < 0 inside the cone, so the first light carries negative ANEC (ANEC_MAP_PASS.md:27-31). Bundles: fan grazing the tip → fold caustic (width 9×10⁻⁴, 14 crossings), energy bounded (GEOMETRY_CLOSURE:254-258).
- (d) SW (angle), SC (rounding, layer), ID (I15 flank; I18 axial sign), EST (I14 tip rate).
- (e) Flank criterion GEN-sub (any lapse front moving through a flat exterior); angle-gain numbers DES.
- (f) Angle ↔ length ↔ content; angle ↔ speed (v sin θ_c < 1); rounding ↔ axial lapse curvature ↔ tip shedding.
- (h) Wider cones and blunter tips are worse; a slender, sharply peaked cone sheds best.

### K21. Shelf lapse α_s and leading-edge speed

- (a) `ForwardShelf.log_lapse`, `lead_speed` (`adm_harness/front_surface.py` HEAD :63-118).
- (b) α_s = e¹ only; lead 3.5c vs ∞ (static).
- (c) Sw: γ' = (α_s² + v²)/(α_s² − v²) = 3.96; exit through resting terminal α_sγ' = 10.77; light 2.72 (static) or ×(u−1)/(u−α_s) = 3.2 → 8.7 (running) (FRONT:120-131,167-170). N: 1.58 per unit length; running shelf holds ≤0.4 of the route at once. Ar: signal lead 0.109 per unit distance (≈40 days per light-year at L = 1 m).
- (d) ID (I12 shelf law) + SC. (e) Swept-γ law GEN-sub (1D, α_s > v); costs DES.
- (h) The shelf makes the carry causally steerable from the packet during transit, at a route-proportional cost.

### K22. Reset schedule of a decompressing support (CS, transferred to the axial core)

- (a) Decompression q(σ): uniform; after the live window at quarter rate; trailing front at full/half/quarter local rate (onset σ_on(ℓ) = σ₀ + w I((ℓ−ℓ₀)/w)/v) (RESET_SCHEDULE_OPTIONS.md:41-54; `adm_harness/constant_radius_track.py:358-365`).
- (b) Five schedules (+ four extended-carry variants, K23).
- (c) N (angular): minimum −0.270 (current) → −0.052 (all slow, the catch-phase floor); deficit integral 0.373 → 0.0063 (−98%) / 0.0727 (half-rate front, −80%) (RESET:63-73). Ar: velocity-reading delivery delay +2.07 / +4.06 / +7.28 / +6.99. Oc: live packet norm margin −9.94 → −11.92. Axial core (no 1/8πR² cushion): p_Ω deficit reduction only 60–72% (:161-175). Ty (axial boundary layer, D-ax0): Type IV share 20% → 7% but samples with Type IV 2,844 → 7,871 (AXIAL:175-177).
- (d) SW. (e) DES; the transfer to the axial core uses I4.
- (h) The spherical cushion absorbs weak curvature, so slow resets help much less in a flat-transverse core; slowing the reset thins each band but spreads it over more samples.

### K23. Extended carry (CS)

- (b) Catch moved later by 0.4, 0.8, 1.2, 2.2 at V = 5.
- (c) Ar: delivery +5.39, +2.24, −1.47, −7.84 vs current. N: minimum −0.247 / −0.598 / −0.707 / −0.808; peak curvature 7.1 → 20.6. Oc: packet margin −8.48 → +6.82 (3 spacelike points at 2.2); feasible shift ends between 1.2 and 2.2 (RESET:22-30,70-73,84-90).
- (d) SW. (e) DES.
- (h) Earlier delivery comes from carrying at V through more of a weakening support, at 4.7–13.6× the local deficit floor.

### K24. Support dynamics: decompressing vs held vs static; carve

- (a) `standing_support` (spatial metric static; carve and γ windows removed) vs `hold_support` (no decompression; carve kept) (`adm_harness/constant_radius_track.py:269-277,358-365,432`).
- (b) D-1S and D-ch comparisons.
- (c) Ty: single layer 74,700 → 18,931 (held); final stack: held 1 Type IV, 22/60 samples with bands (2.2×10⁻⁵); static 0, no bands (ONE_SPACE_REVISION.md:62-71). With path choreography, held+carve → 25/60 banded (3.2×10⁻⁵); static → 0 (CHOREOGRAPHY:34-38,106). Ar: packet-coordinate advantage 1.233 → 1.195 (held) → 0.352 (static, window reading); velocity-read arrival 10.1 → 23.4 → 39.8 (ONE_SPACE:135-155). N: service-region minimum −0.283 → −0.153 (ONE_SPACE:52-56). Oc: live packet norm −9.94 → −194 → −1,716.
- (d) SC. (e) DES; the general lesson (time-dependent stretch splits the Hessians) is I7.
- (h) The carve carried the speed advantage and the residual bands together; a path-matched shift on a static support restores the lead band-free.

### K25. Single-layer boundary width, spacing, service-region radius, string cushion (D-ax0, stretch-bearing)

- (b) Width 0.5, 1, 2, 4; logarithmic 4 and 16; region radius 1, 1.75, 3; string cushion K_Σ = 1/1.75².
- (c) Ty: Type IV persists at 16–21% of layer points for every width (AXIAL_TRACK.md:149-171). N: static minimum −6.40 (0.5) → −0.052 (log 16) ≈ 1/w²; static radial ANEC −0.603 → −0.022 ≈ 1/w; layer content stays ≈ 90–210 ("a stretch of log 800 = 6.7 relaxes across the transverse plane at a cost set by the plane's logarithmic capacity", :165-171); service-region content 1.38 / 4.23 / 12.44 (∝ area). Cushion: minimum −0.283 → −0.270 at a 4.53 rad (72%) deficit angle (:136-140). D-1S wide vs narrow stacks: −2.65 vs −10.62, content 490 vs 592, outer radius 13.25 vs 7.5 (ONE_SPACE:157-169).
- (d) SW. (e) DES; 1/w², 1/w are dimensional; the log-capacity statement is an argument without derivation.
- (h) Widening redistributes cost but never removes Type IV: its origin is a sign structure (I6, I7), not a magnitude.

### K26. Termination: two-ended spherical track vs one space; end-transition width, track length, track radius (CS)

- (b) End-transition width 0.75, 1.5, 3.0; half-length 4.5, 6.0; radius 1.4, 2.14.
- (c) Ty: all Type I (40,071 points each). N: peak static radial deficit −0.118 / −0.058 / −0.028 while the integrated opening measure stays fixed at 1 per end (CONSTANT_RADIUS_TRACK.md:181-185,322-334). Axial one-space alternative: ends removed, but the transverse layer carries ≈12× the static negative-null content (AXIAL:272-284).
- (d) ID (I24 opening theorem) + SW. (e) Opening requirement GEN-sub (static spherical, topology-driven).
- (h) Width redistributes the deficit; the integral is topological.

### K27. Physical scale L (and QI sampling fraction f)

- (a) Rail unit length L; f = τ₀/(local curvature or inverse-acceleration scale) in the QI test.
- (b) L = 204 ℓ_P (recorded normalization), 1 μm, 1 mm, 1 m, 10 m, 100 m, 1 km; f = 0.01, 0.1, 0.3.
- (c) S ∝ 1/L² (D-lap peak 3.5×10⁴⁴ Pa at 1 m); energies/contents ∝ L; energy per unit length scale-free (DEMAND_CENSUS.md:223-227). Src: N ≥ Q(L/ℓ_P)², Q = 0.013 (f = 0.1), 3×10⁻⁶ (f = 0.01); species length √Q L = 0.12L equals the sharpest curvature radius 0.117L; L ≤ 0.45 mm (f = 0.1) or 2.9 cm (f = 0.01) (SOURCE_SCALING_TEST.md:144-177). Casimir gap a = 0.58√(ℓ_P L); mirror energy exceeds deficit by ~10⁷ at every gap (:197-232). Trace anomaly/demand ∝ (ℓ_P/L)² (~2×10⁻⁷⁰ at 1 m) (QUANTUM:14-19). Oθ: horizon temperature ∝ 1/L (2.75 mK at 1 m, 2.8 μK at 1 km). Ot: D-lap tides 3×10¹⁶ m/s² per metre at 1 m (∝ 1/L²).
- (d) ID (dimensional; QI inequality; species bound; Casimir formula) + computed tables.
- (e) Scalings GEN-any (for a fixed shape); Q values DES (D-lap staged only).

---

## 3. Identities

### 3.1 Identities stated in the reports

**I1. Flat-slice energy density.** With A ≡ 1, 16πρ = K² − K_ijK^ij, K_ẑẑ = β_z/α, K_ẑr̂ = β_r/2α, hence
ρ = −(β_r/α)²/32π.
Source: LAPSE_AND_STAGING_PASS.md:56-73; tex:154-166, 247-262. Validity: class C0 (flat static slices, shift along z depending on σ, z, r); any lapse. Consequences: ρ ≤ 0 everywhere in C0; the lapse enters ρ only as the α⁻² suppression of the radial shear; β_z contributes nothing. The report writes the formula with a factor A (−(Aβ_r/α)²/32π) while stating A = 1; for A ≠ 1 extra stretch terms enter and the formula as written is not established (§3.3). Confirmed on data: plateau e⁴ → e³ raises the peak negative energy by e² exactly (GEOMETRY_CLOSURE_PASS.md:81; 0.0013 → 0.0096). ID-c verified.

**I2. Pure-lapse identity (shift-free or shift-uniform regions).** Where the spatial metric is static and flat and the shift is spatially uniform (including zero), K_ij = 0, so ρ = 0, j_i = 0 and
8πT_ij = (δ_ij D²α − D_iD_jα)/α,
Type I for any α(σ, x), including any time dependence. Sources: tex:162-166; LAPSE_AND_STAGING_PASS.md:69-73; COMPARTMENT_PASS.md:64-69; FRONT_LIGHT_SURFACE_PASS.md:105-107; GEOMETRY_CLOSURE_PASS.md:86-88. The general flux statement (static spatial metric + zero shift ⇒ zero Eulerian flux for any lapse, via the momentum constraint) is GEN-any: AXIAL_TRACK.md:227-231, `tests/test_axial_track.py:340-350` (static z-dependent stretch, time-dependent lapse), `:476-483` (sheath alone). Used to justify: time staging (K13), outer-fall placement (K18), hole boundary (K17), clock-rate invariance (K16), front elements (K19), speed scaling (K2).

**I3. Uniform-field flatness.** If α = α(σ) and β = β(σ) on a region, then t = ∫α dσ, x = z + ∫β dσ make the metric Minkowski; normal observers are geodesic (acceleration D ln α = 0); a packet carried at β = −v rests on them and ages at rate α. Source: COMPARTMENT_PASS.md:54-62; `adm_harness/compartment_service.py` HEAD :1-23; test `tests/test_compartment_service.py:51`. GEN-C0.

**I4. Product (service-region) identity.** For a product of a 2D Lorentzian service metric (Gaussian curvature K) with a transverse 2D metric of curvature K_Σ: T = diag(K_Σ, −K_Σ, −K, −K)/8π in (n, z, r, φ); along-track null energies vanish; minimum null energy min(0, (K_Σ − K)/8π). Source: AXIAL_TRACK.md:98-105,127-129; tex:146-152; test `tests/test_axial_track.py:125`. GEN-any for products. Spherical analogue: ρ = −p_ℓ = 1/8πR², p_Ω = −K/8π (CONSTANT_RADIUS_TRACK.md:75-95).
- **I4c (ID-c)**: the report sign convention corresponds to K = −α_zz/α − n(β_z/α) + (β_z/α)², n(f) ≡ α⁻¹(∂_σ − β∂_z)f (derived from the full tensor, §3.2). Convex lapse along z ⇒ K < 0 ⇒ p_r > 0.

**I5. Momentum flux of the shift (report form, approximate).** "A lapse gradient under a shift that varies along the track carries a radial energy flux 8πT_n̂r̂ ≈ −a′β_z/α, against the null-energy term 8π(ρ+p_r) ≈ a′/r" (a = ln α). Source: ONE_SPACE_REVISION.md:87-95; tex:193. Status: leading terms of the exact expressions in §3.2 (EST as stated).
- **I5c (ID-c) exact forms**: 8πT_n̂ẑ = −(1/2r)∂_r(rβ_r/α); 8πT_n̂r̂ = (1/2α²)∂_z(αβ_r) − (β_z/α)∂_r ln α. Flux is linear in β and O(1/α); energy is quadratic and O(1/α²).

**I6. Shear identity.** In a layer with α = A = 1 and any β(σ,z,r):
8πT(n ± e_z, n ± e_z) = −(β_r² ± Δ⊥β), Δ⊥β = β_rr + β_r/r;
Type IV wherever |Δ⊥β| > β_r², which always happens where a shift begins to vary and across the whole layer for a weak shift. Source: AXIAL_TRACK.md:191-204; test `tests/test_axial_track.py:297-317`. GEN-C0 (α = 1). The general-lapse extension (flux scales with proper shear Aβ_r/α, suppressed where A/α ≪ 1; AXIAL:252-256; ONE_SPACE:99-102) is stated without derivation (§3.3); for A = 1 it follows from I5c.

**I7. Hessian identity (stretch, zero shift).** For z-independent fields and β = 0, the axial metric is a doubly warped product over (σ, r):
8πT(k±,k±) = −∇_{k±}∇_{k±}A/A − ∇_{k±}∇_{k±}C/C, k± = n ± e_r; for C = r the second term is α_r/(rα).
Static: both Hessians equal. Time dependence splits them by the mixed Hessian; a band opens where their static part changes sign. Band width grows linearly with the decay rate; translation gives bands ≈4.7× narrower (SW table). Source: AXIAL_TRACK.md:206-225; test `tests/test_axial_track.py:320-337`. GEN-sub (C0A, z-independent, zero shift).

**I8. Lapse envelope (heuristic).** Type I requires α > 2r|β_z| wherever the lapse varies radially under a shift that varies along the track. Source: ONE_SPACE_REVISION.md:87-95; tex:114. Status: EST. Compiler reconstruction: it is the (n,r)-block discriminant condition (ρ + p_r)² > 4T_n̂r̂² evaluated with only the leading terms 8π(ρ+p_r) ≈ α_r/(rα), 8πT_n̂r̂ ≈ −α_rβ_z/α² (neglects α_zz/α, the n(K) − K² terms, β_rz, α_zβ_r and the coupling to the (n,z) block). The reports call it "the sufficient estimate, and the classifier decides" (CHOREOGRAPHY_PASS.md:114-119); Type I was found at ratios up to 1.59 (AMPLITUDE_PASS.md:111-113), so it is neither necessary nor exact.

**I9. Conformal rise is flux-free.** Where ln α and ln A rise together (a_r = b_r) the radial flux vanishes exactly even under a moving shift that varies along the track: A_σ/α is r-independent and the gradients cancel in β_z(b_r − a_r). The pre-sheath scales service curvature by e^(−2φ). Source: ONE_SPACE_REVISION.md:103-107; test `tests/test_axial_track.py:519-526` (shift layer placed outside the rise). Validity requires β_r = 0 across the rise (not stated explicitly; §3.3). GEN-C0A.

**I10. Static energy and Komar balances.** Static, β = 0, spatial metric dr² + r²dφ² + A²dz²: 16πρ = R⁽³⁾ = −2Δ⊥A/A, so ρ√γ = −(1/8π)∂_r(r∂_rA), which integrates to zero across every z-slice; the lapse enters only through 4πα(ρ + Σp_i) = D²α, whose integral also vanishes (zero Komar mass, as the exactly flat exterior requires). A lapse maximum carries negative active mass on its shoulders and positive on its flanks. Checked to 2.6×10⁻⁴ (12-node) and 10⁻¹⁶ (dense rule). Source: DEMAND_CENSUS.md:126-149. GEN-sub (static, zero shift; A may depend on z). Consequences: energy each sign follows the stretch amplitude (pre-sheath e^φ law, K9); support lapse leaves energy unchanged (K11).

**I11. Speed scaling isometry.** Around the shift the metric depends on α dσ and β dσ; (α, β) → (cα, cβ) with σ → σ/c is an isometry, so raising the log-lapse by ln(v/v₀) wherever the shift is non-zero gives the same local geometry at carry speed v. Source: GEOMETRY_CLOSURE_PASS.md:121-134; test `tests/test_speed_scaling.py:10-20` (HEAD) asserts agreement to 10⁻³ of the tensor scale at mid-lane for v = 1.5 and 10; the report quotes 10⁻⁵. Validity: exact during a steady lane (pattern-frame stationarity); ramps are time-compressed, not identical; requires the lapse to be multiplied everywhere the shift is non-zero (true for the trim design: plateau covers r ≤ 8.75 ⊃ shift transition, `scripts/run_geometry_closure_pass.py:69-85`). Data confirm constant peak negative energy and envelope ratio across 1.5–20 (`data/geometry_closure_pass/speed_scan_scaled.csv`). GEN-C0.

**I12. Killing-energy laws in the pattern frame.** During a steady lane the pattern-frame metric (b = β + v) is stationary, so E = α√(m² + |k|²) − b k_z is conserved. Where the shift vanishes, d ln|k|/dσ = −k̂·∇α; kept gain for light that starts and ends in the exterior exp(v∫(−∂_ζ ln α)dσ) (FRONT_LIGHT_SURFACE_PASS.md:62-78). Exit-angle law for light overtaken in the steady lane: gain = (v − 1)/(v cos θ_f − 1), verified on 20 exits to 3×10⁻⁹ (:139-141). Shelf law: matter at rest in a shelf of lapse α_s > v leaves at γ' = (α_s² + v²)/(α_s² − v²) and exits a resting terminal at α_sγ' (:120-131). GEN-sub (stationary pattern frame, flat exterior).

**I13. Killing-horizon criterion.** On S: α² = b² the normal n = ∇(α² − b²) has norm (1 − b²/α²)n_ζ² + n_r² = n_r², so S is null (a Killing horizon) exactly where its transverse gradient vanishes, and timelike (crossable) elsewhere; surface gravity κ = |∂_ζα| on the null part where the shift vanishes. Source: CONE_TIP_FIELD_PASS.md:61-71; QUANTUM_ESTIMATES_PASS.md:111-117. GEN-sub (stationary pattern frame of C0). Consequences: front fall with no transverse gradient = white-hole disk (energy density of modes grows as e^{2κt}); rear fall = black-hole disk (Hawking-like flux at κ/2π).

**I14. Tip shedding rate (estimate).** λ = ½(√(κ² + 4v(−∂_r²α)) − κ); mode energy density at the tip changes as 2(κ − λ). Source: CONE_TIP_FIELD_PASS.md:92-104. EST ("in this estimate"); paraxial derivation not shown. Field evolution agrees qualitatively (tip density decays 1.6–4.0 per unit time; flat front grows 1.07–1.10 ≈ 2κ = 1.13).

**I15. Flank normal-speed criterion.** A front surface whose normal makes angle θ_c with the radius moves along that normal at v sin θ_c; since the layer holds every lapse from 1 to its interior value, light moving along the normal can ride the flank once v sin θ_c > 1. Source: GEOMETRY_CLOSURE_PASS.md:29-36,136-147; test `tests/test_speed_scaling.py:23-27`. Kinematic, GEN-sub (lapse front moving through a flat exterior). Confirmed by the fixed-15° scan (threshold 3.9 between v = 3 and 5).

**I16. Lapse cavity.** Where the shift is uniform (pattern frame static) a lapse acts on light as refractive index 1/α with α|k| conserved; light leaving a region of lapse α_in into α_out is totally reflected unless within arcsin(α_in/α_out) of the normal. Source: GEOMETRY_CLOSURE_PASS.md:205-218. GEN-sub (Fermat for static pure-lapse regions).

**I17. Tolman reading of horizon flux.** Passengers read κ/(2πN), N = √(α² − b²) (N = 1 at the unit clock). Source: QUANTUM_ESTIMATES_PASS.md:139-142; test `tests/test_quantum_estimates.py:52`. GEN-sub.

**I18. Null energy of pure-lapse regions.** On the axis, for light along the axis, T(k,k) = α_rr/(4πα) (negative where the lapse peaks on the axis) (ANEC_MAP_PASS.md:27-31). Static radial ray: ∫T(k,k)dλ over the falls = (E/8π)∫α′/(rα²)dr, negative wherever the lapse drops back to one (SOURCE_SCALING_TEST.md:289-292). ID-c generalization from I2: for any unit spatial direction e, 8πT(n+e, n+e) = (Δα − ∂_e²α)/α (the transverse Hessian of α). Axisymmetric α(r, z): radial light (α_zz + α_r/r)/α; axial light (α_rr + α_r/r)/α; azimuthal light (α_rr + α_zz)/α. So every lapse hill that returns to one violates radial NEC on its fall, and violates axial/azimuthal NEC on its concave shoulder.

**I19. Global time and one-rail causality.** g^{σσ} = −1/α² < 0 everywhere, so σ is a global time function on a single rail (CHOREOGRAPHY_PASS.md:187-191; tex:315). GEN-C0. Two rails in relative motion can close causal curves (stated by analogy with Krasnikov tubes; no computation).

**I20. Light speeds and static frames.** Radial null rays of one family obey dℓ/dσ = −β ± α/√γ_ℓℓ, so rays of a family stay ordered (CHOREOGRAPHY_PASS.md:152-154). Along-track light in the pattern-free standing geometry moves at α/A (:163-165). Static observers (fixed z, r, φ) exist iff α > |β| (C0), which is why they are absent inside a low-lapse compartment carried at 2.1c (COMPARTMENT_PASS.md:183-192). GEN-C0.

**I21. Source-scaling identities.** Fewster–Roman bound ⇒ N ≥ 64π² d τ₀⁴ (L/ℓ_P)² ≡ Q(L/ℓ_P)² (SOURCE_SCALING_TEST.md:75-92); species length ℓ* = √Q L (:157-166); Casimir gap a = 0.58√(ℓ_P L) and ~10⁷ mirror overhead (:197-232). F(φ)R theories: F″ ≤ 8πT(k,k)F along affinely parametrized null geodesics; F vanishes by the first zero of ψ″ = 8πT(k,k)ψ; zero count = bound states of −d²/dλ² + 8πT(k,k), scale-free (:240-263). Validity as stated there (flat-space QI form requires τ₀ short vs curvature and inverse acceleration).

**I22. Trace anomaly.** ⟨T^μ_μ⟩ = (cW² − aE)/16π² · ħc/L⁴ for conformal fields, R² counterterm omitted (QUANTUM_ESTIMATES_PASS.md:42-56); zero in the flat compartment (test `tests/test_quantum_estimates.py:44`). GEN-any for conformal fields.

**I23. Lead over light needs achronal ANEC violation.** "The design needs negative ANEC along achronal light rays, as any lead over exterior light does" (ANEC_MAP_PASS.md:41-51). Stated as general; the general theorem is not cited (§3.3). Measured: first light −0.0012 to −2.2×10⁴.

**I24. Spherical (CS) identities.** 8πT(k,k) = −(2/R)k^ak^b∇_a∇_bR for radial null k; Δ_rad = (ρ + p_ℓ)² − 4j_ℓ² = T(k₊,k₊)T(k₋,k₋), so Type IV exactly where the two radial null energies have opposite signs (CONSTANT_RADIUS_TRACK.md:33-49). Static region with lapse A: (R′/A)′ = −(4πR/A)(ρ + p_ℓ), so widening from R′ = 0 to R′/A = 1 needs integrated radial deficit ≥ 1 per end (:326-334). String boost invariance of the radial block (:92-95). GEN-sub (spherical).

**I25. Dimensional scaling.** Fixed shape: stresses ∝ 1/L², energies and contents ∝ L, energy per unit length ∝ c²/G × shape factor (DEMAND_CENSUS.md:223-227; tex:355-357). GEN-any.

**I26. Passenger aging.** Along a lane at speed v, a passenger in a compartment of lapse α_c ages α_c/v of light's crossing time per unit distance (COMPARTMENT_PASS.md:146-154). GEN-C0 (follows from I3).

### 3.2 Complete demanded tensor of class C0 (ID-c; not stated in the reports)

Symbolic computation for ds² = −α²dσ² + (dz + β dσ)² + dr² + r²dφ² with α(σ,z,r), β(σ,z,r), orthonormal frame
n = (∂_σ − β∂_z)/α, e_z = ∂_z, e_r = ∂_r, e_φ = r⁻¹∂_φ (scripts: `scratchpad/textbook/verify_identities.py`, `verify_compact.py`).
Notation: s ≡ β_r/α (proper radial shear), 𝒦 ≡ β_z/α (trace of extrinsic curvature), n(f) ≡ α⁻¹(∂_σ − β∂_z)f, Q ≡ n(𝒦) − 𝒦², Δ⊥f = f_rr + f_r/r.

| Component | 8π × component |
|---|---|
| T_n̂n̂ = ρ | −s²/4 |
| T_n̂ẑ | −(1/2r)∂_r(r s) |
| T_n̂r̂ | (1/2α²)∂_z(α²s) − 𝒦 ∂_r ln α |
| T_ẑẑ | Δ⊥α/α − 3s²/4 |
| T_r̂r̂ | (α_zz + α_r/r)/α + s²/4 + Q |
| T_φ̂φ̂ | (α_rr + α_zz)/α − s²/4 + Q |
| T_ẑr̂ | −α_rz/α − ½n(s) + s𝒦 |
| T_n̂φ̂, T_ẑφ̂, T_r̂φ̂ | 0 |

Derived null sums: 8π(ρ + p_z) = Δ⊥α/α − s² (no time derivatives); 8π(ρ + p_r) = (α_zz + α_r/r)/α + Q; 8π(ρ + p_φ) = (α_rr + α_zz)/α − s²/2 + Q. Checks: β = 0 reproduces I2; α = 1 reproduces I6; r-independent fields give p_r = p_φ = −K/8π with I4c; ρ reproduces I1; leading terms reproduce I5 and I8. Reading: the lapse enters every null sum through its flat-space Hessian divided by α (scale-free), the shift's shear enters quadratically and suppressed by α⁻², and the fluxes are linear in β and suppressed by α⁻¹ — the algebraic reason a high, radially rising lapse around the shift transition keeps the tensor Type I.

### 3.3 Identities with missing derivations or unclear validity

1. **Proper-shear flux scaling with stretch** ("the shift's flux scales with the proper shear Aβ_r/α; the lapse suppresses it wherever A/α ≪ 1"; AXIAL_TRACK.md:252-256; ONE_SPACE_REVISION.md:99-102): stated, no derivation; §3.2 covers A = 1 only.
2. **I1 written with A**: LAPSE_AND_STAGING_PASS.md:16 writes ρ = −(Aβ_r/α)²/32π "with the stretch equal to one everywhere"; the A is decorative and the formula does not hold for non-constant A.
3. **Lapse envelope I8**: approximate; neglected terms unstated in the reports; observed Type I at ratios up to 1.59 and one-per-lane exceedances at 1.06–1.59 (CHOREOGRAPHY_PASS.md:114-119).
4. **Conformal flux-free I9**: requires β_r = 0 across the conformal rise (implicit in the stack ordering and test geometry, not stated).
5. **Speed scaling I11**: exact only during a steady lane; the report's 10⁻⁵ agreement vs the test's 10⁻³ tolerance; the lapse must be scaled everywhere the shift is non-zero.
6. **Tip rates I14**: paraxial estimate; derivation not shown.
7. **I23 (lead needs achronal ANEC violation)**: asserted generally without citing a theorem (the relevant general result appears to be the Gao–Wald time-delay theorem; not cited in the repo reports).
8. **Hessian identity I7**: exact for z-independent fields and zero shift; the reports apply it qualitatively to z-dependent, shifted services.
9. **Log-capacity argument** for constant layer content (AXIAL_TRACK.md:167-169): argument without derivation.
10. **Lapse-maximum dynamics** ("free particles fall away from a lapse maximum… the sheath holds the packet… and deflects exterior matter", ONE_SPACE_REVISION.md:129-131): Newtonian-limit statement, not measured.
11. **Service-curvature formula K**: reports use K throughout without an explicit formula; the code computes it as −`product_rr` (`adm_harness/axial_track.py:416-421`); §3.2 supplies it.
12. **Rear-horizon flux**: relies on 1+1 results (Finazzi et al.); κ varies 7.55–8.3 across the disk; 3+1 renormalized stress not computed (CONE_TIP_FIELD_PASS.md:159-172).
13. **Exterior mixing**: only an upper bound at the level of the window-edge control (QUANTUM_ESTIMATES_PASS.md:185-198).
14. **Radial falls ANEC (I18)**: sign on each fall is pointwise; the net integral over a whole hill is not established in general.

---

## 4. Coupling matrix

Codes: **I** identity-backed for the class (or stated sub-class), **i** estimate/heuristic or identity-inferred but not computed,
**M** measured sweep (≥3 values), **S** single comparison, **·** untested. Combinations like I/M mean both.
Columns as in §0.4.

| Knob | E | N | S | Loc | Ty | Oc | Ot | Oθ | Ar | Sw | Src |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K1 Lane speed (choreography era) | · | S | · | S | M | M (norm) | · | · | M | · | · |
| K2 Carry speed, lapse scaled (closure) | I/M | M | M | M | I/M | I | I | I/S | M | M | S |
| K3 Choreography timing | · | · | · | · | · | M (norm) | · | · | M | · | · |
| K4 Trip/lane length | · | i/M (shelf) | · | · | · | I | · | · | M | I/M | S |
| K5 Plateau height | I/M | M | M | · | M | I | S | i/S | · | S | · |
| K6 Convexity | · | · | S | · | M | S | · | · | · | · | · |
| K7 Plateau shape / cutoff | · | · | S | · | · | · | · | · | · | · | · |
| K8 Sheath amplitude / rise / envelope | I | S/M | · | S | M | S (sheath clocks) | · | · | S (light channel) | · | S |
| K9 Conformal pre-sheath | I/M | M | · | M | M | · | · | · | S | · | · |
| K10 Support stretch | I/S | S | S | S | S | S | · | · | S | · | S (source speeds) |
| K11 Support lapse | I/M | M | · | · | M | · | · | · | · | · | · |
| K12 Stretch → lapse (A ≡ 1) | I/S | S | S | S | S | S | · | · | S | · | S (source speeds) |
| K13 Time staging | I | S | S | S | I/S | · | · | · | S | · | S |
| K14 Live-window gating, lead, lag | · | S | · | S | S | · | · | · | · | · | · |
| K15 Shift placement / ordering / edge | I/M | M | M | · | S/M | · | · | · | · | · | · |
| K16 Clock rate | M | M | M | S | I/M | I/M | I | i | I | · | · |
| K17 Hole sharpness | · | · | · | S | I/S | · | · | S (trace peak) | · | · | · |
| K18 Outer fall / sheath rise (trim) | · | M | M | S | I/M | · | · | · | · | M (cone base) | · |
| K19 Front element type | · | S | S | S | S | S | S | · | S (signals) | I/S | S |
| K20 Cone angle / layer / rounding | · | M (length) | · | · | M (at speed) | · | · | · | · | I/M | S (ANEC sign) |
| K21 Shelf lapse / lead speed | · | S | · | · | S | · | · | · | S | I/S | · |
| K22 Reset schedule (CS→core) | · | M | · | M | M | M (norm) | · | · | M | · | · |
| K23 Extended carry (CS) | · | M | · | M | · | M (norm) | · | · | M | · | · |
| K24 Support dynamics / carve | · | S | · | · | S | S (norm) | · | · | S | · | · |
| K25 Layer width / region radius / cushion | · | M | · | M | M | · | · | · | · | · | · |
| K26 Termination / end transitions (CS) | · | I/M | · | · | M | · | · | · | · | · | · |
| K27 Physical scale L (and f) | I | I | I | · | · | · | I | I | · | · | I/M |

---

## 5. Gaps (untested or single-point)

- Source-family tests (QI requirement, F(φ)R rays, Casimir) ran only on D-lap staged at 2.1c. The compartment, fronts, trimmed reference and speed-scaled designs have ANEC and trace-anomaly estimates but no QI requirement.
- Passenger temperature and cavity escape cone are computed at clock rate 1 only; the 1/α_c scaling is inferred.
- Tides and proper acceleration are quantified for D-lap (single value) and are exactly zero in every compartment design; no intermediate designs.
- Shift-transition radius and width were swept only in stretch-bearing probes; in the flat-slice designs they are fixed at 4.25–6.25.
- Lane speed vs demand was not measured in the choreography era; in the compartment era speed is tied to the lapse by the scaling rule, so speed at fixed lapse is untested there.
- Sheath amplitude sweeps are pass/fail; demand vs sheath amplitude is not tabulated in the lapse designs.
- The 0.1–5 clock sweep uses σ-spacing 0.2, coarser than the full gate.
- Renormalized 3+1 stress, emission rates, fields through acceleration and cone extension, and rays off the meridian remain open (CONE_TIP_FIELD_PASS.md:174-181; QUANTUM_ESTIMATES_PASS.md:200-209; ANEC_MAP_PASS.md:116-121).
- Coupled dynamics, back-reaction and stability of the lapse maximum are open (tex:470).
- The working tree holds an uncommitted, later "deficit minimization pass" (`scripts/run_deficit_minimization_pass.py`, `data/deficit_minimization_pass/`, pattern-shape parameters in `compartment_service.py`); it postdates this era and was not examined.
