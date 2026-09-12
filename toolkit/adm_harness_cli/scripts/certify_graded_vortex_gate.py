#!/usr/bin/env python3
"""Eliminate time-fixed tube amplitudes and check a short LP contradiction.

For each position, existence of A>=0 is equivalent to every upper bound
being positive and every lower bound being below every upper bound through
time. Temporal separation generates only the violated pair constraints.
"""
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import multiprocessing
import subprocess
import time

import numpy as np
from scipy.optimize import OptimizeResult
from scipy.sparse import csr_matrix, vstack

import adm_harness.cutting_plane_lp as cuts
from adm_harness.lp_infeasibility_certificate import certificate
from adm_harness.source_ledger import sha256_file
import run_graded_vortex_gate as gate
from run_joint_response_family import NPARAM
from run_poynting_delivery import BASE, ROOT, write_json

OUTPUT = BASE/'graded_vortex_eliminated_gate'


def evaluate(intervals):
    nx = intervals+1
    captured = {}; original_linprog = cuts.linprog

    def record(cost, **kwargs):
        result = original_linprog(cost, **kwargs)
        if result.status == 2:
            proof = certificate(kwargs['A_ub'], kwargs['b_ub'], kwargs['bounds'])
            captured.update({key:value for key, value in proof.items() if not isinstance(value, np.ndarray)})
            if proof.get('valid'):
                arrays = {key:value for key, value in proof.items() if isinstance(value, np.ndarray)}
                np.savez_compressed(OUTPUT/f'n{intervals}_certificate.npz', **arrays)
                captured['retained_constraint_count'] = len(proof['weights'])
        return result

    def eliminate(cost, matrix, rhs, bounds, **unused):
        start = time.monotonic()
        # The registered runner has three material blocks and seven null
        # blocks. Each block contains every time at every spatial node.
        count = matrix.shape[0]//10
        assert count*10 == matrix.shape[0] and count % nx == 0
        nt = count//nx; controls = NPARAM+2
        keep = np.r_[np.arange(controls), matrix.shape[1]-1]
        reduced = matrix[:, keep].tocsr()
        amplitude = np.asarray(matrix[:3*count, controls:controls+nx].sum(axis=1)).ravel()
        assert np.all(amplitude[:2*count] > 0.) and np.all(amplitude[2*count:] < 0.)
        # Bound expressions A >= L(z), A <= U(z), represented as const+row*z.
        polynomial = reduced[:3*count].multiply((-1/amplitude)[:, None]).tocsr()
        constant = rhs[:3*count]/amplitude
        lower_matrix = polynomial[2*count:]
        lower_constant = constant[2*count:]
        upper_matrix = polynomial[:2*count]
        upper_constant = constant[:2*count]
        local = [lower_matrix-upper_matrix[k*count:(k+1)*count] for k in range(2)]
        local_rhs = [upper_constant[k*count:(k+1)*count]-lower_constant for k in range(2)]
        fixed = vstack([reduced[:2*count], *local, reduced[3*count:]], format='csr')
        target = np.r_[rhs[:2*count], *local_rhs, rhs[3*count:]]
        reduced_bounds = bounds[:controls]+[bounds[-1]]
        reduced_cost = cost[keep]
        history = []; generated = set()
        for iteration in range(15):
            remaining = 240.-(time.monotonic()-start)
            if remaining <= 0.:
                break
            result = cuts.solve_with_cuts(reduced_cost, fixed, target, reduced_bounds,
                                           deadline=min(90., remaining), max_rounds=45)
            row = dict(iteration=iteration, status=int(result.status),
                       active_program_rows=fixed.shape[0], inner_history=result.cut_history)
            history.append(row)
            if not result.success:
                result['cut_history'] = history; result['total_rows'] = matrix.shape[0]
                return result
            z = result.x
            lower = (lower_constant+lower_matrix@z).reshape(nt, nx)
            upper = (upper_constant+upper_matrix@z).reshape(2*nt, nx)
            lo = lower.max(axis=0); hi = upper.min(axis=0)
            gap = lo-hi
            row['maximum_temporal_pair_gap'] = float(np.maximum(gap, 0.).max())
            if np.max(gap) <= 2e-8:
                a = (np.maximum(lo, 0.)+hi)/2
                result.x = np.r_[z[:controls], a, z[-1]]
                result['cut_history'] = history; result['total_rows'] = matrix.shape[0]
                return result
            # Multiple extreme time pairs resolve the persistent spatial
            # grading conflict without introducing one LP variable per x.
            lows = np.argsort(lower, axis=0)[-3:]
            highs = np.argsort(upper, axis=0)[:3]
            pairs = []
            for j in np.flatnonzero(gap > 2e-8):
                for ti in lows[:, j]:
                    for ui in highs[:, j]:
                        key = (int(ti*nx+j), int(ui*nx+j))
                        if key not in generated:
                            generated.add(key); pairs.append(key)
            if not pairs:
                break
            li, ui = np.array(pairs).T
            fixed = vstack([fixed, lower_matrix[li]-upper_matrix[ui]], format='csr')
            target = np.r_[target, upper_constant[ui]-lower_constant[li]]
        return OptimizeResult(success=False, status=1, message='temporal separation budget reached',
                              cut_history=history, total_rows=matrix.shape[0])

    cuts.linprog = record
    gate.solve_with_cuts = eliminate
    gate.OUTPUT = OUTPUT
    result = gate.evaluate(intervals)
    if result['status'] == 2 and not captured.get('valid'):
        raise ArithmeticError('finite-family infeasibility lacks a checked certificate')
    result['certificate'] = captured
    result['amplitude_elimination'] = 'all-time lower/upper compatibility at each spatial node'
    write_json(OUTPUT/f'n{intervals}_summary.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if OUTPUT.exists():
        raise RuntimeError('preserve completed eliminated-amplitude evidence')
    previous = BASE/'graded_vortex_support_gate/manifest.json'
    hashes = dict(json.loads(previous.read_text())['input_sha256'])
    for source in [previous, Path(__file__),
                   ROOT/'toolkit/adm_harness_cli/adm_harness/lp_infeasibility_certificate.py']:
        hashes[str(source.relative_to(ROOT))] = sha256_file(source)
    for relative, expected in hashes.items():
        if sha256_file(ROOT/relative) != expected:
            raise RuntimeError('changed eliminated-amplitude input: '+relative)
    OUTPUT.mkdir()
    with ProcessPoolExecutor(max_workers=max(1, min(args.workers, 2)),
                             mp_context=multiprocessing.get_context('spawn')) as pool:
        results = list(pool.map(evaluate, [128, 256]))
    write_json(OUTPUT/'summary.json', dict(cases=results))
    write_json(OUTPUT/'manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        input_sha256=hashes,
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__ == '__main__':
    main()
