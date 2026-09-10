# Refinement of the active endpoint reservoir ensemble

Date: 10 September 2026.

The proposed reservoir combines elastic mechanical support, local thermal
storage, and a confined electromagnetic store with passive heat conversion.
Its endpoint partner remains the reconstructed heat/current medium on the
full scheduled rail metric. The present refinement first resolves the
internal-heat verification barrier identified in the
[electromagnetic comparison](ELECTROMAGNETIC_ENDPOINT_STORAGE_INVESTIGATION.md),
then tests the resulting response against its operating interval and source
accounting requirements.

## Component responsibilities and operating gates

| Duty | Supplied variables and tensor | Required check |
| --- | --- | --- |
| Longitudinal support | Conserved material labels, deformation, and momentum; the existing positive-energy elastic law | Timelike material motion, positive ordered strain, causal longitudinal response, and counted end reactions |
| Thermal buffer | Heat per material reference unit, with positive heat capacity | Positive local heat throughout the required interval, with its complete power/work balance |
| Electromagnetic store | Radial electric flux and the Maxwell tensor, including angular pressure | Finite counted field energy, confined charge arrangement, reciprocal Lorentz work, and nonnegative Ohmic heating |
| Endpoint heat/current medium | The archived active fitted tensor and its power and force divergence | Opposite reservoir exchange on the prescribed history; a responding microscopic contact law remains required for a complete plant |
| Thermal redistribution | Existing endpoint routing plus an eventual material transport law | A local heat buffer supplies capacity. Any added internal heat current requires its own energy, momentum, propagation law, and exchange budget. |
| External support | Reaction forces at the two fixed material ends | Explicit force and power ports; their anchor material tensors remain a separate construction |

The first worldtube remains \(-2.1\leq\ell\leq-0.5\), starting at
service coordinate \(s=0\). The first verification interval ends at 0.5.
Successful candidates can then be tested through release at 0.745, the
carrying-flow fade ending at 1.285, and reset through 3. The earlier
preparation interval remains an additional spatial and causal matching task.
This late patch carries 35.75% of the previously measured full-interval
exchange weight. The original standing backbone, angular jacket, and live
handoff components retain their own duties.

## Material-coordinate energy formulation

Let \(a\) denote conserved material reference length and \(x(s,a)\) the
material position. With radial metric scale \(B\), lapse \(\alpha\),
shift \(\beta\), and areal radius \(R\),

\[
v=\frac{B}{\alpha}(\partial_sx+\beta),\qquad
\Gamma=(1-v^2)^{-1/2},\qquad
n=\frac{1}{B\Gamma\partial_a x}.
\]

The elastic line energy and pressure retain their previous definitions:

\[
\epsilon=n(m+q)+\frac K2(n-1)^2,\qquad
p=\frac K2(n^2-1),\qquad K=0.1,\quad m=1,\quad A=0.4.
\]

