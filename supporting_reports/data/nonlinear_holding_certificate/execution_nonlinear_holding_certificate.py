"""A nonlinear thermal and spin certificate for the local holding ensemble.

The proof uses the existing rail-transfer envelope, including guide and
converter flights. It preserves the other rail components as independent
suppliers of their own tensors, currents, reaction paths and controller work.
"""
from fractions import Fraction as F
from itertools import product, permutations

import numpy as np

from .scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_NET_POWER, CONVERTER_RAMP, GUIDE_MASS,
    GUIDE_RADIUS, PILOT_POWER, RAMP_TIME, ROTOR_DAMPING, ROTOR_MASS,
    ROTOR_RADIUS, SPIN_FLOOR, guide_bounds, preparation,
)

H_MIN, H_MAX = 1.117, 1.3001
INPUT_MAX = .00155
W_DOMAIN, V_DOMAIN = .012, .012
W_BOUND, V_BOUND = .00913, .00818
THERMAL_GAIN = 3.4
DECAY_RATE = .175
P_INVARIANT = np.array([[1., .24], [.24, 1.]])
P_THERMAL = np.array([[1.1, .24], [.24, 1.1]])


def guide_input_certificate():
    """Uniform analytic positivity of guide input for every allowed ramp.

    On a falling septic ramp, 1-f >= 35*s^3*(1-s)^4. Minimizing
    A*z^4-B*z^3 on z>=0 bounds the negative work correction even near
    the pilot endpoint. Acceleration and gamma derivatives are bounded
    separately, as in the original inverse guide envelope.
    """
    b = guide_bounds()
    lo, hi = b["radius_minimum"], b["radius_maximum"]
    amplitude = hi-lo
    speed = b["maximum_speed"]
    gamma = 1/np.sqrt(1-speed*speed)
    acceleration = b["maximum_acceleration_parameter"]
    xd, xdd = amplitude*2.1875/RAMP_TIME, amplitude*8/RAMP_TIME**2
    log_gamma_rate = gamma**2*GUIDE_RADIUS**2*xd*xdd
    accel_rate = GUIDE_RADIUS**2*gamma**2*(
        (2*log_gamma_rate*hi+xd)*xdd+hi*amplitude*60/RAMP_TIME**3)
    hmax = b["maximum_energy"]/GUIDE_MASS
    derivative_correction = GUIDE_MASS*hmax*(log_gamma_rate+accel_rate/(1-acceleration))
    A = 35*5/hi**3
    B = 140*GUIDE_MASS*hmax/(lo*RAMP_TIME)
    falling_work = amplitude*27*B**4/(256*A**3)
    lower = PILOT_POWER-b["output_correction_bound"]-derivative_correction-falling_work
    if lower <= 0:
        raise ValueError("Guide input positivity is unproved by this envelope")
    rotor = preparation()
    net_max = (b["maximum_nominal_store_net_power"]
               +CONVERTER_DELAY*CONVERTER_NET_POWER/SPIN_FLOOR*2.1875/CONVERTER_RAMP)
    result = dict(input_power_lower_bound=float(lower), falling_work_correction=float(falling_work),
        acceleration_derivative_correction=float(derivative_correction),
        rotor_energy_lower_bound=rotor["quasistatic_rotor_energy_floor"],
        rotor_energy_upper_bound=(rotor["initial_dynamic_energy"]-GUIDE_MASS)/ROTOR_MASS,
        net_power_upper_bound=net_max, reduced_input_upper_bound=ROTOR_RADIUS*net_max/ROTOR_MASS)
    if (result["rotor_energy_lower_bound"] < H_MIN or result["rotor_energy_upper_bound"] > H_MAX
            or result["reduced_input_upper_bound"] > INPUT_MAX):
        raise ValueError("Rail envelope exceeds the fixed nonlinear-certificate domain")
    return result


def reduced_rhs(state, *, damping=ROTOR_DAMPING):
    """Exact derivatives in s=t/R0 for state (w,y,h,b,u).

    Here w=x-h, y=p=h*v, u=R0*q/M. The returned first four derivatives
    evolve w,y,h,b; u is the specified input at the current time.
    """
    w, y, h, b, u = np.asarray(state, float)
    x, v = h+w, y/h
    if (not np.isfinite([w, y, h, b, u, damping]).all() or h <= 0
            or x <= 0 or abs(v) >= 1 or b < 0 or damping < 0):
        raise ValueError("positive energies/radius and subluminal radial motion required")
    s = np.sqrt(1-v*v)
    d = damping+s*v/(x*(1+s))-u/h
    return np.array([y/h-u, -s/x*w-d*y, u, damping*x/(h*s)*y*y])


def spin_squared(w, y, h, thermal_action):
    x, v = h+w, y/h
    return 2*x*h*np.sqrt(1-v*v)-x*x-1-2*thermal_action


def _determinant(matrix):
    n = len(matrix)
    total = F(0)
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i+1, n))
        term = F((-1)**inversions)
        for i, j in enumerate(order):
            term *= matrix[i][j]
        total += term
    return total


