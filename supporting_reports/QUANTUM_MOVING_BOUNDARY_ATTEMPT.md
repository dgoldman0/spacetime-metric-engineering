# Quantum Field with Moving Material Boundaries

Date: 8 September 2026.

## Registered question and model

The [vacuum support comparisons](VACUUM_SUPPORT_SELECTION_ROUNDS.md) match the
initial rail tensor algebraically, while their local elastic identification
has negative radial kinetic energy. This round retains independent quantum
field degrees of freedom and lets their radiation pressure determine the
motion of material boundaries.

The bounded model is a real scalar field in 3+1 dimensional flat spacetime,
with translational symmetry parallel to two partially transmitting planar
walls. The normal direction includes the gap and its exterior. Transverse
Fourier modes reduce the calculation to independent one-dimensional quantum
oscillator systems. The wall positions are \(z=\pm a(t)/2\); each has
positive bare mechanical mass per area \(\sigma\). Their separation has bare
wall reduced mass \(\mu_W=\sigma/2\). The field starts in the two-wall Gaussian ground
state. Subsequent mode functions and the wall separation evolve together.

This is a local source-model calculation. The retained curved rail metric
and its service conditions provide the subsequent stress requirements;
the present evolution takes place in the planar model. Its scope includes
the field inside and outside the gap and the mechanical boundary work.
Mirror force fluctuations and a quantum wave function for the wall motion
remain beyond this semiclassical mean-force approximation.

