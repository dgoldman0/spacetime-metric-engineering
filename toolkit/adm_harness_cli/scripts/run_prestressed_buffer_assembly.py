#!/usr/bin/env python3
"""Compare a prestressed backbone and its equal-energy control on the active rail."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse
import json
import multiprocessing
from pathlib import Path

import numpy as np
import pandas as pd

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.elastic_endpoint_reservoir import ElasticLaw
from adm_harness.electrothermal_endpoint import ElectricalLaw
from adm_harness.material_ensemble import evolve_material_ensemble
from adm_harness.relaxing_material_ensemble import RelaxingMaterialEnsemble, StrainRelaxation
from adm_harness.prestressed_buffer_assembly import PrestressedBufferAssembly
from adm_harness.source_ledger import sha256_file

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'
OUTPUT = ROOT/'supporting_reports/data/prestressed_buffer_assembly'


def run_case(task):
    case, cells, duration, max_step, cfl, snapshots, deadline, output, minimum_sound_speed = task
    model = TabulatedActiveMedium(INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')
    template = RelaxingMaterialEnsemble(model, ElasticLaw(stiffness=.1, scale=.4),
                                         ElectricalLaw(energy_ratio=4., conductivity=.1, profile='capacitor'),
                                         relaxation=StrainRelaxation(stiffness=.1, proper_time=1.),
                                         cells=cells, thermal_share=1., forcing=1.)
    patch = PrestressedBufferAssembly(template, backbone_scale=.001)
    preload = patch.equilibrate_initial_preload(minimum_sound_speed=minimum_sound_speed)
    fraction = patch.match_template_energy(preload) if case == 'energy_matched' else 1.
    if case == 'unforced':
        patch.forcing = 0.
    initial_residual = float(np.max(abs(patch.fixed_motion_residual())))
    result = evolve_material_ensemble(patch, duration=duration, max_step=max_step, cfl=cfl,
                                      snapshots=snapshots, deadline_seconds=deadline, max_steps=100000)
    for row, t, state in zip(result['history'], result['times'], result['states']):
        f = patch.fields(float(t), state)
        g = f['metric']
        density = patch.law.scale*f['energy_int']/(f['volume']*g.radius**2)
        stress = patch.law.scale*f['radial_int']/(f['volume']*g.radius**2)
        row.update(receiver_velocity=float(f['velocity'][cells//2]),
                   receiver_heat=float(f['heat'][cells//2]),
                   receiver_l=float(f['x'][cells//2]),
                   receiver_effective_n=float(f['effective_n'][cells//2]),
                   maximum_gamma=float(f['gamma'].max()),
                   minimum_sound2=float(f['sound2'].min()),
                   minimum_rest_dec_margin=f['minimum_rest_dec_margin'],
                   maximum_density=float(density.max()), maximum_abs_radial_stress=float(abs(stress).max()),
                   backbone_slice_energy=float(4*np.pi*f['backbone_adm'].sum()),
                   maximum_backbone_inverse_stretch=float(f['backbone_stretch'].max()),
                   minimum_backbone_inverse_stretch=float(f['backbone_stretch'].min()))
    label = f'{case}_n{cells}_end{duration:g}_dt{max_step:g}_cfl{cfl:g}'
    frame = pd.DataFrame(result['history'])
    frame.to_csv(output/f'{label}_history.csv', index=False)
    np.savez_compressed(output/f'{label}_states.npz', t=result['times'], states=result['states'],
                         initial_x=patch.initial_x, thermal_reference=patch.reference,
                         backbone_weight=patch.backbone_weight)
    first, final = frame.iloc[0], frame.iloc[-1]
    summary = dict(case=case, cells=cells, duration=duration, max_step=max_step, cfl=cfl, snapshots=snapshots,
                   backbone_scale=patch.backbone_scale, density_scale=patch.law.scale,
                   status=result['status'], failure=result['failure'], elapsed_seconds=result['elapsed_seconds'],
                   preload_fraction=fraction, initial_fixed_motion_residual=initial_residual,
                   requested_equilibrium_minimum_sound_speed=minimum_sound_speed,
                   actual_initial_minimum_sound_speed=float(np.sqrt(first.minimum_sound2)),
                   minimum_preload_initial_slice_energy=preload['initial_slice_energy'],
                   template_initial_slice_energy=patch.template_initial_slice_energy,
                   initial_slice_energy=float(first.slice_energy), initial_canonical_energy=float(first.canonical_energy),
                   initial_thermal_inventory=float(first.thermal_inventory),
                   initial_energy_ratio=float(first.slice_energy/patch.template_initial_slice_energy),
                   maximum_velocity_over_run=float(frame.maximum_abs_velocity.max()),
                   maximum_receiver_velocity_over_run=float(abs(frame.receiver_velocity).max()),
                   maximum_gamma_over_run=float(frame.maximum_gamma.max()),
                   minimum_heat_over_run=float(frame.minimum_heat.min()),
                   maximum_density_over_run=float(frame.maximum_density.max()),
                   maximum_radial_stress_over_run=float(frame.maximum_abs_radial_stress.max()),
                   maximum_anchor_force_over_run=float(frame.maximum_anchor_force.max()),
                   maximum_canonical_balance_error=float(abs(frame.canonical_balance_residual).max()),
                   maximum_momentum_balance_error=float(abs(frame.momentum_balance_residual).max()),
                   maximum_thermal_balance_error=float(abs(frame.thermal_balance_residual).max()),
                   minimum_packet_gap_over_run=float(frame.minimum_packet_gap.min()), **final.to_dict())
    for speed in (.5, .9, .99, .999):
        rows = frame[frame.maximum_abs_velocity >= speed]
        summary[f'first_saved_time_velocity_ge_{speed}'] = None if rows.empty else float(rows.s.iloc[0])
    sources = [Path(__file__)]+[ROOT/'toolkit/adm_harness_cli/adm_harness'/name for name in (
        'prestressed_buffer_assembly.py', 'material_ensemble.py', 'relaxing_material_ensemble.py',
        'elastic_endpoint_reservoir.py', 'electrothermal_endpoint.py', 'active_transfer_reservoir.py')]
    manifest = dict(completed_utc=datetime.now(timezone.utc).isoformat(),
                     scope='evolved bonded causal backbone and thermal buffers on the full active metric; initial prestress solves the discrete interior acceleration balance; fixed end reactions and reciprocal endpoint power are counted; endpoint response and anchor tensors remain external requirements',
                     software_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in sources},
                     input_sha256={str(p.relative_to(ROOT)): sha256_file(p) for p in
                                   (INPUT/'metric_fine.npz', INPUT/'medium_baseline.npz')})
    for suffix, data in (('summary', summary), ('manifest', manifest)):
        (output/f'{label}_{suffix}.json').write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')
    print(f'{label}: {result["status"]} at s={final.s:.9g}; peak |v|={summary["maximum_velocity_over_run"]:.7g}; '
          f'receiver v={final.receiver_velocity:.7g}; q_min={final.minimum_heat:.6g}; '
          f'energy ratio={summary["initial_energy_ratio"]:.5g}; canonical error={summary["maximum_canonical_balance_error"]:.5g}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', nargs='+', choices=('equilibrated', 'energy_matched', 'unforced'),
                         default=['equilibrated', 'energy_matched'])
    parser.add_argument('--cells', nargs='+', type=int, default=[32, 64])
    parser.add_argument('--duration', type=float, default=1.285)
    parser.add_argument('--max-step', type=float, default=.0005)
    parser.add_argument('--cfl', type=float, default=.05)
    parser.add_argument('--snapshots', type=int, default=258)
    parser.add_argument('--deadline', type=float, default=240.)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--minimum-sound-speed', type=float, default=0.)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 6 or any(n < 8 or n % 2 for n in args.cells) or not 0 <= args.minimum_sound_speed < 1:
        parser.error('one to six workers and even material cell counts >=8 required')
    args.output.mkdir(parents=True, exist_ok=True)
    tasks = [(case, cells, args.duration, args.max_step, args.cfl, args.snapshots, args.deadline, args.output, args.minimum_sound_speed)
             for case in args.cases for cells in args.cells]
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context('spawn')) as pool:
        list(pool.map(run_case, tasks))


if __name__ == '__main__':
    main()
