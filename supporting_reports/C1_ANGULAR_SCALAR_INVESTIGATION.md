# C1 angular scalar: finite spectra and the cylindrical limit

17 September 2026.

A separate four-dimensional conformal scalar provides a concrete field
candidate for the existing angular signed-source role. Its finite-domain
mode calculation has positive lowest squared frequencies in all 574
registered comparisons on the retained C1 geometry. An independent
calculation in the original scalar variable confirms 44 selected spectra.
These results support constructing its stationary vacuum tensor alongside
the existing radial channels. The absolute tensor, material reflection law
and exterior state remain to be supplied.

The field's cylindrical limit has the required angular stress structure.
The native transition, however, has substantial radius and lapse derivatives.
The next source calculation therefore uses the full curved mode operator and
retains the angular field's finite boundaries and material exchange.

The subsequent [normalized response investigation](C1_ANGULAR_NORMALIZATION_AND_BOUNDARY_RESPONSE.md)
computes finite vacuum-stress differences and original-end load changes on
this geometry. Its useful throat response accompanies substantial confinement
burdens, motivating angular transparency through short radial compartments
and a joint absolute-state, material and exterior calculation.

## Component assignment and placement record

The [component ledger](RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md)
assigns angular signed stress separately from radial opening, ordinary angular
support and the transition/quantum environment. The scalar considered here is
a candidate within that assignment. The radial conformal channels retain
their own state, populations and reflector reactions from the
[signed-source comparison](C1_SIGNED_SOURCE_CHANNEL_SCREEN.md).

| Quantity | Treatment |
|---|---|
| Spacetime geometry | Unchanged: archived phase-0.745 lapse and spatial metric, with zero shift and time derivatives. |
| Electric source, material module domains and electric overlaps | Unchanged; broad overlap `[0.5,2.5]`, narrow overlap `[0.5,1]`. |
| Existing radial quantum placement and channel populations | Unchanged; the retained 32-compartment allocations remain separate inputs. |
| Existing radial quantum overlaps | Unchanged: `[0.55,2.45]` and `[0.55,0.95]`. |
| New trial angular field | One real massless four-dimensional scalar with curvature coupling `1/6`, separate from the radial channel fields. |
| Trial angular reflection | Dirichlet conditions at the inherited 1-, 8- or 32-compartment boundaries. The first two choices grant transparency to this field at the other radial reflectors. This introduces field-selective material-response assumptions. |
| Auxiliary spectral cuts | `[-4,4]`, `[-6,6]` and `[-8,8]`, with two boundary conditions for comparison. These cuts specify finite spectral problems; the physical exterior matching remains open. |
| Physical layout selection | Both C1 overlap brackets retain their previous standing. |

The 1- and 8-compartment boundaries are subsets of the 32-compartment
locations. Thus these trials add an angular field and change its assumed
reflection pattern while preserving the existing hardware coordinates.
Angular-field forces will add to the reflector and transition duties already
assigned to material components. Their magnitude requires the renormalized
field-and-material calculation.

## Field law and the angular-source connection

