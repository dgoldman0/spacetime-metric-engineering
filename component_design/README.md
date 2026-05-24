# Component Design Track

Status: first local component-design overview.

This folder is for thinking about the active rail as a possible physical
machine, not only as a unified metric/source model. The current controlling
article is still the sealed beta075 `V=5` operating embodiment described in
[`../README.md`](../README.md) and
[`../active_rail_technical_disclosure.tex`](../active_rail_technical_disclosure.tex).
The cards below are physical-design hypotheses constrained by the current
reports. They are not fabrication plans, final matter actions, coupled
Einstein-matter solutions, or broad service-family claims.

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
| Live packet corridor | Quiet passenger bore inside a larger active support plant | Protected corridor, not source plant | [`001_live_packet_corridor.md`](constraints/001_live_packet_corridor.md) |
| Standing support substrate / radial backbone | Prepared railbed/throat scaffold carrying most non-live radial support | Strong role evidence, physical realization open | [`002_standing_support_substrate.md`](constraints/002_standing_support_substrate.md) |
| Support-shell metric actuator layer | Annular actuator shell controlling carrying-flow, lapse, rail-stretch, and throat-capacity channels | Good routing evidence, physical actuator still abstract | [`003_support_shell_metric_actuator_layer.md`](constraints/003_support_shell_metric_actuator_layer.md) |
| Handoff, rematch, and carrier collar | Entry/catch/release phase-matching collar around the live packet | Mature prescribed-metric control layer | [`004_handoff_rematch_release_collar.md`](constraints/004_handoff_rematch_release_collar.md) |
| Endpoint receiver and reset plant | Station-end receiver, reset cap, support-edge closure, decompression plant | Effective-source freeze, matter mechanism open | [`005_endpoint_receiver_reset_plant.md`](constraints/005_endpoint_receiver_reset_plant.md) |
| Regulated heat/current medium and support reservoir | Physical source plant for endpoint/support exchange and heat/current regulation | Strongest current physical-source target | [`006_regulated_heat_current_medium_support_reservoir.md`](constraints/006_regulated_heat_current_medium_support_reservoir.md) |
| Carrier governance and diagnostics | Supervisory timing, carrier, reachability, and chronology safety system | Required safety/control layer | [`007_carrier_governance_and_diagnostics.md`](constraints/007_carrier_governance_and_diagnostics.md) |

## Working Guess

If this were a machine, it would not be one exotic material wrapped around a
passenger. It would be a nested rail service plant:

1. A quiet live bore is kept out of the hard source budget.
2. A prepared support substrate supplies the standing throat/radial/angular
   support.
3. A support-shell actuator layer carries the scheduled service load in
   controlled annular windows.
4. Entry, catch, rematch, collar, and release hardware phase-match the live
   packet to the support plant.
5. Endpoint receiver/reset hardware catches the support-edge source burden and
   prevents it from leaking into live service.
6. A regulated anisotropic heat/current medium plus support reservoir is the
   current best guess for the physical source plant that pays the sharp
   endpoint/support exchange bill.
7. A chronology and carrier-governance layer decides when the rail may arm,
   release, reset, and connect to other rails.

The near-term goal is not to declare a buildable device. It is to make the
physical burden explicit enough that each subsystem can be tested against the
same evidence chain: source channels, location, timing, margin, failure mode,
and what would have to be true physically.
