#!/usr/bin/env python3
"""One bounded conservative blend toward the scalar-potential response target."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess

import numpy as np

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.scalar_flux_support import decompose, minimum_energy
from adm_harness.source_ledger import sha256_file
from audit_joint_support import bilinear
from run_joint_response_family import ResponseFamily
from run_joint_route_response import routed_coefficients
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'scalar_flux_support_blend'


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed conservative blend evidence')
    sources = [('joint_refined_response', 'members_fraction0.99'),
               ('scalar_flux_response_family', 'n256_potential')]
    states, hashes = [], {}
    for directory, label in sources:
        path = BASE/directory/(label+'_states.npz')
        manifest_path = path.parent/'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        assert sha256_file(path) == manifest['output_sha256'][path.name]
        hashes.update(manifest['input_sha256'])
        for source in [path, manifest_path]:
            hashes[str(source.relative_to(ROOT))] = sha256_file(source)
        with np.load(path) as data:
            states.append({key:data[key] for key in data.files})
    for key in ['t', 'x', 'local_exchange']:
        np.testing.assert_array_equal(states[0][key], states[1][key])
    fraction = .9
    result = {key:states[0][key] for key in ['t', 'x', 'local_exchange']}
    for key in ['support_energy', 'radial_pressure', 'radial_volume', 'angular_volume', 'parameters']:
        result[key] = (1-fraction)*states[0][key]+fraction*states[1][key]
    t, x = result['t'], result['x']
    # Verify that this is a registered affine solution, including work-route
    # controls, rather than an independently patched stress tensor.
    with np.load(BASE/'joint_refined_response/responses.npz') as basis:
        coefficients = np.r_[1., result['parameters']]
        replay = {key:float(np.max(abs(basis[source]@coefficients-result[key])))
                  for key, source in [('support_energy', 'energy'),
                                      ('radial_pressure', 'pressure'),
                                      ('angular_volume', 'angular')]}
    assert max(replay.values()) < 1e-9, replay
    family = ResponseFamily(256, 2)
    c = routed_coefficients(family, result['parameters'], t, x)
    rho = result['support_energy']/c['D']; p = result['radial_pressure']
    q = result['angular_volume']/c['D']
    old = family.h.reference.h.state
    u = bilinear(old['t'], old['x'], old['thermal'], t, x)[0]
    n = np.interp(x, old['x'], old['number'])
    tensor = anisotropic_moments((n+u)/c['D']+rho, u/(3*c['D'])+p,
                                u/(3*c['D'])+q, c['v'])
    components = decompose(rho, p, q)
    result['component_energy'] = components
    summary = dict(label='fraction0.9', potential_target_fraction=fraction,
        reference_target_fraction=1-fraction, response_basis_replay_residuals=replay,
        maximum_node_density_shortfall=float(np.maximum(minimum_energy(p, q)-rho, 0.).max()),
        maximum_node_component_cost_fraction=float((minimum_energy(p, q)/rho).max()),
        minimum_component_energy=float(components.min()),
        material_peak_upper=float(maximum_null(tensor)[0].max()),
        initial_support_rest=float(4*np.pi*np.trapezoid(result['support_energy'][0], x)),
        final_support_rest=float(4*np.pi*np.trapezoid(result['support_energy'][-1], x)),
        absorption_left_feed_fraction=float(result['parameters'][-2]),
        recovery_left_emission_fraction=float(result['parameters'][-1]),
        physical_field_law_supplied=False, continuing_connections_supplied=False,
        changed_route_stress_counted=False)
    for source in [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/scalar_flux_support.py']:
        hashes[str(source.relative_to(ROOT))] = sha256_file(source)
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('changed blend source: '+relative)
    OUTPUT.mkdir()
    np.savez_compressed(OUTPUT/'fraction0.9_states.npz', **result)
    write_json(OUTPUT/'fraction0.9_summary.json', summary)
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
