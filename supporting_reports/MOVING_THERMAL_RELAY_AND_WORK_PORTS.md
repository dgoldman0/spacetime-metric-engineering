# Moving thermal relay and work ports

A common radial trajectory gives the paired thermal relay explicit finite
photon paths, variable arrival times and matched bath injection. Separate
source guides, a central mixer and destination collectors carry the local
reactions. Opposed radial photon actuators supply their incremental radial
work through additional finite leads. The selected construction counts
both populations of flight photons.

## Annular geometry and arrival clocks

One opposed rotor pair occupies annular source/bath planes at
\(z=\pm L\). A separate annular mixer lies at \(z=0\). All three
guide surfaces follow the prescribed radius \(R(t)\), with radial speed
\(u(t)\) and zero angular velocity. The rotor material retains its
opposed tangential velocities. Each axial route stays at fixed azimuth;
its radial direction follows from the future receiving surface.

For one leg, emission and arrival obey

\[
t_a-t_e=\sqrt{L^2+[R(t_a)-R(t_e)]^2},\qquad
n_r=\frac{R(t_a)-R(t_e)}{t_a-t_e}.
\]

If \(|u|\le v_*<1\), the arrival is unique and

\[
L\le t_a-t_e\le\gamma_*L,\qquad |n_r|\le v_*,\qquad
J\equiv\frac{dt_a}{dt_e}
=\frac{1-n_ru(t_e)}{1-n_ru(t_a)}.
\]

Ballistic propagation therefore converts departure power \(P_e\) into
arrival power \(P_e/J\). Both members of an opposed pair share this
arrival map. The optical commands and aiming angles are prescribed
feedforward functions, consistent with the existing scheduled ports.

The retained comparison uses \(L=1/128\) and \(v_*=0.00905\).
Its complete thermal route delay lies between \(0.015625\) and
\(0.015625639903\). Uniform radial motion has delay
\(2\gamma_uL\); changes in radial velocity vary the delay.

## Thermal turns, mixing and recoil

The [paired emission law](PAIRED_THERMAL_EXCHANGE_INTERFACES.md) supplies
source power

\[
P_{\sigma\epsilon}(t)
=\frac{1+\sigma\epsilon j(t)}2Q_0(t),
\qquad \sigma,\epsilon\in\{-1,+1\}.
\]

Here \(Q_0\) is the material-rest heat power of one rotor, \(\sigma\)
labels the opposed rotors and \(\epsilon\) labels the eventual
tangential bath direction. Incoming thermal rays at the source guides
have radial cosine \(u\). The two direction channels remain distinct
through 50:50 mixing.

A radially moving elastic turn multiplies photon energy by

\[
A=\frac{1-u n_{{\rm in},r}}{1-u n_{{\rm out},r}}.
\]

Writing \(n_1,n_2\) for the two leg directions and
\(u_0,u_1,u_2\) for the velocities at their successive events gives

\[
A_s=\frac{1-u_0^2}{1-u_0n_1},\quad
A_m=\frac{1-u_1n_1}{1-u_1n_2},\quad
A_d=\frac{1-u_2n_2}{1-u_2^2}.
\]

The destination turn restores radial cosine \(u_2\) and tangential
cosine \(\epsilon\sqrt{1-u_2^2}\). Each destination receives

\[
P_{\delta\epsilon}(t_2)
=\frac12\sum_\sigma P_{\sigma\epsilon}(t_0)
\frac{A_sA_mA_d}{J_1J_2}.
\]

The common factors preserve equal arriving counterstreams at each local
bath. This conclusion uses paired source symmetry and the full retarded
path, including the moving collection event.

Guide recoil is the incoming minus outgoing photon four-force. It obeys
\(F_g^0=uF_g^r\). With \(G=-F_g^0\) denoting work delivered to
photons, the thermal flight inventory satisfies

\[
\dot W=Q_e-Q_a+G_s+G_m+G_d.
\]

