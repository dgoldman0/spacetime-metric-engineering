# Stage II Entry-Gated Source-Sector Closure

## Summary

The entry-gated `wide4_start_m1p40` branch now has a dense source-sector closure pass on a `151 x 225` extended grid. The run preserves live packet safety, closes the radial-null and radial-pressure channels at the constrained sector level, and keeps the hard-affine SNEC benchmark clean at broad affine widths.

This is still not a physical matter-model solution. It is a constrained demanded-source sector closure: it tests whether a small set of source sectors can account for the full-grid ADM burden in a stable way before replacing those sectors with explicit matter models.

## Dense Ledger

Input branch:

```text
label = wide4_start_m1p40
live_packet_start = -1.40
entry_carve = 0.75
entry_width_multiplier = 4.8
catch_carve = 0.15
catch_width_multiplier = 3.4
edge_carve = 0.16
edge_width_multiplier = 7.2
null_cushion_log_gain = -0.07
```

Dense ledger:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_candidate_ledger_151x225/wide4_start_m1p40/
```

The ledger contains `33,975` rows on:

```text
s in [-1.50, 2.40]
l in [-4.20, 4.20]
grid = 151 x 225
h_s = h_l = 0.0025
```

It completed in about `2185 s` and has:

```text
positive live packet-norm samples: 0
```

## Sector-Basis Refinement

The first dense component pass repeated the earlier `101 x 151` pattern: live `p_l` was fully assigned, but non-live support-edge radial pressure remained as a large residual. That was not the same as the old Stage I live radial-pressure tradeoff. The residual was almost entirely infrastructure-side:

```text
catch_rematch / support_edge:   9.755215
entry_precatch / support_edge:  4.924728
live p_l residual:              0.000000
```

The closure basis was therefore refined by promoting:

```text
I_support_edge_radial_pressure_balance
```

as a non-live support-edge radial-pressure component. It is included in the infrastructure radial-support sector alongside:

```text
A_infrastructure_radial_null_support
B_core_radial_pressure_balance
```

This is a source-sector bookkeeping refinement, not a new metric knob.

## Dense Closure Fractions

Refined component source output:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_component_source_151x225_refined_roles/
```

| channel | total burden | assigned burden | residual fraction |
| --- | ---: | ---: | ---: |
| `neg_Tkk_radial` | `482.018354` | `475.555444` | `1.341%` |
| `abs_p_l` | `79.039467` | `78.024372` | `1.284%` |
| `abs_pOmega` | `11.323975` | `10.340515` | `8.685%` |
| `abs_j_l` | `0.736903` | `0.271242` before H | `63.192%` before H |

The current residual is handled by the H-promoted ansatz rather than by the base role labels:

```text
H_distributed_current_relaxation burden: 0.465661
H live burden: 0.000000
H constraint pass: true
H / D burden ratio: 2.561
```

The refined `101 x 151` comparison remains consistent:

```text
p_l residual fraction:       1.335%
radial-null residual:        1.445%
angular-pressure residual:   9.576%
current residual before H:  63.788%
```

## Sector Fit

H-promoted ansatz output:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_composite_ansatz_151x225_refined_with_H/
```

The required constrained sectors pass:

```text
infrastructure radial support:      pass
infrastructure angular capacity:    pass
live handoff trim:                  pass
distributed current relaxation H:   pass
```

The infrastructure radial-support fit remains essentially radial-tension-like even after adding the support-edge pressure sector:

```text
p_l_unit_per_rho_euler = -0.999288
j_l_unit_per_rho_euler = -0.000485
mean cross-component residual = 0.690989
```

The large cross-component residual is a reminder that this is still an effective anisotropic sector fit, not a physical constitutive law.

## Hard Affine SNEC

Refined dense SNEC output:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_hard_affine_snec_151x225_refined_tau2_tau3_tau4_sector_sum/
```

The scan used sector-sum accounting, affine widths:

```text
tau = 2.0, 3.0, 4.0
```

and scanned `203,838` affine windows. It found:

```text
raw benchmark-floor violations:       0
scoreable benchmark-floor violations: 0
```

Worst scoreable margins:

| tau | branch | worst `T_hat_kk` | floor | margin | worst center |
| ---: | --- | ---: | ---: | ---: | --- |
| `2.0` | minus | `-0.002734` | `-0.062500` | `0.059766` | `entry_precatch / support_edge` |
| `2.0` | plus | `-0.002610` | `-0.062500` | `0.059890` | `catch_rematch / support_edge` |
| `3.0` | minus | `-0.001194` | `-0.027778` | `0.026583` | `entry_precatch / support_edge` |
| `3.0` | plus | `-0.001128` | `-0.027778` | `0.026649` | `entry_precatch / support_edge` |
| `4.0` | minus | `-0.000602` | `-0.015625` | `0.015023` | `entry_precatch / support_edge` |
| `4.0` | plus | `-0.000656` | `-0.015625` | `0.014969` | `entry_precatch / support_edge` |

The limiting sector in the worst windows is `sector_closure_residual`, not a live packet condition.

## Interpretation

The dense closure pass supports the entry-gated source-placement story:

```text
protected live packet corridor
  coupled to
infrastructure radial-null and radial-pressure support
  plus
infrastructure angular capacity
  plus
live handoff trim
  plus
non-live distributed current relaxation H
```

The old Stage I `p_l` worry does not reappear here as a live-packet closure failure. In this pass, live `p_l` is assigned with zero live residual. The apparent `p_l` gap was a missing non-live support-edge pressure sector, and adding that sector leaves the constrained radial-support fit intact.

The remaining open problem is physical replacement of the effective sectors. The current result is report-grade as a demanded-source sector closure, but it should not be described as a matter-source proof.

## Design Alignment

The closure sectors are source-side roles, while the design components are metric/service mechanisms. They align as follows:

| closure sector | dense burden | live burden | designed components | source-replacement target |
| --- | ---: | ---: | --- | --- |
| `A/B/I` infrastructure radial support | `538.872629` | `0.000000` | cold support skeleton, radial-soft support edge, two-feature `gamma_ll` radial support, compact entry/catch support | radial tension plus radial-pressure balance for core and support-edge infrastructure |
| `G` infrastructure angular capacity | `8.625375` | `0.000000` | angular/effective jacket, throat-capacity comparator, support-shell geometry | angular/throat pressure support without large radial-current leakage |
| `C/E/F` live handoff trim | `16.511753` | `16.511753` | entry service gate, compact handoff layer, packet beta-rematch, locked catch/rematch | packet-facing trim for live angular/current, radial-null, and radial-pressure handoff |
| `D/H` current relaxation | `0.647478` | `0.000000` | support-contained carried shift, reset/decompression, release choreography, support-shell carrying-flow bookkeeping | non-live shift/current sink plus distributed current relaxation |
| closure residual | channel-dependent | `0.000000` in residual summaries | not yet a designed component | residual model or conservation-correction target, mainly support-edge and outer-shell structure |

This alignment is the main practical value of the closure pass. The result is no longer just a channel table; it says which design mechanisms have corresponding source-sector roles and which roles still need physical realization.

## Residual Priorities

After the refined sector basis, the residual hierarchy is:

| residual channel | residual burden | residual fraction | interpretation |
| --- | ---: | ---: | --- |
| `neg_Tkk_radial` | `6.462910` | `1.341%` | small non-live radial-null residue, mostly outside the live packet corridor |
| `abs_p_l` | `1.015095` | `1.284%` | support-edge/core pressure basis mostly closed after adding I |
| `abs_pOmega` | `0.983459` | `8.685%` | broad angular residual, still infrastructure-side |
| `abs_j_l` | `0.465661` | `63.192%` before H | current is small in absolute burden but needs H as a real non-live relaxation sector |

The current residual percentage looks large only because the absolute current burden is small and the base role set intentionally kept D narrow. With H promoted, the current sector is non-live and constraint-compatible. That makes H a physical-source modeling target rather than an immediate geometry failure.

The SNEC-limiting windows are also residual-dominated, not live-packet dominated. The worst broad windows sit in `entry_precatch / support_edge` or `catch_rematch / support_edge`, and the dominant negative sector is `sector_closure_residual`. This points to source-basis refinement and conservation modeling before any new geometry knob.

## Next Step

The next rigorous step is to replace the effective sectors with one or more explicit source-family models:

```text
A/B/I: infrastructure radial support and pressure balance
G: angular/throat capacity
C/E/F: live handoff trim
D/H: reset and distributed current relaxation
```

The first physical-source replacement should focus on whether `H` and the support-edge pressure sector can be represented without reintroducing live packet contamination or large conservation defects.
