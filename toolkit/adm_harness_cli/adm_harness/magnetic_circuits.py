"""Leading longitudinal vacuum and magnetic bend load of complete rail loops."""
from functools import lru_cache

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import cumulative_simpson
from scipy.interpolate import PchipInterpolator

from .curved_boundary import StaticGeometry


class RailChart:
    def __init__(self, cache):
        with np.load(cache) as data:
            self.geometry = StaticGeometry(**{key: data[key] for key in
                ('coordinate', 'radius', 'lapse', 'radial_scale')})
        x = np.r_[np.linspace(-256, -8, 15873)[:-1], self.geometry.coordinate,
                  np.linspace(8, 256, 15873)[1:]]
        proper = cumulative_simpson(self.geometry.values(x)[2], x=x, initial=0)
        proper -= np.interp(0, x, proper)
        self.proper_of_x = PchipInterpolator(x, proper, extrapolate=False)
        self.x_of_proper = PchipInterpolator(proper, x, extrapolate=False)

    def fields(self, proper):
        x = self.x_of_proper(proper)
        if not np.isfinite(x).all():
            raise ValueError('circuit exceeds the retained chart and analytic tails')
        r, a, b = self.geometry.values(x)
        rx, ax, bx = self.geometry.values(x, derivative=1)
        return r, a, rx/b, ax/b


@lru_cache(maxsize=8)
def quadrature(nodes):
    return leggauss(nodes)


def loop_integrals(fields, center, leg, cap, nodes=128, second_log_lapse=None):
    """Full capsule path in a meridian; fields returns R,A,R'/R,(log A)'."""
    if leg < 0 or cap <= 0:
        raise ValueError('nonnegative leg and positive cap required')
    r0 = float(fields(center)[0])
    delta = cap/r0
    z, weights = quadrature(nodes)
    records = []
    if leg > 0:
        panels = max(1, int(np.ceil(leg/4)))
        edges = np.linspace(center-leg/2, center+leg/2, panels+1)
        half = np.diff(edges)/2
        l = ((edges[:-1]+half)[:, None]+half[:, None]*z).ravel()
        leg_weights = (2*half[:, None]*weights).ravel()
        r,a,u,ap = fields(l)
        records.append((l,r,a,u,ap, np.ones_like(l), leg_weights, np.zeros_like(l), np.zeros_like(l)))
    phase = np.r_[np.pi*z/2, -np.pi/2, 0., np.pi/2]
    cap_weights = np.r_[weights*np.pi/2, 0., 0., 0.]
    for sign in (-1., 1.):
        l = center+sign*(leg/2+cap*np.cos(phase))
        lp, lpp = -sign*cap*np.sin(phase), -sign*cap*np.cos(phase)
        tp, tpp = sign*delta*np.cos(phase), -sign*delta*np.sin(phase)
        r,a,u,ap = fields(l)
        rp = r*u
        speed = np.sqrt(lp*lp+(r*tp)**2)
        speed_prime = (lp*lpp+r*rp*lp*tp*tp+r*r*tp*tpp)/speed
        lss = (lpp*speed-lp*speed_prime)/speed**3
        tss = (tpp*speed-tp*speed_prime)/speed**3
        curvature = np.hypot(lss-r*rp*(tp/speed)**2,
                            r*tss+2*rp*lp*tp/speed**2)
        records.append((l,r,a,u,ap,(lp/speed)**2, cap_weights*speed,curvature,lss))
    l,r,a,u,ap,t2,ds,curvature,lss = [np.concatenate([rec[i] for rec in records]) for i in range(9)]
    w = 1/(a*r)
    length = float(np.dot(ds, 1/a))
    casimir = float(np.dot(ds, (1+t2)/(a**3*r))*np.pi/(6*length**2))
    anomaly = float(np.dot(ds, w*t2*(ap*ap*(3-t2)+2*ap*u))/(24*np.pi))
    result = dict(center=center, leg=leg, cap=cap, half_angle=delta,
        optical_length=length, proper_length=float(ds.sum()),
        casimir_coefficient=casimir, anomaly_coefficient=anomaly,
        quantum_coefficient=casimir-anomaly,
        bend_integral=float(np.dot(ds,w*(1-t2))),
        maximum_curvature=float(curvature.max()), minimum_radius=float(r.min()),
        minimum_lapse=float(a.min()), maximum_lapse=float(a.max()),
        minimum_proper=float(l.min()), maximum_proper=float(l.max()))
    if second_log_lapse is not None:
        ass = second_log_lapse(l)*t2+ap*lss
        result['anomaly_by_direct_derivative'] = float(np.dot(ds, w*(2*ass+ap*ap*t2*(1-t2)))/(24*np.pi))
    return result


def magnetic_budget(loop, flux, margin, gap_ratio=.1):
    if flux < 1 or margin <= 1 or gap_ratio <= 0:
        raise ValueError('positive integer flux, separated tube and positive gap ratio required')
    tube = min(1/(margin*loop['maximum_curvature']),
               loop['half_angle']*loop['minimum_radius']/margin)
    field_geometry = 2*flux/tube**2
    field_landau = .5*(np.pi/(gap_ratio*loop['optical_length']*loop['minimum_lapse']))**2
    field = max(field_geometry, field_landau)
    cost = 2*np.pi*flux*field*loop['bend_integral']
    quantum = flux*loop['quantum_coefficient']
    threshold = cost/quantum if quantum > 0 else None
    return dict(flux=flux, margin=margin, field=field,
        field_geometry=field_geometry, field_landau=field_landau,
        tube_radius=float(np.sqrt(2*flux/field)),
        landau_ratio=float(np.pi/(loop['optical_length']*loop['minimum_lapse']*np.sqrt(2*field))),
        magnetic_load_at_e1=cost, quantum_opening_per_species=quantum,
        required_flavors_times_e_squared=threshold,
        required_loop_measure=threshold/(16*np.pi**2) if threshold is not None else None)
