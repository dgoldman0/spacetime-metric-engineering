# Paired thermal exchange interfaces

Equal opposed rotors can transfer absorption heat into a common
countercirculating radiation bath through passive directional ports and
a symmetric finite relay. The source law includes thermal angular
momentum, cold-material recoil, photon flight energy and guide impulses.
A frozen relay realizes the required local bath symmetry. Moving
collection adds a calculable guide-work term whose coupled history
remains a separate connection requirement.

## Absorption and thermal recoil

Let \(q\) be total optical power entering the rotor pair,
\(s=\operatorname{sign}q\), \(j>0\) the tangential speed in the
radially comoving frame, and \(\gamma_r=(1-v^2)^{-1/2}\).
An absorption fraction \(a\), measured in the moving facet's rest
frame, gives

\[
P_{\rm out}=(1-a)\frac{1-sj}{1+sj}P_{\rm in},\qquad
P_{\rm in}=\frac{|q|(1+sj)}{2j+sa(1-sj)}.
\]

The discharge branch requires \(a<2j/(1+j)\).

Write \(S=s(P_{\rm in}+P_{\rm out})\). Optical energy and
momentum entering the positive-spin rotor are proportional to
\((q,vq,S/\gamma_r,0)\), in coordinates
\((E,p_r,p_\theta,p_z)\). The negative-spin copy reverses the
tangential component; each copy receives half the stated pair power.

The material-rest heat power and the reduced zero-angular-momentum
heating expression are

\[
Q'=\frac{a|q|}{2j+sa(1-sj)},\qquad
H=q-jS=(1-j^2)Q'.
\]

