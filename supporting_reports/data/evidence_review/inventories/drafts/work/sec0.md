# Part-and-knob → physics response map: the spherical-throat era (16 May – 17 Sep 2026)

Inventory for the metric-engineering textbook. Source: the active-rail
repository `/media/projectspace/active-rail-refined-design-base`, read-only.
Report paths are relative to `supporting_reports/`; code paths are relative to
`toolkit/adm_harness_cli/`. Line numbers are `cat -n` lines of the committed
state at HEAD `19a367a` (2026-09-25); every cited report and code file is
unmodified in the working tree at that commit. One source is not committed:
[RUN-CSV] = `toolkit/adm_harness_cli/runs/stage1_v5_topology_support_scaling_41x61/shell_throat_case_metrics.csv`,
a gitignored local run output; numbers taken from it are marked. The May 16
write-up PDF is cited by page. Every entry is marked as an **identity** holding for a class
of metrics or a **measurement** on one design. "INVENTORY DERIVATION" marks
algebra done for this inventory from the repo's own definitions; it appears in
no report and needs a textbook derivation before use.

## 0. Reading guide

### 0.1 Metric class and notation

The era's reduced metric (`ACTIVE_RAIL_ADM_PROCESS_WRITEUP_2026-05-16.pdf` p.2, eq. (1)):

ds² = −α²dσ² + A(dl+βdσ)² + B dΩ², A = γ_ll, B = γ_ΩΩ, R = √B.

The throat is Ellis-type, B = (l² + R_th²)c_Ω², minimal sphere R_th·c_Ω at
l = 0, two asymptotic ends (`THROAT_GEOMETRY_CLARIFICATION.md:46-68`). In code
(`adm_harness/source_ledger.py:1381-1565`, current HEAD; the May 17 version at
commit f8bb7fe has the same forms):

| Metric function | Construction |
|---|---|
| Support scalar | W = ½[1 − tanh((l² − R_th²)/(2R_th w_th))] × carve factor (`source_ledger.py:376-383, 1457`) |
| Decompression | q(σ) falls from 1 at σ = −0.40 over 3.0 (`:1391`, defaults `:86-87`) |
| Radial metric | √A = b·C₀^{qW}·(local factors), b = 1 + (B₀−1)Wq, C₀ = 100, B₀ = 8 (`:1459-1461, 1497-1513`) |
| Lapse | α = n_cushion·(λC₀)^{qW}·(local factors), λC₀ = 600, n_cushion = exp(0.18 η_N q e^{−((\|l\|−1.05)/0.35)²}) (`:1460-1463, 1488-1496`) |
| Shift | β = −U_β E(σ) W^{p_β} S_packet(l−σ)/b + overlays, p_β = 4 (`:1466`) |
| Carry speeds | U_X = v_exit + (V − v_exit)·catch_X(σ), v_exit = 0.5; X = β (support catch) or packet (rematch) (`:1385-1388`) |
| Areal radius | B = (l² + R_th²)c_Ω² × local factors, c_Ω = exp(a_Ω q_Ω(σ) W_Ω(l)), a_Ω = 0.20 (`:1552-1565`) |
| Packet speed | v = U_packet/b (`:1515`) |

Local coordinate light speed α/√A = n·λ^{qW}/b; C₀ cancels (`:1530`; INVENTORY
DERIVATION). One scalar W drives α, A and β together; that coupling is this
design's choice, not a property of the class.

### 0.2 Nomenclature traps

