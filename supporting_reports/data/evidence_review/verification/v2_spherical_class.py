#!/usr/bin/env python3
"""
v2_spherical_class.py -- independent verification of the spherical warped-product
identities I1-I28 (inventory/knobs_throat_era.md section 5) and of the one-space
cross-check I24 (inventory/knobs_one_space.md section 3.1).

Written from scratch with sympy and mpmath.  No project code is imported or adapted.

Conventions (book, 05_STRUCTURE.md):
  signature (-,+,+,+); G_{mu nu} = 8 pi T_{mu nu}; MTW Riemann
      R^a_{bcd} = d_c Gam^a_{db} - d_d Gam^a_{cb} + Gam^a_{ce} Gam^e_{db} - Gam^a_{de} Gam^e_{cb},
      R_{bd} = R^a_{bad};
  rho = T(n,n), j_i = -T(e_i,n), p_i = T(e_i,e_i) in the orthonormal frame of the
  normal (Eulerian) observer n = (d_t - beta d_l)/alpha, e_l = A^(-1/2) d_l,
  e_theta = B^(-1/2) d_theta, e_phi = (B^(1/2) sin theta)^(-1) d_phi.

Metric class S:  ds^2 = -alpha^2 dt^2 + A (dl + beta dt)^2 + B dOmega^2,
                 alpha, beta, A, B functions of (t,l);  R = sqrt(B).
Radial null vectors of the normal observer: k+- = n +- e_l, so T(k+-,k+-) = rho + p_l -+ 2 j_l.

Method.  General identities are checked in jet space: each field and each of its
partial derivatives up to order 4 is an independent symbol, and d/dt, d/dl act as total
derivatives (chain rule).  A pointwise differential identity holds for all smooth fields
iff it holds on all jets.  Each jet identity is checked two ways:
  (a) exact symbolic reduction of the difference to 0 (sympy.cancel), and
  (b) exact evaluation of the difference at random rational jets (Schwartz-Zippel test).
A second, independent engine differentiates explicit sympy expressions (validation
spacetimes, field-theory sources, areal gauge).  Integrals and finite-difference
scalings use mpmath at 30 significant digits.

Run (from any directory):
  nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
      python3 v2_spherical_class.py
Exit status 0 iff every check passes.  Output is deterministic (fixed seeds; symbols are
sorted before random substitution).  Checks that confirm a counterexample to an inventory
statement are labelled CORRECTION and pass when the counterexample is confirmed.
"""
import sys
import time
import random
import sympy as sp
import mpmath as mp

mp.mp.dps = 30
PI = sp.pi
RESULTS = []
T_START = time.time()


def check(item, desc, cond, detail=''):
    ok = bool(cond)
    RESULTS.append((item, desc, ok, detail))
    tag = 'PASS' if ok else 'FAIL'
    print(f'[{tag}] {item}: {desc}' + (f'  ({detail})' if detail else ''), flush=True)
    return ok


def note(item, text):
    print(f'[NOTE] {item}: {text}', flush=True)


def section(title):
    print('\n' + '=' * 78 + f'\n{title}   [t = {time.time() - T_START:.1f} s]\n' + '=' * 78, flush=True)


# ----------------------------------------------------------------------------
# Jet space
# ----------------------------------------------------------------------------
t, l, th, ph = sp.symbols('t l theta phi', real=True)
XC = (t, l, th, ph)


class Jets:
    """Fields of (t,l) whose jets up to order maxord are independent symbols."""

    def __init__(self, fields, positive=(), maxord=4):
        self.maxord = maxord
        self.J = {}
        for f in fields:
            for i in range(maxord + 1):
                for j in range(maxord + 1 - i):
                    pos = (f in positive) and i == 0 and j == 0
                    self.J[(f, i, j)] = (sp.Symbol(f'{f}_{i}{j}', positive=True) if pos
                                         else sp.Symbol(f'{f}_{i}{j}', real=True))
        self.S2J = {v: k for k, v in self.J.items()}

    def __call__(self, f, i=0, j=0):
        return self.J[(f, i, j)]

    def jet_part(self, expr, k):
        """Chain-rule part of the total derivative along coordinate k (k = 0: t, 1: l)."""
        res = 0
        if k < 2:
            for s in sorted(expr.free_symbols, key=lambda z: z.name):
                if s in self.S2J:
                    f, i, j = self.S2J[s]
                    ni, nj = (i + 1, j) if k == 0 else (i, j + 1)
                    if ni + nj > self.maxord:
                        raise ValueError('jet order exceeded')
                    res += sp.diff(expr, s) * self.J[(f, ni, nj)]
        return res

    def D(self, expr, k):
        expr = sp.sympify(expr)
        return sp.diff(expr, XC[k]) + self.jet_part(expr, k)

    def order(self, s):
        f, i, j = self.S2J[s]
        return i + j


def Dtot(expr, k, *spaces):
    """Total derivative when several jet spaces are in use."""
    expr = sp.sympify(expr)
    return sp.diff(expr, XC[k]) + sum(js.jet_part(expr, k) for js in spaces)


# ----------------------------------------------------------------------------
# Geometry engine (any derivative operator)
# ----------------------------------------------------------------------------
def christoffel(g, gi, Dop, n=4, simplify=True):
    cf = sp.cancel if simplify else (lambda e: e)
    return [[[cf(sum(sp.Rational(1, 2) * gi[a, d] * (Dop(g[d, c], b) + Dop(g[d, b], c) - Dop(g[b, c], d))
                             for d in range(n))) for c in range(n)] for b in range(n)] for a in range(n)]


def ricci_component(Gam, Dop, b, d, n=4, simplify=True):
    e = 0
    for a in range(n):
        e += Dop(Gam[a][d][b], a) - Dop(Gam[a][a][b], d)
        for c in range(n):
            e += Gam[a][a][c] * Gam[c][d][b] - Gam[a][d][c] * Gam[c][a][b]
    return sp.cancel(e) if simplify else e


def ricci(Gam, Dop, n=4, simplify=True):
    Ric = sp.zeros(n)
    for b in range(n):
        for d in range(b, n):
            Ric[b, d] = Ric[d, b] = ricci_component(Gam, Dop, b, d, n, simplify)
    return Ric


def einstein(g, gi, Dop, n=4, simplify=True):
    cf = sp.cancel if simplify else (lambda e: e)
    Gam = christoffel(g, gi, Dop, n, simplify)
    Ric = ricci(Gam, Dop, n, simplify)
    Rs = cf(sum(gi[a, b] * Ric[a, b] for a in range(n) for b in range(n)))
    G = (Ric - g * Rs / 2).applyfunc(cf)
    return G, Gam, Ric, Rs


def bil(M, u, v):
    return sp.cancel((u.T * M * v)[0])


# ----------------------------------------------------------------------------
# Zero tests
# ----------------------------------------------------------------------------
RNG = random.Random(20260926)
TH_VAL = sp.atan(sp.Rational(3, 4))           # sin = 3/5, cos = 4/5 exactly


def rand_rat(lo=-2, hi=2, den=7):
    q = RNG.randint(1, den)
    return sp.Rational(RNG.randint(lo * q, hi * q), q)


def rand_point(expr, fixed=None):
    subs = {}
    for s in sorted(sp.sympify(expr).free_symbols, key=lambda z: z.name):
        if fixed and s in fixed:
            subs[s] = fixed[s]
        elif s == th:
            subs[s] = TH_VAL
        elif s.is_positive:
            q = RNG.randint(2, 6)
            subs[s] = sp.Rational(RNG.randint(q + 1, 3 * q), q) ** 2       # perfect square > 1
        else:
            subs[s] = rand_rat()
    return subs


def zero_random(expr, npts=4, fixed=None):
    expr = sp.sympify(expr)
    for _ in range(npts):
        val = expr.xreplace(rand_point(expr, fixed))
        val = sp.nsimplify(sp.radsimp(val)) if not val.is_Rational else val
        if val != 0:
            return False
    return True


def zero_symbolic(expr):
    e = sp.cancel(sp.together(sp.sympify(expr)))
    if e == 0:
        return True
    return sp.expand(sp.simplify(e)) == 0


def check_id(item, desc, expr, npts=4, fixed=None, symbolic=True):
    r = zero_random(expr, npts, fixed)
    s = zero_symbolic(expr) if symbolic else True
    how = f'random-exact x{npts}' + (' + symbolic' if symbolic else '')
    return check(item, desc, r and s, how)


def check_not_id(item, desc, expr, detail=''):
    """Confirm that a claimed identity fails (counterexample at random rational jets)."""
    return check(item, desc, not zero_random(expr, npts=2), detail or 'counterexample at random rational jets')


# ----------------------------------------------------------------------------
# Class S in jets
# ----------------------------------------------------------------------------
JS = Jets(['al', 'be', 'A', 'B'], positive=('al', 'A', 'B'), maxord=4)
al, be, A, B = JS('al'), JS('be'), JS('A'), JS('B')
Rr = sp.sqrt(B)
g4 = sp.Matrix([[-al**2 + A * be**2, A * be, 0, 0], [A * be, A, 0, 0], [0, 0, B, 0],
                [0, 0, 0, B * sp.sin(th)**2]])
gi4 = sp.Matrix([[-1 / al**2, be / al**2, 0, 0], [be / al**2, 1 / A - be**2 / al**2, 0, 0],
                 [0, 0, 1 / B, 0], [0, 0, 0, 1 / (B * sp.sin(th)**2)]])
nS = sp.Matrix([1 / al, -be / al, 0, 0])
eL = sp.Matrix([0, 1 / sp.sqrt(A), 0, 0])
eT = sp.Matrix([0, 0, 1 / sp.sqrt(B), 0])
eP = sp.Matrix([0, 0, 0, 1 / (sp.sqrt(B) * sp.sin(th))])
kP = nS + eL
kM = nS - eL
vP = -be + al / sp.sqrt(A)
vM = -be - al / sp.sqrt(A)
ETA = sp.Symbol('eta', real=True)
GS = GamS = None
ORTHO = {}
QUOT = {}


def build_class_S():
    global GS, GamS
    GS, GamS, _, _ = einstein(g4, gi4, JS.D)
    ORTHO['rho'] = bil(GS, nS, nS) / (8 * PI)
    ORTHO['j'] = -bil(GS, eL, nS) / (8 * PI)
    ORTHO['pl'] = bil(GS, eL, eL) / (8 * PI)
    ORTHO['pO'] = bil(GS, eT, eT) / (8 * PI)
    ORTHO['pP'] = bil(GS, eP, eP) / (8 * PI)
    ORTHO['Tpp'] = bil(GS, kP, kP) / (8 * PI)
    ORTHO['Tmm'] = bil(GS, kM, kM) / (8 * PI)
    # quotient objects
    g2 = g4[:2, :2]
    gi2 = gi4[:2, :2]
    Gam2 = christoffel(g2, gi2, JS.D, n=2)
    Ric2 = ricci(Gam2, JS.D, n=2)
    K = sp.cancel(sum(gi2[a, b] * Ric2[a, b] for a in range(2) for b in range(2)) / 2)
    dR = [JS.D(Rr, a) for a in range(2)]
    H = sp.Matrix(2, 2, lambda a, b: sp.cancel(JS.D(dR[b], a) - sum(Gam2[c][a][b] * dR[c] for c in range(2))))
    box = sp.cancel(sum(gi2[a, b] * H[a, b] for a in range(2) for b in range(2)))
    grad2 = sp.cancel(sum(gi2[a, b] * dR[a] * dR[b] for a in range(2) for b in range(2)))
    QUOT.update(g2=g2, gi2=gi2, Gam2=Gam2, K=K, dR=dR, H=H, box=box, grad2=grad2)


def jet_static(expr):
    """Static restriction: beta = 0 and every t-derivative = 0."""
    sub = {s: 0 for (f, i, j), s in JS.J.items() if f == 'be' or i > 0}
    return expr.xreplace(sub)


def jets_of(fields, expr, jets=JS, point=None):
    """Replace jet symbols of expr by derivatives of explicit fields (functions of t,l)."""
    sub = {}
    for (f, i, j), s in jets.J.items():
        if s in expr.free_symbols and f in fields:
            d = fields[f]
            if i:
                d = sp.diff(d, t, i)
            if j:
                d = sp.diff(d, l, j)
            sub[s] = d
    out = expr.xreplace(sub)
    if point is not None:
        out = out.xreplace(point)
    return out


