"""Independent reconstruction of minimal positive wave supersolutions."""
import numpy as np


def least_upwind_supersolution(generator, source_rate, initial):
    """Solve the triangular obstacle problem z>=initial, Gz+source<=0.

    A one-direction upwind operator has an acyclic spatial dependency.
    Its least constant positive supersolution follows from one substitution.
    """
    g=np.asarray(generator); source_rate=np.asarray(source_rate); initial=np.asarray(initial)
    if np.any(np.diag(g)>=0) or min(source_rate.min(),initial.min())<0:
        raise ValueError('a stable positive upwind system is required')
    if not np.any(np.triu(g,1)):
        order=range(len(g))
    elif not np.any(np.tril(g,-1)):
        order=range(len(g)-1,-1,-1)
    else:
        raise ValueError('the wave envelope requires one-direction spatial transport')
    z=np.zeros(len(g))
    for j in order: z[j]=max(initial[j],(source_rate[j]+g[j]@z)/(-g[j,j]))
    return z
