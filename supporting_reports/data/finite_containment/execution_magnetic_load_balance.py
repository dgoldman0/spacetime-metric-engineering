"""Necessary tensor and energy tests for an attached magnetic heat reservoir.

The local capsule loop is affinely carried by diag(ell/ell0, R/R0, R/R0).
Its straight sections have initial length L each and its two semicircles
have radius a. Opposite tilts and azimuthal averaging cancel mixed stresses.
Radiation fills the complete tube. A common flux amplitude keeps magnetic
pressure above radiation pressure at the weakest part of the loop.

Units are c=mu0=1 for the electromagnetic/current calculation. The current
coefficient is m/abs(q) in the SAME field and stress normalization. It is
left as a parameter; no particle species or physical scale is assigned.
Auxiliary supports retain the existing field/radiation/membrane cone.
Spatial force closure, induction fields, opacity and constitutive evolution
are subsequent requirements, separate from these necessary comparisons.
"""
from __future__ import annotations

import numpy as np


def _positive_arrays(*values):
    arrays = np.broadcast_arrays(*[np.asarray(v, float) for v in values])
    if not all(np.isfinite(v).all() and np.all(v > 0) for v in arrays):
        raise ValueError("finite positive physical arrays required")
    return arrays


def radiation_inventory(initial, panel_heat, volume, mean_volume_root):
    """Integrate d(E V**(1/3)) = V**(1/3) dQ at fixed positive panel heat.

    mean_volume_root is the time mean of V**(1/3) on each panel. The
    prescribed gross receipts have constant rate within a replay panel.
    """
    volume, = _positive_arrays(volume)
    initial, heat, means = [np.asarray(v, float) for v in
                            (initial, panel_heat, mean_volume_root)]
    if (volume.ndim != 2 or volume.shape[0] < 2
            or initial.shape != volume.shape[1:]
            or heat.shape != (volume.shape[0]-1, volume.shape[1])
            or means.shape != heat.shape
            or not all(np.isfinite(v).all() for v in (initial, heat, means))
            or np.any(initial < 0) or np.any(heat < 0) or np.any(means <= 0)):
        raise ValueError("compatible nonnegative initial energy and panel heat required")
    root = volume**(1/3)
    start = initial*root[0]
    invariant = np.vstack([start, start+np.cumsum(heat*means, axis=0)])
    energy = invariant/root
    return dict(energy=energy, invariant=invariant,
                compression_work=np.diff(energy, axis=0)-heat,
                balance_residual=np.diff(invariant, axis=0)-heat*means)


def loop_field(energy, radial_stretch, transverse_stretch, *, aspect, angle,
               beta_limit=1.):
    """Full straight, return and bend magnetic energies per material label.

    aspect=a/L>0; angle is the initial straight-section tilt from radial.
    Radiation and field occupy the complete closed tube. Fields are the
    solenoidal affine image B=F B0/det(F), with a controlled common amplitude.
    The weakest tangent samples min(lambda_r**2, lambda_t**2) on the bends.
    """
    e, lr, lt = _positive_arrays(energy, radial_stretch, transverse_stretch)
    if (not np.isfinite([aspect, angle, beta_limit]).all() or aspect <= 0
            or not 0 <= angle <= np.pi/2 or beta_limit <= 0):
        raise ValueError("positive aspect/beta and tilt between zero and pi/2 required")
    delta = np.pi*aspect
    weight = (np.cos(angle)**2+delta/2)/(1+delta)
    weakest = np.minimum(lr*lr, lt*lt)
    radial = e/(3*beta_limit)*weight*lr*lr/weakest
    transverse = e/(3*beta_limit)*(1-weight)*lt*lt/weakest
    # Both energies include every part of the loop, including the bends.
    return dict(radial=radial, transverse=transverse, energy=radial+transverse,
                radial_pressure_energy=transverse-radial,
                angular_pressure_energy=radial,
                initial_radial_weight=weight, weakest_stretch_squared=weakest)


