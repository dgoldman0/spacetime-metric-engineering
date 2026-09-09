# Coupled source roles and the origin of their different loads

Date: 9 September 2026.

The rail's existing source architecture separates standing radial support,
endpoint angular response and transport, and support-reservoir exchange.
The recent scalar–Higgs–gauge plus neutral-quantum-field construction realizes
a restricted allocation of those jobs. At the smooth throat, its relaxed
classical material carries 0.612% of the demanded radial tension. The assigned
quantum remainder therefore carries 99.388%, as well as the required negative
radial null stress and the angular remainder. This allocation asks the quantum
sector to supply most of the bulk throat support.

The original differentiation remains essential to selecting a broader coupled
construction. The measured quantum shortfall applies to the tested source and
its nearby fixed-profile metric update. Its negative-null-stress bound also
survives adding ordinary components with nonnegative null stress. A new source
allocation must address both the bulk support assignment and this independent
opening requirement.

## The source roles already identified

The [component-source ledger](STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md)
separated infrastructure radial-null support, core radial-pressure balance,
infrastructure angular capacity, live angular/current handling, live pressure
and null-stress adjustments, and a reset current sink. These were assignments
of demanded stress. Subsequent work developed the
[endpoint source law](STAGE2_BETA075_SOURCE_LAW_DEFINITION_PACKAGE.md) around an
anisotropic heat-current medium, a radial director, and a localized support
reservoir with explicit exchange.

The later tests retained several parts of this differentiation:

| Investigation | Explicit source organization | Remaining construction requirement |
| --- | --- | --- |
| [Comer current evolution](COMER_TWO_CURRENT_EVOLUTION_ROUND.md) | Independent particle and entropy currents, resistance, and a separately conserved radial-tension source | A physical support sector satisfying the initial rail junction |
| [Vacuum support selection](VACUUM_SUPPORT_SELECTION_ROUNDS.md) | Separate radial and angular vacuum orientations, ordinary-current preload, and a counted host-material remainder | A healthy material and quantum realization of the algebraic tensor fit |
| [Screened condensate](SCREENED_SCALAR_CONDENSATE.md) | Matter scalar, Higgs field, and gauge field supplying screening, stress, and a finite transition | Regular continuation and the complete quantum remainder |
| [Smooth semiclassical calculation](SEMICLASSICAL_JOINT_INVESTIGATION.md) | The condensate action and one minimally coupled neutral scalar, coupled through the Higgs amplitude | Sufficient absolute quantum stress for the prescribed smooth geometry |

Thus the recent calculation contained several fields, while restricting their
relative responses through one material action, one selected branch, and one
quantum state. The endpoint medium and reservoir were absent as independent
dynamical sectors in that static test. The earlier independently weighted
radial and angular vacuum patterns were replaced by the tensor of the single
neutral scalar. The resulting limitation concerns this restricted realization
of the support problem.

## The actual allocation at the throat

The audit reads the saved relaxed material from the bounded semiclassical
investigation and uses its registered gravitational conversion
\(\eta=2.41279045\times10^{-5}\), material scale \(v=12/6.8\), and frequency
\(\omega=0.8528237074\). All entries below use geometric source units; the
material tensor includes \(\eta v^4\). The quantum remainder is the required
difference, distinct from the computed quantum supply.

| Channel at \(R_0=2.0395751\), \(A_0=69.343216\) | Geometry demand | Relaxed material | Assigned quantum remainder |
| --- | ---: | ---: | ---: |
| Energy density \(\rho\) | \(9.56354\times10^{-3}\) | \(5.85000\times10^{-5}\) | \(9.50504\times10^{-3}\) |
| Radial pressure \(p_r\) | \(-9.56491\times10^{-3}\) | \(-5.84981\times10^{-5}\) | \(-9.50641\times10^{-3}\) |
| Angular pressure \(p_t\) | \(3.26418\times10^{-5}\) | \(-5.85000\times10^{-5}\) | \(9.11418\times10^{-5}\) |

The potential-dominated condensate selected by the enclosing radial load is
far below the bulk throat tension scale. Its angular tension also increases
the positive angular pressure assigned to the quantum remainder at this
point. The scalar's measured five-order integrated opening deficit concerns
\(\rho+p_r\); it is a separate failure from this allocation of bulk tension.

