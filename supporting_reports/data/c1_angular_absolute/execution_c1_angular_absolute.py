"""Covariant regulator controls for the absolute C1 angular scalar.

Finite regulator values are controls. Acceptance requires regulator, mode,
radial shooting and geometric-derivative convergence on the same state.
The reference subtraction retains the full native curvature counterterm.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import ctypes
import hashlib
import os
import subprocess
import tempfile

import numpy as np
from scipy.interpolate import CubicSpline, make_interp_spline
from scipy.special import factorial
from numpy.polynomial.legendre import leggauss

from .c1_angular_scalar import scalar_curvature
from .c1_signed_channels import einstein_source
from .semiclassical_joint import local_action_source


class NativeMetric:
    """Higher-order interpolation of the unchanged archived metric samples."""
    def __init__(self, coordinate, radius, lapse, radial_scale, order=7):
        self.coordinate = np.asarray(coordinate)
        self.radius, self.lapse, self.radial_scale = radius, lapse, radial_scale
        self.splines = [make_interp_spline(self.coordinate, np.log(v), k=order)
                        for v in (radius,lapse,radial_scale)]

    def jets(self, coordinate):
        x=np.asarray(coordinate,float)
        r,a,b=[np.exp(s(x)) for s in self.splines]
        rx,ax,bx=[s(x,1) for s in self.splines]
        rxx,axx=[s(x,2) for s in self.splines[:2]]
        return r,a,b,r*rx/b,r*(rxx+rx*rx-bx*rx)/b**2,ax/b,(axx-bx*ax)/b**2

    def proper_log_jets(self, coordinate):
        """Transform coordinate Taylor jets by D_l=exp(-log B) D_x."""
        jets=np.array([[s(coordinate,n) for n in range(5)] for s in self.splines],float)
        exponent=-jets[2]/factorial(np.arange(5))
        reciprocal=np.zeros(5); reciprocal[0]=np.exp(exponent[0])
        for n in range(1,5):
            reciprocal[n]=sum(k*exponent[k]*reciprocal[n-k] for k in range(1,n+1))/n
        result=[]
        for values in jets[:2]:
            polynomial=values/factorial(np.arange(5))
            row=[polynomial[0]]
            for n in range(1,5):
                polynomial=np.convolve(reciprocal,np.arange(1,len(polynomial))*polynomial[1:])[:5-n]
                row.append(polynomial[0])
            result.append(row)
        return np.array(result)


def conformal_log_source(log_radius,log_lapse):
    """Coefficient of sum(c_i log(m_i²/mu²)) in the heavy-field local action.

    The bulk a2 combination is (3 Ricci²-R²)/180 up to Euler and divergence
    terms; twice a2 multiplies the logarithm in the 1/(64 pi²) action.
    """
    return local_action_source(log_radius,log_lapse,np.zeros_like(log_radius),
        np.array([0.,0.,0.,0.,0.,-1/90,1/30])/(64*np.pi**2))[:3]


def conformal_anomaly(log_radius, log_lapse):
    """Bulk trace in the covariant PV scheme, including positive Box R."""
    from .semiclassical_joint import curvature
    r, r1, r2, r3, r4 = log_radius
    _, a1, a2, a3, a4 = log_lapse
    sections, _, _, ricci2 = curvature(log_radius, log_lapse)
    x,y,z,w = sections
    scalar_first = (-2*(a3+2*a1*a2)-4*(a2*r1+a1*r2)
                    -4*(r3+2*r1*r2)+2*(-2*r1*np.exp(-2*r)-2*r1*r2))
    scalar_second = (-2*(a4+2*a2*a2+2*a1*a3)
                     -4*(a3*r1+2*a2*r2+a1*r3)-4*(r4+2*r2*r2+2*r1*r3)
                     +2*((4*r1*r1-2*r2)*np.exp(-2*r)-2*r2*r2-2*r1*r3))
    box = scalar_second+(a1+2*r1)*scalar_first
    riemann2 = 4*(x*x+2*y*y+2*z*z+w*w)
    return (riemann2-ricci2+box)/(2880*np.pi**2)


@lru_cache(maxsize=1)
def radial_library():
    source=Path(__file__).with_name("c1_angular_absolute_kernel.c")
    identity=hashlib.sha256(source.read_bytes()).hexdigest()[:20]
    directory=Path(tempfile.gettempdir())/"c1-angular-absolute-kernels"
    directory.mkdir(exist_ok=True)
    output=directory/f"{identity}.so"
    if not output.exists():
        temporary=directory/f"{identity}-{os.getpid()}.so"
        subprocess.run(["cc","-O3","-std=c11","-fPIC","-shared",str(source),"-lm","-o",str(temporary)],
                       check=True,capture_output=True)
        os.replace(temporary,output)
    library=ctypes.CDLL(str(output))
    pointer=np.ctypeslib.ndpointer(dtype=np.float64,flags="C_CONTIGUOUS")
    integer=np.ctypeslib.ndpointer(dtype=np.int32,flags="C_CONTIGUOUS")
    for fn in (library.c1_pv_difference,library.c1_mass_difference):
        fn.argtypes=[pointer,ctypes.c_int,ctypes.c_double,ctypes.c_double,pointer,
            ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_int,pointer,integer,
            ctypes.c_double,ctypes.c_double,ctypes.c_double,pointer]
        fn.restype=ctypes.c_int
    return library


@dataclass
class AbsoluteComparison:
    chart: object
    domain: tuple
    probe: float
    proper_spacing: float=.01

    def __post_init__(self):
        lo,hi=self.domain
        if not lo < self.probe < hi or self.proper_spacing<=0:
            raise ValueError("interior probe and positive interpolation spacing required")
        x=self.chart.coordinate
        primitive=CubicSpline(x,self.chart.radial_scale).antiderivative()
        offset=float(primitive(self.probe))
        inverse=make_interp_spline(primitive(x)-offset,x,k=5)
        ends=primitive(np.array([lo,hi]))-offset
        points=int(np.ceil((ends[1]-ends[0])/self.proper_spacing))+1
        l=np.linspace(*ends,points)
        self.lower,self.upper=float(l[0]),float(l[-1])
        self.spacing=float(l[1]-l[0])
        self.cells=len(l)-1
        self.proper_of_coordinate=lambda coordinate: primitive(coordinate)-offset
        cx=np.clip(inverse(l),lo,hi)
        r,a,_,rp,rpp,ap,app=self.chart.jets(cx)
        r0,a0,_,rp0,_,ap0,_=self.chart.jets(np.array([self.probe]))
        self.radius=float(r0[0])
        geometric=rpp/r+app/2+ap*ap/4+ap*rp/r
        values=np.array([(float(a0[0])/a)**2,1/r**2,geometric+scalar_curvature(self.chart,cx)/6])
        self.coefficients=np.ascontiguousarray(np.stack([CubicSpline(l,v).c.T for v in values]))
        self.geometry=np.array([r0[0],rp0[0]/r0[0]+ap0[0]/2,rp0[0]/r0[0],ap0[0],
            scalar_curvature(self.chart,np.array([self.probe]))[0],
            *(8*np.pi*einstein_source(self.chart,np.array([self.probe]))[0])])

    def differences(self,frequencies,harmonics,scale,phase_step=.08,attenuation=40,
                    single_mass=False):
        w,j=np.broadcast_arrays(frequencies,harmonics)
        if (not np.all(np.isfinite(w)) or np.any(w<0) or not np.all(np.isfinite(j))
            or np.any(j<0) or np.any(j!=np.floor(j)) or not np.isfinite(scale)
            or scale<0 or (scale==0 and not single_mass) or phase_step<=0 or attenuation<=0):
            raise ValueError("finite nonnegative modes and positive regulator and controls required")
        shape=w.shape
        w=np.ascontiguousarray(w.ravel(),dtype=float)
        j=np.ascontiguousarray(j.ravel(),dtype=np.int32)
        output=np.empty((len(w),3))
        library=radial_library()
        method=library.c1_mass_difference if single_mass else library.c1_pv_difference
        code=method(self.coefficients,self.cells,self.lower,
            self.spacing,self.geometry,self.lower,self.upper,0.,len(w),w,j,
            scale,phase_step,attenuation,output)
        if code:
            raise RuntimeError(f"radial shooting failed at mode {code-1}")
        return output.reshape(*shape,3)


def integrate_comparison(problem, scale, angular_max, frequency_max,
                         frequency_order=16, phase_step=.08, attenuation=40):
    """Finite mode controls, retaining individual harmonic contributions."""
    nodes, weights = leggauss(frequency_order)
    edges = [0., .25]
    while edges[-1] < frequency_max:
        edges.append(min(frequency_max, 2*edges[-1]))
    w = np.concatenate([lo+(nodes+1)*(hi-lo)/2 for lo,hi in zip(edges[:-1],edges[1:])])
    measure = np.concatenate([weights*(hi-lo)/2 for lo,hi in zip(edges[:-1],edges[1:])])
    j = np.arange(angular_max+1)
    values = problem.differences(w[None,:], j[:,None], scale, phase_step, attenuation)
    harmonic = np.einsum('jwk,w->jk', values, measure)*(2*j[:,None]+1)/(4*np.pi**2)
    return dict(tensor=harmonic.sum(axis=0), harmonic_tensor=harmonic,
                frequency_nodes=len(w))


def cylinder_pv(radius,scale,mu_squared=1.,dps=55):
    """Independent analytic frequency integral and accelerated angular sum.

    Returns the unconverted one-field tensor after heavy bulk counterterms,
    together with the raw PV tensor. The field mass is zero; regulators have
    m_i²=i M² and weights (1,-3,3,-1).
    """
    import mpmath as mp
    with mp.workdps(dps):
        r,M,mu=map(mp.mpf,(radius,scale,mu_squared))
        weights=[1,-3,3,-1]
        beta=[mp.mpf(1)/12+r*r*i*M*M for i in range(4)]
        start=max(24,int(mp.ceil(3*mp.sqrt(max(beta)))))
        rho,pt=mp.mpf(0),mp.mpf(0)
        for j in range(start):
            v=mp.mpf(j)+mp.mpf(".5")
            a=sum(c*(v*v+b)*mp.log(v*v+b) for c,b in zip(weights,beta))
            b=sum(c*mp.log(v*v+b) for c,b in zip(weights,beta))
            rho-=v*a/(16*mp.pi**2*r**4)
            pt-=v*(v*v+beta[0])*b/(16*mp.pi**2*r**4)
        v=mp.mpf(start)+mp.mpf(".5")
        for k in range(3,35):
            moment=sum(c*b**k for c,b in zip(weights,beta))
            rho-=(-1)**k*moment*mp.zeta(2*k-3,v)/(16*mp.pi**2*r**4*k*(k-1))
            pt-=(-1)**(k+1)*moment*(mp.zeta(2*k-3,v)+beta[0]*mp.zeta(2*k-1,v))/(16*mp.pi**2*r**4*k)
        raw=[rho,-rho,pt]
        c0=sum(weights[i]*mp.log(i*M*M/mu) for i in range(1,4))
        c4=sum(weights[i]*(i*M*M)**2*(mp.log(i*M*M/mu)-mp.mpf("1.5")) for i in range(1,4))/(64*mp.pi**2)
        h=(4*(-mp.mpf(1)/90)+2*(mp.mpf(1)/30))/(64*mp.pi**2*r**4)
        renormalized=[rho-c4-c0*h,-rho+c4+c0*h,pt+c4-c0*h]
        return dict(raw_tensor=list(map(float,raw)),renormalized_tensor=list(map(float,renormalized)),
                    sum_start=start,log_coefficient=float(c0))


def cylinder_calibration(reference_radius, reference_log=1.):
    """Fix one finite curvature coupling once, for every native probe."""
    masses = np.array([16.,32.,64.])
    values = np.array([cylinder_pv(reference_radius,m)['renormalized_tensor'] for m in masses])
    limit = np.polynomial.polynomial.polyfit(masses**-2, values, 2)[0]
    k = 1/(2880*np.pi**2*reference_radius**4)
    return dict(finite_coefficient=float((-2*reference_log*k-limit[0])/k),
                reference_radius=reference_radius,reference_log=reference_log,
                masses=masses.tolist(),tensors=values.tolist(),limit=limit.tolist())


def calibrated_tensor(problem, difference, scale, calibration):
    """Absolute finite-regulator control, with exact cylinder limit inserted."""
    from .c1_angular_scalar import cylinder_tensor
    jets = problem.chart.proper_log_jets(problem.probe)
    h = conformal_log_source(*jets)
    k = 1/(2880*np.pi**2*problem.radius**4)
    hc = k*np.array([1.,-1.,1.])
    c0 = -np.log(scale*scale)+3*np.log(2.)-np.log(3.)
    baseline = cylinder_tensor(problem.radius,calibration['reference_radius'],
                               calibration['reference_log'])
    value = baseline+difference+(calibration['finite_coefficient']-c0)*(h-hc)
    return dict(tensor=value,correction=value-baseline,cylinder=baseline,
                log_source=h,anomaly=float(conformal_anomaly(*jets)))
