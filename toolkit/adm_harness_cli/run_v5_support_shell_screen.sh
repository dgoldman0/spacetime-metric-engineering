#!/usr/bin/env bash
set -euo pipefail

OUT_ROOT="runs/v5_support_shell_screen"
RESULT_ZIP="v5_support_shell_results.zip"

BASE_CONFIG="configs/v5_service_carrying_flow_localizer.yaml"
FLOW_OFF_CONFIG="configs/v5_service_flow_off.yaml"

rm -f configs/screen_v5_support_shell_*.yaml
rm -rf "$OUT_ROOT"
mkdir -p "$OUT_ROOT"

echo "Preparing V=5 support-shell ansatz screen configs..."

python - <<'PY'
from pathlib import Path
import copy
import yaml

base_path = Path("configs/v5_service_carrying_flow_localizer.yaml")
with base_path.open("r", encoding="utf-8") as f:
    base = yaml.safe_load(f)

def token(value):
    return str(value).replace("-", "m").replace(".", "p")

def set_nested(d, path, value):
    cur = d
    for key in path[:-1]:
        cur = cur.setdefault(key, {})
    cur[path[-1]] = value

def make_config(name, changes):
    cfg = copy.deepcopy(base)
    cfg["run_name"] = name

    carry = cfg.setdefault("service", {}).setdefault("carrying_flow", {})
    carry.update({
        "enabled": True,
        "target_service_field": "carrying_flow",
        "signal": "delta_j_l",
        "scope": "catch_rematch_support_shell",
        "allocation_mode": "support_shell",
        "packet_exclusion": 1.0,
        "edge_bias": 0.0,
        "support_shell_gain": 0.0,
        "smoothness_order": 1,
        "catch_lead": 0.5,
        "temporal_width": 0.5,
    })

    for path, value in changes.items():
        set_nested(cfg, path.split("."), value)

    out = Path("configs") / f"screen_v5_support_shell_{name}.yaml"
    with out.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

variants = []

# Compact support-shell localizer: low burden, tests whether the existing
# momentum-following law can be constrained to the shell.
for amp in [0.0005, 0.001, 0.002, 0.004]:
    for lead in [0.0, 0.5, 0.75]:
        for width in [0.35, 0.5, 0.75]:
            variants.append((
                f"compact_a{token(amp)}_lead{token(lead)}_tw{token(width)}",
                {
                    "service.carrying_flow.law": "compact_momentum_localizer",
                    "service.carrying_flow.scope": "catch_rematch_support_shell",
                    "service.carrying_flow.allocation_mode": "support_shell",
                    "service.carrying_flow.amplitude": amp,
                    "service.carrying_flow.max_abs_change": amp,
                    "service.carrying_flow.catch_lead": lead,
                    "service.carrying_flow.temporal_width": width,
                },
            ))

# Support-heavy mixed localizer: allows the mixed-window machinery, but erases
# packet-side allocation before smoothing.
for amp in [0.001, 0.002]:
    for lead in [0.5, 0.75]:
        for gain in [2.0, 5.0, 10.0]:
            variants.append((
                f"mixed_a{token(amp)}_lead{token(lead)}_gain{token(gain)}",
                {
                    "service.carrying_flow.law": "compact_momentum_localizer",
                    "service.carrying_flow.scope": "catch_rematch_edge_support_mix",
                    "service.carrying_flow.allocation_mode": "edge_support_mix",
                    "service.carrying_flow.packet_exclusion": 1.0,
                    "service.carrying_flow.support_shell_gain": gain,
                    "service.carrying_flow.amplitude": amp,
                    "service.carrying_flow.max_abs_change": amp,
                    "service.carrying_flow.catch_lead": lead,
                    "service.carrying_flow.temporal_width": 0.5,
                },
            ))

# Direct support-shell adjustment: tests a support-bearing control ansatz that
# does not follow the packet-dominated delta_j_l signal.
for amp in [1e-7, 2.5e-7, 5e-7, 1e-6, 2.5e-6, 5e-6, 1e-5]:
    for sign_name, sign in [("pos", 1.0), ("neg", -1.0)]:
        for lead in [0.5, 0.75]:
            variants.append((
                f"window_{sign_name}_a{token(amp)}_lead{token(lead)}",
                {
                    "service.carrying_flow.law": "windowed_adjustment",
                    "service.carrying_flow.scope": "catch_rematch_support_shell",
                    "service.carrying_flow.allocation_mode": "support_shell",
                    "service.carrying_flow.amplitude": sign * amp,
                    "service.carrying_flow.max_abs_change": amp,
                    "service.carrying_flow.catch_lead": lead,
                    "service.carrying_flow.temporal_width": 0.5,
                },
            ))

