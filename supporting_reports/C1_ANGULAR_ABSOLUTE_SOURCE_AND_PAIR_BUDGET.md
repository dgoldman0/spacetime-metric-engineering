# C1 angular scalar: absolute bulk stress and a shared pair budget

17 September 2026.

The whole-module angular scalar supplies a useful, physically normalized
bulk contribution in specified parameter cases. On the retained geometry,
fixed global curvature-coupling choices with
\(\ell_0=\log(R_0/a_0)=2\) or \(4\) admit an ordinary-material remainder
at the throat and the sampled broad-overlap point, together with the retained
Maxwell and radial quantum sources. The logarithm-1 benchmark helps at the
throat but has the wrong stress structure in the overlap.

This establishes a conditional bulk contribution and a reason to continue
the angular field. The complete module cost still includes its end material,
exterior state, transition profile and recoil. The field multiplicity is
substantial: the logarithm-2 case requires about 25 million independent real
fields in the throat-bearing population. Its microscopic realization and
physical curvature couplings remain source-construction inputs.

## Retained construction and explicit changes

The [source-feasibility workflow](SOURCE_FEASIBILITY_WORKFLOW.md) and
[C1 topology decision](RAIL_BUILD_TOPOLOGY_DECISION.md) govern this comparison.
The separate radial, angular, ordinary-material, transition and exchange
duties remain assigned to their respective components.

| Quantity | Treatment |
|---|---|
| Geometry | Retained phase-0.745 static surrogate. Radius, lapse and radial scale are unchanged. |
| Source placement | Retained Maxwell populations, material module extents and inset quantum module endpoints. |
| Overlap | Retained broad electric overlap \([0.5,2.5]\) and narrow comparison \([0.5,1]\). The pair budget here samples the broad overlap at \(x=0.75\). |
| Radial source | Retained 32-compartment populations and their independently allocated strengths. |
| Angular field extent | Whole original module interiors: broad left \([-2.95,2.45]\), narrow left \([-2.95,0.95]\), shared right \([0.55,2.95]\). |
| Angular coupling change | Internal radial reflectors are transparent to the angular scalar. Its two original module ends impose Dirichlet reflection. |
| Population assignment | Independent left and right angular populations, each transparent to the other population's material boundaries. |
| Absolute normalization | Fixed covariant bulk prescription, followed by separately declared global \(\ell_0=0.5,1,2,4\) parameter cases. Each case has one spatially constant \(a_0\). |
| Numerical geometry representation | Higher-order interpolation of the same metric samples supplies curvature derivatives. Fresh evaluations of the original metric check those derivatives. |
| End/exterior accounting | The interior ground state is specified by the ideal reflecting ends. Exterior stress, surface self stress and the finite material action remain separate entries. |

Thus the trial changes angular coupling at existing locations and compares
global source parameters. Geometry, physical endpoint coordinates, radial
populations and overlap widths stay fixed. The narrow throat comparison
checks sensitivity to the inherited endpoint bracket; its full pair budget
retains a separate construction requirement.

## Absolute state and normalization

The field is a real, massless four-dimensional scalar with curvature coupling
\(\xi=1/6\), in the static ground state inside its module. The inherited
source conversion is

\[
\eta=2.4127904527582454\times10^{-5},\qquad
S_\phi=\eta N\langle T_\phi\rangle_{\rm one\ real\ field}.
\]

\(N\) counts independent real fields in this model. The computed single-field
tensor fixes its meaning and scale. Realizing an equivalent multiplicity
requires a microscopic source law with the same tensor and counted costs.

The bulk prescription fixes flat vacuum energy and the measured Newton
coefficient. For conformal coupling, the heavy-field term proportional to
\(m^2\mathcal R\) vanishes. Define the conserved local tensor \(H_{\mu\nu}\)
by variation of the action density

\[
\frac{3\mathcal R_{\alpha\beta}\mathcal R^{\alpha\beta}
      -\mathcal R^2}{5760\pi^2}.
\]

The finite coupling in this direction is calibrated on the exact infinite
product cylinder. The second independent finite curvature coupling is zero
in this prescription. The trace convention is

\[
\langle T^\mu{}_\mu\rangle
=\frac{\mathcal R_{\alpha\beta\gamma\delta}
             \mathcal R^{\alpha\beta\gamma\delta}
        -\mathcal R_{\alpha\beta}\mathcal R^{\alpha\beta}
        +\Box\mathcal R}{2880\pi^2}.
\]

