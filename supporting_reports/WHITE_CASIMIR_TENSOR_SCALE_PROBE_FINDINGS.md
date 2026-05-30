# White Casimir Tensor-Scale Probe Findings

Date: 2026-05-30

Status: `stage3_tensor_scale_probe_complete`

## Summary

The focused tensor-scale probe completes the second White/Casimir audit
question. The first question was scalar morphology: whether White et al.'s
sphere-cylinder geometry produces a coherent near-shell interaction rather
than a diffuse apparatus-wide negative field. The final scalar fidelity probe
answered that question positively inside the local v-loop proxy. This run asks
the next question: whether that morphology carries stable source-channel
behavior, physical scale, material robustness, and readout-path relevance.

The result is sharply divided by claim type. The run supports White's narrow
Alcubierre-shell interpretation in the morphology/source-placement sense. The
proxy is strongly concentrated in the declared source-shell role, not in the
central readout path, far field, or ordinary electromagnetic competitor region.
That is favorable to White against the simplest artifact objection: the
structure is not primarily a readout-axis bookkeeping artifact.

The same run does not support a warp-functional source claim at physical scale.
After calibration to analytic parallel-plate Casimir brackets, the best
source-demand ratio is about `1.02e-39`, and the largest linearized timing
bound is about `7.81e-76 s`. Those numbers are not close to an Alcubierre
metric-source requirement in this harness. They turn the strong interpretation
into a scale problem: the geometry can organize a shell-like source proxy, but
the calibrated magnitude is far below a warp-source demand.

The readout conclusion is also split. Lack of source proxy in the readout
channel is good for the shell-morphology claim, because it means the source
proxy is not mostly living where the measurement path was declared. It is not,
by itself, a full statement about White's proposed optical/electron/current
measurement. A real propagation observable would need a separate material,
finite-conductivity, phase-response, detector, and ordinary-EM model. This run
only says that the finite-difference source proxy is not behaving as a
readout-channel source.

## Claim Ladder Read

| claim layer | current read | interpretation |
| --- | --- | --- |
| Scalar sphere-cylinder morphology | Supported by prior final fidelity probe | White's geometry has a stable near-shell scalar interaction in the local pair-resolved v-loop proxy. |
| Source-shell placement | Supported by this run | The finite-difference source proxy is overwhelmingly shell-localized across wall thicknesses and scale windows. |
| Readout-artifact objection | Weakened | The source proxy is not primarily in the transit/readout channel, ordinary-EM competitor region, or far-field control. |
| Operational readout/transit effect | Not established | This harness does not model a full current, photon, or electron propagation experiment. |
| Warp-functional source scale | Provisionally negative | The calibrated source-demand ratios and metric/timing bounds are many orders below Alcubierre source requirements. |
| Material and ordinary-EM cleanliness | Cautionary | Material rest energy, patch potential energy, contact loading, and waveguide scale dominate or warn in the current proxy. |

This separation is the important narrative result. White receives support for
the existence of a real shell-like Casimir morphology in the audit's source
role map. White does not receive support here for an operational warp shell or
a transit-time effect at physically consequential scale.

## Run Scope

The completed run was:

```text
run id: stage3_focused_20260530
stage: stage3_tensor_scale_probe
git commit: b1c0606
workers: 4
elapsed: 6744.7 s
tensor blocks: 48
stress-channel rows: 4032
source-demand rows: 1536
material rows: 576
proxy boundary: finite_difference_stress_channel_proxy_not_worldline_stress_tensor
```

Core configuration:

```text
grid: 73 x 73 over +/- 2.5 um
loop blocks: 12
loops per block: 32
points per loop: 256
scale windows: 0.75-1.50 um and 1.50-2.75 um
wall thicknesses: 0.2 um and 0.4 um
sphere diameter: 1.0 um
cylinder diameter: 4.0 um
cylinder length: 8.0 um
finite-difference step: 0.025 um
readout accounting radius: 0.05 um
material factors: 1.0, 0.5, 0.1, 0.01
calibration gaps: 0.75, 1.00, 1.25, 1.50, 2.00, 2.75 um
```

The run is intentionally a focused local audit, not a production White
worldline stress-energy reconstruction. It uses common-random-number
finite-difference source-channel proxies and calibration brackets against
analytic parallel-plate Casimir scales. The output is therefore a disciplined
source-function proxy read, not a full stress tensor.

