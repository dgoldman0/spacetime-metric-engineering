import time, sys
sys.path.insert(0, '.')
import sympy as sp
import mpmath as mp
import engine
from engine import curvature, project, is_zero, J, canon

def say(*a):
    print(*a, flush=True)

T0 = time.time()
# 1. Schwarzschild in Painleve-Gullstrand form, beta = B(r) = sqrt(2M/r)
t, th, ph = sp.symbols('t theta phi', real=True)
r = sp.Symbol('r', positive=True)
Bf = sp.Function('B')(r)
g = sp.Matrix([[-1 + Bf**2, Bf, 0, 0], [Bf, 1, 0, 0], [0, 0, r**2, 0], [0, 0, 0, r**2 * sp.sin(th)**2]])
out = curvature(g, (t, r, th, ph), riemann=True)
say('PG curvature done', time.time() - T0)
B, B_r, B_rr = sp.symbols('B B_r B_rr', real=True)
sub = {B_r: -B / (2 * r), B_rr: sp.Rational(3, 4) * B / r**2}
Gs = out['G'].applyfunc(lambda e: sp.cancel(sp.together(e.xreplace(sub))))
say('PG G with B=sqrt(2M/r):', Gs)
Rtrtr = sp.cancel(sp.together(out['Riem'][(0, 1, 0, 1)].xreplace(sub)))
say('PG R^t_{rtr} =', Rtrtr, ' (with B^2 = 2M/r this is', sp.simplify(Rtrtr.subs(B, sp.sqrt(2 * sp.Symbol('M', positive=True) / r))), ')')

# 2. FRW
T1 = time.time()
x, y, z = sp.symbols('x y z', real=True)
tt = sp.Symbol('t', real=True)
af = sp.Function('a')(tt)
g = sp.diag(-1, af**2, af**2, af**2)
out = curvature(g, (tt, x, y, z))
a, a_t, a_tt = sp.symbols('a a_t a_tt', real=True)
H = a_t / a
say('FRW G_tt - 3H^2:', canon(out['G'][0, 0] - 3 * H**2), ' G_xx/a^2 + 2a_tt/a + H^2:', canon(out['G'][1, 1] / a**2 + 2 * a_tt / a + H**2))
tp = sp.Symbol('tp', positive=True)
H0 = sp.Symbol('H0', positive=True)
for name, s_ in [('dust a=t^(2/3)', {a_t: sp.Rational(2, 3) * a / tp, a_tt: -sp.Rational(2, 9) * a / tp**2}),
                 ('radiation a=t^(1/2)', {a_t: a / (2 * tp), a_tt: -a / (4 * tp**2)}),
                 ('de Sitter a=exp(H0 t)', {a_t: H0 * a, a_tt: H0**2 * a})]:
    rho = canon(out['G'][0, 0].xreplace(s_) / (8 * sp.pi))
    p = canon(out['G'][1, 1].xreplace(s_) / a**2 / (8 * sp.pi))
    HH = canon(H.xreplace(s_))
    say(name, ' rho =', rho, ' rho - 3H^2/8pi =', canon(rho - 3 * HH**2 / (8 * sp.pi)), ' p/rho =', canon(p / rho))
say('FRW done', time.time() - T1)

# 3. Alcubierre
T2 = time.time()
Bx = sp.Function('Bx')(tt, x, y, z)
g = sp.Matrix([[-1 + Bx**2, Bx, 0, 0], [Bx, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
out = curvature(g, (tt, x, y, z))
nvec = [1, -Bx, 0, 0]
Gnn = project(out['G'], [nvec])[0, 0]
say('Alcubierre curvature done', time.time() - T2, 'Gnn terms', len(sp.Add.make_args(Gnn)))
Gnn_c = canon(Gnn)
say('Gnn (jets) =', Gnn_c)
# explicit Alcubierre profile
vs, sig, R = sp.Rational(3, 2), sp.Rational(8, 1), sp.Rational(1, 1)
rs = sp.sqrt((x - vs * tt)**2 + y**2 + z**2)
fexp = (sp.tanh(sig * (rs + R)) - sp.tanh(sig * (rs - R))) / (2 * sp.tanh(sig * R))
Bexp = -vs * fexp
inv = {v: k for k, v in engine._JET.items()}
syms = sorted(Gnn_c.free_symbols, key=lambda s: s.name)
vals_fns = {}
for s in syms:
    d = inv[s]
    e = d.xreplace({Bx: Bexp}).doit() if isinstance(d, sp.Derivative) else Bexp
    vals_fns[s] = sp.lambdify((tt, x, y, z), e, 'mpmath')
fprime = sp.lambdify(sp.Symbol('q'), sp.diff(fexp.subs(rs, sp.Symbol('q')), sp.Symbol('q')), 'mpmath') if False else None
q = sp.Symbol('q', positive=True)
fq = (sp.tanh(sig * (q + R)) - sp.tanh(sig * (q - R))) / (2 * sp.tanh(sig * R))
fprime = sp.lambdify(q, sp.diff(fq, q), 'mpmath')
Gnn_fn = sp.lambdify(syms, Gnn_c, 'mpmath')
mp.mp.dps = 40
import random
rng = random.Random(7)
for k in range(4):
    P = [mp.mpf(rng.uniform(-1, 1)), mp.mpf(rng.uniform(-1.5, 1.5)), mp.mpf(rng.uniform(-1.2, 1.2)), mp.mpf(rng.uniform(-1.2, 1.2))]
    vals = [vals_fns[s](*P) for s in syms]
    rho_engine = Gnn_fn(*vals) / (8 * mp.pi)
    rsv = mp.sqrt((P[1] - vs * P[0])**2 + P[2]**2 + P[3]**2)
    rho_alc = -(1 / (8 * mp.pi)) * (vs**2 * (P[2]**2 + P[3]**2)) / (4 * rsv**2) * fprime(rsv)**2
    say('pt', k, 'rho_engine =', mp.nstr(rho_engine, 20), ' Alcubierre eq19 =', mp.nstr(rho_alc, 20), ' diff =', mp.nstr(rho_engine - rho_alc, 5))
say('total', time.time() - T0)
