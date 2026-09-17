# Neutral fermionic hosts and occupation requirements

A charge-symmetric specialization of the local vortex supplies explicit
counterpropagating carrier profiles whose classical gauge and Higgs source
bilinears vanish separately. The resulting straight-string mean field
supports the required elastic energy law for fixed, balanced occupations.
This supplies a more specific hypothetical field host for the rotor
material. Curved spectra, transitions, quantum corrections, preparation
and material interfaces determine its physical realization.

The same calculation exposes a limit of the single-carrier escape screen:
two oppositely moving carriers can have enough invariant energy to leave
as massive particles even when each has a large curvature barrier.
Increasing the number of independent carrier species lowers the occupied
Fermi momentum at fixed elastic energy. Their collective quantum
corrections must accompany that change.

## Charge-symmetric local field model

The [two-fermion local-vortex model of Ringeval](https://arxiv.org/pdf/hep-ph/0007015)
provides the Higgs, gauge and chiral Yukawa equations used here.
The following charge assignment and mode reduction specialize those
equations. Normalize the Higgs gauge charge to one and assign

\[
(q_{\psi L},q_{\psi R})=(1/2,-1/2),\qquad
(q_{\chi L},q_{\chi R})=(-1/2,1/2).
\]

The two Yukawa terms use the Higgs field and its conjugate, respectively.
Their charge differences satisfy gauge invariance. Their cubic gauge
and mixed gravitational anomaly sums cancel pairwise. Each species
also has equal left/right squared charges, so its vector flavor number
has zero mixed gauge anomaly. Independent conserved flavor numbers
are part of the selected field theory.
The half-integer carrier charges leave a residual \(Z_2\) gauge symmetry
after Higgs condensation. The carriers have zero mean gauge current
while retaining this gauge charge.

Use chiral matrices with
\(\gamma^5=\operatorname{diag}(-1,-1,1,1)\).
For a unit vortex, \(eA_\theta=-a/\rho\),
\(\rho=e\eta r\), the charge matrices are
\(Q_\psi=-\gamma^5/2\) and \(Q_\chi=+\gamma^5/2\).
The dimensionless transverse Hamiltonian for species \(\sigma=\pm1\) is

\[
H_\perp=-i\alpha_r\partial_\rho
-\frac{i\alpha_\theta}{\rho}\partial_\theta
-\frac{a}{\rho}\alpha_\theta Q_\sigma
+\beta_D\frac ge f\,e^{i\sigma\gamma^5\theta}.
\]

Here \(\beta_D=\gamma^0\), distinct from the scalar/vector coupling
ratio \(\beta\). The two zero-mode spinors are

\[
\psi_\perp=F(\rho)(1,0,0,i)^T,\qquad
\chi_\perp=F(\rho)(0,1,i,0)^T,
\]

where

\[
F'=-\left(\frac ge f+\frac{a}{2\rho}\right)F,\qquad
4\pi\int_0^\infty \rho F^2\,d\rho=1.
\]

They have longitudinal velocities \(-1\) and \(+1\).
The full four-component Hamiltonian annihilates these spinors, as
verified independently of the radial profile integration.
Their gauge four-currents and the Higgs amplitude and phase sources
vanish pointwise. Thus adding occupations within these zero modes
preserves the classical straight-vortex profiles in this mean-field
specialization. The bare string energy remains
\(\mu=\pi\eta^2B(\beta)\).

This cancellation concerns occupied mean sources. Vacuum polarization,
exchange corrections and transitions into other transverse modes retain
their own matrix elements.

## Two-carrier escape requirement

In a local material rest frame, opposite massless carriers of momenta
\(k_1,k_2>0\) have invariant energy squared \(s=4k_1k_2\).
Two equal-mass bulk final particles are kinematically accessible when
\(k_1k_2>m_f^2\). For equal filled branches extending to \(k_F\), the
fraction of number pairs above this threshold is

\[
f_{\rm pair}=
\begin{cases}
0,&k_F\le m_f,\\
1-z+z\log z,&k_F>m_f,
\end{cases}
\qquad z=\frac{m_f^2}{k_F^2}.
\]

This fraction measures available initial pairs. A decay rate additionally
needs the transition amplitude, final-state occupation, recoil and
time dependence. The lab-frame centrifugal action in the
[finite-radius screen](FINITE_RADIUS_CARRIER_REQUIREMENTS.md) addresses
a different escape comparison.

The certified rotor rectangle gives the conservative proper-stretch bound

\[
\lambda\ge
\frac{1.08-0.01140}{\sqrt{1-0.3^2}}=1.12019718.
\]

For one carrier pair with \(\beta=e=g=1\), its largest required proper
\(k_F/m_f\) is 3.96616. Approximately 0.76125 of the uniformly counted
opposite-branch pairs then exceed the two-bulk-particle threshold.

## Counted carrier multiplicity

With \(N\) independent pairs of equally occupied species,

\[
u_{\rm carriers}=\frac{Nk_F^2}{2\pi},\qquad
\frac{k_F}{m_f}=\frac{\pi\sqrt{2B/N}}{g\lambda}.
\]

The occupation can therefore provide
\(u_{\rm carriers}=\mu/\lambda^2\) with

\[
U=\mu(1+\lambda^{-2}),\qquad
T=\mu(1-\lambda^{-2}),\qquad
E=\frac M2(\lambda+\lambda^{-1})
\]

under a uniform stretch and conserved particle numbers. Each added pair
contains two Dirac species. Their contributions to three unit-coefficient
loop diagnostics are retained as

\[
D_Y=\frac{2Ng^2}{16\pi^2},\qquad
D_4=\frac{2Ng^4}{16\pi^2\beta e^2},\qquad
D_A=\frac{Ne^2}{16\pi^2}.
\]

These diagnostics measure species and coupling dependence; actual
renormalized corrections depend on the field theory and prescription.
For the stated tree normalization
\(V_0=\lambda_H(\phi^2-\eta^2)^2/8\), the homogeneous fermion contribution
in the MS scheme is

\[
\Delta V_F=-\frac{2Ng^4\phi^4}{16\pi^2}
\left[\log\frac{g^2\phi^2}{Q^2}-\frac32\right].
\]

This follows from the degree-of-freedom sum in
[Martin's effective-potential convention](https://arxiv.org/pdf/hep-ph/0111209).
Its logarithmic coefficient relative to the tree quartic is \(8D_4\):
1.77312 for the 70-pair example. A quantum-corrected vortex therefore
requires explicit renormalization and inhomogeneous field response;
the smaller unit-coefficient diagnostic alone gives no potential-control
bound.

| \(\beta,e,g\) | Pairs \(N\) | Required proper \(k_F/m_f\) | \(D_Y\) | \(D_4\) | \(D_A\) |
|---|---:|---:|---:|---:|---:|
| \(1,1,1\) | 1 | 3.96616 | 0.01267 | 0.01267 | 0.006333 |
| \(1,0.5,0.5\) | 64 | 0.991540 | 0.20264 | 0.20264 | 0.10132 |
| \(1,0.5,0.5\) | 70 | 0.948094 | 0.22164 | 0.22164 | 0.11082 |

The 70-pair case closes the selected two-bulk-particle channel throughout
the declared proper-stretch envelope. It also introduces 140 hypothetical
Dirac species and collective corrections on the scale shown. It is a
field-theory requirement set, with empirical material realization open.

Using the same finite-radius criteria, its forward lab-energy bound is
\(0.426196\sqrt\mu\). The scalar core width sets
\(R\sqrt\mu\ge1621.16\), where the exterior action diagnostic is 169.56.
The corresponding six-rotor node requirement is
\(C\delta/\hbar\ge3.44707\times10^8\). This remains an instantaneous
curvature comparison, alongside the separate pair-escape and spectrum tests.

This example uses the rotor's operating stretch. At \(\lambda=1\), its
\(k_F/m_f\) is approximately 1.062; closing the same bulk threshold at
that relaxed stretch requires at least 79 pairs for \(g=0.5,\beta=1\).
Other support populations retain their own stretch and occupation ranges.

Massive *bound* modes can lie below the bulk mass. The
[massive-mode calculation](https://arxiv.org/abs/hep-ph/0106179)
shows that their occupations change the string equation of state.
The actual transverse spectrum and occupation history therefore decide
whether this multi-species candidate retains the elastic law.

## Torque and branch populations

The conserved-flavor specialization supplies a stationary host. Changing
rotor spin adds a branch-population requirement. If
\(A=R_0\sqrt{2\pi\mu/N}\), a balanced filled sea in the material rest frame
has laboratory branch populations

\[
N_\pm=A(1\pm j).
\]

Their sum stays fixed, while their difference follows the spin.
Consequently a driven rotor needs branch conversion, particle exchange,
or a broader occupied-state law. Separate branch-number conservation
alone fixes that difference. The optical torque equation therefore
requires a microscopic occupation interface as well as a stress law.

Summing the continuum occupied levels gives
\(E_{\rm carriers}=M(1+j^2)/(2x)\) and \(J=MR_0j\), recovering
the cold rotor energy when the bare string is included. This identifies
the population change the interface must produce. Its field energy,
momentum transfer, relaxation and finite-mode corrections belong to the
physical coupling calculation.

## Host, interface and evidence scope

The carrier construction supplies a one-dimensional tensile material
candidate. Two-dimensional support populations, crossings, joints and
traction boundaries need their own material tensors. Optical reflecting
surfaces, thermal receivers and electrical current hosts remain separate
components; their duties continue in the shared rail allocation.

Five tests check the Clifford algebra, full Hamiltonian, local source
bilinears, anomaly sums, independently differentiated profiles,
two-particle phase space and counted elastic energy. A four-worker audit
resolves 12 profile cases at two background resolutions and compares
360 coupling/flavor choices. Normalization includes the regular inner
core and the retained asymptotic tail.

~~~sh
PYTHONPATH=toolkit/adm_harness_cli python toolkit/adm_harness_cli/scripts/audit_neutral_fermionic_hosts.py --workers 4
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests/test_neutral_fermionic_hosts.py -q
~~~

The [evidence](data/neutral_fermionic_hosts/) retains the normalized
profiles, numerical requirements, source snapshots and provenance.
