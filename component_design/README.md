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

## Chronology

Use the newer reports as controlling evidence:

- May 16 ADM writeup: older scaffold/prototype framing.
- May 17 support-shell reports: early reduced routing and V5 control freeze.
- May 18-20 Stage I/II decomposition: component roles and source-sector
  separation.
- May 22-23 beta075 reports: current endpoint/support source-family,
  closure, transport, energy, 3+1, ANEC, and boundedness evidence.

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
