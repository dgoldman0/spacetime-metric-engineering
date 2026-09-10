"""Source compatibility and dimensional requirements of the prepared reservoir.

Local field decomposition is an orientation-averaged constitutive witness.
Global magnetic flux closure, confinement, and current carriers are separate
source contributions. A negative remainder measures a required source; it
does not impose an assumed universal quantum-energy ceiling.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from .elastic_endpoint_reservoir import ElasticDomainError

C_LIGHT = 299792458.
G_NEWTON = 6.67430e-11
MU_ZERO = 1.25663706212e-6


def radial_null(moments):
    """T(k,k) for k=(1,+/-1,0,0), with moments (rho,p_r,j,p_t)."""
    rho, pressure, current, _ = np.asarray(moments)
    return np.array([rho+pressure-2*current, rho+pressure+2*current])


def boost_radial(rest_energy, radial_pressure, angular_pressure, velocity):
    v = np.asarray(velocity)
    gamma2 = 1/(1-v*v)
    enthalpy = rest_energy+radial_pressure
    return np.array([enthalpy*gamma2-radial_pressure,
                     enthalpy*gamma2*v*v+radial_pressure,
                     enthalpy*gamma2*v, np.broadcast_to(angular_pressure, v.shape)])


def field_decomposition(patch, t, state):
    """Split the archived rod tensor into transverse field, string, and buffer.

The radial string has p_r=-rho and p_t=0. Equal transverse magnetic
orientation energies have p_r=rho and mean p_t=0. Flux freezing gives
B_perp proportional to 1/(R B Gamma h), exactly the rod's quadratic
compression energy. This local equality supplies no global return geometry.
"""
    f = patch.fields(t, state)
    g, gamma, volume = f['metric'], f['gamma'], f['volume']
    area_factor = patch.law.scale/g.radius**2
    magnetic = area_factor*f['a']/(g.b*gamma**2*volume)
    string = area_factor*.5*patch.backbone_scale*np.ones_like(volume)
    rest_mass = area_factor*patch.mass/(g.b*gamma*volume)
    buffer = rest_mass*(patch.buffer_mass+f['heat'])
    moments = boost_radial(buffer+magnetic+string, magnetic-string,
                           np.zeros_like(volume), f['velocity'])
    archived = area_factor*np.array([f['energy_int'], f['radial_int'],
                                    f['current_int'], np.zeros_like(volume)])/volume
    denominator = buffer+2*magnetic
    return dict(fields=f, moments=moments, magnetic=magnetic, string=string,
                rest_mass=rest_mass, buffer=buffer,
                sigma=2*magnetic/buffer, fast_speed2=2*magnetic/denominator,
                extra_enthalpy_at_speed_half=6*magnetic-buffer,
                decomposition_absolute_error=float(np.max(abs(moments-archived))))


def scale_coefficients(magnetic, energy_density, slice_energy):
    """T_model=G*T_SI*L^2/c^4; slice energy is a local slice integral.

This integral is not identified with asymptotic ADM mass or recoverable
electrical energy. L rescales the full dimensionless metric uniformly.
"""
    factor = C_LIGHT**4/G_NEWTON
    return dict(magnetic_tesla_metres=np.sqrt(2*MU_ZERO*factor*np.asarray(magnetic)),
                pressure_pascal_metres_squared=factor*np.asarray(energy_density),
                slice_energy_joules_per_metre=factor*np.asarray(slice_energy))


def taub_mathews_pressure(rest_mass_energy, heat_per_rest_mass):
    """Pressure if the buffers were an unconfined ideal relativistic gas.

TM: h=5*Theta/2+sqrt(9*Theta^2/4+1), with h-Theta=1+q.
This is a counterfactual equation-of-state audit, not an evolved replacement.
"""
    z = 1+np.asarray(heat_per_rest_mass)
    return np.asarray(rest_mass_energy)*(z*z-1)/(3*z)


def classical_completion_requirement(demand, supplied):
    """Minimum negative null contribution if all other additions obey NEC."""
    remainder = np.asarray(demand)-np.asarray(supplied)
    null_remainder = radial_null(remainder)
    return remainder, np.maximum(-null_remainder, 0.)


def minimize_initial_null_requirement(patch, demand, medium, *, minimum_sound_speed=.5):
    """Minimize the largest required negative radial-null remainder.

