# White Casimir Stage 5 Readout-Transduction Handoff

Date: 2026-05-30

Status: `stage5_readout_transduction_ladder_ready_for_build`

## Executive Read

The Stage 3 and Stage 4 result changed the problem. The White sphere-cylinder
geometry still has a real shell-forming Casimir morphology in the audit proxy.
The direct timing/readout interpretation is closed under the current modeled
laboratory backgrounds. Geometry modulation can discriminate a shell-coded
observable once that observable is already near background scale; it supplies
identification, not amplitude.

Stage 5 is therefore a readout-transduction ladder. It should test candidate
laboratory apparatuses that might measure the same shell-shaped boundary
response through a different physical channel. The result can support a
Casimir-boundary morphology claim, a material-response claim, or a metric-like
readout claim depending on what the apparatus actually measures. The code must
make that distinction explicit.

The purpose of Stage 5 is:

```text
Given the Stage 3 shell derivative template and the Stage 4 recovery gate,
which candidate readout channels, if any, can produce a shell-coded observable
with enough amplitude, enough template orthogonality, and enough EM-only
false-positive control to justify a physical test?
```

The most likely outcome is a ranked ledger where most candidate readouts close.
That is useful. The goal is a falsification and design apparatus, not a way to
smooth over the Stage 4 gate.

## Current Evidence To Carry Forward

Primary paper:

```text
white_casimir_intersection/white_casimir_fidelity_probe_paper.tex
white_casimir_intersection/white_casimir_fidelity_probe_paper.pdf
```

Stage 3 focused tensor-scale output:

```text
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_tensor_scale_probe/stage3_focused_20260530
```

Stage 4 refined synthetic discrimination output:

```text
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_synthetic_discrimination/
stage4_block_bootstrap_geometry_sbr_refine_20260530
```

Stage 4 code:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/
  white_casimir_audit/synthetic_discrimination.py
  scripts/run_stage4_synthetic_discrimination.sh
  tests/test_synthetic_discrimination.py