[Butcher's conformal scalar calculation, equation (59)](https://arxiv.org/pdf/1405.1283)
gives the cylindrical vacuum tensor

\[
(\rho,p_r,p_t)_\phi=
\frac{\eta N}{2880\pi^2R^4}
\left(-2\log(R/a_0),\ 2\log(R/a_0),\ 1-2\log(R/a_0)\right).
\]

Here \(N\) counts independent real fields and \(a_0\) is a fixed
renormalization length. The inherited conversion is
\(\eta=2.4127904527582454\times10^{-5}\). The logarithmic part has exactly
the directional structure of the existing angular target
\((-2v,2v,-2v)\). The additional angular term supplies the cylindrical
trace anomaly. Its radial null projection is zero; its angular null
projection is negative for \(\log(R/a_0)>1/4\).

This identifies a field candidate for the angular assignment while the
radial channels retain their opening role. The renormalization prescription,
field multiplicity and boundary response are shared physical inputs to its
eventual tensor. The present calculation keeps the cylindrical expression
as a limiting benchmark.

For the actual static metric
\(ds^2=-A^2dt^2+B^2dx^2+R^2d\Omega^2\), the proposed scalar action is

\[
S_\phi=-\frac12\int\sqrt{-g}\left[(\nabla\phi)^2+
\frac{\mathcal R}{6}\phi^2\right]d^4x.
\]

Write \(\phi=e^{-i\omega t}Y_{jm}u(x)/R(x)\) and define optical
distance by \(dy=B\,dx/A\). The radial eigenproblem is

\[
\left[-\frac{d^2}{dy^2}+V_j\right]u=\omega^2u,
\qquad
V_j=\frac{R_{,yy}}R+A^2\left[\frac{j(j+1)}{R^2}
+\frac{\mathcal R}{6}\right].
\]

The code evaluates \(\mathcal R\), the lapse and the radius derivatives
on the retained geometry. Linear finite elements use consistent mass
normalization \(\int (B/A)u^2dx=1\). In a constant-radius cylinder of
proper length \(d\), the exact Dirichlet spectrum is
\(\omega_{nj}^2=A^2[(n\pi/d)^2+(j(j+1)+1/3)/R^2]\).
This provides an independent normalization and convergence check.

Since \(V_j-V_0=A^2j(j+1)/R^2\geq0\), the lowest angular harmonic
controls the bottom of the spectrum for common boundary conditions.
Higher harmonics remain necessary when summing the quantum stress.

## Finite-domain spectral results

The calculation compares 1, 8 and 32 compartments per module, three spatial
resolutions, metric downsampling controls and explicit higher-harmonic
checks. The finest lowest squared frequencies are:

| Layout | Complete left module | Complete right module | Minimum across its 32-compartment modules |
|---|---:|---:|---:|
| Broad | 2.588779 | 2.589718 | 190.364001 |
| Narrow | 2.588756 | 2.589718 | 369.001308 |

Frequencies refer to the unchanged coordinate time. Constant clock rescaling
changes their numerical squares by the clock factor squared and preserves
their signs. The 32-compartment geometry strengthens the positive spectral
gap. Complete-module spectra already have positive lowest modes, so this
field's spectral condition alone selects neither compartment count nor
overlap bracket.

The auxiliary cuts supply a separate extent comparison:

| Auxiliary interval | Dirichlet \(u=0\) | Natural \(u_{,y}=0\) |
|---|---:|---:|
| `[-4,4]` | 0.849591 | 0.128679 |
| `[-6,6]` | 0.275926 | 0.056683 |
| `[-8,8]` | 0.143871 | 0.032859 |

The natural condition acts on \(u=R\phi\); it corresponds to a Robin
condition on the original scalar. Its larger variational domain provides
the lower finite-interval comparison. Increasing the interval softens the
lowest mode. Exterior continuation and its state determine the global
spectrum and vacuum response.

## Where the cylindrical limit helps

The local indicators are

\[
\epsilon(x)=\max\left(|R'|,\ |R(\log A)'|,\ |RR''|,
\left|R^2A''/A\right|\right),
\]

with proper-distance derivatives. Constant-radius, constant-lapse geometry
has \(\epsilon=0\). These dimensionless quantities locate slowly varying
regions; they provide a diagnostic for a derivative expansion. Finite-boundary
and nonlocal state effects require the complete mode problem.

At the throat \(\epsilon\simeq0.01185\). At \(x=\pm2.5\),
\(|R'|\simeq0.4702\), \(|R(\log A)'|\simeq2.0179\),
\(|RR''|\simeq1.8556\), and \(|R^2A''/A|\simeq17.3902\).
Thus the same field can encounter nearly cylindrical bulk regions and a
strongly varying transition on this metric.

Weighting these regions by the previous angular target's proper energy gives:

| Layout | Target energy magnitude | Fraction at \(\epsilon\leq0.1\) | Fraction at \(\epsilon>1\) |
|---|---:|---:|---:|
| Broad | 38.057681 | 83.76% | 10.51% |
| Narrow | 35.550566 | 89.96% | 1.96% |

The thresholds are declared diagnostic cuts. These fractions describe the
location of the assigned target; the scalar's supplied stress fraction remains
to be calculated. In particular, substituting the cylindrical formula at each
local radius leaves the transition's curved spectrum and finite-boundary
response unresolved. That substitution is itself conserved in the bulk,
which makes the separate geometry and state checks consequential.

## Construction consequence

The angular scalar has a specified action, an implemented curved spectral
operator and positive finite-domain mode evidence. Continue to its
renormalized four-dimensional stress and the reciprocal force on the
reflecting/transition material, using one fixed renormalization prescription.
Combine that tensor with the retained radial channels, Maxwell source and
separately supplied material components. Both field orientations contribute
their complete tensors to that common equation.

The transition and quantum-environment role retains exterior matching. A
field-selective reflector must supply its response to both quantum sectors,
its material stress and their combined reaction loads. These requirements
belong to the existing component construction. The new scalar candidate
introduces no mandatory architectural role or change of C1 preference.

## Validation and reproduction

Twenty-eight focused tests pass: eight new scalar tests and twenty inherited
C1 channel/module tests. The scalar checks include the exact cylinder
spectrum, four-dimensional conformal covariance, angular spectral ordering,
clock rescaling, virtual-work pressures, conservation and mode normalization.

The independent audit uses the original scalar \(\phi\), its radial
finite-volume operator and the Einstein trace for curvature. Its 44 selected
comparisons cover all 22 stored mode sets at two independent resolutions.
Four additional analytic cylinder/conformal-rescaling controls agree within
\(4.70\times10^{-7}\) fractionally. Across the retained spectra, the largest
independent difference is \(4.57\times10^{-5}\), the finest mesh change is
\(1.35\times10^{-4}\), and the metric-sampling change is
\(7.45\times10^{-9}\). The largest relative matrix eigen-residual is
\(4.31\times10^{-9}\). Every retained sign survives these controls.

The production run uses four worker processes and takes 2.49 seconds. It
checks 37 parent hashes; the independent audit checks 44 current source,
input and artifact hashes. The [summary](data/c1_angular_scalar/summary.json),
[spectra](data/c1_angular_scalar/spectra.csv),
[verification](data/c1_angular_scalar/verification.json) and
[manifest](data/c1_angular_scalar/manifest.json) retain the numerical record
and execution-source snapshots. The narratives are written manually.

Reproduction uses a fresh output directory:

```bash
PYTHONPATH=toolkit/adm_harness_cli \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python toolkit/adm_harness_cli/scripts/screen_c1_angular_scalar.py \
  --workers 4 --output /tmp/c1-angular-repeat

PYTHONPATH=toolkit/adm_harness_cli \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python toolkit/adm_harness_cli/scripts/audit_c1_angular_scalar.py \
  --workers 4 --output /tmp/c1-angular-repeat

PYTHONPATH=toolkit/adm_harness_cli \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
python -m pytest -q \
  toolkit/adm_harness_cli/tests/test_c1_angular_scalar.py \
  toolkit/adm_harness_cli/tests/test_c1_signed_channels.py \
  toolkit/adm_harness_cli/tests/test_c1_module_overlap.py
```
