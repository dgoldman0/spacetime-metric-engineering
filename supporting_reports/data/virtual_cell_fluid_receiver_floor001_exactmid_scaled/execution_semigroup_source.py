"""Coherent phase cells with positive exponential transport and midpoint gates.

This alternate discretization integrates the frozen-panel finite-volume wave
operator exactly. One phase amplitude and one pair of conversion increments
serve each whole physical cell. Both endpoint and midpoint stresses are
constrained. Independent explicit replay still tests spatial and coefficient
discretization errors on the original active metric.
"""
import warnings

import numpy as np
from scipy.linalg import expm
from scipy.optimize import OptimizeWarning, linprog

from .virtual_cell_transport import Rows, upwind_operator


def transport_map(dt, faces, gain, source, dx, backwards=False, observable=None):
    """Positive homogeneous map and response to one panel's source increment."""
    n=len(gain)
    generator=upwind_operator(-faces if backwards else faces,dx)
    generator+=np.diag(-gain if backwards else gain)
    size=n+1+(observable is not None)
    block=np.zeros((size,size)); block[:n,:n]=dt*generator
    block[:n,n]=source
    if observable is not None:
        block[n+1,:n]=dt*np.asarray(observable)
    exponential=expm(block)
    if observable is not None:
        return (exponential[:n,:n],exponential[:n,n],
                exponential[n+1,:n],exponential[n+1,n])
    return exponential[:n,:n],exponential[:n,n]


