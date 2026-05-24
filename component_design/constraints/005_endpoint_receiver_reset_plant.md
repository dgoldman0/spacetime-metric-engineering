# Constraint Card 005: Endpoint Receiver and Reset Plant

Status: component-level physical construction hypothesis.

## Controlling Sources

- Internal: endpoint-J source freeze, endpoint current-regulator screen,
  covariant endpoint-medium audit, support total-closure reports.
- External analogs:
  [`wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf`](../sources/wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf),
  [`cook_solid_state_high_voltage_pulse_modulators_e00_tup6a07.pdf`](../sources/cook_solid_state_high_voltage_pulse_modulators_e00_tup6a07.pdf),
  [`duran_thermal_instability_superconducting_fault_current_limiters_cond-mat0312190.pdf`](../sources/duran_thermal_instability_superconducting_fault_current_limiters_cond-mat0312190.pdf),
  [`noe_high_temp_superconducting_fault_current_microlimiters_0901.2299.pdf`](../sources/noe_high_temp_superconducting_fault_current_microlimiters_0901.2299.pdf),
  [`sha_printable_freeform_thermal_metamaterials_s41467-021-27543-7.pdf`](../sources/sha_printable_freeform_thermal_metamaterials_s41467-021-27543-7.pdf),
  [`schittny_transient_heat_flux_shielding_1305.3197.pdf`](../sources/schittny_transient_heat_flux_shielding_1305.3197.pdf).

## Role

The endpoint receiver/reset plant absorbs and organizes the source burden that
appears at support-edge and reset/decompression phases. It includes the
beta-memory receiver, bounded reset-cap body, finite support-edge closure
component, and reset-domain wake-tail handling.

## Physical Construction Hypothesis

The endpoint plant is station machinery: buffer, pulse receiver, current
limiter, thermal router, reset store, and decompression stage. It takes the
service waveform arriving from the support shell and collar, stores the
history-dependent part in finite variables, and releases the remaining energy,
current, heat, and stress through controlled reset paths.

The closest engineering anchors are:

- solid-state high-voltage pulse modulators and pulse-forming networks for
  scheduled high-power waveform delivery;
- superconducting circuit boundaries for fast effective-length and phase
  storage analogs;
- superconducting fault-current limiters for current-regulator and quench/
  protection behavior;
- thermal metamaterials and transient heat-flux shields for routing reset heat
  away from protected regions;
- causal heat-flow models for relaxation variables with finite propagation
  speed.

## Candidate Physical Stack

- Beta-memory receiver: resonator, superconducting circuit, magnetic storage,
  or strain/phase register that records release history.
- Pulse-power interface: solid-state modulator, pulse-forming network, and
  snubber path feeding support-shell and collar hardware.
- Current limiter: superconducting or solid-state current-regulator stage with
  thermal telemetry and recovery margin.
- Reset-cap buffer: finite distributed storage volume for stress, current, or
  thermal load.
- Thermal routing manifold: anisotropic thermal metamaterial layer that moves
  heat flux into dump channels while preserving live-bore isolation.
- Decompression chamber: staged release path for wake-tail and reset-domain
  traces after live service exits.
- Reservoir port: explicit exchange path to card `006` for power `P`, radial
  force `F`, and support stress.

## Mathematical Constraints Carried Over

- Endpoint-J source rows remain non-live.
- Reset-cap source stays broad, bounded, no-tail, and coefficient-stable.
- Support-edge closure stays finite-width and low-coupling.
- Dense ledgers keep live leakage and singular support under the gate limits.
- Wake-tail traces remain reset-domain monitors.

## Design Implications

"Turning service off" is an engineered reset event. The endpoint plant needs
the design habits of pulsed power and protection hardware: defined stored
energy, shaped discharge, fault-current limit, thermal path, cooldown/recovery
time, and measured readiness before the next arm. The current math points to a
finite reset body with explicit reservoir exchange and distributed endpoint
depth.

## Open Questions

1. Which physical memory variable stores beta-release transfer with measurable
   recovery?
2. What pulse-power architecture can supply the collar and support shell while
   preserving endpoint closure headroom?
3. Can superconducting or solid-state limiter behavior implement the endpoint
   current-regulator role?
4. How should the thermal-routing manifold couple to the regulated
   heat/current reservoir in card `006`?