def classS_explicit(alpha, beta, AA, BB, x0=t, x1=l, simplify=True):
    """Second engine: explicit class-S metric, returns orthonormal components."""
    g = sp.Matrix([[-alpha**2 + AA * beta**2, AA * beta, 0, 0], [AA * beta, AA, 0, 0], [0, 0, BB, 0],
                   [0, 0, 0, BB * sp.sin(th)**2]])
    gi = sp.Matrix([[-1 / alpha**2, beta / alpha**2, 0, 0], [beta / alpha**2, 1 / AA - beta**2 / alpha**2, 0, 0],
                    [0, 0, 1 / BB, 0], [0, 0, 0, 1 / (BB * sp.sin(th)**2)]])
    coords = (x0, x1, th, ph)
    Dop = lambda e, k: sp.diff(e, coords[k])
    G, Gam, Ric, Rs = einstein(g, gi, Dop, simplify=simplify)
    n = sp.Matrix([1 / alpha, -beta / alpha, 0, 0])
    e1 = sp.Matrix([0, 1 / sp.sqrt(AA), 0, 0])
    e2 = sp.Matrix([0, 0, 1 / sp.sqrt(BB), 0])
    if simplify:
        comp = dict(rho=sp.simplify(bil(G, n, n) / (8 * PI)), j=sp.simplify(-bil(G, e1, n) / (8 * PI)),
                    pl=sp.simplify(bil(G, e1, e1) / (8 * PI)), pO=sp.simplify(bil(G, e2, e2) / (8 * PI)))
    else:
        comp = dict(rho=(n.T * G * n)[0] / (8 * PI), j=-(e1.T * G * n)[0] / (8 * PI),
                    pl=(e1.T * G * e1)[0] / (8 * PI), pO=(e2.T * G * e2)[0] / (8 * PI))
    return comp, G


# ============================================================================
# STEP 0: validation of the Einstein-tensor engine
# ============================================================================
def step0():
    section('STEP 0. Validation of the Einstein-tensor engines')
    r0 = sp.Symbol('r0', positive=True)
    g2 = sp.Matrix([[r0**2, 0], [0, r0**2 * sp.sin(th)**2]])
    Dop = lambda e, k: sp.diff(e, (th, ph)[k])
    _, _, _, Rs2 = einstein(g2, g2.inv(), Dop, n=2)
    check('S0', 'MTW convention: round S^2 of radius r0 has Ricci scalar +2/r0^2', sp.simplify(Rs2 - 2 / r0**2) == 0)

    M = sp.Symbol('M', positive=True)
    r = sp.Symbol('r', positive=True)
    comp, G = classS_explicit(sp.Integer(1), sp.sqrt(2 * M / r), sp.Integer(1), r**2, x1=r)
    check('S0', 'Painleve-Gullstrand Schwarzschild (alpha=1, beta=sqrt(2M/r), A=1, B=r^2): G_mu nu = 0',
          all(sp.simplify(G[a, b]) == 0 for a in range(4) for b in range(4)))
    fields = dict(al=sp.Integer(1), be=sp.sqrt(2 * M / l), A=sp.Integer(1), B=l**2)
    check('S0', 'jet engine on PG Schwarzschild: rho = j = p_l = p_Omega = 0',
          all(sp.simplify(jets_of(fields, ORTHO[k])) == 0 for k in ('rho', 'j', 'pl', 'pO')))

    a = sp.Function('a')(t)
    chi = sp.Symbol('chi', positive=True)
    for kval, S in ((1, sp.sin(chi)), (0, chi), (-1, sp.sinh(chi))):
        comp, _ = classS_explicit(sp.Integer(1), sp.Integer(0), a**2, a**2 * S**2, x1=chi)
        ad, add = sp.diff(a, t), sp.diff(a, t, 2)
        ok = (sp.simplify(8 * PI * comp['rho'] - 3 * (ad**2 + kval) / a**2) == 0 and
              sp.simplify(8 * PI * comp['pl'] + 2 * add / a + (ad**2 + kval) / a**2) == 0 and
              sp.simplify(comp['pl'] - comp['pO']) == 0 and sp.simplify(comp['j']) == 0)
        check('S0', f'FRW k={kval:+d}, generic a(t): Friedmann equations, isotropic pressure, j = 0', ok)
    tt = sp.Symbol('t', positive=True)
    comp, _ = classS_explicit(sp.Integer(1), sp.Integer(0), tt**sp.Rational(4, 3), tt**sp.Rational(4, 3) * chi**2,
                              x0=tt, x1=chi)
    check('S0', 'FRW dust a = t^(2/3): rho = 1/(6 pi t^2), p_l = p_Omega = 0, j = 0',
          sp.simplify(comp['rho'] - 1 / (6 * PI * tt**2)) == 0 and sp.simplify(comp['pl']) == 0
          and sp.simplify(comp['pO']) == 0 and sp.simplify(comp['j']) == 0)

    aa = sp.Symbol('a', positive=True)
    comp, _ = classS_explicit(sp.Integer(1), sp.Integer(0), sp.Integer(1), l**2 + aa**2)
    target = aa**2 / (8 * PI * (l**2 + aa**2)**2)
    check('S0', 'Ellis throat: rho = p_l = -a^2/(8 pi (l^2+a^2)^2), p_Omega = +a^2/(8 pi (l^2+a^2)^2), j = 0',
          sp.simplify(comp['rho'] + target) == 0 and sp.simplify(comp['pl'] + target) == 0 and
          sp.simplify(comp['pO'] - target) == 0 and comp['j'] == 0)

    Phi = sp.Function('Phi')(r)
    b = sp.Function('b')(r)
    comp, _ = classS_explicit(sp.exp(Phi), sp.Integer(0), 1 / (1 - b / r), r**2, x1=r)
    rho_MT = sp.diff(b, r) / (8 * PI * r**2)
    tau_MT = (b / r - 2 * (r - b) * sp.diff(Phi, r)) / (8 * PI * r**2)
    p_MT = r / 2 * ((rho_MT - tau_MT) * sp.diff(Phi, r) - sp.diff(tau_MT, r)) - tau_MT
    check('S0', "Morris-Thorne: rho = b'/(8 pi r^2)", sp.simplify(comp['rho'] - rho_MT) == 0)
    check('S0', "Morris-Thorne: radial tension tau = -p_r = [b/r - 2(r-b)Phi']/(8 pi r^2)",
          sp.simplify(comp['pl'] + tau_MT) == 0)
    check('S0', "Morris-Thorne: p_t = (r/2)[(rho - tau)Phi' - tau'] - tau", sp.simplify(comp['pO'] - p_MT) == 0)
    bp, r0s = sp.symbols('bp r0', positive=True)
    expr_throat = (rho_MT - tau_MT).subs(sp.Derivative(b, r), bp).subs(b, r).subs(r, r0s)
    check('S0', "Morris-Thorne throat b(r0) = r0: rho + p_r = rho - tau = (b'(r0) - 1)/(8 pi r0^2), negative under flare-out b'(r0) < 1",
          sp.simplify(expr_throat - (bp - 1) / (8 * PI * r0s**2)) == 0)
    check('S0', 'Morris-Thorne throat: tension tau(r0) = 1/(8 pi r0^2) for finite Phi\'',
          sp.simplify(tau_MT.subs(b, r).subs(r, r0s) - 1 / (8 * PI * r0s**2)) == 0)

    Q, H = sp.symbols('Q H', positive=True)
    f = 1 - 2 * M / r + Q**2 / r**2
    comp, _ = classS_explicit(sp.sqrt(f), sp.Integer(0), 1 / f, r**2, x1=r)
    e = Q**2 / (8 * PI * r**4)
    check('S0', 'Reissner-Nordstrom: rho = -p_r = p_t = Q^2/(8 pi r^4)',
          all(sp.simplify(x) == 0 for x in (comp['rho'] - e, comp['pl'] + e, comp['pO'] - e)))
    f = 1 - H**2 * r**2
    comp, _ = classS_explicit(sp.sqrt(f), sp.Integer(0), 1 / f, r**2, x1=r)
    e = 3 * H**2 / (8 * PI)
    check('S0', 'de Sitter static patch: rho = -p_r = -p_t = 3H^2/(8 pi) > 0',
          all(sp.simplify(x) == 0 for x in (comp['rho'] - e, comp['pl'] + e, comp['pO'] + e)))

    rng = random.Random(7)

    def rpoly():
        return sum(sp.Rational(rng.randint(-3, 3), rng.randint(1, 4)) * t**i * l**j for i in range(3) for j in range(3 - i))
    alpha_e = 1 + rpoly() / 10
    beta_e = rpoly() / 5
    A_e = 1 + (rpoly() / 10)**2
    B_e = 2 + l**2 + (rpoly() / 10)**2
    comp_e, _ = classS_explicit(alpha_e, beta_e, A_e, B_e, simplify=False)
    pt = {t: sp.Rational(1, 3), l: sp.Rational(-2, 5), th: TH_VAL}
    fields = dict(al=alpha_e, be=beta_e, A=A_e, B=B_e)
    ok = True
    for key in ('rho', 'j', 'pl', 'pO'):
        v1 = sp.N(comp_e[key].xreplace(pt), 60)
        v2 = sp.N(jets_of(fields, ORTHO[key], point=pt), 60)
        ok &= abs(v1 - v2) < sp.Float('1e-45') * (1 + abs(v1))
    check('S0', 'jet engine = explicit engine on a random polynomial class-S metric (rational point, 60 digits)', ok)

    Gmix = gi4 * GS
    div = []
    for nu in range(4):
        e = sum(JS.D(Gmix[mu, nu], mu) for mu in range(4))
        e += sum(GamS[mu][mu][lam] * Gmix[lam, nu] for mu in range(4) for lam in range(4))
        e -= sum(GamS[lam][mu][nu] * Gmix[mu, lam] for mu in range(4) for lam in range(4))
        div.append(e)
    check('S0', 'contracted Bianchi identity nabla_mu G^mu_nu = 0 for the general class-S jet tensor',
          all(zero_random(d, npts=3) for d in div), 'random-exact x3, all four components, third-order jets')
    # negative control: the Ricci tensor alone is not divergence-free (nabla_mu R^mu_nu = d_nu R / 2)
    _, _, RicS, RsS = einstein(g4, gi4, JS.D)
    Rmix = gi4 * RicS
    e = sum(JS.D(Rmix[mu, 1], mu) for mu in range(4))
    e += sum(GamS[mu][mu][lam] * Rmix[lam, 1] for mu in range(4) for lam in range(4))
    e -= sum(GamS[lam][mu][1] * Rmix[mu, lam] for mu in range(4) for lam in range(4))
    check('S0', 'negative control: nabla_mu R^mu_l != 0 but equals d_l R/2 (the test discriminates)',
          (not zero_random(e, npts=2)) and zero_random(e - JS.D(RsS, 1) / 2, npts=2))


