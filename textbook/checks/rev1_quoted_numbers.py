"""Checks of the numbers quoted in the rewritten Chapters 1-3 (two-column draft,
2026-09-26) and of the geometry drawn in their figures.

Each check recomputes a quoted number from its inputs and prints it beside the
value the text uses. Run with `make checks` (needs sympy and mpmath); the output
is kept in checks/rev1_quoted_numbers.log. The earlier checks of the worked
examples remain in checks/ch02_ch03_examples.py.
"""
import math
import sympy as sp

c = 2.99792458e8          # m/s
G = 6.674e-11             # N m^2 kg^-2
GM_earth = 3.986004e14    # m^3 s^-2
R_earth = 6.371e6         # m
M_earth = 5.97e24         # kg
day = 86400.0             # s
year = 3.156e7            # s
hbar = 1.054571817e-34    # J s
M_sun = 1.989e30          # kg

failures = []


def check(label, value, quoted, rel=0.05):
    ok = abs(value - quoted) <= rel * abs(quoted)
    print(f"{'ok ' if ok else 'BAD'} {label}: computed {value:.6g}, text {quoted:.6g}")
    if not ok:
        failures.append(label)


def section(title):
    print()
    print("== " + title)


# ---------------------------------------------------------------- Chapter 1
section("Chapter 1: clocks that disagree (Figure 1.1)")
K = GM_earth / (c**2 * R_earth) * day * 1e6        # microseconds per day
check("height-gain asymptote far away (us/day)", K, 60.15, 0.01)


def rates(r):
    height = GM_earth / c**2 * (1 / R_earth - 1 / r) * day * 1e6
    speed = -GM_earth / (2 * c**2 * r) * day * 1e6
    return height, speed, height + speed


h, s, n = rates(26.56e6)
check("GPS gain from height (us/day)", h, 45.7, 0.01)
check("GPS loss from speed (us/day)", -s, 7.2, 0.01)
check("GPS net gain (us/day)", n, 38.5, 0.01)
check("GPS orbital speed (km/s)", math.sqrt(GM_earth / 26.56e6) / 1e3, 3.87, 0.01)
check("ranging error per day (km)", n * 1e-6 * c / 1e3, 11.5, 0.02)
check("net fractional rate (parts in 1e10)", n * 1e-6 / day * 1e10, 4.465, 0.01)
_, _, n_iss = rates(R_earth + 420e3)
check("space station net (us/day)", n_iss, -24.5, 0.02)
check("space station orbital speed (km/s)", math.sqrt(GM_earth / (R_earth + 420e3)) / 1e3, 7.66, 0.01)
check("orbit radius where the effects cancel (Earth radii)", 1.5, 1.5)
print("   (net = K (1 - 3R/(2r)) vanishes at r = 3R/2 exactly)")

section("Chapter 1: spacetime is stiff")
check("c^4/G (N)", c**4 / G, 1.2e44, 0.02)
check("c^2/G (kg/m)", c**2 / G, 1.35e27, 0.01)
check("Earth GM/(c^2 R)", G * M_earth / (c**2 * R_earth), 7.0e-10, 0.01)
check("Earth M/R (kg/m)", M_earth / R_earth, 9.4e17, 0.01)
check("Earth clock loss per day (us)", G * M_earth / (c**2 * R_earth) * day * 1e6, 60, 0.02)
M_needed = 1e-9 * 1.0 * c**2 / G
check("mass to slow a clock 1e-9 at 1 m (kg)", M_needed, 1.3e18, 0.05)
rock_radius = (3 * M_needed / (4 * math.pi * 3000.0)) ** (1 / 3)
check("diameter of such a rock at 3000 kg/m^3 (km)", 2 * rock_radius / 1e3, 100, 0.1)
check("Sun GM/(c^2 R)", G * 2.0e30 / (c**2 * 7.0e8), 2e-6, 0.1)
ns = G * 1.4 * M_sun / (c**2 * 12e3)
check("neutron star GM/(c^2 R)", ns, 0.17, 0.03)
check("neutron star exact clock rate", math.sqrt(1 - 2 * ns), 0.81, 0.01)
check("stress to bend 1 m (Pa)", c**4 / G, 1e44, 0.3)
print("   strongest materials ~1e11 Pa, so the gap is ~33 orders of magnitude:",
      round(math.log10(c**4 / G / 1.3e11), 1))

