# Smooth Quantum Mirror with Trapped Material

Date: 9 September 2026.

The enclosing boundary selected by the curved scalar calculation requires
positive tangential surface pressure. A resolved scalar wall supplies its
own thickness and tension. Fermions bound to that wall provide a concrete
source of tangential pressure. This attempt examines their common material
description and its first quantum and mechanical conditions.

## Field model and literature basis

[Mazzitelli, Nery and Satz](https://arxiv.org/abs/1110.3554), equations
(2), (12)–(14) and (37)–(38), give a semiclassical scalar mirror model,
its gravitational and material counterterms, and a renormalized stress
for smooth weak potentials. [Franchino-Viñas, Mantiñan and Mazzitelli](https://arxiv.org/abs/2110.14692)
extend the stress and force analysis and establish the common conservation
law. A prescribed mirror profile supplies scattering data; a material
solution additionally satisfies the mirror equation with its quantum force.

The explicit wall profile follows
[Olum and Graham](https://arxiv.org/abs/gr-qc/0205134). The pressure-bearing
component follows the wall-bound fermions of
[Ogure, Yoshida and Arafune](https://arxiv.org/abs/hep-ph/0212332).
The following combined action is the candidate examined here. These papers
establish its individual ingredients; the combined gravitating quantum
solution remains the construction problem.

In the local proper normal coordinate \(z\), use a canonical real wall
field \(\chi\), a quantum real scalar \(\phi\), and a Dirac field with
Yukawa mass \(y\chi\). Their scalar potential is
\[
U(\chi,\phi)=\frac{\lambda_\chi}{4}(\chi^2-v^2)^2
+\frac{g}{2}(v^2-\chi^2)\phi^2+\frac{\beta}{4}\phi^4.
\]
Positive \(\lambda_\chi,\beta\), with
\(\lambda_\chi\beta>g^2\), make this potential bounded below.
At leading order in the quantum backreaction the wall is
\[
\chi=v\tanh(z/d),\qquad
d=\frac{\sqrt2}{v\sqrt{\lambda_\chi}},\qquad
\tau=\int\rho_\chi dz=\frac{4v^2}{3d}.
\]
Its optical potential and integrated strength are
\[
V(z)=g(v^2-\chi^2)=\frac{\Lambda}{2d}\operatorname{sech}^2(z/d),
\qquad \Lambda=2gv^2d.
\]
Thus the same wall profile sets the reflection and the material gradient
energy. The vacuum scalar is massless outside the wall and minimally
coupled at the specified renormalization scale. Curvature counterterms
remain part of the covariant completion. The quartic vacuum interaction
enters beyond the Gaussian vacuum calculation.

The lowest planar fermion branch has dispersion \(E=|\mathbf p_\parallel|\)
and transverse wavefunction proportional to
\(\operatorname{sech}^{yvd}(z/d)\). Its zero-temperature surface gas has
\(p_F=\epsilon_F/2\), so the leading material surface equation of state is
\[
\Sigma=\tau+C n^{3/2},\qquad
P=-\tau+\tfrac12 C n^{3/2},\qquad
\frac{dP}{d\Sigma}=\frac12.
\]
This is a conserved particle-current specialization of a surface fluid.
Independent entropy dynamics can be added when a thermal state is needed.
The occupied modes have to remain confined, and their finite-size and
curvature corrections enter the complete material problem.

The microscopic formulas above use \(\hbar=c=1\). For a physical length
scale \(L\), the conversion to the dimensionless geometric surface stress
contains \(\eta=G\hbar/L^2\). A microscopic parameter match therefore
specifies \(\eta\) together with the field couplings and the occupied
fermion modes. The junction coefficients alone leave that match open.

## Registered calculations

The first calculation resolves the renormalized *planar, first-order*
vacuum stress throughout the smooth wall. With
\(\widehat V(k)=\Lambda(\pi k d/2)/\sinh(\pi k d/2)\), the minimal
scalar energy is
\[
\rho_Q^{(1)}(z)=-\frac{1}{96\pi^2}
\mathcal F^{-1}\!\left[k^2\log(k^2/\mu^2)\widehat V(k)\right],
\qquad p_{z,Q}^{(1)}=0,\quad p_{t,Q}^{(1)}=-\rho_Q^{(1)}.
\]
The inverse Fourier transform includes \(1/(2\pi)\). The small parameter
for this expansion is \(V(0)d^2=\Lambda d/2\). The field variance at
first order fixes a force at second order, so the first-order stress and
that force belong to different truncation orders. The numerical stress
benchmark uses \(\mu d=1\), \(\Lambda d/2=0.05\), and widths
0.025, 0.05 and 0.1. Changing \(\mu\) changes local material couplings
as well as the displayed quantum contribution.

The second calculation matches the leading material equation of state to
the existing \(R=6.8\) junction across its full allowed exterior-mass
range. This gives
\[
\tau=(\Sigma-2P)/3,\qquad \epsilon_F=2(\Sigma+P)/3.
\]
The surface energies at this stage are measured effective coefficients;
matching them to the microscopic action requires the quantum self-energy
and material corrections. The existing nonzero bulk momentum flux is
retained in the conditional radial response. A closed particle-number
evolution requires its own exchange calculation.

Both tangential density waves and normal shape perturbations are checked.
The latter are a separate condition from spherical radial stability.
Any instability in the leading material description stops its promotion
to a full curved vacuum calculation. Required additional bending or bulk
response is quantified without fitting a stabilizing coefficient.

Independent quadrature levels, a direct cosine-integral check, and the
far-wall thin-potential asymptote assess the quantum benchmark. Direct
surface-energy variations assess the mechanical quadratic form. Numerical
cases support one to six workers, with four used for the evidence run.
The evidence allowance is 20 MB and the registered computation allowance
is 600 seconds. The complete curved vacuum, quantum force, finite-width
material equilibrium and Einstein equations remain coupled requirements.

## Smooth stress and surface matching results

The first evidence run uses four workers and takes 2.94 seconds, retaining
0.57 MB. The resolved stress is finite at the wall center and at every
sample through its smooth transition. For width 0.05, strength 2 and
\(\mu=20\), the first-order central energy is -26.5824572 in the
single-field quantum normalization. Positive shoulders and negative
outer tails accompany that central contribution. The profile depends on
the specified local renormalization convention.

At nine locations from the center to 40 widths, the 1,024-node integral
agrees with an independent adaptive cosine integral to a maximum relative
difference of \(5.66\times10^{-11}\). The 512-to-1,024-node change is
\(9.53\times10^{-9}\) of the profile peak and \(4.79\times10^{-4}\)
of the much smaller 40-width tail. The 256-node control under-resolves
the far oscillatory integral; the retained higher levels resolve it.
The \(-\Lambda/(48\pi^2|z|^3)\) tail is the asymptote of the
*first-order coefficient*. At finite strength, a Born approximation in the
exterior also requires \(\Lambda|z|\ll1\); the far-tail coefficient
check supplies a normalization test separately from that physical regime.

Positive wall tension and gas energy reproduce the junction for
\(0.459336278<M<2.963212742\). The specified surface law has positive
conditional radial frequency squared for
\(0.706038106<M<2.338601517\). At \(M=1.5\), the wall tension is
0.00055572145 and the gas energy is 0.00200447860. Their sum is the
required surface energy 0.00256020005, and their combined pressure is
0.000446517848. The gas longitudinal speed squared is 0.5.

The separate normal-shape diagnostic has negative stiffness throughout
the 1,029 scan rows that pass the material and radial checks. Direct
area-dependent energy variations reproduce that sign. This result selects
normal deformations as the next independent audit and blocks promotion
of the leading surface law by radial stability alone.

![Smooth quantum and material diagnostics](data/smooth_quantum_material/smooth_material_findings.png)
