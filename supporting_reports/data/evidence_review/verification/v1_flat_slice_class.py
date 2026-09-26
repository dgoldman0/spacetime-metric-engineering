#!/usr/bin/env python3
"""v1_flat_slice_class.py -- independent verification of the flat-slice (class C0) identities.

Written from scratch with sympy (no code from the active-rail repository or the inventory
scripts).  Run with

    nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
        python3 v1_flat_slice_class.py

Deterministic (fixed seeds).  Runtime about a minute on one core.  Exit status 0 iff
every check came out as recorded in v1_flat_slice_class.md.

Conventions (book, 05_STRUCTURE.md): signature (-,+,+,+); G_ab = 8 pi T_ab; MTW Riemann
R^a_{bcd} = d_c Gam^a_{bd} - d_d Gam^a_{bc} + Gam^a_{ec} Gam^e_{bd} - Gam^a_{ed} Gam^e_{bc},
R_{bd} = R^a_{bad}; K_ij = -(1/2 alpha)(d_t gamma_ij - D_i beta_j - D_j beta_i), so
K = -nabla_mu n^mu;  rho = T(n,n), j_i = -T(n, e_i), S_ij = T(e_i, e_j).

Class C0:  ds^2 = -alpha^2 dt^2 + A^2 (dz + beta dt)^2 + dr^2 + r^2 dphi^2,
alpha, beta, A functions of (t, z, r); frame n = (d_t - beta d_z)/alpha, e_z = d_z/A,
e_r = d_r, e_phi = d_phi/r.  "8 pi T_ab" below always means orthonormal lower components.

Method.  The engine differentiates only metric components (to second order), replaces
every derivative of an undefined function by an independent jet symbol, and assembles
Christoffel symbols, their derivatives, Ricci and Einstein tensors algebraically.  An
identity at an arbitrary point with arbitrary jets is an identity for all C^2 fields.
Each claimed identity is checked (i) symbolically: the numerator of the difference,
brought over a common denominator, expands to zero; and (ii) by exact evaluation at
random rational jets.  Explicit examples are evaluated with mpmath at 40 digits.
"""
import sys
import time
import random
import sympy as sp
import mpmath as mp
import numpy as np
from sympy.core.function import AppliedUndef

mp.mp.dps = 40
T_START = time.time()
RESULTS = []


def say(*a):
    print(*a, flush=True)


def record(item, label, ok, method):
    RESULTS.append((item, label, bool(ok), method))
    say(f"  [{'PASS' if ok else 'FAIL'}] {label}  ({method})")


# =============================================================================
# Engine
# =============================================================================
_JET = {}        # derivative/function object -> symbol
_JET_INV = {}    # symbol -> object
_NAMES = {}      # name -> object


def _jet_symbol(obj):
    if obj in _JET:
        return _JET[obj]
    if isinstance(obj, sp.Derivative):
        base = obj.expr.func.__name__ + '_' + ''.join(str(v) * c for v, c in obj.variable_count)
    else:
        base = obj.func.__name__
    name, k = base, 1
    while name in _NAMES and _NAMES[name] != obj:
        k += 1
        name = f'{base}__{k}'
    _NAMES[name] = obj
    s = sp.Symbol(name, real=True)
    _JET[obj] = s
    _JET_INV[s] = obj
    return s


def J(expr):
    """Replace applied undefined functions and all their derivatives by jet symbols."""
    expr = sp.sympify(expr)
    reps = {d: _jet_symbol(d) for d in expr.atoms(sp.Derivative)}
    expr = expr.xreplace(reps)
    reps = {f: _jet_symbol(f) for f in expr.atoms(AppliedUndef)}
    return expr.xreplace(reps)


