# Constraint Card 001: Live Packet Corridor

Status: component-level physical-design hypothesis.

## Role

The live packet corridor is the passenger-facing region. It is the part of the
rail that must remain quiet while the support plant does hard work around it.
The reports consistently treat this region as protected, not as the place where
the main source burden should be paid.

## Physical-Building Guess

Think of this as an isolated inner bore or capsule corridor inside a larger
active railbed. Its physical design would prioritize:

- geometric and field isolation from the support shell;
- smooth entry into the supported region;
- active monitoring of packet norm and packet-local density increments;
- a quiet center with only small handoff trim near the packet edge;
- fail-safe release/reset behavior if support margins are consumed.

The live corridor should not contain the radial scaffold, endpoint receiver, or
main support reservoir. It may include small packet-edge trim fields and
sensors, but the hard plant lives outside it.

## Inherited Constraints

- Live packet norm remains safely negative at the sealed `V=5` operating point.
- Packet `Delta rho` should remain quiet after standing-substrate subtraction.
- Live handoff trim may exist, but hard infrastructure roles must not
  contaminate the live packet.
- `V=10` currently fails live packet source safety, so high-service operation
  requires additional causal-margin engineering before promotion.
- Finite-domain radial ANEC is not clean for the demanded total, but the main
  negativity is not assigned to a passenger-filling live source layer.

## Interfaces

- Receives service from the handoff/rematch/collar layer.
- Is shielded from the support-shell actuator layer.
- Is monitored by the carrier-governance and diagnostic layer.
- Exposes only small live handoff trim demands to source-family accounting.

## Open Questions

1. What physical isolation mechanism keeps support-shell stress and endpoint
   exchange out of the live corridor?
2. Can live handoff trim be realized as a boundary/collar effect rather than a
   bulk passenger-region source?
3. What sensor set would detect packet-norm margin loss quickly enough to abort
   or retime service?
4. How much margin must be added before a high-service `V` ladder can be safe?
