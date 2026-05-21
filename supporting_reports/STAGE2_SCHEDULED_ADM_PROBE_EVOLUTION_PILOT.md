# Stage II Scheduled ADM Probe Evolution Pilot

Date: 2026-05-21

## Purpose

This pilot starts the semi-dynamical audit tier after the beta075 branch-band
convergence check. It treats the promoted beta075 `p003_mid` metric fields as a
prescribed service program:

```text
alpha(sigma,l), beta(sigma,l), gamma_ll(sigma,l), gamma_omega(sigma,l)
```

and evolves probe families through that scheduled geometry. This is not a
physical matter evolution and not a full dynamical Einstein evolution.

## Runner

New harness entry point:

```text
toolkit/adm_harness_cli/scripts/run_scheduled_adm_probe_evolution.py
```

Run output:

```text
toolkit/adm_harness_cli/runs/scheduled_adm_beta075_p003_mid_pilot/
```

Input ledger:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/ledgers/horizon_escape_beta075_p003_mid/source_ledger_point_ledger.csv
```

Command:

```text
python toolkit/adm_harness_cli/scripts/run_scheduled_adm_probe_evolution.py \
  --point-ledger toolkit/adm_harness_cli/runs/horizon_escape_ladder_beta075_refined_121x121/ledgers/horizon_escape_beta075_p003_mid/source_ledger_point_ledger.csv \
  --label scheduled_adm_beta075_p003_mid_pilot \
  --outdir toolkit/adm_harness_cli/runs/scheduled_adm_beta075_p003_mid_pilot \
  --seeds-per-family 24 \
  --red-tag-seeds 80 \
  --trace-step-scale 0.5 \
  --max-steps 8000 \
  --angular-fraction 0.35
```

## Probe Families

The pilot traces:

```text
packet_centerline
packet_tube_edge
radial_null_branch_band
offaxis_null_branch_band
congruence_branch_band
red_tag_reset_tail
```

The red tag is explicit:

```text
reset_decompression packet_geom minus-branch wake tail
```

## Summary

| probe family | branch | traces | radial escapes | future-boundary traces | live entries | red-tag touches | branch sign changes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `packet_centerline` | packet | 24 | 0 | 24 | 24 | 0 | 0 |
| `packet_tube_edge` | packet | 24 | 13 | 11 | 0 | 24 | 0 |
| `radial_null_branch_band` | plus | 24 | 24 | 0 | 24 | 0 | 0 |
| `radial_null_branch_band` | minus | 24 | 24 | 0 | 24 | 0 | 22 |
| `offaxis_null_branch_band` | offaxis_plus | 24 | 24 | 0 | 24 | 24 | 0 |
| `offaxis_null_branch_band` | offaxis_minus | 24 | 24 | 0 | 24 | 0 | 22 |
| `congruence_branch_band` | plus | 25 | 25 | 0 | 25 | 0 | 0 |
| `congruence_branch_band` | minus | 25 | 25 | 0 | 25 | 0 | 22 |
| `red_tag_reset_tail` | minus | 41 | 0 | 41 | 0 | 41 | 0 |

Interpretation notes:

```text
packet_centerline future-boundary traces are scheduled-service completions, not
radial escape failures.

radial/off-axis/congruence branch-band probes escape cleanly, including the
minus-branch families with branch sign changes.

the red-tag reset tail remains unresolved on the current future domain.
```

## Red-Tag Monitor

The red-tag monitor selected 41 unique reset-decompression packet-geometry tail
seeds after de-duplication. All 41 minus-branch traces reached the future
domain boundary rather than a radial boundary:

| traces | lower radial escapes | upper radial escapes | future-boundary traces | live-packet entries | final l range |
| ---: | ---: | ---: | ---: | ---: | --- |
| 41 | 0 | 0 | 41 | 0 | -5.098563 .. 2.443750 |

The red tag therefore stays open. The favorable part is that these traces did
not re-enter the live packet. The unfavorable part is that wake-tail closure is
not decided on the present `s_max = 9.0` domain.

## Source-Channel And Expansion Monitors

The runner records max absolute channel activity along each probe for:

```text
alpha
beta
gamma_ll
gamma_omega
```

It also records finite-difference areal-expansion proxies from
`sqrt(gamma_omega)` along each trace. These are probe monitors only, not
trapped-surface diagnostics. In this pilot the branch-band congruence bundles
all reached radial boundaries, so no bundle-level trapped behavior was observed
at this rung. The expansion proxy still has mixed signs and should remain a
later dedicated diagnostic.

## Current Read

The scheduled ADM pilot preserves the branch-band result in a richer probe
audit:

```text
Prescribed-metric radial, off-axis, and small-bundle branch-band probes escape.
The reset-decompression packet-geometry wake tail remains unresolved but stays
outside the live packet.
```

Next scheduled-ADM work should extend or retime the reset-decompression tail
domain before any stronger release/wake claim. Full dynamical Einstein evolution
still comes later.
