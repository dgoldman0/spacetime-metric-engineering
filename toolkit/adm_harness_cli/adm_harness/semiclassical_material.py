"""Fixed-charge material block of the smooth semiclassical iteration."""
import numpy as np
from scipy.integrate import cumulative_simpson, solve_bvp
from scipy.interpolate import PchipInterpolator, make_interp_spline

from .condensate_joint import proper_matter_rhs
from .condensate_joint_audit import integral_audit
from .screened_condensate import field_stress


def relax_material(seed, source_proper, polarization, tolerance=2e-6, points=5001):
    """Solve material and charge equations at the registered physical couplings.

    The metric and quantum polarization form the other, frozen blocks of
    this alternating update. Their consistency is tested after recomputing
    the quantum state; a material-block solution alone is not a fixed point.
    """
    profile = seed.profile
    target = integral_audit(profile.solution, profile.core, profile.material)['matter_number']
    quantum = PchipInterpolator(source_proper, polarization, extrapolate=False)
    def phi(l):
        return np.nan_to_num(quantum(l), nan=0.)
    def rhs(l, fields, frequency):
        jets = seed.jets(l, 1)
        radius, lapse = np.exp(jets[0, 0]), np.exp(jets[0, 1])
        v = profile.v
        out = proper_matter_rhs(v*radius, lapse, jets[1, 0]/v, jets[1, 1]/v,
                               fields[:6], frequency[0], profile.material)
        out[3] += 1.4*fields[2]*phi(l)/(2*v*v)
        number = field_stress(fields[:6], frequency[0], profile.material,
                             1., lapse)['matter_number']
        return np.vstack((v*out, 4*np.pi*v**3*radius**2*number/target))
    def bc(left, right, frequency):
        return np.r_[left[[0, 2, 4]]-[0., 1., 0.], right[[0, 2, 4]]-[0., 1., 0.],
                     left[6], right[6]-1.]
    l = np.linspace(*seed.domain, points)
    initial = seed.state(l)[4:10]
    number_density = rhs(l, np.vstack((initial, np.zeros_like(l))), [profile.omega])[-1]
    number = cumulative_simpson(number_density, x=l, initial=0.)
    number /= number[-1]
    result = solve_bvp(rhs, bc, l, np.vstack((initial, number)), p=[profile.omega],
                       tol=tolerance, max_nodes=32000)
    checks = {'solver_success': bool(result.success), 'status': int(result.status),
              'nodes': len(result.x), 'target_matter_number': float(target),
              'frequency': float(result.p[0]), 'tolerance': tolerance}
    cells = np.diff(result.x)
    witness = np.r_[result.x[:-1]+.25*cells, result.x[:-1]+.75*cells]
    values = result.sol(witness)
    equation = rhs(witness, values, result.p)
    error = float(np.max(abs(result.sol(witness, 1)-equation)/(1+abs(equation))))
    checks['independent_equation_residual'] = error
    checks['boundary_residual'] = float(np.max(abs(bc(result.y[:, 0], result.y[:, -1], result.p))))
    checks['minimum_higgs'] = float(values[2].min())
    checks['maximum_field_change'] = float(np.max(abs(result.sol(l)[:6:2]-initial[::2])))
    checks['maximum_frequency_for_two_end_decay'] = float(np.sqrt(profile.material.matter_coupling)*
        min(seed.values(seed.domain)[1]))
    checks['accepted'] = bool(result.success and error < 5e-5 and checks['boundary_residual'] < 1e-7
        and 0 < result.p[0] < checks['maximum_frequency_for_two_end_decay'])
    return result, checks


class UpdatedMaterialSeed:
    """Keep the metric spline and install the relaxed material amplitudes."""
    def __init__(self, seed, proper, amplitudes):
        self.base, self.profile = seed, seed.profile
        self.domain = seed.domain
        self.coordinate_of_proper = seed.coordinate_of_proper
        self.proper_of_coordinate = seed.proper_of_coordinate
        self.material = make_interp_spline(proper, amplitudes, k=5, axis=1)

    def jets(self, proper, order=4):
        result = self.base.jets(proper, order)
        result[:, 2:] = np.array([self.material(proper, nu=n) for n in range(order+1)])
        return result

    def values(self, proper):
        r, a, _ = self.base.values(proper)
        h = self.material(proper)[1]
        return r, a, 1.4*self.profile.v**2*h*h

    def demanded_tensor(self, proper):
        return self.base.demanded_tensor(proper)
