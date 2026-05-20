# Stage II Source Picture: Entry-Gated Wide4

## Summary

The entry-gated `wide4_start_m1p40` design has a coherent source-placement picture at the demanded-source ledger level. The entry service gate separates setup support from live packet scoring, the live packet norm is clean on the extended high-resolution ledger, and the full-grid decomposition assigns the dominant source burdens to support-plant roles rather than to the live packet corridor.

The result is not a matter-model solution. It is an algebraic demanded-source decomposition that sits between top-point diagnostics and a physical source solve. Its value is that it tests whether the current design has a stable, representative source-role structure across the whole ledger.

## Input Design

Representative branch:

```text
label = wide4_start_m1p40
live_packet_start = -1.40
entry_carve = 0.75
entry_width_multiplier = 4.8
catch_carve = 0.15
catch_width_multiplier = 3.4
edge_carve = 0.16
edge_width_multiplier = 7.2
null_cushion_log_gain = -0.07
grid = 101 x 151 on s [-1.50, 2.40], l [-4.20, 4.20]
```

Ledger input:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_compact_entry_start_candidate_ledger_101x151/wide4_start_m1p40/
```

The demanded-source ledger has zero positive live packet-norm samples and maximum live packet norm about `-1.242423`. The corresponding hard-affine SNEC run has zero raw and zero scoreable benchmark violations at `tau = 2.0`, `3.0`, and `4.0`; the tightest scoreable margin is about `0.01494` at `tau = 4.0`.

## Artifacts

Top-40 source-decomposition map:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_source_decomposition_compact_entry_start_101x151/
```

Full-grid source-decomposition map:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_source_decomposition_compact_entry_start_101x151_full_grid/
```

Easy and moderate check outputs:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_source_decomposition_compact_entry_start_101x151_full_grid/checks/
```

The full-grid decomposition uses `limit_per_channel = 20000`, so every point in the `101 x 151` point ledger is included for each of the four principal channels. It contains `61,004` detail rows and `230` summary rows.

## Channel Summary

| Channel | Full-grid burden | Live fraction | Primary assignment |
| --- | ---: | ---: | --- |
| `neg_Tkk_radial` | `483.808454` | `2.889%` | infrastructure radial-null support |
| `abs_p_l` | `79.388610` | `0.787%` | core/support radial pressure balance |
| `abs_pOmega` | `11.459660` | `14.706%` | distributed/support-edge angular capacity plus live handoff capacity |
| `abs_j_l` | `0.738850` | `11.976%` | reset/background current plus live handoff current |

The dominant burden is radial-null infrastructure support. Radial pressure is also almost entirely an infrastructure balance role. Angular pressure is the largest live-facing source sector. Current is small in absolute size and mostly distributed through reset/background roles.

## Source-Role Decomposition

`neg_Tkk_radial` is support-plant dominated. `95.665%` of the channel burden maps to `infrastructure_radial_null_support`, concentrated in non-live `core_throat` and `support_edge` regions. The live packet radial-null share is `2.889%` and is carried by packet-in-support rows rather than positive packet-norm conditions.

`abs_p_l` is the cleanest infrastructure sector. `77.648%` maps to `core_radial_pressure_balance`, `20.230%` maps to `support_edge_radial_pressure_balance`, and only `0.787%` is live.

`abs_pOmega` is the broadest sector. `63.257%` maps to distributed angular pressure, `22.037%` to support-edge angular capacity, and `14.706%` to live angular-pressure capacity. This is the main live-facing channel in the current source picture.

`abs_j_l` is small but diffuse. `82.435%` maps to reset/background current, `11.976%` to live shift current or momentum flux, and `5.589%` to catch/rematch infrastructure current. The top-point view overstated the live/current-entry emphasis because integrated current burden is spread through reset/background rows.

## Top-K Versus Full Grid

The top-40 decomposition is useful as a peak locator, but it is not an integrated source picture. Top-40 rows capture only:

| Channel | Top-40 share of full burden |
| --- | ---: |
| `neg_Tkk_radial` | `6.328%` |
| `abs_p_l` | `2.747%` |
| `abs_pOmega` | `10.439%` |
| `abs_j_l` | `2.607%` |