def solve_pair(t, edges, target, nodes, mids, wave_geometry, *, efficiency=1.,
               interface_sigma=0., coherent_cells=True, return_heat=True,
               guide_drift=None, reservoir_eos=None, confine_reservoir=False,
               wave_envelope=False, matched_pair=False, thermal_eos=None,
               thermal_reference_density=None,
               receiver_reference=None,
               receiver_contact=None, split_receiver=False, target_budget_only=False,
               thermal_particle_number=None, maximize_thermal_floor=False,
               minimum_thermal_floor=None, midpoint_credited_target=None,
               solver_threads=None, solver_method=None, solver_crossover=None,
               solver_log=False, deadline=180.):
    """Frozen-panel transport with independently supplied available stresses.

    midpoint_credited_target, when supplied, is the COMPLETE available target
    at actual midpoint geometry, shape (3, nt-1, nx). The caller includes its
    chosen reserve and every reopened baseline fluid/receiver credit exactly
    once. The default remains the average of the credited endpoint targets.

    minimum_thermal_floor sets a fixed lower bound on U/(3*N_mass) at nodes
    and midpoints in direct-budget mode, using a single inventory optimization.
    maximize_thermal_floor retains the separate two-stage floor search.
    """
    if not coherent_cells or not return_heat:
        raise ValueError('exponential gate uses coherent cells and a heat-return stream')
    t,edges,target=map(np.asarray,(t,edges,target))
    nt,nx=len(t),len(edges)-1; halfnx=nx//2; dx=edges[1]-edges[0]
    if nx%2 or not 0<efficiency<=1 or interface_sigma<0:
        raise ValueError('two equal cells and physical conversion parameters required')
    guide=0. if guide_drift is None else .5*(guide_drift**-2-1)
    if guide_drift is not None and not 0<guide_drift<1:
        raise ValueError('guide drift fraction must be subluminal and positive')
    distributed=thermal_eos is not None
    if distributed and (thermal_eos!=1/3 or reservoir_eos is not None):
        raise ValueError('thermal_eos must be 1/3 and uses a separate distributed reservoir')
    if thermal_reference_density is not None:
        reference=np.asarray(thermal_reference_density,dtype=float)
        if (not distributed or reference.shape!=(nt,nx) or
                not np.all(np.isfinite(reference)) or np.any(reference<0)):
            raise ValueError('thermal_reference_density requires nonnegative finite thermal_eos=1/3 history')
        # Reopen the existing fluid thermal state. The caller's target excludes
        # that baseline fluid; its full stress is available exactly once.
        target=target+np.array([reference,reference/3,reference/3])
    receiver_reopened=receiver_reference is not None
    if receiver_reopened:
        if thermal_reference_density is None or len(receiver_reference)!=2:
            raise ValueError('receiver_reference requires existing fluid and (heat, rated capacity)')
        receiver_old,receiver_cap=map(np.asarray,receiver_reference)
        if (receiver_old.shape!=(nt,nx) or receiver_cap.shape!=(nx,) or
                not np.all(np.isfinite(receiver_old)) or not np.all(np.isfinite(receiver_cap)) or
                np.any(receiver_old<0) or np.any(receiver_cap<0) or
                np.any(receiver_old>receiver_cap+1e-10)):
            raise ValueError('receiver_reference requires finite heat within nonnegative rated capacity')
        # Only stored heat is reopened. Its fixed containment and cold fluid
        # mass retain their original allocation outside this target.
        target=target.copy();target[0]+=receiver_old/nodes['D']
    midpoint_target=(target[:,:-1]+target[:,1:])/2
    if midpoint_credited_target is not None:
        midpoint_target=np.asarray(midpoint_credited_target,dtype=float)
        if midpoint_target.shape!=(3,nt-1,nx) or not np.isfinite(midpoint_target).all():
            raise ValueError('midpoint_credited_target requires finite shape (3, nt-1, nx) including all baseline credits')
    if receiver_contact is not None:
        if not receiver_reopened or len(receiver_contact)!=3:
            raise ValueError('receiver_contact requires a reopened receiver and (loss, proper duration, turnover)')
        contact_loss,contact_duration,turnover=receiver_contact
        contact_loss,contact_duration=map(np.asarray,(contact_loss,contact_duration))
        if (contact_loss.shape!=(nt-1,nx) or contact_duration.shape!=contact_loss.shape or
                not np.isfinite(turnover) or turnover<=0 or np.any(contact_loss<0) or
                np.any(contact_duration<=0) or
                not np.isfinite(contact_loss).all() or not np.isfinite(contact_duration).all()):
            raise ValueError('receiver_contact requires finite nonnegative loss and positive duration/turnover')
    if split_receiver and receiver_contact is None:
        raise ValueError('split_receiver requires total contact loss and a finite donor comparison')
    if minimum_thermal_floor is not None:
        if (isinstance(minimum_thermal_floor,(bool,np.bool_)) or
                not isinstance(minimum_thermal_floor,(int,float,np.integer,np.floating)) or
                not np.isfinite(minimum_thermal_floor) or minimum_thermal_floor<0):
            raise ValueError('minimum_thermal_floor must be a finite nonnegative scalar or None')
        if maximize_thermal_floor:
            raise ValueError('minimum_thermal_floor and maximize_thermal_floor are mutually exclusive')
    thermal_floor_active=maximize_thermal_floor or minimum_thermal_floor is not None
    if thermal_floor_active:
        thermal_number=np.asarray(thermal_particle_number,float)
        if (not distributed or not target_budget_only or thermal_number.shape!=(nx,) or
                np.any(thermal_number<=0) or not np.isfinite(thermal_number).all()):
            raise ValueError('thermal floor requires a direct thermal budget and positive particle inventory')
    if solver_threads is not None and (
            isinstance(solver_threads,(bool,np.bool_)) or
            not isinstance(solver_threads,(int,np.integer)) or solver_threads<1):
        raise ValueError('solver_threads must be a positive integer or None')
    if solver_method is not None and solver_method not in ('highs-ipm','highs-ds'):
        raise ValueError('solver_method must be highs-ipm, highs-ds, or None')
    method=solver_method or ('highs-ds' if distributed else 'highs-ipm')
    if solver_crossover is not None and (
            not isinstance(solver_crossover,(bool,np.bool_)) or method!='highs-ipm'):
        raise ValueError('solver_crossover requires a boolean and highs-ipm')
    phase_groups=1 if matched_pair else 2
    A=np.arange(phase_groups*nt).reshape(nt,phase_groups)
    positive=np.arange(phase_groups*(nt-1)).reshape(nt-1,phase_groups)+phase_groups*nt
    negative=positive+phase_groups*(nt-1)
    if matched_pair:
        # One actual control variable serves both arms. Eliminating duplicate
        # equalities avoids a rank-deficient representation of this choice.
        A=np.repeat(A,2,axis=1)
        positive=np.repeat(positive,2,axis=1)
        negative=np.repeat(negative,2,axis=1)
    control_columns=phase_groups*(3*nt-2)
    absorption=np.arange(nt*nx).reshape(nt,nx)+control_columns
    recovery=absorption+nt*nx
    epsilon=control_columns+2*nt*nx
    if wave_envelope:
        ceiling_abs=np.arange((nt-1)*nx).reshape(nt-1,nx)+epsilon
        ceiling_rec=ceiling_abs+(nt-1)*nx
        epsilon+=2*(nt-1)*nx
    closed=reservoir_eos is not None
    if distributed:
        balanced_inventory=np.arange(nt*nx).reshape(nt,nx)+epsilon
        material_inventory=balanced_inventory+nt*nx
        epsilon+=2*nt*nx
        measure=(nodes['ell']*nodes['radius'])**2
        measure_mid=(mids['ell']*mids['radius'])**2
        thermal_weight=nodes['D']**(4/3)
        thermal_weight_mid=mids['D']**(4/3)
        reference_inventory=(thermal_weight*reference if thermal_reference_density is not None
                             else np.zeros((nt,nx)))
        reference_power_panel=(measure_mid/thermal_weight_mid)*np.diff(reference_inventory,axis=0)
        if receiver_reopened:
            receiver_inventory=np.arange(nt*nx).reshape(nt,nx)+epsilon
            epsilon+=nt*nx
            if split_receiver:
                hot_inventory=np.arange(nt*nx).reshape(nt,nx)+epsilon
                epsilon+=nt*nx
            receiver_weight=measure_mid/mids['D']
            receiver_reference_panel=receiver_weight*np.diff(receiver_old,axis=0)
    if confine_reservoir and (not closed or tuple(reservoir_eos)!=(1.,0.)):
        raise ValueError('axial confinement comparison is defined for the directed radiation store')
    if closed:
        wr,wt=map(float,reservoir_eos)
        if abs(wr)>1 or abs(wt)>1:
            raise ValueError('reservoir comparison requires dominant-energy pressure bounds')
        useful=np.arange(nt*nx).reshape(nt,nx)+epsilon
        store=np.arange(nt)+epsilon+nt*nx
        epsilon+=nt*nx+nt
        # Fixed material volume weights permit a favorable, perfectly mixed
        # shared inventory. Its local redistribution and supports are open.
        weights=nodes['D'][0]/(dx*nodes['D'][0].sum())
        density_weight=weights[None,:]/(4*np.pi*nodes['D'])
        density_weight_mid=weights[None,:]/(4*np.pi*mids['D'])
        work_rate=dx*np.sum(weights[None,:]*(wr*mids.get('log_ell_t',np.zeros_like(mids['D']))
                         +2*wt*mids.get('log_radius_t',np.zeros_like(mids['D']))),axis=1)
    if maximize_thermal_floor:
        temperature_column=epsilon;epsilon+=1
    columns=epsilon+1
    eq,ub=Rows(columns),Rows(columns)
    direction=np.r_[-np.ones(halfnx),np.ones(halfnx)]
    def factors(c):
        volume=c['b']*c['radius']**2
        return (c['gamma']**2*(1-direction*c['v'])**2/volume,
                c['gamma']**2*(1+direction*c['v'])**2/volume)
    ca,cr=factors(nodes); cam,crm=factors(mids)
    wall=2*interface_sigma/(nodes['ell']*halfnx*dx)
    wallm=2*interface_sigma/(mids['ell']*halfnx*dx)

    def material_terms(index,j,midpoint=False):
        """Independent local material/radiation inventories in the same frame."""
        if distributed:
            receiver=()
            if receiver_reopened:
                receiver=([(receiver_inventory[index,j],.5/mids['D'][index,j]),
                           (receiver_inventory[index+1,j],.5/mids['D'][index,j])] if midpoint
                          else [(receiver_inventory[index,j],1/nodes['D'][index,j])])
            if midpoint:
                return ([(material_inventory[index,j],.5/thermal_weight_mid[index,j]),
                         (material_inventory[index+1,j],.5/thermal_weight_mid[index,j])],
                        [(balanced_inventory[index,j],.5/measure_mid[index,j]),
                         (balanced_inventory[index+1,j],.5/measure_mid[index,j])],receiver)
            return ([(material_inventory[index,j],1/thermal_weight[index,j])],
                    [(balanced_inventory[index,j],1/measure[index,j])],receiver)
        if closed:
            if midpoint:
                return ([(store[index],.5*density_weight_mid[index,j]),
                         (store[index+1],.5*density_weight_mid[index,j])],())
            return ([(store[index],density_weight[index,j])],())
        return (),()

    def add_budget(amplitude,ua,ur,rho,p,q,radius,wall_density,buffer=(),balanced=(),receiver=()):
        scaled=lambda items,k:[(i,k*v) for i,v in items]
        aa=scaled(amplitude,1/radius**2)
        w1,w2,w3=(0,1,2) if distributed else ((1-wr-2*wt,1-wr+wt,1+2*wr+wt) if closed else (0,0,0))
        facets=[(scaled(aa,2)+scaled(buffer,w1),rho-p-2*q-3*wall_density),
                (scaled(aa,2)+scaled(buffer,w2),rho-p+q)]
        if distributed:
            facets.append((scaled(aa,-1)+scaled(balanced,3)+scaled(buffer,w3),rho+2*p+q))
            # W includes drive, useful return, heat return and complementary
            # photons. Nonnegative populations require both directional floors.
            ub.add(scaled(ua,2)+scaled(balanced,-1))
            ub.add(scaled(ur,2)+scaled(balanced,-1))
        else:
            facets.extend([(scaled(aa,-1)+scaled(ua,6)+scaled(buffer,w3),rho+2*p+q),
                           (scaled(aa,-1)+scaled(ur,6)+scaled(buffer,w3),rho+2*p+q)])
        for entries,rhs in facets:
            ub.add(entries+list(receiver)+[(epsilon,-1)],rhs)
        if guide:
            # Radial field already in the balanced core supplies a/2. Only
            # the remaining guide requirement constrains the auxiliary field.
            ub.add(scaled(aa,.5)+scaled(ua+ur,3*guide)+scaled(buffer,w2)+list(receiver)+[(epsilon,-1)],rho-p+q)

    def add_confinement(index,midpoint=False):
        # Generous integrated axial-restraint bound for a locally contained,
        # quasistatic directed radiation store. Reuse every available radial
        # tensile field, including the balanced core. Omit host and attachment
        # mass. The maximum auxiliary radial field is
        # (rho-p+q-2s-b)/3, hence integral(rho-p+q+s-3b) >= 0.
        c=mids if midpoint else nodes
        local_target=midpoint_target[:,index] if midpoint else target[:,index]
        measures=dx*c['D'][index]
        entries=[]
        for j,measure in enumerate(measures):
            amplitude=[(A[index,j//halfnx],.5),(A[index+1,j//halfnx],.5)] if midpoint else [(A[index,j//halfnx],1.)]
            buffer=[(store[index],.5*density_weight_mid[index,j]),
                    (store[index+1],.5*density_weight_mid[index,j])] if midpoint else [(store[index],density_weight[index,j])]
            entries.extend((k,-measure*v/c['radius'][index,j]**2) for k,v in amplitude)
            entries.extend((k,3*measure*v) for k,v in buffer)
        entries.append((epsilon,-measures.sum()))
        ub.add(entries,float(np.sum(measures*(local_target[0]-local_target[1]+local_target[2]))))

    for i in range(nt):
        for j in range(nx):
            add_budget([(A[i,j//halfnx],1)],[(absorption[i,j],ca[i,j])],
                [(recovery[i,j],cr[i,j])],*target[:,i,j],nodes['radius'][i,j],wall[i,j],
                *material_terms(i,j))
            if split_receiver:
                ub.add([(hot_inventory[i,j],1),(receiver_inventory[i,j],-1)])
                # Separately rated, insulated banks: max hot + max cold must
                # fit the old rating. Cold is monotone, so its final value is
                # its maximum. Fixed containment remains sufficient for both.
                ub.add([(hot_inventory[i,j],1),(receiver_inventory[-1,j],1),
                        (hot_inventory[-1,j],-1)],receiver_cap[j])
            if maximize_thermal_floor:
                ub.add([(temperature_column,3*thermal_number[j]*nodes['D'][i,j]**(1/3)),
                        (material_inventory[i,j],-1)])
            elif minimum_thermal_floor is not None:
                ub.add([(material_inventory[i,j],-1)],
                       -3*thermal_number[j]*nodes['D'][i,j]**(1/3)*minimum_thermal_floor)
        if confine_reservoir: add_confinement(i)
    operators=[]
    port_terms=[]
    for i,dt in enumerate(np.diff(t)):
        panel=[]
        incident=[]; returned=[]; total_return=[]
        for half in (0,1):
            start=half*halfnx; stop=start+halfnx; sl=slice(start,stop)
            if not matched_pair or half==0:
                eq.add([(A[i+1,half],1),(A[i,half],-1),(positive[i,half],-1),(negative[i,half],1)])
            pair={}
            for back,ids,sign in [(True,absorption,int(direction[start])),
                                  (False,recovery,-int(direction[start]))]:
                faces=wave_geometry[sign]['faces'][i,start:stop+1]
                gain=wave_geometry[sign]['gain'][i,sl]
                source=mids['b'][i,sl]/(1-sign*mids['v'][i,sl])
                if closed:
                    port_index=halfnx-1 if half==0 else 0
                    face_index=halfnx if half==0 else 0
                    port_v=.5*(mids['v'][i,halfnx-1]+mids['v'][i,halfnx])
                    boost=(1-sign*port_v)/np.sqrt(1-port_v*port_v)
                    observable=np.zeros(halfnx)
                    observable[port_index]=4*np.pi*abs(faces[face_index])*boost
                    mapped=transport_map(dt,faces,gain,source,dx,back,observable)
                    full=mapped[:2]; flux_row,flux_source=mapped[2:]
                    if back:
                        incident.extend((absorption[i+1,start+k],v) for k,v in enumerate(flux_row) if v)
                        incident.append((positive[i,half],flux_source/efficiency))
                    else:
                        returned.extend((useful[i,start+k],v) for k,v in enumerate(flux_row) if v)
                        returned.append((negative[i,half],efficiency*flux_source))
                        total_return.extend((recovery[i,start+k],v) for k,v in enumerate(flux_row) if v)
                        total_return.extend([(negative[i,half],flux_source),
                            (positive[i,half],(1/efficiency-1)*flux_source)])
                else:
                    full=transport_map(dt,faces,gain,source,dx,back)
                mid=transport_map(dt/2,faces,gain,source/2,dx,back)
                pair[back]=(full,mid)
                matrix,response=full
                at=i if back else i+1; other=i+1 if back else i
                if wave_envelope:
                    ceiling=ceiling_abs if back else ceiling_rec
                    generator=upwind_operator(-faces if back else faces,dx)
                    generator+=np.diag(-gain if back else gain)
                for local,j in enumerate(range(start,stop)):
                    items=[(ids[at,j],1)]+[(ids[other,start+k],-value)
                        for k,value in enumerate(matrix[local]) if value!=0]
                    if back:
                        items.append((positive[i,half],-response[local]/efficiency))
                    else:
                        items.extend([(negative[i,half],-response[local]),
                                      (positive[i,half],-response[local]*(1/efficiency-1))])
                    eq.add(items)
                    if wave_envelope:
                        # A positive supersolution bounds the whole frozen
                        # time interval, including unresolved transit peaks:
                        # z >= y(start), G z + source_rate <= 0.
                        ub.add([(ids[other,j],1),(ceiling[i,j],-1)])
                        envelope=[(ceiling[i,start+k],value)
                            for k,value in enumerate(generator[local]) if value]
                        if back:
                            envelope.append((positive[i,half],source[local]/(dt*efficiency)))
                        else:
                            envelope.extend([(negative[i,half],source[local]/dt),
                                (positive[i,half],source[local]*(1/efficiency-1)/dt)])
                        ub.add(envelope)
                    if closed and not back:
                        eq.add([(useful[i+1,j],1)]+[(useful[i,start+k],-value)
                            for k,value in enumerate(matrix[local]) if value!=0]
                            +[(negative[i,half],-response[local]*efficiency)])
            for local,j in enumerate(range(start,stop)):
                ma,sa=pair[True][1]; mr,sr=pair[False][1]
                ua=[(absorption[i+1,start+k],cam[i,j]*v) for k,v in enumerate(ma[local]) if v!=0]
                ua.append((positive[i,half],cam[i,j]*sa[local]/efficiency))
                ur=[(recovery[i,start+k],crm[i,j]*v) for k,v in enumerate(mr[local]) if v!=0]
                ur.extend([(negative[i,half],crm[i,j]*sr[local]),
                           (positive[i,half],crm[i,j]*sr[local]*(1/efficiency-1))])
                add_budget([(A[i,half],.5),(A[i+1,half],.5)],ua,ur,
                    *midpoint_target[:,i,j],mids['radius'][i,j],wallm[i,j],
                    *material_terms(i,j,True))
                if maximize_thermal_floor:
                    ub.add([(temperature_column,3*thermal_number[j]*mids['D'][i,j]**(1/3)),
                            (material_inventory[i,j],-.5),(material_inventory[i+1,j],-.5)])
                elif minimum_thermal_floor is not None:
                    ub.add([(material_inventory[i,j],-.5),(material_inventory[i+1,j],-.5)],
                           -3*thermal_number[j]*mids['D'][i,j]**(1/3)*minimum_thermal_floor)
                if wave_envelope:
                    for end in (i,i+1):
                        add_budget([(A[end,half],1.)],
                            [(ceiling_abs[i,j],ca[end,j])],[(ceiling_rec[i,j],cr[end,j])],
                            *target[:,end,j],nodes['radius'][end,j],wall[end,j],
                            *material_terms(end,j))
                    add_budget([(A[i,half],.5),(A[i+1,half],.5)],
                        [(ceiling_abs[i,j],cam[i,j])],[(ceiling_rec[i,j],crm[i,j])],
                        *midpoint_target[:,i,j],mids['radius'][i,j],wallm[i,j],
                        *material_terms(i,j,True))
            panel.append(pair)
        operators.append(panel)
        if distributed:
            for j in range(nx):
                half=j//halfnx;phi=mids['ell'][i,j]**2
                psi=measure_mid[i,j]/thermal_weight_mid[i,j]
                receiver=[];forcing=reference_power_panel[i,j]
                if receiver_reopened:
                    receiver=[(receiver_inventory[i+1,j],receiver_weight[i,j]),
                              (receiver_inventory[i,j],-receiver_weight[i,j])]
                    forcing+=receiver_reference_panel[i,j]
                eq.add([(balanced_inventory[i+1,j],1),(balanced_inventory[i,j],-1),
                    (A[i+1,half],phi),(A[i,half],-phi),
                    (material_inventory[i+1,j],psi),(material_inventory[i,j],-psi)]+receiver,forcing)
                if receiver_contact is not None:
                    # Total contact heat H=loss-DeltaZ. Bound the outgoing
                    # power by each donor's actual energy at both panel ends.
                    for end in (i,i+1):
                        rate=turnover*contact_duration[i,j]
                        ub.add([(receiver_inventory[i,j],1),
                                (receiver_inventory[i+1,j],-1),
                                (receiver_inventory[end,j],-rate)],-contact_loss[i,j])
                        ub.add([(receiver_inventory[i+1,j],1),
                                (receiver_inventory[i,j],-1),
                                (material_inventory[end,j],-rate/nodes['D'][end,j]**(1/3))],contact_loss[i,j])
                    if split_receiver:
                        dh=[(hot_inventory[i+1,j],1),(hot_inventory[i,j],-1)]
                        dc=[(receiver_inventory[i+1,j],1),(receiver_inventory[i,j],-1)]+[(k,-v) for k,v in dh]
                        ub.add(dh,contact_loss[i,j])  # Q_hot = loss-DeltaHot >= 0.
                        ub.add([(k,-v) for k,v in dc])  # Q_cold = DeltaCold >= 0.
                        for end in (i,i+1):
                            ub.add([(k,-v) for k,v in dh]+[(hot_inventory[end,j],-rate)],-contact_loss[i,j])
                            ub.add(dc+[(material_inventory[end,j],-rate/nodes['D'][end,j]**(1/3))])
        if confine_reservoir: add_confinement(i,True)
        if closed:
            eq.add([(store[i+1],1+dt*work_rate[i]/2),
                    (store[i],-1+dt*work_rate[i]/2)]+incident+[(k,-v) for k,v in returned])
            port_terms.append((incident,returned,total_return))
    bounds=[(0.,None)]*columns
    if receiver_reopened:
        for i in range(nt):
            for j in range(nx):bounds[int(receiver_inventory[i,j])]=(0.,float(receiver_cap[j]))
    for k in np.r_[absorption[-1],recovery[0]]: bounds[int(k)]=(0.,0.)
    if closed:
        for k in useful[0]: bounds[int(k)]=(0.,0.)
    ae,be=eq.matrix(),np.array(eq.rhs); au,bu=ub.matrix(),np.array(ub.rhs)
    inventory_cost=np.zeros(columns)
    time_weight=np.r_[np.diff(t)[0]/2,(np.diff(t)[:-1]+np.diff(t)[1:])/2,np.diff(t)[-1]/2]
    inventory_cost[absorption.ravel()]=(time_weight[:,None]*dx*nodes['D']*ca).ravel()
    inventory_cost[recovery.ravel()]=(time_weight[:,None]*dx*nodes['D']*cr).ravel()
    inventory_cost[positive.ravel()]=1e-9; inventory_cost[negative.ravel()]=1e-9
    if closed: inventory_cost[store]=time_weight/(4*np.pi)
    if distributed:
        inventory_cost[absorption.ravel()]=0.;inventory_cost[recovery.ravel()]=0.
        inventory_cost[balanced_inventory.ravel()]=(time_weight[:,None]*dx*nodes['D']/measure).ravel()
        inventory_cost[material_inventory.ravel()]=(time_weight[:,None]*dx*nodes['D']/thermal_weight).ravel()
        if receiver_reopened:
            inventory_cost[receiver_inventory.ravel()]=np.broadcast_to(time_weight[:,None]*dx,(nt,nx)).ravel()
    # The physical quadrature weights can be O(1e-9). Normalize this positive
    # linear objective without changing its minimizer or any constraint.
    inventory_cost_max=float(np.max(np.abs(inventory_cost)))
    inventory_cost_scale=1/inventory_cost_max if inventory_cost_max else 1.
    inventory_cost=inventory_cost*inventory_cost_scale
    cost=np.zeros(columns); cost[epsilon]=1
    if target_budget_only:
        bounds[epsilon]=(0.,0.);cost=inventory_cost
    if maximize_thermal_floor:
        cost=np.zeros(columns);cost[temperature_column]=-1
    options={'time_limit':deadline if target_budget_only and not maximize_thermal_floor else deadline/2,'primal_feasibility_tolerance':1e-9,
             'dual_feasibility_tolerance':1e-9,'ipm_optimality_tolerance':1e-10,
             'small_matrix_value':1e-12}
    if solver_threads is not None:options['threads']=int(solver_threads)
    if solver_crossover is not None:options['run_crossover']='on' if solver_crossover else 'off'
    if solver_log:options['disp']=True
    def optimize():
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore',message='Unrecognized options detected',category=OptimizeWarning)
            return linprog(cost,A_eq=ae,b_eq=be,A_ub=au,b_ub=bu,bounds=bounds,
                           method=method,options=options)
    first=optimize()
    if not first.success:
        return dict(success=False,status=int(first.status),message=first.message,solver_method=method,
                    solver_crossover=solver_crossover,solver_iterations=getattr(first,'nit',None),
                    crossover_iterations=getattr(first,'crossover_nit',None),
                    inventory_objective_scale=inventory_cost_scale,solver_matrix_drop_threshold=1e-12,
                    fixed_uniform_fluid_temperature_floor=minimum_thermal_floor,
                    explicit_credited_midpoint_target=midpoint_credited_target is not None,
                    target_budget_only=bool(target_budget_only))
    optimum=float(first.x[epsilon]); bounds[epsilon]=(0.,optimum+1e-10)
    if maximize_thermal_floor:
        maximum_floor=float(first.x[temperature_column])
        bounds[temperature_column]=(.99*maximum_floor,None)
        bounds[epsilon]=(0.,0.)
    cost=inventory_cost
    second=first if target_budget_only and not maximize_thermal_floor else optimize()
    r=second if second.success else first
    amplitude=np.repeat(r.x[A],halfnx,axis=1)
    plus=np.repeat(r.x[positive],halfnx,axis=1)
    minus=np.repeat(r.x[negative],halfnx,axis=1)
    ua=ca*r.x[absorption]; ur=cr*r.x[recovery]
    core=amplitude/nodes['radius']**2
    rho,p,q=target
    reservoir={}
    if maximize_thermal_floor:
        reservoir.update(maximum_uniform_fluid_temperature=maximum_floor,
            retained_uniform_fluid_temperature=float(r.x[temperature_column]),
            thermal_floor_retention_fraction=.99,
            temperature_convention='gamma-law U/(3*N_mass); microscopic caloric equation remains a material choice')
    elif minimum_thermal_floor is not None:
        observed_node=r.x[material_inventory]/(3*thermal_number*nodes['D']**(1/3))
        observed_mid=(r.x[material_inventory][:-1]+r.x[material_inventory][1:])/(6*thermal_number*mids['D']**(1/3))
        reservoir.update(fixed_uniform_fluid_temperature_floor=float(minimum_thermal_floor),
            retained_uniform_fluid_temperature=float(minimum_thermal_floor),
            minimum_observed_fluid_temperature=float(min(observed_node.min(),observed_mid.min())),
            thermal_floor_violation=float(max(0.,minimum_thermal_floor-observed_node.min(),
                                              minimum_thermal_floor-observed_mid.min())),
            temperature_convention='gamma-law U/(3*N_mass); microscopic caloric equation remains a material choice')
    if wave_envelope:
        reservoir.update(absorption_panel_ceiling=r.x[ceiling_abs],
            recovery_panel_ceiling=r.x[ceiling_rec],
            within_panel_wave_bound=True,
            within_panel_wave_bound_scope='positive supersolution for frozen-panel finite-volume geometry')
    confinement_added_density=0.
    if distributed:
        u=r.x[balanced_inventory];k_state=r.x[material_inventory]
        buffer_density=k_state/thermal_weight;balanced_density=u/measure
        rho=rho-buffer_density;p=p-buffer_density/3;q=q-buffer_density/3
        phase_weight=mids['ell']**2;exchange_weight=measure_mid/thermal_weight_mid
        thermal_balance=(np.diff(u,axis=0)+phase_weight*np.diff(amplitude,axis=0)
                         +exchange_weight*np.diff(k_state,axis=0)-reference_power_panel)
        if receiver_reopened:
            receiver_energy=r.x[receiver_inventory];receiver_density=receiver_energy/nodes['D']
            rho=rho-receiver_density
            thermal_balance+=receiver_weight*np.diff(receiver_energy,axis=0)-receiver_reference_panel
            reservoir.update(receiver_thermal_energy=receiver_energy,receiver_rest=receiver_density,
                receiver_reference_energy=receiver_old,receiver_rated_capacity=receiver_cap,
                receiver_reference_power_panel=receiver_reference_panel,
                receiver_contact_energy_to_fluid=-np.diff(receiver_energy-receiver_old,axis=0),
                receiver_capacity_violation=float(np.maximum(receiver_energy-receiver_cap,0).max()),
                receiver_containment_energy_reallocated=False,
                receiver_contact_temperature_and_rate_supplied=False)
            if receiver_contact is not None:
                H=contact_loss-np.diff(receiver_energy,axis=0)
                fluid_energy=k_state/nodes['D']**(1/3)
                donor_violation=np.maximum.reduce([
                    H-turnover*contact_duration*receiver_energy[:-1],
                    H-turnover*contact_duration*receiver_energy[1:],
                    -H-turnover*contact_duration*fluid_energy[:-1],
                    -H-turnover*contact_duration*fluid_energy[1:]])
                reservoir.update(receiver_total_contact_panel_heat=H,
                    receiver_converter_loss_panel=contact_loss,
                    receiver_contact_proper_duration=contact_duration,
                    receiver_donor_turnover=float(turnover),
                    receiver_donor_energy_violation=float(np.maximum(donor_violation,0).max()))
                if split_receiver:
                    hot=r.x[hot_inventory];cold=receiver_energy-hot
                    qhot=contact_loss-np.diff(hot,axis=0);qcold=np.diff(cold,axis=0)
                    split_violation=np.maximum.reduce([
                        qhot-turnover*contact_duration*hot[:-1],
                        qhot-turnover*contact_duration*hot[1:],
                        qcold-turnover*contact_duration*fluid_energy[:-1],
                        qcold-turnover*contact_duration*fluid_energy[1:]])
                    reservoir.update(receiver_hot_energy=hot,receiver_cold_energy=cold,
                        receiver_hot_contact_panel_heat=qhot,receiver_cold_contact_panel_heat=qcold,
                        receiver_hot_rated_capacity=hot.max(axis=0),receiver_cold_rated_capacity=cold.max(axis=0),
                        receiver_split_rating_violation=float(np.maximum(hot.max(axis=0)+cold.max(axis=0)-receiver_cap,0).max()),
                        receiver_split_donor_violation=float(np.maximum(split_violation,0).max()),
                        receiver_split_direction_violation=float(max(0.,-qhot.min(),-qcold.min())),
                        receiver_split_contact_identity=float(abs(qhot-qcold-H).max()),
                        receiver_two_separately_rated_banks=True)
        floor_violation=np.maximum(2*np.maximum(ua,ur)-balanced_density,0.)
        reservoir.update(thermal_eos=float(thermal_eos),thermal_inventory=k_state,
            thermal_reservoir_rest=buffer_density,balanced_radiation_inventory=u,
            balanced_radiation_rest=balanced_density,
            counterstream_rest=balanced_density-ua-ur,
            thermal_exchange_balance_residual=float(abs(thermal_balance).max()),
            thermal_exchange_panel_residual=thermal_balance,
            maximum_balanced_wave_floor_violation=float(floor_violation.max()),
            distributed_thermal_inventory_jointly_optimized=True,
            existing_thermal_state_reallocated=thermal_reference_density is not None,
            thermal_reference_inventory=reference_inventory,
            thermal_reference_power_panel=reference_power_panel,
            thermal_inventory_increment=k_state-reference_inventory,
            thermal_force_and_opacity_supplied=False,
            thermal_exchange_scope='piecewise-linear A,K and frozen-panel geometry; midpoint U equals midpoint K divided by D_mid^(1/3); changing-geometry reconstruction remains independent')
    if closed:
        buffer_density=r.x[store,None]*density_weight
        # Use the reduced target so the same facets independently reconstruct
        # the total required density, including the optimized buffer tensor.
        eos_r,eos_t=map(float,reservoir_eos)
        rho=rho-buffer_density; p=p-eos_r*buffer_density; q=q-eos_t*buffer_density
        port_in=np.array([sum(v*r.x[k] for k,v in a) for a,b,c in port_terms])
        port_out=np.array([sum(v*r.x[k] for k,v in b) for a,b,c in port_terms])
        port_total=np.array([sum(v*r.x[k] for k,v in c) for a,b,c in port_terms])
        geometric_work=np.diff(t)*work_rate*(r.x[store][:-1]+r.x[store][1:])/2
        reservoir.update(reservoir_energy=r.x[store],reservoir_rest=buffer_density,
            reservoir_incident_panel_energy=port_in,reservoir_recovered_work_panel_energy=port_out,
            reservoir_exported_heat_panel_energy=port_total-port_out,
            reservoir_geometric_work_panel_energy=geometric_work,
            useful_return_state=r.x[useful],
            reservoir_eos=list(reservoir_eos),shared_reservoir_jointly_optimized=True,
            reservoir_initial_energy=float(r.x[store][0]),reservoir_final_energy=float(r.x[store][-1]),
            reservoir_balance_residual=float(abs(np.diff(r.x[store])+geometric_work+port_in-port_out).max()),
            reservoir_distribution='fixed material weights; perfectly mixed energy; redistribution stress omitted',
            reservoir_heat_reconverted_to_work=False,reservoir_confinement_supplied=False)
        if confine_reservoir:
            original_rho,original_p,original_q=target
            available=(original_rho-original_p+original_q+core-3*buffer_density)/3
            integrated=4*np.pi*dx*np.sum(nodes['D']*available,axis=1)
            confinement_added_density=max(0.,float(np.max(-3*integrated/(4*np.pi*dx*np.sum(nodes['D'],axis=1)))))
            reservoir.update(integrated_axial_restraint_gate=True,
                confinement_added_density=confinement_added_density,
                reservoir_minimum_integrated_axial_tension_margin=float(integrated.min()),
                reservoir_axial_tension_margin=integrated,
                reservoir_confinement_model='locally contained quasistatic store; all radial core and auxiliary fields available; host and attachment mass omitted')
    if distributed:
        shortfall=np.maximum.reduce([p+2*q+2*core+3*wall,p-q+2*core,
            -2*p-q-core+3*balanced_density])-rho
    else:
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
        solver_method=method,
        solver_crossover=solver_crossover,solver_iterations=getattr(r,'nit',None),
        crossover_iterations=getattr(r,'crossover_nit',None),
        inventory_objective_scale=inventory_cost_scale,solver_matrix_drop_threshold=1e-12,
        target_budget_only=bool(target_budget_only),
        explicit_credited_midpoint_target=midpoint_credited_target is not None,
        minimum_added_density=optimum,exact_added_density=max(confinement_added_density,0.,float(shortfall.max())),
        scaled_equality_residual=eqerror,scaled_inequality_violation=uberror,
        second_optimization_success=None if target_budget_only and not maximize_thermal_floor else bool(second.success),
        inventory_minimization_success=bool(second.success),
        matched_pair_phase_history=bool(matched_pair),
        transport_method='positive matrix exponential with node and midpoint budgets',
        guide_drift_bound=guide_drift,guide_field_reused_from_core_and_auxiliary=True,
        amplitude=amplitude,absorption_state=r.x[absorption],recovery_state=r.x[recovery],
        absorption_rest=ua,recovery_rest=ur,heat_rest=np.zeros_like(ua),wall_rest=wall,
        thermal_return_state=thermal,thermal_return_rest=cr*thermal,
        positive_increment=plus,negative_increment=minus,density_shortfall=shortfall,
        variables=columns,equalities=ae.shape[0],inequalities=au.shape[0],**reservoir)
