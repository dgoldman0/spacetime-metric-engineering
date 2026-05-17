from __future__ import annotations

"""Canonical service vocabulary for the ADM harness.

The exact-builder bundles use conventional ADM array keys. The public config and
reports use service names so knobs describe what the active-rail service does.
"""

from typing import Any

SERVICE_TO_INTERNAL = {
    "carrying_flow": "beta",
    "radial_carrying_flow": "beta",
    "carry_flow": "beta",
    "flow": "beta",
    "shift_flow": "beta",
    # Legacy and mathematical aliases are accepted for old configs only.
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
    "flow_off": "betaoff",
    "carrying_flow_off": "betaoff",
    "carry_flow_off": "betaoff",
    "shift_off": "betaoff",
    "shift_flow_off": "betaoff",
    "betaoff": "betaoff",
    "beta_off": "betaoff",
    "time_matched_betaoff": "betaoff",
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


def internal_field_name(name: str | None) -> str:
    if not name:
        raise ValueError("field name is required")
    key = str(name).strip()
    try:
        return SERVICE_TO_INTERNAL[key]
    except KeyError as exc:
        allowed = sorted(k for k in SERVICE_TO_INTERNAL if k not in {"beta", "alpha", "gamma_ll", "gamma_omega"})
        raise ValueError(f"Unknown service field {name!r}. Use one of: {allowed}") from exc


def service_field_name(name: str | None) -> str:
    if not name:
        raise ValueError("field name is required")
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


def service_delta_name(internal_name: str) -> str:
    return f"delta_{INTERNAL_TO_SERVICE.get(internal_name, internal_name)}"
