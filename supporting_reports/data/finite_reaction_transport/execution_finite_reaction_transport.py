"""Finite photon paths for the rail's separate reaction-work branch.

Two path lengths make the causal command inverse stable. Opposed spatial
copies cancel momentum; three equal axis populations supply isotropic
integrated stress. Endpoint commands are prescribed feedforward functions.
The relay ports are fixed; the mechanical transducer has its own geometry.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import sqrt

import numpy as np
from scipy.integrate import solve_ivp
from scipy.signal import lfilter

from .constitutive_joints_and_optics import series_state
from .coupled_rail_reactions import scalar_sheet_state, guide_trace_rate
from .scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_NET_POWER, CONVERTER_RAMP, GUIDE_MASS,
    PILOT_POWER, RAMP_TIME, ROTOR_MASS, ROTOR_RADIUS, ROTOR_DAMPING, SPIN_FLOOR, guide_radius,
    inverse_guide, preparation, rotor_optical_ports, rotor_rhs, rotor_state, smooth_step,
)
from .shared_rail_reactions import rotor_trace_and_rate, total_trace_bound


def inverse_filter_certificate(taps=64):
    """Exact rational prefix and an outward analytic tail for the impulse l1 norm."""
    if taps < 2:
        raise ValueError("at least two taps required")
    h = [Fraction(1), Fraction(-1, 2)]
    for _ in range(2, taps):
        h.append(-(h[-1]+h[-2])/2)
    prefix = sum(abs(x) for x in h)
    # r=1/sqrt(2), sin(theta)=sqrt(7/8), with outward rational bounds.
    r, sine = Fraction(".707106782"), Fraction(".935414346")
    assert r*r > Fraction(1, 2) and sine*sine < Fraction(7, 8)
    tail = r**taps/(sine*(1-r))
    return dict(taps=taps, exact_prefix=str(prefix), tail_upper=float(tail),
                l1_upper=float(prefix+tail), pole_modulus_upper=float(r))


def septic_primitive(t, duration):
    """Integral from zero of the saturated septic ramp."""
    u = np.asarray(t, float)/duration
    s = np.clip(u, 0., 1.)
    return duration*(s**5*(7+s*(-14+s*(10-2.5*s)))+np.maximum(u-1, 0.))


@dataclass
class TwoDelayLine:
    short_delay: float
    begin: float
    end: float
    peak: float = 1.2
    pilot: float = .001
    ramp: float = CONVERTER_RAMP

    def __post_init__(self):
        if (not np.isfinite([self.short_delay, self.begin, self.end, self.peak, self.pilot, self.ramp]).all()
                or min(self.short_delay, self.pilot, self.ramp) <= 0 or self.peak < self.pilot
                or self.end < self.begin+self.ramp):
            raise ValueError("positive delays/pilot and nonoverlapping ramps required")

    def bias(self, time):
        return self.pilot+(self.peak-self.pilot)*(
            smooth_step(np.asarray(time)-self.begin, self.ramp)[0]
            -smooth_step(np.asarray(time)-self.end, self.ramp)[0])

    def primitive(self, time):
        return self.pilot*np.asarray(time)+(self.peak-self.pilot)*(
            septic_primitive(np.asarray(time)-self.begin, self.ramp)
            -septic_primitive(np.asarray(time)-self.end, self.ramp))

    def state(self, time):
        t, ell = np.asarray(time, float), self.short_delay
        bias = self.bias(t)
        delayed = .5*(self.bias(t-ell)+self.bias(t-2*ell))
        energy = (self.primitive(t)-self.primitive(t-ell)
                  +self.primitive(t)-self.primitive(t-2*ell))
        return dict(bias=bias, half_energy_rate=bias-delayed,
                    energy_rate=2*(bias-delayed), energy=energy)

    @property
    def energy_ceiling(self):
        return 3*self.short_delay*self.peak

    @property
    def pilot_energy(self):
        return 3*self.short_delay*self.pilot


def inverse_commands(forcing, samples_per_delay):
    """Causal inverse on a uniform clock; initial modulation is zero."""
    f = np.asarray(forcing, float)
    lag = int(samples_per_delay)
    if f.ndim != 1 or not np.isfinite(f).all() or lag < 1 or lag != samples_per_delay:
        raise ValueError("one finite time series and a positive integer lag required")
    padded = np.pad(f, (0, (-len(f)) % lag)).reshape((-1, lag)).T
    filtered = lfilter([1.], [1., .5, .5], padded, axis=1)
    return filtered.T.reshape(-1)[:len(f)]


def channel_powers(time, support_power, line, *, samples_per_delay=4):
    """Delayed source/load fluxes, including a nonempty prepared pilot."""
    t, P = np.asarray(time, float), np.asarray(support_power, float)
    step = line.short_delay/samples_per_delay
    if (P.shape != t.shape or t.ndim != 1 or len(t) < 2
            or not np.allclose(np.diff(t), step, rtol=1e-8, atol=1e-12)):
        raise ValueError("uniform clock resolving each delay required")
    s = line.state(t)
    a = inverse_commands(P+s["half_energy_rate"], samples_per_delay)
    def delay(v, lag, initial):
        return np.r_[np.full(lag, initial), v][:-lag]
    outgoing = .5*(s["bias"]+a)
    returning = .5*(s["bias"]-a)
    arriving = sum(delay(outgoing, k*samples_per_delay, .5*line.pilot) for k in (1, 2))
    received = sum(delay(returning, k*samples_per_delay, .5*line.pilot) for k in (1, 2))
    return dict(modulation=a, minimum_emitted_power=np.minimum(outgoing, returning),
        source_outgoing=2*outgoing, source_returning=received,
        support_incoming=arriving, support_outgoing=2*returning,
        support_power_error=arriving-2*returning-P,
        source_power_error=2*outgoing-received-P-s["energy_rate"], **s)


@dataclass
class SupportWithPhotons:
    tension: np.ndarray
    core_inventory: np.ndarray
    joint_inventory: np.ndarray
    line_energy_ceiling: float
    dynamic_trace_bound: float = total_trace_bound()

    def __post_init__(self):
        self.tension, self.core_inventory, self.joint_inventory = (
            np.asarray(a, float) for a in (self.tension, self.core_inventory, self.joint_inventory))
        if any(a.shape != (2,) for a in (self.tension, self.core_inventory, self.joint_inventory)):
            raise ValueError("two original support populations required")
        self.base = [scalar_sheet_state(*x) for x in zip(self.tension, self.core_inventory, self.joint_inventory)]

    def state(self, total_trace):
        trace = np.asarray(total_trace, float)
        if (np.any(trace < -self.dynamic_trace_bound-1e-10)
                or np.any(trace > self.dynamic_trace_bound+self.line_energy_ceiling+1e-10)):
            raise ValueError("combined reaction leaves its charged envelope")
        amplitude = np.maximum((self.dynamic_trace_bound+trace)/3, 0.)
        if trace.ndim == 0:
            after = [scalar_sheet_state(T+w*amplitude, M, m) for w, T, M, m in
                     zip((1., .5), self.tension, self.core_inventory, self.joint_inventory)]
            energy = sum(a["energy"]-b["energy"] for a, b in zip(after, self.base))+self.dynamic_trace_bound
            gain = (after[0]["derivative"]+.5*after[1]["derivative"])/3
        else:
            shape = (2,)+(1,)*trace.ndim
            loads = self.tension.reshape(shape)+np.array([1., .5]).reshape(shape)*amplitude
            after = series_state(loads, self.core_inventory.reshape(shape),
                                 self.joint_inventory.reshape(shape), dimension=2)
            base = np.array([v["energy"] for v in self.base]).reshape(shape)
            energy = (after["total_energy"]-base).sum(axis=0)+self.dynamic_trace_bound
            derivative = after["core_energy_derivative"]+after["joint_energy_derivative"]
            gain = (derivative[0]+.5*derivative[1])/3
        return dict(energy=energy, derivative=gain)


def finite_branch_power(state, network_power, support, photon_energy, photon_rate,
                        guide_trace=0., guide_rate=0., *, inventory=ROTOR_MASS):
    if np.asarray(state).ndim == 1:
        rotor = rotor_trace_and_rate(state, 0., inventory=inventory)
    else:
        x, p, j, b = np.asarray(state)
        s = rotor_state(state)
        h, v, gamma = s["energy"], s["radial_speed"], s["gamma"]
        xd = v/ROTOR_RADIUS
        pd = (1+j*j+2*b-x*x)/(2*gamma*x*x*ROTOR_RADIUS)-ROTOR_DAMPING*p/ROTOR_RADIUS
        rotor = dict(trace=inventory*(h-x/gamma-ROTOR_DAMPING*x*p),
            trace_rate=inventory*(-xd/gamma+x*v*pd/h*gamma-ROTOR_DAMPING*(xd*p+x*pd)),
            input_rate_coefficient=1-ROTOR_DAMPING*x*v)
    trace = rotor["trace"]+guide_trace+photon_energy
    r = support.state(trace)
    c, a = r["derivative"], rotor["input_rate_coefficient"]
    free_rate = rotor["trace_rate"]+guide_rate+photon_rate
    q = (network_power-photon_rate-c*free_rate)/(1+c*a)
    return dict(rotor_power=q, support_power=c*(free_rate+a*q),
        support_energy=r["energy"], energy_trace_derivative=c,
        total_trace=trace, dynamic_trace=rotor["trace"]+guide_trace,
        denominator=1+c*a)


def simulate_finite_branch(left, right, context, *, short_delay=1/64,
                           peak_bias=1.2, samples_per_delay=4,
                           pilot_bias=.001, inventory=ROTOR_MASS,
                           maximum_step=.12, rtol=2e-9, atol=2e-11):
    """Lossless local evolution plus its actual delayed optical endpoint fluxes."""
    onset = -RAMP_TIME-.5 if right >= left else -.5
    begin = min(onset-.5, 0.)-CONVERTER_RAMP-CONVERTER_DELAY-1
    end_ramp = max(onset+RAMP_TIME+.5, 1.)+1
    line = TwoDelayLine(short_delay, begin, end_ramp, peak=peak_bias, pilot=pilot_bias)
    support = SupportWithPhotons(context["tension"], context["core_inventory"],
                                context["joint_inventory"], line.energy_ceiling)
    prep = preparation(inventory=inventory)
    def guide(t):
        return inverse_guide(np.asarray(t)-onset, left+PILOT_POWER, right+PILOT_POWER)
    def loop(t):
        return CONVERTER_NET_POWER/SPIN_FLOOR*(smooth_step(np.asarray(t)-begin, CONVERTER_RAMP)[0]
            -smooth_step(np.asarray(t)-end_ramp, CONVERTER_RAMP)[0])
    def network(t, difference=None):
        difference = (np.where(np.asarray(t) < 1, left, right)-np.where(np.asarray(t) < 0, left, right)
                      if difference is None else difference)
        return difference+guide(t-.5)["output_power"]-guide(t+.5)["input_power"]+loop(t-CONVERTER_DELAY)-loop(t)
    initial_h = (prep["initial_dynamic_energy"]-GUIDE_MASS*guide_radius(left+PILOT_POWER)
                 -(left+PILOT_POWER)-left)/inventory
    initial = np.array([initial_h, 0., sqrt(initial_h**2-1-2e-8), 1e-8])
    initial_support = float(support.state(line.pilot_energy)["energy"])
    start, end = min(-RAMP_TIME-2, begin-1), max(RAMP_TIME+8, end_ramp+CONVERTER_RAMP+8)
    cuts = [s+d for s in (begin, begin+CONVERTER_RAMP, end_ramp, end_ramp+CONVERTER_RAMP)
            for d in (0., CONVERTER_DELAY, short_delay, 2*short_delay)]
    cuts = sorted(set([start, end, 0., 1., onset, onset-.5, onset+.5,
        onset+RAMP_TIME, onset+RAMP_TIME-.5, onset+RAMP_TIME+.5, *cuts]))
    cuts = [t for t in cuts if start <= t <= end]
    y0, segments = np.r_[initial, 0., 0., 0.], []
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        mid = (lo+hi)/2
        difference = (left if mid < 1 else right)-(left if mid < 0 else right)
        def rhs(t, y):
            g, p = guide(t), line.state(t)
            r = finite_branch_power(y[:4], network(t, difference), support, p["energy"], p["energy_rate"],
                                    g["pressure_trace"], guide_trace_rate(g), inventory=inventory)
            return np.r_[rotor_rhs(y[:4], r["rotor_power"], inventory=inventory), network(t, difference),
                         r["rotor_power"]**2, abs(r["support_power"])]
        solution = solve_ivp(rhs, (lo, hi), y0, method="DOP853", dense_output=True,
            max_step=maximum_step, rtol=rtol, atol=atol)
        if not solution.success or np.min(solution.y[2]) <= SPIN_FLOOR:
            raise ValueError("finite branch leaves the rotor operating domain")
        segments.append(solution.sol)
        y0 = solution.y[:, -1]
    step = short_delay/samples_per_delay
    time = start+np.arange(int(round((end-start)/step))+1)*step
    values = np.empty((7, len(time)))
    for index, dense in enumerate(segments):
        mask = (time >= cuts[index]) & ((time < cuts[index+1]) if index < len(segments)-1 else (time <= cuts[index+1]))
        values[:, mask] = dense(time[mask])
    g, p = guide(time), line.state(time)
    r = finite_branch_power(values[:4], network(time), support, p["energy"], p["energy_rate"],
                            g["pressure_trace"], guide_trace_rate(g), inventory=inventory)
    waves = channel_powers(time, r["support_power"], line, samples_per_delay=samples_per_delay)
    s = rotor_state(values[:4])
    nodes, weights = np.polynomial.legendre.leggauss(20)
    feed, returned, converter = (np.zeros_like(time) for _ in range(3))
    for node, weight in zip(nodes, weights):
        feed += .25*weight*guide(time+.25*(node+1))["input_power"]
        returned += .25*weight*guide(time-.25*(node+1))["output_power"]
        converter += CONVERTER_DELAY/2*weight*loop(time-CONVERTER_DELAY/2*(node+1))
    useful = left+(right-left)*np.clip(time, 0, 1)
    energy = inventory*s["energy"]+r["support_energy"]+p["energy"]
    ledger = energy+g["energy"]+feed+returned+useful+converter
    available = (np.where(time < 1, left, right)-np.where(time < 0, left, right)
        +guide(time-.5)["output_power"]+loop(time-CONVERTER_DELAY)+waves["source_returning"])
    ports = rotor_optical_ports(r["rotor_power"], values[2])
    bypass = available-ports["incoming"]
    demanded = guide(time+.5)["input_power"]+loop(time)+waves["source_outgoing"]
    return dict(time=time, state=values[:4], **r, **{k: v for k, v in waves.items() if k != "energy_rate"},
        photon_energy=p["energy"], photon_energy_rate=p["energy_rate"],
        thermal_energy=inventory*s["thermal_energy"], rotor_input_l2=values[5],
        support_work_throughput=values[6], guide_energy=g["energy"],
        complete_ledger_error=ledger-prep["initial_dynamic_energy"]-initial_support-line.pilot_energy,
        coupled_ledger_error=energy-inventory*initial_h-initial_support-line.pilot_energy-values[4],
        incident_margin=bypass, output_balance_error=bypass+ports["outgoing"]-demanded,
        initial_photon_energy=line.pilot_energy, initial_support_energy=initial_support,
        additional_continuous_energy_ceiling=3*total_trace_bound()+2*line.energy_ceiling,
        photon_energy_ceiling=line.energy_ceiling,
        emitted_energy=2*(line.primitive(time)-line.primitive(start)))
