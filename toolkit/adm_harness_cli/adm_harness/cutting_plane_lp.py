"""Constraint generation for linear programs with few controls and many rows."""
import time
import numpy as np
from scipy.optimize import OptimizeResult, linprog
from scipy.sparse import csr_matrix


def solve_with_cuts(cost, matrix, rhs, bounds, *, deadline=150., initial_count=1800,
                    add_count=400, tolerance=2e-8, max_rounds=30):
    matrix=csr_matrix(matrix);rhs=np.asarray(rhs);start=time.monotonic()
    scale=np.maximum(np.asarray(abs(matrix).max(axis=1).toarray()).ravel(),1e-12)
    scaled=matrix.multiply((1/scale)[:,None]).tocsr();target=rhs/scale
    selected=np.unique(np.linspace(0,len(rhs)-1,min(initial_count,len(rhs)),dtype=int))
    history=[]
    for iteration in range(max_rounds):
        remaining=deadline-(time.monotonic()-start)
        if remaining<=0:break
        result=linprog(cost,A_ub=scaled[selected],b_ub=target[selected],bounds=bounds,
            method='highs-ds',options={'time_limit':min(30.,remaining),
            'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
        row=dict(iteration=iteration,active_rows=len(selected),status=int(result.status))
        if not result.success:
            history.append(row);result['cut_history']=history
            result['total_rows']=len(rhs)
            return result
        raw=matrix@result.x-rhs;normalized=raw/scale
        violation=np.maximum(raw,0);worst=float(violation.max())
        row['maximum_full_violation']=worst;history.append(row)
        if worst<=tolerance:
            result['cut_history']=history;result['total_rows']=len(rhs)
            result['maximum_full_violation']=worst
            return result
        bad=np.flatnonzero(raw>tolerance)
        order=np.argsort(normalized[bad])[-add_count:]
        fresh=bad[order]
        # Include the largest original-unit violation as well as scaled cuts.
        fresh=np.r_[fresh,int(np.argmax(violation))]
        updated=np.union1d(selected,fresh)
        if len(updated)==len(selected):
            return OptimizeResult(success=False,status=4,message='active rows retain an original-unit violation',
                                  cut_history=history,total_rows=len(rhs))
        selected=updated
    return OptimizeResult(success=False,status=1,message='constraint-generation budget reached',
                          cut_history=history,total_rows=len(rhs))
