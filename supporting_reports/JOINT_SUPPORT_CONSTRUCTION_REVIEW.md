# Joint support construction review

The joint construction remains open at the physical backing and its continuing
rail attachments. The capacitor retains its registered electrical duties.
Accurate work accounting and momentum balance place a substantially larger
load on the support than the early approximate tensor suggested. Enlarged
material-response families expose useful momentum-routing freedom, alongside
a strong demand for radial tension and a costly angular reaction when that
tension is supplied electromagnetically.

This review records the final part of the three-hour investigation authorized
on 12 September 2026, following the
[conservation correction](JOINT_SUPPORT_CONTINUUM_CORRECTION.md),
[passive coupling and joint inverse](JOINT_SUPPORT_CONSERVATION_AND_PASSIVITY.md),
and [refinement and end-load milestone](JOINT_SUPPORT_REFINEMENT_AND_END_LOADS.md).
The session began at 14:50:29 UTC with a deadline of 17:50:29 UTC. The design
disclosure and its PDF retain their design content.

## Conservative work changes the acceptance test

Support energy is reconstructed from its actual radial work, angular work,
and counted exchange:

```
M_t = -D p_r (ln ell)_t - 2Q (ln R)_t - N D P_fixed.
```

Four Gauss samples per source panel define a cubic power history and its
quartic energy primitive. The independent audit differentiates that
primitive and compares it with the physical power equation. It therefore
measures quadrature error in a conserved energy history. Spatial quadrature
includes every original source and sharing knot, and the material tests also
include both physical cuts and every temporal knot.

For the retained support history at 256 cells and 515 times, the weighted
power residual falls from 1.58% under bilinear energy interpolation to
`3.46e-8`. The weighted force residual is 0.4177%. Its member-energy deficit
remains 0.58077: near `t=1.024, x=-2.1`, density 0.59549 carries radial
compression 1.17282 and angular pressure 0.00172. The maximum energy-density
change caused by the work reconstruction is only 0.000213.

The three source-remainder peaks for this conserved history are 0.22500,
0.66006, and 3.18149. These are residual tensor demands. Supplying their
quantum contribution belongs to the complete source construction.

## Momentum routing helps, with a remaining material cost

The earlier delivery comparison selected the receiver-side feed partly
because leftward recovered waves gained substantial energy from the changing
geometry. The present test separates absorption direction from recovery
direction. Let `a` be the fraction of absorbed work fed from the left and `b`
the fraction of recovered work emitted leftward. With the established
efficiency 0.98, the work route's rest-frame force becomes

```
F_wave = (1-2a) max(J,0)/0.98
       + (1-2b) 0.98 max(-J,0),
```

while its rest-frame power stays fixed. Opposite-direction responses are
evolved through the same force and work equations, so the support solution
is affine in `a,b`.

Holding the original preparation and angular history fixed, the best constant
direction fractions are `a=0.24521, b=0`. The member deficit falls to 0.13802,
but the backing density reaches -0.02093 elsewhere. This is an optimistic
momentum gate: extra travelling inventory, finite taps, guide stress, and
return connections would still need their own accounting. Its failure already
excludes that particular support history as a complete material construction.

The existing smooth response family then frees prepared energy, angular
stress, and incoming pressure together with the two route fractions. Removing
the original amplitude limit permits a coarse separate-member candidate with
fraction `f=0.99`, `a=0.22671`, and `b=0`. It uses both feed directions and
keeps recovery rightward. Its initial support inventory is 7952.49, compared
with 2297.42 for the earlier smooth approximate candidate. The material null
peak is 1.65572, compared with the earlier comparison cap 0.2. These figures
cover the fluid and backing tensor; the changed route's complete tensor is
additional construction work.

Continuous work reconstruction retains positive member energy on that coarse
candidate, with a minimum required fraction about 0.99038. Keeping its
controls fixed under refinement gives the following result.

| Cells / time nodes | Weighted force residual | Weighted power residual | Maximum member density deficit |
| --- | ---: | ---: | ---: |
| 128 / 258 | 0.6776% | `1.81e-6` | 0 |
| 256 / 515 | 0.3724% | `1.33e-7` | 0.00744 |
| 512 / 515 | 0.1981% | `1.33e-7` | 0.00767 |

