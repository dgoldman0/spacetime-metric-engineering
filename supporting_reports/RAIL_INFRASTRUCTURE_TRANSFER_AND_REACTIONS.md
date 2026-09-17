# Rail infrastructure, nonlinear holding and shared reactions

17 September 2026.

The scheduled transfer construction admits a nonlinear heat and spin bound
through all four inherited histories, with its existing storage inventory.
The tightest certified spin is 0.320534, above the converter requirement
of 0.3. A common quadratic inequality covers the changing rotor energy,
guide transitions, useful-flight delays and converter circulation. The
guide's positive input power also has a uniform analytic bound.

These results apply to the lossless, axisymmetric holding and transfer
model. Optical absorption, rotational drag, finite actuator response and
spatial reaction paths retain their own state and interface requirements.
The complete rail continues to supply several coupled functions through
distinct constituents.

## Infrastructure and component responsibilities

The [architecture review](ACTIVE_RAIL_ARCHITECTURE_SCOPE_REVIEW.md) places
the protected packet, carrying flow, support response, handoff and reset
inside one scheduled service. Its source roles include the standing
substrate, radial backbone, angular jacket, endpoint receiver, live
handoff response, current relaxation and support reservoir. The four
metric controls coordinate these roles through their common geometry.

| Rail responsibility | Existing members and interfaces | Construction requirement carried forward |
| --- | --- | --- |
| Protected packet, entry and release | Packet corridor, catch/rematch collars, release sleeve and packet-edge controls | Preserve packet exclusion, service timing, carrier margins and exterior matching when physical sources are coupled. |
| Standing radial and angular support | Six conserved elastic constituents, original Maxwell fields and photon populations | Preserve fixed inventories, constitutive states, radial/hoop loads and finite-end connections. |
| Current transport and return | Original carriers, added coaxial field, inner/outer current surfaces and annular returns | Supply particle tensors, induction response, end shear and shared return paths. The tested independent added-host construction still has ten rejected first-fine samples. |
| Material connections | Force-matched cores and inline joints, with separate directional populations for sheets | Retain shared transmitted force, joint material energy and local propagation dynamics. |
| Local transfer and holding | Eighteen exchange nodes per label, guides, counterrotating stores, pilot and converter paths | Carry signed work between constituents and the complementary rail port, with counted finite flights, heat and optical losses. |
| Reaction distribution | Backbone, angular support, local route walls and interfaces between these members | Derive the changing support tensor and its work across the shared plant. |
| Receiver memory, reset and governance | Endpoint medium, support reservoir, sensors and chronology/readiness control | Retain release history, power and radial-force exchange, cycle-end storage, controller energy and readiness. |

The transfer model serves the exchange row of this table. Its eighteen
nodes represent six material cores, six joint populations, four field
populations, remaining inventory and the complementary rail port. The
largest first-fine thermal bound occurs at that complementary rail port.
Thus the calculation includes the exchange with the surrounding rail as
well as transfers between local constituents. The inherited material
allocations retain their stated current-host and finite-interface scope.

## Exact nonlinear reduction

Use \(C=P_*\delta\), time in \(\delta\), rotor inventory \(M=18C\)
and reference radius \(R_0=\delta/(12\pi)\), as in the
[scheduled-transfer study](SCHEDULED_TRANSFER_AND_MECHANICAL_HOLDING.md).
Let \(h=H/M\), \(v=p/h\), and define

\[
s=t/R_0,\qquad w=x-h,\qquad y=hv=p,\qquad u=R_0q/M.
\]