## Calibration

Calibration passed the expected gap-ordering check across both scale windows
and both calibration families:

```text
calibration gap ordering all pass: true
calibration families: ideal_em, scalar_dirichlet
scale windows: mid_0p75_1p50, upper_1p50_2p75
```

The calibration is useful as an explicit SI bridge, not as a precision
worldline normalization. The mid window is strongest at smaller gaps and
becomes sparse at the widest gap; the upper window remains nonzero across the
full calibration range. This is exactly the fidelity boundary expected from a
local loop-block proxy: the gap ordering is robust, while absolute amplitude
and wide-gap occupancy remain bracketed.

Aggregate calibration brackets:

| scale window | family | proxy mean median range | alpha energy median range | gap ordering |
| --- | --- | ---: | ---: | --- |
| `mid_0p75_1p50` | `ideal_em` | `-3.216498` to `0.000000` | `3.33e-4` to `7.46e-3` | pass |
| `mid_0p75_1p50` | `scalar_dirichlet` | `-3.216498` to `0.000000` | `1.66e-4` to `3.73e-3` | pass |
| `upper_1p50_2p75` | `ideal_em` | `-0.546288` to `-0.016825` | `3.19e-4` to `2.51e-3` | pass |
| `upper_1p50_2p75` | `scalar_dirichlet` | `-0.546288` to `-0.016825` | `1.59e-4` to `1.25e-3` | pass |

The calibration noise affects amplitude claims most strongly. It does not
erase the role-accounting result, because the shell/readout split is large and
stable across independent tensor blocks.

## Source-Role Accounting

The primary source-channel result is the role fraction table. The source proxy
is concentrated in the source-shell candidate in every baseline group.

| wall um | scale window | source-shell fraction | readout fraction | ordinary-EM region fraction | stress-body fraction | boundary fraction | far-field leakage |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.2` | `mid_0p75_1p50` | `0.995759` | `0.000231` | `0.000679` | `0.004074` | `0.000448` | `0.000000` |
| `0.4` | `mid_0p75_1p50` | `0.992679` | `0.000340` | `0.001962` | `0.007203` | `0.001623` | `0.000000` |
| `0.2` | `upper_1p50_2p75` | `0.938713` | `0.009849` | `0.019400` | `0.050144` | `0.009550` | `0.003941` |
| `0.4` | `upper_1p50_2p75` | `0.932350` | `0.011070` | `0.031461` | `0.057991` | `0.020390` | `0.000807` |

The mid window is the clean source-shell read. It is almost entirely shell
localized, with readout and far-field channels essentially absent. The upper
window is broader and admits more stress-body, boundary, and ordinary-EM
competitor fraction, but it remains strongly shell dominated.

This matters for the White interpretation. A readout-centered proxy would have
weakened the shell claim by making the result look like a measurement-channel
or apparatus-role artifact. The observed pattern does the opposite: it keeps
the source proxy in the shell role that the Alcubierre comparison cares about.

## Finite-Difference Channel Structure

The finite-difference channels identify which geometry controls move the proxy
source most strongly. Two parameters dominate the source-shell channel:
cylinder inner radius and sphere diameter. Cylinder length is essentially
null at this scale, and readout-accounting-radius perturbations mainly affect
the readout accounting channel in the upper window, not the source shell.

Representative signed source-channel medians per micrometer:

| wall um | scale window | cylinder radius shell | sphere diameter shell | axial offset shell | radial offset shell | readout-radius shell |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `0.2` | `mid_0p75_1p50` | `541.771646` | `-345.018369` | `2.005895` | `2.583515` | `0.000000` |
| `0.4` | `mid_0p75_1p50` | `739.543130` | `-492.059826` | `-0.116441` | `20.023276` | `0.000000` |
| `0.2` | `upper_1p50_2p75` | `366.475146` | `-314.090824` | `-0.604325` | `-0.988001` | `0.000000` |
| `0.4` | `upper_1p50_2p75` | `386.855389` | `-340.640621` | `-0.694625` | `-0.656564` | `0.000000` |

Representative readout-channel medians per micrometer:

| wall um | scale window | cylinder radius readout | sphere diameter readout | readout-radius readout |
| ---: | --- | ---: | ---: | ---: |
| `0.2` | `mid_0p75_1p50` | `0.000000` | `0.000000` | `0.000000` |
| `0.4` | `mid_0p75_1p50` | `0.000000` | `0.000000` | `0.000000` |
| `0.2` | `upper_1p50_2p75` | `7.172467` | `-2.149219` | `-110.413035` |
| `0.4` | `upper_1p50_2p75` | `12.933255` | `-2.750227` | `-151.567947` |

This is a useful mechanical read. The source-shell proxy responds to the
actual sphere-cylinder boundary geometry. The readout-radius perturbation does
not create a hidden source-shell response; it mostly changes what the readout
mask accounts for in the broader upper window. That again supports the
interpretation that the shell result is geometry anchored, not readout-axis
anchored.

## Readout Coupling

The readout summary gives the clearest resolution of the earlier ambiguity
around "coupling." There are two distinct meanings:

1. Source proxy living in the readout path. That would be bad for White's
   shell-morphology interpretation, because it would suggest a readout
   artifact.
2. A later physical measurement coupling, such as optical phase, electron
   propagation, or current timing response caused by the shell. That is a
   separate propagation problem and is not fully modeled here.

This run tests the first meaning directly and finds little to none of it.

| calibration family | scale window | readout source fraction | shell channel fraction | shell/readout ratio | far-field leakage | calibrated readout energy |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `ideal_em` | `mid_0p75_1p50` | `0.000000` | `0.996502` | `inf` | `0.000000` | `0.0 J` |
| `scalar_dirichlet` | `mid_0p75_1p50` | `0.000000` | `0.996502` | `inf` | `0.000000` | `0.0 J` |
| `ideal_em` | `upper_1p50_2p75` | `0.010449` | `0.934467` | `89.434661` | `0.001950` | `-9.98e-25 J` |
| `scalar_dirichlet` | `upper_1p50_2p75` | `0.010449` | `0.934467` | `89.434661` | `0.001950` | `-4.99e-25 J` |

The mid window has no calibrated readout coupling in this accounting. The
upper window has a small readout fraction, but the shell channel is still
about `89x` larger than the readout channel by the median summary.

The correct interpretation is therefore not "White's readout experiment is
disproved." The correct interpretation is narrower and stronger: the source
proxy does not look like a readout-path artifact. A full White-style
measurement claim still needs a propagation and material-response model.

## Source-Demand Scale

The scale comparison is the strongest negative result for the warp-functional
interpretation. The best source-demand ratio in the full table is:

```text
max source_demand_ratio: 1.0192005703064743e-39
case: ideal_em, mid_0p75_1p50, material factor 1.0,
      target delta 2.0 um, speed parameter 1e-9
