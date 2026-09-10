# Component Design Track

Status: local component-design overview with physical construction hypotheses.

This folder treats the active rail as a nested physical service plant. The
current controlling article is the sealed beta075 `V=5` operating embodiment
described in [`../README.md`](../README.md) and
[`../active_rail_technical_disclosure.tex`](../active_rail_technical_disclosure.tex).
The cards translate the current mathematical component split into construction
hypotheses, hardware analogs, source burdens, and measurement targets.

The local source library is
[`sources/SOURCES.md`](sources/SOURCES.md). It includes the older effective
geometry literature together with engineering-facing sources on programmable
metamaterials, space-time modulation, active acoustic cells, elastic and
piezoelectric metamaterials, thermal metamaterials, superconducting current
limiters, high-voltage pulse modulators, magnetic field routing, and
distributed fiber diagnostics.

## Current source construction

The [source-construction selection constraints](../supporting_reports/SOURCE_CONSTRUCTION_SELECTION.md)
set the current search preference: constructions without string matter or
ideal string-cloud sources receive priority. A string-based candidate requires
a substantial, quantified improvement in complete assembly viability.
The prestressed backbone/heat-buffer assembly is set aside following its
measured source-completion burden.

The [distributed electrothermal comparison](../supporting_reports/GRADED_ELECTROTHERMAL_ASSEMBLY.md)
identifies a conditional continuation with graded radial capacitors, local
stores, and confined-fluid pressure couplings connected to the endpoint
heat/current and reset plant. It quantifies the separate momentum and thermal
ports. The [connected-pressure completion](../supporting_reports/PRESSURE_LINKED_STORAGE_COMPLETION.md)
closes the interior force equations with a thermal-fluid EOS and finite
bidirectional field conversion. Its small stress estimate requires an explicit
electrical-work and heat-return interface, supplied terminal reactions, and
physical carrier and converter tensors. Coupled evolution and the remaining
negative-stress source continue to determine physical selection.

The [finite regenerative-converter evaluation](../supporting_reports/REGENERATIVE_CONVERTER_EVALUATION.md)
measures a local prepared-work requirement of about 43 units even with ideal
recovery. A benchmark capacitor bank's material mass produces a decisive
source burden. A formal field/enclosure control retains a much smaller burden
and requires a physical supporting material, thermal law, and work route.
The switching role and its finite work reserve therefore remain separate
construction requirements.

The [finite electromagnetic delivery study](../supporting_reports/POYNTING_WORK_DELIVERY.md)
selects a receiver-side paired work/return guide with part of its magnetic
field allocated from the existing radial electric-support budget. Finite
absorption and conserved-current checks retain an improved late-patch energy
and stress comparison. The physical continuation supplies the converter's
force and loss law, finite guide turns and electric isolation, and the thermal
receiver's material stress while preserving earlier arming and full reset.

The [finite work-interface investigation](../supporting_reports/FINITE_WORK_INTERFACE.md)
retains useful conversion-efficiency and recovery choices and quantifies the
remaining capacitor's electrical and mechanical duties. Limiting recovery
can reduce added guide energy while increasing the electric storage requiring
confinement. The next construction couples charged boundaries to the existing
pressure/support material, with their full stress and work exchange included.

The [component cross-reference and joint-coordination review](../supporting_reports/RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md)
connects this architecture to the September boundary, current, quantum, and
material tests. It retains the separate bulk, angular, handoff, current, and
reservoir roles while requiring a counted tensor and reciprocal exchange law
for each physical component. The source-role ledger is an assignment of
responsibilities; the coupled material construction supplies those stresses.

The selected condensate remains a regular transition-material candidate.
Its measured bulk support share and the tested neutral scalar's opening deficit
require distinct attention. The [source-role audit](../supporting_reports/COUPLED_SOURCE_ROLE_AUDIT.md)
records those quantities. Cards 002 and 006 carry the resulting backbone and
transport/reservoir requirements.

## Chronology

