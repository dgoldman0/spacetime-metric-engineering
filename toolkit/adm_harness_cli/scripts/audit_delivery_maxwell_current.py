#!/usr/bin/env python3
"""Finite main-field charge/current after guide sharing, with counted cold carriers."""
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
from scipy.constants import epsilon_0, G, e, m_p, m_e

from adm_harness.pressure_linked_storage import fluid_coefficients
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import DeliveryHistory, BASE, ROOT, write_json

OUTPUT = BASE/'poynting_delivery/maxwell_current'


def evaluate(cells):
    h = DeliveryHistory(cells)
    z = np.load(BASE/f'poynting_delivery/finite_taps/finite_n{cells}_states.npz')
    c = fluid_coefficients(h.model, h.t, h.x)
    field = h.interpolate_state(h.state['flux_energy'])-z['shared_flux'][None, :]
    charge_flux = np.sqrt(2*field)
    qt = np.gradient(charge_flux, h.t, axis=0, edge_order=2)
    qx = np.gradient(charge_flux, h.x, axis=1, edge_order=2)
    density_adm = qx/(c['b']*c['radius']**2)
    current_adm = -qt/(c['alpha']*c['radius']**2)+c['v']*density_adm
    density = c['gamma']*(density_adm-c['v']*current_adm)
    current = c['gamma']*(current_adm-c['v']*density_adm)
    # Ions follow the prescribed rail labels. Their conserved number per label
    # is prepared to cover every charge and electron-current demand at speed .2.
    required_ions = 1.01*(abs(density)+abs(current)/.2)+1e-30
    prepared = np.max(required_ions*c['rest_volume'], axis=0)
    ions = prepared/c['rest_volume']
    electrons = ions-density
    velocity = -current/electrons
    if electrons.min() <= 0 or abs(velocity).max() > .2:
        raise RuntimeError('finite positive charged-carrier construction failed')
    gamma = 1/np.sqrt(1-velocity**2)
    scale = np.sqrt(epsilon_0*G)/e
    rho = scale*(m_p*ions+m_e*electrons*gamma)
    pr = scale*m_e*electrons*gamma*velocity**2
    j = scale*m_e*electrons*gamma*velocity
    v, boost = c['v'], c['gamma']**2
    tensor = np.array([boost*(rho+2*v*j+v*v*pr), boost*(pr+2*v*j+v*v*rho),
                       boost*((1+v*v)*j+v*(rho+pr)), np.zeros_like(rho)])
    volume = c['b']*c['radius']**2
    dx = h.x[1]-h.x[0]
    # Maxwell continuity is independently evaluated as d_t Q_x-d_x Q_t.
    continuity = np.gradient(qx, h.t, axis=0, edge_order=2)-np.gradient(qt, h.x, axis=1, edge_order=2)
    normalization = max(1e-30, abs(np.gradient(qx, h.t, axis=0, edge_order=2)).max())
    charge_reconstruction = ions-electrons-density
    current_reconstruction = -electrons*velocity-current
    write_json(OUTPUT/f'n{cells}_summary.json', dict(cells=cells,
        maximum_rest_electron_velocity=float(abs(velocity).max()),
        maximum_prescribed_ion_velocity=float(abs(v).max()),
        minimum_electron_density_in_charge_units=float(electrons.min()),
        maximum_carrier_null_stress=float(maximum_null(tensor)[0].max()),
        maximum_carrier_slice_energy=float((4*np.pi*dx*np.sum(volume*tensor[0], axis=1)).max()),
        maximum_rest_current_in_geometric_charge_units=float(abs(current).max()),
        maximum_rest_charge_in_geometric_charge_units=float(abs(density).max()),
        maximum_charge_reconstruction_residual=float(abs(charge_reconstruction).max()),
        maximum_current_reconstruction_residual=float(abs(current_reconstruction).max()),
        relative_Maxwell_charge_continuity_residual=float(abs(continuity).max()/normalization),
        maximum_added_carrier_rest_energy_over_existing_cold_fluid=float(np.max(
            rho/(h.spatial(h.state['number'])[0]/c['rest_volume'])))))


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve the completed Maxwell-current audit')
    sources = [Path(__file__), Path(__file__).with_name('run_poynting_delivery.py'),
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/pressure_linked_storage.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/graded_electrothermal.py',
        BASE/'pressure_linked_storage/retained_coefficients/powered_finite_joint_states.npz',
        BASE/'active_transfer_reservoir/metric_fine.npz', BASE/'active_transfer_reservoir/medium_baseline.npz']
    sources += [BASE/f'poynting_delivery/finite_taps/finite_n{n}_states.npz' for n in (512, 1024)]
    before = {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}
    OUTPUT.mkdir(parents=True)
    for cells in (512, 1024):
        evaluate(cells)
    if before != {str(p.relative_to(ROOT)): sha256_file(p) for p in sources}:
        raise RuntimeError('source changed during current audit')
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256=before,
        output_sha256={p.name: sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print('Charged-carrier inventory and velocity audit complete.', flush=True)


if __name__ == '__main__':
    main()
