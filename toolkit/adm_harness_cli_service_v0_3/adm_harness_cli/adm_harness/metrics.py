from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


FIELD_COLUMNS = [
    "alpha",
    "beta",
    "gamma_ll",
    "gamma_omega",
    "packet_norm",
    "gtt",
    "k_l",
    "k_omega",
    "K",
    "R3",
    "rho",
    "j_l",
]

DELTA_MAP = {
    "flow_off": ("delta_betaoff_rho", "delta_betaoff_j_l"),
    "carrying_flow_off": ("delta_betaoff_rho", "delta_betaoff_j_l"),
    "shift_off": ("delta_betaoff_rho", "delta_betaoff_j_l"),
    "betaoff": ("delta_betaoff_rho", "delta_betaoff_j_l"),
    "beta_off": ("delta_betaoff_rho", "delta_betaoff_j_l"),
    "time_matched_betaoff": ("delta_betaoff_rho", "delta_betaoff_j_l"),
    "static": ("delta_static_rho", "delta_static_j_l"),
    "static_ready": ("delta_static_rho", "delta_static_j_l"),
    "none": (None, None),
    None: (None, None),
}

MASK_COLS = [
    "inside_packet_live",
    "packet_core",
    "packet_edge_strip",
    "packet_inner_edge",
    "packet_outer_edge",
    "packet_live",
    "packet_edge",
    "support_shell",
]


@dataclass
class GateThresholds:
    max_abs_delta_rho_packet: float | None = None
    max_abs_delta_j_packet: float | None = None
    min_catch_rematch_localization_fraction: float | None = None
    min_support_shell_load_fraction: float | None = None

    @classmethod
    def from_config(cls, cfg: dict) -> "GateThresholds":
        return cls(
            max_abs_delta_rho_packet=cfg.get("max_abs_delta_rho_packet"),
            max_abs_delta_j_packet=cfg.get("max_abs_delta_j_packet"),
            min_catch_rematch_localization_fraction=cfg.get("min_catch_rematch_localization_fraction"),
            min_support_shell_load_fraction=cfg.get("min_support_shell_load_fraction"),
        )


def _flat_grid(fields: dict[str, np.ndarray]) -> pd.DataFrame:
    s = fields["s_grid"]
    l = fields["l_grid"]
    ss, ll = np.meshgrid(s, l, indexing="ij")
    return pd.DataFrame({"s": ss.ravel(), "l": ll.ravel()})


def _as_bool_array(x: np.ndarray) -> np.ndarray:
    if x.dtype == bool:
        return x
    return x.astype(bool)


