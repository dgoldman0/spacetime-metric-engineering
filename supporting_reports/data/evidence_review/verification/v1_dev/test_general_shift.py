import time, sys
sys.path.insert(0, '.')
import sympy as sp
import engine
from engine import curvature, project, is_zero, J, canon

def say(*a):
    print(*a, flush=True)

T0 = time.time()
t, x, y, z = sp.symbols('t x y z', real=True)
X = (t, x, y, z)
al = sp.Function('alpha')(*X)
bx, by, bz = [sp.Function(n)(*X) for n in ('bx', 'by', 'bz')]
b = [bx, by, bz]
g = sp.zeros(4, 4)
g[0, 0] = -al**2 + bx**2 + by**2 + bz**2
for i in range(3):
    g[0, i + 1] = g[i + 1, 0] = b[i]
    g[i + 1, i + 1] = 1
out = curvature(g, X)
say('general flat-slice curvature', time.time() - T0)
frame = [[1 / al, -bx / al, -by / al, -bz / al], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
T8 = project(out['G'], frame)
say('projected', time.time() - T0, [len(sp.Add.make_args(T8[i, j])) for i in range(4) for j in range(i, 4)])
D = sp.diff
xs = (x, y, z)
sig = [[(D(b[i], xs[j]) + D(b[j], xs[i])) / 2 for j in range(3)] for i in range(3)]
th = sum(D(b[i], xs[i]) for i in range(3))
om = [D(bz, y) - D(by, z), D(bx, z) - D(bz, x), D(by, x) - D(bx, y)]
curl = lambda v: [D(v[2], y) - D(v[1], z), D(v[0], z) - D(v[2], x), D(v[1], x) - D(v[0], y)]
cc = curl(om)
rho_claim = (th**2 - sum(sig[i][j]**2 for i in range(3) for j in range(3))) / (2 * al**2)  # = 8 pi rho
say('8pi rho = (theta^2 - sigma:sigma)/(2 alpha^2):', is_zero(T8[0, 0] - rho_claim), time.time() - T0)
for i in range(3):
    j8 = -cc[i] / (2 * al) - sum((sig[i][k] - (th if i == k else 0)) * D(al, xs[k]) for k in range(3)) / al**2
    say(f'8pi j_{xs[i]} = -curl(omega)/(2alpha) - (sigma - theta I).grad(alpha)/alpha^2 (T_ni = -j_i):', is_zero(T8[0, i + 1] + j8), time.time() - T0)
say('total', time.time() - T0)
