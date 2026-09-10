# Active-rail architecture and source-study scope review

Date: 9 September 2026.

The active rail is a scheduled transport service supported by prepared,
spatially distributed infrastructure. Its operating object is the protected
packet together with the carrying flow, handoff, support response, and reset.
The later complete static quantum background is an additional source-study
model. Its identification with a required rail operating state remains
unestablished. Consequently its source exclusions apply to the registered
static constructions; transferring them to the active rail requires a matching
or approximation argument.

This review checks the disclosure at pre-September commit `d44e923`, the May
component and carrier reports, the metric implementation, and the September
source-study provenance through `734156c`. It preserves the existing numerical
artifacts and records a correction to their use in selecting rail sources.
The technical disclosure and its PDF are unchanged by this review.

## Operating architecture

The [service sequence](../active_rail_technical_disclosure.tex) proceeds from
prepared substrate and ready support plant through packet entry, locked
catch/rematch, support-contained carry, packet release, and infrastructure
reset. The release law includes a finite matched hold, a smooth carrying-flow
fade, continued lapse/carve support through handoff, and subsequent support
relaxation. The held interval is part of the active protocol.

The [component ledger](STAGE2_COMPONENT_SOURCE_LEDGER_PROMOTED_PAIR.md) assigns
overlapping, coupled responsibilities. The later source-target grammar is
\(S_0+J+R+C_{\rm live}+G+D_H\), supplemented by support-reservoir exchange.
Here \(R\) denotes the core residual target.

| Subsystem | Responsibility in the rail |
| --- | --- |
| Protected packet corridor | Carry the payload with a timelike packet trajectory and controlled local coupling. Packet-edge trims handle designated live handoff loads. |
| Standing substrate and radial backbone | Carry prepared radial support and stored load through distributed non-live infrastructure, with explicit finite-end forces. |
| Angular jacket | Carry transverse/angular capacity and its response to deformation alongside the radial backbone. |
| Support-shell actuators | Coordinate carrying flow, lapse, radial stretch, and angular capacity through timed, packet-excluding support windows. |
| Entry, catch, and release collars | Match packet/support motion, smooth derivative-sensitive handoff, preserve packet margin, and control finite-bundle compression. |
| Endpoint receiver, current medium, and reservoir | Receive release history, carry current and angular response, exchange power and radial force, store energy, and restore readiness. |
| Sensing and governance | Admit service according to packet, carrier, source, endpoint-readiness, timing, and network chronology conditions. |

The [component cards](../component_design/README.md) supply engineering analogs
for these responses. Their optical, elastic, electrical, and thermal examples
provide construction vocabulary and observable behavior. A gravitational
realization additionally requires the corresponding physical stress tensors
and interaction laws. Four metric controls also do not imply four independent
materials: each field's derivatives affect several demanded stress channels.

## Carrier and causal requirements

The May [reachability report](STAGE2_HORIZON_REACHABILITY_AND_CAUSAL_GUARD_REPORT.md)
expressly identifies the rail as a service carrier using a controlled one-way
region to move support burden while protecting the live packet. It treats
accidental entrance access into the carried packet, and an accidental
through-corridor, as causal questions to investigate. Local coordinate-null
branch crossings receive separate reachability and escape tests.

In the reported sweeps, entry-to-live-packet hits vanish during catch/rematch,
held carry, and release. Some support-edge seeds reconnect in the post-release
buffer. The [beta-collar generator study](STAGE2_BETA_COLLAR_GENERATOR_SCREEN.md)
then evaluates the modified metric and its demanded source together; its
selected finite-bundle audit records escape and recovery for all 136 tested
rays, with zero caustic-like flags in eight bundles. These are scoped
prescribed-metric results, with global causal completion remaining a separate
obligation.

The [service-time ledger](STAGE2_SERVICE_TIME_ADVANTAGE_LEDGER.md) compares
scheduled transport proxies with exterior-null timing. Its direct
service-factor and packet-coordinate proxies are favorable, while its strict
source-grid centerline control is neutral. Thus the timing evidence retains
its stated endpoint and proxy conventions. The network governor separately
requires monotone shared rail-time advance across service, return, reset, and
cross-link edges.

## The source target includes active geometry

The implemented metric is

\[
ds^2=-\alpha(\ell,\sigma)^2d\sigma^2
+\gamma_{\ell\ell}(\ell,\sigma)
(d\ell+\beta(\ell,\sigma)d\sigma)^2
+\gamma_\Omega(\ell,\sigma)d\Omega^2.
\]

The [source kernel](../toolkit/adm_harness_cli/adm_harness/source_ledger.py)
evaluates all four fields throughout its spacetime differentiation stencil.
It computes \(T^{\rm dem}_{\mu\nu}=G_{\mu\nu}[g]/8\pi\), with the shift in
both the metric and the ADM frame. For the disclosure's extrinsic-curvature
convention,

\[
K_{ij}=\frac{D_i\beta_j+D_j\beta_i-\partial_\sigma\gamma_{ij}}
{2\alpha}.
\]

Keeping the spatial profile while removing its evolution and shift changes
these data and the required stress. A static minimum-radius identity therefore
needs its static hypotheses attached when used as a source constraint.

Several distinct objects acquired similar names during the investigation:

| Object | Meaning and scope |
| --- | --- |
| Frozen reference design | Fixed parameters and archived artifacts for a metric that still depends on service time. The early full 4D Le diagnostic evaluates this active metric. |
| `matched_hold` release setting | An active choreography setting controlling when carrying flow fades. It preserves the other scheduled fields and their derivatives. |
| Time-matched carrying-flow-off subtraction | An accounting control with zero shift and the scheduled spatial metric. `build_betaoff_fields` retains both spatial-metric time derivatives in its extrinsic curvature. |
| `holding=True` curvature control | A freshly computed static comparison: freeze lapse and spatial metric throughout the temporal stencil and set shift to zero. |
| Complete static quantum background | Extend the phase-0.745 static control across both branches and choose a static quantum ground state with specified outer conditions. |

