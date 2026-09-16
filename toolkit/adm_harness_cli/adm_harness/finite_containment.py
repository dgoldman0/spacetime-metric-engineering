"""Finite coaxial current paths and fixed-inventory containment tests.

The added hoop field occupies the existing straight annulus. Axial surface
currents return across both annular ends. The magnetostatic construction
resolves radial tractions; axial end forces and background-field torques
are separate interface duties. Units are the inherited c=mu0=1 units.

The particle realization retains the original carriers and supplies new
opposed charges. Bounds on this realization allow every subluminal drift
speed. Fixed-material tests use several distinct constituents, with each
energy counted once. These are construction tests, not material identities
for all possible ensembles.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from .magnetic_load_balance import support_cone


EVOLUTION_NAMES = ("inner_longitudinal_sheet", "inner_hoop_strings",
                   "outer_longitudinal_sheet", "outer_hoop_strings",
                   "transverse_sheet", "inner_hoop_photons",
                   "outer_hoop_photons", "transverse_photons", "hoop_field")
# Rows are energy, axial pressure, and transverse pressure trace.
EVOLUTION_BASIS = np.array([[1., 1., 1., 1., 1., 1., 1., 1., 1.],
                            [-1., 0., -1., 0., 0., 0., 0., 0., 1.],
                            [-1., -1., -1., -1., -2., 1., 1., 1., 0.]])


def annular_factor(eta):
    if not np.isfinite(eta) or eta <= 1:
        raise ValueError("outer/inner radius ratio must exceed one")
    return np.expm1(2*np.log(eta))/(2*np.log(eta))


def geometry(volume, axial_stretch, transverse_stretch, initial_ell,
             coordinate_span, *, eta=1.01, aspect=.01, tube_ratio=.1, fill=.1):
    D, lr, lt = map(lambda x: np.asarray(x, float),
                    (volume, axial_stretch, transverse_stretch))
    annular_factor(eta)
    if (D.ndim != 2 or lr.shape != D.shape or lt.shape != D.shape
            or not all(np.isfinite(x).all() and np.all(x > 0) for x in (D, lr, lt))
            or not np.isfinite([coordinate_span, aspect, tube_ratio, fill]).all()
            or min(coordinate_span, aspect, tube_ratio, fill) <= 0
            or eta*tube_ratio >= 1 or fill*eta**2 >= 1):
        raise ValueError("positive compatible histories and a fitting annulus required")
    L0 = .5*coordinate_span*np.asarray(initial_ell)/(1+2*aspect*(1+eta*tube_ratio))
    L, r = L0*lr, tube_ratio*aspect*L0*lt
    Vs = fill*D/(1+np.pi*aspect)
    return dict(leg=L, inner_radius=r, straight_core_volume=Vs,
                cartridges=Vs/(np.pi*r*r*L), eta=eta,
                axial_current_per_root_energy=4/r*np.sqrt(Vs/np.log(eta)),
                return_to_axial_current_ratio=(eta-1)*r/L)


def field_interfaces(energy, geom, background_axial_field=0.):
    """Exact static B_theta=C/s solution, including both end returns.

    A stack of transverse sheets has constant tensile density m=b_inner.
    Its radial stress cancels the added field at the inner interface.
    At the outer interface it unloads the original hoop by 2*M, where
    M=R_eta*energy. Superposing the original axial field also gives a
    shear traction and equal/opposite torques on the two annular ends.
    """
    U = np.asarray(energy, float)
    if not np.isfinite(U).all() or np.any(U < 0):
        raise ValueError("nonnegative finite field energy required")
    eta, r, L, Vs = (geom[k] for k in ("eta", "inner_radius", "leg", "straight_core_volume"))
    Bi = np.sqrt(U/(Vs*np.log(eta)))
    J = geom["axial_current_per_root_energy"]*np.sqrt(U)
    m = Bi*Bi/2
    return dict(inner_field=Bi, current_per_cartridge=2*np.pi*r*Bi,
                axial_current_integral=J,
                return_current_integral=J*geom["return_to_axial_current_ratio"],
                transverse_net_tension_energy=annular_factor(eta)*U,
                inner_extra_radial_traction=np.zeros_like(U),
                outer_extra_radial_traction=m/eta**2-m,
                axial_force_per_end_set=U/L,
                torque_per_end_set=Vs*(eta**2-1)*r*Bi*background_axial_field/L,
                integrated_axial_hoop_shear=2*Vs*(eta-1)*Bi*background_axial_field)


def particle_inventory(current, coefficient, *, peak_speed=1/np.sqrt(2)):
    """A conserved opposed-charge population on each material path family.

    N is total absolute charge, including both species. Equal currents
    enter/leave each cylindrical or return face; N stays fixed in that
    moving face. Distinct face speeds allow the radial and axial lengths
    to change independently. Junction acceleration needs counted control
    work and reactions. This excludes conductor lattice and binding costs.
    """
    J = np.asarray(current, float)
    if (J.ndim != 2 or not np.isfinite(J).all() or np.any(J < 0)
            or not np.isfinite(coefficient) or coefficient < 0
            or not np.isfinite(peak_speed) or not 0 < peak_speed < 1):
        raise ValueError("nonnegative currents/coefficient and subluminal peak speed required")
    N = J.max(axis=0)/peak_speed
    speed = np.divide(J, N, out=np.zeros_like(J), where=N > 0)
    E = coefficient*N/np.sqrt(1-speed*speed)
    return dict(charge_inventory=N, speed=speed, energy=E, pressure=E*speed*speed)


def allocate_field(target, floor, inner_hoop, outer_hoop, field_energy, *, eta=1.01,
                   carrier_energy=0., carrier_axial_pressure=0., return_pressure=0.):
    """Reallocate sheets/strings with finite radial interfaces at fixed field.

    All inputs are integrated energies/stresses. Ideal radial strings at
    the end returns cancel the return carriers' positive radial pressure;
    their minimum energy equals that pressure. Their finite joints and
    constitutive history remain additional requirements.
    """
    T = np.asarray(target, float)
    Hi, Ho, B = np.broadcast_arrays(inner_hoop, outer_hoop, field_energy)
    H, M = Hi+Ho, annular_factor(eta)*B
    if np.min(Ho-2*M) < -1e-10 or np.min(B) < 0:
        raise ValueError("field overcompresses the tensile outer interface")
    F = support_cone(*T, floor)["facets"]
    Ec = np.asarray(carrier_energy)+np.asarray(return_pressure)
    Pc = np.asarray(carrier_axial_pressure)
    first = np.maximum(F[0]+2*H, F[1]+H/2)-M+Ec-Pc
    third = F[2]+H/2+3*B-M+Ec+2*Pc
    W = np.clip((third-first)/3, 0., np.maximum(H-2*M, 0.))
    Wi = np.minimum(W, Hi)
    Wo = W-Wi
    parts = np.stack([Wi, Hi-Wi, Wo, Ho-2*M-Wo, M, B,
                      np.broadcast_to(carrier_energy, H.shape),
                      np.broadcast_to(return_pressure, H.shape)])
    tensor = np.stack([parts.sum(axis=0), B-W+Pc, -H/2])
    cone = support_cone(*(T-tensor), floor)
    return dict(components=parts, tensor=tensor, support=cone,
                shortfall=cone["shortfall"], longitudinal_energy=W,
                extra_end_tension=np.maximum(B+Pc-W, 0.),
                full_support_end_capacity=cone["field"]+W-B-Pc,
                above_floor_end_capacity=cone["field"]-floor+W-B-Pc)


def necessary_host_bound(facets, inner_hoop, outer_hoop, current_per_root_energy,
                       coefficient, *, eta=1.01):
    """A continuous, all-speed rejection bound for independent new carriers.

    Omit all return carriers, end ties and shear hosts. Write E=P+Q for
    axial particles. Cauchy-Schwarz gives P*Q >= (chi*J)**2 for arbitrary
    velocity mixtures. The support facets imply Q <= R*B-a and
    E <= E0+(R-1)*B, with a=max(F0+2H,F1+H/2), E0=-(2a+c)/3.
    For a>0 and E0>=0, (R-a/B)*(E0+(R-1)*B) increases with B.
    Its value at Bmax=Ho/(2R) gives a generous necessary chi upper bound.
    A positive excess certifies failure; the converse grants no witness.
    """
    F = np.asarray(facets)
    H = np.asarray(inner_hoop)+outer_hoop
    R = annular_factor(eta)
    a, c = np.maximum(F[0]+2*H, F[1]+H/2), F[2]+H/2
    Bmax = np.asarray(outer_hoop)/(2*R)
    E0 = -(2*a+c)/3
    Qmax, Emax = R*Bmax-a, E0+(R-1)*Bmax
    required = a > 0
    allowed_product = np.maximum(Qmax, 0.)*np.maximum(Emax, 0.)
    needed_product = coefficient**2*np.asarray(current_per_root_energy)**2*Bmax
    excess = needed_product-allowed_product
    applicable = required & (E0 >= 0)
    rejected = required & ((Qmax < 0) | (Emax < 0) | (applicable & (excess > 1e-12)))
    upper = np.full_like(a, np.inf)
    np.divide(allowed_product, np.asarray(current_per_root_energy)**2*Bmax,
              out=upper, where=applicable & (Bmax > 0))
    return dict(a=a, field_cap=Bmax, applicable=applicable, rejected=rejected,
                product_excess=excess, coefficient_upper=np.sqrt(upper),
                self_closed_end_gap=a-(R-1)*Bmax)


def pointwise_particle_search(target, floor, inner_hoop, outer_hoop, geom,
                             coefficient, *, field_steps=161, speed_steps=161):
    """Construct witnesses; search failure is distinct from a proved bound.

    At each point select equal drift magnitudes for both new current path
    families. Their inventories can differ between times in this search.
    A separate replay below restores conserved inventories.
    """
    base = allocate_field(target, floor, inner_hoop, outer_hoop,
                          np.zeros_like(inner_hoop), eta=geom["eta"])
    failed = base["shortfall"] > 1e-12
    energy = np.zeros_like(inner_hoop)
    drift = np.zeros_like(energy)
    if not failed.any():
        return dict(field_energy=energy, speed=drift, **base)
    T, fl = np.asarray(target)[:, failed], np.asarray(floor)[failed]
    hi, ho = np.asarray(inner_hoop)[failed], np.asarray(outer_hoop)[failed]
    j = geom["axial_current_per_root_energy"][failed]
    ratio = geom["return_to_axial_current_ratio"][failed]
    cap = ho/(2*annular_factor(geom["eta"]))
    best = base["shortfall"][failed].copy()
    Bbest, vbest = np.zeros_like(best), np.zeros_like(best)
    # Log spacing resolves the relativistic drift region as well as slow flow.
    speeds = np.sqrt(1-np.geomspace(1e-6, .99, speed_steps))
    for fraction in np.linspace(0, 1, field_steps)[1:]:
        B = fraction*cap
        J = j*np.sqrt(B)
        for speed in speeds:
            Ea = coefficient*J/(speed*np.sqrt(1-speed*speed))
            Er = Ea*ratio
            trial = allocate_field(T, fl, hi, ho, B, eta=geom["eta"],
                carrier_energy=Ea+Er, carrier_axial_pressure=Ea*speed*speed,
                return_pressure=Er*speed*speed)
            better = trial["shortfall"] < best
            best = np.minimum(best, trial["shortfall"])
            Bbest = np.where(better, B, Bbest)
            vbest = np.where(better, speed, vbest)
    energy[failed], drift[failed] = Bbest, vbest
    currents = field_interfaces(energy, geom)
    Ea = np.divide(coefficient*currents["axial_current_integral"],
                   drift*np.sqrt(1-drift*drift), out=np.zeros_like(drift), where=drift > 0)
    Er = Ea*geom["return_to_axial_current_ratio"]
    result = allocate_field(target, floor, inner_hoop, outer_hoop, energy, eta=geom["eta"],
        carrier_energy=Ea+Er, carrier_axial_pressure=Ea*drift*drift,
        return_pressure=Er*drift*drift)
    return dict(field_energy=energy, speed=drift, **result)


def controlled_material_history(facets, inner_hoop, outer_hoop, lr, lt, *, eta=1.01):
    """Whole-history LP with five fixed material populations per label.

    Fixed longitudinal sheets scale as lr*lt, hoop strings as lt, and
    transverse sheets as lt**2. Opposed hoop photons lower boundary tension.
    Isotropic in-plane photons lower both transverse sheet tensions equally.
    Field energy B(t) remains driven. The new field's currents and all end
    fixtures are free in this optimistic history test. Positive optimum is
    therefore an obstruction for this family even before those costs.

    The six LP variables are Wi0, Ki0, Wo0, Ko0, A0, uniform energy deficit.
    Eliminating each B(t) gives exact linear inequalities, retaining every
    sampled time. The emitted history uses the smallest allowed B(t).
    """
    F, hi, ho, lr, lt = map(np.asarray, (facets, inner_hoop, outer_hoop, lr, lt))
    if (hi.ndim != 1 or ho.shape != hi.shape or lr.shape != hi.shape or lt.shape != hi.shape
            or F.shape != (3, hi.size) or np.any(hi < 0) or np.any(ho < 0)
            or np.any(lr <= 0) or np.any(lt <= 0)
            or not all(np.isfinite(x).all() for x in (F, hi, ho, lr, lt))):
        raise ValueError("one label's finite time history required")
    R, H, n = annular_factor(eta), hi+ho, hi.size
    v = np.zeros((5, n, 6))
    for i, stretch in enumerate((lr*lt, lt, lr*lt, lt, lt*lt)):
        v[i, :, i] = stretch
    wi, ki, wo, ko, A = v
    W, K = wi+wo, ki+ko
    deficit = np.zeros((n, 6))
    deficit[:, -1] = 1
    matrix = np.concatenate([wi, -wi-ki, wo, -wo-ko-2*A,
        3*W+2*K+3*A-deficit, 3*W+2*K+3*A-deficit,
        2*K+3*A-deficit, 2*K+3*A-3/(2*R)*(wo+ko)-deficit])
    rhs = np.concatenate([hi, -hi, ho, -ho, -F[0], -F[1]+1.5*H,
                          -F[2]+1.5*H, -F[2]+1.5*H-3*ho/(2*R)])
    objective = np.array([0., 0., 0., 0., 0., 1.])
    lp = linprog(objective, A_ub=matrix, b_ub=rhs,
                 bounds=[(0., None)]*5+[(None, None)], method="highs",
                 options={"primal_feasibility_tolerance": 1e-10,
                          "dual_feasibility_tolerance": 1e-10})
    if not lp.success:
        raise ValueError(f"Material-history LP failed: {lp.message}")
    passive = np.einsum("itj,j->it", v, lp.x)
    Wi, Ki, Wo, Ko, Aenergy = passive
    B = np.maximum((ho-Wo-Ko)/(2*R), 0.)
    M = R*B
    photons = np.stack([Wi+Ki-hi, Wo+Ko-ho+2*M, 2*(Aenergy-M)])
    energies = np.concatenate([passive, photons, B[None]])
    # The primal/dual pair supplies an independent lower certificate on the
    # uniform deficit, in addition to reconstructing all tensor constraints.
    dual = float(rhs @ lp.ineqlin.marginals)
    stationarity = matrix.T @ lp.ineqlin.marginals+lp.lower.marginals-objective
    return dict(initial_populations=lp.x[:5], energy=energies,
                tensor_trace=EVOLUTION_BASIS @ energies,
                shortfall=float(lp.fun), dual_lower_bound=dual,
                dual_stationarity_error=float(np.max(np.abs(stationarity))),
                maximum_primal_violation=float(np.max(matrix @ lp.x-rhs)),
                minimum_dual_bound_slack=float(np.min(lp.lower.marginals)),
                maximum_dual_inequality_multiplier=float(np.max(lp.ineqlin.marginals)))


def reservoir_interval(panel_exchange, available_energy):
    """Count a pressureless control store once within the available reserve.

    The proposed store receives the negative of every component exchange.
    A constant initial store energy exists exactly when lower <= upper.
    This is a capacity test; it grants lossless transfer and zero hardware
    cost, and supplies no rate or entropy capacity.
    """
    Q, cap = np.asarray(panel_exchange), np.asarray(available_energy)
    if Q.shape != (cap.shape[0]-1,)+cap.shape[1:]:
        raise ValueError("panel exchanges and state reserves must agree")
    cumulative = np.concatenate([np.zeros_like(cap[:1]), np.cumsum(Q, axis=0)])
    lower, upper = cumulative.max(axis=0), (cumulative+cap).min(axis=0)
    return dict(lower_initial_energy=lower, upper_initial_energy=upper,
                capacity_gap=lower-upper, cumulative_exchange=cumulative,
                store_energy=lower-cumulative)
