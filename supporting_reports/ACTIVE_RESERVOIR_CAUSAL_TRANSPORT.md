# Causal heat delivery to the active endpoint reservoir

Date: 10 September 2026.

The [reservoir refinement](ACTIVE_RESERVOIR_ENSEMBLE_REFINEMENT.md) preserves
local heat and accounts for field and strain conversion, while its tested
allocations reach local depletion during release. The body's thermal
inventory grows over the same interval. The next question is whether a
conducting support can deliver some of that energy to the material
undergoing withdrawal before the recorded depletion event.

Heat/current routing remains an existing responsibility of the
[endpoint plant](../component_design/constraints/006_regulated_heat_current_medium_support_reservoir.md).
This investigation examines its missing connection to the reservoir's
moving material. The standing backbone, angular jacket, and other rail
components retain their assignments. The main disclosure and PDF retain
their existing design content.

## Registered causal-access screen

The input histories are the relaxing mixed reservoir at 32 and 64 cells,
and the relaxing thermal-only reservoir at 64 cells. Their final positive
states identify the first depleted material element. For each event,
trace signals backward through the full active metric, within the body
\(-2.1\leq\ell\leq-0.5\). The saved histories cover the interval
from \(s=0\) to their respective stopping times. Earlier preparation
remains a separate extension.

Let \(v\) be the local normal-frame material velocity and \(c_h\) a
signal-speed bound in that material's rest frame. The two characteristic
edges obey

\[
\frac{d\ell_\pm}{ds}=-\beta+\frac{\alpha}{B}
\frac{v\pm c_h}{1\pm v c_h}.
\]

The registered speeds are 0.1, 0.3, \(1/\sqrt3\), 0.9, 0.99, and
the null bound 1. These values characterize candidate signal cones. A
physical heat conductor still requires its own energy, momentum, entropy,
and constitutive response. In particular, a signal characteristic speed
alone specifies neither transported power nor available energy.

For a null ray, the material velocity cancels from its coordinate speed.
Its frequency measured by the normal observer evolves as

\[
\frac{d\log\omega}{ds}=\alpha K_\ell
 \mp\frac{\partial_\ell\alpha}{B}.
\]

Emitter and receiver energies include the additional factors
\(\Gamma(1\mp v)\). This supplies a counted null-packet frequency
comparison on the active background. Photon redshift is evaluated only
for the null controls. Emission, absorption, recoil, and the associated
material response remain physical transport duties.

The screen records the reachable material interval at selected service
coordinates and the latest emission time from eight material labels.
The large thermal reserve on the higher-label side receives particular
attention because the depleted element approaches negative normal-frame
velocity \(-0.9995\). A signal emitted behind that material must catch
its moving worldline.

The metric is evaluated directly from the archived active interpolants.
Saved positions and timelike material velocities use convex interpolation
between snapshots. Refinement compares the two material resolutions and
the integration step. A reachable edge that encounters a timelike body
end follows that end at earlier times; all counted routes remain within
the declared body. Five analytic controls verify relativistic velocity
addition, the null limit, flat moving-worldline emission deadlines, static
lapse redshift, and waiting at a confined timelike end.

## Constitutive basis for a possible continuation

Separately evolving material and entropy currents provide a suitable
starting point for finite heat propagation and reciprocal exchange.
[Comer, Andersson, Celora, and Hawke](https://arxiv.org/html/2606.17686v1)
derive such equations from dissipative relativistic actions. Their
small-drift reductions recover Cattaneo heat transport and permit an
explicit entropy-production analysis. The general nonlinear entropy
condition requires additional restrictions on the chosen constitutive
model. This distinction matters for the rapid motion and strongly
inhomogeneous temperature of the present reservoir.

The immediate calculation therefore establishes causal access before
selecting a heat-current law. A useful continuation must show positive
temperature, a causal characteristic cone, admissible added stress, and
the force and work needed to couple that current to the material. The
unresolved compressions near the existing fixed anchors retain their
separate mechanical verification requirement.