The archive retains all three guide forces separately. In particular,
the source guides receive the opposed tangential impulses. Their
mechanical connection carries this torque between spatially separated
hosts. Radial work is only one part of that reaction duty.

## Selected radial work-photon route

For each guide stage, an additional reflecting facet receives the radial
force \(F=-F_g^r\). Two opposed optical ports select the required force
sign \(s=\operatorname{sign}F\). Powers crossing the moving facet are

\[
P_{\rm in}=\frac{|F|}{2}(1+su),\qquad
P_{\rm out}=\frac{|F|}{2}(1-su).
\]

Consequently the actuator supplies force
\(s(P_{\rm in}+P_{\rm out})=F\), work
\(P_{\rm in}-P_{\rm out}=Fu=G\), and optical encounter exposure
\(P_{\rm in}+P_{\rm out}=|F|\). A held force retains optical
throughput even when its mechanical work vanishes.

The fixed radial source/return ports lie at \(R_{\rm ref}\mp g_0\).
For side \(s\), define
\(g_s(t)=g_0+s[R(t)-R_{\rm ref}]\). A facet event at time \(t\)
connects to remote emission and reception at

\[
t_e=t-g_s(t),\qquad t_r=t+g_s(t),
\]

with remote powers

\[
P_{\rm emit}(t_e)=\frac{P_{\rm in}(t)}{1-su(t)},\qquad
P_{\rm return}(t_r)=\frac{P_{\rm out}(t)}{1+su(t)}.
\]

These monotone maps determine the exact retarded work commands. The
additional photon inventory \(V\), including both travel directions,
obeys

\[
\dot V=P_{\rm remote}-G,\qquad
P_{\rm remote}=\sum(P_{\rm emit}-P_{\rm return}).
\]

The code also retains the stationary ports' radial reactions. Combining
thermal and actuator photons eliminates the intermediate guide work:

\[
\boxed{\dot W_{\rm total}=Q_e-Q_a+P_{\rm remote}},\qquad
W_{\rm total}=W+V.
\]

If \(q_{\rm net}=q_{\rm rotor\ port}+P_{\rm remote}\), the
rotor excluding flight photons receives
\(q_r=q_{\rm net}-\dot W_{\rm total}\). Heat production depends on
the actual rotor-port power. The difference between that power and
\(q_{\rm net}\) is retained in the remote-port bounds below.

Guide rest mass and acceleration belong to the guide hosts. The radial
actuator cancels the incremental thermal recoil while those hosts follow
their assigned trajectory. Their axial and torsional support remains a
separate material load.

## Uniform bounds and reaction-port comparison

Set \(r=(1+v_*^2)/(1-v_*^2)\). Each thermal turn and each arrival
Jacobian lies between \(1/r\) and \(r\). Thus

\[
\sum_k\|G_k\|_1\le(r^3-1)\|Q_e\|_1,\qquad
\sum_k|G_k|\le(r-1)(1+r^2+r^4)Q_{e,\max}.
\]

For a turn carrying incident power \(P\),

\[
F_g^r=P\frac{n_{{\rm in},r}-n_{{\rm out},r}}
                       {1-un_{{\rm out},r}},\qquad
|F_g^r|\le\frac{2v_*}{1-v_*^2}P.
\]

This force bound supplies the selected actuator exposure and finite-lead
inventory. The comparison radial range is
\(R/R_0\in[1.068,1.332]\), with \(R_0=1/(12\pi)\),
\(R_{\rm ref}=1.2R_0\) and \(g_0=1.1(0.132R_0)\).
The largest work gap is \(g_{\max}=0.007352958371\).

The resulting coefficients apply to the complete six-rotor population
when its equal pairs share the emitted heat:

