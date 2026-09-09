# Smooth joint condensate and quantum source

The joint source problem uses one smooth proper-distance chart,

\[
ds^2=-A(l)^2dt^2+dl^2+R(l)^2d\Omega^2,
\]

with the radius, lapse, condensate amplitudes, gauge potential, and quantum state determined consistently. The starting fields are the regular nodeless condensate. A Gaussian mollifier of proper width 0.25 gives a smooth numerical seed through its former geometric join. Its Einstein tensor is recomputed from the smoothed metric.

## Fixed model and renormalization conditions

The material couplings retain \(e=0.1\), \(\lambda=1\), \(\mu=1.4\), \(v=12/6.8\), and \(G=\eta=2.4127904527582454\times10^{-5}\) in rail length units. The quantum sector contains one real minimally coupled scalar in the static ground state, with \(V_\chi=\kappa v^2h^2\) and \(\kappa=1.4\). Its stress and Higgs force follow from a common renormalized effective action. The material number of the initial branch, approximately 48,954.28, supplies the conserved-charge target for a joint continuation.

An absolute source also requires finite renormalization conditions. Here the subtraction scale satisfies \(\mu_R^2=\kappa v^2\). The flat \(h=1\) vacuum has zero quantum energy and force; the Higgs mass and quartic coupling retain their registered values there. The vacuum Newton coefficient is fixed to the existing \(\eta\). Finite coefficients of \(R_{ab}R^{ab}\), \(\mathcal R^2\), and \(V_\chi\mathcal R\) are zero at this scale. These are explicit physical model choices for this round.

Writing \(m_0^2=\mu_R^2\), the homogeneous quantum potential is

\[
F(V)=\frac{V^2[\log(V/m_0^2)-3/2]+2m_0^2V-m_0^4/2}{64\pi^2},
\qquad \langle\chi^2\rangle_{\rm flat}=2F_V.
\]

Thus both the stress and force vanish at the flat exterior vacuum. A finite \(-m_0^2\mathcal R/(192\pi^2)\) action term fixes the vacuum Newton coefficient in the same convention.

## Coupled equations

Let \(r=\log R\), \(a=\log A\), and let a prime denote proper distance. For the complete orthonormal source \((\rho,p_r,p_t)\),

\[
r''=\frac{e^{-2r}-3r'^2-8\pi\rho}{2},\qquad
a''=8\pi p_t-a'^2-a'r'-r''-r'^2,
\]

while the radial constraint is

\[
\frac{-e^{-2r}+r'^2+2a'r'}{8\pi}=p_r.
\]

The source is \(\eta[v^4T_{\rm material}+\langle T_\chi\rangle]\). Material fields use the dimensionless distance \(s=vl\). The Higgs amplitude equation receives

\[
\delta h_{ss}=\frac{\kappa h\langle\chi^2\rangle}{2v^2}.
\]

The factor of two follows from the complex Higgs amplitude's kinetic term. This force supplies the exchange required by

\[
p_{r,Q}'+a'(\rho_Q+p_{r,Q})+2r'(p_{r,Q}-p_{t,Q})
=-\tfrac12\langle\chi^2\rangle V_\chi'.
\]

The matter equation supplies the opposite exchange. Consequently the complete source conserves stress and propagates the radial Einstein constraint. The implementation retains that constraint independently from the two metric evolution equations.

## Absolute-source calculation and acceptance

The numerical control uses Pauli–Villars squared masses \(V_\chi+jM^2\), \(j=0,1,2,3\), with weights \((1,-3,3,-1)\). Their sums cancel the quartic, quadratic, and logarithmic ultraviolet orders. Spherical Euclidean modes use the reduced field \(\sqrt A R\chi\), with potential

\[
U=\frac{\zeta^2}{A^2}+\frac{j(j+1)}{R^2}+V_\chi+
\frac{R''}{R}+\frac{A''}{2A}+\frac{A'R'}{AR}-\frac{A'^2}{4A^2}.
\]

An exact flat-space Bessel reference at each observation removes the large common homogeneous contribution before summation. Its physical, renormalized value is restored analytically. The remaining heavy-field action terms through the second heat-kernel coefficient are removed covariantly, including their curvature-squared and variable-potential variations. The local action is varied before setting the radial metric coefficient to unity, preserving the radial-pressure equation.

The heat-kernel construction follows [Vassilevich's account](https://arxiv.org/abs/hep-th/0306138). The common effective-action treatment of stress and variable-mass force is developed by [Franchino-Viñas, Mantiñan, and Mazzitelli](https://arxiv.org/abs/2110.14692). The mode representation follows the static spherical construction of [Arrechea and collaborators](https://arxiv.org/html/2607.07583v1).

The registered checks independently vary the radial mesh, frequency quadrature, angular range, regulator mass, and smooth-seed representation. Known flat-space modes, homogeneous vacuum conditions, local action variations, and constraint propagation provide analytic controls. Four workers perform independent angular calculations. A finite regulator value becomes eligible for geometric feedback only when these controls establish its limit and the quantum stress–force conservation identity is resolved. A failed numerical source check stops geometric feedback and yields a computational limitation for this round.

Eight initial tests pass. They include an independent high-precision Bessel comparison, second-order radial convergence, the local Ward identity, and radial-constraint propagation with quantum material exchange. Full absolute-source refinement results are recorded at the next calculation milestone.
