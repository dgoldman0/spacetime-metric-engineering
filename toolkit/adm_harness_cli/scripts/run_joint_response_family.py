#!/usr/bin/env python3
"""Bounded joint repair through conservative linear response functions.

Twenty-seven controls alter prepared energy, angular response, and incoming
pressure. Every response is evolved by the same implicit conservation solver.
A small linear program counts all resulting stresses and optional end jackets.
"""
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
import json
import multiprocessing
import subprocess
import time as stopwatch

import numpy as np
from scipy.interpolate import BSpline
from scipy.sparse import csr_matrix,vstack

from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.graded_electrothermal import maximum_null
from adm_harness.monotone_field_allocation import monotone_allocation
from adm_harness.pressure_linked_storage import retained_coefficient_program
from adm_harness.source_ledger import sha256_file
from adm_harness.time_support_projection import evolve_support
from audit_joint_support import bilinear
from run_joint_backing_link import JointHistory
from run_joint_continuum_projection import fixed_coefficients,audit_projection
from run_joint_spacetime_support import assemble_fixed
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_response_family'
TARGET=BASE/'joint_support_smooth_allocation/n64_stride1_fraction0.9_pchip_cap0.2_states.npz'
NSPACE=6;NTIME=3;NPARAM=NSPACE+NSPACE*NTIME+NTIME


