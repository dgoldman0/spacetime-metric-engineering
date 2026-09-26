"""Checks for the review of thought experiments, checks and examples in
Chapters 1-3 (2026-09-26, after the two-column draft was committed).

The review replaced weak thought experiments, rewrote or added
check-your-understanding questions, and added a worked example (the Sun as a
lens), the Baez-Bunn statement of Einstein's equation and a problem (the orbit
paradox). Each check recomputes a number or verifies a claim the new text
makes. Run with `make checks`; the output is kept in
checks/rev2_teaching_devices.log. The earlier checks remain in
checks/rev1_quoted_numbers.py and checks/ch02_ch03_examples.py.
"""
import math

import numpy as np
import sympy as sp
from scipy.integrate import quad
from scipy.optimize import brentq

c = 2.99792458e8          # m/s
G = 6.674e-11             # N m^2 kg^-2
GM_earth = 3.986004e14    # m^3 s^-2
R_earth = 6.371e6         # m
GM_sun = 1.32712e20       # m^3 s^-2
R_sun = 6.957e8           # m
AU = 1.495979e11          # m
hbar = 1.054571817e-34    # J s
g = 9.81                  # m s^-2
year = 3.156e7            # s
arcsec = math.pi / (180 * 3600)

failures = []


def check(label, value, quoted, rel=0.05):
    ok = abs(value - quoted) <= rel * abs(quoted)
    print(f"{'ok ' if ok else 'BAD'} {label}: computed {value:.6g}, text {quoted:.6g}")
    if not ok:
        failures.append(label)


def claim(label, ok):
    print(f"{'ok ' if ok else 'BAD'} {label}")
    if not ok:
        failures.append(label)


def section(title):
    print()
    print("== " + title)


# ---------------------------------------------------------------- Chapter 1
section("Chapter 1: how stiff is the sheet? (unchanged numbers, new wording)")
M_needed = 1e-9 * c**2 / G * 1.0
check("mass to slow a clock 1e-9 at 1 m (kg)", M_needed, 1.3e18, 0.05)
rho_rock = 2500.0
D = 2 * (3 * M_needed / (4 * math.pi * rho_rock)) ** (1 / 3)
check("diameter of a rocky asteroid of that mass (km)", D / 1e3, 100, 0.05)
claim("far more than a loaded truck (4e4 kg) or a large mountain (~1e15 kg)",
      M_needed > 1e3 * 1e15)

section("Chapter 1: Example, the Sun as a lens")
alpha = 4 * GM_sun / (c**2 * R_sun)
check("deflection at the limb (rad)", alpha, 8.5e-6, 0.01)
check("deflection at the limb (arcsec)", alpha / arcsec, 1.75, 0.01)
check("GM_sun/c^2 quoted in the example (km)", GM_sun / c**2 / 1e3, 1.48, 0.01)
F = R_sun / alpha
check("distance where grazing rays cross the axis (m)", F, 8.2e13, 0.01)
check("same, in AU", F / AU, 550, 0.01)
check("ratio to Pluto's mean distance, 39.5 AU", F / AU / 39.5, 14, 0.03)
check("deflection is four times the clock-slowing fraction at the limb",
      alpha / (GM_sun / (c**2 * R_sun)), 4, 1e-9)
b = sp.symbols('b', positive=True)
F_b = b / (4 * sp.Symbol('M', positive=True) / b)
claim("rays at larger impact parameter cross the axis farther away",
      sp.diff(F_b, b).is_positive)

section("Chapter 1: Check, the Casimir force")
d = sp.symbols('d', positive=True)
hb, cc = sp.symbols('hbar c', positive=True)
E_area = -sp.pi**2 * hb * cc / (720 * d**3)           # u times d
force_area = -sp.diff(E_area, d)                       # force per area along +d
claim("energy per area falls (more negative) as d shrinks",
      sp.simplify(sp.diff(E_area, d)) == sp.pi**2 * hb * cc / (240 * d**4))
claim("force per area is -pi^2 hbar c/(240 d^4): attractive",
      sp.simplify(force_area + sp.pi**2 * hb * cc / (240 * d**4)) == 0)
P1 = math.pi**2 * hbar * c / (240 * (1e-6) ** 4)
check("Casimir pressure at 1 um (mPa)", P1 * 1e3, 1.3, 0.02)

section("Chapter 1: Check, aging in a warp bubble versus a fast ship")
check("time-dilation factor at 0.99c (sevenfold)", 1 / math.sqrt(1 - 0.99**2), 7, 0.02)