The concentration curves show that source claims should be made from the full-grid decomposition, not from peak rows alone. The top `2,500` rows capture about `87.0%` of radial-null burden, `90.6%` of radial-pressure burden, `61.9%` of angular-pressure burden, and `70.9%` of current burden. The angular and current sectors are therefore broader and less peak-dominated than the radial sectors.

## Patch Continuity

Connected-component checks were run on cumulative channel-burden cores at `50%`, `80%`, and `95%` mass using 4-neighbor connectivity in the `(s,l)` grid. This is still postprocessing of the existing ledger, not a new source solve.

Radial pressure is the most coherent sector. At `95%` mass, two dominant `core_throat` patches carry about `71.8%` and `23.2%` of the channel, with essentially no live burden. This supports treating radial pressure as a stable core/support balance role.

Radial-null burden is coherent but two-lobed. At `95%` mass, two infrastructure patches carry about `61.8%` and `33.1%` of the channel. Their live fractions are about `2.3%` and `1.9%`, so the radial-null source picture remains support-plant dominated.

Angular pressure is broad. At `95%` mass, one connected support/outer-shell patch carries about `94.9%` of the channel and has about `15.3%` live fraction. This supports interpreting angular pressure as a broad support-capacity and live-handoff sector rather than a localized packet failure.

Current is small and diffuse. At `95%` mass, the largest merged current patch carries about `53.0%` of the channel with about `20.6%` live fraction, and the next patch carries about `40.9%` with no live fraction. This is compatible with reset/background current plus smaller live handoff current.

## Comparison With Earlier Promoted Pair

A fair full-grid comparison was generated for the older promoted-pair track using the same decomposition method:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_source_decomposition_promoted_pair_61x83_full_grid/
```

Raw totals are not directly comparable because the entry-gated artifact uses a larger `101 x 151` extended domain while the promoted pair uses `61 x 83` ledgers. The useful comparison is normalized live fraction:

| Design | `neg_Tkk_radial` live | `abs_p_l` live | `abs_pOmega` live | `abs_j_l` live |
| --- | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | `2.385%` | `0.833%` | `21.560%` | `18.825%` |
| `wide4_radius205` | `1.824%` | `0.627%` | `28.279%` | `16.986%` |
| `wide4_start_m1p40` | `2.889%` | `0.787%` | `14.706%` | `11.976%` |

The entry-gated design improves the live angular-pressure and live current fractions relative to the older compact promoted track. Radial pressure is comparable. Live radial-null fraction is slightly higher than the older promoted pair, but it remains small and is paired with clean live packet-norm and hard-affine SNEC behavior.

## Interpretation

The current design looks better as a representative source-placement design than the earlier promoted compact branch in the channels that were most visibly live-facing: angular pressure and current. It is not a claim that the total demanded source is smaller in every raw ledger number, because the domain and grid differ. It is a claim that the source-role structure is cleaner and more representative of the intended architecture.

The active-rail source picture at this checkpoint is:

```text
protected live packet corridor
  coupled to
support-plant radial-null infrastructure
  plus
core/support radial-pressure balance
  plus
broad angular-capacity and live handoff sector
  plus
small reset/background and live handoff current sector
```

The entry gate is doing the intended accounting work. It keeps pre-entry setup in infrastructure accounting and starts live scoring inside the supported corridor. The remaining live source-facing burden is not a positive packet-norm failure; it is a modest angular/current handoff sector plus a small radial-null fraction.

## Cost Classification

The checks in this report are easy to moderate:

```text
Easy:
  full-grid aggregation, live fractions, source-role summaries,
  stage/region summaries, top-k versus full-grid concentration.

Moderate:
  connected-component patch continuity,
  full-grid comparison against existing promoted-pair ledgers.
```

High-computation work starts when the demanded-source ledger itself is rebuilt or when SNEC/component screens are rerun:

```text
High computation:
  new Stage II candidate ledgers,
  regenerated demanded-source ledgers at high resolution,
  hard-affine SNEC sweeps,
  tau/boundary ladders,
  component-source ledgers,
  new parameter screens.
```

## Decision

The easy and moderate checks are sufficient to use the entry-gated `wide4_start_m1p40` decomposition as the current representative source picture. The next rigor step is source-sector closure: fit the full-grid burden to a small set of constrained source sectors and measure residuals. That remains below a full matter-model solve, but it is more rigorous than algebraic role labeling.
