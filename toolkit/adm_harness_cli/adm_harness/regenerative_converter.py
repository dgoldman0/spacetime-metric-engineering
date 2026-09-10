"""Finite local work/heat inventories for the active rail converter screen.

The port laws preserve an archived field/fluid history. Compact, internally
balanced cells supply an optimistic averaged tensor; their supporting mass
and the force needed to hold their prescribed worldlines are counted
separately. A remaining endpoint tensor must supply transport and reaction.
"""
from __future__ import annotations

import numpy as np


def conversion_ports(charging, endpoint_net, *, efficiency=1., recovery=0.):
    """Rest power densities, positive into the named receiving subsystem.

Field discharge fraction `recovery` returns electrical energy to the bank;
the remainder heats the pressure fluid. Converter losses enter the separate
thermal receiver. `endpoint_heat` is heat entering the pressure fluid.
"""
    charging, endpoint_net, recovery = np.broadcast_arrays(
        np.asarray(charging, dtype=float), endpoint_net, recovery)
    if (not 0 < efficiency <= 1 or not np.isfinite(efficiency)
            or np.any((recovery < 0) | (recovery > 1))
            or not all(np.isfinite(v).all() for v in (charging, endpoint_net, recovery))):
        raise ValueError('finite powers, 0 < efficiency <= 1 and 0 <= recovery <= 1 required')
    positive, negative = np.maximum(charging, 0.), np.maximum(-charging, 0.)
    recovered = recovery*negative
    work = positive/efficiency-efficiency*recovered
    loss = (1/efficiency-1)*positive+(1-efficiency)*recovered
    heat = endpoint_net-positive+recovered
    return dict(bank_output=work, endpoint_heat=heat,
                receiver_input=-heat+loss, converter_loss=loss,
                recovered_work=efficiency*recovered,
                local_discharge_heat=negative-recovered)


def proper_prefix(times, proper_weight, power):
    """Integrate local rest power with N_lapse D ds per material label.

Inputs are interval midpoint values, with power constant in this quadrature
representation. Spatial integration uses 4 pi dx outside this function.
"""
    times = np.asarray(times, dtype=float)
    weight, power = np.broadcast_arrays(np.asarray(proper_weight, dtype=float), power)
    if (times.ndim != 1 or len(times) < 2 or np.any(np.diff(times) <= 0)
            or not np.isfinite(times).all() or power.ndim != 2
            or power.shape[0] != len(times)-1 or np.any(weight <= 0)
            or not np.isfinite(weight).all() or not np.isfinite(power).all()):
        raise ValueError('ordered times and finite interval-by-position proper powers required')
    increments = np.diff(times)[:, None]*weight*power
    return np.concatenate((np.zeros((1, power.shape[1])), np.cumsum(increments, axis=0)))


def finite_local_stores(times, proper_weight, bank_output, receiver_input, *, voltage_fraction=.5):
    """Smallest capacities for a specified local work/heat history.

Each bank has fixed capacitance, V_min/V_max = voltage_fraction, and zero
external electrical feed during the patch. Each thermal receiver has a
nonnegative energy inventory and zero external heat export during the patch.
The chosen initial states realize both minimum capacities exactly.
"""
    if not 0 <= voltage_fraction < 1 or not np.isfinite(voltage_fraction):
        raise ValueError('0 <= minimum voltage fraction < 1 required')
    withdrawal = proper_prefix(times, proper_weight, bank_output)
    received = proper_prefix(times, proper_weight, receiver_input)
    bank_capacity = np.ptp(withdrawal, axis=0)/(1-voltage_fraction**2)
    bank_initial = withdrawal.max(axis=0)+voltage_fraction**2*bank_capacity
    heat_initial = -received.min(axis=0)
    return dict(bank_capacity=bank_capacity, bank_initial=bank_initial,
                bank=bank_initial[None, :]-withdrawal,
                heat_capacity=np.ptp(received, axis=0), heat_initial=heat_initial,
                heat=heat_initial[None, :]+received,
                withdrawal=withdrawal, received=received)


def work_reserve_lower_bound(times, proper_weight, charging, *, efficiency=1., voltage_fraction=.5):
    """Necessary local initial work and rated capacity under ANY recovery control.

Recovering every available discharge minimizes every cumulative withdrawal.
Every admissible recovery policy therefore needs at least its largest positive
prefix as initial work, and that prefix/(1-V_min^2/V_max^2) as rated capacity.
This bound grants a massless converter and arbitrary heat return.
"""
    if not 0 <= voltage_fraction < 1 or not np.isfinite(voltage_fraction):
        raise ValueError('0 <= minimum voltage fraction < 1 required')
    port = conversion_ports(charging, np.zeros_like(charging), efficiency=efficiency, recovery=1.)
    prefix = proper_prefix(times, proper_weight, port['bank_output'])
    initial = prefix.max(axis=0)
    return dict(initial_work=initial, bank_capacity=initial/(1-voltage_fraction**2))


def compact_cell_moments(energy_per_label, coefficients):
    """Averaged T for locally equilibrated, internally supported small cells.

Includes the energy of internal fields, thermal contents AND their walls in
energy_per_label. Leading integrated internal stresses cancel in the local
small-cell limit. This effective dust tensor still needs external acceleration
force rho*a and a physical cell/transport realization.
"""
    energy, volume, gamma, velocity = np.broadcast_arrays(
        energy_per_label, coefficients['rest_volume'],
        coefficients['gamma'], coefficients['v'])
    if (np.any(energy < -1e-12) or np.any(volume <= 0)
            or not all(np.isfinite(v).all() for v in (energy, volume, gamma, velocity))):
        raise ValueError('nonnegative finite cell energy and positive volume required')
    normal = energy/volume*gamma**2
    return np.array([normal, normal*velocity**2, normal*velocity, np.zeros_like(normal)])


def isotropic_wall_energy(bank_capacity, heat_capacity):
    """Optimistic DEC trace bound for separate isotropic EM/radiation cells.

Their contents have integrated spatial trace equal to their energy. A wall
obeying |p_i| <= rho has |trace p| <= 3 rho, so a static closed cell requires
wall energy >= maximum stored energy/3. Saturation is a necessary lower
bound, with no elastic law or attainable material implied.
"""
    bank, heat = np.broadcast_arrays(bank_capacity, heat_capacity)
    if not np.isfinite(bank).all() or not np.isfinite(heat).all() or np.any(bank < 0) or np.any(heat < 0):
        raise ValueError('finite nonnegative capacities required')
    return (bank+heat)/3