The equilibrium family and cellwise stiffness floor are exactly those of
the registered mechanical study. The endpoint and full active geometry
are retained. The scalar objective has geometrized stress units; it is
a measured requirement, with no assigned quantum-source allowance.
"""
    if not 0 <= minimum_sound_speed < 1:
        raise ValueError('sound-speed floor must lie in [0,1)')
    original = patch.backbone_weight.copy()
    try:
        patch.backbone_weight = np.zeros(patch.cells)
        base_residual = patch.fixed_motion_residual()
        base = field_decomposition(patch, 0., patch.initial())
        f, g = base['fields'], base['fields']['metric']
        cell_bg = np.array([g.b[:-1]*f['gamma'][:-1], g.b[1:]*f['gamma'][1:]])
        heat = np.array([f['heat'][:-1], f['heat'][1:]])
        ratio = minimum_sound_speed**2/(1-minimum_sound_speed**2)
        lower = np.maximum(1e-12, ratio*np.max(patch.reference[None, :]
                           *(patch.buffer_mass+heat)*f['width'][None, :]*cell_bg, axis=0))
        base_null = radial_null(base['moments'])
        matrices, null_columns = [], []
        for i in range(patch.cells):
            weights = np.zeros(patch.cells)
            weights[i] = 1.
            patch.backbone_weight = weights
            matrices.append(patch.fixed_motion_residual()-base_residual)
            moments = field_decomposition(patch, 0., patch.initial())['moments']
            null_columns.append((radial_null(moments)-base_null).ravel())
        matrix = np.array(matrices).T
        null_matrix = np.array(null_columns).T
        row_scale = np.maximum(np.maximum(np.max(abs(matrix), axis=1), abs(base_residual)), 1e-15)
        null_offset = (base_null+radial_null(medium)-radial_null(demand)).ravel()
        objective = np.r_[np.zeros(patch.cells), 1.]
        equalities = np.column_stack([matrix/row_scale[:, None], np.zeros(patch.cells-1)])
        inequalities = np.column_stack([null_matrix, -np.ones(null_matrix.shape[0])])
        result = linprog(objective, A_eq=equalities, b_eq=-base_residual/row_scale,
                         A_ub=inequalities, b_ub=-null_offset,
                         bounds=[(x, None) for x in lower]+[(0., None)], method='highs')
        if not result.success:
            raise ElasticDomainError('initial null-requirement optimization failed: '+result.message)
        patch.backbone_weight = result.x[:-1].copy()
        solved = field_decomposition(patch, 0., patch.initial())
        _, requirement = classical_completion_requirement(demand, medium+solved['moments'])
        primal_gap = float(abs(requirement.max()-result.fun))
        # SciPy's marginal sign conventions give the dual objective below.
        dual_objective = float(np.dot(-base_residual/row_scale, result.eqlin.marginals)
                               +np.dot(-null_offset, result.ineqlin.marginals)
                               +np.dot(np.r_[lower, 0.], result.lower.marginals))
        return dict(optimized_negative_null_requirement=float(result.fun),
                    measured_negative_null_requirement=float(requirement.max()),
                    maximum_equilibrium_residual=float(np.max(abs(patch.fixed_motion_residual()))),
                    minimum_cell_sound_speed=float(np.sqrt(solved['fields']['sound2'].min())),
                    initial_slice_energy=float(4*np.pi*solved['fields']['matter_adm'].sum()),
                    relative_weight_change=float(np.max(abs(patch.backbone_weight-original)
                                                        /np.maximum(abs(original), 1e-30))),
                    objective_measurement_error=primal_gap,
                    dual_objective=dual_objective,
                    primal_dual_gap=float(abs(result.fun-dual_objective)),
                    optimized_weights=patch.backbone_weight.tolist())
    finally:
        patch.backbone_weight = original
