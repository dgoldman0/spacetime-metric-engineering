# Constraint Card 004: Handoff, Rematch, Release, and Carrier Collar

Status: component-level physical-design hypothesis.

## Controlling Sources

- Internal: release-choreography, compact handoff, beta-collar generator,
  dense finite-bundle carrier, finite-domain radial ANEC reports.
- External analogs:
  [`philbin_fiber_optical_event_horizon_0711.4796.pdf`](../sources/philbin_fiber_optical_event_horizon_0711.4796.pdf),
  [`leonhardt_philbin_transformation_optics_0805.4778.pdf`](../sources/leonhardt_philbin_transformation_optics_0805.4778.pdf),
  [`barcelo_liberati_visser_analogue_gravity_gr-qc0505065.pdf`](../sources/barcelo_liberati_visser_analogue_gravity_gr-qc0505065.pdf),
  [`wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf`](../sources/wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf).

## Role

The handoff/collar system manages the transition between the live packet and
the support plant. It catches, rematches, briefly holds, releases, and restores
the packet while keeping derivative cost out of the packet center.

## Actual Physical Construction Hypothesis

The collar is an impedance-matching and phase-matching device. A realistic
analog would look like a tunable coupler section between a quiet guide and an
active medium, not like a passive doorway. Existing analogs point to two
families:

- optical horizon hardware, where a moving index front interacts with probe
  waves and produces horizon-like frequency shifts;
- superconducting-circuit boundary modulation, where effective length and
  boundary conditions are changed rapidly without moving macroscopic hardware.

For a bench analog, the collar could be implemented as:

- a nonlinear optical fiber or integrated photonic waveguide with a shaped pump
  pulse acting as the catch/rematch front;
- a ring-resonator or photonic-crystal segment with time-dependent coupling;
- a superconducting microwave line with a SQUID-tunable boundary/coupler,
  using matched pulses to emulate catch, hold, and release phases.

For a speculative rail-scale design, the collar would be a station-throat
assembly:

- an entry pressure-containment ring;
- a catch/rematch ring that couples the live packet to the support shell;
- a trailing-edge beta-rematch sleeve concentrated near the packet edge;
- a widened carrier collar to prevent branch-band bundle collapse;
- a controlled release sequence that fades the active field through a
  minimum-jerk or higher-smoothness profile.

## Hardware Sketch

- Entry ring: broad, smooth containment and pressure matching.
- Catch ring: stronger but brief annular coupling to support-shell actuator.
- Edge sleeve: asymmetric/trailing-edge trim field.
- Release modulator: time-programmed fade, not abrupt shutdown.
- Bundle monitor: measures compression/recovery of neighboring carrier rays or
  their lab-analog wave packets.

## Mathematical Constraints Carried Over

- The packet center should stay quiet; strongest correction sits near the
  trailing/inner packet edge.
- Compact handoff separates entry pressure containment from catch/edge
  derivative smoothing.
- Widened trailing-edge rematch preserves finite-bundle carrier behavior.
- Live handoff trim exists, but should remain small and explicitly assigned.
- The finite-domain ANEC diagnostic shows a secondary plus-branch live-handoff
  trim extreme after closure residual removal; this subsystem must not hide
  that cost.

## Design Implications

This component is the most "machine-like" part of the rail. It should be
engineered around pulse shape, timing, impedance, and mode matching. The
physical risk is derivative violence: abrupt transitions create exactly the
sort of point peaks and live handoff residue the math has been trying to move
out of the packet.

## Open Questions

1. Can packet-edge trim be implemented as a collar boundary condition rather
   than a live bulk source?
2. What physical timing mechanism provides matched hold and smooth beta fade?
3. Can collar widening be service-aware, especially for high-service cases?
4. Can handoff trim be averaged or source-completed to reduce finite-domain
   ANEC residue?
