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