def build_point_ledger(
    exact_fields: dict[str, np.ndarray],
    velocity: float | None,
    point_ledger_path: str | Path | None = None,
    substrate_fields: dict[str, np.ndarray] | None = None,
    substrate_mode: str | None = None,
    recompute_substrate_delta: bool = False,
) -> pd.DataFrame:
    """Build one flattened point ledger from exact field arrays and optional bundle ledgers."""
    base: pd.DataFrame | None = None
    if point_ledger_path:
        raw = pd.read_csv(point_ledger_path)
        if velocity is not None and "V" in raw.columns:
            raw = raw[np.isclose(raw["V"].astype(float), float(velocity))].copy()
        base = raw.reset_index(drop=True)
        # Keep all descriptive columns, but overwrite numeric field values from NPZ below.
        if len(base) != exact_fields["rho"].size:
            raise ValueError(
                f"Point ledger row count {len(base)} does not match field grid size {exact_fields['rho'].size}."
            )
    else:
        base = _flat_grid(exact_fields)
        if velocity is not None:
            base.insert(0, "V", float(velocity))
        base["stage"] = "unknown"
        base["region"] = "unknown"

    for col in FIELD_COLUMNS:
        if col in exact_fields:
            base[col] = exact_fields[col].ravel()

    # Use cell volume from point ledger if present; otherwise use substrate volume; otherwise 1.
    if "cell_volume" not in base.columns:
        if substrate_fields is not None and "volume" in substrate_fields:
            base["cell_volume"] = substrate_fields["volume"].ravel()
        else:
            base["cell_volume"] = 1.0
    base["volume"] = base["cell_volume"]

    if substrate_fields is not None:
        # Preserve masks from the subtraction bundle when available.
        mask_sources = {
            "packet_live": "packet_live",
            "packet_edge": "packet_edge",
            "support_shell": "support_shell",
        }
        for out_col, arr_key in mask_sources.items():
            if arr_key in substrate_fields:
                base[out_col] = _as_bool_array(substrate_fields[arr_key]).ravel()
        mode_key = str(substrate_mode).lower() if substrate_mode is not None else substrate_mode
        d_rho, d_j = DELTA_MAP.get(substrate_mode, DELTA_MAP.get(mode_key, (None, None)))
        if recompute_substrate_delta:
            if mode_key in {"flow_off", "carrying_flow_off", "shift_off", "betaoff", "beta_off", "time_matched_betaoff"}:
                if "betaoff_rho" not in substrate_fields or "betaoff_j_l" not in substrate_fields:
                    raise KeyError("Cannot recompute carrying-flow-off deltas without substrate betaoff_rho and betaoff_j_l arrays.")
                base["delta_rho"] = base["rho"].to_numpy() - substrate_fields["betaoff_rho"].ravel()
                base["delta_j_l"] = base["j_l"].to_numpy() - substrate_fields["betaoff_j_l"].ravel()
            elif mode_key in {"static", "static_ready"}:
                if "static_rho" not in substrate_fields or "static_j_l" not in substrate_fields:
                    raise KeyError("Cannot recompute static deltas without substrate static_rho and static_j_l arrays.")
                base["delta_rho"] = base["rho"].to_numpy() - substrate_fields["static_rho"].ravel()
                base["delta_j_l"] = base["j_l"].to_numpy() - substrate_fields["static_j_l"].ravel()
        else:
            if d_rho and d_rho in substrate_fields:
                base["delta_rho"] = substrate_fields[d_rho].ravel()
            if d_j and d_j in substrate_fields:
                base["delta_j_l"] = substrate_fields[d_j].ravel()
    if "delta_rho" not in base.columns:
        base["delta_rho"] = 0.0
    if "delta_j_l" not in base.columns:
        base["delta_j_l"] = 0.0

    # Harmonize mask names.
    if "inside_packet_live" not in base.columns and "packet_live" in base.columns:
        base["inside_packet_live"] = base["packet_live"].astype(bool)
    if "packet_live" not in base.columns and "inside_packet_live" in base.columns:
        base["packet_live"] = base["inside_packet_live"].astype(bool)
    if "packet_edge_strip" not in base.columns and "packet_edge" in base.columns:
        base["packet_edge_strip"] = base["packet_edge"].astype(bool)
    if "packet_edge" not in base.columns and "packet_edge_strip" in base.columns:
        base["packet_edge"] = base["packet_edge_strip"].astype(bool)
    for col in MASK_COLS:
        if col in base.columns:
            base[col] = base[col].astype(bool)

    # Useful absolute columns.
    for col in ["rho", "j_l", "delta_rho", "delta_j_l"]:
        base[f"abs_{col}"] = base[col].abs()
        base[f"weighted_abs_{col}"] = base[f"abs_{col}"] * base["volume"].astype(float)
        base[f"weighted_{col}"] = base[col] * base["volume"].astype(float)
    return base


def _mask(df: pd.DataFrame, name: str) -> pd.Series:
    if name in df.columns:
        return df[name].astype(bool)
    if name == "global":
        return pd.Series(True, index=df.index)
    if name == "packet_core" and "packet_live" in df.columns and "packet_edge" in df.columns:
        return df["packet_live"].astype(bool) & ~df["packet_edge"].astype(bool)
    return pd.Series(False, index=df.index)


