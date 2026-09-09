# Comer–Andersson Spherical Startup Attempt

Date: 8 September 2026.

## Question and scope

The [bounded reset search](LE_RESET_INVERSE_SEARCH.md) found an angular
startup mismatch for source laws whose additional material stress starts too
late. This attempt examines the deformation-rate dependence in Comer,
Andersson, Celora, and Hawke's model (iii), then tests one explicit quadratic
choice of that dependence. The question is whether the new term supplies
the required angular stress with consistent density, radial pressure, entropy
behavior, and regular gravitational dynamics.

The retained initial data are the same matched-static controls, on the same
areal annulus. Particles start at rest in the areal frame; a pre-existing
thermal sector supplies a finite heat-current capacity. The direct and
waypoint mass/lapse paths remain prescribed in this attempt. The analysis
therefore tests an inverse constitutive specialization on those paths. An
initially moving medium, different mass/lapse evolution, and a fully specified
nonlinear two-current action define broader constructions.

## Paper reduction

The primary source is [Comer et al., arXiv:2606.17686v1](https://arxiv.org/html/2606.17686v1),
especially equations (35), (149)–(162), and (168)–(172). Model (iii) permits
the entropy three-form to depend on proper-time derivatives of material
metrics. Equation (150) then contains a derivative of the spatial tensor
\(D^{ab}_{6}\). This is the candidate source of an earlier angular response.

The paper's controlled simplification makes the additional choice
\(D^{ab}_{6}=\upsilon_6\widetilde D_4 h^{ab}\), with
\(\widetilde D_4=O(v_s^2)\), where \(v_s\) is entropy drift. The viscosity
terms are proportional to expansion and shear. The
[2024 companion paper](https://eprints.soton.ac.uk/495878/1/entropy-26-00621.pdf)
develops the constitutive metric dependence underlying these terms. The
positive entropy expression in the simplified limit pertains to those
additional choices. The quadratic functional below is a separate choice
within the general allowed dependence and carries its own entropy test.

Write
\[
ds^2=-N^2dt^2+L^2dr^2+R^2d\Omega^2,\qquad
H_r=N^{-1}\partial_t\log L,\quad
H_t=N^{-1}\partial_t\log R,\quad
\Theta=H_r+2H_t.
\]
The material rate tensor is \(B^i{}_j=\operatorname{diag}(H_r,H_t,H_t)\).
In the retained areal paths \(R=r\), so \(H_t=0\). If the first change
in \(\log f\), with \(f=L^{-2}\), is order \(u^n\), then
\(H_r=O(u^{n-1})\) and its proper-time derivative is \(O(u^{n-2})\).
The required current is
\(J=-\sqrt f H_r/(4\pi r)\).

With finite initial thermal density and bounded transport coefficients,
the heat drift is \(O(u^{n-1})\). Consequently the published simplified
closure has the following onset orders:

| Contribution | Direct path, \(n=3\) | Waypoint path, \(n=9\) |
|---|---:|---:|
| Required angular time-curvature stress | 1 | 7 |
| Ordinary bulk/shear viscous stress | 2 | 8 |
| Derivative of the simplified \(D_6\) | 3 | 15 |
| Diagonal correction from preloaded heat drift | 4 | 16 |

Thus preloading the thermal sector regularizes its heat capacity while the
published simplified deformation term still enters too late for these
static-start paths. Independent initial motion or a different internal
material evolution can alter these orders.

## Explicit quadratic functional

The single additional rate-sector choice is
\[
Q=\frac12\left[a\Theta^2+b B_{ab}B^{ab}\right],\qquad
S_Q=\int\sqrt{-g}\,Q\,d^4x,
\]
with constant coefficients \(a,b\). These invariants are built from the
material metric and its proper-time derivative, as permitted in the general
model. This specialization can be represented explicitly by a thermal
master energy \(\epsilon=C s^{1+w}\), \(w=1/3\), and a scaled entropy
three-form
\[
s_{ABC}=F\,\bar s_{ABC},\qquad
F=\left(1-\frac{Q}{\bar\epsilon}\right)^{1/(1+w)},\qquad
\bar\epsilon=C\bar s^{1+w}>Q.
\]
Here \(\bar s_{ABC}\) is a closed reference three-form. Substitution gives
\(-\epsilon=-\bar\epsilon+Q\). A particle rest-energy term may be included
in the master function. This establishes a specific functional dependence;
its entropy production and equations of motion remain physical conditions.

Varying the lapse and both spatial scale factors before imposing \(R=r\)
gives
\[
\rho_Q=Q,\qquad
p_{i,Q}=Q-\dot C_i-\Theta C_i,\qquad
C_i=a\Theta+b H_i,
\]
where the dot denotes particle proper time. The rate sector carries zero
radial current in this comoving reduction. An independent weak variation of
the action checks all three expressions, including a case where \(Q=0\)
on the areal trajectory while its angular variation is finite.

For \(H_t=0\), writing \(H=H_r\), the channels reduce to
\[
\rho_Q=\tfrac12(a+b)H^2,\qquad
p_{r,Q}=-(a+b)\dot H-\tfrac12(a+b)H^2,
\]
\[
p_{t,Q}=-a\dot H+\tfrac12(b-a)H^2.
\]
The instantaneous static tensor of the same metric differs from its full
Einstein tensor by a current and the angular time-curvature term
\[
P_{t,G}-P_{t,G}^{\mathrm{static}}=-\frac{\dot H+H^2}{8\pi}.
\]
Matching that angular term while retaining the prescribed density and radial
pressure therefore fixes
\[
a=\frac1{8\pi},\qquad b=-\frac1{8\pi}.
\]
Preloaded heat produces additional diagonal corrections at higher onset
order. They preserve this leading coefficient requirement under the stated
static-start assumptions. The numerical tensor fit records the required
current separately, so it supplies a rate-sector match rather than a completed
two-current source.

## Kinetic and entropy conditions

For material worldlines normal to the slices, the Einstein–Hilbert kinetic
density is \((B_{ab}B^{ab}-\Theta^2)/(16\pi)\). The fitted \(Q\) cancels
it. More specifically, the quadratic kinetic coefficient of a transverse,
traceless metric perturbation, divided by its GR value, is
\[
K_{\mathrm{TT}}=1+8\pi b.
\]
At the exact tensor match \(K_{\mathrm{TT}}=0\). Thus the apparently exact
stress correction sits at a degenerate gravitational principal part. The
acceptance condition requires a strictly positive tensor kinetic coefficient.
This diagnostic concerns the explicit constant-coefficient action; the
characteristics of the full general Comer–Andersson system remain a separate
problem.

The entropy test is also explicit. In the comoving limit,
\(\dot{\bar\epsilon}=-(1+w)\Theta\bar\epsilon\), and the closed reference
entropy current implies
\[
\frac{\Gamma_s}{s}=\frac{\dot F}{F}
=-\frac{\dot Q+(1+w)\Theta Q}{(1+w)(\bar\epsilon-Q)}.
\]
For the quadratic action, \(Q=(a+b)H^2/2\). When \(a+b>0\), increasing
the magnitude of the initial deformation rate gives negative entropy
production at order \(u^{2n-3}\). When \(a+b<0\), the corresponding
negative contribution occurs during the return to zero rate. Since \(F=1\)
at both rate-free endpoints, any nonconstant intermediate \(F\) returns
to its original value. Its comoving entropy derivative changes sign.
Ordinary finite-coefficient heat and viscous production scale one order
later at these endpoints. The exact match has \(Q=0\) on the areal path
and avoids this entropy variation, while retaining the kinetic degeneracy.

## Numerical contract

Four independent scenarios combine the direct and waypoint paths with
\((T,z)=(4,-0.65)\) and \((14.255,0.65)\). Each is evaluated at
129 × 65, 257 × 129, and 513 × 257 radial/time points. The controls, written
as \((8\pi a,8\pi b)\), are
\((0,0),(1,-1),(1,0),(0,1),(0.975,-0.95),(1,-1.25)\).
An independent linear least-squares fit uses the density, radial-pressure,
and angular channels simultaneously. Full four-dimensional curvature probes
compare the dynamic and matched-static tensors at three finite-difference
steps and retain their complete eigensystems.

The heat diagnostic retains the required current explicitly. For a thermal
fluid with \(p=w\rho\), energy \(E\) and current \(J\) in the particle
frame obey
\[
\frac{J}{E}=\frac{(1+w)v_s}{1+w v_s^2}.
\]
With \(w=1/3\) and \(|v_s|\leq0.1\), this requires
\(E\geq7.525|J|\). One positive diagnostic thermal normalization, fixed
across resolutions and controls, supplies that capacity and keeps every
entropy root real. Its initial Tolman profile and comoving adiabatic
continuation are recorded, together with the mass cost of adding that initial
profile to the frozen source. This prices the assumed preload; matching it
to the existing signed infrastructure remains part of a full construction.

The Cattaneo column records the required combination
\(\nabla_r T+T a_r=-(\tau\dot J+J)/\kappa\), using positive unit
\(\tau,\kappa\) in the reference units. It is an inverse transport demand.
The constituent force equations, a common evolving temperature, and the full
model-(iii) corrections to heat transport would be required for a survivor.

The run uses four workers with a 1,536 MiB address-space limit per worker,
a 600-second compute cap, and a 100 MB output cap. No additional source
layer, coefficient function, or matching surface is introduced after a failed
test of this specialization. Narrative findings are written manually.
