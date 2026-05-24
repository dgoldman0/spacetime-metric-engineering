# Constraint Card 005: Endpoint Receiver and Reset Plant

Status: component-level physical-design hypothesis.

## Controlling Sources

- Internal: endpoint-J source freeze, endpoint current-regulator screen,
  covariant endpoint-medium audit, support total-closure reports.
- External analogs:
  [`wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf`](../sources/wilson_dynamical_casimir_superconducting_circuit_1105.4714.pdf),
  [`denicol_heat_flow_transient_relativistic_fluid_1207.6811.pdf`](../sources/denicol_heat_flow_transient_relativistic_fluid_1207.6811.pdf),
  [`natario_rigid_elastic_solids_relativity_1912.08221.pdf`](../sources/natario_rigid_elastic_solids_relativity_1912.08221.pdf),
  [`pfenning_ford_quantum_inequality_curved_spacetimes_gr-qc9805037.pdf`](../sources/pfenning_ford_quantum_inequality_curved_spacetimes_gr-qc9805037.pdf).

## Role

The endpoint receiver/reset plant absorbs and organizes the source burden that
appears at support-edge and reset/decompression phases. It includes the
beta-memory receiver, bounded reset-cap body, finite support-edge closure
component, and reset-domain wake-tail handling.

## Actual Physical Construction Hypothesis

This subsystem is station-end machinery. It is the rail's buffer, brake,
receiver, and decompression plant. The physical hypothesis is that endpoint
cost should be stored and released through finite state variables rather than
sharp boundary counterterms.

Lab-scale analog options:

- superconducting circuit endpoint with tunable SQUID boundary, storing phase
  and releasing it through controlled modulation;
- optical resonator/cavity endpoint with controlled coupling and decay,
  recording pulse history as beta-memory analog;
- elastic/metamaterial termination whose strain/stress state carries the reset
  cap and support-edge closure response;
- active transmission-line termination that changes impedance through a
  scheduled reset cycle.

Speculative rail-scale assembly:

- receiver ring that records beta-release transfer;
- reset-cap buffer distributed over finite length, not an edge singularity;
- support-edge absorber layer coupled to angular/current endpoint demand;
- decompression chamber that keeps wake-tail traces outside live service;
- energy/stress handoff port to the support reservoir.

## Hardware Sketch

- Beta-memory register: phase, flux, strain, or field-history variable.
- Reset-cap buffer: finite distributed storage with no sharp edge-tail.
- Support-edge receiver: localized but broad enough to avoid coefficient growth.
- Decompression stage: releases stored stress after live service exits.
- Wake-tail monitor: verifies reset-domain tails do not re-enter live service.

## Mathematical Constraints Carried Over

- Endpoint-J source rows remain non-live.
- Reset-cap source stays broad, bounded, no-tail, and coefficient-stable.
- Support-edge closure stays finite-width and low-coupling.
- Dense ledgers should not grow live leakage or hidden singular support.
- Wake-tail traces are reset-domain monitors, not live-service carrier
  acceptance.

## Design Implications

The endpoint plant is where "turning the service off" becomes physical. It
must catch the pulse without creating a singular layer. The DCE superconducting
circuit is not an active-rail source model, but it is a useful reminder that
fast effective-boundary changes can be implemented as controlled circuit
modulation rather than literal moving walls. That style of thinking fits the
reset-cap and beta-memory receiver better than an edge-tail source sheet.

## Open Questions

1. What physical memory variable stores beta-release transfer?
2. Can reset/decompression support be implemented as finite storage rather than
   edge-tail counterterms?
3. How does the reset plant hand power/radial-force exchange to the support
   reservoir?
4. Can endpoint source completion remove the closure-residual ANEC deficit?