# ============================================================================
# I1-I15: time-dependent identities
# ============================================================================
def items_time_dependent():
    g2, gi2, Gam2, K, dR, H, box, grad2 = (QUOT[k] for k in ('g2', 'gi2', 'Gam2', 'K', 'dR', 'H', 'box', 'grad2'))

    section('I1. Warped-product Einstein tensor')
    for a in range(2):
        for b in range(a, 2):
            target = -2 / Rr * H[a, b] + g2[a, b] * (2 / Rr * box + (grad2 - 1) / Rr**2)
            check_id('I1', f'G_ab = -(2/R) Hess_ab R + g_ab[(2/R) box R + ((grad R)^2 - 1)/R^2] for (a,b) = ({"tl"[a]},{"tl"[b]})',
                     GS[a, b] - target)
    check_id('I1', 'G^theta_theta = box R/R - K, K = Gaussian curvature of the quotient (MTW: Ric_ab = K g_ab)',
             gi4[2, 2] * GS[2, 2] - (box / Rr - K))
    check_id('I1', 'G^phi_phi = G^theta_theta', gi4[3, 3] * GS[3, 3] - gi4[2, 2] * GS[2, 2])
    check('I1', 'components G_{a theta}, G_{a phi}, G_{theta phi} vanish',
          all(GS[a, b] == 0 for a in range(2) for b in (2, 3)) and GS[2, 3] == 0)

    section('I2. Radial null energy is the null Hessian of the areal radius')
    for kv, name in ((kP, 'n+e_l'), (kM, 'n-e_l')):
        hess = sum(kv[a] * kv[b] * H[a, b] for a in range(2) for b in range(2))
        check_id('I2', f'G(k,k) = -(2/R) k^a k^b nabla_a nabla_b R, k = {name}', bil(GS, kv, kv) + 2 / Rr * hess)
    JF = Jets(['F'], positive=('F',), maxord=3)
    Fk = JF('F')
    for v, name in ((vP, 'v+'), (vM, 'v-')):
        kvec = [Fk, Fk * v]
        null = sp.cancel(sum(g2[a, b] * kvec[a] * kvec[b] for a in range(2) for b in range(2)))
        check('I2', f'k = F (d_t + {name} d_l) is null for arbitrary F(t,l)', null == 0)

        def Dk(expr):
            return sum(kvec[a] * Dtot(expr, a, JS, JF) for a in range(2))
        acc = [sp.cancel(Dk(kvec[c]) + sum(Gam2[c][a][b] * kvec[a] * kvec[b] for a in range(2) for b in range(2)))
               for c in range(2)]
        kap = sp.cancel(acc[0] / kvec[0])
        check('I2', f'radial null curves are pregeodesics: nabla_k k = kappa k ({name})', sp.cancel(acc[1] - kap * kvec[1]) == 0)
        kR = sum(kvec[a] * dR[a] for a in range(2))
        hess = sum(kvec[a] * kvec[b] * H[a, b] for a in range(2) for b in range(2))
        check_id('I2', f'k(k(R)) = Hess(k,k) + kappa k(R); affine (kappa = 0): 8 pi T(k,k) = -(2/R) d^2R/dlambda^2 ({name})',
                 Dk(kR) - hess - kap * kR, npts=3)
        theta = 2 * kR / Rr
        Gkk = sum(kvec[a] * kvec[b] * GS[a, b] for a in range(2) for b in range(2))
        check_id('I2', f'equivalently Raychaudhuri: k(theta) = -theta^2/2 - 8 pi T(k,k) + kappa theta, theta = 2k(R)/R ({name})',
                 Dk(theta) + theta**2 / 2 + Gkk - kap * theta, npts=3)

    section('I3. Radial discriminant equals the product of the radial null energies')
    rho_, p_, j_ = sp.symbols('rho p j', real=True)
    Tpp, Tmm = rho_ + p_ - 2 * j_, rho_ + p_ + 2 * j_
    check_id('I3', 'jet engine: T(n+e_l,n+e_l) = rho + p_l - 2 j_l with j_l = -T(e_l,n)',
             ORTHO['Tpp'] - (ORTHO['rho'] + ORTHO['pl'] - 2 * ORTHO['j']))
    check_id('I3', 'jet engine: T(n-e_l,n-e_l) = rho + p_l + 2 j_l', ORTHO['Tmm'] - (ORTHO['rho'] + ORTHO['pl'] + 2 * ORTHO['j']))
    check_id('I3', 'rho + p = [T(k+,k+) + T(k-,k-)]/2 and j = [T(k-,k-) - T(k+,k+)]/4',
             (rho_ + p_ - (Tpp + Tmm) / 2)**2 + (j_ - (Tmm - Tpp) / 4)**2)
    check_id('I3', 'Delta = (rho + p)^2 - 4 j^2 = T(k+,k+) T(k-,k-)', (rho_ + p_)**2 - 4 * j_**2 - Tpp * Tmm)
    Mx = sp.Matrix([[-rho_, j_], [-j_, p_]])
    lam = sp.Symbol('lam')
    disc = sp.discriminant(sp.expand((Mx - lam * sp.eye(2)).det()), lam)
    check_id('I3', 'mixed radial block T^a_b has real eigenvalues iff Delta >= 0 (discriminant of its characteristic polynomial = Delta)',
             disc - ((rho_ + p_)**2 - 4 * j_**2))
    Tcov = sp.Matrix([[rho_, -j_], [-j_, p_]])
    npr = sp.Matrix([sp.cosh(ETA), sp.sinh(ETA)])
    epr = sp.Matrix([sp.sinh(ETA), sp.cosh(ETA)])
    kpp, kmp = npr + epr, npr - epr
    ok = (sp.simplify(((kpp.T * Tcov * kpp)[0] - sp.exp(2 * ETA) * Tpp).rewrite(sp.exp)) == 0 and
          sp.simplify(((kmp.T * Tcov * kmp)[0] - sp.exp(-2 * ETA) * Tmm).rewrite(sp.exp)) == 0)
    check('I3', 'radial boost by rapidity eta: T(k+-,k+-) -> exp(+-2 eta) T(k+-,k+-), so Delta is boost invariant', ok)
    ok = True
    h0 = sp.Symbol('h0', positive=True)
    pv = sp.Symbol('p0', real=True)
    etam = sp.diag(-1, 1)
    for sgn in (1, -1):
        hv = sgn * h0
        rv = hv - pv
        u = sp.Matrix([sp.cosh(ETA), sp.sinh(ETA)])
        s = sp.Matrix([sp.sinh(ETA), sp.cosh(ETA)])
        ul, sl = etam * u, etam * s
        Tlab = rv * ul * ul.T + pv * sl * sl.T
        rho_l, p_l, j_l = Tlab[0, 0], Tlab[1, 1], -Tlab[1, 0]
        hl = rho_l + p_l
        ok &= sp.simplify(hl**2 - 4 * j_l**2 - h0**2) == 0
        ok &= sp.simplify((rho_l - p_l + sgn * h0) / 2 - rv) == 0
        ok &= sp.simplify((2 * j_l / (hl + sgn * h0) - sp.tanh(ETA)).rewrite(sp.exp)) == 0
    check('I3', 'Type I rest frame, either enthalpy sign: rho_rest = (rho - p + sgn(h) sqrt(Delta))/2, '
                'v = 2j/(h + sgn(h) sqrt(Delta)) = tanh(eta) (h = rho + p)', ok)
    jj = sp.Symbol('jj', positive=True)
    pp = sp.Symbol('pp', real=True)
    Mx2 = sp.Matrix([[-(2 * jj - pp), jj], [-jj, pp]])
    ev = Mx2.eigenvals()
    lam0 = list(ev.keys())[0]
    check('I3', 'Delta = 0 with j != 0: double eigenvalue and rank(T - lambda) = 1, a Jordan block (Type II)',
          len(ev) == 1 and (Mx2 - lam0 * sp.eye(2)).rank() == 1)

    section('I4. Constant areal radius: exact, boost-invariant string cloud')
    Bc = sp.Symbol('Bc', positive=True)
    subB = {s: (Bc if (i + j == 0) else 0) for (f, i, j), s in JS.J.items() if f == 'B'}
    rhoC, jC, plC, pOC = (ORTHO[k].xreplace(subB) for k in ('rho', 'j', 'pl', 'pO'))
    check_id('I4', 'R constant (alpha, beta, A arbitrary): rho = 1/(8 pi R^2)', rhoC - 1 / (8 * PI * Bc))
    check_id('I4', 'R constant: p_l = -1/(8 pi R^2)', plC + 1 / (8 * PI * Bc))
    check_id('I4', 'R constant: j_l = 0', jC)
    check_id('I4', 'R constant: p_Omega = -K/(8 pi)', pOC + K / (8 * PI))
    check_id('I4', 'R constant: rho + p_Omega = (1/R^2 - K)/(8 pi)', rhoC + pOC - (1 / Bc - K) / (8 * PI))
    quot = [GS[a, b].xreplace(subB) + g4[a, b] / Bc for a in range(2) for b in range(2)]
    check('I4', 'R constant: quotient block G_ab = -g_ab/R^2, identical in every radially boosted frame',
          all(zero_random(q) and zero_symbolic(q) for q in quot))
    Lam, Qq = sp.symbols('Lambda Q', positive=True)
    compN, _ = classS_explicit(sp.cos(sp.sqrt(Lam) * l), sp.Integer(0), sp.Integer(1), 1 / Lam)
    compB, _ = classS_explicit(sp.cosh(l / Qq), sp.Integer(0), sp.Integer(1), Qq**2)
    check('I4', 'control: Nariai dS2 x S2 (N = cos(sqrt(Lambda) l), K = +Lambda, R^2 = 1/Lambda) gives T = -(Lambda/8 pi) g',
          sp.simplify(compN['rho'] - Lam / (8 * PI)) == 0 and sp.simplify(compN['pl'] + Lam / (8 * PI)) == 0 and
          sp.simplify(compN['pO'] + Lam / (8 * PI)) == 0)
    check('I4', 'control: Bertotti-Robinson AdS2 x S2 (N = cosh(l/Q), K = -1/Q^2, R = Q) gives rho = -p_l = p_Omega = 1/(8 pi Q^2)',
          sp.simplify(compB['rho'] - 1 / (8 * PI * Qq**2)) == 0 and sp.simplify(compB['pl'] + 1 / (8 * PI * Qq**2)) == 0 and
          sp.simplify(compB['pO'] - 1 / (8 * PI * Qq**2)) == 0)

    section('I5. Radial null speeds')
    vv = sp.Symbol('v', real=True)
    norm = -al**2 + A * (vv + be)**2
    check_id('I5', 'g(d_t + v d_l, d_t + v d_l) = -alpha^2 + A (v + beta)^2',
             sum(g4[a, b] * [1, vv][a] * [1, vv][b] for a in range(2) for b in range(2)) - norm)
    check_id('I5', 'factorization A (v - v+)(v - v-) = -alpha^2 + A (v + beta)^2 with v+- = -beta +- alpha/sqrt(A)',
             A * (vv - vP) * (vv - vM) - norm)
    check_id('I5', 'v+ v- = g_tt/A', vP * vM - g4[0, 0] / A)
    check_id('I5', 'v+ + v- = -2 beta', vP + vM + 2 * be)
    check_id('I5', 'if d_t R = 0: (grad R)^2 = -(d_l R)^2 g_tt/(A alpha^2), so g_tt > 0 on a flank <=> trapped spheres',
             grad2.xreplace({JS('B', 1, 0): 0}) + dR[1].xreplace({JS('B', 1, 0): 0})**2 * g4[0, 0] / (A * al**2))

    section('I6. Packet norm and clock')
    check_id('I6', 'comoving v = -beta: norm = -alpha^2, so dtau/dt = alpha', norm.subs(vv, -be) + al**2)
    note('I6', 'timelike <=> norm < 0 <=> (v - v+)(v - v-) < 0 <=> v- < v < v+ (A > 0, factorization in I5); dtau/dt = sqrt(-norm).')

    section('I7. Shift re-match algebra')
    gW, vpb = sp.symbols('gW vpb', real=True)
    check_id('I7', 'delta beta = -gW (v + beta) gives v + beta_new = (1 - gW)(v + beta)', (vpb - gW * vpb) - (1 - gW) * vpb)
    check('I7', '|1 - gW| < 1 <=> 0 < gW < 2; comoving match (v + beta_new = 0) at gW = 1',
          sp.solve_univariate_inequality(sp.Abs(1 - gW) < 1, gW, relational=False) == sp.Interval.open(0, 2))
    check_not_id('I7', 'CORRECTION: the Eulerian-frame tensor depends on undifferentiated beta in class S (d rho/d beta != 0)',
                 sp.diff(ORTHO['rho'], be))
    # normal-derivative variables: m_f = n(f), mL_f = d_l n(f), mm_f = n(n(f)), n = (d_t - beta d_l)/alpha
    mS = {f: sp.Symbol(f'n_{f}', real=True) for f in ('al', 'be', 'A', 'B')}
    mL = {f: sp.Symbol(f'nl_{f}', real=True) for f in ('al', 'be', 'A', 'B')}
    mm = {f: sp.Symbol(f'nn_{f}', real=True) for f in ('al', 'be', 'A', 'B')}
    X10 = {f: al * mS[f] + be * JS(f, 0, 1) for f in mS}
    X11 = {f: JS('al', 0, 1) * mS[f] + al * mL[f] + JS('be', 0, 1) * JS(f, 0, 1) + be * JS(f, 0, 2) for f in mS}
    X20 = {f: X10['al'] * mS[f] + al * (al * mm[f] + be * mL[f]) + X10['be'] * JS(f, 0, 1) + be * X11[f] for f in mS}
    subN = {}
    for f in mS:
        subN[JS(f, 1, 0)] = X10[f]
        subN[JS(f, 1, 1)] = X11[f]
        subN[JS(f, 2, 0)] = X20[f]
    ok = True
    for k in ('rho', 'j', 'pl', 'pO'):
        e = sp.diff(ORTHO[k].xreplace(subN), be)
        ok &= zero_random(e) and zero_symbolic(e)
    check('I7', 'CORRECTED STATEMENT: written with normal derivatives n = (d_t - beta d_l)/alpha of the fields, '
                'rho, j, p_l, p_Omega contain no undifferentiated beta', ok)
    subL = {s: 0 for (f, i, j), s in JS.J.items() if f in ('al', 'A', 'B') and j > 0}
    check_not_id('I7', 'even with alpha, A, B independent of l, beta enters p_Omega through n(d_l beta) = (d_t d_l beta - beta d_l^2 beta)/alpha',
                 sp.diff(ORTHO['pO'].xreplace(subL), be))
    check('I7', 'with alpha, A, B independent of l, rho, j, p_l are free of undifferentiated beta (K, and with it n(d_l beta), enters only p_Omega)',
          all(zero_random(sp.diff(ORTHO[k].xreplace(subL), be)) for k in ('rho', 'j', 'pl')))
    b0 = sp.Symbol('b0', real=True)
    comp, _ = classS_explicit(sp.Integer(1), b0, sp.Integer(1), l**2 + 1)
    check('I7', 'example: static Ellis slice with uniform shift b0 has rho depending on b0',
          sp.simplify(sp.diff(comp['rho'], b0)) != 0, f"rho = {sp.factor(sp.simplify(comp['rho']))}")

    section('I8. Coordinate-normalized null energy carries alpha^2')
    kPc = sp.Matrix([1, vP, 0, 0])
    kMc = sp.Matrix([1, vM, 0, 0])
    check('I8', 'k^t = 1: k+- = alpha (n +- e_l)',
          all(sp.cancel(x) == 0 for x in list(kPc - al * kP) + list(kMc - al * kM)))
    check_id('I8', 'T(k+,k+)/alpha^2 = rho + p_l - 2 j_l',
             bil(GS, kPc, kPc) / (8 * PI * al**2) - (ORTHO['rho'] + ORTHO['pl'] - 2 * ORTHO['j']), npts=3)
    check_id('I8', 'T(k-,k-)/alpha^2 = rho + p_l + 2 j_l',
             bil(GS, kMc, kMc) / (8 * PI * al**2) - (ORTHO['rho'] + ORTHO['pl'] + 2 * ORTHO['j']), npts=3)

    section('I9. Uniform slowdown at a static-enthalpy zero')
    kap = sp.Symbol('kappa', positive=True)
    subK, sub0 = {}, {}
    for (f, i, j), s in JS.J.items():
        if f == 'be':
            subK[s] = kap**(i + 1) * s
            sub0[s] = 0
        else:
            subK[s] = kap**i * s
            if i > 0:
                sub0[s] = 0
    Xk = {k: ORTHO[k].xreplace(subK) for k in ('rho', 'pl', 'pO', 'j')}
    X0 = {k: ORTHO[k].xreplace(sub0) for k in ('rho', 'pl', 'pO', 'j')}
    for k in ('rho', 'pl', 'pO'):
        check_id('I9', f'{k}_kappa = {k}_0 + kappa^2 ({k}_1 - {k}_0) (family alpha(kt,l), A(kt,l), B(kt,l), kappa beta(kt,l))',
                 Xk[k] - (X0[k] + kap**2 * (ORTHO[k] - X0[k])), npts=3)
    check_id('I9', 'j_kappa = kappa j_1', Xk['j'] - kap * ORTHO['j'], npts=3)
    check_id('I9', 'static control (frozen phase, zero shift) has j_0 = 0', X0['j'])
    h2, j1 = sp.symbols('h2 j1', real=True)
    check_id('I9', 'at h_0 = 0: Delta_kappa = (kappa^2 h_2)^2 - 4 (kappa j_1)^2 = kappa^2 (kappa^2 h_2^2 - 4 j_1^2)',
             (kap**2 * h2)**2 - 4 * (kap * j1)**2 - kap**2 * (kap**2 * h2**2 - 4 * j1**2))
    kc = 2 * sp.Abs(j1) / sp.Abs(h2)
    check_id('I9', 'threshold: kappa^2 h_2^2 - 4 j_1^2 = h_2^2 (kappa - kappa_c)(kappa + kappa_c), kappa_c = 2|j_1|/|h_2|, '
                   'so Delta_kappa < 0 exactly for 0 < kappa < kappa_c when j_1 != 0',
             sp.expand(kap**2 * h2**2 - 4 * j1**2 - h2**2 * (kap - kc) * (kap + kc)))
    xs, sl_ = sp.symbols('x s', real=True)
    j1p = sp.Symbol('j1p', positive=True)
    # linear static enthalpy h_0 = s x near its root: Delta_kappa < 0 between the two roots below
    xr = sp.solve(sp.Eq((sl_ * xs + kap**2 * h2)**2, 4 * kap**2 * j1p**2), xs)
    check('I9', 'with h_0 = s x near the root (h_2, j_1 frozen): the Type IV interval has width 4 kappa |j_1|/|s| (layer width proportional to kappa)',
          len(xr) == 2 and sp.simplify((xr[0] - xr[1])**2 - 16 * kap**2 * j1p**2 / sl_**2) == 0)
    lamIm = sp.sqrt(-(kap**2 * (kap**2 * h2**2 - 4 * j1p**2))) / 2
    check('I9', '|Im lambda| = sqrt(-Delta_kappa)/2 = kappa sqrt(4 j_1^2 - kappa^2 h_2^2)/2 at the root (proportional to kappa as kappa -> 0)',
          sp.simplify(sp.limit(lamIm / kap, kap, 0) - j1p) == 0)

    section('I10. Null expansions of the symmetry spheres')
    for v, name in ((vP, '+'), (vM, '-')):
        Kup = sp.Matrix([1, v, 0, 0])
        Klow = g4 * Kup
        theta = 0
        for mu in (2, 3):
            cov = JS.D(Klow[mu], mu) - sum(GamS[lam][mu][mu] * Klow[lam] for lam in range(4))
            theta += gi4[mu, mu] * cov
        check_id('I10', f'exact expansion q^mn nabla_m K_n of the round sphere along K{name} = d_t + v{name} d_l '
                        f'equals the proxy 2(d_t R + v{name} d_l R)/R', theta - 2 * (dR[0] + v * dR[1]) / Rr)
    thP = 2 * (dR[0] + vP * dR[1]) / Rr
    thM = 2 * (dR[0] + vM * dR[1]) / Rr
    check_id('I10', 'theta+ theta- = -(4 alpha^2/R^2)(grad R)^2', thP * thM + 4 * al**2 / B * grad2)
    check('I10', 'R constant: theta+ = theta- = 0', all(sp.simplify(x.xreplace(subB)) == 0 for x in (thP, thM)))
    note('I10', 'K+- = alpha(n +- e_l) are future directed (K^t = 1, g^tt = -1/alpha^2); both theta < 0 is the definition of a trapped sphere.')

    section('I11. Radial light paths do not involve the areal radius')
    Bjets = {s for (f, i, j), s in JS.J.items() if f == 'B'}
    check('I11', 'Gamma^a_bc (a,b,c in {t,l}) are B-free and Gamma^A_bc = 0: radial geodesics are geodesics of the quotient',
          all(not (GamS[a][b][c].free_symbols & Bjets) for a in range(2) for b in range(2) for c in range(2))
          and all(GamS[a][b][c] == 0 for a in (2, 3) for b in range(2) for c in range(2)))
    check('I11', 'v+- = -beta +- alpha/sqrt(A) are B-free, so d(delta l)/dt = (d_l v+-) delta l is B-free',
          not ((vP.free_symbols | vM.free_symbols) & Bjets))
    check('I11', 'SCOPE: the areal expansion 2 k(R)/R of the same rays depends on B', bool(thP.free_symbols & Bjets))

    section('I12. Areal flux of a radial string cloud')
    JM = Jets(['mu', 'P'], maxord=2)
    mu, Pp = JM('mu'), JM('P')
    Tlow = sp.zeros(4)
    for a in range(2):
        for b in range(2):
            Tlow[a, b] = -mu * g4[a, b]
    Tlow[2, 2] = Pp * B
    Tlow[3, 3] = Pp * B * sp.sin(th)**2
    Tmix = (gi4 * Tlow).applyfunc(sp.cancel)
    ok = True
    for nu in range(2):
        e = sum(Dtot(Tmix[m, nu], m, JS, JM) for m in range(4))
        e += sum(GamS[m][m][lm] * Tmix[lm, nu] for m in range(4) for lm in range(4))
        e -= sum(GamS[lm][m][nu] * Tmix[m, lm] for m in range(4) for lm in range(4))
        target = -Dtot(mu * B, nu, JS, JM) / B - Pp * Dtot(B, nu, JS, JM) / B
        ok &= zero_random(e - target) and zero_symbolic(e - target)
    check('I12', 'T_ab = -mu g_ab, T^A_B = p_Omega delta^A_B: nabla_mu T^mu_a = -(1/R^2) d_a(mu R^2) - (2 p_Omega/R) d_a R', ok)
    note('I12', 'with p_Omega = 0, conservation <=> d_a(mu R^2) = 0 on the quotient.')
    check_id('I12', 'geometric string flux of any class-S metric: 8 pi R^2 (rho - p_l)/2 = 1 - (grad R)^2 - R box R',
             8 * PI * B * (ORTHO['rho'] - ORTHO['pl']) / 2 - (1 - grad2 - Rr * box), npts=3)

    section('I13. Join regularity: principal part and cusp scaling')
    canon = {k: sp.cancel(ORTHO[k]) for k in ('rho', 'j', 'pl', 'pO')}
    second = [s for s in JS.J.values() if JS.order(s) == 2]
    used = set().union(*[e.free_symbols for e in canon.values()])
    absent = sorted(s.name for s in second if s not in used)
    check('I13', 'second-derivative jets absent from (rho, j, p_l, p_Omega): exactly alpha_tt, alpha_tl, beta_tt',
          absent == ['al_11', 'al_20', 'be_20'], f'absent = {absent}')
    static_canon = [sp.cancel(jet_static(ORTHO[k])) for k in ('rho', 'pl', 'pO')]
    used_st = set().union(*[e.free_symbols for e in static_canon])
    absent_st = sorted(s.name for s in (JS('al', 0, 2), JS('A', 0, 2), JS('B', 0, 2)) if s not in used_st)
    check('I13', 'static region: the second radial derivative of gamma_ll = A never appears (A is a radial-gauge function there)',
          absent_st == ['A_02'], f'absent among static second derivatives = {absent_st}')
    ok_lin, ok_den, ok_w = True, True, True
    for k, e in canon.items():
        num, den = sp.fraction(e)
        if any(JS.order(s) > 0 for s in den.free_symbols if s in JS.S2J):
            ok_den = False
        for term in sp.Add.make_args(sp.expand(num)):
            w = 0
            n2 = 0
            for s, pw in term.as_powers_dict().items():
                if s in JS.S2J:
                    w += JS.order(s) * pw
                    if JS.order(s) == 2:
                        n2 += pw
            ok_w &= w in (0, 2)
            ok_lin &= n2 <= 1
    check('I13', 'denominators contain undifferentiated fields only; the tensor is linear in second derivatives', ok_den and ok_lin)
    check('I13', 'every term has total derivative weight 0 (the 1/R^2 sphere term) or 2', ok_w)
    dd, cc = sp.symbols('d c', positive=True)
    ok = True
    for pexp in (sp.Rational(1, 2), sp.Rational(3, 2), sp.Rational(5, 2)):
        fields = dict(al=sp.Integer(1), be=sp.Integer(0), A=sp.Integer(1), B=((1 + dd**2) * (1 + cc * dd**pexp)).subs(dd, l))
        rho_c = jets_of(fields, ORTHO['rho']).subs(l, dd)
        rho_s = rho_c.subs(cc, 0)                       # smooth reference (no cusp)
        lead = sp.limit((rho_c - rho_s) * dd**(2 - pexp), dd, 0, '+')
        ok &= sp.simplify(lead + pexp * (pexp - 1) * cc / (8 * PI)) == 0
    check('I13', 'B = (1 + l^2)(1 + c d^p), d = l > 0 (p = 1/2, 3/2, 5/2): rho - rho[c=0] = -p(p-1) c d^(p-2)/(8 pi) + o(d^(p-2))', ok)

    def fd_jets(syms, fields_num, t0, l0, h):
        vals = []
        for s in syms:
            f, i, j = JS.S2J[s]
            F = fields_num[f]
            if (i, j) == (0, 0):
                vals.append(F(t0, l0))
            elif (i, j) == (1, 0):
                vals.append((F(t0 + h, l0) - F(t0 - h, l0)) / (2 * h))
            elif (i, j) == (0, 1):
                vals.append((F(t0, l0 + h) - F(t0, l0 - h)) / (2 * h))
            elif (i, j) == (2, 0):
                vals.append((F(t0 + h, l0) - 2 * F(t0, l0) + F(t0 - h, l0)) / h**2)
            elif (i, j) == (0, 2):
                vals.append((F(t0, l0 + h) - 2 * F(t0, l0) + F(t0, l0 - h)) / h**2)
            elif (i, j) == (1, 1):
                vals.append((F(t0 + h, l0 + h) - F(t0 + h, l0 - h) - F(t0 - h, l0 + h) + F(t0 - h, l0 - h)) / (4 * h**2))
            else:
                raise ValueError(s)
        return vals
    syms_pO = sorted(ORTHO['pO'].free_symbols, key=lambda z: z.name)
    lam_pO = sp.lambdify(syms_pO, ORTHO['pO'], 'mpmath')
    pos = lambda x: x if x > 0 else mp.mpf(0)
    m_ = mp.mpf
    L0 = m_('0.5')                          # join location: R', N' and beta are nonzero there
    base = dict(al=lambda T, L: 1 + m_('0.1') * L**2 + m_('0.05') * T * L, be=lambda T, L: m_('0.3') * L * (1 + T / 5),
                A=lambda T, L: 1 + m_('0.2') * L**2, B=lambda T, L: (1 + L**2) * (1 + m_('0.1') * T))
    base_static = dict(al=lambda T, L: 1 + m_('0.1') * L**2, be=lambda T, L: m_(0),
                       A=lambda T, L: 1 + m_('0.2') * L**2, B=lambda T, L: 1 + L**2)
    cases = [
        ('B, spatial cusp d^(1/2)', base, 'B', lambda T, L: (1 + L**2) * (1 + m_('0.1') * T + m_('0.2') * mp.sqrt(pos(L - L0))), 2 ** 1.5),
        ('B, spatial kink d^1', base, 'B', lambda T, L: (1 + L**2) * (1 + m_('0.1') * T + m_('0.2') * pos(L - L0)), 2.0),
        ('alpha, spatial kink d^1', base, 'al', lambda T, L: 1 + m_('0.1') * L**2 + m_('0.05') * T * L + m_('0.3') * pos(L - L0), 2.0),
        ('beta, spatial kink d^1', base, 'be', lambda T, L: m_('0.3') * L * (1 + T / 5) + m_('0.2') * pos(L - L0), 2.0),
        ('B, time kink', base, 'B', lambda T, L: (1 + L**2) * (1 + m_('0.1') * T + m_('0.2') * pos(T)), 2.0),
        ('A, time kink', base, 'A', lambda T, L: 1 + m_('0.2') * L**2 + m_('0.2') * pos(T), 2.0),
        ('static A, spatial cusp d^(1/2) (milder: d^(-1/2))', base_static, 'A',
         lambda T, L: 1 + m_('0.2') * L**2 + m_('0.2') * mp.sqrt(pos(L - L0)), 2 ** 0.5),
        ('B, C2 join d^3 (first-order sampling error)', base, 'B',
         lambda T, L: (1 + L**2) * (1 + m_('0.1') * T + m_('0.2') * pos(L - L0)**3), 0.5),
        ('smooth non-polynomial B (second-order sampling error)', base, 'B',
         lambda T, L: (1 + L**2) * (1 + m_('0.1') * T) * (1 + m_('0.2') * mp.sin(L)), 0.25),
        ('alpha, time kink', base, 'al', lambda T, L: 1 + m_('0.1') * L**2 + m_('0.05') * T * L + m_('0.3') * pos(T) * (1 + L), None),
        ('beta, time kink', base, 'be', lambda T, L: m_('0.3') * L * (1 + T / 5) + m_('0.2') * pos(T) * (1 + L), None),
    ]
    for name, bdict, fld, F, expect in cases:
        fields_num = dict(bdict)
        fields_num[fld] = F
        hs = [mp.mpf(2) ** (-k) for k in range(14, 19)]
        vals = [lam_pO(*fd_jets(syms_pO, fields_num, mp.mpf(0), L0, h)) for h in hs]
        if expect is None:
            diffs = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
            okc = max(abs(v) for v in vals) < 10 and diffs[-1] < m_('1e-6')
            detail = f'bounded: sampled p_Omega {mp.nstr(vals[0], 10)} -> {mp.nstr(vals[-1], 10)}'
        else:
            rr = (vals[-1] - vals[-2]) / (vals[-2] - vals[-3])      # successive differences remove the finite part
            okc = abs(rr - expect) < 1e-3 * expect
            detail = f'difference ratio per step halving {mp.nstr(rr, 7)}, expected {expect:.5f}'
        check('I13', f'sampled p_Omega at the join, {name}', okc, detail)

    section('I14. Lapse-only dynamics carry no Eulerian energy flux')
    subLap = {s: 0 for (f, i, j), s in JS.J.items() if f == 'be' or (f in ('A', 'B') and i > 0)}
    check_id('I14', 'beta = 0 and d_t A = d_t B = 0, alpha(t,l) arbitrary: j_l = 0', ORTHO['j'].xreplace(subLap))
    check('I14', 'same hypotheses: rho contains no lapse jets (rho = 3R/(16 pi) of the static slice)',
          not any(s.name.startswith('al_') for s in sp.cancel(ORTHO['rho'].xreplace(subLap)).free_symbols))
    x, y, z = sp.symbols('x y z', real=True)
    alp = sp.Function('alpha')(t, x, y, z)
    h1, h2_, h3 = (sp.Function(f'h{i}')(x, y, z) for i in (1, 2, 3))
    g = sp.diag(-alp**2, h1, h2_, h3)
    gi = sp.diag(-1 / alp**2, 1 / h1, 1 / h2_, 1 / h3)
    Dop = lambda e, k: sp.diff(e, (t, x, y, z)[k])
    Gam = christoffel(g, gi, Dop)
    check('I14', 'no symmetry: -alpha(t,x,y,z)^2 dt^2 + h1 dx^2 + h2 dy^2 + h3 dz^2 with static h_i gives G_0i = R_0i = 0',
          all(sp.simplify(ricci_component(Gam, Dop, 0, i)) == 0 for i in (1, 2, 3)))

    section('I15. Divergence does not fix the algebraic type')
    rho0, p0, jx = sp.symbols('rho0 p0 jx', real=True)
    T1 = sp.diag(rho0, p0, p0, p0)
    S = sp.zeros(4)
    S[0, 1] = S[1, 0] = -jx
    mix = lambda T: sp.diag(-1, 1, 1, 1) * T
    evs = list(mix(T1 + S).subs({rho0: 1, p0: 0, jx: 1}).eigenvals().keys())
    check('I15', 'Minkowski: constant T1 = diag(rho,p,p,p) (Type I) and T1 + S, S_01 = -j (constant), are both divergence-free; '
                 'for rho=1, p=0, j=1 the second has a complex eigenpair (Type IV)', any(sp.im(e) != 0 for e in evs))
    r = sp.Symbol('r', positive=True)
    ep, em = sp.symbols('ep em', real=True)
    gM = sp.diag(-1, 1, r**2, r**2 * sp.sin(th)**2)
    giM = gM.inv()
    Dop = lambda e, k: sp.diff(e, (t, r, th, ph)[k])
    GamM = christoffel(gM, giM, Dop)
    kp_ = sp.Matrix([1, 1, 0, 0])
    km_ = sp.Matrix([1, -1, 0, 0])
    Tup = ep / r**2 * kp_ * kp_.T + em / r**2 * km_ * km_.T
    div = [sp.simplify(sum(Dop(Tup[m, nu], m) for m in range(4)) + sum(GamM[m][m][lm] * Tup[lm, nu] for m in range(4) for lm in range(4))
                       + sum(GamM[nu][m][lm] * Tup[m, lm] for m in range(4) for lm in range(4))) for nu in range(4)]
    Tl = gM * Tup * gM
    check('I15', 'Minkowski, T = (e+/r^2) k+ k+ + (e-/r^2) k- k-: divergence-free for every e+-, and '
                 'T(k+,k+) T(k-,k-) = 16 e+ e-/r^4 (Type I, II or IV by the signs alone)',
          all(dv == 0 for dv in div) and sp.simplify(bil(Tl, kp_, kp_) * bil(Tl, km_, km_) - 16 * ep * em / r**4) == 0)


