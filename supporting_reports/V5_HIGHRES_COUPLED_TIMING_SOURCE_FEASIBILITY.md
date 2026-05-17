# V5 High-Resolution Coupled Timing Source-Feasibility Report

This report records the V5 high-resolution coupled timing stage for the continuous support-shell metric family. The earlier continuous source-ledger sweep established that a single-channel carrying-flow overlay is packet-safe but source-expensive when pushed to load-bearing amplitude. The next question was whether the same carrying-flow component becomes source-cheaper when its timing is coupled to a clock-lapse partner and then screened at high resolution.

The answer is materially better than the first continuous-overlay result. The coupled timing family remains packet-safe, lowers the additive burden relative to the earlier high-amplitude carrying-flow-only cases, and gives a coherent timing prescription. The present best family is a narrow, slightly later support-shell event with clock-lapse coupling and no rail-stretch by default:

```text
service factor:              V = 5
variant:                     tuned_w0569_eta200
carrying-flow amplitude:      a_beta = +0.5
support-shell catch lead:     1.45 to 1.55
support-shell temporal width: 0.30
clock-lapse ratio:            0.375 to 0.5
rail-stretch ratio:           0.0
```

Rail-stretch remains useful as a secondary peak-shaping comparator, but the high-resolution aggregate ledger favors clock-lapse-only coupling for this stage.

## Runs Used

The main high-resolution sweep was:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_coupled_timing_highres_grid
```

This was an 81-case grid:

```text
catch_leads:          1.15, 1.25, 1.35
temporal_widths:      0.30, 0.35, 0.40
clock_lapse_ratios:   0.25, 0.375, 0.5
rail_stretch_ratios:  0.0, 0.25, 0.5
grid:                 ns = 53, nl = 73
failures:             0
```

Two focused confirmation slices were also run:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_coupled_timing_highres_width_slice
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_coupled_timing_highres_lead_edge_slice
```

The width slice confirmed that `temporal_width = 0.30` is cleaner than `0.35` and `0.40` at `catch_lead = 1.35`. The lead-edge slice checked `catch_lead = 1.35, 1.45, 1.55` at `temporal_width = 0.30` and found that the best cases are around `1.45` to `1.55`.

## Principal Results

The best aggregate case in the full 81-case grid was:

| catch lead | temporal width | clock ratio | rail ratio | max total burden | radial-null ratio | radial-current ratio | angular-pressure ratio | packet norm drift |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1.35` | `0.30` | `0.5` | `0.0` | `1.053421` | `1.027862` | `1.014999` | `1.053421` | `0.024236` |

The strongest robust-score case in the full grid was:

| catch lead | temporal width | clock ratio | rail ratio | max total burden | radial-null ratio | radial-current ratio | angular-pressure ratio | packet norm drift |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1.35` | `0.30` | `0.375` | `0.0` | `1.054433` | `1.026188` | `1.015207` | `1.054433` | `0.019314` |

The lead-edge confirmation slice improved the timing center:

| catch lead | temporal width | clock ratio | rail ratio | max total burden | radial-null ratio | radial-current ratio | angular-pressure ratio | packet norm drift |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `1.45` | `0.30` | `0.5` | `0.0` | `1.053076` | `1.024110` | `1.013124` | `1.053076` | `0.021838` |
| `1.55` | `0.30` | `0.5` | `0.0` | `1.053086` | `1.021197` | `1.011647` | `1.053086` | `0.019676` |
| `1.55` | `0.30` | `0.375` | `0.0` | `1.054489` | `1.019950` | `1.011789` | `1.054489` | `0.019314` |

The practical interpretation is that the high-resolution ledger likes a narrow support-shell timing window and a later catch/support lead than the earlier `1.25` prototype. The aggregate burden is nearly flat between `lead = 1.45` and `1.55`, while radial-null, radial-current, packet drift, and shell-throat radial-null concentration continue to improve slightly at `1.55`.

## Comparison To Expectations

The result is better than the minimal expectation. The expected outcome was packet survival with modest aggregate improvement from clock-lapse coupling. The high-resolution sweep delivered that and also narrowed the viable timing family. The source ledger is now giving a repeatable design direction with a stable timing preference.

The result also confirms one earlier expectation about rail-stretch. Rail-stretch can lower point peaks, but it tends to raise aggregate burden. In the full grid:

```text
rail_stretch_ratio = 0.0   best max burden: 1.053421
rail_stretch_ratio = 0.25  best max burden: 1.059448
rail_stretch_ratio = 0.5   best max burden: 1.068181
```

Median point peaks improve with rail-stretch, so rail-stretch should remain available for local peak-shaping. The default load-bearing candidate should stay clock-lapse-only until a richer objective shows that peak shaping is worth the aggregate cost.

## Source-Feasibility Implications

