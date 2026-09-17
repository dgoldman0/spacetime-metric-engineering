# Finite C1 source pair: shared field and separate support

17 September 2026.

The first C1 screen constructs two finite, neutral electrostatic source
populations, counts their shared Maxwell field, and solves separate static
material-support requirements with zero radial end traction. Offset overlap
placements have substantially smaller support requirements than the tested
throat-centered placements. A broad overlap over coordinate labels
\([0.5,2.5]\) is retained as the C1 construction bracket, alongside the
lower-energy, narrower \([0.5,1.0]\) comparison.

The result supports doing finite-module design before refining the earlier
local fixtures. Placement, source overlap and the extent of each internal
load path materially change those fixtures' duties. Full source completion,
physical material laws, angular packing and a service cycle remain open.

The [module specification](../component_design/C1_FINITE_MODULE_PAIR.md)
defines component responsibilities, accounting boundaries, motion requirements
and advancement gates. The [topology decision](RAIL_BUILD_TOPOLOGY_DECISION.md)
continues to supply the provisional C1 preference.

## Standing comparison and actual source

The metric is the static, zero-shift surrogate of the archived phase-0.745
lapse and spatial geometry. This is the background of the earlier
[geometry/source comparison](ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md).
The active beta075 V5 service metric retains its separate time-dependent
equations and evidence.

The common radial electric flux \(Q=R^2E\) has a plateau through
\(|x|=1\), a quintic taper to \(|x|=3\), and zero exterior flux. Its
amplitude sets the throat electric tension to 95% of the geometric throat
radial-pressure magnitude. The total field is identical in every placement.
The 95% fraction is a declared load comparison. The Maxwell angular pressure
and complete remaining tensor are evaluated with it.

For a smooth step \(h\) through \([a,b]\),

\[
Q_L=(1-h)Q,\quad Q_R=hQ,\quad
\rho_{q,i}=\frac{Q_{i,x}}{BR^2},\quad
F_i=\rho_{q,i}\frac{Q}{R^2}.
\]

Module L's charged material and internal supports occupy \([-3,b]\), while
module R occupies \([a,3]\). Each flux and material tensor vanishes at its
own ends. Each module is neutral, with finite positive and negative charge
inventories. The source has a real local Maxwell stress under these specified
charge distributions. Its stationary charge binding and material response
remain constitutive requirements.

The field interaction is counted explicitly:

\[
u_E=\frac{Q_L^2+Q_R^2}{2R^4}+\frac{Q_LQ_R}{R^4},\qquad
\nabla_aT_E^{a\hat l}=-(F_L+F_R).
\]

The cross term carries half the local field energy where the two amplitudes
are equal. All placements have field proper energy **93.396712**. The
interaction energy belongs within that fixed total. In particular, an overlap
inventory assembled from the two isolated self-fields would miss this term.

## Finite internal reaction requirements

For each material support, put
\(Y=AR^2\rho\), \(X=AR^2p_r\), \(Z=AR^2p_t\). Its static force equation is

\[
X_x+(\log A)_xY-2(\log R)_xZ=ABR^2F_i.
\]

The finite-domain conditions set \(X=Y=Z=0\) at both module ends. Material
energy obeys \(\rho\geq|p_r|,|p_t|\). Thus each module can transmit force
through its own radial stress while exchanging force electromagnetically
with its neighbor. A one-assembly control carries the same total charge and
electric field across \([-3,3]\). That control compares finite internal
connectivity; it supplies a limited reference for the broader A/C1 decision.

The optimizer minimizes \(4\pi\int BR^2\rho\,dx\). It interpolates \(Y\)
and \(Z\) linearly and reconstructs \(X\) by integrating the force equation
within each cell. Endpoint matching and interior stress guards enter the
linear program. A separate sample checks the reconstructed stress, and an
independent derivative of its radial pressure checks the force equation.
The resulting optima belong to this finite-dimensional comparison family.

The initial relaxation allowed arbitrarily concentrated supports. Its maximum
density grew under refinement, and one narrow outer-overlap case changed
sharply when the grid admitted a different concentration location. Those
outcomes motivated a finite envelope:

\[
\rho\leq4\rho_{E,0}=0.0363466842,\qquad
|\partial_l\rho|,|\partial_lp_t|\leq0.0363466842.
\]

The gradient scale is one unit of proper length. Both limits are comparison
parameters, with additional factor-two tighter and broader controls on the
narrow offset case. Their physical values must ultimately follow from the
selected material and metric scale. A zero mass-per-charge coefficient grants
an optimistic carrier-cost relaxation throughout this round. Absolute charge
inventories expose the additional species-dependent requirement.

## Placement and overlap results

The table uses 128 cells per coordinate unit, with the bounded support
envelope. Energies are geometric proper-volume integrals over the full solid
angle. They have a different measure from the earlier local storage ledgers.

| Overlap labels | Proper overlap length | Material support energy | Numerical standing result |
|---|---:|---:|---|
| Connected finite control | — | 3.101879 | One finite material support |
| \([-0.25,0.25]\) | 61.4669 | — | Bounded support LP infeasible |
| \([-0.5,0.5]\) | 101.5302 | — | Bounded support LP infeasible |
| \([-1,1]\) | 162.5864 | 106.712367 | Separate bounded supports |
| \([0.5,1]\) | 2.8940 | 5.492905 | Lowest sampled support energy |
| \([0.25,1.25]\) | 16.2942 | 8.982077 | Separate bounded supports |
| \([-0.25,1.75]\) | 98.0714 | 20.895785 | Separate bounded supports |
| \([1.25,1.75]\) | 20.3103 | — | Bounded support LP infeasible |
| \([1,2]\) | 28.9229 | 11.317216 | Separate bounded supports |
| \([0.5,2.5]\) | 33.2046 | 8.866203 | Broad C1 construction bracket |