def burden_for(df: pd.DataFrame, channel: str, mask: pd.Series | np.ndarray | None = None) -> dict:
    if mask is None:
        sub = df
    else:
        sub = df.loc[mask]
    if len(sub) == 0:
        return {
            "points": 0,
            "abs_burden": 0.0,
            "signed_burden": 0.0,
            "neg_burden": 0.0,
            "pos_burden": 0.0,
            "peak_abs": float("nan"),
            "peak_signed": float("nan"),
            "min_signed": float("nan"),
        }
    vals = sub[channel].astype(float)
    vol = sub["volume"].astype(float)
    weighted = vals * vol
    return {
        "points": int(len(sub)),
        "abs_burden": float((vals.abs() * vol).sum()),
        "signed_burden": float(weighted.sum()),
        "neg_burden": float((-weighted[weighted < 0]).sum()),
        "pos_burden": float(weighted[weighted > 0].sum()),
        "peak_abs": float(vals.abs().max()),
        "peak_signed": float(vals.max()),
        "min_signed": float(vals.min()),
    }


def stage_region_burdens(df: pd.DataFrame, channels: Iterable[str]) -> pd.DataFrame:
    rows = []
    if "stage" not in df.columns:
        df = df.assign(stage="unknown")
    if "region" not in df.columns:
        df = df.assign(region="unknown")
    for channel in channels:
        global_abs = burden_for(df, channel)["abs_burden"]
        grouped = df.groupby(["stage", "region"], dropna=False)
        for (stage, region), sub in grouped:
            b = burden_for(sub, channel)
            rows.append(
                {
                    "channel": channel,
                    "stage": stage,
                    "region": region,
                    **b,
                    "fraction_of_global_abs": b["abs_burden"] / global_abs if global_abs else 0.0,
                }
            )
    return pd.DataFrame(rows).sort_values(["channel", "fraction_of_global_abs"], ascending=[True, False])


def scope_burdens(df: pd.DataFrame, channels: Iterable[str]) -> pd.DataFrame:
    scopes = [
        "global",
        "packet_live",
        "packet_core",
        "packet_edge",
        "packet_edge_strip",
        "support_shell",
    ]
    rows = []
    for channel in channels:
        gb = burden_for(df, channel)
        for scope in scopes:
            m = _mask(df, scope)
            if scope not in df.columns and scope not in {"global", "packet_core"}:
                continue
            b = burden_for(df, channel, m)
            rows.append({
                "channel": channel,
                "scope": scope,
                **b,
                "fraction_of_global_abs": b["abs_burden"] / gb["abs_burden"] if gb["abs_burden"] else 0.0,
                "fraction_of_global_neg": b["neg_burden"] / gb["neg_burden"] if gb["neg_burden"] else 0.0,
            })
    return pd.DataFrame(rows)


def packet_exposure(df: pd.DataFrame) -> pd.DataFrame:
    channels = ["rho", "j_l", "delta_rho", "delta_j_l"]
    scopes = ["packet_live", "packet_core", "packet_edge", "packet_edge_strip"]
    rows = []
    for channel in channels:
        global_abs = burden_for(df, channel)["abs_burden"]
        for scope in scopes:
            if scope not in df.columns and scope != "packet_core":
                continue
            b = burden_for(df, channel, _mask(df, scope))
            rows.append({
                "channel": channel,
                "scope": scope,
                **b,
                "fraction_of_global_abs": b["abs_burden"] / global_abs if global_abs else 0.0,
            })
    return pd.DataFrame(rows)


def support_shell_load(df: pd.DataFrame) -> pd.DataFrame:
    channels = ["rho", "j_l", "delta_rho", "delta_j_l"]
    rows = []
    shell_mask = _mask(df, "support_shell")
    for channel in channels:
        gb = burden_for(df, channel)
        sb = burden_for(df, channel, shell_mask)
        rows.append({
            "channel": channel,
            **sb,
            "global_abs_burden": gb["abs_burden"],
            "support_shell_load_fraction": sb["abs_burden"] / gb["abs_burden"] if gb["abs_burden"] else 0.0,
        })
    return pd.DataFrame(rows)


