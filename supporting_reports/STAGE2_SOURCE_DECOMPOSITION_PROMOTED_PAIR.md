# Stage II Source-Decomposition Map: Promoted Pair

## Purpose

After the simple scalar kill screen and fixed-metric localized scalar solve failed to pay the radial-null bill, this pass asks what the demanded source is asking for by role rather than by one-source fitting.

The mapped candidates are:

```text
compact7_wide4_edge160
wide4_radius205
```

The map classifies the top demanded rows by:

```text
channel;
stage and region;
live-packet status;
algebraic signature;
likely source role.
```

This is not a matter-model solve. It is a source-assignment map for choosing component source families.

## Run

Output directory:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_source_decomposition_promoted_pair_61x83/
```

Files:

```text
source_decomposition_detail.csv
source_decomposition_summary.csv
source_decomposition_manifest.json
```

The mapper used the top `40` rows per channel:

```text
neg_Tkk_radial
abs_p_l
abs_j_l
abs_pOmega
```

## Main Finding

The promoted pair decomposes into three different source jobs:

```text
1. infrastructure radial-null support;
2. core radial-pressure balance;
3. live packet handoff angular/current handling.
```

That matches the composite support-plant interpretation. It also explains why the single simple scalar failed: it was asked to supply roles that are separated by both region and algebraic mechanism.

## Radial-Null Support

All top radial-null rows are infrastructure-side:

| candidate | dominant radial-null locations | dominant mechanisms |
| --- | --- | --- |
| `compact7_wide4_edge160` | `catch_rematch/support_edge`, `entry_precatch/core_throat`, `catch_rematch/core_throat` | `rho_p_l` cancellation residual plus current-selected null branch |
| `wide4_radius205` | `catch_rematch/core_throat`, `catch_rematch/support_edge`, `entry_precatch/support_edge`, `entry_precatch/core_throat` | mostly `rho_p_l` cancellation residual, plus current-selected null branch |

Compact split:

```text
catch_rematch / support_edge / cancellation residual: burden 7.80
entry_precatch / core_throat / current-selected:      burden 3.98
catch_rematch / core_throat / current-selected:       burden 3.52
entry_precatch / support_edge / cancellation residual: burden 2.20
```

Radius205 split:

```text
catch_rematch / core_throat / cancellation residual:  burden 8.25
catch_rematch / support_edge / cancellation residual: burden 5.63
entry_precatch / support_edge / cancellation residual: burden 4.75
entry_precatch / core_throat / current-selected:      burden 4.12
```

Interpretation:

```text
radial-null support is not a live packet source job;
it is an infrastructure exotic-support job;
its algebra is cancellation-sensitive and branch-selecting, not simple scalar-gradient shaped.
```

This is the specific source role that the simple scalar did not pay.

## Radial Pressure

Top radial-pressure rows are entirely core-throat pressure-balance rows and non-live:

| candidate | entry/core burden | catch/core burden | mechanism |
| --- | ---: | ---: | --- |
| `compact7_wide4_edge160` | 2.51 | 0.44 | `rho_p_l_pressure_balance` |
| `wide4_radius205` | 2.53 | 0.74 | `rho_p_l_pressure_balance` |

Interpretation:

```text
radial pressure is a core balance component;
it is not the same job as live angular/current handling;
it is also not obviously solved by the scalar profile tested so far.
```

Radius broadening lowers point badness but leaves a larger catch/core pressure-balance burden in the top-row map.

## Angular Pressure

Top angular-pressure rows are mostly live packet handoff rows:

Compact:

```text
catch_rematch / packet_in_support / live: burden 0.139
entry_precatch / packet_in_support / live: burden 0.049
entry_precatch / support_edge / non-live: burden 0.047
```

Radius205:

```text
catch_rematch / packet_in_support / live: burden 0.205
entry_precatch / support_edge / non-live: burden 0.123
entry_precatch / packet_in_support / live: burden 0.040
```

Interpretation:

```text
angular pressure is still primarily a live handoff/capacity job;
radius broadening charges this job, consistent with the topology-support screen;
this is a different source component from radial-null infrastructure support.
```

## Radial Current

Top radial-current rows split between live packet handoff and reset/background support-edge current:

Compact:

```text
catch_rematch / packet_in_support / live: burden 0.00945
reset_decompression / support_edge / non-live: burden 0.00400
entry_precatch / packet_in_support / live: burden 0.00361
```

Radius205:

```text
catch_rematch / packet_in_support / live: burden 0.00817
reset_decompression / support_edge / non-live: burden 0.00803
entry_precatch / packet_in_support / live: burden 0.00196
```

Interpretation:

```text
radial current is a shift/momentum-flux source role;
compact keeps more of this in live catch handoff;
radius205 moves more current burden into reset/support-edge infrastructure.
```

## Source Assignment Implication

The next source model should not be one scalar asked to do everything.

The demanded-source roles look like:

| role | likely source-family requirement |
| --- | --- |
| infrastructure radial-null support | exotic radial-null support component with cancellation/branch control |
| core radial-pressure balance | pressure-balance component coupled to throat/core metric scale |
| live angular pressure | handoff/capacity source or effective anisotropic stress component |
| radial current | shift-sector momentum-flux component |

The simple scalar might still be useful as:

```text
an auxiliary smoothing/timing field;
a subcomponent for angular/current shaping;
a component in a hybrid source assignment.
```

But it should not be treated as the main radial-null payer for this branch.

## Next Step

The highest-value next Stage II test is a component-source ledger rather than a wider scalar search:

```text
1. Define target source roles from this decomposition.
2. Add a toy anisotropic/exotic radial-null component for infrastructure rows only.
3. Add a separate angular/current handoff component for live packet rows.
4. Score whether the composite assignment can cover the demanded ledger without packet contamination.
```

That would test the composite support-plant idea directly, instead of asking one scalar field to play every role.
