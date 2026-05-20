# Stage II Hard Affine SNEC Adversarial Pass

## Purpose

This pass stress-tests the first hard affine SNEC result against the most suspicious failure modes and then adjudicates the broad-window boundary hits on an extended domain:

```text
boundary-truncated broad affine windows and their extended-domain resolution;
sector-sum versus geometric total accounting;
sector ablations for G, H, D, and closure residual.
```

The target is the denser compact ledger:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_source_compact_81x109_full_roles/
```

The adversarial widths are:

```text
tau = 2.0, 3.0, 4.0
```

Scoreable windows require both:

```text
support coverage >= 0.80 across the requested +/- 4 tau trace support;
Gaussian kernel weight coverage >= 0.80.
```

## Output Directories

```text
boundary-aware geometric total:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_81x109_boundary_broad_geometric/

sector-sum baseline:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_81x109_sector_sum_broad/

G ablation:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_81x109_ablate_G_broad/

H ablation:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_81x109_ablate_H_broad/

D ablation:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_81x109_ablate_D_broad/

closure-residual ablation:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_81x109_ablate_closure_broad/

extended source ledger:
toolkit/adm_harness_cli/runs/stage2_external/stage2_compact_kill_candidate_ledger_extended_s1p5_2p4_l4p2_101x151/compact7_wide4_edge160/

extended component ledger:
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_source_compact_extended_s1p5_2p4_l4p2_101x151_full_roles/

extended-domain hard SNEC adjudication:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_extended_s1p5_2p4_l4p2_101x151_tau2_tau3_tau4_boundary/
```

## Boundary-Aware Baseline

The coverage-aware geometric-total run scanned `52,962` windows.

No scoreable benchmark-floor violations were found.

| tau | scoreable windows | rejected windows | raw all-window violations | scoreable violations | worst scoreable `T_hat_kk` | floor | margin | dominant sector |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2.0 | 3,954 / 3,997 | 4,873 / 4,830 | 0 / 0 | 0 / 0 | -0.00105 | -0.06250 | 0.06145 | G |
| 3.0 | 3,459 / 3,564 | 5,368 / 5,263 | 0 / 0 | 0 / 0 | -0.00067 | -0.02778 | 0.02711 | live trim |
| 4.0 | 3,145 / 3,259 | 5,682 / 5,568 | 189 / 189 | 0 / 0 | -0.00041 | -0.01563 | 0.01521 | live trim |

The important result is the `tau = 4.0` split:

```text
raw all-window scan: boundary-truncated windows can fail;
scoreable-window scan: no failures after enforcing affine support coverage.
```

This did not mean the raw failures were physically real. It meant the current domain was not sufficient to score those broad boundary windows. The extended-domain pass below resolves that ambiguity.

## Extended-Domain Adjudication

The compact target was rerun on a larger grid:

```text
101 x 151
s in [-1.50, 2.40]
l in [-4.20, 4.20]
```

This was an adjudication domain, not a newly promoted safe candidate. It found two positive live packet-norm points at the newly exposed early-entry boundary:

| s | l | stage | region | packet norm |
| ---: | ---: | --- | --- | ---: |
| -1.500 | -1.792 | entry_precatch | packet_outer | 1.6255 |
| -1.422 | -1.736 | entry_precatch | packet_in_support | 1.2549 |

Those two points matter for future geometry/domain work, but they do not explain a SNEC failure: the extended hard affine SNEC scan found no benchmark-floor violations at all.

The extended SNEC run scanned `91,494` windows.

| tau | scoreable windows | rejected windows | raw all-window violations | scoreable violations | worst scoreable `T_hat_kk` | floor | margin | dominant sector |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2.0 | 4,117 / 4,127 | 11,132 / 11,122 | 0 / 0 | 0 / 0 | -0.00261 | -0.06250 | 0.05989 | closure residual |
| 3.0 | 3,631 / 3,647 | 11,618 / 11,602 | 0 / 0 | 0 / 0 | -0.00107 | -0.02778 | 0.02671 | closure residual |
| 4.0 | 3,293 / 3,343 | 11,956 / 11,906 | 0 / 0 | 0 / 0 | -0.00069 | -0.01563 | 0.01494 | closure residual / live trim |

The old `tau = 4.0` raw failures disappeared when the affine traces were given enough surrounding domain. That turns the previous broad-window concern into a boundary-truncation artifact, not a real SNEC kill.

## Sector-Sum Baseline

The sector-sum baseline matches the coverage-aware geometric result at the scoreable-window level. This confirms that the H-promoted sector decomposition plus closure residual reconstructs the tested geometric total well enough for this screen.

Worst scoreable margins:

| tau | worst margin | worst `T_hat_kk` | floor | dominant sector |
| ---: | ---: | ---: | ---: | --- |
| 2.0 | 0.06145 | -0.00105 | -0.06250 | G |
| 3.0 | 0.02711 | -0.00067 | -0.02778 | live trim |
| 4.0 | 0.01521 | -0.00041 | -0.01563 | live trim |

## Sector Ablations

All ablations pass the scoreable benchmark.

The table reports the worst scoreable margin across both radial branches.

| run | tau = 2.0 | tau = 3.0 | tau = 4.0 | interpretation |
| --- | ---: | ---: | ---: | --- |
| sector-sum baseline | 0.06145 | 0.02711 | 0.01521 | baseline effective sector total |
| remove G | 0.05996 | 0.02614 | 0.01465 | still passes; G is not hiding the pass |
| remove H | 0.06129 | 0.02715 | 0.01525 | still passes; H not required for broad-window pass |
| remove D | 0.06145 | 0.02712 | 0.01523 | still passes; D not required for broad-window pass |
| remove closure residual | 0.06085 | 0.02650 | 0.01463 | still passes; closure is not hiding a scoreable failure |

Interpretation:

```text
the scoreable broad-window pass is not produced by one fragile positive sector cancellation;
removing G or closure residual worsens the tightest broad margin slightly, but does not break it;
H/D matter more at short widths than broad widths, consistent with earlier sector readout.
```

## What Broke And What Held

The thing that broke was not the SNEC benchmark. The thing that broke was the naive assumption that all broad-width windows are equally scorable on the original `81 x 109` domain.

At `tau = 4.0`, many original-domain windows were boundary truncated. Some of those raw all-window averages violated the benchmark floor. Because they lacked enough affine support, they were not trustworthy pass/fail windows.

The extended-domain rerun answered the domain-coverage question:

```text
the tau = 4 boundary failures do not persist when the source ledger domain is extended far enough to score them.
```

## Verdict

The current compact model still holds under scoreable broad-width, sector-ablation, and extended-domain hard affine SNEC tests.

The broad-window SNEC result is stronger after this pass, not weaker:

```text
original-domain tau = 4 raw failures were boundary truncation artifacts;
extended-domain tau = 2, 3, and 4 scans have zero raw and zero scoreable benchmark violations;
the limiting concern has shifted from SNEC failure to packet-safety/domain behavior at the newly exposed early-entry edge.
```

This still is not a physical-source proof. The right next deeper work is to use the remaining SNEC margin while replacing oracle-like sector accounting with a more constrained source ansatz, and separately decide whether the extended early-entry packet-norm failures require a geometry boundary refinement or simply mark the edge of the adjudication-only domain.

## Harness Progress Note

The long extended-domain runs also exposed a practical reporting gap. The candidate-ledger and hard-affine SNEC runners now emit start records, progress heartbeats, and elapsed seconds by default, with `--no-progress` available for quiet batch runs.