An ideal radial-tension contribution \(I(1,-1,0)\) can remove equal amounts
of the positive-density and radial-tension remainder. It leaves
\(\rho+p_r\) unchanged. If separately conserved and static, this ideal pattern
requires \(I\propto R^{-2}\). A varying flux or termination requires angular
stress or exchange with other components. Consequently a bulk allocation
also specifies its continuation through the interfaces.

## Why the geometry asks for different responses

The static support study uses proper distance \(l\), areal radius \(R(l)\),
and lapse \(A(l)\):

\[
ds^2=-A^2dt^2+dl^2+R^2d\Omega^2.
\]

Primes denote proper-distance derivatives. Define

\[
X=\frac{A''}{A},\qquad Y=\frac{A'R'}{AR},\qquad
Z=\frac{R''}{R},\qquad W=\frac{1-R'^2}{R^2}.
\]

The exact geometric source is

\[
8\pi(\rho,p_r,p_t)
=W(1,-1,0)+Z(-2,0,1)+Y(0,2,1)+X(0,0,1).
\]

These terms describe distinct curvature contributions. Their sum is the
conserved tensor; the displayed pieces acquire physical component meanings
only through a source model and its exchange equations.

**Finite radius and opening.** At a smooth minimum of radius,
\(R'=0\), the radial pressure is \(-1/(8\pi R_0^2)\). This creates the large
radial-tension job. A strict minimum also has \(R''>0\), giving
\(\rho+p_r=-R''/(4\pi R_0)<0\). Tension and opening are therefore different
requirements even at the same location. The former can have positive density
and zero radial null stress; the latter requires a negative null contribution.

**Clock shape and angular stress.** Clock curvature enters \(p_t\) through
\(X\), while its overlap with radius variation enters through \(Y\). Equivalently,

\[
(R^2A')'=4\pi R^2A(\rho+p_r+2p_t).
\]

A strict interior lapse maximum needs a negative value of this source there.
Positive potential energy can provide that sign while saturating both null
conditions. Thus the clock requirement is distinct from the opening
requirement. The active rail's clock enhancement, proper-distance stretch,
capacity profile, and packet/receiver shaping encode separate service choices
in [the geometry kernel](../toolkit/adm_harness_cli/adm_harness/source_ledger.py).
Their spatial derivatives create different stress demands as those profiles
overlap and return toward their exterior values.

**Transitions and force balance.** Static conservation requires

\[
p_r'+\frac{A'}A(\rho+p_r)+2\frac{R'}R(p_r-p_t)=0.
\]

Changing the radial load or ending a support profile therefore couples the
angular response, clock gradient, and radial enthalpy. This is the origin of
the repeated boundary-load problem. A component that fits a bulk pressure
pattern still needs the appropriate transition and exchange response.

**Startup and transport.** The earlier
[startup expansion](LE_RESET_INVERSE_SEARCH.md) found an angular demand at
order \(u^{n-2}\), while the initially empty moving-material sector produced
angular stress at order \(u^{2n-2}\). This established a need for initial
stored material state and an earlier stress response within those prescribed
startup families. Particle/entropy transport and support preload therefore
remain separate dynamical jobs. The present static audit evaluates their
initial support background; their evolution still requires the current and
exchange equations.

## Where the static opening requirement lies

For the saved smooth geometry, define

\[
B_-=4\pi\int \frac{R}{A}\max[-(\rho+p_r),0]\,dl.
\]

The following intervals use the existing rail coordinate \(x\). They are
integration bins. Physical interfaces continue to require field-defined
locations and gradients.

| Coordinate region | Negative radial-null balance \(B_-\) | Fraction of total |
| --- | ---: | ---: |
| \(|x|\leq2\) | 0.0770001 | 3.31% |
| \(2<|x|<3\) | 1.5791410 | 67.92% |
| \(3\leq|x|\leq40\) | 0.6689162 | 28.77% |
| Complete interval | 2.3250573 | 100% |

The signed opening balance is 2.1765898; positive radial-null regions reduce
it from \(B_-\). The exact identity

\[
\left(\frac{R'}A\right)'=-4\pi\frac RA(\rho+p_r)
\]

independently reproduces that signed integral from the endpoint data. About
96.69% of the negative part lies outside \(|x|\leq2\). Bulk throat matching
alone therefore addresses a small fraction of this integrated null-stress
requirement. Angular null stress also becomes negative in part of the outer
profile: at \(x=-4\), \(\rho+p_t\simeq-2.2397\times10^{-4}\).

The detailed distribution belongs to this retained, smoothed static geometry.
Its negative-side exterior is the solved condensate exterior, while its
positive far tail inherits \(R=\sqrt{x^2+1.75^2}\) with constant lapse. That
tail itself requires negative radial null stress. Source selection can
therefore distinguish necessary throat properties from the adjustable taper,
clock, and exterior-completion choices. A revised profile also has to satisfy
the rail's operational constraints.

## Consequences for component selection

The canonical condensate has positive time kinetic, spatial gradient,
potential, and radial electric energies \(K,D,V,E\), with

\[
(\rho,p_r,p_t)=(K+D+V+E,\ K+D-V-E,\ K-D-V+E).
\]

Its radial and angular null stresses are \(2(K+D)\) and \(2(K+E)\).
Combining ordinary positive-kinetic components preserves their nonnegative
null contributions. However, their different pressure patterns can distribute
the bulk and clock loads: radial electric energy has positive angular
pressure, potential energy has angular tension, and radial string tension
has small angular stress in its ideal limit.

The proposed local combination
\(E(1,-1,1)+V(1,-1,-1)+q(1,1,0)\) illustrates both the useful split and its
limits. Here \(q\) is a signed, traceless longitudinal stress coefficient.
At the throat its formal coefficients are positive
\(E\simeq0.0047984\), \(V\simeq0.0047658\), with
\(q\simeq-6.8201\times10^{-7}\). At \(x=-4\), the same inversion instead
requires \(V\simeq-0.00058774\), outside the positive-potential family.
Around \(x=3\), \((\rho-p_r)/2<0\); positive \(V+E\) cannot supply that
combination. Adding positive \(K,D\) leaves this latter mismatch unchanged.
The quantum tensor or the local geometry must carry an additional response.
These conclusions concern the displayed local basis. Curvature, trace
anomalies, and transverse modes extend its quantum stress pattern.

The next component selection can therefore retain the established roles:

| Required response | Physical ingredients to assess | Coupled condition |
| --- | --- | --- |
| Bulk positive energy and radial tension | Radial flux, tension medium, and potential-dominated material | Carry a stated fraction of the bulk load while counting their angular and interface stresses |
| Radial and angular negative null stress | Specified quantum modes and states with the required directions and spatial placement | Supply both residual null channels across the transitions with absolute normalization |
| Finite transition, optical confinement, and restoring force | Existing condensate fields, or an additional material degree of freedom with a defined coupling | Match mechanical and optical response and retain a healthy perturbation spectrum |
| Angular/current handoff and reset exchange | The anisotropic endpoint medium and Comer particle/entropy currents with stored support state | Evolve the initial preload, exchange, and service conditions consistently |

These are physical jobs; a suitable component can perform several. In the
current condensate, the same Higgs amplitude controls potential energy,
positive gradient energy, and the neutral scalar's mass. This ties mechanical
load and optical confinement together. An additional field is useful when its
coupling provides independent control of a response that this relation locks,
with its own energy and force included in the complete tensor.

A next candidate should specify its share of the original source roles before
solving its fields. The required quantum remainder then follows from the
counted classical support, and can be screened in all tensor channels and
spatial regions. The earlier source-role assignments supply that design map;
their microscopic realization and common exchange law supply the construction
problem. The neutral scalar's measured opening deficit remains a restriction
on retaining that particular quantum mechanism near the present geometry.

## Reproduction and controls

The [audit script](../toolkit/adm_harness_cli/scripts/audit_coupled_source_roles.py)
uses four workers and the saved geometry and relaxed material. It performs no
new field solve. Independent exact controls cover Minkowski space, a
constant-radius cylinder, the ultrastatic Ellis throat, and a de Sitter static
patch. Proper-distance quadrature uses 30,001 and 60,001 points per band. The
largest negative-balance relative change is \(6.47\times10^{-7}\), and the
largest signed-integral discrepancy from the endpoint identity is
\(2.68\times10^{-12}\). The static conservation and lapse identities close
at floating-point precision.

The [numeric audit](data/coupled_source_roles/audit.json),
[band integrals](data/coupled_source_roles/bands.csv), and
[tensor allocations](data/coupled_source_roles/witnesses.csv) retain the
normalizations, source hashes, and checks. Serial and four-worker executions
produce identical numerical tables. The evidence run takes under one second
and retains approximately 13 kB. This report is written manually.

```bash
PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 toolkit/adm_harness_cli/scripts/audit_coupled_source_roles.py --workers 4
```
