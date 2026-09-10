# Finite work interface for the prepared active rail support

This investigation connects the selected electromagnetic delivery route to a
finite electrical work port. It retains the late non-live support interval,
connected pressure fluid, separate heat receiver, shared radial guide field,
and the archived charging schedule from the
[delivery study](POYNTING_WORK_DELIVERY.md). Its construction question is
whether a reversible work coupler can preserve the measured benefit while
providing finite matching, reaction, and storage duties.

## Registered calculations

The first calculation varies conversion efficiency on the existing finite
absorption solution with chi=100. Transport is linear in each prescribed
source: charging and its transparent carrier scale as 0.98/eta, while
electrical recovery scales as eta/0.98. The heat receiver is recomputed from
its proper-time energy balance for each efficiency. Guide allocation retains
the original electric floor, rate ceiling, and union of material and transport
sample positions. This produces a matched-load efficiency comparison on the
same material history.

An additional reflected-amplitude envelope measures the guide margin
required by a specified unwanted amplitude r. This envelope changes the
guide requirement by the factor

    k(r) = [(1+r)^2/v_d^2 - (1-r)^2]/2,

with v_d=0.5. It is a sensitivity of the guide allocation. Propagating a
reflected field requires its emission and boundary data; those data remain
separate from this envelope. The full matched-load tensors are compared only
at r=0. Break-even values refer to the previous formal enclosed-store
comparison and express selection margins.

The second calculation examines the electrical load itself. A small radial
capacitor cell of solid angle dOmega and coordinate length dx has

    Q_cell = sqrt(2 H_e) dOmega,
    C_cell = R^2 dOmega/(Gamma B dx),
    U_cell = H_e Gamma B dx dOmega/R^2,

where H_e=H-S is the retained electrical flux-energy. Along its material
worldline,

    dU_cell/dtau = V_cell dQ_cell/dtau - U_cell d(ln C_cell)/dtau.

The second term is the mechanical work of the changing cell geometry. It is
already part of the radial field's stress coupling to the rail. This identity
keeps electrical charging distinct from changes in field energy caused by
the scheduled geometry.

At a locally frozen capacitive port connected to a real line impedance Z,
incident and outgoing voltages obey a=(V+ZI)/2 and b=(V-ZI)/2. Therefore

    b/a = (1-Z I/V)/(1+Z I/V).

During charging, zero reflection requires Z=V/I. For fixed cell geometry,
this implies an exponentially increasing charge. The actual rail has a
changing capacitance and a prescribed charge history, so the inverse port
calculation measures the required impedance range and signed current. It
also measures the storage retained after guide sharing. A time-varying
matching network requires its own energy and force law.

## Literature basis

[Marini and colleagues](https://doi.org/10.1109/TAP.2022.3177571) demonstrate
temporary reactive-load matching with shaped excitation. The author's
[arXiv deposit](https://arxiv.org/abs/2502.03076) appeared in 2025; the paper
was published in 2022. Its transient storage and release provide a useful
capacitive-port control.

[Wenner and colleagues](https://doi.org/10.1103/PhysRevLett.112.210501)
demonstrate capture and release through an adjustable superconducting
resonator coupler. Their small-signal experiment establishes the physical
principle of reversible capture through controlled interference. The
required rail field strength, current, and supporting material remain
independent construction requirements.

[Mirmoosa and colleagues](https://arxiv.org/abs/1802.07719) derive matching
with time-varying reactances and explicitly identify energy exchange with the
modulation source. Consequently any rail adaptation includes the modulation
port alongside work input, electrical storage, and heat return.

## Evidence and decision

Numerical results and the construction decision follow the registered
calculations. Evidence is kept under data/finite_work_interface. The main
technical disclosure continues to contain the established design.
