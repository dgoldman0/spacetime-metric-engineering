"""Finite electrical leads, charged states, and explicit host requirements.

Energy is measured in one physical cell capacity C, length in c*delta,
and time in delta. Charge and voltage units are sqrt(epsilon0*C*c*delta)
and sqrt(C/(epsilon0*c*delta)). The inherited capacity is already D-weighted
per radial label and solid angle. Its physical cell conversion requires the
label/solid-angle measure and the metric scale; another D would double-count
proper volume. Global metric scaling leaves physical C/delta unchanged.

The distributed circuit is a low-drift, long-wavelength material model.
Positive carrier kinetic inductance makes its characteristic speed less
than c. It has an exact effective energy theorem. Vacuum coax field
reconstruction supplies the leading Maxwell stress and surface loads;
finite penetration, material dispersion and termination geometry remain
requirements of a full Maxwell/matter construction.
"""
from dataclasses import dataclass

import numpy as np
from scipy.constants import c as C_LIGHT, G as NEWTON_G, epsilon_0, elementary_charge, electron_mass, proton_mass
from scipy.interpolate import PchipInterpolator

from .constitutive_joints_and_optics import series_state
from .hosted_reaction_dynamics import HostedSupport
from .reaction_work_interfaces import sheet_boundary_state, periodic_capacitor_cell, capacitor_field_split


PORT_NAMES = ("outer_gap", "angular_gap", "complementary_hoop", "complementary_radial")
PORT_COPIES = np.array([2., 2., 2., 1.])


@dataclass(frozen=True)
class ElectricalScale:
    cell_energy_joule: float
    flight_time_second: float

    def __post_init__(self):
        if not np.isfinite([self.cell_energy_joule, self.flight_time_second]).all() or min(self.cell_energy_joule, self.flight_time_second) <= 0:
            raise ValueError("Positive physical cell energy and flight time required")

    @property
    def length(self):
        return C_LIGHT*self.flight_time_second

    @property
    def charge(self):
        return np.sqrt(epsilon_0*self.cell_energy_joule*self.length)

    @property
    def voltage(self):
        return self.cell_energy_joule/self.charge

    def carrier_coefficient(self, mass_per_charge):
        return mass_per_charge*C_LIGHT**2*self.charge/self.cell_energy_joule

    def fields(self, electric, magnetic):
        return (np.asarray(electric)*self.voltage/self.length,
                np.asarray(magnetic)*self.voltage/(C_LIGHT*self.length))


def required_power_scale(host_coefficient, *, mass_per_charge=proton_mass/elementary_charge):
    """C/delta fixing chi=(m/q)c^2*sqrt(epsilon0*c*delta/C)."""
    if host_coefficient <= 0 or mass_per_charge <= 0:
        raise ValueError("Positive host coefficient and mass/charge required")
    return (mass_per_charge*C_LIGHT**2)**2*epsilon_0*C_LIGHT/host_coefficient**2


def geometrized_cell_scale(capacity_per_label, proper_delay, metric_length_metre, label_solid_angle_measure):
    """Convert the existing D-weighted ledger under a metric homothety.

    The source chain forms D*T with D=ell*R^2, ell=gamma*b. Capacity
    already carries this proper-volume density per radial label and solid
    angle. Its physical cell measure is Delta x_hat*Delta Omega; another D
    would count volume twice. For an already integrated geometric energy,
    use measure=1. Under length scale Lg, E=(c^4/G)*Lg*C_hat*measure and
    delta=(Lg/c)*delta_hat. E/delta is therefore independent of Lg.
    The cell measure, spatial packing and material state remain to be chosen.
    """
    if (not np.isfinite([capacity_per_label, proper_delay, metric_length_metre,
                        label_solid_angle_measure]).all()
            or min(capacity_per_label, proper_delay, metric_length_metre, label_solid_angle_measure) <= 0):
        raise ValueError("Positive geometric capacity, delay, length scale and label measure required")
    return ElectricalScale(C_LIGHT**4/NEWTON_G*metric_length_metre*capacity_per_label*label_solid_angle_measure,
        metric_length_metre/C_LIGHT*proper_delay)


