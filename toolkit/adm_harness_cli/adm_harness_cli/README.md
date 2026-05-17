# ADM Harness CLI

Command-line harness for active-rail ADM ledger runs, substrate subtraction, absorber sidecar diagnostics, and narrow absorber-field synthesis.

## Commands

```bash
python -m adm_harness.cli validate --config configs/v5_compact_synthesis_betaoff.yaml
python -m adm_harness.cli run --config configs/v5_compact_synthesis_betaoff.yaml
python -m adm_harness.cli compare --runs runs/v5_identity runs/v5_compact --output-dir runs/comparison
```

Legacy wrappers are also included:

```bash
python run_adm_harness.py --config configs/v5_betaoff.yaml
python compare_adm_runs.py --runs runs/a runs/b --output-dir runs/comparison
```

## Synthesis mode

Synthesis is enabled by adding a `synthesis` block and an absorber law. The first implementation intentionally supports one target field, `beta`, because this is the safest early interface for testing compact absorber effects against the ADM ledger.

```yaml
synthesis:
  enabled: true
  smoothing_passes: 2

absorber:
  mode: compact_beta_localizer
  law: compact_beta_localizer
  target_field: beta
  support_mask: catch_rematch_edge
  signal: delta_j_l
  coefficients:
    amplitude: 0.002
    gain: 1.0
    max_abs_delta: 0.002
```

The law computes a bounded `delta_beta` from the selected residual signal, applies it inside the selected support mask, smooths the window, recomputes `k_l`, `k_omega`, `K`, `rho`, and `j_l`, and then recomputes `delta_rho` and `delta_j_l` directly against the chosen substrate channels.

Identity laws are supported and should reproduce the baseline ledger to numerical tolerance:

```yaml
synthesis:
  enabled: true

absorber:
  mode: identity
  law: identity
  target_field: beta
```

## Validation

Validation runs before scientific outputs are trusted. It checks:

- config contract
- required field arrays
- grid monotonicity and shape consistency
- finite values
- positive `alpha`, `gamma_ll`, and `gamma_omega`
- substrate grid compatibility
- field-delta shape, target, finiteness, and positivity preservation
- identity ADM recomputation self-check when enabled

Every run writes `validation_report.json`. Synthesis runs also write `field_delta_summary.csv` and `field_delta_metadata.json`.

## Standard outputs

Each run folder contains:

```text
run_metadata.json
status.json
validation_report.json
point_ledger.csv
stage_region_burden.csv
scope_burden.csv
packet_exposure.csv
support_shell_load.csv
catch_rematch_localization.csv
peak_locations.csv
decision_sheet.csv
report.md
figures/
```

Synthesis runs additionally contain:

```text
field_delta_summary.csv
field_delta_metadata.json
```

## Current scope

This is still a radial ADM harness, not a full 3+1 constraint solver. The synthesis path currently modifies `beta` only. That is enough to test early compact absorber/control-law behavior against `delta_rho`, `delta_j_l`, packet exposure, support-shell load, and catch/rematch localization without turning the tool into a larger source-family modeling framework.
