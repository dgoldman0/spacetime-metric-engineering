"""Checks for the third round of revisions to Chapters 1-3 (26 September 2026).

This round began when the user found that "How stiff is the sheet?" had passed
the written review criteria although its answer taught the fall-off of gravity
with distance instead of stiffness. The puzzle was redesigned with the design
worksheet in reviews/puzzle-design-worksheet.md, and every thought experiment
and check was then re-reviewed independently. This script verifies the numbers
and claims of the redesigned items. Run with `make checks`; the output is kept
in checks/rev3_redesigns.log.
"""
import math

import sympy as sp

c = 2.99792458e8          # m/s
G = 6.674e-11             # N m^2 kg^-2
atm = 101325.0            # Pa
E_steel = 2.0e11          # Pa, Young's modulus of steel
E_rubber = 2.0e6          # Pa, a typical rubber (1-10 MPa)
strongest = 1.3e11        # Pa, breaking strength of the strongest materials (graphene)

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
section("Chapter 1: How stiff is the sheet? (stress per strain)")
check("stress to strain steel by 1e-9 (Pa)", E_steel * 1e-9, 200, 0.01)
check("that stress as a fraction of an atmosphere (1/500)", E_steel * 1e-9 / atm, 1 / 500, 0.02)
check("steel is about 1e5 times stiffer than rubber", E_steel / E_rubber, 1e5, 0.01)
stiff_1m = c**4 / (8 * math.pi * G)
check("stiffness of spacetime on the scale of 1 m, c^4/(8 pi G) (Pa)", stiff_1m, 5e42, 0.05)
claim("more than thirty orders beyond the strongest materials",
      math.log10(stiff_1m / strongest) > 30)
print(f"    log10(stiffness / strongest strength) = {math.log10(stiff_1m / strongest):.2f}")
p9 = 1e-9 * stiff_1m
check("stress for a strain of 1e-9 across 1 m (Pa)", p9, 5e33, 0.05)
claim("more than 1e31 times the stress steel needs for the same strain", p9 / (E_steel * 1e-9) > 1e31)
print(f"    ratio to steel = {p9 / (E_steel * 1e-9):.3g}")
eps, L = sp.symbols('epsilon L', positive=True)
ratio = (eps * sp.Symbol('K') / L**2) / (E_steel * eps)
claim("the comparison with steel does not depend on the size of the strain",
      sp.diff(ratio, eps) == 0)
# GW170817 (Abbott et al. 2018): pressure at twice nuclear saturation density
# 3.5 (+2.7, -1.7) x 10^34 dyn/cm^2 at 90% credibility; 1 dyn/cm^2 = 0.1 Pa.
lo, mid, hi = (3.5 - 1.7) * 1e33, 3.5e33, (3.5 + 2.7) * 1e33
print(f"    GW170817 pressure at twice nuclear density: {lo:.2g} to {hi:.2g} Pa (median {mid:.2g})")
claim("5e33 Pa lies inside the GW170817 range at twice nuclear density", lo <= p9 <= hi)

# The rule of thumb against the exact demand of Chapter 3: a Gaussian bump
# alpha = 1 + eps exp(-x^2/L^2) in flat space demands p = alpha''/(8 pi alpha).
x = sp.symbols('x', real=True)
alpha = 1 + eps * sp.exp(-x**2 / L**2)
p_exact = sp.diff(alpha, x, 2) / (8 * sp.pi * alpha)
p_centre = sp.simplify(sp.series(p_exact.subs(x, 0), eps, 0, 2).removeO())
claim("exact demand at the centre of the bump is -2 eps/(8 pi L^2): the rule to within a factor 2",
      sp.simplify(p_centre + 2 * eps / (8 * sp.pi * L**2)) == 0)


# ------------------------------------------------ after the independent reviews
# The stress-per-strain version above failed review (a steady gradient is free;
# the stiffness depends on the scale). Its checks stay as the record of that
# version. The checks below cover the text written after the reviews.
GM_earth = 3.986004e14
R_earth = 6.371e6
GM_sun = 1.32712e20
year = 3.156e7
AU = 1.495979e11
hbar = 1.054571817e-34
day = 86400.0

section("Chapter 1: Denting time in the laboratory (osmium ball)")
rho_os = 22590.0
R_ball = 0.5
M_ball = rho_os * 4 / 3 * math.pi * R_ball**3
check("mass of a 1 m osmium ball (kg), 'about twelve tonnes'", M_ball, 1.2e4, 0.02)
check("mass per unit radius (kg/m)", M_ball / R_ball, 2.4e4, 0.02)
dent_surface = G * M_ball / (c**2 * R_ball)
check("slowing at the surface", dent_surface, 2e-23, 0.15)
d_far = 10.0
far = G * M_ball / (c**2 * d_far)
print(f"    clock 10 m away is slowed by {far / dent_surface * 100:.1f}% of the surface value")
claim("the far clock's slowing is only a few percent of the surface value", far / dent_surface < 0.1)
diff = dent_surface - far
print(f"    difference {diff:.3g}; best clocks 1e-18; factor {1e-18 / diff:.3g}")
claim("difference is tens of thousands of times below 1e-18", 1e4 < 1e-18 / diff < 1e5)
R_needed = math.sqrt(1e-18 * 3 * c**2 / (4 * math.pi * G * rho_os))
check("diameter of an osmium ball denting time by 1e-18 (m)", 2 * R_needed, 240, 0.02)
check("its mass in tonnes (160 million)", rho_os * 4 / 3 * math.pi * R_needed**3 / 1e3, 1.6e8, 0.03)

