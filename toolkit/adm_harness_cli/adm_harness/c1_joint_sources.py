"""Small source libraries with complete tensors and explicit force exchange.

The angular-ring candidate is a leading 1+1 conformal-channel construction
on closed great circles, plus a positive-tension carrier. Its microscopic
confinement, stability and ordinary support law remain physical requirements.
"""
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix

from .c1_signed_channels import channel_tensor, dec_projections


PROJECTION_NAMES = ('rho_plus_pr', 'rho_minus_pr', 'rho_plus_pt', 'rho_minus_pt')
RADIAL_ZONES = ((0,0,8),(0,8,22),(0,22,32),(1,0,8),(1,24,32))


def compact_population(coordinate, domain, taper=.15):
    """Fixed C2 density profile; taper is specified in the retained coordinate."""
    x=np.asarray(coordinate,float);lo,hi=domain
    if not lo<hi or not 0<taper<(hi-lo)/2:
        raise ValueError('ordered domain and a resolved positive taper required')
    t=np.clip(np.minimum(x-lo,hi-x)/taper,0.,1.)
    return t**3*(10+t*(-15+6*t))


def angular_rings(chart, coordinate, charge_density, tension_per_charge, eta):
    """Closed angular CFT loops and Nambu-type carrier, averaged over angles.

    charge_density = c * loops per proper radial length.
    tension_per_charge = renormalized physical line tension / central charge.
    E_Q=-c/(12 R), E_carrier=2*pi*mu*R for each loop.
    Tensor components are (rho,pr,pt); radial forces are on each sector.
    """
    x,n=np.broadcast_arrays(np.asarray(coordinate,float),np.asarray(charge_density,float))
    if (not np.isfinite(n).all() or np.any(n<0) or not np.isfinite(tension_per_charge)
            or tension_per_charge<0 or not np.isfinite(eta) or eta<=0):
        raise ValueError('nonnegative finite population/tension and positive eta required')
    r,_,_,rp,_,ap,_=chart.jets(x)
    q=eta*n/(48*np.pi*r**3)
    u=eta*tension_per_charge*n/(2*r)
    quantum=q[...,None]*np.array([-1.,0.,-.5])
    carrier=u[...,None]*np.array([1.,0.,-.5])
    fq=-q*(ap-rp/r)
    fc=u*(ap+rp/r)
    return dict(quantum=quantum,carrier=carrier,total=quantum+carrier,
        quantum_force=fq,carrier_force=fc,force_on_additional_support=-fq-fc,
        carrier_over_quantum=24*np.pi*tension_per_charge*r*r)


def radial_columns(chart, coordinate, row, eta, mode, charge_unit=1e6):
    """One law, with declared fixed-shape or independent population controls."""
    x=np.asarray(coordinate,float);columns=[];counts=[];labels=[]
    if mode=='zones':
        for module,lower,upper in RADIAL_ZONES:
            part=row['partitions'][module];ends=np.asarray(part['coordinate'])
            columns.append(channel_tensor(chart,x,ends[lower:upper+1],
                part['optical_lengths'][lower:upper],strength=eta*charge_unit))
            counts.append(float(upper-lower));labels.append(f'radial_module_{module}_uniform_cells_{lower}_{upper}')
        return np.stack(columns,axis=1),np.array(counts),labels
    for module,(part,old) in enumerate(zip(row['partitions'],row['central_charge_per_compartment'])):
        ends=np.asarray(part['coordinate']);old=np.asarray(old)
        single=channel_tensor(chart,x,ends,part['optical_lengths'],strength=eta)
        index=np.clip(np.searchsorted(ends,x,side='right')-1,0,len(old)-1)
        if mode=='module_scales':
            columns.append(single*old[index,None]);counts.append(float(old.sum()/charge_unit))
            labels.append(f'radial_module_{module}_retained_shape')
        elif mode=='compartments':
            for compartment in range(len(old)):
                columns.append(single*(index==compartment)[:,None]*charge_unit)
                counts.append(1.);labels.append(f'radial_module_{module}_cell_{compartment}')
        else:
            raise ValueError('module_scales, compartments or zones required')
    return np.stack(columns,axis=1),np.array(counts),labels


def joint_cone(target, columns, inventory_weights=None, component_envelopes=None, reserve=0.):
    """Necessary sampled DEC remainder, with fixed complete source tensors."""
    target=np.asarray(target,float);columns=np.asarray(columns,float)
    if (target.ndim!=2 or target.shape[1]!=3 or columns.ndim!=3
            or columns.shape[0]!=len(target) or columns.shape[2]!=3
            or not np.isfinite(target).all() or not np.isfinite(columns).all()):
        raise ValueError('finite aligned target and source columns required')
    n=columns.shape[1]
    if not np.isfinite(reserve) or reserve<0:
        raise ValueError('finite nonnegative margin reserve required')
    if n==0:
        margins=dec_projections(target)
        return dict(feasible=bool(np.all(margins>=reserve)),source_columns=0,
                    physical_material_supplied=False,minimum_margin=float(margins.min()),
                    coefficients=[],active_columns=[],inventory_proxy=0.,material=target.tolist())
    matrix=dec_projections(columns).transpose(0,2,1).reshape(-1,n)
    envelope=np.zeros(columns.shape[:2]) if component_envelopes is None else np.asarray(component_envelopes,float)
    if envelope.shape!=columns.shape[:2] or not np.isfinite(envelope).all() or np.any(envelope<0):
        raise ValueError('aligned nonnegative component envelopes required')
    matrix+=np.repeat(2*envelope[:,None,:],4,axis=1).reshape(-1,n)
    bound=dec_projections(target).ravel()-reserve
    direct=np.flatnonzero((bound<0)&np.all(matrix>=0,axis=1))
    record=dict(feasible=False,source_columns=n,physical_material_supplied=False)
    if len(direct):
        i=int(direct[np.argmin(bound[direct])])
        record['direct_witness']=dict(sample=i//4,projection=PROJECTION_NAMES[i%4],
            required=float(bound[i]),all_source_projections=matrix[i].tolist())
    cost=np.ones(n) if inventory_weights is None else np.asarray(inventory_weights,float)
    if cost.shape!=(n,) or np.any(cost<=0) or not np.isfinite(cost).all():
        raise ValueError('positive finite inventory weights required')
    scale=np.maximum(np.maximum(abs(matrix).max(axis=1),abs(bound)),1e-12)
    solution=linprog(cost,A_ub=csr_matrix(matrix/scale[:,None]),b_ub=bound/scale,
                     bounds=(0,None),method='highs',options={
                     'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    record.update(solver_status=int(solution.status),solver_message=solution.message)
    if solution.success:
        supplied=np.einsum('nsc,s->nc',columns,solution.x)
        material=target-supplied
        record.update(feasible=True,coefficients=solution.x.tolist(),inventory_proxy=float(solution.fun),
            active_columns=np.flatnonzero(solution.x>1e-8).tolist(),
            minimum_margin=float(dec_projections(material).min()),
            maximum_scaled_violation=float(np.max(np.maximum(matrix@solution.x-bound,0)/scale)),
            minimum_margin_after_envelope=float((dec_projections(material)-2*(envelope@solution.x)[:,None]).min()),
            material=material.tolist())
    return record


def required_extra_projection(target, supplied):
    """Negative entries are remaining duties, not independently supplied fields."""
    return np.minimum(dec_projections(np.asarray(target)-np.asarray(supplied)),0.)
