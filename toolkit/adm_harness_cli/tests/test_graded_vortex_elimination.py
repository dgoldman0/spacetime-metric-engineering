"""Compare temporal amplitude elimination with an independent full LP."""
from pathlib import Path
import importlib

import numpy as np
import pytest
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


@pytest.mark.parametrize('time_conflict', [False, True])
def test_elimination_preserves_full_program_feasibility(monkeypatch, tmp_path, time_conflict):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    module = importlib.import_module('certify_graded_vortex_gate')
    nx, nt, controls = 3, 4, 29
    count = nx*nt; dim = controls+nx+1
    matrix = np.zeros((10*count, dim)); rhs = np.zeros(10*count)
    low = np.tile(np.arange(nx, dtype=float), (nt, 1))+.2*np.arange(nt)[:, None]
    high = low+(.1 if time_conflict else 1.)
    for i in range(nt):
        for j in range(nx):
            k = i*nx+j
            # Both upper bounds admit a separate A(t,x). Only consistency
            # across time distinguishes the positive and negative controls.
            for block, offset in [(0, 0.), (1, .03)]:
                matrix[block*count+k, controls+j] = 2.
                matrix[block*count+k, 0] = -.4
                rhs[block*count+k] = 2*(high[i, j]+offset)
            matrix[2*count+k, controls+j] = -1.
            matrix[2*count+k, 0] = .2
            rhs[2*count+k] = -low[i, j]
    matrix[3*count:, -1] = -1.
    cost = np.zeros(dim); cost[-1] = 1.
    bounds = [(-1., 1.)]+[(0., 0.)]*(controls-1)+[(0., None)]*(nx+1)
    expected = linprog(cost, A_ub=matrix, b_ub=rhs, bounds=bounds)
    assert expected.success == (not time_conflict)
    original_results = []

    def fixture_evaluate(intervals):
        assert intervals == nx-1
        result = module.gate.solve_with_cuts(cost, csr_matrix(matrix), rhs, bounds)
        original_results.append(result)
        return dict(success=bool(result.success), status=int(result.status), message=result.message)

    monkeypatch.setattr(module, 'OUTPUT', tmp_path)
    monkeypatch.setattr(module.gate, 'OUTPUT', tmp_path)
    monkeypatch.setattr(module.gate, 'evaluate', fixture_evaluate)
    monkeypatch.setattr(module.gate, 'solve_with_cuts', module.gate.solve_with_cuts)
    monkeypatch.setattr(module.cuts, 'linprog', linprog)
    actual = module.evaluate(nx-1)
    assert actual['success'] == expected.success
    if actual['success']:
        assert np.max(matrix@original_results[0].x-rhs) <= 2e-8
    else:
        assert actual['certificate']['valid']