def support_cone(density, radial, angular, radial_field_floor=0.):
    """Exact positive component cone with a separately counted field floor.

    Components: radial B, opposed radial photons, angular photons,
    angular membrane, and pressureless inventory. Transverse B has exactly
    the same diagonal tensor as opposed radial photons.
    """
    rho, p, q, floor = np.broadcast_arrays(*[np.asarray(v, float) for v in
                                            (density, radial, angular, radial_field_floor)])
    if (not all(np.isfinite(v).all() for v in (rho, p, q, floor))
            or np.any(floor < 0)):
        raise ValueError("finite stresses and nonnegative field floor required")
    facets = np.stack([p+2*q-rho, p-q+3*floor-rho, -2*p-q-rho])
    field = np.maximum.reduce([floor, -p, np.zeros_like(p)])
    radial_wave = p+field
    angular_wave = 2*np.maximum(q-field, 0.)
    membrane = np.maximum(field-q, 0.)
    spare = rho-field-radial_wave-angular_wave-membrane
    return dict(facets=facets, shortfall=facets.max(axis=0),
                field=field, radial_wave=radial_wave, angular_wave=angular_wave,
                membrane=membrane, spare=spare)


def attached_bank(state, energy, field, *, reopened="cold", share_core=True,
                  carrier_tensor=None):
    """Replace one compact receiver by pressure-bearing plasma and its loop.

    Only that bank's max(reference energy)/3 enclosure credit is released.
    Both-bank replacement releases the original whole enclosure allowance.
    Core sharing grants overlap with its ALREADY counted radial B half.
    The other half of the phase, all photons, fluid, guide and interface
    obligations retain their original values.
    """
    keys = dict(cold="receiver_cold_energy", hot="receiver_hot_energy",
                both="receiver_thermal_energy")
    if reopened not in keys or not isinstance(share_core, (bool, np.bool_)):
        raise ValueError("registered receiver selection and Boolean core sharing required")
    D = state["D"]
    old = state[keys[reopened]]
    energy = np.asarray(energy, float)
    if (energy.shape != D.shape or not np.isfinite(energy).all()
            or np.any(energy < 0)):
        raise ValueError("matching nonnegative reservoir energy required")
    credit = (state["receiver_fixed_containment_energy"] if reopened == "both"
              else old.max(axis=0)/3)
    if np.any(credit > state["receiver_fixed_containment_energy"]+1e-10):
        raise ValueError("released enclosure exceeds counted original enclosure")
    phase = state["amplitude"]/state["radius"]**2
    wave, thermal, wall = (state[k] for k in
                           ("balanced_radiation_rest", "thermal_reservoir_rest", "wall_rest"))
    rho, p, q = state["credited_target"]
    overlap = np.minimum(field["radial"]/D, phase/2) if share_core else np.zeros_like(D)
    floor = np.maximum(state["guide_rest"], field["radial"]/D-overlap)
    transverse = field["transverse"]/D
    carrier = np.zeros((3,)+D.shape) if carrier_tensor is None else np.asarray(carrier_tensor, float)
    if carrier.shape != (3,)+D.shape or not np.isfinite(carrier).all():
        raise ValueError("matching finite carrier tensor required")
    rr = (rho-phase-wave-thermal-state["receiver_rest"]-wall
          +credit/D-(energy-old)/D-transverse-carrier[0])
    rp = p+phase-wave-thermal/3-energy/(3*D)-transverse-carrier[1]
    rq = q+wall-thermal/3-energy/(3*D)-carrier[2]
    result = support_cone(rr, rp, rq, floor)
    result.update(residual_target=np.stack([rr, rp, rq]),
                  radial_field_floor=floor, core_field_overlap=overlap,
                  released_enclosure_energy=credit, transverse_field_density=transverse)
    return result


def carrier_limit(facets, unit_tensor):
    """Exact admissible m/|q| for a fixed conserved-current-inventory choice."""
    rho, p, q = np.asarray(unit_tensor, float)
    slopes = np.stack([rho-p-2*q, rho-p+q, rho+2*p+q])
    if (slopes.shape != np.asarray(facets).shape or not np.isfinite(slopes).all()
            or np.any(slopes < -1e-12)):
        raise ValueError("compatible positive-cost carrier tensor required")
    bounds = np.full_like(slopes, np.inf)
    np.divide(-facets, slopes, out=bounds, where=slopes > 0)
    bounds[(slopes == 0) & (facets > 0)] = -np.inf
    return float(bounds.min()), slopes


