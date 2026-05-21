# Stage II Horizon Escape Ladder Pilot

Date: 2026-05-21

## Purpose

This report records the first ladder-style global-horizon pilot after the local
GZ obstruction and entry-to-packet reachability screens. The goal was not to
prove theorem-level event-horizon freedom. The goal was to test the next
operational rung: when the finite ADM ledger is given a longer future domain,
do sampled radial null families from the live packet and carrier actually escape
to exterior radial boundaries, or do they remain trapped in the service region?

The prior reachability result already found no service-entry-to-live-packet
hits during active service/carry. This pilot asks the complementary question:
from packet/carrier seed masks themselves, can the outgoing radial null families
leave the domain?

## Harness Additions

New committed script:

```text
toolkit/adm_harness_cli/scripts/run_horizon_escape_ladder.py
```

New committed pilot spec:

```text
toolkit/adm_harness_cli/specs/endpoint_horizon_escape_ladder_pilot.json
```

The script traces sampled 1+1 radial null families from explicit seed masks:

```text
packet_live
packet_geom
main_carrier
support_plant
branch_band_live
post_release_packet
post_release_carrier
lower_boundary
upper_boundary
```

For each seed it follows both

```text
v_plus  = -beta + alpha / sqrt(gamma_ll)
v_minus = -beta - alpha / sqrt(gamma_ll)
```

and records whether the plus branch reaches the upper radial boundary, the minus
branch reaches the lower radial boundary, or the trace remains unresolved at the
upper `sigma` boundary.

## Runs

Initial finite-domain pilot, original/dense and guarded sets:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_pilot_61x83/original_and_dense/
toolkit/adm_harness_cli/runs/horizon_escape_ladder_pilot_61x83/guarded_causal_margin/
```

Existing domain:

```text
s: -1.5 .. 2.4
l: -4.2 .. 4.2
```

Extended four-anchor domain:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_pilot_extended_61x83/
s: -1.5 .. 6.0
l: -6.0 .. 6.0
grid: 61 x 83
```

Long-tail two-anchor domain:

```text
toolkit/adm_harness_cli/runs/horizon_escape_ladder_pilot_longtail_85x83/
s: -1.5 .. 9.0
l: -6.0 .. 6.0
grid: 85 x 83
```

The extended and long-tail ledgers were live-clean:

```text
positive_packet_norm_live = 0
```

for every computed pilot case.

## Initial Finite-Domain Result

On the existing `s_max = 2.4` domain, the escape diagnostic mainly confirmed
that the domain was too short. For original/dense cases, only the exterior
boundary outward branches escaped: lower-boundary minus and upper-boundary plus.
All packet, carrier, branch-band, and post-release seed traces hit
`s_upper_boundary`.

Aggregate original/dense result:

```text
traces:                 450
expected radial escapes: 50
s_upper_boundary:       400
```

Aggregate guarded result:

```text
traces:                 720
expected radial escapes: 80
s_upper_boundary:       640
```

This is not evidence of trapping by itself. It says the old ledger ended before
packet/carrier null escape could be decided.

## Extended Four-Anchor Result

The `s_max = 6.0`, `l = +/-6.0` run was the first informative rung. It compared:

```text
horizon_escape_beta075_p003_mid
horizon_escape_beta100_baseline
horizon_escape_beta100_p003_mid
horizon_escape_beta100_p003_mid_post1p5
```

All four remained live-clean. Escape counts improved sharply:

| label | traces | expected escapes | unresolved at `s_max` |
| --- | ---: | ---: | ---: |
| `horizon_escape_beta075_p003_mid` | 90 | 40 | 50 |
| `horizon_escape_beta100_baseline` | 90 | 41 | 49 |
| `horizon_escape_beta100_p003_mid` | 90 | 41 | 49 |
| `horizon_escape_beta100_p003_mid_post1p5` | 90 | 41 | 49 |

The important resolved part was directional: every live-packet plus branch,
packet-geometry plus branch, branch-band-live plus branch, main-carrier plus
branch, and support-plant plus branch reached the upper radial boundary. The
remaining live-packet minus branches were not stuck near the packet; they ended
near the lower boundary. In the unresolved packet-live minus traces, final
`l` values were about `-5.31 .. -5.99` against a lower boundary of `-6.0`.

That made the next rung obvious: extend the future domain again and check
whether the near-boundary minus traces exit.

## Long-Tail Two-Anchor Result

The `s_max = 9.0`, `l = +/-6.0` run tested the two anchor geometries:

```text
horizon_escape_beta075_p003_mid
horizon_escape_beta100_baseline
```