```

By target size and speed, the best ratios are:

| target delta um | speed parameter | max source-demand ratio |
| ---: | ---: | ---: |
| `0.75` | `1e-9` | `1.43e-40` |
| `1.00` | `1e-9` | `2.55e-40` |
| `1.50` | `1e-9` | `5.73e-40` |
| `2.00` | `1e-9` | `1.02e-39` |
| `0.75` | `1e-6` | `1.43e-46` |
| `1.00` | `1e-6` | `2.55e-46` |
| `1.50` | `1e-6` | `5.73e-46` |
| `2.00` | `1e-6` | `1.02e-45` |
| `0.75` | `1e-3` | `1.43e-52` |
| `1.00` | `1e-3` | `2.55e-52` |
| `1.50` | `1e-3` | `5.73e-52` |
| `2.00` | `1e-3` | `1.02e-51` |
| `0.75` | `1` | `1.43e-58` |
| `1.00` | `1` | `2.55e-58` |
| `1.50` | `1` | `5.73e-58` |
| `2.00` | `1` | `1.02e-57` |

The ratios are small enough that the conclusion is not sensitive to ordinary
rounding or presentation. Within this calibrated proxy, the White geometry is
not close to supplying an Alcubierre source demand. This is the cleanest
provisional negative statement in the run.

## Linearized Metric Bound

The linearized metric bound is labeled as a scale bound, not a transport
prediction. It is still useful because it prevents the morphology from being
overstated.

Aggregate absolute ranges:

```text
integrated shell energy:       5.24e-25 J to 2.35e-21 J
readout coupled energy:        0.00e+00 J to 1.42e-23 J
gravitational radius:          0.00e+00 m to 2.34e-67 m
fractional path scale:         0.00e+00 to 2.93e-62
timing bound:                  0.00e+00 s to 7.81e-76 s
```

The largest timing bound appears in the upper window with ideal EM
normalization and material factor `1.0`. It is still about `7.81e-76 s`.
That value is not an operational measurement scale. It is a reminder that
source-shell morphology and warp-functional magnitude are different claim
levels.

## Material and Ordinary-EM Competition

The material/ordinary-EM table is cautionary across the board:

```text
casimir/material rest-energy ratio:
  min    1.06e-29
  median 2.19e-27
  max    3.95e-25