The refined failure lies near `t=0.0452, x=-1.9754`, where density 0.04700
carries radial tension 0.05465. Its negative radial enthalpy also obstructs
repair by adding a conserved radial-tension increment. Thus the coarse
controls supply a useful response direction, with feasibility lost under
refinement.

## What an electromagnetic replacement must pay for

The generic member cone allows an independently load-bearing radial member
to approach `|p_r|=rho`. A radial Maxwell field also carries angular pressure.
For a specific field-based comparison, use these positive-energy components
in the local material frame:

| Component | `(rho, p_r, p_t)` per unit energy |
| --- | --- |
| Radial electromagnetic field | `(1, -1, 1)` |
| Balanced radial radiation | `(1, 1, 0)` |
| Angular radiation | `(1, 0, 1/2)` |
| Angular tensile membrane | `(1, 0, -1)` |
| Additional rest inventory | `(1, 0, 0)` |

Minimizing the sum of their energies gives the exact local requirement

```
rho >= max(p_r+2p_t, p_r-p_t, -2p_r-p_t).
```

For example, radial tension `p_r=-1` with zero angular stress costs at least
two units of energy: one in the radial field and one in the angular membrane
that carries its transverse reaction. This accounting already grants the
membrane its limiting stress-to-energy ratio. Currents, finite interfaces,
material response, and a physical restoring law add further requirements.

Approximately 99.4% of the coarse routed candidate's energy-weighted history
is under radial tension. The field/radiation/membrane construction exceeds
the available density by as much as 0.45940, and fails over 98.27% of that
energy-weighted history. The original unbounded generic candidate has the
same composition problem.

Reoptimizing all 27 material controls with this explicit component cone fails
for the original route. The first complete variable-route program reaches
its time limit. Constraint generation resolves that numerical uncertainty:
after checking all 332820 original inequalities, a subset of 2602 constraints
is infeasible. The direction fractions remain free in `[0,1]`, and the
material amplitudes have no imposed upper bound. This obstruction belongs
to the registered finite response family and component basis.

An independently checked certificate reduces that contradiction to 30
nonnegative weighted inequalities. The floating-point coefficients cancel to
`2.49e-16`, while their weighted right-hand side is `-0.00176574`. A subsequent
rational calculation treats every archived binary coefficient as its exact
dyadic value, obtains exact coefficient cancellation, and preserves the
negative right-hand side. The finite normalized matrix therefore requires
`0 <= -0.00176574`. The coefficient matrix and rational weights reproduce
this check directly. Its scope is the archived finite representation of the
response family, its component cone, and its bounded routing fractions.

## Re-solving the refined family

The final comparison regenerates every material and directional response at
256 cells and 515 time nodes. Constraint generation verifies up to 1455905
original inequalities while keeping the active optimization problem small.
This separates the loss of feasibility of old controls from the existence
of improved controls on the refined representation.

The generic separate-member family again fails at `f=0.9` and succeeds at
`f=0.99` and `f=1`. At `f=0.99`, the material null peak is 1.76512, initial
support inventory 7914.71, left-feed fraction 0.22749, and leftward recovery
fraction zero. Its original matrix violation is `1.68e-11`.

Independent continuous work reconstruction preserves its basic member-energy
gate. The weighted force and power residuals are 0.3752% and `1.33e-7`.
The minimum density is 0.04825, and the stress-to-energy fraction reaches
approximately 0.99130 between nodes. Thus the nominal 1% inventory reserve
becomes about 0.87% in that audit. Further continuum refinement remains a
numerical obligation for this target.

The explicit field/radiation/membrane family is also infeasible on the refined
representation. A subset of 3003 inequalities already conflicts, within a
full system of 1323550 rows. The refined generic target therefore gives a
stress schedule that passes necessary material-energy accounting, while the
tested physical component mixture supplies insufficient correlated stress.

The dominance of tension is consistent with the support force term
`(rho+p_r)a`: radial tension reduces the inertial force associated with its
prepared energy. A Maxwell realization simultaneously adds angular pressure,
which the backing must also carry. The refined field/membrane result counts
that angular reaction explicitly. Other constitutive stress correlations
remain separate physical hypotheses.

