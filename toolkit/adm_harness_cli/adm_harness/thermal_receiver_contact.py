"""Passive contact screens for a fixed-volume photon receiver and gamma fluid.

The receiver's rated energy capacity is distinct from its caloric equation.
Here T_receiver**4=coefficient*Z and T_fluid=U/(3*number). The contact uses
total receiver-to-fluid power, including the original transfer duties.
"""
import numpy as np


def photon_contact_interval(power, fluid_energy, receiver_energy, number, *,
                            relative_power_tolerance=1e-8, absolute_power_tolerance=1e-10):
    """Constant positive temperature coefficients admitting passive transfer.

    Positive power requires coefficient*Z > T_fluid**4; negative power
    requires the opposite strict inequality. Zero contact is allowed at any
    temperature difference. These are sample-wise conditions; a panel audit
    needs an independent check for unresolved internal reversals.
    """
    power,fluid_energy,receiver_energy=np.broadcast_arrays(
        np.asarray(power,float),fluid_energy,receiver_energy)
    number=np.asarray(number,float)
    if (power.ndim!=2 or number.shape!=(power.shape[1],) or np.any(number<=0) or
            np.any(fluid_energy < -1e-9) or np.any(receiver_energy < -1e-9) or
            not all(np.isfinite(v).all() for v in (power,fluid_energy,receiver_energy,number))):
        raise ValueError('finite time-position histories and positive conserved particle numbers required')
    fluid=np.maximum(fluid_energy,0)/(3*number)
    receiver=np.maximum(receiver_energy,0)
    tolerance=np.maximum(absolute_power_tolerance,
                         relative_power_tolerance*np.max(abs(power),axis=0))
    positive=power>tolerance;negative=power<-tolerance
    fourth=fluid**4
    ratio=np.divide(fourth,receiver,out=np.full_like(fourth,np.inf),where=receiver>0)
    lower=np.max(np.where(positive,ratio,0.),axis=0)
    upper=np.min(np.where(negative&(receiver>0),ratio,np.inf),axis=0)
    zero_hot=(receiver==0)&positive
    zero_cold=(receiver==0)&(fluid==0)&negative
    blocked=np.any(zero_hot|zero_cold,axis=0)
    compatible=(lower<upper)&(upper>0)&np.isfinite(lower)&~blocked
    return dict(lower=lower,upper=upper,compatible=compatible,
        positive=positive,negative=negative,ratio=ratio,fluid_temperature=fluid,
        zero_energy_positive_outflow=zero_hot,zero_temperatures_nonzero_contact=zero_cold,
        power_tolerance=tolerance,
        lower_witness=np.argmax(np.where(positive,ratio,-1.),axis=0),
        upper_witness=np.argmin(np.where(negative&(receiver>0),ratio,np.inf),axis=0))
