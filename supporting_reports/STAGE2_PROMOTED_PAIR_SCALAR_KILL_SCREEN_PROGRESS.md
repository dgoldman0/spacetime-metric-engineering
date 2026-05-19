# Stage II Promoted Pair Scalar Kill-Screen Progress

## Purpose

This is the first narrow Stage II test of the promoted pair:

```text
compact7_wide4_edge160
wide4_radius205
```

The goal was not to optimize a scalar source. The goal was to ask whether a simple Barceló-Visser-like nonminimally coupled scalar profile is immediately killed by sign, placement, packet-contamination, or Planck-scale warnings.

## Run Location

The run was written to the large mounted volume:

```text
/media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs/
```

Candidate ledgers:

```text
stage2_compact_kill_candidate_ledger_61x83/compact7_wide4_edge160/
stage2_radius205_kill_candidate_ledger_61x83/wide4_radius205/
```

Scalar screens:

```text
stage2_scalar_kill_compact_61x83/
stage2_scalar_kill_radius205_61x83/
```

## Candidate Ledgers

Both candidates were regenerated as full source ledgers:

| candidate | rows | grid | live packet points | max live packet norm | positive live packet norm |
| --- | ---: | --- | ---: | ---: | ---: |
| `compact7_wide4_edge160` | 5063 | 61 x 83 | 530 | -22.7000 | 0 |
| `wide4_radius205` | 5063 | 61 x 83 | 530 | -23.2837 | 0 |

So the Stage II input ledgers preserved the Stage I packet-safety condition.

## Scalar Kill Screen

Both scalar screens used the same narrow ansatz set:

```text
profiles:
  standing_support
  compact_handoff
  core_throat
  support_edge
  catch_support

phi0:
  0.05, 0.1, 0.2, 0.5, 1

xi:
  0, 1/6, 0.5, 1
```

Each screen produced:

```text
candidate rows: 100
```

## Best Aggregate Rows

| candidate | profile | phi0 | xi | score | mean residual | mean coverage | live scalar fraction | max abs phi | max grad proxy | warnings |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | `standing_support` | 0.5 | 0 | 0.9565 | 0.9510 | 0.0777 | 0.0109 | 0.5 | 0.2440 | 0 |
| `wide4_radius205` | `standing_support` | 0.05 | 0 | 0.9504 | 0.9492 | 0.0811 | 0.0024 | 0.05 | 0.0235 | 0 |

These are not useful scalar-source fits. The live scalar fractions are low, especially for `wide4_radius205`, but coverage is too small and residuals remain near `0.95`.

## Kill Metric

The radial-null channel is the kill for both candidates.

| candidate | best no-warning `neg_Tkk_radial` coverage | residual | profile | xi | no-warning rows with coverage > 0.05 |
| --- | ---: | ---: | --- | ---: | ---: |
| `compact7_wide4_edge160` | 0.007208 | 0.994207 | `standing_support` | 1.0 | 0 |
| `wide4_radius205` | 0.005061 | 0.996003 | `standing_support` | 1.0 | 0 |

The radius-broadened comparator does not rescue the simple scalar source. It slightly improves aggregate score and lowers live scalar contamination, but it does worse on the main radial-null coverage test.

## Channel Details

Best no-warning channel coverage:

| candidate | `neg_Tkk_radial` | `abs_p_l` | `abs_j_l` | `abs_pOmega` |
| --- | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | 0.0072 | 0.0108 | 0.1505 | 0.2180 |
| `wide4_radius205` | 0.0051 | 0.0068 | 0.1713 | 0.2168 |

The scalar proxy weakly touches the angular/current channels. It does not meaningfully pay the radial-null or radial-pressure bill.

Localized support profiles such as `support_edge` and `core_throat` did not solve this. They generally left aggregate residuals near or above `1.0`, and the best localized rows still had tiny radial-null coverage.

## Interpretation

This is an immediate kill for the tested narrow pure-scalar screen:

```text
simple prescribed scalar profiles do not pay the promoted pair's radial-null bill.
```

This should not be overread as a no-go theorem. It does not rule out:

```text
more structured scalar profiles;
hybrid source assignment;
different source families;
a full scalar-tensor solve rather than this reduced proxy.
```

But it does say the first simple BV-like scalar placement is not promising for either the compact candidate or the radius-broadened comparator.

The active-rail Stage I result survives as a demanded-source architecture. The first Stage II source-family payer fails the main radial-null payment test.

## Miss Mechanism

The scalar miss is mainly a location/timing derivative miss.

Using the best radial-null scalar family from the screen:

```text
profile = standing_support
xi = 1.0
phi0 = 0.1 for inspection
```

the top demanded radial-null rows and the top scalar negative-`Tkk` proxy rows had:

