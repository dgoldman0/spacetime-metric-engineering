"""Necessary stress and conserved-flux gates for a condensate-backed support.

The local basis is (rho, p_r, p_t) per unit positive energy:
radial Maxwell (1,-1,1), scalar potential (1,-1,-1), radial waves
(1,1,0), angular waves (1,0,1/2), angular membrane (1,0,-1), and
rest inventory (1,0,0). Scalar gradients, currents, and interfaces require
their own tensors. A local decomposition supplies no field evolution law.
"""
import numpy as np


BASIS = np.array([[1., 1., 1., 1., 1., 1.],
                  [-1., -1., 1., 0., 0., 0.],
                  [1., -1., 0., .5, -1., 0.]])


def minimum_energy(radial, angular):
    """Exact positive-energy cone after adding scalar potential energy."""
    p, q = np.broadcast_arrays(radial, angular)
    return np.maximum.reduce([p+2*q, p-q, -p, -q])


def potential_interval(density, radial, angular):
    """Allowed potential energies with all other basis weights nonnegative.

For V in this interval, max(0,-p_r-V) <= E <= (rho-p_r+p_t-V)/3.
An empty interval denotes an inadmissible target, without clipping it away.
"""
    rho, p, q = np.broadcast_arrays(density, radial, angular)
    lower = np.maximum(0., (-2*p-rho-q)/2)
    upper = np.minimum((rho-p-2*q)/4, rho-p+q)
    return lower, upper


def decompose(density, radial, angular):
    """One exact allocation, using the least admissible potential energy."""
    rho, p, q = np.broadcast_arrays(density, radial, angular)
    potential, unused = potential_interval(rho, p, q)
    field = np.maximum(0., -p-potential)
    wave = p+field+potential
    angular_residual = q-field+potential
    angular_wave = 2*np.maximum(angular_residual, 0.)
    membrane = np.maximum(-angular_residual, 0.)
    inventory = rho-field-potential-wave-angular_wave-membrane
    return np.array([field, potential, wave, angular_wave, membrane, inventory])


def equilibrium_vortex_interval(density, radial, angular, radius):
    """Allowed A for (A/R^2,-A/R^2,0) plus the old field/membrane basis.

A single population of equilibrium, identical, straight tubes has constant A
along each uninterrupted radial bundle and through time. That requirement
is stronger than allowing an independent A at every sample.
"""
    rho, p, q, r = np.broadcast_arrays(density, radial, angular, radius)
    lower = np.maximum(0., r*r*(-2*p-q-rho))
    upper = r*r*np.minimum((rho-p-2*q)/2, (rho-p+q)/2)
    return lower, upper


def bag_invariant_interval(density, radial, angular, radius):
    """Allowed A0=2 R^2 sqrt(E V) in the leading large-flux bag model.

For fixed tube count, magnetic flux, and core potential, E is proportional
to 1/(R^2 a), V to a/R^2, where a is a tube's cross-sectional area.
A0 is conserved even when a changes. This leading-volume approximation
allows the same auxiliary field/radiation/angular-membrane/rest basis.
Finite tube walls, transverse kinetics, and longitudinal gradients lie
outside this gate; they can change its conclusion when appreciable.
"""
    rho, p, q, r = np.broadcast_arrays(density, radial, angular, radius)
    vl, vh = potential_interval(rho, p, q)
    b = rho-p+q
    # At fixed V the smallest product uses E=max(0,-p-V). Its minimum
    # over the interval occurs at an endpoint (or on its zero segment).
    product_low = np.minimum(vl*np.maximum(0., -p-vl),
                             vh*np.maximum(0., -p-vh))
    optimum = np.minimum(np.maximum(b/2, vl), vh)
    product_high = optimum*(b-optimum)/3
    feasible = (vl <= vh) & (vh >= 0.) & (product_high >= 0.)
    low = np.where(feasible, 2*r*r*np.sqrt(np.maximum(product_low, 0.)), np.nan)
    high = np.where(feasible, 2*r*r*np.sqrt(np.maximum(product_high, 0.)), np.nan)
    return low, high


def invariant_summary(lower, upper, times, positions):
    """Report simultaneous and time-independent spatial-grading tests."""
    lower, upper = np.broadcast_arrays(lower, upper)
    t, x = np.asarray(times), np.asarray(positions)
    if lower.shape != (len(t), len(x)) or not np.all(np.isfinite([lower, upper])):
        raise ValueError('finite time-by-position interval arrays required')
    def witness(values, which):
        i, j = np.unravel_index(which(values), values.shape)
        return dict(value=float(values[i, j]), time=float(t[i]), x=float(x[j]))
    lower_global, upper_global = float(lower.max()), float(upper.min())
    graded_low, graded_high = lower.max(axis=0), upper.min(axis=0)
    ratios = np.divide(graded_low, graded_high, out=np.full_like(graded_low, np.inf),
                       where=graded_high > 0)
    ratios[(graded_low == 0) & (graded_high == 0)] = 1.
    j = int(np.argmax(ratios))
    return dict(local_intervals_nonempty=bool(np.all(lower <= upper)),
                common_invariant_feasible=bool(lower_global <= upper_global),
                required_lower=witness(lower, np.argmax),
                permitted_upper=witness(upper, np.argmin),
                lower_over_upper=float(lower_global/upper_global) if upper_global > 0 else None,
                static_spatial_grading_feasible=bool(np.all(graded_low <= graded_high)),
                worst_temporal_ratio=dict(x=float(x[j]), lower=float(graded_low[j]),
                    upper=float(graded_high[j]), ratio=float(ratios[j]) if np.isfinite(ratios[j]) else None),
                positions_requiring_time_variation=int(np.sum(graded_low > graded_high)),
                spatial_samples=len(x), temporal_samples=len(t))
