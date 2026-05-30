# White Casimir Stage 5 Priority Physical Closeout

Date: 2026-05-30

Status: `priority_physical_backend_run_complete`

## Summary

The Stage 5 priority physical run upgrades the readout-transduction ladder
from analytic triage to first-pass apparatus physics for the three surviving
branches:

```text
1. differential Casimir pressure
2. high-Q microwave/optical cavity shift
3. superconducting resonator boundary shift
```

The central timing reference and material/impedance control remain in the run
as guardrails. The central timing reference represents the White-style
current/photon/electron transit readout and remains closed by amplitude. The
material/impedance control remains a background/calibration channel rather
than a shell result.

The physical branch result is sharper than the analytic Stage 5 triage. The
line of research is not exhausted as a physical readout program. It is
exhausted as a direct central timing or warp-readout program under the current
audit. The surviving question is whether a real apparatus can measure a
shell-coded Casimir/Lifshitz boundary response through pressure or resonant
mode shifts.

The priority physical run found:

```text
central timing:              closed by amplitude in all rows
material/impedance control:  background calibration only in all rows
differential pressure:       survives only in strong-control optimistic rows
high-Q cavity shift:         strongest surviving non-superconducting branch
superconducting resonator:   strongest sensitivity branch, with nuisance risk
```

This is a positive apparatus-design result, not a warp result. A successful
future experiment in one of the surviving branches would identify a
geometry-coded Casimir-boundary response: the sphere-cylinder boundary
conditions organize a measurable force, pressure, frequency, phase, or loss
observable into the same shell-coded geometry template seen in the proxy
calculations. It would not by itself identify a warp-functional metric source.

## Run

The closeout run reused the current focused Stage 3 and Stage 4 artifacts:

```text
Stage 3 input:
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_tensor_scale_probe/stage3_focused_20260530

Stage 4 input:
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_synthetic_discrimination/
stage4_block_bootstrap_geometry_sbr_refine_20260530
```

The run output is:

```text
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_stage5_readout_ladder/
stage5_priority_physical_closeout_20260530
```

Command:

```bash
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage5_readout_ladder.sh \
  priority_physical \
  --run-id stage5_priority_physical_closeout_20260530
```

The first attempt inside the workspace sandbox could not create the external
research output directory because `/media` was read-only in the sandbox. The
approved external run completed normally.

Run scale:

```text
backend mode:                physical
candidate families:          5
candidate/scenario gates:    33
physical backend rows:       27
synthetic observation rows:  237600
fit rows:                    19800
Stage 4 required SBR:        1.2
elapsed:                     about 26.9 s
```

Verification before the run:

```text
PYTHONPATH=white_casimir_intersection/experiments/white_casimir_source_function_audit \
python -m pytest white_casimir_intersection/experiments/white_casimir_source_function_audit/tests

20 passed
```

## Code Refinement

The priority physical run adds candidate-specific physical backends behind the
same Stage 5 ledger contract. The new files are:

```text
white_casimir_audit/stage5_physical_priors.py
white_casimir_audit/stage5_pressure_backend.py
white_casimir_audit/stage5_cavity_backend.py
white_casimir_audit/stage5_superconducting_backend.py
```

The existing Stage 5 runner now supports:

```text
priority_physical
--backend-mode physical
```

The output contract remains compatible with the earlier Stage 5 ladder:

```text
candidates/readout_candidates.parquet
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
```

The physical mode adds:

```text
backends/physical_backend_sweep.parquet
backends/physical_backend_sweep.csv
```

Those backend rows record the prior assumptions that generated each physical
candidate row: pressure common-mode rejection and patch residuals; cavity
mode overlap, finite-conductivity and loss terms; superconducting kinetic,
surface-loss, vortex, quasiparticle, thermal, and material-control terms.

The new gate statuses are:

```text
closed_physical_scale
closed_nuisance_degeneracy
candidate_survives_for_experiment
```

These statuses distinguish failure to reach the Stage 4 SBR gate from failure
to separate plausible material/loss nuisances. A survivor is not a discovery
claim. It is a physical-backend row that reaches amplitude, recovery, and
false-positive gates while keeping the modeled nuisance ratio under the
declared branch threshold.

## Gate Summary

The priority physical run produced:

```text
background_calibration_only:       3
candidate_survives_for_experiment: 11
closed_amplitude:                  3
closed_nuisance_degeneracy:        2
closed_physical_scale:             14
```

By candidate:

| Candidate | Status distribution |
|---|---|
| `central_timing_reference` | `closed_amplitude`: 3 |
| `material_impedance_control` | `background_calibration_only`: 3 |
| `differential_pressure_cell` | `candidate_survives_for_experiment`: 2; `closed_physical_scale`: 7 |
| `high_q_cavity_shift` | `candidate_survives_for_experiment`: 4; `closed_physical_scale`: 5 |
| `superconducting_resonator_shift` | `candidate_survives_for_experiment`: 5; `closed_nuisance_degeneracy`: 2; `closed_physical_scale`: 2 |

