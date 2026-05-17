from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


def _expand(value: Any, base_dir: Path) -> Any:
    if isinstance(value, str):
        expanded = os.path.expandvars(os.path.expanduser(value))
        # Treat paths as paths only when they look path-like. This keeps names such as
        # "carrying_flow_off" untouched.
        if (
            expanded.startswith("./")
            or expanded.startswith("../")
            or expanded.startswith("~/")
            or expanded.startswith("/")
            or "/" in expanded
            or "\\" in expanded
        ):
            p = Path(expanded)
            if not p.is_absolute():
                p = (base_dir / p).resolve()
            return str(p)
        return expanded
    if isinstance(value, dict):
        return {k: _expand(v, base_dir) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(v, base_dir) for v in value]
    return value


def load_config(path: str | Path) -> dict[str, Any]:
    path = Path(path).resolve()
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML configs. Use JSON or install pyyaml.")
        cfg = yaml.safe_load(text) or {}
    else:
        cfg = json.loads(text)
    cfg = _expand(cfg, path.parent)
    cfg.setdefault("run_name", path.stem)
    cfg.setdefault("service", {})
    if cfg.get("velocity") is None and isinstance(cfg.get("service"), dict):
        cfg["velocity"] = cfg["service"].get("velocity")
    cfg.setdefault("velocity", None)
    cfg.setdefault("substrate", {})
    cfg.setdefault("absorber", {})
    cfg.setdefault("outputs", {})
    cfg.setdefault("thresholds", {})
    return cfg


def require_path(cfg: dict[str, Any], *keys: str) -> Path:
    cur: Any = cfg
    for k in keys:
        if not isinstance(cur, dict) or k not in cur or cur[k] in (None, ""):
            dotted = ".".join(keys)
            raise KeyError(f"Missing required config path: {dotted}")
        cur = cur[k]
    p = Path(cur)
    if not p.exists():
        dotted = ".".join(keys)
        raise FileNotFoundError(f"Configured path does not exist for {dotted}: {p}")
    return p
