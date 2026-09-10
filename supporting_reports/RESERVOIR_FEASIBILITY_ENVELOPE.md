# Physical response and source compatibility of the prepared reservoir

Date: 10 September 2026.

The slower [prestressed assembly](PRESTRESSED_BUFFER_VELOCITY_INVESTIGATION.md)
has a measured mechanical response and a separately unresolved physical
source. This investigation assigns feasibility questions to explicit
mechanisms and the actual active geometry. Its energy and stress multipliers
remain comparisons with the previous reservoir. Physical acceptance depends
on the supplied tensor, component response, and complete operating cycle.

## Registered scope

The study uses the archived freely evolving interiors at 64 and 128 cells,
the 64-cell prior-energy control, and the preceding thermal reservoir. The
full active lapse, shift, radial and angular scales, time derivatives,
endpoint tensor, and protected packet separation remain in the comparison.
Each registered phase samples every material node. Material fractions
0.15 through 0.85 also receive an interior diagnostic. The phases are startup,
0.5, and fade completion at 1.285; the older reservoir's last comparison is
0.815, within its completed history.

Four independent workers evaluate the original regularized metric with
curvature steps 0.0025 and 0.00125. A separate curvature calculation uses
the interpolated metric that drove the reservoir. This tests both curvature
resolution and the source effect of metric interpolation. The numerical
output comprises tensors, source requirements, dimensional coefficients,
and optimization certificates. This report is maintained manually.

## Local field construction

Write the backbone energy and pressure as

\[
 u_B=\frac{A K_b n_b^2}{2R^2},\qquad
 u_s=\frac{A K_b}{2R^2},\qquad
 (\epsilon_b,p_b,p_{\Omega b})=(u_B+u_s,u_B-u_s,0).
\]

Equal transverse magnetic orientation energies have the averaged Maxwell
tensor \((u_B,u_B,0,0)\), in the order energy, radial pressure, current,
and angular pressure. Flux freezing under radial compression gives
\(B_\perp\propto (R B\Gamma h)^{-1}\), supplying the quadratic
compression term. A radial string contribution supplies
\((u_s,-u_s,0,0)\). The latter retains the disclosed standing-tension
source role and its physical-realization requirement.

The attached buffers have rest energy density
\(w_b=A n_t(1+q)/R^2\). The common radial compression mode has

\[
 c_f^2=\frac{2u_B}{w_b+2u_B},\qquad \sigma=\frac{2u_B}{w_b}.
\]

This is a local perpendicular magnetic compression response. Its stress
direction and angular average are evaluated explicitly. Global return
paths, confinement, currents, field stability, and the inertia of their
hardware require a physical assembly. The Maxwell and material equations
are developed in [Hernandez and Kovtun](https://arxiv.org/html/1703.08757);
the original elastic law is given by
[Natário](https://arxiv.org/html/1406.0634). The tensor decomposition and
its application to the archived reservoir are calculations of this study.

If the pressure-free heat buffers are instead interpreted as a free
relativistic gas, their pressure follows a gas equation of state. The
Taub--Mathews approximation gives

\[
 p_g=\rho_{\rm rest}\frac{(1+q)^2-1}{3(1+q)}.
\]

This counterfactual diagnoses the additional radial and angular pressure
of that interpretation. A pressure-free composite heat store instead needs
its internal confinement and associated stresses counted. The gas law and
its range of approximation are described by
[Mignone and McKinney](https://arxiv.org/html/0704.1679).

## Source and scale requirements

Let \(D=G[g]/8\pi\) and let \(M\) and \(S\) denote the fitted endpoint
and the supplied reservoir tensors. Their remaining source requirement is
\(D-M-S\). For the two local radial null vectors
\(k_\pm=n\pm e_r\), the required magnitude of a negative contribution is

\[
 Q_\pm=\max\{0,(M+S-D)_{\mu\nu}k_\pm^\mu k_\pm^\nu\}.
\]

Any additional sector obeying the radial null energy condition contributes
nonnegative stress to this projection. Thus \(Q_\pm\) is a lower bound on
the total negative contribution required from the remaining sectors under
that completion assumption. The quantum allowance is unspecified; the
calculation measures the allowance a construction would have to supply.
Standing radial tension has zero radial null projection. Its allocation
can change density and radial pressure individually while preserving this
particular requirement.

A linear program searches the full discrete initial equilibrium family
for the smallest maximum \(Q_\pm\), using initial signal-speed floors
0, 0.3, and 0.5. These are response comparisons. Its primal and dual
objectives bound the best source burden available within this family,
without assigning a numerical feasibility ceiling to quantum stress.

The disclosure's physical length conversion remains free. If one model
length unit is \(L\) metres, the full uniform metric scaling gives

\[
 T_{\rm SI}=\frac{c^4}{G L^2}\widehat T,\qquad
 B_{\rm SI}=\frac{1}{L}\sqrt{\frac{2\mu_0c^4}{G}\widehat u_B},\qquad
 E_{\rm slice,SI}=\frac{c^4L}{G}\widehat E_{\rm slice}.
\]

The slice energy is the proper-volume integral of local normal-frame
energy. It has a different meaning from asymptotic ADM mass and recoverable
electrical energy. Ratios between the geometrical demand and supplied
classical tensors remain invariant under this uniform scaling. A particular
material or quantum realization introduces further physical scales.

The bounded round ends when these calculations identify either a compatible
source range or a necessary contribution for which the current construction
has no supplied mechanism. Its results guide selection of the next physical
calculation. Main disclosure changes are outside this investigation.
