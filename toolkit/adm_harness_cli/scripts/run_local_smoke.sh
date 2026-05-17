#!/usr/bin/env bash
set -euo pipefail
python -m unittest discover -s tests
python -m adm_harness.cli validate -c configs/v5_service_baseline.yaml --output-json runs/validation_baseline.json
python -m adm_harness.cli validate -c configs/v5_service_flow_off.yaml --output-json runs/validation_flow_off.json
python -m adm_harness.cli validate -c configs/v5_service_identity_synthesis.yaml --output-json runs/validation_identity.json
python -m adm_harness.cli validate -c configs/v5_service_carrying_flow_localizer.yaml --output-json runs/validation_localizer.json
python -m adm_harness.cli run -c configs/v5_service_baseline.yaml
python -m adm_harness.cli run -c configs/v5_service_flow_off.yaml
python -m adm_harness.cli run -c configs/v5_service_identity_synthesis.yaml
python -m adm_harness.cli run -c configs/v5_service_carrying_flow_localizer.yaml
python -m adm_harness.cli compare --runs runs/v5_service_flow_off runs/v5_service_identity_synthesis runs/v5_service_carrying_flow_localizer --output-dir runs/comparison_v5_smoke
python scripts/collect_results.py --runs runs --output local_test_results.zip