| Quantity | Upper coefficient |
|---|---:|
| \(W_{\rm total,max}/Q_{e,\max}\) | 0.016033804094 |
| \(\|\dot W_{\rm total}\|_1/\|Q_e\|_1\) | 2.054804879990 |
| \(\|\dot W_{\rm total}\|_\infty/Q_{e,\max}\) | 1.028476588159 |
| \(\|P_{\rm remote}\|_1/\|Q_e\|_1\) | 0.0543133442245 |
| \(\|P_{\rm remote}\|_\infty/Q_{e,\max}\) | 0.0276572276650 |

In particular, the total flight-energy coefficient is 2.616% above the
frozen \(1/64\) thermal-delay coefficient. The work leads carry the
larger correction; thermal delay variation contributes a smaller term.

For absorption \(a=0.62\) ppm, spin floor \(j_f=0.3\), and the
independently assigned M19 optical-peak comparison \(4.297704\), the
passive gain is \(\kappa=1.033334721\times10^{-6}\).
The added guide-work peak is at most \(2.183252\times10^{-9}\),
the summed radial force at most \(2.412433\times10^{-7}\), and
the finite work leads demand remote net power at most
\(1.228249\times10^{-7}\). Their photon energy is bounded by
\(1.789906\times10^{-9}\).

The existing two-delay reaction inverse has absolute gain below
\(2.638292563\). It therefore needs additional emitted half-channel
margin at most \(1.620240\times10^{-7}\) for these finite work
leads. The [published local endpoint trials](data/hosted_reaction_dynamics/summary.json)
have minimum emitted half-channel margin approximately
\(5.0\times10^{-4}\). This establishes headroom for the incremental
work-port command in that comparison. Incorporating the complete photon
inventory and retarded heat into the shared history remains the separate
coupled calculation.

## Tensor population and actuator alternative

At each azimuth the thermal photons occupy radial/axial directions;
the actuator photons occupy opposed radial directions. Annular
integration cancels the radial momentum vectors while retaining their
in-plane stress. The three equal axis pairs then have total spatial
stress \(W_{\rm total}\delta_{ij}/3\) and zero net momentum.
Their six rotors and all source, mixer, collection and work-port hosts
remain counted populations. The independently translated axis copies
can occupy disjoint regions; their placement within the full assembly
requires the common spatial design.

An alternative local drive uses opposed fixed-area capacitor gaps,
\(F_\pm=F_b\pm F/2\), \(g_\pm=g_0\mp d\). Its field energy
and electrical input are

\[
U=2F_bg_0-Fd,\qquad P_e=\dot U+F\dot d=-d\dot F.
\]

This alternative needs field inventory, force-rate information, return
electrodes and finite leads. A radial-speed bound alone supplies no
electrical bandwidth bound. The selected route uses radial work photons;
its numerical inventory excludes these alternative capacitor fields.

## Evidence

The [four-worker archive](data/moving_thermal_relay/summary.json) covers
stationary, uniform, slow-reversal and fast-reversal trajectories. Each
case uses 1,153 source samples, 289 observation times and independent
Hermite-panel speed checks. Every bath retains equal arriving tangent
streams. The maximum combined energy-balance residual is
\(1.57\times10^{-16}\); the largest actuator-inventory change from
8-point to 12-point panel quadrature is \(4.14\times10^{-13}\).
All runs begin and end with empty thermal and actuator flight inventories.

Thirteen tests cover hidden interpolation speed extrema, independently
differentiated arrival Jacobians, rest-frame elastic work, moving
four-momentum balances, flight-momentum derivatives, finite work leads,
six-copy tensor counting and the distinct capacitor alternative. The
[manifest](data/moving_thermal_relay/manifest.json) retains source and
evidence hashes.

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_moving_thermal_relay.py --workers 4

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_moving_thermal_relay.py
```

Finite apertures, optical aiming, absorption/scatter, finite-temperature
reciprocal heat flux and guide material laws set the physical realization
requirements. The current construction supplies their explicit paths,
ports, forces and energy inventories. This report was manually authored.
