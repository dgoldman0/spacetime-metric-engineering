# Stage II Beta-Memory Receiver Smoke Memo

Date: 2026-05-20

## Scope

This memo records the first `61 x 83` smoke test of the beta-memory
support-edge receiver source grammar. It is a short branch note, not a full
source-model report.

The test kept the beta/support co-design baseline geometry and added a
non-live support-edge receiver driven by accumulated beta-release memory. The
receiver was split into:

```text
R1 radial/current cap:
  bilateral, outer-weighted support-edge cap with radial metric and beta
  relaxation partners.

R2 angular flange:
  positive-l support-edge angular capacity partner.
```

Outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_smoke_61x83/
```

## Result

All five source-ledger cases were live-clean on the smoke grid:

| label | positive live packet-norm samples |
| --- | ---: |
| `receiver_baseline_beta075` | `0` |
| `receiver_R1_radial_current_beta075` | `0` |
| `receiver_R2_angular_pos_beta075` | `0` |
| `receiver_R1_R2_combined_beta075` | `0` |
| `receiver_R1_R2_combined_beta100` | `0` |

The selected-null/J total moved in the desired direction for the angular and
combined variants:

| label | J selected-null deficit |
| --- | ---: |
| `receiver_baseline_beta075` | `0.964417` |
| `receiver_R1_radial_current_beta075` | `0.964788` |
| `receiver_R2_angular_pos_beta075` | `0.949838` |
| `receiver_R1_R2_combined_beta075` | `0.948694` |
| `receiver_R1_R2_combined_beta100` | `0.944040` |

But the support-edge current and angular costs grew sharply:

| label | support-edge current | support-edge angular |
| --- | ---: | ---: |
| `receiver_baseline_beta075` | `0.105033` | `1.912497` |
| `receiver_R1_radial_current_beta075` | `0.105575` | `2.023708` |
| `receiver_R2_angular_pos_beta075` | `0.551170` | `2.313310` |
| `receiver_R1_R2_combined_beta075` | `0.546722` | `2.433692` |
| `receiver_R1_R2_combined_beta100` | `0.584386` | `2.667844` |

## Interpretation

The data supports the branch direction but rejects this first stress-channel
realization.

The beta-memory receiver geometry is viable enough to keep: it is non-live,
full-grid smoke-safe, and can move the stubborn selected-null endpoint total.
However, direct rail-stretch/beta-relaxation plus positive-l angular
`gamma_omega` gain does not behave like a clean support-edge absorber. It
reduces selected-null burden by creating a larger current/angular burden at
the support edge.

Narrative update:

```text
Right track: beta-memory support-edge receiver.
Wrong realization: direct R1/R2 metric partners are too stress-expensive.
```

Next branch should keep the memory-driven non-live receiver localization, but
try a different stress-channel realization before any promotion claim.
