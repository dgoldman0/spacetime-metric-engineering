# Constraint Card 003: Support-Shell Metric Actuator Layer

Status: component-level physical-design hypothesis.

## Role

The support-shell actuator layer is the annular infrastructure band that routes
service-induced demand away from the live packet. In metric terms it acts
through carrying-flow `beta`, clock-lapse `alpha`, rail-stretch `gamma_ll`,
and throat-capacity `gamma_OmegaOmega`.

## Physical-Building Guess

This subsystem looks like a distributed actuator shell wrapped around the live
bore. It would not be a single engine. It would be an array of timed annular
modules that can shape several coupled channels:

- carrying-flow modules for the support-contained shift/load field;
- clock-lapse modules for causal-margin support;
- rail-stretch modules for radial metric capacity and peak shaping;
- throat-capacity modules for angular/throat support;
- timing electronics that place the actuator pulse relative to entry, catch,
  rematch, release, and reset.

The reports suggest that same-window single-channel forcing is too blunt. The
physical actuator should be designed as a coupled support-shell plant.

## Inherited Constraints

- Reduced support-shell routing must put incremental `Delta j_l` into
  catch/rematch support infrastructure with tiny packet exposure.
- Raised-cosine annular bearing is the preferred matched-strength comparator.
- Clock-lapse is the strongest default partner for aggregate burden reduction.
- Rail-stretch is useful as a peak-shaping comparator.
- Same-window throat-capacity is neutral by default and should remain a
  comparator unless a later intrinsic-window design earns promotion.
- High-amplitude or high-service cases consume packet margin, so actuator
  strength is not unlimited.

## Interfaces

- Built on top of the standing support substrate.
- Timed by the handoff/rematch/release choreography.
- Must not leak into the live packet corridor.
- Feeds source ledgers that assign non-live burden to support and endpoint
  roles.

## Open Questions

1. What physical actuation mechanism can couple `beta`, `alpha`, and
   `gamma_ll` without overproducing radial-null or current burden?
2. Can annular actuator modules be made smooth enough to avoid point-peak
   growth under refinement?
3. Should throat-capacity be a separate physical layer rather than same-window
   support-shell actuation?
4. What service-aware scaling law should retune this layer away from `V=5`?