Primes below mean derivatives in \(s\). Because \(h'=u\), the full
rotor equations become

\[
w'=y/h-u,
\]
\[
y'=-\frac{\sqrt{1-v^2}}x w-
\left[k+\frac{\sqrt{1-v^2}\,v}{x(1+\sqrt{1-v^2})}-\frac uh\right]y,
\qquad
b'=\frac{kx}{h\sqrt{1-v^2}}y^2.
\]

This reduction retains the exact velocity dependence and thermal action.
It follows directly from the matched energy and radial-momentum ports;
the radial velocity force proportional to \(q\) cancels when forming
the reduced equations.

The network energy ledger gives
\(1.1170011\le h\le1.3000927\). Its power bounds give
\(|q|\le1.048962P_*\), including loop fill/drain, so
\(|u|<0.00155\). On the trial neighborhood
\(|w|,|v|\le0.012\), write \(z=(w,y)\) and

\[
z'=Az+Bu,\qquad
A=\begin{pmatrix}0&\omega\\-\omega-e&-d\end{pmatrix},\quad
B=\begin{pmatrix}-1\\0\end{pmatrix}.
\]

Rational bounds enclose the exact coefficients:

\[
0.7691\le\omega\le0.8953,\quad |e|\le0.00981,\quad
0.39318\le d\le0.40682,\quad b'\le0.4044y^2.
\]

Two constant matrices provide the certificate:

\[
P_I=\begin{pmatrix}1&0.24\\0.24&1\end{pmatrix},\qquad
P_H=\begin{pmatrix}1.1&0.24\\0.24&1.1\end{pmatrix}.
\]

For all eight coefficient-box vertices, exact rational arithmetic verifies

\[
A^TP_I+P_IA+2(0.175)P_I\prec0,
\]
\[
\begin{pmatrix}
A^TP_H+P_HA+\operatorname{diag}(0,0.4044)&P_HB\\
B^TP_H&-3.4
\end{pmatrix}\prec0.
\]

The matrices are affine in the enclosed coefficients, extending these
inequalities throughout the box. This is the common quadratic approach
developed in [Boyd et al., *Linear Matrix Inequalities in System and Control
Theory*](https://web.stanford.edu/~boyd/lmibook/). Here every leading
principal minor used for definiteness is evaluated exactly as a rational
number; optimization tolerances play no role in admission.

The first inequality makes
\(z^TP_Iz\le(0.00155/0.175)^2\) invariant. Its coordinate bounds are
\(|w|<0.00913\) and \(|v|<0.00818\), strictly inside the assumed
neighborhood. The prepared state has \(z(0)=0\), thermal action
\(b(0)=10^{-8}\), and the corresponding paid reduction in spin.

The second inequality gives the whole-history thermal bound

\[
b(t)\le b(0)+z(0)^TP_Hz(0)
 +\frac{3.4R_0}{M^2}\int_0^t q(\tau)^2\,d\tau.
\]

The archived forcing bound includes receipt slopes and jumps, guide
motion, and converter-loop preparation and drainage. It therefore
supplies the integral in this inequality directly. The common matrices
cover arbitrary coefficient variation inside the certified region.

## Spin, tension and guide admission

Reconstructing spin from the exact state gives

\[
j^2=h^2-1-2b-w^2
 -2h(h+w)\left(1-\sqrt{1-v^2}\right).
\]

The certified radial bounds reduce the permitted thermal action slightly
from the equilibrium allowance, to **0.07874587**. Every history fits:

| History | Maximum thermal-action bound | Minimum certified spin | Maximum thermal-energy bound |
| --- | ---: | ---: | ---: |
| First, 16 labels × 2,057 samples | 0.03906590 | 0.411534 | 0.634740C |
| First, 32 labels × 4,113 samples | 0.07237482 | 0.320534 | 1.175941C |
| Second, 16 labels × 1,029 samples | 0.01440299 | 0.467638 | 0.234019C |
| Second, 32 labels × 2,057 samples | 0.02307417 | 0.448713 | 0.374908C |

Moreover \(x\ge1.10787\) ensures tensile material stretch, while
\(j^2\le1.3001^2-1<1\) supplies a subluminal spin bound. These strict
margins close the continuation argument for the stated nonlinear ODE.
Different initial heat or radial motion enters through the displayed
initial-state terms; warm isolated trials retain their own preparation.

Guide input also has a uniform lower bound. For the septic radius ramp
\(f(s)=35s^4-84s^5+70s^6-20s^7\),
\(1-f\ge35s^3(1-s)^4\). This bounds the potentially negative
falling-ramp work by minimizing a quartic. Adding the separate
acceleration and Lorentz-factor derivative bounds gives

\[
U_{\rm guide}\ge0.000960955P_*>0
\]

for every permitted pair of guide plateaus. The existing pilot therefore
covers the complete guide family analytically. The loop's local
reflected/bypass ramp admission remains the previous numerical check;
finite-slew dispatch and spatially matched reflection remain separate
interface constructions.

## Reaction tensor and next coupled construction

The rotor's integrated pressure trace simplifies exactly to

\[
\Pi/M=h-x\sqrt{1-v^2}-kxp.
\]

The invariant bounds give \(|\Pi|\le0.251193C\) per active local
holding package, throughout the histories. Three equally populated ring
planes make the summed spatial stress isotropic in the local averaging
frame; opposite spins cancel angular momentum. This specifies a finite
reaction demand for the surrounding component ensemble.

The next allocation connects that demand to the existing longitudinal
support, transverse jacket, photon populations and their inline joints.
Their fixed inventories and force laws remain in the ledger, with the
additional state energy charged to reserve. A successful integrated
allocation must also supply its spatial traction paths and reciprocal
operating work. The rotor has its own containment duty; the rail's other
materials retain the support and response roles listed above.

## Reproducibility

The [certificate archive](data/nonlinear_holding_certificate/summary.json)
contains all eight rational matrix checks, analytic guide bounds and the
four verified history applications. Source snapshots and parent hashes
retain the complete forcing provenance. Four new tests compare the exact
reduction against the original equations, verify the rational inequalities,
check guide admission and exercise the initial-state and heat limits.

```sh
env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python toolkit/adm_harness_cli/scripts/audit_nonlinear_holding_certificate.py \
  --workers 4 --output /tmp/nonlinear_holding_replay

env PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  python -m pytest -q toolkit/adm_harness_cli/tests/test_nonlinear_holding_certificate.py
```
