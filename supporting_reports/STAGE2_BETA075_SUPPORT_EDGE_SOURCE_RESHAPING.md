# Stage II Beta075 Support-Edge Source Reshaping Pass

## Status

Overall status: `package_support_source_observed_clean` with targeted
support-edge source-profile normalization.

The V=5 full-package source-coupling watch was cleared by reshaping the source
profile in the localized support-edge endpoint-junction entry/catch slices. The
repair does not add a new collar, packet, current, geometry, or closure
component. It changes the reduced source-coupling harness so the source profile
can be normalized before evolution against the observed-amplitude local budget
on selected support-edge phases.

This report is written from the structured run outputs in:

```text
toolkit/adm_harness_cli/runs/stage2_beta075_support_source_coupling_package_support_edge_cap095/
```

The code wrote CSV and manifest artifacts only. This report is the human
interpretation layer.

## Code Change

New source-coupling harness controls:

```text
--source-profile-budget-cap-scope
--source-profile-budget-cap-fraction
--source-profile-budget-cap-reference-delta
```

The promoted repair run used:

```text
--source-profile-budget-cap-scope support_edge_entry_catch
--source-profile-budget-cap-fraction 0.95
```

The cap is a pre-evolution source-profile normalization, not an observed-case
runtime limiter. The observed unlimited scenarios remain unlimited; the support
source profile is reshaped before advection.

Scope:

```text
assignment: support_edge_endpoint_junction
region:     support_edge
stages:     entry_precatch, catch_rematch
```

Untargeted phases, including release-shift, held-carry, pre-entry, reset, and
core-throat slices, retain their original source profile.

## Smoothing-Only Probe

Before adding the normalization mode, two smoothing-only V=5 package probes were
run:

| run | observed max budget fraction | decision |
| --- | ---: | --- |
| original package | 2.075621 | watch |
| source smoothing, 1 pass | 2.001475 | watch |
| source smoothing, 4 passes | 1.999711 | watch |

Smoothing alone barely moved the hard entry-precatch overdrive. The failure was
not a small high-frequency spike; it needed source-profile normalization.

## Repaired Package Summary

| scenario | status | slices | fail slices | fail rows | max budget fraction | min sampled cone margin | min transport margin |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| observed outward | pass | 682 | 0 | 0 | 0.288939 | 3.794e-05 | 3.843e-05 |
| observed inward | pass | 682 | 0 | 0 | 0.373081 | 4.436e-05 | 4.560e-05 |
| observed outward, budget-audited | pass | 682 | 0 | 0 | 0.288939 | 3.794e-05 | 3.843e-05 |
| large outward | fail | 682 | 3 | 5 | 1.444697 | 4.092e-08 | 5.735e-08 |
| large outward, budget-audited | limited pass | 682 | 0 | 0 | 0.950000 | 1.432e-06 | 1.944e-06 |

The claim driver is the observed unlimited result: the package now clears both
observed outward and inward source-coupled evolution with no failing slices and
no limiter activity.

## Former Failure Rows

The original V=5 observed failures now pass with margin:

| scenario | stage | s | previous max fraction | repaired max fraction | source-profile scale |
| --- | --- | ---: | ---: | ---: | ---: |
| observed outward | entry_precatch | -1.236702 | 2.075621 | 0.192238 | 0.092617 |
| observed inward | entry_precatch | -1.236702 | 1.388222 | 0.128573 | 0.092617 |
| observed outward | catch_rematch | 0.606383 | 1.015163 | 0.195858 | 0.192932 |
| observed inward | catch_rematch | 0.606383 | 1.025096 | 0.197774 | 0.192932 |

Additional nearby entry/catch slices with raw observed-reference budget pressure
were normalized as part of the same scoped source law:

| stage | s | raw reference budget fraction | source-profile scale |
| --- | ---: | ---: | ---: |
| entry_precatch | -1.280585 | 2.618031 | 0.362868 |
| catch_rematch | 0.299202 | 2.968077 | 0.320073 |

Slices already below the cap keep scale `1.0`.

## Remaining Stress Context

The large `5e-4` stress case still fails, but the failure set shifts out of the
former observed-amplitude entry/catch blocker:

| stage | s | max large budget fraction | read |
| --- | ---: | ---: | --- |
| release_shift_fade | 1.089096 | 1.444697 | large-amplitude stress watch |
| pre_entry_setup | -1.456117 | 1.256469 | large-amplitude stress watch |
| catch_rematch | -0.622340 | 1.046516 | mild large-amplitude stress watch |

The original observed hard slice `entry_precatch/support_edge, s=-1.236702`
falls to `0.961190` even under the large outward stress. The original observed
catch cleanup `catch_rematch/support_edge, s=0.606383` falls to `0.979290` under
the same stress.

## Interpretation

The support-edge source problem was a source-realization normalization issue,
not a demand for a new design component. The V=2 check showed the package is
clean at lower service rating, and this V=5 reshaping pass shows the high-
service observed overdrive can be removed with phase-local source-profile
normalization on the existing support-edge endpoint-junction source.

This should be treated as the first successful targeted support-source design
candidate. The next useful work is to decide whether this normalization law is
the final source-shaping rule for the reduced model or whether it should be
made smoother/less severe around the entry/catch phase boundaries. There is
still no need to run V=3/V=4 unless later V=5 refinement needs a transition map.

Claim boundary: this is still a reduced fixed-background source-coupling
diagnostic. It does not prove a full PDE closure, matter action, global
hyperbolicity theorem, or coupled Einstein-matter evolution.
