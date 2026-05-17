#!/usr/bin/env bash
set -euo pipefail

OUT_ROOT="runs/v10_support_shell_edge"
RESULT_ZIP="v10_support_shell_edge_results.zip"

FLOW_OFF_CONFIG="configs/v10_service_flow_off.yaml"
TARGET_CONFIG="configs/v10_service_support_shell_target.yaml"

rm -f configs/screen_v10_support_shell_edge_*.yaml
rm -rf "$OUT_ROOT"
mkdir -p "$OUT_ROOT"

echo "Checking V=10 input artifacts..."
python - <<'PY'
from pathlib import Path
import shutil
import zipfile

artifacts = [
    (
        Path("../../included_bundles/exact_builder_adm_v5_bundle.zip"),
        "exact_builder_adm_v5/adm_exact_fields_V10p0.npz",
        Path("data/sample_v5/exact_builder_adm_v5/adm_exact_fields_V10p0.npz"),
    ),
    (
        Path("../../included_bundles/standing_substrate_subtraction_v10_bundle.zip"),
        "substrate_subtraction_fields_v10.npz",
        Path("data/sample_v5/substrate_subtraction_fields_v10.npz"),
    ),
]

for zip_path, member, out_path in artifacts:
    if out_path.exists():
        continue
    if not zip_path.exists():
        raise SystemExit(f"Missing bundle needed for {out_path}: {zip_path}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member) as src, out_path.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    print(f"extracted {out_path}")
PY

echo "Preparing focused V=10 support-shell edge configs..."
python - <<'PY'
from pathlib import Path
import copy
import yaml

base_path = Path("configs/v10_service_support_shell_target.yaml")
with base_path.open("r", encoding="utf-8") as f:
    base = yaml.safe_load(f)

def token(value):
    return str(value).replace("-", "m").replace(".", "p").replace("e-0", "em0").replace("e-", "em")

def set_nested(d, path, value):
    cur = d
    for key in path[:-1]:
        cur = cur.setdefault(key, {})
    cur[path[-1]] = value

variants = {}

def add_variant(name, amp, lead=0.75, width=0.5):
    variants[name] = {
        "service.carrying_flow.amplitude": amp,
        "service.carrying_flow.max_abs_change": abs(amp),
        "service.carrying_flow.catch_lead": lead,
        "service.carrying_flow.temporal_width": width,
    }

for amp in [5e-8, 1e-7, 2.5e-7, 5e-7, 1e-6, 2.5e-6]:
    for sign_name, sign in [("pos", 1.0), ("neg", -1.0)]:
        add_variant(f"amp_{sign_name}_{token(amp)}", sign * amp)

for lead in [0.0, 0.5, 0.75, 1.0, 1.25]:
    for sign_name, sign in [("pos", 1.0), ("neg", -1.0)]:
        add_variant(f"lead_{sign_name}_{token(lead)}", sign * 1e-7, lead=lead)

for width in [0.25, 0.35, 0.5, 0.75, 1.0]:
    for sign_name, sign in [("pos", 1.0), ("neg", -1.0)]:
        add_variant(f"tw_{sign_name}_{token(width)}", sign * 1e-7, width=width)

for name, changes in sorted(variants.items()):
    cfg = copy.deepcopy(base)
    cfg["run_name"] = name
    carry = cfg.setdefault("service", {}).setdefault("carrying_flow", {})
    carry.update({
        "enabled": True,
        "law": "windowed_adjustment",
        "scope": "catch_rematch_support_shell",
        "allocation_mode": "support_shell",
        "packet_exclusion": 1.0,
        "support_shell_gain": 0.0,
        "edge_bias": 0.0,
        "target_service_field": "carrying_flow",
        "smoothness_order": 1,
    })
    for path, value in changes.items():
        set_nested(cfg, path.split("."), value)

    out = Path("configs") / f"screen_v10_support_shell_edge_{name}.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

print(f"Wrote {len(variants)} configs into configs/")
PY

echo "Running V=10 flow-off edge reference..."
python -m adm_harness.cli validate \
  -c "$FLOW_OFF_CONFIG" \
  --output-json "$OUT_ROOT/validation_baseline_flow_off.json"

python -m adm_harness.cli run \
  -c "$FLOW_OFF_CONFIG" \
  --output-dir "$OUT_ROOT"

echo "Running promoted target..."
python -m adm_harness.cli validate \
  -c "$TARGET_CONFIG" \
  --output-json "$OUT_ROOT/validation_target.json"

python -m adm_harness.cli run \
  -c "$TARGET_CONFIG" \
  --output-dir "$OUT_ROOT"

RUN_DIRS=("$OUT_ROOT/v10_service_flow_off" "$OUT_ROOT/v10_support_shell_window_target")

echo "Running focused edge stress variants..."
for cfg in configs/screen_v10_support_shell_edge_*.yaml; do
  name="$(basename "$cfg" .yaml)"
  name="${name#screen_v10_support_shell_edge_}"
  validation_json="$OUT_ROOT/validation_$name.json"

  echo "==> $name"

  python -m adm_harness.cli validate \
    -c "$cfg" \
    --output-json "$validation_json"

  python -m adm_harness.cli run \
    -c "$cfg" \
    --output-dir "$OUT_ROOT"

  RUN_DIRS+=("$OUT_ROOT/$name")
done

echo "Comparing all runs..."
python -m adm_harness.cli compare \
  --runs "${RUN_DIRS[@]}" \
  --output-dir "$OUT_ROOT/comparison"

echo "Scoring V=10 support-shell edge routing..."
python - <<'PY'
from pathlib import Path
import pandas as pd

root = Path("runs/v10_support_shell_edge")
baseline_dir = root / "v10_service_flow_off"
baseline_path = baseline_dir / "point_ledger.csv"
if not baseline_path.exists():
    raise SystemExit(f"Missing baseline point ledger: {baseline_path}")

baseline = pd.read_csv(baseline_path)
required = {"s", "l", "delta_j_l", "delta_rho", "volume", "stage", "packet_live", "support_shell"}
missing = required - set(baseline.columns)
if missing:
    raise SystemExit(f"Baseline point ledger missing columns: {sorted(missing)}")

base = baseline[["s", "l", "delta_j_l", "delta_rho"]].rename(
    columns={"delta_j_l": "baseline_delta_j_l", "delta_rho": "baseline_delta_rho"}
)
base_global_delta_j = float((baseline["delta_j_l"].astype(float).abs() * baseline["volume"].astype(float)).sum())
base_packet_delta_rho = float(
    (baseline.loc[baseline["packet_live"].astype(bool), "delta_rho"].astype(float).abs()
     * baseline.loc[baseline["packet_live"].astype(bool), "volume"].astype(float)).sum()
)

decision_rows = {}
for sheet in sorted(root.glob("*/decision_sheet.csv")):
    if "comparison" in sheet.parts:
        continue
    row = pd.read_csv(sheet).iloc[0].to_dict()
    decision_rows[sheet.parent.name] = row

rows = []
for ledger_path in sorted(root.glob("*/point_ledger.csv")):
    run_dir = ledger_path.parent
    if run_dir == baseline_dir or "comparison" in ledger_path.parts:
        continue
    df = pd.read_csv(ledger_path)
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"{ledger_path} missing columns: {sorted(missing)}")

    merged = df.merge(base, on=["s", "l"], how="left", validate="one_to_one")
    if merged["baseline_delta_j_l"].isna().any():
        raise SystemExit(f"{ledger_path} did not align with baseline grid")

    vol = merged["volume"].astype(float)
    inc_j_signed = merged["delta_j_l"].astype(float) - merged["baseline_delta_j_l"].astype(float)
    inc_rho_signed = merged["delta_rho"].astype(float) - merged["baseline_delta_rho"].astype(float)
    abs_inc_j = inc_j_signed.abs() * vol
    abs_inc_rho = inc_rho_signed.abs() * vol

    packet = merged["packet_live"].astype(bool)
    support = merged["support_shell"].astype(bool)
    catch = merged["stage"].astype(str).eq("catch_rematch")
    catch_support = catch & support
    catch_packet = catch & packet

    global_inc_j = float(abs_inc_j.sum())
    catch_inc_j = float(abs_inc_j[catch].sum())
    support_inc_j = float(abs_inc_j[support].sum())
    catch_support_inc_j = float(abs_inc_j[catch_support].sum())
    catch_packet_inc_j = float(abs_inc_j[catch_packet].sum())
    packet_inc_j = float(abs_inc_j[packet].sum())
    packet_inc_rho = float(abs_inc_rho[packet].sum())

    catch_frac = catch_inc_j / global_inc_j if global_inc_j else 0.0
    support_frac = support_inc_j / global_inc_j if global_inc_j else 0.0
    catch_support_frac = catch_support_inc_j / global_inc_j if global_inc_j else 0.0
    catch_packet_frac = catch_packet_inc_j / global_inc_j if global_inc_j else 0.0
    packet_j_frac = packet_inc_j / global_inc_j if global_inc_j else 0.0
    support_to_packet_ratio = catch_support_inc_j / packet_inc_j if packet_inc_j else float("inf")

    # Lower is better. This intentionally scores the promoted ansatz as a
    # support-shell-routing control: high catch-support fraction, low packet
    # momentum, low packet density, and small added total burden.
    support_routing_score = (
        (1.0 - catch_support_frac)
        + 10.0 * packet_j_frac
        + 1.0e6 * packet_inc_rho
    ) * (1.0 + global_inc_j / 1.0e-6)

    decision = decision_rows.get(run_dir.name, {})
    rows.append({
        "run_name": run_dir.name,
        "global_abs_incremental_delta_j_l": global_inc_j,
        "catch_abs_incremental_delta_j_l": catch_inc_j,
        "support_abs_incremental_delta_j_l": support_inc_j,
        "catch_support_abs_incremental_delta_j_l": catch_support_inc_j,
        "catch_packet_abs_incremental_delta_j_l": catch_packet_inc_j,
        "packet_abs_incremental_delta_j_l": packet_inc_j,
        "packet_abs_incremental_delta_rho": packet_inc_rho,
        "catch_incremental_fraction": catch_frac,
        "support_incremental_fraction": support_frac,
        "catch_support_incremental_fraction": catch_support_frac,
        "catch_packet_incremental_fraction": catch_packet_frac,
        "packet_incremental_j_fraction": packet_j_frac,
        "catch_support_to_packet_j_ratio": support_to_packet_ratio,
        "global_incremental_j_fraction_of_baseline": global_inc_j / base_global_delta_j if base_global_delta_j else 0.0,
        "packet_incremental_rho_fraction_of_baseline_packet": packet_inc_rho / base_packet_delta_rho if base_packet_delta_rho else 0.0,
        "max_abs_delta_rho_packet": decision.get("max_abs_delta_rho_packet"),
        "max_abs_delta_j_packet": decision.get("max_abs_delta_j_packet"),
        "passes_packet_rho_gate": decision.get("passes_packet_rho_gate"),
        "passes_packet_j_gate": decision.get("passes_packet_j_gate"),
        "passes_catch_j_gate": decision.get("passes_catch_j_gate"),
        "support_routing_score_lower_better": support_routing_score,
    })

