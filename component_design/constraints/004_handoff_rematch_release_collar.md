# Constraint Card 004: Handoff, Rematch, Release, and Carrier Collar

Status: component-level physical-design hypothesis.

## Role

The handoff/collar system manages the transition between the live packet and
the support plant. It catches, rematches, briefly holds, releases, and restores
the packet while keeping derivative cost out of the packet center.

## Physical-Building Guess

This subsystem looks like a phase-matching collar or station throat around the
live bore. It would include:

- entry containment windows for live radial-pressure control;
- catch/rematch bearing windows for angular/current and radial-null relief;
- trailing-edge beta-rematch sleeve hardware near the packet edge;
- finite beta-collar widening for branch-band bundle preservation;
- smooth release timing with matched hold and derivative-limited beta fade;
- local limiter/abort logic if handoff residuals exceed margin.

It is less like a passenger cabin and more like a precision docking and
impedance-matching system for the metric service.

## Inherited Constraints

- The packet center should stay quiet; strongest correction sits near the
  trailing/inner packet edge.
- Compact handoff separates entry pressure containment from catch/edge
  derivative smoothing.
- Widened trailing-edge rematch preserves finite-bundle carrier behavior.
- Live handoff trim exists, but should remain small and explicitly assigned.
- The finite-domain ANEC diagnostic shows a secondary plus-branch live-handoff
  trim extreme after closure residual removal; this subsystem must not hide
  that cost.

## Interfaces

- Receives scheduled service from the support-shell actuator layer.
- Protects the live packet corridor during entry/catch/release.
- Feeds endpoint receiver memory through beta-release transfer.
- Is monitored by causal-carrier reachability and dense-bundle diagnostics.

## Open Questions

1. Can packet-edge trim be implemented as a collar boundary condition rather
   than a live bulk source?
2. What physical timing mechanism provides matched hold and smooth beta fade?
3. Can collar widening be service-aware, especially for high-service cases?
4. Can handoff trim be averaged or source-completed to reduce finite-domain
   ANEC residue?
