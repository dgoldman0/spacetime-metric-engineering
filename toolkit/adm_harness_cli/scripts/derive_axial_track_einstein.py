#!/usr/bin/env python3
"""Derive the orthonormal Einstein tensor of the axial track metric; write a numeric module.

Metric on (sigma, z, r, phi) with phi a Killing direction:

    ds^2 = -alpha^2 dsigma^2 + A^2 (dz + beta dsigma)^2 + dr^2 + C(r)^2 dphi^2,

with alpha, A, beta functions of (sigma, z, r). In the frame n = (d_sigma - beta d_z)/alpha,
e_z = d_z/A, e_r = d_r, e_phi = d_phi/C, the tensor splits into a product part, obtained by
setting every r-derivative of alpha, A and beta to zero, and a wall part in which every term
carries such a derivative. The script verifies that the (n, z) block of the product part
equals (C''/C) times the frame metric exactly, so the along-track null energies vanish
identically wherever the service fields are independent of r. The generated module is
consumed by adm_harness.axial_track; tests compare it with a four-dimensional
finite-difference kernel.
"""
from __future__ import annotations

from pathlib import Path
import sys

import sympy as sp
from sympy.core.function import AppliedUndef
from sympy.printing.numpy import NumPyPrinter

s, z, r = sp.symbols("sigma z r", real=True)
coords = (s, z, r)
FIELDS = ("alpha", "A", "beta")
alpha, A, beta = (sp.Function(name)(s, z, r) for name in FIELDS)
C = sp.Function("C")(r)


def einstein():
    g = sp.zeros(4, 4)
    g[0, 0] = -alpha**2+A**2*beta**2
    g[0, 1] = g[1, 0] = A**2*beta
    g[1, 1] = A**2
    g[2, 2] = 1
    g[3, 3] = C**2
    inverse = sp.simplify(g.inv())

    def d(expr, index):
        return sp.diff(expr, coords[index]) if index < 3 else 0

    gamma = [[[sp.simplify(sum(inverse[l, m]*(d(g[m, i], j)+d(g[m, j], i)-d(g[i, j], m)) for m in range(4))/2)
               for j in range(4)] for i in range(4)] for l in range(4)]
    ricci = sp.zeros(4, 4)
    for i in range(4):
        for j in range(i, 4):
            term = sum(d(gamma[l][i][j], l) for l in range(4))-sum(d(gamma[l][i][l], j) for l in range(4))
            term += sum(gamma[l][l][m]*gamma[m][i][j] for l in range(4) for m in range(4))
            term -= sum(gamma[l][j][m]*gamma[m][i][l] for l in range(4) for m in range(4))
            ricci[i, j] = ricci[j, i] = term
    scalar = sum(inverse[i, j]*ricci[i, j] for i in range(4) for j in range(4))
    einstein_tensor = ricci-g*scalar/2
    frame = sp.zeros(4, 4)
    frame[0, 0], frame[1, 0] = 1/alpha, -beta/alpha
    frame[1, 1] = 1/A
    frame[2, 2] = 1
    frame[3, 3] = 1/C
    return frame.T*einstein_tensor*frame


def jet_symbols():
    names, table = [], {}
    for name, function in zip(FIELDS, (alpha, A, beta)):
        base = sp.Symbol(name)
        table[function] = base
        names.append(name)
        for i, x in enumerate(coords):
            symbol = sp.Symbol(f"{name}_{'szr'[i]}")
            table[sp.Derivative(function, x)] = symbol
            names.append(symbol.name)
            for k in range(i, 3):
                y = coords[k]
                label = "".join(sorted("szr"[i]+"szr"[k], key="szr".index))
                symbol = sp.Symbol(f"{name}_{label}")
                table[sp.Derivative(function, x, y) if x != y else sp.Derivative(function, (x, 2))] = symbol
                names.append(symbol.name)
    for symbol, derivative in (("C", C), ("C_r", sp.Derivative(C, r)), ("C_rr", sp.Derivative(C, (r, 2)))):
        table[derivative] = sp.Symbol(symbol)
        names.append(symbol)
    return names, table


