# Constraint Card 007: Carrier Governance and Diagnostics

Status: component-level physical-design hypothesis.

## Role

Carrier governance is the supervisory layer that decides when the rail can arm,
carry, release, reset, and connect to other rails. It includes causal-carrier
diagnostics, reachability gates, dense finite-bundle carrier audits,
service-time ledgers, wake-tail monitoring, and rail-time chronology rules.

## Physical-Building Guess

This subsystem is the control room and sensor fabric of the rail. It is not the
source plant itself. It would likely include:

- field/geometry monitors for branch margins and packet norm;
- probe/diagnostic channels for reachability and radial escape;
- bundle-quality monitors for carrier-collar compression;
- timing controllers for service-coordinate source release;
- reset/wake-tail monitors after live service;
- a chronology governor for single-rail and networked operation.

In a build design, this layer would probably be as important as the source
hardware, because the accepted V5 package is timing- and margin-sensitive.

## Inherited Constraints

- Measured branch behavior is accepted only through reachability, escape,
  finite-bundle, and scheduled-probe gates.
- Dense finite-bundle carrier transport must avoid caustic-like collapse flags.
- Exterior-null service-time advantage is an operational rating, not a global
  causal theorem.
- Rail-time chronology governance is mandatory for return links, cross-links,
  reset intervals, and network routing.
- Timing jitter is bounded around service-coordinate aligned envelopes.

## Interfaces

- Monitors live packet corridor safety.
- Arms support-shell actuator and handoff/release timing.
- Supervises endpoint/reset readiness.
- Carries margin data back to the source-family and support-reservoir design.

## Open Questions

1. What live observables correspond to branch margin, packet norm, and support
   closure in a physical rail?
2. How conservative should the rail-time governor be relative to service-time
   advantage?
3. Can carrier-bundle compression be monitored locally, or only by full
   scheduled probe reconstruction?
4. What abort/reset policy is required when cone, closure, or timing margins
   approach their watch constants?
