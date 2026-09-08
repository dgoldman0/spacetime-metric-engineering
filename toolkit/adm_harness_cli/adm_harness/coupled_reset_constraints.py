"""Necessary Einstein/source checks for one tangential-support reset candidate.

The prescribed background is a matched static rail source. The candidate
reassigns radial string energy to a tangential material body and two null
transfer streams. A radial Einstein solve changes the metric in response.
These are initial-data/compatibility equations, not a spacetime evolution.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import cumulative_trapezoid

from .radial_stress import radial_tensor


@dataclass(frozen=True)
class ResetSourceSpec:
    string_flux: float = .039783
    material_to_transfer_density: float = 1.
    tangential_pressure_ratio: float = .25
    counterstream_fraction: float = .01
    edge_fraction: float = .03


def handoff_window(radius, edge_fraction=.03):
    """One C2 source handoff with a central plateau and finite radial extent."""
    radius = np.asarray(radius, dtype=float)
    if radius.ndim != 1 or len(radius) < 3 or np.any(np.diff(radius) <= 0):
        raise ValueError("radius must be a strictly increasing one-dimensional grid")
    if not 0 < edge_fraction < .5:
        raise ValueError("edge fraction must lie in (0, .5)")
    x = (radius-radius[0])/(radius[-1]-radius[0])
    def rise(t):
        t = np.clip(t, 0., 1.)
        return t**3*(10.-15.*t+6.*t*t)
    return rise(x/edge_fraction)*rise((1.-x)/edge_fraction)


def prescribed_reset_source(radius, background, outward_current, spec=ResetSourceSpec()):
    """Return explicit component tensors in the candidate's areal rest frame.

    background columns are (rho, p_r, j_r=0, p_t). The current waveform is
    calibrated from the reference ADM ledger and is an input to this model.
    The new geometry must subsequently reproduce it. This calibration is not
    an assertion that reference and candidate observers coincide in spacetime.
    """
    r = np.asarray(radius, dtype=float)
    bg = np.asarray(background, dtype=float)
    current = np.asarray(outward_current, dtype=float)
    if bg.shape != (len(r), 4) or current.shape != r.shape:
        raise ValueError("one four-channel background and one current per radius required")
    if not np.isfinite(bg).all() or not np.isfinite(current).all() or np.any(r <= 0):
        raise ValueError("finite source data and positive radii required")
    if np.any(bg[:, 2] != 0):
        raise ValueError("the prescribed background must be a static control")
    if spec.string_flux < 0 or spec.material_to_transfer_density < 0 or not 0 <= spec.tangential_pressure_ratio <= 1:
        raise ValueError("nonnegative string/material densities and a DEC-compatible tangential ratio required")
    if spec.counterstream_fraction <= 0:
        raise ValueError("positive counterstream fraction required for smooth signed transport")
    window = handoff_window(r, spec.edge_fraction)
    command = window*current
    reserve = spec.counterstream_fraction*float(np.max(np.abs(current)))*window
    transfer = np.hypot(command, reserve)
    released = spec.string_flux*window/r**2
    material_density = spec.material_to_transfer_density*transfer
    infrastructure = bg.copy()
    infrastructure[:, 0] -= released
    infrastructure[:, 1] += released
    material = np.column_stack([material_density, np.zeros(len(r)), np.zeros(len(r)),
                                spec.tangential_pressure_ratio*material_density])
    mu_out, mu_in = .5*(transfer+command), .5*(transfer-command)
    outgoing = np.column_stack([mu_out, mu_out, mu_out, np.zeros(len(r))])
    incoming = np.column_stack([mu_in, mu_in, -mu_in, np.zeros(len(r))])
    # A fixed partition identifies the outer storage body. It adds no stress.
    x = np.clip(((r-r[0])/(r[-1]-r[0])-.55)/.25, 0., 1.)
    reservoir_weight = x**3*(10.-15.*x+6.*x*x)
    reservoir = material*reservoir_weight[:, None]
    endpoint = material-reservoir
    total = infrastructure+endpoint+reservoir+outgoing+incoming
    return {"window": window, "released_string_density": released,
            "transfer_density": transfer, "commanded_current": command,
            "reservoir_weight": reservoir_weight, "infrastructure": infrastructure,
            "endpoint": endpoint, "reservoir": reservoir, "outgoing": outgoing,
            "incoming": incoming, "total": total}


def solve_radial_constraints(radius, reference_mass, background_density, target, outer_lapse):
    """Solve the Hamiltonian difference and the polar-areal radial pressure law.

    ds^2=-alpha^2 dt^2+dr^2/f+r^2 dOmega^2, f=1-2m/r.
    The inner Misner-Sharp mass is held fixed; the outer mass may respond.
    If f<=0, stationary areal material observers cease to be timelike and this
    constitutive ansatz fails. No lapse is fabricated across that obstruction.

    m_r=4*pi*r^2*E and (log alpha)_r=(m+4*pi*r^3*P)/(r*(r-2m)).
    The radial momentum constraint fixes m_t=-4*pi*r^2*alpha*sqrt(f)*J.
    Full time/angle compatibility is a subsequent test on any surviving family.
    """
    r = np.asarray(radius, dtype=float)
    mass0 = np.asarray(reference_mass, dtype=float)
    bg = np.asarray(background_density, dtype=float)
    source = np.asarray(target, dtype=float)
    if r.ndim != 1 or len(r) < 3 or np.any(r <= 0) or np.any(np.diff(r) <= 0):
        raise ValueError("positive increasing radii required")
    if mass0.shape != r.shape or bg.shape != r.shape or source.shape != (len(r), 4):
        raise ValueError("constraint inputs must use the same radial grid")
    if not np.isfinite(source).all() or not np.isfinite(mass0).all() or not np.isfinite(bg).all():
        raise ValueError("finite constraint inputs required")
    if not np.isfinite(outer_lapse) or outer_lapse <= 0:
        raise ValueError("positive finite outer lapse required")
    increment = cumulative_trapezoid(4*np.pi*r*r*(source[:, 0]-bg), r, initial=0.)
    mass = mass0+increment
    f = 1.-2.*mass/r
    result = {"mass": mass, "mass_increment": increment, "f": f,
              "source_radial_discriminant": (source[:, 0]+source[:, 1])**2-4*source[:, 2]**2,
              "stationary_areal_domain": bool(np.all(f > 0)),
              "lapse": np.full_like(r, np.nan), "mass_time_derivative": np.full_like(r, np.nan)}
    if result["stationary_areal_domain"]:
        gradient = (mass+4*np.pi*r**3*source[:, 1])/(r*r*f)
        integral = cumulative_trapezoid(gradient, r, initial=0.)
        log_lapse = np.log(outer_lapse)+integral-integral[-1]
        result["log_lapse"] = log_lapse
        if np.max(np.abs(log_lapse)) < 300:
            result["lapse"] = np.exp(log_lapse)
            result["mass_time_derivative"] = -4*np.pi*r*r*result["lapse"]*np.sqrt(f)*source[:, 2]
    return result


def tensors(channels):
    return np.array([radial_tensor(*row) for row in np.asarray(channels)])
