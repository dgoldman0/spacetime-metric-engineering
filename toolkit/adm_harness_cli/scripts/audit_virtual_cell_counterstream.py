#!/usr/bin/env python3
"""Finite-difference source audit of a replayed minimal counterstream."""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess

import numpy as np
from scipy.ndimage import maximum_filter, minimum_filter
from numpy.polynomial.legendre import leggauss

from adm_harness.active_transfer_reservoir import TabulatedActiveMedium
from adm_harness.source_ledger import sha256_file
from adm_harness.virtual_cell_counterstream import (
    directional_adm_exchange, material_kinematics, minimal_counterstream,
    passive_total_radiation_interval, tetrad_exchange,
)

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'supporting_reports/data'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def geometry(model, times, positions):
    names = ('alpha', 'beta', 'b', 'radius', 'alpha_x', 'beta_x',
             'logb_t', 'logb_x', 'logr_t', 'logr_x')
    rows = [model.metric(float(t), positions) for t in times]
    g = {key: np.array([getattr(row, key) for row in rows]) for key in names}
    tt, xx = np.meshgrid(times, positions, indexing='ij')
    g['alpha_t'] = g['alpha']*model.metric_splines[0].ev(tt, xx, dx=1)
    g['beta_t'] = model.metric_splines[1].ev(tt, xx, dx=1)
    return g


def find_control(source, label, explicit=None):
    if explicit is not None:
        return Path(explicit)/(label+'_states.npz')
    manifest = json.loads((source/'manifest.json').read_text())
    matches = [ROOT/key for key in manifest.get('input_sha256', {})
               if Path(key).name == label+'_states.npz']
    # A reconstructed archive is an input to replay. Select the matching
    # wave-free control when several earlier optimization histories remain.
    for path in reversed(matches):
        with np.load(path) as z:
            if ('positive_increment' in z and 'amplitude' in z and
                    'absorption_state' not in z):
                return path
    if len(matches) == 1:
        return matches[0]
    raise ValueError('identify the replayed controls explicitly with --controls')


def integrated_phase_work(model, times, positions, control_times, increments, order):
    """Gauss integration of ell^2 A_t, resolving every amplitude-control knot."""
    if (np.any(positions<model.x_min) or np.any(positions>model.x_max)):
        raise ValueError('quadrature requires positions inside the registered metric table')
    z, weights=leggauss(order); result=np.zeros((len(times),len(positions)))
    dt=np.diff(times); middle=(times[:-1]+times[1:])/2
    interval=np.clip(np.searchsorted(control_times,middle,side='right')-1,0,len(control_times)-2)
    if (np.any(times[:-1]<control_times[interval]-1e-13) or
            np.any(times[1:]>control_times[interval+1]+1e-13)):
        raise ValueError('replay intervals must retain all control knots')
    rates=increments[interval]/np.diff(control_times)[interval,None]
    for begin in range(0,len(dt),128):
        end=min(begin+128,len(dt))
        quad=(middle[begin:end,None]+dt[begin:end,None]*z[None,:]/2).ravel()
        tt,xx=np.meshgrid(quad,positions,indexing='ij')
        alpha=np.exp(model.metric_splines[0].ev(tt,xx))
        beta=model.metric_splines[1].ev(tt,xx)
        b=np.exp(model.metric_splines[2].ev(tt,xx))
        ell2=b*b/(1-(b*beta/alpha)**2)
        integral=(ell2.reshape(end-begin,order,len(positions))*weights[None,:,None]).sum(axis=1)
        result[begin+1:end+1]=rates[begin:end]*integral*dt[begin:end,None]/2
    return np.cumsum(result,axis=0)


