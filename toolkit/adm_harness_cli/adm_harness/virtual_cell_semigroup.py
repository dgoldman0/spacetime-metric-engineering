"""Coherent phase cells with positive exponential transport and midpoint gates.

This alternate discretization integrates the frozen-panel finite-volume wave
operator exactly. One phase amplitude and one pair of conversion increments
serve each whole physical cell. Both endpoint and midpoint stresses are
constrained. Independent explicit replay still tests spatial and coefficient
discretization errors on the original active metric.
"""
import numpy as np
from scipy.linalg import expm
from scipy.optimize import linprog

from .virtual_cell_transport import Rows, upwind_operator


def transport_map(dt, faces, gain, source, dx, backwards=False):
    """Positive homogeneous map and response to one panel's source increment."""
    n=len(gain)
    generator=upwind_operator(-faces if backwards else faces,dx)
    generator+=np.diag(-gain if backwards else gain)
    block=np.zeros((n+1,n+1)); block[:n,:n]=dt*generator
    block[:n,n]=source
    exponential=expm(block)
    return exponential[:n,:n],exponential[:n,n]


def solve_pair(t, edges, target, nodes, mids, wave_geometry, *, efficiency=1.,
               interface_sigma=0., coherent_cells=True, return_heat=True,
               guide_drift=None, deadline=180.):
    if not coherent_cells or not return_heat:
        raise ValueError('exponential gate uses coherent cells and a heat-return stream')
    t,edges,target=map(np.asarray,(t,edges,target))
    nt,nx=len(t),len(edges)-1; halfnx=nx//2; dx=edges[1]-edges[0]
    if nx%2 or not 0<efficiency<=1 or interface_sigma<0:
        raise ValueError('two equal cells and physical conversion parameters required')
    guide=0. if guide_drift is None else .5*(guide_drift**-2-1)
    if guide_drift is not None and not 0<guide_drift<1:
        raise ValueError('guide drift fraction must be subluminal and positive')
    A=np.arange(2*nt).reshape(nt,2)
    positive=np.arange(2*(nt-1)).reshape(nt-1,2)+2*nt
    negative=positive+2*(nt-1)
    absorption=np.arange(nt*nx).reshape(nt,nx)+6*nt-4
    recovery=absorption+nt*nx
    epsilon=6*nt-4+2*nt*nx; columns=epsilon+1
    eq,ub=Rows(columns),Rows(columns)
    direction=np.r_[-np.ones(halfnx),np.ones(halfnx)]
    def factors(c):
        volume=c['b']*c['radius']**2
        return (c['gamma']**2*(1-direction*c['v'])**2/volume,
                c['gamma']**2*(1+direction*c['v'])**2/volume)
    ca,cr=factors(nodes); cam,crm=factors(mids)
    wall=2*interface_sigma/(nodes['ell']*halfnx*dx)
    wallm=2*interface_sigma/(mids['ell']*halfnx*dx)

    def add_budget(amplitude,ua,ur,rho,p,q,radius,wall_density):
        scaled=lambda items,k:[(i,k*v) for i,v in items]
        aa=scaled(amplitude,1/radius**2)
        for entries,rhs in [(scaled(aa,2),rho-p-2*q-3*wall_density),
                            (scaled(aa,2),rho-p+q),
                            (scaled(aa,-1)+scaled(ua,6),rho+2*p+q),
                            (scaled(aa,-1)+scaled(ur,6),rho+2*p+q)]:
            ub.add(entries+[(epsilon,-1)],rhs)
        if guide:
            # Radial field already in the balanced core supplies a/2. Only
            # the remaining guide requirement constrains the auxiliary field.
            ub.add(scaled(aa,.5)+scaled(ua+ur,3*guide)+[(epsilon,-1)],rho-p+q)

    for i in range(nt):
        for j in range(nx):
            add_budget([(A[i,j//halfnx],1)],[(absorption[i,j],ca[i,j])],
                [(recovery[i,j],cr[i,j])],*target[:,i,j],nodes['radius'][i,j],wall[i,j])
    operators=[]
    for i,dt in enumerate(np.diff(t)):
        panel=[]
        for half in (0,1):
            start=half*halfnx; stop=start+halfnx; sl=slice(start,stop)
            eq.add([(A[i+1,half],1),(A[i,half],-1),(positive[i,half],-1),(negative[i,half],1)])
            pair={}
            for back,ids,sign in [(True,absorption,int(direction[start])),
                                  (False,recovery,-int(direction[start]))]:
                faces=wave_geometry[sign]['faces'][i,start:stop+1]
                gain=wave_geometry[sign]['gain'][i,sl]
                source=mids['b'][i,sl]/(1-sign*mids['v'][i,sl])
                full=transport_map(dt,faces,gain,source,dx,back)
                mid=transport_map(dt/2,faces,gain,source/2,dx,back)
                pair[back]=(full,mid)
                matrix,response=full
                at=i if back else i+1; other=i+1 if back else i
                for local,j in enumerate(range(start,stop)):
                    items=[(ids[at,j],1)]+[(ids[other,start+k],-value)
                        for k,value in enumerate(matrix[local]) if value!=0]
                    if back:
                        items.append((positive[i,half],-response[local]/efficiency))
                    else:
                        items.extend([(negative[i,half],-response[local]),
                                      (positive[i,half],-response[local]*(1/efficiency-1))])
                    eq.add(items)
            for local,j in enumerate(range(start,stop)):
                ma,sa=pair[True][1]; mr,sr=pair[False][1]
                ua=[(absorption[i+1,start+k],cam[i,j]*v) for k,v in enumerate(ma[local]) if v!=0]
                ua.append((positive[i,half],cam[i,j]*sa[local]/efficiency))
                ur=[(recovery[i,start+k],crm[i,j]*v) for k,v in enumerate(mr[local]) if v!=0]
                ur.extend([(negative[i,half],crm[i,j]*sr[local]),
                           (positive[i,half],crm[i,j]*sr[local]*(1/efficiency-1))])
                add_budget([(A[i,half],.5),(A[i+1,half],.5)],ua,ur,
                    *(target[:,i,j]+target[:,i+1,j])/2,mids['radius'][i,j],wallm[i,j])
            panel.append(pair)
        operators.append(panel)
    bounds=[(0.,None)]*columns
    for k in np.r_[absorption[-1],recovery[0]]: bounds[int(k)]=(0.,0.)
    ae,be=eq.matrix(),np.array(eq.rhs); au,bu=ub.matrix(),np.array(ub.rhs)
    cost=np.zeros(columns); cost[epsilon]=1
    options={'time_limit':deadline/2,'primal_feasibility_tolerance':1e-9,
             'dual_feasibility_tolerance':1e-9,'ipm_optimality_tolerance':1e-10}
    first=linprog(cost,A_eq=ae,b_eq=be,A_ub=au,b_ub=bu,bounds=bounds,method='highs-ipm',options=options)
    if not first.success:
        return dict(success=False,status=int(first.status),message=first.message)
    optimum=float(first.x[epsilon]); bounds[epsilon]=(0.,optimum+1e-10)
    cost[:]=0
    wt=np.r_[np.diff(t)[0]/2,(np.diff(t)[:-1]+np.diff(t)[1:])/2,np.diff(t)[-1]/2]
    cost[absorption.ravel()]=(wt[:,None]*dx*nodes['D']*ca).ravel()
    cost[recovery.ravel()]=(wt[:,None]*dx*nodes['D']*cr).ravel()
    cost[positive.ravel()]=1e-9; cost[negative.ravel()]=1e-9
    second=linprog(cost,A_eq=ae,b_eq=be,A_ub=au,b_ub=bu,bounds=bounds,method='highs-ipm',options=options)
    r=second if second.success else first
    amplitude=np.repeat(r.x[A],halfnx,axis=1)
    plus=np.repeat(r.x[positive],halfnx,axis=1)
    minus=np.repeat(r.x[negative],halfnx,axis=1)
    ua=ca*r.x[absorption]; ur=cr*r.x[recovery]
    core=amplitude/nodes['radius']**2
    rho,p,q=target
    shortfall=np.maximum.reduce([p+2*q+2*core+3*wall,p-q+2*core,
        -2*p-q-core+6*ua,-2*p-q-core+6*ur])-rho
    if guide:
        shortfall=np.maximum(shortfall,p-q+.5*core+3*guide*(ua+ur)-rho)
    thermal=np.zeros((nt,nx))
    for i in range(nt-1):
        for half in (0,1):
            sl=slice(half*halfnx,(half+1)*halfnx)
            matrix,response=operators[i][half][False][0]
            loss=(1/efficiency-1)*r.x[positive[i,half]]+(1-efficiency)*r.x[negative[i,half]]
            thermal[i+1,sl]=matrix@thermal[i,sl]+response*loss
    eqerror=float(abs(ae@r.x-be).max()); uberror=float(np.maximum(au@r.x-bu,0).max())
    return dict(success=eqerror<2e-7 and uberror<2e-7,
        minimum_added_density=optimum,exact_added_density=max(0.,float(shortfall.max())),
        scaled_equality_residual=eqerror,scaled_inequality_violation=uberror,
        second_optimization_success=bool(second.success),
        transport_method='positive matrix exponential with node and midpoint budgets',
        guide_drift_bound=guide_drift,guide_field_reused_from_core_and_auxiliary=True,
        amplitude=amplitude,absorption_state=r.x[absorption],recovery_state=r.x[recovery],
        absorption_rest=ua,recovery_rest=ur,heat_rest=np.zeros_like(ua),wall_rest=wall,
        thermal_return_state=thermal,thermal_return_rest=cr*thermal,
        positive_increment=plus,negative_increment=minus,density_shortfall=shortfall,
        variables=columns,equalities=ae.shape[0],inequalities=au.shape[0])
