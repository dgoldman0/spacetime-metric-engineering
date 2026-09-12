"""Necessary member-energy gate for an exactly conserved radial increment.

delta(rho,p_r,p_t)=(A/R^2,-A/R^2,0) has zero divergence for constant A.
This tensor degree alone supplies neither a material law nor end reactions.
"""
import numpy as np


def admissible_amplitude(radius, density, radial, angular, fraction):
    """Return the complete constant A>=0 interval for the member-cost cone."""
    r, rho, p, q = map(np.asarray, (radius, density, radial, angular))
    if np.any(r <= 0) or not 0 < fraction <= 1:
        raise ValueError('positive radius and member fraction in (0,1] required')
    cost = np.maximum(-q, 2*q)
    lower = max(0., float(np.max(-rho*r*r)),
                float(np.max(r*r*(p+cost-fraction*rho)/(1+fraction))))
    if fraction == 1:
        margin = float(np.min(p+rho-cost))
        return dict(feasible=margin>=-1e-12, lower=lower, upper=None,
                    minimum_radial_enthalpy_margin=margin)
    upper = float(np.min(r*r*(p+fraction*rho-cost)/(1-fraction)))
    return dict(feasible=bool(lower<=upper), lower=lower, upper=upper)


def minimum_member_fraction(radius, density, radial, angular):
    if not admissible_amplitude(radius, density, radial, angular, 1.)['feasible']:
        return None
    lo, hi = 0., 1.
    for unused in range(55):
        mid = (lo+hi)/2
        if admissible_amplitude(radius, density, radial, angular, mid)['feasible']:
            hi = mid
        else:
            lo = mid
    return hi
