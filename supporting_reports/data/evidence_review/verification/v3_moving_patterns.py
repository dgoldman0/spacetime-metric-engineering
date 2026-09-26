#!/usr/bin/env python3
"""
v3_moving_patterns.py -- independent verification of the kinematics of a
moving pattern in the pattern frame (inventory knobs_one_space.md, items
I12-I17, I19, I20).

Run (single process, as the machine rules require):

    nice -n 10 env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
        python3 v3_moving_patterns.py

Conventions (book, 05_STRUCTURE.md): signature (-,+,+,+), G = c = 1.
Lab frame (class C0, transverse Cartesian x, y):

    ds^2 = -alpha^2 dsigma^2 + (dz + beta dsigma)^2 + dx^2 + dy^2 ,

with a carriage at speed v described by beta = -v (book convention).
Steady lane: alpha and beta depend on sigma only through zeta = z - v sigma.
Pattern frame: (sigma, zeta, x, y), b = beta + v,

    ds^2 = -alpha^2 dsigma^2 + (dzeta + b dsigma)^2 + dx^2 + dy^2 .

Everything here is written from scratch.  Nothing is imported or copied
from the project repository.  The script is deterministic: no random numbers,
fixed tolerances, fixed launch grids.  Results are printed and written to
v3_moving_patterns_results.json next to this file.
"""

import json
import math
import os
import sys
import time

import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = {}
CHECKS = []          # (label, passed, detail)


def check(label, passed, detail=""):
    passed = bool(passed)
    CHECKS.append((label, passed, detail))
    flag = "PASS" if passed else "FAIL"
    print(f"  [{flag}] {label}" + (f"  ({detail})" if detail else ""))
    return passed


def is_zero(expr):
    """Exact symbolic zero test (simplify, then simplify of the combined fraction)."""
    e = sp.simplify(sp.expand(expr))
    if e == 0:
        return True
    e2 = sp.simplify(sp.together(sp.expand(e)))
    return e2 == 0


# ---------------------------------------------------------------------------
# Common symbols
# ---------------------------------------------------------------------------
s, x, y, z = sp.symbols("sigma x y z", real=True)
v = sp.symbols("v", positive=True)
ps, px, py, pz = sp.symbols("p_sigma p_x p_y p_z", real=True)
X4 = (s, x, y, z)
P4 = (ps, px, py, pz)


def c0_metric(alpha, beta):
    g = sp.zeros(4, 4)
    g[0, 0] = -alpha**2 + beta**2
    g[0, 3] = g[3, 0] = beta
    g[1, 1] = g[2, 2] = g[3, 3] = 1
    return g


def hamilton_sigma(alpha, beta):
    """Hamilton's equations for H = g^{mn} p_m p_n / 2, re-parametrized by
    sigma.  Returns (dX/dsigma list, dP/dsigma list, dsigma/dlambda)."""
    g = c0_metric(alpha, beta)
    gi = sp.simplify(g.inv())
    H = sp.Rational(1, 2) * sum(gi[m, n] * P4[m] * P4[n]
                                for m in range(4) for n in range(4))
    dX = [sp.diff(H, P4[m]) for m in range(4)]
    dP = [-sp.diff(H, X4[m]) for m in range(4)]
    lam_s = sp.simplify(dX[0])
    return ([sp.simplify(d / lam_s) for d in dX],
            [sp.simplify(d / lam_s) for d in dP], lam_s, gi, H)


# ===========================================================================
# PART S1.  I12 part one: Killing energy, rate law, kept gain (symbolic)
# ===========================================================================
def sym_I12_part1():
    print("\n=== S1  I12 part one: Killing energy and rate laws (symbolic) ===")
    out = {}
    Af, Bf = sp.Function("A"), sp.Function("B")   # pattern lapse, lab shift
    zeta = z - v * s
    al_p = Af(zeta, x, y)
    be_p = Bf(zeta, x, y)
    g = c0_metric(al_p, be_p)
    xi = [1, 0, 0, v]                               # d_sigma|_zeta = d_sigma + v d_z
    # Lie derivative of g along xi (constant components): xi^k d_k g_mn
    Lg = sp.zeros(4, 4)
    for m in range(4):
        for n in range(4):
            Lg[m, n] = sp.simplify(sum(xi[k] * sp.diff(g[m, n], X4[k])
                                       for k in range(4)))
    check("S1.1 xi = d_sigma + v d_z is Killing for alpha(z - v sigma, x, y),"
          " beta(z - v sigma, x, y)", Lg == sp.zeros(4, 4))

    # E = -p.xi and its 3+1 form
    E = -(ps + v * pz)
    n_up = [1 / al_p, 0, 0, -be_p / al_p]             # Eulerian observer
    En = -sum(n_up[m] * P4[m] for m in range(4))       # energy they measure
    b_pat = be_p + v
    check("S1.2 E = -p.xi equals alpha*E_n - b*p_z with b = beta + v",
          is_zero(E - (al_p * En - b_pat * pz)))

    # General lab-frame rate laws for arbitrary alpha(s,x,y,z), beta(s,x,y,z)
    a = sp.Function("a")(s, x, y, z)
    b = sp.Function("b")(s, x, y, z)
    dXs, dPs, lam_s, gi, H = hamilton_sigma(a, b)
    Q = ps - b * pz
    En_g = -Q / a
    # geodesic equations in the compact form used by the numerical engine
    ok_x = is_zero(dXs[1] - a * px / En_g) and is_zero(dXs[2] - a * py / En_g) \
        and is_zero(dXs[3] - (a * pz / En_g - b))
    ok_p = all(is_zero(dPs[m] - (pz * sp.diff(b, X4[m]) - En_g * sp.diff(a, X4[m])))
               for m in range(4))
    check("S1.3 sigma-parametrized geodesic equations: dx^i/dsigma = alpha k^i/E_n"
          " - beta^i, dp_m/dsigma = p_z d_m beta - E_n d_m alpha", ok_x and ok_p)

    # explicit: dE/dsigma = 0 along the flow when alpha, beta depend on z - v sigma
    dXp, dPp, _, _, _ = hamilton_sigma(al_p, be_p)
    dE_dsig = -(dPp[0] + v * dPp[3])
    check("S1.2b dE/dsigma = -(dp_sigma/dsigma + v dp_z/dsigma) = 0 along every geodesic"
          " of a steady pattern", is_zero(dE_dsig))

    # rate of E_n along any geodesic (off-shell identity)
    def along(f):
        """d f / d sigma along the Hamiltonian flow."""
        tot = sp.diff(f, s)
        for i in (1, 2, 3):
            tot += sp.diff(f, X4[i]) * dXs[i]
        for m in range(4):
            tot += sp.diff(f, P4[m]) * dPs[m]
        return tot

    kvec = (px, py, pz)
    grad = lambda f: (sp.diff(f, x), sp.diff(f, y), sp.diff(f, z))
    kdot = lambda u, w: sum(ui * wi for ui, wi in zip(u, w))
    dEn = along(En_g)
    claim_dEn = pz * kdot(kvec, grad(b)) / En_g - kdot(kvec, grad(a))
    check("S1.4 dE_n/dsigma = p_z (k.grad beta)/E_n - k.grad alpha  (any geodesic,"
          " any time dependence)", is_zero(dEn - claim_dEn))
    # For light E_n = |k|; the pure-lapse law needs grad beta = 0 along k
    out["rate_law_general"] = ("d ln|k|/dsigma = khat_z (khat.grad beta)"
                               " - khat.grad alpha")

    # lapse-weighted energy: d ln(alpha E_n)/dsigma = alpha n(ln alpha) + shear
    dlnaEn = along(sp.log(a)) + dEn / En_g
    alpha_n_lnalpha = (sp.diff(a, s) - b * sp.diff(a, z)) / a
    claim = alpha_n_lnalpha + pz * kdot(kvec, grad(b)) / En_g**2
    check("S1.5 d ln(alpha E_n)/dsigma = (d_sigma - beta d_z) ln alpha"
          " + p_z (k.grad beta)/E_n^2", is_zero(dlnaEn - claim))

    # steady lane: (d_sigma - beta d_z) ln alpha = -b d_zeta ln alpha
    steady = (sp.diff(al_p, s) - be_p * sp.diff(al_p, z)) / al_p
    target = -(be_p + v) * sp.diff(al_p, z) / al_p
    check("S1.6 steady lane: (d_sigma - beta d_z) ln alpha = -b d_zeta ln alpha",
          is_zero(steady - target))
    out["kept_gain_identity"] = ("ln(alpha_f|k_f|/alpha_i|k_i|) = int[ b(-d_zeta ln alpha)"
                                 " + khat_z (khat.grad beta) ] dsigma ;"
                                 " beta = 0 on the path => int v(-d_zeta ln alpha) dsigma")
    return out


# ===========================================================================
# PART S2.  I12 part two: exit-angle law and shelf law (symbolic)
# ===========================================================================
def sym_I12_part2():
    print("\n=== S2  I12 part two: exit-angle and shelf laws (symbolic) ===")
    out = {}
    K, Kf, th, thf = sp.symbols("K K_f theta theta_f", positive=True)
    # exterior: alpha = 1, beta = 0, b = v  ->  E = |k|(1 - v cos theta)
    Ei = K * (1 - v * 1)            # launched along +z (overtaken, v > 1)
    Ef = Kf * (1 - v * sp.cos(thf))
    gain = sp.solve(sp.Eq(Ei, Ef), Kf)[0] / K
    check("S2.1 exit-angle law: gain = (v-1)/(v cos theta_f - 1)",
          is_zero(gain - (v - 1) / (v * sp.cos(thf) - 1)))
    out["exit_angle_general"] = "gain = (1 - v cos theta_i)/(1 - v cos theta_f)"
    # negative Killing energy for v>1 => cos theta_f > 1/v
    out["exit_angle_range"] = "cos theta_f > 1/v (overtaken light exits inside arccos(1/v))"

    # Shelf law: particle at rest in shelf alpha_s: E = alpha_s m (m = 1)
    als, gam = sp.symbols("alpha_s gamma", positive=True)
    sols = sp.solve(sp.Eq(als * gam - v * sp.sqrt(gam**2 - 1), als), gam)
    sols = [sp.simplify(q) for q in sols]
    target = (als**2 + v**2) / (als**2 - v**2)
    check("S2.2 shelf law: alpha_s gamma - v sqrt(gamma^2-1) = alpha_s has the"
          " non-trivial root (alpha_s^2+v^2)/(alpha_s^2-v^2)",
          any(is_zero(q - target) for q in sols), f"roots {sols}")
    # turning point: E = m sqrt(alpha^2 - v^2) at pattern-frame rest
    al_t = sp.symbols("alpha_t", positive=True)
    En_t = al_t / sp.sqrt(al_t**2 - v**2)          # gamma w.r.t. Eulerian at u = v/alpha
    E_t = al_t * En_t - v * (En_t * v / al_t)
    check("S2.3 pattern-frame turning point: E = m sqrt(alpha^2 - v^2)",
          is_zero(sp.simplify(E_t - sp.sqrt(al_t**2 - v**2))))
    # moving-mirror reading: u = v/alpha_s, gamma' = (1+u^2)/(1-u^2)
    u = v / als
    check("S2.4 same as reflection off a mirror moving at v/alpha_s in the shelf's"
          " light units", is_zero((1 + u**2) / (1 - u**2) - target))
    # off-axis exit at angle th to the axis inside the shelf
    c = sp.symbols("c", positive=True)            # c = cos(theta')
    sols2 = sp.solve(sp.Eq(als * gam - v * c * sp.sqrt(gam**2 - 1), als), gam)
    target2 = (als**2 + v**2 * c**2) / (als**2 - v**2 * c**2)
    check("S2.5 exit at angle theta' in the shelf: gamma' = (alpha_s^2+v^2cos^2)/"
          "(alpha_s^2-v^2cos^2), maximal on the axis",
          any(is_zero(sp.simplify(q) - target2) for q in sols2))
    # running leading edge (u_e > alpha_s): (u_e - 1)/(u_e - alpha_s)
    ue, K2 = sp.symbols("u_e K_2", positive=True)
    g_edge = sp.solve(sp.Eq(K * (1 - ue), K2 * (als - ue)), K2)[0] / K
    check("S2.6 corollary: light overtaken by a shelf edge running at u_e > alpha_s"
          " gains (u_e-1)/(u_e-alpha_s)", is_zero(g_edge - (ue - 1) / (ue - als)))
    out["shelf_numbers_report"] = {
        "gamma_prime(alpha_s=e, v=2.1)": float(target.subs({als: sp.E, v: 2.1})),
        "terminal alpha_s*gamma_prime": float((als * target).subs({als: sp.E, v: 2.1})),
        "edge gain (u_e=3.5)": float(((ue - 1) / (ue - als)).subs({ue: 3.5, als: sp.E})),
    }
    print("   report numbers reproduced:", out["shelf_numbers_report"])
    return out