Here \(Q'\) is the sum of proper-time heat powers for the equal
rotors. Their identical clock factors make this sum unambiguous.
For one emitter with signed speed \(w\), equal rest-frame tangential
emission powers \(Q'_\sigma/2\) become laboratory powers
\((1\pm w)Q'_\sigma/2\). Its emitted four-force is

\[
K_{\rm em}=Q'_\sigma(1,v,w/\gamma_r,0).
\]

Thus isotropic emission within these two tangential modes carries
angular momentum. Cold material receives optical four-force minus
\(K_{\rm em}\). Their difference is orthogonal to the material
four-velocity, as required for the fixed cold constitutive inventory.
For the pair, emitted tangential momenta are equal and opposite.

The maximum passive heating ratio over \(j\ge j_f\) is

\[
\kappa=\sup\frac{Q'}{|q|}
 =\frac{a}{2j_f-a(1+j_f)}.
\]

At \(j_f=0.3\), this is \(1.098901\) times the bound based on
\(H\). For \(a=0.62\) ppm, \(\kappa=1.033334721\times10^{-6}\).

A directional alternative emits rest-frame powers
\(Q'_\sigma(1\mp w)/2\). Both laboratory counterstreams then
have power \((1-w^2)Q'_\sigma/2\). The emitted proper-frame
momentum is \(-wQ'_\sigma\), and its recoil supplies the additional
cold torque. This realizes the smaller heating expression \(H\)
through a spin-dependent angular emission distribution. The passive
paired construction uses equal proper-frame emission instead.

## Finite symmetric routing

The retained relay places sources and baths at \(z=\pm d/2\),
with a central mixer at \(z=0\). Source guides turn the emitted
tangential streams inward along the axial direction. Two independent
direction channels undergo 50:50 mixing, after which destination guides
restore the positive or negative tangential direction. Incoherent
thermal input powers add at the mixer. Every route has delay
\(\tau=d\) in this frozen local frame.

For source index \(\sigma=\pm1\), final tangential direction
\(\epsilon=\pm1\), and equal per-rotor proper heat power \(Q_0\),

\[
P_{\sigma\epsilon}(t)=\frac{1+\epsilon\sigma j(t)}2Q_0(t).
\]

Each bath receives
\(\tfrac12\sum_\sigma P_{\sigma\epsilon}(t-\tau)
=Q_0(t-\tau)/2\) in each direction. Local counterstream balance
therefore follows from a specified transfer path as well as source
symmetry. Photon flight energy is

\[
W(t)=\int_{t-\tau}^{t}2Q_0(u)\,du,\qquad
\dot W=2Q_0(t)-2Q_0(t-\tau).
\]

The turning guides carry local reactions. Per ray of power \(P\),
the source turn receives spatial force
\((0,\epsilon P,\sigma P)\); the destination turn receives
\((0,-\epsilon P,\sigma P)\). Central mixing also carries the
input axial momentum imbalance in each direction channel. The audit
retains these forces separately and verifies four-momentum balance
including the changing photon inventory.

These guides are separate, stationary, nonrotating reaction hosts in the
frozen construction. Their source collectors receive the emitted
opposed torques. Connecting those hosts across the pair requires a
mechanical stress path. Attaching a collector directly to rotating cold
material returns its captured angular momentum and adds rotational
work to the source law.

Axial flight photons have \(T_{zz}=W\), whereas the final circular
bath has tangential stress. Three equally weighted rotated relay copies
give mean spatial stress \(W\delta_{ij}/3\) while preserving
total energy \(W\). The corresponding guide reactions and host
inventories accompany all three copies.

## Connection to the rotor equations

For emitted power \(Q_e\), arriving bath power \(Q_a\), and
optical input \(q_{\rm port}\), the rotor excluding flight photons
receives

\[
q_r=q_{\rm port}-Q_e+Q_a.
\]

Its absorption contribution to thermal action and its optical/emission
spin rate satisfy

\[
\dot b_{\rm abs}=\frac{xQ_a}{\gamma_r M},\qquad
\dot j=\frac{x(q_{\rm port}-Q_e)}{\gamma_r Mj}
=\frac{xq_r}{\gamma_r Mj}-\frac{\dot b_{\rm abs}}j.
\]

Thus the existing radial combination \(j^2+2b\) follows the
original law driven by \(q_r\), provided all received and emitted
ports have the required current radial direction cosine. In the frozen
relay, \(q_r=q_{\rm port}-\dot W\). Optical absorption is evaluated
using \(q_{\rm port}\), and bath heating uses the delayed arrival
power \(Q_a\).

## Moving collection and its work port

A reflecting guide moving radially at speed \(u\) obeys rest-frame
photon energy conservation:

\[
\frac{E_{\rm out}}{E_{\rm in}}
=\frac{1-u n_{{\rm in},r}}{1-u n_{{\rm out},r}}.
\]

Choosing the rotor-matched outgoing ray
\(n_{{\rm out},r}=u\) gives
\(E_{\rm out}/E_{\rm in}=\gamma_u^2(1-u n_{{\rm in},r})\).
Guide recoil is the incident minus outgoing photon four-momentum and
satisfies \(\Delta E_{\rm guide}=u\Delta p_{{\rm guide},r}\).

For an axial incident ray, the added photon energy is
\(u^2E_{\rm in}/(1-u^2)\). At the assigned comparison speed
\(|u|\le0.00905\), its maximum is
\(8.19092\times10^{-5}E_{\rm in}\). Allowing incoming radial
cosines within the same speed bound gives the larger upper cost
\(1.63818\times10^{-4}E_{\rm in}\).

If moving guides deliver total power \(G\) to the photons,
\(\dot W=Q_e-Q_a+G\), so the rotor excluding guide hosts has
\(q_r=q_{\rm port}-\dot W+G\). The guide hosts supply \(-G\)
and the associated recoil. Including those hosts in the rotor subsystem
also includes their forces. A constant-delay moving geometry, these
guide work ports, and their material stress response require coupled
evolution. Finite-temperature reciprocal radiation and thermalization
also determine the physical heat-transfer rate.

## Evidence and reproduction

The [interface evidence](data/thermal_exchange_interfaces/summary.json)
checks 180 source/cold-force cases, 882 moving collectors, and four
finite frozen relays. Maximum cold-force orthogonality error is
\(2.23\times10^{-16}\); maximum relay four-momentum residual is
\(5.56\times10^{-17}\). Each local bath has balanced arriving
counterstreams. Eight tests independently check Lorentz boosts and
clock conversion, recoil, heating bounds, finite inventory, guide forces,
tensor averaging and moving-collector work.

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_thermal_exchange_interfaces.py \
  --workers 4 --output /tmp/thermal_exchange_interfaces_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_thermal_exchange_interfaces.py
```

The [manifest](data/thermal_exchange_interfaces/manifest.json) retains
source and output hashes. This report was manually authored.