The partially transmitting scalar-wall interaction follows the model class
of [Fosco, Giraldo, and Mazzitelli](https://arxiv.org/abs/1704.07198).
We resolve a finite Gaussian thickness in place of the singular wall.
The need to retain field back-reaction and its energy balance is also
developed in [Butera](https://arxiv.org/abs/2603.13932v1). Our numerical
Hamiltonian keeps the Gaussian field explicitly instead of truncating a
time-derivative expansion of its force. These source papers motivate the
interaction and balance conditions; the finite regulator and numerical
implementation below are specified for this investigation.

In units \(\hbar=c=a(0)=1\), the normal box has length 12 and periodic
boundaries. Each wall contributes
\[
V_j(z,a)=\frac{8}{\sqrt{2\pi}\,0.16}
\exp\left[-\frac{(z-z_j)^2}{2(0.16)^2}\right].
\]
The positive potential gives reflection at low frequency and increasing
transparency at high frequency. It carries a finite physical thickness.
The two-dimensional transverse integral is
\(\int_0^8 k\,dk/(2\pi)\). A real Fourier basis includes normal harmonics
through \(m_{\max}\), giving \(2m_{\max}+1\) canonical oscillators.
The registered levels use
\((m_{\max},N_k,h)=(16,8,0.02),(24,12,0.01),(32,16,0.005)\).
The finite field bandwidth is explicit. These levels compare the normal
cutoff and integration accuracy; temporal convergence is checked separately
using the middle bandwidth at steps 0.02, 0.01, and 0.005 for the released
and moving-held cases. Static transverse cutoffs 8 and 12 are compared
through normal harmonic 48. Their interaction observables and one-wall
dressing energies are recorded separately.

Four scenarios run for at most three gap light-crossing times:

| Scenario | Wall mass per area | Holding stiffness | Initial separation velocity |
|---|---:|---:|---:|
| Equilibrium control | 1 | 0.5 | 0 |
| Released walls | 1 | 0 | 0 |
| Released lighter walls | 0.25 | 0 | 0 |
| Moving held walls | 1 | 0.5 | 0.02 |

For held walls the spring's natural separation balances the calculated
initial quantum force. The spring's stored energy is included. Its holding
mass per area is \(M_H=4K(1.20)^2\), supplying a nominal longitudinal speed
\(a\sqrt{K/M_H}\leq1/2\) over the permitted range and a separately
checked axial-energy margin. Uniform extension contributes \(M_H/12\)
to the separation's reduced inertia. This specifies the single mechanical
mode retained for the holding structure; its full internal modes remain
outside the calculation.
Released cases have neither a holding force nor that allowance.

Each evolution stops if the separation leaves \([0.65,1.20]\), either
wall's speed exceeds 0.10, a field operator loses positivity, or the
registered numerical budget is reached. The speed limit bounds corrections
to the finite-width wall shape and the single-mode representation of the
holding structure.

## Coupled Hamiltonian and energy accounting

The wall interaction retains the proper-time factor
\(\chi=\sqrt{1-\dot a^2/4}\). For Gaussian mode matrices \(F_k,P_k\),
let \(U=\frac12\sum_k w_k\operatorname{tr}(F_k^\dagger V(a)F_k)\)
denote the positive expectation of the two wall potentials. With
\(\mu_0=\sigma/2+M_H/12\), \(M_0=4\mu_0\), and separation momentum
\(p_a\), the finite mean-field Hamiltonian per area is
\[
H=E_{\mathrm{free}}[F,P]+B+\tfrac12 K(a-a_\mathrm{nat})^2+2M_H/3,
\qquad B=\sqrt{(M_0+U)^2+4p_a^2}.
\]
Here \(E_{\mathrm{free}}[F,P]\) contains the canonical scalar kinetic
and gradient energies. The last constant restores the rest energy of the
holding structure after its separation-mode inertia has been included.
The equations are
\[
\dot a=\frac{4p_a}{B},\qquad
\dot p_a=-\frac{\chi}{2}\sum_k w_k
  \operatorname{tr}(F_k^\dagger V_a F_k)-K(a-a_\mathrm{nat}),
\]
\[
\dot F_k=P_k,\qquad
\dot P_k=-[K_{\mathrm{free}}+k^2+\chi V(a)]F_k,
\qquad \chi=(M_0+U)/B.
\]
The positive interaction expectation adds \(U/4\) to the rest separation
inertia. The scalar kinetic term and the bare mechanical kinetic term
are positive. Positive scalar wall coupling contributes a cutoff-dependent
mirror mass in the underlying wall model as well; the discussion around
equation 14 of Fosco, Giraldo, and Mazzitelli gives this dependence explicitly.

The discrete-gradient integrator pairs an exact Gaussian field step at an
averaged operator with the same averaged force in the wall equation.
Its common difference quotient of \(B\) preserves the total Hamiltonian;
quantum mode normalization is preserved by the oscillator step. Time-step
refinement separately tests the resulting trajectory. Free-subtracted
spatial stresses use the actual instantaneous coupling \(\chi V\).
Excitation and the force lag compare the evolved state with the ground
state of that same instantaneous operator.

Energy histories split \(H\) into \(E_\mathrm{free}+U\) and
\(B-U+K(a-a_\mathrm{nat})^2/2+2M_H/3\). These two complementary
bookkeeping components exchange energy while their sum stays fixed.
The physical scalar profile energy at nonzero velocity uses
\(E_\mathrm{free}+\chi U\), also recorded separately.

The static Casimir interaction is
\(E_\mathrm{int}=E_g[V_1+V_2]-2E_g[V_1]+E_g[0]\).
The total free-subtracted field energy instead retains both one-wall
dressing contributions. A finite barrier width regulates spatial shape;
the scalar one-body energy still depends on the field bandwidth.
Matching a microscopic material's measured mass, dispersion, and
renormalized stress would supply further physical input. The present
positive-bare-mass calculation makes this dependence explicit.

The finite-width profile is translated at fixed laboratory width with the
proper-time coupling retained. The mechanical coordinate follows a
semiclassical mean force. These are the specified approximations of this
local planar prototype.

The tests require conservation of field-plus-mechanical energy, preservation
of quantum mode normalization, and improving temporal and spatial
agreement. Static ground-state forces are checked against energy
derivatives. The final rail comparison includes both wall masses, the
one-wall field dressing, the vacuum interaction energy, and the holding
contribution. It tests the sign of the energy of locally homogenized
complete cells against the retained initial rail profile. Placing negative
gaps and positive boundaries in spatially distinct parts of a curved
construction requires a separately resolved geometry.

Four worker processes and single-thread numerical libraries are used.
The main calculation has a 600-second allowance, 1,536 MiB address space
per worker, and a 40 MB evidence allowance. State summaries are retained
at 61 times, with spatial field profiles at five times and complete final
mode functions and momenta. Initial states follow from the retained
operators and their ground-state spectra. The narrative report is written
manually.
