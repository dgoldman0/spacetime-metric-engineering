"""Scheduled optical guides and a mechanical holding-store candidate.

Units are C=P_peak*delta for energy and delta for time. The rotor uses the
same stiff elastic string law as the earlier optical wall. Opposite spins
cancel total angular momentum; reference inventory, strain and torque-port
traffic remain explicit. Material realization and spatial ports are gates.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .constitutive_joints_and_optics import series_state
from .material_reconfiguration import MATERIAL_DIMENSIONS, PRESSURE_BASIS

GUIDE_MASS = 10/3
GUIDE_RADIUS = 1/(3*np.pi)
PILOT_POWER = .001
RAMP_TIME = 128.
ROTOR_MASS = 18.
ROTOR_RADIUS = 1/(12*np.pi)
ROTOR_DAMPING = .4
INITIAL_ROTOR_ENERGY = 1.3
SPIN_FLOOR = .3
CONVERTER_DELAY = 1/16
CONVERTER_NET_POWER = 1.5


def smooth_step(time, duration):
    """Septic position ramp, with three vanishing endpoint derivatives."""
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("positive finite ramp duration required")
    t = np.asarray(time, float)
    if not np.isfinite(t).all():
        raise ValueError("finite time required")
    s = np.clip(t/duration, 0, 1)
    active = (t >= 0) & (t <= duration)
    return (s**4*(35+s*(-84+s*(70-20*s))),
        np.where(active, 140*s**3*(1-s)**3/duration, 0.),
        np.where(active, 420*s*s*(1-s)**2*(1-2*s)/duration**2, 0.),
        np.where(active, 840*s*(1-s)*(1-5*s+5*s*s)/duration**3, 0.))


def guide_radius(power):
    p = np.asarray(power, float)
    if not np.isfinite(p).all() or np.any(p < 0) or np.any(p >= 2.5):
        raise ValueError("guide power must be finite and in [0,2.5)")
    return 1/np.sqrt(1-.4*p)


def inverse_guide(time, left_power, right_power, *, duration=RAMP_TIME):
    """Inverse dynamics for one smooth radial guide ramp.

    Constant escape depth is one. Ports are evaluated from the full radial
    equations, including the acceleration pressure, rather than assumed
    to remain in instantaneous equilibrium. Powers include the pilot.
    """
    x0, x1 = guide_radius(left_power), guide_radius(right_power)
    f, f1, f2, f3 = smooth_step(time, duration)
    a = x1-x0
    x, xd, xdd, xddd = x0+a*f, a*f1, a*f2, a*f3
    v = GUIDE_RADIUS*xd
    if np.any(abs(v) >= 1):
        raise ValueError("guide ramp is superluminal")
    gamma = 1/np.sqrt(1-v*v)
    gd = gamma**2*GUIDE_RADIUS**2*xd*xdd  # gamma_dot / gamma
    b = gamma**2*x*GUIDE_RADIUS**2*xdd
    bd = GUIDE_RADIUS**2*gamma**2*((2*gd*x+xd)*xdd+x*xddd)
    if np.any(b >= 1):
        raise ValueError("guide acceleration exceeds positive-energy inverse domain")
    e, tension = .5*(x+1/x), .5*(x-1/x)
    photons = (tension+b*e)/(1-b)
    h = gamma*x/(1-b)
    hd = h*(gd+xd/x+bd/(1-b))
    outgoing = GUIDE_MASS*photons/(2*np.pi*GUIDE_RADIUS*x)
    incoming = outgoing+GUIDE_MASS*hd
    trace = GUIDE_MASS*(h*v*v+(photons-tension)/gamma)
    return dict(radius=x, momentum=h*v, photon_action=x*photons,
        energy=GUIDE_MASS*h, energy_rate=GUIDE_MASS*hd,
        input_power=incoming, output_power=outgoing, pressure_trace=trace,
        speed=v, acceleration_parameter=b)


def guide_bounds(*, duration=RAMP_TIME, pilot=PILOT_POWER):
    """Conservative derivative, output and inventory bounds for all ramps.

    Useful plateaus lie in [0,1]; additive pilot covers the acceleration
    correction to the output-power envelope. Input positivity is additionally
    screened against the actual ramp family by the audit.
    """
    if not np.isfinite([duration, pilot]).all() or duration <= 0 or not 0 < pilot < 1:
        raise ValueError("positive duration and pilot in (0,1) required")
    lo, hi = guide_radius(pilot), guide_radius(1+pilot)
    a = hi-lo
    d1, d2, d3 = 2.1875/duration, 8/duration**2, 60/duration**3
    xd, xdd = a*d1, a*d2
    v = GUIDE_RADIUS*xd
    if v >= 1:
        raise ValueError("ramp speed bound exceeds light speed")
    gamma = 1/np.sqrt(1-v*v)
    b = gamma**2*hi*GUIDE_RADIUS**2*xdd
    if b >= 1:
        raise ValueError("ramp acceleration bound exceeds inverse domain")
    bd_per_amplitude = GUIDE_RADIUS**2*gamma**2*(
        xd*d2+hi*d3+2*gamma**2*GUIDE_RADIUS**2*hi*xd*xdd*d2)
    hmax = gamma*hi/(1-b)
    hd_per_amplitude = hmax*(gamma**2*GUIDE_RADIUS**2*xd*d2+d1/lo+bd_per_amplitude/(1-b))
    q_error = 5*b/(1-b)
    qmax = 1+pilot+q_error
    umax = qmax+GUIDE_MASS*a*hd_per_amplitude
    qd_per_amplitude = 5*d1/lo**3+5*bd_per_amplitude/(1-b)**2
    return dict(radius_minimum=lo, radius_maximum=hi, maximum_speed=v,
        maximum_acceleration_parameter=b, output_correction_bound=q_error,
        output_envelope_margin=pilot-q_error,
        maximum_output_power=qmax, maximum_input_power=umax,
        maximum_energy=GUIDE_MASS*hmax, initial_energy=GUIDE_MASS*lo,
        guide_energy_variation_per_radius_change=GUIDE_MASS*duration*hd_per_amplitude,
        output_power_variation_per_radius_change=duration*qd_per_amplitude,
        maximum_nominal_store_net_power=1+a*(qd_per_amplitude+GUIDE_MASS*hd_per_amplitude))


def rotor_state(state):
    """Axisymmetric stiff-string rotor plus contained thermal radiation.

    j=J/(M R0) is radial-comoving tangential speed; lab tangential speed is
    j/gamma_r. Heat action b has pressure b/x, with entropy proportional to
    sqrt(b) for the equilibrated 1D radiation specialization.
    """
    x, p, j, b = np.asarray(state, float)
    if (not np.isfinite([x, p, j, b]).all() or np.any(x <= 0)
            or np.any(abs(j) >= 1) or np.any(b < 0)):
        raise ValueError("positive radius, subluminal spin and nonnegative heat required")
    e, tension = .5*(x+1/x), .5*(x-1/x)
    V = e+(j*j/2+b)/x
    h = np.hypot(p, V)
    v, gamma = p/h, h/V
    return dict(energy=h, rest_energy=V, radial_speed=v, gamma=gamma,
        tangential_speed=j/gamma, proper_stretch=x/np.sqrt(1-j*j),
        pressure_trace=h*v*v+((j*j/2+b)/x-tension)/gamma,
        thermal_energy=gamma*b/x, entropy_proxy=np.sqrt(b))


def rotor_rhs(state, net_power, *, inventory=ROTOR_MASS, radius=ROTOR_RADIUS, damping=ROTOR_DAMPING):
    """Matched torque and radial momentum; viscous work becomes internal heat."""
    if (not np.isfinite([net_power, inventory, radius, damping]).all()
            or min(inventory, radius) <= 0 or damping < 0):
        raise ValueError("finite power, positive scales and nonnegative damping required")
    x, p, j, b = np.asarray(state, float)
    if not 0 < j < 1 or x <= 0:
        raise ValueError("powered rotor needs positive, subluminal spin")
    # Smooth extension across b=0 for internal Runge-Kutta stages only.
    V = .5*(x+(1+j*j+2*b)/x)
    h = np.hypot(p, V)
    v, gamma = p/h, h/V
    friction = damping*p/radius
    return np.array([v/radius,
        (1+j*j+2*b-x*x)/(2*gamma*x*x*radius)+v*net_power/inventory-friction,
        x*net_power/(gamma*inventory*j), gamma*x*friction*v])


def rotor_optical_ports(power, spin):
    """Powers crossing moving reflective facets, for positive spin.

    Pin-Pout=q, Pin+Pout=|q|/j. The sum counts two-port optical exposure,
    with absorption per moving-mirror encounter needing its own spectrum
    and frame convention. Discharge needs an incident seed.
    """
    q, j = np.broadcast_arrays(np.asarray(power, float), np.asarray(spin, float))
    if not np.isfinite(q).all() or not np.isfinite(j).all() or np.any((j <= 0) | (j >= 1)):
        raise ValueError("finite power and positive subluminal spin required")
    return dict(incoming=(abs(q)+j*q)/(2*j), outgoing=(abs(q)-j*q)/(2*j),
                total_port_exposure=abs(q)/j, maximum_doppler_ratio=(1+j)/(1-j))


def reflect_seed(state, incident_energy, *, direction=-1, inventory=ROTOR_MASS):
    """Exact finite pulse recoil at fixed radius, including radial boost.

    Direction +1 charges the rotor; -1 extracts rotational energy. Pulse
    energies are in the local lab frame. Propagation to the next encounter
    is an additional counted flight, and facets must supply tangential
    reflection rather than the smooth ring's radial surface normal.
    """
    if not np.isfinite([incident_energy, inventory]).all() or incident_energy <= 0 or inventory <= 0 or direction not in (-1, 1):
        raise ValueError("positive incident pulse/inventory and direction +/-1 required")
    x, p, j, b = np.asarray(state, float)
    s = rotor_state(state)
    local_in = incident_energy/s["gamma"]
    linear = 1+direction*j
    total_local = 4*local_in/(linear+np.sqrt(linear*linear+4*x*local_in/inventory))
    outgoing = s["gamma"]*(total_local-local_in)
    jnew = j+direction*x*total_local/inventory
    Vnew = .5*(x+(1+jnew*jnew+2*b)/x)
    new = np.array([x, s["gamma"]*s["radial_speed"]*Vnew, jnew, b])
    rotor_state(new)
    return dict(state=new, outgoing_energy=outgoing,
                rotor_energy_change=incident_energy-outgoing,
                angular_impulse_over_reference_radius=inventory*(jnew-j))


def preparation(*, inventory=ROTOR_MASS):
    """Count cold guide, pilot paths, mechanical store and static route walls.

    Converter photons are filled from the rotor and capped separately;
    their maximum inventory reduces usable spin/heat capacity. Static
    support prices remain a variable-load material-evolution requirement.
    """
    if not np.isfinite(inventory) or inventory <= 0:
        raise ValueError("positive finite rotor inventory required")
    bound = guide_bounds()
    converter_photons = CONVERTER_DELAY*CONVERTER_NET_POWER/SPIN_FLOOR
    route_wall = 2.6*(2.75+converter_photons)
    initial = bound["initial_energy"]+PILOT_POWER+inventory*INITIAL_ROTOR_ENERGY
    maximum_flight_and_guide = bound["maximum_energy"]+1+.5*(
        bound["maximum_input_power"]+bound["maximum_output_power"])+converter_photons
    rotor_floor = (initial-maximum_flight_and_guide)/inventory
    heat_action_capacity = .5*(rotor_floor**2-1-SPIN_FLOOR**2)
    return dict(**bound, candidate_preparation=initial+route_wall,
        initial_dynamic_energy=initial, route_wall_energy=route_wall,
        converter_photon_capacity=converter_photons,
        quasistatic_rotor_energy_floor=rotor_floor,
        quasistatic_heat_action_capacity=heat_action_capacity,
        quasistatic_heat_energy_capacity=inventory*heat_action_capacity/rotor_floor,
        initial_reference_inventory=inventory+GUIDE_MASS)


def schedule_exposure(panel_peaks, node_peaks, duration, delay):
    """Conservative cumulative exposure with ramps, pilot and converter legs.

    Powers have shape (node,panel,label). Up-ramps finish before a useful
    plateau rises; down-ramps start after it falls. The outgoing and feed
    flight advances are each delta/2. Entire upcoming ramp allowances are
    charged to the preceding panel's end for interior loss screening.

    Converter net variation is bounded by 2*integral(A)+3*TV(Hg)+delta*TV(Q).
    No smoothness of the prescribed receipt is assumed in the first term.
    Restart exposure includes a full charge/discharge of converter photons
    at every changing plateau. These are exposure bounds, not a port control
    solution through its finite recirculation flight.
    """
    P, peak, dt, delta = map(lambda a: np.asarray(a, float), (panel_peaks, node_peaks, duration, delay))
    if (P.ndim != 3 or peak.shape != (P.shape[0], P.shape[2]) or dt.shape != P.shape[1:]
            or delta.shape != (P.shape[2],) or not all(np.isfinite(a).all() for a in (P, peak, dt, delta))
            or np.any(P < 0) or np.any(peak < 0) or np.any(dt <= 0) or np.any(delta <= 0)
            or np.any(P > peak[:, None]*(1+1e-12))):
        raise ValueError("nonnegative bounded node-panel powers and positive matching durations required")
    if np.min(dt/delta) <= 2*(RAMP_TIME+1):
        raise ValueError("panels are too short for separated preview/decay ramps")
    normalized = np.divide(P, peak[:, None], out=np.zeros_like(P), where=peak[:, None] > 0)
    padded = np.concatenate([np.zeros_like(normalized[:, :1]), normalized,
                              np.zeros_like(normalized[:, :1])], axis=1)
    steps = abs(np.diff(padded, axis=1))
    changes = steps > 0
    radius_steps = abs(np.diff(guide_radius(padded+PILOT_POWER), axis=1))
    C = peak*delta
    bound = guide_bounds()
    edge_guide = C[:, None]*RAMP_TIME*(steps+bound["output_correction_bound"]*changes)
    edge_Hvar = C[:, None]*bound["guide_energy_variation_per_radius_change"]*radius_steps
    edge_Qvar = C[:, None]*bound["output_power_variation_per_radius_change"]*radius_steps
    useful = np.cumsum(P*dt, axis=1)
    base = np.cumsum((P+PILOT_POWER*peak[:, None])*dt, axis=1)
    def edge_prefix(array):
        return np.cumsum(array, axis=1)[:, 1:]
    guide = base+edge_prefix(edge_guide)+2*(RAMP_TIME+1)*PILOT_POWER*C[:, None]
    converter_net = 2*useful+3*edge_prefix(edge_Hvar)+edge_prefix(edge_Qvar)
    boot_per_change = 2*preparation()["converter_photon_capacity"]/SPIN_FLOOR
    bootstrap = boot_per_change*C[:, None]*edge_prefix(changes.astype(float))
    converter = converter_net/SPIN_FLOOR+bootstrap
    exposure = 3*guide+useful+converter
    return dict(useful_upper=useful.sum(axis=0), guide_upper=guide.sum(axis=0),
        converter_upper=converter.sum(axis=0), bootstrap_upper=bootstrap.sum(axis=0),
        total_exposure_upper=exposure.sum(axis=0),
        changed_plateaus=changes.sum(axis=1),
        minimum_panel_over_delay=float(np.min(dt/delta)))


def receipt_derivative_bound(tension, core_inventory, joint_inventory, fields,
                             target, lr, lt, duration, *, reference_fraction=1e-4):
    """Absolute within-panel power derivatives for the inherited joint law.

    Independent positive interval products enclose the second derivatives
    of core and joint energies. This resolves short-flight receipt changes
    without replacing them by the much wider whole-panel power intervals.
    The positive part of a Lipschitz power has the same Lipschitz bound.
    """
    dt = np.asarray(duration)
    d = MATERIAL_DIMENSIONS[:, None, None]
    M, m = core_inventory[:, None], joint_inventory[:, None]
    low = series_state(np.minimum(tension[:, :-1], tension[:, 1:]), M, m, dimension=d,
                       reference_fraction=reference_fraction)
    high = series_state(np.maximum(tension[:, :-1], tension[:, 1:]), M, m, dimension=d,
                        reference_fraction=reference_fraction)
    alpha = reference_fraction
    s = np.where(d == 2, .9, 1.)*M
    tlo, thi = low["core_tension"], high["core_tension"]
    Rlo, Rhi = np.hypot(tlo, s), np.hypot(thi, s)
    f, fp = high["force_times_core_reference_span"], low["force_derivative"]
    fpp = (s*s/(d*Rlo**3)+(1-tlo/(d*Rlo))/(d*Rlo))/low["core_linear_stretch"]
    jlo, jhi = low["joint_stretch"], high["joint_stretch"]
    jp = alpha*fp*jhi**3/m
    jpp = alpha*fpp*jhi**3/m+3*alpha**2*fp**2*jhi**5/m**2
    Dmin = (1+alpha*high["force_derivative"]*jlo
            +alpha**2*low["force_times_core_reference_span"]*high["force_derivative"]*jlo**3/m)
    Dp = alpha*(fpp*jhi+2*fp*jp+f*jpp)
    core_second = s*s/Rlo**3/Dmin**2+(thi/Rhi)*Dp/Dmin**3
    joint_first_t = d*m/2*jp*(1-jhi**-2)
    joint_second_t = d*m/2*(jpp*(1-jhi**-2)+2*jp*jp/jlo**3)
    joint_second = joint_second_t/Dmin**2+joint_first_t*Dp/Dmin**3
    load_rate = np.diff(tension, axis=1)/dt
    dz, da = np.diff(np.log(lr), axis=0)/dt, np.diff(np.log(lt), axis=0)/dt
    work = PRESSURE_BASIS[0, :6, None, None]*dz+PRESSURE_BASIS[1, :6, None, None]*da
    core = core_second*load_rate**2+abs(load_rate*work)/Dmin
    joint = joint_second*load_rate**2+abs(load_rate*work)  # 0<=d(T-t)/dT<=1.
    field_rate = np.diff(fields, axis=1)/dt
    field_work = PRESSURE_BASIS[0, 6:10, None, None]*dz+PRESSURE_BASIS[1, 6:10, None, None]*da
    field = abs(field_rate*field_work)
    dust = ((core_second+joint_second)*load_rate**2).sum(axis=0)
    rail = abs(np.diff(target[1], axis=0)/dt*dz+2*np.diff(target[2], axis=0)/dt*da)
    return np.concatenate([core, joint, field, dust[None], rail[None]])


def delayed_receipt_l2_bound(left_power, right_power, derivative_bound, node_peak, duration, delay):
    """Bound integral |A(t)-A(t-delta)|^2 / (P_peak^2 delta).

    Interior points use the Lipschitz change over one flight. At each panel
    interface the exact positive-power jump plus two one-flight derivative
    allowances bounds the crossing interval. Endpoint extensions are zero.
    """
    peak = np.asarray(node_peak)[:, None]
    delta = np.asarray(delay)[None, None]
    normalize = lambda a: np.divide(a, peak, out=np.zeros_like(a), where=peak > 0)
    left, right = normalize(np.maximum(left_power, 0)), normalize(np.maximum(right_power, 0))
    rate = normalize(derivative_bound)*delta
    if np.any(np.asarray(duration) <= np.asarray(delay)):
        raise ValueError("flight must fit each panel")
    zero = np.zeros_like(left[:, :1])
    next_left, prev_right = np.concatenate([left, zero], axis=1), np.concatenate([zero, right], axis=1)
    slope = np.concatenate([rate, zero], axis=1)+np.concatenate([zero, rate], axis=1)
    crossing = np.minimum(1., abs(next_left-prev_right)+slope)**2
    interior = np.minimum(1., rate)**2*(np.asarray(duration)/np.asarray(delay))
    return np.cumsum(interior, axis=1)+np.cumsum(crossing, axis=1)[:, 1:]


def guide_drive_l2_bound(panel_peaks, node_peak):
    """Normalized cumulative L2 bound for Q(t-.5)-U(t+.5).

    Separated guide ramps have |Q'| and |H'| bounded per radius change.
    The shifted Q difference has support at most RAMP_TIME+1, while H'
    has support RAMP_TIME. Endpoint guide levels include the pilot.
    """
    peak = np.asarray(node_peak)[:, None]
    normalized = np.divide(panel_peaks, peak, out=np.zeros_like(panel_peaks), where=peak > 0)
    padded = np.concatenate([np.zeros_like(normalized[:, :1]), normalized,
                             np.zeros_like(normalized[:, :1])], axis=1)
    changes = np.diff(guide_radius(padded+PILOT_POWER), axis=1)
    bound = guide_bounds()
    qrate = bound["output_power_variation_per_radius_change"]/RAMP_TIME
    hrate = bound["guide_energy_variation_per_radius_change"]/RAMP_TIME
    edge = 2*(qrate*qrate*(RAMP_TIME+1)+hrate*hrate*RAMP_TIME)*changes**2
    return np.cumsum(edge, axis=1)[:, 1:]


def frozen_thermal_gain(equilibrium_radius, *, inventory=ROTOR_MASS, damping=ROTOR_DAMPING):
    """Heat/C per normalized integral q^2 for a fixed linear equilibrium.

    This induced L2 gain covers the zero-initial-state linear radial mode.
    Applying it across a varying equilibrium is a diagnostic, requiring a
    separate nonlinear, variable-coefficient certificate for a full history.
    """
    h = np.asarray(equilibrium_radius, float)
    if (not np.isfinite(h).all() or not np.isfinite([inventory, damping]).all()
            or np.any(h <= 0) or inventory <= 0 or damping <= 0):
        raise ValueError("positive finite radius, inventory and damping required")
    a = damping*h
    # The peak leaves finite frequency at a=sqrt(2); DC then dominates.
    return np.where(a < np.sqrt(2),
        ROTOR_RADIUS/(inventory*damping*h*(1-a*a/4)),
        ROTOR_RADIUS*damping*h/inventory)


def simulate_transition(left, right, *, initial_heat=1e-8, damping=ROTOR_DAMPING,
                        inventory=ROTOR_MASS,
                        maximum_step=.08, output_step=.08, rtol=2e-9, atol=2e-11):
    """One isolated scheduled step with both local flights and useful delay.

    Receipt and panel envelope coincide on each plateau. Guide preview
    ensures exact receipt despite its smooth radial transition. All retained
    guide/path energy and rotor heat enter the integrated energy identity.
    Converter seed/recycle flight is screened separately, not hidden here.
    """
    if (not np.isfinite([left, right, initial_heat, damping]).all() or min(left, right, damping) < 0
            or initial_heat <= 0 or max(left, right) > 1):
        raise ValueError("unit-bounded plateaus, positive seed thermal action and nonnegative damping required")
    prep = preparation(inventory=inventory)
    onset = -RAMP_TIME-.5 if right >= left else -.5
    def guide(t):
        return inverse_guide(t-onset, left+PILOT_POWER, right+PILOT_POWER)
    initial_h = (prep["initial_dynamic_energy"]-GUIDE_MASS*guide_radius(left+PILOT_POWER)
                 -(left+PILOT_POWER)-left)/inventory
    j2 = initial_h**2-1-2*initial_heat
    if j2 <= SPIN_FLOOR**2:
        raise ValueError("initial heat leaves insufficient usable spin")
    state = np.array([initial_h, 0., np.sqrt(j2), initial_heat])
    start, end = -RAMP_TIME-2., RAMP_TIME+8.
    cuts = sorted(set([start, end, 0., 1., onset, onset-.5, onset+.5,
                       onset+RAMP_TIME, onset+RAMP_TIME-.5, onset+RAMP_TIME+.5]))
    cuts = [t for t in cuts if start <= t <= end]
    def spin(t, y):
        return y[2]-SPIN_FLOOR
    def causal(t, y):
        return .999-y[2]
    def tensile(t, y):
        return y[0]/np.sqrt(1-y[2]**2)-1
    for event in (spin, causal, tensile):
        event.terminal = True
        event.direction = -1
    records, times = [], []
    boundary = None
    for a, b in zip(cuts[:-1], cuts[1:]):
        m = (a+b)/2
        delayed_difference = (left if m < 1 else right)-(left if m < 0 else right)
        def rhs(t, y):
            q = delayed_difference+guide(t-.5)["output_power"]-guide(t+.5)["input_power"]
            return np.r_[rotor_rhs(y[:4], q, damping=damping, inventory=inventory), q]
        y0 = np.r_[state, 0.] if not records else np.r_[state, net_integral]
        solution = solve_ivp(rhs, (a, b), y0, method="DOP853", dense_output=True,
            max_step=maximum_step, rtol=rtol, atol=atol, events=(spin, causal, tensile))
        if not solution.success:
            raise ValueError(solution.message)
        rotor_state(solution.y[:4])
        stop = solution.t[-1]
        grid = np.linspace(a, stop, max(2, int(np.ceil((stop-a)/output_step))+1))
        if times:
            grid = grid[1:]
        times.append(grid)
        records.append(solution.sol(grid))
        state, net_integral = solution.y[:4, -1], solution.y[4, -1]
        if solution.status:
            boundary = ("spin", "causal", "tensile")[next(i for i, e in enumerate(solution.t_events) if len(e))]
            break
    time, values = np.concatenate(times), np.concatenate(records, axis=1)
    s = rotor_state(values[:4])
    q = (np.where(time < 1, left, right)-np.where(time < 0, left, right)
         +guide(time-.5)["output_power"]-guide(time+.5)["input_power"])
    # Gauss-Legendre integrates finite paths independently of rotor power.
    nodes, weights = np.polynomial.legendre.leggauss(20)
    F = .25*np.sum(weights[:, None]*guide(time[None]+.25*(nodes[:, None]+1))["input_power"], axis=0)
    G = .25*np.sum(weights[:, None]*guide(time[None]-.25*(nodes[:, None]+1))["output_power"], axis=0)
    O = left+(right-left)*np.clip(time, 0, 1)
    Hguide = guide(time)["energy"]
    rotor_energy = inventory*s["energy"]
    ledger = rotor_energy+Hguide+F+G+O
    return dict(time=time, state=values[:4], net_power=q, rotor_energy=rotor_energy,
        guide_energy=Hguide, guide_output=guide(time-.5)["output_power"],
        required_receipt=np.where(time < 0, left, right), feed_energy=F, output_energy=G, useful_inflight=O,
        thermal_energy=inventory*s["thermal_energy"], heat_action_increase=values[3]-initial_heat,
        pressure_trace=inventory*(s["pressure_trace"]-damping*values[0]*values[1]),
        proper_stretch=s["proper_stretch"], radial_speed=s["radial_speed"],
        rotor_energy_balance_error=rotor_energy-inventory*initial_h-values[4],
        complete_ledger_error=ledger-prep["initial_dynamic_energy"],
        ports=rotor_optical_ports(q, values[2]), complete=boundary is None, boundary=boundary)
