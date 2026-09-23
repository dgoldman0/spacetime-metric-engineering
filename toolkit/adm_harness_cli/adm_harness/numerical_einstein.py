"""Einstein tensor of a coordinate metric by central differences, as an independent check.

The metric callable returns the 4x4 covariant components at a coordinate
point. First and second partial derivatives are taken by second-order central
differences in the first `varying` coordinates; the remaining coordinates are
Killing directions. Christoffel symbols, their derivatives, the Ricci tensor
and G = Ric - g R/2 follow in closed form from those derivatives.
"""
from __future__ import annotations

import numpy as np


def einstein_fd(metric, x, step: float, varying: int = 4) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    cache = {}

    def at(offset):
        key = tuple(offset)
        if key not in cache:
            cache[key] = np.asarray(metric(x+step*np.asarray(offset, dtype=float)), dtype=float)
        return cache[key]

    zero = (0, 0, 0, 0)
    g = at(zero)
    dg = np.zeros((4, 4, 4))
    ddg = np.zeros((4, 4, 4, 4))
    unit = np.eye(4, dtype=int)
    for k in range(varying):
        plus, minus = tuple(unit[k]), tuple(-unit[k])
        dg[k] = (at(plus)-at(minus))/(2*step)
        ddg[k, k] = (at(plus)-2*g+at(minus))/step**2
        for m in range(k+1, varying):
            pp, pm = tuple(unit[k]+unit[m]), tuple(unit[k]-unit[m])
            mp, mm = tuple(-unit[k]+unit[m]), tuple(-unit[k]-unit[m])
            ddg[k, m] = ddg[m, k] = (at(pp)-at(pm)-at(mp)+at(mm))/(4*step*step)
    inverse = np.linalg.inv(g)
    first_kind = .5*(np.einsum("jmk->mjk", dg)+np.einsum("kmj->mjk", dg)-dg)
    gamma = np.einsum("im,mjk->ijk", inverse, first_kind)
    d_first = .5*(np.einsum("ljmk->lmjk", ddg)+np.einsum("lkmj->lmjk", ddg)-ddg)
    d_inverse = -np.einsum("ia,lab,bm->lim", inverse, dg, inverse)
    d_gamma = np.einsum("lim,mjk->lijk", d_inverse, first_kind)+np.einsum("im,lmjk->lijk", inverse, d_first)
    ricci = (np.einsum("iijk->jk", d_gamma)-np.einsum("kiij->jk", d_gamma)
             + np.einsum("iip,pjk->jk", gamma, gamma)-np.einsum("ikp,pij->jk", gamma, gamma))
    scalar = np.einsum("jk,jk->", inverse, ricci)
    return ricci-.5*g*scalar
