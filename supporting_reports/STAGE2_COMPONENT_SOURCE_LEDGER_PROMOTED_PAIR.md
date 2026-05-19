# Stage II Component-Source Ledger: Promoted Pair

## Purpose

This toy Stage II ledger tests whether the demanded source for the promoted pair can be partitioned into role-specific source components before choosing detailed physical matter models.

Mapped candidates:

```text
compact7_wide4_edge160
wide4_radius205
```

Run directory:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_source_promoted_pair_61x83_full_roles/
```

This is not a physical source solve. It is an oracle assignment of demanded-source burden by channel, stage, region, and live-packet status. Its job is to test whether the active-rail support plant has a coherent source-role decomposition.

## Component Roles

The full toy role set is:

```text
A: infrastructure radial-null support
   non-live core_throat/support_edge radial-null rows

B: core radial-pressure balance
   non-live core_throat radial-pressure rows

C: live handoff angular/current handling
   live packet_in_support angular-pressure and radial-current rows

D: reset/support-edge current sink
   non-live reset_decompression/support_edge radial-current rows

E: live handoff radial-null trim
   live packet_in_support radial-null rows

F: live handoff radial-pressure trim
   live packet_in_support radial-pressure rows

G: infrastructure angular-capacity support
   non-live support-plant angular-pressure rows
```

The important distinction is not spatial disjointness. Several components can share grid points while paying different source channels. The question is whether the demanded burden separates by role without assigning the hard infrastructure support plant to the live packet corridor.

## Channel Coverage

Full-role channel coverage:

| candidate | radial-null | radial pressure | radial current | angular pressure |
| --- | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | 0.9901 | 0.7244 | 0.3419 | 0.9627 |
| `wide4_radius205` | 0.9960 | 0.7345 | 0.4003 | 0.9536 |

The role set now captures the major radial-null, pressure, and angular-capacity jobs. Radial current remains the least-covered channel because the only non-live current role included here is the reset/support-edge sink `D`.

## Component Burdens

| candidate | A null | B pressure | C current | C angular | D current | E null | F pressure | G angular |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | 344.29 | 37.96 | 0.0585 | 1.2278 | 0.0478 | 8.4975 | 0.4416 | 4.2544 |
| `wide4_radius205` | 489.91 | 54.97 | 0.0577 | 1.6340 | 0.0783 | 9.1380 | 0.4732 | 3.8758 |

The radius-broadened comparator carries substantially larger infrastructure radial-null and core-pressure assignments. It also moves more reset/support-edge current into `D`, while charging the live angular handoff component `C`.

## Live Packet Gate

With `C`, `E`, and `F` included, all live packet demanded-source channels in this toy assignment have explicit live handoff roles:

| candidate | live radial-null residual | live radial-pressure residual | live current residual | live angular residual |
| --- | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | 0.0 | 0.0 | 0.0 | 0.0 |
| `wide4_radius205` | 0.0 | 0.0 | 0.0 | 0.0 |

This should not be read as physical closure. It means the live packet burden is no longer a mystery category in the demanded-source ledger. It is represented by a coupled handoff package:

```text
C: angular/current;
E: radial-null;
F: radial-pressure.
```

The `F` component matters because it is exactly the Stage I pressure problem resurfacing in source-assignment language:

| candidate | F live pressure burden | max live `p_l` demand |
| --- | ---: | ---: |
| `compact7_wide4_edge160` | 0.4416 | 0.0198 |
| `wide4_radius205` | 0.4732 | 0.0141 |

So the compact branch did not make live radial pressure disappear. It made it small, localized to the packet handoff role, and explicit.

## Contamination And Overlap

Hard infrastructure components stayed out of the live packet:

| candidate | hard-component live contamination fraction |
| --- | ---: |
| `compact7_wide4_edge160` | 0.0 |
| `wide4_radius205` | 0.0 |

Multi-component overlap is very high after adding `G`:

| candidate | multi-component burden fraction | live multi-component burden |
| --- | ---: | ---: |
| `compact7_wide4_edge160` | 0.9921 | 10.2253 |
| `wide4_radius205` | 0.9963 | 11.3030 |

This does not mean the role assignment failed. `G` is a broad non-live angular-capacity role across the support plant, so it naturally overlaps the infrastructure radial-null and pressure-balance roles at many grid points. The source model should therefore be treated as a coupled support plant, not as isolated matter layers.

## Remaining Unassigned Burden

The main residuals after the full role set are:

```text
non-live radial current outside reset/support-edge D;
non-live radial pressure outside core-throat B;
small non-live radial-null residual outside A/E;
small non-live angular residual outside C/G.
```

The largest deliberately incomplete channel is radial current:

| candidate | current coverage | current unassigned burden |
| --- | ---: | ---: |
| `compact7_wide4_edge160` | 0.3419 | 0.2046 |
| `wide4_radius205` | 0.4003 | 0.2038 |

This suggests a possible later current-distribution role, but it is not the immediate live-packet blocker.

## Interpretation

The full component-source ledger supports the composite source-plant direction.

Strong findings:

```text
the hard radial-null support role is infrastructure-side;
core radial-pressure balance is a separate infrastructure role;
live packet burden is representable as C/E/F handoff trims;
infrastructure angular capacity is a real broad support-plant role;
hard infrastructure roles do not contaminate the live packet.
```

Weak findings:

```text
the role set is an oracle partition, not a physical stress tensor;
the support plant is highly coupled rather than spatially disjoint;
F confirms the stubborn Stage I live p_l issue instead of solving it physically;
radial current remains under-modeled outside the reset/support-edge sink.
```

The practical implication is that the next physical source model should not be asked to produce a single scalar payer. It needs at least:

```text
an infrastructure radial-null/pressure support sector: A/B;
a live handoff trim sector: C/E/F;
an angular-capacity support sector: G;
and probably a current-sector refinement if radial current becomes the next limiting channel.
```

The compact candidate remains the cleaner source-target despite its live pressure trim, because the radius-broadened comparator increases the infrastructure radial-null and pressure assignments and charges the live angular handoff burden.
