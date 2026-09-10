# Graded radial capacitors and distributed reservoir contacts

## Construction and scope

This bounded study tests a radial electric force profile coupled to local
energy buffers on the repaired active rail. It follows the
[source selection](SOURCE_CONSTRUCTION_SELECTION.md) and the
[prestressed reservoir feasibility audit](RESERVOIR_FEASIBILITY_ENVELOPE.md).
The radial field supplies tension and local electrical conversion; the buffers
carry stored material energy and the endpoint exchange. A segmented variant
exposes finite mechanical contacts for transferring momentum to infrastructure.

The domain is the previous late reservoir patch, \(x\in[-2.1,-0.5]\), starting
at \(s=0\). The main comparison ends at carrying-flow fade, \(s=1.285\),
with one segmented extension to \(s=3\). The geometry retains its lapse,
shift, radial stroke, angular evolution, and protected moving packet.
The reconstructed endpoint tensor and its divergence are the earlier pinned
candidate. This patch carries 35.75% of the earlier full-interval exchange
weight; earlier preparation and the other rail duties retain their own scope.

The prescribed material worldlines have fixed coordinate position. This
inverse problem determines field and energy histories required to support
those worldlines. A physical realization additionally requires a responding
charged material, finite current inertia, confinement, and stable control.
The pressure-free buffer is an optimistic effective store. Its physical
equation of state and confinement remain part of source completion.

