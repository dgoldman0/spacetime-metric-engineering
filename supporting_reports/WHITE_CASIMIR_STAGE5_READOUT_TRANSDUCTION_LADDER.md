# White Casimir Stage 5 Readout-Transduction Ladder Findings

Date: 2026-05-30

Status: `stage5_readout_transduction_ladder_first_pass_complete`

## Summary

Stage 5 changes the readout question without changing the claim boundary.
The earlier White Casimir audit established a stable shell-forming morphology
in the sphere-cylinder proxy, then closed the direct metric/timing readout
interpretation under calibrated scale and ordinary electromagnetic/material
backgrounds. Stage 5 asks what remains scientifically alive after that closure.

The answer is not a direct warp readout. The answer is a physical
Casimir-boundary readout program.

White et al.'s proposed readout is naturally interpreted as a central
current/photon/electron transit comparison through the sphere-cylinder array.
In this audit, that channel is represented by the
`central_timing_reference` candidate. It remains closed by amplitude. The
source proxy is shell-placed rather than central-path placed, the calibrated
timing scale is effectively null at laboratory scale, and the geometry-coded
schedule cannot recover a signal that is many orders below ordinary
EM/material backgrounds.

Stage 5 then asks a different but closely related question:

```text
If the White sphere-cylinder geometry creates a real shell-shaped
Casimir-boundary response, can another readout channel measure that response
directly enough to break through ordinary EM/material noise?
```

The first analytic ladder finds that this question is worth pursuing. The
candidate readouts that survive are not metric/timing readouts. They are
apparatuses that could measure a shell-coded boundary response through force,
pressure, or resonant mode shifts. A positive experiment in this branch would
identify a geometry-coded Casimir/Lifshitz boundary phenomenon: the engineered
boundary conditions reshape the vacuum/electromagnetic mode response in a
shell-like way that can be transduced into a laboratory observable. It would
not, by itself, identify a warp-functional metric source.

The three highest-priority next options are:

```text
1. differential Casimir pressure geometry
2. high-Q microwave or optical cavity shift
3. superconducting resonator boundary shift
```

Each of these now deserves a higher-fidelity physical model. More synthetic
dataset count alone is not the useful next step. The limiting uncertainty has
moved from synthetic recovery statistics to apparatus physics: patch
potentials, finite conductivity, roughness, membrane response, mode overlap,
thermal drift, surface loss, vortex/quasiparticle effects, and calibration
controls.

## What Stage 5 Adds

Stages 2 through 4 answered three separate questions.

First, the scalar v-loop morphology result showed that the sphere-cylinder
geometry can concentrate a signed boundary proxy in the annular shell region.
That result is the basis for taking White's geometry seriously as a
shell-forming Casimir configuration.

Second, the Stage 3 tensor-scale audit separated source placement from scale.
The proxy remained overwhelmingly shell-localized, which supports the
morphology/source-placement interpretation. The same calibration placed the
metric/source scale many orders below Alcubierre demand and gave a linearized
timing bound around `1e-76 s`. That closes the direct metric-scale reading in
the present audit class.

Third, Stage 4 converted ordinary EM/material background worries into a
recoverability gate. Geometry modulation can recover a shell-coded template
when the shell observable is already near background scale. In the current
block-bootstrap, geometry-derived nuisance run, the required
signal-to-background ratio is about `1.2`, with an EM-only false-positive rate
around `0.034`. That is a useful gate because it names the burden a physical
readout must carry.

Stage 5 places candidate readout apparatuses in front of that gate. It does
not recompute the Casimir field. It treats the Stage 3 shell derivative
template and Stage 4 recovery threshold as inherited constraints, then asks
whether candidate transduction channels can plausibly supply a shell-coded
observable at sufficient amplitude while preserving claim identity.

The key design point is that every candidate carries a `claim_class`.

| Claim class | Meaning in Stage 5 | Allowed conclusion |
|---|---|---|
| `metric_proxy` | Propagation/timing/current observable with a bridge to metric perturbation. | Closed unless amplitude, nuisance, and controls all pass. |
| `casimir_boundary` | Force, pressure, or resonator response tied to boundary geometry. | A measurable shell-shaped Casimir-boundary morphology. |
| `material_response` | Patch, impedance, contact, thermal, loss, or conductivity response. | A geometry-correlated material/background channel. |
| `control` | Null or calibration channel. | Background calibration and false-positive control. |

This prevents the central mistake. A force-gradient or pressure success is not
a warp success. A resonator shift success is not automatically a metric
success. A material/impedance success explains backgrounds rather than
confirming the shell channel. The ladder keeps those meanings separate.

## Implementation Read

The Stage 5 implementation adds a readout-transduction layer under:

```text
white_casimir_intersection/experiments/
white_casimir_source_function_audit/white_casimir_audit/
```

The new modules are:

```text
readout_transduction.py
stage5_models.py
stage5_gates.py
stage5_readout_ladder.py
```

The runner is:

```text
scripts/run_stage5_readout_ladder.sh
```

The test file is:

```text
tests/test_stage5_readout_ladder.py
```

The harness writes the planned ledger tree:

```text
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

The first pass uses transparent analytic scaling laws. It does not claim
high-fidelity physical prediction. It is an apparatus triage and falsification
harness. Each candidate receives conservative, nominal, and optimistic
scenario rows with explicit required gain to the Stage 4 gate.

The focused validation run used the existing Stage 3 and Stage 4 focused
artifacts:

```text
Stage 3 input:
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_tensor_scale_probe/stage3_focused_20260530

Stage 4 input:
/media/kir/9CDCBD3EDCBD140C/Research/
white_casimir_synthetic_discrimination/
stage4_block_bootstrap_geometry_sbr_refine_20260530
```

It produced:

```text
candidate families:         6
candidate/scenario rows:    18
synthetic observation rows:  86400
fit rows:                   7200
Stage 4 required SBR:       1.2
elapsed on laptop:          about 6.7 s
```

Verification:

```text
PYTHONPATH=white_casimir_intersection/experiments/white_casimir_source_function_audit \
python -m pytest white_casimir_intersection/experiments/white_casimir_source_function_audit/tests

