# Active endpoint exchange with a preloaded radial transfer sector

Date: 9 September 2026.

## Construction and scope

This bounded investigation uses the scheduled, repaired beta075 V5 metric.
The carrying shift, lapse, radial stretch, and angular capacity retain their
time dependence. The prepared substrate, endpoint medium, and transfer sector
have separate responsibilities. The calculation tests whether a positive,
preloaded radial radiation sector can supply the endpoint medium's opposite
exchange while respecting the protected live corridor.

The initial timing reconnaissance evaluates nine angular-jacket/receiver
schedules at seven previously established active witnesses. Every schedule
retains Type IV witnesses. Individual improvements accompany worsening at
other locations. This result ends that timing-only comparison and motivates
an explicit source and exchange construction.

The endpoint input is its archived regulated orthonormal tensor. Cubic
interpolation fills absent table cells with zero. An explicit C2 taper reaches
zero between absolute rail coordinates 1.9 and 2.1, and a C2 exclusion window
rises from zero to one between packet offsets 0.35 and 0.45. This defines a
continuous candidate medium for the transfer test. It modifies the archived
edge representation; its difference from the archived fitted tensor and the
geometric target remains a separate source-accounting quantity.

The complete geometric tensor continues to require its other assigned source
roles. This calculation supplies a candidate transfer tensor on a fixed active
background. A successful exchange calculation would precede tests of its
microscopic interaction, other component stresses, and metric backreaction.

## Causal transfer equations

Write the active metric as
\(ds^2=-\alpha^2dt^2+B^2(dx+\beta dt)^2+R^2d\Omega^2\).
Let \(n\) and \(e\) be its ADM time and radial unit vectors. The candidate is

\[
T_R^{ab}=\mu_+ k_+^a k_+^b+\mu_- k_-^a k_-^b,
\qquad k_\pm=n\pm e,\qquad \mu_\pm\geq0.
\]

It has density and radial pressure \(\mu_++\mu_-\), radial current
\(\mu_+-\mu_-\), and zero angular pressure. Angular response remains in the
endpoint medium and jacket. Its four-force is the opposite of the freshly
evaluated medium divergence on the same active metric.

For medium divergence projections \(P=-n_b\nabla_aT_J^{ab}\) and
\(F=e_b\nabla_aT_J^{ab}\), define \(D_\pm=BR^2\mu_\pm\). Then

\[
\partial_t D_\pm+\partial_x(v_\pm D_\pm)
=\left(\alpha K^x{}_x\mp\frac{\partial_x\alpha}{B}\right)D_\pm
-\frac{\alpha BR^2}{2}(P\pm F),\qquad
v_\pm=-\beta\pm\frac\alpha B.
\]

These are spherical covariant radiation balance equations. Their conservative
organization follows the general relativistic transport formulation described
in the [Einstein Toolkit GRHydro documentation](https://einsteintoolkit.org/thornguide/EinsteinEvolve/GRHydro/documentation.html).
The implemented medium energy and momentum equations receive an independent
four-dimensional covariant-divergence check.

Along each characteristic the solution has the form
\(D=g(D_0+I)\), with positive homogeneous factor \(g\) and integrated forcing
\(I\). Positivity over the tested interval requires

\[
D_0\geq\max\{0,-\min_t I(t)\}.
\]

Thus the forcing determines a minimum preloaded energy for each ray. Any
additional positive initial or incident radiation increases its density
throughout that characteristic. A positive lower bound inside the packet
therefore supplies a direct obstruction to this freely propagating radial
completion, independent of choosing a larger reservoir reserve.

## Registered bounded calculation

The interval is service time \([-1.5,3]\): it includes live entry, carry,
release, and the first reset, with the original live interval retained. Rays
start over \([-9,9]\); the medium acts only inside \(|x|<2.1\). Metric
interpolation covers \([-6,6]\), with the specified unit-lapse analytic tails
outside that interval. Edge preload and characteristic coverage are monitored.

Four comparisons separate metric, transport, and archived-medium sensitivity:

| Comparison | Metric time/radial spacing | Medium input | Initial rays per direction | Time step |
| --- | --- | --- | ---: | ---: |
| Coarse | 0.025 / 0.05 | Baseline interpolant | 401 | 0.01 |
| Refined | 0.0125 / 0.025 | Same baseline interpolant | 801 | 0.005 |
| Time refinement | Same fine metric | Same baseline interpolant | 801 | 0.0025 |
| Source sensitivity | Same fine metric | Dense archived interpolant | 801 | 0.005 |

The dense archived medium has its own fit coefficients. It is a source
sensitivity comparison; transport convergence uses the pinned baseline
interpolant. Minimum preload obtained from sampled times is a lower bound,
since any missed intermediate minimum could only increase the required
reserve. Numerical integration errors receive the separate refinement checks.

The first physical gate requires nonnegative streams and zero transfer-sector
stress in the live packet. An interior witness uses an additional 0.05 radial
margin from the packet edge. A stable positive lower bound there ends this
candidate before attempting an Einstein-source repair. The calculation uses
up to four workers, with a 50 MB evidence allowance. The main disclosure stays
unchanged.

Implementation:
[`active_transfer_reservoir.py`](../toolkit/adm_harness_cli/adm_harness/active_transfer_reservoir.py)
and [`run_active_transfer_reservoir.py`](../toolkit/adm_harness_cli/scripts/run_active_transfer_reservoir.py).