# ---------------------------------------------------------------- Chapter 2
section("Chapter 2: Check, the zigzag worldline")
T = 10.0
for v in (0.9, 0.99, 0.9999):
    print(f"    zigzag at v = {v}: clock records {T * math.sqrt(1 - v**2):.4g} of {T} years")
claim("zigzag proper time goes to zero as v -> 1",
      T * math.sqrt(1 - 0.999999**2) < 0.02)

section("Chapter 2: Check, a clock riding a grid point (flowing coordinates)")
v0 = 0.6
check("proper time over 10 years of t at v0 = 0.6 (years)", 10 * math.sqrt(1 - v0**2), 8, 1e-12)
check("equals special-relativistic time dilation at 0.6", 10 / (1 / math.sqrt(1 - v0**2)), 8, 1e-12)

section("Chapter 2: Thought experiment, light climbing a tower (Pound-Rebka)")
h_PR = 74 * 0.3048
check("74 ft in metres", h_PR, 22.6, 0.005)
check("one-way shift gh/c^2 over the tower", g * h_PR / c**2, 2.5e-15, 0.03)
check("two-way shift predicted in the paper, 4.92e-15", 2 * g * h_PR / c**2, 4.92e-15, 0.005)
# Crests leave and arrive one coordinate interval Dt apart (static metric).
# The bottom clock measures the period (1 + Phi_b) Dt, the top clock
# (1 + Phi_t) Dt, so f_top/f_bottom = (1 + Phi_b)/(1 + Phi_t).
eps, a_b, a_t = sp.symbols('epsilon a_b a_t', real=True)
ratio = (1 + eps * a_b) / (1 + eps * a_t)
first_order = sp.series(ratio, eps, 0, 2).removeO()
claim("f_top/f_bottom = 1 - (Phi_t - Phi_b) to first order in the potentials",
      sp.simplify(first_order - (1 - eps * (a_t - a_b))) == 0)

section("Chapter 2: Check, twins on Everest (moved from a thought experiment)")
frac = 9.8 * 8850 / (3.0e8) ** 2
check("gh/c^2 at the summit", frac, 9.6e-13, 0.01)
check("80 years in seconds", 80 * year, 2.5e9, 0.02)
check("age difference (ms)", frac * 80 * year * 1e3, 2.4, 0.03)

section("Chapter 2: Check, the volume of a falling ball in empty space")
x, y, z, GMs = sp.symbols('x y z GM', positive=True)
r = sp.sqrt(x**2 + y**2 + z**2)
Phi = -GMs / r
tidal = sp.Matrix(3, 3, lambda i, j: -sp.diff(Phi, [x, y, z][i], [x, y, z][j]))
at_axis = tidal.subs({x: 0, y: 0}).applyfunc(sp.simplify)
claim("on the z axis: stretch 2GM/r^3 along z, squeeze GM/r^3 across",
      at_axis == sp.diag(-GMs / z**3, -GMs / z**3, 2 * GMs / z**3))
claim("sum of the three rates (trace) is zero in empty space",
      sp.simplify(tidal.trace()) == 0)
check("stretching rate 2GM/r^3 at the Earth's surface (s^-2)",
      2 * GM_earth / R_earth**3, 3.08e-6, 0.01)

section("Chapter 2: Problem, the orbit paradox")
r_iss = 6.79e6
frac_orbit = GM_earth / (r_iss * c**2) + GM_earth / (2 * r_iss * c**2)
frac_hover = GM_earth / (r_iss * c**2)
check("hovering minus orbiting rate, GM/(2rc^2)", frac_orbit - frac_hover, 3.27e-10, 0.01)
P = 2 * math.pi * math.sqrt(r_iss**3 / GM_earth)
check("orbital period at 6790 km (min)", P / 60, 93, 0.01)
check("difference over one orbit (us)", (frac_orbit - frac_hover) * P * 1e6, 1.8, 0.03)


# A third free-fall worldline between the same two events: straight up and
# back down, taking one orbital period. Radial Kepler motion with semi-major
# axis a: r = a(1 - cos eta), t = sqrt(a^3/GM)(eta - sin eta). The trip from
# r0 to apoapsis 2a and back lasts 2 sqrt(a^3/GM)(pi - eta0 + sin eta0).
def up_down_time(a):
    eta0 = math.acos(1 - r_iss / a)
    return 2 * math.sqrt(a**3 / GM_earth) * (math.pi - eta0 + math.sin(eta0))


a_up = brentq(lambda a: up_down_time(a) - P, r_iss / 2 * 1.0000001, 50 * r_iss)