class ReconstructedWorkPorts:
    """Four charged terminal states on a finite-rise-time local reconstruction.

    A shape-preserving C1 reconstruction of the archived total trace makes
    terminal currents continuous with bounded piecewise acceleration. It
    changes the ideal derivative jumps and retains high-frequency tails;
    that reconstruction is distinct from a full coupled rotor replay or
    a material bandwidth certificate.
    Each gap bank contains two complete fixed-area gaps. Complementary
    hoop/radial fields use respectively two/one fixed-geometry capacitors.
    """
    def __init__(self, time, trace, context, *, area_fraction=.25,
                 complementary_gap_fraction=.01, bias=.62, reconstruction_step=1/16):
        self.time = np.asarray(time, float)
        if (self.time.ndim != 1 or len(self.time) < 4 or np.any(np.diff(self.time) <= 0)
                or not 0 < area_fraction <= 1 or not 0 < complementary_gap_fraction <= 1):
            raise ValueError("Ordered local history and positive fitting geometry required")
        trace = np.asarray(trace, float)
        if trace.shape != self.time.shape or not np.isfinite(trace).all():
            raise ValueError("One finite trace value per time required")
        self.archived_trace = PchipInterpolator(self.time, trace, extrapolate=False)
        self.reconstruction_step = reconstruction_step
        if reconstruction_step is not None:
            if not np.isfinite(reconstruction_step) or reconstruction_step <= 0:
                raise ValueError("Positive fixed reconstruction step required")
            knots = np.unique(np.r_[self.time[0],
                np.arange(np.ceil(self.time[0]/reconstruction_step),
                    np.floor(self.time[-1]/reconstruction_step)+1)*reconstruction_step,
                self.time[-1]])
            trace = self.archived_trace(knots)
        else:
            knots = self.time
        # Constant outer panels give exactly zero endpoint current and a
        # C1 extension, including at the finite history boundaries.
        padding = max(1., np.max(np.diff(knots)))
        self.trace = PchipInterpolator(np.r_[self.time[0]-padding, knots, self.time[-1]+padding],
            np.r_[trace[0], trace, trace[-1]], extrapolate=False)
        self.support = HostedSupport(*(np.asarray(context[k]) for k in ("tension", "core_inventory", "joint_inventory")),
                                     .05625, bias=bias)
        self.span = .1/(12*np.pi)
        self.area = np.full(4, area_fraction*self.span**2)
        self.complementary_gap = complementary_gap_fraction*self.span
        self.bias = bias

    def __call__(self, time):
        t = np.asarray(time, float)
        clipped = np.clip(t, self.time[0], self.time[-1])
        pi = self.trace(clipped)
        pid = np.where((t >= self.time[0]) & (t <= self.time[-1]), self.trace.derivative()(clipped), 0.)
        pidd = np.where((t >= self.time[0]) & (t <= self.time[-1]), self.trace.derivative(2)(clipped), 0.)
        return self.from_trace(pi, pid, pidd)

    def from_trace(self, trace, trace_rate, trace_acceleration):
        """Terminal states for specified local support trace and its rates."""
        pi, pid, pidd = np.broadcast_arrays(trace, trace_rate, trace_acceleration)
        shape = (2,)+(1,)*pi.ndim
        support = self.support
        weight = support.weight.reshape(shape)
        tension = support.tension.reshape(shape)+weight*(self.bias+pi)/3
        boundary = sheet_boundary_state(tension, support.core_inventory.reshape(shape),
            support.joint_inventory.reshape(shape), weight*pid/3, support.reference.reshape(shape))
        acceleration = sheet_acceleration(tension, support.core_inventory.reshape(shape),
            support.joint_inventory.reshape(shape), weight*pid/3, weight*pidd/3,
            support.reference.reshape(shape))
        gaps = periodic_capacitor_cell(boundary, support.pitch.reshape(shape))
        gap_energy = gaps["field_energy"]
        gap_rate = gaps["field_energy_rate"]
        comp = self.bias*np.array([2/3, 1/3]).reshape(shape)-capacitor_field_split(*gap_energy)
        comp_rate = -capacitor_field_split(*gap_rate)
        gap_acceleration = 2*(acceleration["force_acceleration"]*gaps["full_gap"]
            -2*boundary["force_rate_per_facet"]*boundary["length_rate"]
            -boundary["force_per_facet"]*acceleration["length_acceleration"])
        comp_acceleration = -capacitor_field_split(*gap_acceleration)
        if np.min(comp) <= 0:
            raise ValueError("Complementary field channel is exhausted")
        energy = np.concatenate((gap_energy, comp))
        full_gap = np.concatenate((gaps["full_gap"], np.full_like(comp, self.complementary_gap)))
        area = self.area.reshape((4,)+(1,)*pi.ndim)
        copies = PORT_COPIES.reshape((4,)+(1,)*pi.ndim)
        capacitance = copies*area/full_gap
        charge = np.sqrt(2*capacitance*energy)
        voltage = charge/capacitance
        force, force_rate = boundary["force_per_facet"], boundary["force_rate_per_facet"]
        gap_current = 2*np.sqrt(self.area[:2].reshape(shape)/(2*force))*force_rate
        comp_current = capacitance[2:]*comp_rate/charge[2:]
        current = np.concatenate((gap_current, comp_current))
        gap_current_rate = charge[:2]*(acceleration["force_acceleration"]/(2*force)
            -force_rate**2/(4*force**2))
        comp_current_rate = charge[2:]*(comp_acceleration/(2*comp)-comp_rate**2/(4*comp**2))
        current_rate = np.concatenate((gap_current_rate, comp_current_rate))
        voltage_rate = np.concatenate(((gap_current*full_gap[:2]-charge[:2]*boundary["length_rate"])
            /(2*area[:2]), comp_current/capacitance[2:]))
        mechanical = gaps["mechanical_power"].sum(axis=0)
        power = voltage*current
        return dict(voltage=voltage, current=current, voltage_rate=voltage_rate,
            current_rate=current_rate, charge=charge, energy=energy,
            capacitance=capacitance, full_gap=full_gap, field=voltage/full_gap,
            mechanical_power=mechanical, electrical_power=power,
            port_work_error=power.sum(axis=0)-mechanical,
            gap_facet_force=force, complementary_plate_force=comp/(copies[2:]*full_gap[2:]),
            total_trace=pi, total_trace_rate=pid, total_trace_acceleration=pidd)


