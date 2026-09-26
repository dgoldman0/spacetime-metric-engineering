import sys, random
sys.path.insert(0, '.')
import v1_flat_slice_class as V
import sympy as sp
T8, out = V.c0_tensor()
c = -V.D(V.r * V.s_, V.r) / (2 * V.r)
d = T8[V.N_, V.Z_] - c
e = V.J(d)
syms = sorted(e.free_symbols, key=lambda s: s.name)
print([(s, s.assumptions0.get('positive')) for s in syms])
rng = random.Random(2026)
vals = {}
for s in syms:
    if s.name.split('__')[0] in V.POSITIVE or s.is_positive:
        vals[s] = sp.Rational(rng.randint(3, 29), rng.randint(2, 9))
    else:
        k = rng.randint(-19, 19)
        vals[s] = sp.Rational(k if k else 1, rng.randint(1, 9))
print(vals)
v = e.xreplace(vals)
print('value', v, type(v))
print('terms of e:', sp.Add.make_args(e)[:6])