section("Chapter 1: other corrected numbers")
check("stress to curve spacetime with radius of curvature 1 m, c^4/(8 pi G) (Pa)",
      c**4 / (8 * math.pi * G), 5e42, 0.05)
check("airliner speed effect v^2/2c^2 at 250 m/s", 250**2 / (2 * c**2), 3.5e-13, 0.02)
check("height effect gh/c^2 at 11 km", 9.8 * 11e3 / c**2, 1.2e-12, 0.02)
check("space station speed (km/s)", math.sqrt(GM_earth / 6.791e6) / 1e3, 7.7, 0.01)
check("white dwarf 0.6 Msun, 7000 km: GM/(c^2 R)", 0.6 * GM_sun / (c**2 * 7.0e6), 1.3e-4, 0.03)
check("warp round trip of 20 ly at 5c (years)", 20 / 5, 4.0, 1e-12)
check("coasting round trip at 0.99c, home (years)", 20 / 0.99, 20.2, 0.005)
check("coasting round trip, crew (years)", 20 / 0.99 * math.sqrt(1 - 0.99**2), 2.85, 0.01)
u1 = math.pi**2 * hbar * c / (720 * (1e-6) ** 4)
check("orders of magnitude between 5e42 and the 1 um gap", math.log10(5e42 / u1), 46, 0.01)
d_needed = (math.pi**2 * hbar * c / (720 * 5e42)) ** 0.25
check("plate gap giving 5e42 J/m^3 (m)", d_needed, 3e-18, 0.05)
check("times smaller than a proton (radius 0.84 fm)", 0.84e-15 / d_needed, 275, 0.05)
d_atm = (math.pi**2 * hbar * c / (240 * 101325)) ** 0.25
check("gap at which the Casimir pressure is one atmosphere (nm)", d_atm * 1e9, 11, 0.05)
check("robots at 0.9c to 10 ly (years)", 10 / 0.9, 11.1, 0.005)

section("Chapter 2: Betelgeuse and the passing ship")
gam = 1 / math.sqrt(1 - 0.25)
t_crew = gam * (0 - 0.5 * 550)
check("crew's time of the explosion (years before passing)", -t_crew, 318, 0.005)
check("distance by the crew's reckoning (ly)", math.sqrt(550**2 + t_crew**2), 635, 0.002)
check("contracted distance as they pass (ly)", 550 / gam, 476, 0.002)
check("light still on its way when they pass (ly)", math.sqrt(550**2 + t_crew**2) + t_crew, 318, 0.005)

section("Chapter 2: the twins' signals")
T_leg = 4.24 / 0.8 * 0.6
dop = math.sqrt((1 + 0.8) / (1 - 0.8))
check("Doppler factor at 0.8", dop, 3, 1e-12)
check("traveller receives, outbound (Earth years)", T_leg / dop, 1.06, 0.01)
check("traveller receives, inbound (Earth years)", T_leg * dop, 9.54, 0.01)
check("light from the turnaround reaches Earth (years)", 4.24 / 0.8 + 4.24, 9.54, 0.01)
check("gap for a star ten times farther (years)", 10 * (2 * 4.24 / 0.8) * (1 - 0.6), 42.4, 0.005)

section("Chapter 2: checks and river")
check("probe A to C: speed", 4 / 5, 0.8, 1e-12)
check("probe A to C: proper time (s)", math.sqrt(25 - 16), 3, 1e-12)
check("distance of A and B for an observer who finds them simultaneous (ls)", math.sqrt(7), 2.65, 0.005)
frac_centre = 0.5 * GM_earth / (c**2 * R_earth)
check("centre clock slow compared with the surface (uniform Earth)", frac_centre, 3.5e-10, 0.01)
check("per year (ms)", frac_centre * year * 1e3, 11, 0.01)
check("hanging clock at 2 r_s: sqrt(1 - 1/2)", math.sqrt(0.5), 0.71, 0.005)
v_esc = math.sqrt(2 * GM_earth / R_earth)
check("ground clock lag from the river at the escape speed (us/day)", v_esc**2 / (2 * c**2) * day * 1e6, 60, 0.01)
check("Pound-Rebka: sigma by which 1.05 +- 0.10 excludes 2", (2 - 1.05) / 0.10, 9.5, 1e-12)