def sheet_acceleration(tension, inventory, joints, tension_rate, tension_acceleration, reference_span):
    """Differentiate the exact dimension-two force-matched sheet inverse.

    Derivatives are first formed with respect to the core duty, then
    transformed through T=t+alpha*f*j. No finite time difference enters.
    """
    s = series_state(tension, inventory, joints, dimension=2)
    core, S, f, j = (s[k] for k in
        ("core_tension", "core_linear_stretch", "force_times_core_reference_span", "joint_stretch"))
    alpha, scale = 1e-4, .9*np.asarray(inventory)
    root = np.hypot(core, scale)
    fp = s["force_derivative"]
    fpp = (-scale**2/(2*root**3)-(1-core/(2*root))/(2*root))/S
    jp = alpha*fp*j**3/joints
    jpp = alpha*(fpp*j**3+3*fp*j*j*jp)/joints
    D = s["effective_load_derivative"]
    Dp = alpha*(fpp*j+2*fp*jp+f*jpp)
    td = np.asarray(tension_rate)/D
    tdd = (np.asarray(tension_acceleration)-Dp*td*td)/D
    Sp = S/(2*root)
    Spp = S/(4*root**2)-S*core/(2*root**3)
    return dict(force_acceleration=(fpp*td*td+fp*tdd)/reference_span,
        length_acceleration=reference_span*((Spp+alpha*jpp)*td*td+(Sp+alpha*jp)*tdd))