def balance_pitch(state, energy, *, aspect, beta_limit=1., reopened="cold",
                  share_core=True):
    """Optimize ONE initial pitch across every archived time and label.

    With z=cos(angle)**2, all four support constraints are affine in z.
    Their scalar interval intersection covers the continuous pitch range.
    A bisection minimizes the signed uniform density shortfall.
    """
    D = state["D"]
    lr, lt = state["ell"]/state["ell"][0], state["radius"]/state["radius"][0]
    zero = dict(radial=np.zeros_like(D), transverse=np.zeros_like(D))
    base = attached_bank(state, energy, zero, reopened=reopened, share_core=share_core)
    rho, p, q = base["residual_target"]
    loop_field(energy, lr, lt, aspect=aspect, angle=0., beta_limit=beta_limit)
    delta = np.pi*aspect
    common = energy/(3*beta_limit*D*np.minimum(lr*lr, lt*lt)*(1+delta))
    ar, at = common*lr*lr, common*lt*lt
    overlap = state["amplitude"]/(2*state["radius"]**2) if share_core else 0.
    fixed = max(float((p+2*q-rho).max()),
                float((p-q+3*state["guide_rest"]-rho).max()))
    rising = p-q-rho-3*overlap+1.5*ar*delta
    falling = -2*p-q-rho+3*at*(1+delta/2)

    def interval(epsilon):
        lower = max(0., float(((falling-epsilon)/(3*at)).max()))
        upper = min(1., float(((epsilon-rising)/(3*ar)).min()))
        return lower, upper

    def objective(z):
        return max(fixed, float((rising+3*ar*z).max()),
                   float((falling-3*at*z).max()))

    low = fixed
    high = min(objective(0.), objective(1.))
    for _ in range(60):
        mid = .5*(low+high)
        lo, hi = interval(mid)
        if lo <= hi:
            high = mid
        else:
            low = mid
    lo, hi = interval(high+1e-14)
    chosen = np.clip(.5*(lo+hi), 0., 1.)
    admitted_lo, admitted_hi = interval(0.)
    return dict(angle=float(np.arccos(np.sqrt(chosen))),
                best_shortfall=objective(chosen),
                minimax_lower_bound=low,
                zero_allowance_cosine_squared_lower=admitted_lo,
                zero_allowance_cosine_squared_upper=admitted_hi,
                zero_allowance_pitch_exists=bool(fixed <= 0 and admitted_lo <= admitted_hi),
                unavoidable_fixed_facet=fixed)


