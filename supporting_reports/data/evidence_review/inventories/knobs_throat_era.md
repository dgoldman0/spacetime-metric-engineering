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

Additional measurement scoping (INVENTORY INFERENCE; see G2 and
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
| **Carrying shift in a packet tube** | β | The shift carries the packet: v + β ≈ 0 at the tube centre. Shift demand appears mainly as radial momentum j_l, affine in β, with Δρ quadratic in β/α (PDF p.2 eqs. (9)–(14); INVENTORY DERIVATION). | Transport mechanism and j_l/ρ scaling GEN-I; confinement to a unit-speed tube is DESIGN and the origin of L2. |
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

## 2. Knob index

| ID | Knob (general) | Project name | Background | Evidence | Headline response | Generality |
|---|---|---|---|---|---|---|
| G1 | Minimal areal radius of the throat (with support radius) | `Rth`, `support_radius`, `wide4_radius205` | Stage I; promoted pair; § transfer | SWEEP + SINGLE | Pointwise tension ∝ 1/R² (p_l peak ratio 0.7656 = (1.75/2)²); integrated and live-angular burdens rise | tension GEN-I; rest DESIGN |
| G2 | Support-edge width | `w_th` (0.569/0.570 cliff) | pre-stage; † type sweep | SWEEP | Global burden falls ~20%; packet margin and V headroom spent; Type IV worsens with width † | DESIGN |
| G3 | Clock partner that buys causal margin | `eta_N` lapse cushion | pre-stage | SWEEP | Packet safety at fixed p_l | sign GEN-I |
| G4 | Areal-radius jacket width | `wOmega` | Stage I; § transfer | SWEEP | Nearly neutral | DESIGN |
| G5 | Decompression schedule; uniform slowdown | `q(σ)`, κ | † | SWEEP + DERIVATION | Decompression ≈98% of Type IV; slowdown thins but never removes it | GEN-I mechanism |
| G6 | Carry-speed load | `V` (2.5/5/10) | pre-stage, Stage I, † ladder | SWEEP | Null burden and packet cliff move; p_l, j_l totals and core peak V-independent | structure GEN-I |
| G7 | Catch timing: one-component shaping vs two-component split | `shape_early_minjerk_w32`, `split_*` | pre-stage | SWEEP | Shaping wins; temporal split breaks the packet handoff | mechanism GEN-I |
| G8 | Support excision under the occupant tube | packet carve | Stage I | SWEEP | Live exposure down, total burden up, margin spent | DESIGN |
| G9 | Packet-local lapse, gain and footprint | lapse compensator | Stage I | SWEEP | Margin back; null burden re-imported unless the gradient leaves the tube | sign GEN-I |
| G10 | Second carve zone | two-zone, annular shoulder | Stage I | SWEEP | Radial pressure yields; radial null stalls | DESIGN |
| G11 | Carve splitting, null cushion, composition, edge sleeve | split carve, `smooth_union`/`additive` | Stage I (lineage of †) | SWEEP | Radial vs angular/current trade; overlap structure matters | DESIGN |
| G12 | Restoring support in the carved annulus | pressure rebate | Stage I | SWEEP | Every radial channel worse | DESIGN |
| G13 | Local radial proper-length shaping | core/ring/skirt | Stage I; § transfer | SWEEP | Core sets peaks, ring sets live fractions | DESIGN |
| G14 | Local areal-radius edit on the edge footprint | smooth-split angular partner | Stage I | SWEEP | Moves cost between radial null and angular/current | direction GEN-I |
| G15 | Time-edge profile and schedule of packet windows | tanh/minjerk; coordinated release | Stage I | SWEEP | No gain from smoother profiles; lapse retiming loads the live tube | DESIGN |
| G16 | Transition width vs order of carve windows | compact handoff wide3/wide4 | Stage I | SWEEP | Width beats smoothness order | DESIGN |
| G17 | Live-accounting start | `live_packet_start` | Stage I | SWEEP | Relabels, changes no metric | definitional |
| G18 | Shell shift amplitude and sign | support-shell overlay | pre-stage V5/V10 | SWEEP | Packet-safe, only adds demand; sign a tie-breaker | structure GEN-I |
| G19 | Shell timing | lead, temporal width | pre-stage | SWEEP | Later lead cleaner | DESIGN |
| G20 | Shell metric partners | clock-lapse, rail-stretch, `kappa_Q = a_beta × ratio` | pre-stage | SWEEP | Throat-capacity 0 best; clock effect confounded | DESIGN |
| G21 | Shell radial profile, width, strength | raised-cosine vs smooth box; 0.20–0.35 | pre-stage | SWEEP | Compact support keeps occupant quiet; burden linear, peaks superlinear in strength | DESIGN |
| G22 | Endpoint window thickness | edge 7.2/9/11 smearing | Stage II (+†) | SWEEP | Endpoint J invariant | DESIGN |
| G23 | Shift-removal duration | release width `beta025…100` | † | SWEEP | Reset −24% (0.75), ~80% moved to shoulder | type reading GEN-I |
| G24 | Receiver metric channel | lapse/radial/β/angular | † | SWEEP | Only the areal channel moves radial null | direction GEN-I |
| G25 | Receiver side, gain, window, persistence | negative-l `p003_mid` | † | SWEEP | −l cheap, +l costly; √ cusp singular | superposition GEN-I |
| G26 | Shift re-match collar | `rematch_w6_t1p5`, gain/floor/width | Stage I; † | SWEEP | Buys margin algebraically; β shear sets focusing | algebra GEN-I |
| G27 | Causal-margin guard | packet/edge/support guard | † | SWEEP | Fewer crossings, sharper pinch | construction GEN-I |
| G28 | Join regularity class | √ cusp → C2 Hermite; origin r_a; cap | † | SWEEP + DERIVATION | Stress ∝ d^{p−2}; type unchanged | GEN-I |
| G29 | Explicit reset source | string pairs + material + null streams | † | SINGLE | Type IV moves; mass budget exceeded | mass law GEN-I |
| G30 | Reset path and infrastructure motion | inverse search | † | SWEEP | Motion cuts material deficit, not Type IV | GEN-I (I26) |
| G31 | Constant R where the metric evolves (post-era) | constant-radius track | repaired † service, new geometry | IDENTITY + SWEEP | Type IV 13,587 → 0; cost moves to p_Ω | GEN-I |
| M1–M8 | Source-model choices on the demand | regulator, source class, reservoir, timing, rapidity, reshaping, mesh, 3+1 | † | SWEEP | Admissibility-dependent; undermined by L1 | mixed |
| D1–D3 | Demand-reading choices | role partition, SNEC τ/coverage/λ, scalar screen | promoted pair; † | SWEEP | Decide verdicts; not metric knobs | mixed |
| S1–S18 | Source architecture | C1 overlap, modules, cavities, populations, ℓ₀, backbone 95%, reflectors, magnetic jacket, storage | § (C1, cavities); † (storage, magnetic) | SWEEP + IDENTITY | Laws general, magnitudes throat-tied | GEN-S laws |

## 3. Geometry knobs

### 3.A Throat, standing plant and service load (May 16 – 20, with later transfers)

#### G1. Throat radius R_th (with support radius; compact vs wide)

- (a) Minimal areal radius of the throat. In this design the same parameter
  also sets the support-bump radius, and in the Stage I screen also R_Ω, the
  region masks and the shell band (§0.2). Project names: `Rth`,
  `support_radius`, `wide4_radius205`.
- (b) 1.75 vs 2.0 at V10, 41×61 (`POINT_LEVEL_FINDINGS.md:15-26`);
  1.75/1.90/2.05 on the compact wide4 base (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:60-66`);
  promoted pair `compact7_wide4_edge160` (1.75) vs `wide4_radius205` (2.05)
  (`STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md:66-67`); 1.90/2.05 transferred
  to the repaired beta075 static slice (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:132-143`).
- (c) Responses:
  - *Demand magnitude, pointwise.* Live |p_l| peak 0.009531 → 0.007297 for
    1.75 → 2.0 (`POINT_LEVEL_FINDINGS.md:16, 22`): ratio 0.7656 = (1.75/2.0)²
    exactly. Radial-null point peak 1.039 → 0.878 → 0.751 for 1.75/1.90/2.05
    (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:62-64`), ratios 0.845 and 0.723
    against (1.75/R)² = 0.848 and 0.729 (INVENTORY arithmetic). Mean ρ of the
    infrastructure role A falls by 0.728 for 1.75 → 2.05 (INVENTORY arithmetic
    on `STAGE2_COMPONENT_ALGEBRA_PROMOTED_PAIR.md:39-41`: 0.00714 → 0.00520).
  - *Demand magnitude, integrated.* Total neg-T_kk 458 → 558.9, total |p_l|
    69.12 → 83.04 (`POINT_LEVEL_FINDINGS.md:15-22`). Assigned infrastructure
    radial support 382.25 → 544.88 (+43%)
    (`STAGE2_COMPOSITE_SOURCE_ANSATZ_PROMOTED_PAIR.md:60-65`). On the repaired
    static slice over [−7,7]: negative-density integral +15.8%, negative
    radial-null +11.2%, |p_t| +27.4% (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:185-189`).
  - *Demand location.* Live |p_Ω| burden 1.245 → 1.435 → 1.651
    (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:62-64`); live p_Ω fraction 21.56% →
    28.28% (`STAGE2_FULL_GRID_SOURCE_DECOMPOSITION_ENTRY_GATE.md:114-115`);
    radial-null fractions fall (26.7% → 22.5%, `POINT_LEVEL_FINDINGS.md:15, 21`).
  - *Algebraic type.* Untested in every radius comparison.
  - *Packet norm.* Safe throughout; max live norm −22.82 → −23.40
    (topology run CSV [RUN-CSV], rows 2–4) [L2].
  - *Source supply ratio (longitudinal quantum gate).* Radius 1.90/2.05 lower
    the supplied fraction by 4.55%/8.45% at k/R₀²=0.01 on [−7,7]; optical
    length 15.780 → 16.233 and throat lapse 81.66 → 88.47
    (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:132-143, 177-181`). At
    k/R₀²=0.9 on [−3,3] the short-interval gate improves 1.18350 → 1.63076
    (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:164-170`).
- (d) SWEEP (3 values) + SINGLE comparisons across four contexts.
- (e) **GEN-I for the pointwise throat tension**: at a minimal sphere
  p_r = −1/(8πR₀²) independent of lapse and stretch (I17;
  `COUPLED_SOURCE_ROLE_AUDIT.md:104-107`). The exact (1.75/2)² ratio of the
  live p_l peak is this identity (INVENTORY match; the report does not state
  it). Throat-scale curvature stress falling ∝ R⁻² is dimensional. The
  integrated increases are DESIGN: the √A·B weight grows with R² and the
  R_th-scaled region masks grow too.
- (f) "radius broadening helps the non-live radial-null infrastructure peak
  while charging the live angular-pressure ledger" (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:94`);
  "R2.0 improves the radial-null and radial-pressure fractions, but by making a
  larger infrastructure ledger" (`POINT_LEVEL_FINDINGS.md:107`); "a smaller
  local peak can accompany a larger counted support requirement"
  (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:193-194`).
- (g) Not isolated: R_th moves the support bump with the throat, so packet
  norms change too. Combined with w_th = 0.75 at R 2.05 the mixed derivative
  score doubles (2.017×) while the peak stays low (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:70, 106`).
- (h) Peaks fall by the 1/R² law while every integrated measure rises; the
  compact reference was preferred on assigned burden
  (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:32`).
- (i) [L4] this is the radius of a two-ended wormhole throat; [L1] type
  untested; [L6] for the September transfer; [L2] for packet norms.

#### G2. Support-edge width w_th ("radial softening") and the packet-norm cliff

- (a) Transition width of the support scalar W in the variable l². W sets
  the log-stretch, log-lapse, b and the shift (as W⁴) together.
- (b) 0.35 (shaped base) … 0.60 coarse (`RADIAL_PRESSURE_SOFTENING_FINDINGS.md:7, 58`);
  0.520–0.570 at 41×73 (`HIGHRES_BOUNDARY_REPORT.md:10-16`); 0.65, 0.75 on the
  wide4 base (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:49`); ×{0.5,1,2} on frozen
  beta075 (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:209-214`).
- (c) Responses (41×73, V10, η_N=1; `HIGHRES_BOUNDARY_REPORT.md:10-16, 66-72`):

| w_th | live p_l ratio | live T_kk ratio | T_kk peak ratio | max live packet norm |
|---|---:|---:|---:|---:|
| 0.35 | 1 | 1 | 1 | −467.882 |
| 0.520 | 0.8525 | 0.8018 | 0.954 | −258.474 |
| 0.540 | 0.8320 | 0.7736 | 0.943 | +4276.14 |
| 0.565 | 0.8061 | 0.7384 | 0.929 | +15119.3 |
| 0.569 | 0.8020 | 0.7327 | 0.926 | +16714.1 |
| 0.570 | 0.8010 | 0.7313 | 0.926 | +17106.8 (2 pts) |

  - *Magnitude.* Total p_l 69.1145 → 51.0469 and total T_kk 424.4 → 286.709:
    widening reduces demand globally (`HIGHRES_BOUNDARY_REPORT.md:10-16`). The
    live |p_l| **point peak** is 0.00953056 for every w_th (same table, column
    `live_packet_point_peak__abs_p_l`); it equals the throat tension 1/(8πB(0)) ≈ 0.00953 with the
    jacket's c_Ω (INVENTORY DERIVATION).
  - *Location.* Live fractions rise slightly (p_l 0.2495 → 0.2706) while
    absolute live burdens fall.
  - *Packet norm / cliff.* With the lapse cushion at η_N = 2 (G3): 0.569 safe
    (−198.925), 0.570 unsafe (+228.109) at V10 (`ROBUSTNESS_FINDINGS.md:27, 38`).
    "The `w_th = 0.570` cliff is not a universal cliff at lower V. It is safe
    at `V = 2` and `V = 5`, unsafe at `V = 10`" (`V_SWEEP_FINDINGS.md:83`).
    Failing nodes: (σ,l) = (−0.35, −0.7) for raw widening and (−0.35, 0) for
    0.570, both on the first sampled time row (`HIGHRES_BOUNDARY_REPORT.md:66-72`).
  - *V headroom.* Shaped base (w_th 0.35) stays safe to V ≈ 12.0; tuned 0.569
    only to 10.00 (`V_SWEEP_FINDINGS.md:62-75`): "radial softening and lapse
    cushioning improved source burden but spent a lot of V headroom" (`:85`).
  - *Algebraic type (frozen beta075, repaired classifier).* Widening worsens
    Type IV: w_th × {0.5, 1, 2} give minimum discriminants −0.001403,
    −0.002064, −0.002272 and ∫|Im λ| 0.06619, 0.07617, 0.09026
    (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:211-214`).
  - Wider still (0.65, 0.75) on wide4: live T_kk burden falls 8.83 → 8.01 while
    the mixed derivative score rises ~56% and the max point peak rises 1.04 →
    1.98 ([RUN-CSV] rows 2, 5, 6; `STAGE1_TOPOLOGY_SUPPORT_SCALING.md:67-68, 96-101`).
- (d) SWEEP.
- (e) DESIGN. INVENTORY INFERENCE: the p_l burden
  reduction tracks the shortened proper radial length √A inside the packet
  window (√A ratio ≈0.74–0.81 against burden ratio 0.802), not a lower local
  stress; with an invariant p_l peak this is consistent with I17.
- (f) "Tkk wants shaped catch timing. p_l wants radial support-edge widening.
  packet safety sets a hard upper bound on w_th" (`RADIAL_PRESSURE_BOUNDARY_FINDINGS.md:58-60`).
- (g) w_th and R_th are the only pre-stage knobs that move p_l; w_th moves p_l
  and T_kk together.
- (h) Resolution reversed the verdict: "The previously reported safety cliff
  was therefore under-resolved and moved substantially downward"
  (`HIGHRES_BOUNDARY_REPORT.md:129`). INVENTORY INFERENCE (closed-form
  reconstruction from the code definitions): both cliffs are the sign flip of a single
  packet-mask-edge node (S = ½) on the first sampled row; a closed-form
  estimate of v_rel = √A|v+β|/α at (−0.35, 0) reproduces the 12.0/12.1 base
  cliff and the 10.00/10.01 tuned cliff, and predicts the η_N sensitivity
  (1.82 per 0.2 in η_N) that is measured as 1.817 and 1.818
  (`ROBUSTNESS_FINDINGS.md:24, 27, 29`). The same estimate at unsampled
  earlier catch times (σ ≈ −0.45 to −0.64) gives v_rel ≈ 1.05–1.07 for the
  tuned design at V10, i.e. a packet failure outside the sampled domain
  (unverified).
- (i) [L2] governs the cliff; [L1] (w_th shapes the transition hosting 3,764
  Type IV points); the cliff values are properties of where the mask edge was
  sampled.

#### G3. Lapse cushion η_N

- (a) Gaussian log-lapse shoulder: α ∝ exp(0.18 η_N q e^{−((|l|−1.05)/0.35)²})
  (`source_ledger.py:1462-1463`). Raises local light speed α/√A in a band
  around |l| = 1.05.
- (b) 1.0, 1.2, 1.5, 1.8, 2.0, 2.2.
- (c) *Packet norm*: raw widening that failed becomes safe — w_th 0.54 at
  η 1.2 (−249.3), 0.55 at 1.5 (−250.5), 0.565 at 2.0 (−254.0), 0.569 at 2.0
  (−198.9); 0.570 at 2.0 stays unsafe (+228.1), 0.580 fails (+4423)
  (`COMPENSATOR_HIGHRES_REPORT.md:24-38`). η 1.8/2.0/2.2 at w_th 0.569:
  −197.108/−198.925/−200.743 (`ROBUSTNESS_FINDINGS.md:24, 27, 29`). V
  headroom unchanged: tuned_eta220 10.00/10.01 (`V_SWEEP_FINDINGS.md:65`).
  *Radial pressure*: unchanged — "increasing `eta_N` barely changes the live
  `p_l` burden at a fixed `w_th` … The lapse cushion is therefore a safety
  compensator, not the source-reduction knob itself"
  (`COMPENSATOR_HIGHRES_REPORT.md:56`). *Radial null*: live burden rises
  slightly (0.7384 → 0.7418 at w 0.565), peak falls (0.9287 → 0.8984)
  (`COMPENSATOR_HIGHRES_REPORT.md:32-35`).
- (d) SWEEP.
- (e) **Sign GEN-I**: ∂(−α² + A(v+β)²)/∂α = −2α < 0, so raising α makes every
  carried worldline more timelike (I6). Everything else DESIGN.
- (f) Enables wider w_th. INVENTORY INFERENCE: the shoulder weight at l = 0 is
  e⁻⁹, so the cushion cannot protect the throat-centre node that sets the
  0.570 and V ≈ 10.01 cliffs; "more cushion does not reopen much room beyond
  the old w_th ≈ 0.569 boundary" (`ROBUSTNESS_FINDINGS.md:18`).
- (g) **Decoupling result**: η_N moves packet safety at fixed p_l.
- (h) Part of any lapse effect on the coordinate T_kk channel is α²
  normalization (I8).
- (i) [L2]; [L1]. Its |l| kink at the origin gives an h⁻¹ angular-pressure
  surface term later repaired (G28).

#### G4. Angular capacity jacket (width w_Ω; transferred width 1.80/2.20)

- (a) Radial width of the time-dependent R-widening factor c_Ω.
- (b) w_Ω 1.40/1.80/2.20 (`STAGE1_TOPOLOGY_SUPPORT_SCALING.md:50, 62-66`); the
  jacket amplitude a_Ω = 0.20 was never varied.
- (c) Live |p_Ω| 1.245 → 1.221 → 1.205; T_kk peak 1.039 → 1.051 → 1.063;
  packet norm identical ("nearly neutral for the radial-null mixed score",
  `:104`). Transferred to repaired beta075: supply ratio −0.117%/−0.194%
  (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:138-139`).
- (d) SWEEP. (e) DESIGN.
- (g) Largely decoupled from packet norm and radial null.
- (i) The jacket's time dependence is one of three sources of R variation on
  which decompression generates Type IV (`CONSTANT_RADIUS_TRACK.md:68-71`) [L1].

#### G5. Support decompression schedule (the "reset") and uniform slowdown

- (a) The time profile q(σ) that relaxes the standing stretch and support
  lapse; and a uniform reparametrization σ = κt of the whole service
  (`LE_BOUNDED_METRIC_REPAIR.md:101-110`).
- (b) Attribution toggles on repaired beta075 (`CONSTANT_RADIUS_TRACK.md:55-65`);
  κ = 1 … 1/64 at 28 roots × 3 resolutions (`LE_BOUNDED_METRIC_REPAIR.md:150-192`);
  decompression schedule on the constant-R track (post-era,
  `CONSTANT_RADIUS_TRACK.md:297-315`).
- (c) *Algebraic type*: attribution (grid 0.1):

| control | Type IV points | ∫\|Im λ\| |
|---|---:|---:|
| repaired beta075 | 842 | 3.37×10⁻² |
| decompression alone | 874 | 3.58×10⁻² |
| decompression removed | 252 | 6.69×10⁻⁴ |
| static support, moving packet windows, zero shift | 236 | 8.06×10⁻⁴ |
| static support with carrying flow, no windows | 19 | 2.01×10⁻⁷ |

  Slowdown: "At rates from 1/4 through 1/64, all 28 root locations have Type IV
  demand at every resolution" (`LE_BOUNDED_METRIC_REPAIR.md:153-154`); at the
  reset root Δ = −1.2757×10⁻⁴ (κ=1) → −7.72×10⁻⁸ (κ=1/64), |Im λ| 0.005647 →
  0.000139, layer width ≈0.00556 → 0.00272 (`:173-192`); on the ordinary
  0.025 grid the slow cases look all Type I (`:187-192`).
  *Angular NEC on a constant-R track (post-era)*: integrated angular deficit
  0.373 (current) → 0.311 (after live window) → 0.118 (half rate) → 0.0063
  (quarter rate) → 0.0037 (removed); all points Type I
  (`CONSTANT_RADIUS_TRACK.md:297-303`). *Service*: packet-coordinate proxy
  1.2368 → 1.1989 [L3] (`:313-315`). *Endpoint J*: release lapse lag and
  carve lag 0 → 0.25 leave J unchanged to 6 digits
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:185-202`).
- (d) SWEEP + DERIVATION (I9).
- (e) **GEN-I**: (i) by I2+I3, time dependence acting where R varies separates
  the radial null energies — the attribution confirms decompression is the
  dominant Type IV generator; (ii) by I9, uniform slowdown cannot remove Type IV
  at an enthalpy zero with nonzero current (|Δ| ∝ κ², width ∝ κ). Magnitudes
  DESIGN.
- (f) Slower decompression thins the layer and lengthens the service.
- (g) Lapse-only and carve-only retiming are decoupled from endpoint J.
- (h) "the static limit can be Type I while every nearby evolving member still
  contains Type IV stress" (`LE_BOUNDED_METRIC_REPAIR.md:134-136`); coarse grids
  hide the thin layer.
- (i) The design rule that follows is G31 (hold R constant where the metric
  evolves). The "relax throat" reading is invalid: the minimal sphere persists
  [L4].

#### G6. Service factor V (carry-speed load)

- (a) U = v_exit + (V − v_exit)·catch; scales β and the packet speed v = U/b.
  V5 is the operating reference, V10 the "recognized edge" (PDF p.1).
- (b) V = 2, 5, 10, 11–15 (`V_SWEEP_FINDINGS.md:14-32`), fine scan 10.00–10.21
  and coarse 10–15 (`:58-75`); V2/V5/V8/V10 across Stage I branches; V2, 2.5, 5,
  10 on dense beta075 (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md`;
  `STAGE2_BETA075_V2_LOWER_SERVICE_SOURCE_COUPLING.md`).
- (c) Responses:
  - *Radial null (tuned design, live burden)*: 42.21 (V2), 52.06 (V5), 72.38
    (V10), 96.76 (V15); live fraction 0.150 → 0.178 → 0.228 → 0.280; point
    peak 0.1001 (V2, V5) → 0.1427 (V10) → 0.2044 (V15)
    (`V_SWEEP_FINDINGS.md:18-32`). V pushes null demand into the packet.
  - *Radial pressure*: live |p_l| 13.8318–13.8319 for V = 2–15; point peak
    0.0115534 at every V (`V_SWEEP_FINDINGS.md:14-32`): "The radial pressure
    burden is essentially fixed by the standing support geometry"
    (PDF p.3). Stage I: p_l, p_Ω, j_l totals unchanged V5 → V10 on the shell
    candidate (87.356; 3.923 → 3.928; 0.2643 → 0.2644)
    (`STAGE1_V5_MINIMAL_TRAVERSABILITY_SCREEN.md:87-92`; `STAGE1_V10_SELECTED_CANDIDATE_EDGE_CHECK.md:75-80`).
  - *Non-live core null peak*: identical at V2 and V5, 1.289256
    (`STAGE1_SPLIT_CARVE_NULL_CUSHION_PROGRESS.md:132, 201`).
  - *Shift response (ADM)*: live Δj_l fraction 0.1175 → 0.1925, "about 1.79×"
    from V5 to V10; "The live service signal is ∆jl , not ∆ρ" (PDF p.4-5).
  - *Packet norm*: tuned max live norm −251.3 (V2, V5) → −198.9 (V10) →
    +42,605 (V11) … +254,483 (V15); last safe V 10.00, first unsafe 10.01
    (`V_SWEEP_FINDINGS.md:38-66`). Beta075 dense: −6.3337225 identical to 16
    digits at V2, V2.5, V5; +1135.50 with 123/966 positive live points at V10
    (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md:213-218`;
    `STAGE2_BETA075_V2_LOWER_SERVICE_SOURCE_COUPLING.md:50-52`).
  - *Source model (beta075)*: total demand nearly flat V2 → V5 (neg-T_kk
    480.68 vs 476.99) while live fraction rises 0.0165 → 0.0251 and the
    support-edge source-coupling budget rises 0.616 → 2.076
    (`STAGE2_BETA075_V2_LOWER_SERVICE_SOURCE_COUPLING.md:41-46, 84-94`).
    Constrained field closure is non-monotone: pass V2 (0.0123), fail V2.5
    (0.17851321), pass V5 (0.0095), fail V10 (0.17851277)
    (`STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md:82-84, 259-261`).
- (d) SWEEP across four branches.
- (e) DESIGN magnitudes. **GEN-I structure**: from the ADM constraints
  (PDF p.2 eqs. (9)–(14)), at fixed (α, A, B) j_l is affine in β with a 1/α
  prefactor and Δρ quadratic with 1/α² (INVENTORY
  DERIVATION); where B′ = Ḃ = 0 a shift produces no j_l at all. The V-independence
  of p_l is consistent with I17 (throat tension depends on R only) and with the
  1/α suppression of shift terms (α ≈ 450 at the throat).
- (f) V consumes packet margin first; softening/cushioning spends V headroom
  (G2, G3). Restoring V8/V10 safety by β rematch "again raises live radial-null
  burden" (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:167, 203`).
- (g) **Decoupling**: V moves radial null and packet norm; p_l, total j_l, total
  p_Ω and the non-live core null peak are V-independent.
- (h) Lowering V does not reach the strict live-fraction criterion: "The strict
  packet/source-separation criterion still fails even at V2"
  (`STAGE1_V2_LOW_SERVICE_GATE_MEMO.md:80`). The beta075 V2.5 and V10 closure
  errors agree to 6 digits, unexplained.
- (i) [L2] for every cliff; [L3] if V is read as service speed; [L1] for
  closure/source results; the G2 cliff reconstruction applies to the V ≈ 10.01
  cliff.

#### G7. Catch/rematch shaping: one-component shaping vs two-component split

- (a) Timing, width and profile of the two catch schedules (support-side shift
  catch c_β and packet rematch c_packet), and their lead
  (`BIFURCATION_INTERIM_DECISION.md:1-14`). Side knobs: packet-window edge
  width w_pass; a localized lapse "shock absorber" at the inner packet edge.
- (b) Shaping (`shape_early_minjerk_w32`) vs spatial splits (`broad100`,
  `broad75`) vs temporal split (`split_temporal_beta_early`), 25×41
  (`BIFURCATION_INTERIM_DECISION.md:32-36`); locked lead 0.05 with w 0.32
  (`SHAPED_CATCH_CANDIDATE_NOTE.md:31-59`); earlier/later/softer on the tuned
  design (`ROBUSTNESS_FINDINGS.md:25-26, 40`); w_pass 0.055/0.06/0.08; shock
  absorber amplitude 0.15–0.80 (`SHOCK_ABSORBER_FINDINGS.md:36-41`).
- (c) Fork outcome:

| case | live T_kk vs base | live p_l vs base | T_kk peak vs base | packet failure |
|---|---:|---:|---:|---|
| temporal split | 0.816 | 1.000 | 0.983 | yes |
| early min-jerk shaping | 0.859 | 1.000 | 0.999 | no |
| spatial broad100 | 0.930 | 1.000 | 1.423 | no |
| spatial broad75 | 0.933 | 1.000 | 1.180 | no |

  Shaping moves null burden between stages: entry 61.53 → 0.00, catch 66.67 →
  116.59, release 17.95 → 8.94 (`BIFURCATION_INTERIM_DECISION.md:47-55`). On
  the tuned design, a later locked lead fails the packet norm (+2169.02)
  while earlier/softer variants stay safe (`ROBUSTNESS_FINDINGS.md:25-26, 40`).
  w_pass 0.06 → 0.08 lowers the T_kk peak 0.9081 → 0.7607 at fixed p_l
  (`RADIAL_PRESSURE_SOFTENING_FINDINGS.md:29-30`). Shock absorber: live catch
  T_kk 0.983/0.978/0.972 with global peak 1.024/1.042/1.113; amplitude 0.80
  gives 1.002 and peak 1.843 (`SHOCK_ABSORBER_FINDINGS.md:36-41`).
- (d) SWEEP (small).
- (e) DESIGN. **Mechanism GEN-I**: inside the packet v + β = (U_p −
  U_β E W⁴ S)/b, so any lag between shift and packet schedules enters the
  timelike test directly (I6; INVENTORY DERIVATION from `source_ledger.py:1466, 1515, 1550`). "the system wants
  beta/support catch to happen earlier, but packet-frame rematch cannot be left
  behind" (`BIFURCATION_INTERIM_DECISION.md:38`).
- (f) Catch timing trades radial NEC exposure against packet safety.
- (g) **Decoupling**: "negative radial-null exposure = mostly catch shaping /
  timing; radial pressure exposure = likely a separate radial-geometry/support-
  channel issue" (`BIFURCATION_INTERIM_DECISION.md:100-101`); p_l = 1.000 in
  every catch, w_pass and shock-absorber case.
- (h) The strongest null reducer (temporal split) breaks the packet handoff;
  spatial splits lower fractions by "mostly moving denominators and peak
  locations" (`BIFURCATION_INTERIM_DECISION.md:26`); a strong lapse guard is
  counterproductive (`SHOCK_ABSORBER_FINDINGS.md:45`).
- (i) [L2] — the packet norm is exactly the mismatch readout; sampling of the
  entry stage differs across grids (§0.5); [L1].

**Knob-separation summary for the pre-stage design** (`FREEZE_REPORT.md:40-43`;
`ROBUSTNESS_FINDINGS.md:86-89`): radial null ← catch timing; radial pressure ←
w_th and R_th; packet safety ← lapse cushion; V headroom ← a sharp cliff. The
p_l separation is explained by I17 (INVENTORY match); the others are measured.

### 3.B Packet-local containment knobs (Stage I, May 17 – 20)

All results in 3.B are measured on one design family at V5 or V10 on grids of
31×55 to 81×109. Absolute burdens change with grid and domain: the same
wide4 case gives live T_kk burden 8.83 (41×61), 8.50 (61×83) and 15.94
(extended domain) ([RUN-CSV] row 2;
`STAGE1_COMPACT_HANDOFF_HIGHRES_FINDINGS.md:53`; `STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:68`).
No report in 3.B computes a Hawking–Ellis type, DEC, SEC, tangential NEC or an
occupant tide/acceleration; the radial-NEC channel is the coordinate
quantity of I8. Every packet-norm number carries [L2]; every source ranking
is blind to the Type IV content later found in this lineage [L1].

**Design-family causal-headroom relation (INVENTORY DERIVATION from
`source_ledger.py:1459-1466, 1497, 1515, 1550`).** With overlays off, the
support scalar W drives lapse (λC₀)^{qW}, stretch √A = b·C₀^{qW} and shift
∝ W⁴/b together (b the code's angular factor 1+(B₀−1)Wq, not γ_ΩΩ); C₀ and b
cancel and the packet is timelike iff
√f_r·|U_p − U_β E W⁴ S| < f_α·n_cushion·λ^{qW} (f_r, f_α the local γ_ll and α
factors). Without shift the condition is U < n·λ^{qW}. Carving W removes
headroom, positive γ_ll gain divides it by e^{g/2}, lapse gain multiplies it
by e^{g}. This is the algebraic core of the three-way trade (live exposure,
causal margin, point peak) that the Stage I reports rediscover repeatedly
(`STAGE1_V2_LOW_SERVICE_GATE_MEMO.md:83-89`). It is specific to the tied-field
construction; the class-level content is I6.

#### G8. Packet carve (exclusion of support under the occupant tube)

- (a) W → W_raw(1 − c·window(|l−s|)): locally removes the prepared stretch,
  lapse and carrying shift under the occupant worldtube
  (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:14, 35-44`).
  Project name `standing_support_packet_exclusion`.
- (b) V5: 0–0.24; V10: 0–0.16 (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:113, 159-164`);
  later 0.32, 0.60, 0.70, 0.90.
- (c) V5 (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:118-124`):

| carve | packet failures | live T_kk fraction | live p_l fraction | max total ratio |
|---:|---:|---:|---:|---:|
| 0.00 | 0 | 0.221837 | 0.261006 | 1.054489 |
| 0.12 | 0 | 0.107606 | 0.169186 | 1.070796 |
| 0.16 | 0 | 0.087072 | 0.144818 | 1.079520 |
| 0.20 | 0 | 0.072283 | 0.123389 | 1.089866 |
| 0.24 | 1 | 0.061485 | 0.104700 | 1.102152 |

  V10 failures 3 → 11 → 20 → 80 → 135 → 162 for carve 0 → 0.16
  (`:157-164`): "carving improves source placement but consumes causal margin"
  (`:166`). Demand location: top hard points move from packet_in_support to
  core_throat (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:97`). Weaker carve on
  the May 18 candidate (0.90 → 0.70) raised packet margin ~9× and cut
  angular/current peaks (p_Ω ×0.152, j_l ×0.317) while raising live null
  burden ×1.353 and live p_l ×2.087
  (`STAGE1_CURRENT_CANDIDATE_ALGEBRA_LEDGER.md:289-297`).
- (d) SWEEP. (e) Measured on this design; the causal cost follows from the
  tied-field relation above.
- (f) Live exposure against total burden and causal margin.
- (g) **Live p_l fraction is fixed by the carve footprint alone**, to 5–6
  digits across V and lapse settings: 0.169186 (V5) / 0.169187 (V10) /
  0.169190 (V5 and V10 with lapse gain 0.75)
  (`STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md:121, 163`;
  `STAGE1_CARVE_LAPSE_COMPENSATOR_SWEEP.md:94, 129`). The live T_kk fraction
  does depend on V (0.2218 V5, 0.3073 V10). No report explains the invariance.
- (h) Total burden rises while live exposure falls.
- (i) [L1] carve edits the decompressing plant that alone produces Type IV
  (`CONSTANT_RADIUS_TRACK.md:59-68`); [L2].

#### G9. Packet lapse compensator: gain and footprint

- (a) α → α·exp(g·window), α only. Co-located (same window as the carve,
  `STAGE1_CARVE_LAPSE_COMPENSATOR_SWEEP.md:7-9`) or decoupled (independent
  radius r and width w multipliers, `STAGE1_DECOUPLED_CARVE_LAPSE_COMPENSATOR_SWEEP.md:18-26`).
- (b) Co-located g 0–0.30 (V5), up to 0.75 (V10). Decoupled at V10: carve
  0.12–0.16, g 0.55–0.75, r 1.1–1.4, w 0.5–2.5 (108 cases).
- (c) Co-located at V10 (carve 0.12, g 0.75): 0 failures (135 without lapse),
  live T_kk 0.2825; the same setting at V5 raises live T_kk to 0.2516, above
  the uncarved 0.2218 (`STAGE1_CARVE_LAPSE_COMPENSATOR_SWEEP.md:94, 126-129`):
  "packet-local lapse can buy back causal margin, but it partially
  reintroduces radial-null burden" (`:158`). Decoupled: 103 of 108 safe;
  best carve 0.16 / g 0.55 / r 1.4 / w 1.2 gives live T_kk 0.1597 at V10;
  w ≥ 2.0 fails the V10 packet gate
  (`STAGE1_DECOUPLED_CARVE_LAPSE_COMPENSATOR_SWEEP.md:82-96`). V5 back-check
  point-peak ratio 2.08 (`:122`).
- (d) SWEEP. (e) Measured.
- (g) **Partial decoupling.** Lapse leaves the live p_l fraction unchanged
  (G8g). It does not separate from T_kk: moving the lapse gradient out of the
  tube (r 1.4, w 1.2–1.6) cut V10 live T_kk from 0.2825 to 0.1596 at equal
  safety. The footprint of the lapse gradient, more than its gain, sets how
  much null burden returns to the tube.
- (h) Part of the lapse effect on the T_kk channel is the α² normalization of
  I8; the reports never separate it.
- (i) [L2]; superseded by G10.

#### G10. Carve shoulder: filled two-zone vs annular

- (a) A second carve zone around the core, either filled (clip(core+shoulder))
  or an annulus (outer minus inner window)
  (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:15-19`; `STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:17-21`).
- (b) Two-zone: core 0.17, shoulder 0.05. Annular moderate: core 0.32,
  annulus 0.08; deep: core 0.60, annulus 0.12.
- (c) Two-zone vs decoupled lapse: V10 live T_kk 0.1596 → 0.1295, live p_l
  0.1448 → 0.1143, safe at V5 and V10 (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:90-95`).
  Annular (`STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:67-96`):

| case | failures | live T_kk | live p_l | point-peak ratio |
|---|---:|---:|---:|---:|
| moderate V5 | 0 | 0.0965 | 0.0754 | 7.60 |
| moderate V10 | 0 | 0.0957 | 0.0754 | 4.10 |
| deep V5 | 0 | 0.0572 | 0.0237 | 11.10 |
| deep V10 | 165 | 0.0419 | 0.0235 | 6.14 |

- (d) SWEEP. (e) Measured.
- (g) Radial pressure yields to carving more readily than radial null:
  "Radial pressure can be pushed much lower, but radial-null exposure stalls
  unless the metric pays with V10 causal-margin failure and large peaks"
  (`STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:112`).
- (h) "The rising V5 point peaks suggest that the transition geometry is now
  the limiting design problem" (`STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md:120`).
- (i) [L2]. Deep branch is "a diagnostic boundary, not a selected architecture"
  (`STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md:129`).

#### G11. Split carve, null cushion, smooth-split composition and edge sleeve

- (a) Entry and catch carves on separate schedules; a weak negative α gain on
  an annulus during catch ("null cushion"); a composition rule for
  overlapping carve pieces (`smooth_union` 1−Π(1−v_i) vs `additive` clip(Σv_i));
  an annular edge sleeve carve (`STAGE1_SPLIT_CARVE_NULL_CUSHION_PROGRESS.md:19-56`;
  `STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:22-67`; `source_ledger.py:633-646`).
- (b) Split: entry 0.75 / catch 0.15 vs single 0.90. Cushion −0.03, −0.05,
  −0.07. Edge sleeve 0–0.08.
- (c) Split vs single (V5, 81×109): live j_l 0.119 → 0.0655, live p_Ω 2.747 →
  1.952, p_Ω peak 0.5705 → 0.2202, T_kk peak 1.289 → 1.068; live T_kk burden
  9.714 → 10.017; margin −5.455 → −23.767
  (`STAGE1_SPLIT_CARVE_NULL_CUSHION_PROGRESS.md:124-147`). Cushion −0.03 →
  −0.07: live T_kk 9.626 → 9.546, p_Ω 1.949 → 1.928, p_l and j_l up by
  ~0.05%, slight margin loss (`STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:225-248`).
  Edge sleeve 0 → 0.08: live T_kk 9.977 → 9.228 and p_l 0.4013 → 0.3790 down,
  j_l 0.0659 → 0.0684 and p_Ω 1.908 → 1.979 up, monotone
  (`STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:159-211`).
- (d) SWEEP and single comparisons. (e) Measured.
- (f) Radial (null, pressure) against angular/current, monotone and
  sign-coherent.
- (h) `smooth_union` "removed useful overlap between the entry/catch/shoulder
  pieces and raised the integrated live radial burden"
  (`STAGE1_SMOOTH_SPLIT_ANSATZ_PROGRESS.md:67`): superposition of pieces
  matters, the envelope alone does not decide the demand. A wiring bug first
  made `additive` look worse (`:86-90`).
- (i) This smooth-split lineage becomes the frozen beta075 geometry with the
  Type IV layer (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:21`) [L1]; [L2].

#### G12. Coupled edge carve and pressure rebate

- (a) Edge carve plus a "rebate" that restores W in the same annulus:
  carve = raw − min(raw, rebate·edge_window) (`source_ledger.py:1447-1455`).
- (b) Edge 0.18/0.24; rebate 0, 25%, 50% (31×55).
- (c) (`STAGE1_COUPLED_PROFILE_PRESSURE_REBATE_FINDINGS.md:116-170`)

| case | live T_kk | live p_l | T_kk peak |
|---|---:|---:|---:|
| current | 10.150 | 0.410 | 1.228 |
| edge 0.24, no rebate | 11.284 | 0.610 | 0.822 |
| edge 0.24, rebate 25% | 16.39 | 0.816 | 0.963 |
| edge 0.24, rebate 50% | 24.97 | 1.119 | 4.193 |

  Edge carve alone cut live p_Ω 2.669 → 0.908 and live j_l 0.1235 → 0.0390.
- (d) SWEEP (5 cases). (e) Measured.
- (h) Restoring support mass made every radial channel worse: "The next law
  should preserve derivative/cancellation structure, not local support mass"
  (`STAGE1_COUPLED_PROFILE_PRESSURE_REBATE_FINDINGS.md:224`).

#### G13. Local radial stretch profile on A (core, catch ring, outer skirt)

- (a) γ_ll *= exp(core·w_core + ring·w_ring + skirt·w_skirt): local
  proper-length shaping around the packet, A only
  (`STAGE1_TWO_FEATURE_RADIAL_PROFILE_PROBE.md:33-38`;
  `STAGE1_REFINED_RADIAL_SUPPORT_LAW_PROGRESS.md:38-42`).
- (b) Sign ±; core 0.05/0.06; ring 0.08/0.12; ring radius 2.0–2.4 × width
  2.4–3.2; skirt +0.05.
- (c) "negative radial softening was not the right direction; positive radial
  stretch was the useful direction" (`STAGE1_REFINED_RADIAL_SUPPORT_LAW_PROGRESS.md:92-93`).
  2.4/2.4 ring vs base: live T_kk fraction −0.000174, p_l +0.000067, j_l
  −0.000305, p_Ω −0.00800; T_kk peak ×0.961, p_Ω peak ×0.943
  (`STAGE1_RADIAL_SUPPORT_GEOMETRY_REFINEMENT.md:106-114`). Skirt: changes of
  order 1e−7 to 1e−5, "fine-trim scale"
  (`STAGE1_TWO_FEATURE_RADIAL_PROFILE_PROBE.md:170-181, 197`).
- (d) SWEEP. (e) Measured. Effects (≤2.6% relative) are smaller than the
  grid sensitivity documented above.
- (g) **The core sets the peaks; the ring moves only live fractions.** Identical
  T_kk peak 1.285178196 and packet norm −21.612436 across ring gains 0.08/0.12
  and three ring geometries (`STAGE1_REFINED_RADIAL_SUPPORT_LAW_PROGRESS.md:140, 150`;
  `STAGE1_RADIAL_SUPPORT_GEOMETRY_REFINEMENT.md:80-101`).
- (f) Narrow ring: better T_kk/p_Ω, worse p_l/j_l; wide ring the reverse
  (`STAGE1_RADIAL_SUPPORT_GEOMETRY_REFINEMENT.md:137-144`).
- (i) Retained in the September construction manifest
  (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:118-121`); transferred to repaired
  beta075, core gain 0.04/0.06 changed the longitudinal supply ratio by
  −0.314%/+0.315%, ring/skirt by <0.06%
  (`ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md:132-143`).

#### G14. Local areal-radius partner (smooth-split angular log gain)

- (a) γ_Ω *= exp(g·window) on the edge footprint: the only Stage I packet
  knob that edits R (`STAGE1_SMOOTH_SPLIT_PAIRED_COMPENSATOR_RESULTS.md:13-21`).
- (b) g = −0.20 … +0.20 (8 values, 41×61).
- (c) (`STAGE1_SMOOTH_SPLIT_PAIRED_COMPENSATOR_RESULTS.md:53-66`)

| g | live T_kk | live p_l | live j_l | live p_Ω | T_kk peak |
|---:|---:|---:|---:|---:|---:|
| −0.20 | 30.750 | 0.4317 | 0.0654 | 1.884 | 5.643 |
| −0.025 | 11.447 | – | – | – | 1.147 |
| 0 | 9.745 | 0.3971 | 0.0682 | 1.957 | 0.958 |
| +0.10 | 8.417 | – | – | – | – |
| +0.20 | 8.864 | 0.3715 | 0.0983 | 2.035 | 1.232 |

- (d) SWEEP. (e) Numbers measured. **Direction identity-backed**: by I2 a local
  dip in R (negative g) makes R convex along null rays and costs radial null
  energy; a bump relieves it until its own flanks turn convex (non-monotone
  at +0.20). The report does not make this connection.
- (f)/(g) "the local `gamma_omega` factor can move cost between the radial-null
  side and the current/angular side … It does not provide an independent
  cancellation direction" (`STAGE1_SMOOTH_SPLIT_PAIRED_COMPENSATOR_RESULTS.md:96`).
- (h) A −0.025 trim erases the whole smooth-split radial gain (`:94`); +0.20
  introduces a live packet-frame negative density 1.7e−4 (`:66-70`).
- (i) [L1]: by I3, any time-dependent R edit is a candidate Type IV source.

#### G15. Temporal edge profile and schedule of packet windows

- (a) Time-edge shape (tanh, minimum-jerk, smoothstep7) and schedule
  (live_only, entry_catch_release, catch_only, coordinated_release) of carve
  and lapse windows (`STAGE1_INFRA_DERIVATIVE_SMOOTHING_PROGRESS.md:19-32`).
- (b) 64 profile cases, 72 schedule cases.
- (c) Profiles: "did not improve the current candidate … the best rows were
  the existing `tanh` timing" (`:71`). Coordinated carve release: "live source
  fractions worsen sharply even though packet-norm safety still holds" (`:97`).
  Coordinated lapse (81×109): live T_kk 0.024255 → 0.016849, live p_l
  0.006986 → 0.008749, margin −5.456 → −3.860; the steepest lapse slope moves
  from 5.61 (non-live) to 10.21 (post-release, **live**) (`:119-141`).
- (d) SWEEP + single high-resolution check. (e) Measured.
- (f) Lapse retiming trims null burden by placing lapse-derivative burden in
  the live tube. "carve appears to preserve packet/support separation during
  transport and catch" (`:163`).
- (h) Derivative-limited time profiles bought nothing here; the hard `max`
  floor union has point-peak ratio 32.65 against 8.75 for `blend` (`:88-95`).

#### G16. Compact handoff: transition profile and width of the carve windows

- (a) Replace tanh carve-window transitions by finite-support smoothstep5/7
  profiles; "wide" multipliers (entry 4.8, catch 3.4, edge 7.2) spread the
  transition across the packet (`STAGE1_COMPACT_HANDOFF_COMPONENT_PROGRESS.md:14-27`).
- (b) Narrow compact5/compact7 vs tanh; wide3/wide4; edge carve 0.04–0.16;
  entry carve 0.70–0.80, entry width 4.2–5.4.
- (c) Narrow compact is much worse: live T_kk 9.745 (tanh) → 21.73 (compact5)
  → 30.46 (compact7); T_kk peak 0.958 → 7.24 → 12.73
  (`STAGE1_COMPACT_HANDOFF_COMPONENT_PROGRESS.md:53-55`): "Endpoint smoothness
  alone is not enough; the transition must be broad enough" (`:57`). Wide4 vs
  split_ref (61×83): live T_kk −10.8%, p_l +12.2%, j_l −10.2%, p_Ω −35.9%;
  T_kk peak +5.0%, p_Ω peak −32.5%; rel|∂²_lγ_ll| 1297.40 → 394.93 (−69.6%)
  (`STAGE1_COMPACT_HANDOFF_HIGHRES_FINDINGS.md:49-64, 93-105`). Top live p_Ω
  rows 18/20 → 10/20 (`STAGE1_SHELL_THROAT_OVERLAP_PROXY.md:108-115`).
- (d) SWEEP + high-resolution single comparisons. (e) Measured. The
  width-over-order result is consistent with G being linear in second
  derivatives (a transition of width Δ has second derivatives ∝ 1/Δ²),
  which no report derives.
- (f) "entry containment -> radial pressure balance / live p_l control; broad
  compact handoff -> angular-current relief / derivative concentration
  control; edge carve recovery -> live Tkk recovery with peak/current cost"
  (`STAGE1_COMPACT_HANDOFF_HIGHRES_FINDINGS.md:130-132`).
- (h) "Weakening entry actually worsens live `p_l`" (`:85`).
- (i) `compact7_wide4_edge160` became the promoted Stage II pair [L1 untested].

#### G17. Entry gate (`live_packet_start`)

- (a) An accounting boundary: points with σ < start are labelled pre-entry
  setup and leave live accounting. **No metric function changes**
  (`STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:16-28`; `source_ledger.py:2002-2004, 2037-2041`).
- (b) Unset, −1.40, −1.36, −1.32, −1.28.
- (c) Positive live packet-norm points 2 → 0; live T_kk 15.94 → 13.98
  (`STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:68-69`). The two positive-norm points
  at σ = −1.500 and −1.422 remain in the geometry
  (`STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md:96-99`).
- (e) Definitional. (h) The −1.40/−1.36/−1.32 rows are identical at the grid
  spacing (`STAGE1_COMPACT_ENTRY_STAGE_SCREEN.md:83-85`).
- (i) "Live burden 0" statements downstream partly reflect this relabelling.

### 3.C Support-shell overlay (V5/V10, May 16 – 17)

The shell is an infrastructure-local shift actuator δβ_shell = A·W_shell in the
annulus 0.65–1.20 R_th, excluding the packet, with optional exp(gain·W_shell)
partners on α (clock-lapse), A (rail-stretch) and B (throat-capacity)
(`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:12, 18, 35-37`;
`source_ledger.py:492-551, 1487-1499, 1556`). Two ledgers are used: the reduced
ADM constraint ledger (PDF eqs. (13)–(17), with β-off substrate subtraction)
and the 4D point ledger.

#### G18. Shell amplitude and sign

- (a) Peak added shift in the support-edge annulus.
- (b) 1e−7 … 2.0, both signs, 27×37; 0.5 and 1.0 at 53×73
  (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:120-163`); signed-objective
  pairs at V5 (14) and V10 (16).
- (c) *Packet*: 0 failures through amplitude 2.0; packet drift exactly
  linear, 1.71028e−4 at 1e−3 → 0.171028 at 1.0. *Demand*: onset of visible
  burden growth at 1e−3 to 1e−2; at 0.5: max total ratio 1.0909, radial null
  1.0562, radial current 1.040, p_l 1.000013, point peak 1.286; at 1.0: null
  1.1339, current 1.0804, point peak 2.539. Live-packet burden changes 10⁻⁵ to
  10⁻¹⁰: all added demand lands outside the packet
  (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:120-184`). *Sign*: positive
  wins all pairs by ≤2.89e−6 (V5) and ≤1.53e−5 (V10)
  (`V5_SIGNED_SOURCE_OBJECTIVE_SIGN_TEST.md:36`; `V10_SIGNED_SOURCE_OBJECTIVE_SIGN_TEST.md:34`):
  "treat this as a numerical tie-breaker, not a physical source conclusion"
  (`V5_SIGNED_SOURCE_OBJECTIVE_SIGN_TEST.md:60`). At amplitude 1.0 the sign
  matters in the packet-frame density: neg-ρ_packet ratio 1.4157 (negative)
  vs 1.000008 (positive) (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:162-163`).
- (d) SWEEP.
- (e) DESIGN magnitudes. **GEN-I structure** (INVENTORY DERIVATION from PDF
  eqs. (9)–(14)): j_l is affine in β at fixed (α, A, B), so small actuators
  route demand sign-symmetrically; sign enters only through alignment with the
  baseline current, |b + εδ| − |b| ≈ ε·sgn(b)·δ, which is why the gaps are tiny.
  Sign becomes physical only in channels nonlinear in β (ρ_packet).
- (f) "The overlay changes the off-diagonal carrying-flow part of the metric
  while leaving the clock-lapse, rail-stretch, and throat-capacity parts
  unchanged" (`V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:226`); load
  bearing "likely requires coupled metric shaping" (`:299`).
- (g) Moves radial-null and current channels; p_l and packet safety fixed.
- (h) Packet-safe over a 10⁷-fold amplitude range, yet it only adds demand.
  At V10 the reduced-ADM routing is "only about `3.21e-6` of the V10 baseline
  global `delta_j_l` burden" (`V10_SUPPORT_SHELL_EDGE_STRESS.md:77`).
- (i) [L1] 60 dense Type IV points on the shell transition
  (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:87`); [L2]. No report checks g_σσ in the
  shell; an INVENTORY estimate gives α/√A ≈ 0.6 at the annulus centre,
  so amplitudes near 1 may tip the radial cones there (unverified).

#### G19. Shell timing: catch lead, temporal width, profile

- (a) Pulse centred at x_catch_packet − lead, normalized at the catch-window
  start, width w.
- (b) Reduced ADM: leads 0–1.25, widths 0.25–1.0; 4D: leads 1.0–1.55, widths
  0.25–0.40, gaussian/raised-cosine/minjerk.
- (c) 4D lead scan at width 0.30 (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:53, 65-66`):

| lead | radial null | radial current | packet drift |
|---:|---:|---:|---:|
| 1.35 | 1.027862 | 1.014999 | 0.024236 |
| 1.45 | 1.024110 | 1.013124 | 0.021838 |
| 1.55 | 1.021197 | 1.011647 | 0.019676 |

  Width 0.30 cleaner than 0.35/0.40 (`:45`); the best width shifts to 0.35 as
  strength rises (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:184`). Width
  0.25: neg-ρ_packet ratio 1.3068 while packet drift is 3.16e−8 (`:171-182`).
- (d) SWEEP. (e) DESIGN.
- (h) "The active metric can keep the live packet norm safe while still
  producing a packet-comoving source-accounting penalty elsewhere in the grid"
  (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:182`).
- (i) [L1] [L2].

#### G20. Shell metric partners: clock-lapse, rail-stretch, throat-capacity (κ_Q/a_β)

- (a) Each partner multiplies one metric function by exp(gain·W_shell), gain
  = a_β × ratio. Verbatim for the throat-capacity partner:
  "G_throat(s,l) = G_throat_base(s,l) * exp(kappa_Q * W_shell(s,l)),
  kappa_Q = a_beta * throat_capacity_ratio"
  (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:173-174`).
- (b) a_β = 0.5; clock ratios 0.25/0.375/0.5; rail ratios 0/0.25/0.5; throat
  ratios −0.5 … +0.5 (`V5_THROAT_CAPACITY_AND_GRADIENT_MATCHING_NOTE.md:6-12`;
  `STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md:41-51`).
- (c) *Clock-lapse*: best cases max burden 1.053–1.054, radial null
  1.020–1.028, current 1.012–1.015, angular pressure sets the max channel
  (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:89`); ~88% of the added
  radial-current burden lands in the shell–throat overlap band (`:91`).
  *Rail-stretch*: best max burden 1.0534 (0) → 1.0594 (0.25) → 1.0682 (0.5)
  (`:78-80`). *Throat-capacity*: best objective at ratio 0 (1.0974); −0.05
  lowers radial null 1.01995 → 1.01209 but raises current 1.0118 → 1.0205 and
  point peak 1.183 → 1.762; +0.05 puts max total and null in 1.079–1.080 with
  point peaks >2.68× (`STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md:57-80`);
  "the throat-capacity partner trades angular/throat shaping against
  radial-null/current and point-peak penalties too aggressively" (`:68`);
  "the failure mode is not packet causality" (`:68`).
- (d) SWEEP.
- (e) DESIGN. The report's summary "timing and gradient matching dominate
  amplitude tuning" (`V5_THROAT_CAPACITY_AND_GRADIENT_MATCHING_NOTE.md:31`) is a
  reading of these sweeps, not a derivation.
- (f) Clock 0.5 favours aggregate burden, 0.375 favours packet drift and
  shell–throat concentration (`V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:105, 279`).
- (h) **Confound**: the "coupled clock helps" comparison against the
  carrying-flow-only shell (max 1.0909) also changed lead and width
  (1.0/0.35 → 1.35–1.55/0.30), and the 81-case grid has no clock = 0 control
  (INVENTORY reading of `V5_HIGHRES_COUPLED_TIMING_SOURCE_FEASIBILITY.md:53, 65-66` against
  `V5_CONTINUOUS_SUPPORT_SHELL_4D_SOURCE_SWEEP.md:160`). The isolated clock effect is untested.
- (i) Throat-capacity edits R where the metric evolves, which I3 identifies as
  the Type IV mechanism and G31 forbids; its measured sharp null penalty
  points the same way [L1]. Stage I-A closed with throat capacity = 0
  (`STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md:110`).

#### G21. Shell radial profile, radial half-width and strength band

- (a) Radial window shape (raised-cosine annulus, Gaussian annulus, smooth
  box), half-width, and matched strength: "abs_amplitude * max |W_shell| =
  target_delta_beta_abs_max." (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:27`).
- (b) 48 matched-shape cases, 40 width cases, 120 strength cases
  (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:35`); strengths 0.15–0.35.
- (c) Shape at matched strength 0.25 (`V5_SUPPORT_SHELL_SHAPE_ROBUSTNESS_REPORT.md:113-115`):

| profile | max burden | packet drift | radial null | radial current |
|---|---:|---:|---:|---:|
| raised-cosine annulus | 1.013261 | 3.09e−8 | 1.007942 | 1.002684 |
| Gaussian annulus | 1.016165 | 1.51e−3 | 1.008492 | 1.003251 |
| smooth box | 1.052003 | 1.81e−2 | 1.019290 | 1.011380 |

  Half-width 0.48125 → 1.00: max burden 1.0133 → 1.0379, packet drift 3.09e−8
  → 3.13 (`:131-137`); 0.48125 is the code minimum, so narrower widths were
  untestable (`half_width = max(float(width), default_half_width, 1.0e-12)`,
  `source_ledger.py:448`). Strength ladder 0.15 → 0.35: max burden
  1.0083 → 1.0180 (≈0.05 per unit peak δβ, near-linear), point peak 1.000 →
  1.294 (superlinear above 0.25); drift < 1e−6 throughout (`:147-161`).
- (d) SWEEP. (e) DESIGN. INVENTORY INFERENCE: the raised-cosine annulus is
  compactly supported on the support-edge band while Gaussian and tanh-edged
  profiles have tails reaching the packet, consistent with the 10⁵-fold drift
  spread.
- (g) Aggregate burden linear in strength; point peak decouples above 0.25.
- (h) Compact support, not smoothness order alone, keeps the occupant readout
  quiet.
- (i) The September construction manifest uses a smooth-box shell, "so the old
  shape winner has a separate lineage" (`GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md:35`);
  regularity repair covers only the smooth-box/Gaussian shell (`:124-126`) [L1] [L2].

### 3.D Endpoint, release, receiver, collar and causal knobs (Stage II, May 19 – 24)

Stage II works on the entry-gated `wide4_start_m1p40` design and then on the
**beta075** geometry: release width 0.75, negative-l receiver `p003_mid`,
collar `rematch_w6_t1p5`. That frozen case,
`V5_smooth_split_horizon_escape_beta075_p003_mid_rematch_w6_t1p5`, is the one
that failed the Hawking–Ellis boundary gate (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:5-24`).
Entries marked **[β075]** rest on that geometry or on its release-0.75
predecessors.

The endpoint metric "J" is the selected radial-null deficit of the endpoint
layer. Selected margin = ρ + p_l − 2|j_l|; J = reset cap + support edge exactly
in every table (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:128-130`). The
receiver reports' one-sided "transfer" metric clips opposite-sign changes and
can disagree in sign with the raw J change; for example `post1p5` reports net
relief +0.0075 while raw J rises 0.9448 → 0.9493
(`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:94-97, 129`). The
entries below use raw J. Baselines move with grid by amounts comparable to
many knob effects: J at release width 0.25 is 0.986686 (61×83), 0.990430 (81×121)
and 1.010455 (151×225) (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:140`;
`STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md:132`; `STAGE2_ENDPOINT_JUNCTION_SOURCE_MILESTONE.md:182`).

#### G22. Endpoint smearing: edge width, catch width, edge carve, guard blend, temporal width

- (a) Spatial width and strength of the compact carve windows at the
  support-edge handoff, and their temporal width.
- (b) Edge width 7.2 → 9 → 11; catch 3.4 → 4.2; carve 0.16 → 0.12; current
  guard blend 0.25; temporal ×1.0 → ×1.4, at release width 0.25 (81×121) and
  0.75 (61×83) (`STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md:81-89`;
  `STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:15-24`).
- (c) J 0.990430395 → 0.990415489 at edge width 11; every spatial variant
  moves J by ≤ 8.6×10⁻⁵; the reset cap stays 0.568413667 (0.568412635 with the
  guard) (`STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md:130-137`). Temporal
  ×1.4 creates the only live defect: packet norm +16.81 at (σ, l) = (−0.769,
  −0.42), entry pre-catch (`:114-121, 138`). At release width 0.75 the reset
  stays 0.442605 across all variants (`STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:178-185`).
  SNEC screen: 0 violations in 17,052 windows (`STAGE2_ENDPOINT_THICKNESS_LADDER_CLOSEOUT.md:227-233`).
- (d) SWEEP (5 + 5 variants, two grids).
- (e) DESIGN.
- (g) **Decoupling**: endpoint J is insensitive to the spatial thickness of
  the carve windows; "the effective burden fraction and current share stay
  effectively fixed" while the apparent volume changes (`:188-192`).
- (h) "the endpoint obligation is stubborn enough that the next model should
  not try to hide it by another mask smear" (`:262-264`). Temporal broadening
  pushes support action into the live pre-catch corridor.
- (i) [L2] for the live defect; the release-0.75 repetition is [β075].

#### G23. Release-fade width ("reset-release widening"), matched hold and lags

- (a) Duration of shift removal: the fade lasts 4·w_β·multiplier after a hold
  (`source_ledger.py:313-316`). The project names `beta025/050/075/100` are
  these multipliers.
- (b) Multiplier 0.25/0.50/0.75/1.00; hold 0.10/0.25/0.50; lapse lag and
  carve lag 0/0.25 (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:98-106, 141-143, 170-172, 185-202`).
- (c) (61×83; `STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:130-139`)

| width | J | reset cap | reset current | support edge | support-edge current | support-edge p_Ω |
|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.986686 | 0.582542 | 0.318861 | 0.404144 | 0.060721 | 1.506623 |
| 0.75 | 0.964417 | 0.442605 | 0.240184 | 0.521812 | 0.105033 | 1.912497 |
| 1.00 | 0.944764 | 0.371175 | 0.177826 | 0.573589 | 0.133567 | 2.093173 |

  At 0.75: J −2.26%, reset −24.02%, reset current −24.67%, support edge
  +29.12%, support-edge current +72.98%, support-edge p_Ω +26.94%. About
  80–84% of the reset relief reappears in the support-edge shoulder
  (`STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN.md:157-164`). Reset-cap burden
  spreads: effective volume fraction 0.286 → 0.588 (0.75) → 0.780 (1.00)
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:211-213`). Hold 0.50: J 0.983927,
  reset 0.559395 (`:170-172`). Lags: "All three reproduce the baseline J split
  exactly at this precision" (`:185-186`). Live-clean at every width. Causal:
  post-release reachability hits 1 (0.75) vs 13 (1.00)
  (`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:193-194`).
- (d) SWEEP (4 widths, one grid); "needs confirmation on a denser grid"
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:264-265`).
- (e) DESIGN. **Type reading GEN-I**: the reset cap is 75.6%
  one-branch-negative (Type IV by I3) and the support edge 85.5%
  both-branches-negative (Type I NEC violation)
  (`STAGE2_ENDPOINT_THEORY_MEMO.md:36-49`). The knob converts current-selected
  (Type IV-like) reset deficit into support-edge load; the type of the
  transferred load was not measured.
- (f) Reset relief against support-edge load at ~80% transfer. The width also
  sets the receiver drive (w_rel − 0.25) and its timing
  (`source_ledger.py:559-576`), so release width, receiver dose and receiver
  phase move together.
- (g) **Decoupling**: only the release width moves the reset cap materially;
  "release beta width is load-bearing for endpoint source closure"
  (`STAGE2_ENDPOINT_RESET_RELEASE_LADDER.md:16`). Lapse and carve lags are
  fully decoupled from J.
- (h) Endpoint load follows the time profile of the shift removal, not the
  spatial thickness of the endpoint windows (contrast G22).
- (i) Width 0.75 is the beta075 geometry [β075][L1]; decompression is the
  Type IV generator acting on this reset cap (G5).

#### G24. Receiver actuation channel (lapse, radial stretch, shift relaxation, areal radius)

- (a) Which metric function a post-release support-edge "receiver" window
  edits: α, A, β toward comoving, or B (`source_ledger.py:1484-1562`).
- (b) Radial/current R1, positive-l angular R2, R1+R2; lapse 0.04, radial
  0.04, lapse+radial, lapse+radial+angular 0.015 (all release width 0.75)
  (`STAGE2_BETA_MEMORY_RECEIVER_SMOKE_MEMO.md:34-60`;
  `STAGE2_BETA_MEMORY_RECEIVER_LAPSE_RADIAL_MEMO.md:39-56`).
- (c)

| variant | J | support-edge current | support-edge angular |
|---|---:|---:|---:|
| baseline | 0.964417 | 0.105033 | 1.912497 |
| lapse 0.04 | 0.965803 | 0.104954 | 2.537997 |
| radial 0.04 | 0.965790 | 0.106144 | 1.941453 |
| lapse + radial | 0.967548 | 0.106048 | 2.464310 |
| lapse + radial + angular 0.015 | 0.954120 | 0.214547 | 2.566714 |
| R2 positive angular | 0.949838 | 0.551170 | 2.313310 |

  "The only tested knob that moves selected-null is angular capacity, and
  every tested positive-l angular realization has carried a current/angular
  penalty" (`STAGE2_BETA_MEMORY_RECEIVER_LAPSE_RADIAL_MEMO.md:72-75`).
- (d) SWEEP (9 variants). (e) Measured. **Direction GEN-I**: by I2 only an R
  edit changes the radial null energies directly; lapse and stretch enter
  them only through the null Hessian. A lapse-only edit raising angular stress
  33% is consistent with I16 (clock curvature X feeds p_t), which no report
  derives.
- (i) [β075] [L1] [L2].

#### G25. Receiver placement, angular gain, localization and persistence

- (a) Side of the throat (positive l, negative l, bilateral) and log gain of
  a post-release areal-radius flange at the support edge; its radial window
  (inner/outer multipliers, outer power), memory gain and post-release
  persistence (`source_ledger.py:559-630`).
- (b) Dose 0.0075/0.015 on each side (`STAGE2_BETA_MEMORY_RECEIVER_ANGULAR_SYMMETRY_MEMO.md:40-48`);
  negative-l 0.0075/0.015/0.0225/0.03 (`STAGE2_NEGATIVE_L_RECEIVER_LADDER_CLOSEOUT.md:40-60`);
  mid (0.50/1.025, power 0.5) vs outer at 81×121
  (`STAGE2_NEGATIVE_L_RECEIVER_PROMOTION_GATE.md:15-18, 46-56`); persistence,
  gain and localization variants at release width 1.00
  (`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:55-100`).
- (c) Side at 0.015: positive J 0.957289 with support current 0.215404
  (+105%); negative J 0.954948 with current 0.107180 (+2%); bilateral 0.947820
  (`STAGE2_BETA_MEMORY_RECEIVER_ANGULAR_SYMMETRY_MEMO.md:43-45`). Negative-l
  dose: J 0.964417 → 0.959711 → 0.954948 → 0.950129 → 0.946962; reset cap
  0.442605 → 0.425718; support edge flat 0.5218 → 0.5212; current +0.00108 per
  step; angular flat 1.9124–1.9126 (`STAGE2_NEGATIVE_L_RECEIVER_LADDER_CLOSEOUT.md:40-60`).
  Dense mid vs outer (raw J): baseline 0.970928, mid 0.958663 (−1.26%), outer
  0.939090 (−3.28%) (`STAGE2_NEGATIVE_L_RECEIVER_PROMOTION_GATE.md:46-48`).
  At release width 1.00 only `gain1p0` beats the baseline in raw J (0.934785
  vs 0.944764); `p003_mid` gives 0.964451 (`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:94-100`).
  *Algebraic type (later)*: receiver width ×{0.5, 1, 2} gives minimum
  discriminants −0.00422/−0.00206/−0.00125, Type IV at all three; narrowing
  raises the peak while ∫|Im λ| changes little (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:219-228`).
  *Curvature*: the mid profile's u^{1/2} factor makes a √ cusp at the inner
  edge; density −0.064 → −107.6 as the step falls 0.0025 → 1.95×10⁻⁵;
  setting only the receiver gain to 0 gives finite values
  (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:160-183`).
- (d) SWEEP.
- (e) DESIGN. **GEN-I pieces**: (i) spatially disjoint edits superpose
  exactly by locality of G_μν — bilateral J drop 0.016597 = 0.007128 +
  0.009469 and current +0.112518 = +0.110371 + 0.002147 (INVENTORY arithmetic
  on `STAGE2_BETA_MEMORY_RECEIVER_ANGULAR_SYMMETRY_MEMO.md:43-45`); (ii) J
  linear in small log gain (exp(g·w) ≈ 1 + g·w); (iii) a d^p cusp gives
  d^{p−2} stress (I13).
- (f) The receiver phase must match the release width: "the receiver should
  not be scaled by geometry alone. It should carry a phase/tail knob"
  (`STAGE2_NEGATIVE_L_RECEIVER_BETA100_RETIMING_LOCALITY.md:262-265`). The
  receiver dose lowers reset J but introduced the singular inner edge.
- (g) The two sides decouple exactly. Short memory underperforms: "the
  post-release memory tail is doing real work"
  (`STAGE2_NEGATIVE_L_RECEIVER_LADDER_CLOSEOUT.md:114-116`).
- (h) Orientation matters: +l costs 105% current, −l costs 2%, and the reports
  give no mechanism. INVENTORY INFERENCE: the packet centreline follows l = σ,
  so the +l flange overlaps the just-released carrier near l ≈ 1.5–1.9. The
  removed burden is booked almost entirely to the reset cap though the flange
  sits at the support edge. `mid` was promoted over `outer` on the one-sided
  transfer metric while `outer` had the larger raw J drop. The reset effect
  reverses sign between release widths 0.75 and 1.00.
- (i) **[β075]; `p003_mid` is the frozen geometry's receiver. Its √ cusp and
  outer slope jump are the singular-curvature finding, and the Type IV peak
  sits just outside its outer clip** (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:5-11, 185-189`) [L1].
  The May statement "There is no evidence here of a new curvature blow-up caused
  by the receiver" (`STAGE2_GZ_OBSTRUCTION_SCREEN.md:105`) is contradicted by that refinement.

#### G26. β-rematch collar: gain, shape, floor, width, temporal width, schedule

- (a) δβ = −g·W_r·(v + β), which drives the local shift toward the packet's
  coordinate velocity (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:29`;
  `source_ledger.py:1522-1526`); shapes core/shoulder/annular/edge_soften/
  trailing_edge; centre floor joined by max, blend or add; spatial and temporal
  width multipliers; schedule live_only/catch_release/coordinated_release.
- (b) Gain 0.1–1.8; floor 0.45–0.65; width ×1.0–1.6 (Stage I); Stage II
  generator `rematch_w6_t1p5` vs `rematch_w8_t2p0` (gain 1.8, floor 0.6); local
  bracket w5.5/6.0/6.5 at t1.5 and t1.25 on dense beta075; mitigation edits
  (β smoothing, packet-β relaxation, areal smoothing, γ_ll smoothing).
- (c) Stage I: rematch gain alone at V5 lowers the point peak 7.60 → 6.56 at
  flat live null (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:78-80`); at V10
  gain 0.6–1.0 restores safety while live null rises 0.120 → 0.157 (`:132-134`):
  "high beta rematch can restore V10 safety, but it restores radial-null burden
  too" (`:177`). Moving the collar off the pre-catch schedule gives 0 safe
  rows: "The beta floor is not merely a release cleanup term. At V5 it is also
  preserving live packet causal margin before catch/rematch"
  (`STAGE1_RELEASE_CHOREOGRAPHY_REFREEZE.md:100-105`). Blend vs max union at
  81×109: blend 1.6/1.0 safe with point peak 8.63; max 1.0/1.0 peak 117.2
  (`STAGE1_RELEASE_CHOREOGRAPHY_ARTIFACT_CHECK.md:113-120`). Stage II generator
  (`STAGE2_BETA_COLLAR_GENERATOR_SCREEN.md:74-168`):

| quantity | baseline | w6_t1p5 | w8_t2p0 |
|---|---:|---:|---:|
| caustic-like bundles | 8/8 | 0/8 | 0/8 |
| worst l-width ratio | 0.009603 | 0.275792 | 0.394689 |
| max live packet norm | – | −9.935129 | −6.577702 |
| live neg-T_kk ratio | 1 | 0.852 | 0.819 |
| live \|j_l\| ratio | 1 | 0.718 | 0.674 |
| live neg-ρ_packet | – | 0.000483 | 0.005930 |

  Local bracket w5.5 → w6.5: live neg-T_kk 12.163 → 11.867, live
  neg-ρ_packet 3.28×10⁻⁵ → 1.35×10⁻³, support-edge selected null 0.6381 →
  0.6463; temporal width "essentially neutral"
  (`STAGE2_BETA075_COLLAR_LOCAL_BRACKET_CHECKPOINT.md:29-74`; "essentially neutral", `:71`). Mitigation:
  β l-smoothing 0.45 widens the bundle 1.942×, packet-β relaxation 1.461×,
  areal smoothing 0.989×, γ_ll smoothing 0.354× (worse)
  (`STAGE2_COLLAR_MITIGATION_SCREEN.md:91-99`).
- (d) SWEEP + SINGLE.
- (e) **GEN-I**: the timelike margin gains algebraically,
  v+β → (1−gW)(v+β), best at gW = 1 (I7); radial bundle width responds to
  ∂_lβ and ∂_l(α/√A), never to B (I11), which the mitigation ranking
  confirms. Source-side effects DESIGN.
- (f) Collar width trades live relief against support-edge J and live
  packet-frame negative density (41× rise over the bracket); optical relief
  trades against packet-norm margin.
- (g) Live p_l is insensitive to rematch gain
  (`STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:78-134`); reset-cap J is flat
  across the bracket.
- (h) The rematch is needed before the catch, not only at release. The wider
  collar places negative energy density inside the packet frame, an occupant
  WEC violation.
- (i) `rematch_w6_t1p5` is in the frozen geometry; 1,862 dense Type IV points
  sit on the rematch transition (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:89-90`)
  [β075][L1]. The collar's packet-norm success is built on the unit-speed
  window [L2].

#### G27. Causal-margin guard and local cone tilt

- (a) Clamp |β| to (1−m)α/√A inside a guard window (packet, edge or support),
  implementing "enforce a local margin such as `abs(beta) < alpha /
  sqrt(gamma_ll)`" (`STAGE2_GZ_OBSTRUCTION_SCREEN.md:143-144`;
  `source_ledger.py:1527-1546`).
- (b) Packet/edge/support guard on four release-width/receiver variants.
- (c) (`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:132-140`)

| guard | live branch-crossing edges | live g_σσ ≥ 0 points | min branch margin |
|---|---:|---:|---:|
| none | 53 | 133 | 0.008881 |
| packet | 31 | 87 | 0.024927 |
| edge | 30 | 86 | 0.006818 |
| support | 26 | 82 | 0.000029 |

  Every guarded case keeps a live g_σσ ≥ 0 region and fails the GZ screen;
  live packet norms stay negative (`:119-126`). About 39–42% of live samples
  have g_σσ ≥ 0 across ledgers: 259/620, 98/237, 133/342
  (`STAGE2_GZ_OBSTRUCTION_SCREEN.md:77`; `STAGE2_HORIZON_ESCAPE_REFINED_BETA075_CORE.md:105`;
  `STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:132`). All radial
  seeds escape to the domain boundary (136/136, 1056/1056 at s12/s15)
  (`STAGE2_BETA_COLLAR_GENERATOR_SCREEN.md:127`; `STAGE2_SCHEDULED_ADM_CONFIDENCE_RUN.md:56-60`).
- (d) SWEEP. (e) Construction GEN-I (I5); effect DESIGN.
- (h) "it suppresses some discrete crossings while sharpening one local
  pinch" (`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:142-147`):
  fewer crossings can mean a thinner margin. By I5, g_σσ ≥ 0 marks an ergo-like
  region, not a horizon, and escape audits confirm rays leave it.
- (i) [β075]; [L4] escape means reaching either end of a two-ended space.

### 3.E Regularity repairs, reset sources and the constant-radius rule (Sept 8 – 23)

These are the LE repair attempts on the frozen beta075 geometry, plus the
design rule that closed the era. All use the repaired classifier. Every entry
is **[β075]** except G31, which replaces the geometry.

#### G28. Join regularity: receiver cusp, origin kink, shell cap

- (a) Smoothness class of the joins where localized metric edits switch on:
  the receiver's u^{1/2} inner edge (√ cusp) and clipped outer edge (slope
  jump), replaced by quintic Hermite C2 ends; the |l| kink of the lapse
  shoulder and shell radius at l = 0, replaced by
  r_a = a(15/8 t² − 5/4 t⁴ + 3/8 t⁶) inside a = 0.1; the shell's temporal cap,
  which began at a nonzero Gaussian slope, replaced by a C2 quintic cap
  (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:28-35`; `LE_BOUNDED_METRIC_REPAIR.md:26-46`).
- (b) √ cusp vs C2; blend fraction 0.0625/0.125/0.25; control receiver gain 0;
  origin a = 0.1 vs kink; control η_N = 0; cap slope jump vs C2.
- (c) *Receiver inner edge*: frozen density −0.064 → −107.6 over five step
  halvings, ×2^{3/2} per halving (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:171-180`);
  repaired 0.013457 → 0.013684, approaching the receiver-free value 0.013686
  (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:66-77`). One-sided absolute stress
  integral over [ε, 0.02]: frozen 0.001205/0.003796/0.012015 for ε =
  10⁻³/10⁻⁴/10⁻⁵ (unbounded, ∝ ε^{−1/2}); repaired static 0.000408/0.000430/
  0.000432 (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:190-199`; `LE_RECEIVER_C2_REPAIR_ATTEMPT.md:89-93`).
  *Outer clip*: density ∝ h⁻¹ (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:185-188`).
  *Origin*: angular pressure 0.001905 → 0.025804 (∝ h⁻¹) with the kink,
  ≈0.0017263 across eight levels after repair (`LE_BOUNDED_METRIC_REPAIR.md:57-61`).
  *Shell cap*: the slope jump (−4.70514 in the shift derivative) gave finite
  sampled G at the join (`LE_BOUNDED_METRIC_REPAIR.md:49-55`).
  *Algebraic type*: unchanged — the 104 Type IV witnesses outside the repair
  bands have bit-identical tensors; 1,365 vs 1,361 active Type IV samples;
  the repaired inner edge is "finite and Type IV" (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:100-120`).
  *Packet/service*: not re-evaluated.
- (d) DERIVATION ("The metric is continuous with a square-root cusp there.
  Its second radial derivative grows as d^{−3/2}", `LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:167-169`)
  + SWEEP (refinement ladders) + CONTROL.
- (e) **GEN-I** (I13): stress growth follows the join class — √ cusp
  divergent and non-integrable, slope jump h⁻¹ surface term, C2 first-order
  convergent, C∞ scheme-order convergent. Coefficients DESIGN.
- (f) Blend fraction changes burdens by < 0.3%.
- (g) **Decoupling**: repairs are exactly local — "These witnesses lie outside
  the repair bands, including their curvature stencils, so this equality is a
  direct locality check" (`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:102-104`). Regularity
  and algebraic type decouple.
- (h) Removing the singular term reveals Type IV beneath it: "the original
  singular term had dominated its classification" (`:119-120`). After repair
  the active edge burden is ~10× the static one (0.004625 vs 0.000432). A
  temporal slope jump gave no measured divergence, unexplained.
- (i) Local success; gate still fails (`LE_BOUNDED_METRIC_REPAIR.md:236-249`).
  Superseded by C∞ primitives on the constant-R track
  (`CONSTANT_RADIUS_TRACK.md:122-137`). C1-only joins never tested.

#### G29. Coupled reset source: tangential material plus two null streams

- (a) Replace the demanded reset stress by an explicit source: released string
  pairs B, a positive-enthalpy material of density F with p_t/ρ = 1/4, and two
  counter-streaming null streams, blended by a C2 handoff window
  (`LE_COUPLED_RESET_SOURCE_ATTEMPT.md:62-93`).
- (b) One registered value per parameter, 9 phases × 3 resolutions.
- (c) 2,030 Type IV of 8,253 samples (`:151-153`). At the old witness Δ turns
  from −0.00206 to +0.00123 (Type I), and a new converged Type IV witness
  appears at l = −2.133 inside the source plateau, plus Type IV at σ = 2.6
  where the reference had none (`:168-191`). Mass: the areal-gauge constraint
  needs δm ≈ 1.433 where ≈0.533 is available before f = 0; f reaches −0.61 at
  reset (`:196-210`).
- (d) SINGLE; mechanism is DERIVATION: "h_total=E+P_r=h_b+3F, Δ=(h_b+3F)²−4J²
  … the energy change 2F−B enters the Hamiltonian equation and consumes more
  radial mass allowance than this geometry provides" (`:229-243`).
- (e) Mass relation GEN-I (I27); the enthalpy relation is an identity of this
  prescription.
- (f) Positive-enthalpy material helps Type IV and costs mass: "These two
  requirements therefore need a common source and geometry construction"
  (`:246-247`).
- (g) "Changing the tangential-pressure ratio alone leaves both failing
  expressions unchanged" (`:243-244`); B cancels from the enthalpy.
- (h) Fixing one witness moves Type IV outward into the source plateau.
- (i) Stopped; superseded by G30 and G31.

#### G30. Reset inverse search: geometry path and moving infrastructure

- (a) Ten controls on the reset geometry and source (duration, offsets,
  donor/reservoir placement), a direct blend vs a path through rest
  waypoints, and stationary vs moving (|v| ≤ 0.5) infrastructure
  (`LE_RESET_INVERSE_SEARCH.md:64-125, 168-187`).
- (b) 1,024 Sobol points, 16 boundary seeds, 8 Powell solves.
- (c) Best objective: direct/stationary 0.3015, direct/moving 0.2523,
  waypoints 38.5/37.6 (`:263-270`). Best moving candidate: minimum material
  density −5.92×10⁻⁵ vs −2.56×10⁻³ stationary (≈43×), radial margin
  −7.30×10⁻⁴ (Type IV remains), angular mismatch 2.86×10⁻³ vs 1.49×10⁻³
  (`:282-286`). Type IV persists at positive density (`:305-310`). 780
  controls exhausted the lapse range and remain undecided (`:272-274`).
- (d) SWEEP + DERIVATION of an onset obstruction (I28).
- (e) The obstruction holds "for these source families and boundary
  conditions" (`:419-421`); boosting infrastructure preserves the radial
  discriminant (I26), so motion alone cannot cure Type IV.
- (f) Moving infrastructure trades material deficit against angular mismatch,
  speed saturation and a lapse shift of up to 93% (`:312-316`).
- (h) The direct path beats rest waypoints by >100× in objective.
- (i) Stopped; superseded by G31.

#### G31. Constant areal radius wherever the metric evolves (post-era design rule, Sept 23)

- (a) "Hold the areal radius constant wherever the service metric evolves, and
  confine every variation of the radius to regions where the geometry is
  static" (`CONSTANT_RADIUS_TRACK.md:73-76`). Knobs within it: track radius
  R_b, half-length L_b, end-transition width Δ, decompression schedule.
- (b) R_b 1.4/1.75/2.14; L_b 4.5/5/6; Δ 0.75/1.5/3; five decompression
  schedules (`CONSTANT_RADIUS_TRACK.md:181-185, 297-303`).
- (c) Type IV 13,587 → 0 of 141,661; min T₊T₋ −2.079×10⁻³ → 0; max |j|
  0.0230 → 0 (`:171-176`); all 40,071 points Type I across R_b/L_b variants
  (`:181-183`). Live corridor: min T_kk −0.656 → 0; min packet-frame density
  −1.33×10⁻³ → +0.012992 = 1/(8πR_b²) (`:269-274`). Packet norms, null speeds,
  carrying flow and schedule unchanged, −9.935129 (`:115-116, 233`).
  Both-shrinking traces 77 → 0 (`:233-243`). Cost: angular NEC fails where
  K > 1/R_b² (min ρ+p_Ω −0.0741) (`:269-274, 288-292`). End transitions:
  peak static radial deficit −0.118/−0.058/−0.028 for Δ = 0.75/1.5/3 at fixed
  integrated opening 2.000001 (`:183-185, 325-326`).
- (d) IDENTITY (I4, I18) + SWEEP.
- (e) **GEN-I**: the Type IV removal, the string-cloud radial block, the
  transfer of all 2D dynamics to p_Ω = −K/8π, the invariance of packet
  kinematics under B edits, and peak ∝ 1/Δ at fixed opening all follow from
  I1–I4 and I18.
- (g) **Decoupling identity**: "Packet norms, radial null speeds, the carrying
  flow and the service schedule depend only on (α,β,γ_ℓℓ)" (`:115-116`).
- (h) The throat-era "S0 string cloud" becomes exact: "ρR_b²=1/(8π) … the S_0
  role, now exact" (`:346-348`).
- (i) Post-era. Still two-ended [L4]; the end transitions "follow from the
  reduced model's two asymptotic ends" (`:119-120`). Service ratios still use
  l = σ [L3]. The one-space axial track later moves the Type IV question into
  its transverse boundary layer (`:338-342`).

### 3.F Source-model knobs on the beta075 demand (May 21 – 24)

Every entry here is **[β075]** (dense 377×241 and 189×121 meshes over
σ ∈ [−1.5, 15], l ∈ [−6, 6]; `STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md:19, 37, 41`).
Each is tagged **(Adm)** when its conclusion assumes a medium with a rest
frame can supply the demand — undermined by the Type IV layer [L1] — or
**(Geo)** when it reads only the demanded geometry. The cluster saw the Type
IV content in May: before regulation the endpoint-J sector was Type IV on
11.1% of volume and 25.9% of burden (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:100-101`).
It then changed the stress (M1) rather than the geometry. The endpoint fit
later measured 46–48% off its J target (`LE_BOUNDARY_GATE_PREFLIGHT.md:115-119`),
and stored rest energies were wrong on most dense rows [L5]. No file in this
cluster reports passenger aging, tides or acceleration.

#### M1. Endpoint current regulator (safety factor) — (Adm)

- (a) Minimal Type I restoration: reg = max(0, 2|j_l| − |ρ+p_l|), added as
  δρ = δp_l = ½ sgn(ρ+p_l)·reg, scaled by a safety factor SF
  (`STAGE2_BETA075_ENDPOINT_CURRENT_REGULATOR_SCREEN.md:56-66`).
- (b) SF 1.00/1.05/1.10/1.25; depletion to ½, 1/10, 1%, 0.
- (c) Regulator/source 0.0377 → 0.0472 (baseline); p99 heat ratio 1.000
  (luminal) → 0.9465 (`STAGE2_BETA075_REGULATED_MEDIUM_ADMISSIBILITY_AUDIT.md:109-114`);
  0 post-regulator Type IV rows, 0 live regulator rows (regulator screen
  `:84-87`); local regulator/source ratio up to 1.0527 at the release support
  edge (`STAGE2_BETA075_BV_ANALOGUE_SOURCE_PATHOLOGY_MAP.md:116, 180-184`).
  Zero regulator: all 56 watch rows fail at unchanged cone margin
  (`STAGE2_BETA075_PRINCIPAL_SYMBOL_SENSITIVITY.md:21-24, 65-69`).
- (d) SWEEP. (e) The formula and its D = 0 endpoint at SF = 1 are GEN-I (I24).
- (h) The regulated tensor is not the Einstein demand.
- (i) Core (Adm) item: on the Type IV rows no rest-frame medium supplies the
  demand (`THROAT_GEOMETRY_CLARIFICATION.md:157-158`).

#### M2. Source class — (Adm)

- (b) Canonical scalar, phantom scalar, ordinary Type I anisotropic fluid,
  regulated anisotropic medium.
- (c) Scalar-compatible volume 0.380/0.336 (canonical) and 0.382/0.407
  (phantom); the Type I fluid fails because Type IV carries 0.2515/0.2590 of
  the burden; the regulated medium passes
  (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:84-103`).
- (e) **GEN-I exclusion**: a minimally coupled scalar's radial block "is
  boost-diagonalizable and the signs of rho+p_l and p_l-pOmega are tied to the
  scalar kinetic sign" (`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md:79-81`),
  so it never supplies Type IV (I23).

#### M3. Support-reservoir ansatz and basis size — (Adm)

- (a) Exchange current J_support = P u + F s between endpoint medium and
  support, fitted by a smooth algebraic P/F form or by a phase-aware
  stroke/stress wave operator with basis, ridge and Laplacian options
  (`STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md:55-58`;
  `STAGE2_BETA075_SOURCE_FAMILY_VALIDATION.md:44-52`).
- (c) Smooth P/F: best normalized L1 0.614/0.793 (fails 0.50). Stroke/stress
  24×14: 0.223/0.449 (passes) with 13,088/15,527 effective coefficients against
  28,359 active rows; Laplacian off on dense 0.5688 (fails); total closure
  local P/F 0.5446 against a 0.55 gate
  (`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md:896-915, 1116-1139, 1367-1373, 1524-1531`).
- (e) DESIGN. The split ∇·T_endpoint + J = 0 is GEN-I, and J_perp = 0 is forced
  by spherical symmetry, so "angular exchange absence" gates carry no evidential
  weight (INVENTORY DERIVATION). The support tensor's type is left free by its
  divergence (I15).
- (h) A near-interpolating basis passes; ~45% (L2) of the endpoint divergence
  remains uncancelled at "pass".

#### M4. Source-time class and service-aligned scheduling — (Adm, transport)

- (b) Observed schedule; service-aligned pulses of 1–47 steps; convex-kernel
  envelope; common jitter radius 0–8 (165 cases); arbitrary impulse.
- (c) Max budget fraction 0.121 (observed) → 0.176–0.194 (widest aligned pulse)
  → 0.743 (1-step pulse and convex envelope; unchanged under jitter) → 1.159
  (arbitrary impulse, fail) (`STAGE2_BETA075_FULL_SYSTEM_FIXED_BACKGROUND_EVOLUTION.md:23-28`;
  `STAGE2_BETA075_SERVICE_ALIGNED_SCHEDULE.md:47-66`;
  `STAGE2_BETA075_TIMING_JITTER_CERTIFICATE.md:38-55`;
  `STAGE2_BETA075_ACTION_PDE_PROOF_OBLIGATION.md:48-51`).
- (e) The convex-kernel bound is a DERIVATION: "The one-step service-aligned
  basis response bounds any common nonnegative temporal kernel over the same
  service-ordered source bins by linearity and positivity of the transport
  operator" (`STAGE2_BETA075_ALIGNED_ENVELOPE_CERTIFICATE.md:14-16`). It holds
  for any linear positive transport; magnitudes DESIGN.
- (h) With the same source, schedule order alone moves the budget 0.12 → 0.74 → 1.16.

#### M5. Heat-current rapidity: evolution variable, kick amplitude, injection form — (Adm, transport)

- (c) Raw heat ratio +1e−4 fails, rapidity +1e−4 passes (margin 2.25e−5,
  independent of damping) (`STAGE2_BETA075_REDUCED_TRANSPORT_EVOLUTION_PILOT.md:13-20`);
  large (5×) impulse budget 1.434 fails, distributed pulse 0.850 passes
  (`STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28`;
  `STAGE2_BETA075_SUPPORT_SOURCE_DYNAMICS.md:25-29`).
- (e) **GEN-I link** (I25): the heat-mode margin equals the Type I margin; the
  minimum cone margin 7.881e−5 and transport margin 7.983e−5 sit on the same
  row (`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:43`;
  `STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28`). These "transport"
  results are therefore not geometric-only: on Type IV rows v_q > 1 and the
  rapidity is undefined.
- (h) Spreading the same large source in time turns a fail into a pass.

#### M6. Support-edge source reshaping (cap 0.95) — (Adm, transport)

- (c) Smoothing leaves overdrive at 2.0 (2.0756 → 1.9997); a per-slice cap at
  0.95 of local budget brings outward/inward to 0.289/0.373, with slice scales
  down to 0.093, and moves the large-amplitude failure to release (1.445)
  (`STAGE2_BETA075_SUPPORT_EDGE_SOURCE_RESHAPING.md:61-114`).
- (h) Smoothing does not repair amplitude overdrive; normalization does, at
  the cost of sharp scale jumps.

#### M7. Mesh resolution (189×121 → 377×241) — mixed

- (c) Integrated channel totals agree within ~1%
  (`STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md:93-98`); extrema degrade:
  max live packet norm −9.935 → −6.334 (`:84-85`), min cone margin 2.41e−4 →
  7.88e−5 (`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:34-35`),
  reset-cap edge-tail fit coefficient 1.067 → 4.828 (`STAGE2_BETA075_DENSE_ENDPOINT_SOURCE_STABILITY.md:158-159`).
- (h) Integrated demand converges while minima keep shrinking — consistent
  with the singular receiver edge and thin Type IV layer later found (G25, G28).
  Packet norm (Geo) [L2]; the rest (Adm).

#### M8. 3+1 "backreaction" scenario amplitude — (Adm)

- (c) No Einstein solve: the driver is the residual ∇·(T_endpoint + T_support),
  propagated with scenario multipliers ≤1.0588; mean driver 0.476/0.55, peak
  1.652/1.75 (`STAGE2_BETA075_FIRST_ORDER_3P1_COUPLING.md:61-66`;
  `STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md:48-75`); the light version was
  demoted to a "light local off-axis/backreaction proxy"
  (`STAGE2_BETA075_3P1_BACKREACTION_CAPSTONE.md:7-14`).
- (i) (Adm): the driver comes from fitted sources.

### 3.G Demand-decomposition and diagnostic choices (May 19 – 24)

These change how the demand is read, not the metric. They matter for the book
because they decided verdicts.

#### D1. Source-role partition (A–I oracle roles; composite ansatz)

- (a) Assignment of demand by channel, stage, region and live flag to roles
  A (infrastructure radial null) … I
  (`STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md:20, 26-47`).
- (c) Coverage 0.99 (radial null), 0.72 (pressure), 0.34–0.40 (current);
  live residuals 0 "should not be read as physical closure" (`:57-58, 77-80`).
  Fitted sector ratios: infrastructure p_l/ρ = −1.002; live trim p_l/ρ = −1.148;
  current relaxation H ρ/j = 0.115 (`STAGE2_COMPOSITE_SOURCE_ANSATZ_PROMOTED_PAIR.md:60-65, 92-93`).
- (e) Accounting. INVENTORY DERIVATION from the fitted means: H is
  flux-dominated (|ρ+p_l| = 0.011|j| < 2|j|), i.e. Type IV; the near-saturated
  string-cloud fit p_l/ρ = −0.999288, j/ρ = −0.000485
  (`STAGE2_ENTRY_SECTOR_CLOSURE_DENSE.md:124-125`) gives radial null energies
  of opposite sign — a tiny current flips a string cloud to Type IV.
- (h) The "constant-flux string cloud" Φ = 0.039772 is the geometry's own
  W-term ≈ 1/(8π) (I12), not an independent matter finding.
- (i) Promoted pair and entry-gated geometry (pre-beta075); type untested.

#### D2. SNEC smearing width, coverage filter, domain and parameterization

- (a) Gaussian smearing width τ of the null-projected stress along radial
  rays; a scoreability filter (≥80% support and kernel coverage); lapse vs
  affine parameter; harness floor −8πB/τ² with B = 1/(32π)
  (`STAGE2_HARD_AFFINE_SNEC_PROMOTED_PAIR.md:22-43`;
  `STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md:25-29`;
  `STAGE2_AFFINE_REPARAM_SNEC_AUDIT.md:17-24`).
- (c) Margin shrinks with τ (15.97 at τ = 0.125 → 0.0412 at τ = 2) because the
  floor scales as τ⁻² while smeared stress saturates
  (`STAGE2_HARD_AFFINE_SNEC_ROBUSTNESS.md:42-53`). Scoreability flips verdicts:
  189 raw violations and 0 scoreable at τ = 4 on 81×109
  (`STAGE2_HARD_AFFINE_SNEC_ADVERSARIAL.md:73`). Affine non-affinity is large
  (max dλ/dσ 1291) yet the beta075 run stays clean: 0 violations in 175,851
  windows (`STAGE2_AFFINE_REPARAM_SNEC_AUDIT.md:106-107, 130-133, 171-172`).
  The finite-domain ANEC total on beta075 is negative (worst −1.797/−1.143),
  dominated by the closure residual
  (`STAGE2_BETA075_FINITE_DOMAIN_RADIAL_ANEC_DIAGNOSTIC.md:60-73`).
- (e) Screen on demanded channels, "not a physical SNEC". INVENTORY flag: the
  integrand stays the orthonormal T̂_kk (only the measure is affine), and the
  harness floor −1/(4τ²) is 8π looser than the unit-normalized
  Freivogel–Krommydas form −B/τ²; the extended-domain scoreable values
  −0.00261 (τ = 2) and −0.00069 (τ = 4) would fail the tighter form
  (INVENTORY flag; unverified against the literature normalization).
- (h) SNEC-clean does not imply finite-domain ANEC-clean.
- (i) Only the beta075 package was rerun with affine λ [β075]; promoted-pair
  results remain lapse-parameterized.

#### D3. Nonminimal scalar source screen (profile × φ₀ × ξ)

- (b) 5 profiles, φ₀ ∈ {0.05 … 1}, ξ ∈ {0, 1/6, 0.5, 1}; a localized fixed-metric
  solve (`STAGE2_PROMOTED_PAIR_SCALAR_KILL_SCREEN_PROGRESS.md:49-70`).
- (c) Best radial-null coverage 0.0072 at ξ = 1; top-20 demand/supply overlap
  0/20 (the scalar's negative T_kk lands in reset rows, the demand in
  entry/catch rows); localized solve 7.77×10⁻⁶ (`:87-88, 142-171, 228-232`).
- (e) Measured; minimally coupled canonical fields supply none by I23.

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

## 5. General identities for spherical warped products

Status labels:

- **DERIVED-IN-REPO**: the report states the relation and derives it or
  checks it against analytic controls.
- **STATED**: asserted in a report or docstring without derivation; standard GR.
- **INVENTORY DERIVATION**: derived for this inventory from the repo's
  definitions; not stated in any report. Needs a textbook derivation before use.

Notation: the book's class is ds² = −α²dσ² + A(dl+βdσ)² + B dΩ², R=√B.
`COUPLED_SOURCE_ROLE_AUDIT.md` and `ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md`
write **A for the lapse** in a static proper-distance gauge
(ds² = −A²dt² + dl² + R²dΩ²); `LE_COUPLED_RESET_SOURCE_ATTEMPT.md` and
`LE_RESET_INVERSE_SEARCH.md` use areal gauge (r, f=1−2m/r) and write B for a
string density. The identities below keep each source's notation and state it.

Several of the cleanest statements (I1–I4) were written on 2026-09-23 in
`CONSTANT_RADIUS_TRACK.md` and `adm_harness/warped_product.py`, after the era
closed. They are exact for every metric of the class, so they govern every
throat-era geometry retroactively.

### 5.1 Time-dependent class identities (any α, β, A, B)

**I1. Warped-product Einstein tensor.** For g = g_ab dx^a dx^b + R²dΩ² on the
(σ,l) quotient,
"G_ab = −(2/R)∇_a∇_bR + g_ab[(2/R)□R + ((∇R)²−1)/R²], G^θ_θ = □R/R − K"
(`CONSTANT_RADIUS_TRACK.md:145-149`; `toolkit/adm_harness_cli/adm_harness/warped_product.py:3-7`).
K is the Gaussian curvature of the quotient metric. STATED; validated on
Ellis, a dust cosmology and Painlevé–Gullstrand Schwarzschild
(`CONSTANT_RADIUS_TRACK.md:154-158`).

**I2. Radial null energy is the null Hessian of the areal radius.**
"every radial null vector k satisfies 8πT(k,k) = G(k,k) = −(2/R) k^a k^b ∇_a∇_b R"
(`CONSTANT_RADIUS_TRACK.md:29-35`; `warped_product.py:9-10`). For an affinely
parametrized radial null ray this reads 8πT(k,k) = −(2/R) d²R/dλ²: the radial
NEC fails exactly where R is convex along affine radial null rays (INVENTORY
DERIVATION). Consequence: lapse, shift and radial stretch reach the radial
null energy only through the null geodesics along which R is differentiated.

**I3. Radial discriminant = product of the two radial null energies.**
"With k±=n±e_ℓ, the orthonormal radial block has ρ+p_ℓ=½[T(k+,k+)+T(k−,k−)] and
j_ℓ=¼[T(k−,k−)−T(k+,k+)], so Δ_rad=(ρ+p_ℓ)²−4j_ℓ²=T(k+,k+)T(k−,k−). The
demanded tensor is therefore Type IV exactly where the outgoing and ingoing
radial null energies have opposite signs … A static geometry has equal values
and a zero current; time dependence acting on a varying radius separates them."
(`CONSTANT_RADIUS_TRACK.md:37-49`). DERIVED-IN-REPO. The same discriminant
D=(ρ+p_l)²−4j_l² with "D < 0: flux-dominant Type-IV block" is the May-era
criterion (`STAGE2_BETA075_ENDPOINT_SOURCE_CLASS_SCREEN.md:49-57`). Under a
radial boost T(k±) rescale by e^{±2η}, so the verdict is frame-invariant.
Rest-frame quantities of a Type I block:
"ρ_rest=(ρ−p_l+sgn(ρ+p_l)√((ρ+p_l)²−4j_l²))/2" (`LE_BOUNDARY_GATE_PREFLIGHT.md:70-72`),
"v=2j_l/(ρ+p_l+sgn(ρ+p_l)√((ρ+p_l)²−4j_l²))" (`LE_CLASSIFIER_REPAIR.md:19-21`).
Combining I2 and I3: **Type IV demand requires time dependence acting on a
region where R varies** (both radial null Hessians must differ in sign).

**I4. Constant areal radius gives an exact, boost-invariant string cloud.**
"Where R is constant its Hessian vanishes, so the radial block is exactly
ρ=−p_ℓ=1/(8πR²), j_ℓ=0 … p_Ω=(1/8π)(□R/R−K)=−K/8π" and "A string's worldsheet
stress is invariant under boosts along the string"
(`CONSTANT_RADIUS_TRACK.md:77-94`). Angular null energy on such a track:
"ρ+p_Ω=(1/8π)(1/R_b²−K)" (`CONSTANT_RADIUS_TRACK.md:288-290`). DERIVED-IN-REPO
from I1; unit-tested (`tests/test_warped_product.py:55-66`). Consequence: holding R constant moves every
two-dimensional (α, β, A) dynamic into the angular pressure, whose NEC fails
where K > 1/R².

**I5. Radial null speeds and cone tilt.** "`dl/dsigma = -beta +/- alpha/sqrt(gamma_ll)`"
(`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:17`;
`STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md:81-82`), with the
stationary-vector test "g_sigma_sigma = -alpha^2 + gamma_ll beta^2"
(`STAGE2_GZ_OBSTRUCTION_SCREEN.md:22-25`). INVENTORY DERIVATION:
v₊v₋ = g_σσ/A and v₊+v₋ = −2β, so g_σσ ≥ 0 ⇔ |β| ≥ α/√A ⇔ both radial null
branches move in the same coordinate direction. This marks an ergo-like
region (no observer can hold fixed l); it is a horizon only if the v=0
surface bounds a region null rays cannot leave, which the escape audits
refuted for this design (`STAGE2_HORIZON_ESCAPE_REFINED_BETA075_CORE.md:151-167`).

**I6. Packet (occupant) norm and clock.** For a radial worldline dl/dσ = v:
`packet_norm = -alpha*alpha + gamma_ll*(vcoord + beta)**2`
(`toolkit/adm_harness_cli/adm_harness/source_ledger.py:1550`). Timelike ⇔
v₋ < v < v₊ (I5); the proper-time rate is dτ/dσ = √(−norm). A comoving shift
v+β=0 gives norm = −α² and dτ/dσ = α (INVENTORY DERIVATION). Only the sign is
frame-free; the magnitude scales with α², so the reported "max live packet
norm" values are not comparable margins across designs with different lapse.

**I7. Shift re-match algebra.** The collar edit δβ = −g·W·(v+β)
(`source_ledger.py:1522-1526`; `STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md:29`)
gives v+β_new = (1−gW)(v+β_pre): causal margin improves for 0 < gW < 2 and is
maximal at gW = 1 (INVENTORY DERIVATION). The margin is bought pointwise and
algebraically; its price appears only through derivatives of β in G.

**I8. Coordinate-normalized null energy carries α².** With k^σ = 1,
"Tkk_plus / alpha^2 = rho_H + p_l - 2 j_l; Tkk_minus / alpha^2 = rho_H + p_l + 2 j_l"
(`STAGE1_CHANNEL_CAUSE_LEDGER_FINDINGS.md:36-41`). "The coordinate `Tkk` peak
is large because the local metric scale is large, not because the local ADM
pieces are huge" (`STAGE1_CURRENT_CANDIDATE_ALGEBRA_LEDGER.md:203`). The
throat-era `neg_Tkk_radial` burden is this coordinate quantity integrated with
weight √A·B (`source_ledger.py:1888, 2436`). Any lapse knob rescales it by α²
at fixed orthonormal stress; the reports never separate that share.

**I9. Uniform slowdown (rate κ) cannot cure Type IV at an enthalpy zero.**
With σ=κt, α and γ fixed at matched phase and β→κβ,
"j_κ=κj_1 … X_κ=X_0+κ²(X_1−X_0), X∈{ρ,p_ℓ,p_Ω}" and at a spatial zero of the
static enthalpy h_0, "Δ_κ=(ρ_κ+p_{ℓ,κ})²−4j_κ²=κ²(κ²h_2²−4j_1²)", threshold
"κ_c=2|j_1|/|h_2|. Thus the static limit can be Type I while every nearby
evolving member still contains Type IV stress" (`LE_BOUNDED_METRIC_REPAIR.md:101-136`).
DERIVED-IN-REPO; exact for the uniform-rate family of any metric of the class.
Measured: |Δ| ∝ κ², |Im λ| ∝ κ, layer width ∝ κ (`LE_BOUNDED_METRIC_REPAIR.md:173-192`).

**I10. Null expansions of the symmetry spheres (proxy form).**
"R = sqrt(gamma_omega); v_+/- = -beta +/- alpha / sqrt(gamma_ll);
theta_+/- = 2 (d_s R + v_+/- d_l R) / R" (`STAGE2_NULL_EXPANSION_PROXY.md:26-30`),
along the coordinate null directions K± = α(n ± e_l); only the sign is
invariant, and the report calls it "not a theorem-level trapped-surface
calculation" (`STAGE2_NULL_EXPANSION_PROXY.md:12-14`). INVENTORY DERIVATION:
θ₊θ₋ = −(4α²/R²)(∇R)², so both expansions share a sign only where ∇R is
timelike; with ∂_σR = 0 that requires |β|√A > α on a flank with ∂_lR ≠ 0.
Constant R gives θ± ≡ 0 (`CONSTANT_RADIUS_TRACK.md:253-255`).

**I11. Radial bundle focusing ignores the areal radius.** INVENTORY
DERIVATION from I5: d(δl)/dσ = (∂_l v±)δl = (−∂_lβ ± ∂_l(α/√A))δl, independent
of B. Measured agreement: areal smoothing changed bundle width by 0.989×, β
smoothing by 1.65–1.94×, γ_ll smoothing made it worse (0.354×)
(`STAGE2_COLLAR_MITIGATION_SCREEN.md:93-99, 135-137`).

**I12. Areal flux of a radial string cloud.** For T_ab = −μ g_ab on the
quotient with p_Ω = 0, ∇·T = 0 ⇔ ∂_a(μR²) = 0 (INVENTORY DERIVATION; static
form asserted: "If separately conserved and static, this ideal pattern
requires I∝R^{-2}. A varying flux or termination requires angular stress or
exchange", `COUPLED_SOURCE_ROLE_AUDIT.md:70-74`). From I1 the geometry's own
flux is 8πR²(ρ−p_l)/2 = 1 − (∇R)² − R□R, i.e. ≈1/(8π)=0.039789 where R is
nearly constant. The Stage II fitted flux Φ = 0.039772
(`STAGE2_RADIAL_STRING_CLOUD_ENDPOINT_CROSSWALK.md:72`) is this geometric
W-term, not an independent matter finding; `CONSTANT_RADIUS_TRACK.md:346-348`
later makes it exact.

**I13. Join regularity sets stress growth.** A metric function with a d^p
cusp has second derivatives ∝ d^{p−2}: "The metric is continuous with a
square-root cusp there. Its second radial derivative grows as d^{−3/2}"
(`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:167-169`), measured as ×2^{3/2} per
halving (`:179-180`) with an unbounded absolute stress integral (`:194-199`).
A first-derivative jump gives a sampled h⁻¹ surface term (`:185-188`); "C2
matching permits first-order curvature convergence at the exact joins"
(`LE_RECEIVER_C2_REPAIR_ATTEMPT.md:80-81`); C∞ primitives converge at the
scheme order (`CONSTANT_RADIUS_TRACK.md:193-196`). Exception measured: a
temporal slope jump in a shell cap gave finite sampled G
(`LE_BOUNDED_METRIC_REPAIR.md:52-55`). C1-only joins were never tested.

**I14. Lapse-only dynamics carry no energy flux.** "the momentum constraint
makes the Eulerian energy flux vanish wherever the spatial metric is static
and the shift is zero, whatever the lapse does" (`AXIAL_TRACK.md:228-230`,
post-era; general ADM). Measured corollary in this era: static support with
moving packet windows and zero shift contributed 236 Type IV points against
842 for the full geometry (`CONSTANT_RADIUS_TRACK.md:59-65`).

**I15. Divergence does not fix type.** "∇_μT^{μν}=J^ν … allows addition of any
divergence-free tensor, so it leaves the support tensor's algebraic type
underdetermined" (`LE_BOUNDARY_GATE_PREFLIGHT.md:137-145`).

### 5.2 Static identities (β=0, time-independent; proper-distance gauge, lapse A)

**I16. Static source decomposition.** For ds² = −A²dt² + dl² + R²dΩ²:
"X=A''/A, Y=A'R'/(AR), Z=R''/R, W=(1−R'²)/R²" and
"8π(ρ,p_r,p_t)=W(1,−1,0)+Z(−2,0,1)+Y(0,2,1)+X(0,0,1)"
(`COUPLED_SOURCE_ROLE_AUDIT.md:79-98`); "the displayed pieces acquire physical
component meanings only through a source model and its exchange equations"
(`:99-102`). Checked against flat space, cylinder, Ellis and de Sitter static
patch (`toolkit/adm_harness_cli/scripts/audit_coupled_source_roles.py:33-56`).
Roles: W = finite-radius tension, null-neutral; Z = opening, the only term
in 8π(ρ+p_r) = −2Z + 2Y besides clock–radius overlap; X = clock curvature,
angular only; Y = clock–radius overlap, radial pressure and angular.

**I17. Tension and opening are separate duties at a throat.** "At a smooth
minimum of radius, R'=0, the radial pressure is −1/(8πR_0²) … A strict minimum
also has R''>0, giving ρ+p_r=−R''/(4πR_0)<0. Tension and opening are therefore
different requirements even at the same location"
(`COUPLED_SOURCE_ROLE_AUDIT.md:104-110`). General static radial null energy
from I16: 8π(ρ+p_r) = −2(R'' − A'R'/A)/R (INVENTORY DERIVATION). Unit lapse:
"both radial null energies equal −R''/(4πR)" (`CONSTANT_RADIUS_TRACK.md:94-95`).

**I18. Flare-out (opening) identity and bound.** "(R'/A)'=−(4πR/A)(ρ+p_ℓ), so
widening a uniform track from R'=0 to R'/A=1 requires an integrated radial
null deficit of at least one per end, a uniform continuation requires none,
and a closing cap decreases R'/A with non-negative ρ+p_ℓ"
(`CONSTANT_RADIUS_TRACK.md:327-334`; also `COUPLED_SOURCE_ROLE_AUDIT.md:170-172`).
Measured opening 2.000001 on a two-ended slice (`CONSTANT_RADIUS_TRACK.md:325-326`).
Transition width sets only the peak: −0.118, −0.058, −0.028 at widths 0.75,
1.5, 3 (`CONSTANT_RADIUS_TRACK.md:183-185`), i.e. peak ∝ 1/width.

**I19. Clock identity.** "(R²A')'=4πR²A(ρ+p_r+2p_t). A strict interior lapse
maximum needs a negative value of this source there. Positive potential energy
can provide that sign while saturating both null conditions"
(`COUPLED_SOURCE_ROLE_AUDIT.md:113-119`). A clock maximum costs a strong-energy
(ρ+p_r+2p_t) violation, not a null-energy violation.

**I20. Static conservation.** "p_r'+(A'/A)(ρ+p_r)+2(R'/R)(p_r−p_t)=0"
(`COUPLED_SOURCE_ROLE_AUDIT.md:129-131`): ending a radial load couples angular
stress, clock gradient and radial enthalpy at every interface (`:133-136`).

**I21. Ellis throat, closed form (ultrastatic, α=A=1, β=0, c_Ω=1).**
"ds²=−dσ²+dl²+(l²+a²)dΩ² … ρ=p_l=−a²/(8π(l²+a²)²), j_l=0, p_Ω=a²/(8π(l²+a²)²)"
(`LE_BOUNDARY_GATE_PREFLIGHT.md:159-171`; matches samples within 8.02e-11,
`:173`). Type I, negative energy, |l|⁻⁴ tail whose two-ended norm integral
beyond L is "2a arctan(a/L) ∼ 2a²/L" (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:235-253`).
With a constant angular jacket c_Ω ≠ 1 the far tail approaches a string cloud
ρ ≈ −p_l ≈ (1−c_Ω²)/(8πR²) (INVENTORY DERIVATION).

**I22. Static geometries are Type I in the radial block.** From I3 (j=0 in the
static frame). Measured: all 4,504 matched static-control samples Type I while
every active phase contains Type IV (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:133-144`).
Consequence: a static surrogate cannot detect the Type IV layer.

**I23. Canonical fields supply no null deficit.** Static canonical condensate:
"(ρ,p_r,p_t)=(K+D+V+E, K+D−V−E, K−D−V+E) … radial and angular null stresses are
2(K+D) and 2(K+E)" (`COUPLED_SOURCE_ROLE_AUDIT.md:193-197`). A minimally
coupled scalar's radial block "is boost-diagonalizable and the signs of
rho+p_l and p_l-pOmega are tied to the scalar kinetic sign"
(`STAGE2_BETA075_MATTER_ACTION_FEASIBILITY_WORKLOG.md:79-81`), so it is never
Type IV. Components with non-negative null stress cannot reduce the negative
null requirement (`COUPLED_SOURCE_ROLE_AUDIT.md:15-17`).

### 5.3 Algebraic-type and source-model relations

**I24. The minimal Type I regulator changes the source.** "minimal regulator =
max(0, 2 |j_l| - |rho + p_l|)", split "delta rho = 0.5 sign(rho+p_l) regulator;
delta p_l = 0.5 sign(rho+p_l) regulator" (`STAGE2_BETA075_ENDPOINT_CURRENT_REGULATOR_SCREEN.md:56-66`).
Adding it gives |ρ+p_l| = 2|j_l|, i.e. D=0 exactly ("exactly luminal at safety
factor 1.00", `STAGE2_BETA075_REGULATED_MEDIUM_ADMISSIBILITY_AUDIT.md:100-101`).
The regulated tensor is a different T from the Einstein demand.

**I25. Heat-mode speed equals the Type I margin.** "v_q = 2 j_l / |rho + p_l| =
tanh(psi); h_reg = 1 - v_q^2 >= 0" (`STAGE2_BETA075_SOURCE_FAMILY_EQUATION_PACKAGE.md:69-70`).
D = (ρ+p_l)²(1−v_q²) (INVENTORY DERIVATION): a medium realizing a near-Type-II
radial block has a near-luminal heat characteristic. Measured coincidence:
minimum cone margin 7.881e-5 and transport margin 7.983e-5 on the same row
(`STAGE2_BETA075_REDUCED_PRINCIPAL_SYMBOL_HYPERBOLICITY.md:43`;
`STAGE2_BETA075_RAPIDITY_BUDGET_DIAGNOSTIC.md:28`).

**I26. Boosted infrastructure preserves the discriminant.**
"j_b=J c²h_b²/(J²+c²h_b²), c=2v_max/(1−v_max²)", D=h_b sinh²ψ; this "preserves
the infrastructure's radial discriminant" (`LE_RESET_INVERSE_SEARCH.md:115-125`).

**I27. Areal-gauge mass relations** (metric −α²dt²+dr²/f+r²dΩ², f=1−2m/r):
"m_b=(r/2)[1−(∂_ℓ r)²/γ_ℓℓ]", "∂_r log α=(m+4πr³P_r)/(r(r−2m))",
"∂_t m=−4πr²α√f J" (`LE_COUPLED_RESET_SOURCE_ATTEMPT.md:103-117`). Consequence
measured there: adding positive-enthalpy material to remove Type IV consumes
the f>0 mass allowance (required δm ≈ 1.433 against 0.533 available,
`LE_COUPLED_RESET_SOURCE_ATTEMPT.md:197-205`).

**I28. Onset obstruction (registered families).** A prescribed geometric
acceleration with J=j_*u^{n−1} demands angular stress at order u^{n−2} while
initially empty moving material supplies it at u^{2n−2}
(`LE_RESET_INVERSE_SEARCH.md:389-421`); scoped "for these source families and
boundary conditions" (`:419-421`).

### 5.4 Source-physics identities (independent of the throat)

**Q1. Radial 1+1 conformal channels (spherically averaged).**
"ρ_Q = ηc/(4πR²)[−π/(24L²A²) + (2a''+a'²)/(24π)], p_r,Q = ηc/(4πR²)[−π/(24L²A²) − a'²/(24π)],
p_t,Q = 0" with L=∫dl/A, a=log A (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:80-85`).

**Q2. Anomaly lock.** "ρ_Q−p_{r,Q}=ηc/(48π²R²)(a''+a'²). Consequently
shortening a cavity increases its negative radial-null stress while preserving
this independent tensor constraint" (`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:128-134`).

**Q3. Reflector reaction and subdivision scaling.** F = −4πR²[p_r]
(`C1_SIGNED_SOURCE_CHANNEL_SCREEN.md:103-113`); outer end loads ∝ (compartment
count)², internal forces balance (`:115-117`); "fourfold shortening multiplies
the local Casimir part by 16", Σc_jL_j invariant under repartitioning
(`C1_POPULATION_BOUNDARY_AND_REFINEMENT.md:162-166`).

**Q4. Longitudinal supply bound.** With W=exp[−(R²−R₀²)/2k], the 1+1 source
must satisfy C∫W/A² dl − (∫WRR''/k dl + [Wa']) = (4π/k)∫WR²H_rem dl ≥ 0
(`COUPLED_REORIENTATION_INVESTIGATION.md:209-218`); "A global rescaling of time
leaves the source and the bound unchanged" (`:260-262`); AdS₂ positive control
gives exactly 4 (`:304-307`).

**Q5. Conformal scalar on a cylinder and the curvature-coupling logarithm.**
"(ρ,p_r,p_t) = ηN/(2880π²R⁴)(−2log(R/a₀), 2log(R/a₀), 1−2log(R/a₀))"
(`C1_ANGULAR_SCALAR_INVESTIGATION.md:58-61`), angular-null negative for
log(R/a₀) > 1/4 (`:68-69`); T(ℓ₀) = T(1) − 2(ℓ₀−1)H
(`C1_ANGULAR_ABSOLUTE_SOURCE_AND_PAIR_BUDGET.md:125`); a subtraction-convention
change "supplies no additional stress" (`:143-150`).

**Q6. Boundary-state response and holding cost.** Dirichlet end:
(Δρ,Δp_r,Δp_t) = Δb(1/6,1/2,−1/6); held product-cylinder interaction
d|F|/|E| = 1 + zK₀(z)/K₁(z) > 1, so E_int + d|F_int| > 0 for a DEC-obeying
direct static support (`C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md:199-201, 253-268`).

**Q7. Planar EM Casimir cells.** C = ηπ²/(720d⁴); independently held cells need
holder energy ≥ 3(C_r+2C_t), complete cells ≥ 2(C_r+2C_t)
(`COUPLED_REORIENTATION_INVESTIGATION.md:129-145`).

**Q8. Shared-field pair cross term.** u_E = (Q_L²+Q_R²)/2R⁴ + Q_LQ_R/R⁴
(`C1_FINITE_MODULE_PAIR_SCREEN.md:56-57`).

**Q9. Scalar-mirror proximity co-scaling.** h_I and h_χ both ∝ η/a³ at fixed
optical strength and relative thickness (`NARROW_CURVED_CAVITY_EVALUATION.md:82-87`).

**Q10. Capacitor shells.** σ = (√f_in − √f_out)/(4πr); U_E/(M_in+M_out) ≤
2(b−a)/(b+a) (`CHARGED_CAPACITOR_CONSTRUCTION.md:56-59, 116-121`).

**Q11. Magnetic confinement.** B²/8π > P_γ + P_e±
(`STORAGE_CONTAINMENT_LITERATURE_REVIEW.md:57-59`); sleeve virial
E_sleeve ≥ 2E/(3k(1+πa/L)) (`MAGNETIC_GEOMETRY_COMPARISON.md:182-183`).

**Q12. Oriented ensembles.** T^Maxwell = u(δ−2bb), T^sheet = −u(δ−aa),
T^string = −uss; H ≤ 2kE_material (`CONTAINMENT_ENSEMBLE_ROLE_AUDIT.md:63-66, 160-164`).

**Q13. Scale invariance of module power.** C_J/δ_s ∝ c⁵/G independent of L_g;
C_Jδ_s/ħ ∝ (L_g/ℓ_P)² (`RAIL_STORAGE_AND_INTERFACE_STATUS.md:111-133`).

## 6. Coupling matrix: knob × physics channel

Channels: **DM** demand magnitude (integrated burdens and peaks); **DL**
demand location (live vs infrastructure, stage, region); **AT** algebraic
(Hawking–Ellis) type; **PN** packet/occupant norm and clock; **CS** causal
and service-time behaviour (null speeds, cone tilt, escape, V headroom,
service ratios); **SR** source burden by role (p_l vs T_kk vs p_Ω vs j_l
separation, role decomposition, supply ratios); **EC** energy-condition class
(radial/angular NEC, packet-frame WEC, SEC, DEC).

Cell codes:

- **I** — response fixed by an identity for the class (section 5)
- **I/M** — the identity fixes the direction or scaling; the magnitude is measured on this design
- **M** — measured on this design only
- **0** — tested, and the channel does not respond (a measured decoupling)
- **0I** — the channel cannot respond, by identity
- **U** — untested
- **–** — no pathway (for example, an accounting-only knob)

Markers: **†** the cell's evidence rests on the beta075 geometry that failed
the Type IV gate. **§** it rests on the static zero-shift slice of repaired
beta075. Every PN cell carries the packet-reading mismatch [L2]. Every CS cell
that involves service time carries [L3].

### 6.1 Geometry knobs

| Knob | DM | DL | AT | PN | CS | SR | EC |
|---|---|---|---|---|---|---|---|
| G1 throat radius R_th | I/M (1/R² tension) | M | U | M | M§ (optical length, lapse) | M; M§ (supply −8.45%) | I/M |
| G2 support-edge width w_th | M | M | M† (widening worsens Type IV) | M (cliff) | M (V headroom 12 → 10) | M (moves p_l and T_kk) | M |
| G3 lapse cushion η_N | M (T_kk only) | M | U | I/M | 0 (V headroom) | 0 (p_l) | M |
| G4 jacket width w_Ω | M | M | U | 0 | U | M; M§ | M |
| G5 decompression / slowdown κ | I/M† | M† | I/M† | U | M (service length) | 0† (lags vs J) | I/M (angular NEC, post-era) |
| G6 service factor V | M (T_kk up) | M | U | M (cliff) | M | I/M (j_l affine in β); 0 (p_l) | M |
| G7 catch shaping vs split | M | M (stage shift) | U | I/M | U | 0 (p_l) | M |
| G8 packet carve | M | M | U | M | M (V10 failures) | M (p_l fraction set by footprint) | M |
| G9 lapse compensator | M | M | U | I/M | M | 0 (p_l fraction) | M (α² normalization, I8) |
| G10 shoulder: two-zone / annular | M | M | U | M | M | M | M |
| G11 split carve, null cushion, composition, edge sleeve | M | M | U | M | U | M | M |
| G12 pressure rebate | M | M | U | 0 | U | M | M |
| G13 radial stretch core/ring/skirt | M | M | U | 0 (ring) | U | M; M§ (±0.3%) | M |
| G14 local areal partner | I/M | M | U | M | U | M | I/M |
| G15 time-edge profile / schedule | M | M | U | M | U | M | M |
| G16 compact handoff width | M | M | U | M | U | M | M |
| G17 entry gate | – | M (relabel) | – | M (relabel) | – | – | – |
| G18 shell amplitude / sign | M | M | U | M (drift linear) | U | I/M (sign symmetry) | M (ρ_packet sign asymmetry) |
| G19 shell timing | M | M | U | M | U | M | M |
| G20 shell partners (clock, rail, κ_Q) | M | M | U | 0 (κ_Q) | U | M | M |
| G21 shell profile / width / strength | M | M | U | M | U | M | M |
| G22 endpoint smearing | 0 | M | U | M (temporal defect) | U | 0 (J) | M (SNEC clean) |
| G23 release-fade width | M† | M† | I/M† (branch-sign reading) | 0† (live-clean) | M† (reachability) | M† | I/M† |
| G24 receiver channel | M† | M† | U | 0† | U | M† | I/M† (only B moves radial null) |
| G25 receiver side / gain / window | M† (additive, I) | M† | M† (Type IV persists) | 0† | U | M† | M† |
| G26 re-match collar | M (†) | M (†) | M† (1,862 points on its transition) | I/M (†) | I/M† (focusing ∝ ∂_lβ) | M (†) | M† (packet-frame WEC) |
| G27 causal-margin guard | U | U | U | 0† | I/M† | U | U |
| G28 join regularity | I/M† (d^{p−2}) | M† | 0† | U | U | U | M† |
| G29 coupled reset source | M† | M† | M† | U | U | I/M† (mass law) | M† (DEC per component) |
| G30 reset inverse search | M† | M† | I/M† (boost keeps Δ) | U | M† (infrastructure speed) | M† | M† |
| G31 constant R (post-era) | I/M | I/M | I/M (Type IV → 0) | 0I | 0I (null speeds); I/M (θ± → 0) | I (string cloud) | I/M (angular NEC K > 1/R²) |

### 6.2 Source-model and demand-reading knobs

| Knob | DM | DL | AT | PN | CS | SR | EC |
|---|---|---|---|---|---|---|---|
| M1 regulator safety factor | M† | M† | I/M† (D = 0 at SF 1) | U | I/M† (heat mode luminal) | M† | M† |
| M2 source class | U | M† | I/M† (scalar never Type IV) | U | U | M† | M† |
| M3 reservoir ansatz / basis | U | M† | U | U | U | M† | U |
| M4 source-time class | M† | M† | U | U | I/M† (convex-kernel bound) | M† | U |
| M5 rapidity variable / amplitude | U | M† | I/M† (I25) | U | M† | M† | U |
| M7 mesh resolution | M† (totals converge) | M† | U | M† (minima degrade) | M† (cone margin) | M† | U |
| D1 role partition | – (accounting) | M | M (fitted H is Type IV) | – | – | M | M |
| D2 SNEC τ / coverage / λ | – | M (†) | – | – | – | – | M (†) |
| D3 nonminimal scalar screen | M | M (misplaced) | U | U | U | M | I/M |

### 6.3 Source-architecture knobs

| Knob | DM | DL | AT | PN | CS | SR | EC |
|---|---|---|---|---|---|---|---|
| S1 mechanical connectivity (C1 vs connected) | M§ | U | U | U | U | I/M§ (charge ×2) | M§ |
| S2 C1 overlap width / offset | M§ | M§ | U | U | M§ (light-crossing) | I/M§ (cross term) | M§ |
| S3 backbone share / carrier (95%) | M§ | U | U | U | U | I/M§ | I (null-neutral radial, +angular null) |
| S4 cavity length / subdivision | I/M§ (1/L², N² loads) | M§ | U | U | U | I/M§ | I/M§ (anomaly lock) |
| S5 population grouping | M§ | M§ | U | U | U | M§ | M§ |
| S6 local subdivision at a boundary | I/M§ (×16) | M§ | U | U | U | I/M§ | M§ |
| S7 angular division coordinate | M§ | M§ | U | U | U | M§ | M§ |
| S8 reflector pattern / transparency | I/M§ | M§ | U | U | U | I/M§ (holding bound) | I/M§ |
| S9 curvature-coupling logarithm ℓ₀ | I/M§ | M§ | U | U | U | M§ | I/M§ |
| S10 longitudinal strength / interval / clock band | I/M§ | M§ | U | U | 0I (time rescaling) | I/M§ | I/M§ |
| S11 cavity gap / mirror | I/M (η/a³); M§ | U | U | U | U | I/M | M§ |
| S12 short magnetic circuits | M§ | U | U | U | U | M§ | M§ |
| S13 planar EM Casimir cells | I (d⁻⁴) | U | U | U | U | I (holder ≥ 3×) | I/M§ |
| S14 magnetic loop / sleeve strength k | I/M† (virial) | U | U | U | U | I/M† | I/M† (material k) |
| S15 magnetic jacket geometry | I/M† | U | U | U | U | M† | U |
| S16 containment ensemble orientation | U | U | U | U | U | I/M† | M† (DEC reserves) |
| S17 storage medium (capacitor vs pressure-linked vs elastic vs EM) | M† | M† | U | U | M† (discharge rate) | M† | M† (null burden) |
| S18 physical scale L | I | – | – | – | – | I | U |

### 6.4 What the matrix shows

- **Algebraic type is the emptiest column.** Only G2, G5, G23, G25, G26 and
  G28–G31 carry any AT entry, all from the September repaired classifier or
  its May precursor, and all on the † geometry except G31. The two identities
  that decide it (I2, I3) show that any knob adding time dependence where R
  varies is a Type IV candidate (G5, G14, G20-κ_Q, G24/G25). None of those
  predictions was tested knob by knob.
- **The PN column is never an occupant-safety result.** Every entry carries
  [L2]. No knob reports aging, tides or acceleration.
- **Identity-backed decouplings.** These are the most transferable facts:
  - p_l at a minimal sphere depends on R alone (G1, G3, G6, G7);
  - packet kinematics ignore B (G31, I4/I6);
  - radial focusing ignores B (G26, I11);
  - disjoint edits superpose (G25);
  - a boost preserves the discriminant (G30);
  - time rescaling leaves the longitudinal quantum balance invariant (S10).
- **Measured-only decouplings.** These are design facts:
  - the live p_l fraction is set by the carve footprint (G8, G9);
  - the ring leaves peaks and packet norm unchanged (G13);
  - endpoint J is invariant to window thickness (G22);
  - release lapse and carve lags do not move J (G5/G23);
  - the non-live core null peak is V-independent (G6).

## 7. Invalidation register

### 7.1 Results resting on the beta075 geometry (failed the Type IV gate) — marked †

The frozen case is `V5_smooth_split_horizon_escape_beta075_p003_mid_rematch_w6_t1p5`.
It has `w_th = 0.569`, receiver angular gain 0.03, a negative-side receiver
and outer power 0.5 (`LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md:21-25`). Its demand
carries a refinement-stable Type IV layer, and its receiver inner edge has
singular curvature (`:5-11`).

| Result family | Reports | Status |
|---|---|---|
| Release width 0.75/1.00 endpoint ladders; receiver channel, side, dose and localization screens; receiver promotion (G23–G25) | `STAGE2_ENDPOINT_BETA_SUPPORT_CODESIGN`, `STAGE2_BETA_MEMORY_RECEIVER_*`, `STAGE2_NEGATIVE_L_RECEIVER_*` | Demand-geometric numbers stand as measurements on a geometry whose demand has no rest-frame source. `p003_mid` introduced the √ cusp. The "transfer-clean" promotions rest on a one-sided metric (§3.D). |
| Collar generator, local bracket, repaired-lead promotion (G26) | `STAGE2_BETA_COLLAR_GENERATOR_SCREEN`, `STAGE2_BETA075_COLLAR_LOCAL_BRACKET_CHECKPOINT`, `STAGE2_BETA075_REPAIRED_LEAD_PROMOTION_AUDIT` | The optical and causal readouts stand as measurements. 1,862 Type IV points sit on the rematch transition. |
| Horizon/escape, reachability, causal guard, GZ screen, null-expansion proxy, trace expansion, dense caustic audit (G27) | `STAGE2_HORIZON_*`, `STAGE2_GZ_OBSTRUCTION_SCREEN`, `STAGE2_NULL_EXPANSION_PROXY`, `STAGE2_TRACE_EXPANSION_AUDIT`, `STAGE2_DENSE_CONGRUENCE_CAUSTIC_AUDIT` | The causal geometry stands; escape means reaching either end [L4]. "There is no evidence here of a new curvature blow-up caused by the receiver" (`STAGE2_GZ_OBSTRUCTION_SCREEN.md:105`) is **contradicted** by the September refinement. |
| Affine SNEC and finite-domain ANEC on beta075 (D2) | `STAGE2_AFFINE_REPARAM_SNEC_AUDIT`, `STAGE2_BETA075_FINITE_DOMAIN_RADIAL_ANEC_DIAGNOSTIC` | Demand screens; the floor normalization is unverified. |
| All `STAGE2_BETA075_*` source-model work: regulator, source class, reservoir, closure, energy certificates, rapidity/transport, timing, reshaping, 3+1 proxies (M1–M8) | 46 files, May 21–24 | **Invalidated as source realizations.** The regulator changes T to make it Type I. On Type IV rows no rest-frame medium supplies the demand (`THROAT_GEOMETRY_CLARIFICATION.md:157-158`). The fit is 46–48% off its target (`LE_BOUNDARY_GATE_PREFLIGHT.md:115-119`), and stored rest energies were wrong on most rows [L5]. Structural mathematics survives: I24, I25, the convex-kernel bound, positive upwind transport. |
| Service rating ladder V2/V2.5/V5/V10 (G6) | `STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC`, `STAGE2_BETA075_V2_LOWER_SERVICE_SOURCE_COUPLING` | The packet norm is (Geo) [L2]. The closure results are (Adm), and their non-monotone pattern is unexplained. |
| LE repairs: join regularity, slowdown, coupled reset source, reset inverse search (G5, G28–G30) | `LE_*` | These are valid diagnostics of the failed geometry, and they established that it cannot be patched: "The present work therefore stops further parameter patching" (`LE_BOUNDED_METRIC_REPAIR.md:247`). |
| Storage, capacitor and magnetic-containment thresholds (S14–S17) | `PRESSURE_LINKED_STORAGE_COMPLETION`, `ELASTIC_/ELECTROMAGNETIC_ENDPOINT_STORAGE_*`, `CHARGED_CAPACITOR_CONSTRUCTION`, `MAGNETIC_*`, `CONTAINMENT_ENSEMBLE_ROLE_AUDIT`, `RAIL_STORAGE_AND_INTERFACE_STATUS` | The thresholds come from active beta075 V5 histories whose demand includes the Type IV layer. The constitutive laws and bounds are GEN-S and survive. |
| C1 screens, cavities, longitudinal gate, archived transfers (S1–S13, G1/G4/G13 transfers) — **§** | `C1_*`, `NARROW_CURVED_CAVITY_EVALUATION`, `CAVITY_AND_MAGNETIC_SOURCE_COMPARISON`, `COUPLED_REORIENTATION_INVESTIGATION`, `ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT` | These run on a static slice of repaired beta075. By I22 they are blind to Type IV and to currents, and they are tied to the Ellis throat [L4, L7]. The source laws survive. |

### 7.2 Other later findings and what they overturn

| Finding | Overturned or scoped |
|---|---|
| **L2** packet-reading mismatch | Every packet-safety verdict in the era. Specific cases: the w_th 0.569/0.570 cliff and the V ≈ 10.01 cliff. INVENTORY INFERENCE: each is a single mask-edge node on the first sampled row, so the cliff values are sampling-dependent (G2). "Live-clean" claims and the collar's margin gains (G26) are also affected. |
| **L3** service ratios on l = σ | 2.569/1.233 and the plateau extrapolations (`STAGE2_SERVICE_TIME_ADVANTAGE_LEDGER.md:68-93`). "They are proxies, and the geometry defines no arrival lead" (`THROAT_GEOMETRY_CLARIFICATION.md:175`). |
| **L4** two-ended topology | The "relax throat" reading of the reset (the minimal sphere persists). End-transition opening deficits are a consequence of two ends. The 28.77% outer band of the static null balance (`COUPLED_SOURCE_ROLE_AUDIT.md:160-165`) partly prices the two-ended flare (INVENTORY INFERENCE). |
| **L5** classifier repair | Legacy Type II labels and rest-frame energy-condition columns of the May endpoint work. The branch-sign reading of the endpoint shares (G23) depends only on the signs of ρ+p_l±2j_l and survives. |
| Grid/domain effects | Default 41×73 grids omit σ < −0.35, so the entry/pre-catch stage burdens are not comparable across reports. Peak values flip with resolution (`STAGE1_RELEASE_CHOREOGRAPHY_ARTIFACT_CHECK.md:113-120`; `STAGE1_MATURE_RELEASE_CHOREOGRAPHY_PROBE.md:113-116`). |
| Coordinate normalization (I8) | Every `neg_Tkk_radial` magnitude carries α². Lapse knobs (G3, G9, G11 null cushion, G15) change it at fixed orthonormal stress. The reports never separate this share, so "radial-null relief" from a lapse knob is partly normalization. |

### 7.3 What survives unchanged

- Every identity in section 5.
- The identity-backed decouplings listed in 6.4.
- The qualitative knob-separation pattern: radial pressure follows R and the
  support width; radial null follows catch timing and shift profile; causal
  margin follows lapse. For p_l this is backed by I17; the rest are
  measurements on this design class.
- The design rule G31 and its consequences.
- The source laws and scaling identities Q1–Q13.

## 8. Gaps

### 8.1 Channels never measured

- **Occupant physics.** No throat-era report computes passenger aging, tidal
  acceleration or occupant acceleration. The packet-norm sign is the only
  occupant readout, and [L2] applies to it.
- **Algebraic type.** Type was never tested for:
  - any Stage I knob (G7–G21);
  - R_th, V or w_Ω dynamically;
  - the shell partners.

  The Type IV attribution isolates decompression and moving windows only
  (G5).
- **Energy conditions beyond the radial NEC and the packet WEC.** SEC, DEC and
  the tangential NEC were never computed for geometry knobs. The static
  identity I19 (a clock maximum costs ρ+p_r+2p_t < 0) was never checked
  against any design.
- **Physical normalization.** Every burden is α²-weighted (I8) and
  coordinate-volume weighted. No lapse-normalized or proper-time-weighted
  burden was ever reported.
- **Arrival comparison.** The throat era has none; the first well-posed one is
  in the later one-space choreography pass [L3].

### 8.2 Knobs never varied

- **Plant constants.** C₀, λ, B₀, the shift exponent p_β, R_pass and the
  jacket amplitude a_Ω were never varied.
- **Shift amplitude.** It was never varied independently of V.
- **Join classes.** The receiver outer power was fixed at 0.5, and C1-only
  joins were never tested.
- **Radius sweep.** The R_th sweep is not a similarity transformation: w_th,
  w_Ω, R_pass and the time scales stay fixed. The 1/R² and R² scaling readings
  (G1) are therefore INVENTORY inferences, not controlled scaling results.
- **Throat-capacity partner.** No numbers are reported at nonzero ratios.
- **Clock-lapse partner.** Its isolated effect was never measured: there is
  no clock = 0 control at matched timing.
- **Shell half-width.** Widths narrower than the code minimum 0.48125 cannot
  be tested.
- **C1 handoff.** The handoff schedule was never computed. No
  quantum-inequality or ANEC bound was applied to the September sources.

### 8.3 Open questions the identities pose but the reports leave unanswered

- **Type IV necessity.** It is unknown whether every time-dependent stretch
  acting where R varies must produce Type IV. I2 and I3 give a necessary
  condition only. The 28 enthalpy zeros that make slowdown fail (I9) are not
  traced to specific profile features.
- **p_l invariance.** The live p_l fraction is invariant to V and to lapse
  (G8), and there is no derivation of why.
- **Receiver side asymmetry.** The mechanism behind the +l/−l asymmetry of
  the receiver (G25) is not derived.
- **Closure pattern.** The non-monotone V2/V2.5/V5/V10 closure pattern (G6)
  is unexplained.
- **SNEC floor normalization.** The harness floor is −1/(4τ²). A
  unit-normalized Freivogel–Krommydas form gives −B/τ², and the conversion is
  not derived (D2).
- **Unsampled catch interval.** The inventory's closed-form estimate predicts
  a V10 packet failure in the unsampled early-catch interval
  (σ ≈ −0.45 to −0.64). It remains unverified (G2).

### 8.4 Evidence hygiene issues the book should avoid inheriting

- **One-sided transfer metrics.** These disagree in sign with raw changes
  (§3.D).
- **Promotion on proxy metrics.** Promotions were made on proxies while the
  raw metric favoured the alternative (`mid` vs `outer`, G25).
- **Fits called passes.** Fits with normalized L1 > 1 were promoted on
  integrated ratios (endpoint-J structured source family; component L1 errors 1.14/1.06/1.18 for ρ, p_l, p_Ω,
  `STAGE2_BETA075_STRUCTURED_ENDPOINT_SOURCE_MODEL.md:97-100`).
- **Symmetry-guaranteed gates.** Examples are angular exchange = 0 and ADM
  re-projection at 10⁻¹⁷. These carry no evidential weight.
- **Relabelling counted as improvement.** The entry gate (G17) relabels
  points without changing the metric.

