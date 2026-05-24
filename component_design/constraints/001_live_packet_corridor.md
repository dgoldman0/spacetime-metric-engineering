# Constraint Card 001: Live Packet Corridor

Status: component-level physical-design hypothesis.

## Controlling Sources

- Internal: current disclosure and service-rating ladder. `V=5` is the
  operating point; `V=10` is a live-packet safety failure.
- External analogs:
  [`barcelo_liberati_visser_analogue_gravity_gr-qc0505065.pdf`](../sources/barcelo_liberati_visser_analogue_gravity_gr-qc0505065.pdf),
  [`leonhardt_philbin_transformation_optics_0805.4778.pdf`](../sources/leonhardt_philbin_transformation_optics_0805.4778.pdf),
  [`greenleaf_electromagnetic_wormholes_metamaterials_140836.pdf`](../sources/greenleaf_electromagnetic_wormholes_metamaterials_140836.pdf),
  [`pfenning_ford_quantum_inequality_curved_spacetimes_gr-qc9805037.pdf`](../sources/pfenning_ford_quantum_inequality_curved_spacetimes_gr-qc9805037.pdf).

## Role

The live packet corridor is the passenger-facing region. It is the part of the
rail that must remain quiet while the support plant does hard work around it.
The reports consistently treat this region as protected, not as the place where
the main source burden should be paid.

## Actual Physical Construction Hypothesis

The best near-term physical picture is not "put exotic matter in the passenger
tube." It is a shielded inner guide inside a much more active annular plant.
The closest real engineering analog is a protected test channel inside a
transformation-optics or analogue-gravity apparatus: the medium around the bore
is structured to route waves/fields as if a geometry were present, while the
interior remains a quiet observation or payload channel.

For a lab-scale analog, build the live corridor as one of:

- a central microwave/optical waveguide bore inside a programmable metamaterial
  shell;
- a microstructured-fiber or integrated-photonic channel whose core is kept
  below the nonlinear/horizon-forming intensity while the surrounding pulse or
  index front does the active work;
- a cryogenic microwave cavity/transmission-line section with SQUID or
  tunable-boundary elements outside the protected mode volume.

For a speculative rail-scale design, the live corridor would be a mechanically
and electromagnetically isolated bore with:

- a passive inner liner chosen for low coupling to the support shell;
- packet-edge trim coils/metasurfaces only near entry/catch/release regions;
- distributed packet-norm/field-margin sensors;
- hard interlocks that prevent arming if support-edge or cone margins are
  outside the allowed window;
- no radial backbone, endpoint receiver, or support reservoir inside the
  passenger-facing volume.

This card therefore treats the live corridor as an exclusion zone with boundary
actuation, not as a primary source medium.

## Hardware Sketch

- Inner bore: low-loss, low-dispersion guide or cavity volume.
- Isolation liner: metamaterial/acoustic/EM shield tuned to suppress coupling
  from support-shell actuator modes into the packet center.
- Packet-edge trims: short collar segments, not full-bore active media.
- Sensor ring: field probes, timing probes, packet-edge residual probes.
- Abort path: dump actuator timing, hold support shell, then reset endpoint
  plant before packet enters unsafe region.

## Mathematical Constraints Carried Over

- Live packet norm remains safely negative at sealed `V=5`.
- Packet `Delta rho` remains quiet after standing-substrate subtraction.
- Live handoff trim may exist, but hard infrastructure roles must not
  contaminate the live packet.
- `V=10` currently fails live packet source safety, so high-service operation
  requires additional causal-margin engineering.
- Finite-domain radial ANEC is not clean for the demanded total, but the main
  negativity is not assigned to a passenger-filling live source layer.

## Design Implications

The corridor's construction job is mostly negative: keep things out. That means
the physical success metric is not how strong the corridor is, but how small
its coupling is to the support shell, endpoint exchange, and reset plant. This
also makes `V=10` a corridor-design failure mode: the high-service repair is
likely additional collar/cushion margin or service-aware actuator timing, not a
new bulk source in the live bore.

## Open Questions

1. What physical isolation mechanism best maps to packet-norm margin?
2. Can live handoff trim be realized as a boundary/collar effect rather than a
   bulk passenger-region source?
3. What sensor set would detect packet-norm margin loss quickly enough to abort
   or retime service?
4. Can transformation-optics style shielding provide a useful lab analog for
   support-shell exclusion, even though it is not gravitational engineering?
