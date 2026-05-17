# Stage I-A V5 Throat-Capacity Source-Placement Screen

## Purpose

This screen tested whether the remaining V5 angular-pressure and shell-throat ceiling in the coupled support-shell family could be improved by adding a throat-capacity partner. The current best V5 family already uses a positive support-shell carrying-flow overlay with a clock-lapse partner. The question here was narrower: does coupling the same support-shell window into `gamma_omega` clean up the demanded angular/throat source channel without moving cost into radial-null, radial-current, packet, or point-peak channels?

This is a demanded-source placement test only. It recomputes the source ledger implied by the metric through `G_munu[g] / 8pi`; it does not construct a physical matter source.

## Runs Used

The report uses existing high-resolution sweep outputs already present in the repository:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_throat_capacity/
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_throat_capacity_fine/
```

Repository commit at review time:

```text
f8bb7fe
```

Both runs used the same V5 support-shell family:

```text
variant:                 tuned_w0569_eta200
service factor:          V = 5
grid:                    ns = 53, nl = 73
support-shell amplitude: +0.5
sign:                    pos
catch leads:             1.45, 1.55
temporal width:          0.30
clock-lapse ratios:      0.375, 0.5
rail-stretch ratio:      0.0
packet exclusion:        1.0
support-shell band:      0.65 Rth to 1.20 Rth
failures:                0 in both sweeps
```

The broad run scanned:

```text
throat_capacity_ratios: -0.5, -0.25, 0.0, 0.25, 0.5
```

The fine run scanned:

```text
throat_capacity_ratios: -0.1, -0.05, 0.0, 0.05, 0.1
```

## Result

Throat-capacity coupling did not become the missing default load-bearing partner. The objective ranking continues to prefer `throat_capacity_ratio = 0.0`, meaning the best current V5 candidate remains the clock-lapse-only support-shell family.

The important nuance is that small negative throat-capacity coupling can improve selected readouts. For example, at `lead = 1.55`, `clock_lapse_ratio = 0.375`, and `throat_capacity_ratio = -0.05`, the radial-null total ratio improves from `1.019950` to `1.012090`. But that improvement is not free: radial-current cost rises from `1.011789` to `1.020490`, and the worst point-peak ratio jumps from `1.182934` to `1.762021`. The richer source objective therefore rejects it as a default candidate.

Positive throat-capacity coupling is worse as a load-bearing direction. Even the small `+0.05` fine-sweep cases move the max total/radial-null burden toward the `1.079` to `1.080` band and push point peaks above `2.68x`. The broader `+0.25` and larger cases are substantially worse.

Packet safety stayed intact across the scanned cases:

```text
positive_packet_norm_live = 0
packet_norm_live_delta_max_abs stayed in the existing clock-lapse band
```

That means the failure mode is not packet causality. The failure mode is source placement: the throat-capacity partner trades angular/throat shaping against radial-null/current and point-peak penalties too aggressively.

## Top Fine-Sweep Cases

These are the top five cases in `source_overlay_sweep_v5_throat_capacity_fine/source_overlay_sweep_objective_ranking.csv`.

| catch lead | clock ratio | throat-capacity ratio | objective | max total ratio | radial-null ratio | angular-pressure ratio | radial-current ratio | packet drift | max point peak |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.55 | 0.375 | 0.00 | 1.097425 | 1.054489 | 1.019950 | 1.054489 | 1.011789 | 0.019314 | 1.182934 |
| 1.55 | 0.500 | 0.00 | 1.110917 | 1.053086 | 1.021197 | 1.053086 | 1.011647 | 0.019676 | 1.192215 |
| 1.45 | 0.375 | 0.00 | 1.118764 | 1.054435 | 1.022678 | 1.054435 | 1.013294 | 0.019314 | 1.182934 |
| 1.45 | 0.500 | 0.00 | 1.134288 | 1.053076 | 1.024110 | 1.053076 | 1.013124 | 0.021838 | 1.192215 |
| 1.55 | 0.375 | -0.05 | 1.440003 | 1.054104 | 1.012090 | 1.054104 | 1.020490 | 0.019314 | 1.762021 |

## Interpretation

The angular/throat-capacity sector is indeed coupled to the remaining ceiling, but the simple support-shell `gamma_omega` partner is not clean enough in this timing/radial band. It does not lower the angular-pressure ceiling enough to compensate for the new radial-null/current and point-peak penalties.

This result is still useful. It says the next source-placement work should not keep pushing a single co-located throat-capacity factor as though it were the natural missing actuator. If throat-capacity is used later, it should probably be treated as a local/peak-shaping or differently timed partner, not as the default V5 load-bearing component.

## Selected Stage I Candidate

Pass the following clock-lapse-only case to the packet-worldtube report:

```text
variant:                  tuned_w0569_eta200
service factor:           V = 5
support-shell amplitude:  +0.5
sign:                     pos
catch lead:               1.55
temporal width:           0.30
clock-lapse ratio:        0.375
clock-lapse log gain:     0.1875
rail-stretch ratio:       0.0
throat-capacity ratio:    0.0
throat-capacity log gain: 0.0
```

Use the `clock_lapse_ratio = 0.5`, `throat_capacity_ratio = 0.0` case as the aggregate-burden comparator if needed. It has a slightly lower max total burden, but the selected `0.375` case has the better source objective, lower point peak, lower radial-null ratio, and comparable packet drift.

## Stage I-A Decision

Stage I-A is complete. The V5 throat-capacity screen does not improve the selected architecture. The project should proceed to Stage I-B using the clock-lapse-only candidate and ask the more important architecture question: whether the live packet worldtube actually overlaps the hard support-source burden.