def catch_rematch_localization(df: pd.DataFrame) -> pd.DataFrame:
    channels = ["rho", "j_l", "delta_rho", "delta_j_l"]
    stage_mask = df.get("stage", pd.Series("", index=df.index)).astype(str).eq("catch_rematch")
    rows = []
    for channel in channels:
        gb = burden_for(df, channel)
        cb = burden_for(df, channel, stage_mask)
        packet_cb = burden_for(df, channel, stage_mask & _mask(df, "packet_live"))
        support_cb = burden_for(df, channel, stage_mask & _mask(df, "support_shell"))
        rows.append({
            "channel": channel,
            "catch_abs_burden": cb["abs_burden"],
            "catch_points": cb["points"],
            "catch_fraction_of_global_abs": cb["abs_burden"] / gb["abs_burden"] if gb["abs_burden"] else 0.0,
            "catch_packet_abs_burden": packet_cb["abs_burden"],
            "catch_packet_fraction_of_global_abs": packet_cb["abs_burden"] / gb["abs_burden"] if gb["abs_burden"] else 0.0,
            "catch_support_abs_burden": support_cb["abs_burden"],
            "catch_support_fraction_of_global_abs": support_cb["abs_burden"] / gb["abs_burden"] if gb["abs_burden"] else 0.0,
            "peak_abs_in_catch": cb["peak_abs"],
        })
    return pd.DataFrame(rows)


def peak_locations(df: pd.DataFrame, channels: Iterable[str]) -> pd.DataFrame:
    rows = []
    for channel in channels:
        if channel not in df.columns or len(df) == 0:
            continue
        idx = df[channel].abs().idxmax()
        row = df.loc[idx]
        rows.append({
            "channel": channel,
            "peak_abs": float(abs(row[channel])),
            "signed_value": float(row[channel]),
            "s": float(row["s"]),
            "l": float(row["l"]),
            "stage": row.get("stage", "unknown"),
            "region": row.get("region", "unknown"),
            "inside_packet_live": bool(row.get("inside_packet_live", False)),
            "packet_edge": bool(row.get("packet_edge", row.get("packet_edge_strip", False))),
            "support_shell": bool(row.get("support_shell", False)),
        })
    return pd.DataFrame(rows)


