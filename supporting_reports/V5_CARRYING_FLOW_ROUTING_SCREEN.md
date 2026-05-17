# V5 Carrying-flow Routing Screen

## Scope

This screen asks whether the frozen `V = 5` active-rail service has a stable, controllable ADM burden pattern in the carrying-flow/control layer.

The target question was:

```text
Can the extra radial momentum demand, delta_j_l, be concentrated in catch/rematch
and support-shell infrastructure while packet delta_rho stays quiet?
```

This is not a new geometry proposal and not a source-feasibility proof. It is a service-layer routing diagnostic: does the compact carrying-flow modifier move burden into infrastructure, or does it remain packet-side?

## Method

The screen uses `v5_service_flow_off` as the pointwise baseline. For each screened run, the harness computes incremental fields before aggregation:

```text
incremental_delta_j_l   = run.delta_j_l   - baseline.delta_j_l
incremental_delta_rho   = run.delta_rho   - baseline.delta_rho
```

It then scores the absolute incremental `delta_j_l` burden by location:

- global incremental burden,
- catch/rematch fraction,
- support-shell fraction,
- catch-support fraction,
- packet-live fraction,
- packet incremental `delta_rho`.

The generated files are local harness products:

- `toolkit/adm_harness_cli/runs/v5_screen/incremental_routing_summary.csv`
- `toolkit/adm_harness_cli/runs/v5_screen/incremental_routing_report.md`

## Main result

The answer is mixed.

The screen supports a weak positive result:

```text
V5 carrying-flow perturbations are stable, controllable, and keep packet
delta_rho quiet at the tested amplitudes.
```

It does not support the stronger routing claim:

```text
The current compact carrying-flow/control layer does not route the extra
delta_j_l burden into the support shell.
```

Most incremental `delta_j_l` remains catch/rematch-localized, but it is still overwhelmingly packet-region burden rather than support-shell burden.

## Quantitative read

Top routing-penalty cases from the incremental screen:

| Rank | Run | Global abs incremental `delta_j_l` | Catch fraction | Support fraction | Catch-support fraction | Packet `j` fraction | Packet abs incremental `delta_rho` |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | `catch_lead_0p75` | 4.625e-06 | 1.000000 | 1.872e-08 | 6.549e-09 | 0.973761 | 1.867e-08 |
| 2 | `catch_lead_0p5` | 7.836e-06 | 1.000000 | 1.105e-08 | 3.867e-09 | 0.973154 | 2.932e-08 |
| 3 | `catch_lead_0p0` | 2.963e-05 | 0.999921 | 2.919e-09 | 1.020e-09 | 0.969726 | 6.991e-08 |
| 4 | `amp_0p001` | 1.793e-05 | 0.999294 | 4.823e-09 | 1.685e-09 | 0.970078 | 4.772e-08 |
| 5 | `packet_exclusion_0p95` | 3.476e-05 | 0.999469 | 3.207e-09 | 1.577e-09 | 0.973188 | 9.556e-08 |

Interpretation:

- Catch/rematch localization is very strong: many cases put about `99.9%` or more of incremental `delta_j_l` in the catch/rematch stage.
- Support-shell routing is effectively absent: support fractions are only about `1e-9` to `1e-8`.
- Packet `delta_rho` remains quiet in absolute terms.
- Packet `delta_j_l` is not quiet in routing terms: the best-ranked cases still put about `97%` of incremental `delta_j_l` in the packet-live region.

## Best options suggested by this screen

The least disruptive family is positive catch lead:

```text
catch_lead_0p75
catch_lead_0p5
catch_lead_0p0
```

These minimize added incremental `delta_j_l` burden while preserving catch/rematch localization and keeping packet `delta_rho` quiet.

The lowest-amplitude branch is also reasonable:

```text
amp_0p001
```

It is not as quiet as the best catch-lead cases, but it is a low-cost perturbation.

High-amplitude cases are the wrong direction for this objective:

```text
amp_0p008
amp_0p012
```

They add more global and packet-region incremental momentum burden without solving support-shell routing.

## Design implication

The compact momentum localizer is probably the wrong primitive if the goal is infrastructure load bearing. It follows the existing `delta_j_l` signal, and that signal is catch/packet dominated. The modifier therefore stays near the packet-side catch layer.

The next branch should not simply keep tuning this mixed window. It should introduce a support-bearing ansatz, for example:

- a `catch_rematch_support_shell` target window,
- stronger packet-live exclusion built into the modifier,
- a support-shell-only counterflow/control component,
- an objective that directly rewards incremental support-shell routing and penalizes packet-live incremental `delta_j_l`.

The promising starting point is:

```text
low amplitude, positive catch lead, support-shell-only or support-shell-heavy window
```

A concrete next screen should begin near:

```text
amplitude = 0.001 to 0.002
catch_lead = 0.5 to 0.75
scope = catch_rematch_support_shell or a support-dominant mixed scope
packet_exclusion >= 0.95
```

## Bottom line

The V5 service is controllable and packet-density quiet under small carrying-flow perturbations. It is not yet architecturally routed.

Promotable wording:

```text
The V5 carrying-flow screen confirms stable catch/rematch-localized momentum
control with quiet packet density, but it does not yet demonstrate support-shell
load-bearing. The current compact localizer remains packet-side and should be
replaced or supplemented by an explicitly support-bearing control ansatz.
```