The strongest survivor rows were:

| Candidate | Scenario | Predicted SBR | EM-only FP | Required gain |
|---|---|---:|---:|---:|
| `high_q_cavity_shift` | `cavity_optimistic_clean` | `19.34` | `0.040` | `0.062` |
| `superconducting_resonator_shift` | `sc_optimistic_clean` | `17.76` | `0.0367` | `0.0676` |
| `superconducting_resonator_shift` | `sc_optimistic_balanced` | `12.10` | `0.040` | `0.099` |
| `high_q_cavity_shift` | `cavity_optimistic_matched` | `11.88` | `0.0267` | `0.101` |
| `superconducting_resonator_shift` | `sc_optimistic_lossy` | `7.94` | `0.0433` | `0.151` |
| `high_q_cavity_shift` | `cavity_optimistic_lossy` | `6.07` | `0.0433` | `0.198` |
| `superconducting_resonator_shift` | `sc_nominal_clean` | `5.46` | `0.0267` | `0.220` |
| `differential_pressure_cell` | `pressure_optimistic_quiet` | `5.31` | `0.0267` | `0.226` |
| `superconducting_resonator_shift` | `sc_nominal_balanced` | `3.59` | `0.0333` | `0.334` |
| `high_q_cavity_shift` | `cavity_nominal_clean` | `2.22` | `0.0133` | `0.540` |
| `differential_pressure_cell` | `pressure_optimistic_balanced` | `2.02` | `0.030` | `0.595` |

The largest predicted SBR was `19.34` in the clean high-Q cavity case. The
lowest required gain to the Stage 4 gate was `0.062`, which means that row
exceeds the Stage 4 SBR gate by roughly a factor of sixteen under its own
physical prior assumptions.

## Branch Read: Differential Pressure

The differential pressure branch is the cleanest claim identity branch. It is
a direct Casimir-boundary observable: a paired-cell pressure contrast under
opposite shell-gap modulation. When it passes, its allowed conclusion is a
shell-shaped Casimir-boundary morphology, not a metric effect.

The physical run is strict with pressure because patch residuals dominate
unless common-mode rejection and surface controls are strong. Seven of nine
pressure cases close on physical scale. Two survive:

| Scenario | Predicted SBR | Nuisance/shell | Status |
|---|---:|---:|---|
| `pressure_optimistic_quiet` | `5.31` | `0.186` | survives |
| `pressure_optimistic_balanced` | `2.02` | `0.493` | survives |

The pressure branch therefore remains alive only as a disciplined apparatus
design with strong common-mode rejection, patch-potential suppression, and
roughness/membrane controls. It is not a broad easy win. It is the cleanest
physics interpretation if it can be engineered.

The immediate implication is:

```text
Pressure can read the shell only if the apparatus is designed around patch
suppression and common-mode rejection from the start.
```

## Branch Read: High-Q Cavity Shift

The high-Q cavity branch is the strongest non-superconducting survivor in the
priority run. It models a perturbative fractional frequency shift from shell
energy over stored mode energy, multiplied by an annular shell-overlap factor
and challenged by finite-conductivity, thermal, waveguide, mode-mixing, and
loss-channel nuisances.

Four of nine cavity cases survive:

| Scenario | Predicted SBR | Nuisance/shell | Status |
|---|---:|---:|---|
| `cavity_optimistic_clean` | `19.34` | `0.025` | survives |
| `cavity_optimistic_matched` | `11.88` | `0.040` | survives |
| `cavity_optimistic_lossy` | `6.07` | `0.060` | survives |
| `cavity_nominal_clean` | `2.22` | `0.080` | survives |

The important feature is not only amplitude. The high-Q cavity branch can
beat the Stage 4 gate while keeping modeled nuisance-to-shell ratios small in
clean and optimistic cases. That makes it the strongest candidate for a
non-superconducting physical readout.

The limitation is equally clear. The surviving rows assume usable mode
overlap and controlled loss/mode artifacts. The next physical model must
replace the overlap prior with an actual electromagnetic mode calculation in
the sphere-cylinder boundary geometry.

The immediate implication is:

```text
The cavity branch deserves an eigenmode/perturbation backend before this line
is closed. It is the most promising ordinary resonator readout.
```

## Branch Read: Superconducting Resonator

The superconducting branch has the strongest sensitivity and the richest
false-positive space. It models a fractional frequency/phase response with
mode overlap and challenges it with kinetic inductance, surface loss, vortex,
quasiparticle, thermal, and material-control terms.

Five of nine superconducting cases survive:

| Scenario | Predicted SBR | Nuisance/shell | Status |
|---|---:|---:|---|
| `sc_optimistic_clean` | `17.76` | `0.030` | survives |
| `sc_optimistic_balanced` | `12.10` | `0.045` | survives |
| `sc_optimistic_lossy` | `7.94` | `0.070` | survives |
| `sc_nominal_clean` | `5.46` | `0.100` | survives |
| `sc_nominal_balanced` | `3.59` | `0.160` | survives |