def decision_sheet(
    df: pd.DataFrame,
    run_name: str,
    velocity: float | None,
    absorber_mode: str | None,
    substrate_mode: str | None,
    thresholds: GateThresholds,
    absorber_summary: dict | None = None,
) -> pd.DataFrame:
    packet = _mask(df, "packet_live")
    support = _mask(df, "support_shell")
    catch = df.get("stage", pd.Series("", index=df.index)).astype(str).eq("catch_rematch")

    d_rho_packet = burden_for(df, "delta_rho", packet)
    d_j_packet = burden_for(df, "delta_j_l", packet)
    d_j_global = burden_for(df, "delta_j_l")
    d_j_catch = burden_for(df, "delta_j_l", catch)
    d_j_support = burden_for(df, "delta_j_l", support)
    rho_packet = burden_for(df, "rho", packet)

    catch_frac = d_j_catch["abs_burden"] / d_j_global["abs_burden"] if d_j_global["abs_burden"] else 0.0
    support_frac = d_j_support["abs_burden"] / d_j_global["abs_burden"] if d_j_global["abs_burden"] else 0.0
    packet_exposure_score = d_rho_packet["abs_burden"] / rho_packet["abs_burden"] if rho_packet["abs_burden"] else 0.0

    passes_packet_rho = (
        True if thresholds.max_abs_delta_rho_packet is None else d_rho_packet["peak_abs"] <= thresholds.max_abs_delta_rho_packet
    )
    passes_packet_j = (
        True if thresholds.max_abs_delta_j_packet is None else d_j_packet["peak_abs"] <= thresholds.max_abs_delta_j_packet
    )
    passes_catch_j = (
        True if thresholds.min_catch_rematch_localization_fraction is None else catch_frac >= thresholds.min_catch_rematch_localization_fraction
    )
    passes_support = (
        True if thresholds.min_support_shell_load_fraction is None else support_frac >= thresholds.min_support_shell_load_fraction
    )
    recommended = "review"
    if passes_packet_rho and passes_packet_j and passes_catch_j and passes_support:
        recommended = "promote_or_compare"
    elif not passes_packet_rho or not passes_packet_j:
        recommended = "do_not_promote_packet_exposure"
    elif not passes_catch_j:
        recommended = "retune_catch_localization"
    elif not passes_support:
        recommended = "retune_support_shell_load"

    row = {
        "run_name": run_name,
        "velocity": velocity,
        "absorber_mode": absorber_mode or "none",
        "substrate_mode": substrate_mode or "none",
        "max_abs_delta_rho_packet": d_rho_packet["peak_abs"],
        "max_abs_delta_j_packet": d_j_packet["peak_abs"],
        "max_abs_delta_j_catch": d_j_catch["peak_abs"],
        "delta_j_catch_abs_burden": d_j_catch["abs_burden"],
        "delta_j_global_abs_burden": d_j_global["abs_burden"],
        "support_shell_load_fraction": support_frac,
        "catch_rematch_localization_fraction": catch_frac,
        "packet_exposure_score": packet_exposure_score,
        "passes_packet_rho_gate": passes_packet_rho,
        "passes_packet_j_gate": passes_packet_j,
        "passes_catch_j_gate": passes_catch_j,
        "passes_support_shell_gate": passes_support,
        "recommended_next_step": recommended,
    }
    if absorber_summary:
        row.update({f"absorber_{k}": v for k, v in absorber_summary.items()})
    return pd.DataFrame([row])


def summarize_absorber(absorber_cfg: dict) -> dict:
    """Read optional absorber score/fit files and return compact sidecar metrics."""
    mode = absorber_cfg.get("mode", "none")
    out: dict = {"mode": mode}
    fit_summary = absorber_cfg.get("fit_summary")
    candidate_scores = absorber_cfg.get("candidate_scores")
    selected = absorber_cfg.get("selected_fit") or absorber_cfg.get("selected_candidate")
    if fit_summary and Path(fit_summary).exists():
        df = pd.read_csv(fit_summary)
        key_col = "fit" if "fit" in df.columns else df.columns[0]
        if selected and selected in set(df[key_col].astype(str)):
            row = df[df[key_col].astype(str) == str(selected)].iloc[0]
        else:
            # Prefer the explicit mode when possible.
            matches = df[df[key_col].astype(str).str.contains(str(mode), case=False, regex=False)]
            row = matches.iloc[0] if len(matches) else df.iloc[-1]
        out.update({
            "fit": str(row.get(key_col)),
            "underfit_live_catch_fraction": float(row.get("underfit_live_catch_fraction", np.nan)),
            "l1_live_catch_fraction": float(row.get("l1_live_catch_fraction", np.nan)),
            "rnorm_weighted_l2": float(row.get("rnorm_weighted_l2", np.nan)),
        })
    if candidate_scores and Path(candidate_scores).exists():
        df = pd.read_csv(candidate_scores)
        if selected and "candidate" in df.columns and selected in set(df["candidate"].astype(str)):
            row = df[df["candidate"].astype(str) == str(selected)].iloc[0]
        elif "selection_score_lower_better" in df.columns:
            row = df.sort_values("selection_score_lower_better").iloc[0]
        else:
            row = df.iloc[0]
        out.update({
            "candidate": str(row.get("candidate", "unknown")),
            "coverage_pct_of_target_underfit": float(row.get("coverage_pct_of_target_underfit", np.nan)),
            "post_absorber_live_catch_underfit_pct_of_actual": float(row.get("post_absorber_live_catch_underfit_pct_of_actual", np.nan)),
            "selection_score_lower_better": float(row.get("selection_score_lower_better", np.nan)),
        })
    return out