def straight_sleeve(facets, energy, volume, radial_stretch, transverse_stretch,
                    *, aspect, angle, stress_fraction=1., beta_limit=1.):
    """Necessary mechanical sleeve cost for BOTH straight legs of the loop.

    The loop has zero exterior field. Its sidewall bears p_plasma+B**2/2.
    The two-dimensional transverse virial identity requires hoop energy
    H=2*(p_plasma+B**2/2)*V_straight. For a circular cross-section this is
    the thin hoop minimum; for a deformed section it is a favorable bound.
    H here is divided by the total material-label volume.

    A wall with allowable stress/energy k has rho_wall>=H/k and freely
    chosen integrated axial stress z with |z|<=k*rho_wall. Its transverse
    integrated pressures are fixed by hoop balance. All three remaining
    cone facets are checked. Bend material, finite thickness, end junctions
    and a constitutive law are omitted; passing remains a necessary test.
    """
    e, D, lr, lt = _positive_arrays(energy, volume, radial_stretch, transverse_stretch)
    if (not np.isfinite(stress_fraction) or not 0 < stress_fraction <= 1
            or np.asarray(facets).shape != (3,)+e.shape):
        raise ValueError("matching cone facets and stress fraction in (0,1] required")
    loop_field(e, lr, lt, aspect=aspect, angle=angle, beta_limit=beta_limit)
    tangent = lr*lr*np.cos(angle)**2+lt*lt*np.sin(angle)**2
    radial_fraction = lr*lr*np.cos(angle)**2/tangent
    hoop = 2*e/(3*D*(1+np.pi*aspect))*(
        1+tangent/(beta_limit*np.minimum(lr*lr, lt*lt)))
    f = radial_fraction
    offsets = facets+np.stack([hoop, hoop*(1-3*f)/4, -hoop*(5-3*f)/4])
    slope = np.stack([-np.ones_like(f), (1-3*f)/2, (1+3*f)/2])
    # Convex piecewise linear objective: max_i(offset_i+slope_i*z)
    # + max(H,abs(z))/k. Its minima occur at a kink or an intersection.
    candidates = [-hoop, hoop, np.zeros_like(hoop)]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        denominator = slope[j]-slope[i]
        candidates.append(np.divide(offsets[i]-offsets[j], denominator,
                          out=np.zeros_like(hoop), where=abs(denominator) > 1e-14))
    best = np.full_like(hoop, np.inf)
    chosen = np.zeros_like(hoop)
    for z in candidates:
        density = np.maximum(hoop, abs(z))/stress_fraction
        value = np.max(offsets+slope*z, axis=0)+density
        improve = value < best
        best = np.where(improve, value, best)
        chosen = np.where(improve, z, chosen)
    density = np.maximum(hoop, abs(chosen))/stress_fraction
    radial = -.5*hoop*(1-f)+chosen*f
    angular = -.25*hoop*(1+f)+.5*chosen*(1-f)
    return dict(shortfall=best, tensor=np.stack([density, radial, angular]),
                hoop_energy_floor=hoop, axial_stress=chosen,
                radial_tangent_fraction=f)


def conserved_sleeve_interval(facets, volume, hoop, radial_fraction, *,
                              stress_fraction=1.):
    """Project a fixed sleeve energy M per label through all time samples.

    rho_wall=M/D. Its axial stress is independently free at every sample,
    |z|<=k M/D, and its hoop load requires M>=D H/k. Fourier elimination
    of z gives an exact interval for M. This is a fixed-energy material
    comparison; a wall storing/releasing elastic energy has another law.
    """
    D, = _positive_arrays(volume)
    H, f = np.asarray(hoop, float), np.asarray(radial_fraction, float)
    facets = np.asarray(facets, float)
    k = stress_fraction
    if (D.ndim != 2 or H.shape != D.shape or f.shape != D.shape
            or facets.shape != (3,)+D.shape
            or not all(np.isfinite(v).all() for v in (H, f, facets))
            or np.any(H < 0) or np.any((f < 0) | (f > 1))
            or not np.isfinite(k) or not 0 < k <= 1):
        raise ValueError("compatible physical sleeve arrays and stress fraction required")
    offsets = facets+np.stack([H, H*(1-3*f)/4, -H*(5-3*f)/4])
    beta = np.stack([-np.ones_like(f), (1-3*f)/2, (1+3*f)/2,
                     np.ones_like(f), -np.ones_like(f)])
    alpha = np.stack([1/D, 1/D, 1/D, -k/D, -k/D])
    rhs = np.concatenate([-offsets, np.zeros((2,)+D.shape)])
    lower = D*H/k
    upper = np.full_like(D, np.inf)
    impossible = np.zeros_like(D, dtype=bool)

    def impose(a, b, mask):
        nonlocal lower, upper, impossible
        positive, negative = mask & (a > 1e-14), mask & (a < -1e-14)
        quotient = np.divide(b, a, out=np.zeros_like(D), where=positive | negative)
        upper = np.where(positive, np.minimum(upper, quotient), upper)
        lower = np.where(negative, np.maximum(lower, quotient), lower)
        impossible |= mask & ~(positive | negative) & (b < -1e-12)

    for i in range(5):
        impose(alpha[i], rhs[i], abs(beta[i]) <= 1e-14)
    for lo in range(5):
        for hi in range(5):
            mask = (beta[lo] < -1e-14) & (beta[hi] > 1e-14)
            low_a = np.divide(alpha[lo], beta[lo], out=np.zeros_like(D), where=mask)
            high_a = np.divide(alpha[hi], beta[hi], out=np.zeros_like(D), where=mask)
            low_b = np.divide(rhs[lo], beta[lo], out=np.zeros_like(D), where=mask)
            high_b = np.divide(rhs[hi], beta[hi], out=np.zeros_like(D), where=mask)
            impose(high_a-low_a, high_b-low_b, mask)
    lower_index, upper_index = np.argmax(lower, axis=0), np.argmin(upper, axis=0)
    columns = np.arange(D.shape[1])
    lo, hi = lower[lower_index, columns], upper[upper_index, columns]
    valid = (lo <= hi) & ~impossible.any(axis=0)
    return dict(lower=lo, upper=hi, feasible=valid,
                lower_time_index=lower_index, upper_time_index=upper_index,
                minimum_gap=float(np.min(hi-lo)),
                local_impossibility=impossible.any(axis=0))


