"""Independent integral balances and the retained interior Einstein remainder."""
import numpy as np
from scipy.integrate import simpson

from .condensate_joint import physical_parameters
from .screened_condensate import field_stress


def integral_audit(solution, geometry, material, points=32001):
    setup = geometry.parameters
    gravity, clock, omega = physical_parameters(solution.p, setup, material)
    t = np.linspace(0., 1., points)
    y = solution.sol(t)
    r = setup.inner_radius+(setup.exterior_extent-setup.inner_radius)*t
    f, sigma = 1-2*y[6]/r, np.exp(y[7])
    outer = field_stress(y[:6], omega, material, f, sigma)
    rc, ac, rlog, alog = geometry.values(t)
    core = field_stress(y[8:], omega, material, 1., clock*ac)
    v = setup.vacuum_scale
    dsdt = v*geometry.length
    outer_volume = 4*np.pi*r*r/np.sqrt(f)*(setup.exterior_extent-setup.inner_radius)
    core_volume = 4*np.pi*(v*rc)**2*dsdt
    sums = {key: simpson(outer_volume*outer[key]+core_volume*core[key], x=t)
            for key in ['energy', 'matter_number', 'matter_charge', 'higgs_charge']}
    far_flux = 4*np.pi*(r[-1]**2*y[5, -1]/sigma[-1]+(v*rc[-1])**2*y[13, -1]/(clock*ac[-1]))
    mass_integral = 4*np.pi*gravity*simpson(r*r*outer['energy'], x=r)
    killing_energy = simpson(outer_volume*sigma*np.sqrt(f)*outer['energy']+
                            core_volume*clock*ac*core['energy'], x=t)
    dt = t[1]-t[0]
    pr = core['radial_pressure']
    dp = (pr[:-4]-8*pr[1:-3]+8*pr[3:-1]-pr[4:])/(12*dt*dsdt)
    force = -alog/v*(core['energy']+pr)+2*rlog/v*(core['tangential_pressure']-pr)
    force_error = np.max(abs(dp-force[2:-2]))/np.max(abs(force[2:-2]))
    u, h = y[8], y[10]
    # Ignore roundoff-scale tails when counting resolved sign changes.
    h_active = h[abs(h) > 1e-5]
    return {'quadrature_points': points, 'matter_number': sums['matter_number'],
        'matter_charge': sums['matter_charge'], 'higgs_charge': sums['higgs_charge'],
        'net_charge_fraction': abs(sums['matter_charge']+sums['higgs_charge'])/abs(sums['matter_charge']),
        'gauss_integral_error': abs(sums['matter_charge']+sums['higgs_charge']+far_flux)/abs(sums['matter_charge']),
        'far_electric_flux_fraction': abs(far_flux)/abs(sums['matter_charge']),
        'exterior_mass_integral_error': abs(mass_integral/(y[6, -1]-y[6, 0])-1),
        'core_force_conservation_error': force_error,
        'material_proper_energy_rail_units': gravity/v*sums['energy'],
        'material_killing_energy_rail_units': gravity/v*killing_energy,
        'minimum_matter_field': np.min(u), 'minimum_higgs_field': np.min(h),
        'resolved_higgs_sign_changes': int(np.count_nonzero(h_active[1:]*h_active[:-1] < 0)),
        'inner_electric_normal_derivative': y[13, 0],
        'inner_electric_flux': 4*np.pi*setup.inner_radius**2*y[5, 0]/sigma[0]}


def required_tensor(geometry, t):
    """Static Einstein tensor / 8pi in the physical proper-distance chart."""
    s = np.asarray(t)*geometry.length
    r = np.exp(geometry._r(s))
    dr, ddr = geometry._r(s, 1), geometry._r(s, 2)
    da, dda = geometry._a(s, 1), geometry._a(s, 2)
    return np.array([(1/r**2-3*dr**2-2*ddr)/(8*np.pi),
        (-1/r**2+dr**2+2*dr*da)/(8*np.pi),
        (dda+da**2+da*dr+ddr+dr**2)/(8*np.pi)])


def remainder_profile(solution, geometry, material, retained, points=2049):
    radius = np.linspace(2.15, 6.25, points)
    x = retained.negative_branch_coordinate(radius)
    t = geometry.fraction_at_coordinate(x)
    gravity, clock, omega = physical_parameters(solution.p, geometry.parameters, material)
    fields = solution.sol(t)[8:]
    _, a, _, _ = geometry.values(t)
    stress = field_stress(fields, omega, material, 1., clock*a)
    scale = gravity*geometry.parameters.vacuum_scale**2
    demanded = required_tensor(geometry, t)
    channels = ['energy', 'radial_pressure', 'tangential_pressure']
    result = {'radius': radius, 'coordinate': x}
    for i, channel in enumerate(channels):
        result['required_'+channel] = demanded[i]
        result['material_'+channel] = scale*stress[channel]
        result['remainder_'+channel] = demanded[i]-scale*stress[channel]
    for prefix in ['required_', 'material_', 'remainder_']:
        result[prefix+'radial_enthalpy'] = result[prefix+'energy']+result[prefix+'radial_pressure']
        result[prefix+'angular_enthalpy'] = result[prefix+'energy']+result[prefix+'tangential_pressure']
    return result