- **"beta075" is a release-fade width, not a shift amplitude.** It is
  `release_beta_width_multiplier = 0.75` (baseline 0.25)
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:89-104`;
  `STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:128-132`; fade duration
  4·w_β·multiplier, `source_ledger.py:313-316`). No report varies the shift
  amplitude independently of V.
- **V is a carry-speed load factor**, "not an ordinary passenger velocity claim"
  (`toolkit/adm_harness_cli/README.md:266`). It scales U, hence β and v.
- **R_th is two knobs at once**: the throat's minimal areal radius and the
  support-bump radius; one spec key (`support_radius`) also moves R_Ω, the
  region masks and the shell band (`source_ledger.py:379, 499-500, 582-583, 1555, 2025-2034`).
- **A and B clash across reports.** `COUPLED_SOURCE_ROLE_AUDIT.md:82-84` and
  `ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:76` use A for the **lapse**; the LE
  reset reports use B for a string density and areal gauge (r, f=1−2m/r).
- **"p003_mid"** = receiver angular log gain 0.03, inner/outer multipliers
  0.50/1.025, outer power 0.5 (`STAGE2_NEGATIVE_L_RECEIVER_PROMOTION_GATE.md:15-18`).

### 0.3 Evidence and generality labels

- (d) evidence type: **IDENTITY/DERIVATION** (quote + file:line), **SWEEP**
  (≥3 values), **SINGLE** (single comparison).
- (e) generality: **GEN-I** identity-backed for the spherical warped-product
  class (or the stated subclass); **GEN-S** background-independent source
  physics; **DESIGN** measured on this design only.
- Background markers: **[β075]** (in text) or **†** (in tables) = the result
  rests on the beta075 geometry that failed the Hawking–Ellis boundary gate
  with a Type IV layer — the frozen V5 release-0.75 case with the `p003_mid`
  receiver and `rematch_w6_t1p5` collar, its release-0.75 predecessors, or
  active V5 histories of it. **§** = the result rests on a static zero-shift
  slice of repaired beta075 (phase 0.745), which is Type I by construction
  (I22) and blind to the Type IV layer.

### 0.4 What the channels measure (caveats that apply to every number)

- All demand is `T = G[g]/8π` of a prescribed metric: "not a solved matter
  model or renormalized stress tensor" (`FREEZE_REPORT.md:9`;
  `V_SWEEP_FINDINGS.md:3`).
- `neg_Tkk_radial` uses coordinate null vectors k± = (1, −β ± α/√A), so
  T_kk± = α²(ρ + p_l ∓ 2j_l) (`STAGE1_CHANNEL_CAUSE_LEDGER_FINDINGS.md:36-41`).
  Its magnitude carries α² (α ~ 10² inside the support); only its sign is the
  radial NEC. It counts a point whenever either branch is negative, so it
  never separates Type I NEC violation (both negative) from Type IV (one
  negative).
- "Burden" = badness × √A·B·dσ·dl (`source_ledger.py:1888, 2436`): coordinate
  weighted, no lapse, grid- and domain-dependent. Live fractions depend on the
  live mask and region labels, which scale with R_th.
- The packet norm −α² + A(v+β)² (`source_ledger.py:1550`) is unnormalized; its
  sign is the timelike test, its magnitude mixes α² with relative speed.
- No throat-era report gives passenger aging, tidal acceleration or occupant
  acceleration. The only occupant readout is the packet-norm sign, from which
  dτ/dσ = √(−norm) follows (INVENTORY DERIVATION); reported live values imply
  dτ/dσ from ≈1.1 to ≈420 across designs and within one live window
  (`STAGE2_ENTRY_SERVICE_GATE_MEMO.md:5`; `V_SWEEP_FINDINGS.md:47`).
- No throat-era report before Sept 8 computes a Hawking–Ellis type except the
  May 20–24 endpoint work, which used the legacy classifier [L5].

### 0.5 Later findings that scope or invalidate results

| Tag | Finding | Scope |
|---|---|---|
| **L1** | The frozen beta075/V5 geometry demands a refinement-stable **Type IV layer**: 3,843 dense points, discriminant −0.0020645 converged to 0.00115% (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:5-11, 62-65, 97-122`); 3,764 of them on the standing-support W transition, 1,862 on the β-rematch transition, 60 on the shell (`:84-90`); all matched static controls Type I (`:133-144`). Attribution on the repaired geometry: support decompression alone 874 Type IV points vs 842 for the full geometry; decompression carries ~98% of the integrated imaginary eigenvalue (`CONSTANT_RADIUS_TRACK.md:55-71`). "no source with a rest frame supplies it" (`THROAT_GEOMETRY_CLARIFICATION.md:153-158`). | Every conclusion that assumes the demand is realizable by a medium with a rest frame (source fits, regulators, energy certificates, closure, storage on beta075). Every source ranking in the lineage (Stage I smooth-split → beta075) is blind to Type IV. Geometric/causal readouts (null speeds, escape, cone tilt) survive but belong to an inadmissible geometry. |
| **L2** | **Packet-reading mismatch**: packet windows and live masks advance at unit coordinate speed (l − σ) while the packet-norm test uses carry speed U/b (`THROAT_GEOMETRY_CLARIFICATION.md:159-164`; `source_ledger.py:1393, 1515, 2037-2041`). | Every packet-norm verdict, failure count, V/w_th cliff, packet-frame density and live fraction in the era. |
| **L3** | **Service-time ratios** rest on l = σ; "They are proxies, and the geometry defines no arrival lead" (`THROAT_GEOMETRY_CLARIFICATION.md:165-175`). | The 2.569/1.233 ratios and every service-time comparison. |
| **L4** | **Two-ended topology** persists through every service; forming it needs topology change (`THROAT_GEOMETRY_CLARIFICATION.md:123-141`). | "Relax throat" readings; end-transition opening deficits; escape "to either end". |
| **L5** | **Classifier repair** (Sept 8): the legacy classifier labelled vacuum and small flux-dominated tensors Type II and took the wrong rest-energy root on 6,810 / 26,929 rows (`LE_BOUNDARY_GATE_PREFLIGHT.md:52-82`). | Legacy type labels and rest-frame energy-condition columns (May 20–24 endpoint work). |
| **L6** | **Static surrogate**: Sept source work used the zero-shift phase-0.745 slice (`C1_FINITE_MODULE_PAIR_SCREEN.md:25-29`). By I3/I22 it is blind to Type IV and to currents. | All C1, cavity and longitudinal-gate numbers. |
| **L7** | **Architecture superseded** by the one-space axial track (`THROAT_GEOMETRY_CLARIFICATION.md:184-250`). | All design-specific magnitudes. Identities (section 5) survive. |