| candidate | top-20 demanded / scalar-supply overlap | scalar supply on top demanded rows |
| --- | ---: | ---: |
| `compact7_wide4_edge160` | 0 / 20 | 0.0 |
| `wide4_radius205` | 0 / 20 | 0.0 |

For `compact7_wide4_edge160`, the demanded radial-null rows are mostly:

```text
entry_precatch / core_throat
catch_rematch / support_edge
```

but the scalar proxy's strongest negative-`Tkk` rows land at:

```text
reset_decompression / outer_quarantine_shell
reset_decompression / support_edge
```

For `wide4_radius205`, the demanded rows are mostly:

```text
entry_precatch / support_edge
entry_precatch / core_throat
catch_rematch / support_edge
```

while the scalar proxy again puts its strongest negative-`Tkk` rows at:

```text
reset_decompression / support_edge
```

So the scalar ansatz is not merely weak. Its negative radial-null contribution is being generated in the wrong part of the service cycle.

## Next Step

Do not widen the scalar search yet. The useful next step is to inspect why the scalar proxy misses the radial-null channel:

```text
compare top demanded radial-null rows against scalar profile support;
check whether the miss is location, sign, derivative order, or normalization;
then decide whether a hybrid source assignment is the right next Stage II branch.
```

That inspection now points to:

```text
location/timing mismatch first;
then inadequate radial-null coverage;
not live-packet contamination as the primary failure.
```

## Fixed-Metric Localized Scalar Solve

A first fixed-metric scalar field solve was then run for:

```text
compact7_wide4_edge160
```

This was not a full metric-backreaction scalar-tensor solve. It optimized a localized scalar basis around the top demanded radial-null rows on the fixed Stage I metric.

Run path, via symlink:

```text
toolkit/adm_harness_cli/runs/stage2_scalar_field_solve_compact_61x83/
```

External target:

```text
/media/kir/9CDCBD3EDCBD140C/Research/active_rail_stage2_runs/stage2_scalar_field_solve_compact_61x83/
```

Progress files:

```text
scalar_field_solve_progress.csv
scalar_field_solve_latest.json
scalar_field_solve_best.json
scalar_field_solve_top_demand_tracking.csv
```

Final metrics:

| metric | value |
| --- | ---: |
| iterations | 80 |
| elapsed | 124.1 s |
| optimizer result | iteration limit |
| radial-null relative residual | 0.999992 |
| radial-null coverage | 0.00000777 |
| scalar live-stress fraction | 0.0000114 |
| max abs phi | 0.1895 |
| max grad proxy | 0.00337 |
| effective coupling margin proxy | 0.0971 |
| mean coverage | 0.0226 |
| mean residual | 0.9839 |

The progress data showed the run was chugging, not choking:

```text
iteration 1  -> loss 1.2981
iteration 40 -> loss 1.2462
iteration 80 -> loss 1.2453
```

But the improvement came mostly from suppressing live scalar stress and trimming secondary residuals. The radial-null coverage remained effectively zero:

```text
iteration 1:  0.0000683
iteration 40: 0.0000080
iteration 80: 0.0000078
```

The top demanded radial-null rows still received no scalar negative-`Tkk` supply. In `scalar_field_solve_top_demand_tracking.csv`, the top demanded rows have:

```text
scalar_neg_Tkk_supply = 0.0
```

even where the optimized `phi` is nonzero.

This means the more flexible localized solve did not rescue the simple scalar-source branch. It reinforced the kill-screen conclusion: on the fixed metric, the scalar proxy does not generate the required negative radial-null support in the demanded entry/catch core-throat/support-edge rows.

## Design Interpretation

This result is not surprising under the composite support-plant interpretation.

The active-rail design was never strongly committed to one matter source paying every bill. The architecture naturally decomposes into:

```text
packet corridor safety;
standing throat/support plant;
catch/rematch infrastructure;
radial-null support;
angular/current handling;
radial-pressure balance.
```

The Stage II scalar result therefore should be read narrowly:

```text
single simple BV-like scalar support is not the radial-null payer for this promoted pair.
```

It should not be read as:

```text
the active-rail source-placement architecture failed.
```

The active-rail Stage I claim still stands in its limited form: the metric branch improves packet/source separation and keeps the worst radial-null and radial-pressure rows out of the live packet. What failed is the first source-family audition, where one scalar profile was asked to supply a multi-channel support plant.

The immediate source-assignment implication is:

```text
scalar field: possible auxiliary/timing/smoothing component;
radial-null support: likely needs a different exotic source channel;
angular/current relief: may be tied to shift/handoff-sector source structure;
radial-pressure balance: likely another infrastructure component.
```

The next useful Stage II artifact is therefore a source-decomposition map, not a wider scalar sweep. It should classify the top demanded rows by channel, region, algebraic signature, live-packet status, and plausible source role before selecting the next matter model.