Use the newer reports as controlling evidence:

- May 16 ADM writeup: older scaffold/prototype framing.
- May 17 support-shell reports: early reduced routing and V5 control freeze.
- May 18-20 Stage I/II decomposition: component roles and source-sector
  separation.
- May 22-23 beta075 reports: archived endpoint/support source-family,
  closure, transport, energy, 3+1, ANEC, and boundedness evidence.
- September 8-9 tests: corrected tensor classification, explicit limits of
  support-exchange fitting, metric regularity and active boundary behavior,
  independent current evolution, and counted material/quantum source trials.
  These reports control physical source acceptance and the joint construction.

The present design scope is `V=5`. `V=2.5` is a useful source-safe
service-law calibration diagnostic, while `V=10` is a high-service boundary
diagnostic that currently fails live packet source safety.

## Assembly Map

| Subsystem | Physical-building intuition | Current maturity | Constraint card |
| --- | --- | --- | --- |
| Live packet corridor | Protected passenger/payload bore inside a field-routed active plant | Construction picture: shielded guide, magnetic/EM routing, boundary trims | [`001_live_packet_corridor.md`](constraints/001_live_packet_corridor.md) |
| Standing support substrate / radial backbone | Preloaded architected railbed carrying radial and angular support | Construction picture: mechanical/elastic metamaterial backbone with active shunts | [`002_standing_support_substrate.md`](constraints/002_standing_support_substrate.md) |
| Support-shell metric actuator layer | Annular programmable actuator shell for carrying-flow, lapse, rail-stretch, and throat capacity | Construction picture: space-time-modulated cells and tunable impedance/index/stress layers | [`003_support_shell_metric_actuator_layer.md`](constraints/003_support_shell_metric_actuator_layer.md) |
| Handoff, rematch, and carrier collar | Entry/catch/hold/release impedance transformer around the packet edge | Construction picture: time-modulated couplers, resonators, and moving-front collars | [`004_handoff_rematch_release_collar.md`](constraints/004_handoff_rematch_release_collar.md) |
| Endpoint receiver and reset plant | Station-end buffer, pulse receiver, current limiter, thermal router, and decompression plant | Construction picture: pulse-power hardware, superconducting/current-limit analogs, thermal metamaterial manifold | [`005_endpoint_receiver_reset_plant.md`](constraints/005_endpoint_receiver_reset_plant.md) |
| Regulated heat/current medium and support reservoir | Endpoint/support source plant with bounded heat/current and explicit exchange | Construction picture: anisotropic thermal/current medium with reservoir, regulator, and limiter channels | [`006_regulated_heat_current_medium_support_reservoir.md`](constraints/006_regulated_heat_current_medium_support_reservoir.md) |
| Carrier governance and diagnostics | Supervisory timing, carrier, reachability, and chronology safety system | Construction picture: embedded distributed sensing, probe injection, actuator telemetry, and rail-time controller | [`007_carrier_governance_and_diagnostics.md`](constraints/007_carrier_governance_and_diagnostics.md) |

## Working Guess

The active rail reads as a layered infrastructure machine:

1. A protected live bore carries the packet through a low-coupling guide.
2. A prepared support substrate supplies standing throat, radial, and angular
   capacity.
3. A support-shell actuator layer applies scheduled annular modulation in
   separate flow, lapse, stretch, and capacity channels.
4. Entry, catch, rematch, collar, and release hardware phase-match the packet
   to the active plant.
5. Endpoint receiver/reset hardware catches support-edge source burden, stores
   release history, routes heat/current, and decompresses after service.
6. A regulated anisotropic heat/current medium plus support reservoir supplies
   the lead physical source plant for endpoint/support exchange.
7. A chronology and carrier-governance layer arms, measures, releases, resets,
   and routes networked service.

The design task is to make the physical burden explicit enough for each
subsystem to be tested against the same evidence chain: source channel,
location, timing, margin, failure mode, construction analog, and required
measurement.
