# V5 Support-shell Ansatz Screen

## Scope

The previous V5 carrying-flow screen showed stable, catch/rematch-localized control, but failed the key infrastructure-routing test: incremental `delta_j_l` remained mostly packet-side rather than support-shell-bearing.

This follow-up screen asks which control ansatz can actually place incremental radial momentum burden into the catch/rematch support shell while keeping packet `delta_rho` and packet incremental `delta_j_l` quiet.

This remains a reduced ADM service-layer diagnostic. It is not a matter-source construction and not a new geometry proof.

## Screen design

Baseline:

```text
v5_service_flow_off
```

Each candidate is compared pointwise against the baseline:

```text
incremental_delta_j_l = run.delta_j_l - baseline.delta_j_l
incremental_delta_rho = run.delta_rho - baseline.delta_rho
```

The screen ranks candidates by:

- total absolute incremental `delta_j_l`,
- catch-support fraction of incremental `delta_j_l`,
- support-shell fraction of incremental `delta_j_l`,
- packet-live fraction of incremental `delta_j_l`,
- packet absolute incremental `delta_rho`.

The generated local harness outputs are:

- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/support_shell_routing_summary.csv`
- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/support_shell_pareto_frontier.csv`
- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/support_shell_routing_report.md`

## Families tested

### 1. Compact support-shell momentum localizer

```text
law: compact_momentum_localizer
scope: catch_rematch_support_shell
amplitude: 0.0005 to 0.004
catch_lead: 0.0, 0.5, 0.75
temporal_width: 0.35, 0.5, 0.75
```

This asks whether the previous momentum-following law can be constrained to the support shell.

### 2. Support-heavy mixed localizer

```text
law: compact_momentum_localizer
scope: catch_rematch_edge_support_mix
packet_exclusion: 1.0
support_shell_gain: 2.0, 5.0, 10.0
```

This asks whether the mixed-window machinery can become support-bearing once packet allocation is erased.

### 3. Direct support-shell window adjustment

```text
law: windowed_adjustment
scope: catch_rematch_support_shell
amplitude: +/- 1e-7 to +/- 1e-5
catch_lead: 0.5, 0.75
```

This asks whether an explicitly support-shell-localized control component can create the desired routing pattern without following the packet-dominated `delta_j_l` signal.

## Main result

The direct support-shell window adjustment is the preferred support-shell-bearing ansatz.

It is the first tested branch that cleanly routes incremental `delta_j_l` into catch-support infrastructure:

```text
catch-support incremental fraction: about 0.9926 to 0.9928
support-shell incremental fraction: about 0.9927 to 0.9928
packet incremental j fraction: about 1e-7 or less for the smallest amplitudes
packet incremental delta_rho: numerical-floor small
```

The compact support-shell localizer is a useful fallback, but it is not as clean:

```text
best compact catch-support fraction: about 0.737
best compact packet incremental j fraction: about 8e-8
```

The support-heavy mixed localizer mostly collapses to the compact support-shell behavior and does not beat it.

## Top candidates

The top ranked candidates were:

| Rank | Run | Global abs incremental `delta_j_l` | Catch-support fraction | Support fraction | Packet `j` fraction | Packet abs incremental `delta_rho` |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `window_neg_a1em07_lead0p75` | 1.230e-07 | 0.992775 | 0.992811 | 1.382e-07 | 5.442e-16 |
| 2 | `window_pos_a1em07_lead0p75` | 1.230e-07 | 0.992775 | 0.992811 | 1.382e-07 | 5.442e-16 |
| 3 | `window_neg_a1em07_lead0p5` | 1.661e-07 | 0.992578 | 0.992680 | 1.024e-07 | 5.442e-16 |
| 4 | `window_pos_a1em07_lead0p5` | 1.661e-07 | 0.992578 | 0.992680 | 1.024e-07 | 5.442e-16 |
| 5 | `window_neg_a2p5em07_lead0p75` | 3.075e-07 | 0.992776 | 0.992812 | 5.529e-08 | 5.442e-16 |
| 6 | `window_pos_a2p5em07_lead0p75` | 3.075e-07 | 0.992776 | 0.992812 | 5.529e-08 | 5.442e-16 |

Positive and negative signs are nearly symmetric at these amplitudes. That means the current screen is identifying a support-localizable control placement, not yet a physically meaningful sign choice.

## Best compact fallback

The best compact support-shell localizer was:

```text
compact_a0p0005_lead0p0_tw0p35
```

Its key metrics:

```text
global abs incremental delta_j_l: 2.051e-07
catch-support incremental fraction: 0.736622
support incremental fraction: 0.740486
packet incremental j fraction: 8.292e-08
packet abs incremental delta_rho: 5.442e-16
```

This is low-burden and packet-quiet, but it does not achieve the clean support-shell routing of the direct window ansatz.

## Design implications

### 1. The old compact localizer failed because it followed the wrong signal

The earlier mixed carrying-flow localizer followed `delta_j_l`, and the dominant `delta_j_l` structure was catch/packet-side. That made the modifier stable but not infrastructure-bearing.

The support-shell screen confirms that the issue is not that support-shell routing is impossible in the harness. It is that the previous law was too signal-following and inherited packet localization from the baseline residual.

### 2. Support-shell routing wants an explicit support-shell component

The successful branch is not subtle:

```text
law: windowed_adjustment
scope: catch_rematch_support_shell
catch_lead: 0.5 to 0.75
amplitude: about 1e-7 to 5e-7
```

This acts more like a prescribed support-shell control layer than a momentum residual localizer. That aligns better with the service architecture: infrastructure carries the prepared control load instead of merely reacting to packet-side residuals.

### 3. Lead 0.75 is slightly preferred for routing purity

At the smallest amplitude, `lead0p75` ranked above `lead0p5`:

```text
window_*_a1em07_lead0p75:
  global incremental delta_j_l: 1.230e-07
  catch-support fraction: 0.992775

