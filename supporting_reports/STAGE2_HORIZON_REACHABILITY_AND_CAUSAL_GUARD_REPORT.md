# Stage II Horizon Reachability And Causal Guard Report

Date: 2026-05-21

## Purpose

This report records the small/medium horizon-aware follow-up after the initial
Garattini-Zatrimaylov-style obstruction screen. The prior screen established a
real local causal-structure warning: the active-rail ADM point ledgers contain
minus-branch zero-crossing edges in the live packet and shell/throat overlap
band. That is the right channel to worry about, because packet-norm cleanliness,
selected-null improvement, and SNEC companion passes do not by themselves prove
that the rail avoids a horizon/trapping pathology.

The new question was sharper. The design does not need to remove every local
one-way-cone feature if that feature is the controlled service carrier. It does
need to avoid the stronger no-go-like behavior: a service entrance causally
reaching the carried live packet during active transport, especially if that
access rides with the shift and turns the support plant into an accidental
entry-to-exit throat. The test here therefore asks whether the local GZ-like
branch behavior is accompanied by actual radial reachability from an entrance
side into the carried packet.

The result is a split but useful one:

```text
Local branch-pinch diagnostics remain adverse.
Entry-to-carried-packet reachability is not observed during service/carry.
```

That distinction matters. The current evidence still does not prove global
horizon freedom, but it also does not show the more damaging GZ-like no-go
criterion that motivated the concern.

## Source Artifacts

Primary guard run:

```text
toolkit/adm_harness_cli/runs/endpoint_horizon_causal_margin_guard_small_61x83/
```

Primary reachability run:

```text
toolkit/adm_harness_cli/runs/endpoint_horizon_causal_reachability_61x83/
```

Reusable reachability script:

```text
toolkit/adm_harness_cli/scripts/run_entry_packet_reachability.py
```

Key generated files:

| file | role |
| --- | --- |
| `causal_margin_guard_small_summary.csv` | source-ledger summary for the causal-margin guard variants |
| `gz_obstruction/gz_obstruction_report.md` | GZ obstruction screen for the guarded variants |
| `gz_obstruction_beta075_reference_61x83/gz_obstruction_summary.csv` | same-grid beta075 unguarded reference |
| `combined_reachability_summary.csv` | combined entry-to-packet reachability result table |
| `*/entry_packet_reachability_summary.csv` | per-sweep reachability summaries |
| `*/entry_packet_reachability_hits.csv` | localized reachable packet hits |

The causal margin guard code was committed before the long run in commit
`cfbfe7e Add horizon causal margin guard`. The reachability script and this
report are follow-up artifacts from the present analysis.

## Diagnostic Definitions

The ADM convention remains

```text
ds^2 = -alpha^2 dsigma^2 + gamma_ll (dl + beta dsigma)^2 + gamma_omega dOmega^2
```

so the sampled radial coordinate null speeds are

```text
v_plus  = -beta + alpha / sqrt(gamma_ll)
v_minus = -beta - alpha / sqrt(gamma_ll)
```

The GZ obstruction screen uses these speeds to detect local branch pinches,
branch zero-crossing edges, stationary-vector sign changes through
`g_sigma_sigma = -alpha^2 + gamma_ll beta^2`, and shell/throat overlap between
the active support plant and the packet corridor.

The reachability screen is different. It starts from a chosen entrance-side seed
set and propagates a sampled 1+1 radial causal flood forward in `sigma`. At each
slice, a reachable grid point can reach the interval

```text
l + min(v_minus, v_plus) * Delta sigma
l + max(v_minus, v_plus) * Delta sigma
```

on the next slice. If the propagated mask intersects `inside_packet_live`, the
script records a packet hit with the corresponding stage and location.

The tested seed choices were deliberately redundant:

| seed mode | purpose |
| --- | --- |
| `domain_boundary`, width 1 | literal lower/upper radial domain boundary |
| `domain_boundary`, width 5 | conservative thicker entrance boundary |
| `support_outer_edge` | first side-facing cells inside support/quarantine service regions |
| `main_support_outer_edge` | first side-facing cells inside the main throat/support/packet-support carrier, excluding the outer quarantine shell |

All sweeps used both lower and upper entry sides, because the sign/orientation
convention should not be allowed to hide the answer.

## Causal-Margin Guard Result

The causal-margin guard was useful, but it did not solve the branch-pinch gate.
Every guarded case remained live-clean in the packet-norm channel:

```text
positive_live = 0 for all eight guarded ledgers
```

That means the guard did not make the receiver dangerous to the packet corridor.
It preserved the important safety result. It also trimmed some branch-crossing
counts, which makes it an informative local instrument. But the GZ obstruction
decision still failed for every guarded case.

Representative live-packet branch diagnostics:

| label | live positives | live branch-crossing edges | live `gtt >= 0` points | min branch abs margin | GZ decision |
| --- | ---: | ---: | ---: | ---: | --- |
| `beta075_p003_mid_61x83` reference | 0 | 53 | 133 | 0.008881 | fail |
| `beta075_p003_cg_packet` | 0 | 31 | 87 | 0.024927 | fail |
| `beta075_p003_cg_edge` | 0 | 30 | 86 | 0.006818 | fail |
| `beta075_p003_cg_support` | 0 | 26 | 82 | 0.000029 | fail |
| `beta100_base_cg_edge` | 0 | 30 | 86 | 0.006818 | fail |
| `beta100_base_cg_support` | 0 | 26 | 82 | 0.000029 | fail |
| `beta100_p003_cg_edge` | 0 | 30 | 86 | 0.006818 | fail |
| `beta100_post1p5_cg_edge` | 0 | 30 | 86 | 0.006818 | fail |
| `beta100_post1p5_cg_support` | 0 | 26 | 82 | 0.000029 | fail |

The most important nuance is that fewer crossing edges did not necessarily mean
a better causal margin. The support guard reduced the crossing count to 26, but
also produced a near-zero live branch point with a minimum branch margin of only
`2.932e-05`. That is the wrong shape for a clean fix: it suppresses some
discrete crossings while sharpening one local pinch. The packet guard was the
cleanest beta075 local-margin nudge by this metric, improving the minimum live
branch margin to `0.024927`, but it still failed the obstruction decision.

Narratively, this means the earlier attempt to "clamp away" the local GZ
signature was overkill as a design direction and underpowered as a proof tool.
It tells us the branch behavior is not a fragile artifact of one exact receiver
choice, and it should not be treated as a simple source-model typo. It is part
of the active carrier geometry. The question is whether that carrier geometry is
controlled and bounded, or whether it opens a physical through-corridor.

## Reachability Result

The reachability sweep gives the first direct answer to that sharper question.
Across original, dense, beta100 stress, retimed beta100, and guarded causal-margin
variants, there were no service-stage or carry-stage entry-to-live-packet hits.

Combined reachability summary:

| sweep | seed mode | entry width | side | total packet hits | service hits | carry hits |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| original/dense | domain boundary | 1 | lower | 0 | 0 | 0 |
| original/dense | domain boundary | 1 | upper | 0 | 0 | 0 |
| original width-5 | domain boundary | 5 | lower | 0 | 0 | 0 |
| original width-5 | domain boundary | 5 | upper | 0 | 0 | 0 |
| original support-edge | support outer edge | 1 | lower | 0 | 0 | 0 |
| original support-edge | support outer edge | 1 | upper | 0 | 0 | 0 |
| original main-support-edge | main support outer edge | 1 | lower | 0 | 0 | 0 |
| original main-support-edge | main support outer edge | 1 | upper | 44 | 0 | 0 |
| guarded | domain boundary | 1 | lower | 0 | 0 | 0 |
| guarded | domain boundary | 1 | upper | 0 | 0 | 0 |
| guarded width-5 | domain boundary | 5 | lower | 0 | 0 | 0 |
| guarded width-5 | domain boundary | 5 | upper | 0 | 0 | 0 |
| guarded support-edge | support outer edge | 1 | lower | 0 | 0 | 0 |
| guarded support-edge | support outer edge | 1 | upper | 0 | 0 | 0 |
| guarded main-support-edge | main support outer edge | 1 | lower | 0 | 0 | 0 |
| guarded main-support-edge | main support outer edge | 1 | upper | 68 | 0 | 0 |

The nonzero hits are all post-release-buffer hits from the upper main-support
edge. There are no hits in `catch_rematch`, `held_carry`, or
`release_shift_fade`.

Localized nonzero cases:

| label group | upper main-support-edge hits | stage | sigma range |
| --- | ---: | --- | --- |
| dense `beta075_p003_mid` | 4 | `post_release_buffer` | `1.57125..1.620` |
| 61x83 `beta075_p003_mid` | 1 | `post_release_buffer` | `1.620` |
| original beta100 baseline/p003/post1p5 | 13 each | `post_release_buffer` | `1.620..1.815` |
| guarded beta075 packet/edge/support | 1 each | `post_release_buffer` | `1.620` |
| guarded beta100 edge/support variants | 13 each | `post_release_buffer` | `1.620..1.815` |

This is the central result of the follow-up. The reachability test was designed
to catch the worrisome case: service-side causal access into the packet during
active carry. It did not find that case, even when the seed was moved inward to
the support edge and the boundary was widened.