def gain_integrand(eta):
    # weak-field clock rate minus the hovering clock's rate, times dt/deta
    rr = a_up * (1 - math.cos(eta))
    E = -GM_earth / (2 * a_up)                       # specific orbital energy
    v2 = 2 * (E + GM_earth / rr)
    rate = (-GM_earth / rr - v2 / 2) / c**2 - (-GM_earth / r_iss) / c**2
    return rate * math.sqrt(a_up**3 / GM_earth) * (1 - math.cos(eta))


eta0 = math.acos(1 - r_iss / a_up)
gain_up, _ = quad(gain_integrand, eta0, 2 * math.pi - eta0, limit=200)
print(f"    up-and-down path: apoapsis {2 * a_up / 1e3:.0f} km from the centre, "
      f"gain over hovering {gain_up * 1e6:.3f} us")
claim("straight up and down records more than hovering", gain_up > 0)
claim("hovering records more than orbiting", frac_orbit > frac_hover)

# ---------------------------------------------------------------- Chapter 3
section("Chapter 3: Check, a laser beam seen by a moving observer")
u, v = sp.symbols('u v', real=True)
eta = sp.diag(-1, 1, 1, 1)
T_up = sp.zeros(4)
T_up[0, 0] = T_up[0, 1] = T_up[1, 0] = T_up[1, 1] = u
T_dn = eta * T_up * eta
gam = 1 / sp.sqrt(1 - v**2)
w = sp.Matrix([gam, gam * v, 0, 0])
rho_w = sp.simplify((w.T * T_dn * w)[0])
claim("T_tx = -u after lowering", T_dn[0, 1] == -u)
claim("rho_w = u (1 - v)/(1 + v)", sp.simplify(rho_w - u * (1 - v) / (1 + v)) == 0)
check("chasing at 0.8: fraction of u", float(rho_w.subs({u: 1, v: sp.Rational(4, 5)})), 1 / 9, 1e-12)
check("running into it at 0.8: multiple of u", float(rho_w.subs({u: 1, v: -sp.Rational(4, 5)})), 9, 1e-12)
Dop = sp.sqrt((1 - v) / (1 + v))
claim("factor is the Doppler factor squared", sp.simplify(rho_w / u - Dop**2) == 0)
N_up = sp.Matrix([1, 1, 0, 0])                         # photon current per unit lab density
n_w = sp.simplify(-(N_up.T * eta * w)[0])
# gamma (1 - v) equals sqrt((1 - v)/(1 + v)) only for |v| < 1, which sympy
# cannot assume for a real symbol (first run, rev2_teaching_devices_run1.log).
# With the rapidity, v = tanh(phi), both sides are exp(-phi).
phi = sp.symbols('phi', real=True)
n_phi = sp.simplify((n_w.subs(v, sp.tanh(phi))).rewrite(sp.exp))
claim("photon number density seen by the observer scales by the Doppler factor, exp(-phi)",
      sp.simplify(n_phi - sp.exp(-phi)) == 0
      and all(abs(float(n_w.subs(v, vv)) - math.sqrt((1 - vv) / (1 + vv))) < 1e-12
              for vv in (-0.9, -0.3, 0.0, 0.5, 0.99)))

section("Chapter 3: Einstein's equation as a falling ball (Baez-Bunn)")
rho, px, py, pz = sp.symbols('rho p_x p_y p_z', real=True)
T_rest = sp.diag(rho, px, py, pz)                      # T_{mu nu} in the rest frame
trace_T = sum(eta[i, i] * T_rest[i, i] for i in range(4))
ricci_tt = 8 * sp.pi * (T_rest[0, 0] - sp.Rational(1, 2) * trace_T * eta[0, 0])
claim("R_tt = 4 pi (rho + p_x + p_y + p_z), so Vddot/V = -4 pi (rho + sum p)",
      sp.simplify(ricci_tt - 4 * sp.pi * (rho + px + py + pz)) == 0)