summary = pd.DataFrame(rows)
if summary.empty:
    raise SystemExit("No run point ledgers found for V=10 edge routing summary.")

summary = summary.sort_values(["support_routing_score_lower_better", "global_abs_incremental_delta_j_l"])
summary.insert(0, "support_routing_rank", range(1, len(summary) + 1))
summary.to_csv(root / "v10_support_shell_edge_summary.csv", index=False)
print(f"Wrote {root / 'v10_support_shell_edge_summary.csv'}")

frontier_rows = []
for _, row in summary.iterrows():
    dominated = False
    for _, other in summary.iterrows():
        if row["run_name"] == other["run_name"]:
            continue
        at_least_as_good = (
            other["global_abs_incremental_delta_j_l"] <= row["global_abs_incremental_delta_j_l"]
            and other["packet_incremental_j_fraction"] <= row["packet_incremental_j_fraction"]
            and other["packet_abs_incremental_delta_rho"] <= row["packet_abs_incremental_delta_rho"]
            and other["catch_support_incremental_fraction"] >= row["catch_support_incremental_fraction"]
        )
        strictly_better = (
            other["global_abs_incremental_delta_j_l"] < row["global_abs_incremental_delta_j_l"]
            or other["packet_incremental_j_fraction"] < row["packet_incremental_j_fraction"]
            or other["packet_abs_incremental_delta_rho"] < row["packet_abs_incremental_delta_rho"]
            or other["catch_support_incremental_fraction"] > row["catch_support_incremental_fraction"]
        )
        if at_least_as_good and strictly_better:
            dominated = True
            break
    if not dominated:
        frontier_rows.append(row)

