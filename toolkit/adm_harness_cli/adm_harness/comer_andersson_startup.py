"""A bounded spherical audit of the Comer--Andersson model-(iii) rate sector.

The published slow-drift closure and the quadratic rate action are distinct
objects. The latter is one explicit choice of the general entropy-form
dependence, not the paper's thermodynamically controlled closure. This module
evaluates necessary stress, entropy, and kinetic conditions; it does not
provide a completed nonlinear two-current Einstein evolution.
"""
from __future__ import annotations

import numpy as np

PI = np.pi


def areal_rates(f, f_t, f_tt, alpha, nu_t):
    """Particle worldlines at fixed areal radius: B=diag(H,0,0)."""
    f, f_t, f_tt, alpha, nu_t = np.broadcast_arrays(f, f_t, f_tt, alpha, nu_t)
    if np.any(f <= 0) or np.any(alpha <= 0):
        raise ValueError("positive radial metric and lapse required")
    radial = -f_t/(2*alpha*f)
    radial_dot = -(f_tt-f_t*nu_t-f_t*f_t/f)/(2*alpha*alpha*f)
    return radial, radial_dot


def quadratic_rate_action(radial, tangential, a, b):
    """Q=(a theta^2+b B_ab B^ab)/2, with constant coefficients."""
    hr, ht = np.asarray(radial), np.asarray(tangential)
    # Preserve the exact areal cancellation when a+b=0.
    return .5*(a+b)*hr*hr+2*a*hr*ht+(2*a+b)*ht*ht


def quadratic_rate_channels(radial, tangential, radial_dot, tangential_dot, a, b):
    """Hilbert variation of integral sqrt(-g) Q, before setting R_t=0.

    Channels are density, radial pressure, radial current, angular pressure
    in the particle frame. Coefficients a,b are constants. Algebraic base
    material and entropy/heat currents must be accounted for separately.
    """
    hr, ht, dhr, dht = np.broadcast_arrays(radial, tangential, radial_dot, tangential_dot)
    theta, theta_dot = hr+2*ht, dhr+2*dht
    q = quadratic_rate_action(hr, ht, a, b)
    cr, ct = (a+b)*hr+2*a*ht, a*hr+(2*a+b)*ht
    dcr, dct = (a+b)*dhr+2*a*dht, a*dhr+(2*a+b)*dht
    return np.stack([q, q-dcr-theta*cr, np.zeros_like(q), q-dct-theta*ct], axis=-1)


def kinetic_conditions(a, b):
    """Constant-coefficient action tests in a local comoving frame.

    The tensor ratio follows by adding Q to the Einstein--Hilbert ADM kinetic
    density. It tests the two transverse, traceless metric modes, not all
    characteristics of the coupled matter system.
    """
    return {
        "tensor_kinetic_ratio": float(1+8*PI*b),
        "rate_shear_hessian_eigenvalue": float(b),
        "rate_trace_hessian_eigenvalue": float(3*a+b),
        "rate_quadratic_form_nonnegative": bool(b >= -1e-14 and 3*a+b >= -1e-14),
        "tensor_kinetic_strictly_positive": bool(1+8*PI*b > 1e-12),
    }


def entropy_embedding(base_energy, q, q_dot, theta, thermal_ratio=1/3):
    """Rate-sector entropy scaling in the comoving, conserved-bare-flux limit.

    Let epsilon_bar=C s_bar^(1+w), with s_bar's three-form closed. Scaling
    that form by F=(1-Q/epsilon_bar)^(1/(1+w)) gives Lambda=Lambda_bar+Q.
    The returned Gamma/s is the actual convective entropy creation rate of
    this specific functional when the two currents coincide. A nonzero heat
    drift adds transport terms; it is not certified by this reduction.
    """
    if not 0 < thermal_ratio <= 1:
        raise ValueError("thermal pressure ratio must lie in (0,1]")
    energy, q, q_dot, theta = np.broadcast_arrays(base_energy, q, q_dot, theta)
    if np.any(energy <= 0):
        raise ValueError("positive pre-existing thermal energy required")
    remaining = energy-q
    valid = remaining > 0
    gamma = 1+thermal_ratio
    factor = np.full_like(remaining, np.nan, dtype=float)
    entropy_rate = np.full_like(remaining, np.nan, dtype=float)
    factor[valid] = (remaining[valid]/energy[valid])**(1/gamma)
    entropy_rate[valid] = -(q_dot[valid]+gamma*q[valid]*theta[valid])/(gamma*remaining[valid])
    return {"entropy_factor": factor, "entropy_rate_per_entropy": entropy_rate,
            "thermal_energy": remaining, "valid": valid}