```

Stage 4 uses zstd parquet for heavy data and JSON/CSV for summaries. Stage 5
should keep that contract.

Important current numbers:

```text
Stage 4 required SBR gate:             about 1.2
Stage 4 EM-only false-positive rate:   about 0.034
Stage 4 shell recovery at SBR 1.2:     about 0.845
Stage 4 max shell/nuisance correlation about 0.928
Stage 3 patch/Casimir median ratio:    about 2.4e3
Stage 3 timing/readout scale:          effectively null for direct metric readout
```

Interpretation of those numbers:

```text
The schedule can separate templates at near-background shell amplitude.
The calibrated direct Casimir/metric readout is far below that amplitude.
Stage 5 must search for a real physical transduction channel, or close the
candidate apparatus cleanly.
```

## Stage 5 Claim Ladder

Each candidate readout must be labeled by the strongest claim it can carry.

| Claim class | What it means | Example readout | Allowed conclusion |
|---|---|---|---|
| `casimir_boundary` | Measures boundary-force, boundary-energy, or mode-shift response tied to the sphere-cylinder geometry. | Force gradient, differential pressure, cavity frequency shift. | Shell-shaped Casimir boundary morphology is measurable. |
| `material_response` | Measures conductivity, patch, contact, thermal, or surface response with shell-correlated geometry dependence. | Contact loading, impedance, roughness-sensitive resonator loss. | A material channel follows the geometry schedule. |
| `metric_proxy` | Measures a propagation/timing/current observable with a modeled bridge to metric perturbation. | Central transit timing, photon/electron phase, current path. | Metric-like readout candidate survives only if amplitude and false-positive gates pass. |
| `control` | Known null or calibration channel. | Far-field control, symmetric dummy cavity, EM-only schedule. | Background model calibration. |

The Stage 5 code should refuse ambiguous successes. A force-gradient pass is a
Casimir-boundary pass. A resonator-loss pass is a material/readout pass unless
the transduction model shows a distinct shell-coded boundary observable. A
central timing pass is a metric-proxy pass only after amplitude, nuisance, and
control gates pass together.

## Candidate Readout Ladder

Build the first Stage 5 apparatus ledger with these candidates.

### 1. Direct Central Transit Timing Reference

Purpose: keep the old readout in the ladder as a reference closure.

Observable:

```text
delta_t, phase delay, current shift, or photon/electron transit perturbation
along the central bore/readout path.
```

Expected result: closed unless an explicit propagation model supplies a new
transduction mechanism. This candidate should almost certainly fail amplitude.
It is still useful because it anchors the old interpretation.

Primary gates:

```text
required_gain_to_stage4_gate
readout_path_source_fraction
EM-only false positive
capacitance/readout-circuit degeneracy
```

### 2. Force-Gradient MEMS/NEMS Readout

Purpose: test a direct Casimir-boundary observable.

Observable:

```text
force gradient, spring-frequency shift, or displacement response as the sphere,
cylinder, or a coupled probe element is geometry-modulated.
```

This is a likely first serious physical apparatus because force-gradient
measurements are naturally sensitive to Casimir boundary physics. The claim is
Casimir-boundary morphology, not metric timing.

Primary nuisances:

```text
patch potentials
surface roughness
electrostatic calibration drift
vibration alignment
thermal drift
finite conductivity
```

Useful control geometry:

```text
dummy conductor without sphere
far-field offset
wall-thickness modulation
sphere-diameter modulation
radial/axial offset modulation
```

### 3. Differential Casimir Pressure Geometry

Purpose: make shell-coded pressure differences visible through a differential
mechanical balance or membrane.

Observable:

```text
differential pressure or force between paired sphere-cylinder cells with
opposite shell-gap modulation.
```

This can exploit common-mode rejection. Its success would support a shell-coded
Casimir boundary response. It needs careful patch-potential controls.

Primary nuisances:

```text
patch energy
capacitance shifts
membrane stress drift
surface roughness
temperature gradients
```

### 4. High-Q Microwave Or Optical Cavity Shift

Purpose: test whether the shell-coded boundary morphology shifts an
electromagnetic mode in a measurable way.

Observable:

```text
delta_f / f, mode splitting, Q shift, or phase shift across geometry schedules.
```

This readout may be easier to measure than force if a mode overlaps the
annular shell region strongly and rejects the central path. It can also turn
into a material-response readout if losses dominate.

Primary nuisances:

```text
thermal expansion
finite conductivity
surface roughness
waveguide cutoff
mode-mixing
readout-circuit artifact
mechanical alignment
```

### 5. Superconducting Resonator Boundary Shift

Purpose: explore whether a superconducting cavity/resonator gives a cleaner
frequency or impedance observable.

Observable:

```text
resonator frequency shift, kinetic inductance shift, Q shift, or phase readout
under sphere-cylinder geometry modulation.
```

This candidate can be powerful and dangerous. Superconducting devices have
excellent readout sensitivity, but material, vortex, quasiparticle, and surface
loss effects can impersonate geometry-coded signals. Stage 5 should mark this
candidate as high sensitivity and high nuisance complexity.

### 6. Material/Impedance Readout

Purpose: track ordinary material channels as first-class competitors.

Observable:

```text
impedance, capacitance, contact resistance, surface potential, or loss tangent
under the same geometry schedule.
```

This candidate is mainly a background model and calibration asset. A strong
signal here can explain away other channels.

## Stage 5 Gates

Every candidate must emit a row in `gate_ledger.parquet` with these gates.

| Gate | Field | Passing meaning |
|---|---|---|
| Physics identity | `claim_class` | The observable states what it actually measures. |
| Amplitude | `predicted_sbr`, `required_gain_to_gate` | The predicted shell observable reaches the Stage 4 gate, or the required gain is recorded as an open physical burden. |
| Orthogonality | `max_abs_shell_nuisance_correlation` | The shell template separates from nuisance templates under the schedule. |
| Recovery | `recovery_fraction_at_predicted_sbr` | Synthetic datasets recover the shell coefficient at the candidate's predicted amplitude. |
| False positive | `em_only_false_positive_rate` | EM/material-only synthetic runs stay below the declared threshold. |
| Calibration | `calibration_control_status` | A control apparatus can measure or bound the dominant nuisance. |
| Claim boundary | `allowed_claim` | The result maps to Casimir boundary, material response, metric proxy, or control. |

Suggested first thresholds:

```text
recovery_fraction_at_predicted_sbr >= 0.80
em_only_false_positive_rate <= 0.05
predicted_sbr >= 1.2 or required_gain_to_gate explicitly carried
max_abs_shell_nuisance_correlation <= 0.85 preferred
```

The correlation threshold is a guide, not a law. Stage 4 already saw a hard
geometry-derived nuisance correlation around 0.928, so a candidate with high
correlation can still remain in the ladder if controls or added schedule
dimensions lower false positives.

## Proposed Code Layout

Add Stage 5 as a sibling to Stage 4 inside the existing White Casimir audit
package.

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/
  white_casimir_audit/
    readout_transduction.py
    stage5_readout_ladder.py
    stage5_models.py
    stage5_gates.py
  scripts/
    run_stage5_readout_ladder.sh
  tests/
    test_stage5_readout_ladder.py
```

