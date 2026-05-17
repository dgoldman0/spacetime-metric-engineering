# ADM Harness CLI service v0.5 self-contained

This package contains the active-rail ADM harness CLI, relative-path V=5 configs, tests, and a small prepared V=5 sample dataset. It should run immediately after unzip.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run the built-in tests

```bash
python -m unittest discover -s tests
```

## Validate configs

```bash
python -m adm_harness.cli validate -c configs/v5_service_baseline.yaml --output-json runs/validation_baseline.json
python -m adm_harness.cli validate -c configs/v5_service_flow_off.yaml --output-json runs/validation_flow_off.json
python -m adm_harness.cli validate -c configs/v5_service_identity_synthesis.yaml --output-json runs/validation_identity.json
python -m adm_harness.cli validate -c configs/v5_service_carrying_flow_localizer.yaml --output-json runs/validation_localizer.json
```

## Run the smoke suite

```bash
python -m adm_harness.cli run -c configs/v5_service_baseline.yaml
python -m adm_harness.cli run -c configs/v5_service_flow_off.yaml
python -m adm_harness.cli run -c configs/v5_service_identity_synthesis.yaml
python -m adm_harness.cli run -c configs/v5_service_carrying_flow_localizer.yaml
python -m adm_harness.cli compare --runs runs/v5_service_flow_off runs/v5_service_identity_synthesis runs/v5_service_carrying_flow_localizer --output-dir runs/comparison_v5_smoke
```

Or run the same sequence with:

```bash
bash scripts/run_local_smoke.sh
```

## Send results back

After the smoke suite finishes, create a results ZIP:

```bash
python scripts/collect_results.py --runs runs --output local_test_results.zip
```

Upload `local_test_results.zip` here. The most useful files are `decision_sheet.csv`, `status.json`, `validation_report.json`, `field_delta_summary.csv`, `service_modifier_summary.csv`, and `comparison_report.md`.

## Config path policy

All included configs use paths relative to the config file location. No `/mnt/data` or machine-local paths are required.

## Service-facing names

Public configs and outputs use service terms:

- `carrying_flow`
- `clock_lapse`
- `rail_stretch`
- `throat_capacity`
- `carrying_flow_off`

The loader still accepts legacy internal array keys from older bundles where needed, but generated configs and reports use service-facing names.
