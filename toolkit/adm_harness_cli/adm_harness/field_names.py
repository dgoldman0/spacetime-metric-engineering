from __future__ import annotations

"""Canonical service vocabulary for the ADM harness.

The exact-builder bundles use compact ADM array keys internally. The public
config, reports, validation summaries, and generated ledgers use active-rail
service names so knobs describe what the service does.
"""

from typing import Any

# Internal keys are kept only because the existing NPZ/CSV bundles use them.
SERVICE_TO_INTERNAL = {
    "carrying_flow": "beta",
    "radial_carrying_flow": "beta",
    "carry_flow": "beta",
    "flow": "beta",
    # Legacy mathematical aliases are accepted for old configs and bundle
    # interoperability. New generated artifacts should not use these names.
    "beta": "beta",
    "shift_beta_l_contra": "beta",
    "beta_l_contra": "beta",
    "clock_lapse": "alpha",
    "service_clock": "alpha",
    "lapse": "alpha",
    "alpha": "alpha",
    "rail_stretch": "gamma_ll",
    "radial_geometry": "gamma_ll",
    "radial_stretch": "gamma_ll",
    "gamma_ll": "gamma_ll",
    "throat_capacity": "gamma_omega",
    "angular_capacity": "gamma_omega",
    "angular_geometry": "gamma_omega",
    "gamma_omega": "gamma_omega",
    "gamma_omegaomega": "gamma_omega",
}

INTERNAL_TO_SERVICE = {
    "beta": "carrying_flow",
    "alpha": "clock_lapse",
    "gamma_ll": "rail_stretch",
    "gamma_omega": "throat_capacity",
}

SUBSTRATE_MODE_ALIASES = {
    "flow_off": "carrying_flow_off",
    "carrying_flow_off": "carrying_flow_off",
    "carry_flow_off": "carrying_flow_off",
    # Legacy aliases accepted for old configs only.
    "shift_off": "carrying_flow_off",
    "shift_flow_off": "carrying_flow_off",
    "betaoff": "carrying_flow_off",
    "beta_off": "carrying_flow_off",
    "time_matched_betaoff": "carrying_flow_off",
    "static": "static",
    "static_ready": "static",
    "ready_geometry": "static",
    "none": "none",
    None: None,
}

FIELD_BLOCKS = {
    "carrying_flow": "beta",
    "clock_lapse": "alpha",
    "rail_stretch": "gamma_ll",
    "throat_capacity": "gamma_omega",
}

POSITIVE_SERVICE_FIELDS = {"clock_lapse", "rail_stretch", "throat_capacity"}
POSITIVE_INTERNAL_FIELDS = {"alpha", "gamma_ll", "gamma_omega"}

PUBLIC_COLUMN_RENAMES = {
    "alpha": "clock_lapse",
    "beta": "carrying_flow",
    "gamma_ll": "rail_stretch",
    "gamma_omega": "throat_capacity",
}


def internal_field_name(name: str | None) -> str:
    if not name:
        raise ValueError("service field name is required")
    key = str(name).strip()
    try:
        return SERVICE_TO_INTERNAL[key]
    except KeyError as exc:
        allowed = sorted(FIELD_BLOCKS)
        raise ValueError(f"Unknown service field {name!r}. Use one of: {allowed}") from exc


def service_field_name(name: str | None) -> str:
    if not name:
        raise ValueError("service field name is required")
    key = str(name).strip()
    if key in INTERNAL_TO_SERVICE:
        return INTERNAL_TO_SERVICE[key]
    if key in SERVICE_TO_INTERNAL:
        return INTERNAL_TO_SERVICE[SERVICE_TO_INTERNAL[key]]
    return key


def normalize_substrate_mode(mode: Any) -> Any:
    if mode is None:
        return None
    key = str(mode).strip().lower()
    return SUBSTRATE_MODE_ALIASES.get(key, key)


def public_substrate_mode(mode: Any) -> str:
    normalized = normalize_substrate_mode(mode)
    return "none" if normalized in {None, "none"} else str(normalized)


def service_delta_name(internal_name: str) -> str:
    return f"delta_{INTERNAL_TO_SERVICE.get(internal_name, internal_name)}"


def service_check_name(prefix: str, internal_or_service_name: str) -> str:
    return f"{prefix}:{service_field_name(internal_or_service_name)}"


def service_facing_dataframe(df):
    """Return a copy of a ledger/table with internal field columns renamed.

    Only direct geometric/service field columns are renamed. ADM ledger channels
    such as rho, j_l, delta_rho, and delta_j_l keep their standard names.
    """
    return df.rename(columns={k: v for k, v in PUBLIC_COLUMN_RENAMES.items() if k in df.columns}).copy()
