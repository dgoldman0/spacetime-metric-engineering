"""Explicitly retain native HiGHS LP primals after independent feasibility checks.

This adapter serves an already fixed budget with a secondary inventory cost.
Its success flag means primal feasibility, including on an unfinished solve;
optimality_certified separately records native optimal termination. It must
not replace an optimization whose optimum supplies the claimed bound.

The private SciPy/HiGHS binding is intentionally isolated here. Process-global
thread scheduling is left untouched; request threads only in a fresh worker.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import OptimizeResult
from scipy.sparse import csr_matrix, vstack


def _bounds(bounds, n):
    if bounds is None:
        bounds = (0., None)
    raw = np.asarray(bounds, dtype=object)
    if raw.shape == (2,):
        raw = np.broadcast_to(raw, (n, 2))
    if raw.shape != (n, 2):
        raise ValueError('bounds must be one pair or one pair per variable')
    lower = np.array([-np.inf if value is None else float(value) for value in raw[:, 0]])
    upper = np.array([np.inf if value is None else float(value) for value in raw[:, 1]])
    if (np.isnan(lower).any() or np.isnan(upper).any() or np.any(lower > upper)
            or np.isposinf(lower).any() or np.isneginf(upper).any()):
        raise ValueError('ordered finite-or-open variable bounds required')
    return lower, upper


def _rows(matrix, rhs, n, name):
    if matrix is None:
        if rhs is not None and np.size(rhs):
            raise ValueError(name+' requires its matrix')
        return csr_matrix((0, n), dtype=float), np.empty(0)
    result = csr_matrix(matrix, dtype=float, copy=True)
    values = np.asarray(rhs, dtype=float)
    if (result.shape[1] != n or values.shape != (result.shape[0],)
            or not np.isfinite(result.data).all() or not np.isfinite(values).all()):
        raise ValueError(name+' requires finite matching matrix and right-hand side')
    return result, values


def _problem(c, A_ub, b_ub, A_eq, b_eq, bounds):
    cost = np.asarray(c, dtype=float)
    if cost.ndim != 1 or not len(cost) or not np.isfinite(cost).all():
        raise ValueError('finite nonempty one-dimensional objective required')
    au, bu = _rows(A_ub, b_ub, len(cost), 'A_ub/b_ub')
    ae, be = _rows(A_eq, b_eq, len(cost), 'A_eq/b_eq')
    lower, upper = _bounds(bounds, len(cost))
    return cost, au, bu, ae, be, lower, upper


def _check(x, problem, tolerance):
    cost, au, bu, ae, be, lower, upper = problem
    candidate = np.asarray(x, dtype=float) if x is not None else np.empty(0)
    finite = candidate.shape == cost.shape and np.isfinite(candidate).all()
    if not finite:
        return OptimizeResult(verified_feasible=False, candidate_finite=False,
            equality_residual=np.inf, inequality_violation=np.inf,
            lower_bound_violation=np.inf, upper_bound_violation=np.inf,
            maximum_feasibility_violation=np.inf, con=None, slack=None,
            lower_residual=None, upper_residual=None)
    # These are the ORIGINAL supplied rows, before any native presolve,
    # scaling, small-coefficient removal, or other solver transformation.
    with np.errstate(over='ignore', invalid='ignore'):
        con = be-ae@candidate
        slack = bu-au@candidate
        lr, ur = candidate-lower, upper-candidate
    finite_rows = np.isfinite(con).all() and np.isfinite(slack).all()
    eq = float(np.max(abs(con), initial=0.)) if finite_rows else np.inf
    ine = float(np.max(-slack, initial=0.)) if finite_rows else np.inf
    low = float(np.max(-lr, initial=0.))
    up = float(np.max(-ur, initial=0.))
    maximum = max(eq, ine, low, up)
    return OptimizeResult(verified_feasible=bool(finite_rows and maximum <= tolerance),
        candidate_finite=True, equality_residual=eq, inequality_violation=ine,
        lower_bound_violation=low, upper_bound_violation=up,
        maximum_feasibility_violation=maximum, con=con, slack=slack,
        lower_residual=lr, upper_residual=ur)


def verify_candidate(c, x, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
                     bounds=(0., None), *, feasibility_tolerance=2e-7):
    """Check a candidate directly against every supplied row and variable bound."""
    if not np.isfinite(feasibility_tolerance) or not 0 < feasibility_tolerance <= 2e-7:
        raise ValueError('feasibility_tolerance must be positive and at most 2e-7')
    problem = _problem(c, A_ub, b_ub, A_eq, b_eq, bounds)
    return _check(x, problem, feasibility_tolerance)


def _verified_result(problem, x, *, value_valid, backend_status, backend_message,
                     feasibility_tolerance, nit=0, crossover_nit=0,
                     backend_status_code=None, run_status=None, backend_run_ok=True):
    check = _check(x, problem, feasibility_tolerance)
    # Retain feasible points from ordinary unfinished terminations. A backend
    # load/solve error or infeasible/unbounded declaration stays a failure even
    # if an unexpected stale candidate happens to fit the rows.
    unfinished = {'Unknown', 'Time limit reached', 'Iteration limit reached',
                  'Solution limit reached', 'Bound on objective reached',
                  'Target for objective reached', 'Interrupted by user'}
    eligible = backend_status == 'Optimal' or backend_status in unfinished
    feasible = bool(backend_run_ok and value_valid and eligible and check.verified_feasible)
    optimal = bool(feasible and backend_status == 'Optimal')
    status = (0 if backend_status == 'Optimal' else
              1 if backend_status in unfinished-{'Unknown'} else
              2 if backend_status == 'Infeasible' else
              3 if backend_status == 'Unbounded' else 4)
    if not backend_run_ok or (backend_status == 'Optimal' and not feasible):
        status = 4
    point = np.asarray(x, dtype=float).copy() if feasible else None
    message = (backend_message+'; original matrices and bounds verify a feasible primal'
               if feasible else backend_message+'; no independently verified admissible primal retained')
    if feasible and not optimal:
        message += '; inventory optimality is uncertified'
    if not backend_run_ok:
        message += '; backend model loading or solving returned an error'
    result = OptimizeResult(success=feasible, x=point,
        fun=float(problem[0]@point) if feasible else None, status=status, message=message,
        nit=int(nit), crossover_nit=int(crossover_nit),
        optimality_certified=optimal, feasibility_only_success=feasible and not optimal,
        backend_model_status=backend_status, backend_model_status_code=backend_status_code,
        backend_run_status=run_status, backend_run_ok=bool(backend_run_ok),
        backend_value_valid=bool(value_valid),
        feasibility_tolerance=float(feasibility_tolerance), **check)
    result.lower = OptimizeResult(residual=check.lower_residual)
    result.upper = OptimizeResult(residual=check.upper_residual)
    return result


def checked_highs_result(c, x, *, value_valid, backend_status, A_ub=None, b_ub=None,
                        A_eq=None, b_eq=None, bounds=(0., None),
                        feasibility_tolerance=2e-7, backend_run_ok=True,
                        backend_run_status=None):
    """Testable native-result boundary; backend claims never replace row checks."""
    if not np.isfinite(feasibility_tolerance) or not 0 < feasibility_tolerance <= 2e-7:
        raise ValueError('feasibility_tolerance must be positive and at most 2e-7')
    if not isinstance(backend_run_ok, (bool, np.bool_)):
        raise ValueError('backend_run_ok must be a boolean')
    problem = _problem(c, A_ub, b_ub, A_eq, b_eq, bounds)
    return _verified_result(problem, x, value_valid=value_valid,
        backend_status=backend_status, backend_message=backend_status,
        feasibility_tolerance=feasibility_tolerance, backend_run_ok=backend_run_ok,
        run_status=backend_run_status)


def linprog_feasible(c, A_ub=None, b_ub=None, A_eq=None, b_eq=None,
                     bounds=(0., None), *, method='highs-ipm', options=None,
                     feasibility_tolerance=2e-7):
    """Run a continuous LP and retain independently verified unfinished primals.

    success certifies ONLY the stated absolute primal tolerance. status keeps
    the SciPy-style termination category, so success can be True with status
    1 or 4. optimality_certified requires native Optimal termination as well.
    No exact-arithmetic dual certificate is produced.
    """
    if not np.isfinite(feasibility_tolerance) or not 0 < feasibility_tolerance <= 2e-7:
        raise ValueError('feasibility_tolerance must be positive and at most 2e-7')
    if method not in ('highs-ipm', 'highs-ds'):
        raise ValueError('method must be highs-ipm or highs-ds')
    problem = _problem(c, A_ub, b_ub, A_eq, b_eq, bounds)
    cost, au, bu, ae, be, lower, upper = problem
    # The installed private binding is isolated here; unsupported versions
    # fail explicitly instead of falling back to a result-discarding wrapper.
    from scipy.optimize._highspy import _core as core
    highs = core._Highs()
    supplied = {} if options is None else dict(options)
    settings = {'output_flag': False, 'solver': 'ipm' if method == 'highs-ipm' else 'simplex'}
    if 'solver' in supplied and supplied['solver'] != settings['solver']:
        raise ValueError('native solver option conflicts with requested method')
    if 'threads' in supplied and (isinstance(supplied['threads'], (bool, np.bool_))
            or not isinstance(supplied['threads'], (int, np.integer)) or supplied['threads'] < 1):
        raise ValueError('threads must be a positive integer when explicitly supplied')
    if 'disp' in supplied:
        supplied['output_flag'] = bool(supplied.pop('disp'))
    if 'maxiter' in supplied:
        key = 'ipm_iteration_limit' if method == 'highs-ipm' else 'simplex_iteration_limit'
        supplied[key] = supplied.pop('maxiter')
    settings.update(supplied)
    for key, value in settings.items():
        if value is None:
            continue
        if isinstance(value, np.generic):
            value = value.item()
        if key in ('presolve', 'parallel', 'run_crossover') and isinstance(value, bool):
            value = 'on' if value else 'off'
        if highs.setOptionValue(key, value) == core.HighsStatus.kError:
            raise ValueError('native HiGHS rejected option '+repr(key)+'='+repr(value))
    matrix = vstack([au, ae], format='csc')
    matrix.sum_duplicates(); matrix.sort_indices()
    if max(matrix.shape+(matrix.nnz,)) > np.iinfo(np.int32).max:
        raise ValueError('problem exceeds this native binding index range')
    lp = core.HighsLp()
    lp.num_col_, lp.num_row_ = matrix.shape[1], matrix.shape[0]
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = cost, lower, upper
    lp.row_lower_ = np.r_[np.full(len(bu), -np.inf), be]
    lp.row_upper_ = np.r_[bu, be]
    lp.a_matrix_.num_col_, lp.a_matrix_.num_row_ = matrix.shape[1], matrix.shape[0]
    lp.a_matrix_.format_ = core.MatrixFormat.kColwise
    lp.a_matrix_.start_ = matrix.indptr.astype(np.int32)
    lp.a_matrix_.index_ = matrix.indices.astype(np.int32)
    lp.a_matrix_.value_ = matrix.data
    load_status = highs.passModel(lp)
    run_status = highs.run() if load_status != core.HighsStatus.kError else load_status
    model_status = highs.getModelStatus()
    status_name = highs.modelStatusToString(model_status)
    info, solution = highs.getInfo(), highs.getSolution()
    result = _verified_result(problem, solution.col_value,
        value_valid=solution.value_valid,
        backend_run_ok=(load_status != core.HighsStatus.kError and run_status != core.HighsStatus.kError),
        backend_status=status_name, backend_message='HiGHS '+status_name,
        feasibility_tolerance=feasibility_tolerance,
        nit=max(info.ipm_iteration_count, info.simplex_iteration_count, 0),
        crossover_nit=max(info.crossover_iteration_count, 0),
        backend_status_code=int(model_status), run_status=int(run_status))
    result.native_version = highs.version()
    result.backend_load_status = int(load_status)
    result.backend_dual_valid = bool(solution.dual_valid)
    result.backend_info_valid = bool(info.valid)
    result.backend_reported_primal_infeasibility = float(info.max_primal_infeasibility)
    result.backend_reported_dual_infeasibility = float(info.max_dual_infeasibility)
    result.requested_method = method
    return result