# ============================================================================
# I16-I28: static identities and source relations
# ============================================================================
def items_static():
    g2, gi2, Gam2, K, dR, H, box, grad2 = (QUOT[k] for k in ('g2', 'gi2', 'Gam2', 'K', 'dR', 'H', 'box', 'grad2'))
    st = {k: jet_static(ORTHO[k]) for k in ('rho', 'j', 'pl', 'pO', 'Tpp', 'Tmm')}
    N = al
    R = Rr
    Ds = lambda e: JS.D(e, 1) / sp.sqrt(A)          # proper radial derivative d/ds
    Rs, Rss = Ds(R), Ds(Ds(R))
    Ns, Nss = Ds(N), Ds(Ds(N))
    X = Nss / N
    Y = Ns * Rs / (N * R)
    Z = Rss / R
    W = (1 - Rs**2) / R**2
    subA1 = {s: (1 if (i, j) == (0, 0) else 0) for (f, i, j), s in JS.J.items() if f == 'A'}

    section('I16. Static source decomposition')
    check_id('I16', 'static, any radial gauge (gamma_ll = A, s = proper distance, lapse N): 8 pi rho = W - 2Z', 8 * PI * st['rho'] - (W - 2 * Z))
    check_id('I16', '8 pi p_r = -W + 2Y', 8 * PI * st['pl'] - (-W + 2 * Y))
    check_id('I16', '8 pi p_t = Z + Y + X', 8 * PI * st['pO'] - (Z + Y + X))
    check_id('I16', 'static: j_l = 0', st['j'])
    Rp, Rpp = JS.D(R, 1), JS.D(JS.D(R, 1), 1)
    Np, Npp = JS.D(N, 1), JS.D(JS.D(N, 1), 1)
    Xr, Yr, Zr, Wr = Npp / N, Np * Rp / (N * R), Rpp / R, (1 - Rp**2) / R**2
    ok = all(zero_random(e.xreplace(subA1)) and zero_symbolic(e.xreplace(subA1)) for e in (
        8 * PI * st['rho'] - (Wr - 2 * Zr), 8 * PI * st['pl'] - (-Wr + 2 * Yr), 8 * PI * st['pO'] - (Zr + Yr + Xr)))
    check('I16', "report gauge ds^2 = -N^2 dt^2 + dl^2 + R^2 dOmega^2: 8 pi (rho,p_r,p_t) = W(1,-1,0) + Z(-2,0,1) + Y(0,2,1) + X(0,0,1)", ok)
    m_MS = R / 2 * (1 - jet_static(grad2))
    check_id('I16', 'W = 2 m/R^3 with the Misner-Sharp mass m = (R/2)(1 - (grad R)^2)', W - 2 * m_MS / R**3)
    check_id('I16', 'W - 2Z = 3R/2, the scalar curvature of the static slice over 2 (Hamiltonian constraint)',
             (W - 2 * Z) - sp.Rational(1, 2) * 16 * PI * st['rho'])
    check_id('I16', 'radial null energy 8 pi (rho + p_r) = 2(Y - Z)', 8 * PI * (st['rho'] + st['pl']) - (2 * Y - 2 * Z))
    check_id('I16', 'CORRECTION: angular null energy 8 pi (rho + p_t) = W - Z + Y + X, so W is null-neutral only radially',
             8 * PI * (st['rho'] + st['pO']) - (W - Z + Y + X))
    Hh = sp.Symbol('H', positive=True)
    Rb = sp.Symbol('Rb', positive=True)
    ctrl = {
        'flat (R = l, N = 1)': (dict(al=sp.Integer(1), be=sp.Integer(0), A=sp.Integer(1), B=l**2), (0, 0, 0)),
        'cylinder (R = Rb, N = 1)': (dict(al=sp.Integer(1), be=sp.Integer(0), A=sp.Integer(1), B=Rb**2), (1 / Rb**2, -1 / Rb**2, 0)),
        'de Sitter static patch (R = sin(Hl)/H, N = cos(Hl))': (
            dict(al=sp.cos(Hh * l), be=sp.Integer(0), A=sp.Integer(1), B=sp.sin(Hh * l)**2 / Hh**2), (3 * Hh**2, -3 * Hh**2, -3 * Hh**2)),
    }
    for name, (fields, target) in ctrl.items():
        vals = [sp.simplify(8 * PI * jets_of(fields, st[k])) for k in ('rho', 'pl', 'pO')]
        check('I16', f'control {name}: 8 pi (rho, p_r, p_t) = {target}', all(sp.simplify(v - tg) == 0 for v, tg in zip(vals, target)))

    section('I17. Tension and opening are separate duties')
    subMin = {JS('B', 0, 1): 0}
    check_id('I17', "at R' = 0 (any lapse, any radial gauge): p_r = -1/(8 pi R^2)", st['pl'].xreplace(subMin) + 1 / (8 * PI * B))
    check_id('I17', "at R' = 0: rho + p_r = -R_ss/(4 pi R)", (st['rho'] + st['pl']).xreplace(subMin) + Rss.xreplace(subMin) / (4 * PI * R))
    check_id('I17', 'static radial null energy: 8 pi (rho + p_r) = -(2/R)(R_ss - N_s R_s/N)', 8 * PI * (st['rho'] + st['pl']) + 2 / R * (Rss - Ns * Rs / N))
    check_id('I17', 'static: T(k+,k+) = T(k-,k-) = rho + p_r', (st['Tpp'] - st['Tmm'])**2 + (st['Tpp'] - st['rho'] - st['pl'])**2)
    R0 = sp.Symbol('R0', positive=True)
    fields = dict(al=sp.Integer(1), be=sp.Integer(0), A=sp.Integer(1), B=(R0 + l**4)**2)
    hnull = sp.simplify(jets_of(fields, st['rho'] + st['pl']))
    check('I17', "CORRECTION: a strict minimum need not have R'' > 0; R = R0 + l^4 gives rho + p_r = -3 l^2/(pi (R0 + l^4)): "
                 'zero at the throat, negative on both sides', sp.simplify(hnull + 3 * l**2 / (PI * (R0 + l**4))) == 0,
          f'rho + p_r = {sp.factor(hnull)}')

    section('I18. Flare-out identity and the opening bound')
    check_id('I18', 'static, any radial gauge: d/ds (R_s/N) = -(4 pi R/N)(rho + p_r)', Ds(Rs / N) + 4 * PI * R / N * (st['rho'] + st['pl']))
    check_id('I18', "report gauge (l proper distance, lapse N): (R'/N)' = -(4 pi R/N)(rho + p_r)",
             (JS.D(Rp / N, 1) + 4 * PI * R / N * (st['rho'] + st['pl'])).xreplace(subA1))
    aa = sp.Symbol('a', positive=True)
    val = sp.integrate(4 * PI * sp.sqrt(l**2 + aa**2) * 2 * aa**2 / (8 * PI * (l**2 + aa**2)**2), (l, 0, sp.oo))
    check('I18', 'Ellis (N = 1): 4 pi Int_0^oo R [-(rho + p_r)] dl = 1 on each side', sp.simplify(val - 1) == 0, f'value {sp.simplify(val)}')
    hsym = (st['rho'] + st['pl']).xreplace(subA1)
    syms_h = sorted(hsym.free_symbols, key=lambda z: z.name)
    lam_h = sp.lambdify(syms_h, hsym, 'mpmath')
    for Ninf, amp, l1 in ((1, sp.Rational(3, 10), 0), (1, -sp.Rational(1, 2), 0), (2, sp.Rational(3, 10), 0), (1, -sp.Rational(4, 5), 2)):
        Nf = Ninf * (1 + amp * sp.exp(-(l - l1)**2))
        Bf = l**2 + 1
        fields = dict(al=Nf, B=Bf)
        jet_exprs = [sp.diff(fields[JS.S2J[s][0]], l, JS.S2J[s][2]) for s in syms_h]
        fnum = sp.lambdify(l, jet_exprs, 'mpmath')
        Nnum = sp.lambdify(l, Nf, 'mpmath')
        Rnum = sp.lambdify(l, sp.sqrt(Bf), 'mpmath')
        integrand = lambda L: 4 * mp.pi * Rnum(L) / Nnum(L) * lam_h(*fnum(L))
        signed = mp.quad(integrand, [0, 0.5, 1, 2, 4, mp.inf])
        # negative part, integrated between the sign changes of the integrand
        grid = [mp.mpf(k) / 50 for k in range(0, 401)]
        cuts = [mp.mpf(0)]
        for i in range(len(grid) - 1):
            if integrand(grid[i]) * integrand(grid[i + 1]) < 0:
                cuts.append(mp.findroot(integrand, (grid[i], grid[i + 1]), solver='bisect'))
        cuts += [mp.mpf(8), mp.inf]
        neg = sum(max(-mp.quad(integrand, [cuts[i], cuts[i + 1]]), 0) for i in range(len(cuts) - 1))
        okn = abs(signed + mp.mpf(1) / Ninf) < mp.mpf('1e-18') and neg >= mp.mpf(1) / Ninf - mp.mpf('1e-18')
        check('I18', f'R^2 = l^2 + 1, N = {Ninf}(1 {"+" if amp > 0 else "-"} {abs(amp)} e^(-(l-{l1})^2)): '
                     f'4 pi Int_0^oo (R/N)(rho + p_r) dl = -1/N_inf and B_- >= 1/N_inf',
              okn, f'signed {mp.nstr(signed, 16)}, B_- {mp.nstr(neg, 16)}, sign changes {len(cuts) - 3}')
    Ms, r = sp.symbols('M r', positive=True)
    fsch = 1 - 2 * Ms / r
    check('I18', 'Schwarzschild exterior (proper radial derivative dr/ds = sqrt(f), N = sqrt(f)): R_s/N = 1 identically',
          sp.simplify(sp.sqrt(fsch) / sp.sqrt(fsch) - 1) == 0)
    note('I18', 'integrating the identity: 4 pi Int (R/N)[-(rho + p_r)] ds = Delta(R_s/N); hence B_- >= Delta(R_s/N) on any interval.')
    # unification: static radial null ray of unit Killing energy has dR/dlambda = R_s/N and dlambda = N ds, so
    # (R_s/N)_s = -(4 pi R/N)(rho + p_r) is I2 (d^2R/dlambda^2 = -4 pi R T(k,k)) integrated along the ray.
    kS = sp.Matrix([1 / N**2, 1 / (N * sp.sqrt(A)), 0, 0])        # static jets: E = -g(k, d_t) = 1, outgoing
    check_id('I18', 'static radial null ray with unit Killing energy: T(k,k) = (rho + p_r)/N^2 and dR/dlambda = R_s/N',
             (jet_static(bil(GS, kS, kS)) / (8 * PI) - (st['rho'] + st['pl']) / N**2)**2 +
             (jet_static(kS[0] * dR[0] + kS[1] * dR[1]) - Rs / N)**2)
    # time-dependent generalization, integrated along an actual affinely parametrized radial null geodesic
    mp.mp.dps = 20
    al_e = 1 + sp.Rational(1, 10) * sp.sin(t) * sp.exp(-l**2)
    be_e = sp.Rational(1, 5) * sp.exp(-l**2) * sp.cos(t)
    A_e = 1 + sp.Rational(1, 10) * l**2 * sp.exp(-l**2)
    B_e = (l**2 + 1) * (1 + sp.Rational(1, 10) * t * sp.exp(-l**2))
    fields = dict(al=al_e, be=be_e, A=A_e, B=B_e)
    g2e = sp.Matrix([[-al_e**2 + A_e * be_e**2, A_e * be_e], [A_e * be_e, A_e]])
    gi2e = sp.Matrix([[-1 / al_e**2, be_e / al_e**2], [be_e / al_e**2, 1 / A_e - be_e**2 / al_e**2]])
    Gam2e = christoffel(g2e, gi2e, lambda e, k: sp.diff(e, (t, l)[k]), n=2, simplify=False)
    Gab = [jets_of(fields, GS[a, b]) for a in range(2) for b in range(2)]
    Re = sp.sqrt(B_e)
    exprs = [Gam2e[a][b][c] for a in range(2) for b in range(2) for c in range(2)] + Gab + [Re, sp.diff(Re, t), sp.diff(Re, l), al_e, be_e, A_e]
    fnum = sp.lambdify((t, l), exprs, 'mpmath')

    def rhs(y):
        v = fnum(y[0], y[1])
        Gm = v[:8]
        Gv = v[8:12]
        R_, Rt, Rl = v[12:15]
        k = (y[2], y[3])
        acc = [-sum(Gm[a * 4 + b * 2 + c] * k[b] * k[c] for b in range(2) for c in range(2)) for a in range(2)]
        Gkk = sum(Gv[a * 2 + b] * k[a] * k[b] for a in range(2) for b in range(2))
        return [k[0], k[1], acc[0], acc[1], R_ * Gkk / 2], Rt * k[0] + Rl * k[1]
    t0v, l0v = mp.mpf(0), mp.mpf('-1.5')
    v0 = fnum(t0v, l0v)
    a0, b0_, A0 = v0[15], v0[16], v0[17]
    y = [t0v, l0v, mp.mpf(1), -b0_ + a0 / mp.sqrt(A0), mp.mpf(0)]
    hstep = mp.mpf(1) / 400
    F0 = None
    Fs = []
    dRs = []
    for step in range(1201):
        f1, dRdl = rhs(y)
        F = y[4] + dRdl                       # 4 pi Int R T(k,k) dlambda + dR/dlambda
        if step % 300 == 0:
            Fs.append(F)
            dRs.append(dRdl)
        k1 = f1
        k2, _ = rhs([y[i] + hstep / 2 * k1[i] for i in range(5)])
        k3, _ = rhs([y[i] + hstep / 2 * k2[i] for i in range(5)])
        k4, _ = rhs([y[i] + hstep * k3[i] for i in range(5)])
        y = [y[i] + hstep / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(5)]
    spread = max(abs(F - Fs[0]) for F in Fs)
    change = max(abs(d - dRs[0]) for d in dRs)
    mp.mp.dps = 30
    check('I18', 'time-dependent generalization (any spherical metric): along an affine radial null geodesic '
                 '4 pi Int R T(k,k) dlambda = -Delta(dR/dlambda); RK4 on a metric with alpha, beta, A, B all (t,l)-dependent',
          spread < mp.mpf('1e-9') and change > mp.mpf('1e-2'),
          f'invariant spread {mp.nstr(spread, 3)} while dR/dlambda changes by {mp.nstr(change, 4)}')

    section('I19. Clock identity (static Tolman/Komar form)')
    check_id('I19', 'static, any radial gauge: d/ds(R^2 N_s) = 4 pi R^2 N (rho + p_r + 2 p_t)',
             Ds(R**2 * Ns) - 4 * PI * R**2 * N * (st['rho'] + st['pl'] + 2 * st['pO']))
    check_id('I19', "report gauge: (R^2 N')' = 4 pi R^2 N (rho + p_r + 2 p_t)",
             (JS.D(R**2 * Np, 1) - 4 * PI * R**2 * N * (st['rho'] + st['pl'] + 2 * st['pO'])).xreplace(subA1))
    check_id('I19', 'at N_s = 0: 4 pi N (rho + p_r + 2 p_t) = N_ss (negative at a nondegenerate lapse maximum)',
             (4 * PI * N * (st['rho'] + st['pl'] + 2 * st['pO']) - Nss).xreplace({JS('al', 0, 1): 0}))
    Vv = sp.Symbol('V', positive=True)
    Tv = -Vv * sp.diag(-1, 1, 1, 1)
    check('I19', 'potential-dominated source T = -V g: rho + p_r + 2 p_t = -2V, rho + p_r = rho + p_t = 0',
          Tv[0, 0] + Tv[1, 1] + 2 * Tv[2, 2] == -2 * Vv and Tv[0, 0] + Tv[1, 1] == 0 and Tv[0, 0] + Tv[2, 2] == 0)

    section('I20. Static conservation (anisotropic TOV)')
    cons = Ds(st['pl']) + Ns / N * (st['rho'] + st['pl']) + 2 * Rs / R * (st['pl'] - st['pO'])
    check_id('I20', 'd_s p_r + (N_s/N)(rho + p_r) + 2(R_s/R)(p_r - p_t) = 0 for every static class-S Einstein tensor', cons, npts=3)

    section('I21. Ellis closed form and tail')
    note('I21', 'closed form verified in STEP 0 (explicit engine).')
    Rl = sp.sqrt(l**2 + aa**2)
    normF = sp.sqrt((aa**2 / (8 * PI * Rl**4))**2 * 4)
    Lc = sp.Symbol('L', positive=True)
    tail = sp.simplify(2 * sp.integrate(normF * 4 * PI * Rl**2, (l, Lc, sp.oo)))
    check('I21', 'two-ended tail of the orthonormal Frobenius norm beyond L: 2 Int_L^oo |T|_F 4 pi R^2 dl = 2a arctan(a/L)',
          sp.simplify(sp.tan(tail / (2 * aa)) - aa / Lc) == 0, f'value {tail}')
    c = sp.Symbol('c', positive=True)
    fields = dict(al=sp.Integer(1), be=sp.Integer(0), A=sp.Integer(1), B=(l**2 + aa**2) * c**2)
    rj = sp.simplify(jets_of(fields, ORTHO['rho']))
    pj = sp.simplify(jets_of(fields, ORTHO['pl']))
    tj = sp.simplify(jets_of(fields, ORTHO['pO']))
    Rc2 = (l**2 + aa**2) * c**2
    check('I21', 'constant jacket B = (l^2 + a^2) c^2: rho R^2 -> (1 - c^2)/(8 pi), p_l R^2 -> -(1 - c^2)/(8 pi), p_Omega R^2 -> 0',
          sp.limit(rj * 8 * PI * Rc2, l, sp.oo) == 1 - c**2 and sp.limit(pj * 8 * PI * Rc2, l, sp.oo) == -(1 - c**2)
          and sp.limit(tj * Rc2, l, sp.oo) == 0)

    section('I22. Static implies Type I; extension to stationary regions')
    check_id('I22', 'static (beta = 0, no t-dependence): j_l = 0, so T is diagonal in the static frame', st['j'])
    stat = {s: 0 for (f, i, j), s in JS.J.items() if i > 0}
    Gst = GS.xreplace(stat)
    xi = sp.Matrix([1, 0, 0, 0])
    zeta = sp.Matrix([-g4[0, 1], g4[0, 0], 0, 0])
    check_id('I22', 'stationary with shift (no t-dependence, beta(l) arbitrary): G(xi, zeta) = 0, xi = d_t, zeta orthogonal to xi',
             bil(Gst, xi, zeta), npts=3)
    check_id('I22', 'g(zeta,zeta) = g_tt det(g_quotient): zeta is spacelike where xi is timelike and timelike where xi is spacelike',
             bil(g4, zeta, zeta) - g4[0, 0] * (g4[0, 0] * g4[1, 1] - g4[0, 1]**2))
    note('I22', 'so (xi, zeta) normalized is an orthonormal radial frame with T(xi,zeta) = 0 wherever g_tt != 0: '
                'the radial block is diagonal there, Delta = (T(u,u) + T(s,s))^2 >= 0 (Type I).')

    section('I23. Canonical condensates supply no null deficit')
    Nf, Af, Bf, ff, Pf = (sp.Function(nm)(l) for nm in ('N', 'Arad', 'Bsph', 'f', 'Phi'))
    w, q = sp.symbols('omega q', real=True)
    Vf = sp.Function('V')
    g = sp.diag(-Nf**2, Af, Bf, Bf * sp.sin(th)**2)
    gi = sp.diag(-1 / Nf**2, 1 / Af, 1 / Bf, 1 / (Bf * sp.sin(th)**2))
    phi = ff * sp.exp(-sp.I * w * t)
    phic = ff * sp.exp(sp.I * w * t)
    Amu = [Pf, 0, 0, 0]
    crd = (t, l, th, ph)
    Dphi = [sp.diff(phi, crd[m]) - sp.I * q * Amu[m] * phi for m in range(4)]
    Dphic = [sp.diff(phic, crd[m]) + sp.I * q * Amu[m] * phic for m in range(4)]
    kin = sum(gi[a, b] * Dphic[a] * Dphi[b] for a in range(4) for b in range(4))
    Fmn = sp.Matrix(4, 4, lambda a, b: sp.diff(Amu[b], crd[a]) - sp.diff(Amu[a], crd[b]))
    F2 = sum(Fmn[a, b] * Fmn[c, d] * gi[a, c] * gi[b, d] for a in range(4) for b in range(4) for c in range(4) for d in range(4))
    T = sp.Matrix(4, 4, lambda a, b: Dphic[a] * Dphi[b] + Dphic[b] * Dphi[a] - g[a, b] * (kin + Vf(ff**2))
                  + (sum(Fmn[a, c] * Fmn[b, d] * gi[c, d] for c in range(4) for d in range(4)) - g[a, b] * F2 / 4) / (4 * PI))
    T = T.applyfunc(sp.simplify)
    n_ = sp.Matrix([1 / Nf, 0, 0, 0])
    e1_ = sp.Matrix([0, 1 / sp.sqrt(Af), 0, 0])
    e2_ = sp.Matrix([0, 0, 1 / sp.sqrt(Bf), 0])
    rho_c, pr_c, pt_c, j_c = (sp.simplify(bil(T, n_, n_)), sp.simplify(bil(T, e1_, e1_)), sp.simplify(bil(T, e2_, e2_)),
                              sp.simplify(-bil(T, e1_, n_)))
    Kk = (w + q * Pf)**2 * ff**2 / Nf**2
    Dd = sp.diff(ff, l)**2 / Af
    Ee = sp.diff(Pf, l)**2 / (8 * PI * Nf**2 * Af)
    VV = Vf(ff**2)
    check('I23', 'charged scalar phi = f(l) e^(-i w t) with radial electric field, static background: '
                 '(rho, p_r, p_t) = (K+D+V+E, K+D-V-E, K-D-V+E), j = 0; K = (w + q Phi)^2 f^2/N^2, D = f_s^2, E = E_r^2/(8 pi)',
          sp.simplify(rho_c - (Kk + Dd + VV + Ee)) == 0 and sp.simplify(pr_c - (Kk + Dd - VV - Ee)) == 0 and
          sp.simplify(pt_c - (Kk - Dd - VV + Ee)) == 0 and j_c == 0)
    check('I23', 'radial null stress 2(K+D) and angular null stress 2(K+E), both independent of V and nonnegative',
          sp.simplify(rho_c + pr_c - 2 * (Kk + Dd)) == 0 and sp.simplify(rho_c + pt_c - 2 * (Kk + Ee)) == 0)
    Jphi = Jets(['ph'], maxord=2)
    eps, Vs = sp.symbols('epsilon V0', real=True)
    dphi = [Jphi.D(Jphi('ph'), a) for a in range(2)]
    gradsq = sum(gi4[a, b] * dphi[a] * dphi[b] for a in range(2) for b in range(2))
    Tsc = sp.Matrix(4, 4, lambda a, b: eps * ((dphi[a] * dphi[b] if (a < 2 and b < 2) else 0) - g4[a, b] * (gradsq / 2 + Vs)))
    ok = all(zero_random(bil(Tsc, kv, kv) - eps * sum(kv[a] * dphi[a] for a in range(2))**2) for kv in (kP, kM))
    check('I23', 'time-dependent minimally coupled scalar, kinetic sign eps: T(k,k) = eps (k.dphi)^2 for both radial null k, '
                 'so Delta >= 0 (never radial Type IV) and sgn(rho + p_l) = eps', ok)
    check_id('I23', 'same scalar: p_l - p_Omega = eps (e_l.dphi)^2, so the sign of p_l - p_Omega is also tied to eps',
             bil(Tsc, eL, eL) - bil(Tsc, eT, eT) - eps * (eL[1] * dphi[1])**2)
    # where the gradient is null (d phi proportional to k+ with lowered index) the block is Type II, still never Type IV
    cnull = sp.Symbol('cnull', positive=True)
    kPlow = g4 * kP
    subNull = {Jphi('ph', 1, 0): cnull * kPlow[0], Jphi('ph', 0, 1): cnull * kPlow[1]}
    Tpp_s = bil(Tsc, kP, kP).xreplace(subNull)
    Tmm_s = bil(Tsc, kM, kM).xreplace(subNull)
    j_s = -bil(Tsc, eL, nS).xreplace(subNull)
    check('I23', 'CORRECTION: where d phi is null and nonzero, T(k+,k+) = 0 != T(k-,k-) and j != 0: Delta = 0 with a Jordan block '
                 '(Type II); "boost-diagonalizable" holds only where d phi is non-null',
          zero_random(Tpp_s) and not zero_random(Tmm_s, npts=2) and not zero_random(j_s, npts=2))
    note('I23', 'any NEC-satisfying tensor has T(k+,k+), T(k-,k-) >= 0, hence Delta >= 0 (I3): radial Type IV requires radial NEC violation.')

    section('I24. Minimal Type I regulator')
    ok = True
    for hv, jval in ((sp.Rational(3, 10), sp.Rational(1, 2)), (-sp.Rational(3, 10), sp.Rational(1, 2)), (sp.Rational(1, 5), -sp.Rational(7, 10))):
        reg = max(0, 2 * abs(jval) - abs(hv))
        hn = hv + sp.sign(hv) * reg
        ok &= abs(hn) == 2 * abs(jval) and hn**2 - 4 * jval**2 == 0
        Mreg = sp.Matrix([[-(hn - sp.Rational(1, 7)), jval], [-jval, sp.Rational(1, 7)]])     # p = 1/7 arbitrary
        evr = Mreg.eigenvals()
        ok &= len(evr) == 1 and (Mreg - list(evr.keys())[0] * sp.eye(2)).rank() == 1
    check('I24', 'reg = max(0, 2|j| - |h|), delta rho = delta p = sgn(h) reg/2 gives |h_new| = 2|j|: Delta = 0 and '
                 'a Jordan block (Type II) whenever j != 0', ok)
    note('I24', 'minimality: |h + dh| >= 2|j| forces |dh| >= 2|j| - |h| (triangle inequality); dh = sgn(h) reg attains it.')
    jz = sp.Rational(1, 3)
    regz = max(0, 2 * abs(jz) - 0)
    hz = 0 + sp.sign(0) * regz
    check('I24', 'CORNER CASE: at h = 0, j != 0 the prescription gives delta rho = delta p = sgn(0) reg/2 = 0 and leaves Delta = -4j^2 < 0; '
                 'a sign must be chosen there (either sign attains the minimum 2|j|)', hz**2 - 4 * jz**2 < 0)
    hh_, jj_, s_ = sp.symbols('h j s', positive=True)
    reg_ = 2 * jj_ - hh_                     # case 2j > h > 0 (the other sign is the mirror image)
    hnew = hh_ + s_ * reg_
    check_id('I24', 'safety factor s: |h_new| - 2|j| = (s - 1)(2|j| - |h|), so s > 1 gives Delta > 0 (Type I) and s = 1 gives Delta = 0',
             (hnew - 2 * jj_) - (s_ - 1) * reg_)

    section('I25. Heat-mode speed and the Type I margin')
    h0p = sp.Symbol('h0', positive=True)
    hh = h0p * sp.cosh(2 * ETA)
    jj = h0p * sp.sinh(2 * ETA) / 2
    vq = 2 * jj / sp.Abs(hh)
    check('I25', 'D = (rho + p)^2 (1 - v_q^2), v_q = 2 j/|rho + p|', sp.simplify((hh**2 - 4 * jj**2) - hh**2 * (1 - vq**2)) == 0)
    check('I25', 'for a Type I block boosted by eta from its rest frame: v_q = tanh(2 eta), twice the rest-frame rapidity',
          sp.simplify(vq - sp.tanh(2 * ETA)) == 0)

    section('I26. Boosted infrastructure preserves the discriminant')
    Eb, Pb, psi = sp.symbols('E_b P_b psi', real=True)
    hb = Eb + Pb
    Eboost = Eb * sp.cosh(psi)**2 + Pb * sp.sinh(psi)**2
    Pboost = Pb * sp.cosh(psi)**2 + Eb * sp.sinh(psi)**2
    jboost = hb * sp.sinh(psi) * sp.cosh(psi)
    check('I26', 'boost by psi: E, P each gain D = h_b sinh^2 psi, j_b = (h_b/2) sinh 2 psi, Delta = h_b^2 unchanged',
          sp.simplify(Eboost - (Eb + hb * sp.sinh(psi)**2)) == 0 and sp.simplify(Pboost - (Pb + hb * sp.sinh(psi)**2)) == 0 and
          sp.simplify(sp.sinh(2 * psi) * hb / 2 - jboost) == 0 and sp.simplify((Eboost + Pboost)**2 - 4 * jboost**2 - hb**2) == 0)
    Jc, cc2, hbv, vm = sp.symbols('J c h_b v', real=True)
    check('I26', '|2 j_b/h_b| <= c for j_b = J c^2 h_b^2/(J^2 + c^2 h_b^2) (since J^2 + c^2 h_b^2 - 2|J| c |h_b| = (|J| - c|h_b|)^2), '
                 'and c = 2v_max/(1 - v_max^2) = sinh(2 artanh v_max), so |v| <= v_max',
          sp.expand((Jc**2 + cc2**2 * hbv**2) - 2 * Jc * cc2 * hbv - (Jc - cc2 * hbv)**2) == 0 and
          sp.simplify(2 * vm / (1 - vm**2) - sp.expand_trig(sp.sinh(2 * sp.atanh(vm)))) == 0)

    section('I27. Areal-gauge mass relations')
    r = sp.Symbol('r', positive=True)
    ff_ = sp.Function('f')(t, r)
    aa_ = sp.Function('alpha')(t, r)
    g = sp.diag(-aa_**2, 1 / ff_, r**2, r**2 * sp.sin(th)**2)
    gi = sp.diag(-1 / aa_**2, ff_, 1 / r**2, 1 / (r**2 * sp.sin(th)**2))
    Dop = lambda e, k: sp.diff(e, (t, r, th, ph)[k])
    G, _, _, _ = einstein(g, gi, Dop)
    m = r * (1 - ff_) / 2
    n_ = sp.Matrix([1 / aa_, 0, 0, 0])
    e1_ = sp.Matrix([0, sp.sqrt(ff_), 0, 0])
    e2_ = sp.Matrix([0, 0, 1 / r, 0])
    E_ = bil(G, n_, n_) / (8 * PI)
    Pr_ = bil(G, e1_, e1_) / (8 * PI)
    J_ = -bil(G, e1_, n_) / (8 * PI)
    Pt_ = bil(G, e2_, e2_) / (8 * PI)
    check('I27', 'areal gauge, time dependent: E = m_r/(4 pi r^2)', sp.simplify(E_ - sp.diff(m, r) / (4 * PI * r**2)) == 0)
    check('I27', 'd_r log alpha = (m + 4 pi r^3 P_r)/(r (r - 2m)) holds with time dependence',
          sp.simplify(sp.diff(sp.log(aa_), r) - (m + 4 * PI * r**3 * Pr_) / (r * (r - 2 * m))) == 0)
    check('I27', 'd_t m = -4 pi r^2 alpha sqrt(f) J, J the outward Eulerian energy flux',
          sp.simplify(sp.diff(m, t) + 4 * PI * r**2 * aa_ * sp.sqrt(ff_) * J_) == 0)
    nu = sp.log(aa_)
    ftt, ft, fr = sp.diff(ff_, t, 2), sp.diff(ff_, t), sp.diff(ff_, r)
    Pt_report = (ff_ * (sp.diff(nu, r, 2) + sp.diff(nu, r)**2 + sp.diff(nu, r) / r) + fr / 2 * (sp.diff(nu, r) + 1 / r)
                 + (ftt - ft * sp.diff(nu, t) - 3 * ft**2 / (2 * ff_)) / (2 * aa_**2 * ff_))
    check('I27', 'angular equation 8 pi P_t = f(nu_rr + nu_r^2 + nu_r/r) + f_r(nu_r + 1/r)/2 + (f_tt - f_t nu_t - 3 f_t^2/(2f))/(2 alpha^2 f)',
          sp.simplify(8 * PI * Pt_ - Pt_report) == 0)
    d2 = [sp.Derivative(ff_, (t, 2)), sp.Derivative(aa_, (t, 2))]
    check('I27', 'second time derivatives appear only in P_t (E, P_r, J contain none)',
          not any(X_.has(dd) for X_ in (E_, Pr_, J_) for dd in d2) and Pt_.has(d2[0]))
    mMS = Rr / 2 * (1 - grad2)
    check_id('I27', "static class S: Misner-Sharp m = (R/2)[1 - (d_l R)^2/gamma_ll] (the report's m_b)", jet_static(mMS) - Rr / 2 * (1 - dR[1]**2 / A))
    nR = (dR[0] - be * dR[1]) / al
    check_id('I27', 'general class S: m = (R/2)[1 + (n R)^2 - (e_l R)^2]; the m_b formula needs n(R) = 0',
             mMS - Rr / 2 * (1 + nR**2 - dR[1]**2 / A))
    Tmix2 = [[sum(gi4[a, c] * GS[c, b] for c in range(2)) / (8 * PI) for b in range(2)] for a in range(2)]
    tr2 = Tmix2[0][0] + Tmix2[1][1]
    ok = all(zero_random(JS.D(mMS, a) - 4 * PI * B * (sum(Tmix2[b][a] * dR[b] for b in range(2)) - tr2 * dR[a]), npts=3)
             for a in range(2))
    check('I27', 'Misner-Sharp gradient d_a m = 4 pi R^2 (T^b_a d_b R - T^c_c d_a R) (quotient trace), general class S', ok, 'random-exact x3')

    section('I28. Onset obstruction (areal gauge)')
    u = sp.Symbol('u', positive=True)
    tau0, tau2, a_, fi, ai, cN = sp.symbols('tau0 tau2 a f_i alpha_i c_N', positive=True)
    ok = True
    for nexp in (3, 4, 9):
        tt_u = tau0 * u + tau2 * u**2
        f_u = fi * sp.exp(a_ * u**nexp)
        al_u = ai * (1 + cN * u**(nexp - 1))
        Dt = lambda e: sp.diff(e, u) / sp.diff(tt_u, u)
        ft_u = Dt(f_u)
        ftt_u = Dt(ft_u)
        nut = Dt(sp.log(al_u))
        timepart = (ftt_u - ft_u * nut - 3 * ft_u**2 / (2 * f_u)) / (2 * al_u**2 * f_u)
        ok &= sp.simplify(sp.limit(timepart / u**(nexp - 2), u, 0) - nexp * (nexp - 1) * a_ / (2 * ai**2 * tau0**2)) == 0
        J_u = -(-r * ft_u / 2) / (4 * PI * r**2 * al_u * sp.sqrt(f_u))
        ok &= sp.simplify(sp.limit(J_u / u**(nexp - 1), u, 0) - nexp * sp.sqrt(fi) * a_ / (8 * PI * r * ai * tau0)) == 0
    check('I28', 'log f = log f_i + a u^n, t = tau0 u + O(u^2), lapse change O(u^(n-1)): time part of 8 pi P_t,G = '
                 'n(n-1) a u^(n-2)/(2 alpha_i^2 tau0^2) + ..., J = j_* u^(n-1) + ..., j_* = n sqrt(f_i) a/(8 pi r alpha_i tau0)',
          ok, 'n = 3, 4, 9')
    Jv, hv_, cv = sp.symbols('J h c', real=True)
    jb = Jv * cv**2 * hv_**2 / (Jv**2 + cv**2 * hv_**2)
    Dv = hv_ * sp.sinh(sp.asinh(2 * jb / hv_) / 2)**2
    check('I28', 'registered moving family: j_b = J - J^3/(c^2 h^2) + ..., D = J^2/h + O(J^4): its stress response starts at u^(2n-2)',
          sp.simplify(sp.series(jb, Jv, 0, 4).removeO() - (Jv - Jv**3 / (cv**2 * hv_**2))) == 0 and
          sp.simplify(sp.series(Dv, Jv, 0, 4).removeO() - Jv**2 / hv_) == 0)
    note('I28', 'the obstruction compares an angular demand at u^(n-2) with a family whose angular stress starts at u^(2n-2); '
                'a family whose stresses respond linearly to the geometric acceleration removes it (see md).')


