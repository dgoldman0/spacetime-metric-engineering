# Bounded Reset Construction Search

Date: 8 September 2026.

## Registered question and acceptance conditions

This search seeks a local spherical reset whose mass history, transfer current,
material stresses, and Einstein tensor agree. The preceding
[single source trial](LE_COUPLED_RESET_SOURCE_ATTEMPT.md) fixed the ordinary
material density equal to transfer density. Its source retained Type IV stress
and required more mass than its stationary geometry allowed. Here, a changing
reservoir state determines a mass redistribution; the field equations then
determine the current and the material energy remaining after transfer costs.

The construction is a necessary local relaxation of the beta075 V=5 reset.
It retains the matched-static initial and final reference profiles, their inner
and outer mass histories, and the resulting net mass transfer. The active
rail metric and source kernel remain the reference outside this calculation.
Full matching to the original time-dependent worldtubes and the V=5 service
checks are required for any survivor. A local solution alone supplies an
endpoint construction candidate. Its microscopic signed-source realization
remains the existing constitutive question.

Acceptance requires nonnegative ordinary material and null-stream densities,
an admissible complete stress tensor, a positive stationary areal metric,
agreement with all four independent Einstein channels, conserved total
exchange, and the stated endpoint and matching conditions. Regular null
transfer is permitted. Negative ordinary density, a stable Type IV witness,
or a finite angular Einstein mismatch rejects a candidate. Numerical lapse
range exhaustion and optimizer termination are recorded separately from a
physical incompatibility.

## Mass history and source equations

The common domain is \(r\in[2.15,6.25]\), contained in all nine retained
negative-side static annuli. The input comprises the finest static controls
from the preceding trial. Each radial profile is interpolated in \(\log f_b\)
and \(\log\alpha_b\) onto 1,025 fixed radii. Cubic radial splines and bounded
C2 quintic blends between adjacent static phases define the reference family.
Each static shape is a rest waypoint. The interpolation stays between adjacent
log-metric values, preserving the nearly settled late controls. Its radial and
phase derivatives are evaluated analytically. Every numerical refinement
samples this same interpolant.

Let \(u\in[0,1]\), \(q=10u^3-15u^4+6u^5\), and
\[
\sigma(u)=0.745+14.255\frac{e^{4q}-1}{e^4-1},
\qquad t(u)=0.745+T[u+z u(1-u)].
\]
The exponential phase map assigns additional clock time to the active part
of the reference reset. The static endpoint at phase 15 is retained, and
phase derivatives through second order vanish at both ends. The duration
and skew vary within the bounds below. The candidate continues statically
after its endpoint through \(t=15\).

A second geometric path blends directly between the initial and final static
shapes with weight \(q(u)\), omitting the intermediate rest waypoints. It
uses the same clock law, storage controls, source laws, and endpoint mass
contract. This comparison tests whether the intermediate reference geometry
itself supplies an avoidable obstruction. Both paths are fixed before the
exploration batch.

Two compact nonnegative radial distributions identify donor and reservoir.
Their cumulative distributions \(C_d,C_R\) each range from zero to one on
the annulus. A C3 polynomial provides each compact cumulative profile. With
\(K(u)=\sin^4(\pi u)\), the mass history is
\[
m(t,r)=m_b(\sigma(t),r)+A K(u)[C_R(r)-C_d(r)].
\]
Thus \(AK\) is the temporarily redistributed coordinate mass: its donor
and reservoir contributions integrate to \(-AK\) and \(+AK\). It changes
the geometry and the current. Both endpoint profiles and both boundary mass
histories remain fixed. Truncation of a donor profile at the inner domain is
normalized explicitly; derivative matching is part of the subsequent full
rail matching condition.

The areal metric is
\(ds^2=-\alpha^2dt^2+dr^2/f+r^2d\Omega^2\), with \(f=1-2m/r\).
The energy and current equations give
\[
E=\frac{m_r}{4\pi r^2},\qquad
J=-\frac{m_t}{4\pi r^2\alpha\sqrt f}.
\]
In particular, the luminosity \(4\pi r^2\alpha\sqrt f J=-m_t\)
has a fixed integrated transfer. Changing the clock distribution preserves
the endpoint mass difference.

The static reference stress supplies an effective infrastructure path
\((E_b,P_b,0,P_{tb})\). A bounded release of the fitted string component is
\(B=0.039783\,b K W(r)/r^2\), where the C2 window reaches its plateau
through the first and last 3% of the annulus. The rest-frame infrastructure
then has channels \((E_b-B,P_b+B,0,P_{tb})\).

Two source families are registered. The first keeps this infrastructure at
rest in the areal frame. The second permits a bounded radial response of the
same rest-frame stress. Writing \(h_b=E_b+P_b\),
\[
j_b=J\frac{c^2h_b^2}{J^2+c^2h_b^2},\qquad
c=\frac{2v_{\max}}{1-v_{\max}^2},\qquad v_{\max}=0.5,
\]
and \(\psi=\tfrac12\operatorname{asinh}(2j_b/h_b)\).
The continuous tensor limit at \(h_b=0\) has zero infrastructure current
and boost contribution. The added diagonal term is
\(D=h_b\sinh^2\psi\). This is a Lorentz transformation of the prescribed
signed source, with \(|v|\leq0.5\); it preserves the infrastructure's
radial discriminant. The stationary family has \(D=j_b=0\).

