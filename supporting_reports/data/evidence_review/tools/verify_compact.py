import sympy as sp
exec(open('verify_identities.py').read().split("names=")[0])
a=al; b=be
nf=lambda f: (sp.diff(f,s)-b*sp.diff(f,z))/a
K=sp.diff(b,z)/a; sh=sp.diff(b,r)/a
Q=nf(K)-K**2
dpa=sp.diff(a,r,2)+sp.diff(a,r)/r
checks={
 'nn': -sh**2/4,
 'nz': -sp.diff(r*sh,r)/(2*r),
 'nr': sp.diff(a**2*sh,z)/(2*a**2)-K*sp.diff(a,r)/a,
 'zz': dpa/a-3*sh**2/4,
 'rr': (sp.diff(a,z,2)+sp.diff(a,r)/r)/a+sh**2/4+Q,
 'pp': (sp.diff(a,r,2)+sp.diff(a,z,2))/a-sh**2/4+Q,
 'zr': -sp.diff(a,r,z)/a-nf(sh)/2+sh*K,
}
idx={'n':0,'z':1,'r':2,'p':3}
for k,v in checks.items():
    i,j=idx[k[0]],idx[k[1]]
    print(k, sp.simplify(8*sp.pi*T[i,j]-v)==0)
# service-region Gaussian curvature convention: r-independent fields, p_r=-K_G/8pi