Additional measurement scoping (pre-stage extraction, INFERENCE, see G2 and
G6): on the default 41×73 grid every packet-norm failure sits on the first
sampled row σ = −0.35, at mask-edge nodes (`HIGHRES_BOUNDARY_REPORT.md:64-72`);
the grid never samples the entry/pre-catch interval (σ < −0.35), so stage
burdens differ across reports (`BIFURCATION_INTERIM_DECISION.md:48` samples
entry, `HIGHRES_BOUNDARY_REPORT.md:30, 42` does not).

## 1. Parts

Each part is a localized, scheduled edit of one or more of α, β, A, B, or a
source component. "General function" states what the part does in the class;
"General?" says whether that function is class-level (with the identity that
makes it so) or specific to this design.

### 1.1 Geometry parts

| Part (project name) | Metric functions edited | General function | General? |
|---|---|---|---|
| **Throat** (Ellis areal profile, R_th) | B | A minimal sphere joining two ends. At R'=0 it demands radial tension p_r = −1/(8πR₀²) and, where R''>0, a radial null deficit ρ+p_r = −R''/(4πR₀) (`COUPLED_SOURCE_ROLE_AUDIT.md:104-110`); flare-out to R'/A = 1 costs an integrated null deficit ≥1 per end (`CONSTANT_RADIUS_TRACK.md:327-334`). | GEN-I (I17, I18). Ellis form and two-endedness are design choices [L4]. |
| **Standing support stretch** (W, C₀, B₀) | A, α, β (tied) | Stretches proper radial distance (√A up to ~800) at nearly fixed R, driving the local demand toward a string cloud with areal flux ≈1/(8π) (`CONSTANT_RADIUS_TRACK.md:51-54`). | Near-string-cloud tendency GEN-I (I4, I12); the tied α–A–β construction is DESIGN. |
| **Support decompression** q(σ) ("relax/reset") | A, α (via W·q) | Time-dependent relaxation of the stretch. Acting on a region where R varies, it separates the two radial null energies (I3) and produced ~98% of the Type IV burden (`CONSTANT_RADIUS_TRACK.md:55-71`). | Mechanism GEN-I (I2+I3); magnitude DESIGN. |
| **Support lapse** (λC₀)^{qW} | α | Clock enhancement; sets local light speed α/√A and hence causal headroom (I5, I6). Clock curvature enters p_t through X, overlap with R' through Y (I16); an interior lapse maximum costs ρ+p_r+2p_t < 0 (I19). | GEN-I (I6, I16, I19). |
| **Lapse cushion** (η_N shoulder at \|l\|=1.05) | α | Local clock partner that buys packet causal margin without changing radial pressure: "a safety compensator, not the source-reduction knob itself" (`COMPENSATOR_HIGHRES_REPORT.md:56`). Its \|l\| kink at l=0 gives an h⁻¹ angular pressure (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:146-150`). | Sign of margin effect GEN-I (∂norm/∂α = −2α); placement DESIGN. |
| **Angular capacity jacket** c_Ω | B | Time-dependent widening of R by up to 22% (`THROAT_GEOMETRY_CLARIFICATION.md:56-58`); one of three sources of R variation on which decompression acts (`CONSTANT_RADIUS_TRACK.md:68-71`). | Any time-dependent R edit is a candidate Type IV source (I3) — GEN-I; shape DESIGN. |
| **Carrying shift in a packet tube** | β | The shift carries the packet: v + β ≈ 0 at the tube centre. Shift demand appears mainly as radial momentum j_l, affine in β, with Δρ quadratic in β/α (PDF p.2 eqs. (9)–(14); pre-stage extraction C17). | Transport mechanism and j_l/ρ scaling GEN-I; confinement to a unit-speed tube is DESIGN and the origin of L2. |
| **Catch/rematch** (U: V → v_exit; β-side and packet-side schedules) | β, v | Decelerates the carried packet; any lag between shift and packet schedules enters the packet norm directly: "packet-frame rematch cannot be left behind" (`BIFURCATION_INTERIM_DECISION.md:38`). | Mismatch mechanism GEN-I (I6); schedules DESIGN. |
| **Release fade** E(σ) | β | Removal of the carrying shift; its duration is "part of the endpoint source machinery, not just a background choreography detail" (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:222-224`). | DESIGN. |
| **Packet carve** (entry/catch/edge) | W → α, A, β | Excises the prepared plant under the occupant tube; moves hard demand off the packet and spends causal margin when α, A, β share W (G8). | DESIGN. |
| **Packet lapse compensator / null cushion** | α | Restores causal margin (positive gain) or trims coordinate null exposure (negative gain). | Margin sign GEN-I; rest DESIGN. |
| **Local radial stretch** (core, ring, skirt) | A | Local proper-length shaping; core sets peaks, ring moves live fractions (G13). | DESIGN. |
| **Local areal partner / receiver flange** | B | Moves cost between radial-null and angular/current channels (G14, G25); by I2 a dip in R costs radial null energy. | Direction GEN-I; magnitude DESIGN. |
| **β-rematch collar** | β | Drives the local shift toward comoving, v+β → (1−gW)(v+β) (I7); controls radial bundle focusing through ∂_lβ (I11). | Algebra GEN-I; shapes DESIGN. |
| **Support-shell overlay** (+ clock-lapse, rail-stretch, throat-capacity partners) | β (+α, A, B) | Infrastructure-local shift actuator in the annulus 0.65–1.20 R_th; "packet-safe and controllable … not, by itself, a strong 4D source-redistribution mechanism" (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:297-299`). | DESIGN. |
| **Endpoint/junction layer J** (support-edge shoulder, reset cap, angular jacket) | demand bookkeeping | Where the null deficit not carried by the string-cloud scaffold sits. Support edge: 85.5% both-branches-negative (Type I NEC violation); reset cap: 75.6% one-branch-negative (Type IV by I3) (`STAGE2_ENDPOINT_THEORY_MEMO.md:36-49`). | Type reading GEN-I (I3); shares DESIGN. |
| **Beta-memory support-edge receiver** | B (or α, A, β) | Post-release edit at the support edge driven by accumulated release; relieves the reset cap (G25). | DESIGN. |
| **Causal-margin guard** | β | Clamps \|β\| ≤ (1−m)α/√A in a window (`source_ledger.py:1527-1546`). | Construction GEN-I (I5); effect DESIGN. |
| **Entry gate** (`live_packet_start`) | none | Accounting boundary; changes no metric function (G17). | Definitional. |
| **String-cloud scaffold S0** (demand decomposition) | none | The geometric W-term: p_l/ρ = −0.999288 fit (`STAGE2_ENTRY_SECTOR_CLOSURE_DENSE.md:124-125`), flux 0.039772 ≈ 1/(8π) (`STAGE2_RADIAL_STRING_CLOUD_ENDPOINT_CROSSWALK.md:72`). A null-neutral scaffold pushes the null deficit to its ends (I12, I20). | GEN-I. |
| **Constant-R track** (post-era, Sept 23) | B held constant where metric evolves | Exact string cloud in the radial block; all 2D dynamics move to p_Ω = −K/8π; Type IV 13,587 → 0 (`CONSTANT_RADIUS_TRACK.md:77-94, 171-176`). | GEN-I (I4). |

### 1.2 Source-architecture parts (Sept 9 – 17)

| Part | General function (stress role supplied) | General or throat-tied |
|---|---|---|
| Standing radial backbone / tension carrier | Radial tension (1,−1,0) with zero radial-null stress and positive angular-null stress; needs a reacted force density −Φ′/R² (`COUPLED_REORIENTATION_INVESTIGATION.md:37-52, 100-102`). C1 uses a radial E field at 95% of throat tension, Maxwell tensor ½E²(1,−1,0,+1) (`C1_FINITE_MODULE_PAIR_SCREEN.md:31-36`; `ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md:51-52`). | Role GEN-S; magnitude throat-tied. |
| Ordinary host / module support | DEC aggregate transmitting force inside a module with zero end traction (`C1_FINITE_MODULE_PAIR_SCREEN.md:71-75`). | GEN-S. |
| C1 module | Finite, mechanically independent multicomponent assembly; fields, radiation and packet exchange still transfer energy and momentum; recoil counted (`RAIL_BUILD_TOPOLOGY_DECISION.md:70-77`). | Architecture, general. |
| Overlap region | Must hold actual material/field states supplying local stress; contributions solved on one shared geometry because Einstein's equations are nonlinear (`RAIL_BUILD_TOPOLOGY_DECISION.md:87-97`). | GEN-S. |
| Radial signed quantum source (reflecting 1+1 conformal channels) | Negative energy and negative radial-null stress ("opening"); ρ−p_r locked by the anomaly (Q1, Q2). | Law GEN-S; need throat-tied. |
| Radial reflectors | Take F = −4πR²[p_r] as material reaction (Q3). | GEN-S. |
| Angular signed source (4D conformal scalar, ξ=1/6) | Negative angular-null stress with zero radial-null stress (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:176-180`; Q5). | Law GEN-S; duty size throat-tied. |
| Angular reflectors / Dirichlet ends | Field-selective boundaries; add end tractions (Q6). | GEN-S. |
| Scalar-mirror cavity | Proximity interaction gives negative radial-null stress; mirror gradients give positive stress at the same rate (Q9). | Planar GEN-S; curved throat-tied. |
| Short magnetic circuits | Longitudinal Casimir stress of charged modes on field lines; turn Maxwell stress positive (`CAVITY_AND_MAGNETIC_SOURCE_COMPARISON.md:57-64`). | Mechanism GEN-S. |
| Planar EM Casimir cells | Target (−C_r−2C_t, −3C_r+2C_t, C_r−2C_t) (Q7). | GEN-S. |
| Pressure-linked store; elastic reservoir; EM store; charged capacitor | Endpoint work and heat supply with reactions to standing support (`PRESSURE_LINKED_STORAGE_COMPLETION.md:313-318`; `ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md:72-84`; `ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md:40-43`; `CHARGED_CAPACITOR_CONSTRUCTION.md:30-34`). | Laws GEN-S; numbers on beta075 [L1]. |
| Magnetic containment jacket and sleeves | Closed flux tube confining an ultrarelativistic gas; sleeves carry hoop and axial load (`MAGNETIC_LOAD_BALANCING_TEST.md:24-30, 104-111`). | Pressure balance GEN-S; thresholds on beta075. |
| Containment ensemble | Sheets, hoop strings, hoop-directed Maxwell field, host; each with its own directional stress (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:47-53`). | Tensor algebra GEN-S. |
