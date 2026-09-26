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
