"""Independently checkable nonnegative-constraint certificate for an LP."""
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix, vstack


def certificate(matrix, rhs, bounds):
    matrix=csr_matrix(matrix);rhs=np.asarray(rhs);dimension=matrix.shape[1]
    extra=[];values=[];labels=[]
    for j,(lower,upper) in enumerate(bounds):
        if lower is not None:
            row=np.zeros(dimension);row[j]=-1.
            extra.append(row);values.append(-lower);labels.append((j,'lower'))
        if upper is not None:
            row=np.zeros(dimension);row[j]=1.
            extra.append(row);values.append(upper);labels.append((j,'upper'))
    combined=vstack([matrix,csr_matrix(np.array(extra).reshape(-1,dimension))],format='csr')
    values=np.r_[rhs,values]
    equations=vstack([combined.T,csr_matrix(np.ones((1,len(values))))],format='csr')
    result=linprog(values,A_eq=equations,b_eq=np.r_[np.zeros(dimension),1.],
        bounds=(0.,None),method='highs',options={'primal_feasibility_tolerance':1e-9,
                                             'dual_feasibility_tolerance':1e-9})
    if not result.success:return dict(valid=False,solver_status=int(result.status))
    selected=np.flatnonzero(result.x>1e-14)
    a=combined[selected].toarray();b=values[selected];weights=result.x[selected]
    balance=a.T@weights;margin=float(b@weights)
    residual=float(abs(balance).max())
    return dict(valid=bool(residual<1e-9 and margin<-1e-8 and weights.min()>=0),
        balance_residual=residual,weighted_rhs=margin,weight_sum=float(weights.sum()),
        matrix=a,rhs=b,weights=weights,selected_rows=selected,original_row_count=matrix.shape[0],
        appended_bound_labels=labels)
