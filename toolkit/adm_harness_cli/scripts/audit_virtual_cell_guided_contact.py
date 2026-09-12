#!/usr/bin/env python3
"""Necessary power ordering for fixed gapless 1D photon channels.

The conditional equilibrium law is c_eq=a2*Theta**2/R**2, with both
directions included and a2=pi*g*l_P**2/(6*DeltaOmega*lambda_eff**2).
The channel count, material solid angle and fluid caloric normalization are
fixed. Finite guide, spectrum, opacity, momentum and entropy closure remain
physical construction requirements.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import sys

import numpy as np

from adm_harness.source_ledger import sha256_file
from audit_joint_dense_work import DenseHistory
from audit_joint_support import bilinear
from audit_virtual_cell_ports import validate_controls
from audit_virtual_cell_thermal_replay import geometry, linear_history
from run_poynting_delivery import BASE, ROOT, write_json

POWER_TOLERANCE = 1e-9
POPULATION_TOLERANCE = 1e-10
TEMPERATURE_TOLERANCE = 1e-12


def guided_interval(power, density, radius, temperature, *,
                    power_tolerance=POWER_TOLERANCE,
                    population_tolerance=POPULATION_TOLERANCE,
                    temperature_tolerance=TEMPERATURE_TOLERANCE):
    """Strict fixed-a2 intervals, with explicitly reported numerical deadbands.

    Positive power creates counter photons; negative power absorbs them.
    Zero-temperature emission and absorption from an empty population are
    incompatible. Strictly positive states retain their mathematical sign,
    including values below the negative-state validation tolerances.
    Zero-temperature absorption from positive density supplies no bound on
    a2. Raw state arrays are preserved without clipping.
    """
    power, density, radius, temperature = np.broadcast_arrays(
        *[np.asarray(a, dtype=float) for a in (power, density, radius, temperature)])
    tolerances = (power_tolerance, population_tolerance, temperature_tolerance)
    if (power.ndim != 2 or min(power.shape) < 1 or np.any(radius <= 0)
            or not all(np.isfinite(a).all() for a in (power, density, radius, temperature))
            or any(not np.isfinite(v) or v <= 0 for v in tolerances)):
        raise ValueError('finite time-position arrays, positive radii and fixed positive tolerances required')
    emission = power > power_tolerance
    absorption = power < -power_tolerance
    warm = temperature > 0
    populated = density > 0
    bad_population = density < -population_tolerance
    bad_temperature = temperature < -temperature_tolerance
    forbidden_emission = emission & ~warm
    forbidden_absorption = absorption & ~populated
    ratio = np.divide(density*radius**2, temperature**2,
                      out=np.full_like(power, np.nan), where=warm)
    lo_table = np.where(emission & warm, ratio, -np.inf)
    hi_table = np.where(absorption & warm & populated, ratio, np.inf)
    lower = np.maximum(0., np.max(lo_table, axis=0))
    upper = np.min(hi_table, axis=0)
    invalid = np.any(bad_population | bad_temperature | forbidden_emission | forbidden_absorption, axis=0)
    compatible = (lower < upper) & (upper > 0) & np.isfinite(lower) & ~invalid
    low_witness = np.where(np.any(emission & warm, axis=0), np.argmax(lo_table, axis=0), -1)
    high_witness = np.where(np.any(absorption & warm & populated, axis=0), np.argmin(hi_table, axis=0), -1)
    return dict(lower=lower, upper=upper, compatible=compatible, ratio=ratio,
        emission=emission, absorption=absorption, bad_population=bad_population,
        bad_temperature=bad_temperature, forbidden_emission=forbidden_emission,
        forbidden_absorption=forbidden_absorption, lower_witness=low_witness,
        upper_witness=high_witness)


def required_counter_power(U0, U0_t, Z0_t, Z_t, K_t, lapse, D, logD_t):
    """Full original fluid/receiver power, less their actual replacement."""
    return (U0_t+U0*logD_t/3+Z0_t-Z_t-K_t/D**(1/3))/(lapse*D)


def receiver_inventory_rate(state, times, lapse, D, loss_density):
    """Use saved proper contact rates when the receiver was reconstructed."""
    if 'contact_control_time' not in state:
        return linear_history(state['t'], state['receiver_thermal_energy'], times)[1], 'linear replay-node receiver history'
    control = np.asarray(state['contact_control_time'])
    hot, cold = [np.asarray(state[key]) for key in
        ('applied_hot_parent_proper_rate', 'applied_cold_parent_proper_rate')]
    expected = (len(control)-1, lapse.shape[1])
    if (control.ndim != 1 or len(control) < 2 or np.any(np.diff(control) <= 0)
            or hot.shape != expected or cold.shape != expected
            or not all(np.isfinite(a).all() for a in (control, hot, cold))
            or np.any(hot < 0) or np.any(cold < 0)
            or np.min(times) < control[0] or np.max(times) > control[-1]):
        raise ValueError('valid saved nonnegative proper contact rates required')
    owner = np.clip(np.searchsorted(control, times, side='right')-1, 0, len(control)-2)
    return lapse*(D*loss_density-hot[owner]+cold[owner]), 'exact converter loss and saved parent proper heat rates'


def necessary_overall_pass(parent_passes, pair_interval_passes, directional_violation):
    return bool(parent_passes and pair_interval_passes
                and directional_violation <= POPULATION_TOLERANCE)


def finite_or_none(value):
    return float(value) if np.isfinite(value) else None


def evaluate(spec):
    path, output = map(Path, spec)
    meta_path = path.with_name(path.stem.removesuffix('_states')+'_summary.json')
    parent = json.loads(meta_path.read_text())
    with np.load(path) as f:
        s = {key: f[key] for key in f.files}
    t, x = s['t'], s['x']
    if len(t) < 2 or len(x) % 2 or np.any(np.diff(t) <= 0) or np.any(np.diff(x) <= 0):
        raise ValueError('ordered replay times and two equal spatial cell grids required')
    tm = (t[:-1]+t[1:])/2
    h = DenseHistory('routed_family', ROOT/parent['input'])
    model = h.h.reference.h.model
    c = geometry(model, tm, x)
    old = h.h.reference.h.state
    ref = h.h.reference
    U0, U0t, unused = bilinear(old['t'], old['x'], old['thermal'], tm, x)
    Z0t = bilinear(ref.t, ref.x, h.h.state['heat'], tm, x)[1]
    Ft = bilinear(old['t'], old['x'], old['flux_energy'], tm, x)[1]
    K, Kt = linear_history(t, s['thermal_inventory'], tm)
    loss = ((1/.98-1)*np.maximum(Ft, 0)+(1-.98)*np.maximum(-Ft, 0))/(c['lapse']*c['radius']**4)
    Zt, receiver_rate_method = receiver_inventory_rate(s, tm, c['lapse'], c['D'], loss)
    V = linear_history(t, s['balanced_radiation_inventory'], tm)[0]
    incident = linear_history(t, s['absorption_rest'], tm)[0]
    returned = linear_history(t, s['work_return_rest']+s['heat_return_rest'], tm)[0]
    radiation = V/c['M']
    counter = radiation-incident-returned
    direction = np.r_[-np.ones(len(x)//2), np.ones(len(x)//2)]
    current = -direction*(incident-returned)
    directional_violation = max(0., float((abs(current)-counter).max()))
    number = np.asarray(s['fluid_particle_number'])
    if number.shape != (len(x),) or not np.isfinite(number).all() or np.any(number <= 0):
        raise ValueError('positive archived fluid particle inventory required')
    number_error = float(abs(number-np.interp(x, old['x'], old['number'])).max())
    if number_error > 1e-10:
        raise ValueError('archived particle inventory differs from registered fluid')
    theta = K/(3*number*c['D']**(1/3))
    power = required_counter_power(U0, U0t, Z0t, Zt, Kt, c['lapse'], c['D'], c['logD_t'])
    fluid_power = Kt/(c['lapse']*c['D']**(4/3))
    old_fluid_power = (U0t+U0*c['logD_t']/3)/(c['lapse']*c['D'])
    old_receiver_power = Z0t/(c['lapse']*c['D'])
    fixed = old_fluid_power+old_receiver_power-loss
    receiver_contact = loss-Zt/(c['lapse']*c['D'])
    result = guided_interval(power, counter, c['radius'], theta)
    lower, upper = float(result['lower'].max()), float(result['upper'].min())
    pair_ok = bool(result['compatible'].all() and lower < upper and upper > 0 and np.isfinite(lower))

    def witness(i, j):
        if i < 0:
            return None
        return dict(time=float(tm[i]), x=float(x[j]), power=float(power[i, j]),
            counter_density=float(counter[i, j]), current=float(current[i, j]),
            fluid_temperature=float(theta[i, j]), radius=float(c['radius'][i, j]),
            a2_threshold=finite_or_none(result['ratio'][i, j]))

    positions = []
    for j in range(len(x)):
        invalid = np.flatnonzero(result['bad_population'][:, j] | result['bad_temperature'][:, j]
            | result['forbidden_emission'][:, j] | result['forbidden_absorption'][:, j])
        positions.append(dict(x=float(x[j]), compatible=bool(result['compatible'][j]),
            a2_lower=float(result['lower'][j]), a2_upper=finite_or_none(result['upper'][j]),
            upper_unbounded=not np.isfinite(result['upper'][j]),
            lower_witness=witness(int(result['lower_witness'][j]), j),
            upper_witness=witness(int(result['upper_witness'][j]), j),
            first_invalid_state_witness=witness(int(invalid[0]), j) if len(invalid) else None,
            emission_samples=int(result['emission'][:, j].sum()),
            absorption_samples=int(result['absorption'][:, j].sum()),
            zero_temperature_emission_samples=int(result['forbidden_emission'][:, j].sum()),
            empty_population_absorption_samples=int(result['forbidden_absorption'][:, j].sum())))
    lj, uj = int(result['lower'].argmax()), int(result['upper'].argmin())
    di, dj = np.unravel_index(np.argmax(abs(current)-counter), counter.shape)
    parent_pass = bool(parent.get('success') and parent.get('full_sampled_gate_passes'))
    summary = dict(input=str(path.relative_to(ROOT)), parent_full_sampled_gate_passes=parent_pass,
        parent_maximum_density_shortfall=parent.get('maximum_density_shortfall'),
        spatial_samples=len(x), time_samples=len(tm),
        compatible_positions=int(result['compatible'].sum()), conditional_pair_power_interval_passes=pair_ok,
        conditional_guided_gate_passes=necessary_overall_pass(parent_pass, pair_ok, directional_violation),
        a2_lower=lower, a2_upper=finite_or_none(upper), upper_unbounded=not np.isfinite(upper),
        pair_lower_witness=witness(int(result['lower_witness'][lj]), lj),
        pair_upper_witness=witness(int(result['upper_witness'][uj]), uj),
        minimum_counter_density=float(counter.min()), minimum_fluid_temperature=float(theta.min()),
        maximum_directional_population_violation=directional_violation,
        worst_directional_population_witness=witness(int(di), int(dj)),
        negative_counter_samples=int(result['bad_population'].sum()),
        negative_temperature_samples=int(result['bad_temperature'].sum()),
        zero_temperature_emission_samples=int(result['forbidden_emission'].sum()),
        empty_population_absorption_samples=int(result['forbidden_absorption'].sum()),
        power_range=[float(power.min()), float(power.max())],
        retained_support_to_fluid_power_range=[float(fixed.min()), float(fixed.max())],
        retained_support_supplies_samples=int((fixed > POWER_TOLERANCE).sum()),
        retained_support_receives_samples=int((fixed < -POWER_TOLERANCE).sum()),
        reciprocal_power_accounting_residual=float(abs(power+fluid_power-receiver_contact-fixed).max()),
        particle_inventory_reconstruction_error=number_error,
        power_tolerance=POWER_TOLERANCE, population_tolerance=POPULATION_TOLERANCE,
        temperature_tolerance=TEMPERATURE_TOLERANCE, input_values_clipped=False,
        equilibrium_law='c_eq=a2*Theta_f**2/R**2; a2=pi*g*l_P**2/(6*DeltaOmega*lambda_eff**2)',
        mode_assumption='fixed gapless nondispersive 1D channels; g counts species/polarizations, each with both directions; guide stress counted separately',
        fluid_caloric_assumption='Theta_f=U/(3*N_mass), requiring a specified thermal-particle normalization',
        opacity_law_constructed=False, momentum_balance_supplied=False,
        remaining_support_contact_entropy_supplied=False, full_source_construction_supplied=False,
        scope='necessary grey power sign ordering; one fixed a2 per position or common to the pair',
        receiver_derivative_method=receiver_rate_method,
        midpoint_approximation='V,K and explicit beam rest energies are linearly interpolated between replay nodes; metric is independently evaluated at midpoints; receiver derivative follows its reported saved-contact or linear-history method',
        positions=positions)
    label = path.stem.removesuffix('_states')
    write_json(output/(label+'_summary.json'), summary)
    np.savez_compressed(output/(label+'_contact.npz'), t=tm, x=x, radius=c['radius'],
        counter_density=counter, counter_current=current, balanced_radiation_rest=radiation,
        fluid_temperature=theta, required_counter_power=power, fluid_power=fluid_power,
        total_receiver_to_fluid_power=receiver_contact, retained_support_to_fluid_power=fixed,
        **result)
    print(label+': '+json.dumps({key: summary[key] for key in
        ('parent_full_sampled_gate_passes', 'conditional_pair_power_interval_passes',
         'conditional_guided_gate_passes', 'a2_lower', 'a2_upper')}), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', nargs='+', required=True)
    parser.add_argument('--output-name', required=True)
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 2:
        parser.error('one or two workers required')
    output = BASE/args.output_name
    if output.exists():
        raise RuntimeError('preserve completed guided-contact evidence')
    paths, hashes, historical = [], {}, []
    for folder in args.inputs:
        source = BASE/folder
        selected = sorted(source.glob('*_states.npz'))
        if not selected:
            raise ValueError('completed replay states required: '+str(source))
        labels = [p.stem.removesuffix('_states') for p in selected]
        verified, previous = validate_controls(source, labels)
        hashes.update(verified); historical.extend(previous); paths.extend(selected)
    if len({p.stem for p in paths}) != len(paths):
        raise ValueError('input folders have colliding output labels; audit them separately')
    sources = [Path(__file__), ROOT/'toolkit/adm_harness_cli/tests/test_virtual_cell_guided_contact.py']
    for module in list(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename:
            path = Path(filename).resolve()
            if path.suffix == '.py' and path.is_relative_to(ROOT):
                sources.append(path)
    for path in sources:
        hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    output.mkdir()
    with ProcessPoolExecutor(max_workers=min(args.workers, len(paths)),
            mp_context=multiprocessing.get_context('spawn')) as pool:
        cases = list(pool.map(evaluate, [(p, output) for p in paths]))
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('runtime input changed during guided-contact audit: '+relative)
    write_json(output/'summary.json', dict(cases=cases))
    write_json(output/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        workers=min(args.workers, len(paths)), input_sha256=hashes, historical_source=historical,
        output_sha256={p.name: sha256_file(p) for p in sorted(output.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