Keep Stage 4 intact. Stage 5 should import or mirror these Stage 4 concepts:

```text
schedule matrix
template orthogonality
synthetic observation generation
recovery ledger fitting
EM-only false-positive ledger
heartbeat recorder
zstd parquet writers
```

Avoid building Stage 5 as a pile of one-off scripts. Treat readouts as data
objects and models.

## Core Data Model

Use dataclasses with explicit units.

```python
@dataclass(frozen=True)
class ReadoutCandidate:
    candidate_id: str
    claim_class: str
    observable_name: str
    observable_unit: str
    transduction_family: str
    sensitivity_floor: float
    sensitivity_floor_unit: str
    dominant_nuisances: tuple[str, ...]
    control_requirements: tuple[str, ...]

@dataclass(frozen=True)
class TransductionResult:
    candidate_id: str
    schedule_step: str
    schedule_order: int
    shell_observable: float
    background_observable_rms: float
    predicted_sbr: float
    required_gain_to_stage4_gate: float
    claim_class: str

@dataclass(frozen=True)
class Stage5Config:
    preset: str
    run_id: str
    source_stage3_dir: str
    source_stage4_dir: str
    outdir: str
    base_seed: int
    shell_datasets_per_candidate: int
    em_only_datasets_per_candidate: int
    chunk_size: int
    heartbeat_interval_s: float
```

The important design feature is `claim_class`. A candidate can pass as a
Casimir-boundary detector and still fail as a metric-proxy detector. The code
should keep that distinction in every ledger.

## Model Interfaces

Start with analytic and semi-analytic models. Add FEM/BEM/Lifshitz solvers as
later backends behind the same interface.

```python
class ReadoutModel(Protocol):
    candidate: ReadoutCandidate

    def evaluate(
        self,
        schedule: pd.DataFrame,
        stage3_templates: Stage3TemplateBundle,
        material_context: MaterialContext,
    ) -> pd.DataFrame:
        ...
```

Each model should return one row per schedule step:

```text
candidate_id
claim_class
schedule_order
schedule_step
shell_observable
shell_observable_unit
background_observable_rms
predicted_sbr
required_gain_to_stage4_gate
dominant_nuisance
model_status
model_notes
```

For first implementation, use transparent scaling laws:

```text
central_timing:       Stage 3 linearized timing bound and readout fraction
force_gradient:       calibrated shell pressure/energy scale times effective area and gradient length
differential_pressure: paired shell pressure contrast with common-mode rejection factor
cavity_shift:         perturbative mode-overlap factor times shell boundary-energy scale
superconducting:      cavity_shift model plus lower readout noise and higher material nuisance
material_impedance:   Stage 3 material/patch/capacitance scales as direct nuisance observables
```

Every scaling law must carry a provenance field and a pessimism/optimism
level. The first ladder should include conservative, nominal, and optimistic
rows per candidate rather than a single magic number.

## Output Tree

Use the external Research partition for runs.

