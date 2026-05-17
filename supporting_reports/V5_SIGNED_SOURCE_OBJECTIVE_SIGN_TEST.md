# V5 Signed Source-Objective Sign Test

## Question

This is the V5 baseline counterpart to the V10 signed source-objective sign test. Since V5 is the primary target-selection case, this is the main sign diagnostic. The V10 version should be read only as an edge-survival check.

The question is whether positive or negative direct support-shell window amplitude matters when measured against signed source/objective behavior, rather than only absolute routing placement.

## Method

The post-run analyzer is:

`toolkit/adm_harness_cli/scripts/analyze_signed_objective.py`

It compares every V5 sign-paired run against `v5_service_flow_off` and computes:

- absolute burden changes relative to baseline;
- signed opposition or reinforcement of the baseline `delta_j_l` demand;
- packet `delta_j_l`, packet `delta_rho`, and packet peak changes;
- a lower-is-better signed source objective:

```text
global delta_j_l abs burden change
+ 10 * packet delta_j_l abs burden change
+ 1e6 * packet delta_rho abs burden change
+ 0.1 * catch-support delta_j_l abs burden change
+ packet peak-growth penalties
```

This is still a reduced ADM diagnostic. It is not a physical matter-source selection.

## Result

The positive sign is the consistent V5 tie-breaker, but the sign is not decision-grade at the tested amplitudes.

Across all 14 direct-window positive/negative sign pairs, the positive sign wins the signed objective. The largest relative objective gap is only `2.890e-06`.

| family | winner | relative objective gap | positive catch-support opposition | negative catch-support opposition |
|---|---:|---:|---:|---:|
| `window_SIGN_a1em07_lead0p75` | positive | `2.890e-06` | `0.009978` | `-0.009978` |
| `window_SIGN_a1em07_lead0p5` | positive | `2.166e-06` | `0.008074` | `-0.008074` |
| `window_SIGN_a2p5em07_lead0p75` | positive | `1.169e-06` | `0.009978` | `-0.009978` |
| `window_SIGN_a2p5em07_lead0p5` | positive | `8.662e-07` | `0.008074` | `-0.008074` |
| `window_SIGN_a5em07_lead0p75` | positive | `5.846e-07` | `0.009978` | `-0.009978` |

The selected V5 target row:

| run | global `delta_j_l` abs change | catch-support `delta_j_l` abs change | catch-support opposition | packet `delta_j_l` abs change | packet `delta_rho` abs change |
|---|---:|---:|---:|---:|---:|
| `window_pos_a1em07_lead0p75` | `1.230133e-07` | `1.221250e-07` | `0.009978` | `7.494005e-16` | `-2.886688e-17` |

## Interpretation

Positive amplitude is the better default at V5 because it slightly opposes the existing signed catch-support `delta_j_l` demand. Negative amplitude slightly reinforces that signed demand.

But the effect is tiny. Both signs are essentially tied on packet exposure and support-shell routing. Neither sign creates meaningful source relief in the current tiny-control regime; positive only adds slightly less signed-objective cost.

So the V5 design rule is:

**Use positive `+1e-7` as the default target sign, but treat this as a numerical tie-breaker, not a physical source conclusion.**

To make sign a real design decision, the next test needs a load-bearing amplitude ramp or a source-family objective with explicit sign-asymmetric costs.

## Output Files

- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/signed_source_objective_summary.csv`
- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/signed_source_objective_pair_comparison.csv`
- `toolkit/adm_harness_cli/runs/v5_support_shell_screen/signed_source_objective_report.md`
