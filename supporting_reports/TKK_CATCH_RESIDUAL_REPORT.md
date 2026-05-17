# Targeted Tkk Catch/Rematch Residual Fit

## Scope

This is a source-proxy refinement for the new freeze candidate. It isolates the negative radial null channel, `neg_Tkk_radial`, and asks whether the catch/rematch residual has a specific missing transient shape.

It is still a proxy fit. It does not prove a matter model. It tests whether the demanded source burden can be represented by a cleaner component story.

## Result

The old generic catch/rematch component was too blunt. The remaining live `Tkk` underfit concentrates on the inner packet edge during catch/rematch, roughly where `l - s` lies near `-Rpass`. Adding packet-edge catch transients cuts the live catch underfit substantially.

| fit | live packet underfit | live catch/rematch underfit | global underfit |
|---|---:|---:|---:|
| original proxy | 12.1% | 13.0% | 13.8% |
| targeted Tkk proxy | 9.4% | 9.9% | 13.1% |

Targeted basis improvement: live catch underfit reduced by about **23.9%**; total live packet underfit reduced by about **21.9%**.

## Dominant new transient components

| component | live catch allocation | share of live catch actual |
|---|---:|---:|
| `shift_packet_carrier` | 24 | 37.6% |
| `catch_rematch_transient` | 21.55 | 33.8% |
| `radial_support_edge_shell` | 8.318 | 13.0% |
| `catch_inner_edge_shift_coupled` | 5.654 | 8.9% |
| `catch_outer_packet_edge_transient` | 3.312 | 5.2% |
| `lapse_cushion_sector` | 1.133 | 1.8% |
| `outer_quarantine_jacket` | 0 | 0.0% |
| `cold_core_substrate` | 0 | 0.0% |

## Inner-edge structure

The residual is not a whole-packet catch demand. It is strongest near the inner radial packet boundary. The binned live-catch diagnostic is written to `tkk_live_catch_xi_bins.csv`.

| xi bin | actual burden | underfit burden |
|---|---:|---:|
| `(-0.351, -0.25]` | 10.79 | 1.262 |
| `(-0.25, -0.15]` | 8.308 | 0.5737 |
| `(-0.15, -0.05]` | 8.311 | 0.7998 |
| `(-0.05, 0.05]` | 8.989 | 0.9679 |
| `(0.05, 0.15]` | 8.77 | 0.936 |
| `(0.15, 0.25]` | 8.757 | 0.933 |
| `(0.25, 0.35]` | 9.92 | 0.8563 |

## Interpretation

This supports a more precise source story: the freeze candidate needs a **localized inner-edge catch/rematch transient** in the radial null channel. The transient should live on the packet-facing catch boundary, not across the whole rail and not in reset/decompression.

Design implication: do not solve this by adding a broad global exotic layer. The better target is a narrow catch-edge source or geometry modifier tied to the locked-lead handoff.

## Geometry-side implication

Because the residual is edge-localized, the next geometry poke should test a small inner-edge catch smoothing/guard layer: soften the negative `l-s` packet boundary during catch/rematch without widening the whole packet or moving the radial support edge further. This is different from uniform `w_th` pushing, which already hit the packet-safety cliff.

## Files

- `tkk_residual_fit_summary.csv`
- `tkk_original_allocations.csv`
- `tkk_targeted_allocations.csv`
- `tkk_residual_stage_region.csv`
- `tkk_top_underfit_points.csv`
- `tkk_live_catch_xi_bins.csv`
- `tkk_point_residuals.csv`
- `tkk_residual_proxy_fit.py`