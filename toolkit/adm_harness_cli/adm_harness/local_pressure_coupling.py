"""Instantaneous positive-pressure coupling for a measured mechanical port.

The loaded end remains a pressure-transmission port. Holding p_t=0 on the
examined slice introduces an explicit thermal exchange. These local slices
are component requirements, not a time-evolved, confined support network.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import cumulative_trapezoid

from .graded_electrothermal import fixed_kinematics


def positive_pressure_profile(x, coefficient, drive):
    """Solve p_x+coefficient*p=drive, with the free end at zero pressure.

The drive has one sign. The nonzero loaded-end pressure is retained as the
next mechanical port. Trapezoidal integrating factors converge quadratically.
"""
    x, coefficient, drive = np.asarray(x), np.asarray(coefficient), np.asarray(drive)
    significant = drive[abs(drive) > 1e-14*max(1., abs(drive).max())]
    if significant.size and np.min(significant)*np.max(significant) < 0:
        raise ValueError('one signed contact drive required')
    direction = -1 if significant.size and significant[0] < 0 else 1
    order = slice(None, None, direction)
    distance = direction*(x[order]-x[order][0])
    integral = cumulative_trapezoid(direction*coefficient[order], distance, initial=0.)
    if abs(integral).max() > 500:
        raise ArithmeticError('pressure integrating factor exceeded bounded range')
    pressure = np.exp(-integral)*cumulative_trapezoid(np.exp(integral)*direction*drive[order], distance, initial=0.)
    return pressure[order], direction


def pressure_contact_slice(model, time, center, width, applied_force, *, density_ratio=3., nodes=257):
    """A rho=kappa*p fluid, kappa>=1, supplying opposite rest-frame force.

kappa=3 is the ultrarelativistic isotropic-fluid limit. It has c_s^2=1/3.
The force profile is the continuum C2 profile, with its integrated force
fixed by the archived contact amplitude. Pressure is instantaneous (p_t=0);
the required comoving heat exchange is calculated explicitly.
"""
    if density_ratio < 1 or nodes < 5 or width <= 0:
        raise ValueError('causal density ratio, positive width, and resolved grid required')
    x = np.linspace(center-width/2, center+width/2, nodes)
    g = model.metric(time, x)
    tt = np.full_like(x, time)
    alpha_t = g.alpha*model.metric_splines[0].ev(tt, x, dx=1)
    beta_t = model.metric_splines[1].ev(tt, x, dx=1)
    v, gamma, lapse, acceleration, _ = fixed_kinematics(g, alpha_t, beta_t)
    z = 2*(x-center)/width
    profile = np.maximum(0., 1-z*z)**3/(16*width/35)
    required_force = -applied_force*profile/(4*np.pi*gamma*g.b*g.radius**2)
    coefficient = (density_ratio+1)*gamma*g.b*acceleration
    drive = gamma*g.b*required_force
    p, direction = positive_pressure_profile(x, coefficient, drive)
    pt_x = drive-coefficient*p
    vt = v*(g.logb_t-alpha_t/g.alpha)+g.b*beta_t/g.alpha
    expansion = (g.logb_t+2*g.logr_t+gamma**2*v*vt)/lapse
    heat_exchange = (density_ratio+1)*p*expansion
    moving = (density_ratio+1)*p*gamma**2
    stress = np.array([moving-p, moving*v*v+p, moving*v, p])
    return dict(x=x, pressure=p, pressure_x=pt_x, moments=stress,
                required_rest_force=required_force, required_rest_heat=heat_exchange,
                boundary_direction=direction, loaded_end_pressure=float(p[-1] if direction == 1 else p[0]),
                slice_energy=float(4*np.pi*np.trapezoid(g.volume*stress[0], x)),
                peak_supplied_null=float(np.max((density_ratio+1)*p*gamma**2*(1+abs(v))**2)),
                heat_exchange_integral=float(4*np.pi*np.trapezoid(g.volume*gamma*heat_exchange, x)))
