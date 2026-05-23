# Stage II Beta075 Service-Aligned Scheduled Evolution

## Status

Status: `service_aligned_schedule_pass_all_widths`.

The action-level timing question now has the expected scheduled-service answer.
The arbitrary impulse certificate was useful because it exposed the proof gap,
but it was also deliberately broader than the physical active-rail claim. A rail
service is scheduled: support-source activation is tied to service position and
phase, not allowed to collapse everywhere at one instant.

When the observed beta075 source is released on a service-coordinate-aligned
schedule, the sealed package passes across every tested pulse width and all
tested transport directions.

## Test Object

The service-aligned certificate keeps the same sealed package and source law as
the action-PDE proof-obligation rung:

- dense `rematch_w6_t1p5` closure
- covariant endpoint medium and `24x14` support closure
- cap-0.95 support-source coupling law
- bounded rapidity transport variable
- active non-live support-source domain

The difference is timing. Instead of allowing the observed source budget to
arrive as an arbitrary all-domain impulse, each row is assigned a source-release
time from its service coordinate `s`. Forward service runs activate increasing
`s`; backward service runs activate decreasing `s`. The harness then sweeps
raised-cosine pulse widths over:

`1, 3, 5, 7, 9, 15, 31, 47` steps.

The machine output is structured only:

`toolkit/adm_harness_cli/runs/stage2_beta075_service_aligned_schedule/`

## Result

All 24 tested width/direction cases pass.

Decision summary:

- status: `service_aligned_schedule_pass_all_widths`
- scenario count: `24`
- narrowest passing width: `1` step
- max budget fraction across the sweep: `0.742835`
- min budget fraction across the sweep: `0.176333`
- max state/source ratio: `0.985750`
- live support exclusion: `True`

Worst case:

- scenario: `observed_action_inward_forward`
- width: `1` step
- max budget fraction: `0.742835`
- row: `194`
- location: `support_edge_endpoint_junction / entry_precatch / support_edge`
- coordinates: `s=-1.2367021276595744`, `l=-2.1`

The narrowest aligned pulses therefore keep about `25.7%` budget headroom even
in the worst tested row. Wider source-time envelopes increase that headroom:
the broadest tested width reaches a max budget fraction of about `0.193666` in
the outward/backward case and `0.176333` in the inward/forward case.

## Interpretation

This result explains the previous action-PDE gap in a healthy way.

The temporal-profile-independent impulse certificate failed at budget fraction
`1.158579` because it allowed all observed source burden to arrive at once at
the wrong support-edge row. That adversary is valuable as a mathematical stress
test, but it is not the natural operating class for a scheduled active rail.

The service-aligned certificate restores the missing physical structure. Once
source activation is tied to service coordinate, the same sealed beta075 package
stays inside local rapidity budgets with comfortable margin. Even the one-step
aligned schedule, which is still sharp in time, does not reproduce the impulse
failure because the release is distributed along the service order rather than
collapsed globally.

This is a strong sign that the current problem is not a hidden support-edge
defect. The bad case was an overbroad timing adversary. The good case is the
active-rail timing class the design is actually meant to inhabit.

## Implications

The source-time regularity obligation is now more specific. It is no longer
"find some temporal smoothing that makes the numbers behave." The aligned sweep
shows that service-order scheduling itself is the protective structure.

The next proof should formalize that structure:

1. Define the admissible source-time class as service-coordinate aligned.
2. State the minimum assumptions on pulse width, ordering, and nonnegative
   source release.
3. Prove or certify that this class cannot collapse into the arbitrary impulse
   adversary.
4. Propagate that class through the fixed-background radial and service-time
   transport operators.
5. Gate against local rapidity budgets, cone/transport margins, live exclusion,
   and no hidden component.

The narrowest tested width already passes, so the proof does not appear to need
a generous smoothing assumption. The stronger and more natural condition is
alignment to the service schedule.

## Next Rung

Promote service-coordinate-aligned timing as the lead admissible envelope for
the action-level fixed-background PDE proof.

The next useful rung is a formal aligned-envelope certificate: instead of
sweeping finite pulse widths as separate numerical cases, prove a bound for the
whole admissible service-aligned class and identify the exact minimum
regularity assumptions needed to keep the invariant rapidity margin.

Do not reopen component tuning from this result. The evidence now points toward
schedule-law formalization, not geometry/source redesign.