def _leading_minors(matrix):
    return [_determinant([row[:i] for row in matrix[:i]]) for i in range(1, len(matrix)+1)]


def rational_certificate():
    """Verify the coefficient enclosure and all LMIs in exact rational arithmetic.

    Affinity in omega, e and d extends the vertex inequalities to every
    time-varying coefficient inside their rectangular enclosure.
    """
    h0, h1, w, v, umax = map(F, ("1.117", "1.3001", ".012", ".012", ".00155"))
    s0 = F(".99992799")
    assert s0*s0 <= 1-v*v
    assert F(".7691") <= 1/h1 and 1/h0 <= F(".8953")
    assert (w+h1*(1-s0))/(h0*(h0-w)) <= F(".00981")
    assert v/((h0-w)*(1+s0))+umax/h0 <= F(".00682")
    assert F(".4")*(1+w/h0)/s0 <= F(".4044")
    P = [[F(1), F(".24")], [F(".24"), F(1)]]
    Q = [[F("1.1"), F(".24")], [F(".24"), F("1.1")]]
    assert all(d > 0 for matrix in (P, Q) for d in _leading_minors(matrix))
    rows = []
    for om, e, d in product((".7691", ".8953"), ("-.00981", ".00981"), (".39318", ".40682")):
        omega, epsilon, damping = map(F, (om, e, d))
        A = [[F(0), omega], [-omega-epsilon, -damping]]
        def lyapunov(R):
            return [[sum(A[k][i]*R[k][j]+R[i][k]*A[k][j] for k in range(2))
                     for j in range(2)] for i in range(2)]
        L = lyapunov(P)
        invariant = [[-L[i][j]-2*F(".175")*P[i][j] for j in range(2)] for i in range(2)]
        L = lyapunov(Q)
        thermal = [[-L[i][j]-(F(".4044") if i == j == 1 else 0) for j in range(2)]
                   +[Q[i][0]] for i in range(2)]
        thermal.append([Q[0][0], Q[0][1], F("3.4")])
        minors = _leading_minors(invariant)+_leading_minors(thermal)
        if min(minors) <= 0:
            raise ValueError("A rational certificate matrix lacks strict definiteness")
        rows.append(dict(omega=om, epsilon=e, damping=d,
            invariant_principal_minors=[str(z) for z in minors[:2]],
            thermal_principal_minors=[str(z) for z in minors[2:]]))
    level = (umax/F(".175"))**2
    inverse_diagonal = 1/(1-F(".24")**2)
    assert level*inverse_diagonal < F(".00913")**2
    assert level*inverse_diagonal/h0**2 < F(".00818")**2
    return dict(coefficient_domain_verified=True, vertices=rows,
        invariant_level=str(level), maximum_radius_error=W_BOUND, maximum_radial_speed=V_BOUND,
        gain=THERMAL_GAIN, invariant_matrix=P_INVARIANT.tolist(), thermal_matrix=P_THERMAL.tolist())


def history_certificate(power_l2_upper, *, initial_heat=1e-8, initial_error=(0., 0.)):
    """Certify heat and spin under the established whole-history input envelope."""
    q2 = np.asarray(power_l2_upper, float)
    z0 = np.asarray(initial_error, float)
    if (not np.isfinite(q2).all() or np.any(q2 < 0) or z0.shape != (2,)
            or not np.isfinite(z0).all() or not np.isfinite(initial_heat) or initial_heat < 0):
        raise ValueError("finite nonnegative forcing/heat and two initial errors required")
    if z0@P_INVARIANT@z0 > (INPUT_MAX/DECAY_RATE)**2:
        raise ValueError("Initial radial state lies outside the invariant ellipse")
    heat = initial_heat+z0@P_THERMAL@z0+THERMAL_GAIN*ROTOR_RADIUS/ROTOR_MASS**2*q2
    s_lower = .99996654
    assert s_lower*s_lower <= 1-V_BOUND**2
    radial_penalty = W_BOUND**2+2*H_MAX*(H_MAX+W_BOUND)*(1-s_lower)
    spin_lower_squared = H_MIN**2-1-2*heat-radial_penalty
    thermal_ceiling = .5*(H_MIN**2-1-SPIN_FLOOR**2-radial_penalty)
    # Pi/M=h-x*sqrt(1-v²)-k*x*p, with |p|=|y|<=W_BOUND.
    trace = ROTOR_MASS*(W_BOUND+(H_MAX+W_BOUND)*(1-s_lower)
                         +ROTOR_DAMPING*(H_MAX+W_BOUND)*W_BOUND)
    return dict(thermal_action_upper=heat, spin_squared_lower=spin_lower_squared,
        thermal_energy_upper=ROTOR_MASS*heat/((H_MIN-W_BOUND)*s_lower),
        spin_upper_squared=H_MAX**2-1, radius_minimum=H_MIN-W_BOUND,
        thermal_action_ceiling=thermal_ceiling, rotor_trace_magnitude_upper=trace,
        passed=spin_lower_squared > SPIN_FLOOR**2)
