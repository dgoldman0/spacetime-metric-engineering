import time, sympy as sp
t, l, th, ph = sp.symbols('t l theta phi', real=True)
X = (t, l, th, ph)
FIELDS = ('al', 'be', 'A', 'B')
MAXORD = 4
JET = {}
for f in FIELDS:
    for i in range(MAXORD + 1):
        for j in range(MAXORD + 1 - i):
            pos = f in ('al', 'A', 'B') and i == 0 and j == 0
            JET[(f, i, j)] = sp.Symbol(f'{f}_{i}{j}', positive=True) if pos else sp.Symbol(f'{f}_{i}{j}', real=True)
S2J = {v: k for k, v in JET.items()}

def D(expr, k):
    res = sp.diff(expr, X[k])
    if k < 2:
        for s in expr.free_symbols:
            if s in S2J:
                f, i, j = S2J[s]
                ni, nj = (i + 1, j) if k == 0 else (i, j + 1)
                res += sp.diff(expr, s) * JET[(f, ni, nj)]
    return res

al, be, A, B = (JET[(f, 0, 0)] for f in FIELDS)
g = sp.Matrix([[-al**2 + A*be**2, A*be, 0, 0], [A*be, A, 0, 0], [0, 0, B, 0], [0, 0, 0, B*sp.sin(th)**2]])
gi = sp.Matrix([[-1/al**2, be/al**2, 0, 0], [be/al**2, 1/A - be**2/al**2, 0, 0], [0, 0, 1/B, 0], [0, 0, 0, 1/(B*sp.sin(th)**2)]])
assert sp.simplify(g*gi - sp.eye(4)) == sp.zeros(4)
T0 = time.time()
Gam = [[[sp.cancel(sum(sp.Rational(1, 2)*gi[a, d]*(D(g[d, c], b) + D(g[d, b], c) - D(g[b, c], d)) for d in range(4))) for c in range(4)] for b in range(4)] for a in range(4)]
print('christoffel', time.time() - T0)
T0 = time.time()
Ric = sp.zeros(4)
for b in range(4):
    for d in range(b, 4):
        e = 0
        for a in range(4):
            e += D(Gam[a][d][b], a) - D(Gam[a][a][b], d)
            for c in range(4):
                e += Gam[a][a][c]*Gam[c][d][b] - Gam[a][d][c]*Gam[c][a][b]
        Ric[b, d] = Ric[d, b] = sp.cancel(e)
print('ricci', time.time() - T0)
T0 = time.time()
Rs = sp.cancel(sum(gi[a, b]*Ric[a, b] for a in range(4) for b in range(4)))
G = (Ric - g*Rs/2).applyfunc(sp.cancel)
print('einstein', time.time() - T0)
n = sp.Matrix([1/al, -be/al, 0, 0]); e1 = sp.Matrix([0, 1/sp.sqrt(A), 0, 0]); e2 = sp.Matrix([0, 0, 1/sp.sqrt(B), 0])
rho = sp.cancel((n.T*G*n)[0]); pl = sp.cancel((e1.T*G*e1)[0]); j = sp.cancel(-(e1.T*G*n)[0]); pO = sp.cancel((e2.T*G*e2)[0])
print('frame', time.time() - T0)
print(sp.count_ops(rho), sp.count_ops(pl), sp.count_ops(j), sp.count_ops(pO))
print(pO.free_symbols)
