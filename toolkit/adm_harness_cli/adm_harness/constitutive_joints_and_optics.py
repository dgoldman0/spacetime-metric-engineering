"""Force-matched series joints and a homogeneous elastic optical ring.

Joints participate in the existing tensile load path. Their reference
length and material inventory are fixed, and their actual length follows
the same transmitted force as the core. The optical ring is a reduced
axisymmetric classical model with ideal guiding and comoving optical ports.
It includes its elastic, photon and radial kinetic energies explicitly.
"""
from __future__ import annotations

import numpy as np

from .material_reconfiguration import (
    MATERIAL_DIMENSIONS, PRESSURE_BASIS, elastic_state_from_tension,
)


def series_state(total_tension, core_inventory, joint_inventory, *, dimension=1,
                 reference_fraction=1e-4, shear_fraction=.1):
    """Invert the effective constitutive law of a core and inline joints.

    Each loaded direction has a core span d0*S and total added joint span
    alpha*d0*j. If t is core tensile energy, f=t/S is force times d0.
    Fixed relaxed joint energy m gives j=(1-2*alpha*f/m)**(-1/2).
    The effective tensile duty is t+alpha*f*j. A sheet has two equal
    directional joint populations; a string has one. Returned energies
    count each direction once.
    """
    T, M, m, d, alpha = np.broadcast_arrays(*map(lambda a: np.asarray(a, float),
        (total_tension, core_inventory, joint_inventory, dimension, reference_fraction)))
    if (not all(np.isfinite(a).all() for a in (T, M, m, d, alpha))
            or np.any(T < 0) or np.any(M <= 0) or np.any(m <= 0) or np.any(alpha <= 0)
            or np.any((d != 1) & (d != 2)) or not 0 <= shear_fraction < 1):
        raise ValueError("nonnegative duties, positive fixed inventories/lengths and dimensions 1 or 2 required")
    eps = np.where(d == 2, shear_fraction, 0.)
    scale = (1-eps)*M

    def values(t):
        root = np.hypot(t, scale)
        logS = np.arcsinh(t/scale)/d
        S = np.exp(logS)
        force = np.where(d == 1, -.5*M*np.expm1(-2*logS), t/S)
        # A same-density string approaches its force capacity at large
        # stretch. This equivalent expression retains its small margin.
        den = np.where(d == 1, (m-alpha*M)/m+(alpha*M/m)*np.exp(-2*logS),
                       1-2*alpha*force/m)
        j = 1/np.sqrt(np.maximum(den, np.finfo(float).tiny))
        tie = alpha*force*j
        return root, S, force, j, tie, den

    low, high = np.zeros_like(T), T.copy()
    for _ in range(60):
        t = (low+high)/2
        _, _, _, _, tie, den = values(t)
        above = (t+tie > T) | (den <= 0)
        high, low = np.where(above, t, high), np.where(above, low, t)
    t = (low+high)/2
    root, S, force, j, tie, den = values(t)
    if np.any(den <= 0):
        raise ValueError("joint force exceeds its constitutive capacity")
    fp = np.where(d == 1, scale**2/(root*(root+t)*S), (1-t/(d*root))/S)
    jp = alpha*fp*j**3/m
    derivative = 1+alpha*fp*j+alpha*force*jp
    core_E = root+eps*M
    joint_E = .5*m*(j+1/j)
    cell = S+alpha*j
    return dict(core_tension=t, joint_tension=tie, effective_tension=t+tie,
        core_energy=core_E, joint_energy_per_direction=joint_E,
        total_energy=core_E+d*joint_E, core_linear_stretch=S, joint_stretch=j,
        cell_linear_stretch=cell/(1+alpha), joint_to_core_span=alpha*j/S,
        force_times_core_reference_span=force, force_margin=den,
        core_load_derivative=1/derivative,
        core_energy_derivative=(t/root)/derivative,
        joint_energy_derivative=d*tie*jp/(j*derivative),
        cell_log_derivative=(S/(d*root)+alpha*jp)/(cell*derivative),
        joint_log_derivative=jp/(j*derivative), force_derivative=fp,
        effective_load_derivative=derivative)


