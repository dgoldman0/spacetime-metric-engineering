"""Conditional nonlinear certificate for independently partitioned rail cells.

Each cell has its own rotor, guide and finite reaction-photon branch. Fixed
capacity fractions partition the original two sheet/joint populations and
their field bias; constitutive homogeneity preserves the summed inventories.
The certificate includes changing baseline duties. Spatial packing, current
returns, geometric traction work and physical port realization are separate
requirements of the complete rail.

Time s=t/R0 is used by the differential inequalities. Histories supply
dimensionless powers in units C/delta and time in units delta. The matrices
are verified with exact integer interval arithmetic at resolution 10^-18;
the constitutive history enclosures use analytic formulas with a declared
floating-point guard.
"""
from fractions import Fraction as F
from itertools import product
from math import isqrt

import numpy as np

from .constitutive_joints_and_optics import series_state
from .scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_NET_POWER, CONVERTER_RAMP, GUIDE_MASS,
    GUIDE_RADIUS, RAMP_TIME, ROTOR_RADIUS, SPIN_FLOOR, guide_bounds,
)

H_MIN, H_MAX = 1.08, 1.32
C_MAX, N_MAX, U_MAX, C_RATE_MAX = .5001, .0018, .006, .006
RADIAL_DOMAIN = .012
DAMPING, HEAT_GAIN, HEAT_ETA, HEAT_COEFFICIENT = .8, 2.7, .3, .809
ISS_EPSILON, ISS_DECAY, ISS_INPUT_SQUARED = .27, .22, 1.152
RADIUS_ERROR_BOUND, SPEED_BOUND, PHI_BOUND = .01140, .00905, .00981
TRACE_CURVATURE_BOUND, BASELINE_C_RATE_BOUND = .018, 3.4e-6
EXTERNAL_TRACE_RATE_BOUND = .001
FIELD_BIAS_ENERGY = .62
ADDED_DUTY_LIMITS = np.array([.32, .16])
SHORT_DELAY, PHOTON_PEAK, PHOTON_PILOT = 1/64, 1.2, .001
FLOAT_GUARD = 1e-9


