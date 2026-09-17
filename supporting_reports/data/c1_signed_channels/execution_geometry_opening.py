"""Static opening gate on tabulated metric controls in their native chart.

The longitudinal quantum law and ordinary-aggregate assumption are those of
longitudinal_balance. Integrating the radius term by parts provides an
independent evaluation using first derivatives, with every endpoint retained.
"""
from dataclasses import dataclass

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize_scalar


@dataclass
class StaticSlice:
    coordinate: np.ndarray
    radius: np.ndarray
    lapse: np.ndarray
    radial_scale: np.ndarray

    def __post_init__(self):
        arrays = [np.asarray(a, float) for a in
                  (self.coordinate, self.radius, self.lapse, self.radial_scale)]
        if (any(a.ndim != 1 or not np.isfinite(a).all() for a in arrays)
                or any(a.shape != arrays[0].shape for a in arrays)
                or len(arrays[0]) < 5 or np.any(np.diff(arrays[0]) <= 0)
                or any(np.any(a <= 0) for a in arrays[1:])):
            raise ValueError('aligned finite positive metric on an increasing coordinate required')
        self.coordinate, self.radius, self.lapse, self.radial_scale = arrays
        self.splines = [CubicSpline(arrays[0], np.log(a)) for a in arrays[1:]]
        i = int(np.argmin(self.radius))
        if i in (0, len(self.radius)-1):
            raise ValueError('the opening comparison requires an interior throat')
        result = minimize_scalar(self.splines[0],
            bounds=(self.coordinate[i-1], self.coordinate[i+1]), method='bounded',
            options={'xatol': 1e-13})
        if not result.success:
            raise RuntimeError('throat location failed')
        self.throat_coordinate = float(result.x)
        self.throat_radius = float(np.exp(result.fun))

    def jets(self, coordinate):
        """R, A, B, R', R'', (log A)', (log A)''; primes are proper."""
        x = np.asarray(coordinate, float)
        if np.any(x < self.coordinate[0]) or np.any(x > self.coordinate[-1]):
            raise ValueError('requested coordinate lies outside the tabulated metric')
        r, a, b = [np.exp(s(x)) for s in self.splines]
        rx, ax, bx = [s(x, 1) for s in self.splines]
        rxx, axx = [s(x, 2) for s in self.splines[:2]]
        return r, a, b, r*rx/b, r*(rxx+rx*rx-bx*rx)/(b*b), ax/b, (axx-bx*ax)/(b*b)

    def quadrature(self, lower, upper, minimum_kappa, order=8):
        """Composite Gaussian quadrature with resolved small-k throat weight."""
        if not (self.coordinate[0] <= lower < self.throat_coordinate < upper <= self.coordinate[-1]):
            raise ValueError('an interior throat and endpoints inside the metric are required')
        if minimum_kappa <= 0 or not np.isfinite(minimum_kappa) or order < 2:
            raise ValueError('positive finite kappa and Gaussian order >= 2 required')
        x0, r0 = self.throat_coordinate, self.throat_radius
        # Coordinate width of the local Gaussian W near a nondegenerate throat.
        second = r0*(self.splines[0](x0, 2)+self.splines[0](x0, 1)**2)
        width = np.sqrt(minimum_kappa/max(r0*second, 1e-30))
        focus = np.linspace(max(lower, x0-12*width), min(upper, x0+12*width), 129)
        cuts = np.unique(np.r_[lower, self.coordinate[(self.coordinate > lower)
            & (self.coordinate < upper)], focus, upper])
        nodes, weights = leggauss(order)
        half = np.diff(cuts)/2
        x = ((cuts[:-1]+half)[:, None]+half[:, None]*nodes).ravel()
        weights = (half[:, None]*weights).ravel()
        return SliceQuadrature(x, weights, self.jets(x), self.jets(np.array([lower, upper])), r0)


@dataclass
class SliceQuadrature:
    coordinate: np.ndarray
    weights: np.ndarray
    fields: tuple
    endpoints: tuple
    reference_radius: float

    def integral(self, value):
        return float(np.dot(self.weights, value))

    def balance(self, kappa, optical_return=0.):
        """Compare first-derivative, curvature, and Einstein/CFT identities."""
        if kappa <= 0 or not np.isfinite(kappa) or optical_return < 0 or not np.isfinite(optical_return):
            raise ValueError('positive finite kappa and finite nonnegative return required')
        r, a, b, rp, rpp, ap, app = self.fields
        re, ae, be, rpe, rppe, ape, appe = self.endpoints
        w = np.exp(-(r*r-self.reference_radius**2)/(2*kappa))
        we = np.exp(-(re*re-self.reference_radius**2)/(2*kappa))
        optical_length = self.integral(b/a)+optical_return
        numerator = self.integral(w*b/(a*a))
        radial_endpoint = float(np.diff(we*re*rpe/kappa)[0])
        clock_endpoint = float(np.diff(we*ape)[0])
        # Integral W R R''/k = [W R R'/k] + integral W (R²/k²-1/k) R'².
        slope_demand = self.integral(w*b*(r*r/kappa-1)*rp*rp/kappa)
        required = radial_endpoint+clock_endpoint+slope_demand
        curvature_demand = self.integral(w*b*r*rpp/kappa)+clock_endpoint
        supply = 4*np.pi**2*numerator/optical_length**2
        h_geometry = (ap*rp-rpp)/(4*np.pi*r)
        h_quantum = kappa/(4*np.pi*r*r)*(app-4*np.pi**2/(optical_length*a)**2)
        direct = 4*np.pi/kappa*self.integral(w*b*r*r*(h_geometry-h_quantum))
        norm = max(abs(required), abs(supply), 1e-30)
        return dict(optical_length=optical_length, numerator=numerator,
            required=required, slope_demand=slope_demand,
            radial_endpoint=radial_endpoint, clock_endpoint=clock_endpoint,
            supply=supply, supply_over_required=supply/required if required > 0 else None,
            residual=supply-required,
            curvature_identity_error=abs(required-curvature_demand)/norm,
            einstein_cft_identity_error=abs(direct-(supply-required))/norm)

    def tensor_summary(self):
        r, a, b, rp, rpp, ap, app = self.fields
        rho = ((1-rp*rp)/(r*r)-2*rpp/r)/(8*np.pi)
        pr = (-(1-rp*rp)/(r*r)+2*ap*rp/r)/(8*np.pi)
        pt = (app+ap*ap+ap*rp/r+rpp/r)/(8*np.pi)
        volume = 4*np.pi*r*r*b
        return dict(minimum_density=float(rho.min()), minimum_radial_null=float((rho+pr).min()),
            minimum_angular_null=float((rho+pt).min()),
            negative_density_volume_integral=self.integral(volume*np.maximum(-rho, 0)),
            negative_radial_null_volume_integral=self.integral(volume*np.maximum(-rho-pr, 0)),
            absolute_angular_pressure_volume_integral=self.integral(volume*abs(pt)))
