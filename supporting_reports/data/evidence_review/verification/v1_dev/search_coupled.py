"""Search for jets where the (n,r) discriminant is positive but the full (n,z,r) block is Type IV,
using the verified C0 table (A = 1)."""
import numpy as np
rng = np.random.default_rng(3)


def tensor(j):
    al, ar, az, at, arr, arz, azz = j['a'], j['ar'], j['az'], j['at'], j['arr'], j['arz'], j['azz']
    b, br, bz, bt, brr, brz, bzz, brt, bzt = j['b'], j['br'], j['bz'], j['bt'], j['brr'], j['brz'], j['bzz'], j['brt'], j['bzt']
    r = j['r']
    s = br / al
    K = bz / al
    s_r = brr / al - br * ar / al**2
    s_z = brz / al - br * az / al**2
    s_t = brt / al - br * at / al**2
    K_z = bzz / al - bz * az / al**2
    K_t = bzt / al - bz * at / al**2
    nK = (K_t - b * K_z) / al
    ns = (s_t - b * s_z) / al
    Q = nK - K**2
    T = np.zeros((4, 4))
    T[0, 0] = -s**2 / 4
    T[0, 1] = -(s + r * s_r) / (2 * r)
    # (1/2al^2) d_z(al^2 s) - K a_r/al
    T[0, 2] = (2 * al * az * s + al**2 * s_z) / (2 * al**2) - K * ar / al
    T[1, 1] = (arr + ar / r) / al - 3 * s**2 / 4
    T[2, 2] = (azz + ar / r) / al + s**2 / 4 + Q
    T[3, 3] = (arr + azz) / al - s**2 / 4 + Q
    T[1, 2] = -arz / al - ns / 2 + s * K
    T = T + np.triu(T, 1).T
    return T


def typ(T):
    M = np.diag([-1, 1, 1, 1]) @ T
    ev = np.linalg.eigvals(M)
    return 'IV' if np.max(np.abs(ev.imag)) > 1e-9 * np.max(np.abs(T)) else 'I?'


found = []
for k in range(200000):
    j = dict(a=3.0, ar=1.0, az=0.0, at=0.0, arr=0.0, arz=0.0, azz=0.0, b=0.0, br=rng.uniform(-1, 1) * 0.5,
             bz=rng.uniform(-1, 1), bt=0.0, brr=rng.uniform(-1, 1), brz=rng.uniform(-1, 1), bzz=0.0, brt=0.0,
             bzt=0.0, r=1.0)
    T = tensor(j)
    dnr = (T[0, 0] + T[2, 2])**2 - 4 * T[0, 2]**2
    dnz = (T[0, 0] + T[1, 1])**2 - 4 * T[0, 1]**2
    if dnr > 0.05 and typ(T) == 'IV' and dnz > 0:
        found.append((j, dnr, dnz))
        if len(found) > 5:
            break
for j, dnr, dnz in found:
    print({k: round(v, 3) for k, v in j.items() if v != 0}, 'dnr', round(dnr, 4), 'dnz', round(dnz, 4))