def sleeve_at_inventory(facets, volume, hoop, radial_fraction, inventory, *,
                        stress_fraction=1.):
    """Choose a permissible axial stress for a specified conserved sleeve."""
    D = np.asarray(volume, float)
    H, f, M = map(lambda v: np.asarray(v, float), (hoop, radial_fraction, inventory))
    interval = conserved_sleeve_interval(facets, D, H, f, stress_fraction=stress_fraction)
    if (M.shape != (D.shape[1],) or not np.isfinite(M).all()
            or np.any(M < interval["lower"]-1e-12)
            or np.any(M > interval["upper"]+1e-12) or not interval["feasible"].all()):
        raise ValueError("conserved sleeve inventory outside the common interval")
    density = M/D
    offsets = facets+np.stack([H, H*(1-3*f)/4, -H*(5-3*f)/4])+density
    slopes = np.stack([-np.ones_like(f), (1-3*f)/2, (1+3*f)/2])
    lower, upper = -stress_fraction*density, stress_fraction*density
    for a, b in zip(offsets, slopes):
        bound = np.divide(-a, b, out=np.zeros_like(a), where=abs(b) > 1e-14)
        lower = np.where(b < -1e-14, np.maximum(lower, bound), lower)
        upper = np.where(b > 1e-14, np.minimum(upper, bound), upper)
    z = .5*(lower+upper)
    tensor = np.stack([density, -.5*H*(1-f)+z*f,
                       -.25*H*(1+f)+.5*z*(1-f)])
    return dict(tensor=tensor, axial_stress=z,
                axial_interval_violation=float(np.max(lower-upper)))


