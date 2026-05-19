# Stage II Component Algebra Ledger: Promoted Pair

## Purpose

This ledger reads the full-role component-source assignment and asks what each toy source role is algebraically asking for.

Input component run:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_source_promoted_pair_61x83_full_roles/
```

Output directory:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_algebra_promoted_pair_61x83_full_roles/
```

This is still not a physical matter solve. It is a bridge between source-role assignment and a possible physical source ansatz. It summarizes signs, cancellation proxies, null-branch behavior, component overlap, and the remaining current residual.

## Main Algebraic Picture

The component roles split into three source sectors:

```text
infrastructure support sector: A/B/G;
live handoff trim sector: C/E/F;
current relaxation sector: D plus a possible unresolved H.
```

This is the important result. The promoted pair does not look like one scalar source with one profile. It looks like a coupled support plant plus a packet-side handoff package.

## Infrastructure Sector: A/B/G

Components `A` and `B` are highly compatible.

| candidate | component | mean rho | mean p_l | null cancellation | pressure cancel | dominant branch |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `compact7_wide4_edge160` | A | 0.00714 | -0.00718 | 0.9963 | 0.9945 | plus |
| `compact7_wide4_edge160` | B | 0.00849 | -0.00848 | 0.9995 | 0.9992 | plus |
| `wide4_radius205` | A | 0.00520 | -0.00524 | 0.9957 | 0.9938 | plus |
| `wide4_radius205` | B | 0.00606 | -0.00605 | 0.9996 | 0.9992 | plus |

Interpretation:

```text
A and B are both rho ≈ -p_l support-sector jobs;
the radial-null role is cancellation/branch sensitive;
the pressure-balance role is the cleanest rho/p_l cancellation role.
```

Component `G` is different. It is angular-capacity dominated:

| candidate | G mean rho | G mean p_l | G mean pOmega | angular dominance |
| --- | ---: | ---: | ---: | ---: |
| `compact7_wide4_edge160` | -0.00458 | -0.00833 | 0.04082 | 2.4507 |
| `wide4_radius205` | -0.00172 | -0.00641 | 0.02797 | 2.6575 |

So `G` should not be collapsed into A/B. It is a broad angular/throat-capacity stress role that overlaps the same infrastructure points while paying a different channel.

## Live Handoff Sector: C/E/F

The live handoff package is algebraically coherent.

| candidate | component | burden | mean rho | mean p_l | mean pOmega | null cancellation | branch |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `compact7_wide4_edge160` | C | 1.2863 | 0.00881 | -0.00876 | 0.05119 | 0.9444 | minus |
| `compact7_wide4_edge160` | E | 8.4975 | 0.00782 | -0.00993 | 0.02341 | 0.9591 | minus |
| `compact7_wide4_edge160` | F | 0.4416 | 0.00836 | -0.00892 | 0.01952 | 0.9594 | minus |
| `wide4_radius205` | C | 1.6917 | 0.00649 | -0.00644 | 0.05150 | 0.9450 | minus |
| `wide4_radius205` | E | 9.1380 | 0.00580 | -0.00717 | 0.02161 | 0.9618 | minus |
| `wide4_radius205` | F | 0.4732 | 0.00619 | -0.00647 | 0.01816 | 0.9614 | minus |

Interpretation:

```text
C/E/F should probably be one coupled live handoff source package;
E is the largest live trim burden;
F is smaller, but it is the Stage I pressure problem in source form;
the live package selects the opposite null branch from the infrastructure A/B sector.
```

That branch difference matters for the next physical ansatz. A matter model that pays A/B may not automatically pay C/E/F.

## Overlap

The corrected overlap matrix confirms that the source roles are not spatially disjoint.

Key complete or near-complete overlaps:

```text
A overlaps G at all A points;
B overlaps G at all B points;
C overlaps F at all C points;
E overlaps C at all E points;
F overlaps E on about 80 percent of F burden;
B overlaps A on about 96 percent of B burden.
```

Interpretation:

```text
the support plant is coupled;
the live handoff trim is coupled;
do not model these as isolated, non-overlapping matter sheets.
```

## Current Residual

Radial current remains the under-modeled channel after A-G.

| candidate | unassigned current burden | largest residual location |
| --- | ---: | --- |
| `compact7_wide4_edge160` | 0.2046 | `reset_decompression / outer_quarantine_shell` |
| `wide4_radius205` | 0.2038 | `post_release_buffer / support_edge` |

The residual is non-live and spread across reset, post-release, catch, support-edge, core-throat, and outer-quarantine regions. It is not a live packet blocker.

The top compact residuals are:

```text
reset_decompression / outer_quarantine_shell: 0.0352
reset_decompression / core_throat:            0.0295
post_release_buffer / support_edge:           0.0271
post_release_buffer / outer_quarantine_shell: 0.0245
```

The top radius205 residuals are:

```text
post_release_buffer / support_edge:           0.0412
reset_decompression / core_throat:            0.0370
reset_decompression / outer_quarantine_shell: 0.0214
reset_decompression / packet_in_support:      0.0178
```

## Decision

Do not run the hard SNEC calculation as the immediate next step. The algebra ledger says the source-sector assumptions are still too oracle-like.

Do not add a large H as a major role yet. The current residual suggests a possible non-live current-relaxation role, but it is diffuse and not the next physical blocker.

The best next step is to choose a first composite physical source ansatz at the sector level:

```text
A/B: anisotropic infrastructure support with rho ≈ -p_l cancellation;
G: angular-capacity stress coupled to the support plant;
C/E/F: coupled live handoff trim with angular/current, radial-null, and radial-pressure pieces;
D/H?: non-live current relaxation, initially kept diagnostic.
```

Then use that ansatz to decide whether H needs to be promoted into a real source component. The hard affine SNEC calculation should come after the component sectors are less purely oracle-defined.
