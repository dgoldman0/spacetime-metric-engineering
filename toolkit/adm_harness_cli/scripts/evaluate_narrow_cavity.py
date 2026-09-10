#!/usr/bin/env python3
"""Bounded finite-mirror interaction evaluation; numerical artifacts only."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from scipy.integrate import cumulative_simpson, simpson
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq

from adm_harness.curved_boundary import StaticGeometry, radial_mesh
from adm_harness.narrow_cavity import bump, interaction_logdet, planar_interaction, spectral_quadrature

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT/'supporting_reports/data/archived_geometry_opening/reference_metric.npz'
ETA = 2.4127904527582454e-5
PROBLEMS = None


def planar_case(parameters):
    q, s, cells, nodes = parameters
    return planar_interaction(q, s, cells, nodes)


def geometry_chart():
    with np.load(CACHE) as data:
        geometry = StaticGeometry(**{key: data[key] for key in
            ('coordinate', 'radius', 'lapse', 'radial_scale')})
    x = np.r_[np.linspace(-192, -8, 11777)[:-1], geometry.coordinate,
              np.linspace(8, 192, 11777)[1:]]
    proper = cumulative_simpson(geometry.values(x)[2], x=x, initial=0)
    proper -= np.interp(0, x, proper)
    return geometry, PchipInterpolator(x, proper), PchipInterpolator(proper, x)


def make_problem(radius, gap, q, s, args):
    geometry, proper_of_x, x_of_proper = geometry_chart()
    center_x = brentq(lambda x: float(geometry.values(x)[0])-radius, -8., -.4)
    center = float(proper_of_x(center_x))
    width = s*gap
    half = gap/2+2*width+6*gap
    local = np.linspace(center-half, center+half,
        int(np.ceil(2*half/(min(gap, width)/args.cells)))+1)
    # Include exact gap center and material edges without almost-zero cells.
    local = np.unique(np.r_[local, center, center-gap/2, center+gap/2])
    xlocal = x_of_proper(local)
    x = radial_mesh(args.spacing, args.extent)
    x = np.unique(np.r_[x[(x < xlocal[0]-1e-8) | (x > xlocal[-1]+1e-8)], xlocal])
    # Near coincidences arise only from explicit local anchors.
    x = x[np.r_[True, np.diff(x) > 1e-11]]
    cut_node = int(np.argmin(abs(x-center_x)))
    r, a, b = geometry.values(x)
    mid = (x[1:]+x[:-1])/2
    rm, am, bm = geometry.values(mid)
    l = proper_of_x(x)
    centers = [center-gap/2-width, center+gap/2+width]
    profiles = [bump((l-c)/width) for c in centers]
    mass = [q/gap**2*profile[0]**2 for profile in profiles]
    delta = np.diff(x)
    volume = (delta[:-1]+delta[1:])/2
    links = am*rm*rm/(bm*delta)
    frequency_term = volume*b[1:-1]*r[1:-1]**2/a[1:-1]
    angular_term = volume*a[1:-1]*b[1:-1]
    increments = [angular_term*r[1:-1]**2*v[1:-1] for v in mass]
    f = 1/(a*a*r)
    fm = 1/(am*am*rm)
    # Canonical tensor at g=1; the gradient null stress scales as 1/g.
    gradient = q/gap**2/width**2*sum(p[1]**2 for p in profiles)
    potential = q*q/gap**4/4*sum(p[0]**4 for p in profiles)
    material = ETA*np.array([.5*gradient+potential, .5*gradient-potential,
                            -.5*gradient-potential])
    mirror_opening = float(-4*np.pi*simpson(r/a*gradient*b, x=x)*ETA)
    ac = float(geometry.values(center_x)[1])
    k, w = spectral_quadrature(args.frequency_nodes, 1e-8, 24.)
    return dict(radius=radius, gap=gap, q=q, s=s, center_x=center_x, center_proper=center,
        center_lapse=ac, coordinate=x, proper=l, field_radius=r, lapse=a,
        material_tensor_g1=material, gradient_null=ETA*gradient,
        links=links, frequency_term=frequency_term, angular_term=angular_term,
        increments=increments, cut=cut_node-1, f=f[1:-1], fm=fm,
        frequencies=k*ac/gap, weights=w*ac/gap,
        angular_max=int(np.ceil(args.angular_factor*radius/gap)),
        mirror_opening_g1=mirror_opening, deadline=time.monotonic()+args.seconds)


def initialize(problems):
    global PROBLEMS
    PROBLEMS = problems


def angular_case(task):
    label, j = task
    p = PROBLEMS[label]
    links = p['links']
    angular = p['angular_term']*j*(j+1)
    derivative_links = 2*p['fm']*links
    energy = derivative = 0.
    for frequency, weight in zip(p['frequencies'], p['weights']):
        if time.monotonic() > p['deadline']:
            raise TimeoutError('registered cavity allowance expired')
        freq = p['frequency_term']*frequency**2
        diagonal = links[:-1]+links[1:]+angular+freq
        dd = derivative_links[:-1]+derivative_links[1:]-2*p['f']*freq
        value, tangent = interaction_logdet(diagonal, links[1:-1], *p['increments'],
                                            p['cut'], (dd, derivative_links[1:-1]))
        energy += weight*value
        derivative += weight*tangent
    factor = (2*j+1)/(2*np.pi)
    return label, dict(angular=j, energy=energy*factor, opening=-ETA*derivative*factor,
                       max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--planar', action='store_true')
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--radii', nargs='+', type=float, default=[3., 4.2, 6.8])
    parser.add_argument('--gaps', nargs='+', type=float, default=[.5, .25, .125])
    parser.add_argument('--q', type=float)
    parser.add_argument('--s', type=float)
    parser.add_argument('--cells', type=int, default=32)
    parser.add_argument('--spacing', type=float, default=1/64)
    parser.add_argument('--extent', type=float, default=48.)
    parser.add_argument('--frequency-nodes', type=int, default=64)
    parser.add_argument('--angular-factor', type=float, default=8.)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--seconds', type=float, default=900.)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError('one to four workers required')
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError('use a fresh evidence directory')
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    paths = [Path(__file__), ROOT/'toolkit/adm_harness_cli/adm_harness/narrow_cavity.py',
             ROOT/'toolkit/adm_harness_cli/adm_harness/curved_boundary.py', CACHE]
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    if args.planar:
        jobs = [(q, s, 256, 128) for s in (.05, .1, .2, .5, 1., 2.)
                for q in np.geomspace(1e-4, 1e4, 81)]
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            rows = list(pool.map(planar_case, jobs))
        best = min((r for r in rows if r['crossing_coupling'] is not None),
                   key=lambda r: r['crossing_coupling'])
        result = dict(planar_cases=rows, best=best)
    else:
        if args.selection:
            selected = json.loads(args.selection.read_text())['best']
            q, s = selected['q'], selected['s']
        elif args.q is not None and args.s is not None:
            q, s = args.q, args.s
        else:
            raise ValueError('a planar selection or explicit q,s is required')
        problems = {f'r{r:g}_a{a:g}': make_problem(r, a, q, s, args)
                    for r in args.radii for a in args.gaps}
        rows = {label: [] for label in problems}
        jobs = [(label, j) for label, p in problems.items() for j in range(p['angular_max']+1)]
        print(json.dumps(dict(angular_tasks=len(jobs), points={k: len(p['coordinate']) for k,p in problems.items()})), flush=True)
        with ProcessPoolExecutor(max_workers=args.workers, initializer=initialize, initargs=(problems,)) as pool:
            futures = [pool.submit(angular_case, task) for task in jobs]
            for i, future in enumerate(as_completed(futures)):
                label, value = future.result()
                rows[label].append(value)
                if (i+1) % 100 == 0:
                    print(json.dumps(dict(completed=i+1, total=len(jobs))), flush=True)
        result = dict(cases={})
        for label, p in problems.items():
            modes = sorted(rows[label], key=lambda row: row['angular'])
            opening = sum(m['opening'] for m in modes)
            entry = {key: p[key] for key in ('radius','gap','q','s','center_x','center_proper',
                     'center_lapse','angular_max','mirror_opening_g1')}
            entry.update(modes=modes, interaction_energy=sum(m['energy'] for m in modes),
                         interaction_opening=opening, crossing_coupling=-p['mirror_opening_g1']/opening if opening > 0 else None,
                         net_opening={f'g{g:g}': opening+p['mirror_opening_g1']/g for g in (1.,4.,10.)})
            result['cases'][label] = entry
            np.savez_compressed(args.output/f'{label}_material.npz',
                **{key: p[key] for key in ('coordinate','proper','field_radius','lapse','material_tensor_g1','gradient_null')})
    result.update(eta=ETA, elapsed_seconds=time.monotonic()-started,
                  parameters={k: str(v) if isinstance(v, Path) else v for k,v in vars(args).items()},
                  source_hashes=source_hashes)
    (args.output/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: value for key,value in result.items() if key not in ('planar_cases','cases')}, indent=2))
    if 'cases' in result:
        print(json.dumps({label: {k:v for k,v in row.items() if k != 'modes'} for label,row in result['cases'].items()}, indent=2))
    size = sum(p.stat().st_size for p in args.output.iterdir() if p.is_file())
    if size > 20_000_000:
        raise RuntimeError('cavity retained-output allowance exceeded')


if __name__ == '__main__':
    main()
