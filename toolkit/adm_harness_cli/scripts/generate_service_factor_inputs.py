from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


PI8 = 8.0 * math.pi
PI16 = 16.0 * math.pi


@dataclass(frozen=True)
class RailParams:
    V: float
    v_exit: float = 0.5
    p_beta: float = 4.0
    Rpass: float = 0.35
    x_catch_beta: float = -0.05
    w_catch_beta: float = 0.32
    x_catch_packet: float = 0.00
    w_catch_packet: float = 0.32
    C0: float = 100.0
    lam: float = 6.0
    B0: float = 8.0
    eta_N: float = 2.0
    Rth: float = 1.75
    w_th: float = 0.569
    w_pass: float = 0.06
    eps: float = 1.0e-5
    x_beta: float = 0.70
    w_beta: float = 0.18
    q_t0: float = -0.40
    q_Tr: float = 3.00
    aOmega: float = 0.20
    ROmega: float = 1.75
    wOmega: float = 1.40
    xOmega: float = 2.00
    wtOmega: float = 0.60
    live_packet_end_margin_widths: float = 2.0


def _token(value: float) -> str:
    text = f"{value:.10g}"
    return text.replace("-", "m").replace("+", "").replace(".", "p").replace("e", "e")


def service_label(v: float) -> str:
    value = float(v)
    if value.is_integer():
        return f"v{int(value)}"
    return f"v{_token(value)}"


def case_token(v: float) -> str:
    value = float(v)
    if value.is_integer():
        return f"V{int(value)}"
    return f"V{_token(value)}"


def smoothstep_minjerk(t: np.ndarray) -> np.ndarray:
    x = np.clip(np.asarray(t, dtype=float), 0.0, 1.0)
    return 10.0 * x**3 - 15.0 * x**4 + 6.0 * x**5


def minjerk_down_window(s: np.ndarray, x: float, w: float) -> np.ndarray:
    t = (np.asarray(s, dtype=float) - (x - 2.0 * w)) / max(4.0 * w, 1.0e-12)
    return 1.0 - smoothstep_minjerk(t)


def falloff(z: np.ndarray, w: float) -> np.ndarray:
    return 0.5 * (1.0 - np.tanh(np.asarray(z, dtype=float) / w))


def minjerk_down(s: np.ndarray, t0: float, tr: float) -> np.ndarray:
    t = (np.asarray(s, dtype=float) - t0) / max(tr, 1.0e-12)
    return 1.0 - smoothstep_minjerk(t)


def bump_sq(x2: np.ndarray, radius: float, width: float) -> np.ndarray:
    z = (np.asarray(x2, dtype=float) - radius * radius) / max(2.0 * radius * width, 1.0e-12)
    return 0.5 * (1.0 - np.tanh(z))


def _grad_s(arr: np.ndarray, s_grid: np.ndarray) -> np.ndarray:
    return np.gradient(arr, s_grid, axis=0, edge_order=2)


def _grad_l(arr: np.ndarray, l_grid: np.ndarray) -> np.ndarray:
    return np.gradient(arr, l_grid, axis=1, edge_order=2)


