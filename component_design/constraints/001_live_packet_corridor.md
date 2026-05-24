# Constraint Card 001: Live Packet Corridor

Status: component-level physical construction hypothesis.

## Controlling Sources

- Internal: current disclosure and service-rating ladder. `V=5` is the
  operating point; `V=10` marks the live-packet safety boundary that drives
  corridor-margin design.
- External analogs:
  [`greenleaf_electromagnetic_wormholes_metamaterials_140836.pdf`](../sources/greenleaf_electromagnetic_wormholes_metamaterials_140836.pdf),
  [`prat_camps_long_distance_transfer_static_magnetic_fields_1304.6300.pdf`](../sources/prat_camps_long_distance_transfer_static_magnetic_fields_1304.6300.pdf),
  [`prat_camps_magnetic_wormhole_srep12488.pdf`](../sources/prat_camps_magnetic_wormhole_srep12488.pdf),
  [`leonhardt_philbin_transformation_optics_0805.4778.pdf`](../sources/leonhardt_philbin_transformation_optics_0805.4778.pdf),
  [`philbin_fiber_optical_event_horizon_0711.4796.pdf`](../sources/philbin_fiber_optical_event_horizon_0711.4796.pdf).

## Role

The live packet corridor is the passenger-facing guide volume. Its job is to
carry the packet through a low-coupling bore while the surrounding plant routes
field, stress, current, and heat burden through infrastructure layers.

## Physical Construction Hypothesis

The corridor is a protected inner guide inside a field-routed annular service
plant. The strongest physical image is a quiet vacuum/optical/microwave bore
surrounded by metamaterial, magnetic, and structural layers that steer the hard
response around the protected volume.

Existing engineering analogs give concrete pieces for this picture:

- Transformation-optics and electromagnetic-wormhole devices show how material
  parameters can create an effective tunnel for electromagnetic fields.
- Magnetic hoses and magnetic-wormhole experiments show superconductor/
  ferromagnet routing of quasi-static magnetic flux between separated ports.
- Fiber-optical horizon experiments show a protected probe mode interacting
  with a moving index front generated outside the probe itself.

At bench scale, this suggests a central waveguide or cavity whose payload mode
is monitored while surrounding collars create index, impedance, or magnetic
field routing. At infrastructure scale, the live corridor becomes a shielded
rail bore with local trim rings near entry, catch, rematch, and release zones.

## Candidate Physical Stack

- Inner guide: vacuum tube, optical core, microwave cavity, or equivalent
  low-loss payload channel.
- Isolation liner: layered EM/acoustic/mechanical shield tuned to reduce
  coupling from support-shell modes into the packet center.
- Field-routing jacket: superconductor/ferromagnet or metamaterial routing
  channels for support fields and trim fields.
- Packet-edge trim rings: short active collars that act on the packet edge
  during entry, catch, rematch, and release.
- Embedded sensor fibers and probes: packet-norm analog, local field leakage,
  timing jitter, wall strain, thermal flux, and collar phase.
- Abort path: de-arm actuator timing, hold support-shell state, and route the
  packet into endpoint/reset protection if measured margin falls below watch
  constants.

## Mathematical Constraints Carried Over

- Live packet norm remains safely negative at sealed `V=5`.
- Packet `Delta rho` remains quiet after standing-substrate subtraction.
- Live handoff trim is allowed as a small boundary/collar assignment.
- `V=10` consumes live packet source margin and sets the high-service corridor
  design target.
- Finite-domain radial ANEC remains a source-completion target, while the live
  corridor assignment stays focused on isolation and boundary coupling.

## Design Implications

The corridor success metric is isolation ratio: how much support-shell,
endpoint, thermal/current, and collar activity reaches the packet center. The
construction variables are shielding depth, trim-ring bandwidth, bore
dispersion, packet-edge leakage, and measured timing noise. The `V=10` failure
mode points toward stronger collar smoothing, larger endpoint buffer, and
service-aware actuator retiming before any increase in packet-center burden.

## Open Questions

1. What physical isolation observable best maps to packet-norm margin?
2. Can magnetic-hose or transformation-optics routing provide a useful bench
   analog for support-field exclusion around the live bore?
3. What trim-ring bandwidth is needed to keep handoff corrections at the packet
   edge?
4. Which sensor package detects packet-center coupling quickly enough to abort
   or retime service?