@dataclass(frozen=True)
class FiniteCoax:
    length: float
    inner_radius: float
    radius_ratio: float
    kinetic_inductance: np.ndarray
    absolute_charge_per_length: np.ndarray
    mobile_coefficient: float
    host_coefficient: float

    def __post_init__(self):
        lk, charge = map(lambda v: np.asarray(v, float), (self.kinetic_inductance, self.absolute_charge_per_length))
        if (min(self.length, self.inner_radius, self.mobile_coefficient) <= 0 or self.radius_ratio <= 1
                or self.host_coefficient < self.mobile_coefficient
                or lk.ndim != 1 or charge.shape != lk.shape
                or not np.isfinite(lk).all() or not np.isfinite(charge).all()
                or np.any(lk <= 0) or np.any(charge <= 0)):
            raise ValueError("Finite geometry and positive kinetic/host inventories required")
        if not np.allclose(lk, 2*self.mobile_coefficient/charge, rtol=1e-12, atol=0):
            raise ValueError("Kinetic inductance must use both counted carrier populations")

    @property
    def capacitance_per_length(self):
        return 2*np.pi/np.log(self.radius_ratio)

    @property
    def magnetic_inductance(self):
        return np.log(self.radius_ratio)/(2*np.pi)

    @property
    def total_inductance(self):
        return self.magnetic_inductance+np.asarray(self.kinetic_inductance)

    @property
    def impedance(self):
        return np.sqrt(self.total_inductance/self.capacitance_per_length)

    @property
    def delay(self):
        return self.length*np.sqrt(self.total_inductance*self.capacitance_per_length)

    def evaluate(self, terminals, time, *, quadrature=12, source_capacitance=None):
        """Inverse finite-line waves and counted reactive source states.

        Source waves preview the prescribed load by one finite flight. No
        matched resistor or energy sink is introduced. Each optional source
        capacitor has energy Cs*Vs^2/2; its pump must supply line power plus
        the derivative of that energy. Pump conversion is an exposed port.
        """
        t = np.asarray(time, float)
        if t.ndim != 1 or len(t) < 3 or np.any(np.diff(t) <= 0):
            raise ValueError("One ordered time series required")
        ports = len(self.impedance)
        Z, tau = self.impedance[:, None], self.delay[:, None]
        def aligned(clock):
            # Select the matching bank after evaluating the common clock array.
            state = terminals(clock)
            return tuple(state[k][np.arange(ports), np.arange(ports)] for k in
                ("voltage", "current", "voltage_rate", "current_rate"))
        def waves(offset):
            vp, ip, vpd, ipd = aligned(t[None]+offset)
            vm, im, vmd, imd = aligned(t[None]-offset)
            return (vp+Z*ip)/2, (vm-Z*im)/2, (vpd+Z*ipd)/2, (vmd-Z*imd)/2
        plus, minus, plus_rate, minus_rate = waves(tau)
        source_voltage, source_current = plus+minus, (plus-minus)/Z
        source_voltage_rate = plus_rate+minus_rate
        source_power = source_voltage*source_current
        load = terminals(t)
        electric, magnetic, kinetic, momentum, hoop, kinetic_rate, field_rate, momentum_rate = (
            np.zeros((ports, len(t))) for _ in range(8))
        peak_E = np.maximum(abs(source_voltage).max(axis=1), abs(load["voltage"]).max(axis=1))/(self.inner_radius*np.log(self.radius_ratio))
        peak_B = np.maximum(abs(source_current).max(axis=1), abs(load["current"]).max(axis=1))/(2*np.pi*self.inner_radius)
        peak_current = np.maximum(abs(source_current).max(axis=1), abs(load["current"]).max(axis=1))
        peak_line_charge = np.maximum(abs(source_voltage).max(axis=1), abs(load["voltage"]).max(axis=1))*self.capacitance_per_length
        peak_radial_pressure = np.maximum(
            abs((source_voltage/(self.inner_radius*np.log(self.radius_ratio)))**2
                -(source_current/(2*np.pi*self.inner_radius))**2).max(axis=1),
            abs((load["voltage"]/(self.inner_radius*np.log(self.radius_ratio)))**2
                -(load["current"]/(2*np.pi*self.inner_radius))**2).max(axis=1))/2
        nodes, weights = np.polynomial.legendre.leggauss(quadrature)
        # A current acceleration may change at a C1 reconstruction knot.
        # Partition each spatial integral at both retarded/advanced knot
        # images, avoiding a quadrature rule across that discontinuity.
        cuts = [np.zeros((ports, len(t))), np.broadcast_to(tau, (ports, len(t)))]
        if hasattr(terminals, "trace"):
            knots = terminals.trace.x
            index = np.searchsorted(knots, t, side="right")
            for shift in range(int(np.max(tau)/np.min(np.diff(knots)))+1):
                forward = knots[np.minimum(index+shift, len(knots)-1)]-t
                backward = t-knots[np.maximum(index-1-shift, 0)]
                cuts.extend([np.clip(forward[None], 0, tau), np.clip(backward[None], 0, tau)])
        cuts = np.sort(np.stack(cuts), axis=0)
        cells = [(left, right) for left, right in zip(cuts[:-1], cuts[1:]) if np.any(right > left)]
        for left, right in cells:
          for node, weight in zip(nodes, weights):
            offset = left+(right-left)*(node+1)/2
            a, b, ad, bd = waves(offset)
            V, I = a+b, (a-b)/Z
            Vd, Id = ad+bd, (ad-bd)/Z
            ue, ub = .5*self.capacitance_per_length*V*V, .5*self.magnetic_inductance*I*I
            uk = .5*np.asarray(self.kinetic_inductance)[:, None]*I*I
            factor = self.length/tau*(right-left)*weight/2
            electric += factor*ue
            magnetic += factor*ub
            kinetic += factor*uk
            kinetic_rate += factor*np.asarray(self.kinetic_inductance)[:, None]*I*Id
            field_rate += factor*(self.capacitance_per_length*V*Vd+self.magnetic_inductance*I*Id)
            momentum += factor*V*I
            momentum_rate += factor*(Vd*I+V*Id)
            hoop += factor*2*abs(ue-ub)/np.log(self.radius_ratio)
            Er = V/(self.inner_radius*np.log(self.radius_ratio))
            Bphi = I/(2*np.pi*self.inner_radius)
            peak_E = np.maximum(peak_E, np.max(abs(Er), axis=1))
            peak_B = np.maximum(peak_B, np.max(abs(Bphi), axis=1))
            peak_current = np.maximum(peak_current, np.max(abs(I), axis=1))
            peak_line_charge = np.maximum(peak_line_charge, np.max(abs(self.capacitance_per_length*V), axis=1))
            peak_radial_pressure = np.maximum(peak_radial_pressure, np.max(abs(Er*Er-Bphi*Bphi)/2, axis=1))
        line_energy = electric+magnetic+kinetic
        source_capacitance = (np.zeros(ports) if source_capacitance is None else np.asarray(source_capacitance))
        if source_capacitance.shape != (ports,) or not np.isfinite(source_capacitance).all() or np.any(source_capacitance < 0):
            raise ValueError("One finite nonnegative source capacitance per port required")
        source_energy = .5*source_capacitance[:, None]*source_voltage**2
        source_charge = source_capacitance[:, None]*source_voltage
        source_energy_rate = source_capacitance[:, None]*source_voltage*source_voltage_rate
        source_pump_current = source_current+source_capacitance[:, None]*source_voltage_rate
        source_pump_power = source_voltage*source_pump_current
        # This port ledger is exact within the effective line model. The
        # numerical derivative below is a diagnostic, not a prescribed pump.
        line_rate = source_power-load["electrical_power"]
        denergy = np.gradient(line_energy, t, axis=1, edge_order=2)
        carrier_rest = 2*self.host_coefficient*np.asarray(self.absolute_charge_per_length)*self.length
        added_trace = electric+magnetic+2*kinetic+source_energy
        added_trace_rate = line_rate+kinetic_rate+source_energy_rate
        return dict(line_energy=line_energy, electric_energy=electric, magnetic_energy=magnetic,
            carrier_kinetic_energy=kinetic, carrier_rest_energy=carrier_rest,
            integrated_maxwell_axial_stress=electric+magnetic,
            integrated_carrier_axial_stress=2*kinetic,
            field_momentum=momentum, field_momentum_rate=momentum_rate,
            source_voltage=source_voltage, source_current=source_current,
            source_power=source_power, source_capacitor_energy=source_energy,
            source_capacitor_charge=source_charge, source_capacitor_energy_rate=source_energy_rate,
            source_capacitance=source_capacitance,
            source_pump_current=source_pump_current, source_pump_power=source_pump_power,
            source_pump_correction=line_rate+source_energy_rate,
            load_power=load["electrical_power"],
            line_energy_rate=line_rate, sampled_line_energy_rate_error=denergy-line_rate,
            quadrature_energy_theorem_error=field_rate+kinetic_rate-line_rate,
            carrier_kinetic_energy_rate=kinetic_rate,
            unbalanced_added_trace=added_trace, unbalanced_added_trace_rate=added_trace_rate,
            peak_electric_field=peak_E, peak_magnetic_field=peak_B,
            peak_inner_radial_pressure=peak_radial_pressure,
            peak_outer_radial_pressure=peak_radial_pressure/self.radius_ratio**2,
            peak_drift=peak_current/np.asarray(self.absolute_charge_per_length),
            peak_charge_fraction=peak_line_charge/np.asarray(self.absolute_charge_per_length),
            required_axial_host_stress=electric+magnetic+2*kinetic,
            circumferential_host_stress_sum=hoop,
            source_axial_field_traction=.5*self.capacitance_per_length*source_voltage**2+.5*self.magnetic_inductance*source_current**2,
            load_axial_field_traction=.5*self.capacitance_per_length*load["voltage"]**2+.5*self.magnetic_inductance*load["current"]**2,
            finite_delay=self.delay, speed=self.length/self.delay,
            spatial_integrals_partitioned_at_terminal_knots=hasattr(terminals, "trace"),
            source_capacitor_state_counted=bool(np.all(source_capacitance > 0)),
            fixture_trace_included=False, fixture_evolving_work_included=False,
            source_capacitor_normal_and_external_tensor_placement_specified=False)


