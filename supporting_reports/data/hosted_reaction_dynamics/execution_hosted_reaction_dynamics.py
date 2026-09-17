"""Coupled finite reaction paths with explicit periodic capacitor work ports."""
from dataclasses import dataclass
from math import sqrt

import numpy as np
from scipy.integrate import solve_ivp

from .constitutive_joints_and_optics import series_state
from .coupled_rail_reactions import scalar_sheet_state, guide_trace_rate
from .finite_reaction_transport import SupportWithPhotons, TwoDelayLine, channel_powers
from .reaction_work_interfaces import sheet_boundary_state, periodic_capacitor_cell, capacitor_field_split
from .scheduled_optical_transfer import (
    CONVERTER_DELAY, CONVERTER_NET_POWER, CONVERTER_RAMP, GUIDE_MASS,
    PILOT_POWER, RAMP_TIME, ROTOR_RADIUS, SPIN_FLOOR, inverse_guide,
    preparation, rotor_optical_ports, rotor_rhs, rotor_state, smooth_step,
)
from .shared_rail_reactions import total_trace_bound


@dataclass
class HostedSupport:
    tension: np.ndarray
    core_inventory: np.ndarray
    joint_inventory: np.ndarray
    line_ceiling: float
    bias: float = .62
    trace_bound: float = total_trace_bound()

    def __post_init__(self):
        self.tension, self.core_inventory, self.joint_inventory = (
            np.asarray(x, float) for x in (self.tension, self.core_inventory, self.joint_inventory))
        if self.bias < self.trace_bound:
            raise ValueError("field bias must cover the allowed negative trace")
        self.weight = np.array([1., .5])
        shifted = self.tension+self.weight*(self.bias-self.trace_bound)/3
        self.shifted = SupportWithPhotons(shifted, self.core_inventory, self.joint_inventory,
                                         self.line_ceiling, self.trace_bound)
        base = sum(scalar_sheet_state(*v)["energy"] for v in
                   zip(self.tension, self.core_inventory, self.joint_inventory))
        self.offset = sum(v["energy"] for v in self.shifted.base)-base+self.bias-self.trace_bound
        low = series_state(shifted, self.core_inventory, self.joint_inventory, dimension=2)
        high = series_state(self.tension+self.weight*(self.bias+self.trace_bound+self.line_ceiling)/3,
                            self.core_inventory, self.joint_inventory, dimension=2)
        span0 = low["core_linear_stretch"]+1e-4*low["joint_stretch"]
        span1 = high["core_linear_stretch"]+1e-4*high["joint_stretch"]
        self.reference = .1*ROTOR_RADIUS/span1
        self.pitch = self.reference*(span0+1.1*(span1-span0))

    def state(self, trace):
        r = self.shifted.state(trace)
        return dict(energy=r["energy"]+self.offset, derivative=r["derivative"])

    def endpoints(self, trace, trace_rate):
        trace, rate = np.broadcast_arrays(trace, trace_rate)
        if trace.ndim != 1:
            raise ValueError("one local time series required")
        T = self.tension[:, None]+self.weight[:, None]*(self.bias+trace)/3
        boundary = sheet_boundary_state(T, self.core_inventory[:, None], self.joint_inventory[:, None],
                    self.weight[:, None]*rate/3, self.reference[:, None])
        gap = periodic_capacitor_cell(boundary, self.pitch[:, None])
        fields = capacitor_field_split(*gap["field_energy"])
        complementary = self.bias*np.array([2/3, 1/3])[:, None]-fields
        if np.any(complementary < 0):
            raise ValueError("capacitor fields exceed a complementary Maxwell channel")
        electric = gap["electrical_power"].sum(axis=0)
        replacement = -gap["field_energy_rate"].sum(axis=0)
        return dict(capacitor_energy=gap["field_energy"].sum(axis=0),
            capacitor_gap=gap["full_gap"], capacitor_charge=gap["charge_per_facet"],
            facet_velocity=boundary["facet_velocity"], complementary_field_energy=complementary,
            capacitor_electrical_power=electric, complementary_field_power=replacement,
            mechanical_power=gap["mechanical_power"].sum(axis=0),
            terminal_work_error=electric+replacement-gap["mechanical_power"].sum(axis=0))


def hosted_branch_power(state, network_power, support, photon_energy, photon_rate,
                        guide_trace=0., guide_rate=0., *, inventory=18., damping=.8):
    """Exact coupled input for arbitrary selected radial damping and field bias."""
    x, p, j, b = np.asarray(state)
    s = rotor_state(state)
    h, v, gamma = s["energy"], s["radial_speed"], s["gamma"]
    xd = v/ROTOR_RADIUS
    pd = (1+j*j+2*b-x*x)/(2*gamma*x*x*ROTOR_RADIUS)-damping*p/ROTOR_RADIUS
    rotor_trace = inventory*(h-x/gamma-damping*x*p)
    free_rotor_rate = inventory*(-xd/gamma+x*v*pd/h*gamma-damping*(xd*p+x*pd))
    trace = rotor_trace+guide_trace+photon_energy
    r = support.state(trace)
    c, a = r["derivative"], 1-damping*x*v
    free_rate = free_rotor_rate+guide_rate+photon_rate
    q = (network_power-photon_rate-c*free_rate)/(1+c*a)
    trace_rate = free_rate+a*q
    return dict(rotor_power=q, support_power=c*trace_rate, total_trace_rate=trace_rate,
        support_energy=r["energy"], total_trace=trace,
        dynamic_trace=rotor_trace+guide_trace, denominator=1+c*a)


