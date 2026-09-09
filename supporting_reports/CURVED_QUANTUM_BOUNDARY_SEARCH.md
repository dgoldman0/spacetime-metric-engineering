# Spherical Quantum Boundaries on the Frozen Rail

Date: 9 September 2026.

## Registered construction and stopping conditions

The preceding [continuum boundary calculation](RENORMALIZED_BOUNDARY_SUPPORT_ROUNDS.md)
identifies two geometric requirements for an extended source: negative radial
enthalpy throughout the retained annulus and negative angular enthalpy over
part of it. This round calculates the actual change in the vacuum tensor
produced by concentric, semitransparent spherical boundaries on the initial
rail geometry. A radial mode equation retains every included spherical
harmonic and its angular stress.

The background is the complete, two-ended static metric obtained by freezing
the repaired source evaluator at phase 0.745 and setting the shift to zero.
This is the holding geometry used to construct the retained initial annulus.
The source parameters come from the coupled-reset manifest. Its lapse,
radial metric, and areal radius are preserved on both branches. The negative
branch contains the retained annulus. At large coordinate distance the
metric approaches the ultrastatic tail with areal radius
\(r=\sqrt{\ell^2+1.75^2}\).

The field is a real, massless, minimally coupled scalar in the static ground
state. A boundary at \(\ell_i\) has positive proper optical coupling
\(\lambda_i\). The difference between the ground-state tensors with and
without these boundaries, on the same geometry, is calculated away from
the sheets. Local bulk renormalization terms cancel in this difference.
The complete source would additionally contain the boundary-free curved
vacuum tensor, the matched material tensor, and the ordinary currents.
Thus the calculation measures a specified boundary response. The absolute
curved vacuum remains part of the subsequent source equation.

Write the static metric as
\[
ds^2=-\alpha^2dt^2+A^2d\ell^2+r^2d\Omega^2.
\]
For imaginary frequency \(\zeta\) and angular index \(j\), the radial
Green operator is
\[
L_{\zeta j}=-\partial_\ell\left(\frac{\alpha r^2}{A}
\partial_\ell\right)
+\alpha A\left[j(j+1)+\frac{\zeta^2r^2}{\alpha^2}\right].
\]
The boundary adds \(v_i\delta(\ell-\ell_i)\), where
\(v_i=\alpha_i r_i^2\lambda_i\). Its quadratic form is positive.
With \(C_i(\ell)=g_0(\ell,\ell_i)\) and
\(M_{ij}=\delta_{ij}/v_i+g_0(\ell_i,\ell_j)\), the exact resolvent
identity gives
\[
\Delta g(\ell,\ell')=-C(\ell)^T M^{-1}C(\ell').
\]
This formulation evaluates the finite difference directly, avoiding
subtraction of two large coincident Green functions.

The mode weight is \((2j+1)d\zeta/(4\pi^2)\). Define the integrated
derivative moments
\[
a=\int\!\sum_j w_j\frac{-\zeta^2}{\alpha^2}\Delta g,
\quad b=\int\!\sum_j w_j\frac{\partial_\ell\partial_{\ell'}
\Delta g}{A^2},
\quad c=\int\!\sum_j w_j\frac{j(j+1)}{2r^2}\Delta g.
\]
Then \(\Delta\rho=(a+b+2c)/2\),
\(\Delta p_r=(a+b-2c)/2\), and
\(\Delta p_t=(a-b)/2\). The two null channels are \(a+b\) and
\(a+c\). The minus sign in the time moment follows the continuation
back to Lorentzian time. The general spherical Green-function convention
agrees with equations (6)–(10) of
[Arrechea and collaborators](https://arxiv.org/html/2607.07583v1).

The registered placements use negative-branch areal radii 2.35, 2.85, and
6.8. The first two lie in the positive-density portion of the retained
annulus. Four arrangements are compared: an inner sheet at 2.85, two inner
sheets at 2.35 and 2.85, a spanning pair at 2.35 and 6.8, and the outer sheet
alone at 6.8. Each arrangement uses common coupling 1, 8, or 64. The outer
sheet is an explicit extension beyond the retained annulus and introduces
an additional material and junction requirement.

Bulk witnesses cover the retained annulus and remain at least 0.5 proper
length from every sheet. Spatial refinement, angular-mode refinement,
frequency quadrature, and the distance of the auxiliary end boundaries
are checked independently. Exact constant-coefficient Green functions and
the preceding planar continuum stress provide controls. A discrete
conservation residual provides a further check of the assembled tensor.

Four independent workers with single-thread numerical libraries perform
the mode computations. The registered allowance is 900 seconds per main
comparison, 1,536 MiB address space per worker, and 12 MB of saved evidence.
Only profiles, convergence evidence, and manifests are retained.

Continuation requires a converged improvement in the simultaneous radial
and angular requirements with a definite next source calculation. A
resolved sign obstruction or a structural obstruction in the absolute
source equation ends this search round. Parameter changes beyond the
registered placements require an identified physical reason.