class ResponseFamily:
    def __init__(self,intervals=128,time_factor=1):
        self.h=JointHistory(32,8)
        self.h.allocation=monotone_allocation(self.h.knots,self.h.share_values)
        with np.load(TARGET) as z:self.reference={k:z[k] for k in z.files}
        native=self.h.reference.t
        self.t=native if time_factor==1 else np.unique(np.r_[native,(native[:-1]+native[1:])/2])
        self.x=np.linspace(self.h.knots[0],self.h.knots[-1],intervals+1)
        inner=np.linspace(self.x[0],self.x[-1],NSPACE-2)[1:-1]
        knots=np.r_[np.repeat(self.x[0],4),inner,np.repeat(self.x[-1],4)]
        self.spatial=BSpline(knots,np.eye(NSPACE),3,extrapolate=False)
        self.cache={}

    def time_basis(self,t):
        z=np.asarray(t)/self.t[-1]
        return np.array([(1-z)**2,2*z*(1-z),z*z]).T

    def energy_scale(self,t,x,c=None):
        if c is None:c=fixed_coefficients(self.h,t,x)
        g=self.h.reference.h.model.metric(float(self.t[0]),x)
        v=g.b*g.beta/g.alpha;ell0=g.b/np.sqrt(1-v*v)
        m0=np.interp(x,self.reference['x'],self.reference['support_energy'][0])
        return m0[None,:]*c['ell']/ell0[None,:]

    def angular_responses(self,t,x,c=None):
        r=self.reference
        q0=bilinear(r['t'],r['x'],r['angular_volume'],t,x)[0]
        out=np.zeros((len(t),len(x),NPARAM+1));out[...,0]=q0
        angular=(self.energy_scale(t,x,c)[:,:,None,None]*self.spatial(x)[None,:,:,None]*
                 self.time_basis(t)[:,None,None,:])
        out[...,1+NSPACE:1+NSPACE+NSPACE*NTIME]=angular.reshape(len(t),len(x),-1)
        return out

    def cached_coefficients(self,t,x,k):
        key=(len(t),len(x),float(t[0]),float(t[-1]),float(x[0]),float(x[-1]))
        if key not in self.cache:
            c=fixed_coefficients(self.h,t,x)
            self.cache[key]=(c,self.angular_responses(t,x,c),np.zeros_like(c['fixed_power']))
        c,q,zero=self.cache[key]
        result=dict(c);result['Q']=q[...,k]
        if k:result.update(fixed_force=zero,fixed_power=zero)
        return result

    def preparation(self):
        t,x,r=self.t,self.x,self.reference;c=fixed_coefficients(self.h,t,x)
        m0=np.interp(x,r['x'],r['support_energy'][0])
        initial=np.zeros((len(x),NPARAM+1));initial[:,0]=m0
        initial[:,1:1+NSPACE]=m0[:,None]*self.spatial(x)
        p,pt,unused=bilinear(r['t'],r['x'],r['radial_volume'],t,x)
        incoming=np.zeros((len(t),NPARAM+1));incoming[:,0]=p[:,-1]/c['D'][:,-1]
        rate=np.zeros((len(x),NPARAM+1));rate[:,0]=(pt[0]-c['volume_rate'][0]*p[0])/c['D'][0]
        offset=1+NSPACE+NSPACE*NTIME
        density=self.energy_scale(t,x,c)/c['D']
        incoming[:,offset:]=density[:,-1,None]*self.time_basis(t)
        psi=self.time_basis(t[:1])[0];dpsi=np.array([-2.,2.,0.])/t[-1]
        rate[:,offset:]=density[0,:,None]*(dpsi[None,:]-2*c['log_radius_t'][0,:,None]*psi[None,:])
        return initial,incoming,rate

    def build_responses(self):
        initial,incoming,rate=self.preparation()
        def run(k):
            r=evolve_support(self.t,self.x,lambda t,x:self.cached_coefficients(t,x,k),
                initial[:,k],incoming[:,k],rate[:,k],subpanels=max(1,128//(len(self.x)-1)))
            return r
        baseline=run(0)  # Fill the immutable geometry/quadrature cache first.
        with ThreadPoolExecutor(max_workers=4) as pool:results=[baseline,*list(pool.map(run,range(1,NPARAM+1)))]
        return dict(t=self.t,x=self.x,
            energy=np.stack([r['support_energy'] for r in results],axis=-1),
            pressure=np.stack([r['radial_pressure'] for r in results],axis=-1),
            angular=self.angular_responses(self.t,self.x),
            local_exchange=baseline['local_exchange'])

    def selected_coefficients(self,parameters,t,x):
        c=fixed_coefficients(self.h,t,x)
        c['Q']=self.angular_responses(t,x,c)@np.r_[1.,parameters]
        return c


def jacket_responses(t,c,pressure,electric,thermal,end,width,dimension):
    """Surface force and integrated work as affine functions of bulk controls."""
    j=(0,-1)[end];orientation=(-1.,1.)[end];nt=len(t)
    r=c['radius'][:,j];a=c['acceleration'][:,j];k=c['angular_gradient'][:,j]
    load=orientation*r[:,None]**2*pressure[:,j,:]
    load[:,0]+=orientation*r*r*(thermal[:,j]/(3*c['D'][:,j])-electric[:,j])
    ca=a/(2*k);cb=-load/(2*k[:,None])
    A=np.ones(nt);B=np.zeros_like(cb)
    for i,dr in enumerate(np.diff(np.log(r)),1):
        denominator=1+dr*ca[i]
        A[i]=A[i-1]*(1-dr*ca[i-1])/denominator
        B[i]=(B[i-1]*(1-dr*ca[i-1])-dr*(cb[i]+cb[i-1]))/denominator
    scale=max(float(np.max(abs(load[:,0])/(abs(a)+2*abs(k)))),1e-6)
    Y=np.zeros((nt,dimension+1));Y[:,:NPARAM+1]=B;Y[:,NPARAM+1+end]=scale*A
    Z=ca[:,None]*Y;Z[:,:NPARAM+1]+=cb
    return Y,Z,scale


def evaluate(spec):
    fraction,ends=spec;start=stopwatch.monotonic();f=ResponseFamily();h=f.h
    with np.load(OUTPUT/'responses.npz') as z:b={k:z[k] for k in z.files}
    t,x=b['t'],b['x'];c=fixed_coefficients(h,t,x);d=c['D']
    old=h.reference.h.state;u=bilinear(old['t'],old['x'],old['thermal'],t,x)[0]
    number=np.interp(x,old['x'],old['number'])
    field=bilinear(old['t'],old['x'],old['flux_energy'],t,x)[0]
    electric=(field-h.allocation(x)[0])/c['radius']**4
    dim=NPARAM+(2 if ends=='jackets' else 0);peak=dim
    m=b['energy']/d[:,:,None];p=b['pressure'];q=b['angular']/d[:,:,None]
    arrays=[];rhs=[]
    def add_affine(values,peak_coefficient=0.):
        flat=values.reshape(-1,values.shape[-1]);a=np.zeros((len(flat),dim+1))
        a[:,:flat.shape[1]-1]=flat[:,1:];a[:,-1]=peak_coefficient
        arrays.append(csr_matrix(a));rhs.append(-flat[:,0])
    for radial in (-1.,1.):
        for angular in (-1.,2.):add_affine(radial*p+angular*q-fraction*m)
    def null_values(z):
        rr=c['gamma']**2*(1-c['v']*z)**2;pr=c['gamma']**2*(c['v']-z)**2;pt=1-z*z
        a=rr[:,:,None]*m+pr[:,:,None]*p+pt*q
        a[...,0]+=(number+u)/d*rr+u/(3*d)*(pr+pt)
        return a
    for z in np.linspace(-1,1,7):add_affine(null_values(float(z)),-1.)
    jackets=[];width=.01
    if ends=='jackets':
        for end,j in enumerate((0,-1)):
            Y,Z,scale=jacket_responses(t,c,b['pressure'],electric,u,end,width,dim)
            jackets.append((Y,Z,scale))
            for sign in (-1.,1.):add_affine(sign*Z-fraction*Y)
            rho=Y/(c['D'][:,j,None]*width);pt=Z/(c['D'][:,j,None]*width)
            for z in np.linspace(-1,1,7):
                rr=c['gamma'][:,j]**2*(1-c['v'][:,j]*z)**2
                add_affine(rr[:,None]*rho+(1-z*z)*pt,-1.)
    A=vstack(arrays,format='csr');br=np.concatenate(rhs)
    cost=np.zeros(dim+1);cost[-1]=1.
    bounds=[(-5.,5.)]*NPARAM+([(0.,None)]*2 if jackets else [])+[(0.,None)]
    r=retained_coefficient_program(cost,method='highs-ipm',deadline=120.,A_ub=A,b_ub=br,bounds=bounds)
    label=f'fraction{fraction:g}_{ends}'
    s=dict(label=label,success=bool(r.success),status=int(r.status),message=r.message,
           controls=NPARAM,control_bounds=[-5.,5.],fraction=fraction,ends=ends,
           intervals=len(x)-1,time_nodes=len(t))
    if r.success:
        params=r.x[:NPARAM];coef=np.r_[1.,params]
        energy=b['energy']@coef;pressure=b['pressure']@coef;angular=b['angular']@coef
        tensor=anisotropic_moments((number+u+energy)/d,u/(3*d)+pressure,(u/3+angular)/d,c['v'])
        upper=float(maximum_null(tensor)[0].max())
        surface_energy=[];surface_stress=[]
        for end,(Y,Z,scale) in enumerate(jackets):
            y=Y@np.r_[1.,r.x[:-1]];zz=Z@np.r_[1.,r.x[:-1]];j=(0,-1)[end]
            surface_energy.append(y);surface_stress.append(zz)
            tt=anisotropic_moments(y/(d[:,j]*width),np.zeros(len(t)),zz/(d[:,j]*width),c['v'][:,j])
            upper=max(upper,float(maximum_null(tt)[0].max()))
        checked=r.x.copy();checked[-1]=max(upper,checked[-1])
        violation=float(np.maximum(A@checked-br,0).max())
        state=dict(t=t,x=x,support_energy=energy,radial_pressure=pressure,radial_volume=pressure*d,
                   angular_volume=angular,thermal=u,parameters=params,local_exchange=b['local_exchange'])
        proxy=SimpleNamespace(h=h,coefficients=lambda at,ax:f.selected_coefficients(params,at,ax))
        audit=audit_projection(proxy,state)
        s.update(audit,material_peak_lower=float(r.x[-1]),material_peak_upper=upper,
                 max_inequality_violation=violation,parameters=params.tolist(),
                 initial_support_rest=float(4*np.pi*np.trapezoid(energy[0],x)),
                 final_support_rest=float(4*np.pi*np.trapezoid(energy[-1],x)),
                 member_energy_admissible=audit['maximum_separate_member_density_shortfall']<1e-7,
                 constitutive_law_supplied=False,continuum_convergence_established=False)
        fixed,radial=assemble_fixed(h,t,x,c);phases=[]
        for i,time,demand in h.reference.phases:
            geom=np.array([np.interp(x,h.reference.x,row) for row in demand])
            value=maximum_null(tensor[:,i]+fixed[:,i]-geom)[0]
            phases.append(dict(time=time,required_negative_null=float(value.max())))
        s['bulk_phases']=phases
        if jackets:
            state['surface_energy']=np.array(surface_energy).T;state['surface_angular_stress']=np.array(surface_stress).T
            s['initial_surface_rest']=[float(4*np.pi(y[0])) for y in surface_energy]
            s['surface_coordinate_width']=width
            s['maximum_acceleration_thickness']=float(np.max(abs(c['acceleration'][:,[0,-1]])*c['ell'][:,[0,-1]]*width))
            s['finite_thickness_construction_supplied']=False
        if violation>2e-7:s['success']=False
        np.savez_compressed(OUTPUT/(label+'_states.npz'),**state)
    s['elapsed_seconds']=stopwatch.monotonic()-start
    write_json(OUTPUT/(label+'_summary.json'),s)
    print(label+': '+json.dumps({k:v for k,v in s.items() if k in
          ('success','message','material_peak_upper','weighted_force_residual','maximum_separate_member_density_shortfall')}),flush=True)
    return s


def main():
    if (OUTPUT/'manifest.json').exists():raise RuntimeError('preserve completed response-family evidence')
    previous=BASE/'joint_support_smooth_allocation/manifest.json'
    hashes=json.loads(previous.read_text())['input_sha256']
    for p in (Path(__file__),TARGET,previous,ROOT/'toolkit/adm_harness_cli/adm_harness/time_support_projection.py',
              ROOT/'toolkit/adm_harness_cli/scripts/run_joint_continuum_projection.py'):
        hashes[str(p.relative_to(ROOT))]=sha256_file(p)
    for p,expected in hashes.items():
        if sha256_file(ROOT/p)!=expected:raise RuntimeError('changed response-family input: '+p)
    OUTPUT.mkdir(exist_ok=True)
    if not (OUTPUT/'responses.npz').exists():
        f=ResponseFamily();responses=f.build_responses()
        np.savez_compressed(OUTPUT/'responses.npz',**responses)
        print('Built 28 conservative responses on the native time grid.',flush=True)
        del responses,f
    else:
        f=ResponseFamily();initial,incoming,rate=f.preparation()
        with np.load(OUTPUT/'responses.npz') as existing:
            if not np.array_equal(existing['t'],f.t) or not np.array_equal(existing['x'],f.x):
                raise RuntimeError('saved response grid differs from requested grid')
            for k in (0,NSPACE+2):
                checked=evolve_support(f.t,f.x,lambda t,x:f.cached_coefficients(t,x,k),
                    initial[:,k],incoming[:,k],rate[:,k],subpanels=1)
                np.testing.assert_allclose(checked['support_energy'],existing['energy'][...,k],rtol=1e-12,atol=1e-12)
                np.testing.assert_allclose(checked['radial_pressure'],existing['pressure'][...,k],rtol=1e-12,atol=1e-12)
        print('Verified saved base and angular response before resuming.',flush=True)
        del f
    with ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn')) as pool:
        results=list(pool.map(evaluate,[(.9,'exposed'),(.75,'exposed'),(.9,'jackets'),(.75,'jackets')]))
    write_json(OUTPUT/'summary.json',dict(cases=results))
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        input_sha256=hashes,output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':main()
