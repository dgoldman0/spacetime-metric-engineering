# Stage II Affine-Reparameterized SNEC Audit

Date: 2026-05-21

## Purpose

This report records the follow-up to the hard-affine SNEC criticism. The issue
was narrow but important: the older SNEC trace parameter advanced the smearing
coordinate with a lapse-normalized rule, roughly `d lambda = alpha ds`, while
the report language called the result hard-affine. In a general scheduled ADM
metric that lapse parameter is not automatically an affine parameter along the
radial null branch.

The audit therefore adds an explicit radial-null non-affinity calculation. For
the coordinate-time radial null tangent

```text
K = (1, dl/ds)
```

the harness computes `K^nu nabla_nu K^mu`, extracts the time-component
non-affinity `kappa`, integrates the associated center-normalized affine
weight, and records the remaining radial geodesic residual as a diagnostic.
This turns the old lapse-parametrized screen into an affine-reparameterized
radial-null screen with residual monitoring. It is still not a quantum RSET
calculation, conservation proof, physical matter solve, or full off-axis
geodesic theorem.

## Code Changes

Updated files:

```text
toolkit/adm_harness_cli/adm_harness/hard_affine_snec.py
toolkit/adm_harness_cli/scripts/run_hard_affine_snec_screen.py
```

The SNEC runner now accepts:

```text
--parameterization affine
--parameterization lapse
```

`affine` is the default. The legacy lapse-normalized screen remains available
for comparison, but report-grade hard-affine wording should use an audit run
with `parameterization = affine`.

Each window table now records:

```text
trace_parameterization
max_abs_non_affinity_kappa
mean_abs_non_affinity_kappa
max_abs_radial_geodesic_residual
min_dlambda_dsigma
max_dlambda_dsigma
```

## Runs

The focused stride-8 smoke audit was:

```text
toolkit/adm_harness_cli/runs/affine_reparam_snec_beta075_promotion_dense_stride8/
```

It scanned `21,960` windows and found zero benchmark-floor violations.

The report-grade full-stride audit was:

```text
python toolkit/adm_harness_cli/scripts/run_hard_affine_snec_screen.py \
  --component-dir toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_negative_l_promotion_dense_81x121/component_all \
  --outdir toolkit/adm_harness_cli/runs/affine_reparam_snec_beta075_promotion_dense_full \
  --smear-width 0.5 \
  --smear-width 1.0 \
  --smear-width 2.0 \
  --center-stride 1 \
  --parameterization affine \
  --top-limit 120
```

Output:

```text
toolkit/adm_harness_cli/runs/affine_reparam_snec_beta075_promotion_dense_full/
```

Runtime was `1604.372 s`.

## Full-Stride Result

The full audit scanned the dense beta075 negative-l receiver promotion package:

| artifact | rows |
| --- | ---: |
| window table | 175851 |
| summary table | 18 |
| sector summary | 108 |
| top windows | 360 |

Coverage filtering left `52,209` scoreable windows. The result is clean:

```text
all-window benchmark-floor violations: 0
scoreable benchmark-floor violations: 0
summary rows passing benchmark: 18 / 18
```

The scoreable worst margin is:

| label | branch | width | center | stage / region | smeared Tkk | floor | margin | dominant negative sector |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | --- |
| `receiver_neg_promotion_baseline_beta075` | plus | 2.0 | `s=-0.72, l=-0.42` | `entry_precatch / packet_in_support` | -0.001148 | -0.0625 | 0.061352 | `live_handoff_trim` |

The all-window worst margin, including non-scoreable coverage-limited windows,
is still positive:

| label | branch | width | center | stage / region | smeared Tkk | floor | margin | scoreable |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | --- |
| `receiver_neg_promotion_baseline_beta075` | plus | 2.0 | `s=2.3025, l=2.94` | `reset_decompression / outer_quarantine_shell` | -0.026985 | -0.0625 | 0.035515 | false |

## Affine Diagnostics

The affine correction is not cosmetic. Across the full window table:

| diagnostic | median | 90% | 99% | max |
| --- | ---: | ---: | ---: | ---: |
| `max_abs_non_affinity_kappa` | 6.141065 | 14.622550 | 73.738530 | 104.935500 |
| `mean_abs_non_affinity_kappa` | 1.817085 | 6.204035 | 25.943730 | 40.729440 |
| `max_abs_radial_geodesic_residual` | 0.059491 | 1.121512 | 37.594390 | 103.057200 |
| `max_dlambda_dsigma` | 42.767543 | 322.369065 | 497.229223 | 1291.418338 |

This confirms the interpretation issue in the criticism: the old lapse
parameter should not be described as physically affine without qualification.
The new audit directly measures the correction scale and remains clean after
using the affine-reparameterized window coordinate.

## Interpretation

This resolves the specific wording problem for the dense beta075 promotion
package:

```text
Risky old wording:
  clean hard-affine SNEC

Correct current wording:
  clean affine-reparameterized radial-null SNEC screen with residual monitoring
```

The beta075 `p003_mid` effective receiver therefore keeps its SNEC companion
support under the corrected parameterization. This strengthens the evidence
that the promoted effective source grammar is not being saved by a mislabeled
lapse-parametrized smearing coordinate.

The remaining boundary is unchanged. The audit is still an effective-source
screen on demanded ledger channels and an H-promoted sector ansatz. It does not
close endpoint conservation, physical matter realization, semiclassical
acceptability, quantum inequality cost, off-axis null congruence behavior, or
global trapped-surface questions.

## Current Claim Language

Use:

```text
The dense beta075 negative-l receiver package passes a full-stride
affine-reparameterized radial-null SNEC diagnostic at affine smear widths
0.5, 1.0, and 2.0, with zero all-window and zero scoreable benchmark-floor
violations across 175,851 windows.
```

Avoid:

```text
The physical affine SNEC/QI condition is proven.
The source is semiclassically admissible.
The matter model is complete.
```