The two null streams carry net current \(J-j_b\) and energy
\[
F=\sqrt{(J-j_b)^2+(0.01B)^2},\qquad
\mu_\pm=\tfrac12[F\pm(J-j_b)].
\]
Their energy cost leaves ordinary material density
\[
M=E-E_b+B-D-F.
\]
The material law is \(P_r=wM,\ P_t=\eta M\), with \(0\leq w,\eta\leq1\).
Consequently the prescribed total radial and angular pressures are
\[
P=P_b+B+D+wM+F,\qquad P_t=P_{tb}+\eta M.
\]
The lapse solves
\[
\partial_r\log\alpha=\frac{m+4\pi r^3P}{r^2 f},
\]
with the outer reference lapse as clock anchor. This is nonlinear because the
required current and source allocation depend on \(\alpha\). The implementation
solves for \(\alpha/\alpha_b\), using exact reference cancellation. At
\(w=1\), the pressure simplifies to \(P_b+2B+(E-E_b)\), giving a direct
integral control.

The energy, current, and radial pressure equations therefore enter the
construction itself. The independent angular equation is evaluated as
\[
8\pi P_{t,G}=f(\nu_{rr}+\nu_r^2+\nu_r/r)
+\tfrac12 f_r(\nu_r+1/r)
+\frac{f_{tt}-f_t\nu_t-3f_t^2/(2f)}{2\alpha^2f},
\qquad \nu=\log\alpha.
\]
The outer optimization drives the angular mismatch and source violations.
Every detailed candidate also retains the covariant energy and radial-force
exchange for infrastructure, material, and both streams. The null exchanges
have the corresponding null four-force direction. Total radial exchange and
angular Einstein closure are related by the Bianchi identity and are assessed
as complementary consistency measurements.

## Search bounds and numerical budget

| Control | Registered interval |
|---|---:|
| Reset duration \(T\) | 4 to 14.255 |
| Clock skew \(z\) | −0.65 to 0.65 |
| Temporarily redistributed mass \(A\) | 0 to 0.25 |
| Donor center | 2.35 to 2.9 |
| Donor half-width | 0.16 to 0.42 |
| Reservoir center | 3.4 to 5.55 |
| Reservoir half-width | 0.25 to 0.65 |
| Released string fraction \(b\) | 0 to 1 |
| Material radial pressure ratio \(w\) | 0 to 1 |
| Material tangential pressure ratio \(\eta\) | 0 to 1 |

The exploration evaluates 256 scrambled Sobol controls for each combination
of geometric path and source family, using seed 8172026, for 1,024 candidates.
Sixteen additional boundary controls supply analytic seeds. Up to two distinct
candidates per combination receive
bounded Powell refinement, with at most 240 evaluations per local solve.
Mass and string-release amplitudes use the search coordinate
\(x=10^{-5}\operatorname{expm1}[z\log(1+x_{\max}/10^{-5})]\), with
\(z\in[0,1]\). This includes zero and resolves small amplitudes near the
compact inner geometry. The remaining controls use linear search coordinates.
The objective is the largest of negative material density, negative radial
stress margin, and angular equation residual, plus one tenth of their sum,
using a fixed source scale of 0.01. Acceptance uses each physical condition
separately.

Exploration uses 129 radii and 65 time parameters. The best three distinct
candidates are recomputed at 257 by 129 and 513 by 257 points, in addition to
their coarse grids. The static reference jets are preserved exactly while
derivatives of the changed lapse are refined. Independent four-dimensional
curvature probes evaluate the interpolated candidate metric at each
refinement, including witnesses for material density, radial stress, angular
closure, and the relaxed energy bound. A surviving construction also requires
targeted interface and enthalpy-root searches and the full rail/service checks.

The first numerical batch has a 7,200-second compute cap, four worker processes,
and a 500 MB output cap. Each worker has a 1,536 MiB address-space ceiling;
single-threaded BLAS avoids nested worker multiplication. Numerical summaries
are retained for exploration and local solves, with field and exchange arrays
retained only for finalists. Reports are written manually.

## Independent energy bounds

For a specified retained background, the ordinary carrier relaxation imposes
\(E_c\geq|j_c|\) and \(-E_c\leq P_c\leq E_c\). On the positive total
enthalpy branch, it gives
\[
E_{c,\min}=\max\{|j_c|,\ |J|-h_b/2\}.
\]
The negative branch requires \(h_b\leq-2|J|\); its optimistic energy bound
is \(|j_c|\). Here \(J\) is the total current and \(j_c\) is the current
remaining for ordinary carriers after any infrastructure motion. The bound
allows more freedom than the registered source law, so a deficit is a
necessary-condition failure. A feasible bound remains subject to stress type,
constitutive, conservation, and geometric checks.

The implementation checks these formulas against an independent sparse
[HiGHS linear program](https://docs.scipy.org/doc/scipy-1.16.2/reference/optimize.linprog-highs.html).
For the previous fixed-current trial, the positive-branch minimum energy is
integrated through the Hamiltonian equation at all three resolutions. These
bounds apply to that reference current and branch. They supply a diagnostic
control for the construction search, whose current changes with geometry.

## Validation and decision record

Eight dedicated tests pass before the search. They compare the exact reduced
Einstein formulas with independent four-dimensional curvature, reproduce
Schwarzschild and de Sitter stresses, verify Lorentz invariants and the speed
bound, compare analytic energy bounds with linear programming, verify stored
mass and net transfer, preserve a vacuum coupled-solver control, verify
the null exchange direction, and preserve the settled interpolation tail.
The complete harness passes 293 tests, with four existing multiprocessing
deprecation warnings. A four-worker integration pilot exercises exploration,
local optimization, all three field resolutions, component exchanges,
independent four-dimensional curvature, output limits, and the diagnostic
figure. The registered full batch follows these implementation checks.

A failed finite search is reported with its best remaining violations and
numerical convergence. Verified energy bounds can exclude their specified
fixed constructions. Optimizer nonconvergence alone supplies no general
infeasibility result.