The post-release hits should be tracked, but they are not the same finding. They
appear only after service, only from the upper main-support-edge seed, and only
in the post-release buffer. That is consistent with endpoint/wake restoration or
normal post-release causal reconnection. It is not evidence that the service
entrance can ride the shift into the carried packet.

## Narrative Implication

The current picture is no longer "branch pinch means design failure." It is:

```text
The rail has local one-way causal structure in the carrier band, but the first
entry-to-packet reachability diagnostic does not show that the entrance can
causally access the carried live packet during service.
```

That is a materially different physical interpretation. A local GZ-like branch
signature remains a real warning because it says the cones are being tilted
hard enough to change radial accessibility in the sampled ADM chart. But the
no-go concern becomes much stronger only if that local branch behavior creates a
live causal corridor from the service entrance to the packet, or from entry
through packet toward exit. This screen did not observe either condition.

This also changes how to think about the causal-margin guard. The guard was not
the unlock. It did not remove the local obstruction decision and should not be
presented as a horizon fix. Its value was experimental: it showed that direct
local penalization can trim some symptoms while leaving the deeper carrier
structure intact. That pushes the research program away from "delete the pinch"
and toward "classify the pinch, bound it, and prove it does not become a live
throat."

For beta075 `p003_mid`, the result is especially encouraging. That candidate was
already live-clean and endpoint-effective in the receiver/source-accounting
channels. The reachability screen adds that, in the sampled radial causal flood,
the service entrance does not reach the carried packet during active service.
That supports continued promotion of beta075 as a controlled carrier/receiver
mechanism, while keeping horizon freedom as an open gate rather than a settled
claim.

For beta100, the result is also clarifying. Beta100 remains a stress timing case:
the receiver does not give the same transfer-clean endpoint accounting there.
But the reachability screen does not turn beta100 into a safety disaster. It
shows the same basic pattern: local branch behavior persists, while service/carry
entry-to-packet hits remain absent. The wider beta release still weakens
robustness and timing margin, not the measured live-packet causal safety margin.

## Current Claim Language

The old report-grade language should be revised from:

```text
The active-rail metric trips a local GZ-style causal branch gate; horizon/trapping
freedom remains unresolved and currently adverse at ledger-screen level.
```

to:

```text
The active-rail metric still trips local GZ-style branch-pinch diagnostics, but
the follow-up radial reachability screen finds no service-stage or carry-stage
entry-to-live-packet causal access in the sampled ledgers. Horizon/trapping
freedom remains unproven, but the stronger GZ-like no-go criterion is not
observed by the current reachability gate.
```

The strongest honest short version is:

```text
Local GZ-like behavior is present; live service throat behavior is not observed.
```

That is not a final proof. It is a better gate definition.

## Limitations

This is still a sampled 1+1 radial diagnostic. It is not a global causal proof.
It does not include angular null geodesic structure, continuous interpolation of
the metric, adaptive near-branch integration, or refinement scaling of the
reachability result.

The entrance masks are still proxies. `domain_boundary` is deliberately crude.
`support_outer_edge` and `main_support_outer_edge` are better service-region
approximations, but the design now needs explicit masks for packet core, carrier
sheath, entry mouth, exit mouth, trailing wake, and post-release restoration
regions.

The persistent-boundary source mode is conservative for reachability, because it
allows the entry side to keep injecting causal access at every sampled time
slice. That makes the zero service/carry hit result more meaningful, but it also
means the post-release hits should not be overinterpreted until we split entry,
carry, and release source windows.

Finally, the branch-pinch count is still a real adverse local metric diagnostic.
The fact that it does not currently imply live entrance access does not mean it
can be ignored. It means the next gate should classify where the one-way region
lives, when it opens, when it closes, and whether it remains bounded away from
the carried packet during service.

## Recommended Next Work

The next stage should not be a broad source-family replacement. The current
evidence favors instrumentation and claim refinement first:

1. Define explicit geometric masks for packet core, carrier sheath, entry side,
   exit side, trailing wake, and post-release region.
2. Promote the reachability gate into the harness with stage-separated verdicts:
   `catch_rematch`, `held_carry`, and `release_shift_fade` should require zero
   entry-to-live-packet hits.
3. Track post-release hits separately as restoration/wake coupling rather than
   mixing them with service-stage failures.
4. Add exit-to-entry and exit-to-packet reachability variants to test for an
   accidental through-corridor.
5. Run longer-domain or continuous radial null tracing from the explicit entry
   and exit masks.
6. Repeat at higher resolution around the branch-crossing band to test whether
   the local pinch sharpens, smooths, or stays bounded.

If those pass, the design story becomes stronger and more specific: the rail is
not a free warp bubble crossing a wormhole throat; it is a service carrier that
uses a controlled one-way region to move support burden while keeping the live
packet causally protected. That is exactly the architectural distinction we
needed to test.
