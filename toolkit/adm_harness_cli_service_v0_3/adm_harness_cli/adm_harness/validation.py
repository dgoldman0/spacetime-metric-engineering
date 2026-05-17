from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .field_names import SERVICE_TO_INTERNAL, internal_field_name

REQUIRED_FIELD_KEYS = {
    "s_grid",
    "l_grid",
    "alpha",
    "beta",
    "gamma_ll",
    "gamma_omega",
    "rho",
    "j_l",
}

DERIVED_FIELD_KEYS = {"k_l", "k_omega", "K", "R3"}
ALLOWED_DELTA_KEYS = {"alpha", "beta", "gamma_ll", "gamma_omega"}
ALLOWED_SERVICE_FIELDS = {"carrying_flow", "clock_lapse", "rail_stretch", "throat_capacity"}
POSITIVE_FIELD_KEYS = {"alpha", "gamma_ll", "gamma_omega"}


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def merge(self, other: "ValidationReport", prefix: str | None = None) -> None:
        if prefix:
            self.errors.extend(f"{prefix}: {e}" for e in other.errors)
            self.warnings.extend(f"{prefix}: {w}" for w in other.warnings)
            self.checks[prefix] = other.to_dict()
        else:
            self.errors.extend(other.errors)
            self.warnings.extend(other.warnings)
            self.checks.update(other.checks)

    def raise_if_failed(self) -> None:
        if self.errors:
            joined = "\n".join(f"- {e}" for e in self.errors)
            raise ValueError(f"Validation failed:\n{joined}")

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "errors": self.errors, "warnings": self.warnings, "checks": self.checks}


def _finite_stats(arr: np.ndarray) -> dict[str, Any]:
    finite = np.isfinite(arr)
    if arr.size == 0:
        return {"size": 0, "finite_fraction": 0.0, "min": None, "max": None, "mean": None}
    vals = arr[finite]
    if vals.size == 0:
        return {"size": int(arr.size), "finite_fraction": 0.0, "min": None, "max": None, "mean": None}
    return {
        "size": int(arr.size),
        "finite_fraction": float(finite.mean()),
        "min": float(vals.min()),
        "max": float(vals.max()),
        "mean": float(vals.mean()),
    }


def validate_fields(fields: dict[str, np.ndarray], require_derived: bool = False) -> ValidationReport:
    report = ValidationReport()
    required = set(REQUIRED_FIELD_KEYS)
    if require_derived:
        required |= DERIVED_FIELD_KEYS
    missing = sorted(k for k in required if k not in fields)
    if missing:
        report.errors.append(f"missing required field arrays: {missing}")
        return report

    s = np.asarray(fields["s_grid"])
    l = np.asarray(fields["l_grid"])
    if s.ndim != 1 or l.ndim != 1:
        report.errors.append("s_grid and l_grid must be one-dimensional arrays")
        return report
    if len(s) < 3 or len(l) < 3:
        report.errors.append("s_grid and l_grid must each have at least three points for second-order gradients")
    if not np.all(np.diff(s) > 0):
        report.errors.append("s_grid must be strictly increasing")
    if not np.all(np.diff(l) > 0):
        report.errors.append("l_grid must be strictly increasing")

    shape = (len(s), len(l))
    report.checks["grid_shape"] = list(shape)
    report.checks["s_range"] = [float(s[0]), float(s[-1])] if len(s) else None
    report.checks["l_range"] = [float(l[0]), float(l[-1])] if len(l) else None

    for key, arr in fields.items():
        arr = np.asarray(arr)
        if key in {"s_grid", "l_grid"}:
            if not np.all(np.isfinite(arr)):
                report.errors.append(f"{key} contains non-finite values")
            continue
        if arr.shape != shape:
            report.errors.append(f"{key} shape {arr.shape} does not match grid shape {shape}")
            continue
        stats = _finite_stats(arr)
        report.checks[f"field:{key}"] = stats
        if stats["finite_fraction"] != 1.0:
            report.errors.append(f"{key} contains non-finite values")
        if key in POSITIVE_FIELD_KEYS and np.nanmin(arr) <= 0:
            report.errors.append(f"{key} must stay strictly positive; min={float(np.nanmin(arr))}")

    return report