def loop_currents(energy, volume, radial_stretch, transverse_stretch, leg0, *,
                  aspect, angle, fill_fraction=.1, tube_ratio=.1, beta_limit=1.,
                  order=16, batch=64):
    """Sheet and volume current integrals for a thin affinely deformed tube.

    The initial circular tube radius is tube_ratio*a. A tube ensemble fills
    fill_fraction of the local volume. |K|=|B| on the tube boundary, while
    curvature supplies a distributed binormal current inside each bend.
    The integral is per material label; no current return is discarded.

    Opposite charges with opposite drift cancel electric charge and momentum.
    Each family has conserved rest inventory sqrt(2)*max_t integral|J| at
    unit m/|q|. Consequently its drift remains <=1/sqrt(2). Redistribution
    of carriers along the tube and the stresses of their hosts remain open.
    """
    e, D, lr, lt = _positive_arrays(energy, volume, radial_stretch, transverse_stretch)
    leg0 = np.asarray(leg0, float)
    if (e.ndim != 2 or leg0.shape != (e.shape[1],) or np.any(leg0 <= 0)
            or not np.isfinite(leg0).all() or not 0 < fill_fraction <= 1
            or not 0 < tube_ratio < 1 or not isinstance(order, int) or order < 4
            or not isinstance(batch, int) or batch < 1):
        raise ValueError("physical tube, fill, quadrature and label dimensions required")
    loop_field(e, lr, lt, aspect=aspect, angle=angle, beta_limit=beta_limit)
    jacobian = lr*lt*lt
    if not np.allclose(D/D[0], jacobian, rtol=1e-10, atol=1e-12):
        raise ValueError("volume must follow the registered affine stretches")
    a0, r0 = aspect*leg0, tube_ratio*aspect*leg0
    length0 = 2*leg0+2*np.pi*a0
    volume0 = fill_fraction*D[0]
    amplitude = np.sqrt(2*e*jacobian/(3*beta_limit*volume0*np.minimum(lr*lr, lt*lt)))
    # Midpoint periodic quadrature avoids duplicate endpoints. Full circles
    # make the signed curvature correction integrate to zero.
    phi = 2*np.pi*(np.arange(order)+.5)/order
    psi = 2*np.pi*(np.arange(order)+.5)/order
    angles = np.r_[angle, phi]
    sheet = np.empty_like(e)
    radial_fraction = np.empty_like(e)
    for begin in range(0, len(e), batch):
        sl = slice(begin, begin+batch)
        radial_sum = np.zeros_like(e[sl]); total = np.zeros_like(radial_sum)
        for i, tangent in enumerate(angles):
            co, si = np.cos(tangent), np.sin(tangent)
            stretch = np.sqrt((lr[sl]*co)**2+(lt[sl]*si)**2)
            perimeter = np.zeros_like(stretch); radial_part = np.zeros_like(stretch)
            for polar in psi:
                cp, sp = np.cos(polar), np.sin(polar)
                normal = np.sqrt((si*cp/lr[sl])**2+(co*cp/lt[sl])**2+(sp/lt[sl])**2)
                cross = stretch*normal
                perimeter += cross*(2*np.pi/order)
                radial_part += (sp*si)**2/cross*(2*np.pi/order)
            ds0 = 2*leg0 if i == 0 else a0*(2*np.pi/order)
            total += ds0*perimeter
            radial_sum += ds0*radial_part
        # Number of loops per label = volume0/(pi*r0^2*length0).
        sheet[sl] = amplitude[sl]*volume0/(np.pi*r0*length0)*total
        radial_fraction[sl] = radial_sum/total
    bulk = amplitude*volume0*np.pi/length0*(lt/lr+lr/lt)
    tensor = np.zeros((3,)+e.shape)
    inventories = []
    maximum_drift = 0.
    for current, radial in ((sheet, radial_fraction), (bulk, np.zeros_like(e))):
        inventory = np.sqrt(2)*current.max(axis=0)
        speed = current/inventory
        density = inventory/np.sqrt(1-speed*speed)/D
        tensor[0] += density
        tensor[1] += density*speed*speed*radial
        tensor[2] += density*speed*speed*(1-radial)/2
        inventories.append(inventory)
        maximum_drift = max(maximum_drift, float(speed.max()))
    return dict(unit_tensor=tensor, sheet_current_integral=sheet,
                bend_current_integral=bulk, sheet_radial_fraction=radial_fraction,
                unit_sheet_rest_inventory=inventories[0],
                unit_bend_rest_inventory=inventories[1],
                maximum_drift=maximum_drift, initial_leg=leg0, initial_tube_radius=r0)


def loop_work(times, energy, radial_energy, ell, radius):
    """Discrete field work and electrical transfer; energies are per label.

    Trapezoidal pressure work in log strain converges under time refinement.
    The exact discrete difference defines the electrical transfer needed
    by this controlled flux history. This is the COMPLETE loop transfer;
    assigning its already counted overlap to existing ports is separate.
    """
    t = np.asarray(times, float)
    e, radial, length, R = [np.asarray(v, float) for v in
                           (energy, radial_energy, ell, radius)]
    if (t.ndim != 1 or len(t) < 2 or np.any(np.diff(t) <= 0)
            or e.ndim != 2 or e.shape[0] != len(t)
            or any(v.shape != e.shape for v in (radial, length, R))
            or not all(np.isfinite(v).all() for v in (t, e, radial, length, R))
            or np.any(length <= 0) or np.any(R <= 0)):
        raise ValueError("ordered times and matching finite loop histories required")
    pr, pt = e-2*radial, radial
    mechanical = (-.5*(pr[1:]+pr[:-1])*np.diff(np.log(length), axis=0)
                  -(pt[1:]+pt[:-1])*np.diff(np.log(R), axis=0))
    electrical = np.diff(e, axis=0)-mechanical
    return dict(mechanical=mechanical, electrical=electrical,
                balance_residual=np.diff(e, axis=0)-mechanical-electrical)
