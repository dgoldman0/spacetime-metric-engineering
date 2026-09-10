"""Finite work-port controls on a prescribed active-rail field history.

These local circuit and magnetic-envelope relations expose matching and
mechanical duties. They do not specify plasma loss or a material converter.
"""
from __future__ import annotations

import numpy as np


def reflected_guide_factor(amplitude, drift=.5):
    """Worst coherent phase guide coefficient multiplying incident energy."""
    if not 0 < drift < 1 or not 0 <= amplitude < 1:
        raise ValueError('subluminal drift and subunit reflected amplitude required')
    return .5*((1+amplitude)**2/drift**2-(1-amplitude)**2)


def capacitor_port(charge, capacitance, charge_rate):
    """Local capacitor variables; rates use material proper time.

The normalized load impedance is Z/C_geom_units, using precisely the same
charge and capacitance normalization at each cell. A zero current has an
open port, represented separately by its zero admittance.
"""
    charge, capacitance, charge_rate = np.broadcast_arrays(charge, capacitance, charge_rate)
    if (np.any(charge <= 0) or np.any(capacitance <= 0)
            or not all(np.isfinite(a).all() for a in (charge, capacitance, charge_rate))):
        raise ValueError('positive finite charge and capacitance, finite rate required')
    voltage = charge/capacitance
    return dict(voltage=voltage, current=charge_rate, energy=charge*voltage/2,
                electrical_power=voltage*charge_rate,
                load_admittance=charge_rate/voltage)


def capacitor_step_work(q0, q1, inverse_c0, inverse_c1):
    """Exact discrete electrical/mechanical split for linearly varying q^2 and 1/C.

U=(q^2/2)/C. The midpoint product rule is exact between any two endpoint
states. This identity verifies both exchange ports without differentiating
or conflating the geometric capacitance change with electrical charging.
"""
    q0, q1, inverse_c0, inverse_c1 = np.broadcast_arrays(q0, q1, inverse_c0, inverse_c1)
    if not all(np.isfinite(a).all() and np.all(a > 0) for a in (q0, q1, inverse_c0, inverse_c1)):
        raise ValueError('positive finite charge and inverse capacitance required')
    h0, h1 = q0*q0/2, q1*q1/2
    electrical = (h1-h0)*(inverse_c0+inverse_c1)/2
    mechanical = (inverse_c1-inverse_c0)*(h0+h1)/2
    change = h1*inverse_c1-h0*inverse_c0
    return electrical, mechanical, change


def port_reflection(admittance, impedance):
    """Voltage reflection for a real capacitive operating-point admittance.

Use positive charging admittance for incident/reflected comparisons. Negative
admittance is electrical generation and belongs to a recovery port.
"""
    admittance = np.asarray(admittance)
    if np.any(admittance < 0) or not np.isfinite(admittance).all() or impedance <= 0:
        raise ValueError('nonnegative finite receiving admittance and positive impedance required')
    y = impedance*admittance
    return (1-y)/(1+y)


def toroidal_bend_factors(aspect):
    """Vacuum B_phi=k/r in an annular 180-degree bend, per transverse height.

The radial aperture is [b-a,b+a], with aspect a/b. Flux matching to a
uniform straight leg sets k=B_straight*2a/log((b+a)/(b-a)). The returned
energy factor multiplies u_straight*A*pi*b. Peak stress multiplies the
straight-leg energy density. Boundary tractions require material support.
"""
    if not 0 < aspect < 1:
        raise ValueError('a resolved positive annular aperture inside the bend required')
    logarithm = np.log1p(aspect)-np.log1p(-aspect)
    k_over_b = 2*aspect/logarithm
    return dict(energy_factor=k_over_b,
                peak_energy_factor=(k_over_b/(1-aspect))**2,
                outer_energy_factor=(k_over_b/(1+aspect))**2)