def evaluate(item):
    path, control, output = map(Path, item)
    meta = json.loads(path.with_name(path.name.replace('_states.npz', '_summary.json')).read_text())
    with np.load(path) as z:
        state = {key: z[key] for key in z.files}
    with np.load(control) as z:
        controls = {key: z[key] for key in z.files}
    cm = json.loads(control.with_name(control.name.replace('_states.npz', '_summary.json')).read_text())
    t, x = state['t'], state['x']; nt, nx = len(t), len(x)
    if nx % 4 or nt < 9:
        raise ValueError('two cells with even decimated sample counts are required')
    model = TabulatedActiveMedium(BASE/'active_transfer_reservoir/metric_fine.npz',
                                  BASE/'active_transfer_reservoir/medium_baseline.npz')
    g = geometry(model, t, x); k = material_kinematics(g)
    direction = np.r_[-np.ones(nx//2), np.ones(nx//2)]
    returned = state['work_return_rest']+state['heat_return_rest']
    wave_energy = state['absorption_rest']+returned
    c, j = minimal_counterstream(state['absorption_rest'], returned, direction)
    wave_current = -j
    power, force = tetrad_exchange(c, j, t, x, g, nx//2)
    adm_power, adm_force = directional_adm_exchange(c, j, t, x, g, nx//2)
    beam_power, beam_force = tetrad_exchange(wave_energy, wave_current, t, x, g, nx//2)

    control_t = controls['t']; widths = np.diff(control_t)
    interval = np.clip(np.searchsorted(control_t, t, side='right')-1, 0, len(widths)-1)
    oldnx = controls['positive_increment'].shape[1]
    plus = np.column_stack([controls['positive_increment'][interval, half*(oldnx//2)]/widths[interval]
                            for half in (0, 1)])
    minus = np.column_stack([controls['negative_increment'][interval, half*(oldnx//2)]/widths[interval]
                             for half in (0, 1)])
    plus, minus = np.repeat(plus, nx//2, axis=1), np.repeat(minus, nx//2, axis=1)
    eta = cm['efficiency']; denom = k['lapse']*g['radius']**2
    expected_power = (-plus+minus)/denom
    expected_force = -direction*(plus/eta+minus+(1/eta-1)*plus)/denom
    beam_power_error, beam_force_error = beam_power-expected_power, beam_force-expected_force

    increments=np.column_stack([(controls['positive_increment']-controls['negative_increment'])[:,half*(oldnx//2)]
                                for half in (0,1)])
    increments=np.repeat(increments,nx//2,axis=1)
    work4=integrated_phase_work(model,t,x,control_t,increments,4)
    work8=integrated_phase_work(model,t,x,control_t,increments,8)
    core=state['amplitude']/g['radius']**2
    interval_args=(state['absorption_rest'], returned, state['density'],
                   state['radial_pressure'],state['angular_pressure'],core,k['ell'],g['radius'])
    interval4=passive_total_radiation_interval(*interval_args,work4)
    interval8=passive_total_radiation_interval(*interval_args,work8)
    interval_coarse=passive_total_radiation_interval(*[a[::2,::2] for a in interval_args],work8[::2,::2])

    coarse_g = {key: value[::2, ::2] for key, value in g.items()}
    coarse_p, coarse_f = tetrad_exchange(c[::2, ::2], j[::2, ::2], t[::2], x[::2],
                                        coarse_g, nx//4)
    fine_p, fine_f = power[::2, ::2], force[::2, ::2]
    change_p, change_f = abs(fine_p-coarse_p), abs(fine_f-coarse_f)
    form_p = abs((power-adm_power)[::2, ::2]); form_f = abs((force-adm_force)[::2, ::2])
    control_p = abs(beam_power_error[::2, ::2]); control_f = abs(beam_force_error[::2, ::2])
    error_p = np.maximum.reduce([change_p, form_p, control_p])
    error_f = np.maximum.reduce([change_f, form_f, control_f])

    # Firm witnesses have same-sign current throughout every fine/coarse
    # derivative stencil, lie within one control interval, and avoid all cuts.
    sign = np.sign(j)
    same_sign = ((maximum_filter(sign, size=5, mode='nearest') ==
                  minimum_filter(sign, size=5, mode='nearest')) & (sign != 0))
    lower, upper = control_t[interval], control_t[interval+1]
    time_ok = np.zeros(nt, dtype=bool)
    time_ok[2:-2] = ((t[:-4] >= lower[2:-2]-1e-13) &
                    (t[4:] <= upper[2:-2]+1e-13))
    spatial_ok = np.zeros(nx, dtype=bool)
    for start in (0, nx//2): spatial_ok[start+4:start+nx//2-4] = True
    smooth = same_sign & time_ok[:, None] & spatial_ok[None, :]
    smooth &= c > max(float(c.max())*1e-6, 1e-14)
    smooth = smooth[::2, ::2]
    resolved = smooth & (abs(fine_p)>10*error_p+1e-9) & (fine_p*coarse_p>0)
    resolved &= abs(fine_f)>10*error_f+1e-9

    def stats(values, mask):
        selected = values[mask]
        return dict(samples=int(selected.size), maximum_absolute=float(abs(selected).max()) if selected.size else None,
                    median_absolute=float(np.median(abs(selected))) if selected.size else None)

    witnesses = []
    for label, mask in [('positive_power', resolved & (fine_p>0)),
                        ('negative_power', resolved & (fine_p<0))]:
        where = np.argwhere(mask)
        if not len(where): continue
        order = np.argsort(abs(fine_p[mask]))[-5:][::-1]
        for row in order:
            i, jx = where[row]; fi, fj = 2*i, 2*jx
            witnesses.append(dict(kind=label, time=float(t[fi]), x=float(x[fj]),
                counter_energy=float(c[fi, fj]), counter_current=float(j[fi, fj]),
                required_counter_power=float(power[fi, fj]), required_counter_force=float(force[fi, fj]),
                required_partner_power=float(-power[fi, fj]), required_partner_force=float(-force[fi, fj]),
                adm_power=float(adm_power[fi, fj]), adm_force=float(adm_force[fi, fj]),
                coarsened_power=float(coarse_p[i, jx]), coarsened_force=float(coarse_f[i, jx]),
                power_derivative_change=float(change_p[i, jx]), force_derivative_change=float(change_f[i, jx]),
                explicit_beam_power_residual=float(beam_power_error[fi, fj]),
                explicit_beam_force_residual=float(beam_force_error[fi, fj]),
                conservative_power_sensitivity=float(error_p[i, jx]),
                conservative_force_sensitivity=float(error_f[i, jx])))
    null_relation = fine_f-np.sign(j[::2, ::2])*fine_p
    spatial_interval_mask=spatial_ok[::2]
    gap=interval8['constant_interval_gap'][::2]
    gap_quad=abs(gap-interval4['constant_interval_gap'][::2])
    gap_decimation=abs(gap-interval_coarse['constant_interval_gap'])
    interval_resolved=spatial_interval_mask & (gap>10*np.maximum(gap_quad,gap_decimation)+1e-8)
    interval_witnesses=[]
    for cj in np.flatnonzero(interval_resolved)[np.argsort(gap[interval_resolved])[-5:][::-1]]:
        jj=2*cj; lo=int(interval8['lower_witness_index'][jj]); hi=int(interval8['upper_witness_index'][jj])
        interval_witnesses.append(dict(x=float(x[jj]),lower_time=float(t[lo]),upper_time=float(t[hi]),
            initial_constant_lower=float(interval8['initial_constant_lower'][jj]),
            initial_constant_upper=float(interval8['initial_constant_upper'][jj]),
            constant_gap=float(gap[cj]),quadrature_gap_change=float(gap_quad[cj]),
            decimated_gap_change=float(gap_decimation[cj]),
            radiation_capacity_shortfall=float(interval8['radiation_density_shortfall'][jj]),
            equivalent_target_density_relaxation=float(3*interval8['radiation_density_shortfall'][jj])))
    result = dict(label=meta['label'], source=str(path.relative_to(ROOT)),
        controls=str(control.relative_to(ROOT)), fine_time_samples=nt, fine_spatial_samples=nx,
        coarse_time_samples=len(t[::2]), coarse_spatial_samples=len(x[::2]),
        comparison='second-order derivatives of one fine replay versus time/space decimation; no new wave solution',
        smooth_samples=int(smooth.sum()), resolved_nonzero_exchange_samples=int(resolved.sum()),
        maximum_counter_density=float(c.max()),
        counter_power_smooth=stats(fine_p, smooth), counter_force_smooth=stats(fine_f, smooth),
        counter_power_resolved=stats(fine_p, resolved), counter_force_resolved=stats(fine_f, resolved),
        beam_power_control_residual=stats(control_p, smooth), beam_force_control_residual=stats(control_f, smooth),
        adm_tetrad_power_difference=stats(form_p, smooth), adm_tetrad_force_difference=stats(form_f, smooth),
        strict_minimum_null_relation=stats(null_relation, smooth),
        free_counterstream_excluded_by_resolved_witness=bool(resolved.any()),
        zero_power_elastic_scattering_excluded_for_retained_minimum=bool(resolved.any()),
        both_exchange_signs_resolved=bool(np.any(resolved & (fine_p>0)) and np.any(resolved & (fine_p<0))),
        resolution_scope='finite-difference witnesses outside current switches, control knots and material cuts; empirical sensitivity, not a continuum error bound',
        total_backing_force_interpretation='required exchange is internal to the proposed decomposition; existing backing target and its fixed-component divergence remain unchanged',
        energy_partner_supplied=False, scattering_completion_supplied=False,
        passive_energy_interval=dict(arbitrary_prepared_spatial_grading=True,
            permits_extra_balanced_counterphotons=True,source='exact counted beam conversion power; Gauss integral of ell^2 A_t',
            actual_target_density_used=True,numerical_reserve_added=False,
            quadrature_orders=[4,8],maximum_work_quadrature_change=float(abs(work8-work4).max()),
            sampled_incompatible_positions=int(np.sum(interval8['constant_interval_gap']>1e-8)),
            total_positions=nx,resolved_interior_incompatibilities=int(interval_resolved.sum()),
            passive_energy_completion_excluded_by_resolved_witness=bool(interval_resolved.any()),
            maximum_radiation_capacity_shortfall=float(interval8['radiation_density_shortfall'].max()),
            witnesses=interval_witnesses,
            scope='necessary interval intersection on sampled actual replay; quadrature controlled and sampling sensitivity reported; propagation error is inherited from the independent replay'),
        witnesses=witnesses)
    stem=meta['label']; write_json(output/(stem+'_summary.json'), result)
    np.savez_compressed(output/(stem+'_exchange.npz'), t=t[::2], x=x[::2],
        counter_energy=c[::2, ::2], counter_current=j[::2, ::2], power=fine_p, force=fine_f,
        coarse_power=coarse_p, coarse_force=coarse_f, power_sensitivity=error_p, force_sensitivity=error_f,
        smooth_mask=smooth, resolved_mask=resolved,phase_work=work8[::2,::2],
        passive_initial_lower=interval8['initial_constant_lower'][::2],
        passive_initial_upper=interval8['initial_constant_upper'][::2],
        passive_constant_gap=gap,passive_gap_decimation_change=gap_decimation,
        passive_counter_density=interval8['counter_density'][::2,::2],
        passive_resolved_mask=interval_resolved)
    print(stem+': resolved exchange witnesses='+str(int(resolved.sum())), flush=True)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=BASE/'virtual_cell_reconstructed_replay')
    parser.add_argument('--controls', type=Path)
    parser.add_argument('--output', type=Path, default=BASE/'virtual_cell_counterstream_baseline')
    parser.add_argument('--workers', type=int, default=2)
    args=parser.parse_args()
    if not 1<=args.workers<=2: parser.error('--workers must be 1 or 2')
    source=args.source.resolve(); output=args.output.resolve()
    paths=sorted(source.glob('*_factor4_states.npz'))
    if not paths: paths=sorted(source.glob('*_states.npz'))
    if not paths: raise ValueError('no replayed states found')
    if output.exists(): raise RuntimeError('preserve completed counterstream audit')
    pairs=[]; input_paths=[source/'manifest.json', BASE/'active_transfer_reservoir/metric_fine.npz',
        BASE/'active_transfer_reservoir/medium_baseline.npz']
    for path in paths:
        mp=path.with_name(path.name.replace('_states.npz', '_summary.json'))
        meta=json.loads(mp.read_text()); control=find_control(source, meta['label'], args.controls)
        pairs.append((str(path), str(control), str(output)))
        input_paths.extend([path, mp, control, control.with_name(control.name.replace('_states.npz', '_summary.json'))])
    input_paths.extend([Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/virtual_cell_counterstream.py',
        ROOT/'toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py',
        ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_counterstream.py'])
    hashes={str(p.relative_to(ROOT)):sha256_file(p) for p in input_paths}
    output.mkdir(parents=True)
    with ProcessPoolExecutor(max_workers=min(args.workers,len(pairs)),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,pairs))
    write_json(output/'summary.json', dict(cases=results))
    write_json(output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        workers=min(args.workers,len(pairs)), input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__=='__main__': main()