def to_symbols(expr, table):
    second = [(k, v) for k, v in table.items() if isinstance(k, sp.Derivative) and len(k.variables) == 2]
    first = [(k, v) for k, v in table.items() if isinstance(k, sp.Derivative) and len(k.variables) == 1]
    plain = [(k, v) for k, v in table.items() if not isinstance(k, sp.Derivative)]
    for group in (second, first, plain):
        expr = expr.xreplace(dict(group)) if group is plain else expr.subs(dict(group))
    if expr.has(sp.Derivative) or expr.atoms(AppliedUndef):
        raise AssertionError("unconverted derivative or function in generated expression")
    return expr


def random_check(expr, names, trials=6, seed=11):
    """Exact rational evaluation of expr at random jet values; returns True when every value is zero."""
    import random
    generator = random.Random(seed)
    symbols = [sp.Symbol(name) for name in names]
    for _ in range(trials):
        values = {sym: sp.Rational(generator.randint(5, 40), generator.randint(3, 11)) for sym in symbols}
        if sp.nsimplify(expr.xreplace(values)) != 0:
            return False
    return True


def main():
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).resolve().parents[1] / "adm_harness/axial_einstein_generated.py")
    tensor = einstein()
    names, table = jet_symbols()
    radial = [sp.Symbol(f"{f}_{suffix}") for f in FIELDS for suffix in ("r", "sr", "zr", "rr")]
    components = {"nn": (0, 0), "nz": (0, 1), "zz": (1, 1), "nr": (0, 2), "zr": (1, 2), "rr": (2, 2), "pp": (3, 3),
                  "np": (0, 3), "zp": (1, 3), "rp": (2, 3)}
    generated = {}
    for key, (i, j) in components.items():
        full = to_symbols(tensor[i, j], table)
        numerator, denominator = sp.fraction(sp.together(full))
        numerator = sp.expand(numerator)
        assert not (denominator.free_symbols & set(radial))
        product_numerator = numerator.xreplace({symbol: 0 for symbol in radial})
        wall_numerator = sp.expand(numerator-product_numerator)
        assert sp.expand(wall_numerator.xreplace({symbol: 0 for symbol in radial})) == 0
        generated[key] = (product_numerator, wall_numerator, denominator)
        print(key, "wall numerator terms:", len(sp.Add.make_args(wall_numerator)),
              "product numerator terms:", len(sp.Add.make_args(product_numerator)), flush=True)
    ratio = sp.Symbol("C_rr")/sp.Symbol("C")
    for key, value in {"nn": -1, "nz": 0, "zz": 1}.items():
        product_numerator, _, denominator = generated[key]
        assert random_check(product_numerator-ratio*value*denominator, names), key
    for key in ("nr", "zr", "np", "zp", "rp"):
        assert generated[key][0] == 0 or random_check(generated[key][0], names), key
    for key in ("np", "zp", "rp"):
        assert generated[key][1] == 0 or random_check(generated[key][1], names), key
    rr, pp = generated["rr"], generated["pp"]
    assert random_check(rr[0]*pp[2]-pp[0]*rr[2], names)
    print("identities verified", flush=True)

    lines = [
        '"""Orthonormal Einstein tensor of the axial track metric, generated by',
        "scripts/derive_axial_track_einstein.py; edit the derivation script instead.",
        "",
        "The (n, z) block equals (C_rr/C) times the frame metric plus wall terms; rr and pp",
        "share the product value -K of the (sigma, z) metric; nr and zr are wall terms only.",
        '"""',
        "from __future__ import annotations",
        "",
        "import numpy as np",
        "",
        f"JET_NAMES = {tuple(names)!r}",
        "",
    ]
    printer = NumPyPrinter()
    unpack = "    " + ", ".join(names) + " = (j[name] for name in JET_NAMES)"
    for key in ("nn", "nz", "zz", "nr", "zr", "rr", "pp"):
        _, wall_numerator, denominator = generated[key]
        lines += [f"def wall_{key}(j):", unpack,
                  f"    return ({printer.doprint(wall_numerator)})/({printer.doprint(denominator)})", ""]
    product_numerator, _, denominator = generated["rr"]
    lines += ["def product_rr(j):", unpack,
              f"    return ({printer.doprint(product_numerator)})/({printer.doprint(denominator)})", ""]
    output.write_text("\n".join(lines)+"\n")
    print("wrote", output)


if __name__ == "__main__":
    main()
