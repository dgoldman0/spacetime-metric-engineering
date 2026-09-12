"""Energy gates for locally actuated scalar/Maxwell support cells.

The adiabatic controller is the homogeneous limit of a canonical Higgs
amplitude f, a complex matter amplitude u, and their positive interaction
g*f**2*u**2. Write V0=lambda*eta**4/4, z=f**2/eta**2 and
V=V0*(1-z)**2 on the suppressed-Higgs branch 0 <= z <= 1.

The matter equation fixes K_u=I. The Higgs equation fixes
I=2*V0*z*(1-z)+K_f, so the complete scalar tensor is
  (rho,p_r,p_t)=(4*sqrt(V*V0)-3*V,-V,-V)+K_f*(3,1,1).
The last term is already admitted by the auxiliary radiation basis.
Ignoring charge-screening, gradients and finite boundaries makes this a
necessary gate for the adiabatic homogeneous controller, not a solution of
the driven field equations. Varying phase volume has a different scope.
"""
import numpy as np

from .field_membrane_support import minimum_energy as auxiliary_energy
from .scalar_flux_support import minimum_energy, potential_interval


def controller_energy(potential, core_height):
    """Count the potential, matter kinetic energy and interaction energy."""
    v, h = np.broadcast_arrays(potential, core_height)
    if np.any(v < 0) or np.any(h < v):
        raise ValueError('require 0 <= potential <= core height')
    return 4*np.sqrt(v*h)-3*v


def loaded_minimum_energy(radial, angular, core_height):
    """Exact minimum over the locally adjustable condensate amplitude.

Between pressure-basis crossings, the energy is concave as a function of V;
its minimum occurs at an endpoint. Checking these five candidates therefore
resolves the continuous problem without a sampling or optimizer tolerance.
"""
    p, q, h = np.broadcast_arrays(radial, angular, core_height)
    if np.any(h < 0):
        raise ValueError('nonnegative core height required')
    candidates = np.clip(np.array([np.zeros_like(p), h, -q, -p, -(p+q)/2]), 0, h)
    costs = controller_energy(candidates, h)+auxiliary_energy(p+candidates, q+candidates)
    index = np.argmin(costs, axis=0)
    selected = np.take_along_axis(candidates, index[None], axis=0)[0]
    return np.min(costs, axis=0), selected


def core_height_interval(density, radial, angular):
    """Exact allowed fixed V0 at one sample, including controller energy.

When the auxiliary basis alone succeeds, V=0 allows any V0. Otherwise,
the allowed set is [V_lower, max B(V)**2/(16*V)], where
B=min(rho-p-2q, rho-p+q+3V, rho+2p+q+6V). Its maximization is over the
ideal potential interval. B**2/V is convex between the same basis crossings,
so endpoints suffice. An inadmissible ideal tensor returns an empty interval.
"""
    rho, p, q = np.broadcast_arrays(density, radial, angular)
    lo, hi = potential_interval(rho, p, q)
    valid = (rho >= minimum_energy(p, q)) & (rho >= 0)
    optional = rho >= auxiliary_energy(p, q)
    candidates = np.clip(np.array([lo, hi, -q, -p, -(p+q)/2]), lo, np.maximum(lo, hi))
    b = np.minimum(np.minimum(rho-p-2*q, rho-p+q+3*candidates), rho+2*p+q+6*candidates)
    height = np.divide(b*b, 16*candidates,
                       out=np.zeros_like(candidates), where=candidates > 0)
    height = np.where(b >= 0, height, -np.inf)
    upper = np.max(height, axis=0)
    upper = np.where(optional, np.inf, upper)
    lower = np.where(optional, 0., lo)
    return np.where(valid, lower, np.inf), np.where(valid, upper, -np.inf)


def two_cell_phase_inventory(times, masses, power, *, efficiency=1.):
    """Optimistic common lossless/work-converter reservoir for two cells.

`power` is proper-volume integrated input per coordinate time, including
metric work. Positive cell input drains the shared reservoir. Energy can be
recovered with the specified converter efficiency. The initial inventory is
the smallest keeping its energy nonnegative. Transport delay, the reservoir
tensor, interface stress and external reservoir work remain additional gates.
The masses are retained to expose the difference between energy change and
conversion work on a time-dependent background.
"""
    from scipy.integrate import cumulative_trapezoid
    t, m, p = map(np.asarray, (times, masses, power))
    if m.shape != p.shape or m.shape != (len(t), 2) or np.any(np.diff(t) <= 0):
        raise ValueError('ordered times and two cell histories required')
    if not 0 < efficiency <= 1:
        raise ValueError('efficiency in (0,1] required')
    drain = np.maximum(p, 0).sum(axis=1)/efficiency-efficiency*np.maximum(-p, 0).sum(axis=1)
    drawn = cumulative_trapezoid(drain, t, initial=0.)
    initial = max(0., float(drawn.max()))
    return dict(initial_energy=initial, final_energy=float(initial-drawn[-1]),
                reservoir_energy=initial-drawn, net_input=drawn,
                coordinate_power=drain,
                cell_energy_change=m[-1].sum()-m[0].sum())
