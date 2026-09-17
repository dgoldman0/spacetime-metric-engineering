"""Finite-radius diagnostics for the classical fermionic string candidates.

The exterior WKB action integrates a constant-mass centrifugal barrier.
It is a semiclassical exponent diagnostic, not a decay-rate certificate.
The local-string Dirac spectrum, occupied sources and time-dependent
curvature require separate calculation.
"""
import numpy as np
from scipy.optimize import brentq


def exterior_barrier_exponent(energy, mass, loop_radius, core_radius=0., *, mode_number=None):
    """2 int_Rout^Rturn sqrt(n^2/r^2-(E^2-m^2)) dr.

    Exterior mass is constant at the supplied value from R+core_radius
    outward. E<=mass has no energetically open free-particle channel and
    returns infinity. The default n=E*R describes a frozen massless loop
    mode. Separate E and n allow an instantaneous radial-motion comparison.
    Radius and mass use reciprocal natural units.
    """
    E, m, R, width = np.broadcast_arrays(*map(lambda a: np.asarray(a, float),
        (energy, mass, loop_radius, core_radius)))
    if (not all(np.isfinite(x).all() for x in (E, m, R, width))
            or np.any(E <= 0) or np.any(m <= 0) or np.any(R <= 0) or np.any(width < 0)):
        raise ValueError("positive energy, mass, radius and nonnegative core width required")
    n = E*R if mode_number is None else np.asarray(mode_number, float)
    E, m, R, width, n = np.broadcast_arrays(E, m, R, width, n)
    if not np.isfinite(n).all() or np.any(n <= 0):
        raise ValueError("positive finite orbital mode number required")
    ratio = m/E
    z = np.sqrt(np.maximum(E*E-m*m, 0))*(R+width)/n
    closed = ratio >= 1
    barrier = (~closed) & (z < 1)
    root = np.sqrt(np.maximum(1-z*z, 0))
    # arccosh(1/z)=atanh(sqrt(1-z^2)); series avoids cancellation
    # near the turning point. The positive tail is truncated at tiny root.
    series = root**3*(1/3+root*root*(1/5+root*root*(1/7+root*root/9)))
    with np.errstate(divide="ignore", invalid="ignore"):
        action = np.where(root < .01, series, np.arctanh(root)-root)
    result = np.where(closed, np.inf, np.where(barrier, 2*n*action, 0.))
    return float(result) if result.ndim == 0 else result


def required_loop_radius(tension_factor, scalar_radius_rho, *, yukawa=1.,
        gauge_coupling=1., stretch=1.17, scalar_fraction=.99,
        maximum_width_fraction=.01, target_exponent=100., minimum_mode_number=100.,
        lab_fermi_energy_over_sqrt_mu=None, radial_speed_bound=0.):
    """Radius in 1/sqrt(mu) for an instantaneous exterior diagnostic.

    The envelope uses n=E*R/gamma_max. At fixed radial gamma the action
    decreases with E: its integrand derivative has the sign of
    (R/(gamma*r))**2-1. Increasing gamma also decreases the action.
    Thus independent upper bounds on E and |v_r| enclose the instantaneous
    comparisons. Evolving-background transition rates remain separate.
    """
    B, rho, g, e, lam, fraction, epsilon, target, nmin = map(float,
        (tension_factor, scalar_radius_rho, yukawa, gauge_coupling, stretch,
         scalar_fraction, maximum_width_fraction, target_exponent, minimum_mode_number))
    if (not all(np.isfinite(v) and v > 0 for v in (B, rho, g, e, lam, epsilon, target, nmin))
            or not 0 < fraction < 1 or epsilon >= 1):
        raise ValueError("positive scales and fractional core/curvature limits required")
    E = (np.sqrt(2*np.pi)/lam if lab_fermi_energy_over_sqrt_mu is None
         else float(lab_fermi_energy_over_sqrt_mu))
    if not np.isfinite(E) or E <= 0:
        raise ValueError("positive lab-frame Fermi energy required")
    speed = float(radial_speed_bound)
    if not np.isfinite(speed) or not 0 <= speed < 1:
        raise ValueError("radial speed bound must lie in [0,1)")
    inverse_gamma = np.sqrt(1-speed*speed)
    m = g/np.sqrt(np.pi*B)
    width = rho*np.sqrt(np.pi*B)/e
    if E > fraction*m and E*speed >= fraction*m:
        raise ValueError("no exterior barrier survives the selected energy/speed envelope")
    lower = max(width/epsilon, nmin/(E*inverse_gamma))
    def excess(R):
        return exterior_barrier_exponent(E, fraction*m, R, width,
                                         mode_number=E*R*inverse_gamma)-target
    radius = lower
    if excess(lower) < 0:
        upper = 2*lower
        for _ in range(100):
            if excess(upper) >= 0:
                break
            upper *= 2
        else:
            raise RuntimeError("Unable to bracket the requested WKB diagnostic")
        radius = brentq(excess, lower, upper, rtol=2e-13)
    exponent = excess(radius)+target
    return dict(required_radius_sqrt_mu=radius, scalar_core_radius_sqrt_mu=width,
        core_over_loop_radius=width/radius, fermi_momentum_over_sqrt_mu=E,
        bulk_mass_over_sqrt_mu=m, fermi_over_bulk_mass=E/m,
        exterior_mass_fraction=fraction, semiclassical_mode_number=E*radius*inverse_gamma,
        radial_speed_bound=speed, radial_lorentz_factor=1/inverse_gamma,
        exterior_channel_energetically_open=bool(E > fraction*m),
        exterior_wkb_exponent=float(exponent) if np.isfinite(exponent) else None,
        target_exponent=target, minimum_mode_number=nmin,
        yukawa_loop_size=g*g/(16*np.pi*np.pi))