# ===========================================================================
# PART S3.  I13 horizon criterion, surface gravity, null-surface criterion
# ===========================================================================
def sym_I13():
    print("\n=== S3  I13: light surface, Killing horizon, surface gravity (symbolic) ===")
    out = {}
    zt, r, ph = sp.symbols("zeta r phi", real=True)
    al = sp.Function("alpha")(zt, r, ph)
    bb = sp.Function("b")(zt, r, ph)
    Xp = (s, zt, r, ph)
    g = sp.zeros(4, 4)
    g[0, 0] = -al**2 + bb**2
    g[0, 1] = g[1, 0] = bb
    g[1, 1] = 1
    g[2, 2] = 1
    g[3, 3] = r**2
    gi = sp.simplify(g.inv())
    check("S3.0 pattern-frame inverse metric: g^ss=-1/alpha^2, g^sz=b/alpha^2,"
          " g^zz=1-b^2/alpha^2",
          is_zero(gi[0, 0] + 1 / al**2) and is_zero(gi[0, 1] - bb / al**2)
          and is_zero(gi[1, 1] - (1 - bb**2 / al**2)))
    # values and first derivatives at a point are independent symbols; on S only
    # the values satisfy b = +-alpha
    A_, B_ = sp.symbols("A B", positive=True)
    az, ar, ap, bz, br, bp = sp.symbols("a_z a_r a_p b_z b_r b_p", real=True)
    Fz = 2 * A_ * az - 2 * B_ * bz
    Fr = 2 * A_ * ar - 2 * B_ * br
    Fp = 2 * A_ * ap - 2 * B_ * bp
    gi_pt = gi.subs({al: A_, bb: B_})
    dF = [0, Fz, Fr, Fp]
    norm = sp.simplify(sum(gi_pt[m, n] * dF[m] * dF[n] for m in range(4) for n in range(4)))
    ok = True
    for sgn in (1, -1):
        normS = norm.subs(B_, sgn * A_)
        ok &= is_zero(normS - (Fr**2 + Fp**2 / r**2).subs(B_, sgn * A_))
    check("S3.1 on S (alpha^2 = b^2): |dF|^2 = F_r^2 + F_phi^2/r^2 >= 0, so S is"
          " null exactly where its transverse gradient vanishes, timelike elsewhere", ok)

    # Killing vector xi = d_sigma: covector xi_m = g_{m sigma}
    xi_low = [g[m, 0] for m in range(4)]
    on_S_xi = [sp.simplify(q.subs(bb, al)) for q in xi_low]
    check("S3.2 on S the Killing covector is xi_m = (0, b, 0, 0), i.e. proportional"
          " to d zeta; it is normal to S iff F_r = F_phi = 0",
          on_S_xi[0] == 0 and on_S_xi[2] == 0 and on_S_xi[3] == 0)

    # Surface gravity on a planar (r-, phi-independent) portion
    a1 = sp.Function("alpha")(zt)
    b1 = sp.Function("b")(zt)
    g1 = sp.zeros(4, 4)
    g1[0, 0] = -a1**2 + b1**2
    g1[0, 1] = g1[1, 0] = b1
    g1[1, 1] = 1
    g1[2, 2] = 1
    g1[3, 3] = r**2
    g1i = sp.simplify(g1.inv())

    def christoffel(gm, gmi, X):
        n = len(X)
        G = [[[0] * n for _ in range(n)] for _ in range(n)]
        for m in range(n):
            for i in range(n):
                for j in range(n):
                    G[m][i][j] = sp.simplify(sum(
                        gmi[m, l] * (sp.diff(gm[l, i], X[j]) + sp.diff(gm[l, j], X[i])
                                     - sp.diff(gm[i, j], X[l])) for l in range(n)) / 2)
        return G
    Gm = christoffel(g1, g1i, Xp)
    acc = [sp.simplify(Gm[m][0][0]) for m in range(4)]    # xi^n nabla_n xi^m
    Ah, Ap, Bh, Bp = sp.symbols("A A' B B'", real=True)
    rep = {sp.diff(a1, zt): Ap, sp.diff(b1, zt): Bp}
    acc_s = [sp.simplify(q.subs(rep).subs({a1: Ah, b1: Bh})) for q in acc]
    kap_plus = sp.simplify(acc_s[0].subs(Bh, Ah))     # b = +alpha
    kap_minus = sp.simplify(acc_s[0].subs(Bh, -Ah))   # b = -alpha
    check("S3.3 on S: xi^n nabla_n xi^m = kappa xi^m with a^zeta = 0",
          is_zero(acc_s[1].subs(Bh, Ah)) and is_zero(acc_s[1].subs(Bh, -Ah)))
    check("S3.4 signed kappa = d_zeta(alpha - b) for b = +alpha > 0"
          " (and -d_zeta(alpha - |b|) for b = -alpha)",
          is_zero(kap_plus - (Ap - Bp)) and is_zero(kap_minus - (-(Ap + Bp))))
    # kappa^2 = -1/2 nabla_m xi_n nabla^m xi^n
    xil = [g1[m, 0] for m in range(4)]
    cov = sp.zeros(4, 4)                    # nabla_m xi_n = d_m xi_n - Gamma^l_{mn} xi_l
    for m in range(4):
        for n in range(4):
            cov[m, n] = sp.diff(xil[n], Xp[m]) - sum(Gm[l][m][n] * xil[l] for l in range(4))
    inv2 = sum(g1i[m, p] * g1i[n, q] * cov[m, n] * cov[p, q]
               for m in range(4) for n in range(4) for p in range(4) for q in range(4))
    k2 = sp.simplify((-sp.Rational(1, 2) * inv2).subs(rep).subs({a1: Ah, b1: Bh}))
    check("S3.5 kappa^2 = -1/2 (nabla xi)^2 = (d_zeta(alpha - b))^2 on S",
          is_zero(k2.subs(Bh, Ah) - (Ap - Bp)**2))
    # where the lab shift vanishes b = v (const): kappa = |d_zeta alpha|
    check("S3.6 where the lab shift vanishes (b = v, B' = 0): kappa = d_zeta alpha",
          is_zero(kap_plus.subs(Bp, 0) - Ap))
    # normalization: xi -> c xi rescales kappa -> c kappa
    out["kappa_normalization"] = ("xi = d_sigma|_zeta, sigma = proper time of static"
                                  " exterior observers; xi -> c xi gives kappa -> c kappa")

    # Unified stationary null-surface criterion (C0: b along zeta)
    xx, yy = sp.symbols("x y", real=True)
    Fg = sp.Function("F")(zt, xx, yy)
    alg = sp.Function("alpha")(zt, xx, yy)
    bg = sp.Function("b")(zt, xx, yy)
    ginv_c = sp.Matrix([[-1 / alg**2, bg / alg**2, 0, 0],
                        [bg / alg**2, 1 - bg**2 / alg**2, 0, 0],
                        [0, 0, 1, 0], [0, 0, 0, 1]])
    dFg = [0, sp.diff(Fg, zt), sp.diff(Fg, xx), sp.diff(Fg, yy)]
    nrm = sum(ginv_c[m, n] * dFg[m] * dFg[n] for m in range(4) for n in range(4))
    grad2 = sp.diff(Fg, zt)**2 + sp.diff(Fg, xx)**2 + sp.diff(Fg, yy)**2
    Nz = sp.diff(Fg, zt) / sp.sqrt(grad2)
    check("S3.7 stationary surface F(x)=0: g^{mn}F_mF_n = |grad F|^2 (1 - (b N_zeta)^2"
          "/alpha^2): null iff |b.N| = alpha, timelike iff |b.N| < alpha",
          is_zero(nrm - grad2 * (1 - bg**2 * Nz**2 / alg**2)))
    out["null_surface_criterion"] = "|b.N| = alpha (N the unit normal in the flat slice)"

    # Rest points of the pattern-frame light-ray flow
    Ez, pzt, pxx, pyy = sp.symbols("E p_zeta p_x p_y", real=True)
    Hp = sp.Rational(1, 2) * (-(Ez + bg * pzt)**2 / alg**2 + pzt**2 + pxx**2 + pyy**2)
    vel = [sp.diff(Hp, pzt), sp.diff(Hp, pxx), sp.diff(Hp, pyy)]
    force = [-sp.diff(Hp, zt), -sp.diff(Hp, xx), -sp.diff(Hp, yy)]
    # point values: alpha -> A, b -> B, first derivatives -> independent symbols
    ax_, ay_, azt_, bx_, by_, bzt_ = sp.symbols("a_x a_y a_zeta b_x b_y b_zeta", real=True)
    pt = {sp.Derivative(alg, xx): ax_, sp.Derivative(alg, yy): ay_, sp.Derivative(alg, zt): azt_,
          sp.Derivative(bg, xx): bx_, sp.Derivative(bg, yy): by_, sp.Derivative(bg, zt): bzt_}
    P = sp.symbols("P", positive=True)                # p_zeta = +P
    # null, future directed: E + b p_zeta = alpha |p|; at p_perp = 0: E = (A - B) P
    subs_rest = {pxx: 0, pyy: 0, pzt: P, Ez: (A_ - B_) * P}
    v_rest = [sp.simplify(q.subs(pt).subs({alg: A_, bg: B_}).subs(subs_rest)) for q in vel]
    check("S3.8 a null ray with p_perp = 0 has zero pattern-frame velocity iff"
          " b = alpha (with p_zeta along b)",
          all(is_zero(q.subs(B_, A_)) for q in v_rest) and not is_zero(v_rest[0]),
          f"v_zeta = {sp.factor(v_rest[0])}")
    f_rest = [sp.simplify(q.subs(pt).subs({alg: A_, bg: B_}).subs(subs_rest).subs(B_, A_))
              for q in force]
    check("S3.9 there the transverse force is -(P^2/alpha) d_perp(alpha - b): a ray"
          " rests in position and direction only where d_perp(alpha^2 - b^2) = 0,"
          " i.e. at the null points of S",
          is_zero(f_rest[1] + P**2 / A_ * (ax_ - bx_)) and is_zero(f_rest[2] + P**2 / A_ * (ay_ - by_)),
          f"longitudinal force {sp.factor(f_rest[0])} (the blueshift)")
    return out