Infeasibility belongs to the specified field placement, support envelope and
discretized material family. The quantum, geometry and material freedoms of
C1 remain larger. Conversely, a solved LP supplies a static tensor requirement;
its material dynamics and microscopic construction still need to be supplied.

Coordinate width varies substantially from proper width on this background.
The broader C1 bracket has static light-crossing time **2.301640**, compared
with **0.277761** for the narrow offset comparison. These are coordinate times
of the standing surrogate. Causal arming and handoff must use the eventual
active geometry, source response and physical normalization.

At 256 cells per coordinate unit, the broad bracket requires material support
energy **8.862800**, a **0.0384%** change from the previous grid. Its two
module proper lengths are **242.059** and **33.766**; the overlap covers
**98.34%** of the shorter module. The narrow comparison covers **8.57%** of
that shorter module. The broad construction is consequently an asymmetric
throat-containing assembly and neighbor. Comparable-size modules and a
repeating chain retain their own design requirements.

The narrow comparison receives an additional refinement to 256 cells per
coordinate unit. Its material support energy is **5.492386**, compared with
**3.101704** for the connected finite control. The shared field plus support
energies are **98.889098** and **96.498416**. Mechanical separation therefore
costs about 77% more supporting-material energy, or 2.48% more field-plus-support
energy, in this fixed-source comparison. Full hardware and signed-source
inventories remain additional costs.

The narrow pair also carries absolute charge inventory **28.188125**, twice
the connected control's **14.094063**. Each individual module has zero net
charge. The extra opposing charges in the overlap produce real internal
reaction duties even where the summed charge density vanishes. The broad
bracket has absolute charge inventory **21.498014** and interaction energy
**3.176760**, compared with **0.225955** interaction energy in the narrow
case. Charge-host cost and overlap extent therefore supply distinct design
objectives alongside material support energy.

## Remaining source and service gates

The supplied ordinary tensor is the Maxwell field plus the two material
supports. The remaining source is evaluated directly as
\(G[g]/(8\pi)-T_E-T_L-T_R\). At the finest narrow-pair resolution, its
negative radial-null proper-volume requirement is **14.368400**, compared
with **9.649532** for the connected control. Its negative angular-null
requirement is **75.207016**, compared with **74.193194**. These are residual
requirements, with an actual signed source still to be identified.

The Maxwell field saturates the radial null projection, and the support
envelope has nonnegative radial null stress. Consequently the inherited
longitudinal-source exclusion continues to apply when its quantum law,
optical loop, geometry and ordinary-aggregate assumption are retained. At
\(k/R_{0,\mathrm{reference}}^2=0.01\), even the optimistic 50% clock box
supplies only **17.10%**, **7.45%** and **4.15%** of the necessary balance
over \([-3,3]\), \([-5,5]\) and \([-7,7]\), respectively. Finite quantum
loops with turning regions or another signed sector change that problem and
require their own counted boundary and state construction.

The radial force integrals also retain their local meaning. They sum support
duties over solid angle; module center-of-mass acceleration and torque require
angular-resolved forces, field momentum, material locations and a declared
motion model. The current spherical source average leaves those directional
degrees of freedom open.

The subsequent [signed-source channel screen](C1_SIGNED_SOURCE_CHANNEL_SCREEN.md)
retains the broad C1 bracket, narrow cost reference and common geometry while
testing inset finite reflecting quantum channels. Its radial conformal tensor
obstruction and conditional angular-source allocation leave a joint quantum
and boundary construction open. Finite carrier
binding, angular packing, current preparation, recoil and recovery then enter
the coupled evolution. A physical packet handoff/reset calculation follows
source and constitutive closure. Existing local storage and fixture results
remain conditional inputs to that assembly.

## Verification and reproducibility

The numerical record includes the nine overlap placements and connected
control, three spatial resolutions, relaxed and bounded material envelopes,
and additional geometry, quadrature, envelope and spatial checks. Independent
cases run in four worker processes. Execution snapshots, the reference metric
hash, inherited source hashes and output hashes accompany the arrays.
The final record contains **68** case/resolution/envelope comparisons and
**92** verified source, input and artifact hashes. Both retained brackets
pass the numerical audit. Two individual support LPs in other placements
return an unresolved solver status; their messages remain in the record.
The three infeasible table entries each contain a solver-confirmed infeasible
support at the table's resolution. The narrow outer placement's additional
256-cell check remains numerically unresolved.

Twenty-one focused tests cover finite neutral fields, Maxwell cross stress,
independently differentiated force balance, analytic capacitor supports,
closed-boundary force obstruction, finite density bounds and the inherited
geometry/longitudinal-source identities. The final narrow-pair refinement
changes support energy by about **0.0095%**. Its independent force residual is
below **2.6e-7** of peak load; the largest sampled off-grid stress-inequality
error is **4.2e-10** in local stress units. These finite-sample errors retain
their numerical scope.

The [summary](data/c1_module_pair/summary.json),
[comparison table](data/c1_module_pair/comparison.csv) and
[independent audit](data/c1_module_pair/verification.json) retain all cases,
solver outcomes and refinement measurements. This report is written manually.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/screen_c1_module_pair.py --workers 4
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_c1_module_pair.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=toolkit/adm_harness_cli python -m pytest -q toolkit/adm_harness_cli/tests/test_c1_module_overlap.py toolkit/adm_harness_cli/tests/test_geometry_opening.py toolkit/adm_harness_cli/tests/test_longitudinal_balance.py
```