def prepare_series_joints(tension, core_inventory, *, reference_fraction=1e-4,
                          maximum_joint_stretch=2.):
    """Prepare fixed joint material using an upper bound on core force.

    The core duty is at most the total duty and its force increases with
    duty. Evaluating that force at the full duty gives a sufficient relaxed
    joint inventory for the selected maximum stretch. Unloaded directions
    retain a positive same-density reference inventory.
    """
    T, M = np.asarray(tension, float), np.asarray(core_inventory, float)
    if (T.ndim != 3 or T.shape[0] != 6 or M.shape != (6, T.shape[-1])
            or not all(np.isfinite(a).all() for a in (T, M)) or np.any(T < 0)
            or np.any(M <= 0) or not np.isfinite([reference_fraction, maximum_joint_stretch]).all()
            or reference_fraction <= 0 or maximum_joint_stretch <= 1):
        raise ValueError("six finite histories and positive preparation parameters required")
    dims = MATERIAL_DIMENSIONS[:, None, None]
    eps = np.where(dims == 2, .1, 0.)
    plain = elastic_state_from_tension(T, M[:, None], shear_fraction=eps)
    span = np.exp(plain["log_strain"]/dims)
    peak_force = (T/span).max(axis=1)
    joint_M = np.maximum(reference_fraction*M,
        2*reference_fraction*peak_force/(1-maximum_joint_stretch**-2))
    state = series_state(T, M[:, None], joint_M[:, None], dimension=dims,
                         reference_fraction=reference_fraction)
    return dict(joint_inventory_per_direction=joint_M, state=state,
        total_joint_reference_energy=np.einsum("i,ij->j", MATERIAL_DIMENSIONS, joint_M))


def series_power_bounds(tension, core_inventory, joint_inventory, fields, target,
                        lr, lt, proper_duration, *, reference_fraction=1e-4):
    """Conservative panel bounds including core and joint operating work.

    Monotone core force and joint stretch bound the implicit-law derivatives.
    Core force derivative decreases with load. Independent interval products
    yield outward bounds even if power extrema lie inside a panel. The final
    two nodes are the remaining inventory and complementary rail port.
    """
    dt = np.asarray(proper_duration)
    dims = MATERIAL_DIMENSIONS[:, None, None]
    M, m = core_inventory[:, None], joint_inventory[:, None]
    low = series_state(np.minimum(tension[:, :-1], tension[:, 1:]), M, m,
                       dimension=dims, reference_fraction=reference_fraction)
    high = series_state(np.maximum(tension[:, :-1], tension[:, 1:]), M, m,
                        dimension=dims, reference_fraction=reference_fraction)
    alpha = reference_fraction
    fp_lo, fp_hi = high["force_derivative"], low["force_derivative"]
    jlo, jhi = low["joint_stretch"], high["joint_stretch"]
    flo, fhi = low["force_times_core_reference_span"], high["force_times_core_reference_span"]
    Dlo = 1+alpha*fp_lo*jlo+alpha**2*flo*fp_lo*jlo**3/m
    Dhi = 1+alpha*fp_hi*jhi+alpha**2*fhi*fp_hi*jhi**3/m
    eps = np.where(dims == 2, .1, 0.)
    core_lo = low["core_tension"]/np.hypot(low["core_tension"], (1-eps)*M)/Dhi
    core_hi = high["core_tension"]/np.hypot(high["core_tension"], (1-eps)*M)/Dlo
    joint_lo = dims*low["joint_tension"]*alpha*fp_lo*jlo**2/(m*Dhi)
    joint_hi = dims*high["joint_tension"]*alpha*fp_hi*jhi**2/(m*Dlo)
    load_rate = np.diff(tension, axis=1)/dt
    dz, da = np.diff(np.log(lr), axis=0)/dt, np.diff(np.log(lt), axis=0)/dt
    work = PRESSURE_BASIS[0, :6, None, None]*dz+PRESSURE_BASIS[1, :6, None, None]*da
    def product(a, b, coefficient):
        return np.minimum(a*coefficient, b*coefficient), np.maximum(a*coefficient, b*coefficient)
    core_derivative = product(core_lo, core_hi, load_rate)
    joint_derivative = product(joint_lo, joint_hi, load_rate)
    core_work = product(low["core_tension"], high["core_tension"], work)
    joint_work = product(low["joint_tension"], high["joint_tension"], work)
    field_derivative = np.diff(fields, axis=1)/dt
    field_work = PRESSURE_BASIS[0, 6:10, None, None]*dz+PRESSURE_BASIS[1, 6:10, None, None]*da
    fw = product(fields[:, :-1], fields[:, 1:], field_work)
    rho_rate = np.diff(target[0], axis=0)/dt
    dust_base = rho_rate-field_derivative.sum(axis=0)
    dust_lo = dust_base-core_derivative[1].sum(axis=0)-joint_derivative[1].sum(axis=0)
    dust_hi = dust_base-core_derivative[0].sum(axis=0)-joint_derivative[0].sum(axis=0)
    rail0 = -rho_rate-target[1, :-1]*dz-2*target[2, :-1]*da
    rail1 = -rho_rate-target[1, 1:]*dz-2*target[2, 1:]*da
    lower = np.concatenate([core_derivative[0]+core_work[0], joint_derivative[0]+joint_work[0],
        field_derivative+fw[0], dust_lo[None], np.minimum(rail0, rail1)[None]])
    upper = np.concatenate([core_derivative[1]+core_work[1], joint_derivative[1]+joint_work[1],
        field_derivative+fw[1], dust_hi[None], np.maximum(rail0, rail1)[None]])
    return dict(lower=lower, upper=upper)