# ===========================================================================
# PART S4.  I14 tip rates: paraxial linearization
# ===========================================================================
def sym_I14():
    print("\n=== S4  I14: paraxial tip rates (symbolic) ===")
    out = {}
    zt, xx, yy = sp.symbols("zeta x y", real=True)
    kap, Acurv = sp.symbols("kappa A", positive=True)
    ux, uy = sp.symbols("u_x u_y", real=True)
    # general stationary pattern, shift-free there (b = v); ray flow in terms of
    # position and direction u = p/|p| (null rays), derived from H
    alg = sp.Function("alpha")(zt, xx, yy)
    E, pzt, pxx, pyy = sp.symbols("E p_zeta p_x p_y", real=True)
    Kp = sp.symbols("K", positive=True)
    Hp = sp.Rational(1, 2) * (-(E + v * pzt)**2 / alg**2 + pzt**2 + pxx**2 + pyy**2)
    lam_s = sp.diff(Hp, E) * (-1)          # dsigma/dlambda = dH/dp_sigma, p_sigma = -E
    lam_s = sp.simplify((E + v * pzt) / alg**2)
    Xd = [sp.diff(Hp, q) / lam_s for q in (pzt, pxx, pyy)]
    Pd = [-sp.diff(Hp, q) / lam_s for q in (zt, xx, yy)]
    uz = sp.sqrt(1 - ux**2 - uy**2)
    rep = {pzt: Kp * uz, pxx: Kp * ux, pyy: Kp * uy, E: alg * Kp - v * Kp * uz}
    Xd = [sp.simplify(q.subs(rep)) for q in Xd]
    Pd = [sp.simplify(q.subs(rep)) for q in Pd]
    # direction equations du_i/dsigma = (dp_i - u_i (u.dp))/K
    udp = ux * Pd[1] + uy * Pd[2] + uz * Pd[0]
    Ud = [sp.simplify((Pd[1] - ux * udp) / Kp), sp.simplify((Pd[2] - uy * udp) / Kp)]
    check("S4.1 ray-direction equations are independent of |p| (null rays)",
          all(is_zero(sp.diff(q, Kp)) for q in Ud + Xd))
    # paraxial model: alpha = v - kappa*zeta - A (x^2+y^2)/2 near the tip (zeta=0)
    model = v - kap * zt - Acurv * (xx**2 + yy**2) / 2
    sysf = [q.subs(alg, model).doit() for q in (Xd + Ud)]
    state = (zt, xx, yy, ux, uy)
    J = sp.Matrix([[sp.diff(f, w) for w in state] for f in sysf])
    J0 = sp.simplify(J.subs({zt: 0, xx: 0, yy: 0, ux: 0, uy: 0}))
    print("   Jacobian at the tip fixed point (zeta, x, y, u_x, u_y):")
    sp.pprint(J0)
    lamb = sp.symbols("lambda")
    charp = sp.factor(sp.simplify((J0 - lamb * sp.eye(5)).det()))
    print("   characteristic polynomial:", charp)
    lam_plus = (sp.sqrt(kap**2 + 4 * v * Acurv) - kap) / 2
    ok = is_zero(charp.subs(lamb, -kap)) and is_zero(sp.expand(charp.subs(lamb, lam_plus)))
    check("S4.2 tip eigenvalues: -kappa (along track) and lambda_pm from"
          " lambda^2 + kappa lambda - v A = 0; lambda_+ = (sqrt(kappa^2+4vA)-kappa)/2",
          ok)
    # energy growth rate on the axis ray at the tip: d ln|k|/dsigma = -u.grad alpha
    rate = sp.simplify(-(uz * sp.diff(model, zt) + ux * sp.diff(model, xx)
                         + uy * sp.diff(model, yy)).subs({xx: 0, yy: 0, ux: 0, uy: 0}))
    check("S4.3 energy per quantum on the axis ray grows at d ln|k|/dsigma = kappa",
          is_zero(rate - kap))
    dens = sp.simplify(kap - (-kap + 2 * lam_plus))
    check("S4.4 geometric-optics density exponent: kappa - (-kappa + 2 lambda_+)"
          " = 2(kappa - lambda_+)", is_zero(dens - 2 * (kap - lam_plus)))
    # Barcelo et al. 2022 eq. (19): eta_- = (kappa_B/2)(sqrt(1+8 xi/kappa_B^2) - 1)
    kB, xiB = sp.symbols("kappa_B xi_B", positive=True)
    eta_minus = kB / 2 * (sp.sqrt(1 + 8 * xiB / kB**2) - 1)
    check("S4.5 dictionary: Barcelo et al. eta_- with kappa_B = kappa, xi_B = v A/2"
          " equals lambda_+", is_zero(sp.simplify(eta_minus.subs({kB: kap, xiB: v * Acurv / 2})
                                                  - lam_plus)))
    out["report_numbers"] = {
        "lambda(kappa=0.563, A=4.20, v=2.1)": float(lam_plus.subs({kap: 0.563, Acurv: 4.20, v: 2.1})),
        "2(kappa-lambda)": float((2 * (kap - lam_plus)).subs({kap: 0.563, Acurv: 4.20, v: 2.1})),
    }
    print("   report numbers:", out["report_numbers"])
    return out


# ===========================================================================
# PART S5.  I15 flank criterion
# ===========================================================================
def sym_I15():
    print("\n=== S5  I15: flank normal speed (symbolic) ===")
    th = sp.symbols("theta_c", positive=True)
    f = sp.Function("f")
    # level surfaces of alpha = f(N.(x - v sigma e_z)), N = (cos th, 0, sin th)
    n_expr = sp.cos(th) * x + sp.sin(th) * (z - v * s)
    same = sp.simplify(n_expr - (sp.cos(th) * x + sp.sin(th) * z - v * sp.sin(th) * s))
    check("S5.1 a planar layer moving at v along z is the same metric as the layer"
          " moving along its normal N at u = v sin(theta_c)", same == 0)
    # null level from the unified criterion: |b N_zeta| = alpha with b = v, N_zeta = sin th
    al = sp.symbols("alpha", positive=True)
    lvl = sp.solve(sp.Eq(v * sp.sin(th), al), al)[0]
    check("S5.2 the level alpha = v sin(theta_c) of the layer is null (stationary"
          " null-surface criterion)", is_zero(lvl - v * sp.sin(th)))
    check("S5.3 threshold v sin(theta_c) = 1 is theta_c = arcsin(1/v), the Mach angle",
          is_zero(sp.sin(sp.asin(1 / v)) * v - 1))
    return {"threshold_15deg": 1.0 / math.sin(math.radians(15.0))}


# ===========================================================================
# PART S6.  I16 lapse cavity optics
# ===========================================================================
def sym_I16():
    print("\n=== S6  I16: static pure-lapse optics (symbolic) ===")
    ai, ao, psi = sp.symbols("alpha_in alpha_out psi", positive=True)
    K = sp.symbols("K", positive=True)
    # static (b = 0): E = alpha |k| conserved; planar layer: k_parallel conserved
    Ko = ai * K / ao
    sin_out = K * sp.sin(psi) / Ko
    check("S6.1 Snell: sin(psi_out) = (alpha_out/alpha_in) sin(psi_in) (index 1/alpha)",
          is_zero(sin_out - ao / ai * sp.sin(psi)))
    # total reflection iff sin_out > 1  <=> sin psi > alpha_in/alpha_out (needs alpha_in < alpha_out)
    sp_ = sp.symbols("s_psi", positive=True)                      # sin(psi_in) in (0, 1]
    excess = sp.expand((ao / ai * sp_ - 1) - (ao / ai) * (sp_ - ai / ao))
    thr = sp.solve(sp.Eq(ao / ai * sp_, 1), sp_)[0]
    check("S6.2 total reflection iff sin(psi_in) > alpha_in/alpha_out, possible only"
          " for alpha_in < alpha_out", excess == 0 and is_zero(thr - ai / ao),
          "sin_out - 1 = (alpha_out/alpha_in)(sin psi - alpha_in/alpha_out); threshold < 1 iff alpha_in < alpha_out")
    # pattern frame with uniform b != 0 is not static: alpha(zeta) under zeta' = zeta + b sigma
    bb = sp.symbols("b", positive=True)
    zt = sp.symbols("zeta")
    A = sp.Function("alpha")
    expr = A(zt)
    moved = expr.subs(zt, zt - bb * s)       # zeta = zeta' - b sigma
    check("S6.3 a uniform b != 0 cannot be removed without making alpha time"
          " dependent (the static-optics hypothesis needs b = 0, i.e. beta = -v)",
          sp.diff(moved, s) != 0)
    # spherical symmetry: k_r^2 = E^2/alpha^2 - L^2/r^2
    r, E, L = sp.symbols("r E L", positive=True)
    return {"sphere_escape": "k_r^2 = E^2/alpha^2 - L^2/r^2 >= 0  <=>  r/alpha(r) >= L/E"}