The charged multifluid framework supplies an appropriate subsequent dynamics
model: Andersson's [resistive relativistic charged fluids](https://arxiv.org/abs/1204.2695)
couple heat and charge transport, while
[Andersson, Dionysopoulou, Hawke, and Comer](https://arxiv.org/abs/1610.00449)
retain their inertia and their dependence on the equation of state.
The present conservation screen precedes that constitutive evolution.

## Conservation construction

Write \(v=B\beta/\alpha\), \(\Gamma=(1-v^2)^{-1/2}\), and
\(N=\alpha/\Gamma\), the proper-time rate on the chosen worldlines.
The rest energy of a local buffer is \(w\), and a radial electric field has
energy \(u_E\). Its orthonormal stress is
\((u_E,-u_E,0,u_E)\) in the order
\((\rho,p_r,j,p_\Omega)\). Thus it contributes zero radial null stress and
positive angular null stress. Both channels enter the optimization.

Define

\[
M=\Gamma BR^2w,\qquad H=R^4u_E=Q^2/2.
\]

The buffer's conserved rest-mass reference and initial heat profile are
inherited from the preceding thermal allocation control at the same spatial
resolution. Its energy floor is \(M\geq M_{\rm rest}\). Positive field flux
energy obeys \(H\geq10^{-8}\); a \(10^{-6}\) control tests this numerical
regularity floor. Physical size remains a free conversion parameter.

For endpoint divergence \((P,F)\), the sum of buffer and field obeys

\[
M_s+\frac{\Gamma B}{R^2}H_s
 =-\alpha\Gamma BR^2(P-vF),
\]

\[
H_x-\frac{vR^2}{N}M_s-R^2a_s M=BR^4F,
\]

where the acceleration of a fixed-coordinate worldline is

\[
a_s=\Gamma\left[\frac{\partial_s\operatorname{atanh}v}{\alpha}
+\frac{\alpha_x}{\alpha B}-vK_l\right].
\]

These equations retain the reciprocal endpoint power and momentum together.
Passive electrical conversion imposes \(H_s\leq0\), with
\(\sigma=-H_s/(2NH)\geq0\) in the reduced Ohmic description. The initial
field supplies that conversion energy. A finite charged-fluid construction
must also supply charge continuity, carrier inertia, relaxation, and its own
thermal and mechanical response.

The primary objective minimizes the largest supplied null projection over
all directions. A secondary objective minimizes the time integral of local
slice energy at the same peak. Exact maximization of the angular quadratic
checks the directional sampling and adds constraints as needed. The resulting
optima belong to the discretized inverse family.

## Contact variants and gates

The continuous variant enforces interior momentum balance across the body.
The segmented variant places three finite contact bands, centered at
\(-1.7,-1.3,-0.9\), each of coordinate width 0.1. Energy balance continues
through these bands. The remaining momentum divergence defines a mechanical
force port; the infrastructure supplying that force needs the opposite
divergence in its own tensor. Fixed coordinate contacts have zero canonical
mechanical work and can have nonzero normal-frame power. Their force and
material stress remain physical loads.

Both variants retain terminal electrode tractions as external construction
requirements. The segmented contact bands are a proposed addition to the
station plant, with their proper widths measured in the active metric.

A necessary local test examines a co-moving contact supported solely by
positive rest energy and angular stress, with \(w_c\geq|p_{\Omega c}|\) and
zero radial pressure. Its possible radial divergence per unit density lies in

\[
a_s-2|s^\mu\nabla_\mu\log R|
\ \leq\ F_c/w_c\ \leq\
a_s+2|s^\mu\nabla_\mu\log R|.
\]

An opposite-sign force requirement outside this cone excludes that local
contact model even with unrestricted positive density. Radial transmission,
moving supports, and separately routed momentum have different tensors and
remain separate constructions.

## Registered numerical checks

The suite compares 32, 64, and 128 spatial cells, independent time refinement,
the electric-flux floor, and the segmented reset extension. Four workers run
independent cases with one BLAS thread each. Numeric artifacts stay separate
from this manually maintained report.

Seven focused tests check the covariant reduction against independent tensor
divergence, worldline acceleration against its metric definition, exact oblique
null maximization, an analytic forced flat capacitor, and contact-force signs.
Production checks retain sparse optimization residuals and dual gaps, evaluate
the interpolated tensor divergence between grid nodes, and compare geometric
source tensors with two curvature steps and the actual metric interpolation.

The complete remaining source is evaluated as
\(G[g]/(8\pi)-T_{\rm endpoint}-T_{\rm buffer+field}\).
Required negative contributions in its energy and null projections are
reported alongside the added contact requirements. The fixed-background study
assigns no independent quantum capacity ceiling.

## Initial comparison and regularity gate

The initial suite completed five schedules. Two cases encountered a numerical
failure in secondary energy minimization, and the 128-cell optimization
reached its registered time limit. Their status files retain these outcomes.
The successful 64-cell segmented case has initial local slice energy 234.05,
maximum supplied null stress 0.08519, and a fade-time required negative null
contribution 0.07917. The prescribed velocity reaches 0.20214. Its initial
field energy is 199.66, and the remaining buffer energy is 34.39.

The continuous 32-cell case requires initial slice energy 41,391 and supplied
null stress 5.262. The force placement changes the source burden substantially
within this inverse family. The terminal electrodes and the segmented support
tensors remain additional requirements in both comparisons.

Spatial refinement from 32 to 64 cells changes the segmented initial energy
from 249.55 to 234.05 and its largest integrated collar force from 3.476 to
3.346. However, peak collar force density increases from 0.10891 to 0.21843.
The optimizer concentrates the force inside the allowed band. Its effective
discharge conductivity similarly increases from 174.6 to 342.1 under the
combined refinement. These histories provide a relaxed bound; a finite
physical interface and conversion law require a regularity constraint.

The local angular-support test also produces a sign obstruction. At fade in
the 64-cell case, a contact near \(x=-1.7375\) requires support divergence
\(-0.21843\), while every positive-energy angular-only support at the same
motion has positive radial divergence between \(0.31022w_c\) and
\(0.43121w_c\). Its momentum must reach another stress channel or location.

The segmented reset extension requires initial energy 2,303.9 and peak
supplied null stress 1.743. Its fade-time initial-state requirements differ
from those optimized only through fade. The printed spline-curvature
difference at exactly \(s=3\) crosses the metric table's temporal boundary;
that entry requires a smooth boundary extension before use as a curvature
error estimate. The direct repaired-geometry demand uses its full stencil.

A bounded follow-up imposes a smooth fixed contact profile and a finite
proper discharge rate. Within each band, the coordinate profile is
proportional to \((1-z^2)^3\), \(z=2(x-x_c)/0.1\), and vanishes outside.
Its integral is one. A single signed amplitude at each time specifies the
band's integrated force, with normal force density
\(A(s)\psi(x)/(4\pi BR^2)\). The amplitude joins the simultaneous energy
and momentum solve. This resolves the spatial concentration freedom.

The rate control requires
\(H_{i+1}\geq H_i\exp[-2\sigma_{\max}\Delta\tau_i]\), using the
trapezoidal proper-time interval. The main comparison uses
\(\sigma_{\max}=1\), with a value of 10 as a response sensitivity. These
are specified model response rates for comparing source costs, with physical
time conversion \(L/c\); a material conductivity and current-relaxation law
remain to be supplied. They carry no general buildability threshold.

The follow-up retains the independent divergence checks and uses a quadratic
extension of the metric's temporal jets for curvature stencils crossing the
table boundary. Nine focused tests now include the finite contact profile,
its opposite momentum balance, the rate bound, and temporal jet continuity.
The secondary optimization uses an interior-point solve and a numerical
peak allowance of \(10^{-6}\max(1,z_*)\). Its failure preserves the checked
primary optimum and records the missing energy tie-break explicitly.

The remaining contact material and full source completion determine the
stopping gate after this finite-response comparison.

The first finite-profile suite completed the 32- and 64-cell cases, the faster
response control, and the continuous-field recheck. Three larger linear
programs reached their time limits. At 64 cells the smooth-contact case has
initial energy 431.30 and supplied null peak 0.10513, with maximum effective
conductivity 1. Its contact force density is 0.12098. The local angular-only
support obstruction persists. Increasing the permitted conductivity to 10
reduces the initial energy to 332.49 and supplied null peak to 0.08563.

The final numerical refinement uses the HiGHS interior-point method for the
primary optimization. An independent trial completed the formerly timed-out
64-cell time refinement in 22 seconds. Both solver methods pass the analytic
capacitor and smooth-contact tests; the focused and existing tensor checks
total 19 passing cases. A joint spatial and temporal refinement joins the
separate refinements to assess the remaining discretization sensitivity.
Each primary solve retains the 180-second bound and each energy tie-break
the 90-second bound. This final solver comparison retains the same physical
equations, finite contact profile, and response-rate constraints.
