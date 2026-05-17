from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path


def find_one(bundle_dir: Path, pattern: str) -> Path:
    matches = sorted(bundle_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No bundle matched {pattern!r} in {bundle_dir}")
    return matches[0]


def extract(zip_path: Path, out_dir: Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)


def write_config(
    path: Path,
    run_name: str,
    velocity: float,
    exact_fields: Path,
    point_ledger: Path,
    substrate_fields: Path | None,
    substrate_mode: str,
    synthesis: str,
) -> None:
    substrate_input = f"  substrate_fields: {substrate_fields}\n" if substrate_fields else ""
    text = f"""run_name: {run_name}

service:
  velocity: {velocity}
{synthesis}
inputs:
  exact_fields: {exact_fields}
  exact_point_ledger: {point_ledger}
{substrate_input}
substrate:
  mode: {substrate_mode}

outputs:
  root: runs
  format: csv
  figures: true
  report: true
  overwrite: true
"""
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare local ADM harness configs from uploaded bundles.")
    parser.add_argument("--bundle-dir", required=True, help="Directory containing the uploaded ZIP bundles")
    parser.add_argument("--data-dir", default="data", help="Where to extract bundle contents")
    parser.add_argument("--config-dir", default="configs/local", help="Where to write local runnable configs")
    args = parser.parse_args()

    bundle_dir = Path(args.bundle_dir).expanduser().resolve()
    data_dir = Path(args.data_dir).expanduser().resolve()
    config_dir = Path(args.config_dir).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    exact_zip = find_one(bundle_dir, "exact_builder_adm_v5_bundle*.zip")
    substrate_zip = find_one(bundle_dir, "standing_substrate_subtraction_v5_bundle*.zip")
    substrate_v10_zip = find_one(bundle_dir, "standing_substrate_subtraction_v10_bundle*.zip")
    extract(exact_zip, data_dir)
    extract(substrate_zip, data_dir)
    extract(substrate_v10_zip, data_dir)

    exact_fields_v5 = data_dir / "exact_builder_adm_v5" / "adm_exact_fields_V5p0.npz"
    exact_fields_v10 = data_dir / "exact_builder_adm_v5" / "adm_exact_fields_V10p0.npz"
    point_ledger = data_dir / "exact_builder_adm_v5" / "adm_exact_point_ledger_v5_v10.csv"
    substrate_fields_v5 = data_dir / "substrate_subtraction_fields_v5.npz"
    substrate_fields_v10 = data_dir / "substrate_subtraction_fields_v10.npz"

    for p in [exact_fields_v5, exact_fields_v10, point_ledger, substrate_fields_v5, substrate_fields_v10]:
        if not p.exists():
            raise FileNotFoundError(f"Expected extracted file missing: {p}")

    identity_block = "  carrying_flow:\n    enabled: true\n    law: identity\n    scope: global\n\nsynthesis:\n  enabled: true\n\nvalidation:\n  identity_self_check: true\n  identity_tolerance: 1.0e-10\n\n"
    localizer_block = "  carrying_flow:\n    enabled: true\n    law: compact_momentum_localizer\n    scope: catch_rematch_edge\n    signal: delta_j_l\n    amplitude: 0.002\n    gain: 1.0\n    max_abs_change: 0.002\n    smoothness_order: 2\n    packet_exclusion: 0.40\n    support_shell_gain: 0.50\n    edge_bias: 0.25\n\nsynthesis:\n  enabled: true\n\nvalidation:\n  identity_self_check: true\n  identity_tolerance: 1.0e-10\n\n"

    support_shell_target_block = "  carrying_flow:\n    enabled: true\n    law: windowed_adjustment\n    scope: catch_rematch_support_shell\n    allocation_mode: support_shell\n    signal: delta_j_l\n    amplitude: 0.0000001\n    gain: 1.0\n    max_abs_change: 0.0000001\n    smoothness_order: 1\n    packet_exclusion: 1.0\n    support_shell_gain: 0.0\n    edge_bias: 0.0\n    target_service_field: carrying_flow\n    catch_lead: 0.75\n    temporal_width: 0.5\n\nsynthesis:\n  enabled: true\n\nvalidation:\n  identity_self_check: true\n  identity_tolerance: 1.0e-10\n\n"

    write_config(config_dir / "v5_service_flow_off.yaml", "v5_service_flow_off", 5.0, exact_fields_v5, point_ledger, substrate_fields_v5, "carrying_flow_off", "")
    write_config(config_dir / "v5_service_identity_synthesis.yaml", "v5_service_identity_synthesis", 5.0, exact_fields_v5, point_ledger, substrate_fields_v5, "carrying_flow_off", identity_block)
    write_config(config_dir / "v5_service_carrying_flow_localizer.yaml", "v5_service_carrying_flow_localizer", 5.0, exact_fields_v5, point_ledger, substrate_fields_v5, "carrying_flow_off", localizer_block)
    write_config(config_dir / "v10_service_flow_off.yaml", "v10_service_flow_off", 10.0, exact_fields_v10, point_ledger, substrate_fields_v10, "carrying_flow_off", "")
    write_config(config_dir / "v10_service_support_shell_target.yaml", "v10_support_shell_window_target", 10.0, exact_fields_v10, point_ledger, substrate_fields_v10, "carrying_flow_off", support_shell_target_block)

    print(f"extracted bundles into {data_dir}")
    print(f"wrote configs into {config_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
