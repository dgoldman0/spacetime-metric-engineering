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

Six initial tests check Hamiltonian force and velocity derivatives, explicit
metric work, reciprocal Ohmic conversion, ideal preservation of material heat
and electric flux, resistive energy balance, and a controlled physical
heat-depletion event. The old numerical method and evidence remain available
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