def choose_carrier_inventory(terminals, time, *, host_coefficient,
        mobile_mass_fraction=electron_mass/proton_mass, length_fraction=1.,
        radius_fraction=.01, radius_ratio=np.e, maximum_drift=.01,
        maximum_charge_fraction=.01, maximum_kinetic_fraction=.05):
    """Finite conserved inventories from sampled bounds plus declared margin.

    This is a numerical design screen. The final evaluation checks actual
    delayed fields against the inventory limits. Carrier rest energy stays
    present when current vanishes; junction/turn hosts have separate duties.
    """
    t = np.asarray(time)
    state = terminals(t)
    V, I = state["voltage"], state["current"]
    length = length_fraction*terminals.span
    if length < 2*np.sqrt(terminals.area.max()):
        raise ValueError("Lead length must cover finite source/load charge spreading")
    radius = radius_fraction*length
    Cg, Lg = 2*np.pi/np.log(radius_ratio), np.log(radius_ratio)/(2*np.pi)
    Vd, Id = state["voltage_rate"], state["current_rate"]
    vmax = np.max(abs(V), axis=1)+length*Lg*(1+maximum_kinetic_fraction)*np.max(abs(Id), axis=1)
    imax = np.max(abs(I), axis=1)+length*Cg*np.max(abs(Vd), axis=1)
    chi_mobile = host_coefficient*mobile_mass_fraction
    Lambda = 1.01*np.maximum.reduce((Cg*vmax/maximum_charge_fraction,
        imax/maximum_drift, np.full(4, 2*chi_mobile/(maximum_kinetic_fraction*Lg))))
    Lk = 2*chi_mobile/Lambda
    return FiniteCoax(length, radius, radius_ratio, Lk, Lambda, chi_mobile, host_coefficient)