def heat_from_energy_current(energy, current, thermal_ratio=1/3):
    """Exact perfect thermal-fluid moments for prescribed lab energy/current.

    This prices a pre-existing heat carrier. It is a kinematic reconstruction,
    leaving its separate momentum/entropy equations as acceptance conditions.
    """
    if not 0 < thermal_ratio <= 1:
        raise ValueError("thermal pressure ratio must lie in (0,1]")
    e, j = np.broadcast_arrays(energy, current)
    if np.any(e <= 0) or np.any(abs(j) >= e):
        raise ValueError("a timelike positive-energy thermal carrier requires E>|J|")
    w = thermal_ratio
    z = j/e
    velocity = 2*z/(1+w+np.sqrt((1+w)**2-4*w*z*z))
    rest = e*(1-velocity*velocity)/(1+w*velocity*velocity)
    kinetic = e-rest
    channels = np.stack([e, w*rest+kinetic, j, w*rest], axis=-1)
    return {"velocity": velocity, "rest_energy": rest, "kinetic_energy": kinetic,
            "channels": channels}


def minimum_heat_energy(current, maximum_drift=.1, thermal_ratio=1/3):
    if not 0 < maximum_drift < 1 or not 0 < thermal_ratio <= 1:
        raise ValueError("subluminal drift and thermal pressure ratio in (0,1] required")
    return abs(np.asarray(current))*(1+thermal_ratio*maximum_drift**2)/((1+thermal_ratio)*maximum_drift)


def cattaneo_required_drive(current, current_dot, relaxation_time, conductivity):
    """Required grad(T)+T acceleration for tau Dq+q=-kappa drive.

    This is an inverse transport diagnostic, not a solved temperature profile.
    Extra model-(iii) forces and both constituent equations remain to be imposed.
    """
    if relaxation_time <= 0 or conductivity <= 0:
        raise ValueError("positive relaxation time and conductivity required")
    return -(relaxation_time*np.asarray(current_dot)+current)/conductivity


def startup_orders(metric_order):
    if metric_order < 3:
        raise ValueError("the registered static-start paths have order at least three")
    n = int(metric_order)
    return {"metric_order": n, "geometric_angular_order": n-2,
            "current_order": n-1, "viscous_stress_order": n-1,
            "published_D6_derivative_order": 2*n-3,
            "preloaded_heat_diagonal_order": 2*n-2,
            "quadratic_rate_pressure_order": n-2,
            "quadratic_entropy_rate_order": 2*n-3}


def fit_constant_rate_response(radial, radial_dot):
    """Fit the mass/radial/angular dynamic Einstein channels simultaneously.

    The reference is the instantaneous static tensor of the *same* metric;
    the current remains an explicit required heat/transfer channel. This
    inverse tensor fit does not constitute a complete source construction.
    """
    h, dh = np.broadcast_arrays(radial, radial_dot)
    use = np.isfinite(h) & np.isfinite(dh) & (abs(dh)+h*h > 1e-30)
    h, dh = h[use], dh[use]
    target = np.stack([np.zeros_like(h), np.zeros_like(h), -(dh+h*h)/(8*PI)],axis=-1)
    columns = [quadratic_rate_channels(h,0.,dh,0.,a/(8*PI),b/(8*PI))[...,[0,1,3]]
               for a,b in [(1.,0.),(0.,1.)]]
    matrix = np.stack(columns,axis=-1).reshape(-1,2)
    rhs = target.ravel()
    if len(rhs) < 2 or np.linalg.matrix_rank(matrix) < 2:
        raise ValueError("independent radial and angular data required")
    fit, _, rank, singular = np.linalg.lstsq(matrix,rhs,rcond=None)
    residual = matrix@fit-rhs
    return {"a_times_8pi": float(fit[0]), "b_times_8pi": float(fit[1]),
            "max_stress_residual": float(abs(residual).max()), "rank": int(rank),
            "condition_number": float(singular[0]/singular[-1]),
            **kinetic_conditions(fit[0]/(8*PI),fit[1]/(8*PI))}