def curvature(g, X, riemann=False, at=None):
    """Einstein tensor (and optionally Riemann R^a_{bcd}) as rational functions of jets.
    at: optional {coordinate: value}; the metric and its first and second derivatives are
    evaluated there (after the jets are formed), giving the curvature at that point."""
    n = len(X)
    dg_raw = [g.diff(x) for x in X]
    ddg_raw = [[dg_raw[c].diff(X[d]) for d in range(n)] for c in range(n)]
    ev = (lambda m: m.applyfunc(J).xreplace(at)) if at else (lambda m: m.applyfunc(J))
    gJ = ev(g)
    ginv = gJ.inv(method='LU').applyfunc(lambda e: sp.cancel(sp.together(e)))
    dg = [ev(m) for m in dg_raw]
    ddg = [[ev(m) for m in row] for row in ddg_raw]
    dginv = [(-(ginv * dg[c] * ginv)).applyfunc(sp.expand) for c in range(n)]
    Gam = [[[sp.expand(sum(ginv[a, d] * (dg[b][d, c] + dg[c][d, b] - dg[d][b, c])
                           for d in range(n)) / 2)
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
            Ric[b, d] = Ric[d, b] = sp.expand(val)
    Rs = sp.expand(sum(ginv[b, d] * Ric[b, d] for b in range(n) for d in range(n)))
    G = (Ric - Rs * gJ / 2).applyfunc(sp.expand)
    out = dict(g=gJ, ginv=ginv, Gamma=Gam, dGamma=dGam, Ric=Ric, R=Rs, G=G)
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
    m, n = len(frame), G.shape[0]
    fr = [[J(c) for c in v] for v in frame]
    P = sp.zeros(m, m)
    for i in range(m):
        for j in range(i, m):
            P[i, j] = P[j, i] = sp.expand(sum(fr[i][a] * fr[j][b] * G[a, b]
                                              for a in range(n) for b in range(n)))
    return P


def canon(expr):
    return sp.cancel(sp.together(J(expr)))


def sym_zero(expr):
    e = J(expr)
    if e.atoms(sp.Float):
        raise ValueError('floating-point number inside a symbolic check')
    e = sp.together(e)
    return sp.expand(sp.numer(e)) == 0


POSITIVE = {'alpha', 'A', 'r', 'a', 'al', 'P', 'Q', 'S', 'F', 'C', 'aS', 'alst', 'Ast', 'A0',
            'Cw', 'Aw', 'aw', 'tp', 'u', 'M'}


def probe_zero(expr, seed=2026, trials=3):
    e = J(expr)
    syms = sorted(e.free_symbols, key=lambda s: s.name)
    rng = random.Random(seed)
    done = 0
    attempts = 0
    while done < trials and attempts < 20:
        attempts += 1
        vals = {}
        for s in syms:
            if s.name.split('__')[0] in POSITIVE or s.is_positive:
                vals[s] = sp.Rational(rng.randint(3, 29), rng.randint(2, 9))
            else:
                k = rng.randint(-19, 19)
                vals[s] = sp.Rational(k if k else 1, rng.randint(1, 9))
        v = e.xreplace(vals)
        if v.has(sp.zoo, sp.nan, sp.oo):
            continue
        v = sp.nsimplify(v)
        if v != 0:
            return False
        done += 1
    return done == trials


def check_identity(item, label, lhs, rhs=0):
    d = lhs - rhs
    ok_s = sym_zero(d)
    ok_p = probe_zero(d)
    record(item, label, ok_s and ok_p, 'symbolic + exact rational probe')
    return ok_s and ok_p


def check_nonzero(item, label, expr):
    """Negative control: expression must NOT vanish identically."""
    ok = not sym_zero(expr)
    record(item, label, ok, 'symbolic (expected nonzero)')
    return ok


def eval_jets(expr, fields, point, dps=40):
    """Evaluate a jetified expression on explicit fields at a point.
    fields: {AppliedUndef object: explicit sympy expression in the same arguments}
    point:  {coordinate symbol: value}"""
    e = J(expr)
    vals = {}
    for s in e.free_symbols:
        if s in _JET_INV:
            obj = _JET_INV[s]
            if isinstance(obj, sp.Derivative):
                f = obj.expr
                vs = [v for v, c in obj.variable_count for _ in range(c)]
                ex = sp.diff(fields[f], *vs)
            else:
                ex = fields[obj]
            vals[s] = sp.N(ex.xreplace(point), dps)
        else:
            vals[s] = sp.N(point[s], dps)
    return mp.mpf(str(sp.N(e.xreplace(vals), dps)))


def he_type(Tlow, tol=mp.mpf('1e-25')):
    """Hawking-Ellis class of an orthonormal lower-index tensor (index 0 = n)."""
    n = Tlow.rows
    eta = mp.diag([-1] + [1] * (n - 1))
    M = eta * Tlow
    E, ER = mp.eig(M)
    scale = max(abs(x) for x in Tlow) or mp.mpf(1)
    if max(abs(mp.im(x)) for x in E) > tol * scale:
        return 'IV', E
    for k in range(n):
        v = [mp.re(ER[i, k]) for i in range(n)]
        nrm = -v[0] ** 2 + sum(x ** 2 for x in v[1:])
        if nrm < -tol * sum(x ** 2 for x in v):
            return 'I', E
    return 'degenerate', E


# =============================================================================
# Coordinates and the C0 family
# =============================================================================
t, z, ph = sp.symbols('t z phi', real=True)
r = sp.Symbol('r', positive=True)
XC = (t, z, r, ph)
alpha = sp.Function('alpha')(t, z, r)
beta = sp.Function('beta')(t, z, r)
Afun = sp.Function('A')(t, z, r)
D = sp.diff


def c0_metric(al, be, A=1, C=None):
    A = sp.sympify(A)
    C = r if C is None else sp.sympify(C)
    return sp.Matrix([[-al ** 2 + A ** 2 * be ** 2, A ** 2 * be, 0, 0],
                      [A ** 2 * be, A ** 2, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, C ** 2]])


def c0_frame(al, be, A=1, C=None):
    A = sp.sympify(A)
    C = r if C is None else sp.sympify(C)
    return [[1 / al, -be / al, 0, 0], [0, 1 / A, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1 / C]]


def lap_perp(f):
    return D(f, r, 2) + D(f, r) / r


N_, Z_, R_, P_ = 0, 1, 2, 3
CACHE = {}


def c0_tensor():
    if 'c0' not in CACHE:
        out = curvature(c0_metric(alpha, beta), XC, riemann=True)
        CACHE['c0'] = (project(out['G'], c0_frame(alpha, beta)), out)
    return CACHE['c0']


def c0A_tensor():
    if 'c0A' not in CACHE:
        out = curvature(c0_metric(alpha, beta, Afun), XC)
        CACHE['c0A'] = (project(out['G'], c0_frame(alpha, beta, Afun)), out)
    return CACHE['c0A']


# shorthand of the section 3.2 table
s_ = D(beta, r) / alpha                      # proper radial shear
K_ = D(beta, z) / alpha                      # K_zz = trace of extrinsic curvature
nop = lambda f: (D(f, t) - beta * D(f, z)) / alpha   # n(f)
Q_ = nop(K_) - K_ ** 2


# =============================================================================
# Step 0: validation of the engine
# =============================================================================
def step0():
    item = 'Step 0'
    say('\n=== Step 0: engine validation ===')
    # Schwarzschild in Painleve-Gullstrand form
    th = sp.Symbol('theta', real=True)
    B = sp.Function('B')(r)
    g = sp.Matrix([[-1 + B ** 2, B, 0, 0], [B, 1, 0, 0], [0, 0, r ** 2, 0],
                   [0, 0, 0, r ** 2 * sp.sin(th) ** 2]])
    out = curvature(g, (t, r, th, ph), riemann=True)
    Bs, Br, Brr = J(B), J(D(B, r)), J(D(B, r, 2))
    sub = {Br: -Bs / (2 * r), Brr: sp.Rational(3, 4) * Bs / r ** 2}   # B = sqrt(2M/r)
    Gv = out['G'].applyfunc(lambda e: sp.cancel(sp.together(e.xreplace(sub))))
    record(item, 'Schwarzschild (Painleve-Gullstrand, flat slices, beta=sqrt(2M/r)): G_ab = 0',
           Gv == sp.zeros(4, 4), 'symbolic')
    Rt = sp.cancel(out['Riem'][(0, 1, 0, 1)].xreplace(sub))
    record(item, f'  control: spacetime is curved, R^t_(rtr) = {Rt} = 2M/r^3', Rt == Bs ** 2 / r ** 2,
           'symbolic')
    # FRW
    x, y = sp.symbols('x y', real=True)
    a = sp.Function('a')(t)
    out = curvature(sp.diag(-1, a ** 2, a ** 2, a ** 2), (t, x, y, z))
    a0, at, att = J(a), J(D(a, t)), J(D(a, t, 2))
    H = at / a0
    check_identity(item, 'FRW: G_tt = 3H^2', out['G'][0, 0], 3 * H ** 2)
    check_identity(item, 'FRW: G_xx/a^2 = -(2 a_tt/a + H^2)', out['G'][1, 1] / a0 ** 2,
                   -(2 * att / a0 + H ** 2))
    tp = sp.Symbol('tp', positive=True)
    H0 = sp.Symbol('H0', positive=True)
    cases = [('dust a=t^(2/3)', {at: sp.Rational(2, 3) * a0 / tp, att: -sp.Rational(2, 9) * a0 / tp ** 2}, 0),
             ('radiation a=t^(1/2)', {at: a0 / (2 * tp), att: -a0 / (4 * tp ** 2)}, sp.Rational(1, 3)),
             ('de Sitter a=exp(H0 t)', {at: H0 * a0, att: H0 ** 2 * a0}, -1)]
    for name, sb, w in cases:
        rho = sp.cancel(out['G'][0, 0].xreplace(sb) / (8 * sp.pi))
        p = sp.cancel(out['G'][1, 1].xreplace(sb) / a0 ** 2 / (8 * sp.pi))
        HH = sp.cancel(H.xreplace(sb))
        ok = sp.cancel(rho - 3 * HH ** 2 / (8 * sp.pi)) == 0 and sp.cancel(p - w * rho) == 0
        record(item, f'FRW {name}: rho = 3H^2/8pi = {rho}, p = {w} rho', ok, 'symbolic')
    # Alcubierre
    Bx = sp.Function('Bx')(t, x, y, z)
    g = sp.Matrix([[-1 + Bx ** 2, Bx, 0, 0], [Bx, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    out = curvature(g, (t, x, y, z))
    Gnn = project(out['G'], [[1, -Bx, 0, 0]])[0, 0]
    check_identity(item, 'Alcubierre metric (beta^x = Bx(t,x,y,z)): G(n,n) = -(Bx_y^2 + Bx_z^2)/4',
                   Gnn, -(D(Bx, y) ** 2 + D(Bx, z) ** 2) / 4)
    vs, sg, Rb = sp.Rational(3, 2), sp.Integer(8), sp.Integer(1)
    rs = sp.sqrt((x - vs * t) ** 2 + y ** 2 + z ** 2)
    fq = lambda q: (sp.tanh(sg * (q + Rb)) - sp.tanh(sg * (q - Rb))) / (2 * sp.tanh(sg * Rb))
    qq = sp.Symbol('q', positive=True)
    fprime = sp.lambdify(qq, sp.diff(fq(qq), qq), 'mpmath')
    rng = random.Random(7)
    worst = mp.mpf(0)
    for k in range(4):
        P = {t: sp.Rational(rng.randint(-9, 9), 10), x: sp.Rational(rng.randint(-14, 14), 10),
             y: sp.Rational(rng.randint(-11, 11), 10), z: sp.Rational(rng.randint(-11, 11), 10)}
        rho_eng = eval_jets(Gnn, {Bx: -vs * fq(rs)}, P) / (8 * mp.pi)
        rsv = mp.sqrt((mp.mpf(str(P[x])) - vs * mp.mpf(str(P[t]))) ** 2 + mp.mpf(str(P[y])) ** 2
                      + mp.mpf(str(P[z])) ** 2)
        rho_alc = -(1 / (8 * mp.pi)) * vs ** 2 * (mp.mpf(str(P[y])) ** 2 + mp.mpf(str(P[z])) ** 2) \
            / (4 * rsv ** 2) * fprime(rsv) ** 2
        worst = max(worst, abs(rho_eng - rho_alc) / max(abs(rho_alc), mp.mpf('1e-30')))
    record(item, f'Alcubierre 1994 eq. (19), tanh profile (v_s=3/2, sigma=8, R=1), 4 random events: '
           f'max relative difference {mp.nstr(worst, 3)}', worst < mp.mpf('1e-30'), 'mpmath 40 digits')


# =============================================================================
# Item 1: complete orthonormal tensor of C0 with A = 1 (inventory 3.2)
# =============================================================================
def item1():
    item = 'Item 1'
    say('\n=== Item 1: complete C0 tensor (A = 1) ===')
    T8, out = c0_tensor()
    table = {
        (N_, N_): -s_ ** 2 / 4,
        (N_, Z_): -D(r * s_, r) / (2 * r),
        (N_, R_): D(alpha ** 2 * s_, z) / (2 * alpha ** 2) - K_ * D(sp.log(alpha), r),
        (Z_, Z_): lap_perp(alpha) / alpha - 3 * s_ ** 2 / 4,
        (R_, R_): (D(alpha, z, 2) + D(alpha, r) / r) / alpha + s_ ** 2 / 4 + Q_,
        (P_, P_): (D(alpha, r, 2) + D(alpha, z, 2)) / alpha - s_ ** 2 / 4 + Q_,
        (Z_, R_): -D(alpha, r, z) / alpha - nop(s_) / 2 + s_ * K_,
        (N_, P_): 0, (Z_, P_): 0, (R_, P_): 0,
    }
    nm = 'nzr' + 'p'
    for (i, j), c in table.items():
        check_identity(item, f'8 pi T_{nm[i]}{nm[j]} equals the table entry', T8[i, j], c)
    check_identity(item, 'null sum 8 pi (rho + p_z) = Lap_perp(alpha)/alpha - s^2', T8[N_, N_] + T8[Z_, Z_],
                   lap_perp(alpha) / alpha - s_ ** 2)
    check_identity(item, 'null sum 8 pi (rho + p_r) = (alpha_zz + alpha_r/r)/alpha + Q', T8[N_, N_] + T8[R_, R_],
                   (D(alpha, z, 2) + D(alpha, r) / r) / alpha + Q_)
    check_identity(item, 'null sum 8 pi (rho + p_phi) = (alpha_rr + alpha_zz)/alpha - s^2/2 + Q',
                   T8[N_, N_] + T8[P_, P_], (D(alpha, r, 2) + D(alpha, z, 2)) / alpha - s_ ** 2 / 2 + Q_)
    check_identity(item, 'compact flux form: 8 pi T_nr = d_r K - (1/2) d_z s  (K = beta_z/alpha, s = beta_r/alpha)',
                   T8[N_, R_], D(K_, r) - D(s_, z) / 2)
    check_nonzero(item, 'negative control: T_nz with the opposite sign is rejected',
                  T8[N_, Z_] - D(r * s_, r) / (2 * r))
    check_nonzero(item, 'negative control: T_zr without the s*K term is rejected',
                  T8[Z_, R_] - (-D(alpha, r, z) / alpha - nop(s_) / 2))


# =============================================================================
# Item 2: I1 energy density; A != 1
# =============================================================================
def item2():
    item = 'Item 2'
    say('\n=== Item 2: I1 energy density, A = 1 and A != 1 ===')
    T8, _ = c0_tensor()
    check_identity(item, 'A = 1: rho = -(beta_r/alpha)^2/32pi (any alpha(t,z,r), beta(t,z,r))',
                   T8[N_, N_] / (8 * sp.pi), -(D(beta, r) / alpha) ** 2 / (32 * sp.pi))
    # extrinsic curvature from its definition, for general A
    gam = sp.diag(Afun ** 2, 1, r ** 2)          # spatial metric on (z, r, phi)
    Xs = (z, r, ph)
    gi = gam.inv()
    Gam3 = [[[sum(gi[a, d] * (D(gam[d, b], Xs[c]) + D(gam[d, c], Xs[b]) - D(gam[b, c], Xs[d]))
                  for d in range(3)) / 2 for c in range(3)] for b in range(3)] for a in range(3)]
    bup = [beta, 0, 0]
    blow = [sum(gam[i, k] * bup[k] for k in range(3)) for i in range(3)]
    Db = [[D(blow[j], Xs[i]) - sum(Gam3[k][i][j] * blow[k] for k in range(3)) for j in range(3)]
          for i in range(3)]
    Kij = sp.Matrix(3, 3, lambda i, j: -(D(gam[i, j], t) - Db[i][j] - Db[j][i]) / (2 * alpha))
    scale = [Afun, 1, r]                           # orthonormal scale factors of (z, r, phi)
    Khat = sp.Matrix(3, 3, lambda i, j: Kij[i, j] / (scale[i] * scale[j]))
    kA = (D(beta, z) + beta * D(sp.log(Afun), z) - D(sp.log(Afun), t)) / alpha
    sA = Afun * D(beta, r) / alpha
    check_identity(item, 'K_zz(hat) = (beta_z + beta A_z/A - A_t/A)/alpha', Khat[0, 0], kA)
    check_identity(item, 'K_zr(hat) = A beta_r/(2 alpha)', Khat[0, 1], sA / 2)
    check_identity(item, 'K_rr = K_phiphi = K_zphi = K_rphi = 0',
                   Khat[1, 1] ** 2 + Khat[2, 2] ** 2 + Khat[0, 2] ** 2 + Khat[1, 2] ** 2)
    # K = -div n  (book sign convention)
    sqrtg = alpha * Afun * r
    divn = (D(sqrtg * (1 / alpha), t) + D(sqrtg * (-beta / alpha), z)) / sqrtg
    check_identity(item, 'convention check: K = -nabla_mu n^mu', kA, -divn)
    # 3-curvature of the stretched slice
    out3 = curvature(sp.diag(Afun ** 2, 1, r ** 2), Xs)
    check_identity(item, '3R of A^2 dz^2 + dr^2 + r^2 dphi^2 equals -2 Lap_perp(A)/A (A_z, A_t drop out)',
                   out3['R'], -2 * lap_perp(Afun) / Afun)
    T8A, _ = c0A_tensor()
    check_identity(item, 'Hamiltonian constraint 16 pi rho = 3R + K^2 - K_ij K^ij (engine vs ADM)',
                   2 * T8A[N_, N_], out3['R'] + kA ** 2 - (kA ** 2 + 2 * (sA / 2) ** 2))
    check_identity(item, 'A != 1: rho = -(A beta_r/alpha)^2/32pi - Lap_perp(A)/(8 pi A), exact',
                   T8A[N_, N_] / (8 * sp.pi),
                   -sA ** 2 / (32 * sp.pi) - lap_perp(Afun) / (8 * sp.pi * Afun))
    check_nonzero(item, 'the report form -(A beta_r/alpha)^2/32pi alone misses -Lap_perp(A)/(8 pi A)',
                  T8A[N_, N_] / (8 * sp.pi) + sA ** 2 / (32 * sp.pi))
    # report form exact whenever A = A(t, z)
    A2 = sp.Function('A0')(t, z)
    out = curvature(c0_metric(alpha, beta, A2), XC)
    T8b = project(out['G'], c0_frame(alpha, beta, A2))
    check_identity(item, 'A = A0(t,z): rho = -(A0 beta_r/alpha)^2/32pi exactly (report form holds)',
                   T8b[N_, N_] / (8 * sp.pi), -(A2 * D(beta, r) / alpha) ** 2 / (32 * sp.pi))


# =============================================================================
# Item 3: I2 pure lapse (uniform, time-dependent shift, time-dependent lapse) and I18
# =============================================================================
def item3():
    item = 'Item 3'
    say('\n=== Item 3: I2 pure-lapse identity and I18 directional form ===')
    x, y = sp.symbols('x y', real=True)
    X = (t, x, y, z)
    al = sp.Function('al')(t, x, y, z)
    b = [sp.Function(nm)(t) for nm in ('b1', 'b2', 'b3')]
    g = sp.zeros(4, 4)
    g[0, 0] = -al ** 2 + sum(bi ** 2 for bi in b)
    for i in range(3):
        g[0, i + 1] = g[i + 1, 0] = b[i]
        g[i + 1, i + 1] = 1
    out = curvature(g, X)
    fr = [[1 / al, -b[0] / al, -b[1] / al, -b[2] / al], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    T8 = project(out['G'], fr)
    xs = (x, y, z)
    lap = sum(D(al, xi, 2) for xi in xs)
    check_identity(item, 'uniform shift b(t), lapse alpha(t,x,y,z): rho = 0', T8[0, 0])
    check_identity(item, '  j_i = 0 (all three components)', sum(T8[0, i] ** 2 for i in range(1, 4)))
    ok = all(sym_zero(T8[i + 1, j + 1] - ((lap if i == j else 0) - D(al, xs[i], xs[j])) / al)
             for i in range(3) for j in range(i, 3))
    record(item, '  8 pi T_ij = (delta_ij Lap(alpha) - d_i d_j alpha)/alpha (all six components)', ok, 'symbolic')
    e = sp.symbols('e1 e2 e3', real=True)
    Tkk = sum(e[i] * e[j] * T8[i + 1, j + 1] for i in range(3) for j in range(3)) \
        + 2 * sum(e[i] * T8[0, i + 1] for i in range(3)) + T8[0, 0]
    Hee = sum(e[i] * e[j] * D(al, xs[i], xs[j]) for i in range(3) for j in range(3))
    check_identity(item, 'I18: 8 pi T(n+e, n+e) = (|e|^2 Lap(alpha) - e.Hess(alpha).e)/alpha; |e|=1 gives '
                   '(Lap - d_e^2) alpha / alpha', Tkk,
                   ((e[0] ** 2 + e[1] ** 2 + e[2] ** 2) * lap - Hee) / al)
    check_identity(item, '  e = e_z: 8 pi T(n+e_z, n+e_z) = (alpha_xx + alpha_yy)/alpha (transverse Laplacian)',
                   T8[0, 0] + 2 * T8[0, 3] + T8[3, 3], (D(al, x, 2) + D(al, y, 2)) / al)
    # extension: any Killing shift of the flat slice, b(t) + Omega(t) x x (rigid rotation included)
    Om = [sp.Function(nm)(t) for nm in ('Om1', 'Om2', 'Om3')]
    bk = [b[0] + Om[1] * z - Om[2] * y, b[1] + Om[2] * x - Om[0] * z, b[2] + Om[0] * y - Om[1] * x]
    g = sp.zeros(4, 4)
    g[0, 0] = -al ** 2 + sum(bi ** 2 for bi in bk)
    for i in range(3):
        g[0, i + 1] = g[i + 1, 0] = bk[i]
        g[i + 1, i + 1] = 1
    origin = {x: 0, y: 0, z: 0}          # b + Omega x x = (b + Omega x p) + Omega x (x - p): the origin is generic
    outk = curvature(g, X, at=origin)
    frk = [[1 / al, -bk[0] / al, -bk[1] / al, -bk[2] / al], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    frk = [[J(c_).xreplace(origin) for c_ in v_] for v_ in frk]
    Tk = project(outk['G'], frk)
    ok = sym_zero(Tk[0, 0]) and all(sym_zero(Tk[0, i]) for i in range(1, 4)) and all(
        sym_zero(Tk[i + 1, j + 1] - J(((lap if i == j else 0) - D(al, xs[i], xs[j])) / al).xreplace(origin))
        for i in range(3) for j in range(i, 3))
    record(item, 'extension: Killing shift b(t) + Omega(t) x x (translation plus rigid rotation): the same pure-lapse '
           'tensor, rho = j = 0', ok, 'symbolic at a generic point')
    # the shift must be uniform on a time interval: an instantaneously uniform shift adds stress (still Type I)
    T8c, _ = c0_tensor()
    inst = {J(D(beta, v_)): 0 for v_ in (z, r)}
    inst.update({J(D(beta, r, 2)): 0, J(D(beta, r, z)): 0, J(D(beta, z, 2)): 0})
    pl = {(R_, R_): (D(alpha, z, 2) + D(alpha, r) / r) / alpha, (Z_, R_): -D(alpha, r, z) / alpha}
    ok = sym_zero(J(T8c[N_, N_]).xreplace(inst)) and sym_zero(J(T8c[N_, Z_]).xreplace(inst)) and \
        sym_zero(J(T8c[N_, R_]).xreplace(inst)) and \
        sym_zero(J(T8c[R_, R_]).xreplace(inst) - J(pl[(R_, R_)]) - J(D(beta, z, t) / alpha ** 2)) and \
        sym_zero(J(T8c[Z_, R_]).xreplace(inst) - J(pl[(Z_, R_)]) + J(D(beta, r, t) / (2 * alpha ** 2)))
    record(item, 'hypothesis check: shift uniform only at one instant (beta_z = beta_r = 0 on the slice, beta_zt, '
           'beta_rt free): rho = j = 0 (Type I) but 8piT_rr gains beta_zt/alpha^2 and 8piT_zr gains '
           '-beta_rt/(2 alpha^2)', ok, 'symbolic')
    # axisymmetric (cylindrical) version with time-dependent uniform shift
    bt = sp.Function('bt')(t)
    outc = curvature(c0_metric(alpha, bt), XC)
    Tc = project(outc['G'], c0_frame(alpha, bt))
    check_identity(item, 'C0, beta = beta(t): rho = j_z = j_r = 0',
                   Tc[N_, N_] ** 2 + Tc[N_, Z_] ** 2 + Tc[N_, R_] ** 2)
    check_identity(item, '  radial light: 8 pi T(n+e_r) = (alpha_zz + alpha_r/r)/alpha',
                   Tc[N_, N_] + 2 * Tc[N_, R_] + Tc[R_, R_], (D(alpha, z, 2) + D(alpha, r) / r) / alpha)
    check_identity(item, '  axial light: 8 pi T(n+e_z) = (alpha_rr + alpha_r/r)/alpha',
                   Tc[N_, N_] + 2 * Tc[N_, Z_] + Tc[Z_, Z_], lap_perp(alpha) / alpha)
    check_identity(item, '  azimuthal light: 8 pi T(n+e_phi) = (alpha_rr + alpha_zz)/alpha',
                   Tc[N_, N_] + 2 * Tc[N_, P_] + Tc[P_, P_], (D(alpha, r, 2) + D(alpha, z, 2)) / alpha)
    check_identity(item, '  shear stress 8 pi T_zr = -alpha_rz/alpha', Tc[Z_, R_], -D(alpha, r, z) / alpha)
    # on-axis limit for a regular lapse alpha = a0(z) + a2(z) r^2 + a4(z) r^4
    a0, a2, a4 = [sp.Function(nm)(z) for nm in ('a0', 'a2', 'a4')]
    areg = a0 + a2 * r ** 2 + a4 * r ** 4
    lim = sp.limit((D(areg, r, 2) + D(areg, r) / r) / areg, r, 0)
    ok = sp.simplify(lim - 2 * D(areg, r, 2).subs(r, 0) / areg.subs(r, 0)) == 0
    record(item, 'on the axis, axial light: 8 pi T = 2 alpha_rr/alpha, i.e. T(k,k) = alpha_rr/(4 pi alpha)', ok,
           'symbolic limit')
    # radial ray integral for a static z-independent fall alpha(r)
    E = sp.Symbol('E', positive=True)
    ar = sp.Function('aw')(r)
    outw = curvature(c0_metric(ar, 0), XC)
    Gam = outw['Gamma']
    lam_dot_t, lam_dot_r = E / ar ** 2, E / ar      # k = (E/alpha)(n + e_r)
    geo = sp.expand(J(D(lam_dot_r, r) * lam_dot_r) + Gam[2][0][0] * J(lam_dot_t) ** 2
                    + 2 * Gam[2][0][2] * J(lam_dot_t * lam_dot_r) + Gam[2][2][2] * J(lam_dot_r) ** 2)
    record(item, 'radial null geodesic of a static pure-lapse region: k = (E/alpha)(n+e_r) is affine', sym_zero(geo),
           'symbolic geodesic equation')
    Tw = project(outw['G'], c0_frame(ar, 0))
    Tkk = (E / ar) ** 2 * (Tw[N_, N_] + 2 * Tw[N_, R_] + Tw[R_, R_])
    check_identity(item, '  T(k,k) dlambda = (E/8pi) alpha_r/(r alpha^2) dr', Tkk / (8 * sp.pi) * ar / E,
                   E * D(ar, r) / (8 * sp.pi * r * ar ** 2))


# =============================================================================
# Item 4: lapse-only NEC lemma
# =============================================================================
def item4():
    item = 'Item 4'
    say('\n=== Item 4: lapse-only NEC lemma ===')
    x, y = sp.symbols('x y', real=True)
    xs = (x, y, z)
    Rr = sp.sqrt(x ** 2 + y ** 2 + z ** 2)

    def pure_lapse_T(a):
        lap = sum(D(a, v, 2) for v in xs)
        return sp.Matrix(3, 3, lambda i, j: ((lap if i == j else 0) - D(a, xs[i], xs[j])) / a)   # 8 pi T_ij

    al = sp.Function('al')(t, x, y, z)
    T8 = pure_lapse_T(al)
    lap = sum(D(al, v, 2) for v in xs)
    check_identity(item, 'direction sum: alpha * sum_i 8 pi T(n+e_i, n+e_i) = 2 Lap(alpha) (Komar integrand)',
                   al * (T8[0, 0] + T8[1, 1] + T8[2, 2]), 2 * lap)
    # 1/R tail: alpha = 1 - M/R
    M, a = sp.symbols('M a', positive=True)
    al1 = 1 - M / Rr
    Tm = pure_lapse_T(al1)
    pt = {x: 0, y: 0, z: sp.Symbol('Z', positive=True)}
    Zs = pt[z]
    Ttan = sp.simplify(Tm[0, 0].xreplace(pt))      # e_x is tangential at (0,0,Z)
    Trad = sp.simplify(Tm[2, 2].xreplace(pt))
    record(item, f'alpha = 1 - M/R: 8 pi T tangential = {Ttan}, radial = {Trad}',
           sp.simplify(Ttan + M / (Zs ** 3 * (1 - M / Zs))) == 0 and sp.simplify(
               Trad - 2 * M / (Zs ** 3 * (1 - M / Zs))) == 0, 'symbolic')
    # Plummer lapse: Lap alpha > 0 everywhere (Komar density positive), NEC fails for R > sqrt(2) a
    alP = 1 - M / sp.sqrt(Rr ** 2 + a ** 2)
    TP = pure_lapse_T(alP)
    lapP = sp.simplify(sum(D(alP, v, 2) for v in xs))
    Ttan = sp.simplify(TP[0, 0].xreplace(pt))
    ok1 = sp.simplify(lapP - 3 * M * a ** 2 / (Rr ** 2 + a ** 2) ** sp.Rational(5, 2)) == 0
    ok2 = sp.simplify(Ttan * alP.xreplace(pt) - M * (2 * a ** 2 - Zs ** 2) / (Zs ** 2 + a ** 2) ** sp.Rational(5, 2)) == 0
    record(item, 'Plummer lapse 1 - M/sqrt(R^2+a^2): Lap(alpha) = 3Ma^2/(R^2+a^2)^(5/2) > 0 and '
           'tangential 8 pi alpha T = M(2a^2 - R^2)/(R^2+a^2)^(5/2) < 0 for R > sqrt(2) a', ok1 and ok2, 'symbolic')
    # Komar integral of the Plummer lapse: (1/4pi) int Lap(alpha) d^3x = M
    MK = mp.quad(lambda q: 4 * mp.pi * q ** 2 * 3 * mp.mpf('0.3') * 1 / (q ** 2 + 1) ** mp.mpf(2.5), [0, 1, mp.inf]) \
        / (4 * mp.pi)
    record(item, f'  Komar mass of the Plummer lapse (M=0.3, a=1): {mp.nstr(MK, 25)}', abs(MK - mp.mpf('0.3')) < 1e-30,
           'mpmath quadrature')
    # Gaussian dip: direction-summed null energy integrates to zero (zero Komar flux) and changes sign
    lam = sp.Rational(1, 2)
    alG = 1 - lam * sp.exp(-Rr ** 2)
    lapG = sp.simplify(sum(D(alG, v, 2) for v in xs))
    lapG_R = sp.simplify(lapG.xreplace({x: 0, y: 0, z: sp.Symbol('q', positive=True)}))
    q = sp.Symbol('q', positive=True)
    Iflux = sp.integrate(4 * sp.pi * q ** 2 * lapG_R, (q, 0, sp.oo))
    record(item, f'Gaussian dip (lambda=1/2): int Lap(alpha) d^3x = {Iflux}; Lap(alpha) at R=0: '
           f'{lapG_R.subs(q, 0)}, at R=2: {sp.nsimplify(lapG_R.subs(q, 2))}',
           Iflux == 0 and lapG_R.subs(q, 0) > 0 and lapG_R.subs(q, 2) < 0, 'symbolic')
    # counterexamples: unbounded lapse
    alR = 1 + sp.Symbol('g', positive=True) * x
    record(item, 'Rindler lapse 1 + g x: pure-lapse stress vanishes identically (NEC holds, alpha non-constant)',
           pure_lapse_T(alR).applyfunc(sp.simplify) == sp.zeros(3, 3), 'symbolic')
    alQ = 1 + x ** 2 + y ** 2 + z ** 2
    TQ = pure_lapse_T(alQ).applyfunc(sp.simplify)
    record(item, 'lapse 1 + R^2: 8 pi T_ij = 4 delta_ij/alpha, every null energy strictly positive',
           sp.simplify(TQ - 4 * sp.eye(3) / alQ) == sp.zeros(3, 3), 'symbolic')
    # counterexample: non-uniform shift, flat slices, alpha -> 1, T = 0 (Minkowski in a tilted flat slicing)
    u = sp.Function('u')(z)
    outg = curvature(c0_metric(sp.cosh(u), sp.sinh(u)), XC, riemann=True)
    allz = all(sp.expand(sp.numer(sp.together(v.rewrite(sp.exp)))) == 0 for v in outg['Riem'].values())
    record(item, 'C0 with beta = sinh u(z), alpha = cosh u(z) = sqrt(1+beta^2): Riemann = 0 (flat, T = 0) '
           'while alpha is non-constant and -> 1 where beta -> 0', allz, 'symbolic (all Riemann components)')
    # counterexample with strict NEC: interior Schwarzschild star in flat (Painleve-Gullstrand) slices
    th = sp.Symbol('theta', real=True)
    aS, bS = sp.Function('aS')(r), sp.Function('bS')(r)
    gS = sp.Matrix([[-aS ** 2 + bS ** 2, bS, 0, 0], [bS, 1, 0, 0], [0, 0, r ** 2, 0],
                    [0, 0, 0, r ** 2 * sp.sin(th) ** 2]])
    outS = curvature(gS, (t, r, th, ph))
    frS = [[1 / aS, -bS / aS, 0, 0], [0, 1, 0, 0], [0, 0, 1 / r, 0], [0, 0, 0, 1 / (r * sp.sin(th))]]
    TS = project(outS['G'], frS)
    Ms, Rs = sp.Rational(1, 5), sp.Integer(1)
    mfun = Ms * r ** 3 / Rs ** 3
    ePhi = sp.Rational(3, 2) * sp.sqrt(1 - 2 * Ms / Rs) - sp.sqrt(1 - 2 * mfun / r) / 2
    alS = ePhi / sp.sqrt(1 - 2 * mfun / r)
    beS = alS * sp.sqrt(2 * mfun / r)
    rho0 = 3 * Ms / (4 * sp.pi * Rs ** 3)
    ok = True
    notes = []
    for rv in (sp.Rational(3, 10), sp.Rational(6, 10), sp.Rational(9, 10)):
        pt = {r: rv, th: sp.pi / 3, t: 0}
        Tl = mp.matrix(4, 4)
        for i in range(4):
            for j in range(4):
                Tl[i, j] = eval_jets(TS[i, j], {aS: alS, bS: beS}, pt) / (8 * mp.pi)
        typ, E = he_type(Tl)
        ev = sorted([mp.re(v) for v in E])
        p_exp = rho0 * (sp.sqrt(1 - 2 * Ms * rv ** 2 / Rs ** 3) - sp.sqrt(1 - 2 * Ms / Rs)) / (
            3 * sp.sqrt(1 - 2 * Ms / Rs) - sp.sqrt(1 - 2 * Ms * rv ** 2 / Rs ** 3))
        rhov, pv = mp.mpf(str(sp.N(rho0, 40))), mp.mpf(str(sp.N(p_exp, 40)))
        good = typ == 'I' and abs(ev[0] + rhov) < 1e-30 and all(abs(e - pv) < 1e-30 for e in ev[1:])
        ok = ok and good and (rhov + pv > 0)
        notes.append(f'r={rv}: alpha={mp.nstr(mp.mpf(str(sp.N(alS.subs(r, rv), 30))), 6)}')
    a_c = sp.N(alS.subs(r, sp.Rational(1, 10 ** 8)), 15)
    record(item, 'interior Schwarzschild star (M=1/5, R=1) in flat slices: perfect fluid rho=3M/4piR^3, TOV p, '
           f'rho+p>0 (strict NEC), non-uniform shift, lapse alpha(0)={a_c} < alpha(R)=1; ' + '; '.join(notes), ok,
           'mpmath 40 digits, eigen-decomposition')


# =============================================================================
# Item 5: I3 uniform-field flatness, I26 aging, I20 light speeds and static observers
# =============================================================================
def item5():
    item = 'Item 5'
    say('\n=== Item 5: I3, I26, I20 ===')
    at, bt = sp.Function('at')(t), sp.Function('bt')(t)
    out = curvature(c0_metric(at, bt), XC, riemann=True)
    record(item, 'I3: alpha(t), beta(t) => every Riemann component vanishes',
           all(sym_zero(v) for v in out['Riem'].values()), 'symbolic (all R^a_bcd)')
    dT, dX, dt_, dz_ = sp.symbols('dT dX dt dz', real=True)
    line_new = -dT ** 2 + dX ** 2
    line_old = -(at * dt_) ** 2 + (dz_ + bt * dt_) ** 2
    ok = sp.expand(line_new.subs({dT: at * dt_, dX: dz_ + bt * dt_}) - line_old) == 0
    record(item, 'I3: T = int alpha dt, X = z + int beta dt pulls -dT^2 + dX^2 back to the C0 line element', ok,
           'symbolic')
    # Eulerian acceleration for general C0A: a = (A^-1 d_z ln alpha, d_r ln alpha)
    outA = curvature(c0_metric(alpha, beta, Afun), XC)
    Gam = outA['Gamma']
    nvec = [1 / alpha, -beta / alpha, 0, 0]
    nJ = [J(c) for c in nvec]
    acc = []
    for mu in range(4):
        v = sum(nJ[nu] * J(D(nvec[mu], XC[nu])) for nu in range(4)) \
            + sum(Gam[mu][a][b] * nJ[a] * nJ[b] for a in range(4) for b in range(4))
        acc.append(v)
    # components in the frame: a^z(hat) = A a^z (a^t = 0 here), a^r(hat) = a^r
    check_identity(item, 'Eulerian acceleration (C0A): a^t = 0', acc[0])
    check_identity(item, '  a(e_z) = d_z(ln alpha)/A  (frame component A*(a^z + beta a^t))',
                   Afun * (acc[1] + beta * acc[0]), D(alpha, z) / (alpha * Afun))
    check_identity(item, '  a(e_r) = d_r ln alpha', acc[2], D(alpha, r) / alpha)
    check_identity(item, '  a(e_phi) = 0', acc[3])
    # uniform stretched region: the (t,z) plane has K = -d_t(A_t/alpha)/(alpha A); flat iff A_t/alpha constant
    Au = sp.Function('Au')(t)
    hu = sp.Matrix([[-at ** 2 + Au ** 2 * bt ** 2, Au ** 2 * bt], [Au ** 2 * bt, Au ** 2]])
    Ku = curvature(hu, (t, z))['R'] / 2
    check_identity(item, 'remark (stretch): uniform alpha(t), beta(t), A(t) give a product with Gaussian curvature '
                   'K = d_t(A_t/alpha)/(alpha A); flat iff A_t/alpha is constant', Ku,
                   D(D(Au, t) / at, t) / (at * Au))
    # I26 aging
    v, ac = sp.symbols('v alpha_c', positive=True)
    xdot = [1, v, 0, 0]
    gnum = c0_metric(ac, -v)
    dtau_dt = sp.sqrt(-sum(gnum[i, j] * xdot[i] * xdot[j] for i in range(4) for j in range(4)))
    record(item, f'I26: carried worldline dz/dt = v in a compartment (alpha_c, beta=-v): dtau/dt = {dtau_dt}, '
           f'dtau/dz = {sp.simplify(dtau_dt / v)}', sp.simplify(dtau_dt - ac) == 0, 'symbolic')
    # I20 light along the track and static observers
    zd = sp.Symbol('zdot', real=True)
    al_, be_, A_ = sp.symbols('alpha beta A', positive=True)
    gl = c0_metric(al_, be_, A_)
    sols = sp.solve(gl[0, 0] + 2 * gl[0, 1] * zd + gl[1, 1] * zd ** 2, zd)
    ok = set(sp.simplify(s_) for s_ in sols) == {sp.simplify(-be_ + al_ / A_), sp.simplify(-be_ - al_ / A_)}
    record(item, f'I20: light along z moves at dz/dt = -beta +/- alpha/A (solutions {sols})', ok, 'symbolic')
    record(item, 'I20: static observer d_t is timelike iff g_tt = -alpha^2 + A^2 beta^2 < 0, i.e. alpha > A|beta|',
           sp.expand(gl[0, 0] - (-al_ ** 2 + A_ ** 2 * be_ ** 2)) == 0, 'symbolic')


# =============================================================================
# Item 6: I4 product identity and I4c
# =============================================================================
def item6():
    item = 'Item 6'
    say('\n=== Item 6: I4 product (service-region) identity, I4c ===')
    a2, b2, A2 = [sp.Function(nm)(t, z) for nm in ('a2', 'b2', 'A2')]
    Cw = sp.Function('Cw')(r)
    out = curvature(c0_metric(a2, b2, A2, Cw), XC)
    T8 = project(out['G'], c0_frame(a2, b2, A2, Cw))
    h = sp.Matrix([[-a2 ** 2 + A2 ** 2 * b2 ** 2, A2 ** 2 * b2], [A2 ** 2 * b2, A2 ** 2]])
    K2 = curvature(h, (t, z))['R'] / 2        # Gaussian curvature, R_(2) = 2K
    KS = -D(Cw, r, 2) / Cw
    for (i, j), c, lab in (((N_, N_), KS, 'K_S'), ((Z_, Z_), -KS, '-K_S'), ((R_, R_), -K2, '-K'),
                           ((P_, P_), -K2, '-K'), ((N_, Z_), 0, '0'), ((N_, R_), 0, '0'), ((N_, P_), 0, '0'),
                           ((Z_, R_), 0, '0'), ((Z_, P_), 0, '0'), ((R_, P_), 0, '0')):
        check_identity(item, f'product of a general 2D Lorentzian metric with dr^2 + C(r)^2 dphi^2: '
                       f'8 pi T_{"nzrp"[i]}{"nzrp"[j]} = {lab}', T8[i, j], c)
    # I4c with A = 1
    a1, b1 = [sp.Function(nm)(t, z) for nm in ('a1', 'b1')]
    K1 = curvature(sp.Matrix([[-a1 ** 2 + b1 ** 2, b1], [b1, 1]]), (t, z))['R'] / 2
    Kc = b1.diff(z) / a1
    n1 = lambda f: (D(f, t) - b1 * D(f, z)) / a1
    check_identity(item, 'I4c: K = -alpha_zz/alpha - n(beta_z/alpha) + (beta_z/alpha)^2', K1,
                   -D(a1, z, 2) / a1 - n1(Kc) + Kc ** 2)
    Kds = canon(curvature(sp.Matrix([[-sp.cos(z) ** 2, 0], [0, 1]]), (t, z))['R'] / 2)
    record(item, f'sign convention: de Sitter_2 (alpha = cos z) has K = {Kds} > 0', Kds == 1, 'symbolic')
    R0 = sp.Symbol('R0', positive=True)
    outs = curvature(c0_metric(a2, b2, A2, R0 * sp.sin(r / R0)), XC)
    T8s = project(outs['G'], c0_frame(a2, b2, A2, R0 * sp.sin(r / R0)))
    ok = sp.simplify(T8s[N_, N_] - 1 / R0 ** 2) == 0 and sp.simplify(T8s[Z_, Z_] + 1 / R0 ** 2) == 0
    record(item, 'spherical analogue (round sphere radius R0): rho = -p_l = 1/(8 pi R0^2)', ok, 'symbolic')
    # minimum null energy over the Eulerian null sphere
    kS, kk, c = sp.symbols('K_S K c', real=True)          # c = e_z component, |c| <= 1
    Tkk = kS + (-kS * c ** 2 - kk * (1 - c ** 2))
    ok = sp.expand(Tkk - (kS - kk) * (1 - c ** 2)) == 0
    record(item, 'null energy 8 pi T(n+e,n+e) = (K_S - K)(1 - e_z^2): along-track zero, minimum min(0, K_S - K)',
           ok, 'symbolic')


# =============================================================================
# Item 7: I5, I5c, I6 (and the Type IV clause)
# =============================================================================
def item7():
    item = 'Item 7'
    say('\n=== Item 7: I5/I5c exact fluxes, I6 shear identity ===')
    T8, _ = c0_tensor()
    check_identity(item, 'I5c: 8 pi T_nz = -(1/2r) d_r(r beta_r/alpha)', T8[N_, Z_], -D(r * D(beta, r) / alpha, r) / (2 * r))
    check_identity(item, 'I5c: 8 pi T_nr = (1/2alpha^2) d_z(alpha beta_r) - (beta_z/alpha) d_r ln alpha', T8[N_, R_],
                   D(alpha * D(beta, r), z) / (2 * alpha ** 2) - D(beta, z) / alpha * D(alpha, r) / alpha)
    # I5 leading terms become exact where beta is locally r-independent
    br = {J(D(beta, r)): 0, J(D(beta, r, 2)): 0, J(D(beta, r, z)): 0, J(D(beta, r, t)): 0}
    Kserv = -D(alpha, z, 2) / alpha - Q_
    ok1 = sym_zero(J(T8[N_, R_]).xreplace(br) - J(-D(beta, z) * D(alpha, r) / alpha ** 2))
    ok2 = sym_zero(J(T8[N_, N_] + T8[R_, R_]).xreplace(br) - J(D(alpha, r) / (r * alpha) - Kserv).xreplace(br))
    record(item, 'I5: where beta_r = 0 on a neighbourhood, 8 pi T_nr = -beta_z a_r/alpha exactly and '
           '8 pi(rho+p_r) = a_r/r - K exactly (K = service curvature at that radius)', ok1 and ok2, 'symbolic')
    # I6 with alpha = A = 1
    b = sp.Function('beta')(t, z, r)
    out = curvature(c0_metric(1, b), XC)
    T1 = project(out['G'], c0_frame(1, b))
    lapb = lap_perp(b)
    check_identity(item, 'I6: 8 pi T(n+e_z, n+e_z) = -(beta_r^2 + Lap_perp beta)', T1[N_, N_] + 2 * T1[N_, Z_] + T1[Z_, Z_],
                   -(D(b, r) ** 2 + lapb))
    check_identity(item, 'I6: 8 pi T(n-e_z, n-e_z) = -(beta_r^2 - Lap_perp beta)', T1[N_, N_] - 2 * T1[N_, Z_] + T1[Z_, Z_],
                   -(D(b, r) ** 2 - lapb))
    check_identity(item, 'I6 coupling: 8 pi T_nr = beta_rz/2 (alpha = 1)', T1[N_, R_], D(b, r, z) / 2)
    check_identity(item, 'I6 coupling: 8 pi T_zr = -(beta_rt - beta beta_rz)/2 + beta_r beta_z (alpha = 1)', T1[Z_, R_],
                   -(D(b, r, t) - b * D(b, r, z)) / 2 + D(b, r) * D(b, z))
    # 2x2 block lemma
    Tnn, Tnz, Tzz, lam = sp.symbols('T_nn T_nz T_zz lambda', real=True)
    Mm = sp.Matrix([[-Tnn, -Tnz], [Tnz, Tzz]])
    disc = sp.discriminant(sp.expand((Mm - lam * sp.eye(2)).det()), lam)
    ok = sp.expand(disc - (Tnn + Tzz + 2 * Tnz) * (Tnn + Tzz - 2 * Tnz)) == 0
    record(item, 'block lemma: on an invariant (n,e) plane, discriminant = T(n+e,n+e) T(n-e,n-e) '
           '(complex pair iff the two null energies have opposite signs)', ok, 'symbolic')
    # Type IV clause: static z-independent layer (plane invariant) versus coupled counterexample
    r0 = sp.Integer(1)

    def tensor_at(bexpr, pt):
        Tl = mp.matrix(4, 4)
        for i in range(4):
            for j in range(4):
                Tl[i, j] = eval_jets(T1[i, j], {b: bexpr}, pt)
        return Tl

    bstat = sp.Rational(1, 3) * sp.exp(-(r - 2) ** 2)
    pt = {t: 0, z: 0, r: sp.Rational(7, 2)}
    Tl = tensor_at(bstat, pt)
    typ, _ = he_type(Tl)
    record(item, f'static shear layer beta = exp(-(r-2)^2)/3 (plane invariant) at r=3.5 where |Lap beta| > beta_r^2: '
           f'T_nr = {mp.nstr(Tl[0, 2], 3)}, T_zr = {mp.nstr(Tl[1, 2], 3)}, type {typ}', typ == 'IV', 'mpmath eigen')
    res = {}
    for Vv, Bv in ((sp.Rational(21, 10), 2), (sp.Rational(1, 2), 2)):
        bex = Vv + 2 * Bv * (r - r0) * z - (r - r0) ** 2
        Tl = tensor_at(bex, {t: 0, z: 0, r: r0})
        kp = Tl[0, 0] + 2 * Tl[0, 1] + Tl[1, 1]
        km = Tl[0, 0] - 2 * Tl[0, 1] + Tl[1, 1]
        typ, E = he_type(Tl)
        res[Vv] = (typ, kp * km)
        say(f'      beta = {Vv} + {2 * Bv}(r-1)z - (r-1)^2 at (z=0,r=1): T(k+)T(k-) = {mp.nstr(kp * km, 4)}, '
            f'eigenvalues {[mp.nstr(e, 4) for e in E]}')
    record(item, 'I6 Type IV clause FALSE in general: beta = 2.1 + 4(r-1)z - (r-1)^2 (alpha = 1, static) has '
           'opposite along-track null energies at (z=0, r=1) yet is Type I; with 0.5 in place of 2.1 it is Type IV',
           res[sp.Rational(21, 10)][0] == 'I' and res[sp.Rational(21, 10)][1] < 0 and res[sp.Rational(1, 2)][0] == 'IV',
           'mpmath eigen')
    # proper-shear flux with stretch (inventory 3.3 item 1)
    T8A, _ = c0A_tensor()
    sA = Afun * D(beta, r) / alpha
    check_identity(item, 'stretch: 8 pi T_nz = -(1/(2 r A^2)) d_r(r A^2 * A beta_r/alpha) (proper shear A beta_r/alpha)',
                   T8A[N_, Z_], -D(r * Afun ** 2 * sA, r) / (2 * r * Afun ** 2))


# =============================================================================
# Item 8: I7 doubly-warped Hessian identity
# =============================================================================
def item8():
    item = 'Item 8'
    say('\n=== Item 8: I7 doubly warped Hessian identity ===')
    aw, Aw, Cw = [sp.Function(nm)(t, r) for nm in ('aw', 'Aw', 'Cw')]
    g = sp.diag(-aw ** 2, Aw ** 2, 1, Cw ** 2)
    out = curvature(g, XC)
    fr = [[1 / aw, 0, 0, 0], [0, 1 / Aw, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1 / Cw]]
    T8 = project(out['G'], fr)
    base = curvature(sp.diag(-aw ** 2, 1), (t, r))
    Gb = base['Gamma']
    Y = (t, r)

    def hess(f, u, w):
        fj = [J(D(f, y)) for y in Y]
        return sum(u[a] * w[b] * (J(D(f, Y[a], Y[b])) - sum(Gb[c][a][b] * fj[c] for c in range(2)))
                   for a in range(2) for b in range(2))

    for sgn, nm in ((1, '+'), (-1, '-')):
        k = [1 / J(aw), sgn]
        lhs = T8[N_, N_] + 2 * sgn * T8[N_, R_] + T8[R_, R_]
        check_identity(item, f'8 pi T(k{nm},k{nm}) = -Hess(A)(k,k)/A - Hess(C)(k,k)/C, k{nm} = n {nm} e_r', lhs,
                       -hess(Aw, k, k) / J(Aw) - hess(Cw, k, k) / J(Cw))
    check_identity(item, 'C = r: -Hess(r)(k,k)/r = alpha_r/(r alpha)', -hess(r, [1 / J(aw), 1], [1 / J(aw), 1]) / r,
                   D(aw, r) / (r * aw))
    check_identity(item, 'z and phi decouple: T_nz = T_zr = T_nphi = T_rphi = T_zphi = 0',
                   T8[N_, Z_] ** 2 + T8[Z_, R_] ** 2 + T8[N_, P_] ** 2 + T8[R_, P_] ** 2 + T8[Z_, P_] ** 2)
    split = (T8[N_, N_] + 2 * T8[N_, R_] + T8[R_, R_]) - (T8[N_, N_] - 2 * T8[N_, R_] + T8[R_, R_])
    check_identity(item, 'split T(k+,k+) - T(k-,k-) = -4[Hess A(n,e_r)/A + Hess C(n,e_r)/C] (mixed Hessian)', split,
                   -4 * (hess(Aw, [1 / J(aw), 0], [0, 1]) / J(Aw) + hess(Cw, [1 / J(aw), 0], [0, 1]) / J(Cw)))
    stat = {J(D(aw, t)): 0, J(D(Aw, t)): 0, J(D(Cw, t)): 0, J(D(aw, t, r)): 0, J(D(Aw, t, r)): 0,
            J(D(Cw, t, r)): 0, J(D(aw, t, 2)): 0, J(D(Aw, t, 2)): 0, J(D(Cw, t, 2)): 0}
    record(item, 'static fields: the two radial null energies coincide', sym_zero(J(split).xreplace(stat)), 'symbolic')


# =============================================================================
# Item 9: I8 lapse envelope
# =============================================================================
def item9():
    item = 'Item 9'
    say('\n=== Item 9: I8 lapse envelope ===')
    T8, _ = c0_tensor()
    disc = (T8[N_, N_] + T8[R_, R_]) ** 2 - 4 * T8[N_, R_] ** 2
    exact = ((D(alpha, z, 2) + D(alpha, r) / r) / alpha + Q_) ** 2 \
        - (D(alpha * D(beta, r), z) / alpha ** 2 - 2 * D(beta, z) * D(alpha, r) / alpha ** 2) ** 2
    check_identity(item, '(n,r) block: 64 pi^2 Delta_nr = [(alpha_zz + alpha_r/r)/alpha + Q]^2 - '
                   '[d_z(alpha beta_r)/alpha^2 - 2 beta_z alpha_r/alpha^2]^2', disc, exact)
    # explicit examples on alpha = exp(g(r) + c z^2/2), beta = v0 + w z
    def example(cv, wv, alpha0, g1v, r0=1, v0v=0):
        aex = sp.exp(sp.log(alpha0) + g1v * (r - r0) + cv * z ** 2 / 2)
        bex = v0v + wv * z
        pt = {t: 0, z: 0, r: r0}
        Tl = mp.matrix(4, 4)
        for i in range(4):
            for j in range(4):
                Tl[i, j] = eval_jets(T8[i, j], {alpha: aex, beta: bex}, pt)
        typ, E = he_type(Tl)
        env = mp.mpf(alpha0) / (2 * r0 * abs(wv))
        Kv = -mp.mpf(cv) + (mp.mpf(wv) / alpha0) ** 2
        lhs = abs(mp.mpf(g1v) / r0 - Kv)
        rhs = 2 * abs(wv * g1v) / mp.mpf(alpha0)
        return typ, env, lhs, rhs, Tl

    typ, env, lhs, rhs, Tl = example(2, 1, sp.Rational(3, 2), 1)
    record(item, f'not necessary: alpha=1.5, a_r=1, beta_z=1, convexity c=2 at r=1: envelope ratio 2r|beta_z|/alpha = '
           f'{mp.nstr(1 / env, 4)} > 1, exact |a_r/r - K| = {mp.nstr(lhs, 4)} > 2|beta_z a_r|/alpha = {mp.nstr(rhs, 4)}; '
           f'T_nz = {mp.nstr(Tl[0, 1], 2)}, T_zr = {mp.nstr(Tl[1, 2], 2)}; type {typ}', typ == 'I' and env < 1 and lhs > rhs,
           'mpmath eigen')
    typ, env, lhs, rhs, Tl = example(-1, sp.Rational(1, 10), 10, 1)
    record(item, f'not sufficient: alpha=10, a_r=1, beta_z=0.1, concavity c=-1 at r=1: envelope ratio = '
           f'{mp.nstr(1 / env, 4)} < 1, exact |a_r/r - K| = {mp.nstr(lhs, 4)} < 2|beta_z a_r|/alpha = {mp.nstr(rhs, 4)}; '
           f'type {typ}', typ == 'IV' and env > 1 and lhs < rhs, 'mpmath eigen')
    # no convexity, uniform beta_z: K = +(beta_z/alpha)^2 > 0; exact threshold alpha = (1 + sqrt 2) r|beta_z| at r a_r = 1
    res = {}
    for a0v in (sp.Rational(21, 10), sp.Rational(23, 10), sp.Rational(5, 2)):
        res[a0v] = example(0, 1, a0v, 1, v0v=sp.Rational(1, 3))
    thr = 1 + mp.sqrt(2)
    record(item, f'not sufficient, mildest case (no convexity, uniform beta_z = 1, r a_r = 1): alpha = 2.1, 2.3, 2.5 '
           f'give {[res[k][0] for k in res]}; the envelope admits alpha > 2, the exact threshold is 1 + sqrt(2) = '
           f'{mp.nstr(thr, 6)}', [res[k][0] for k in res] == ['IV', 'IV', 'I'], 'mpmath eigen')
    # same family, Type IV window sqrt(q^2+q) - q < x < sqrt(q^2+q) + q with x = r|beta_z|/alpha, q = r a_r
    xs_ = {}
    for a0v in (sp.Rational(1, 2), sp.Rational(3, 10)):
        xs_[a0v] = example(0, 1, a0v, 1, v0v=sp.Rational(1, 3))[0]
    record(item, f'not necessary without convexity: same family at alpha = 0.5 (x = 2, inside the window '
           f'(0.414, 2.414)) -> {xs_[sp.Rational(1, 2)]}; alpha = 0.3 (x = 3.33, envelope ratio 6.7) -> '
           f'{xs_[sp.Rational(3, 10)]}', (xs_[sp.Rational(1, 2)], xs_[sp.Rational(3, 10)]) == ('IV', 'I'),
           'mpmath eigen')
    # coupled example: both 2x2 sub-blocks predict Type I, the full (n,z,r) block is Type IV
    aex = 2 + r
    bex = sp.Rational(9, 20) * z - sp.Rational(3, 20) * (r - 1) - sp.Rational(17, 40) * (r - 1) ** 2 \
        + sp.Rational(3, 4) * (r - 1) * z
    pt = {t: 0, z: 0, r: 1}
    Tl = mp.matrix(4, 4)
    for i in range(4):
        for j in range(4):
            Tl[i, j] = eval_jets(T8[i, j], {alpha: aex, beta: bex}, pt)
    d_nr = (Tl[0, 0] + Tl[2, 2]) ** 2 - 4 * Tl[0, 2] ** 2
    d_nz = (Tl[0, 0] + Tl[1, 1]) ** 2 - 4 * Tl[0, 1] ** 2
    typ, E = he_type(Tl)
    say(f'      coupled example alpha = 2 + r, beta = 0.45z - 0.15(r-1) - 0.425(r-1)^2 + 0.75(r-1)z at (z=0, r=1): '
        f'Delta_nr = {mp.nstr(d_nr, 4)}, Delta_nz = {mp.nstr(d_nz, 4)}, envelope ratio 0.3, '
        f'eigenvalues {[mp.nstr(e, 4) for e in E]}')
    record(item, 'coupling decides: envelope satisfied (ratio 0.3) and both 2x2 sub-block discriminants positive, '
           'yet the full (n,z,r) block is Type IV', d_nr > 0 and d_nz > 0 and typ == 'IV', 'mpmath eigen')
    # the exact general criterion: discriminant of the (n,z,r) cubic
    a_, b_, c_, d_, e_, f_, lam = sp.symbols('Tnn Tnz Tnr Tzz Tzr Trr lambda', real=True)
    Mblk = sp.Matrix([[-a_, -b_, -c_], [b_, d_, e_], [c_, e_, f_]])
    cub = sp.expand((Mblk - lam * sp.eye(3)).det() * (-1))
    disc3 = sp.discriminant(cub, lam)
    vals = {a_: Tl[0, 0], b_: Tl[0, 1], c_: Tl[0, 2], d_: Tl[1, 1], e_: Tl[1, 2], f_: Tl[2, 2]}
    dval = mp.mpf(str(sp.N(disc3.xreplace({k: sp.Float(str(v), 40) for k, v in vals.items()}), 40)))
    record(item, f'criterion: Type IV iff the discriminant of det(T^a_b - lambda) on the (n,z,r) block is negative '
           f'(here {mp.nstr(dval, 4)})', dval < 0, 'symbolic discriminant, evaluated')


# =============================================================================
# Item 10: I9 conformal rise
# =============================================================================
def item10():
    item = 'Item 10'
    say('\n=== Item 10: I9 conformal rise ===')
    F = sp.Function('F')(t, z)
    al = F * Afun                           # ln alpha - ln A independent of r
    out = curvature(c0_metric(al, beta, Afun), XC)
    T8 = project(out['G'], c0_frame(al, beta, Afun))
    br = D(sp.log(Afun), r)
    nb = (D(br, t) - beta * D(br, z)) / al
    check_identity(item, 'a_r = b_r: 8 pi T_nr = d_z(alpha A beta_r)/(2 alpha^2 A) - n(d_r ln A)', T8[N_, R_],
                   D(al * Afun * D(beta, r), z) / (2 * al ** 2 * Afun) - nb)
    check_identity(item, 'a_r = b_r: 8 pi T_nz = -(1/(2rA^2)) d_r(r A^3 beta_r/alpha)', T8[N_, Z_],
                   -D(r * Afun ** 3 * D(beta, r) / al, r) / (2 * r * Afun ** 2))
    # the design form: A = A0(t,z) e^{phi(r)}, alpha = F(t,z) A, beta = beta(t,z)
    A0 = sp.Function('A0')(t, z)
    phi = sp.Function('phir')(r)
    b2 = sp.Function('b2')(t, z)
    Ac = A0 * sp.exp(phi)
    out2 = curvature(c0_metric(F * Ac, b2, Ac), XC)
    T82 = project(out2['G'], c0_frame(F * Ac, b2, Ac))
    check_identity(item, 'static rise profile, beta_r = 0: T_nr = 0 and T_nz = 0 under any moving shift beta(t,z)',
                   T82[N_, R_] ** 2 + T82[N_, Z_] ** 2)
    # counterexample 1: shift varying across the rise
    b3 = sp.Function('b3')(t, z, r)
    out3 = curvature(c0_metric(F * Ac, b3, Ac), XC)
    T83 = project(out3['G'], c0_frame(F * Ac, b3, Ac))
    check_nonzero(item, 'beta_r != 0 across the rise: radial flux is present', T83[N_, R_])
    # counterexample 2: rise amplitude switched in time
    phit = sp.Function('phit')(t, r)
    Act = A0 * sp.exp(phit)
    out4 = curvature(c0_metric(F * Act, b2, Act), XC)
    T84 = project(out4['G'], c0_frame(F * Act, b2, Act))
    check_identity(item, 'time-dependent rise phi(t,r), beta_r = 0: 8 pi T_nr = -d_t d_r phi / alpha (nonzero)',
                   T84[N_, R_], -D(phit, t, r) / (F * Act))
    # curvature scaling of the service metric by a constant conformal factor
    a1, b1, cc = sp.Function('a1')(t, z), sp.Function('b1')(t, z), sp.Symbol('c', real=True)
    h = sp.Matrix([[-a1 ** 2 + b1 ** 2, b1], [b1, 1]])
    K1 = curvature(h, (t, z))['R'] / 2
    K2 = curvature(sp.exp(2 * cc) * h, (t, z))['R'] / 2
    check_identity(item, 'constant conformal factor e^(2 phi) rescales the service curvature by e^(-2 phi)', K2,
                   sp.exp(-2 * cc) * K1)


# =============================================================================
# Item 11: I10 static balances
# =============================================================================
def item11():
    item = 'Item 11'
    say('\n=== Item 11: I10 static energy and Komar balances ===')
    ast, Ast = sp.Function('alst')(z, r), sp.Function('Ast')(z, r)
    out = curvature(c0_metric(ast, 0, Ast), XC)
    T8 = project(out['G'], c0_frame(ast, 0, Ast))
    sqrtg = Ast * r
    check_identity(item, 'rho sqrt(gamma) = -(1/8pi) d_r(r d_r A)', T8[N_, N_] / (8 * sp.pi) * sqrtg,
                   -D(r * D(Ast, r), r) / (8 * sp.pi))
    check_identity(item, 'no flux: j_z = j_r = 0', T8[N_, Z_] ** 2 + T8[N_, R_] ** 2)
    gam = sp.diag(Ast ** 2, 1, r ** 2)
    Xs = (z, r, ph)
    LB = sum(D(sqrtg * (1 / gam[i, i]) * D(ast, Xs[i]), Xs[i]) for i in range(3)) / sqrtg
    trace = T8[N_, N_] + T8[Z_, Z_] + T8[R_, R_] + T8[P_, P_]
    check_identity(item, '4 pi alpha (rho + sum p) = D^2 alpha (Laplace-Beltrami of gamma)',
                   sp.Rational(1, 2) * ast * trace, LB)
    # numerical balances for explicit fields
    eps = mp.mpf('0.7')
    dA = lambda zz, rr: -2 * rr * eps * mp.exp(-rr ** 2 - zz ** 2)
    worst = mp.mpf(0)
    for zz in (mp.mpf('0.2'), mp.mpf('0.9')):
        # integrand -(1/8pi) d_r(r A_r): integrate with quadrature and compare to boundary terms
        integ = mp.quad(lambda rr: -(1 / (8 * mp.pi)) * mp.diff(lambda q: q * dA(zz, q), rr), [0, 2, 6, mp.inf])
        worst = max(worst, abs(integ))
    record(item, f'per z-slice energy balance int rho sqrt(gamma) dr = 0 for A = 1 + 0.7 exp(-r^2-z^2): max |.| = '
           f'{mp.nstr(worst, 3)}', worst < 1e-25, 'mpmath quadrature')
    zs, rs = sp.symbols('zs rs', real=True)
    Aexs = 1 + sp.Rational(7, 10) * sp.exp(-rs ** 2 - zs ** 2)
    aexs = sp.exp(sp.Rational(13, 10) * sp.exp(-(rs - 2) ** 2 - zs ** 2))
    LBs = (D(Aexs * rs * D(aexs, rs), rs) + D(rs / Aexs * D(aexs, zs), zs))     # sqrt(gamma) D^2 alpha (per dphi)
    from scipy.integrate import dblquad
    fnp = sp.lambdify((zs, rs), LBs, 'numpy')
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        I, _ = dblquad(lambda rr, zz: fnp(zz, rr), -9, 9, 0, 11, epsabs=1e-11, epsrel=1e-11)
        scale, _ = dblquad(lambda rr, zz: abs(fnp(zz, rr)), -9, 9, 0, 11, epsabs=1e-4, epsrel=1e-4)
    record(item, f'Komar balance int D^2 alpha sqrt(gamma) d^3x = 0 for a lapse ring maximum (log alpha = '
           f'1.3 exp(-(r-2)^2-z^2)) on a stretched slice: {2 * np.pi * I:.2e} against a scale {2 * np.pi * scale:.2f}',
           abs(I) < 1e-9 * scale, 'scipy 2D quadrature, float64')
    # active-mass sign pattern of a lapse maximum
    ring_top = sp.N(LBs.subs({zs: 0, rs: 2}))
    ring_flank = sp.N(LBs.subs({zs: 0, rs: sp.Rational(7, 2)}))
    record(item, f'lapse maximum: D^2 alpha < 0 on top (r=2: {float(ring_top):.3f}), > 0 on the flank '
           f'(r=3.5: {float(ring_flank):.3f})', ring_top < 0 and ring_flank > 0, 'direct evaluation')


# =============================================================================
# Item 12: I11 speed-scaling isometry
# =============================================================================
def item12():
    item = 'Item 12'
    say('\n=== Item 12: I11 speed scaling ===')
    T8, _ = c0_tensor()
    cfac = sp.Symbol('c', positive=True)

    def scaled(expr, mode):
        """Jet map of (alpha, beta) -> c (alpha, beta); 'compressed' also maps t -> c t."""
        e = J(expr)
        rep = {}
        for s in e.free_symbols:
            obj = _JET_INV.get(s)
            if obj is None:
                continue
            f = obj.expr if isinstance(obj, sp.Derivative) else obj
            if f not in (alpha, beta):
                continue
            nt = dict(obj.variable_count).get(t, 0) if isinstance(obj, sp.Derivative) else 0
            rep[s] = cfac ** (1 + nt) * s if mode == 'compressed' else cfac * s
        return e.xreplace(rep)

    ok = all(sym_zero(scaled(T8[i, j], 'compressed') - J(T8[i, j])) for i in range(4) for j in range(i, 4))
    record(item, 'exact: fields (c alpha(ct,x), c beta(ct,x)) give the identical orthonormal tensor at (t,x) as '
           '(alpha, beta) at (ct,x): t -> ct is an isometry', ok, 'symbolic, all 10 components, jet scaling')
    Kt = D(K_, t) / alpha
    st = D(s_, t) / alpha
    diffs = {(R_, R_): -(1 - 1 / cfac) * Kt, (P_, P_): -(1 - 1 / cfac) * Kt, (Z_, R_): (1 - 1 / cfac) * st / 2}
    ok = True
    for i in range(4):
        for j in range(i, 4):
            ok = ok and sym_zero(scaled(T8[i, j], 'naive') - J(T8[i, j]) - J(diffs.get((i, j), 0)))
    record(item, 'same-time scaling (alpha,beta) -> (c alpha, c beta): only 8piT_rr = 8piT_phiphi change, by '
           '-(1-1/c) d_t(beta_z/alpha)/alpha, and 8piT_zr, by +(1-1/c) d_t(beta_r/alpha)/(2 alpha)', ok,
           'symbolic, all 10 components')

    # explicit pattern: lapse profile and shift profile carried along a path l(t); shift amplitude = speed
    pa = lambda zz, rr: sp.exp(sp.Rational(3, 2) * sp.exp(-rr ** 2) + sp.Rational(1, 5) * zz ** 2 * sp.exp(-zz ** 2))
    pb = lambda zz, rr: sp.exp(-rr ** 2 / 2 - zz ** 2)            # unit shift profile
    V = sp.Rational(21, 10)
    cval = sp.Rational(100, 21)                                  # 2.1c -> 10c
    tau = sp.Rational(3, 2)

    def fields(scale, path, speed):
        """lapse scale*pa(z - path, r); shift -scale*speed*pb(z - path, r) (packet speed = -beta at centre)."""
        return {alpha: scale * pa(z - path, r), beta: -scale * speed * pb(z - path, r)}

    def tensor(fl, pt):
        return {(i, j): eval_jets(T8[i, j], fl, pt) for i in range(4) for j in range(i, 4)}

    # steady lane: l(t) = V t; design: speed cV, fields x c
    lane_old = fields(1, V * t, V)
    lane_new = fields(cval, cval * V * t, V)
    worst = mp.mpf(0)
    for zz, rr, tt0 in ((sp.Rational(1, 3), sp.Rational(7, 10), sp.Rational(3, 10)),
                        (-sp.Rational(1, 2), sp.Rational(13, 10), sp.Rational(7, 5))):
        To = tensor(lane_old, {t: tt0, z: zz + V * tt0, r: rr})
        Tn = tensor(lane_new, {t: tt0, z: zz + cval * V * tt0, r: rr})
        worst = max(worst, max(abs(To[k] - Tn[k]) for k in To))
    record(item, f'steady lane 2.1c -> 10c (lapse and shift x 100/21, pattern speed x 100/21): tensors at equal '
           f'comoving points agree to {mp.nstr(worst, 3)}', worst < 1e-30, 'mpmath 40 digits')

    # ramp: speed v(t) = V (1 + tanh(t/tau))/2, path l(t) = V (t + tau log cosh(t/tau))/2
    lpath = V * (t + tau * sp.log(sp.cosh(t / tau))) / 2
    vpath = sp.diff(lpath, t)
    old = fields(1, lpath, vpath)
    design = fields(cval, cval * lpath, vpath)                     # same ramp duration, everything x c
    image = {alpha: cval * old[alpha].subs(t, cval * t), beta: cval * old[beta].subs(t, cval * t)}
    tt0, zz, rr = sp.Rational(1, 5), sp.Rational(1, 4), sp.Rational(9, 10)
    To = tensor(old, {t: cval * tt0, z: zz + lpath.subs(t, cval * tt0), r: rr})
    Ti = tensor(image, {t: tt0, z: zz + lpath.subs(t, cval * tt0), r: rr})
    w_img = max(abs(To[k] - Ti[k]) for k in To)
    # design at the same ramp stage as the old configuration (same t, same comoving point)
    To2 = tensor(old, {t: tt0, z: zz + lpath.subs(t, tt0), r: rr})
    Td = tensor(design, {t: tt0, z: zz + cval * lpath.subs(t, tt0), r: rr})
    dT = {k: Td[k] - To2[k] for k in To2}
    changed = sorted('nzrp'[i] + 'nzrp'[j] for (i, j), dv in dT.items() if abs(dv) > 1e-25)
    # predicted difference: -(1-1/c) alpha^-1 d_t|_zeta K, +(1/2)(1-1/c) alpha^-1 d_t|_zeta s (explicit time part)
    zeta = sp.Symbol('zeta', real=True)
    a_c = pa(zeta, r)
    b_c = -vpath * pb(zeta, r)
    Kc = sp.diff(b_c, zeta) / a_c
    sc = sp.diff(b_c, r) / a_c
    ptc = {t: tt0, zeta: zz, r: rr}
    fac = 1 - 1 / cval
    pred_rr = -fac * sp.diff(Kc, t) / a_c
    pred_zr = fac * sp.diff(sc, t) / (2 * a_c)
    e_rr = abs(dT[(R_, R_)] - mp.mpf(str(sp.N(pred_rr.xreplace(ptc), 40))))
    e_pp = abs(dT[(P_, P_)] - mp.mpf(str(sp.N(pred_rr.xreplace(ptc), 40))))
    e_zr = abs(dT[(Z_, R_)] - mp.mpf(str(sp.N(pred_zr.xreplace(ptc), 40))))
    say(f'      ramp: image mismatch {mp.nstr(w_img, 3)}; design-minus-old at the same stage: '
        f'rr {mp.nstr(dT[(R_, R_)], 5)}, pp {mp.nstr(dT[(P_, P_)], 5)}, zr {mp.nstr(dT[(Z_, R_)], 5)}')
    record(item, f'ramp (tau = 1.5): the time-compressed image matches the old ramp to {mp.nstr(w_img, 3)}; the '
           f'design ramp (same duration) differs only in {changed}, exactly by the acceleration terms '
           f'-(1-1/c) alpha^-1 d_t|_zeta K and (1-1/c) alpha^-1 d_t|_zeta s / 2 (residual '
           f'{mp.nstr(max(e_rr, e_pp, e_zr), 3)})',
           w_img < 1e-30 and set(changed) <= {'rr', 'pp', 'zr'} and len(changed) > 0
           and max(e_rr, e_pp, e_zr) < 1e-30, 'mpmath 40 digits')


# =============================================================================
# Item 13: general 3+1 lemmas
# =============================================================================
def item13():
    item = 'Item 13'
    say('\n=== Item 13: general 3+1 lemmas ===')
    # (a) algebra: j = 0 => n eigenvector => Type I; j != 0 can be Type IV
    rng = random.Random(99)
    okI = True
    for k in range(5):
        Tl = mp.matrix(4, 4)
        Tl[0, 0] = mp.mpf(rng.uniform(-2, 2))
        for i in range(1, 4):
            for j in range(i, 4):
                Tl[i, j] = Tl[j, i] = mp.mpf(rng.uniform(-2, 2))
        typ, _ = he_type(Tl)
        okI = okI and typ == 'I'
    Tl = mp.matrix(4, 4)
    Tl[0, 1] = Tl[1, 0] = -1
    typ4, _ = he_type(Tl)
    record(item, '(a) five random tensors with j = 0 are Type I; rho = S = 0, j = e_x is Type IV', okI and typ4 == 'IV',
           'mpmath eigen')
    # (a) general static metric in static slicing, time-dependent lapse: j = 0, rho = 3R/16pi,
    #     8 pi S_ij = 3G_ij + (gamma_ij D^2 alpha - D_i D_j alpha)/alpha
    x, y = sp.symbols('x y', real=True)
    Xs = (x, y, z)
    Pf, Qf, Sf = [sp.Function(nm)(x, y, z) for nm in ('P', 'Q', 'S')]
    al = sp.Function('al')(t, x, y, z)
    g = sp.diag(-al ** 2, Pf ** 2, Qf ** 2, Sf ** 2)
    out = curvature(g, (t, x, y, z))
    fr = [[1 / al, 0, 0, 0], [0, 1 / Pf, 0, 0], [0, 0, 1 / Qf, 0], [0, 0, 0, 1 / Sf]]
    T8 = project(out['G'], fr)
    gam = sp.diag(Pf ** 2, Qf ** 2, Sf ** 2)
    o3 = curvature(gam, Xs)
    G3 = o3['G']
    G3J = o3['Gamma']
    sc = [Pf, Qf, Sf]
    DDa = [[J(D(al, Xs[i], Xs[j])) - sum(G3J[k][i][j] * J(D(al, Xs[k])) for k in range(3)) for j in range(3)]
           for i in range(3)]
    D2a = sum(J(1 / sc[i] ** 2) * DDa[i][i] for i in range(3))
    ok = sym_zero(T8[0, 0] - o3['R'] / 2) and all(sym_zero(T8[0, i]) for i in range(1, 4))
    for i in range(3):
        for j in range(i, 3):
            target = (G3[i, j] + ((J(gam[i, j]) * D2a) - DDa[i][j]) / J(al)) / J(sc[i] * sc[j])
            ok = ok and sym_zero(T8[i + 1, j + 1] - target)
    record(item, '(a) static diagonal slice, lapse alpha(t,x,y,z): j = 0, 8 pi rho = 3R/2, '
           '8 pi S_ij = 3G_ij + (gamma_ij D^2 alpha - D_i D_j alpha)/alpha', ok, 'symbolic')
    # (b), (c), (d): flat slices, general lapse and shift vector
    b = [sp.Function(nm)(t, x, y, z) for nm in ('bx', 'by', 'bz')]
    g = sp.zeros(4, 4)
    g[0, 0] = -al ** 2 + sum(bi ** 2 for bi in b)
    for i in range(3):
        g[0, i + 1] = g[i + 1, 0] = b[i]
        g[i + 1, i + 1] = 1
    out = curvature(g, (t, x, y, z))
    T8 = project(out['G'], [[1 / al, -b[0] / al, -b[1] / al, -b[2] / al], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    sig = [[(D(b[i], Xs[j]) + D(b[j], Xs[i])) / 2 for j in range(3)] for i in range(3)]
    th = sum(D(b[i], Xs[i]) for i in range(3))
    curl = lambda vv: [D(vv[2], y) - D(vv[1], z), D(vv[0], z) - D(vv[2], x), D(vv[1], x) - D(vv[0], y)]
    om = curl(b)
    cc = curl(om)
    ok = True
    for i in range(3):
        j8 = -cc[i] / (2 * al) - sum((sig[i][k] - (th if i == k else 0)) * D(al, Xs[k]) for k in range(3)) / al ** 2
        ok = ok and sym_zero(-T8[0, i + 1] - j8)
    record(item, '(b) 8 pi j = -curl(omega)/(2 alpha) - (sigma - theta 1).grad(alpha)/alpha^2, omega = curl beta '
           '(unit lapse: 8 pi j = -curl curl beta / 2)', ok, 'symbolic, general alpha(t,x), beta^i(t,x)')
    # rigid rotation with any lapse gives j = 0; a gradient shift with a non-uniform lapse does not
    Om = sp.symbols('Omega1:4', real=True)
    brot = [Om[1] * z - Om[2] * y, Om[2] * x - Om[0] * z, Om[0] * y - Om[1] * x]
    sig_rot = [[sp.simplify((D(brot[i], Xs[j]) + D(brot[j], Xs[i])) / 2) for j in range(3)] for i in range(3)]
    record(item, '(b) rigid rotation Omega x x: sigma = 0, theta = 0, curl omega = 0, hence j = 0 for any lapse',
           all(v == 0 for row in sig_rot for v in row) and all(sp.simplify(c_) == 0 for c_ in curl(curl(brot))),
           'symbolic')
    # (c) SSV divergence identity and the one-component reduction (d)
    rho16 = (th ** 2 - sum(sig[i][k] ** 2 for i in range(3) for k in range(3))) / al ** 2
    check_identity(item, '(c,d) Shoshany-Snodgrass eq. 4.3: 16 pi rho = [theta^2 - sigma:sigma]/alpha^2', 2 * T8[0, 0],
                   rho16)
    divterm = sum(D(b[i] * th - sum(b[k] * D(b[i], Xs[k]) for k in range(3)), Xs[i]) for i in range(3))
    check_identity(item, '(c) SSV: theta^2 - sigma:sigma = div(beta theta - (beta.grad)beta) - omega.omega/2',
                   th ** 2 - sum(sig[i][k] ** 2 for i in range(3) for k in range(3)),
                   divterm - sum(o ** 2 for o in om) / 2)
    bz1 = sp.Function('bz1')(t, x, y, z)
    one = [0, 0, bz1]
    sig1 = [[(D(one[i], Xs[j]) + D(one[j], Xs[i])) / 2 for j in range(3)] for i in range(3)]
    th1 = D(bz1, z)
    check_identity(item, '(d) one-component shift beta(t,x,y,z) e_z: theta^2 - sigma:sigma = -|grad_perp beta|^2/2, '
                   'so rho = -|grad_perp beta|^2/(32 pi alpha^2)',
                   th1 ** 2 - sum(sig1[i][k] ** 2 for i in range(3) for k in range(3)),
                   -(D(bz1, x) ** 2 + D(bz1, y) ** 2) / 2)
    # (c) integral identity for a localized shift (grid check, spectral accuracy)
    import numpy as np
    Lb, Ng = 7.0, 88
    xg = np.linspace(-Lb, Lb, Ng, endpoint=False)
    hgrid = xg[1] - xg[0]
    Xg, Yg, Zg = np.meshgrid(xg, xg, xg, indexing='ij')
    kk = 2 * np.pi * np.fft.fftfreq(Ng, d=hgrid)
    KX, KY, KZ = np.meshgrid(kk, kk, kk, indexing='ij')
    gau = lambda cx, cy, cz, w: np.exp(-((Xg - cx) ** 2 + (Yg - cy) ** 2 + (Zg - cz) ** 2) / w)
    B = [0.8 * gau(0.3, 0, 0, 1.1) - 0.5 * Yg * gau(0, 0.4, 0, 0.9),
         0.6 * Xg * gau(0, 0, 0.2, 1.0) + 0.3 * gau(-0.5, 0.2, 0, 0.7),
         0.9 * gau(0, 0, 0, 1.3) * (1 + 0.4 * Xg)]
    dfn = lambda f, K: np.real(np.fft.ifftn(1j * K * np.fft.fftn(f)))
    Kd = (KX, KY, KZ)
    grad = [[dfn(B[i], Kd[j]) for j in range(3)] for i in range(3)]      # grad[i][j] = d_j B_i
    thg = grad[0][0] + grad[1][1] + grad[2][2]
    sigsq = sum(((grad[i][j] + grad[j][i]) / 2) ** 2 for i in range(3) for j in range(3))
    omg = [grad[2][1] - grad[1][2], grad[0][2] - grad[2][0], grad[1][0] - grad[0][1]]
    Irho = np.sum((thg ** 2 - sigsq) / (16 * np.pi)) * hgrid ** 3
    Iom = -np.sum(omg[0] ** 2 + omg[1] ** 2 + omg[2] ** 2) / (32 * np.pi) * hgrid ** 3
    record(item, f'(c) localized general shift (Gaussians): int rho d^3x = {Irho:.12e}, -(1/32pi) int omega^2 = '
           f'{Iom:.12e}', abs(Irho - Iom) < 1e-10 * abs(Iom), 'spectral quadrature, float64')
    # (c) fall-off counterexample: unit lapse, radial shift sqrt(2 m(r)/r) (PG slicing of a regular static metric)
    thS = sp.Symbol('theta', real=True)
    bS = sp.Function('bS')(r)
    gP = sp.Matrix([[-1 + bS ** 2, bS, 0, 0], [bS, 1, 0, 0], [0, 0, r ** 2, 0], [0, 0, 0, r ** 2 * sp.sin(thS) ** 2]])
    outP = curvature(gP, (t, r, thS, ph))
    TP = project(outP['G'], [[1, -bS, 0, 0]])
    check_identity(item, '(c) radial shift beta(r) r_hat, unit lapse: 8 pi rho = (1/r^2) d_r(r beta^2)', TP[0, 0],
                   D(r * bS ** 2, r) / r ** 2)
    Mm, aa = sp.Rational(1, 3), sp.Integer(1)
    m = Mm * r ** 3 / (r ** 2 + aa ** 2) ** sp.Rational(3, 2)
    rhoP = sp.simplify(D(r * 2 * m / r, r) / r ** 2 / (8 * sp.pi))
    Itot = sp.integrate(4 * sp.pi * r ** 2 * rhoP, (r, 0, sp.oo))
    record(item, f'(c) with beta = sqrt(2m/r), m = M r^3/(r^2+a^2)^(3/2) (beta ~ r^(-1/2)): omega = 0 but '
           f'int rho d^3x = {Itot} = M > 0, so the fall-off o(r^(-1/2)) is necessary', sp.simplify(Itot - Mm) == 0,
           'symbolic integral')
    # (e) energy quadratic in speed; flux linear; stress = lapse part + v^2 part (C0, pattern moving at v)
    T8c, _ = c0_tensor()
    vv = sp.Symbol('v', real=True)
    zeta = sp.Symbol('zeta', real=True)
    Pa, Pb = sp.Function('Pa')(zeta, r), sp.Function('Pb')(zeta, r)
    ok = True
    comps = {}
    for i in range(4):
        for j in range(i, 4):
            e = J(T8c[i, j])
            rep = {}
            for s in e.free_symbols:
                obj = _JET_INV.get(s)
                if obj is None:
                    continue
                f = obj.expr if isinstance(obj, sp.Derivative) else obj
                if f not in (alpha, beta):
                    continue
                cnt = dict(obj.variable_count) if isinstance(obj, sp.Derivative) else {}
                nt, nz, nr = cnt.get(t, 0), cnt.get(z, 0), cnt.get(r, 0)
                base = Pa if f == alpha else vv * Pb          # pattern-stationary: d_t = -v d_zeta
                der = base
                if nt + nz:
                    der = sp.diff(der, zeta, nt + nz)
                if nr:
                    der = sp.diff(der, r, nr)
                rep[s] = (-vv) ** nt * der
            comps[(i, j)] = sp.expand(J(e.xreplace(rep)))
    def vdeg(e_):
        num, den = sp.fraction(sp.together(e_))
        if den.has(vv):
            return None
        num = sp.expand(num)
        return set() if num == 0 else set(m_[0] for m_ in sp.Poly(num, vv).monoms())

    deg = {k: vdeg(v_) for k, v_ in comps.items()}
    say(f'      powers of v per component: ' + ', '.join(f"{'nzrp'[i]}{'nzrp'[j]}:{sorted(deg[(i, j)])}"
                                                      for (i, j) in sorted(deg)))
    ok = (deg[(N_, N_)] == {2} and deg[(N_, Z_)] == {1} and deg[(N_, R_)] == {1}
          and all(deg[k] is not None and deg[k] <= {0, 2} for k in ((Z_, Z_), (R_, R_), (P_, P_), (Z_, R_))))
    record(item, '(e) pattern moving at v with lapse profile fixed and shift v*b: rho ~ v^2, fluxes ~ v, '
           'stresses = v^0 (lapse) + v^2 parts', ok, 'symbolic polynomial degree in v')


# =============================================================================
def main():
    for fn in (step0, item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, item11, item12, item13):
        t0 = time.time()
        fn()
        say(f'  ({fn.__name__}: {time.time() - t0:.1f} s)')
    say('\n=== Summary of checks ===')
    nfail = 0
    for it, lab, ok, meth in RESULTS:
        if not ok:
            nfail += 1
    by_item = {}
    for it, lab, ok, meth in RESULTS:
        by_item.setdefault(it, [0, 0])
        by_item[it][0] += 1
        by_item[it][1] += int(ok)
    for it, (n, k) in by_item.items():
        say(f'  {it:8s}: {k}/{n} checks as expected')
    say(f'  total: {len(RESULTS) - nfail}/{len(RESULTS)} as expected; runtime {time.time() - T_START:.1f} s')
    return 0 if nfail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
