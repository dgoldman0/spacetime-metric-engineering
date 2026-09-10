# Electromagnetic storage and the endpoint heat balance

Date: 10 September 2026.

The elastic trial identifies a local heat-delivery requirement. Its first
depleted material element exhausts its thermal energy while the whole body's
thermal inventory rises from 5.5689 to 5.8746. The selected material law has
zero thermal expansion and no internal heat transport. Consequently, the
available strain energy and the heat in neighboring elements require specified
conversion or transport before they can meet that element's demand.

## Comparison against the existing results

| Option | Evidence and useful property | Remaining selection question |
| --- | --- | --- |
| Elastic support with revised thermal coupling | The [elastic trial](ELASTIC_ENDPOINT_STORAGE_INVESTIGATION.md) supplies a positive-energy longitudinal response through a finite active segment. Its refined heat balance identifies the local withdrawal mechanism. | Can causal thermal transport, dissipation, and endpoint feedback coordinate heat with moving material? Additional strain preload alone leaves this coupling unspecified. |
| Confined compressible fluid | Compression and advection provide evolving pressure and enthalpy. | A fluid moving along the same unfavorable heat history can also deplete locally. Heat transport, confinement reactions, and an equation of state require construction. No corresponding active-patch fluid calculation has established an advantage. |
| Interacting material and entropy currents | The [independent-current trial](COMER_TWO_CURRENT_EVOLUTION_ROUND.md) demonstrates local dynamical transport with counted resistance and positive entropy production on its registered background. | The active packet-excluding reservoir, container, initial history, and reciprocal endpoint response still require a joint solution. The earlier background and junction differ from this active patch. |
| Electromagnetic storage coupled to support | Maxwell stress supplies an independent, positive field-energy store; resistive conversion supplies material heat with a specified sign. | Field stresses, charges, current paths, conversion rate, and the support response must accompany the stored energy. A nondissipative field exchanges mechanical work and supplies zero Joule heat. |
| Coordinated components | [Constraint card 006](../component_design/constraints/006_regulated_heat_current_medium_support_reservoir.md) already separates heat/current routing, a regulator buffer, and elastic or field storage. | The immediate task is to close their reciprocal exchanges and thermal state dependence. The existing angular jacket and standing backbone retain their distinct duties. |

