"""Constitutive receiving stores and explicit optical hardware requirements.

Energy is measured in C=P_peak*delta and time in delta. Store walls retain
fixed reference inventory. Routing equilibrium, finite splitter response,
and accumulated losses are separate gates; their energy screens do not
assert a spatial, thermodynamic, or microscopic assembly closure.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

from .constitutive_joints_and_optics import ring_state


def splitter_matrix(phase):
    """Two-output unitary for a balanced, push-pull Mach-Zehnder.

    A static phase convention removes the common optical phase. Dynamic
    phase drive and electrode losses are accounted for by the caller.
    """
    phase = np.asarray(phase, float)
    if not np.isfinite(phase).all():
        raise ValueError("finite phase required")
    c, s = np.cos(phase/2), np.sin(phase/2)
    result = np.empty(phase.shape+(2, 2), complex)
    result[..., 0, 0] = result[..., 1, 1] = c
    result[..., 0, 1] = result[..., 1, 0] = 1j*s
    return result


def switched_demand(time, *, half_period, intervals=80, transition=0.):
    """Unit-peak finite train: phase ramps take `transition` time.

    Return power and its exact cumulative integral. Every full cycle has
    half duty, including the ramps. The square limit is a stress test;
    finite ramps change delivery timing and require a separate fit to the
    prescribed component exchanges.
    """
    if (not np.isfinite([half_period, transition]).all() or half_period <= 0
            or not 0 <= transition <= half_period or intervals < 2
            or int(intervals) != intervals or intervals % 2):
        raise ValueError("positive half period, bounded transition and positive even interval count required")
    time = np.asarray(time, float)
    if not np.isfinite(time).all():
        raise ValueError("finite times required")
    duration = intervals*half_period
    clipped = np.clip(time, 0., duration)
    cycles = np.floor(clipped/(2*half_period))
    phase = clipped-2*half_period*cycles
    if transition == 0:
        power = (phase < half_period).astype(float)
        partial = np.minimum(phase, half_period)
    else:
        rise = np.clip(phase, 0., transition)
        fall = np.clip(phase-half_period, 0., transition)
        power = np.where(phase < half_period, np.sin(np.pi*rise/(2*transition))**2,
                         np.cos(np.pi*fall/(2*transition))**2)
        rise_energy = .5*(rise-transition/np.pi*np.sin(np.pi*rise/transition))
        fall_energy = .5*(fall+transition/np.pi*np.sin(np.pi*fall/transition))
        partial = rise_energy+np.clip(phase-transition, 0., half_period-transition)+fall_energy
    power = np.where((time >= 0) & (time < duration), power, 0.)
    return power, cycles*half_period+partial


def store_rhs(state, net_power, *, inventory=8., reference_radius=1/(3*np.pi)):
    """Ring charged through matched comoving ports; no free damping sink.

    State=(R/R0, p/M, K/(M R0)); powers are in P_peak units. Outflow is
    commanded independently of wall state. The required port optical depth
    is subsequently checked against one per circuit.
    """
    if (not np.isfinite([net_power, inventory, reference_radius]).all()
            or min(inventory, reference_radius) <= 0):
        raise ValueError("finite power, positive reference inventory and radius required")
    x, p, z = np.asarray(state, float)
    s = ring_state(x, p, z)
    return np.array([s["speed"]/reference_radius,
        (s["photon_energy"]-s["material_tension"])/(s["gamma"]*x*reference_radius)
        +s["speed"]*net_power/inventory, x*net_power/(s["gamma"]*inventory)])


def thermal_store_state(state):
    """A coherent optical action z and trapped thermal radiation action b.

    Both populations carry longitudinal photon pressure. Thermal radiation
    stays in the wall/store assembly, outside the controlled useful port.
    An equilibrated one-dimensional radiation bath has entropy proportional
    to sqrt(b), assuming a continuum of thermally populated modes.
    This is a constitutive thermal specialization, with its spectral trap
    and material coupling still requiring a microscopic implementation.
    """
    x, p, z, b = np.asarray(state, float)
    if np.any(z < 0) or np.any(b < 0):
        raise ValueError("nonnegative coherent and thermal actions required")
    result = ring_state(x, p, z+b)
    result.update(thermal_energy=result["gamma"]*b/x,
                  coherent_energy=result["gamma"]*z/x, entropy_proxy=np.sqrt(b))
    return result


def thermal_store_rhs(state, net_power, *, inventory=8., reference_radius=1/(3*np.pi),
                      damping=0., absorption_depth=0.):
    """Viscous mode work becomes counted, pressure-carrying internal heat.

    Friction -k*p/R0 transfers exactly its kinetic work to thermal action.
    Absorption transfers coherent action to thermal action. Each process
    conserves total store energy; only the external net power changes it.
    A local causal dissipative material and thermalization timescale remain
    required beyond this homogeneous mode law.
    """
    if (not np.isfinite([net_power, inventory, reference_radius, damping, absorption_depth]).all()
            or min(inventory, reference_radius) <= 0 or min(damping, absorption_depth) < 0):
        raise ValueError("finite net power, positive scales and nonnegative dissipation required")
    x, p, z, b = np.asarray(state, float)
    # Extend the smooth vector field through b=0 for internal Runge-Kutta
    # stages. Accepted/output states are checked by thermal_store_state;
    # neither stored action nor the integrated heat is clipped here.
    s = ring_state(x, p, z+b)
    friction = damping*p/reference_radius
    thermalized = s["gamma"]*x*friction*s["speed"]
    absorbed = absorption_depth*z/(2*np.pi*reference_radius*x*s["gamma"])
    return np.array([s["speed"]/reference_radius,
        (s["photon_energy"]-s["material_tension"])/(s["gamma"]*x*reference_radius)
        +s["speed"]*net_power/inventory-friction,
        x*net_power/(s["gamma"]*inventory)-absorbed, thermalized+absorbed])


def retained_store_orbit(state, *, inventory=8., reference_radius=1/(3*np.pi)):
    """Exact future radii for zero net power, zero damping and zero loss.

    H and total photon action remain constant. This checks all future
    radial phases, including the worst extraction depth, after a trial.
    """
    x, p, z, b = np.asarray(state, float)
    h = float(thermal_store_state(state)["energy"])
    width = np.sqrt(max(h*h-1-2*(z+b), 0.))
    low, high = h-width, h+width
    depth = 2*np.pi*reference_radius*high*high/(inventory*z) if z > 0 else np.inf
    return dict(radius_minimum=low, radius_maximum=high, maximum_extraction_depth=depth,
                admissible=bool(low >= 1 and high <= 1.5 and depth <= 1))


def simulate_store(*, inventory=8., reference_radius=1/(3*np.pi),
                   initial_radius=1/np.sqrt(.6), half_period=3.8238248063636506/(3*np.pi),
                   intervals=80, transition=0., maximum_step=.02, output_step=.02,
                   damping=0., absorption_depth=0., rtol=2e-9, atol=2e-11):
    """Test a physical wall in place of the nominal receiving reservoir.

    The guide remains at its exact steady solution. Store inflow is
    A(t-1)+1-A(t), store outflow is one. Therefore H_store+inflight is
    conserved. No finite-phase ramp is silently substituted for a square
    prescribed delivery. Boundary events stop the candidate at first loss
    of tensile operation, radius cap, photon inventory, or extraction rate.
    """
    switched_demand(0., half_period=half_period, intervals=intervals, transition=transition)
    values = [inventory, reference_radius, initial_radius, maximum_step, output_step, rtol, atol]
    if not np.isfinite(values).all() or min(values) <= 0 or not 1 < initial_radius < 1.5:
        raise ValueError("positive finite store and solver parameters; initial radius inside (1,1.5)")
    if not np.isfinite([damping, absorption_depth]).all() or min(damping, absorption_depth) < 0:
        raise ValueError("nonnegative finite dissipation required")
    final = intervals*half_period+1.
    cuts = [0., final]
    for delay in (0., 1.):
        for k in range(intervals+1):
            for ramp in (0., transition):
                t = k*half_period+delay+ramp
                if 0 < t < final:
                    cuts.append(t)
    cuts = np.unique(cuts)
    state = np.array([initial_radius, 0., .5*(initial_radius**2-1), 0.])
    initial_energy = inventory*float(thermal_store_state(state)["energy"])
    initial_depth = 2*np.pi*reference_radius*state[0]**2/(inventory*state[2])
    if initial_depth >= 1:
        raise ValueError("initial store cannot emit the nominal guide power at optical depth <=1")

    def tensile(t, y):
        return y[0]-1
    def size(t, y):
        return 1.5-y[0]
    def extraction(t, y):
        return inventory*y[2]-2*np.pi*reference_radius*y[0]**2
    for event in (tensile, size, extraction):
        event.terminal = True
        event.direction = -1
    records, times = [], []
    boundary = None
    for start, end in zip(cuts[:-1], cuts[1:]):
        # On a square segment use its interior to avoid evaluating the
        # next jump at the endpoint of a Runge-Kutta stage.
        mid = (start+end)/2
        constant = float(switched_demand(mid-1, half_period=half_period, intervals=intervals)[0]
                         -switched_demand(mid, half_period=half_period, intervals=intervals)[0])
        def rhs(t, y):
            net = constant if transition == 0 else float(
                switched_demand(t-1, half_period=half_period, intervals=intervals, transition=transition)[0]
                -switched_demand(t, half_period=half_period, intervals=intervals, transition=transition)[0])
            return thermal_store_rhs(y, net, inventory=inventory, reference_radius=reference_radius,
                                     damping=damping, absorption_depth=absorption_depth)
        solution = solve_ivp(rhs, (start, end), state, method="DOP853", dense_output=True,
            max_step=maximum_step, rtol=rtol, atol=atol, events=(tensile, size, extraction))
        if not solution.success:
            raise ValueError(solution.message)
        thermal_store_state(solution.y)
        end_time = float(solution.t[-1])
        grid = np.linspace(start, end_time, max(2, int(np.ceil((end_time-start)/output_step))+1))
        # Retain one copy of each interface for interpolation/refinement.
        if times:
            grid = grid[1:]
        times.append(grid)
        records.append(solution.sol(grid))
        state = solution.y[:, -1]
        if solution.status:
            boundary = ("tensile", "radius", "extraction")[next(i for i, e in enumerate(solution.t_events) if len(e))]
            break
    time, history = np.concatenate(times), np.concatenate(records, axis=1)
    values = thermal_store_state(history)
    viscous_trace = -inventory*damping*history[0]*history[1]
    total_hoop_stress = (values["photon_energy"]-values["material_tension"]
                        -values["gamma"]*damping*history[0]*history[1])
    demand, integral = switched_demand(time, half_period=half_period, intervals=intervals, transition=transition)
    arrival, old_integral = switched_demand(time-1, half_period=half_period, intervals=intervals, transition=transition)
    transit = integral-old_integral
    energy = inventory*values["energy"]
    circulating_power = inventory*history[2]/(2*np.pi*reference_radius*history[0]**2)
    return dict(time=time, state=history, energy=energy, speed=values["speed"],
        pressure_trace=inventory*values["pressure_trace"]+viscous_trace,
        elastic_radiation_trace=inventory*values["pressure_trace"], viscous_trace=viscous_trace,
        hoop_stress_energy_ratio=abs(total_hoop_stress)/values["rest_energy"], inflight=transit,
        balance_error=energy+transit-initial_energy, input_power=arrival+1-demand,
        output_power=np.ones_like(time), extraction_depth=1/circulating_power,
        circulating_power=circulating_power, useful_power=demand, useful_energy=integral,
        thermal_energy=inventory*values["thermal_energy"], entropy_proxy=values["entropy_proxy"],
        boundary=boundary, complete=boundary is None, initial_energy=initial_energy,
        quasistatic_energy_floor=initial_energy-1, reference_inventory=inventory,
        reference_radius=reference_radius, transition=transition, damping=damping,
        absorption_depth=absorption_depth,
        retained_orbit=(retained_store_orbit(history[:, -1], inventory=inventory, reference_radius=reference_radius)
                        if boundary is None and damping == 0 and absorption_depth == 0 else None))


def polygon_reactions(vertices, power=1., stretch=1.5):
    """Static closed beam polygon with a continuous elastic tension member.

    c=1, and `power` sums both counterpropagating beams. Reversing half the
    flux cancels angular momentum while preserving force and stress. The
    wall's E=M/2*(stretch+1/stretch) balances every turn at this load.
    A power-dependent equilibrium family is not one fixed-geometry wall.
    """
    vertices = np.asarray(vertices, float)
    if (vertices.ndim != 2 or vertices.shape[1] != 3 or len(vertices) < 3
            or not np.isfinite(vertices).all() or not np.isfinite([power, stretch]).all()
            or power < 0 or stretch <= 1):
        raise ValueError("finite 3D polygon, nonnegative power and tensile stretch required")
    edges = np.roll(vertices, -1, axis=0)-vertices
    lengths = np.linalg.norm(edges, axis=1)
    if np.any(lengths <= 0):
        raise ValueError("each edge must have positive length")
    directions = edges/lengths[:, None]
    force = power*(np.roll(directions, 1, axis=0)-directions)
    photons = power*np.einsum("i,ij,ik->jk", lengths, directions, directions)
    wall = np.einsum("ij,ik->jk", vertices, -force)
    photon_energy = power*lengths.sum()
    mass = 2*photon_energy/(stretch-1/stretch)
    return dict(vertex_force=force, net_force=force.sum(axis=0),
        net_torque=np.cross(vertices, force).sum(axis=0), photon_tensor=photons,
        wall_tensor=wall, photon_energy=photon_energy, wall_reference_inventory=mass,
        wall_energy=.5*mass*(stretch+1/stretch), total_path_length=lengths.sum())


def assembly_energy_screen(capacity, previous_preparation, previous_initial_buffer,
                           *, store_inventory=8., store_radius=1/np.sqrt(.6),
                           path_capacity_multiple=2.75, route_stretch=1.5):
    """Replace the abstract initial charge; price static path support.

    The path photon capacity is already present in previous_preparation.
    Only its elastic wall is added here. This is a candidate energy screen:
    actual variable path tensions and the full target tensor remain gates.
    """
    C, old, buffer = np.broadcast_arrays(capacity, previous_preparation, previous_initial_buffer)
    scalars = [store_inventory, store_radius, path_capacity_multiple, route_stretch]
    if (not all(np.isfinite(a).all() for a in (C, old, buffer))
            or np.any(C < 0) or np.any(buffer < 0) or np.any(old < buffer)
            or not np.isfinite(scalars).all() or store_inventory <= 0
            or store_radius <= 1 or path_capacity_multiple < 0 or route_stretch <= 1):
        raise ValueError("admissible positive inventories and tensile reference required")
    store = store_inventory*store_radius*C
    route_wall = path_capacity_multiple*C*(route_stretch**2+1)/(route_stretch**2-1)
    return dict(store_energy=store, removed_abstract_buffer=buffer, route_wall_energy=route_wall,
                candidate_preparation=old-buffer+store+route_wall,
                added_energy=store-buffer+route_wall)


def loss_budget(reserve, cumulative_throughput, *, circulation_multiple=1.,
                round_trip_loss=0., splitter_unrecovered=0., drive_energy=0.):
    """Finite-run energy screen; all losses need replacement and a heat port.

    Retained loss here is the *additional* preparation needed to preserve
    the lossless useful exchange and charge schedule. Conversion hardware,
    heat pressure and exporter mass require separate components. Export
    removes heat, but leaves the full replacement energy requirement. The
    conditional removal fraction assumes an independently counted supply;
    it cannot rescue this closed, precharged energy screen. Surplus light
    intentionally sent to the second port is absent from losses.
    """
    reserve, traffic = np.broadcast_arrays(reserve, cumulative_throughput)
    vals = [circulation_multiple, round_trip_loss, splitter_unrecovered, drive_energy]
    if (not all(np.isfinite(a).all() for a in (reserve, traffic)) or np.any(traffic < 0)
            or not np.isfinite(vals).all() or min(vals) < 0):
        raise ValueError("finite reserve, nonnegative traffic and loss parameters required")
    loss = traffic*(circulation_multiple*round_trip_loss+splitter_unrecovered)+drive_energy
    ceiling = np.divide(np.maximum(reserve-drive_energy, 0.), traffic,
                        out=np.full_like(traffic, np.inf, dtype=float), where=traffic > 0)
    fraction = np.clip(np.divide(np.maximum(loss-reserve, 0.), loss,
                                out=np.zeros_like(loss), where=loss > 0), 0., 1.)
    return dict(retained_energy=loss, remaining_reserve=reserve-loss,
        effective_loss_ceiling=ceiling, conditional_heat_removal_fraction=fraction,
        required_replacement_energy=loss)