def rotor_lab_fermi_bound(*, maximum_energy=1.32, radius_error=.01140):
    """Largest forward branch energy from the certified rotor rectangle.

    The radial-comoving energy is sqrt(2*pi)*(1+j)/x; laboratory energy
    has an extra radial gamma. Since
    gamma_r=2*h*x/(x*x+1+j*j+2*b), the lab energy divided by sqrt(2*pi)
    is 2*h*(1+j)/(x*x+1+j*j+2*b). On this rectangle its j derivative
    is positive: x*x+1+2*b-2*j-j*j>0. Its maximum is at b=0 and at
    the largest allowed j, where gamma_r=1 and
    j*j=h*h-w*w-1. That envelope increases with h and decreases with w.
    """
    h, w = float(maximum_energy), float(radius_error)
    if (not np.isfinite([h, w]).all() or not 1.08 <= h <= 1.32 or not 0 <= w <= .012):
        raise ValueError("energy and radial error must lie in the certified rectangle")
    j = np.sqrt(h*h-w*w-1)
    x = h-w
    return dict(fermi_energy_over_sqrt_mu=np.sqrt(2*np.pi)*(1+j)/x,
                spin=j, radius=x, proper_stretch=x/np.sqrt(1-j*j),
                maximum_energy=h, radius_error=w)


def required_node_action(radius_sqrt_mu, *, inventory=19., radius_fraction=1/(12*np.pi),
                         minimum_radius_factor=1.068, replicas=6):
    """Minimum C_node*delta/hbar for equal microscopic rotor copies.

    A copy has relaxed M=inventory*C_node/replicas and L0=2*pi*R0.
    Hence mu=M/(4*pi*R0), and
    (Rmin*sqrt(mu))^2=xmin^2*inventory*radius_fraction*Q/(4*pi*replicas).
    Converting C_node to an actual energy needs a representative physical
    cell volume if the inherited ledger is expressed as an energy density.
    """
    radius = np.asarray(radius_sqrt_mu, float)
    if (not np.isfinite(radius).all() or np.any(radius <= 0)
            or not all(np.isfinite(v) and v > 0 for v in (inventory, radius_fraction, minimum_radius_factor))
            or not isinstance(replicas, int) or replicas < 1):
        raise ValueError("positive radius, inventory, geometry and integer replica count required")
    return 4*np.pi*replicas*radius*radius/(minimum_radius_factor**2*inventory*radius_fraction)