The current evidence supports controlled source placement more strongly than source relief. The best high-resolution coupled cases hold packet safety, keep packet-comoving density quiet, reduce radial-null and radial-current penalties relative to the earlier carrying-flow-only path, and preserve a support-infrastructure burden pattern. That is a meaningful improvement over a grid artifact: the support-shell component is behaving like a real metric-side actuator whose timing matters.

The burden is still additive at this stage. The best cases sit around a `5.3%` max total burden increase, with angular pressure setting the maximum channel. Radial-null and radial-current additions are much smaller, roughly `2%` to `3%` and `1%` to `1.5%` in the best lead-edge slice. This is promising because the hard traveler-corridor channels stay quiet. The next feasibility threshold is conversion from controlled source cost into source relief or cleaner source redistribution.

The shell-throat diagnostic remains important. In the best full-grid cases, about `88%` of added radial-current burden still lands in the shell-throat overlap band, and a large fraction of added angular-pressure burden lands there as well. The improved timing reduces the size of the penalty, but the location of the penalty still points to the overlap of the support-shell window with intrinsic support/throat gradients. That makes throat-capacity coupling and mixed-term diagnostics the next natural source-feasibility tests.

## Recommended Current Candidate

For the next V5 source-ledger stage, use the following as the primary candidate:

```text
a_beta = +0.5
catch_lead = 1.55
temporal_width = 0.30
clock_lapse_ratio = 0.375 or 0.5
rail_stretch_ratio = 0.0
```

Use `clock_lapse_ratio = 0.375` when prioritizing packet drift and radial-null shell-throat concentration. Use `clock_lapse_ratio = 0.5` when prioritizing the lowest aggregate burden. The two are close enough that the richer source objective should decide between them.

## Harness Parallelization Plan

The high-resolution sweeps took long enough that the harness should move to staged parallel execution. The natural parallel unit is a single overlay case against a shared baseline grid. The baseline can be computed once in the parent process and passed read-only to workers, or written to a temporary parquet/CSV artifact and loaded by each worker. Each worker computes one overlay case, compares it to the baseline, and returns summary/channel/shell-throat rows.

A minimal process-pool sketch:

```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def run_overlay_spec(spec, base_points_path, grid, variant, service_factor):
    base_points = pd.read_parquet(base_points_path)
    amplitude = spec["amplitude"]
    overlay_case = branch_case(
        variant,
        service_factor,
        support_shell_overlay_enabled=True,
        support_shell_amplitude=amplitude,
        support_shell_catch_lead=spec["catch_lead"],
        support_shell_temporal_width=spec["temporal_width"],
        support_shell_clock_lapse_log_gain=amplitude * spec["clock_lapse_ratio"],
        support_shell_rail_stretch_log_gain=amplitude * spec["rail_stretch_ratio"],
    )
    overlay_points = compute_case(overlay_case, progress=False, **grid)
    summary, channels, shell_throat = _compare_case(base_points, overlay_points, spec)
    return summary, channels, shell_throat

with ProcessPoolExecutor(max_workers=args.jobs) as pool:
    futures = [
        pool.submit(run_overlay_spec, spec, base_points_path, grid, args.variant, args.service_factor)
        for spec in specs
    ]
    for future in as_completed(futures):
        summary, channels, shell_throat = future.result()
        summary_rows.append(summary)
        channel_rows.extend(channels)
        shell_throat_rows.extend(shell_throat)
```

For robustness, the production version should write per-case results as soon as they finish:

```python
case_dir = outdir / "cases" / case_slug(spec)
case_dir.mkdir(parents=True, exist_ok=True)
pd.DataFrame([summary]).to_csv(case_dir / "summary.csv", index=False)
pd.DataFrame(channels).to_csv(case_dir / "channel_deltas.csv", index=False)
pd.DataFrame(shell_throat).to_csv(case_dir / "shell_throat_overlap.csv", index=False)
```

That gives restartability. A failed long sweep should be able to skip completed case directories and resume the missing specs. This also makes it easier to run compact sweeps, focused high-resolution confirmations, and final convergence checks with the same driver.

The CLI should expose:

```text
--jobs N
--resume
--case-output
--fail-fast / --keep-going
```

The default should stay serial or low-parallel for reproducibility on small machines. High-resolution sweeps should use `--jobs` explicitly.

## Throat-Capacity Partner To Add

The next metric partner is throat-capacity:

```text
G_throat(s,l) = G_throat_base(s,l) * exp(kappa_Q * W_shell(s,l))
kappa_Q = a_beta * throat_capacity_ratio
```

In the current notation:

```python
gamma_omega = gamma_omega_base * np.exp(support_shell_throat_capacity_log_gain * W_shell)
support_shell_delta_gamma_omega = gamma_omega - gamma_omega_base
```

CLI additions should mirror the clock-lapse and rail-stretch ratios:

```python
parser.add_argument(
    "--throat-capacity-ratios",
    type=float,
    nargs="+",
    default=[0.0],
    help="Log-gain ratios against the signed carrying-flow amplitude for the support-shell throat-capacity partner.",
)
```

The sweep spec should include:

```python
throat_capacity_log_gain = amplitude * throat_capacity_ratio
overlay_case = branch_case(
    ...,
    support_shell_throat_capacity_log_gain=throat_capacity_log_gain,
)
```

The summary should add:

```python
"support_shell_delta_gamma_omega_abs_max": float(
    overlay_points["support_shell_delta_gamma_omega"].astype(float).abs().max()
)
```

Expected result: if the angular-pressure ceiling is genuinely a missing throat-capacity response, a modest positive or negative throat-capacity partner should lower `abs_pOmega_total_ratio` and reduce the shell-throat angular-pressure concentration. A successful throat-capacity partner should also avoid raising radial-null burden enough to erase the aggregate gain. The first screen should therefore be small:

```text
catch_leads:              1.45, 1.55
temporal_widths:          0.30
clock_lapse_ratios:       0.375, 0.5
rail_stretch_ratios:      0.0
throat_capacity_ratios:  -0.5, -0.25, 0.0, 0.25, 0.5
```

The expected win condition is:

```text
max_total_burden_ratio < 1.053
abs_pOmega_total_ratio < current best angular-pressure ratio
neg_Tkk_radial_total_ratio stays near 1.02
abs_j_l_total_ratio stays near 1.01
packet_norm_live_delta_max_abs stays below the current 0.02 to 0.025 band
shell-throat angular-pressure delta fraction drops materially
```

If throat-capacity worsens radial-null while lowering angular pressure, it should become a peak/local-shaping partner. The default load-bearing partner should remain the clock-lapse family.

## Richer Source Objective

The current ranking uses individual ratios and a provisional robust score. The next source objective should combine aggregate burden, packet safety, point peaks, shell-throat concentration, and channel-specific priorities. It should rank cases by design role and expose the trade space behind the maximum-ratio summary.

A first reusable scoring function could look like:

```python
def source_objective(row):
    aggregate = row["max_total_burden_ratio"] - 1.0
    radial_null = row["neg_Tkk_radial_total_ratio"] - 1.0
    radial_current = row["abs_j_l_total_ratio"] - 1.0
    angular_pressure = row["abs_pOmega_total_ratio"] - 1.0
    packet_drift = row["packet_norm_live_delta_max_abs"]
    point_peak = max(row["max_point_peak_ratio"] - 1.0, 0.0)
    shell_null = max(row["neg_Tkk_radial_shell_throat_weighted_ratio"] - 1.0, 0.0)
    shell_current_fraction = max(row["abs_j_l_shell_throat_delta_fraction"], 0.0)
    shell_angular_fraction = max(row["abs_pOmega_shell_throat_delta_fraction"], 0.0)

    return (
        4.0 * aggregate
        + 2.0 * radial_null
        + 1.5 * radial_current
        + 1.5 * angular_pressure
        + 0.25 * packet_drift
        + 0.5 * point_peak
        + 0.25 * shell_null
        + 0.25 * shell_current_fraction
        + 0.25 * shell_angular_fraction
    )
```

The objective should also report named sub-scores:

```text
aggregate_source_score
packet_safety_score
point_peak_score
shell_throat_score
radial_transport_score
angular_support_score
```

This matters because the preferred candidate can change depending on the design role. For example, `clock=0.5` tends to win aggregate burden, while `clock=0.375` tends to win packet drift and some shell-throat measures. A source objective should make that tradeoff explicit instead of hiding it inside one number.

## Expected Next Findings

The next sweep should identify how much of the remaining `5.3%` aggregate penalty comes from angular/throat-capacity mismatch and how much belongs to the carrying-flow support-shell itself. If throat-capacity lowers angular pressure cleanly, the architecture moves closer to a true coupled source-redistribution family. If throat-capacity trades angular pressure for radial-null burden, the current clock-lapse-only family becomes the clean reduced source-feasibility candidate and the next progress comes from source-family assignment or mixed-term smoothing.

The shell-throat overlap fractions should remain the main warning light. A strong result would lower the size of the burden and reduce the overlap concentration at the same time. A weaker but still useful result would lower total burden while keeping overlap concentration high; that would mean the timing is good but the algebraic mixed layer still needs intrinsic metric-partner refinement.

The practical next stage is therefore:

1. Add parallel sweep execution and resumable per-case outputs.
2. Add throat-capacity as a continuous metric partner.
3. Add the richer source objective and named sub-scores.
4. Run the small throat-capacity screen around `lead = 1.45` to `1.55`, `temporal_width = 0.30`, `clock = 0.375` to `0.5`.
5. Promote the best candidate into convergence and V10 edge checks once V5 source-objective ranking is stable.
