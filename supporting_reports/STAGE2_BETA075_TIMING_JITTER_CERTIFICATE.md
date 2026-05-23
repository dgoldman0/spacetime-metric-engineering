# Stage II Beta075 Bounded Service-Timing Jitter Certificate

## Status

Status: `timing_jitter_pass_all_tested_offsets`.

The aligned-envelope certificate now has a robustness check against bounded
service-time phase error. The test keeps the source release tied to the
service schedule, but allows the whole release pattern to arrive early or late
by a common integer offset. This asks whether small-to-moderate schedule
misalignment can recreate the arbitrary impulse failure without giving every
row its own adversarial clock.

It does not. All tested common offsets pass through jitter radius `8` service
steps.

## Test Object

The test uses the same sealed beta075 package as the aligned-envelope rung:

- dense `rematch_w6_t1p5` closure
- covariant endpoint medium and `24x14` support closure
- cap-0.95 support-source coupling law
- bounded rapidity transport variable
- active non-live support-source domain

The admissible jitter class is a common offset around the service-aligned bins.
For each transport scenario, every source row first receives its
service-coordinate bin. The whole bin assignment is then shifted by
`-J ... +J` steps for each tested radius `J`, with clipping at the start and
end of the 48-step service window.

This remains a scheduled active-rail timing class. It is not row-independent
jitter, and it is not the arbitrary all-domain impulse adversary.

The tested radii were:

`0, 1, 2, 3, 4, 6, 8`

The machine output is structured only:

`toolkit/adm_harness_cli/runs/stage2_beta075_timing_jitter_certificate/`

## Result

Decision summary:

- status: `timing_jitter_pass_all_tested_offsets`
- tested radius count: `7`
- offset cases: `165`
- largest passing jitter radius: `8` steps
- max budget fraction: `0.742835`
- live support exclusion: `True`
- state amplification clean: `True`
- limiter clean: `True`

Worst case:

- scenario: `observed_action_inward_forward`
- radius: `0` steps
- offset: `0` steps
- row: `194`
- location: `support_edge_endpoint_junction / entry_precatch / support_edge`
- coordinates: `s=-1.2367021276595744`, `l=-2.1`

Per-direction maximum budget fractions stayed unchanged across the tested
jitter radii:

- outward/forward: `0.690041`
- inward/forward: `0.742835`
- outward/backward: `0.727448`

The 48-step tail again does not create delayed concentration. The maximum
state/source ratio remains below one, with the radius summaries carrying
`0.985750` as the largest value.

## Interpretation

This result says the service-aligned proof is not balanced on an exact clock
edge. A common early or late shift of the scheduled source pattern does not
increase the worst rapidity-budget pressure. The worst row remains the already
known inward/forward entry-precatch support-edge row, and its budget fraction
stays at the aligned-envelope value.

The main robustness watch is not a budget failure. It is the clipping behavior
at large offsets. At radius `8`, an extreme offset can put about `0.842260` of
the total source into one boundary service step because rows shifted outside
the 48-step window are clipped back to the edge. Even that edge pile remains
inside local rapidity budget, with no limiter clipping and no state/source
amplification. That is useful engineering margin, but it also marks the
boundary of what this certificate means: it covers common phase error, not
arbitrary independent row jitter.

The uncomfortable version of the read is therefore mild and precise. The proof
class should preserve a service-scheduled source law. If a future rung allows
uncorrelated row timing, then it is leaving the certified class and moving back
toward the impulse adversary that already failed.

## Implications

The fixed-background action-level timing story is now coherent:

- arbitrary all-domain impulse timing is too broad and fails;
- service-coordinate aligned schedules pass;
- the common nonnegative aligned-envelope class passes;
- bounded common service-timing jitter through radius `8` also passes.

This is enough to move upward. The remaining support-edge rows are watch rows
inside a passing scheduled class, not a reason to keep retuning the same
component.

## Next Rung

Move to the full `1+1` constitutive source-coupled rung.

The next test should stop treating the timing law as the main object and ask a
larger system question: when the constitutive support-source rule is evolved as
part of the `1+1` fixed-background service/radial system, does the sealed
package preserve the same local rapidity budgets, cone/transport margins,
live exclusion, and non-amplification without hiding a new component?

Carry row `194`, service-edge clipping, dense reset/core tightness, source-law
smoothness, thin characteristic margin, raw heat-current fragility, compact
bracket miss, and artificial `5e-4` overdrive as watches. Do not branch back
into source-edge fitting unless the full `1+1` rung fails and points back to a
specific physical mechanism.
