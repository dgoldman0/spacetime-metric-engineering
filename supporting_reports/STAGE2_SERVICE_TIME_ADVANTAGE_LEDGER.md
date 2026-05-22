# Stage II Service-Time Advantage Ledger

Date: 2026-05-21

## Purpose

This report records the first operational superluminality rating for the active
rail. The question is not whether the packet is locally faster than light and
not whether the metric is physically realized. The question is whether the
reconstructed service sequence reaches a restored exterior endpoint earlier
than an ordinary exterior null reference signal over the same inferred endpoint
separation.

The ledger is therefore a documentation and narrative component. It is not a
packet-timelikeness, dense-bundle, source-family, global-horizon, or physical
matter-model gate.

## Diagnostic

New postprocessor:

```text
toolkit/adm_harness_cli/scripts/run_service_time_advantage_ledger.py
```

Output directory:

```text
toolkit/adm_harness_cli/runs/service_time_advantage_beta_collar_s15/
```

Input cases:

```text
baseline_s15:
  toolkit/adm_harness_cli/runs/scheduled_adm_confidence_beta075_s15_189x121/ledgers/horizon_escape_beta075_p003_mid/source_ledger_point_ledger.csv

rematch_w6_t1p5:
  toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/ledgers/rematch_w6_t1p5/source_ledger_point_ledger.csv

rematch_w8_t2p0:
  toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/ledgers/rematch_w8_t2p0/source_ledger_point_ledger.csv
```

The ledger uses the manifest schedule to define the departure and restored
arrival events. Departure is the configured live-packet start, and restored
arrival is the live-packet end after release and post-release restoration. It
then reconstructs three A-to-B comparison distances:

1. `schedule_factor_distance`: the direct service-factor transport integral
   using `U_packet`.
2. `packet_coord_proxy_distance`: the centerline packet-coordinate proxy using
   `U_packet / B`.
3. `centerline_l_equals_s_distance`: the strict source-grid centerline control,
   using the modeled tube relation `l = s`.

The exterior null reference time is the corresponding exterior distance in
units with `c = 1`. The service has an operational advantage when the inferred
distance divided by service time is greater than one.

## Result

The first service-time ledger is favorable under both transport proxies and
neutral under the strict `l = s` control.

| label | prepared service time | schedule-factor distance | schedule-factor ratio | packet-coordinate distance | packet-coordinate ratio | centerline control |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline_s15` | `3.045` | `7.822491` | `2.568962` | `3.755436` | `1.233312` | `1.000000` |
| `rematch_w6_t1p5` | `3.045` | `7.822491` | `2.568962` | `3.755436` | `1.233312` | `1.000000` |
| `rematch_w8_t2p0` | `3.045` | `7.822491` | `2.568962` | `3.755436` | `1.233312` | `1.000000` |

If setup is treated as request-triggered rather than standing prepared plant,
the service clock starts at the first sampled setup row. The distance remains
the A-to-B distance after packet departure, so only the denominator changes.
The result remains favorable:

| label | request-triggered service time | schedule-factor ratio | packet-coordinate ratio |
| --- | ---: | ---: | ---: |
| `baseline_s15` | `3.145` | `2.487278` | `1.194097` |
| `rematch_w6_t1p5` | `3.145` | `2.487278` | `1.194097` |
| `rematch_w8_t2p0` | `3.145` | `2.487278` | `1.194097` |

The plateau-extension table inserts additional carried-shift duration at the
observed schedule plateau without rebuilding a longer metric ledger. It gives
the expected long-baseline trend:

| plateau extension | schedule-factor ratio | packet-coordinate ratio |
| ---: | ---: | ---: |
| `0` | `2.568962` | `1.233312` |
| `1` | `3.169961` | `1.433150` |
| `3` | `3.775433` | `1.634476` |
| `10` | `4.432540` | `1.852971` |
| `100` | `4.928162` | `2.017770` |

## Interpretation

The service-time result is positive in the intended operational sense. In the
current prescribed schedule, the reconstructed service sequence reaches the
restored endpoint earlier than the exterior null reference associated with the
same service-factor distance, and it also remains above unity under the more
conservative centerline `U_packet / B` proxy. The strict `l = s` control remains
exactly neutral, as expected, because it measures the bookkeeping diagonal of
the source grid rather than the service-factor transport rating.

The beta-collar repair does not reduce the service-time rating in this first
ledger. `baseline_s15`, `rematch_w6_t1p5`, and `rematch_w8_t2p0` have identical
service-time values because the generator-level beta-collar widening changes
the local rematch/shift geometry and finite-bundle optics without changing the
underlying `U_packet` schedule or the centerline `B` profile used by this
ledger. That is favorable: the collar fix removes the dense caustic-like
collapse classification without charging a service-time penalty in the current
schedule.

The result should be documented as operational superluminal rating evidence,
not as a physical superluminality theorem. The remaining interpretive step is
to connect this rating to explicit exterior endpoint conventions in the
technical disclosure: prepared standing plant can be accounted separately, while
request-triggered setup time belongs in the service clock. Longer-baseline
claims should use either a regenerated long-service ledger or an explicitly
declared plateau-extension model.

## Decision

Record the current active-rail prescribed schedule as operationally favorable
under the first service-time advantage ledger. Keep the result separate from
packet timelikeness, dense finite-bundle transport, source-family realization,
and global causal-structure gates. The report-grade wording should say that
the current beta-collar lead preserves the service-time advantage rating while
also preserving packet timelikeness, radial escape, and dense bundle-width
recovery in the tested prescribed-metric ledgers.