Both remained live-clean. The live-service escape result became strongly
favorable:

| seed scope | branch | traces | expected escapes | unresolved |
| --- | --- | ---: | ---: | ---: |
| `packet_live` | plus | 10 | 10 | 0 |
| `packet_live` | minus | 10 | 10 | 0 |
| `packet_geom` | plus | 10 | 10 | 0 |
| `packet_geom` | minus | 10 | 10 | 0 |
| `branch_band_live` | plus | 10 | 10 | 0 |
| `branch_band_live` | minus | 10 | 10 | 0 |
| `main_carrier` | plus | 10 | 10 | 0 |
| `main_carrier` | minus | 10 | 10 | 0 |
| `support_plant` | plus | 10 | 10 | 0 |
| `support_plant` | minus | 10 | 10 | 0 |
| `post_release_carrier` | plus | 10 | 10 | 0 |
| `post_release_carrier` | minus | 10 | 10 | 0 |
| `post_release_packet` | plus | 10 | 10 | 0 |
| `post_release_packet` | minus | 10 | 3 | 7 |

By label:

| label | traces | expected escapes | unresolved |
| --- | ---: | ---: | ---: |
| `horizon_escape_beta075_p003_mid_longtail` | 90 | 76 | 14 |
| `horizon_escape_beta100_baseline_longtail` | 90 | 77 | 13 |

The remaining unresolved traces are not live-service traces. They are:

```text
post_release_packet minus: 4 beta075, 3 beta100
lower_boundary plus: 5 per label
upper_boundary minus: 5 per label
```

The boundary traces are inward-from-boundary controls, not horizon failures.
The post-release packet-minus traces still end near the lower boundary by
`s = 9.0`, with final `l` roughly `-5.46 .. -5.87`. They should be tracked as
post-release restoration/wake-tail residuals, not as live packet trapping.

## Interpretation

This is the first genuinely favorable global-horizon ladder signal. The local
GZ branch-pinch screen remains adverse, but on the longer finite domain the
live packet and main carrier do not behave like trapped regions in the sampled
1+1 radial diagnostic. Both radial null branches escape from the live packet,
the live branch band, the packet geometry mask, the main carrier, and the
support plant in the long-tail beta075 and beta100-baseline anchors.

That directly supports the refined claim architecture:

```text
Local GZ-like branch behavior is present, but live-service radial trapping is
not observed in the long-tail pilot.
```

The result also gives a cleaner reading of the local branch signs. In the
long-tail traces, several minus-branch paths pass through the branch-sensitive
region and still reach the lower exterior boundary. The local one-way feature is
therefore not automatically equivalent to a global no-go throat. At least in
this sampled radial pilot, it behaves more like a controlled carrier cone tilt
than a permanent packet-trapping horizon.

The post-release packet-minus residual is the one remaining caveat. It is not a
live-service failure, but it says the release/wake tail still needs a slightly
longer or more targeted restoration check. The fact that post-release carrier
traces escape while a few post-release packet-minus traces remain near-boundary
unresolved suggests a finite-domain wake-tail issue, not a design-killing live
throat.

## Limits

This is still a radial 1+1 sampled-ledger diagnostic. It is not an angular
geodesic calculation, not a trapped-surface/null-expansion screen, and not a
mathematical event-horizon proof. The long-tail rung covered only beta075
`p003_mid` and beta100 baseline; beta100 `p003_mid` and beta100 `post1p5` were
tested at `s_max = 6.0` but not yet at `s_max = 9.0`.

The long-tail grid is a domain-extension pilot, not a refinement pass. It uses
`85 x 83` over a larger time extent, so it preserves roughly the `s` spacing of
the `s_max = 6.0` pilot but does not refine the branch band. The next numerical
question is convergence: whether the escape result is stable when the branch
band and packet/carrier seeds are sampled more densely.

## Next Rungs

Recommended next work:

1. Run the `s_max = 9.0` long-tail check on beta100 `p003_mid` and beta100
   `p003_mid_post1p5`.
2. Add an automated report-grade verdict that separates live-service masks from
   post-release and boundary-control masks.
3. Increase seed coverage in the live branch band and main carrier.
4. Run a refinement rung around the live branch band, not a broad redesign.
5. Extend only the post-release packet-minus tail if the wake-tail question
   remains narratively important.
6. Add trapped-surface/null-expansion diagnostics after the radial escape ladder
   stabilizes.

Current read:

```text
The design is not globally proven horizon-free, but the first ladder evidence
is favorable: the live packet and carrier escape radially on the long-tail
pilot, despite the local GZ-like branch signature.
```
