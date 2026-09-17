"""Separate energy-decay budgets for the rail's standing pressure fields.

Field energy histories are piecewise linear in proper time. Their residence
exposure is distinct from the work-port throughput used by transfer guides.
Maxwell/photon substitutions preserve the integrated tensor; their physical
hosts, spatial fields and dissipation mechanisms still require construction.
"""
import numpy as np


def photon_to_maxwell(fields, fraction):
    """Replace a fixed fraction of each photon population at equal tensor."""
    E, fraction = np.asarray(fields, float), np.asarray(fraction, float)
    if E.shape[0] != 4 or not np.isfinite(E).all() or np.any(E < 0):
        raise ValueError("four finite nonnegative field energies required")
    if not np.isfinite(fraction).all() or np.any((fraction < 0) | (fraction > 1)):
        raise ValueError("conversion fraction must lie in [0,1]")
    converted = E.copy()
    converted[0] += fraction*(E[2]+.5*E[3])
    converted[1] += fraction*.5*E[3]
    converted[2:] *= 1-fraction
    return converted


def residence_exposure(fields, proper_duration):
    """Exact cumulative energy-time integral through each panel end."""
    E, dt = np.asarray(fields, float), np.asarray(proper_duration, float)
    if (E.ndim != 3 or E.shape[0] != 4 or dt.shape != (E.shape[1]-1, E.shape[2])
            or not np.isfinite(E).all() or not np.isfinite(dt).all()
            or np.any(E < 0) or np.any(dt <= 0)):
        raise ValueError("positive proper-time panels and four nonnegative field histories required")
    return np.cumsum(.5*(E[:, :-1]+E[:, 1:])*dt[None], axis=1)


def decay_rate_ceiling(cumulative_exposure, panel_reserve, *, replacement_factor=1.):
    """One common decay rate for the selected populations, energy screen only.

    At each panel, its end exposure is compared with a lower bound on
    available reserve throughout that panel. Multiple distinct loss rates
    instead obey the joint inequalities sum_i gamma_i*I_i <= reserve.
    """
    I, R = np.asarray(cumulative_exposure, float), np.asarray(panel_reserve, float)
    if (I.shape != R.shape or I.ndim != 2 or np.any(I < 0) or np.any(R <= 0)
            or not np.isfinite(I).all() or not np.isfinite(R).all()
            or not np.isfinite(replacement_factor) or replacement_factor < 1):
        raise ValueError("finite exposure, positive reserve and replacement factor >=1 required")
    allowed = np.divide(R, replacement_factor*I, out=np.full_like(I, np.inf), where=I > 0)
    index = np.argmin(allowed, axis=0)
    return dict(rate=allowed[index, np.arange(I.shape[1])], limiting_panel=index)
