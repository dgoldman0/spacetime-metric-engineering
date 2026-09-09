"""Necessary radial balance for ideal conformal channels plus ordinary matter.

The remaining aggregate may contain any number of interacting components;
only its summed radial null stress is required to be nonnegative. This also
allows an independent angular quantum contribution with zero radial null
stress, such as the ideal pair of tangential-normal planar Casimir tensors.
The longitudinal quantum
model has constant total central charge and zero transverse pressure, as for
spherically averaged radial massless channels. A second quantum sector with
negative radial null stress changes this gate.
"""
import numpy as np
from scipy.integrate import simpson


def weighted_balance(proper, radius, lapse, radius_prime, radius_second,
                     log_lapse_prime, kappa, reference_radius, optical_return=0.):
    """Finite-interval identity; kappa=G c/(12 pi), all primes proper.

    W=exp[-(R^2-R_ref^2)/(2 kappa)] and C=4 pi^2/L_opt^2 give
      C int W/A^2 - int W R R''/kappa - [W (log A)']
        = (4 pi/kappa) int W R^2 H_ordinary.
    The actual loop's optical length includes the supplied return. Zero is
    an optimistic lower bound for a channel spanning this interval.
    """
    l, r, a, rp, rpp, ap = np.broadcast_arrays(
        proper, radius, lapse, radius_prime, radius_second, log_lapse_prime)
    if (l.ndim != 1 or len(l) < 3 or np.any(np.diff(l) <= 0)
            or not all(np.isfinite(v).all() for v in (l, r, a, rp, rpp, ap))
            or np.any(r <= 0) or np.any(a <= 0) or kappa <= 0
            or not np.isfinite(kappa) or optical_return < 0
            or not np.isfinite(optical_return)):
        raise ValueError('finite positive geometry, kappa, ordered grid, and nonnegative return required')
    w = np.exp(-(r*r-reference_radius**2)/(2*kappa))
    path = float(simpson(1/a, x=l)+optical_return)
    numerator = float(simpson(w/a**2, x=l))
    curvature = float(simpson(w*r*rpp/kappa, x=l))
    endpoint = float(w[-1]*ap[-1]-w[0]*ap[0])
    supply = 4*np.pi**2*numerator/path**2
    return dict(weight=w, optical_length=path, numerator=numerator,
                curvature_demand=curvature, endpoint_demand=endpoint,
                required=curvature+endpoint, supply=supply,
                residual=supply-curvature-endpoint)


def lapse_box_upper_bound(proper, lapse, weight, variable_mask,
                          fractional_change, optical_return=0.):
    """An optimistic upper bound valid for every lapse within a pointwise box.

    In the variable region, (1-d) A0 <= A <= (1+d) A0. The numerator uses
    the lower bound everywhere and the optical length uses the upper bound.
    These choices need not be jointly attainable, making this a rejection
    test only. Fixed endpoint slopes are required by weighted_balance.
    """
    if not np.isfinite(fractional_change) or not 0 <= fractional_change < 1:
        raise ValueError('fractional change must be in [0,1)')
    if optical_return < 0 or not np.isfinite(optical_return):
        raise ValueError('finite nonnegative optical return required')
    l, a, w, mask = np.broadcast_arrays(proper, lapse, weight, variable_mask)
    lower = a*np.where(mask, 1-fractional_change, 1.)
    upper = a*np.where(mask, 1+fractional_change, 1.)
    numerator_upper = float(simpson(w/lower**2, x=l))
    length_lower = float(simpson(1/upper, x=l)+optical_return)
    return 4*np.pi**2*numerator_upper/length_lower**2


def lapse_box_from_integrals(total_numerator, total_optical_length,
                            variable_numerator, variable_optical_length,
                            fractional_change):
    """Same bound with variable-region integrals on their own resolved grid.

    Splitting at the exact region endpoints avoids quadrature across a jump
    in the bounding envelope. The total optical length includes any return.
    """
    if not np.isfinite(fractional_change) or not 0 <= fractional_change < 1:
        raise ValueError('fractional change must be in [0,1)')
    fixed_numerator = max(total_numerator-variable_numerator, 0.)
    fixed_length = total_optical_length-variable_optical_length
    if fixed_length < -1e-12 or variable_optical_length <= 0 or variable_numerator < 0:
        raise ValueError('the variable region must lie inside the total optical path')
    numerator = fixed_numerator+variable_numerator/(1-fractional_change)**2
    length = max(fixed_length, 0.)+variable_optical_length/(1+fractional_change)
    return 4*np.pi**2*numerator/length**2
