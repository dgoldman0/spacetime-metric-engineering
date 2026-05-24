# Constraint Card 004: Handoff, Rematch, Release, and Carrier Collar

Status: component-level physical construction hypothesis.

## Controlling Sources

- Internal: release-choreography, compact handoff, beta-collar generator,
  dense finite-bundle carrier, finite-domain radial ANEC reports.
- External analogs:
  [`philbin_fiber_optical_event_horizon_0711.4796.pdf`](../sources/philbin_fiber_optical_event_horizon_0711.4796.pdf),
  [`estakhri_nonreciprocal_metasurface_space_time_phase_modulation_1905.10316.pdf`](../sources/estakhri_nonreciprocal_metasurface_space_time_phase_modulation_1905.10316.pdf),
  [`zang_nonreciprocal_wavefront_time_modulated_gradient_metasurfaces_2019.pdf`](../sources/zang_nonreciprocal_wavefront_time_modulated_gradient_metasurfaces_2019.pdf),
  [`wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf`](../sources/wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf),
  [`pop_a_active_acoustic_metamaterials_realtime_1505.00453.pdf`](../sources/pop_a_active_acoustic_metamaterials_realtime_1505.00453.pdf).

## Role

The handoff/collar system manages the transition between the live packet and
the support plant. It catches, rematches, briefly holds, releases, and restores
the packet while assigning derivative cost to edge/collar hardware.

## Physical Construction Hypothesis

The collar is an active impedance transformer. It sits between the protected
guide and the support-shell plant, then changes coupling, phase, delay, and
effective boundary condition through a smooth scheduled cycle.

The relevant engineered phenomena are already familiar in smaller systems:

- moving optical index fronts that catch and frequency-shift probe waves;
- time-modulated gradient metasurfaces that add controlled phase and frequency
  transitions;
- tunable resonator or photonic-crystal couplers with shaped coupling pulses;
- SQUID-tuned microwave boundaries that change effective length and release
  stored phase;
- active acoustic cells that modify local response through real-time
  electronics.

## Candidate Physical Stack

- Entry pre-match ring: broad impedance and pressure matching between station
  throat and live bore.
- Catch ring: stronger short-duration coupling into the support shell.
- Hold/rematch sleeve: phase and group-delay control around the packet edge.
- Trailing-edge trim band: asymmetric beta-rematch concentrated where the
  current reports place the live handoff correction.
- Release modulator: higher-smoothness fade of coupling and carrying-flow
  phase.
- Carrier collar monitor: probe traces that measure finite-bundle compression,
  recovery, and branch ordering.

## Mathematical Constraints Carried Over

- The packet center stays quiet; strongest correction sits near the
  trailing/inner packet edge.
- Compact handoff separates entry pressure containment from catch/edge
  derivative smoothing.
- Widened trailing-edge rematch preserves finite-bundle carrier behavior.
- Live handoff trim remains small and explicitly assigned.
- The finite-domain ANEC diagnostic identifies a secondary plus-branch
  live-handoff trim extreme after closure residual removal, which makes collar
  smoothing a source-completion target.

## Design Implications

This is the most machine-like subsystem: pulse shape, impedance, phase,
reflection coefficient, mode purity, and derivative smoothness are its design
variables. The collar should be characterized the way a high-performance
coupler is characterized: scattering matrix, time-domain release profile,
stored energy, leakage into protected modes, and recovery after reset.

## Open Questions

1. Which moving-front or time-modulated coupler best realizes packet-edge trim?
2. What release smoothness is required to suppress handoff derivative peaks?
3. Can collar widening be selected from measured bundle compression in real
   time?
4. How much collar-reservoir exchange must be routed to card `006` during
   high-service cases?
