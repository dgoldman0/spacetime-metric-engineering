import time, sys
sys.path.insert(0, '.')
import sympy as sp
import engine
from engine import curvature, project, is_zero, J, canon

def say(*a):
    print(*a, flush=True)

T0 = time.time()
t, z, ph = sp.symbols('t z phi', real=True)
r = sp.Symbol('r', positive=True)
X = (t, z, r, ph)
al = sp.Function('alpha')(t, z, r)
be = sp.Function('beta')(t, z, r)
Af = sp.Function('A')(t, z, r)

def c0_metric(al, be, A):
    return sp.Matrix([[-al**2 + A**2 * be**2, A**2 * be, 0, 0],
                      [A**2 * be, A**2, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, r**2]])

def c0_frame(al, be, A):
    return [[1 / al, -be / al, 0, 0], [0, 1 / A, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1 / r]]

# ---- A = 1
out = curvature(c0_metric(al, be, 1), X)
T8 = project(out['G'], c0_frame(al, be, 1))   # 8 pi T_ab (orthonormal, lower)
say('C0 (A=1) tensor computed', time.time() - T0)
D = sp.diff
s = D(be, r) / al
K = D(be, z) / al
nop = lambda f: (D(f, t) - be * D(f, z)) / al
Q = nop(K) - K**2
Lap = lambda f: D(f, r, 2) + D(f, r) / r
claims = {
    (0, 0): -s**2 / 4,
    (0, 1): -D(r * s, r) / (2 * r),
    (0, 2): D(al**2 * s, z) / (2 * al**2) - K * D(sp.log(al), r),
    (1, 1): Lap(al) / al - 3 * s**2 / 4,
    (2, 2): (D(al, z, 2) + D(al, r) / r) / al + s**2 / 4 + Q,
    (3, 3): (D(al, r, 2) + D(al, z, 2)) / al - s**2 / 4 + Q,
    (1, 2): -D(al, r, z) / al - nop(s) / 2 + s * K,
    (0, 3): 0, (1, 3): 0, (2, 3): 0,
}
names = ['n', 'z', 'r', 'phi']
for (i, j), c in claims.items():
    ok = is_zero(T8[i, j] - c)
    say(f'8piT_{names[i]}{names[j]} matches table: {ok}')
say('elapsed', time.time() - T0)

# ---- A general: energy density and fluxes
T1 = time.time()
outA = curvature(c0_metric(al, be, Af), X)
T8A = project(outA['G'], c0_frame(al, be, Af))
say('C0A tensor computed', time.time() - T1)
sA = Af * D(be, r) / al
kA = (D(be, z) + be * D(sp.log(Af), z) - D(sp.log(Af), t)) / al
LapA = D(Af, r, 2) + D(Af, r) / r
claimA = {
    (0, 0): -LapA / Af - sA**2 / 4,
    (0, 1): -D(r * Af**2 * sA, r) / (2 * r * Af**2),
    (0, 2): D(Af * kA, r) / Af - D(sA, z) / (2 * Af),
}
for (i, j), c in claimA.items():
    say(f'C0A 8piT_{names[i]}{names[j]} matches: {is_zero(T8A[i, j] - c)}')
say('report form rho=-(A beta_r/alpha)^2/32pi holds iff Lap_perp A = 0; residual =', canon(T8A[0, 0] + sA**2 / 4))
say('elapsed', time.time() - T0)
