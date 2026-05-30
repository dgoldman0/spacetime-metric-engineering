# White Casimir Stage 4 Synthetic Discrimination Findings

Date: 2026-05-30

Status: `stage4_synthetic_discrimination_complete`

## Summary

Stage 4 adds a synthetic readout-discrimination layer on top of the White
Casimir Stage 3 tensor-scale audit. It is not a new worldline, stress-tensor,
or Casimir-field calculation. It is a compact data-analysis harness that treats
the Stage 3 geometry derivatives as a shell-channel template, mixes that
template with ordinary electromagnetic and material nuisance templates, and
asks whether a geometry-coded measurement schedule can recover the shell
template without producing false positives under EM-only simulations.

The result is useful and sobering. In this synthetic model, the full geometry
schedule has real discriminating power: EM-only false positives are low, and
template recovery becomes strong once the injected shell-channel signal is
roughly comparable to the nuisance background. But the same result does not
change the physical scale conclusion from Stage 3. Stage 3 placed the Casimir
source scale far below Alcubierre demand and far below ordinary material and
EM backgrounds. Stage 4 therefore says that the design method can separate
templates in principle, not that the present White-scale shell signal is
experimentally reachable.

The best current interpretation is:

```text
Geometry-coded modulation is a promising discriminator if a shell-channel
observable exists at useful signal-to-background ratio. The current calibrated
Casimir gravitational/readout scale does not supply that ratio. Stage 4 is
therefore a design and falsification harness, not positive evidence for a
measurable warp-like effect.
```

## Run

The focused Stage 4 run used the completed Stage 3 focused tensor-scale output:

```text
Stage 3 input:
/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_tensor_scale_probe/stage3_focused_20260530

Stage 4 output:
/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_synthetic_discrimination/stage4_focused_20260530
```

The Stage 4 harness read:

```text
tensor/bootstrap_summary.csv
material/material_competitor_summary.csv
readout/readout_coupling_summary.csv
```

It wrote data-heavy outputs as parquet and compact summaries as JSON/CSV:

```text
summary.json
progress.jsonl
latest_status.json
synthetic/schedule_matrix.parquet
synthetic/template_matrix.parquet
synthetic/synthetic_observations.parquet
synthetic/recovery_ledger.parquet
synthetic/false_positive_ledger.parquet
synthetic/template_orthogonality.csv
synthetic/schedule_recommendation.csv
reports/stage4_synthetic_discrimination_readout.md
```

The focused run produced:

```text
synthetic observation rows: 33600
fit rows:                   2800
schedule steps:             12
templates:                  9
EM-only false-positive rate: 0.002857
recovery at max SBR:         0.965
required SBR by gate:        1.0
recommended schedule:        full_schedule
```

## Template Model

The shell template is a geometry-coded derivative pattern. When Stage 3 output
is available, the harness derives the shell vector from the median
finite-difference response in the Stage 3 bootstrap summary. The focused run
used the `source_shell_candidate_signed_integral` channel and consumed 24
Stage 3 shell-channel rows.

The synthetic nuisance basis currently includes:

```text
capacitance_shift
patch_potential
contact_loading
material_response
thermal_drift
vibration_alignment
waveguide_dispersion
readout_circuit_artifact
```

Stage 3 material/readout summaries set nuisance amplitude weights. In the
focused run, the strongest weights came from the material and patch-potential
warnings:

```text
patch_to_casimir_ratio_median:                 2412.7057
casimir_to_material_rest_energy_ratio_median:  2.1858e-27

patch_potential nuisance weight:               3.3827
material_response nuisance weight:             3.3325
contact_loading nuisance weight:               2.0000
capacitance_shift nuisance weight:             1.5000
waveguide_dispersion nuisance weight:          1.5000
```

This is deliberately unfavorable to a fragile shell interpretation. Ordinary
EM and material backgrounds are treated as first-class competitors, not as
afterthoughts.

## Recovery Results

The recovery curve is the heart of the run:

| Simulation family | SBR | Datasets | Recovery | False positive | Median shell z | Median recovered fraction |
|---|---:|---:|---:|---:|---:|---:|
| shell + EM | 0.02 | 200 | 0.000 | 0.000 | 0.040 | 0.717 |
| shell + EM | 0.05 | 200 | 0.010 | 0.000 | 0.110 | 0.791 |
| shell + EM | 0.10 | 200 | 0.010 | 0.000 | 0.302 | 1.081 |
| shell + EM | 0.20 | 200 | 0.075 | 0.000 | 0.629 | 0.985 |
| shell + EM | 0.50 | 200 | 0.340 | 0.000 | 1.515 | 0.992 |
| shell + EM | 1.00 | 200 | 0.855 | 0.000 | 2.935 | 0.968 |
| shell + EM | 2.00 | 200 | 0.965 | 0.000 | 6.449 | 0.976 |
| EM only | all SBR labels | 1400 | 0.000 | 0.002857 | near 0 | 0.000 |

