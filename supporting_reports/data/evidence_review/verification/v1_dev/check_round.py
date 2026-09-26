import numpy as np
from search_coupled import tensor, typ
for br, bz, brr, brz in [(-0.15, 0.45, -0.85, 0.75), (-0.5, 0.05, -0.6, 0.5), (-0.25, -0.45, -0.7, 0.3)]:
    j = dict(a=3.0, ar=1.0, az=0.0, at=0.0, arr=0.0, arz=0.0, azz=0.0, b=0.0, br=br, bz=bz, bt=0.0, brr=brr, brz=brz, bzz=0.0, brt=0.0, bzt=0.0, r=1.0)
    T = tensor(j)
    dnr = (T[0,0]+T[2,2])**2 - 4*T[0,2]**2; dnz = (T[0,0]+T[1,1])**2 - 4*T[0,1]**2
    M = np.diag([-1,1,1,1]) @ T
    print(br, bz, brr, brz, 'dnr', round(dnr,4), 'dnz', round(dnz,4), typ(T), np.round(np.linalg.eigvals(M),4), 'env ratio 2r|bz|/a', 2*abs(bz)/3)