The reversible matter action is
\(-A\int\alpha B\epsilon\,dx\,ds\). The material-coordinate
description of relativistic elasticity and its variational stress are
developed in [Brown's review](https://arxiv.org/abs/2004.03641).
The discretization and electromagnetic specialization below are the present
calculation's choices.

Material cell \(i\) has conserved reference length \(\mu_i\), width
\(h_i=x_{i+1}-x_i\), and endpoint quadrature stretches
\(n_{i,j}=\mu_i/(B_j\Gamma_jh_i)\). Each cell contributes half its
action at each end, with that end's velocity and heat. This keeps the
canonical momentum inversion local while retaining a strain energy that
responds to each individual cell width.

Define nodal weights
\(M_j=(\mu_{j-1}+\mu_j)/2\), with one-sided half weights at the body
ends, and \(V_j=(h_{j-1}+h_j)/2\). A useful form of the matter Lagrangian
at node \(j\) is

\[
L_j=-A\alpha_j\left[
\frac{M_j(m+q_j-K)}{\Gamma_j}
+\frac{a_j}{\Gamma_j^2}+b_j\right],\qquad
a_j=\frac{K}{4B_j}\sum_{i\sim j}\frac{\mu_i^2}{h_i},\quad
b_j=\frac{KB_j}{4}\sum_{i\sim j}h_i.
\]

Its canonical momentum is

\[
\pi_j=AB_jv_j\left[M_j(m+q_j-K)\Gamma_j+2a_j\right].
\]

The electric variable \(Q_j=R_j^2E_j\) follows the same material label.
The discrete field energy is
\(U_{{\rm em},j}=B_jV_jQ_j^2/(2R_j^2)\), and the canonical energy is

\[
H=\sum_j\left[\alpha_j(U_{{\rm mat},j}+U_{{\rm em},j})
-\beta_j\pi_j\right].
\]

Material velocities and forces are derivatives of this same energy. Its
explicit temporal dependence supplies the geometric-work ledger. Therefore
the active lapse, shift, radial stretch, and angular evolution enter the
motion and energy balance together. The independently reported ADM-slice
energy is \(4\pi\sum_j(U_{{\rm mat},j}+U_{{\rm em},j})\); the canonical
energy has different lapse and shift weights.

The effective nodal number density is
\(n_j=M_j/(B_j\Gamma_jV_j)\). The material heat and electric flux obey

\[
\dot q_j=-\frac{\alpha R^2}{An}(P-vF)
+\frac{\alpha R^2}{An\Gamma}\sigma E^2,
\qquad
\dot Q_j=-\frac{\alpha\sigma}{\Gamma}Q_j.
\]

The conductivity remains the local passive switch from the preceding trial.
Because \(\partial H/\partial q_j=AM_j\alpha_j/\Gamma_j\), the heat
gain from Ohmic conversion cancels the field-energy loss in \(\dot H\).
For an ideal field and zero endpoint exchange, every \(q_j\) and \(Q_j\)
is constant under this material evolution. A thermal floor is a stopping
condition, with no heat injection or energy correction at that floor.

The endpoint momentum source is
\(-\alpha B^2R^2V_jF\). Together with the heat term it gives the
canonical power
\(-\alpha BR^2V_j(\alpha P-\beta BF)\). The constrained end momenta
have reaction forces derived from their required motion. Their canonical
work vanishes for fixed coordinate ends; their physical force and
shift-dependent ADM work remain counted ports.

## Registered comparison and verification

The total additional reserve uses the preceding ratio-4 prescription and the
capacitor flux profile. The main ensemble places three quarters of that
additional initial ADM energy into material heat and one quarter in the
field. Controls allocate the whole reserve to either store, remove the
reserve, disable resistance, or disable endpoint exchange. Initial material
positions, reference amounts, and coordinate-rest velocities are shared.
Adding heat at those velocities changes the initial canonical momentum by
its specified inertia contribution; this preparation differs from the
previous cellwise fixed-momentum allocation control.

Seven initial tests check Hamiltonian force and velocity derivatives, explicit
metric work, reciprocal Ohmic conversion, ideal preservation of material heat
and electric flux, resistive energy balance, and a controlled physical
heat-depletion event, and convergence of the discrete electromagnetic force
to the covariant Lorentz force. The old numerical method and evidence remain available
for comparison.

Active controls begin at 64 material cells and four workers. Spatial
refinement and time-step refinement distinguish continuum response from
integration error. The canonical energy is recomputed from positions,
momenta, heat, and field at each output; it is compared with independently
integrated geometric and endpoint power. The thermal ledger verifies the
implemented heat equation, while the recomputed energy checks whether that
heat was paid for by the combined system. A numerical limit receives its own
classification before any source-family conclusion.

The main disclosure and its PDF retain their existing design content. This
supporting report records the bounded research construction and its tests.

## First active verification milestone

The material-coordinate ideal-field control completes \(s=0.5\), preserving
every material heat value and electric flux. The previously observed
zero-exchange temperature collapse is removed. The forced field-only case
also reaches 0.5, with minimum heat 0.09118 and integrated Ohmic heat 0.03287
per solid angle. The mixed ensemble and thermal-only control retain minimum
heat 0.25 through the same interval. Their initial reserve follows the
registered fixed-energy allocation; the mixed ensemble's conductivity remains
inactive over this first interval because its thermal preparation covers
the withdrawal.

The original elastic-only control retains a physical heat stop, moving from
\(s=0.38387\) at 64 cells to 0.37998 at 128 cells. This approaches the
earlier refined depletion time while using explicit material heat evolution.

The first electromagnetic runs have recomputed canonical-energy errors near
0.5 against initial energies around 34,700. Direct directional derivatives
of the actual active states reproduce the registered energy-power identity;
the remaining error is accumulated time integration during strong compression.
Reducing the maximum step alone leaves much of it because the material-wave
step restriction is already controlling. The next verification therefore
also refines that restriction, from a Courant factor of 0.2 to 0.05, before
using the electromagnetic response for longer-interval conclusions.

## Time accuracy, spatial response, and release

The tighter Courant factor reduces the mixed ensemble's maximum canonical
energy error to 0.009092 through 0.5, a reduction of approximately sixtyfold.
At the final time, temporal refinement changes material positions by an RMS
of \(2.98\times10^{-5}\), velocities by \(3.04\times10^{-4}\), and heat by
\(2.23\times10^{-7}\). Relative RMS changes in density and radial stress
are \(5.42\times10^{-5}\) and \(7.24\times10^{-5}\), respectively.

Spatial refinement exposes a different limitation. At the last common
64/128-cell output, \(s=0.415\), the mixed ensemble has RMS position
and velocity differences of 0.00320 and 0.218. Its density and radial stress
differ by 55.5% and 47.6% in relative RMS. The thermal-only comparison at
0.5 gives 58.0% and 91.7% differences in those tensor components. The
undamped material develops short compressional waves whose supplied stress
requires further resolution or a physically specified dissipative response.
These comparisons use the same normalized material labels, with stress
evaluated on their respective trajectories.

The tight 128-cell electromagnetic run reaches its wall-time budget at
0.41921 with positive heat. The longer 64-cell runs instead reach the
positive-temperature stopping boundary: the mixed ensemble at 0.765334 and
thermal-only at 0.819701. Their maximum canonical-energy errors are 0.01169
and 0.0004932. Both stops occur during release, which begins at 0.745.
Consequently the original allocation provides a verified early heat buffer,
while the release heat duty remains open alongside spatial stress convergence.

## Registered internal-strain relaxation

The next bounded comparison adds one local mechanical relaxation variable
\(z\). Relativistic viscoelastic theories supply an established framework
for finite relaxation and entropy production; see
[Fukuma and Sakatani](https://arxiv.org/abs/1104.1416). Their results motivate
this component. The following energy law and its discretization are a
separate specialization derived for the present reservoir.

With physical rest mass \(m=1\), baseline stiffness \(K_0=0.1\), and
additional stiffness \(\kappa=0.1\), choose

\[
\epsilon=n(m+q)+\frac{K_0}{2}(n-1)^2
 +\kappa n\{\cosh(\log n-z)-1\},\qquad
p=\frac{K_0}{2}(n^2-1)+\kappa n\sinh(\log n-z).
\]

The added energy is nonnegative. At fixed heat and internal strain, define
\(c=m+q-K_0-\kappa>0\) and \(k=K_0+\kappa e^{-z}\). Then

\[
\epsilon_n=c+kn,\qquad p_n=kn,\qquad
c_L^2=\frac{kn}{c+kn}\in(0,1),\qquad
\epsilon-p=nc+K_0+\kappa e^z>0,\qquad
\epsilon+p=n(c+kn)>0.
\]

These inequalities give the material's positive energy, dominant-energy
margin, and causal frozen-strain longitudinal characteristic throughout
\(n,q>0\), \(z\in\mathbb R\), and \(K_0+\kappa<m\).
They concern the longitudinal constitutive system on the prescribed
background. Full transverse and coupled gravitational stability retain
their separate tests.

Let \(\delta=\log n-z\). The continuum relaxation law, in material proper
time, is

\[
\frac{dz}{d\tau}=\frac{\delta}{\tau_r},\qquad
\left.\frac{dq}{d\tau}\right|_{\rm rel}
=\frac{\kappa\delta\sinh\delta}{\tau_r}\geq0,
\qquad \tau_r=1.
\]

The heat gain exactly equals the loss from internal-strain relaxation.
It therefore supplies damping with counted energy and nonnegative entropy
production for the unit-heat-capacity choice \(S=\log q\). The reference
strain evolves locally with finite proper relaxation time.

For the existing two-endpoint quadrature, each node uses
\(n_{\rm rms}=\sqrt{\tfrac12\sum\mu_i^2/h_i\,/V_j}/(B\Gamma)\)
and \(n_{\rm eff}=M_j/(B\Gamma V_j)\). The nodal rates replace
\(\delta\) by \(\log n_{\rm rms}-z\) and multiply the heat rate by
\(n_{\rm rms}/n_{\rm eff}\). This preserves exact cancellation in the
discrete canonical energy. The action coefficients acquire
\(K_0+\kappa e^{-z}\) and \(K_0+\kappa e^z\) in their quadratic
and constant terms, while their linear term contains \(m-\kappa\).
That linear coefficient is the algebraic expansion of the displayed
positive energy; the physical rest mass remains one.

Initialization sets \(z=\log n_{\rm rms}\), minimizing the nodal
internal-strain energy. Neighboring quadrature densities can differ, so
their finite-grid minimum has a small positive energy that remains in the
reported initial inventory. The same reserve allocation and active endpoint
history are retained. Four 32-cell controls compare the mixed ensemble,
thermal-only storage, a frozen internal strain with identical initial
elastic energy, and an unforced mixed ensemble. The single registered
choice \(\kappa=0.1,\tau_r=1\) precedes any active result. Spatial
refinement, release survival, and independent canonical-energy balance
determine whether this refinement is useful.

Six constitutive and evolution tests cover the energy-derived pressure and
wave speed, the zero-modulus limit, reciprocal relaxation heating,
Hamiltonian forces, and energy and anchor-momentum balances in both a
flat control and a metric with active lapse, shift, radial scale, and radius.