The meaning is simple. The geometry-coded template is recoverable, but it is
not magic. Below SBR 0.5, recovery is weak. Around SBR 1.0, recovery becomes
strong under the current detection rule while false positives remain low. At
SBR 2.0, the template is easy to recover.

That threshold matters because the physical interpretation from Stage 3 is
not close to SBR 1.0. Stage 3 found patch-potential scales above the calibrated
Casimir scale in every material row, with a median patch/Casimir ratio around
2400 in this run's material input. Stage 3 also kept the linearized
metric/timing bound effectively null at laboratory scale. So Stage 4 does not
rescue the physical readout claim. It gives a quantitative target: a real
readout mechanism would need to lift the shell-channel observable to roughly
background-comparable scale, or the schedule will not recover it reliably.

## Orthogonality And Schedule

The full schedule is the recommended schedule. That is a meaningful result.
Reduced schedules became rank-poor and more degenerate:

| Schedule | Steps | Template rank | Max shell/nuisance corr. | Condition number | Score |
|---|---:|---:|---:|---:|---:|
| full_schedule | 12 | 7 / 9 | 0.369 | 5742.65 | 0.570 |
| readout_countermodulated | 7 | 5 / 9 | 0.371 | 4475.29 | 0.206 |
| material_controls | 6 | 4 / 9 | 0.473 | 5223.37 | -0.039 |
| shell_core | 6 | 4 / 9 | 0.740 | 2803.66 | -0.293 |
| offset_controls | 6 | 4 / 9 | 0.907 | 1294.82 | -0.444 |

The shell template is only moderately correlated with any single nuisance
template. Its largest correlation is with the patch-potential template, about
0.369. That is encouraging for discrimination. The more serious degeneracy is
inside the nuisance sector itself. Capacitance, contact loading, waveguide
dispersion, and readout-circuit artifact are strongly intercorrelated. That
means a real experiment would probably need additional controls or external
calibrations to distinguish ordinary readout effects from each other.

The schedule lesson is:

```text
Do not use only shell-looking geometry controls. The best discriminator keeps
shell, readout, material, length, wall, and offset controls in the schedule.
The controls that feel like distractions are what prevent a one-family
nuisance model from impersonating the shell channel.
```

## What The Current Results Indicate

The positive result is methodological. A geometry-coded measurement schedule
can be designed as a lock-in-like discriminator. The modulated variable is
geometry, not voltage or phase. The Stage 3 derivative pattern gives the shell
template; ordinary EM/material models give nuisance templates; synthetic
datasets test whether the shell coefficient is identifiable. In the current
run, the answer is yes when the signal-to-background ratio is high enough.

The negative result is physical. The required SBR from this synthetic harness
is around unity, while the currently calibrated Casimir gravitational/readout
scale is nowhere near ordinary material and EM backgrounds. Unless a future
readout model supplies a non-gravitational coupling with a much larger
observable response, the White sphere-cylinder morphology remains a real
Casimir boundary-shaping result rather than a plausible laboratory transit or
warp-effect readout.

This is a useful place to be. Stage 4 turns a vague objection into a number.
It no longer says only "backgrounds may dominate." It says:

```text
Under the current template model, the shell-coded observable must be of order
the nuisance background for robust recovery. Far below that, the schedule
does not recover it reliably even when the shell template is known.
```

## Why This Was Fast

The focused Stage 4 run completed in about a second because it was a synthetic
data-analysis layer. It did not recompute loop fields or tensor blocks. It
worked from compact Stage 3 summaries and generated synthetic observations in
template space. This was intentional for a first discriminator pass.

That speed is also the main limitation. The present Stage 4 is useful enough
to set direction, but it is still toy-like in several ways:

1. It uses median Stage 3 derivative summaries rather than block-level
   derivative uncertainty.
2. Its nuisance templates are hand-shaped proxies, even though their amplitude
   weights are informed by Stage 3 material/readout summaries.
3. It does not solve capacitance, patch, waveguide, thermal, vibration, or
   readout-circuit response from first-principles geometry models.
4. It scores schedule subsets with a simple linear algebra proxy, not with a
   full experimental design optimizer.
5. It does not yet include a modeled propagation observable such as optical
   phase, current response, electron transport, or detector-chain response.

Those limitations are acceptable for a first pass because the goal was to ask
whether synthetic discrimination is worth formalizing. The answer is yes.

## Plan To Make Stage 4 Less Toy-Like

The next Stage 4 upgrade should stay synthetic, but it should stop relying on
only median templates.

### 1. Use Stage 3 block-level parquet rows

Use:

```text
tensor/stress_channel_points.parquet
tensor/stress_channel_baseline_blocks.parquet
```

Instead of a single median shell vector, draw shell templates from the Stage 3
block distribution. This would propagate finite-difference uncertainty into
synthetic recovery. The outputs should include recovery distributions over
template uncertainty, not just observation noise.