def simulate_hosted_transition(left, right, context, *, inventory=19., damping=.8,
        bias=.62, short_delay=1/64, peak_bias=1.2, samples_per_delay=4,
        maximum_step=.12, rtol=2e-9, atol=2e-11):
    """Finite paths and nonlinear storage, with the two electric terminal duties."""
    onset = -RAMP_TIME-.5 if right >= left else -.5
    begin = min(onset-.5, 0.)-CONVERTER_RAMP-CONVERTER_DELAY-1
    end_ramp = max(onset+RAMP_TIME+.5, 1.)+1
    line = TwoDelayLine(short_delay, begin, end_ramp, peak=peak_bias)
    support = HostedSupport(context["tension"], context["core_inventory"],
                            context["joint_inventory"], line.energy_ceiling, bias)
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
    initial_h = (prep["initial_dynamic_energy"]-guide(onset)["energy"]-(left+PILOT_POWER)-left)/inventory
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
        middle = (lo+hi)/2
        difference = (left if middle < 1 else right)-(left if middle < 0 else right)
        def rhs(t, y):
            g, photons = guide(t), line.state(t)
            r = hosted_branch_power(y[:4], network(t, difference), support, photons["energy"], photons["energy_rate"],
                g["pressure_trace"], guide_trace_rate(g), inventory=inventory, damping=damping)
            return np.r_[rotor_rhs(y[:4], r["rotor_power"], inventory=inventory, damping=damping),
                         network(t, difference), r["rotor_power"]**2, abs(r["support_power"])]
        solution = solve_ivp(rhs, (lo, hi), y0, method="DOP853", dense_output=True,
                             max_step=maximum_step, rtol=rtol, atol=atol)
        if not solution.success or solution.y[2].min() <= SPIN_FLOOR:
            raise ValueError("hosted local trajectory leaves the rotor operating domain")
        segments.append(solution.sol)
        y0 = solution.y[:, -1]
    step = short_delay/samples_per_delay
    time = start+np.arange(int(round((end-start)/step))+1)*step
    values = np.empty((7, len(time)))
    for i, dense in enumerate(segments):
        mask = (time >= cuts[i]) & ((time < cuts[i+1]) if i < len(segments)-1 else (time <= cuts[i+1]))
        values[:, mask] = dense(time[mask])
    g, photons = guide(time), line.state(time)
    r = hosted_branch_power(values[:4], network(time), support, photons["energy"], photons["energy_rate"],
        g["pressure_trace"], guide_trace_rate(g), inventory=inventory, damping=damping)
    waves = channel_powers(time, r["support_power"], line, samples_per_delay=samples_per_delay)
    endpoints = support.endpoints(r["total_trace"], r["total_trace_rate"])
    s = rotor_state(values[:4])
    feed, returned, converter = (np.zeros_like(time) for _ in range(3))
    nodes, weights = np.polynomial.legendre.leggauss(20)
    for node, weight in zip(nodes, weights):
        feed += .25*weight*guide(time+.25*(node+1))["input_power"]
        returned += .25*weight*guide(time-.25*(node+1))["output_power"]
        converter += CONVERTER_DELAY/2*weight*loop(time-CONVERTER_DELAY/2*(node+1))
    useful = left+(right-left)*np.clip(time, 0, 1)
    ledger = inventory*s["energy"]+r["support_energy"]+photons["energy"]+g["energy"]+feed+returned+useful+converter
    available = (np.where(time < 1, left, right)-np.where(time < 0, left, right)
        +guide(time-.5)["output_power"]+loop(time-CONVERTER_DELAY)+waves["source_returning"])
    ports = rotor_optical_ports(r["rotor_power"], values[2])
    bypass = available-ports["incoming"]
    demanded = guide(time+.5)["input_power"]+loop(time)+waves["source_outgoing"]
    return dict(time=time, state=values[:4], **r, **endpoints,
        photon_energy=photons["energy"], minimum_emitted_power=waves["minimum_emitted_power"],
        modulation=waves["modulation"], modulation_ratio=abs(waves["modulation"])/waves["bias"],
        thermal_energy=inventory*s["thermal_energy"], rotor_input_l2=values[5],
        support_work_throughput=values[6],
        complete_ledger_error=ledger-prep["initial_dynamic_energy"]-initial_support-line.pilot_energy,
        incident_margin=bypass, output_balance_error=bypass+ports["outgoing"]-demanded,
        endpoint_mechanical_error=endpoints["mechanical_power"]-r["support_power"],
        initial_support_energy=initial_support)
