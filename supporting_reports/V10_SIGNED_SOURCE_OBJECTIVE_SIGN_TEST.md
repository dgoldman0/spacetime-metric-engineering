# V10 Signed Source-Objective Sign Test

## Question

The V5 and V10 support-shell screens used mostly absolute incremental routing metrics. Those metrics are good for asking whether a control increment lands in the support shell, but they mostly hide sign. This follow-up asks whether the direct support-shell window sign matters when judged against a richer source/objective metric.

## Method

The post-run analyzer is:

`toolkit/adm_harness_cli/scripts/analyze_signed_objective.py`

It compares every V10 sign-paired run against `v10_service_flow_off` and computes:

- absolute burden changes relative to baseline, not just absolute incremental burden;
- signed baseline opposition/alignment, where positive opposition means the increment locally cancels the baseline `delta_j_l` sign;
- packet `delta_j_l`, packet `delta_rho`, and packet peak changes;
- a lower-is-better signed source objective:

```text
global delta_j_l abs burden change
+ 10 * packet delta_j_l abs burden change
+ 1e6 * packet delta_rho abs burden change
+ 0.1 * catch-support delta_j_l abs burden change
+ packet peak-growth penalties
```

This is still an ADM reduced-source diagnostic. It is not a matter-source proof, and it does not include a full `Tkk`/`p_l` source-family realization.

## Result

Sign is detectable, but not decision-grade at the tested amplitudes.

Across all 16 positive/negative sign pairs, the positive sign wins the signed objective. However, the largest relative objective gap is only `1.53e-5`, far below a practical design-selection threshold.

| family | winner | relative objective gap | positive catch-support opposition | negative catch-support opposition |
|---|---:|---:|---:|---:|
| `tw_SIGN_0p25` | positive | `1.526e-05` | `0.022052` | `-0.022052` |
| `tw_SIGN_0p35` | positive | `9.080e-06` | `0.015414` | `-0.015414` |
| `lead_SIGN_1p25` | positive | `8.757e-06` | `0.014773` | `-0.014773` |
| `amp_SIGN_5em08` | positive | `8.046e-06` | `0.010307` | `-0.010307` |
| `amp_SIGN_1em07` | positive | `5.555e-06` | `0.010307` | `-0.010307` |

The promoted target behaves like the positive-sign member of the `1e-7`, lead-`0.75`, width-`0.5` family:

| run | global `delta_j_l` abs change | catch-support `delta_j_l` abs change | catch-support opposition | packet `delta_j_l` abs change | packet `delta_rho` abs change |
|---|---:|---:|---:|---:|---:|
| `v10_support_shell_window_target` | `1.230130e-07` | `1.221250e-07` | `0.010307` | `8.604228e-16` | `4.404571e-18` |

## Interpretation

The positive sign is the better placeholder. It very slightly opposes the existing signed catch-support `delta_j_l` demand, while the negative sign very slightly reinforces it.

But neither sign produces real burden relief in this tiny-control regime. Both signs increase absolute global and catch-support `delta_j_l` burden; the positive sign just increases it slightly less. Packet exposure remains essentially unchanged for both signs.

So the practical conclusion is:

**Use the positive sign as the default tie-breaker, but do not treat the sign as physically selected yet.**

For the sign to become a real design decision, the next test needs either:

- a load-bearing amplitude ramp where the support-shell window is large enough to create measurable cancellation or failure asymmetry; or
- a source-family objective with explicit sign-asymmetric costs, such as a concrete preference over positive/negative source components in the support shell.

## Output Files

- `toolkit/adm_harness_cli/runs/v10_support_shell_edge/signed_source_objective_summary.csv`
- `toolkit/adm_harness_cli/runs/v10_support_shell_edge/signed_source_objective_pair_comparison.csv`
- `toolkit/adm_harness_cli/runs/v10_support_shell_edge/signed_source_objective_report.md`