patch/Casimir energy ratio:
  min    2.57
  median 2.41e3
  max    1.15e6

patch potential flags:      576 / 576
contact loading warnings:   576 / 576
waveguide cutoff scale:     1.76e15 Hz
```

Even the best current Casimir/material rest-energy ratio is extremely small.
Patch-potential energy is also large relative to the calibrated Casimir energy
in every row, with the most favorable row still above `2.5x`. This does not
erase the shell morphology. It says that a real measurement interpretation
must treat materials and ordinary electromagnetic backgrounds as first-class
physics, not as afterthoughts.

## Noise and Fidelity Boundary

The run's main noise source is the simplified local proxy, not system
resource pressure. The computation completed cleanly with stable memory and
disk headroom. The numerical limitations are physics/fidelity limitations:
finite loop-block count, finite grid resolution, scale-window sparsity at wide
gaps, and a finite-difference stress-channel proxy rather than a full
worldline stress tensor.

Common random numbers make the finite-difference role comparison more
informative than the absolute amplitude. That is why the role result is
stronger than the SI normalization result. The shell/readout split is a large,
repeatable role-accounting pattern. The physical magnitude remains a
calibrated bracket.

The next fidelity step, if this branch is pursued, is not merely more local
loop count. The next meaningful step is a deeper physics model:

- full worldline stress-energy or validated tensor reconstruction;
- finite-conductivity and material-response treatment;
- explicit optical/electron/current propagation through the proposed readout;
- patch-potential, contact, waveguide, and alignment competitor modeling;
- independent convergence checks on the source-demand and readout tables.

## Interpretation

The strongest positive interpretation is:

```text
White et al.'s sphere-cylinder geometry continues to look like a real
shell-localized Casimir-shaping morphology in this audit. The tensor-scale
source proxy remains concentrated in the declared source-shell role, and it
does not collapse into the readout path, ordinary-EM competitor region, or far
field.
```

The strongest negative interpretation is:

```text
The calibrated source scale is far below Alcubierre source demand, and the
linearized metric/readout bounds are effectively null at operational scale in
this harness. The result does not support an operational warp shell.
```

Those statements are compatible. The audit supports the White/Alcubierre
analogy as a morphology/source-placement observation. It does not promote that
analogy into a physically consequential warp-source or transport claim.

## Artifacts

Run directory:

```text
/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_tensor_scale_probe/stage3_focused_20260530
```

Primary outputs:

```text
manifest.json
summary.json
calibration/calibration_summary.csv
tensor/stress_channel_summary.csv
tensor/bootstrap_summary.csv
tensor/stress_channel_baseline_blocks.parquet
tensor/stress_channel_points.parquet
scale/source_demand_ratio.csv
scale/linearized_metric_bound.csv
material/material_competitor_summary.csv
readout/readout_coupling_summary.csv
progress.jsonl
latest_status.json
reports/second_question_machine_readout.md
```

Committed harness:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/white_casimir_audit/tensor_scale_harness.py
white_casimir_intersection/experiments/white_casimir_source_function_audit/white_casimir_audit/stress_tensor_proxy.py
white_casimir_intersection/experiments/white_casimir_source_function_audit/white_casimir_audit/linearized_metric.py
white_casimir_intersection/experiments/white_casimir_source_function_audit/white_casimir_audit/em_proxy.py
white_casimir_intersection/experiments/white_casimir_source_function_audit/white_casimir_audit/alcubierre_target.py
white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage3_tensor_scale_probe.sh
white_casimir_intersection/experiments/white_casimir_source_function_audit/tests/test_tensor_scale_harness.py
```

Verification before the full run:

```text
PYTHONPATH=white_casimir_intersection/experiments/white_casimir_source_function_audit \
python -m pytest white_casimir_intersection/experiments/white_casimir_source_function_audit/tests

14 passed
```