def build_fields(params: RailParams, *, ns: int, nl: int) -> dict[str, np.ndarray]:
    s_grid = np.linspace(-0.35, 1.65, ns)
    l_grid = np.linspace(-2.80, 2.80, nl)
    s, l = np.meshgrid(s_grid, l_grid, indexing="ij")

    c_beta = minjerk_down_window(s, params.x_catch_beta, params.w_catch_beta)
    c_packet = minjerk_down_window(s, params.x_catch_packet, params.w_catch_packet)
    u_beta = params.v_exit + (params.V - params.v_exit) * c_beta
    u_packet = params.v_exit + (params.V - params.v_exit) * c_packet

    e_release = falloff(s - params.x_beta, params.w_beta)
    q = minjerk_down(s, params.q_t0, params.q_Tr)
    w_support = bump_sq(l * l, params.Rth, params.w_th)
    s_packet = bump_sq((l - s) ** 2 + params.eps * params.eps, params.Rpass, params.w_pass)

    a_spatial = np.exp(q * w_support * math.log(params.C0))
    t_lapse = np.exp(q * w_support * math.log(params.lam * params.C0))
    b_angular = 1.0 + (params.B0 - 1.0) * w_support * q
    shoulder = np.exp(-((np.abs(l) - 1.05) / 0.35) ** 2)
    n_cushion = np.exp(params.eta_N * 0.18 * q * shoulder)

    beta = -u_beta * e_release * (w_support ** params.p_beta) * s_packet / b_angular
    alpha = n_cushion * t_lapse
    gamma_ll = (b_angular * a_spatial) ** 2

    w_omega = bump_sq(l * l, params.ROmega, params.wOmega)
    q_omega = falloff(s - params.xOmega, params.wtOmega)
    c_omega = np.exp(params.aOmega * q_omega * w_omega)
    gamma_omega = (l * l + params.Rth * params.Rth) * c_omega * c_omega

    vcoord = u_packet / b_angular
    gtt = -alpha * alpha + gamma_ll * beta * beta
    packet_norm = -alpha * alpha + gamma_ll * (vcoord + beta) ** 2

    gamma_ll_l = _grad_l(gamma_ll, l_grid)
    gamma_ll_s = _grad_s(gamma_ll, s_grid)
    gamma_omega_l = _grad_l(gamma_omega, l_grid)
    gamma_omega_s = _grad_s(gamma_omega, s_grid)
    beta_l = _grad_l(beta, l_grid)
    gamma_omega_ll = _grad_l(gamma_omega_l, l_grid)

    k_l = (2.0 * beta_l + beta * gamma_ll_l / gamma_ll - gamma_ll_s / gamma_ll) / (2.0 * alpha)
    k_omega = (beta * gamma_omega_l / gamma_omega - gamma_omega_s / gamma_omega) / (2.0 * alpha)
    k_trace = k_l + 2.0 * k_omega
    r3 = (
        -2.0 * gamma_omega_ll / (gamma_ll * gamma_omega)
        + (gamma_omega_l**2) / (2.0 * gamma_ll * gamma_omega**2)
        + (gamma_ll_l * gamma_omega_l) / (gamma_ll**2 * gamma_omega)
        + 2.0 / gamma_omega
    )
    rho = (r3 + 4.0 * k_l * k_omega + 2.0 * k_omega * k_omega) / PI16
    j_l = (-2.0 * _grad_l(k_omega, l_grid) + gamma_omega_l / gamma_omega * (k_l - k_omega)) / PI8

    return {
        "s_grid": s_grid,
        "l_grid": l_grid,
        "alpha": alpha,
        "beta": beta,
        "gamma_ll": gamma_ll,
        "gamma_omega": gamma_omega,
        "packet_norm": packet_norm,
        "gtt": gtt,
        "k_l": k_l,
        "k_omega": k_omega,
        "K": k_trace,
        "R3": r3,
        "rho": rho,
        "j_l": j_l,
        "U_beta": u_beta,
        "U_packet": u_packet,
        "B": b_angular,
        "A_profile": a_spatial,
        "T_profile": t_lapse,
        "W": w_support,
        "S": s_packet,
        "q": q,
        "E": e_release,
        "N": n_cushion,
    }