section("Chapter 1: negative energy in the laboratory")
u1 = -math.pi**2 * hbar * c / (720 * (1e-6) ** 4)
check("Casimir energy density at 1 um (J/m^3)", u1, -4.3e-4, 0.02)
check("growth from 1 um to 10 nm", (1e-6 / 1e-8) ** 4, 1e8)
rest_al = 2700 * c**2
check("aluminium rest-energy density (J/m^3)", rest_al, 2.4e20, 0.02)
print("   ratio plate / gap at 1 um:", f"{rest_al / abs(u1):.2e}", "(text: more than twenty orders)")
check("throat demand c^4/(8 pi G b^2), b = 1 m (J/m^3)", c**4 / (8 * math.pi * G), 4.8e42, 0.02)
u100 = -math.pi**2 * hbar * c / (720 * (1e-7) ** 4)
check("Problem 1.6: Casimir density at 100 nm (J/m^3)", u100, -4.33, 0.01)
check("Problem 1.5: Pfenning-Ford estimate in solar masses", 6e62 / 2.0e30, 3e32, 0.01)
check("Problem 1.3: six months on the station (ms)", 24.5 * 182.5 / 1e3, 4.5, 0.02)
check("Problem 1.4: time to drift 30 ns (minutes)", 30e-9 / (38.5e-6 / day) / 60, 1.12, 0.02)

section("Chapter 1: Figure 1.5 geometry")
# warp: inside the bubble dx/dt = v +- 1 with v = 3
print("   warp cone edges (deg):", round(math.degrees(math.atan2(1, 4)), 2),
      round(math.degrees(math.atan2(1, 2)), 2), "and",
      round(180 - math.degrees(math.atan2(1, 2)), 2), round(180 - math.degrees(math.atan2(1, 4)), 2))
# Krasnikov: inside, light along (1, 1) and (-1, k) with k = -1 + 0.15
k = -1 + 0.15
edge = math.degrees(math.atan2(k, -1)) % 360
path = math.degrees(math.atan2(-0.8, -1)) % 360
check("Krasnikov tipped edge angle (deg)", edge, 220.36, 0.001)
print("   return direction", round(path, 2), "deg lies inside the cone [45,", round(edge, 2), "]:", 45 < path < edge)
xs = [i / 100 for i in range(101)]
inside = all(0.45 + 0.8 * x >= x / 0.8 - 1e-12 for x in xs)
print("   return path t = 0.45 + 0.8 x stays in the tube t >= x/0.8:", inside)
check("Krasnikov home time", 1.25 - 0.8, 0.45)

# ---------------------------------------------------------------- Chapter 2
section("Chapter 2: muons and twins")
v = 0.9995
dt = 15e3 / (v * c)
check("muon trip, Earth time (us)", dt * 1e6, 50.1, 0.002)
check("muon trip, own clock (us)", math.sqrt(1 - v**2) * dt * 1e6, 1.58, 0.005)
check("muon survival fraction", math.exp(-math.sqrt(1 - v**2) * dt / 2.197e-6), 0.49, 0.02)
check("muon trip in lifetimes (Earth time)", dt / 2.197e-6, 23, 0.02)
check("survival without dilation", math.exp(-dt / 2.197e-6), 1.3e-10, 0.1)
check("twins: Earth time (yr)", 2 * 4.24 / 0.8, 10.6, 0.001)
check("twins: traveller (yr)", 0.6 * 2 * 4.24 / 0.8, 6.36, 0.001)
gam = 1 / math.sqrt(1 - 0.5**2)
check("Problem 2.2: explosion time for an observer at 0.5 (yr)", -gam * 0.5 * 550, -317.5, 0.001)

section("Chapter 2: clocks in a gravitational field")
dphi = 9.8 * 8850 / c**2
check("Everest rate difference", dphi, 9.6e-13, 0.01)
check("Everest, 80 years (ms)", dphi * 80 * year * 1e3, 2.4, 0.03)
check("33 cm height shift (Chou et al.)", 9.8 * 0.33 / c**2, 3.6e-17, 0.05)
print("   (measured: (4.1 +- 1.6) x 1e-17, consistent)")
check("Sun r_s (km)", 2 * G * M_sun / c**2 / 1e3, 2.95, 0.01)
check("escape speed at the Earth's surface (km/s)", math.sqrt(2 * GM_earth / R_earth) / 1e3, 11.2, 0.01)
check("Michell: Sun escape speed x 500 exceeds c", 500 * math.sqrt(2 * G * M_sun / 6.957e8) / c, 1.03, 0.02)

section("Chapter 2: the thrown ball")
g = 9.8
T = 2.0
v0 = g * T / 2
t = sp.symbols("t")
h_path = v0 * t - g * t**2 / 2
gain = sp.integrate(g * h_path - sp.diff(h_path, t) ** 2 / 2, (t, 0, T))
check("ball's gain v0^3/(3g) (m^2/s)", float(gain), v0**3 / (3 * g), 1e-9)
check("ball's gain in seconds", float(gain) / c**2, 3.6e-16, 0.02)
eps = sp.symbols("epsilon")
perturbed = h_path + eps * sp.sin(sp.pi * t / T)
gain_eps = sp.integrate(g * perturbed - sp.diff(perturbed, t) ** 2 / 2, (t, 0, T))
second = sp.simplify(gain_eps - gain)
print("   gain(path + eps sin(pi t/T)) - gain(path) =", sp.simplify(second), "(negative for eps != 0)")