The flow-off implementation is in
[`generate_service_factor_inputs.py`](../toolkit/adm_harness_cli/scripts/generate_service_factor_inputs.py);
the fully static control is in
[`geometry_boundary.py`](../toolkit/adm_harness_cli/adm_harness/geometry_boundary.py).
The two procedures have different source tensors. Substrate subtraction also
preserves a separate ledger for the standing support: a small live increment
leaves the baseline physical source requirement to be supplied.

There is a related geometric qualification. The original disclosure uses
intrinsic throat/support terminology, and the angular metric contains
\(\ell^2+R_{\rm th}^2\). The
[pre-flight exterior check](LE_BOUNDARY_GATE_PREFLIGHT.md) confirms a decaying,
nonzero source in the late outer geometry. That support demand remains part
of the specified metric. Establishing its physical exterior and endpoint
matching is distinct from assuming an always-open two-mouth transport route
or a stationary quantum circuit. The operational correction does not remove
the implemented spatial curvature or settle its global completion.

## Where the static source assumption entered

The early [geometry-demand diagnostic](LE_GEOMETRY_BOUNDARY_DIAGNOSTIC.md)
compares the active 4D tensor with explicit static controls. The active Type IV
witnesses and receiver regularity findings come from the former. They were
not obtained by replacing the active metric with the static control.

Commit `af814cd` introduced a coupled reset trial using matched-static
background stresses and a stationary material ansatz on a negative-side
annulus. Commit `9387443` introduced the bounded inverse reset construction
with static endpoint profiles. Its
[report](LE_RESET_INVERSE_SEARCH.md) explicitly states that the rail is active
at the initial reference phase and that static endpoint data are an additional
modeling choice. The angular startup obstruction belongs to those selected
paths, source laws, and boundary conditions.

Commit `1069413` introduced the
[complete two-ended static quantum background](CURVED_QUANTUM_BOUNDARY_SEARCH.md)
at phase 0.745 with zero shift. It is the specific provenance of that complete
quantum background, rather than the beginning of all static assumptions.
Later curved-boundary, material, condensate, and source-allocation trials
inherited this background or constructed explicit static variants of it.

The later [archived-geometry screen](../toolkit/adm_harness_cli/scripts/screen_archived_geometry_opening.py)
likewise evaluates a `StaticSlice`. Its cache saves beta, but the static source
calculation uses radius, lapse, and radial scale. A separate active packet-norm
check screens service damage from the proposed profile changes; it does not
establish that the static source target is a necessary service state. The
finite-cavity and magnetic-circuit scripts consume the same static metric
cache for their source calculations.

The scope error was promoting these conditional source results into necessary
active-rail selection gates without demonstrating the state equivalence. Local
scope qualifications were already present in several reports. The later
recommendations exceeded them.

## Findings retained with their actual scope

| Evidence | Scope after this review |
| --- | --- |
| Original packet, handoff, causal, and timing audits | Retain their recorded prescribed active metric, operating rating, sampling, and endpoint conventions. |
| Classifier repair and tensor-accounting pre-flight | Retain the corrected causal eigensystem logic, reconstruction checks, missing independent support tensor, and endpoint replacement residual. |
| Active regularity and uniform-rate studies | Retain the identified joins, their repairs, and persistent Type IV demand on the tested active families. Their consequences depend on the selected material admissibility class. |
| Reset startup and Comer constructions | Retain the chosen annular initial/boundary data, constitutive assumptions, and local evolution evidence. Matching to the active rail remains an additional condition. |
| Curved quantum boundaries, walls, atmosphere, and condensate | Retain tensor, force, regularity, response, and scale findings on each registered static background and quantum-state prescription. |
| Static allocation, opening, cavity, and magnetic screens | Retain comparisons within those models. Their numerical deficits and return-stress exclusions presently lack an established necessary-state link to rail service. |

This distinction leaves substantive source work outstanding. The
[pre-flight](LE_BOUNDARY_GATE_PREFLIGHT.md) established that component assignment
rows repeat demanded tensors and cannot be added as independent physical
sources. The endpoint medium reconstructs its fitted tensor, which differs
from the original geometric endpoint target. The support exchange fit supplies
a divergence target; it leaves the reservoir's independent tensor unspecified.
Those findings survive the correction to the static background's status.

The [component cross-reference](RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md)
recovered role separation but continued to use static opening identities for
source selection. The repository overview, substrate card, and current
disclosure's static-source discussion also inherit parts of that reasoning.
Their conditional calculations remain available; this review withdraws the
unsupported inference that they establish required static rail states or
exclude the corresponding source families from all active constructions.

## Basis for subsequent construction work

A further rail source calculation needs a declared operating interval,
component role, physical initial state, and matching worldtubes. Its reference
must carry the full scheduled metric and its derivatives, or an explicitly
justified approximation to that state. Quantum calculations additionally need
an initial-state and boundary-history prescription appropriate to that service.

The source sum must include independently evaluated component tensors,
interaction stresses, reservoir storage, reciprocal forces, and remaining
replacement residuals. The field equations and exchanges then determine which
responses can coexist while preserving the packet and service constraints.
Static controls remain useful for separating mechanisms once their role and
relation to a physical preparation state are specified.

This review establishes the architecture and corrects the scope of the search.
It supplies no new material verdict or coupled Einstein–matter solution.
