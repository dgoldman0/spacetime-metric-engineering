import sys
sys.path.insert(0, '..')
sys.path.insert(0, '.')
import v1_flat_slice_class as V
import sympy as sp
T8, out = V.c0_tensor()
c = -V.D(V.r * V.s_, V.r) / (2 * V.r)
d = T8[V.N_, V.Z_] - c
print('sym_zero', V.sym_zero(d))
print('probe', V.probe_zero(d))
e = V.J(d)
print(sorted(e.free_symbols, key=lambda s: s.name))
print(sp.cancel(sp.together(e)))
