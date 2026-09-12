#!/usr/bin/env python3
"""Exact rational verification of the archived finite-matrix contradiction.

The binary floating-point coefficients of the normalized numerical model are
treated as their exact dyadic rationals. This proves infeasibility of that
finite representation; it makes no continuum or constitutive extension.
"""
from datetime import datetime,timezone
from fractions import Fraction
from pathlib import Path
import json
import subprocess

import numpy as np

from adm_harness.source_ledger import sha256_file
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_field_membrane_exact_certificate'
INPUT=BASE/'joint_field_membrane_certificate/certificate.npz'


def exact_weights(matrix,approximate):
    count=matrix.shape[0]
    rows=[[Fraction(float(v)) for v in row]+[Fraction(0)] for row in matrix.T]
    rows.append([Fraction(1)]*count+[Fraction(1)])
    pivot_row=0;pivots=[]
    for column in range(count):
        choices=[i for i in range(pivot_row,len(rows)) if rows[i][column]]
        if not choices:continue
        i=choices[0];rows[pivot_row],rows[i]=rows[i],rows[pivot_row]
        pivot=rows[pivot_row][column]
        rows[pivot_row]=[v/pivot for v in rows[pivot_row]]
        for i in range(len(rows)):
            if i==pivot_row or not rows[i][column]:continue
            factor=rows[i][column]
            for j in range(column,count+1):rows[i][j]-=factor*rows[pivot_row][j]
        pivots.append(column);pivot_row+=1
    for row in rows:
        if not any(row[:-1]) and row[-1]:raise ArithmeticError('exact normalized equations conflict')
    weights=[Fraction(float(v)) for v in approximate]
    free=set(range(count))-set(pivots)
    for i,column in enumerate(pivots):
        weights[column]=rows[i][-1]-sum(rows[i][j]*weights[j] for j in free)
    return weights


def main():
    if OUTPUT.exists():raise RuntimeError('preserve completed exact certificate')
    previous=INPUT.parent/'manifest.json'
    hashes=json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__),previous,INPUT):hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for p,expected in hashes.items():
        if sha256_file(ROOT/p)!=expected:raise RuntimeError('changed exact-certificate input: '+p)
    with np.load(INPUT) as z:a=z['matrix'];b=z['rhs'];approximate=z['weights']
    weights=exact_weights(a,approximate)
    residual=[sum(Fraction(float(v))*w for v,w in zip(column,weights)) for column in a.T]
    rhs=sum(Fraction(float(v))*w for v,w in zip(b,weights))
    assert all(w>=0 for w in weights) and sum(weights)==1
    assert all(r==0 for r in residual) and rhs<0
    encode=lambda v:dict(numerator=str(v.numerator),denominator=str(v.denominator))
    OUTPUT.mkdir()
    write_json(OUTPUT/'weights.json',dict(weights=[encode(w) for w in weights],weighted_rhs=encode(rhs)))
    write_json(OUTPUT/'summary.json',dict(exact_coefficient_cancellation=True,
        nonnegative_weights=True,exact_weight_sum=1,weighted_rhs_decimal=float(rhs),
        constraints=len(weights),controls=a.shape[1],
        scope='Exact dyadic coefficients of the archived normalized finite response matrix; continuum and material laws remain separate'))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))
    print('Exact coefficient cancellation; nonnegative weights; right-hand side '+str(float(rhs)),flush=True)


if __name__=='__main__':main()