19 passed
```

## Candidate Ladder Result

The first-pass focused gate produced this high-level status count:

```text
background_calibration_only:      3
candidate_for_fidelity_upgrade:   5
closed_amplitude:                10
```

The three `background_calibration_only` rows are the material/impedance
control candidate across conservative, nominal, and optimistic scenarios. They
are useful because ordinary material response remains a first-class competitor
in every realistic apparatus. They are not shell evidence.

The ten `closed_amplitude` rows include the central timing reference across
all scenarios and several weak boundary-readout scenarios. This is an
important closure. The White-style central transit comparison remains many
orders below the Stage 4 recovery gate. It is not a channel where more
synthetic fitting is likely to change the story.

The five `candidate_for_fidelity_upgrade` rows are analytic survivors. They
are not ready for apparatus design. They identify where the next physical
modeling budget should go.

Representative focused gate rows:

| Candidate | Scenario | Claim class | Predicted SBR | EM-only FP | Status |
|---|---:|---|---:|---:|---|
| `differential_pressure_cell` | optimistic | `casimir_boundary` | `562.0` | `0.035` | `candidate_for_fidelity_upgrade` |
| `superconducting_resonator_shift` | optimistic | `casimir_boundary` | `198.2` | `0.030` | `candidate_for_fidelity_upgrade` |
| `differential_pressure_cell` | nominal | `casimir_boundary` | `18.7` | `0.020` | `candidate_for_fidelity_upgrade` |
| `superconducting_resonator_shift` | nominal | `casimir_boundary` | `6.61` | `0.025` | `candidate_for_fidelity_upgrade` |
| `high_q_cavity_shift` | optimistic | `casimir_boundary` | `4.02` | `0.040` | `candidate_for_fidelity_upgrade` |
| `force_gradient_mems` | optimistic | `casimir_boundary` | `0.441` | `0.020` | `closed_amplitude` |
| `central_timing_reference` | optimistic | `metric_proxy` | `4.08e-59` | `0.055` | `closed_amplitude` |
| `material_impedance_control` | nominal | `material_response` | `0.0` | `0.000` | `background_calibration_only` |

The absolute values in the survivor rows are not final physics predictions.
They are analytic triage scores under declared sensitivity floors, overlap
factors, and nuisance penalties. Their status means: this channel is plausible
enough to deserve a real physical backend.

The central timing row is more decisive. Its predicted SBR is so far below the
Stage 4 gate that the readout is closed in this audit class even under the
optimistic scenario. That is the right conclusion for White's original-style
transit readout.

## The Central Readout Closure

White et al.'s readout proposal is naturally read as a central-path
comparison: send a current, photon, or electron signal through or along the
array and compare it against a control path. That kind of readout asks whether
the shell-shaped Casimir morphology produces a measurable propagation or
timing perturbation in the central channel.

The audit separates two things that can otherwise be blurred.

First, the source proxy is not mainly in the readout path. That supports the
shell morphology claim because the effect is not just a central-axis
bookkeeping artifact.

Second, the calibrated metric/timing signal associated with the source proxy
is far too small for a physical readout under ordinary backgrounds. That
closes the direct measurement interpretation.

Stage 5 preserves this as a reference closure. The
`central_timing_reference` candidate combines the Stage 3 linearized timing
bound, readout-source fraction, readout-circuit nuisance, waveguide nuisance,
and the Stage 4 recovery gate. It remains `closed_amplitude` in every
scenario.

The conclusion is:

```text
White's original-style central transit readout is not the channel that breaks
through EM/material noise in this model.
```

That is not the same as saying the geometry has no measurable physical
content. It means the measurable content, if present, must be read by a
channel matched to the boundary response rather than by a direct central
metric/timing comparison.

## What A Positive Physical Study Would Identify

A successful Stage 5 follow-up would identify a geometry-coded
Casimir-boundary response.

In practical terms, it would mean:

```text
The sphere-in-cylinder boundary conditions reshape the vacuum/EM mode
response so that a force, pressure, cavity shift, resonator phase shift, or
related observable follows the same shell-coded geometry template found in the
proxy calculations.
```

That is valuable physics. It would show that White's sphere-cylinder geometry
is not merely a numerical resemblance to a shell, but a transducible boundary
system whose response can be read in a laboratory apparatus.

The implication depends on the readout and the controls.

If the signal matches Casimir/Lifshitz boundary predictions, the result
identifies a controlled finite-geometry vacuum-boundary effect. The physics
lesson is that engineered microboundary geometry can organize a measurable
mode response into a shell-like spatial template.

If the signal is explained by patch potentials, impedance, thermal drift,
surface roughness, finite conductivity, contact loading, or material loss, the
result identifies a geometry-correlated material/background channel. That is
still useful because it tells the experiment what ordinary physics imitates
the shell schedule.

If a clean shell-coded signal survives the material controls and exceeds good
Casimir/Lifshitz or electromagnetic-mode predictions, then the result becomes
more interesting. It would indicate an under-modeled finite-geometry
vacuum/material response. It would still not automatically become a warp
claim; it would become a sharper boundary-QFT/material-physics question.

What it would not imply by itself:

```text
It would not imply that a warp-relevant metric source has been produced.
It would not imply measurable spacetime curvature.
It would not validate the central transit/timing interpretation.
```

Those claims require tensor stress scale, source-demand relevance, and a
metric or propagation mechanism that the current audit does not find.

## Why More Synthetic Testing Is Not The Next Main Move

The Stage 4 and Stage 5 synthetic layers have done their useful first job.
They established the recovery gate, kept ordinary EM/material competitors in
the same ledger as the shell template, and turned the problem into a ranked
apparatus question.

Increasing the number of synthetic datasets can tighten the recovery and
false-positive estimates, but it does not address the current limiting
uncertainty. The open question is no longer whether ridge fits can recover a
template at SBR near unity. The open question is whether any actual readout
physics can produce such an observable while keeping material and EM
false-positive controls under control.

The next useful work is therefore candidate-specific physical modeling. The
survivors should be upgraded one at a time. Each upgraded backend should keep
the same Stage 5 output contract: candidate templates, nuisance templates,
synthetic recovery ledgers, false-positive ledgers, and a gate ledger with
claim class preserved.

## High-Priority Follow-Up 1: Differential Casimir Pressure

The differential pressure geometry is the cleanest next branch.

Its intended observable is a paired-cell pressure or force contrast between
two sphere-cylinder cells with opposite shell-gap modulation. It directly
targets a Casimir-boundary response rather than a central transit path. It can
use common-mode rejection, which is exactly the kind of apparatus feature the
Stage 4/5 discriminator rewards.

The first physical backend should model:

```text
paired sphere-cylinder cells
opposite shell-gap modulation
finite conductivity bracket
patch-potential maps or priors
surface roughness
membrane stress drift
temperature gradients
common-mode rejection factor
dummy conductor controls
large-gap or far-field controls
```

The desired result is not only a large pressure estimate. The desired result
is a template result: the pressure contrast must follow the shell-coded
geometry schedule while EM/material-only simulations stay below the
false-positive gate.

This branch has the strongest claim identity. If it passes, the allowed
conclusion is a measurable shell-shaped Casimir-boundary morphology. It still
does not become a metric claim.

## High-Priority Follow-Up 2: High-Q Cavity Shift

The cavity-shift branch asks whether the shell-coded boundary response can be
transduced through an electromagnetic mode whose overlap with the annular
shell region is high enough and whose ordinary mode nuisances are controlled.

Its intended observable is:

```text
delta_f / f
mode splitting
phase shift
Q shift
```

This branch is attractive because resonant frequency and phase can be
measured very precisely. It is also risky because the same apparatus is
naturally sensitive to thermal expansion, finite conductivity, roughness,
waveguide cutoff, readout-circuit artifacts, and mode mixing.

The first physical backend should model:

```text
mode shape in the sphere-cylinder boundary geometry
annular shell overlap integral
boundary perturbation estimate
finite-conductivity correction
surface roughness/loss channel
thermal expansion drift
waveguide cutoff/dispersion
dummy cavity or non-shell geometry control
material-loss observable in the same schedule
```

The key classification rule is important. A frequency shift can pass as a
Casimir-boundary readout only if the mode-shift model separates it from
ordinary material/loss channels. If the observed shift is dominated by loss or
conductivity changes, the allowed conclusion becomes material response.

## High-Priority Follow-Up 3: Superconducting Resonator Shift

The superconducting resonator branch is potentially sensitive and potentially
dangerous. It receives a strong first-pass analytic score because its
readout floor can be low. That same sensitivity makes it vulnerable to
ordinary material effects.

Its intended observable is:

```text
resonator frequency shift
phase readout
Q shift
kinetic-inductance shift
surface-loss shift
```

The first physical backend should model:

```text
resonator mode overlap with the annular shell region
finite-conductivity and superconducting boundary response
kinetic inductance contribution
surface loss
vortex effects
quasiparticle effects
temperature dependence
material-only resonator controls
dummy boundary controls
readout-chain artifacts
```

This branch should be held to a stricter claim boundary than the pressure
branch. A superconducting readout can detect very small shifts, but many
small shifts are not Casimir shell shifts. The result is interesting only if
the shell-coded template remains distinguishable from material and resonator
loss templates.

## Lower-Priority Follow-Up: Force-Gradient MEMS/NEMS

The force-gradient branch remains physically natural because Casimir force
gradients are a direct boundary observable. In the current first-pass ladder,
however, the analytic amplitude/background burden is rough. The optimistic row
still closes on amplitude under the current sensitivity and patch-penalty
assumptions.

This does not mean force-gradient readout is impossible. It means that this
branch should wait until there is a concrete MEMS/NEMS design with:

```text
declared force-gradient sensitivity
realistic gap and probe geometry
patch-potential mapping
electrostatic calibration drift model
roughness model
vibration/alignment budget
thermal drift budget
```

Without those apparatus details, additional synthetic fitting does not add
much information.

## Material/Impedance As An Adversary

The material/impedance candidate is not a failed shell readout. It is a
control and adversary.

It exists because any real apparatus can produce geometry-correlated changes
in:

```text
capacitance
impedance
contact resistance
surface potential
loss tangent
thermal response
conductivity
readout-chain response
```

If this channel lights up in an experiment, it may explain a shell-like signal
without invoking a Casimir-boundary response. Stage 5 keeps it in the same
ledger because a useful experiment needs to know not only what passes, but
what ordinary physics can imitate.

The material/impedance branch should remain attached to every higher-fidelity
upgrade as a required control.

## Current Claim Boundary

The current White Casimir narrative is:

```text
The sphere-cylinder geometry forms a stable shell-like Casimir boundary
morphology in the proxy audit.
```

and:

```text
The direct central metric/timing readout does not survive the calibrated
scale and EM/material background gate.
```

and:

```text
Several nonmetric physical readout channels are worth testing because they
could measure the shell-shaped boundary response directly.
```

The allowed positive outcome of the next phase is a physical readout of a
shell-coded Casimir/Lifshitz boundary response. That would be a real and
valuable physics result. It would say that engineered boundary geometry can
organize a measurable vacuum/EM boundary response into a shell-like template.

The current audit does not support the stronger statement that the device
produces a warp-functional metric source. The stress scale and direct timing
readout remain closed under the modeled apparatus backgrounds.

## Next Work

The next build should not rerun Stage 3 from scratch unless the upstream
physics fidelity changes. The existing Stage 3 and Stage 4 focused outputs are
adequate inputs for the Stage 5 apparatus ladder. Rebuilding them only repeats
the current source-placement and recovery-gate evidence.

The next work should be:

```text
1. Build a differential-pressure physical backend.
2. Build a high-Q cavity mode-overlap and nuisance backend.
3. Build a superconducting resonator mode/loss backend.
4. Keep material/impedance control ledgers attached to each branch.
5. Reserve force-gradient work for a concrete MEMS/NEMS apparatus design.
6. Leave central timing closed unless a new propagation mechanism is supplied.
```

The Stage 5 harness is now the common ledger for those branches. Each upgrade
should emit the same gate fields:

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

The report rule going forward is simple: a candidate may earn a stronger
apparatus recommendation only by preserving its claim identity while passing
amplitude, recovery, false-positive, and control gates together. The prize is
a clean physical readout of the shell-shaped Casimir boundary response. The
warp interpretation remains outside the current positive claim boundary.

