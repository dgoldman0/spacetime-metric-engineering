# ADM Harness CLI

A small command-line harness for active-rail ADM ledger runs.

This version is intentionally narrow. It normalizes the exact-builder ADM bundle products and substrate-subtraction products into repeatable run folders. It does not yet regenerate the full metric fields from first-principles symbolic definitions; it expects exact field arrays and, when needed, substrate arrays as inputs.

## Install or run locally

From this folder:

```bash
python -m adm_harness.cli run --config configs/v5_betaoff.yaml
python -m adm_harness.cli compare --runs /path/to/run_a /path/to/run_b --output-dir /path/to/comparison
```

Wrapper scripts are also included:

```bash
python run_adm_harness.py --config configs/v5_betaoff.yaml
python compare_adm_runs.py --runs runs/v5_betaoff runs/v5_static --output-dir runs/comparison_v5
```

## Inputs

Each config points at:

- `exact_fields`: NPZ with `s_grid`, `l_grid`, `rho`, `j_l`, `K`, `R3`, and related exact ADM fields.
- `exact_point_ledger`: optional CSV with stage, region, packet masks, and cell volumes.
- `substrate_fields`: optional NPZ with beta-off/static delta fields and support masks.
- `absorber.fit_summary` or `absorber.candidate_scores`: optional sidecar diagnostics for absorber/control-law selection.

The example configs in `configs/` are sandbox-ready for the uploaded bundles. Edit the paths for local use.

## Outputs

Each run creates:

```text
run_metadata.json
status.json
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

The comparison command creates:

```text
comparison_decision_sheet.csv
delta_metric_rankings.csv
comparison_report.md
```

## Current limitation

Absorber diagnostics are sidecar metrics in this CLI version unless the config supplies a coupled field/ledger variant. The tool does not synthesize new ADM fields from absorber coefficients yet.
