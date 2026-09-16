# Scheduled material reconfiguration, local transport and joint allowances

16 September 2026.

A prepared load schedule substantially reduces the largest control-rate
estimates while preserving the six conserved material inventories and their
constitutive laws. On the fine histories, the gap-sized control-speed bounds
fall from \(0.0394c\) to \(0.000439c\) at the first location and from
\(0.00170c\) to \(0.000200c\) at the second. Their maximum linear stretches
remain approximately 81.5 and 20.8 times the relaxed size.

Finite-delay reception inventories and additional ideal joint reactions can
also fit the sampled energy budget when their connections are sufficiently
short. This is a conditional transport and tensor-budget construction. The
original six materials retain their fixed reference inventories; the added
joint and optical reaction populations still require their own constitutive
inventories, geometry and dynamics. Current hosts, finite end connections,
optical conversion and the moving actuator tensor remain open parts of the
physical assembly.

## A prepared field history and persistent material duties

The [preceding reconfiguration model](MATERIAL_RECONFIGURATION_TEST.md)
selected allocations separately at each sampled time. Large local rate
estimates occurred as material roles entered or left service. The present
schedule keeps four roles under positive tension and retains the other two
at their counted, relaxed energies.

Let \(H_i,H_o\) be the inherited inner and outer hoop loads, \(U\) the
added hoop-field energy, and
\(R=(\eta^2-1)/(2\ln\eta)\), with \(\eta=1.01\). The duties are

\[
T_{Wi}=0,\quad T_{Si}=H_i,\quad
T_{Wo}=H_o-2RU,\quad T_{So}=0,\quad T_M=RU.
\]

The auxiliary transverse sheet carries at least a prepared positive bias
\(A_0\). Any increase above its minimum required tension receives twice
that increase in angular-photon energy, preserving its net transverse
stress. The extra ideal energy is therefore three times the tension bias.
The inactive inner sheet and outer string retain their positive reference
energies throughout the stroke.

For each label, let \(r_*\) be the minimum reserve from the preceding ideal
finite-interface allocation. The six materials receive total reference
energy \(M_\Sigma=r_*/4\), with \(A_0=M_\Sigma/2\). Their individual
reference amounts are prepared once to minimize the largest linear stretch.
The allowance

\[
m=M_\Sigma+3A_0+0.1r_*
\]

pays the upper bound on elastic surcharge, the entire possible auxiliary
bias cost, and a positive reserve. The original fields, current costs,
centrifugal reactions and separate radial interface loads remain counted.

The support-cone facets of the retained residual target
\((\rho,p,q)\), with field floor \(f\), are

\[
F_0=p+2q-\rho,\qquad F_1=p-q+3f-\rho,\qquad
F_2=-2p-q-\rho.
\]

Writing \(H=H_i+H_o\), \(a=\max(F_0+2H,F_1+H/2)\), and
\(b=F_2+H/2\), the allowed field interval is

\[
U_{\rm lo}=\max\left[0.001\frac{H_o}{2R},
                         \frac{a+H_o+m}{3R}\right],
\]
\[
U_{\rm hi}=\min\left[0.999\frac{H_o}{2R},
                         \frac{2H_o-b-m}{3+3R}\right].
\]

Every sampled interval is nonempty. The field follows the trajectory through
these intervals that minimizes its maximum proper-time slew. For a trial
rate \(k\), its lower envelope is
\(\max_j[U_{{\rm lo},j}-k|\tau_i-\tau_j|]\); feasibility requires this
envelope to lie below every upper bound. A corresponding upper envelope and
their midpoint supply the prepared command. Independent full-history linear
programs verify the minimum rates and their dual bounds.

| History | Previous gap-sized control-speed bound | Scheduled bound | Largest linear stretch |
| --- | ---: | ---: | ---: |
| First, coarse | \(0.01813c\) | \(0.0003928c\) | 78.11 |
| First, fine | \(0.03942c\) | \(0.0004393c\) | 81.47 |
| Second, coarse | \(0.0007788c\) | \(0.0001288c\) | 19.87 |
| Second, fine | \(0.001696c\) | \(0.0002002c\) | 20.77 |

