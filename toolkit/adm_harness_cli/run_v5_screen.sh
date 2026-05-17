#!/usr/bin/env bash
set -euo pipefail

BASE_CONFIG="configs/v5_service_carrying_flow_localizer.yaml"
OUT_ROOT="runs/v5_screen"
CONFIG_ROOT="configs/v5_screen"
BASELINE_RUN="runs/v5_screen/baseline_flow_off"
RESULT_ZIP="v5_screen_results.zip"

mkdir -p "$OUT_ROOT" "$CONFIG_ROOT"

echo "Preparing V=5 one-factor screen configs..."

python - <<'PY'
from pathlib import Path
import copy
import yaml

base_path = Path("configs/v5_service_carrying_flow_localizer.yaml")
config_root = Path("configs/v5_screen")
config_root.mkdir(parents=True, exist_ok=True)

with base_path.open("r", encoding="utf-8") as f:
    base = yaml.safe_load(f)

def set_nested(d, path, value):
    cur = d
    for key in path[:-1]:
        cur = cur.setdefault(key, {})
    cur[path[-1]] = value

def make_config(name, changes):
    cfg = copy.deepcopy(base)
    cfg["run_name"] = name

    # Ensure synthesis/control layer is enabled.
    set_nested(cfg, ["service", "carrying_flow", "enabled"], True)
    set_nested(cfg, ["service", "carrying_flow", "law"], "compact_momentum_localizer")
    set_nested(cfg, ["service", "carrying_flow", "scope"], "catch_rematch_edge_support_mix")
    set_nested(cfg, ["service", "carrying_flow", "allocation_mode"], "edge_support_mix")

    for path, value in changes.items():
        set_nested(cfg, path.split("."), value)

    out = config_root / f"{name}.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

variants = []

# Baseline localizer amplitudes.
for amp in [0.001, 0.002, 0.004, 0.008, 0.012]:
    variants.append((
        f"amp_{str(amp).replace('.', 'p')}",
        {
            "service.carrying_flow.amplitude": amp,
            "service.carrying_flow.max_abs_change": amp,
        },
    ))

# Support-shell allocation.
for gain in [0.25, 0.5, 1.0, 2.0, 3.0]:
    variants.append((
        f"support_gain_{str(gain).replace('.', 'p')}",
        {"service.carrying_flow.support_shell_gain": gain},
    ))

# Packet exclusion.
for excl in [0.0, 0.2, 0.5, 0.8, 0.95]:
    variants.append((
        f"packet_exclusion_{str(excl).replace('.', 'p')}",
        {"service.carrying_flow.packet_exclusion": excl},
    ))

# Edge bias.
for bias in [0.0, 0.25, 0.5, 0.75, 1.0]:
    variants.append((
        f"edge_bias_{str(bias).replace('.', 'p')}",
        {"service.carrying_flow.edge_bias": bias},
    ))

# Widths.
for width in [0.5, 0.75, 1.0, 1.5, 2.0]:
    variants.append((
        f"temporal_width_{str(width).replace('.', 'p')}",
        {"service.carrying_flow.temporal_width": width},
    ))

for width in [0.5, 0.75, 1.0, 1.5, 2.0]:
    variants.append((
        f"radial_width_{str(width).replace('.', 'p')}",
        {"service.carrying_flow.radial_width": width},
    ))

# Timing/lead.
for lead in [-0.75, -0.5, 0.0, 0.5, 0.75]:
    variants.append((
        f"catch_lead_{str(lead).replace('-', 'm').replace('.', 'p')}",
        {"service.carrying_flow.catch_lead": lead},
    ))

for name, changes in variants:
    make_config(name, changes)

print(f"Wrote {len(variants)} configs to {config_root}")
PY

echo "Running baseline flow-off reference..."
python -m adm_harness.cli validate \
  -c configs/v5_service_flow_off.yaml \
  --output-json "$OUT_ROOT/validation_baseline_flow_off.json"

python -m adm_harness.cli run \
  -c configs/v5_service_flow_off.yaml \
  --output-dir "$BASELINE_RUN"

echo "Running screen variants..."
RUN_DIRS=("$BASELINE_RUN")

for cfg in "$CONFIG_ROOT"/*.yaml; do
  name="$(basename "$cfg" .yaml)"
  run_dir="$OUT_ROOT/$name"
  validation_json="$OUT_ROOT/validation_$name.json"

  echo "==> $name"

  python -m adm_harness.cli validate \
    -c "$cfg" \
    --output-json "$validation_json"

  python -m adm_harness.cli run \
    -c "$cfg" \
    --output-dir "$run_dir"

  RUN_DIRS+=("$run_dir")
done

echo "Comparing all runs..."
python -m adm_harness.cli compare \
  --runs "${RUN_DIRS[@]}" \
  --output-dir "$OUT_ROOT/comparison"

echo "Collecting decision sheets..."
python - <<'PY'
from pathlib import Path
import pandas as pd

root = Path("runs/v5_screen")
rows = []

for sheet in sorted(root.glob("*/decision_sheet.csv")):
    if "comparison" in sheet.parts:
        continue
    df = pd.read_csv(sheet)
    df.insert(0, "run_dir", str(sheet.parent))
    rows.append(df)

if rows:
    out = pd.concat(rows, ignore_index=True)
    out.to_csv(root / "all_decision_sheets.csv", index=False)
    print(f"Wrote {root / 'all_decision_sheets.csv'}")
else:
    print("No decision sheets found.")
PY

echo "Creating ZIP..."
rm -f "$RESULT_ZIP"
zip -r "$RESULT_ZIP" "$OUT_ROOT" "$CONFIG_ROOT" >/dev/null

echo
echo "Done."
echo "Upload this file:"
echo "$RESULT_ZIP"