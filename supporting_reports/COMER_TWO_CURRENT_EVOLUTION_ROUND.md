# Comer–Andersson Two-Current Evolution Round

Date: 8 September 2026.

## Question and registered scope

The [quadratic startup attempt](COMER_ANDERSSON_SPHERICAL_STARTUP_ATTEMPT.md)
matched a prescribed angular demand at a degenerate gravitational kinetic
coefficient. This round instead evolves particle and entropy currents through
their own force equations and determines the mass and lapse from their
combined stress. The initial mass profile comes from the retained rail; the
subsequent geometry follows the sources.

The signed infrastructure requires its own constitutive prescription. The
explicit choice here is a separately conserved radial-tension source. It
preserves the reference initial energy after allocating a finite particle
and thermal preload, while changing the initial pressure. That pressure
change is assessed by an independent junction calculation. The evolution
measures whether the earlier kinetic and angular difficulty survives when
the two currents and geometry evolve together. Full rail acceptance also
requires the initial worldtubes and subsequent service conditions to match.

The primary source is [Comer, Andersson, Celora, and Hawke,
arXiv:2606.17686v1](https://arxiv.org/html/2606.17686v1), particularly
equations (78)–(101). These give separate particle and entropy force
equations, a common conserved stress, and an entropy-production condition on
the resistance. This round uses a barotropic specialization of those
two-current equations with an explicit nonlinear resistance law. The
additional deformation-rate terms of model (iii) are zero in this
specialization. The signed support remains an effective source with a
specified conservation law; its microscopic realization is a separate
constitutive question.

## Two currents and positive entropy production

The rest energies are
\[
\rho_n=n^{6/5},\qquad \rho_s=s^{4/3},\qquad
p_n=\rho_n/5,\qquad p_s=\rho_s/3.
\]
Each current has its own radial four-velocity. With zero entrainment, its
stress is the corresponding perfect-fluid stress. The master-function
coefficients still vary with the evolving state:
\(\mathcal B_n=(6/5)\rho_n/n^2\) and
\(\mathcal B_s=(4/3)\rho_s/s^2\). The scalar fluid pressures are
barotropic constitutive choices, with sound speeds \(\sqrt{1/5}\) and
\(\sqrt{1/3}\).

For particle and entropy four-velocities \(u_n,u_s\), define
\[
\gamma_{ns}=-u_n\cdot u_s,\qquad
R^a=\mathcal R\left(u_s^a-\gamma_{ns}u_n^a\right),\qquad
\mathcal R=\frac{h_nh_s}{(h_n+h_s)\tau_0},\quad h_x=\rho_x+p_x.
\]
The resistance coefficient responds to both evolving enthalpies. The
positive constant \(\tau_0\) sets its scale. The force equations are
\[
\nabla_bT_n^{ab}=R^a,\qquad \nabla_bT_s^{ab}=-R^a.
\]
Since \(u_n\cdot R=0\), the particle energy equation implies
\(\nabla_a(nu_n^a)=0\). The entropy equation gives
\[
T\Gamma_s=u_s\cdot R=\mathcal R(\gamma_{ns}^2-1)\geq0,
\qquad T=\frac43\rho_s^{1/4}.
\]
Thus both the total exchange and the physical entropy production are fixed
by the same force law. The resistance is algebraic in the local state, so
the two fluid characteristic cones retain the relativistic Euler speeds
\((v_x\pm c_x)/(1\pm v_xc_x)\). The source contains no metric-rate
quadratic term, and the GR tensor kinetic coefficient remains unchanged.
These statements concern the ordinary currents and gravitational kinetic
term; a microscopic support theory would carry further characteristic
conditions.

## Conserved support and initial data

The areal metric is
\[
ds^2=-\alpha^2dt^2+A^2dr^2+r^2d\Omega^2,\qquad
A=f^{-1/2},\qquad f=1-2m/r.
\]
Choose a signed support energy \(I(r)\), with source-frame channels
\[
E_I=I(r),\qquad P_{r,I}=-I(r),\qquad J_I=0,\qquad
P_{t,I}=-I(r)-\frac r2 I'(r).
\]
Direct covariant differentiation gives \(\nabla_aT_I^a{}_b=0\) for
arbitrary time-dependent positive \(\alpha,A\). The radial pressure and
angular stress are constitutive functions of the specified support profile.
Its zero radial enthalpy makes the energy equation independent of changing
radial volume.

The domain is \(r\in[2.15,6.25]\). Let \(m_i(r)\) be the retained
initial matched-static mass and \(E_i=m_i'/(4\pi r^2)\). Allocate
\[
E_{\mathrm{pre}}(r)=\frac{0.039783\,\eta}{r^2}
\left[\sin^4\!\left(\frac{\pi(r-2.15)}{4.10}\right)+10^{-8}\right],
\qquad I=E_i-E_{\mathrm{pre}}.
\]
The amplitude uses the existing radial-string energy scale. The small
positive floor defines the dilute boundary states. Half of the initial
source-frame preload energy is assigned to each ordinary fluid. Particle
velocity is \(v_n=v_0\sin^4[\pi(r-2.15)/4.10]\); the entropy velocity
is recovered from the opposite current \(J_s=-J_n\). The total initial
energy is exactly \(E_i\) and the total initial current is zero, so the
initial Hamiltonian and momentum data match \(m_i\).

The changed support pressure is an explicit part of this new initial state.
Its lapse is determined by the new radial pressure. The previous prescribed
mass path, static-start acceleration, and initial lapse profile are free to
change in this local evolution. Matching to the reference worldtubes remains
an independent condition.

## Coupled equations and numerical design

For each fluid, source-frame moments are
\[
E_x=(\rho_x+p_x)\gamma_x^2-p_x,\quad
J_x=(\rho_x+p_x)\gamma_x^2v_x,\quad
P_{r,x}=J_xv_x+p_x,\quad P_{t,x}=p_x.
\]
At every Runge–Kutta stage, the total energy and radial pressure determine
\[
m_r=4\pi r^2E,\qquad
\nu_r=\frac{m+4\pi r^3P_r}{r^2f},\qquad \nu=\log\alpha.
\]
The outer boundary fixes \(\alpha=1\). The momentum equation gives
\[
m_t=-4\pi r^2\alpha\sqrt f\,J,\qquad
k=\frac{A_t}{A}=-4\pi r\alpha A J.
\]
For force components \((Q_{E,x},Q_{J,x})\), the two Euler equations are
\[
\partial_tE_x=-\frac1{Ar^2}\partial_r(\alpha r^2J_x)
-\frac{\alpha_r}{A}J_x-k(E_x+P_{r,x})+\alpha Q_{E,x},
\]
\[
\partial_tJ_x=-\frac1{Ar^2}\partial_r(\alpha r^2P_{r,x})
-\frac{\alpha_r}{A}E_x+\frac{2\alpha P_{t,x}}{Ar}
-2kJ_x+\alpha Q_{J,x}.
\]
Their summed conservation equation and the radial constraints imply the
remaining Einstein equation for a regular continuum solution. Independent
four-dimensional curvature probes measure the angular equation numerically.

The finite-volume method reconstructs logarithmic rest energy and rapidity,
uses local relativistic characteristic speeds in a Rusanov flux, and advances
with two-stage strong-stability-preserving Runge–Kutta. The initial reference
mass is represented separately from the integrated fluid-energy perturbation.
This preserves its small positive inner \(f\) without subtracting large
quadrature approximations. The inner mass evolves with the boundary flux.
Both numerical boundaries admit outward escape from the domain and supply
zero inflow. Particle, entropy, and mass balances include the recorded
boundary fluxes; the entropy balance also includes \(\alpha A\Gamma_s\).

Four scenarios are fixed: \((\eta,\tau_0,v_0)=(0.01,2,0.04),
(0.01,0.25,0.04),(0.1,2,0.04),(0.01,2,0)\). Each runs to time 4
at 128, 256, and 512 cells, with 81 retained times. The run uses four
workers, a 600-second compute budget, a 1,536 MiB address-space limit per
worker, and an 80 MB evidence budget. A nonpositive polar metric or invalid
ordinary-fluid state stops that evolution. No further support profile,
matching layer, or fitted coefficient is added after the registered tests.

## Initial worldtube condition

The retained initial rail has \(h_i=E_i+P_{r,i}<0\) throughout the
annulus. The radial-tension support contributes zero to \(E+P_r\), while
both ordinary currents contribute positive radial enthalpy. At either
boundary, the prescribed initial velocities vanish, so
\[
P_{r,\mathrm{candidate}}-P_{r,i}
=\left[1+\tfrac12(1/5+1/3)\right]E_{\mathrm{pre}}-h_i>0.
\]
For the same initial mass and radius, the jump in the acceleration component
normal to the static worldtube, oriented toward increasing radius, is
\[
\Delta a_\perp=\frac{4\pi r}{\sqrt{f_i}}\Delta P_r.
\]
Thus this source choice fails the initial shell-free junction already at
zero preload. The quantity measures extrinsic geometry and survives a time
coordinate relabeling. The local evolution is retained to distinguish the
behavior of the coupled currents from this independent embedding failure.