for name, changes in variants:
    make_config(name, changes)

print(f"Wrote {len(variants)} configs into configs/")
PY

echo "Running baseline flow-off reference..."
python -m adm_harness.cli validate \
  -c "$FLOW_OFF_CONFIG" \
  --output-json "$OUT_ROOT/validation_baseline_flow_off.json"

python -m adm_harness.cli run \
  -c "$FLOW_OFF_CONFIG" \
  --output-dir "$OUT_ROOT"

echo "Running support-shell ansatz variants..."
RUN_DIRS=("$OUT_ROOT/v5_service_flow_off")

for cfg in configs/screen_v5_support_shell_*.yaml; do
  name="$(basename "$cfg" .yaml)"
  name="${name#screen_v5_support_shell_}"
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

echo "Scoring support-shell routing..."
python - <<'PY'
from pathlib import Path
import pandas as pd

root = Path("runs/v5_support_shell_screen")
baseline_dir = root / "v5_service_flow_off"
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
    packet_inc_j = float(abs_inc_j[packet].sum())
    packet_inc_rho = float(abs_inc_rho[packet].sum())

    catch_frac = catch_inc_j / global_inc_j if global_inc_j else 0.0
    support_frac = support_inc_j / global_inc_j if global_inc_j else 0.0
    catch_support_frac = catch_support_inc_j / global_inc_j if global_inc_j else 0.0
    packet_j_frac = packet_inc_j / global_inc_j if global_inc_j else 0.0
    support_to_packet_ratio = catch_support_inc_j / packet_inc_j if packet_inc_j else float("inf")

    # Lower is better. This ranking is deliberately support-bearing: it rewards
    # catch-support routing and penalizes packet-live momentum, packet density,
    # and excessive total added demand.
    support_routing_score = (
        (1.0 - catch_support_frac)
        + 10.0 * packet_j_frac
        + 1.0e6 * packet_inc_rho
    ) * (1.0 + global_inc_j / 1.0e-6)

    rows.append({
        "run_name": run_dir.name,
        "global_abs_incremental_delta_j_l": global_inc_j,
        "catch_abs_incremental_delta_j_l": catch_inc_j,
        "support_abs_incremental_delta_j_l": support_inc_j,
        "catch_support_abs_incremental_delta_j_l": catch_support_inc_j,
        "packet_abs_incremental_delta_j_l": packet_inc_j,
        "packet_abs_incremental_delta_rho": packet_inc_rho,
        "catch_incremental_fraction": catch_frac,
        "support_incremental_fraction": support_frac,
        "catch_support_incremental_fraction": catch_support_frac,
        "packet_incremental_j_fraction": packet_j_frac,
        "catch_support_to_packet_j_ratio": support_to_packet_ratio,
        "support_routing_score_lower_better": support_routing_score,
    })

summary = pd.DataFrame(rows)
if summary.empty:
    raise SystemExit("No run point ledgers found for support-shell routing summary.")

summary = summary.sort_values(["support_routing_score_lower_better", "global_abs_incremental_delta_j_l"])
summary.insert(0, "support_routing_rank", range(1, len(summary) + 1))
summary.to_csv(root / "support_shell_routing_summary.csv", index=False)
print(f"Wrote {root / 'support_shell_routing_summary.csv'}")

frontier_cols = [
    "run_name",
    "global_abs_incremental_delta_j_l",
    "catch_support_incremental_fraction",
    "packet_incremental_j_fraction",
    "packet_abs_incremental_delta_rho",
]
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
frontier.to_csv(root / "support_shell_pareto_frontier.csv", index=False)
print(f"Wrote {root / 'support_shell_pareto_frontier.csv'}")

with (root / "support_shell_routing_report.md").open("w", encoding="utf-8") as f:
    f.write("# V5 support-shell ansatz screen\n\n")
    f.write("Baseline: `v5_service_flow_off`. Incremental channels are pointwise run minus baseline before burden aggregation.\n\n")
    f.write("Lower `support_routing_score_lower_better` is better. The score rewards catch-support routing and penalizes packet-live momentum, packet density, and large total added demand.\n\n")
    f.write("## Top ranked candidates\n\n")
    f.write(summary.head(15).to_markdown(index=False))
    f.write("\n\n## Pareto frontier\n\n")
    f.write(frontier[frontier_cols].head(20).to_markdown(index=False))
    f.write("\n")
print(f"Wrote {root / 'support_shell_routing_report.md'}")
PY

echo "Creating ZIP..."
rm -f "$RESULT_ZIP"
zip -r "$RESULT_ZIP" "$OUT_ROOT" configs/screen_v5_support_shell_*.yaml >/dev/null

echo
echo "Done."
echo "Upload this file:"
echo "$RESULT_ZIP"