section("Chapter 2: tides")
check("stretching gradient at the surface, 2GM/r^3 (1/s^2)", 2 * GM_earth / R_earth**3, 3.1e-6, 0.02)
check("across a 2 m person (m/s^2)", 2 * GM_earth / R_earth**3 * 2, 6e-6, 0.05)
grad_orbit = 2 * GM_earth / (R_earth + 420e3) ** 3
check("stretching gradient in low orbit (1/s^2)", grad_orbit, 2.5e-6, 0.02)
check("drift of balls 10 m apart in a minute (cm)", 0.5 * grad_orbit * 10 * 60**2 * 100, 4.5, 0.03)

section("Chapter 2: Figure 2.3 tick marks")
for tau in (1, 2, 3):
    tt = tau / 0.6
    print(f"   outbound proper year {tau}: t = {tt:.3f}, x = {0.8 * tt:.3f}")
for tau in (4, 5, 6):
    tt = 5.3 + (tau - 0.6 * 5.3) / 0.6
    print(f"   return proper year {tau}: t = {tt:.3f}, x = {0.8 * (10.6 - tt):.3f}")

# ---------------------------------------------------------------- Chapter 3
section("Chapter 3")
vv = sp.symbols("v", positive=True)
gamma = 1 / sp.sqrt(1 - vv**2)
rho0, tau_, rhov = sp.symbols("rho0 tau rho_vac", positive=True)
w = sp.Matrix([gamma, gamma * vv, 0, 0])
eta = sp.diag(-1, 1, 1, 1)
T_rod = sp.diag(rho0, -tau_, 0, 0)                    # lowered components in flat space
print("   rod seen in passing:", sp.simplify((w.T * T_rod * w)[0]), "= gamma^2 (rho0 - v^2 tau)")
T_dust = rho0 * (eta * sp.Matrix([1, 0, 0, 0])) * (eta * sp.Matrix([1, 0, 0, 0])).T
print("   dust (rest frame) seen by w:", sp.simplify((w.T * T_dust * w)[0]))
T_vac = -rhov * eta
print("   vacuum energy seen by w:", sp.simplify((w.T * T_vac * w)[0]))
check("gamma^2 at 0.8", float((1 / (1 - 0.8**2))), 25 / 9, 1e-12)
check("steel tau/rho0 at 1e9 Pa", 1e9 / (7850 * c**2), 1.4e-12, 0.05)
check("lapse stress for alpha'' = 1e-9 /m^2 (Pa)", 1e-9 / (8 * math.pi) * c**4 / G, 5e33, 0.05)
check("shear energy density, beta' = 1/m (J/m^3)", -1 / (32 * math.pi) * c**4 / G, -1.2e42, 0.02)
check("as a mass density (kg/m^3)", -1 / (32 * math.pi) * c**4 / G / c**2, -1.3e25, 0.05)

# von Laue: a static stress field in a box, as an explicit example. A 1D
# balance: gas pressure p over the gas height H pushes, wall tension tau over
# the wall thickness d pulls; equilibrium p H = 2 tau d gives zero total stress.
p, H, d = sp.symbols("p H d", positive=True)
tau_wall = p * H / (2 * d)
print("   net xx stress across a cut:", sp.simplify(p * H - 2 * tau_wall * d))

# the lapse example, rechecked from the metric
x = sp.symbols("x")
alpha = sp.Function("alpha")(x)
coords = sp.symbols("t x y z")
gmet = sp.diag(-alpha**2, 1, 1, 1)
X = [coords[0], x, coords[2], coords[3]]
ginv = gmet.inv()
n4 = 4
Gam = [[[sum(ginv[a, dd] * (sp.diff(gmet[dd, b], X[cc]) + sp.diff(gmet[dd, cc], X[b])
          - sp.diff(gmet[b, cc], X[dd])) for dd in range(n4)) / 2
         for cc in range(n4)] for b in range(n4)] for a in range(n4)]


def ricci(a, b):
    return sp.simplify(sum(sp.diff(Gam[m][a][b], X[m]) - sp.diff(Gam[m][a][m], X[b])
                           + sum(Gam[m][m][l] * Gam[l][a][b] - Gam[m][b][l] * Gam[l][a][m]
                                 for l in range(n4)) for m in range(n4)))


Ric = sp.Matrix(n4, n4, lambda a, b: ricci(a, b))
Rs = sp.simplify(sum(ginv[a, b] * Ric[a, b] for a in range(n4) for b in range(n4)))
Ein = sp.simplify(Ric - Rs * gmet / 2)
print("   lapse metric Einstein tensor diag:", [sp.simplify(Ein[i, i]) for i in range(4)])

print()
print("failures:", failures if failures else "none")