def validate_substrate(fields: dict[str, np.ndarray] | None, exact_fields: dict[str, np.ndarray]) -> ValidationReport:
    report = ValidationReport()
    if fields is None:
        report.warnings.append("no substrate fields supplied; delta channels will default to zero")
        return report
    if "s_grid" not in fields or "l_grid" not in fields:
        report.errors.append("substrate fields must include s_grid and l_grid")
        return report
    if not np.array_equal(fields["s_grid"], exact_fields["s_grid"]):
        report.errors.append("substrate s_grid does not exactly match exact field s_grid")
    if not np.array_equal(fields["l_grid"], exact_fields["l_grid"]):
        report.errors.append("substrate l_grid does not exactly match exact field l_grid")
    shape = exact_fields["rho"].shape
    for key, arr in fields.items():
        if key in {"s_grid", "l_grid"}:
            continue
        arr = np.asarray(arr)
        if arr.shape != shape:
            report.errors.append(f"substrate {key} shape {arr.shape} does not match exact field shape {shape}")
        elif not np.all(np.isfinite(arr)):
            report.errors.append(f"substrate {key} contains non-finite values")
    report.checks["substrate_keys"] = sorted(fields.keys())
    return report


def validate_field_delta(delta: dict[str, np.ndarray], fields: dict[str, np.ndarray]) -> ValidationReport:
    report = ValidationReport()
    shape = fields["rho"].shape
    unknown = sorted(k for k in delta if k not in ALLOWED_DELTA_KEYS)
    if unknown:
        report.errors.append(f"field delta contains unsupported target fields: {unknown}")
    for key, arr in delta.items():
        arr = np.asarray(arr)
        if arr.shape != shape:
            report.errors.append(f"delta_{key} shape {arr.shape} does not match grid shape {shape}")
            continue
        stats = _finite_stats(arr)
        report.checks[f"delta:{key}"] = stats
        if stats["finite_fraction"] != 1.0:
            report.errors.append(f"delta_{key} contains non-finite values")
        if key in POSITIVE_FIELD_KEYS:
            modified = np.asarray(fields[key]) + arr
            if np.nanmin(modified) <= 0:
                report.errors.append(
                    f"delta_{key} would make {key} non-positive; modified min={float(np.nanmin(modified))}"
                )
    if not delta:
        report.warnings.append("field delta is empty; synthesis is an identity operation")
    return report


def validate_config_contract(cfg: dict[str, Any]) -> ValidationReport:
    report = ValidationReport()
    if "inputs" not in cfg:
        report.errors.append("config must include inputs")
    if "exact_fields" not in cfg.get("inputs", {}):
        report.errors.append("config must include inputs.exact_fields")
    synthesis = cfg.get("synthesis", {}) or {}
    service = cfg.get("service", {}) or {}
    absorber = cfg.get("absorber", {}) or {}
    if synthesis.get("enabled", False):
        has_service_modifier = False
        for block in ALLOWED_SERVICE_FIELDS:
            spec = service.get(block)
            if isinstance(spec, dict) and spec.get("enabled", True) and (spec.get("law") or spec.get("mode")):
                has_service_modifier = True
                target = spec.get("target_service_field", spec.get("target_field", block))
                try:
                    internal_field_name(target)
                except ValueError as exc:
                    report.errors.append(str(exc))
        absorber_law = absorber.get("law") or absorber.get("mode")
        if absorber and absorber_law not in {None, "none"}:
            has_service_modifier = True
            target = absorber.get("target_service_field", absorber.get("target_field", "carrying_flow"))
            try:
                internal_field_name(target)
            except ValueError as exc:
                report.errors.append(str(exc))
        if not has_service_modifier:
            report.warnings.append("synthesis is enabled but no service modifier is active; run will be an identity operation")
    return report
