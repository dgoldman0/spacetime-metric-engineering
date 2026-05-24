# Constraint Card 002: Standing Support Substrate and Radial Backbone

Status: component-level physical-design hypothesis.

## Role

The standing support substrate is the prepared railbed: throat/core support,
radial support shell, angular jacket, baseline lapse structure, and the
dominant non-live radial support body. It supplies the infrastructure that lets
the live packet avoid carrying the main source burden.

## Physical-Building Guess

This subsystem most resembles a permanent support scaffold rather than a
vehicle component. Physically, it would be a prepared rail segment with:

- a radial-tension backbone close to a string-cloud-like source;
- throat/core and angular-capacity structure;
- a support shell surrounding the live bore;
- spatial gradients shaped to avoid point-peak and shell/throat concentration;
- reset/decompression capacity at the rail ends.

In ordinary engineering language, this is the railbed and load-bearing
infrastructure. In the source-family language, it is where the near
`p_l = -rho` radial support and angular/throat capacity live.

## Inherited Constraints

- The dominant non-live radial infrastructure body is close to
  NEC-saturating radial tension, with `p_l/rho` near `-1`.
- The areal flux proxy should stay nearly constant across the main radial body.
- The scaffold should remain non-live.
- Residual selected-null burden after subtracting the scaffold must be assigned
  to endpoint/support completion rather than ignored.
- Finite-domain radial ANEC remains a source-completion target, not a current
  pass claim.

## Interfaces

- Provides the stable background for support-shell metric actuators.
- Couples to throat-capacity and angular jacket control.
- Hands endpoint residuals to the receiver/reset plant.
- Supplies the source-family target split used by the regulated medium and
  support reservoir.

## Open Questions

1. What recognizable source family can approximate the constant-flux radial
   string-cloud backbone without singular layers?
2. Can the radial support be made service-aware without changing the live bore?
3. What physical structure supplies angular-capacity support `G` while sharing
   space with radial support `A/B`?
4. Can source-completion reduce the finite-domain ANEC residual while leaving
   the carrier geometry intact?