window_*_a1em07_lead0p5:
  global incremental delta_j_l: 1.661e-07
  catch-support fraction: 0.992578
```

This suggests that the support shell benefits from being slightly ahead of the packet-side catch/rematch event, consistent with the locked-lead intuition from the broader refreeze work.

### 4. Amplitude should stay tiny until a sign/physics interpretation is added

Increasing direct-window amplitude keeps the routing fraction clean, but total incremental burden rises. Since the sign is currently symmetric and source realism is not modeled, there is no reason to push amplitude yet.

The preferred next branch should start at:

```text
amplitude: 1e-7 to 5e-7
catch_lead: 0.75
scope: catch_rematch_support_shell
law: windowed_adjustment
```

### 5. This is a control placement result, not a source proof

The direct support-shell ansatz shows that the ADM harness can place incremental momentum burden into support-shell infrastructure while keeping packet exposure quiet. It does not show that a physical source can realize that component. It should be described as a support-shell control ansatz candidate.

## Recommended next step

Promote the direct support-shell window adjustment to a focused candidate:

```text
support_shell_window_v1
law: windowed_adjustment
target: carrying_flow
scope: catch_rematch_support_shell
amplitude: +/- 1e-7, +/- 2.5e-7, +/- 5e-7
catch_lead: 0.75
temporal_width: 0.5
```

Then test:

1. Whether the sign matters under a richer source/objective metric.
2. Whether the pattern survives at V=10.
3. Whether adding this component on top of the existing shaped-catch/radial-soft/lapse-cushion branch preserves packet safety.
4. Whether a compact physical source family could generate such a support-shell control layer.

## Bottom line

The previous V5 screen found controllability but not infrastructure routing. This support-shell ansatz screen finds the missing routing mechanism.

Promotable wording:

```text
A direct catch/rematch support-shell window adjustment cleanly routes incremental
radial momentum burden into infrastructure in the V5 reduced ADM harness, with
packet density and packet momentum exposure near numerical floor. This identifies
a preferred support-shell-bearing control ansatz for the next focused branch.
```