# ============================================================================
# One-space I24 cross-check
# ============================================================================
def one_space_I24():
    section('One-space I24 (knobs_one_space.md 3.1): cross-check of the same identities')
    H, dR = QUOT['H'], QUOT['dR']
    hessP = sum(kP[a] * kP[b] * H[a, b] for a in range(2) for b in range(2))
    check_id('X24', '8 pi T(k,k) = -(2/R) k^a k^b nabla_a nabla_b R for radial null k (k = n + e_l)', bil(GS, kP, kP) + 2 / Rr * hessP)
    check_id('X24', 'Delta_rad = (rho + p_l)^2 - 4 j_l^2 = T(k+,k+) T(k-,k-) on the class-S tensor',
             ORTHO['Tpp'] * ORTHO['Tmm'] - ((ORTHO['rho'] + ORTHO['pl'])**2 - 4 * ORTHO['j']**2), npts=3)
    stat = jet_static(ORTHO['rho'] + ORTHO['pl'])
    subA1 = {s: (1 if (i, j) == (0, 0) else 0) for (f, i, j), s in JS.J.items() if f == 'A'}
    Rl_ = JS.D(Rr, 1)
    check_id('X24', "static region with LAPSE A (proper distance l): (R'/A)' = -(4 pi R/A)(rho + p_l)",
             (JS.D(Rl_ / al, 1) + 4 * PI * Rr / al * stat).xreplace(subA1))
    Bc = sp.Symbol('Bc', positive=True)
    subB = {s: (Bc if (i + j == 0) else 0) for (f, i, j), s in JS.J.items() if f == 'B'}
    check('X24', 'string boost invariance: at constant R the quotient block is -g_ab/(8 pi R^2)',
          all(zero_random(GS[a, b].xreplace(subB) + g4[a, b] / Bc) for a in range(2) for b in range(2)))
    subN1 = {s: (1 if (i, j) == (0, 0) else 0) for (f, i, j), s in JS.J.items() if f == 'al'}
    check_not_id('X24', "NOTATION: reading A as gamma_ll (unit lapse), (R_l/A)_l = -(4 pi R/A)(rho + p_l) is false",
                 (JS.D(Rl_ / A, 1) + 4 * PI * Rr / A * stat).xreplace(subN1))
    check_id('X24', 'with A = gamma_ll and unit lapse the correct form is (R_l/sqrt(A))_l = -4 pi R sqrt(A)(rho + p_l)',
             (JS.D(Rl_ / sp.sqrt(A), 1) + 4 * PI * Rr * sp.sqrt(A) * stat).xreplace(subN1))


def main():
    t0 = time.time()
    build_class_S()
    print(f'class-S Einstein tensor built in {time.time() - t0:.1f} s', flush=True)
    parts = sys.argv[1:] or ['step0', 'td', 'static', 'x24']
    if 'step0' in parts:
        step0()
    if 'td' in parts:
        items_time_dependent()
    if 'static' in parts:
        items_static()
    if 'x24' in parts:
        one_space_I24()
    section('SUMMARY')
    nfail = sum(1 for r in RESULTS if not r[2])
    items = []
    for r in RESULTS:
        if r[0] not in items:
            items.append(r[0])
    for it in items:
        rs = [r for r in RESULTS if r[0] == it]
        print(f'{it:5s} {sum(r[2] for r in rs):3d}/{len(rs):3d} checks pass')
    print(f'\nTOTAL: {len(RESULTS) - nfail}/{len(RESULTS)} checks pass; runtime {time.time() - T_START:.1f} s')
    sys.exit(1 if nfail else 0)


if __name__ == '__main__':
    main()