## Conserved radial prestress and continuing rail reactions

A constant amplitude `A` gives an exactly conserved increment

```
delta(rho,p_r,p_t) = (A/R^2, -A/R^2, 0).
```

Its radial null projection vanishes. Consequently it changes oblique null
stress and total inventory while preserving the radial enthalpy. This is a
mathematical adjustment of the support target; a physical radial material
and its termination still require construction.

Applied to the original refined support, the least member-admissible
amplitude is `A=2.49844`. It adds 11083.45 units of initial rest inventory.
The best attainable member fraction through this single adjustment is
approximately 0.998233. Its fade source remainder remains 3.18149, and its
end-jacket conditions still fail. Hence this radial-tension degree offers a
precise inventory tradeoff without closing the source or attachment problem.

For an angular termination jacket, surface energy `Y=R^2 sigma` and stress
`Z=R^2 tau` obey

```
a Y - 2k Z = epsilon R^2 jump,
dY = -2Z d(ln R),
|Z| <= Y.
```

The magnetic guide continues across the cut with matched traction; the
electric store, pressure medium, and backing contribute the remaining jump.
On the final reoptimized routed history, the left cut at fade demands
-4.99968, while
every positive-energy admissible jacket supplies force per unit energy in
`[0.57369,0.94360]`. This sign conflict persists at every sampled time. The
right cut requires an initial surface inventory simultaneously above 4273.66
and below 41.70 under adiabatic work evolution.

The active-rail disclosure assigns pre-existing radial tension and continuous
load paths to the standing substrate, and energy/momentum exchange to the
director/support reservoir. Its validated effective operators constrain
exchange shape and response. Its independent tensor and finite attachment
remain physical construction requirements. The present end loads belong to
those existing roles, with their energy and source contribution counted in
the same assembly. An isolated angular jacket supplies an inadequate
termination for the tested histories.

The recovered strong-tension requirement aligns with the disclosure's
dominant `S_0` scaffold role. This locates the remaining gap in the shared
standing-support realization: the electrode, pressure-link, and work-route
loads require a physical continuation of that tension-bearing structure.
Its target-ledger allocation supplies the role; its independently normalized
material tensor supplies the load-bearing capacity.

The session stops at this construction boundary. The useful numerical result
is a conservative, much more demanding backing target with quantified
momentum-routing freedom. Physical completion requires a material stress law
that supplies the correlated radial and angular loads, plus an explicit
continuation into the standing rail with counted work and stress. The tested
field/membrane mixture and isolated angular ends fail those roles. The
complete quantum stress and operating cycle remain part of the joint source
problem. These results delimit the tested assembly and response family.

## Evidence

The principal artifacts are the
[momentum-only gate](data/joint_route_momentum_gate),
[unbounded material responses](data/joint_response_relaxation),
[coupled material and routing family](data/joint_route_response),
[dense work audit](data/joint_dense_work_audit),
[fixed-control refinement](data/joint_routed_support_refinement),
[field/membrane comparison](data/joint_field_membrane_gate), and
[complete constraint check](data/joint_field_membrane_cuts). The final
[refined response family](data/joint_refined_response) and
[independent contradiction certificate](data/joint_field_membrane_certificate)
provide the review controls for the construction boundary.
The [exact rational certificate](data/joint_field_membrane_exact_certificate)
uses the same archived coefficient matrix.

The archived failures distinguish solver limits, finite-family infeasibility,
continuous material violations, and end-force/work obstructions. All final
acceptance statements retain that scope. The physical length remains free;
the stress fractions and comparison caps specify the numerical experiments.

Validation includes 28 passing focused tests for moving-frame force, coupled
elasticity, spacetime balance, surface work, implicit evolution, shape-safe
field allocation, dense energy reconstruction, composite field cost,
constraint generation, and infeasibility certification. The final rational
certificate is also checked by multiplying its exact weights into the
archived equations. Independent computational cases use up to four workers.
Final provenance verification passes 1239 input/output hash comparisons over
204 distinct files.
