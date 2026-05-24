# Constraint Card 005: Endpoint Receiver and Reset Plant

Status: component-level physical-design hypothesis.

## Role

The endpoint receiver/reset plant absorbs and organizes the source burden that
appears at support-edge and reset/decompression phases. It includes the
beta-memory receiver, bounded reset-cap body, finite support-edge closure
component, and reset-domain wake-tail handling.

## Physical-Building Guess

This subsystem resembles station-end machinery: receiver, buffer, cap,
decompression plant, and reset hardware. It would likely include:

- a memory-like receiver channel tied to beta-release transfer;
- support-edge structures that accept angular/current endpoint burden;
- reset-cap storage that spreads decompression demand over finite support;
- wake-tail restoration monitors outside live service;
- local coupling to the support reservoir for exchange-current closure.

The reports point away from a sharp edge-tail source and toward broad,
bounded, finite support.

## Inherited Constraints

- Endpoint-J source rows remain non-live.
- Reset-cap source stays broad, bounded, no-tail, and coefficient-stable.
- Support-edge closure stays finite-width and low-coupling.
- Dense ledgers should not grow live leakage or hidden singular support.
- Wake-tail traces are reset-domain monitors, not live-service carrier
  acceptance.

## Interfaces

- Receives beta-release memory from the handoff/release collar.
- Couples to the regulated heat/current medium.
- Requires support-reservoir exchange to close total conservation.
- Is watched by finite-domain ANEC and BV-style boundedness diagnostics.

## Open Questions

1. What physical memory variable stores beta-release transfer?
2. Can reset/decompression support be implemented as finite storage rather than
   edge-tail counterterms?
3. How does the reset plant hand power/radial-force exchange to the support
   reservoir?
4. Can endpoint source completion remove the closure-residual ANEC deficit?