```text
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_stage5_readout_ladder/<run_id>/
  manifest.json
  summary.json
  progress.jsonl
  latest_status.json
  configs/run_config.json
  candidates/readout_candidates.parquet
  candidates/readout_candidates.csv
  templates/stage3_shell_template.parquet
  templates/stage4_recovery_gate.json
  templates/candidate_observable_templates.parquet
  templates/nuisance_templates.parquet
  synthetic/synthetic_observations.parquet
  synthetic/recovery_ledger.parquet
  synthetic/false_positive_ledger.parquet
  gates/gate_ledger.parquet
  gates/gate_summary.csv
  gates/required_gain_ledger.parquet
  schedules/schedule_matrix.parquet
  schedules/schedule_recommendation.csv
  reports/stage5_readout_ladder_readout.md
```

Data-heavy tables go to parquet with zstd compression. Compact tables may be
CSV. Summary and manifest files are JSON.

## Heartbeat And Long-Run Behavior

Stage 5 must have a first-class heartbeat. The previous tensor blocks were
long enough that silent runs were painful. Use a recorder similar to
`Stage4ProgressRecorder`, with events at these points:

```text
run_start
inputs_loaded
candidate_started
candidate_model_complete
synthetic_chunk_complete
candidate_gate_complete
run_complete
```

For any later FEM/BEM/Lifshitz backend, heartbeat inside the candidate
calculation itself:

```text
backend_grid_started
backend_block_complete
backend_solve_complete
backend_template_projected
```

Write both:

```text
progress.jsonl       append-only full event stream
latest_status.json   single latest machine-readable state
reports/stage5_readout_ladder_readout.md
```

The markdown heartbeat report is machine generated and should say so. The
narrative supporting report remains manually written after the run is
interpreted.

## Stage 5 Implementation Plan

### Stage 5A: Scaffold And Input Loader

Build:

```text
readout_transduction.py
stage5_readout_ladder.py
stage5_models.py
stage5_gates.py
scripts/run_stage5_readout_ladder.sh
tests/test_stage5_readout_ladder.py
```

Input loader responsibilities:

```text
read Stage 3 tensor/bootstrap/material/readout summaries
read Stage 4 summary and template/gate ledgers
derive the current Stage 4 recovery SBR gate
load or recreate the geometry schedule
emit manifest with git commit, command line, input paths, and config
```

Smoke test:

```text
preset: smoke
candidates: central_timing_reference, force_gradient_mems, material_impedance_control
datasets per candidate: 12 shell + 12 EM-only
outputs: all required parquet/csv/json files exist
```

### Stage 5B: Candidate Models

Implement the first analytic models:

```text
CentralTimingModel
ForceGradientModel
DifferentialPressureModel
CavityShiftModel
SuperconductingResonatorModel
MaterialImpedanceControlModel
```

Each model should produce conservative, nominal, and optimistic rows. Use
clear scenario labels:

```text
scenario: conservative
scenario: nominal
scenario: optimistic
```

For each row, compute:

```text
predicted_sbr
required_gain_to_stage4_gate = stage4_required_sbr / max(predicted_sbr, epsilon)
dominant_nuisance
claim_class
allowed_claim
```

The central timing reference should reproduce the closure: huge required gain,
closed direct-readout interpretation.

### Stage 5C: Candidate-Specific Synthetic Recovery

Adapt the Stage 4 synthetic fitting harness so each candidate has:

```text
candidate shell template
candidate nuisance templates
candidate predicted amplitude
candidate noise floor
EM-only synthetic family
shell-plus-background synthetic family
```

Fit outputs:

```text
candidate_id
scenario
dataset_family
predicted_sbr
recovered_shell_coefficient
recovered_shell_z
recovered_fraction
false_positive_flag
template_condition_number
max_abs_shell_nuisance_correlation
```

This is the point where Stage 5 stops being a sensitivity spreadsheet and
becomes an apparatus discriminator.

### Stage 5D: Gate Ledger And Recommendation

The final run should write a ranked gate ledger:

```text
candidate_id
scenario
claim_class
allowed_claim
predicted_sbr
required_gain_to_stage4_gate
recovery_fraction_at_predicted_sbr
em_only_false_positive_rate
max_abs_shell_nuisance_correlation
template_condition_number
dominant_nuisance
gate_status
recommended_next_action
```

Use these gate statuses:

```text
closed_amplitude
closed_false_positive
closed_identity
background_calibration_only
candidate_for_fidelity_upgrade
candidate_for_apparatus_design
```

