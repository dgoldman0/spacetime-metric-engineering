# Source Decomposition Proxy Fit

## Scope

This is a proxy fit against the point-level demanded-source ledger for the new freeze candidate:

```text
V10_tuned_w0569_eta200
R1.75 shaped catch radial-soft lapse-cushion v1
V = 10
```

The fit is diagnostic. It does not prove that any matter model realizes the geometry. It asks whether the demanded burden has a clean source-role story when represented by nonnegative component-shaped basis functions.

## Component basis used

| component | intended role |
|---|---|
| `cold_core_substrate` | standing support/core substrate tied to `q W` in the inner throat/core |
| `radial_support_edge_shell` | radial support-edge shell, using an edge proxy based on `W(1-W)` and support-edge region |
| `outer_quarantine_jacket` | broad angular/scalar-effective outer jacket, tied to `COmega - 1` and outer shell support |
| `lapse_cushion_sector` | lapse-cushion support, tied to `N = alpha/T` excess |
| `shift_packet_carrier` | packet-local carried shift envelope tied to `|beta| S E` |
| `catch_rematch_transient` | transient catch/rematch correction during live handoff |
| `release_shift_transient` | transient release/shift-fade correction |
| `packet_local_residual` | residual source demand inside the live packet corridor |
| `reset_decompression_infra` | reset/decompression infrastructure outside live packet exposure |

Each channel was fit separately with nonnegative least squares using volume-weighted point samples.

## Fit summary

| channel | actual total burden | actual live packet burden | live packet fraction | global underfit fraction | live underfit fraction |
|---|---:|---:|---:|---:|---:|
| neg_Tkk_radial | 317.3 | 72.379 | 22.8% | 13.8% | 12.1% |
| abs_p_l | 51.124 | 13.832 | 27.1% | 4.2% | 3.8% |
| abs_pOmega | 2.8847 | 0.0072147 | 0.3% | 86.9% | 53.7% |
| abs_j_l | 0.26111 | 0.0021128 | 0.8% | 64.5% | 20.5% |
| neg_rho_euler | 0.34431 | 0 | 0.0% | 97.7% | 0.0% |
| neg_rho_packet | 0.52804 | 0 | 0.0% | 98.0% | 0.0% |

## Top source-role allocations

- `neg_Tkk_radial` top proxy components: radial_support_edge_shell (30.3% actual), catch_rematch_transient (22.2% actual), lapse_cushion_sector (19.3% actual).
- `abs_p_l` top proxy components: cold_core_substrate (36.6% actual), outer_quarantine_jacket (27.3% actual), packet_local_residual (20.3% actual).
- `abs_pOmega` top proxy components: outer_quarantine_jacket (108.8% actual), reset_decompression_infra (18.6% actual), release_shift_transient (3.6% actual).
- `abs_j_l` top proxy components: reset_decompression_infra (60.2% actual), outer_quarantine_jacket (55.0% actual), release_shift_transient (5.9% actual).
- `neg_rho_euler` top proxy components: outer_quarantine_jacket (118.4% actual), reset_decompression_infra (9.4% actual), release_shift_transient (3.8% actual).
- `neg_rho_packet` top proxy components: outer_quarantine_jacket (127.5% actual), reset_decompression_infra (11.0% actual), release_shift_transient (3.8% actual).

## Initial interpretation

The proxy fit supports the design story in a limited but useful way. The largest channels are not evenly spread through the live packet; they are structured around support, catch/rematch, and release/reset roles. The angular-pressure burden is overwhelmingly an infrastructure/jacket problem, while live packet angular exposure remains tiny in the raw ledger. Negative Eulerian density and negative packet-comoving density have zero live packet burden in the frozen candidate ledger, so their residuals are infrastructure-only in this diagnostic.

The hard channels remain the same as before: negative radial `Tkk` and radial pressure `p_l`. The fit can represent much of their global shape, but live packet underfit remains nontrivial. That suggests the packet/catch layer still needs a transient source role rather than being fully explained by the standing infrastructure components.

## Practical conclusion

This source decomposition does not reveal a new global failure. It says the new freeze candidate has a plausible source-role split, but the catch/rematch sector still deserves its own transient component. The architecture should now be described as:

```text
standing infrastructure support
+ broad outer jacket
+ lapse-cushion safety support
+ transient locked-lead catch/rematch correction
+ small but real packet-local residual in radial-null/radial-pressure channels
```

The next source-side refinement should fit the catch/rematch correction more carefully rather than further modifying the reset/decompression sector.

## Files

- `source_fit_summary.csv`
- `source_component_allocation_by_channel.csv`
- `source_component_basis_diagnostics.csv`
- `source_residual_by_stage.csv`
- `source_residual_by_stage_region.csv`
- `source_top_underfit_points.csv`
- `source_candidate_point_ledger_with_basis.csv`
- `source_top_component_allocations.csv`