The fine-history reductions are factors of 89.7 and 8.47. Maximum field
slews change from 0.71261 to 0.71740 at the first location and from 0.012624
to 0.012780 at the second under refinement. The material control-speed
estimates change more, especially at the second location. Further temporal
resolution remains necessary. These are bounds for the prescribed local
patch motions, with current patch dimensions at most the annular gap.

## Instantaneous work and finite transport delay

The continuous replay interpolates tensile duties and field energies
linearly, and the rail's stretches logarithmically, on each proper-time
panel. Elastic energies follow their fixed nonlinear constitutive laws.
Consequently the material power is evaluated throughout each panel:

\[
P_j(T)=\dot T\frac{T}{\sqrt{T^2+s_j^2}}-b_jT,
\qquad s_j=(1-\epsilon_j)M_j,
\]

where \(b_j\) is the sum of macro logarithmic strain rates in the material's
loaded directions. Its maximum can occur inside a panel. The calculation
checks the endpoints and its possible stationary point. Field and rail-port
powers are affine; the remaining-inventory power is monotone because the
elastic energies are convex. Thus the transport calculation uses bounded
instantaneous power, including the complementary retained rail port.

Electromagnetic transfer carries energy and momentum, as expressed by the
[Poynting flux and radiation pressure](https://openlearninglibrary.mit.edu/courses/course-v1:MITx%2B8.02.3x%2B1T2019/courseware/802x_week14/802x_lesson_37/).
A steady path of length \(d\) carrying power \(P\) has transit energy
\(Pd/c\). The present allowance uses paths whose delay is bounded by
\(\tau_d=\max_t[(\eta-1)r]/c\) for each label. This describes local
connections between distributed components. A spatial routing with those
path lengths remains part of the assembly construction.

Let \(A_i(t)=\max(P_i(t),0)\) be a node's receipt in a lossless,
instantaneously matched donor/receiver routing. A sufficient prepared
reception energy is

\[
C_i=\tau_d\sup_t A_i(t).
\]

With delayed arrivals, its buffer contains
\(B_i=C_i-O_i\), where \(O_i\) is the energy still in flight to that
node. Since every arrival delay is at most \(\tau_d\),
\(O_i\le\int_{t-\tau_d}^{t}A_i(s)\,ds\le C_i\).
Buffers stay nonnegative through startup, operation and final drainage.
Their combined energy with all in-flight transfers is the constant
\(C=\sum_iC_i\).

An additional ideal tensile allowance equal to the in-flight radiation
energy cancels its directional pressure in the integrated tensor. Its
energy is bounded by \(C\), giving a conservative transport allocation
of \(2C\). This reaction allowance supplies an energy and stress budget;
its changing optical-guide stresses, operating power and material law still
require a dynamical construction.

Including the joint work below, the maximum reception energies are
\(3.7863\times10^{-5}\) and \(1.6657\times10^{-5}\) per label on the
fine histories. Transport plus the ideal reaction allowance uses at most
4.58% and 1.13% of each label's minimum material reserve. All values retain
the existing ledger normalization. Applying this same peak-power buffer
construction to leg-length paths exceeds the available reserve by large
factors. The short-path layout is consequently a substantive requirement
of this particular transport construction.

## Additional connections and their operating work

For a material patch of loaded span \(d\), the tensile force conjugate to
that span is \(F=T/d\). An extra connection of total length \(h\), summed
over the two ends of that direction, has minimum ideal tensile energy
\(Fh=\zeta T\), where \(\zeta=h/d\). Each sheet has two loaded
directions and each string has one.

Writing \(G_z=T_{Wi}+T_{Wo}\) and
\(G_\perp=T_{Wi}+T_{Si}+T_{Wo}+T_{So}+2T_M+2T_A\), the added
connection energies and negative stresses are
\(J_z=\zeta G_z\) and \(J_\perp=\zeta G_\perp\).
Equal directional photon populations provide the opposite stresses. Their
combined energy is \(2(J_z+J_\perp)\), with zero summed pressure.
This additional package leaves the scheduled material duties unchanged.

Its operating work is included explicitly. In either direction, the tie
and photon powers are

\[
P_- = \dot J-J\,\dot{\ln\lambda},\qquad
P_+ = \dot J+J\,\dot{\ln\lambda}.
\]

The remaining-inventory port receives the matching debit
\(-2(\dot J_z+\dot J_\perp)\). Four new transfer nodes therefore enter
the reception-capacity calculation. All sixteen nodes, including the rail
port, have reciprocal total power. At the selected attachment fraction,
counting these extra operating exchanges increases the required reception
inventory by approximately 0.02% or less.

The main allowance keeps joint and transit reactions distinct and charges

\[
E_{\rm allowance}=2(J_z+J_\perp)+2C(\zeta).
\]

A separate comparison permits their opposing stresses to share reactions;
it slightly improves the reserve. The principal result uses the full
separate cost above. Actual shared load paths can also change the original
material duties and belong to a broader joint optimization.

| History | Minimum reserve before the allowance | Minimum reserve with \(h/d=10^{-4}\) and local transport |
| --- | ---: | ---: |
| First, coarse | 0.00176251 | 0.00121662 |
| First, fine | 0.00164046 | 0.00109293 |
| Second, coarse | 0.00326431 | 0.00323009 |
| Second, fine | 0.00296000 | 0.00291016 |

All 246,816 sampled states retain positive reserve under these allowances.
Convex material energies and the linear added joint energy preserve a
positive lower bound between samples for the defined interpolation.

The connection-length restriction is stringent. On the first fine history,
the largest uniform fraction covered by the allowance is approximately
\(3.284\times10^{-4}\), or **0.0328% of the loaded patch span**. The
second permits approximately \(4.305\times10^{-3}\), or **0.430%**.
Even granting free transport, the corresponding ideal neutral-joint energy
ceilings are only \(3.441\times10^{-4}\) and
\(4.320\times10^{-3}\). At \(h/d=0.001\), the joint energy floor alone
exceeds the first fine history's reserve at nine samples. At \(h/d=0.01\),
it exceeds the second fine history's reserve at twenty-five samples.

These ceilings apply to additional unit-strength connections and their
neutralizing reactions, with the present six material duties held fixed.
Continuous interfaces and reuse of existing load-bearing material have
different inventories and force paths. The selected joint materials are
ideal stress carriers whose reference inventories and strain histories
remain to be constructed.

## Physical construction and evidence

The result supplies a smoother prepared material trajectory, a causal
reception-inventory construction, and a quantitative allowance for short
connections with their own operating work counted. The remaining assembly
must realize the patch geometry, photon conversion and momentum reactions,
optical-guide dynamics, joint constitutive inventories and moving material
stresses. The transport-power sensitivity retains positive reserve at both
fine histories with an eightfold increase in the counted traffic. That
sensitivity measures allowance; an operating model must determine the
additional traffic and conversion costs.

The [finite current-host result](FINITE_CONTAINMENT_HOSTS_AND_EVOLUTION.md)
also remains active: its all-speed necessary bound rejects ten first-location
fine samples for independent added particle hosts. The present schedule
preserves the original current costs and leaves that obstruction in place.
Shared current paths, finite end-force transfer and torque transmission
remain coupled construction requirements. Large material stretches and the
absence of an identified physical material also persist.

The [implementation](../toolkit/adm_harness_cli/adm_harness/distributed_reconfiguration.py),
[four-worker audit](../toolkit/adm_harness_cli/scripts/audit_distributed_reconfiguration.py)
and [tests](../toolkit/adm_harness_cli/tests/test_distributed_reconfiguration.py)
are accompanied by the [numerical summary](data/distributed_reconfiguration/summary.json),
four state archives and the [hash manifest](data/distributed_reconfiguration/manifest.json).
The focused suites pass **42 tests**. Fourteen independent full-history
linear programs verify the field schedules; 96 independent panel integrals
verify the instantaneous work. Maximum tensor reconstruction error is below
\(9\times10^{-16}\), exchange error below \(1.1\times10^{-15}\), and
instantaneous reciprocal-power error below \(2.3\times10^{-13}\).
Exact executed sources and parent hashes accompany the evidence.

Reproduction uses a fresh output directory:

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_distributed_reconfiguration.py \
  --workers 4 --output /tmp/distributed_reconfiguration_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_distributed_reconfiguration.py \
  toolkit/adm_harness_cli/tests/test_material_reconfiguration.py \
  toolkit/adm_harness_cli/tests/test_finite_containment.py \
  toolkit/adm_harness_cli/tests/test_containment_ensemble.py
```
