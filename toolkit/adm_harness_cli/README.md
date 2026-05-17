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

## Run the validation ladder

The support-shell target can be checked with the staged validation ladder. The default run is the primary `V=5` service-factor case:

```bash
python scripts/run_validation_ladder.py
```

This runs the flow-off baseline, the promoted positive support-shell target, a generated negative counterpart, the packet-safety overlay on the matching tuned branch, the richer multi-channel source objective, the signed source/objective comparison, reduced balance bookkeeping, and a positive-amplitude load-bearing ramp. Outputs are written to `runs/<v_label>_validation_ladder/` unless `--output-root` is set.

For the `V=10` edge comparison, the same command infers the `V10` packet member and output directory from the configs:

```bash
python scripts/run_validation_ladder.py \
  --baseline-config configs/v10_service_flow_off.yaml \
  --target-config configs/v10_service_support_shell_target.yaml \
  --max-packet-j-fraction 1e-4 \
  --max-packet-abs-delta-rho 1e-12 \
  --max-rich-packet-increment-abs 1e-10
```

The old `scripts/run_v5_validation_ladder.py` entry point remains as a compatibility wrapper.

### Generate arbitrary service-factor inputs

For an intermediate or exploratory `V` value, the ladder can generate reduced ADM exact-field, substrate-subtraction, point-ledger, and config inputs before it runs:

```bash
python scripts/run_validation_ladder.py \
  --service-factor 7 \
  --generate-service-inputs \
  --skip-amplitude-ramp
```

The generated products are written under `data/generated_service_factors/<v_label>/` and `configs/generated/`, then the ladder consumes those products directly. This path is intended for service-factor hardening and interpolation checks between the tracked reference products. It uses the reduced ADM field builder; pressure/null 4D source projections remain separate heavier diagnostics.

Useful low-cost diagnostics are recorded in `validation_ladder_metadata.json` and `validation_ladder_decision_sheet.csv`, including generated-input provenance, packet norm counts, packet/source fractions, partition closure, and a `gate_margin` value for each hard decision row.

## Regenerate the 4D demanded-source ledger

The report-grade source ledger can be regenerated from the toolkit, rather than treated as an opaque bundle-only artifact:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --outdir runs/source_ledgers/V5_tuned_w0569_eta200
```

This computes the finite-difference demanded-source projections `T_munu = G_munu[g] / (8*pi)`, then writes point, summary, stage, safety, decision, top-bad-point, and manifest tables. Use `--reference` to compare a regenerated ledger to a saved artifact:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --reference ../../included_bundles/active_rail_v_sweep.zip::highres_41x73/V5_tuned_w0569_eta200.csv \
  --reference-case V5_tuned_w0569_eta200
```

The frozen support-shell carrying-flow overlay can be included directly in the metric expression:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --support-shell-overlay \
  --outdir runs/source_ledgers/V5_tuned_w0569_eta200_support_shell
```

The overlay defaults to the frozen reduced-harness target: amplitude `1e-7`, catch lead `1.0`, temporal width `0.35`, smoothness order `1`, packet exclusion `1.0`, and an annular support-shell band from `0.65 Rth` to `1.20 Rth`. The point ledger records `beta_base`, `support_shell_window`, and `support_shell_delta_beta` so the metric-side contribution can be audited separately from the baseline shaped-catch/radial-soft/lapse-cushion branch.

Overlay runs expand the default `s` range when needed to include the leading catch/support window while preserving roughly the standard `ds = 0.05` sampling. Pin `--s-min` and `--ns` explicitly when comparing against a fixed historical source-ledger grid.

To ramp the continuous overlay and compare each case against a matched baseline source ledger:

```bash
python scripts/run_source_overlay_sweep.py \
  --outdir runs/source_overlay_sweep_v5 \
  --amplitudes 1e-7 1e-6 1e-5 1e-4 1e-3 1e-2 \
  --signs pos neg
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