Recommended metrics:

```text
shell-template uncertainty envelope
recovery fraction with template mismatch
false-positive rate with template mismatch
required SBR by percentile, not only median
```

### 2. Replace hand-shaped nuisance templates with geometry calculators

Add deterministic nuisance calculators for each schedule row:

```text
capacitance: coaxial/open-bore capacitance with geometry perturbations
patch potential: surface-area, gap, and capacitance-scaled patch energy
contact loading: readout radius, length, wall, and conductor contact proxy
material response: wall/sphere volume and material-factor response
thermal drift: length, wall, and material expansion proxy
vibration: axial/radial offset sensitivity proxy
waveguide: cutoff/dispersion response from bore/readout geometry
readout circuit: capacitance plus impedance/path-length proxy
```

These models do not need to be final laboratory physics on the first upgrade.
They do need to be geometry-derived instead of hand assigned.

### 3. Expand the schedule design space

The current schedule has 12 abstract steps. The next version should generate
candidate schedules from actual geometry moves:

```text
sphere diameter ladder
cylinder radius ladder
wall-thickness ladder
cylinder length ladder
readout/bore radius ladder
axial and radial offset dithers
dummy controls: cylinder only, sphere only, large-gap, matched readout path
```

Then rank schedules by:

```text
shell recovery
EM-only false positives
template condition number
shell/nuisance correlation
template uncertainty sensitivity
number of distinct physical controls
cost/complexity proxy
```

### 4. Add adversarial EM-only fitting

The present EM-only simulation samples nuisance coefficients from a random
distribution. A stricter version should let nuisance coefficients search
against the shell template:

```text
worst-case EM-only false positive rate
adversarial nuisance coefficient vector
minimum nuisance distortion needed to mimic shell
```

This is the real stress test. If ordinary EM can imitate the shell signature
with plausible coefficients, the proposed measurement schedule is weak.

### 5. Add modeled observable channels

Stage 4 should remain honest about scale, but it should allow hypothetical
observable models:

```text
source-proxy observable
capacitance observable
phase observable
current/readout observable
thermal drift observable
vibration/alignment observable
```

Each observable model should declare whether it is:

```text
geometry-proxy only
EM/material proxy
transport proxy
metric/timing scale bound
```

This preserves the claim ladder and prevents a synthetic readout result from
being mistaken for a warp-source result.

### 6. Make reports compare runs

Stage 4 should gain a small report generator that compares:

```text
median-template run
block-bootstrap run
geometry-derived nuisance run
adversarial EM-only run
```

The final decision metric should be a table like:

| Run class | Required SBR | EM-only false positive | Template uncertainty penalty | Recommended schedule | Interpretation |
|---|---:|---:|---:|---|---|
| median template | ... | ... | ... | ... | design smoke |
| block bootstrap | ... | ... | ... | ... | uncertainty-aware |
| geometry nuisance | ... | ... | ... | ... | physics-informed |
| adversarial EM-only | ... | ... | ... | ... | strict falsification |

## Engineering Notes

The Stage 4 implementation also added stronger Stage 3 heartbeat data. The
Stage 3 tensor harness now writes worker heartbeat rows during long tensor
tasks:

```text
tensor_task_started
tensor_task_baseline_complete
tensor_task_parameter_started
tensor_task_parameter_plus_complete
tensor_task_parameter_minus_complete
tensor_task_parameter_complete
tensor_task_readout_accounting_complete
tensor_task_finished
```

This matters because Stage 3 tensor blocks can take tens of minutes. The old
heartbeat moved mostly at block boundaries. The new heartbeat reports progress
inside a block, including which perturbation is being evaluated.

## Bottom Line

Stage 4 is worth keeping because it gives the White Casimir program a real
experimental-design language. It asks whether geometry modulation can separate
a shell-coded response from ordinary backgrounds. The first answer is:

```text
yes in principle, if SBR is near unity;
no evidence that the present calibrated Casimir shell supplies such an SBR;
full schedules are necessary because reduced schedules become degenerate;
ordinary EM/material competitors remain the controlling experimental problem.
```

That is a good result. It is not a sensational result, which is exactly why it
is valuable. It tells us what would have to be true for a laboratory test to
have discriminating power, and it gives a concrete plan for making the next
synthetic run more realistic.

## Artifacts

Implementation:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/
  white_casimir_audit/synthetic_discrimination.py
  scripts/run_stage4_synthetic_discrimination.sh
  tests/test_synthetic_discrimination.py
```

Stage 3 heartbeat update:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/
  white_casimir_audit/tensor_scale_harness.py
  tests/test_tensor_scale_harness.py
```

Verification:

```text
PYTHONPATH=white_casimir_intersection/experiments/white_casimir_source_function_audit \
python -m pytest white_casimir_intersection/experiments/white_casimir_source_function_audit/tests

16 passed
```