def hardware_screen(terminals, time, line, result, *, stress_energy_factor=2.,
                    source_capacitance_fraction=.01, electrode_charge_fraction=.01):
    """Keep carrier inventories and necessary stress duties in one screen.

    Field energy in the four load banks is already part of D=.62 and is
    excluded from added energy. Their added electrode carriers are counted.
    Source states and all lead fields are new. The stress-energy factor is
    a declared allocation for prospective axial/hoop fixtures, including
    either sign of radial traction; it is not a realized elastic-host law.
    """
    if (stress_energy_factor < 1 or source_capacitance_fraction <= 0
            or not 0 < electrode_charge_fraction <= 1):
        raise ValueError("Positive source state and stress allowance at least the DEC lower bound required")
    state = terminals(time)
    if not result["source_capacitor_state_counted"]:
        raise ValueError("Hardware screen requires positive counted source capacitor states")
    source_charge = np.max(abs(result["source_capacitor_charge"]), axis=1)
    electrode_charge = np.max(abs(state["charge"]), axis=1)
    # Two oppositely charged electrode sets at each bank. This counts
    # additional matter; reusing original sheet carriers requires its own law.
    electrode_rest = 2*line.host_coefficient*(source_charge+electrode_charge)/electrode_charge_fraction
    line_rest = result["carrier_rest_energy"]
    axial_duty = np.max(result["required_axial_host_stress"], axis=1)
    hoop_duty = np.max(result["circumferential_host_stress_sum"], axis=1)
    source_energy = np.max(result["source_capacitor_energy"], axis=1)
    # A separate axial/tangential fixture allocation is held at its peak.
    complementary_duty = np.max(state["energy"][2:], axis=1)
    fixture = stress_energy_factor*(axial_duty+hoop_duty+source_energy)
    # Fixed complementary capacitors also need finite separators/anchors.
    # Reusing the parent sheet populations needs a spatial traction law;
    # this screen reserves separate capacity and credits no such reuse.
    complementary_fixture = stress_energy_factor*complementary_duty.sum()
    dynamic_peak = np.max(result["line_energy"], axis=1)+source_energy
    # The carrier/lattice rest inventory supplies its own radial and
    # axial fixtures only after an explicit shared material law is built.
    added = (dynamic_peak+line_rest+electrode_rest+fixture).sum()+complementary_fixture
    pressure = result["peak_inner_radial_pressure"]
    return dict(added_energy_over_C=float(added), line_and_source_state_over_C=float(dynamic_peak.sum()),
        added_lead_carrier_rest_over_C=float(line_rest.sum()),
        added_electrode_rest_over_C=float(electrode_rest.sum()),
        allocated_fixture_energy_over_C=float(fixture.sum()+complementary_fixture),
        allocated_line_and_source_fixture_energy_over_C=float(fixture.sum()),
        allocated_complementary_fixture_energy_over_C=float(complementary_fixture),
        necessary_complementary_plate_duty_over_C=float(complementary_duty.sum()),
        necessary_axial_duty_over_C=float(axial_duty.sum()),
        necessary_hoop_duty_over_C=float(hoop_duty.sum()),
        maximum_normalized_surface_pressure=float(pressure.max()),
        maximum_drift=float(result["peak_drift"].max()),
        maximum_charge_fraction=float(result["peak_charge_fraction"].max()),
        maximum_line_field=float(result["peak_electric_field"].max()),
        maximum_load_gap_field=float(abs(state["field"]).max()),
        maximum_source_capacitor_charge=float(source_charge.max()),
        maximum_load_electrode_charge=float(electrode_charge.max()),
        electrode_charge_fraction=electrode_charge_fraction,
        maximum_added_trace_over_C=float(result["unbalanced_added_trace"].sum(axis=0).max()),
        maximum_added_trace_rate=float(abs(result["unbalanced_added_trace_rate"].sum(axis=0)).max()),
        maximum_pump_power_correction=float(abs(result["source_pump_correction"].sum(axis=0)).max()),
        maximum_pump_current=float(abs(result["source_pump_current"]).max()),
        source_capacitance_fraction=source_capacitance_fraction,
        fixture_stress_energy_factor=stress_energy_factor,
        fixture_constitutive_law_constructed=False,
        fixture_evolving_work_included=False,
        fixture_trace_cancellation_claimed=False,
        electrode_rest_counted_separately_from_original_sheets=True,
        optical_electrical_pump_physical_law_constructed=False,
        effective_line_model=True, full_maxwell_matter_completion=False)