class _Interval:
    """Exact outward intervals whose endpoints are integers divided by SCALE."""
    SCALE = 10**18

    def __init__(self, lower, upper=None):
        if isinstance(lower, _Interval):
            self.lo, self.hi = lower.lo, lower.hi
            return
        lower = lower if isinstance(lower, F) else F(str(lower))
        upper = lower if upper is None else (upper if isinstance(upper, F) else F(str(upper)))
        self.lo = lower.numerator*self.SCALE//lower.denominator
        self.hi = -(-upper.numerator*self.SCALE//upper.denominator)
        if self.lo > self.hi:
            raise ValueError("ordered interval endpoints required")

    @classmethod
    def raw(cls, lo, hi):
        value = cls.__new__(cls)
        value.lo, value.hi = int(lo), int(hi)
        return value

    def __add__(self, other):
        other = _Interval(other)
        return self.raw(self.lo+other.lo, self.hi+other.hi)

    __radd__ = __add__

    def __neg__(self):
        return self.raw(-self.hi, -self.lo)

    def __sub__(self, other):
        return self+-_Interval(other)

    def __rsub__(self, other):
        return _Interval(other)+-self

    def __mul__(self, other):
        other = _Interval(other)
        values = [a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.raw(min(values)//self.SCALE, -(-max(values)//self.SCALE))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = _Interval(other)
        if other.lo <= 0 <= other.hi:
            raise ValueError("interval denominator contains zero")
        values = [F(a*self.SCALE, b) for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        lo, hi = min(values), max(values)
        return self.raw(lo.numerator//lo.denominator, -(-hi.numerator//hi.denominator))

    def __rtruediv__(self, other):
        return _Interval(other)/self

    def square(self):
        low = 0 if self.lo <= 0 <= self.hi else min(self.lo*self.lo, self.hi*self.hi)
        high = max(self.lo*self.lo, self.hi*self.hi)
        return self.raw(low//self.SCALE, -(-high//self.SCALE))

    def sqrt(self):
        if self.lo < 0:
            raise ValueError("nonnegative square-root interval required")
        lo, hi = isqrt(self.lo*self.SCALE), isqrt(self.hi*self.SCALE)
        return self.raw(lo, hi+(hi*hi < self.hi*self.SCALE))

    @property
    def upper(self):
        return self.hi/self.SCALE

    @property
    def lower(self):
        return self.lo/self.SCALE


def storage_matrix(c, h, *, kind="heat"):
    """P in z=(w,y); phi=w+k*h*y gives a simpler congruent matrix."""
    c, h = np.broadcast_arrays(np.asarray(c, float), np.asarray(h, float))
    if not np.isfinite([c, h]).all() or np.any(c < 0) or np.any(h <= 0):
        raise ValueError("finite nonnegative gain and positive energy required")
    if kind == "heat":
        q, e = DAMPING*HEAT_GAIN, HEAT_COEFFICIENT*(1+HEAT_ETA)/2
    elif kind == "invariant":
        q, e = 1., ISS_EPSILON
    else:
        raise ValueError("storage kind must be heat or invariant")
    P = np.empty(c.shape+(2, 2))
    P[..., 0, 0] = q*(1+c)
    P[..., 0, 1] = P[..., 1, 0] = (1+c)*h*(DAMPING*q-e)
    P[..., 1, 1] = q+(1+c)*h*h*(DAMPING**2*q-2*DAMPING*e)
    return P


def storage_derivatives(c, h, *, kind="heat"):
    q, e = ((DAMPING*HEAT_GAIN, HEAT_COEFFICIENT*(1+HEAT_ETA)/2)
            if kind == "heat" else (1., ISS_EPSILON))
    if kind not in ("heat", "invariant"):
        raise ValueError("storage kind must be heat or invariant")
    d, z = DAMPING*q-e, DAMPING**2*q-2*DAMPING*e
    return (np.array([[q, h*d], [h*d, h*h*z]]),
            np.array([[0., (1+c)*d], [(1+c)*d, 2*(1+c)*h*z]]))


def coupled_reduced_rhs(w, y, h, c, n, *, damping=DAMPING):
    """Exact closed dynamics; the supplied n includes guide/line/baseline work."""
    x, v = h+w, y/h
    if (not np.isfinite([w, y, h, c, n, damping]).all() or h <= 0 or x <= 0
            or abs(v) >= 1 or c < 0 or damping < 0):
        raise ValueError("finite causal rotor state and nonnegative coefficients required")
    S = np.sqrt(1-v*v)
    d0 = damping+S*v/(x*(1+S))
    a = 1-damping*x*v
    f = np.array([damping*S-v/h, -(S+damping*y)/h-x*(v/(h*S)-damping)*d0])
    denominator = 1+c*a
    if denominator <= 0:
        raise ValueError("positive coupled input denominator required")
    u = (n-c*(f@[w, y]))/denominator
    return dict(derivative=np.array([v-u, -S/x*w-d0*y+v*u, u]),
                rotor_input=u, heat_rate=damping*x/(h*S)*y*y,
                trace_rate_per_inventory=f@[w, y]+a*u,
                free_trace_coefficients=f, input_trace_coefficient=a)


def _coefficient_intervals(box):
    c, h, w, v = (_Interval(*bounds) for bounds in box)
    k, C = _Interval(DAMPING), 1+c
    x, S = h+w, (1-v.square()).sqrt()
    den = C-c*k*x*v
    db1, db2 = k*v*(h-c*w)/(C*den), v/den
    df1 = k*(S-1)-v/h
    df2 = k*k*(w+h*(1-S))+k*v*(S/(1+S)-x/(h*S))
    E, dd = (w+h*(1-S))/x, S*v/(x*(1+S))
    b1 = -1/C+db1
    da = (k*E-c*(db1*k+b1*df1),
          -k*k*h*E-k*h*dd-c*(-db1/h+b1*df2),
          E/h-c*(db2*k+db2*df1),
          -k*E-dd-c*(-db2/h+db2*df2))
    return c, h, C, db1, db2, b1, da


def _matrix_box(box, kind):
    """Bound the matrix after congruence by z=(phi-k*h*y,y)."""
    c, h, C, db1, db2, b1, (a11, a12, a21, a22) = _coefficient_intervals(box)
    k, u, cd = _Interval(DAMPING), _Interval(-U_MAX, U_MAX), _Interval(-C_RATE_MAX, C_RATE_MAX)
    if kind == "heat":
        G, K, eta = map(_Interval, (HEAT_GAIN, HEAT_COEFFICIENT, HEAT_ETA))
        q11, q12, q22 = k*G*C, -K*(1+eta)*C*h/2, k*G
        p01, p02 = -k*G, K*(1+eta)*h/2
        dp1, dp2 = q11*db1+q12*db2, q12*db1+q22*db2
        l11 = -k*k*G+K*(1+eta)*C+(2*p01*dp1+dp1.square())/G
        l22 = -K*eta+K*K*(1+eta).square()*h.square()/(4*G)+(2*p02*dp2+dp2.square())/G
        l12 = (p01*dp2+p02*dp1+dp1*dp2)/G
        l11 += k*G*cd
        l22 += -k*K*(1+eta)*C*h*u
        l12 += -K*(1+eta)*h/2*cd+C*(k*k*G-K*(1+eta)/2)*u
    else:
        eps, alpha = map(_Interval, (ISS_EPSILON, ISS_DECAY))
        q11, q12, q22 = C, -eps*C*h, _Interval(1)
        l11 = -2*k+2*eps*C+2*alpha*C+cd
        l22 = -2*eps+2*alpha-2*k*eps*C*h*u
        l12 = k*eps*h-2*alpha*eps*C*h-eps*h*cd+C*(k-eps)*u
    l11 += 2*(q11*a11+q12*a21)
    l22 += 2*(q12*a12+q22*a22)
    l12 += q11*a12+q12*a22+q12*a11+q22*a21
    off = max(abs(l12.lo), abs(l12.hi))
    determinant = (_Interval.raw(l11.hi, l11.hi)*_Interval.raw(l22.hi, l22.hi)
                   -_Interval.raw(off, off).square())
    passed = l11.hi < 0 and l22.hi < 0 and determinant.lo > 0
    chi = q11*b1.square()+2*q12*b1*db2+q22*db2.square()
    return passed, (-l11.hi, -l22.hi, determinant.lo), chi.hi


def matrix_certificate():
    """Certify every state/parameter in the declared rectangular domain."""
    limits = [(F(0), F(str(C_MAX))), (F(str(H_MIN)), F(str(H_MAX))),
              (-F(str(RADIAL_DOMAIN)), F(str(RADIAL_DOMAIN))),
              (-F(str(RADIAL_DOMAIN)), F(str(RADIAL_DOMAIN)))]
    grid = [[lo+(hi-lo)*F(i, 4) for i in range(5)] for lo, hi in limits]
    output = {}
    for kind in ("heat", "invariant"):
        pending = [(tuple((g[i], g[i+1]) for g, i in zip(grid, index)), 0)
                   for index in product(range(4), repeat=4)]
        count, deepest, chi_max = 0, 0, 0
        minima = [None, None, None]
        while pending:
            box, depth = pending.pop()
            passed, minors, chi = _matrix_box(box, kind)
            if not passed:
                if depth >= 16:
                    raise ValueError(f"Uncertified {kind} interval: {box}")
                j = max(range(4), key=lambda i: (box[i][1]-box[i][0])/(limits[i][1]-limits[i][0]))
                lo, hi = box[j]
                midpoint = (lo+hi)/2
                for bounds in ((lo, midpoint), (midpoint, hi)):
                    child = list(box)
                    child[j] = bounds
                    pending.append((tuple(child), depth+1))
                continue
            count, deepest, chi_max = count+1, max(deepest, depth), max(chi_max, chi)
            minima = [value if old is None else min(old, value) for old, value in zip(minima, minors)]
        if kind == "invariant" and chi_max > _Interval(ISS_INPUT_SQUARED).lo:
            raise ValueError("Invariant input coefficient exceeds its rounded ceiling")
        output[kind] = dict(accepted_boxes=count, maximum_refinement_depth=deepest,
            minimum_negative_diagonal_and_determinant=[str(F(x, _Interval.SCALE)) for x in minima],
            maximum_input_quadratic_form=chi_max/_Interval.SCALE)
    return dict(exact_integer_interval_arithmetic=True, denominator=_Interval.SCALE,
        state_domain=dict(h=[H_MIN, H_MAX], c=[0., C_MAX], abs_w=RADIAL_DOMAIN,
                          abs_v=RADIAL_DOMAIN, abs_u=U_MAX, abs_c_prime=C_RATE_MAX),
        damping=DAMPING, heat_gain=HEAT_GAIN, heat_coefficient=HEAT_COEFFICIENT,
        matrices=output, **domain_certificate())


def domain_certificate():
    """Close the radial/input/rate bootstrap, conditional on external bounds."""
    k, h0, h1, m, v, c = map(_Interval, (DAMPING, H_MIN, H_MAX, RADIAL_DOMAIN, RADIAL_DOMAIN, C_MAX))
    S = (1-v.square()).sqrt()
    thermal = k*(1+m/h0)/S
    if thermal.hi > _Interval(HEAT_COEFFICIENT).lo:
        raise ValueError("Thermal coefficient leaves its enclosure")
    factor = 1-(1+c)*_Interval(ISS_EPSILON).square()*h1.square()
    level = _Interval(ISS_INPUT_SQUARED)*(_Interval(N_MAX)/ISS_DECAY).square()
    wi = (1+h1.square()*(k*k-2*k*ISS_EPSILON))/factor
    vi = 1/(h0.square()*factor)
    bounds = [(level*wi).sqrt(), (level*vi).sqrt(), (level/factor).sqrt()]
    for actual, limit in zip(bounds, (RADIUS_ERROR_BOUND, SPEED_BOUND, PHI_BOUND)):
        if actual.hi >= _Interval(limit).lo or limit >= RADIAL_DOMAIN:
            raise ValueError("Invariant ellipse exceeds its declared interior bound")
    f1 = k*(1-S)+v/h0
    df2 = k*k*(m+h1*(1-S))+k*v*((1+m/h0)/S-S/(1+S))
    base = 1/h0-k*k*h0  # Absolute frozen f2; it dominates its positive endpoint.
    if base.lo < (k*k*h1-1/h1).hi:
        raise ValueError("Frozen force coefficient endpoint ordering changed")
    f2 = base+df2+k*h1*f1
    fz = (k+f1)*m+f2*h1*v
    amin, amax = 1-k*(h1+m)*v, 1+k*(h1+m)*v
    if fz.lo <= (amin*N_MAX).hi:
        raise ValueError("Coupled input bound requires its increasing-gain endpoint")
    umax = (_Interval(N_MAX)+c*fz)/(1+c*amin)
    trace_rate = 20*(fz+amax*N_MAX)+EXTERNAL_TRACE_RATE_BOUND
    cprime = TRACE_CURVATURE_BOUND*trace_rate+BASELINE_C_RATE_BOUND
    if umax.hi >= _Interval(U_MAX).lo or cprime.hi >= _Interval(C_RATE_MAX).lo:
        raise ValueError("Coupled input or constitutive-rate bootstrap failed")
    # Positive definiteness of both parameter-dependent storage matrices.
    heat_det = (_Interval(DAMPING*HEAT_GAIN).square()
                -_Interval(HEAT_COEFFICIENT).square()*_Interval(1+HEAT_ETA).square()
                *(1+c)*h1.square()/4)
    if min(factor.lo, heat_det.lo) <= 0:
        raise ValueError("Storage matrix lacks strict positive definiteness")
    return dict(invariant_level_upper=level.upper, radius_error_upper=bounds[0].upper,
        radial_speed_upper=bounds[1].upper, phi_upper=bounds[2].upper,
        reduced_input_upper=umax.upper, constitutive_rate_upper=cprime.upper,
        free_trace_linear_form_upper=fz.upper, external_trace_rate_assumption=EXTERNAL_TRACE_RATE_BOUND,
        reduced_network_input_assumption=N_MAX, inventory_domain=[18., 20.],
        constitutive_curvature_assumption=TRACE_CURVATURE_BOUND,
        baseline_constitutive_rate_assumption=BASELINE_C_RATE_BOUND)


def input_l1_certificate():
    """Cold-start rotor L1 gain, for pricing its changed optical encounters.

    The invariant proof gives (sqrt(V))' <= -alpha*sqrt(V)+chi*abs(n).
    An exact interval bound on the dual norm of f then controls u. The
    same gain relates integrals of physical q and the power defining n.
    A history must separately supply that latter L1 bound.
    """
    limits = [(F(0), F(str(C_MAX))), (F(str(H_MIN)), F(str(H_MAX))),
              (-F(str(RADIAL_DOMAIN)), F(str(RADIAL_DOMAIN))),
              (-F(str(RADIAL_DOMAIN)), F(str(RADIAL_DOMAIN)))]
    grid = [[lo+(hi-lo)*F(i, 8) for i in range(9)] for lo, hi in limits]
    k, eps, peak = _Interval(DAMPING), _Interval(ISS_EPSILON), 0
    for index in product(range(8), repeat=4):
        c, h, w, v = (_Interval(g[i], g[i+1]) for g, i in zip(grid, index))
        C, x, S = 1+c, h+w, (1-v.square()).sqrt()
        f1 = k*S-v/h
        f2 = -1/h+k*k*(w+h*(1-S))+k*v*(S/(1+S)-x/(h*S))
        dual = (f1.square()+2*eps*C*h*f1*f2+C*f2.square())/(C*(1-C*eps.square()*h.square()))
        peak = max(peak, dual.hi)
    if peak >= _Interval("1.13").square().lo:
        raise ValueError("Trace dual norm exceeds its rounded L1 ceiling")
    c = _Interval(C_MAX)
    amin = 1-k*(_Interval(H_MAX)+RADIAL_DOMAIN)*RADIAL_DOMAIN
    coefficient = c/(1+c*amin)
    gain = 1+coefficient*_Interval("1.13")*_Interval(ISS_INPUT_SQUARED).sqrt()/ISS_DECAY
    if gain.hi >= _Interval("2.85").lo:
        raise ValueError("Rotor L1 gain exceeds its rounded ceiling")
    return dict(exact_integer_interval_arithmetic=True, interval_boxes=8**4,
        trace_dual_norm_squared_upper=str(F(peak, _Interval.SCALE)), trace_dual_norm_upper=1.13,
        maximum_feedback_coefficient=coefficient.upper,
        rotor_to_effective_network_l1_gain=2.85, initial_radial_error=[0., 0.],
        whole_history_effective_network_l1_evaluated=False)


def constitutive_panel_bounds(tension, core_inventory, joint_inventory, duration_over_delay):
    """Continuous panel enclosures for the original series law and moving duties.

    Duty increments range over [0,.32] and [0,.16]. Curvature uses positive
    interval products, including both joint directions. Duration is delta
    normalized; the reported c' uses s=t/R0. A small declared numerical guard
    surrounds evaluation of these analytic formulas.
    """
    T, M, m, dt = map(lambda x: np.asarray(x, float),
                       (tension, core_inventory, joint_inventory, duration_over_delay))
    if (T.ndim != 3 or T.shape[0] != 2 or M.shape != (2, T.shape[2]) or m.shape != M.shape
            or dt.shape != (T.shape[1]-1, T.shape[2]) or np.any(dt <= 0)):
        raise ValueError("two support histories and positive panel durations required")
    alpha = 1e-4
    M, m = M[:, None], m[:, None]
    lower, upper = np.minimum(T[:, :-1], T[:, 1:]), np.maximum(T[:, :-1], T[:, 1:])+ADDED_DUTY_LIMITS[:, None, None]
    lo, hi = (series_state(t, M, m, dimension=2) for t in (lower, upper))
    for state, target in ((lo, lower), (hi, upper)):
        residual = abs(state["effective_tension"]-target)/np.maximum(1., target)
        if residual.max() > 1e-12 or state["force_margin"].min() <= .2:
            raise ValueError("Constitutive inversion leaves its resolved-margin domain")
    scale, tlo, thi = .9*M, lo["core_tension"], hi["core_tension"]
    Rlo, Rhi = np.hypot(tlo, scale), np.hypot(thi, scale)
    f, fp = hi["force_times_core_reference_span"], lo["force_derivative"]
    fpp = (scale**2/(2*Rlo**3)+(1-tlo/(2*Rlo))/(2*Rlo))/lo["core_linear_stretch"]
    jlo, jhi = lo["joint_stretch"], hi["joint_stretch"]
    jp = alpha*fp*jhi**3/m
    jpp = alpha*fpp*jhi**3/m+3*alpha**2*fp**2*jhi**5/m**2
    Dmin = 1+alpha*hi["force_derivative"]*jlo+alpha**2*lo["force_times_core_reference_span"]*hi["force_derivative"]*jlo**3/m
    Dp = alpha*(fpp*jhi+2*fp*jp+f*jpp)
    core_second = scale**2/Rlo**3/Dmin**2+(thi/Rhi)*Dp/Dmin**3
    jt, jtt = m*jp*(1-jhi**-2), m*(jpp*(1-jhi**-2)+2*jp*jp/jlo**3)
    curvature = core_second+jtt/Dmin**2+jt*Dp/Dmin**3
    eprime = (thi/Rhi+2*alpha*f*jp)/Dmin
    inflate = lambda a: np.nextafter(np.asarray(a)*(1+FLOAT_GUARD)+1e-15, np.inf)
    curvature = inflate(curvature)
    rate = np.diff(T, axis=1)/dt[None]
    baseline = (curvature*ADDED_DUTY_LIMITS[:, None, None]*abs(rate)).sum(axis=0)
    gain = (eprime[0]+.5*eprime[1])/3
    baseline_cprime = ROTOR_RADIUS*(curvature[0]*abs(rate[0])+.5*curvature[1]*abs(rate[1]))/3
    return dict(curvature=curvature, gain_upper=inflate(gain),
        trace_curvature_upper=inflate((curvature[0]+.25*curvature[1])/9),
        baseline_cprime_upper=inflate(baseline_cprime), baseline_power_upper=inflate(baseline),
        baseline_power_l2_upper=inflate(np.sum(baseline**2*dt, axis=0)),
        minimum_force_margin=float(min(lo["force_margin"].min(), hi["force_margin"].min())))


def reaction_initial_energy(tension, core_inventory, joint_inventory):
    pilot_energy = 3*SHORT_DELAY*PHOTON_PILOT
    amplitude = (FIELD_BIAS_ENERGY+pilot_energy)/3
    T, M, m = map(np.asarray, (tension, core_inventory, joint_inventory))
    before = series_state(T, M, m, dimension=2)
    after = series_state(T+np.array([1., .5])[:, None]*amplitude, M, m, dimension=2)
    return FIELD_BIAS_ENERGY+(after["total_energy"]-before["total_energy"]).sum(axis=0)


def guide_trace_rate_bounds():
    b = guide_bounds()
    lo, hi = b["radius_minimum"], b["radius_maximum"]
    amplitude = hi-lo
    d1, d2, d3 = 2.1875/RAMP_TIME, 8/RAMP_TIME**2, 60/RAMP_TIME**3
    xd, xdd, v = amplitude*d1, amplitude*d2, b["maximum_speed"]
    gamma, acc = 1/np.sqrt(1-v*v), b["maximum_acceleration_parameter"]
    gd = gamma**2*GUIDE_RADIUS**2*xd*xdd
    gd_per = gamma**2*GUIDE_RADIUS**2*xd*d2
    ad_per = GUIDE_RADIUS**2*gamma**2*((xd+2*gd*hi)*d2+hi*d3)
    per = GUIDE_MASS*((d1*gamma+hi*gamma*gd_per)*(v*v+acc/(1-acc))
                     +hi*gamma*(2*v*GUIDE_RADIUS*d2+ad_per/(1-acc)**2))
    old_per = 2*((b["output_power_variation_per_radius_change"]/RAMP_TIME)**2*(RAMP_TIME+1)
                 +(b["guide_energy_variation_per_radius_change"]/RAMP_TIME)**2*RAMP_TIME)
    return dict(peak=per*amplitude, derivative_per_radius_change=per,
                l2_to_old_guide_l2=per*per*RAMP_TIME/old_per)


def forcing_history_bounds(receipt_l2, guide_l2, loop_l2, baseline_power_l2, baseline_power_peak):
    """Minkowski bound on N-(1+c)Wdot-c*Pi_g_dot-P_baseline, in delta units."""
    receipt, guide, loop = map(np.asarray, (receipt_l2, guide_l2, loop_l2))
    if receipt.shape != guide.shape or receipt.shape != loop.shape or np.any(np.minimum.reduce([receipt, guide, loop]) < 0):
        raise ValueError("matching nonnegative inherited forcing bounds required")
    old_edge = 2*(CONVERTER_DELAY*CONVERTER_NET_POWER/SPIN_FLOOR*2.1875/CONVERTER_RAMP)**2*(CONVERTER_RAMP+CONVERTER_DELAY)
    event_ratio = loop/old_edge
    events = np.rint(event_ratio)
    if not np.allclose(events, event_ratio, rtol=2e-10, atol=2e-10):
        raise ValueError("Archived converter bound does not identify integer events")
    Wrate = 3*SHORT_DELAY*(PHOTON_PEAK-PHOTON_PILOT)*2.1875/CONVERTER_RAMP
    W2 = 2*Wrate**2*(CONVERTER_RAMP+2*SHORT_DELAY)*events
    gb = guide_trace_rate_bounds()
    g2 = gb["l2_to_old_guide_l2"]*guide
    old = (np.sqrt(2*(receipt+guide))+np.sqrt(loop))**2
    total = (np.sqrt(old)+(1+C_MAX)*np.sqrt(W2)+C_MAX*np.sqrt(g2)
             +np.sqrt(np.asarray(baseline_power_l2))[None])**2
    b = guide_bounds()
    old_peak = (b["maximum_nominal_store_net_power"]
                +CONVERTER_DELAY*CONVERTER_NET_POWER/SPIN_FLOOR*2.1875/CONVERTER_RAMP)
    peak = old_peak+(1+C_MAX)*Wrate+C_MAX*gb["peak"]+np.asarray(baseline_power_peak)
    return dict(power_l2_upper=np.nextafter(total*(1+FLOAT_GUARD), np.inf),
        power_peak_upper=peak*(1+FLOAT_GUARD), inherited_network_l2=old,
        finite_line_l2=W2, guide_trace_l2=g2, events=events.astype(int),
        external_trace_rate_upper=ROTOR_RADIUS*(Wrate+gb["peak"]))


def rotor_trace_bound(inventory=18.):
    S = np.sqrt(1-SPEED_BOUND**2)
    return inventory*(PHI_BOUND+DAMPING*RADIUS_ERROR_BOUND*H_MAX*SPEED_BOUND
                      +(H_MAX+RADIUS_ERROR_BOUND)*(1-S))


def history_result(power_l2, initial_support_energy, *, inventory=18., original_energy_floor,
                   original_dynamic_energy, guide_trace_bound, initial_heat=1e-8):
    """Return conditional spin/energy screens, preserving failed bounds."""
    if not 18 <= inventory <= 20:
        raise ValueError("Certificate inventories lie in [18,20]")
    E0, power_l2 = np.asarray(initial_support_energy, float), np.asarray(power_l2, float)
    if (E0.ndim != 1 or power_l2.ndim != 2 or power_l2.shape[-1] != len(E0)
            or not np.isfinite(E0).all() or not np.isfinite(power_l2).all()
            or np.any(E0 < FIELD_BIAS_ENERGY) or np.any(power_l2 < 0)
            or not np.isfinite(initial_heat) or initial_heat < 0):
        raise ValueError("nonnegative forcing, prepared support energy and matching label axes required")
    Wmax, W0 = 3*SHORT_DELAY*PHOTON_PEAK, 3*SHORT_DELAY*PHOTON_PILOT
    A = rotor_trace_bound(inventory)+guide_trace_bound
    support_ceiling = FIELD_BIAS_ENERGY+C_MAX*(FIELD_BIAS_ENERGY+A+Wmax)
    combined_ceiling = support_ceiling+Wmax
    hlow = original_energy_floor-(combined_ceiling-E0-W0)/inventory
    hhigh = (original_dynamic_energy-GUIDE_MASS+E0-FIELD_BIAS_ENERGY)/inventory
    heat = initial_heat+HEAT_GAIN*ROTOR_RADIUS/inventory**2*power_l2
    S = np.sqrt(1-SPEED_BOUND**2)
    penalty = RADIUS_ERROR_BOUND**2+2*H_MAX*(H_MAX+RADIUS_ERROR_BOUND)*(1-S)
    spin2 = hlow[None]**2-1-2*heat-penalty
    capacity = .5*(hlow**2-1-SPIN_FLOOR**2-penalty)
    return dict(energy_floor=hlow, energy_ceiling=hhigh, thermal_action_upper=heat,
        thermal_action_capacity=capacity, spin_squared_lower=spin2,
        thermal_energy_upper=inventory*heat/((hlow[None]-RADIUS_ERROR_BOUND)*S),
        energy_domain_passed=(hlow >= H_MIN) & (hhigh <= H_MAX),
        spin_passed=spin2 > SPIN_FLOOR**2, support_energy_ceiling=support_ceiling,
        support_and_line_energy_ceiling=combined_ceiling, dynamic_trace_upper=A,
        added_outer_duty_upper=(FIELD_BIAS_ENERGY+A+Wmax)/3)