# ===========================================================================
# PART S7.  I17 Tolman reading
# ===========================================================================
def sym_I17():
    print("\n=== S7  I17: Tolman reading (symbolic) ===")
    al, bb, c, kap, om = sp.symbols("alpha b c kappa omega", positive=True)
    N2 = -(-al**2 + bb**2)                         # -g(xi, xi), xi = d_sigma|_zeta
    check("S7.1 N^2 = -g(xi,xi) = alpha^2 - b^2; N = alpha_c in the compartment (b=0)",
          is_zero(N2 - (al**2 - bb**2)))
    # rescaling xi -> c xi: kappa -> c kappa, N -> c N
    check("S7.2 kappa/(2 pi N) is invariant under xi -> c xi",
          is_zero((c * kap) / (c * sp.sqrt(N2)) - kap / sp.sqrt(N2)))
    # local frequency of a mode with Killing frequency omega seen by u = xi/N
    # explicit: pattern-frame metric at a point, xi = d_sigma, u = xi/N, generic covector p
    P = sp.symbols("P0:4", real=True)
    gpt = sp.Matrix([[-al**2 + bb**2, bb, 0, 0], [bb, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    xi_up = sp.Matrix([1, 0, 0, 0])
    N = sp.sqrt(-(xi_up.T * gpt * xi_up)[0])
    u_up = xi_up / N
    omega_loc = -sum(P[m] * u_up[m] for m in range(4))
    omega_K = -sum(P[m] * xi_up[m] for m in range(4))
    check("S7.3 a pattern-static observer (u = xi/N) measures omega_loc = omega/N,"
          " so a Planck spectrum at kappa/2pi becomes one at kappa/(2 pi N)",
          is_zero(omega_loc - omega_K / sp.sqrt(al**2 - bb**2)) and is_zero((u_up.T * gpt * u_up)[0] + 1),
          "u.u = -1 and -p.u = -p.xi/N for a generic covector p")
    return {}


# ===========================================================================
# PART S8.  I19, I20 causality and light speeds
# ===========================================================================
def sym_I19_I20():
    print("\n=== S8  I19, I20: time function, light speeds, static observers ===")
    out = {}
    a = sp.Function("alpha")(s, x, y, z)
    b = sp.Function("beta")(s, x, y, z)
    A = sp.Function("A")(s, x, y, z)
    g = c0_metric(a, b)
    gi = sp.simplify(g.inv())
    check("S8.1 C0: g^{sigma sigma} = -1/alpha^2 < 0 (sigma is a time function)",
          is_zero(gi[0, 0] + 1 / a**2))
    gA = sp.zeros(4, 4)
    gA[0, 0] = -a**2 + A**2 * b**2
    gA[0, 3] = gA[3, 0] = A**2 * b
    gA[3, 3] = A**2
    gA[1, 1] = gA[2, 2] = 1
    giA = sp.simplify(gA.inv())
    check("S8.2 C0A (stretch A): g^{sigma sigma} = -1/alpha^2 as well",
          is_zero(giA[0, 0] + 1 / a**2))
    # widening g_c = g - c dsigma^2 keeps sigma a time function
    c = sp.symbols("c", positive=True)
    gc = g.copy()
    gc[0, 0] = gc[0, 0] - c
    gci = sp.simplify(gc.inv())
    check("S8.3 widened metric g - c dsigma^2 (c > 0): g_c^{ss} = g^{ss}/(1 + c/alpha^2) < 0",
          is_zero(gci[0, 0] - (-1 / a**2) / (1 + c / a**2)))
    # counterexample to global hyperbolicity: alpha = 1 + z^2, beta = 0
    zf = sp.Function("zf")
    ode = sp.Eq(zf(s).diff(s), 1 + zf(s)**2)
    sol = sp.dsolve(ode, zf(s), ics={zf(0): 0})
    check("S8.4 alpha = 1 + z^2: the light ray z = tan(sigma) leaves every compact set"
          " at sigma = pi/2 (slices sigma > pi/2 are not met)",
          sp.simplify(sol.rhs - sp.tan(s)) == 0)
    # radial / along-track null speeds of a 2D block
    al2, be2, gl = sp.symbols("alpha beta gamma_ll", positive=True)
    w = sp.symbols("w")
    roots = sp.solve(sp.Eq(-al2**2 + gl * (w + be2)**2, 0), w)
    target = {sp.simplify(-be2 + al2 / sp.sqrt(gl)), sp.simplify(-be2 - al2 / sp.sqrt(gl))}
    check("S8.5 null speeds of -alpha^2 dsigma^2 + gamma(dl + beta dsigma)^2:"
          " dl/dsigma = -beta +- alpha/sqrt(gamma)",
          {sp.simplify(q) for q in roots} == target)
    # static observers: g_ss < 0
    check("S8.6 fixed (z,x,y) is timelike iff alpha^2 > beta^2 (C0), alpha^2 > A^2"
          " beta^2 (C0A)", is_zero(g[0, 0] - (b**2 - a**2)) and is_zero(gA[0, 0] - (A**2 * b**2 - a**2)))
    return out


# ===========================================================================
# NUMERICAL ENGINE: lab-frame null and timelike geodesics
# ===========================================================================
DELTA_CUT = 1e-3


def cstep(u):
    """C-infinity step: 0 for u <= -1, 1 for u >= 1 (exactly, in double
    precision beyond |u| = 1 - 1e-3), smooth in between."""
    return sp.Piecewise((0, u <= -1 + DELTA_CUT), (1, u >= 1 - DELTA_CUT),
                        ((1 + sp.tanh(u / (1 - u**2))) / 2, True))


def window(q, a0, a1, w):
    """1 on [a0 + w, a1 - w], 0 outside (a0 - w, a1 + w)."""
    return cstep((q - a0) / w) * cstep((a1 - q) / w)


def rwindow(r2, R, w):
    """radial window in r^2 (smooth in Cartesian x, y): 1 for r^2 <= R^2 - 2Rw."""
    return cstep((R**2 - r2) / (2 * R * w))


class Pattern:
    """Holds sympy expressions alpha(sigma,x,y,z), beta(sigma,x,y,z) and a
    fast lambdified field evaluator returning
    (alpha, a_s, a_x, a_y, a_z, beta, b_s, b_x, b_y, b_z).

    Geodesics are integrated in Eulerian variables: position x^i and the
    spatial momentum k_i = p_i measured by the normal observers, with
    E_n = sqrt(m^2 + |k|^2).  The mass shell is then exact, and the Killing
    energy E = alpha E_n - b k_z (b = beta + v) is *not* a linear invariant of
    the state, so its conservation is a genuine accuracy test."""

    def __init__(self, name, alpha, beta, vel):
        self.name = name
        self.alpha = alpha
        self.beta = beta
        self.v = float(vel)
        exprs = [alpha] + [sp.diff(alpha, q) for q in X4] + [beta] + [sp.diff(beta, q) for q in X4]
        self.F = sp.lambdify(X4, exprs, modules="math", cse=True)

    def fields(self, sg, xx, yy, zz):
        sg, xx, yy, zz = float(sg), float(xx), float(yy), float(zz)   # math semantics
        try:
            return self.F(sg, xx, yy, zz)
        except ZeroDivisionError:          # exact hit on |u| = 1 of a step edge
            return self.F(sg + 1e-13, xx + 1e-13, yy + 1e-13, zz + 1e-13)

    def a_fun(self, sg, xx, yy, zz):
        return self.fields(sg, xx, yy, zz)[0]

    def b_fun(self, sg, xx, yy, zz):
        return self.fields(sg, xx, yy, zz)[5]

    def rhs(self, sg, Y, mass):
        xx, yy, zz, kx, ky, kz = Y[:6]
        a, a_s, a_x, a_y, a_z, b, b_s, b_x, b_y, b_z = self.fields(sg, xx, yy, zz)
        En = math.sqrt(mass * mass + kx * kx + ky * ky + kz * kz)
        dx = a * kx / En
        dy = a * ky / En
        dz = a * kz / En - b
        dkx = kz * b_x - En * a_x
        dky = kz * b_y - En * a_y
        dkz = kz * b_z - En * a_z
        # quadratures: q0 = int v(-d_z ln alpha) dsigma  (kept-gain integrand)
        #              q1 = int [ (a_s - b a_z)/a + k_z (k.grad b)/E_n^2 ] dsigma
        q0 = self.v * (-a_z / a)
        q1 = (a_s - b * a_z) / a + kz * (kx * b_x + ky * b_y + kz * b_z) / En**2
        return [dx, dy, dz, dkx, dky, dkz, q0, q1]

    @staticmethod
    def init_state(sg, pos, kvec):
        return [pos[0], pos[1], pos[2], float(kvec[0]), float(kvec[1]), float(kvec[2]), 0.0, 0.0]

    def diag(self, sg, Y, mass):
        """Eulerian energy, Killing energy E = alpha E_n - (beta + v) k_z, fields."""
        xx, yy, zz, kx, ky, kz = Y[:6]
        f = self.fields(sg, xx, yy, zz)
        a, b = f[0], f[5]
        k = math.sqrt(kx * kx + ky * ky + kz * kz)
        En = math.sqrt(mass * mass + k * k)
        EK = a * En - (b + self.v) * kz
        grad_a = math.sqrt(f[2]**2 + f[3]**2 + f[4]**2)
        grad_b = math.sqrt(f[7]**2 + f[8]**2 + f[9]**2)
        return dict(a=a, b=b, En=En, EK=EK, k=k, grad_a=grad_a, grad_b=grad_b)


def trace(pat, s0, Y0, s1, mass=0.0, events=None, rtol=1e-11, atol=1e-12, dense=False,
          max_step=0.05):
    sol = solve_ivp(pat.rhs, (s0, s1), Y0, method="DOP853", rtol=rtol, atol=atol,
                    events=events, dense_output=dense, max_step=max_step, args=(mass,))
    if sol.status < 0:
        raise RuntimeError(f"integration failed: {sol.message}")
    return sol


def E_drift(pat, sol, mass, E0):
    """largest |E(t) - E0| relative to the size of the terms alpha*E_n that make up E."""
    worst = 0.0
    for i, t in enumerate(sol.t):
        di = pat.diag(t, sol.y[:, i], mass)
        worst = max(worst, abs(di["EK"] - E0) / max(abs(E0), di["a"] * di["En"]))
    return worst


def ev_far(pat, zmin=None, rmax=None, zmax=None):
    """terminal event: ray far from the pattern (in pattern coordinates)."""
    vv = pat.v

    def f(sg, Y, *args):
        zeta = Y[2] - vv * sg
        rr = math.hypot(Y[0], Y[1])
        out = 1.0
        if zmin is not None:
            out = min(out, zeta - zmin)
        if rmax is not None:
            out = min(out, rmax - rr)
        if zmax is not None:
            out = min(out, zmax - zeta)
        return out
    f.terminal = True
    f.direction = -1
    return f



# ===========================================================================
# TEST PATTERNS (sympy expressions in lab coordinates; steady lanes use
# zeta = z - v sigma).  All steps have compact support, so "exterior" means
# alpha = 1 and beta = 0 exactly.
# ===========================================================================
def pattern_carried(vel=2.1, ramp=False):
    """P5: carried region with lab shift beta = -v inside a lapse plateau
    (alpha = 3), flat front and rear falls, flat exterior."""
    zt = z - vel * s
    r2 = x**2 + y**2
    beta = -vel * window(zt, -1.5, 1.5, 1.0) * rwindow(r2, 2.0, 0.8)
    amp = sp.log(3)
    if ramp:                                   # non-steady: plateau height changes
        amp = amp * (1 + sp.Rational(3, 10) * sp.tanh(s - 4))
    alpha = sp.exp(amp * window(zt, -4, 4, 1.5) * rwindow(r2, 4.5, 1.2))
    return Pattern("carried" + ("-ramp" if ramp else ""), alpha, beta, vel)


def pattern_flat_front(vel=2.0):
    """P1: shift-free lapse bump whose front fall is flat for r < 4.9."""
    zt = z - vel * s
    r2 = x**2 + y**2
    alpha = sp.exp(sp.log(4) * window(zt, -6, 3, 2) * rwindow(r2, 6, 1))
    return Pattern("flat-front", alpha, sp.Integer(0), vel)


CONE = dict(theta=15.0, zt=25.0, eps=0.5, wl=1.0, base=0.0, wb=2.0)


def pattern_cone(vel=2.1, Lc=None):
    """P2: shift-free conical front, half-angle 15 deg, lapse peaked on the
    axis, tip rounded over eps, layer of half-width wl, base at zeta = 0.
    Lc defaults to 1.5 + ln(v/2.1) (lapse scaled with speed)."""
    if Lc is None:
        Lc = 1.5 + math.log(vel / 2.1)
    th = math.radians(CONE["theta"])
    zt = z - vel * s
    rho = sp.sqrt(x**2 + y**2 + CONE["eps"]**2)
    d = (CONE["zt"] - zt) * math.sin(th) - rho * math.cos(th)
    alpha = sp.exp(sp.Float(Lc) * cstep(d / CONE["wl"]) * cstep((zt - CONE["base"]) / CONE["wb"]))
    p = Pattern(f"cone(v={vel})", alpha, sp.Integer(0), vel)
    p.Lc = Lc
    return p


def pattern_shelf(vel=2.1, alpha_s=math.e, zT=80.0, wT=1.5, Lb=1.0):
    """P3: static shelf alpha_s for z < zT - wT (resting terminal at zT) with a
    shift-free lapse bump alpha_s*e^{Lb W} moving through it at v."""
    zt = z - vel * s
    shelf = 1 + (alpha_s - 1) * cstep((zT - z) / wT)
    alpha = shelf * sp.exp(Lb * window(zt, -2, 2, 1))
    return Pattern("shelf", alpha, sp.Integer(0), vel)


def pattern_static(alpha_expr, name):
    return Pattern(name, alpha_expr, sp.Integer(0), 0.0)


def pattern_planar_layer(vel, theta_deg, L, w):
    """Planar lapse layer, normal N = (cos th, 0, sin th), high lapse on the
    inner side, moving at v along z."""
    th = math.radians(theta_deg)
    n = math.cos(th) * x + math.sin(th) * (z - vel * s)
    alpha = sp.exp(sp.Float(L) * cstep(-n / w))
    return Pattern(f"planar(v={vel})", alpha, sp.Integer(0), vel)


def exit_angle(Y):
    return math.atan2(math.hypot(Y[3], Y[4]), Y[5])


def event(fun, direction):
    def f(sg, Y, *args):
        return fun(sg, Y)
    f.terminal, f.direction = True, direction
    return f


def is_exterior(pat, sg, Y, mass=0.0):
    d = pat.diag(sg, Y, mass)
    return d["a"] == 1.0 and d["b"] == 0.0 and d["grad_a"] == 0.0 and d["grad_b"] == 0.0


# ===========================================================================
# N1.  I12 part one on the carried pattern (with a shift region)
# ===========================================================================
def num_I12_part1():
    print("\n=== N1  I12 part one: Killing energy and kept gain on geodesics ===")
    out = {}
    pat = pattern_carried()
    vel = pat.v
    runs = [("light fwd, axis", (0.0, 0.0, 8.0), (0, 0, 1.0), 0.0, 14.0),
            ("light fwd, r=4.3", (4.3, 0.0, 8.0), (0, 0, 1.0), 0.0, 40.0),
            ("light bwd, axis", (0.0, 0.0, 8.0), (0, 0, -1.0), 0.0, 40.0),
            ("light bwd, r=4.3", (4.3, 0.0, 8.0), (0, 0, -1.0), 0.0, 40.0),
            ("light oblique", (1.0, 0.5, 7.0), (0.3, 0.1, -1.0), 0.0, 40.0),
            ("matter at rest, axis", (0.0, 0.0, 8.0), (0, 0, 0.0), 1.0, 14.0),
            ("matter at rest, r=4.3", (4.3, 0.0, 8.0), (0, 0, 0.0), 1.0, 40.0)]
    worst = 0.0
    table = []
    for label, pos, kvec, m, s1 in runs:
        Y0 = pat.init_state(0.0, pos, kvec)
        d0 = pat.diag(0.0, Y0, m)
        ev = ev_far(pat, zmin=-9.0, rmax=12.0)
        sol = trace(pat, 0.0, Y0, s1, mass=m, events=[ev])
        Yf = sol.y[:, -1]
        d1 = pat.diag(sol.t[-1], Yf, m)
        errE = E_drift(pat, sol, m, d0["EK"])
        worst = max(worst, errE)
        bmax = max(abs(pat.b_fun(t, *sol.y[:3, i])) for i, t in enumerate(sol.t))
        gain = d1["En"] / d0["En"]
        ext = is_exterior(pat, 0.0, Y0) and is_exterior(pat, sol.t[-1], Yf)
        kept = math.exp(Yf[6]) if m == 0 else float("nan")
        general = (d1["a"] * d1["En"]) / (d0["a"] * d0["En"])
        gen_err = abs(math.log(general) - Yf[7])
        row = dict(run=label, sigma_end=sol.t[-1], gain=gain, E_drift=errE,
                   max_abs_beta_on_path=bmax, both_ends_exterior=ext,
                   kept_gain_formula=kept, general_identity_err=gen_err, E=d0["EK"])
        if m == 0 and ext:
            th = exit_angle(Yf)
            ki = math.acos(kvec[2] / math.sqrt(sum(q * q for q in kvec)))
            row["exit_theta_deg"] = math.degrees(th)
            row["E_law_gain"] = (1 - vel * math.cos(ki)) / (1 - vel * math.cos(th))
        table.append(row)
        print(f"   {label:24s} end={sol.t[-1]:6.2f} gain={gain:11.5g} E-drift={errE:8.1e}"
              f" max|beta|={bmax:6.3g} ext={ext!s:5s} kept-formula={kept:10.5g} gen-err={gen_err:7.1e}")
    out["runs"] = table
    check("N1.1 Killing energy conserved along all 7 geodesics (light and matter; drift"
          " relative to alpha*E_n)", worst < 1e-9, f"max drift {worst:.1e}")
    ok_kept, ok_fail = True, False
    for row in table:
        if row["kept_gain_formula"] == row["kept_gain_formula"] and row["both_ends_exterior"]:
            err = abs(row["kept_gain_formula"] / row["gain"] - 1)
            row["kept_formula_rel_err"] = err
            if row["max_abs_beta_on_path"] == 0.0:
                ok_kept &= err < 1e-8
            elif row["run"] == "light oblique":
                ok_fail = err > 1e-2
    check("N1.2 kept gain exp(v int(-d_zeta ln alpha) dsigma) exact for exterior-to-"
          "exterior light whose path has beta = 0", ok_kept)
    check("N1.3 counterexample: the oblique ray that crosses the shift region violates the"
          " kept-gain formula (the axial head-on ray satisfies it only by the test pattern's"
          " front-back symmetry)", ok_fail,
          f"rel. error {[r.get('kept_formula_rel_err') for r in table if r['run'] == 'light oblique'][0]:.3f}")
    ok_gen = all(r["general_identity_err"] < 1e-8 for r in table)
    check("N1.4 general identity: change of ln(alpha E_n) = int[(d_s - beta d_z) ln alpha"
          " + k_z (k.grad beta)/E_n^2] dsigma on every run", ok_gen)
    ok_exit = all(abs(r["E_law_gain"] / r["gain"] - 1) < 1e-8 for r in table if "E_law_gain" in r)
    check("N1.5 exterior-to-exterior light obeys gain = (1 - v cos th_i)/(1 - v cos th_f)",
          ok_exit)

    # non-steady pattern: the general identity still holds (E does not)
    patr = pattern_carried(ramp=True)
    tab2 = []
    okr = True
    for label, pos, kvec, m in [("light fwd r=4.3", (4.3, 0.0, 8.0), (0, 0, 1.0), 0.0),
                                ("light bwd axis", (0.0, 0.0, 8.0), (0, 0, -1.0), 0.0),
                                ("matter r=1.0", (1.0, 0.0, 8.0), (0.0, 0.0, 0.0), 1.0)]:
        Y0 = patr.init_state(0.0, pos, kvec)
        sol = trace(patr, 0.0, Y0, 30.0, mass=m, events=[ev_far(patr, zmin=-9.0, rmax=12.0)])
        d0, d1 = patr.diag(0.0, Y0, m), patr.diag(sol.t[-1], sol.y[:, -1], m)
        err = abs(math.log(d1["a"] * d1["En"] / (d0["a"] * d0["En"])) - sol.y[7, -1])
        dEK = abs(d1["EK"] / d0["EK"] - 1)
        okr &= err < 1e-8
        tab2.append(dict(run=label, identity_err=err, EK_rel_change=dEK))
        print(f"   ramped pattern, {label:18s}: identity err {err:.1e}, E changes by {dEK:.2e}")
    check("N1.6 non-steady lapse: the general alpha E_n identity holds; E is not conserved",
          okr and all(r["EK_rel_change"] > 1e-4 for r in tab2))
    out["ramped"] = tab2
    return out


# ===========================================================================
# N2.  Exit-angle law on the conical front (below and above the flank threshold)
# ===========================================================================
def run_cone_family(vel, radii, s1=90.0):
    pat = pattern_cone(vel)
    rows = []
    for r0 in radii:
        Y0 = pat.init_state(0.0, (r0, 0.0, CONE["zt"] + 3.0), (0.0, 0.0, 1.0))
        d0 = pat.diag(0.0, Y0, 0.0)
        ev = ev_far(pat, zmin=CONE["base"] - 6.0, rmax=16.0)
        sol = trace(pat, 0.0, Y0, s1, events=[ev], dense=True, rtol=1e-12, atol=1e-13)
        Yf = sol.y[:, -1]
        d1 = pat.diag(sol.t[-1], Yf, 0.0)
        thf = exit_angle(Yf)
        gain = d1["En"] / d0["En"]
        law = (vel - 1) / (vel * math.cos(thf) - 1) if abs(vel * math.cos(thf) - 1) > 0 else float("inf")
        # well-conditioned residual of |k_f|(v cos th_f - 1) = |k_i|(v - 1), relative to the terms
        resid = abs(gain * (vel * math.cos(thf) - 1) - (vel - 1)) / (gain * vel)
        row = dict(r0=r0, sigma_exit=sol.t[-1], exterior=is_exterior(pat, sol.t[-1], Yf),
                   gain=gain, theta_f_deg=math.degrees(thf), law=law,
                   rel_err=abs(law / gain - 1), residual=resid,
                   kept_log_err=abs(Yf[6] - math.log(gain)),
                   cos_minus_1_over_v=math.cos(thf) - 1 / vel,
                   E_drift=E_drift(pat, sol, 0.0, d0["EK"]))
        # state on the flank just before the base fall (zeta = base + 2.5)
        ts = np.linspace(0.0, sol.t[-1], 6001)
        Ys = sol.sol(ts)
        zetas = Ys[2] - vel * ts
        idx = np.where(zetas < CONE["base"] + 2.5)[0]
        if len(idx):
            i = int(idx[0])
            Yi = Ys[:, i]
            rr = math.hypot(Yi[0], Yi[1])
            er = np.array([Yi[0] / rr, Yi[1] / rr, 0.0])
            th = math.radians(CONE["theta"])
            Nn = math.sin(th) * np.array([0.0, 0.0, 1.0]) + math.cos(th) * er
            kh = np.array(Yi[3:6]) / np.linalg.norm(Yi[3:6])
            aa = pat.a_fun(ts[i], *Yi[:3])
            f = pat.fields(ts[i], *Yi[:3])
            row.update(alpha_before_base=aa, dir_deg_before_base=math.degrees(math.acos(kh[2])),
                       vN_pattern_before_base=aa * kh.dot(Nn) - vel * math.sin(th),
                       rate_before_base=-kh.dot(np.array(f[2:5])))
        rows.append(row)
    return pat, rows


def num_I12_exit_and_I15():
    print("\n=== N2  exit-angle law (I12) and flank threshold (I15) on a 15 deg cone ===")
    out = {}
    radii = [0.02, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    allrows = {}
    for vel in (2.1, 3.0, 5.0):
        _, rows = run_cone_family(vel, radii)
        allrows[vel] = rows
        print(f"   v = {vel}:  v sin(theta_c) = {vel * math.sin(math.radians(15)):.3f}")
        for rw in rows:
            print(f"     r0={rw['r0']:5.2f} exit={rw['sigma_exit']:6.2f} ext={rw['exterior']!s:5s}"
                  f" gain={rw['gain']:11.5g} th_f={rw['theta_f_deg']:8.4f} law: rel {rw['rel_err']:.1e},"
                  f" residual {rw['residual']:.1e}; E-drift={rw['E_drift']:.1e} | before base:"
                  f" alpha={rw.get('alpha_before_base', float('nan')):.4f}"
                  f" dir={rw.get('dir_deg_before_base', float('nan')):.2f}"
                  f" vN={rw.get('vN_pattern_before_base', float('nan')):.4f}"
                  f" dlnE/ds={rw.get('rate_before_base', float('nan')):.3f}")
    out["cone_runs"] = {str(k): v for k, v in allrows.items()}
    inter = [rw for rows in allrows.values() for rw in rows if rw["gain"] != 1.0]
    check("N2.1 every overtaken ray reaches the flat exterior during the steady lane",
          all(rw["exterior"] for rows in allrows.values() for rw in rows))
    check(f"N2.2 exit-angle law |k_f|(v cos theta_f - 1) = |k_i|(v - 1) holds on all {len(inter)}"
          " interacting exits (residual relative to the terms; the gain itself is ill-conditioned"
          " as cos theta_f -> 1/v)",
          max(rw["residual"] for rw in inter) < 1e-9,
          f"max residual {max(rw['residual'] for rw in inter):.1e}; max rel. gain error"
          f" {max(rw['rel_err'] for rw in inter):.1e} at gains up to {max(rw['gain'] for rw in inter):.2g};"
          f" max E drift {max(rw['E_drift'] for rw in inter):.1e}")
    check("N2.3 every interacting exit lies inside the cone cos theta_f > 1/v",
          all(rw["cos_minus_1_over_v"] > 0 for rw in inter))
    check("N2.6 the cone is shift-free throughout: ln(gain) = v int(-d_zeta ln alpha) dsigma on"
          " every exit", max(rw["kept_log_err"] for rw in inter) < 1e-8,
          f"max |ln gain - int| = {max(rw['kept_log_err'] for rw in inter):.1e}")
    g21 = max(rw["gain"] for rw in allrows[2.1])
    g3 = max(rw["gain"] for rw in allrows[3.0])
    g5 = max(rw["gain"] for rw in allrows[5.0])
    out["max_gain"] = {"2.1": g21, "3.0": g3, "5.0": g5}
    riders = [rw for rw in allrows[5.0] if rw["gain"] > 1e3]
    ride_alpha = [round(rw["alpha_before_base"], 4) for rw in riders]
    ride_dir = [round(rw["dir_deg_before_base"], 2) for rw in riders]
    ride_vn = [round(rw["vN_pattern_before_base"], 4) for rw in riders]
    print(f"   max gain: v=2.1 {g21:.4g}, v=3 {g3:.4g}, v=5 {g5:.4g};"
          f" v=5 riders (gain > 1e3) before the base: alpha {ride_alpha}, direction {ride_dir},"
          f" pattern-frame normal speed {ride_vn}")
    out["riders"] = dict(alpha=ride_alpha, direction=ride_dir, vN=ride_vn)
    check("N2.4 flank threshold 1/sin15 = 3.86: bounded gains at v = 2.1 and 3,"
          " gains larger by >20x at v = 5 from light riding the flank",
          g5 > 20 * max(g21, g3), f"{g21:.3g}, {g3:.3g}, {g5:.3g}")
    check("N2.5 the v = 5 riders settle on the flank at alpha -> v sin(theta_c) = 1.294, moving"
          " along the flank normal (75 deg to the axis) with pattern-frame normal speed -> 0",
          len(riders) >= 5 and all(abs(a / (5 * math.sin(math.radians(15))) - 1) < 0.02 for a in ride_alpha)
          and all(abs(dg - 75.0) < 0.5 for dg in ride_dir) and all(abs(q) < 0.02 for q in ride_vn))
    return out


# ===========================================================================
# N3.  Shelf law and resting terminal
# ===========================================================================
def num_shelf():
    print("\n=== N3  shelf law (I12): reflection in a shelf and a resting terminal ===")
    out = {}
    vel, als = 2.1, math.e
    pat = pattern_shelf(vel, als)
    gp = (als**2 + vel**2) / (als**2 - vel**2)
    Y0 = pat.init_state(0.0, (0.0, 0.0, 12.0), (0.0, 0.0, 0.0))
    d0 = pat.diag(0.0, Y0, 1.0)
    # leg 1: until the particle is in the pure shelf far ahead of the bump
    sol1 = trace(pat, 0.0, Y0, 60.0, mass=1.0, events=[event(lambda sg, Y: Y[2] - 40.0, 1)], dense=True)
    d1 = pat.diag(sol1.t[-1], sol1.y[:, -1], 1.0)
    drift1 = E_drift(pat, sol1, 1.0, d0["EK"])
    ts = np.linspace(0.0, sol1.t[-1], 20001)
    Ys = sol1.sol(ts)
    vz = np.array([pat.rhs(t, Ys[:, i], 1.0)[2] for i, t in enumerate(ts)])
    i_turn = int(np.argmin(np.abs(vz - vel)))
    a_turn = pat.a_fun(ts[i_turn], *Ys[:3, i_turn])
    # leg 2: to the terminal's support (z = 78.5), across it (to 81.5), and out (84)
    sol2a = trace(pat, sol1.t[-1], sol1.y[:, -1], 200.0, mass=1.0,
                  events=[event(lambda sg, Y: Y[2] - 78.5, 1)])
    sol2b = trace(pat, sol2a.t[-1], sol2a.y[:, -1], 200.0, mass=1.0,
                  events=[event(lambda sg, Y: Y[2] - 81.5, 1)])
    sol2 = trace(pat, sol2b.t[-1], sol2b.y[:, -1], 200.0, mass=1.0,
                 events=[event(lambda sg, Y: Y[2] - 84.0, 1)])
    d2 = pat.diag(sol2.t[-1], sol2.y[:, -1], 1.0)
    # the bump's support is zeta < 3: its front edge while the particle crosses the terminal
    bump_in, bump_out = vel * sol2a.t[-1] + 3.0, vel * sol2b.t[-1] + 3.0
    out.update(gamma_shelf=d1["En"], gamma_prime_law=gp, alpha_turn=a_turn,
               alpha_turn_law=math.sqrt(als**2 + vel**2), gamma_final=d2["En"],
               gamma_final_law=als * gp, E_drift_leg1=drift1,
               bump_front_at_terminal_entry=bump_in, bump_front_at_terminal_exit=bump_out)
    print(f"   gamma' in the shelf {d1['En']:.10f}  law {gp:.10f}  (E drift {drift1:.1e})")
    print(f"   turning lapse {a_turn:.5f}  law sqrt(alpha_s^2+v^2) = {math.sqrt(als**2 + vel**2):.5f}")
    print(f"   after the terminal {d2['En']:.10f}  law alpha_s gamma' = {als * gp:.10f};"
          f" bump front at z = {bump_in:.2f} .. {bump_out:.2f} while the particle crosses"
          f" the terminal (z = 78.5 .. 81.5)")
    check("N3.1 shelf law gamma' = (alpha_s^2+v^2)/(alpha_s^2-v^2)", abs(d1["En"] / gp - 1) < 1e-8)
    check("N3.2 the particle turns where alpha = sqrt(alpha_s^2 + v^2)",
          abs(a_turn / math.sqrt(als**2 + vel**2) - 1) < 2e-3)
    check("N3.3 resting terminal (static while crossed): final gamma = alpha_s gamma'",
          abs(d2["En"] / (als * gp) - 1) < 1e-8 and bump_out < 78.5)
    return out


# ===========================================================================
# N4.  I13: flat front (null disk) and cone light surface
# ===========================================================================
def num_I13():
    print("\n=== N4  I13: blueshift rate on a flat front; causal character of S ===")
    out = {}
    pat = pattern_flat_front(2.0)
    vel = pat.v
    fa = lambda zeta, r: pat.a_fun(0.0, r, 0.0, zeta) - vel
    zS = brentq(lambda q: fa(q, 0.0), 1.2, 4.8)
    Fs = pat.fields(0.0, 0.0, 0.0, zS)
    kappa = abs(Fs[4])
    out.update(zeta_S=zS, kappa=kappa)
    print(f"   S on the axis at zeta = {zS:.6f}; kappa = |d_zeta alpha| = {kappa:.6f} (ln 2 = {math.log(2):.6f})")

    def zeta_S_at(rr):
        return brentq(lambda q: fa(q, rr), 0.0, 5.5) if pat.a_fun(0.0, rr, 0.0, 0.0) > vel else float("nan")
    rows = []
    for label, r0, z0 in [("behind S, axis", 0.0, 2.0), ("behind S, r=2", 2.0, 2.0),
                          ("behind S, r=4", 4.0, 2.0), ("ahead (overtaken), r=2", 2.0, 7.0),
                          ("behind S, r=5.8 (outside the flat disk)", 5.8, 2.0)]:
        Y0 = pat.init_state(0.0, (r0, 0.0, z0), (0.0, 0.0, 1.0))
        d0 = pat.diag(0.0, Y0, 0.0)
        sol = trace(pat, 0.0, Y0, 24.0, events=[ev_far(pat, zmin=-10.0, rmax=12.0)], dense=True)
        t1 = sol.t[-1]
        d1 = pat.diag(t1, sol.y[:, -1], 0.0)
        ta, tb = t1 - 4.0, t1
        Ya, Yb = sol.sol(ta), sol.sol(tb)
        slope = (math.log(pat.diag(tb, Yb, 0.0)["En"]) - math.log(pat.diag(ta, Ya, 0.0)["En"])) / (tb - ta)
        ra, rb = math.hypot(Ya[0], Ya[1]), math.hypot(Yb[0], Yb[1])
        dz_a = abs(Ya[2] - vel * ta - zeta_S_at(ra))
        dz_b = abs(Yb[2] - vel * tb - zeta_S_at(rb))
        conv = math.log(dz_a / dz_b) / (tb - ta) if dz_b == dz_b and dz_a == dz_a and dz_b > 0 else float("nan")
        drift = E_drift(pat, sol, 0.0, d0["EK"])
        rows.append(dict(run=label, sigma_end=t1, held=(t1 >= 24.0 - 1e-9), slope_lnE=slope,
                         convergence_rate=conv, final_r=rb, E_drift=drift, final_gain=d1["En"] / d0["En"]))
        print(f"   {label:40s} end={t1:6.2f} d lnE/ds (last 4) = {slope:.6f}  approach rate = {conv:.5f}"
              f"  final r = {rb:.3f}  gain = {d1['En'] / d0['En']:.4g}  E-drift = {drift:.1e}")
    out["runs"] = rows
    held = [rw for rw in rows if rw["held"]]
    check("N4.1 on the flat disk forward light is held at S and blueshifts at kappa = |d_zeta alpha|",
          len(held) == 4 and all(abs(rw["slope_lnE"] / kappa - 1) < 1e-4 for rw in held),
          ", ".join(f"{rw['slope_lnE']:.6f}" for rw in held))
    check("N4.2 the held light approaches S at the same rate kappa (lab-time normalization of xi)",
          all(abs(rw["convergence_rate"] / kappa - 1) < 1e-3 for rw in held))
    check("N4.3 off the flat disk (S timelike there) the ray is not held: it leaves",
          not rows[-1]["held"])

    # rear fall: alpha rises forward through v, forward light peels away and redshifts at kappa
    zR = brentq(lambda q: fa(q, 0.0), -7.9, -4.1)
    kapR = abs(pat.fields(0.0, 0.0, 0.0, zR)[4])
    rates = []
    for sgn in (1.0, -1.0):
        Y0 = pat.init_state(0.0, (0.0, 0.0, zR + sgn * 1e-7), (0.0, 0.0, 1.0))
        sol = trace(pat, 0.0, Y0, 30.0, dense=True, rtol=1e-13, atol=1e-20, max_step=0.02)
        ts = np.linspace(0.0, 30.0, 3001)
        Ys = sol.sol(ts)
        dist = np.abs(Ys[2] - vel * ts - zR)
        lnE = np.array([math.log(pat.diag(t, Ys[:, i], 0.0)["En"]) for i, t in enumerate(ts)])
        msk = (dist > 1e-6) & (dist < 1e-3)
        rates.append((np.polyfit(ts[msk], np.log(dist[msk]), 1)[0], np.polyfit(ts[msk], lnE[msk], 1)[0]))
    out["rear"] = dict(zeta_S=zR, kappa=kapR, rates=rates)
    print(f"   rear S at zeta = {zR:.6f}, kappa = {kapR:.6f}; forward light starting 1e-7 ahead/behind:"
          f" separation rates {[round(q[0], 5) for q in rates]}, d lnE/ds {[round(q[1], 5) for q in rates]}")
    check("N4.5 rear fall (black-hole type): forward light leaves S on both sides at rate kappa"
          " and redshifts at kappa while near it",
          all(abs(q[0] / kapR - 1) < 2e-3 and abs(q[1] / kapR + 1) < 2e-3 for q in rates))

    cone = pattern_cone(2.1)
    rows2 = []
    for r in (0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0):
        g = lambda q: cone.a_fun(0.0, r, 0.0, q) - 2.1
        qs = np.linspace(CONE["zt"] + 1.5, CONE["base"] + 2.0, 2000)
        vals = [g(q) for q in qs]
        root = None
        for i in range(len(qs) - 1):
            if vals[i] < 0 <= vals[i + 1]:
                root = brentq(g, qs[i + 1], qs[i])
                break
        if root is None:
            continue
        Fv = cone.fields(0.0, r, 0.0, root)
        ratio = abs(Fv[2]) / abs(Fv[4])
        rows2.append(dict(r=r, zeta_S=root, transverse_over_along=ratio))
        print(f"   cone S: r={r:4.2f} zeta={root:8.4f} |d_r alpha|/|d_zeta alpha| = {ratio:.4f}")
    out["cone_S"] = rows2
    check("N4.4 cone: S is null only on the axis; on the flank the gradient ratio -> cot(15 deg) = 3.73",
          rows2[0]["transverse_over_along"] < 1e-12 and all(rw["transverse_over_along"] > 0.1 for rw in rows2[1:])
          and abs(rows2[-1]["transverse_over_along"] / (1 / math.tan(math.radians(15))) - 1) < 0.05)
    return out


# ===========================================================================
# N5.  I14: tip rates on the cone
# ===========================================================================
def num_I14():
    print("\n=== N5  I14: paraxial shedding rate at the cone tip ===")
    out = {}
    vel = 2.1
    pat = pattern_cone(vel)
    zeta_t = brentq(lambda q: pat.a_fun(0.0, 0.0, 0.0, q) - vel, CONE["zt"] - 5.0, CONE["zt"])
    ax2 = sp.lambdify(X4, sp.diff(pat.alpha, x, 2), modules="math")
    F0 = pat.fields(0.0, 0.0, 0.0, zeta_t)
    kappa = -F0[4]
    A = -ax2(0.0, 0.0, 0.0, zeta_t)
    lam = 0.5 * (math.sqrt(kappa**2 + 4 * vel * A) - kappa)
    lam_m = -0.5 * (math.sqrt(kappa**2 + 4 * vel * A) + kappa)
    print(f"   tip at zeta = {zeta_t:.6f}: kappa = {kappa:.6f}, A = -d_r^2 alpha = {A:.6f},"
          f" lambda = {lam:.6f}, lambda_- = {lam_m:.6f}, 2(kappa-lambda) = {2 * (kappa - lam):.6f}")
    out.update(zeta_tip=zeta_t, kappa=kappa, A=A, lam=lam, lam_minus=lam_m, density_rate=2 * (kappa - lam))
    z0 = zeta_t - 0.05
    h_perp, h_par = 1e-7, 1e-6
    launches = {"c": (0.0, 0.0, z0), "x": (h_perp, 0.0, z0), "y": (0.0, h_perp, z0),
                "z": (0.0, 0.0, z0 - h_par)}
    sols = {}
    for k_, pos in launches.items():
        Y0 = pat.init_state(0.0, pos, (0.0, 0.0, 1.0))
        sols[k_] = trace(pat, 0.0, Y0, 9.0, dense=True, rtol=1e-13, atol=1e-20, max_step=0.02)
    ts = np.linspace(0.0, 9.0, 901)
    Yc = sols["c"].sol(ts)
    Yx, Yy, Yz = sols["x"].sol(ts), sols["y"].sol(ts), sols["z"].sol(ts)
    xs = Yx[0]
    lnE = np.array([math.log(pat.diag(t, Yc[:, i], 0.0)["En"]) for i, t in enumerate(ts)])
    vol = np.array([abs(np.linalg.det(np.array([Yx[:3, i] - Yc[:3, i], Yy[:3, i] - Yc[:3, i],
                                                 Yz[:3, i] - Yc[:3, i]]))) for i in range(len(ts))])
    mask = (xs > 1e-5) & (xs < 1e-2) & (ts > 1.0)
    lam_fit = np.polyfit(ts[mask], np.log(xs[mask]), 1)[0]
    kap_fit = np.polyfit(ts[mask], lnE[mask], 1)[0]
    zsep = np.abs(Yz[2] - Yc[2])
    kap_sep = -np.polyfit(ts[mask], np.log(zsep[mask]), 1)[0]
    dens = lnE - np.log(vol)
    dens_fit = np.polyfit(ts[mask], dens[mask], 1)[0]
    print(f"   fit window sigma in [{ts[mask][0]:.2f}, {ts[mask][-1]:.2f}]:")
    print(f"   transverse growth {lam_fit:.5f} (lambda {lam:.5f}); energy growth {kap_fit:.5f} (kappa {kappa:.5f});"
          f" axial convergence {kap_sep:.5f}; density exponent {dens_fit:.5f} (2(kappa-lambda) {2 * (kappa - lam):.5f})")
    out.update(fit_window=[float(ts[mask][0]), float(ts[mask][-1])], lam_fit=lam_fit, kap_fit=kap_fit,
               kap_sep=kap_sep, dens_fit=dens_fit)
    check("N5.1 off-axis displacement grows at lambda = (sqrt(kappa^2 + 4 v A) - kappa)/2",
          abs(lam_fit / lam - 1) < 0.02, f"{lam_fit:.4f} vs {lam:.4f}")
    check("N5.2 energy per quantum grows at kappa, axial separation shrinks at kappa",
          abs(kap_fit / kappa - 1) < 0.02 and abs(kap_sep / kappa - 1) < 0.02,
          f"{kap_fit:.4f}, {kap_sep:.4f} vs {kappa:.4f}")
    check("N5.3 geometric-optics energy density of the ray bundle changes at 2(kappa - lambda)",
          abs(dens_fit / (2 * (kappa - lam)) - 1) < 0.03, f"{dens_fit:.4f} vs {2 * (kappa - lam):.4f}")
    # flat front (no transverse curvature, lambda = 0): the same bundle grows at 2 kappa
    ff = pattern_flat_front(2.0)
    zS = brentq(lambda q: ff.a_fun(0.0, 0.0, 0.0, q) - 2.0, 1.2, 4.8)
    kf = abs(ff.fields(0.0, 0.0, 0.0, zS)[4])
    z0 = zS - 0.05
    sols = {}
    for k_, pos in {"c": (0.0, 0.0, z0), "x": (1e-3, 0.0, z0), "y": (0.0, 1e-3, z0),
                    "z": (0.0, 0.0, z0 - 1e-6)}.items():
        sols[k_] = trace(ff, 0.0, ff.init_state(0.0, pos, (0.0, 0.0, 1.0)), 12.0, dense=True,
                         rtol=1e-13, atol=1e-20, max_step=0.02)
    ts = np.linspace(4.0, 12.0, 801)
    Yc, Yx, Yy, Yz = (sols[q].sol(ts) for q in "cxyz")
    lnE = np.array([math.log(ff.diag(t, Yc[:, i], 0.0)["En"]) for i, t in enumerate(ts)])
    vol = np.array([abs(np.linalg.det(np.array([Yx[:3, i] - Yc[:3, i], Yy[:3, i] - Yc[:3, i],
                                                 Yz[:3, i] - Yc[:3, i]]))) for i in range(len(ts))])
    dens_flat = np.polyfit(ts, lnE - np.log(vol), 1)[0]
    out.update(flat_front_kappa=kf, flat_front_density_rate=dens_flat)
    print(f"   flat front: bundle density exponent {dens_flat:.6f} vs 2 kappa = {2 * kf:.6f}")
    check("N5.4 flat front (lambda = 0): the bundle's energy density grows at 2 kappa",
          abs(dens_flat / (2 * kf) - 1) < 1e-3)
    return out


# ===========================================================================
# N6.  I15: planar oblique layer
# ===========================================================================
def cstep_num(u):
    if u <= -1 + DELTA_CUT:
        return 0.0
    if u >= 1 - DELTA_CUT:
        return 1.0
    return 0.5 * (1 + math.tanh(u / (1 - u * u)))


def num_I15_planar():
    print("\n=== N6  I15: planar layer at 15 deg moving at v along z ===")
    out = {}
    th = math.radians(15.0)
    N = (math.cos(th), 0.0, math.sin(th))
    rows = []
    L, w = math.log(10.0), 1.0
    for vel in (5.0, 2.1):
        pat = pattern_planar_layer(vel, 15.0, L, w)
        u = vel * math.sin(th)
        for n0 in (-0.5, 0.3):
            pos = (n0 * N[0], 0.0, n0 * N[2])
            Y0 = pat.init_state(0.0, pos, N)
            d0 = pat.diag(0.0, Y0, 0.0)
            ev_out = event(lambda sg, Y, vel=vel: (math.cos(th) * Y[0] + math.sin(th) * (Y[2] - vel * sg)) - (w + 2.0), 1)
            sol = trace(pat, 0.0, Y0, 12.0, events=[ev_out], dense=True)
            t1 = sol.t[-1]
            d1 = pat.diag(t1, sol.y[:, -1], 0.0)
            if t1 >= 12.0 - 1e-9:
                Ya = sol.sol(t1 - 3.0)
                slope = (math.log(d1["En"]) - math.log(pat.diag(t1 - 3.0, Ya, 0.0)["En"])) / 3.0
                ncrit = brentq(lambda q: math.exp(L * cstep_num(-q / w)) - u, -0.999, 0.999)
                dn = 1e-6
                kap_n = abs(math.exp(L * cstep_num(-(ncrit + dn) / w)) - math.exp(L * cstep_num(-(ncrit - dn) / w))) / (2 * dn)
                row = dict(v=vel, u=u, n0=n0, held=True, alpha_at_ray=d1["a"], slope=slope, kappa_n=kap_n)
            else:
                gain = d1["En"] / d0["En"]
                law = (d0["a"] - u) / (1 - u)
                row = dict(v=vel, u=u, n0=n0, held=False, gain=gain, law=law)
            rows.append(row)
            print("   ", {k: (round(val, 6) if isinstance(val, float) else val) for k, val in row.items()})
    out["runs"] = rows
    held = [r for r in rows if r["held"]]
    free = [r for r in rows if not r["held"]]
    check("N6.1 v sin(theta_c) = 1.294 > 1: normal light is held at the level alpha = v sin(theta_c)"
          " and blueshifts at |d_n alpha| there",
          len(held) == 2 and all(abs(r["alpha_at_ray"] / r["u"] - 1) < 1e-6 and abs(r["slope"] / r["kappa_n"] - 1) < 1e-3
                                 for r in held))
    check("N6.2 v sin(theta_c) = 0.544 < 1: normal light leaves the layer with the finite gain"
          " (alpha_0 - u)/(1 - u)", len(free) == 2 and all(abs(r["gain"] / r["law"] - 1) < 1e-8 for r in free))
    return out


# ===========================================================================
# N7.  I16: lapse cavity (static, b = 0)
# ===========================================================================
def num_I16():
    print("\n=== N7  I16: static lapse optics (b = 0) ===")
    out = {}
    ain, aout, w = 1.0, 5.0, 1.0
    pat = pattern_static(ain + (aout - ain) * cstep(x / w), "planar-step")
    crit = math.degrees(math.asin(ain / aout))
    rows = []
    for psi in (11.0, 11.4, 11.7, 12.5, 30.0):
        k = (math.cos(math.radians(psi)), math.sin(math.radians(psi)), 0.0)
        Y0 = pat.init_state(0.0, (-3.0, 0.0, 0.0), k)
        sol = trace(pat, 0.0, Y0, 400.0, events=[event(lambda sg, Y: Y[0] - 3.0, 1),
                                                  event(lambda sg, Y: Y[0] + 3.5, -1)])
        Yf = sol.y[:, -1]
        transmitted = Yf[0] > 0
        row = dict(psi_in=psi, transmitted=bool(transmitted), predicted=psi < crit)
        if transmitted:
            row["psi_out"] = math.degrees(math.atan2(abs(Yf[4]), Yf[3]))
            row["snell"] = math.degrees(math.asin(aout / ain * math.sin(math.radians(psi))))
        rows.append(row)
        print("   ", row)
    for psi in (30.0, 60.0, 85.0):
        k = (-math.cos(math.radians(psi)), math.sin(math.radians(psi)), 0.0)
        Y0 = pat.init_state(0.0, (3.0, 0.0, 0.0), k)
        sol = trace(pat, 0.0, Y0, 400.0, events=[event(lambda sg, Y: Y[0] + 3.0, -1),
                                                  event(lambda sg, Y: Y[0] - 3.5, 1)])
        Yf = sol.y[:, -1]
        row = dict(psi_in=psi, reverse=True, transmitted=bool(Yf[0] < 0),
                   psi_out=math.degrees(math.atan2(abs(Yf[4]), -Yf[3])),
                   snell=math.degrees(math.asin(ain / aout * math.sin(math.radians(psi)))))
        rows.append(row)
        print("   ", row)
    out["planar"] = rows
    fwd = [r for r in rows if "reverse" not in r]
    rev = [r for r in rows if "reverse" in r]
    check("N7.1 climbing alpha 1 -> 5: transmitted iff psi < arcsin(1/5) = 11.54 deg",
          all(r["transmitted"] == r["predicted"] for r in fwd))
    check("N7.2 Snell's law with index 1/alpha on transmission",
          all(abs(r["psi_out"] - r["snell"]) < 1e-6 for r in rows if r["transmitted"]))
    check("N7.3 descending alpha 5 -> 1: always transmitted (no total reflection)",
          all(r["transmitted"] for r in rev))

    # curved (spherical) walls: exact criterion L/E <= min r/alpha(r) along the outward path
    def sphere_case(R, wr, r0, launches):
        r_ = sp.sqrt(x**2 + y**2 + z**2)
        pat_s = pattern_static(ain + (aout - ain) * cstep((r_ - R) / wr), f"sphere(R={R},w={wr})")
        alpha_r = lambda rr: ain + (aout - ain) * cstep_num((rr - R) / wr)
        grid = np.linspace(r0, R + wr + 1.0, 200001)
        Mmin = float(min(g / alpha_r(g) for g in grid))
        res = []
        for psi_deg in launches:
            psi0 = math.radians(psi_deg)
            Lval = r0 * math.sin(psi0) / ain          # L/E for a ray at r0 in the alpha_in region
            k = (math.cos(psi0), math.sin(psi0), 0.0)
            Y0 = pat_s.init_state(0.0, (r0, 0.0, 0.0), k)
            sol = trace(pat_s, 0.0, Y0, 300.0,
                        events=[event(lambda sg, Y: math.sqrt(Y[0]**2 + Y[1]**2 + Y[2]**2) - (R + wr + 3.0), 1)])
            res.append(dict(psi0_deg=psi_deg, L=Lval, escaped=bool(sol.status == 1),
                            exact_predicts=bool(Lval <= Mmin), thin_wall_predicts=bool(Lval <= R / aout)))
        return Mmin, res
    # (a) wall of half-width 1 at R = 3: threshold moves from R/alpha_out = 0.6 to min r/alpha
    M1, _ = sphere_case(3.0, 1.0, 1.5, [])
    ps = [math.degrees(math.asin(f * M1 / 1.5)) for f in (0.97, 1.03)]
    M1, res1 = sphere_case(3.0, 1.0, 1.5, ps)
    # (b) wall of half-width 2: r/alpha never falls below its starting value, nothing is trapped
    M2, res2 = sphere_case(3.0, 2.0, 0.9, [30.0, 60.0, 80.0, 89.0])
    print(f"   sphere R=3, half-width 1: exact threshold L* = min r/alpha = {M1:.5f}; thin-wall R/alpha_out = 0.6")
    for q in res1:
        print("    ", q)
    print(f"   sphere R=3, half-width 2, launch r0 = 0.9: min r/alpha = {M2:.5f} (= r0/alpha_in); all launches:")
    for q in res2:
        print("    ", q)
    out["sphere"] = dict(case_a=dict(L_star=M1, runs=res1), case_b=dict(min_r_over_alpha=M2, runs=res2))
    check("N7.4 curved wall: a ray escapes iff L/E <= min r/alpha(r) (exact, 6 rays); the thin-wall"
          " arcsin rule misplaces the threshold (0.6 vs " + f"{M1:.3f}" + ") and predicts trapping"
          " where the half-width-2 wall traps nothing",
          all(q["escaped"] == q["exact_predicts"] for q in res1 + res2)
          and res1[0]["escaped"] and not res1[1]["escaped"]
          and any(q["escaped"] and not q["thin_wall_predicts"] for q in res1 + res2))
    return out


# ===========================================================================
# N8.  I20: ordering of rays of one family
# ===========================================================================
def num_I20():
    print("\n=== N8  I20: ordering of rays of one family ===")
    out = {}
    pat = pattern_carried()
    ok = True
    ts = np.linspace(0.0, 14.0, 1401)
    for sign in (1.0, -1.0):
        Ya = pat.init_state(0.0, (0.0, 0.0, 8.0), (0.0, 0.0, sign))
        Yb = pat.init_state(0.0, (0.0, 0.0, 8.3), (0.0, 0.0, sign))
        sa = trace(pat, 0.0, Ya, 14.0, dense=True)
        sb = trace(pat, 0.0, Yb, 14.0, dense=True)
        za, zb = sa.sol(ts)[2], sb.sol(ts)[2]
        sep = zb - za
        ok &= bool(np.all(sep > 0))
        out[f"family{int(sign)}"] = dict(min_sep=float(sep.min()), final_sep=float(sep[-1]))
        print(f"   axis rays, family {int(sign):+d}: min separation {sep.min():.3e}, final {sep[-1]:.3e}")
    check("N8.1 on the symmetry axis (a 2D reduction) rays of one family never cross", ok)
    # static lapse dip (index up to 2) with a transverse gradient across its whole aperture
    lens = pattern_static(1 - sp.Rational(1, 2) * rwindow(x**2 + y**2, 1.0, 0.5) * window(z, -1, 1, 0.8), "lens")
    xs0 = [0.3, 0.6, 0.9, 1.2]
    finals = []
    for x0 in xs0:
        Y0 = lens.init_state(0.0, (x0, 0.0, -4.0), (0.0, 0.0, 1.0))
        sol = trace(lens, 0.0, Y0, 40.0)
        finals.append(float(sol.y[0, -1]))
    crossed = any(finals[i] > finals[i + 1] for i in range(len(finals) - 1)) or any(f < 0 for f in finals)
    out["lens_final_x"] = finals
    print(f"   lens: initial x {xs0} -> x at sigma = 40: {[round(f, 4) for f in finals]}")
    check("N8.2 off the axis (3D) rays of one family cross (focusing), so ordering is a 2D statement",
          crossed)
    return out


def main():
    t0 = time.time()
    RESULTS["S1"] = sym_I12_part1()
    RESULTS["S2"] = sym_I12_part2()
    RESULTS["S3"] = sym_I13()
    RESULTS["S4"] = sym_I14()
    RESULTS["S5"] = sym_I15()
    RESULTS["S6"] = sym_I16()
    RESULTS["S7"] = sym_I17()
    RESULTS["S8"] = sym_I19_I20()
    t1 = time.time()
    print(f"\n(symbolic part {t1 - t0:.1f} s)")
    if "--symbolic-only" not in sys.argv:
        RESULTS["N1"] = num_I12_part1()
        RESULTS["N2"] = num_I12_exit_and_I15()
        RESULTS["N3"] = num_shelf()
        RESULTS["N4"] = num_I13()
        RESULTS["N5"] = num_I14()
        RESULTS["N6"] = num_I15_planar()
        RESULTS["N7"] = num_I16()
        RESULTS["N8"] = num_I20()
        print(f"\n(numerical part {time.time() - t1:.1f} s)")
    npass = sum(c[1] for c in CHECKS)
    print(f"\nSUMMARY: {npass} of {len(CHECKS)} checks passed")
    for lab, okc, det in CHECKS:
        if not okc:
            print("  FAILED:", lab, det)
    RESULTS["checks"] = [dict(label=l, passed=p, detail=d) for l, p, d in CHECKS]
    with open(os.path.join(HERE, "v3_moving_patterns_results.json"), "w") as fh:
        json.dump(RESULTS, fh, indent=1, default=float)
    return 0 if npass == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
