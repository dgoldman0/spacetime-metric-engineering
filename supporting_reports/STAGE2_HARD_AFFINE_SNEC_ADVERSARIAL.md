# Stage II Hard Affine SNEC Adversarial Pass

## Purpose

This pass stress-tests the first hard affine SNEC result against the most suspicious failure modes:

```text
boundary-truncated broad affine windows;
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

This does not mean the raw failures are physically real. It means the current domain is not sufficient to score those broad boundary windows. They must be tested on an extended domain, not counted as either pass or fail.

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

## What Broke

The thing that broke was not the scoreable SNEC benchmark. The thing that broke was the naive assumption that all broad-width windows are equally scorable on the current domain.

At `tau = 4.0`, many windows are boundary truncated. Some of those raw all-window averages violate the benchmark floor. Because they lack enough affine support, they are not trustworthy pass/fail windows.

This turns the next question into a domain-coverage question:

```text
Do the tau = 4 boundary failures persist when the source ledger domain is extended far enough to score them?
```

## Verdict

The current compact model still holds under scoreable broad-width and sector-ablation tests.

But the adversarial pass found a real next risk:

```text
broad affine windows near the domain boundary are under-resolved/truncated;
some raw truncated tau = 4 windows fail;
the current domain cannot adjudicate those windows.
```

That is not a kill, but it is no longer just a clean pass. The next deeper test should extend the ledger domain in `s` and probably `l`, rerun the compact target at moderate resolution, and rescore `tau = 3.0` and `4.0` boundary windows with adequate affine support.