section("Chapter 3: a drop and a lake")
g_drop = G * (1000 * 4 / 3 * math.pi * 0.01**3) / 0.01**2
check("Earth's pull over the pull at a 1 cm drop's surface", 9.81 / g_drop, 3.5e9, 0.02)
check("Vddot/V = -4 pi G rho for water (s^-2)", 4 * math.pi * G * 1000, 8.4e-7, 0.01)
check("pressure correction a few metres down, 3p/(rho c^2)", 3 * 5e4 / (1000 * c**2), 1.7e-15, 0.05)

section("Chapter 3: checks, price and problems")
R_bh = math.sqrt(3 * c**2 / (8 * math.pi * G * 1000))
check("radius of a water ball that traps its light (m)", R_bh, 4.0e11, 0.01)
check("same in AU", R_bh / AU, 2.7, 0.01)
claim("beyond the orbit of Mars (1.52 AU)", R_bh / AU > 1.52)
fl = 0.8**2 / (1 - 0.8**2)
check("gamma^2 v^2 at 0.8", fl, 16 / 9, 1e-12)
check("dust seen at 0.8 (multiple of rho)", 1 + fl, 25 / 9, 1e-12)
check("radiation seen at 0.8", 1 + fl * 4 / 3, 91 / 27, 1e-12)
check("steel tau/rho at 1e9 Pa", 1e9 / (7850 * c**2), 1.4e-12, 0.02)
B = sp.symbols('B', positive=True)
claim("magnetic field: rho + sum p = B^2", sp.simplify(B**2 / 2 + B**2 / 2 + B**2 / 2 - B**2 / 2 - B**2) == 0)
check("parabolic bump of 1e-9 within 1 m: peak tension (Pa)", 8e-9 * c**4 / (8 * math.pi * G), 4e34, 0.05)
check("shear mass density at beta' = 1/m (kg/m^3), text rounds 1.34e25 to two figures", c**4 / G / (32 * math.pi) / c**2, 1.3e25, 0.05)
check("Sun: (3/5) GM/(R c^2), pressure's share of Mc^2 (uniform star)", 0.6 * GM_sun / (6.957e8 * c**2), 1.3e-6, 0.03)
xs = sp.symbols('x', real=True)
alpha_b = 1 + sp.Rational(1, 2) * sp.exp(-xs**2)
claim("a bump's alpha'' integrates to zero", sp.integrate(sp.diff(alpha_b, xs, 2), (xs, -sp.oo, sp.oo)) == 0)

# The shear claim (riders see -(beta')^2/32pi; light along z sees -(beta')^2/16pi)
# was verified with the (dx - beta dt) convention in the reconciliation scratch
# script verify_claims.py; it is repeated here so the record is in the repository.
t_, x_, y_, z_ = sp.symbols('t x y z', real=True)
bet = sp.Function('beta')(y_)
X = [t_, x_, y_, z_]
gm = sp.Matrix([[-1 + bet**2, -bet, 0, 0], [-bet, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
gi = sp.simplify(gm.inv())
Gm = [[[sp.simplify(sum(gi[m, k] * (sp.diff(gm[k, a], X[b]) + sp.diff(gm[k, b], X[a]) - sp.diff(gm[a, b], X[k]))
                       for k in range(4)) / 2) for b in range(4)] for a in range(4)] for m in range(4)]
def Rm(m, a, n, b):
    e = sp.diff(Gm[m][a][b], X[n]) - sp.diff(Gm[m][a][n], X[b])
    return e + sum(Gm[m][n][l] * Gm[l][a][b] - Gm[m][b][l] * Gm[l][a][n] for l in range(4))
Ric = sp.Matrix(4, 4, lambda a, b: sp.simplify(sum(Rm(m, a, m, b) for m in range(4))))
Rs = sp.simplify(sum(gi[a, b] * Ric[a, b] for a in range(4) for b in range(4)))
Gt = (Ric - Rs * gm / 2).applyfunc(sp.simplify)
w_r = sp.Matrix([1, bet, 0, 0])
k_z = w_r + sp.Matrix([0, 0, 0, 1])
claim("(dx - beta dt): riders unit timelike", sp.simplify((w_r.T * gm * w_r)[0] + 1) == 0)
claim("(dx - beta dt): riders see -(beta')^2/(32 pi)",
      sp.simplify((w_r.T * Gt * w_r)[0] / (8 * sp.pi) + sp.diff(bet, y_)**2 / (32 * sp.pi)) == 0)
claim("light along z: T(k,k) = -(beta')^2/(16 pi), k null",
      sp.simplify((k_z.T * gm * k_z)[0]) == 0
      and sp.simplify((k_z.T * Gt * k_z)[0] / (8 * sp.pi) + sp.diff(bet, y_)**2 / (16 * sp.pi)) == 0)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED: " + "; ".join(failures))
    raise SystemExit(1)
print("all checks passed")
