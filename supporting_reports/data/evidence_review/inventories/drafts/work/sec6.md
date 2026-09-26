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
