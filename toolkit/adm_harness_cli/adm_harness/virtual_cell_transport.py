"""Joint necessary gate for two phase-volume cells and a common power port.

Each cell supplies (A/R^2,-A/R^2,0) by changing phase volume and flux. Its
material-frame power is A_t/(N R^2). Absorbed waves enter from the common
middle port; recovered waves return to that port. Their nonnegative causal
transport, conversion heat, and counter-current stress are counted jointly
with the adjustable A. The complementary tensor belongs to the registered
field/radiation/angular-membrane/rest cone. This supplies a finite transport
and tensor budget, leaving microscopic phase fronts and guide mechanics open.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix


def upwind_operator(velocities, dx):
    """Conservative first-order spatial advection with zero incoming data."""
    v = np.asarray(velocities)
    n = len(v)-1
    a = np.zeros((n, n))
    for face, speed in enumerate(v):
        upstream = face-1 if speed >= 0 else face
        if not 0 <= upstream < n:
            continue
        if face > 0: a[face-1, upstream] -= speed/dx
        if face < n: a[face, upstream] += speed/dx
    return a


class Rows:
    def __init__(self, columns):
        self.columns=columns; self.row=[]; self.col=[]; self.data=[]; self.rhs=[]

    def add(self, entries, rhs=0.):
        entries=[(int(k),float(v)) for k,v in entries if v != 0]
        scale=max([abs(float(rhs)),1e-10]+[abs(v) for unused,v in entries])
        row=len(self.rhs)
        for k,v in entries:
            self.row.append(row); self.col.append(k); self.data.append(v/scale)
        self.rhs.append(float(rhs)/scale)

    def matrix(self):
        return csr_matrix((self.data,(self.row,self.col)),shape=(len(self.rhs),self.columns))


def solve_pair(t, edges, target, nodes, mids, wave_geometry, *, efficiency=1.,
               interface_sigma=0., deadline=120.):
    """Minimize the added local density needed by an actuated cell pair.