These results support an electromagnetic/material continuation. They provide
no demonstrated implementation or maintenance ranking between a field store
and confined fluids. Moreover, charge transport and fluid heat transport can
share a coupled construction: [Andersson's charged-multifluid treatment](https://arxiv.org/abs/1204.2695)
includes interacting heat and charge fluxes with relaxation, while the
[Andersson–Dionysopoulou–Hawke–Comer formulation](https://arxiv.org/abs/1610.00449)
develops Ohm, heat, and thermoelectric equations within the same framework.

## Registered bounded electromagnetic calculation

The first specialization adds a radial electric-field store to the prepared
soft, higher-amount elastic body. The active metric, endpoint forcing, body
interval \(-2.1\leq\ell\leq-0.5\), and prepared initial material state
are inherited from the elastic investigation. The first target is
\(0\leq s\leq0.5\), spanning its refined baseline depletion event at
\(s=0.37839\). The preceding early radiation witness at \(s=-0.5525\)
and the rail's release/reset remain outside this first comparison.

The field occupies this later non-live material patch, with electric flux
zero at both ends. Equal and opposite distributed charges supply a confined,
net-neutral capacitor-like store in the spherical reduction. The main
disclosure and its PDF remain unchanged; this report records the numerical
research model.

Use rationalized electromagnetic units with \(c=1\), and define
\(Q=R^2 E\), where \(E\) is the radial ADM electric field. Its independent
orthonormal tensor moments are

\[
(\rho_{\rm em},p_{\ell\rm em},j_{\rm em},p_{\Omega\rm em})
=\tfrac12 E^2(1,-1,0,1).
\]

Thus the field's angular pressure enters its full spherical conservation law.
The accompanying support tensor remains the longitudinal thermoelastic law
with \(K=0.1\), \(A=0.4\). Its end traction and shift-dependent energy
ports are counted. Physical anchors remain an additional source contribution.

Gauss and Ampere laws give ADM charge density and electrical current

\[
\rho_e=\frac{\partial_\ell Q}{BR^2},\qquad
j_e=\frac{\beta\partial_\ell Q-\partial_sQ}{\alpha R^2}.
\]

For material velocity \(v\), \(\Gamma=(1-v^2)^{-1/2}\), a passive Ohm law
\(\Gamma(j_e-v\rho_e)=\sigma E\) becomes

\[
\left[\partial_s+\left(-\beta+\frac{\alpha v}{B}\right)\partial_\ell\right]Q
=-\frac{\alpha\sigma}{\Gamma}Q.
\]

The field transfers ADM power \(E j_e\) and force \(E\rho_e\) to matter.
Their material-frame heating is \(\sigma E^2\geq0\). The Maxwell tensor's
divergence is the opposite of this Lorentz exchange. This sign and the
zero-heating ideal limit agree with the covariant resistive equations in
[Mignone et al.](https://academic.oup.com/mnras/article/486/3/4252/5479252).
The continuum material heat equation becomes

\[
(\partial_s+v_c\partial_\ell)q
=-\frac{\alpha R^2}{An}(P-vF)
+\frac{\alpha R^2\sigma E^2}{An\Gamma}.
\]

The conductivity uses the evolving local thermal state:
\(\sigma(q)=\sigma_0 H(1-q/0.25)\), where \(H\) is the clipped quintic
smooth rise. Conductivity vanishes above the target heat and increases as
heat falls. Field discharge supplies its heat from counted initial field
energy and subsequent geometric/material work. The algebraic Ohm law is an
effective specialization; carrier densities, drift limits, relaxation, and
microscopic implementation remain to be supplied.

Initial field density follows the local material heat density, with ratios
1 and 4 and a smooth 0.15-wide taper at each end. The two conductivities
are \(\sigma_0=0.03,0.1\). Controls remove the field, set conductivity to
zero with the same field preparation, or place the same initial cellwise
total energy and momentum entirely in material. The last control preserves
conserved material labels and changes the recovered thermal and mechanical
state according to the elastic constitutive law.

The numerical state evolves combined material-plus-field energy and momentum,
alongside material labels and the Maxwell flux. Finite-volume ledgers include
both tensors' geometric and boundary terms. An independent thermal ledger
integrates \(\alpha BR^2[-\Gamma(P-vF)+\sigma E^2]\); its discrepancy
measures thermal error beyond the total discrete conservation identity.
The initial comparison uses 128 cells and four workers. Refinement and
zero-exchange controls follow only where the first comparison identifies a
useful effect or a numerical ambiguity.

The endpoint history remains prescribed. Passing this comparison would
establish a field/material response across the earlier heat stop; endpoint
feedback, a physical current-carrier model, complete-cycle preparation,
transverse stability, anchor tensors, and the active Einstein-source sum
retain their separate requirements.

## Mechanical preparation refinement

The first field preparation follows the material's heat profile. Its charge
gradients consequently inherit that profile's spatial structure. At 512 cells
the ratio-4 initial field exerts peak radial Lorentz force 0.01714, compared
with 0.0005767 for the prescribed endpoint force. Their
\(\int\alpha BR^2|F|\,d\ell\) values are 9.3203 and 0.26547,
respectively. The new field therefore changes the mechanical preparation
substantially.

A single additional preparation tests this identified force burden. Constant
\(Q\) in the interior removes its volume charge and initial Lorentz force;
the original smooth end layers retain the opposite charges. Normalization
preserves the 20.7793 initial field energy at 512 cells. The peak field force
falls to 0.0006256 and its weighted absolute integral to 1.7905. This exchanges
distributed charge for two finite charge layers and makes their mechanical
support explicit. Three cases compare resistive discharge, ideal storage, and
the corresponding cellwise energy allocation to material. The target remains
\(s=0.5\); this fixed profile comparison closes the present shape investigation.

## Results: thermal allocation clears the first depletion interval

The zero-field elastic control reproduces its preceding stop at
\(s=0.37855\) on 128 cells. Allocating the ratio-4 field preparation's
energy to material instead completes \(s=0.5\) at every tested resolution:

| Material thermal allocation | Cells | Final service coordinate | Minimum heat at that final coordinate |
| --- | ---: | ---: | ---: |
| Original field-energy profile, baseline endpoint | 128 | 0.5 | 0.61094 |
| Same profile and endpoint | 256 | 0.5 | 0.59291 |
| Same profile and endpoint | 512 | 0.5 | 0.58697 |
| Same preparation rule, dense endpoint | 512 | 0.5 | 0.62418 |
| Capacitor-energy profile, baseline endpoint | 128 | 0.5 | 0.65695 |
| Capacitor-energy profile, baseline endpoint | 512 | 0.5 | 0.53247 |

At 512 cells the baseline initial ADM-slice energy increases from 101.3898
to 122.1691, approximately 20.5%. The material thermal inventory increases
from 5.5689 to 26.3532. This is a finite additional thermal preparation with
a counted energy cost. It demonstrates how the earlier local stop can move
beyond this comparison interval. The complete service cycle retains its
longer heat, force, and preparation requirements.

The most closely examined baseline thermal control has maximum sampled
material speed 0.9743 and longitudinal sound-speed squared 0.1739. Its discrete
energy and momentum residuals are approximately \(1.1\times10^{-15}\)
and \(4.3\times10^{-13}\), per solid angle. The separate thermal-inventory
balance has error 0.57894, about 2.2% of its initial thermal inventory; this
decreases from 0.74935 at 128 cells and 0.63139 at 256 cells.

The [material-label audit](data/electrothermal_endpoint/material4_control_baseline_n512_force1_end0.5_snap101_material_label_cloud.json)
integrates the smooth heat equation along 496 trajectories that remain inside
the cell-center interpolation range throughout the run. Their integrated heat
stays above 0.25542. The dense control gives the same lower sampled margin on
496 fully covered labels. This supports positive heat availability along the
resolved numerical histories. Local discrepancies remain larger than the
integrated error suggests: their maxima are 0.9333 and 2.2116, respectively,
and the audit omits a shock-heating contribution. These calculations therefore
support a bounded preparation result with finite accuracy. They leave a
quantitatively closed continuum thermal solution to further verification.

The capacitor-profile material control also retains a positive integrated
heat margin, 0.25010 on 498 fully covered labels. Its coldest final element
has evolved heat 0.53247 while its trajectory heat balance gives about 0.25188.
Its thermal accuracy is consequently weaker locally than the principal
baseline control's coldest-element comparison, whose discrepancy is 0.03601.

The two source fits have independent preparations and total energies. The
dense result is a sensitivity check; numerical convergence is assessed using
the fixed baseline fit. Every interval in this table ends before release
onset at \(s=0.745\).

## Results: electric-field cases reach a numerical thermal limit

The electric cases accelerate material strongly and reach a temperature floor
before the target interval ends. Their independent heat balances invalidate a
physical-depletion interpretation of those stops.

For example, the 128-cell ideal-field control with endpoint exchange switched
off starts the eventual cold element at \(q=0.48221\). Its smooth heat law
has zero right-hand side, yet the numerical solution drives that element to
zero heat at \(s=0.03702\). With conductivity enabled and exchange still
off, the cold element starts at 0.57389 and receives an integrated positive
Ohmic contribution of 0.66131, while the evolved heat again approaches zero.
These controls expose a numerical error in the recovered internal heat under
the field-driven motion. Global conservation of the combined tensor leaves
that internal-energy error undetected.

The charge-placement change reduces the initial mechanical burden, as measured
above, and moves the field response to a different trajectory. Its 512-cell
resistive run stops at \(s=0.21472\), compared with 0.11603 at 128 cells.
At the finest stop the tracked element starts with heat 0.56842, receives
Ohmic heat 1.55932, and gives up only 0.00407 through the endpoint term.
The evolved zero temperature disagrees with that budget by 2.12367. Its ideal,
zero-exchange control also loses heat that its continuum equation preserves.

The original profile has the same issue. Even its ratio-1 fast-discharge
stop, which moves comparatively little between 256 and 512 cells, retains a
cold-element heat discrepancy of 0.14090 against initial heat 0.26104 at
512 cells. Convergence of a stopping time alone would therefore give an
incorrect impression of a physical limit.

These field calculations establish the importance of initial electromagnetic
traction and expose the numerical method's thermal limitation. They leave
the electromagnetic reservoir's physical viability open. The bounded
comparison ends at this verification barrier. Further field evolution needs
an internal-energy or entropy treatment whose coupling to Maxwell transport
passes the ideal, zero-exchange material-heat control at the relevant loading.
Additional field shapes or source materials would presently confound that
numerical question with a new physical model.

## Consequence for component selection

The strongest positive result is the retained elastic body with a larger,
explicitly allocated thermal buffer over the first depletion interval.
Elasticity can continue to supply mechanical support while heat storage and
transport receive their own state variables and exchange laws. The original
elastic failure leaves this coordinated continuation available.

Electromagnetic storage remains a reasonable separate store/conversion
candidate. Its initial field preparation needs a mechanical balance, and
its heat evolution needs the verified numerical treatment identified above.
The present field runs supply no successful coupled response that would rank
it above a fluid reservoir, and their numerical temperature floors supply no
physical exclusion that would rank it below one.

A compressible fluid or independently moving entropy component remains useful
for transporting and distributing heat. The completed active calculations
provide no definite preference for replacing the mechanical body with such
a fluid. The most direct role assignment is elastic support, local thermal
buffer and transport, and optional electromagnetic storage/conversion, all
coupled to the existing endpoint heat/current medium. The current-carrier and
entropy degrees of freedom may share a multicomponent material description.

The forced endpoint history, its physical replacement error, counted support
anchors, transverse response, earlier packet-excluding preparation, release,
reset, and the complete active Einstein-source sum remain the construction's
next levels of closure. This comparison supplies a local reservoir selection
result within that architecture.

## Evidence and reproduction

There are 25 response runs, with about 10.3 MB of numerical evidence before
the final integrity manifest. The [evidence directory](data/electrothermal_endpoint/)
contains archived states, charge profiles, balance histories, material heat
audits, and software/input hashes. The capacitor preparation has its own
subdirectory and manifests. Narrative reporting is maintained manually.

The focused suite passes 50 tests. The electromagnetic additions check the
Maxwell tensor's divergence against Lorentz power and force on a varying
metric, passive Ohmic heating under boosts, recovery of the zero-field
elastic equations, equal-energy material allocation, charge-free capacitor
interiors, and convergence of a resolved smooth Joule-heating benchmark.
That benchmark reaches heat-balance error about \(5.1\times10^{-6}\) at
256 cells. The active-field thermal controls above expose the additional
limitation at the present material loading.

The following commands use `PYTHONPATH=toolkit/adm_harness_cli`, with
`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, and
`PYTHONDONTWRITEBYTECODE=1`:

```sh
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 4
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 4 --cells 256 --cases field1_fast field4_fast field4_ideal material4_control
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 4 --cells 512 --cases field1_fast field4_fast field4_ideal material4_control
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 2 --forcing 0 --cases field4_fast field4_ideal
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 1 --medium dense --cells 512 --cases material4_control
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 3 --cases capacitor4_fast capacitor4_ideal capacitor4_material --output supporting_reports/data/electrothermal_endpoint/capacitor
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 3 --cells 512 --cases capacitor4_fast capacitor4_ideal capacitor4_material --output supporting_reports/data/electrothermal_endpoint/capacitor
python toolkit/adm_harness_cli/scripts/run_electrothermal_endpoint.py --workers 1 --forcing 0 --cases capacitor4_ideal --output supporting_reports/data/electrothermal_endpoint/capacitor
python toolkit/adm_harness_cli/scripts/audit_electrothermal_endpoint.py material4_control_baseline_n512_force1_end0.5_snap101 capacitor/capacitor4_fast_baseline_n512_force1_end0.5_snap101
python toolkit/adm_harness_cli/scripts/audit_electrothermal_material_buffer.py material4_control_baseline_n512_force1_end0.5_snap101 material4_control_dense_n512_force1_end0.5_snap101
```
