"""Prototype curvature engine (development copy; the final script inlines it)."""
import time
import random
import sympy as sp
from sympy.core.function import AppliedUndef

_JET = {}


def _jet_name(d):
    if isinstance(d, sp.Derivative):
        f = d.expr
        return f.func.__name__ + '_' + ''.join(str(v) * c for v, c in d.variable_count)
    return d.func.__name__


def jetify(expr):
    """Replace every applied undefined function and its derivatives by a plain symbol."""
    expr = sp.sympify(expr)
    reps = {}
    for d in expr.atoms(sp.Derivative):
        if d not in _JET:
            _JET[d] = sp.Symbol(_jet_name(d), real=True)
        reps[d] = _JET[d]
    expr = expr.xreplace(reps)
    reps = {}
    for f in expr.atoms(AppliedUndef):
        if f not in _JET:
            _JET[f] = sp.Symbol(_jet_name(f), real=True)
        reps[f] = _JET[f]
    return expr.xreplace(reps)


def J(expr):
    return jetify(expr)


def curvature(g, X, riemann=False):
    """Einstein tensor (and optionally Riemann) of g in coordinates X, as rational
    functions of jet symbols.  MTW conventions:
    R^a_{bcd} = d_c Gam^a_{bd} - d_d Gam^a_{bc} + Gam^a_{ec}Gam^e_{bd} - Gam^a_{ed}Gam^e_{bc},
    R_{bd} = R^a_{bad},  G_{ab} = R_{ab} - (1/2) R g_{ab}.
    Only metric components are differentiated (to second order); every Christoffel
    derivative is assembled algebraically."""
    n = len(X)
    dg_raw = [g.diff(x) for x in X]
    ddg_raw = [[dg_raw[c].diff(X[d]) for d in range(n)] for c in range(n)]
    gJ = g.applyfunc(J)
    ginv = gJ.inv(method='LU').applyfunc(lambda e: sp.cancel(sp.together(e)))
    dg = [m.applyfunc(J) for m in dg_raw]
    ddg = [[m.applyfunc(J) for m in row] for row in ddg_raw]
    dginv = [(-(ginv * dg[c] * ginv)).applyfunc(sp.expand) for c in range(n)]
    Gam = [[[sp.expand(sum(ginv[a, d] * (dg[b][d, c] + dg[c][d, b] - dg[d][b, c]) for d in range(n)) / 2)
             for c in range(n)] for b in range(n)] for a in range(n)]
    dGam = [[[[sp.expand(sum(dginv[e][a, d] * (dg[b][d, c] + dg[c][d, b] - dg[d][b, c])
                             + ginv[a, d] * (ddg[e][b][d, c] + ddg[e][c][d, b] - ddg[e][d][b, c])
                             for d in range(n)) / 2)
               for c in range(n)] for b in range(n)] for a in range(n)] for e in range(n)]
    Ric = sp.zeros(n, n)
    for b in range(n):
        for d in range(b, n):
            val = 0
            for a in range(n):
                val += dGam[a][a][b][d] - dGam[d][a][b][a]
                for e in range(n):
                    val += Gam[a][e][a] * Gam[e][b][d] - Gam[a][e][d] * Gam[e][b][a]
            val = sp.expand(val)
            Ric[b, d] = val
            Ric[d, b] = val
    Rs = sp.expand(sum(ginv[b, d] * Ric[b, d] for b in range(n) for d in range(n)))
    G = (Ric - Rs * gJ / 2).applyfunc(sp.expand)
    out = dict(g=gJ, ginv=ginv, Gamma=Gam, Ric=Ric, R=Rs, G=G)
    if riemann:
        Riem = {}
        for a in range(n):
            for b in range(n):
                for c in range(n):
                    for d in range(c + 1, n):
                        val = dGam[c][a][b][d] - dGam[d][a][b][c]
                        for e in range(n):
                            val += Gam[a][e][c] * Gam[e][b][d] - Gam[a][e][d] * Gam[e][b][c]
                        Riem[(a, b, c, d)] = sp.expand(val)
        out['Riem'] = Riem
    return out


def project(G, frame):
    """Frame components G(e_i, e_j); frame = list of upper-index component lists."""
    m = len(frame)
    n = G.shape[0]
    fr = [[J(c) for c in v] for v in frame]
    P = sp.zeros(m, m)
    for i in range(m):
        for j in range(i, m):
            v = sp.expand(sum(fr[i][mu] * fr[j][nu] * G[mu, nu] for mu in range(n) for nu in range(n)))
            P[i, j] = v
            P[j, i] = v
    return P


def is_zero(expr):
    e = sp.together(J(expr))
    return sp.expand(sp.numer(e)) == 0


def canon(expr):
    return sp.cancel(sp.together(J(expr)))