This is the conformal heat-kernel coefficient; a finite
\(\mathcal R^2\) coupling changes the total-derivative term.
[Bertolini and Casarin, equations (2)–(4)](https://arxiv.org/pdf/2406.12464)
give this convention. Keeping that coupling fixed makes the native geometry
comparison definite.

At \(R_0=2.039574013320285\), the logarithm-1 calibration reproduces

\[
T_{\rm cyl}=
\frac{1}{2880\pi^2R^4}
(-2\ell,\ 2\ell,\ 1-2\ell),\qquad
\ell=\log(R/a_0).
\]

This is the [exact cylinder result](https://arxiv.org/pdf/1405.1283),
equation (59). The calculation uses it to calibrate one constant coupling
and to improve numerical subtraction. The curved tensor comes from the
native radial Green problem.

For regulator masses \(m_i^2=iM^2\) and weights
\(c_i=(1,-3,3,-1)\), the calibration coefficient at unit reference
renormalization mass is \(c_{\rm fin}=1.6579842278828654\).
Writing \(\Delta T_{\rm PV}\) for native minus cylinder stress at the same
local radius and clock, the finite-regulator control is

\[
T(M)=T_{\rm cyl}^{\rm calibrated}
     +\Delta T_{\rm PV}(M)
     +(c_{\rm fin}-c_{\log})(H_{\rm native}-H_{\rm cyl}),
\qquad
c_{\log}=-\log M^2+3\log2-\log3.
\]

The common cosmological subtraction cancels in the difference. The full
native curvature tensor remains in the subtraction and finite calibration.
An analytic frequency integral and accelerated angular sum supply the
independent cylinder limit.

Changing the declared global normalization gives the exact finite shift

\[
T(\ell_0)=T(1)-2(\ell_0-1)H_{\rm native}.
\]

This compares different fixed physical curvature couplings. It preserves
covariance and uses the same constant at every point and in both populations.
The corresponding \(a_0\) values are approximately \(1.2371,\ 0.7503,\
0.2760,\ 0.03736\) in the retained length units.

The scalar coupling \(\xi=1/6\) stays fixed in every case. The varied
constant belongs to the finite curvature-squared part of the effective
action. In a semiclassical equation written schematically as

\[
\frac{G_{\mu\nu}}{8\pi G}+\alpha H^{(1)}_{\mu\nu}
 +\beta H^{(2)}_{\mu\nu}
=T^{\rm ren}_{\phi,\mu\nu}+T_{{\rm other},\mu\nu},
\]

a change of subtraction convention is accompanied by a compensating change
of \(\alpha,\beta\). The total balance is invariant. Here the retained
Einstein demand is held fixed, so the different \(\ell_0\) cases represent
different physical assignments of the finite effective-action couplings,
with those terms placed in the source ledger. The favorable cases therefore
require those physical couplings; changing a subtraction label alone supplies
no additional stress. A material mechanism for adjusting the couplings has
yet to be established.

## Native Green calculation and controls

Set \(dl=B\,dx\), \(a=\log A\), and \(\chi=\sqrt A\,R\phi\).
At a probe with lapse \(A_*\), use local Euclidean frequency \(w=\zeta/A_*\).
The continuum radial equation is

\[
\chi''=q_{wjm}\chi,\qquad
q_{wjm}=\frac{A_*^2}{A^2}w^2+\frac{j(j+1)}{R^2}+m^2
 +\frac{R''}{R}+\frac{a''}{2}+\frac{a'^2}{4}
 +\frac{a'R'}R+\frac{\mathcal R}{6}.
\]

Two solutions satisfy the original left and right Dirichlet conditions.
Their logarithmic derivatives give the diagonal Green function and its
separated-point derivatives. The improved scalar stress is integrated with
measure \((2j+1)\,dw/(4\pi^2)\). The radial solver works in the continuum;
the metric interpolation, shooting step, frequency rule, angular cutoff
and regulator mass have separate controls.

The production sweep has 22 cases. Further checks increase the overlap
regulator masses, compare an independent equation for
\(\phi/\phi_l\) in the original coordinate, and evaluate the bulk
conservation identity. Nine independent mode comparisons agree within
\(2.3\times10^{-9}\) of the native-minus-cylinder tensor norm. The
radius-scaled conservation residual at the overlap is
\(4.1\times10^{-5}\).

At the throat, halving the shooting step and increasing frequency order
change each tensor component by less than \(4.8\times10^{-14}\) in
unconverted one-field units. The combined metric-sampling and interpolation
control changes the largest component by \(4.9\times10^{-12}\).
The extrapolated trace differs from the local anomaly by
\(1.9\times10^{-11}\). These controls support the normalized throat scale;
the smaller curvature correction and radial-null projection carry greater
relative uncertainty. Population counts below are rounded accordingly.

Cutoff extrapolation uses the observed inverse fourth-power tail, with
separate larger-cutoff cases at regulator masses 2 and 4. Regulator
extrapolation compares linear and quadratic fits in \(M^{-2}\).
The larger overlap masses are especially relevant near the right module's
original boundary, where finite regulator reflection persists longer.
The overlap audit extends the regulator scale to \(M=16\), using both
cutoff multipliers 16 and 32. The left and right extrapolated trace residuals
are \(5.8\times10^{-8}\) and \(3.4\times10^{-6}\), respectively, in
unconverted one-field units. The right-state tensor is correspondingly
less precise; its largest linear/quadratic fit difference is
\(1.2\times10^{-6}\).
The [audit](data/c1_angular_absolute/audit.json) records those comparisons,
their trace residuals and all retained individual tensors.

The original metric has repaired joins with finite differentiability.
The sampled throat and overlap points lie on smooth portions. A complete
spatial source construction must specify the joins' higher-derivative or
interface treatment before integrating a global absolute stress ledger.
The current computation applies no physical smoothing to those joins.

## Combination with the retained sources

At the throat, after the retained Maxwell and radial quantum contributions,
the required remainder is

\[
S_{\rm rem}(0)\simeq
(0.000477588,\ -0.000477499,\ -0.009054029).
\]

The logarithm-1 absolute angular tensor per real field, including \(\eta\),
is approximately

\[
S_{\phi,1}(0)\simeq
(-9.81087,\ 9.81077,\ -4.90561)\times10^{-11}.
\]

It supplies the required angular-null sign and scale. Its small native radial
correction remains compatible with the fixed radial allocation at the
population needed for the angular duty.

At the overlap witness \(x=0.75\), the retained remainder is

\[
S_{\rm rem}(0.75)\simeq(0.0774401,\ 0.1077563,\ 0.0080129).
\]

Ordinary completion requires all four projections
\(\rho+p_r,\rho-p_r,\rho+p_t,\rho-p_t\) of the remaining tensor
to be nonnegative. In particular, this witness already requires a negative
contribution to \(\rho-p_r\), whose target value is \(-0.0303162\).
Both logarithm-1 whole-module angular populations supply a positive
contribution in that channel. Their independent nonnegative multiplicities
therefore cannot complete this witness with ordinary material.

For the throat-normalized left population, the logarithm-1 overlap remainder
is approximately

\[
(-0.1433,\ 0.1183,\ -0.03245).
\]

This failure concerns the specified field state, curvature couplings and
fixed retained sources. It identifies a spatial source burden in the
existing angular/transition assignment. Changing that assignment, its
state, the radial allocation or the geometry would define a new comparison.

The global coupling cases separate the outcome:

| Fixed \(\ell_0\) | Throat population scale | Throat and overlap bulk comparison |
|---|---:|---|
| 0.5 | About 174.8 million | Overlap stress has the wrong sign. The central throat estimate also exceeds the radial margin. |
| 1 | About 58.28 million | Useful throat contribution; overlap fails for every nonnegative neighboring population. |
| 2 | About 24.98 million | The sampled overlap allows approximately 0–8.9 million neighboring fields at the central minimum left population. Equal module populations exceed that interval. |
| 4 | About 11.66 million | Both sampled points admit ordinary completion, including an equal-population comparison. |

The population bounds describe two bulk witnesses. A spatial scan, a supplied
material tensor and finite interfaces determine the admissible construction
beyond those witnesses. In particular, an unrestricted population bound at
one point grants no unrestricted assembly inventory.

A rounded logarithm-2 comparison uses \(N_L=25.1\) million and \(N_R=5\)
million. Its required ordinary bulk remainders are approximately

\[
S_{\rm ordinary}(0)=(0.00540273,-0.00540250,-0.00536017),
\]
\[
S_{\rm ordinary}(0.75)=(0.11942444,0.11467556,0.06429605).
\]

All four projections are positive. The smallest throat margin is
\(2.29\times10^{-7}\); the smallest overlap margin is \(0.00475\).
The [sensitivity assessment](data/c1_angular_absolute/assessment.json)
perturbs each unconverted one-field component by \(3\times10^{-11}\)
at the throat, \(3\times10^{-7}\) in the left overlap state and
\(6\times10^{-6}\) in the right overlap state. These empirical envelopes
exceed the observed numerical controls. The corresponding worst-case
projection margins remain positive, approximately \(1.93\times10^{-7}\)
and \(0.00294\). A logarithm-4 comparison with 12 million fields per
population also retains positive margins under these envelopes.

These are numerical sensitivity checks for the supplied ideal-field bulk
tensors. The physical uncertainty in achievable multiplicity, curvature
couplings and material response is a separate construction question.

## Boundary/material ledger and next construction

The transparent internal walls carry the retained radial duty. The extra
angular reflection increments measured in the
[previous response comparison](C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md)
are absent in this trial. The absolute bulk contribution above survives
that change.

The original ends retain their angular interaction, surface and exterior
terms. A Dirichlet condition fixes the interior mathematical state, while
the total end traction requires the exterior state and a physical boundary
action. Curved ideal boundaries generally have ultraviolet-sensitive
self energies that gravitate; the material response determines their
completion.
[Mazzitelli, Nery and Satz](https://arxiv.org/abs/1110.3554)
treat this issue through a scalar field coupled to a material background.

The finite ledger therefore contains:

| Entry | Current content |
|---|---|
| Maxwell and radial bulk stress | Retained source laws and populations, counted once. |
| Angular bulk stress | Absolute interior values at the throat and broad-overlap witness, with fixed global parameter cases. |
| Ordinary bulk remainder | Necessary local energy-condition budget; material realization remains to be supplied. |
| Internal radial interfaces | Retained radial loads; angular transparency is a material-response assumption. |
| Original angular ends | Interior state specified; self/material action, exterior pressure and full force remain open. |
| Transition and exterior source | Separate existing duties, including geometry joins and source coverage beyond the sampled points. |
| Momentum and recoil | Complete end and field exchanges are inputs to the mechanically independent assembly dynamics. |

Continue the logarithm-2 and logarithm-4 cases as conditional source
requirements. First place the microscopic multiplicity, finite
curvature-squared couplings and exterior populations in one physical source
accounting. That identifies which parameter cases warrant the full spatial
bulk and finite end/material calculation. The field-state contribution and
the finite effective-action terms remain separately visible. A measured
transition or end burden can motivate an explicit change of source extent,
overlap or geometry under the agreed workflow.

The useful bulk result supports this source investigation. Detailed fixtures
and deployment optimization follow a credible finite material/exchange budget.

## Reproduction

The [specification](../toolkit/adm_harness_cli/specs/c1_angular_absolute.json),
[production data](data/c1_angular_absolute/summary.json),
[production manifest](data/c1_angular_absolute/manifest.json) and
[independent audit](data/c1_angular_absolute/audit.json) preserve the state,
regulator controls, harmonic sums, source reconstruction and execution hashes.
Both drivers support four independent workers with one BLAS thread per worker.
The continuum kernel requires a C compiler; its source is included in the
Python package.

From the repository root, use an empty output directory:

    PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
      python toolkit/adm_harness_cli/scripts/screen_c1_angular_absolute.py \
      --workers 4 --output /tmp/c1-angular-absolute-reproduction
    PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
      python toolkit/adm_harness_cli/scripts/audit_c1_angular_absolute.py \
      --workers 4 --data /tmp/c1-angular-absolute-reproduction
    PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 \
      python toolkit/adm_harness_cli/scripts/assess_c1_angular_absolute.py \
      --data /tmp/c1-angular-absolute-reproduction

The focused tests include exact cylinder images, local clock normalization,
regulator linearity and decoupling, analytic coordinate transformations,
curvature variation and the independently summed cylinder anomaly.
The complete focused suite passes 51 tests across this calculation and the
retained angular, radial and finite-pair components.