Two additional superconducting rows reach amplitude but close on nuisance
degeneracy:

| Scenario | Predicted SBR | Nuisance/shell | Status |
|---|---:|---:|---|
| `sc_nominal_lossy` | `2.30` | `0.250` | nuisance-degenerate |
| `sc_conservative_clean` | `1.60` | `0.350` | nuisance-degenerate |

This branch remains physically interesting, but the report should not let its
sensitivity hide its danger. A superconducting readout can measure small
signals; many small signals are ordinary material/loss signals. The allowed
positive interpretation requires a material-only resonator control and a
loss-channel ledger.

The immediate implication is:

```text
Superconducting resonator readout is a strong candidate only if material,
surface-loss, vortex, quasiparticle, and temperature controls are first-class
parts of the apparatus.
```

## Central Timing Closure

The central timing reference remains closed in all three rows:

```text
central_timing_reference -> closed_amplitude
```

The optimistic predicted SBR remains about `4.08e-59`. The required gain to
the Stage 4 gate remains about `2.94e58`. This is not a marginal result. The
White-style central current/photon/electron transit readout is not a viable
way through the EM/material background gate in this audit.

This conclusion has a stable narrative role:

```text
The source proxy is shell-placed rather than central-path placed, and the
direct metric/timing readout is far below laboratory recovery scale.
```

That closes the direct warp/readout interpretation. It does not close the
physical Casimir-boundary readout program.

## Material/Impedance Control

The material/impedance branch remains a control:

```text
material_impedance_control -> background_calibration_only
```

It is not a failed shell readout. It is the adversarial channel every physical
readout must carry. If capacitance, impedance, contact, patch, thermal, or
loss channels follow the shell schedule, they can explain a positive readout
without invoking a clean Casimir-boundary response.

The material/impedance control should remain attached to every future
apparatus branch.

## Narrative Implication

The current research line now separates into three clear statements.

First:

```text
White's sphere-cylinder geometry remains a real shell-forming Casimir
boundary morphology in the source-function audit.
```

Second:

```text
White's original-style central transit/timing readout remains closed by scale
and ordinary EM/material background competition.
```

Third:

```text
There are surviving physical readout paths for the shell-shaped boundary
response, especially high-Q cavity and superconducting resonator readouts
under clean-control priors, with differential pressure surviving only under
strong common-mode and patch-control assumptions.
```

That is the honest scientific posture. This line is not a warp demonstration
line. It is a finite-geometry Casimir/Lifshitz readout line. If continued, it
would test whether engineered boundary conditions can organize a measurable
vacuum/EM boundary response into a shell-coded template.

If a future experiment or high-fidelity solver confirms one of the survivor
branches, the result would imply:

```text
Engineered microboundary geometry can produce a transducible shell-coded
Casimir/Lifshitz response.
```

It would not imply:

```text
A warp-functional stress-energy source has been generated.
```

The value of continuing is therefore a real but narrower physics value:
finite-geometry boundary-QFT/material response, not metric engineering.

## What Further Work Would Give

Further work would be useful only if it upgrades physical fidelity. More
synthetic count alone is not the key next step.

The next useful artifacts would be:

```text
high-Q cavity:
  electromagnetic eigenmode calculation in the actual sphere-cylinder geometry
  perturbative boundary-frequency shift
  finite-conductivity and surface-loss decomposition
  dummy cavity and material-control ledgers

superconducting resonator:
  resonator mode solver
  kinetic-inductance and surface-loss model
  vortex/quasiparticle/thermal priors tied to measurable controls
  material-only resonator comparison

differential pressure:
  paired-cell Casimir/Lifshitz pressure model
  patch-potential map prior
  roughness and membrane stress model
  common-mode rejection validation
```

Those backends would decide whether the survivor rows remain alive under
apparatus-grade physics. If all three fail under that fidelity, the physical
readout line can close cleanly. If one survives, the line becomes an
apparatus-design proposal.

## Current Decision Point

The priority physical run does not justify stopping by saying "nothing is
left." Something is left: high-Q cavity and superconducting resonator readouts
are plausible under controlled physical priors, and pressure readout is
plausible under strong common-mode/patch control.

The priority physical run also does not justify overstating the result. The
surviving rows are not experimental evidence. They are modeled apparatus
priors that pass the Stage 4 recovery and EM-only false-positive gates.

The decision is therefore strategic:

```text
Continue only if the goal is a Casimir-boundary readout or finite-geometry
boundary-response result.

Stop if the goal requires a warp-functional or central transit/timing claim.
```

That is the useful closure. The broad warp-readout claim is closed. The
narrower physical boundary-readout program has clear survivor branches and a
defined next fidelity step.