p = sp.symbols('p', real=True)
claim("perfect fluid: source rho + 3p", sp.simplify(ricci_tt.subs({px: p, py: p, pz: p}) / (4 * sp.pi) - (rho + 3 * p)) == 0)
claim("ball keeps its volume when p = -rho/3", sp.solve(sp.Eq(rho + 3 * p, 0), p) == [-rho / 3])
claim("vacuum energy p = -rho gives rho + 3p = -2 rho", sp.simplify((rho + 3 * p).subs(p, -rho) + 2 * rho) == 0)
# Newtonian check: inside uniform matter, Phi = (2 pi/3) rho r^2 (G = 1) solves
# Poisson's equation, and a small ball of particles at rest changes volume at
# the trace of the relative accelerations, -laplacian(Phi) = -4 pi rho.
rho0 = sp.symbols('rho_0', positive=True)
Phi_in = sp.Rational(2, 3) * sp.pi * rho0 * (x**2 + y**2 + z**2)
lap = sum(sp.diff(Phi_in, q, 2) for q in (x, y, z))
claim("uniform matter: laplacian(Phi) = 4 pi rho (Poisson)", sp.simplify(lap - 4 * sp.pi * rho0) == 0)
tidal_in = sp.Matrix(3, 3, lambda i, j: -sp.diff(Phi_in, [x, y, z][i], [x, y, z][j]))
claim("Newtonian ball in dust: Vddot/V = -4 pi rho, matching the ball equation with p = 0",
      sp.simplify(tidal_in.trace() + 4 * sp.pi * rho0) == 0
      and sp.simplify(-ricci_tt.subs({px: 0, py: 0, pz: 0, rho: rho0}) + 4 * sp.pi * rho0) == 0)

section("Chapter 3: empty space, trace and counting")
n = 4
claim("g^{mu nu} G_{mu nu} = R - (n/2) R = -R in four dimensions", (1 - sp.Rational(n, 2)) == -1)
claim("Riemann has 20 independent components in 4D", n**2 * (n**2 - 1) // 12 == 20)
claim("Ricci has 10 independent components in 4D", n * (n + 1) // 2 == 10)

section("Chapter 3: Check, water in geometric units")
rho_geo = G * 1000 / c**2
check("energy density of water (m^-2)", rho_geo, 7.4e-25, 0.01)
L = 1 / math.sqrt(8 * math.pi * rho_geo)
check("curvature length 1/sqrt(8 pi rho) (m)", L, 2e11, 0.2)
claim("longer than the Earth-Sun distance", L > AU)

section("Chapter 3: Check, a layer of shear")
beta0, wdt, yy = sp.symbols('beta_0 w y', positive=True)
rho_layer = -(beta0 / wdt) ** 2 / (32 * sp.pi)
claim("linear ramp: rho = -beta0^2/(32 pi w^2)", sp.simplify(rho_layer + beta0**2 / (32 * sp.pi * wdt**2)) == 0)
total = sp.integrate(rho_layer, (yy, 0, wdt))
claim("total per unit area = -beta0^2/(32 pi w)", sp.simplify(total + beta0**2 / (32 * sp.pi * wdt)) == 0)
claim("doubling w divides rho by 4", sp.simplify(rho_layer.subs(wdt, 2 * wdt) / rho_layer) == sp.Rational(1, 4))
claim("doubling w halves the total", sp.simplify(total.subs(wdt, 2 * wdt) / total) == sp.Rational(1, 2))

# The shear formula itself, from the metric, for the riding observers.
t_s, x_s, y_s, z_s = sp.symbols('t x y z')
beta = sp.Function('beta')(y_s)
coords = [t_s, x_s, y_s, z_s]
gmet = sp.Matrix([[-1 + beta**2, beta, 0, 0], [beta, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
ginv = sp.simplify(gmet.inv())
Gam = [[[sp.simplify(sum(ginv[m, k] * (sp.diff(gmet[k, a], coords[b_]) + sp.diff(gmet[k, b_], coords[a])
                                         - sp.diff(gmet[a, b_], coords[k])) for k in range(4)) / 2)
         for b_ in range(4)] for a in range(4)] for m in range(4)]


def riemann(m, a, nn, b_):
    expr = sp.diff(Gam[m][a][b_], coords[nn]) - sp.diff(Gam[m][a][nn], coords[b_])
    expr += sum(Gam[m][nn][l_] * Gam[l_][a][b_] - Gam[m][b_][l_] * Gam[l_][a][nn] for l_ in range(4))
    return expr


Ric = sp.Matrix(4, 4, lambda a, b_: sp.simplify(sum(riemann(m, a, m, b_) for m in range(4))))
Rs = sp.simplify(sum(ginv[a, b_] * Ric[a, b_] for a in range(4) for b_ in range(4)))
Gt = (Ric - Rs * gmet / 2).applyfunc(sp.simplify)
w_ride = sp.Matrix([1, -beta, 0, 0])
claim("riding four-velocity is unit timelike", sp.simplify((w_ride.T * gmet * w_ride)[0] + 1) == 0)
rho_ride = sp.simplify((w_ride.T * Gt * w_ride)[0] / (8 * sp.pi))
claim("riding observers measure -(beta')^2/(32 pi)",
      sp.simplify(rho_ride + sp.diff(beta, y_s) ** 2 / (32 * sp.pi)) == 0)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED: " + "; ".join(failures))
    raise SystemExit(1)
print("all checks passed")