Most first-pass results should probably land in `closed_amplitude` or
`background_calibration_only`. A promising result should land in
`candidate_for_fidelity_upgrade`, meaning it deserves a better physical model.
Reserve `candidate_for_apparatus_design` for a candidate with amplitude,
recovery, false-positive, and claim-identity gates all passing.

## Tests

Add focused pytest coverage:

```text
test_stage5_smoke_writes_required_outputs
test_stage5_candidate_claim_classes_are_preserved
test_stage5_direct_timing_reference_closes_amplitude
test_stage5_required_gain_is_finite_for_zero_sbr
test_stage5_parquet_outputs_are_readable
test_stage5_em_only_false_positive_ledger_has_candidate_ids
test_stage5_gate_summary_matches_gate_ledger
```

The tests should use temporary directories and tiny synthetic inputs. They
should not depend on the external Research partition.

## First Run Commands

Use a smoke run first:

```bash
cd white_casimir_intersection/experiments/white_casimir_source_function_audit
./scripts/run_stage5_readout_ladder.sh smoke
```

The script should default to:

```text
source_stage3_dir=/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_tensor_scale_probe/stage3_focused_20260530
source_stage4_dir=/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_synthetic_discrimination/stage4_block_bootstrap_geometry_sbr_refine_20260530
outdir=/media/kir/9CDCBD3EDCBD140C/Research/white_casimir_stage5_readout_ladder/stage5_smoke_<date>
```

Then a focused run:

```bash
./scripts/run_stage5_readout_ladder.sh focused
```

Focused defaults:

```text
all six candidate families
conservative, nominal, optimistic scenarios
200 shell datasets per candidate/scenario
200 EM-only datasets per candidate/scenario
chunk_size 100
4 workers if backend models become parallel
```

## What To Check First

After the smoke run, inspect:

```text
summary.json or gates/gate_summary.csv
latest_status.json
gates/gate_ledger.parquet
gates/required_gain_ledger.parquet
synthetic/false_positive_ledger.parquet
```

Expected smoke behavior:

```text
central_timing_reference -> closed_amplitude
material_impedance_control -> background_calibration_only or closed_identity
force_gradient_mems -> open candidate, likely requiring better amplitude model
```

After the focused run, answer these questions:

1. Does any non-metric readout reach the Stage 4 SBR gate with plausible
   physical assumptions?
2. Does any candidate keep EM-only false positives below 0.05?
3. Does any candidate reduce shell/nuisance degeneracy relative to the Stage 4
   geometry-derived nuisance run?
4. Does a candidate measure Casimir boundary morphology directly, or merely a
   material nuisance with shell-correlated controls?
5. Is any positive candidate strong enough for a higher-fidelity physical
   backend, such as FEM/BEM/Lifshitz or a real resonator mode calculation?

## Higher-Fidelity Upgrade Path

If a candidate survives the analytic Stage 5 ladder, upgrade only that
candidate.

Possible backends:

```text
force_gradient_mems:
  boundary-element or Lifshitz force-gradient model with finite conductivity
  and patch-potential maps

differential_pressure:
  paired-cell pressure model with common-mode rejection and roughness priors

cavity_shift:
  electromagnetic eigenmode solver with perturbative boundary shifts and
  material loss model

superconducting_resonator:
  resonator mode solver plus kinetic inductance, surface loss, thermal, and
  vortex nuisance terms

central_timing_reference:
  only upgrade if an explicit propagation/transduction mechanism appears
```

The upgrade should keep the same Stage 5 output contract. Heavy solver blocks
write parquet block ledgers and heartbeat continuously.

## Narrative Rule For Reports

The Stage 5 report should tell the current truth without trying to rescue the
old readout. Use this claim structure:

```text
1. White geometry forms a shell-like Casimir boundary morphology in the proxy.
2. Direct metric/timing readout is closed by the Stage 3/4 gate.
3. Stage 5 tests whether another physical readout can measure the shell-coded
   boundary response.
4. A successful non-metric readout validates Casimir boundary morphology, not
   warp functionality.
5. A metric-like claim requires a concrete propagation/readout mechanism that
   supplies amplitude and passes the EM-only false-positive gate.
```

That is the ladder. It is large because the physical question is large. The
code should make every rung explicit and let weak candidates close quickly.
