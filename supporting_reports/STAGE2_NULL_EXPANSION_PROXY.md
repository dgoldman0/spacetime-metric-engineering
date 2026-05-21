# Stage II Null-Expansion Proxy

Date: 2026-05-21

## Purpose

This report records the first trapped-surface-oriented diagnostic after the
scheduled ADM confidence run. The immediate question was whether the favorable
radial escape and scheduled-probe results also look safe under a local
areal-expansion proxy.

This is a higher-tier causal screen than radial escape, but it is still a proxy.
It is not a theorem-level trapped-surface calculation, global event-horizon
proof, matter evolution, or full dynamical Einstein evolution.

## Diagnostic

New postprocessor:

```text
toolkit/adm_harness_cli/scripts/run_null_expansion_proxy.py
```

The diagnostic uses the prescribed ADM point ledger fields:

```text
R = sqrt(gamma_omega)
v_+/- = -beta +/- alpha / sqrt(gamma_ll)
theta_+/- = 2 (d_s R + v_+/- d_l R) / R
```

Rows where both `theta_plus` and `theta_minus` are negative are marked as a
`both_shrinking` trapped-like warning proxy. Rows where either expansion is near
zero are tracked as marginal. The protected read is the live packet, service-live
subset, and the live branch-band subset.

## Runs

The first run used the `s15` scheduled ADM confidence ledger:

```text
toolkit/adm_harness_cli/runs/null_expansion_beta075_p003_mid_s15/
```

To check future-domain sensitivity, the same postprocessor was also run on the
refined `s9` long-tail ledger and the `s12` confidence ledger:

```text
toolkit/adm_harness_cli/runs/null_expansion_beta075_p003_mid_s9/
toolkit/adm_harness_cli/runs/null_expansion_beta075_p003_mid_s12/
```

All three runs used:

```text
theta_eps = 1e-6
```

## Main Result

The result is adverse in the proxy sense. On the `s15` confidence ledger, the
protected live scopes contain both-branch areal-shrinking rows:

| scope | rows | both-shrinking rows | fraction | volume fraction | max trapped-like strength | max packet norm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `packet_live` | 238 | 102 | 42.857% | 56.054% | 0.733217 | -8.943909 |
| `service_live` | 154 | 48 | 31.169% | 28.559% | 0.434664 | -22.726463 |
| `branch_band_live_q20` | 48 | 29 | 60.417% | 59.340% | 0.280469 | -25.074652 |

The reset/wake red-tag channel does not appear to be the cause of this proxy
warning:

| scope | rows | both-shrinking rows | near-marginal rows | split-expansion rows |
| --- | ---: | ---: | ---: | ---: |
| `post_release_packet` | 28 | 0 | 0 | 28 |
| `reset_tail_packet_geom` | 354 | 0 | 0 | 354 |

## Domain Trend

The warning is stable across the future-domain confidence ladder:

| rung | packet live both-shrinking | service live both-shrinking | branch-band live q20 both-shrinking | branch-band max trapped-like strength |
| --- | ---: | ---: | ---: | ---: |
| `s9` | 103 / 237 | 49 / 154 | 31 / 48 | 0.278672 |
| `s12` | 102 / 238 | 48 / 154 | 29 / 48 | 0.279770 |
| `s15` | 102 / 238 | 48 / 154 | 29 / 48 | 0.280469 |

This makes the result unlikely to be a late future-boundary tail artifact. It is
also not explained by the remaining `s15` exterior wake-tail traces, because the
reset-tail packet-geometry scope is split-expansion clean in this proxy.

## Localization

The strongest protected live hits are localized in:

```text
stage:  entry_precatch
region: packet_in_support
l:      negative-l side, approximately -1.6 to -0.8 in the strongest rows
```

Representative high-strength live rows include:

| s | l | stage | region | theta_plus | theta_minus | trapped-like strength | packet norm |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: |
| -1.324468 | -1.6 | `entry_precatch` | `packet_in_support` | -1.244274 | -0.733217 | 0.733217 | -8.943909 |
| -1.324468 | -1.5 | `entry_precatch` | `packet_in_support` | -1.263767 | -0.706316 | 0.706316 | -16.165669 |
| -1.324468 | -1.4 | `entry_precatch` | `packet_in_support` | -1.284584 | -0.680613 | 0.680613 | -17.888895 |

These rows are packet-norm safe. The issue is not packet timelikeness. The issue
is local both-branch areal focusing in the live/service entry band.

## Interpretation

The previous escape result still matters: branch-band radial, off-axis, and
small-bundle scheduled probes reached radial boundaries on the confidence
domains. This diagnostic does not erase that result.

It does change the causal read. The project now has a real diagnostic tension:

```text
radial escape / scheduled probes: favorable
local live areal-expansion proxy: adverse
reset wake-tail proxy: clean
```

The right interpretation is not "global horizon failure is proven." The right
interpretation is:

```text
The promoted beta075 p003_mid service program contains a stable local
both-branch areal-shrinking proxy in live entry/branch-band rows. The next causal
question is whether scheduled probes pass through this focusing patch and
re-expand, or whether the patch produces sustained negative expansion/caustic
behavior consistent with a trapped-surface warning.
```

## Decision

Do not run `s18` as the main branch. The `s18` rung would address exterior
wake-tail closure, while this diagnostic found a stable entry-side live focusing
warning.

Do not jump directly to full dynamical Einstein evolution or a broad source
redesign either. The next high-value rung is a trace-integrated
expansion/focusing audit along the already-used scheduled ADM probe families,
especially:

```text
radial_null_branch_band minus traces
offaxis_null_branch_band minus traces
congruence_branch_band minus traces
entry_precatch packet_in_support live seeds
```

Promotion criterion for the next rung:

```text
The both-shrinking patch is transient, integrated focusing is bounded, no probe
develops sustained negative expansion or caustic-like compression, and traces
recover split or positive outgoing expansion after exiting the entry band.
```

Failure criterion:

```text
The branch-band/live-entry probes accumulate sustained both-branch negative
expansion, develop caustic-like bundle compression, or remain trapped-like after
leaving the entry packet-in-support band.
```
