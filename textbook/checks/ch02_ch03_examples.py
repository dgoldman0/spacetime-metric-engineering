"""Checks for the worked examples and numbers in Chapters 2 and 3.

Run: python3 checks/ch02_ch03_examples.py  (needs sympy)
Each check prints its result; nothing here is used by the LaTeX build.
"""
import sympy as sp

# ---------------------------------------------------------------- utilities
def christoffel(g, X):
    n = len(X); gi = g.inv()
    return [[[sp.simplify(sum(gi[a, d]*(sp.diff(g[d, b], X[c]) + sp.diff(g[d, c], X[b]) - sp.diff(g[b, c], X[d]))
                            for d in range(n))/2) for c in range(n)] for b in range(n)] for a in range(n)]

def ricci(g, X):
    n = len(X); G = christoffel(g, X)
    R = sp.zeros(n)
    for b in range(n):
        for c in range(n):
            R[b, c] = sp.simplify(sum(sp.diff(G[a][b][c], X[a]) - sp.diff(G[a][b][a], X[c])
                                      + sum(G[a][a][d]*G[d][b][c] - G[a][c][d]*G[d][b][a] for d in range(n))
                                      for a in range(n)))
    return R

def einstein(g, X):
    R = ricci(g, X); gi = g.inv()
    Rs = sp.simplify(sum(gi[a, b]*R[a, b] for a in range(len(X)) for b in range(len(X))))
    return sp.simplify(R - Rs*g/2), R, Rs

t, x, y, z = sp.symbols('t x y z', real=True)
X = [t, x, y, z]

# ------------------------------------------ Chapter 2: numbers
c = 2.99792458e8; GM = 3.986004e14; RE = 6.371e6; rG = 2.6560e7; day = 86400
grav = (GM/RE - GM/rG)/c**2*day*1e6
v = (GM/rG)**0.5
vel = v**2/(2*c**2)*day*1e6
print(f"GPS: gravitational +{grav:.2f} us/day, velocity -{vel:.2f} us/day, net {grav-vel:.2f} us/day, v = {v:.0f} m/s")
print(f"GPS: ranging error per day {c*(grav-vel)*1e-6/1e3:.1f} km")
print(f"Twin: Earth time {2*4.24/0.8:.2f} yr, traveller {2*4.24/0.8*(1-0.8**2)**0.5:.2f} yr")
Msun_m = 1476.6  # G*Msun/c^2 in metres
rate_ns = (1 - 2*1.4*Msun_m/12000)**0.5
print(f"Neutron star (1.4 Msun, 12 km): surface clock rate {rate_ns:.3f}")
print(f"c^4/G = {c**4/6.674e-11:.3e} N;  c^2/G = {c**2/6.674e-11:.3e} kg/m")

# ------------------------------------------ Chapter 2: moving coordinates are flat
v0 = sp.symbols('v0', real=True)
g_flow = sp.Matrix([[-1 + v0**2, -v0, 0, 0], [-v0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])  # -dt^2 + (dx - v0 dt)^2
Gf, Rf, _ = einstein(g_flow, X)
print("Uniform flow metric is flat:", sp.simplify(Rf) == sp.zeros(4))

# ------------------------------------------ Chapter 3: clock-rate (lapse) example
a = sp.Function('alpha')(x)
g_lapse = sp.diag(-a**2, 1, 1, 1)
G_l, R_l, Rs_l = einstein(g_lapse, X)
print("Lapse example: R_tt =", sp.simplify(R_l[0, 0]), "; R_xx =", sp.simplify(R_l[1, 1]), "; R =", sp.simplify(Rs_l))
print("Lapse example: G_tt =", sp.simplify(G_l[0, 0]), "; G_xx =", sp.simplify(G_l[1, 1]),
      "; G_yy =", sp.simplify(G_l[2, 2]), "; G_zz =", sp.simplify(G_l[3, 3]))
Gamma_l = christoffel(g_lapse, X)
print("Lapse example: Gamma^t_tx =", Gamma_l[0][0][1], "; Gamma^x_tt =", Gamma_l[1][0][0])
# linear lapse (Rindler-like) is flat
g_lin = sp.diag(-(1 + sp.symbols('g0', positive=True)*x)**2, 1, 1, 1)
print("Linear lapse is flat:", sp.simplify(ricci(g_lin, X)) == sp.zeros(4))

# ------------------------------------------ Chapter 3: shear-flow example, energy density for observers at rest in the flow
b = sp.Function('beta')(y)
g_shear = sp.Matrix([[-1 + b**2, b, 0, 0], [b, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])  # -dt^2 + (dx + beta dt)^2
G_s, _, _ = einstein(g_shear, X)
n_up = sp.Matrix([1, -b, 0, 0])  # normal observer 4-velocity (unit lapse)
rho = sp.simplify((n_up.T*G_s*n_up)[0]/(8*sp.pi))
print("Shear flow: energy density seen by observers at rest in the flow rho =", rho)

# ------------------------------------------ Chapter 3: weak-field static metric, Newtonian limit
eps = sp.symbols('epsilon', positive=True)
Phi = sp.Function('Phi')(x, y, z)
g_wf = sp.diag(-(1 + 2*eps*Phi), 1 - 2*eps*Phi, 1 - 2*eps*Phi, 1 - 2*eps*Phi)
G_wf, _, _ = einstein(g_wf, X)
G00_first = sp.simplify(sp.series(G_wf[0, 0], eps, 0, 2).removeO().coeff(eps, 1))
lap = sp.diff(Phi, x, 2) + sp.diff(Phi, y, 2) + sp.diff(Phi, z, 2)
print("Weak field: G_tt at first order minus 2*Laplacian(Phi) =", sp.simplify(G00_first - 2*lap))