frontier = pd.DataFrame(frontier_rows).sort_values("global_abs_incremental_delta_j_l")
frontier.to_csv(root / "v10_support_shell_edge_pareto_frontier.csv", index=False)
print(f"Wrote {root / 'v10_support_shell_edge_pareto_frontier.csv'}")

report_cols = [
    "support_routing_rank",
    "run_name",
    "global_abs_incremental_delta_j_l",
    "catch_support_incremental_fraction",
    "packet_incremental_j_fraction",
    "packet_abs_incremental_delta_rho",
    "global_incremental_j_fraction_of_baseline",
    "support_routing_score_lower_better",
]

with (root / "v10_support_shell_edge_report.md").open("w", encoding="utf-8") as f:
    f.write("# V10 support-shell target edge stress\n\n")
    f.write("Baseline: `v10_service_flow_off`. Incremental channels are pointwise run minus baseline before burden aggregation.\n\n")
    f.write(f"Baseline global abs `delta_j_l` burden: `{base_global_delta_j:.12g}`.\n\n")
    f.write("Lower `support_routing_score_lower_better` is better. The score rewards catch-support routing and penalizes packet-live momentum, packet density, and large total added demand.\n\n")
    f.write("## Top ranked candidates\n\n")
    f.write(summary[report_cols].head(15).to_markdown(index=False))
    f.write("\n\n## Promoted target row\n\n")
    target = summary[summary["run_name"].eq("v10_support_shell_window_target")]
    if len(target):
        f.write(target[report_cols].to_markdown(index=False))
    else:
        f.write("Target run not found in summary.")
    f.write("\n\n## Pareto frontier\n\n")
    f.write(frontier[report_cols].head(20).to_markdown(index=False))
    f.write("\n")
print(f"Wrote {root / 'v10_support_shell_edge_report.md'}")
PY

echo "Creating ZIP..."
rm -f "$RESULT_ZIP"
zip -r "$RESULT_ZIP" "$OUT_ROOT" configs/screen_v10_support_shell_edge_*.yaml >/dev/null

echo
echo "Done."
echo "Result bundle:"
echo "$RESULT_ZIP"
