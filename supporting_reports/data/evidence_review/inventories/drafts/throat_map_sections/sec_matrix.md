## 8. Coupling matrix: knob × physics channel

Channels: **DM** demand magnitude · **DL** demand location · **AT** algebraic
(Hawking–Ellis) type · **PN** packet/occupant norm and clock · **CS** causal and
service-time behaviour · **SR** source burden by role · **EC** energy-condition
class.

Cell codes: **I** response identity-backed for the class (section 7) · **M**
measured on this design · **I+M** identity-backed direction or law with a
measured magnitude · **–** untested. "Flags" lists the later findings (§0.5)
that scope the row. Every PN entry in the era inherits L2; every AT entry
before Sept 8 inherits L5.

### 8.1 Geometry knobs

| Knob | DM | DL | AT | PN | CS | SR | EC | Flags |
|---|---|---|---|---|---|---|---|---|
| G1 throat radius R_th | I+M | M | – | M | M | M | M | L1 L2 L4 L6 |
| G2 support-edge width w_th | M | M | M | M | M | M | M | L1 L2 |
| G3 lapse cushion η_N | M | M | – | I+M | M | M | M | L2 |
| G4 angular jacket width | M | M | – | M | – | M | – | L1 |
| G5 decompression schedule / slowdown κ | M | M | I+M | – | M | – | M | L1 L3 L4 |
| G6 service factor V | I+M | M | M | M | M | M | M | L1 L2 L3 |
| G7 catch shaping fork (+ w_pass, shock absorber) | M | M | – | I+M | – | M | M | L1 L2 |
| G8 packet carve | M | M | – | M | M | M | M | L1 L2 |
| G9 packet lapse compensator (gain, footprint) | M | M | – | I+M | M | M | M | L2 |
| G10 two-zone / annular shoulder | M | M | – | M | M | M | M | L2 |
| G11 split carve, null cushion, composition, edge sleeve | M | M | – | M | – | M | M | L1 L2 |
| G12 edge carve + pressure rebate | M | – | – | M | – | M | M | L2 |
| G13 local radial stretch (core, ring, skirt) | M | M | – | M | – | M | M | L2 L6 |
| G14 local areal partner | I+M | M | – | M | – | M | M | L1 L2 |
| G15 temporal edge profile / schedule | M | M | – | M | – | M | M | L2 |
| G16 compact handoff profile and width | M | M | – | M | – | M | M | L1 L2 |
| G17 entry gate (accounting) | – | M | – | M | – | – | – | L2 |
| G18 shell amplitude and sign | I+M | M | M | M | – | M | M | L1 L2 |
| G19 shell timing | M | M | – | M | – | M | M | L1 L2 |
| G20 shell partners (clock, rail, throat-capacity κ_Q/a_β) | M | M | – | M | – | M | M | L1 L2 |
| G21 shell shape, half-width, strength | M | M | – | M | – | M | M | L1 L2 |
| G22 endpoint smearing | M | M | – | M | – | M | M | L2 |
| G23 release-fade width, hold, lags | M | M | I+M | M | M | M | M | L1 L2 L5 |
| G24 receiver actuation channel | I+M | M | – | M | – | M | M | L1 L2 |
| G25 receiver side, dose, localization | I+M | M | I+M | M | – | M | M | L1 L2 |
| G26 β-rematch collar | M | M | M | I+M | I+M | M | M | L1 L2 |
| G27 causal-margin guard | – | M | – | M | I+M | – | – | L2 L4 |
| G28 join regularity repairs | I+M | M | M | – | – | – | – | L1 |
| G29 coupled reset source | M | M | I+M | – | – | I+M | M | L1 |
| G30 reset inverse search | M | M | I+M | – | M | M | M | L1 |
| G31 constant areal radius (post-era) | I+M | I+M | I+M | I+M | I+M | I | I+M | L3 L4 |

Notes on I entries:

- G1 DM: throat tension −1/(8πR₀²) (I17); live p_l peak ratio exactly (1.75/2)².
- G3, G7, G9, G26 PN: ∂(norm)/∂α = −2α and the timelike window v₋ < v < v₊ (I5, I6); rematch algebra (I7).
- G5 AT: I2+I3 (time dependence on varying R), I9 (slowdown).
- G6, G18 DM: j_l affine in β with 1/α, Δρ quadratic with 1/α² (PDF eqs. (9)–(14); INVENTORY DERIVATION).
- G14, G24 DM: I2 (only R edits move radial null energy directly); I16 (clock curvature feeds p_t).
- G23 AT: one-branch-negative share = Type IV (I3).
- G25: DM superposition of disjoint edits (locality); AT via I13 (cusp) and I3.
- G26, G27 CS: focusing law I11; ergo-like tilt I5.
- G28: I13. G29: I27 (mass) and the prescription's enthalpy identity. G30: I26.
- G31: I2–I4, I18; PN unchanged because packet kinematics depend only on (α, β, A).

### 8.2 Source-model knobs (fits to the fixed demand)

| Knob | DM | DL | AT | PN | CS | SR | EC | Flags |
|---|---|---|---|---|---|---|---|---|
| M1 regulator safety factor | – | M | I+M | – | M | M | M | L1 L5 |
| M2 source class | – | – | I+M | – | – | M | I+M | L1 L5 |
| M3 endpoint basis form | – | M | – | – | – | M | – | L1 |
| M4 reservoir exchange model | – | M | – | – | – | M | – | L1 |
| M5 source timing class | – | M | – | – | M | M | – | L1 |
| M6 heat-current perturbation / rapidity | – | M | I+M | – | M | M | – | L1 |
| M7 support-edge reshaping | – | M | – | – | M | M | – | L1 |
| M8 3+1 proxy scenario | – | M | – | – | M | M | – | L1 |
| M9 source-role partition / composite ansatz | M | M | I | – | – | M | M | L1 |
| M10 nonminimal scalar model | – | M | – | – | – | M | I+M | L1 |

### 8.3 Source-architecture knobs

| Knob | DM | DL | AT | PN | CS | SR | EC | Flags |
|---|---|---|---|---|---|---|---|---|
| S1 mechanical connectivity (C1 vs connected) | M | – | – | – | – | I+M | M | L6 L7 |
| S2 C1 overlap width and offset | M | M | – | – | M | I+M | M | L6 L7 |
| S3 tension-carrier share / type (95% backbone) | – | M | – | – | – | I+M | I+M | L6 L7 |
| S4 radial cavity length and subdivision | – | M | – | – | – | I+M | I+M | L6 |
| S5 population grouping | – | M | – | – | – | M | M | L6 |
| S6 local subdivision at a population boundary | – | M | – | – | – | I+M | M | L6 |
| S7 angular division coordinate | – | M | – | – | – | M | M | L6 |
| S8 angular reflector pattern / transparency | – | M | – | – | – | I+M | I+M | L6 |
| S9 curvature-coupling logarithm ℓ₀ | – | M | – | – | – | I+M | M | L6 |
| S10 longitudinal channel strength / clock box | – | – | – | – | I | I+M | M | L6 |
| S11 cavity gap and mirror profile | – | – | – | – | – | I+M | I+M | L6 |
| S12 short magnetic circuits | – | – | – | – | – | M | M | L6 |
| S13 planar EM Casimir cells and holding | – | M | – | – | – | I+M | I+M | L6 |
| S14 magnetic loop geometry / sleeve strength | – | – | – | – | – | I+M | – | L1 |
| S15 magnetic jacket | – | – | – | – | – | I+M | – | L1 |
| S16 containment ensemble orientation | – | – | – | – | – | I+M | – | L1 |
| S17 storage medium and converter directionality | – | – | – | – | M | I+M | M | L1 |
| S18 physical scale L | – | – | – | – | – | I | – | – |

S10 CS: "A global rescaling of time leaves the source and the bound unchanged"
(`COUPLED_REORIENTATION_INVESTIGATION.md:260-262`). No source-architecture
knob was evaluated on packet norms, algebraic type (the surrogate is Type I by
construction) or a handoff schedule.