`nodes/mids` contain radius, ell, lapse, gamma, v, b, D. `wave_geometry`
contains face speeds and gains for direction +1/-1 at panel midpoints.
interface_sigma is the constant surface energy of two angular end membranes
per cell, conservatively volume-averaged as 2*sigma/(ell*cell_width).
Absorption is solved backward with zero final/outgoing inventory; recovery
forward with zero initial/incoming inventory. Shared-port energies are paid.
"""
    t, edges, target=map(np.asarray,(t,edges,target))
    nt,nx=len(t),len(edges)-1
    if nx%2 or nx<4 or target.shape!=(3,nt,nx) or not 0<efficiency<=1:
        raise ValueError('two equally discretized cells, three target components, and valid efficiency required')
    dx=edges[1]-edges[0]
    if np.any(np.diff(t)<=0) or not np.allclose(np.diff(edges),dx) or interface_sigma<0:
        raise ValueError('ordered time, uniform space, and nonnegative interface energy required')
    count=nt*nx; panels=(nt-1)*nx
    A=np.arange(count).reshape(nt,nx)
    absorption=A+count; recovery=A+2*count; heat=A+3*count; counter=A+4*count
    positive=np.arange(panels).reshape(nt-1,nx)+5*count
    negative=positive+panels
    epsilon=5*count+2*panels; columns=epsilon+1
    eq,ub=Rows(columns),Rows(columns)
    direction=np.r_[-np.ones(nx//2),np.ones(nx//2)]
    volume=nodes['b']*nodes['radius']**2
    ca=nodes['gamma']**2*(1-direction*nodes['v'])**2/volume
    cr=nodes['gamma']**2*(1+direction*nodes['v'])**2/volume
    wall=2*interface_sigma/(nodes['ell']*(nx//2)*dx)
    rho,p,q=target
    for i in range(nt):
        for j in range(nx):
            a=A[i,j]; ya=absorption[i,j]; yr=recovery[i,j]; h=heat[i,j]; k=counter[i,j]
            invr2=1/nodes['radius'][i,j]**2; invd=1/nodes['D'][i,j]
            ub.add([(a,2*invr2),(h,invd),(epsilon,-1)],rho[i,j]-p[i,j]-2*q[i,j]-3*wall[i,j])
            ub.add([(a,2*invr2),(h,invd),(epsilon,-1)],rho[i,j]-p[i,j]+q[i,j])
            ub.add([(a,-invr2),(ya,3*ca[i,j]),(yr,3*cr[i,j]),(k,3),(h,invd),(epsilon,-1)],
                   rho[i,j]+2*p[i,j]+q[i,j])
            for sign in (1.,-1.):
                ub.add([(ya,sign*direction[j]*ca[i,j]),(yr,-sign*direction[j]*cr[i,j]),(k,-1)])
    for i,dt in enumerate(np.diff(t)):
        for j in range(nx):
            eq.add([(A[i+1,j],1),(A[i,j],-1),(positive[i,j],-1),(negative[i,j],1)])
            ell=mids['ell'][i,j]
            eq.add([(heat[i+1,j],1),(heat[i,j],-1),
                    (positive[i,j],-ell*(1/efficiency-1)),
                    (negative[i,j],-ell*(1-efficiency))])
        for half in (0,1):
            start=half*(nx//2); stop=start+nx//2
            for kind, ids, sign, increments in (
                    ('absorption',absorption,int(direction[start]),positive),
                    ('recovery',recovery,-int(direction[start]),negative)):
                faces=wave_geometry[sign]['faces'][i,start:stop+1]
                gain=wave_geometry[sign]['gain'][i,start:stop]
                back=kind=='absorption'
                operator=upwind_operator(-faces if back else faces,dx)
                matrix=np.eye(stop-start)-dt*operator+(dt if back else -dt)*np.diag(gain)
                if np.any(np.diag(matrix)<=0):
                    raise ValueError('refine temporal panels to resolve homogeneous wave growth')
                at=i if back else i+1; other=i+1 if back else i
                factor=(1/efficiency if back else efficiency)
                source=mids['b'][i,start:stop]/(1-sign*mids['v'][i,start:stop])*factor
                for local,j in enumerate(range(start,stop)):
                    nz=np.flatnonzero(matrix[local])
                    eq.add([(ids[at,start+k],matrix[local,k]) for k in nz]+
                           [(ids[other,j],-1),(increments[i,j],-source[local])])
    bounds=[(0.,None)]*columns
    for k in np.r_[absorption[-1],recovery[0],heat[0]]: bounds[int(k)]=(0.,0.)
    matrix_eq=eq.matrix(); rhs_eq=np.array(eq.rhs)
    matrix_ub=ub.matrix(); rhs_ub=np.array(ub.rhs)
    cost=np.zeros(columns); cost[epsilon]=1
    first=linprog(cost,A_eq=matrix_eq,b_eq=rhs_eq,A_ub=matrix_ub,b_ub=rhs_ub,
                  bounds=bounds,method='highs',options={'time_limit':deadline/2})
    if not first.success:
        return dict(success=False,status=int(first.status),message=first.message)
    optimum=float(first.x[epsilon])
    # At the optimal density allowance, minimize the travelling and thermal
    # inventory. This removes unconstrained simultaneous absorption/recovery.
    bounds[epsilon]=(0.,optimum+1e-9)
    cost[:]=0
    wt=np.r_[np.diff(t)[0]/2,(np.diff(t)[:-1]+np.diff(t)[1:])/2,np.diff(t)[-1]/2]
    weight=wt[:,None]*dx
    cost[absorption.ravel()]=(weight*ca).ravel()
    cost[recovery.ravel()]=(weight*cr).ravel()
    cost[heat.ravel()]=(weight/nodes['D']).ravel()
    cost[positive.ravel()]=1e-8; cost[negative.ravel()]=1e-8
    second=linprog(cost,A_eq=matrix_eq,b_eq=rhs_eq,A_ub=matrix_ub,b_ub=rhs_ub,
                   bounds=bounds,method='highs',options={'time_limit':deadline/2})
    r=second if second.success else first
    a=r.x[A]; ua=ca*r.x[absorption]; ur=cr*r.x[recovery]
    w=ua+ur; current=direction*(ua-ur); h=r.x[heat]/nodes['D']
    s=a/nodes['radius']**2
    from .field_membrane_support import minimum_energy
    exact=s+w+abs(current)+h+wall+minimum_energy(p+s-w-abs(current),q+wall)-rho
    eqerror=float(np.max(abs(matrix_eq@r.x-rhs_eq)))
    uberror=float(np.max(np.maximum(matrix_ub@r.x-rhs_ub,0)))
    return dict(success=eqerror<2e-7 and uberror<2e-7,
        minimum_added_density=optimum, exact_added_density=max(0.,float(exact.max())),
        scaled_equality_residual=eqerror, scaled_inequality_violation=uberror,
        second_optimization_success=bool(second.success),
        amplitude=a, absorption_state=r.x[absorption], recovery_state=r.x[recovery],
        absorption_rest=ua,recovery_rest=ur,heat_rest=h,wall_rest=wall,
        positive_increment=r.x[positive],negative_increment=r.x[negative],
        density_shortfall=exact,
        variables=columns,equalities=matrix_eq.shape[0],inequalities=matrix_ub.shape[0])
