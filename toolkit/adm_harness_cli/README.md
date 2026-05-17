# ADM Harness CLI

Command-line harness for active-rail ADM ledger runs, substrate subtraction, whole-service field synthesis, and compact catch/rematch control-law tests.

## Commands

```bash
python -m adm_harness.cli validate --config configs/v5_service_carrying_flow_localizer.yaml
python -m adm_harness.cli run --config configs/v5_service_carrying_flow_localizer.yaml
python -m adm_harness.cli compare --runs runs/v5_service_flow_off runs/v5_service_carrying_flow_localizer --output-dir runs/comparison
```

Legacy wrappers are also included:

```bash
python run_adm_harness.py --config configs/v5_service_flow_off.yaml
python compare_adm_runs.py --runs runs/a runs/b --output-dir runs/comparison
```

## Service vocabulary

The config uses service names instead of raw ADM shorthand:

| Service name | Meaning in the active-rail service | Exact-builder internal field |
|---|---|---|
| `carrying_flow` | radial carrying flow that moves the packet through the service | radial shift array |
| `clock_lapse` | service clock-rate and causal-margin field | lapse array |
| `rail_stretch` | radial rail/stretch geometry | radial spatial metric component |
| `throat_capacity` | angular/throat capacity geometry | angular spatial metric component |

The loader still accepts old internal field names for backward compatibility with existing bundle files, but generated configs, metadata, and summaries use the service names.

## Whole-service synthesis

Synthesis is enabled with a `synthesis` block and one or more `service` modifier blocks. Each modifier produces a bounded field change, recomputes the ADM ledger, and writes the same decision-sheet products.

```yaml
service:
  velocity: 5.0

  carrying_flow:
    enabled: true
    law: compact_momentum_localizer
    scope: catch_rematch_edge
    signal: delta_j_l
    amplitude: 0.002
    gain: 1.0
    max_abs_change: 0.002
    smoothness_order: 2
    packet_exclusion: 0.40
    support_shell_gain: 0.50
    edge_bias: 0.25

  clock_lapse:
    enabled: false
    law: windowed_scale
    scope: support_shell
    amplitude: 0.0
    max_abs_change: 0.0

  rail_stretch:
    enabled: false
    law: windowed_scale
    scope: support_shell
    amplitude: 0.0
    max_abs_change: 0.0

  throat_capacity:
    enabled: false
    law: windowed_scale
    scope: support_shell
    amplitude: 0.0
    max_abs_change: 0.0

substrate:
  mode: carrying_flow_off

synthesis:
  enabled: true
```

Supported first-pass laws:

```text
identity
windowed_adjustment
scale_existing
compact_momentum_localizer
```

The `compact_momentum_localizer` law is intended for the carrying-flow service field. It uses a selected residual channel, usually `delta_j_l`, builds a compact window, applies the bounded counterflow, recomputes `k_l`, `k_omega`, `K`, `rho`, and `j_l`, then recomputes `delta_rho` and `delta_j_l` against the selected substrate.

## Adjustable knobs in this revision

Service knobs:

```text
velocity
carrying_flow.enabled/law/scope/amplitude/gain/max_abs_change
clock_lapse.enabled/law/scope/amplitude/max_abs_change
rail_stretch.enabled/law/scope/amplitude/max_abs_change
throat_capacity.enabled/law/scope/amplitude/max_abs_change
```

Window and lifecycle knobs:

```text
scope
radial_center
radial_width
schedule_center
schedule_width
stage_weights
smoothness_order
packet_exclusion
support_shell_gain
edge_bias
```

Substrate knobs:

```text
mode: none | carrying_flow_off | static
```

## Validation

Validation runs before scientific outputs are trusted. It checks:

- config contract
- required field arrays
- grid monotonicity and shape consistency
- finite values
- positive clock and geometry fields
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
service_modifier_summary.csv
```

## Current scope

This is still a radial ADM harness, not a full 3+1 constraint solver. The revision now exposes whole-service knobs first, with catch/rematch control as one service modifier rather than the center of the tool. Source-family modeling remains outside this harness pass.