def ring_state(radius, momentum, photon_action):
    """Dimensionless homogeneous ring: R/Rref, p/M, K/(M*Rref).

    Opposed circulating photons share the elastic ring's radial motion.
    V=E_string+K/R and H=sqrt(p^2+V^2). The returned pressure trace includes
    radial kinetic pressure and the boosted hoop stress. Three equally
    populated orthogonal ring planes give an isotropic averaged pressure.
    """
    x, p, z = np.broadcast_arrays(radius, momentum, photon_action)
    if (not all(np.isfinite(a).all() for a in (x, p, z)) or np.any(x <= 0) or np.any(z < 0)):
        raise ValueError("positive radius and nonnegative photon action required")
    material, tension, photons = .5*(x+1/x), .5*(x-1/x), z/x
    rest = material+photons
    H = np.hypot(p, rest)
    v, gamma = p/H, H/rest
    trace = H*v*v+(photons-tension)/gamma
    return dict(energy=H, material_energy=material, material_tension=tension,
        photon_energy=photons, rest_energy=rest, speed=v, gamma=gamma,
        kinetic_energy=H-rest, pressure_trace=trace)


def ring_rhs(state, input_power, *, escape_depth=1.):
    """Open radial dynamics in units Rref/c and M*c^2/Rref.

    Escape is a distributed optical-depth rate per circuit; comoving ports
    supply/remove radial momentum v*P together with energy P. Their action
    rate R*P/gamma makes dH/dt=P exactly. The external path delay is supplied
    by the caller. The axisymmetric guiding and optical ports are explicit
    reduced-model assumptions, with microscopic reflectors left open.
    """
    x, p, z = np.asarray(state)[:3]
    if not np.isfinite([input_power, escape_depth]).all() or input_power < 0 or escape_depth < 0:
        raise ValueError("nonnegative finite input power and escape depth required")
    s = ring_state(x, p, z)
    emitted = escape_depth*z/(2*np.pi*x*x)
    net = input_power-emitted
    return np.array([s["speed"], (s["photon_energy"]-s["material_tension"])/(s["gamma"]*x)
                     +s["speed"]*net, x*net/s["gamma"], net])


def ring_equilibrium(power_fraction, *, escape_depth=1.):
    """Steady drive divided by the finite elastic force-capacity threshold.

    A tensile equilibrium exists for 0<=s<1, with radius 1/sqrt(1-s).
    In time units equal to the equilibrium radius, the linear characteristic
    polynomial is lambda^3+b*lambda^2+lambda+b*(1-s), b=escape_depth/(2*pi).
    For 0<s<1 and escape_depth>0 its roots have negative real parts.
    """
    s = float(power_fraction)
    if not np.isfinite([s, escape_depth]).all() or not 0 <= s < 1 or escape_depth <= 0:
        raise ValueError("equilibrium requires 0<=power fraction<1 and positive escape depth")
    x = 1/np.sqrt(1-s)
    z = .5*(x*x-1)
    b = escape_depth/(2*np.pi)
    return dict(state=np.array([x, 0., z]), input_power=b*s/2,
                eigenvalues=np.roots([1., b, 1., b*(1-s)])/x,
                threshold_input_power=b/2)