def build_betaoff_fields(fields: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    betaoff = dict(fields)
    betaoff["beta"] = np.zeros_like(fields["beta"])
    betaoff["packet_norm"] = -fields["alpha"] ** 2 + fields["gamma_ll"] * (fields["U_packet"] / fields["B"]) ** 2
    betaoff["gtt"] = -fields["alpha"] ** 2
    s_grid = fields["s_grid"]
    l_grid = fields["l_grid"]
    gamma_ll = fields["gamma_ll"]
    gamma_omega = fields["gamma_omega"]
    alpha = fields["alpha"]
    gamma_ll_l = _grad_l(gamma_ll, l_grid)
    gamma_ll_s = _grad_s(gamma_ll, s_grid)
    gamma_omega_l = _grad_l(gamma_omega, l_grid)
    gamma_omega_s = _grad_s(gamma_omega, s_grid)
    gamma_omega_ll = _grad_l(gamma_omega_l, l_grid)
    k_l = (-gamma_ll_s / gamma_ll) / (2.0 * alpha)
    k_omega = (-gamma_omega_s / gamma_omega) / (2.0 * alpha)
    r3 = (
        -2.0 * gamma_omega_ll / (gamma_ll * gamma_omega)
        + (gamma_omega_l**2) / (2.0 * gamma_ll * gamma_omega**2)
        + (gamma_ll_l * gamma_omega_l) / (gamma_ll**2 * gamma_omega)
        + 2.0 / gamma_omega
    )
    betaoff["k_l"] = k_l
    betaoff["k_omega"] = k_omega
    betaoff["K"] = k_l + 2.0 * k_omega
    betaoff["R3"] = r3
    betaoff["rho"] = (r3 + 4.0 * k_l * k_omega + 2.0 * k_omega * k_omega) / PI16
    betaoff["j_l"] = (-2.0 * _grad_l(k_omega, l_grid) + gamma_omega_l / gamma_omega * (k_l - k_omega)) / PI8
    return betaoff


def _cell_volume(fields: dict[str, np.ndarray]) -> np.ndarray:
    ds = float(np.mean(np.diff(fields["s_grid"])))
    dl = float(np.mean(np.diff(fields["l_grid"])))
    return np.sqrt(fields["gamma_ll"]) * fields["gamma_omega"] * ds * dl


def _stage_name(s: np.ndarray, params: RailParams) -> np.ndarray:
    out = np.full(s.shape, "reset_decompression", dtype=object)
    wc = max(params.w_catch_packet, params.w_catch_beta)
    out[s < params.x_catch_packet - 2.0 * wc] = "entry_precatch"
    out[np.abs(s - params.x_catch_packet) <= 2.0 * wc] = "catch_rematch"
    held = (params.x_catch_packet + 2.0 * wc < s) & (s < params.x_beta - 2.0 * params.w_beta)
    out[held] = "held_carry"
    out[np.abs(s - params.x_beta) <= 2.0 * params.w_beta] = "release_shift_fade"
    post = (params.x_beta + 2.0 * params.w_beta < s) & (s < params.x_beta + 4.0 * params.w_beta)
    out[post] = "post_release_buffer"
    return out


def _region_name(s: np.ndarray, l: np.ndarray, params: RailParams) -> np.ndarray:
    al = np.abs(l)
    xi = l - s
    out = np.full(s.shape, "far_exterior", dtype=object)
    out[al <= 1.85 * params.Rth] = "outer_quarantine_shell"
    out[al <= 1.20 * params.Rth] = "support_edge"
    out[al <= 0.65 * params.Rth] = "core_throat"
    packet = np.abs(xi) <= params.Rpass
    out[packet & (al <= params.Rth)] = "packet_in_support"
    out[packet & (al > params.Rth)] = "packet_outer"
    return out


def build_point_ledger(fields: dict[str, np.ndarray], params: RailParams) -> pd.DataFrame:
    s_grid = fields["s_grid"]
    l_grid = fields["l_grid"]
    ss, ll = np.meshgrid(s_grid, l_grid, indexing="ij")
    xi = ll - ss
    packet_geom = np.abs(xi) <= params.Rpass
    live = packet_geom & (ss <= params.x_beta + params.live_packet_end_margin_widths * params.w_beta)
    core = np.abs(xi) <= max(params.Rpass - params.w_pass, 0.0)
    edge = packet_geom & ~core
    support = (np.abs(ll) <= 1.20 * params.Rth) & ~live
    volume = _cell_volume(fields)

    data: dict[str, Any] = {
        "V": np.full(ss.size, params.V),
        "s": ss.ravel(),
        "l": ll.ravel(),
        "xi": xi.ravel(),
        "stage": _stage_name(ss, params).ravel(),
        "region": _region_name(ss, ll, params).ravel(),
        "inside_packet_live": live.ravel(),
        "packet_live": live.ravel(),
        "packet_core": (live & core).ravel(),
        "packet_edge_strip": (live & edge).ravel(),
        "packet_edge": (live & edge).ravel(),
        "packet_inner_edge": (live & edge & (xi < 0.0)).ravel(),
        "packet_outer_edge": (live & edge & (xi >= 0.0)).ravel(),
        "support_shell": support.ravel(),
        "sqrt_gamma": (np.sqrt(fields["gamma_ll"]) * fields["gamma_omega"]).ravel(),
        "cell_volume": volume.ravel(),
    }
    for key in [
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
        "U_beta",
        "U_packet",
        "B",
        "W",
        "S",
        "q",
        "E",
        "N",
    ]:
        data[key] = fields[key].ravel()
    return pd.DataFrame(data)


def write_configs(out_dir: Path, config_dir: Path, params: RailParams) -> tuple[Path, Path]:
    label = service_label(params.V)
    exact_fields = out_dir / f"adm_exact_fields_{case_token(params.V)}.npz"
    point_ledger = out_dir / f"adm_exact_point_ledger_{label}.csv"
    substrate_fields = out_dir / f"substrate_subtraction_fields_{label}.npz"

    def rel(path: Path) -> str:
        return os.path.relpath(path, config_dir)

    common = {
        "service": {"velocity": float(params.V)},
        "inputs": {
            "exact_fields": rel(exact_fields),
            "exact_point_ledger": rel(point_ledger),
            "substrate_fields": rel(substrate_fields),
        },
        "substrate": {"mode": "carrying_flow_off"},
        "thresholds": {
            "max_abs_delta_rho_packet": 1.0e-6,
            "max_abs_delta_j_packet": 1.0e-4 if params.V <= 5.0 else 1.0e-3,
            "min_catch_rematch_localization_fraction": 0.50,
        },
        "outputs": {"root": "../runs", "format": "csv", "figures": False, "report": True, "overwrite": True},
    }
    baseline = {"run_name": f"{label}_service_flow_off", **common, "control_law": {"mode": "none"}}
    target = {
        "run_name": f"{label}_support_shell_window_pos_target",
        **common,
        "service": {
            "velocity": float(params.V),
            "carrying_flow": {
                "enabled": True,
                "law": "windowed_adjustment",
                "scope": "catch_rematch_support_shell",
                "allocation_mode": "support_shell",
                "signal": "delta_j_l",
                "amplitude": 1.0e-7,
                "gain": 1.0,
                "max_abs_change": 1.0e-7,
                "smoothness_order": 1,
                "packet_exclusion": 1.0,
                "support_shell_gain": 0.0,
                "edge_bias": 0.0,
                "target_service_field": "carrying_flow",
                "catch_lead": 0.75,
                "temporal_width": 0.5,
            },
        },
        "synthesis": {"enabled": True},
        "validation": {"identity_self_check": True, "identity_tolerance": 1.0e-10},
    }
    baseline_path = config_dir / f"{label}_service_flow_off.yaml"
    target_path = config_dir / f"{label}_service_support_shell_target.yaml"
    baseline_path.write_text(yaml.safe_dump(baseline, sort_keys=False), encoding="utf-8")
    target_path.write_text(yaml.safe_dump(target, sort_keys=False), encoding="utf-8")
    return baseline_path, target_path


def generate_products(args: argparse.Namespace) -> dict[str, Any]:
    service_factor = float(args.service_factor)
    ns = int(args.ns)
    nl = int(args.nl)
    w_th = float(args.w_th)
    eta_n = float(args.eta_N)
    support_radius = float(args.support_radius)
    if not math.isfinite(service_factor) or service_factor <= 0.0:
        raise SystemExit(f"Service factor V must be finite and positive, got {service_factor!r}")
    if ns < 5 or nl < 5:
        raise SystemExit(f"Generated service-factor grid must be at least 5 x 5, got {ns} x {nl}")
    if not math.isfinite(w_th) or w_th <= 0.0:
        raise SystemExit(f"Support-shell width must be finite and positive, got {w_th!r}")
    if not math.isfinite(support_radius) or support_radius <= 0.0:
        raise SystemExit(f"Support radius must be finite and positive, got {support_radius!r}")
    if not math.isfinite(eta_n):
        raise SystemExit(f"Lapse-cushion coefficient must be finite, got {eta_n!r}")

    params = RailParams(
        V=service_factor,
        eta_N=eta_n,
        w_th=w_th,
        Rth=support_radius,
        ROmega=support_radius,
    )
    label = service_label(params.V)
    out_dir = Path(args.output_dir) / label
    config_dir = Path(args.config_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    fields = build_fields(params, ns=ns, nl=nl)
    betaoff = build_betaoff_fields(fields)
    ledger = build_point_ledger(fields, params)
    volume = _cell_volume(fields)

    exact_path = out_dir / f"adm_exact_fields_{case_token(params.V)}.npz"
    np.savez_compressed(
        exact_path,
        **{k: fields[k] for k in ["s_grid", "l_grid", "alpha", "beta", "gamma_ll", "gamma_omega", "packet_norm", "gtt", "k_l", "k_omega", "K", "R3", "rho", "j_l"]},
    )
    substrate_path = out_dir / f"substrate_subtraction_fields_{label}.npz"
    np.savez_compressed(
        substrate_path,
        s_grid=fields["s_grid"],
        l_grid=fields["l_grid"],
        live_rho=fields["rho"],
        live_j_l=fields["j_l"],
        betaoff_rho=betaoff["rho"],
        betaoff_j_l=betaoff["j_l"],
        static_rho=betaoff["rho"],
        static_j_l=betaoff["j_l"],
        delta_betaoff_rho=fields["rho"] - betaoff["rho"],
        delta_betaoff_j_l=fields["j_l"] - betaoff["j_l"],
        delta_static_rho=fields["rho"] - betaoff["rho"],
        delta_static_j_l=fields["j_l"] - betaoff["j_l"],
        packet_live=ledger["packet_live"].to_numpy().reshape(fields["rho"].shape),
        packet_edge=ledger["packet_edge"].to_numpy().reshape(fields["rho"].shape),
        support_shell=ledger["support_shell"].to_numpy().reshape(fields["rho"].shape),
        volume=volume,
    )
    ledger_path = out_dir / f"adm_exact_point_ledger_{label}.csv"
    ledger.to_csv(ledger_path, index=False)
    baseline_config, target_config = write_configs(out_dir, config_dir, params)

    live = ledger["inside_packet_live"].astype(bool)
    support = ledger["support_shell"].astype(bool)
    catch = ledger["stage"].eq("catch_rematch")
    delta_j = np.abs((fields["j_l"] - betaoff["j_l"]).ravel()) * volume.ravel()
    delta_rho = np.abs((fields["rho"] - betaoff["rho"]).ravel()) * volume.ravel()
    global_delta_j = float(delta_j.sum())
    metadata = {
        "service_factor": params.V,
        "service_factor_label": label,
        "params": asdict(params),
        "grid": {"ns": ns, "nl": nl},
        "files": {
            "exact_fields": str(exact_path),
            "substrate_fields": str(substrate_path),
            "point_ledger": str(ledger_path),
            "baseline_config": str(baseline_config),
            "target_config": str(target_config),
        },
        "diagnostics": {
            "max_live_packet_norm": float(ledger.loc[live, "packet_norm"].max()),
            "positive_live_packet_norm_points": int((ledger.loc[live, "packet_norm"] > 0.0).sum()),
            "global_abs_delta_j_l": global_delta_j,
            "catch_support_delta_j_l_fraction": float(delta_j[(catch & support).to_numpy()].sum() / global_delta_j) if global_delta_j else 0.0,
            "packet_abs_delta_j_l_fraction": float(delta_j[live.to_numpy()].sum() / global_delta_j) if global_delta_j else 0.0,
            "packet_abs_delta_rho": float(delta_rho[live.to_numpy()].sum()),
        },
        "caveat": "Reduced ADM input generator for validation-ladder hardening; pressure/null 4D source projections remain separate heavier diagnostics.",
    }
    metadata_path = out_dir / "service_factor_input_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate reduced ADM harness input products for an arbitrary active-rail service factor V.")
    parser.add_argument("--service-factor", type=float, required=True)
    parser.add_argument("--output-dir", default="data/generated_service_factors")
    parser.add_argument("--config-dir", default="configs/generated")
    parser.add_argument("--ns", type=int, default=121)
    parser.add_argument("--nl", type=int, default=241)
    parser.add_argument("--w-th", type=float, default=0.569)
    parser.add_argument("--eta-N", type=float, default=2.0)
    parser.add_argument("--support-radius", type=float, default=1.75)
    return parser


def main() -> int:
    metadata = generate_products(build_parser().parse_args())
    print(json.dumps(metadata["files"], indent=2))
    print(json.dumps(metadata["diagnostics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
