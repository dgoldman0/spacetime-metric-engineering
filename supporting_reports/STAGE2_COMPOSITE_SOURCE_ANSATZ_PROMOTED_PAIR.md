# Stage II Composite Source Ansatz Screen: Promoted Pair

## Purpose

This screen is the first reduced physical-source bridge after the component-source and component-algebra ledgers.

It tests whether the Stage II promoted pair can be represented by a small effective anisotropic source package rather than by one scalar source.

Input component assignment:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_source_promoted_pair_61x83_full_roles/
```

Output directories:

```text
baseline diagnostic:
toolkit/adm_harness_cli/runs/stage2_external/stage2_composite_source_ansatz_promoted_pair_61x83_v0/

H-promoted fit:
toolkit/adm_harness_cli/runs/stage2_external/stage2_composite_source_ansatz_promoted_pair_61x83_with_H/
```

This is not a field-equation solve, conservation proof, or SNEC certification. It is a constrained algebraic fit asking whether the component roles can be grouped into a plausible effective anisotropic source package.

## Source Template

The fitted stress template is the orthonormal anisotropic form:

```text
T_hat ~ rho u u
      + p_l e_l e_l
      + pOmega (e_theta e_theta + e_phi e_phi)
      + j_l (u e_l + e_l u)
```

The baseline diagnostic groups components into:

```text
infrastructure radial support: A/B
infrastructure angular capacity: G
live handoff trim: C/E/F
reset current sink: D
residual current diagnostic: unassigned abs_j_l
```

The H-promoted fit keeps the same sectors and promotes the residual-current diagnostic into:

```text
H: non-live distributed current-relaxation sector
```

## Baseline Sector Fit

All required baseline sectors pass the first primary sign/ratio constraints.

| candidate | sector | burden | key fit |
| --- | --- | ---: | --- |
| `compact7_wide4_edge160` | infrastructure radial support | 382.25 | `p_l/rho = -1.002`, `j_l/rho = -0.00068` |
| `compact7_wide4_edge160` | angular capacity | 4.25 | `rho/pOmega = -0.146`, `p_l/pOmega = -0.142` |
| `compact7_wide4_edge160` | live handoff trim | 10.23 | `p_l/rho = -1.148`, `pOmega/rho = 3.095`, `j_l/rho = 0.037` |
| `wide4_radius205` | infrastructure radial support | 544.88 | `p_l/rho = -1.002`, `j_l/rho = -0.00058` |
| `wide4_radius205` | angular capacity | 3.88 | `rho/pOmega = -0.106`, `p_l/pOmega = -0.126` |
| `wide4_radius205` | live handoff trim | 11.30 | `p_l/rho = -1.115`, `pOmega/rho = 4.029`, `j_l/rho = 0.023` |

Interpretation:

```text
A/B really do look like one radial-tension infrastructure support sector.
G is compatible with a separate pOmega-dominant angular jacket.
C/E/F look like one live handoff source package, not three independent fluids.
```

The compact and radius-broadened candidates tell the same qualitative story. The radius-broadened comparator asks for a larger infrastructure support sector and a stronger live angular ratio.

## H Promotion

The baseline ansatz changes the status of `H`.

| candidate | residual current burden | D current burden | residual/D ratio | promote H? |
| --- | ---: | ---: | ---: | --- |
| `compact7_wide4_edge160` | 0.2046 | 0.0478 | 4.28 | yes |
| `wide4_radius205` | 0.2038 | 0.0783 | 2.60 | yes |

The component algebra ledger showed that current residual is diffuse and non-live, so it was not the immediate packet blocker. But after fitting a sector-level source package, the reset current sink `D` is too small to represent the remaining current burden. That residual should not stay as an unassigned bucket.

The H-promoted run therefore treats the residual as a non-live distributed current-relaxation sector.

| candidate | H burden | H live fraction | H current dominance | `rho/j_l` | `p_l/j_l` | `pOmega/j_l` | H constraint |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `compact7_wide4_edge160` | 0.2046 | 0.000 | 4.371 | 0.115 | -0.126 | 0.082 | pass |
| `wide4_radius205` | 0.2038 | 0.000 | 3.134 | 0.173 | -0.056 | -0.044 | pass |

Both H fits are non-live and current-dominant. The current-relaxation sector is larger than D, so D should be read as a localized reset/support-edge sink while H is the distributed background current-relaxation role.

## Decision

The H-promoted fit passes the required sector constraints for both candidates:

| candidate | required sectors pass | residual current after H | H burden | current-relaxation/D ratio |
| --- | --- | ---: | ---: | ---: |
| `compact7_wide4_edge160` | yes | 0.0000 | 0.2046 | 4.28 |
| `wide4_radius205` | yes | 0.0000 | 0.2038 | 2.60 |

This is a positive result for the composite-source direction.

The failed scalar branch asked one field to be the whole plant. The effective anisotropic screen instead finds that the demanded source is compatible with:

```text
radial-tension infrastructure support;
angular-capacity infrastructure jacket;
coupled live handoff trim;
localized reset current sink;
distributed non-live current relaxation.
```

The compact candidate remains the better source target. It requires less infrastructure radial support than the radius-broadened comparator and lower live angular amplification in the handoff sector.

## SNEC Readiness

The H-promoted ansatz makes the source-sector picture cleaner, but it still does not certify SNEC.

Reasons:

```text
the fit is algebraic, not derived from a conserved stress tensor;
sector amplitudes are not generated by fields or a Lagrangian;
SNEC still needs physical smearing, null geodesics, and source-sector assumptions.
```

The right next screen is now the hard affine SNEC calculation on the compact promoted target, with the H-promoted source-sector assumptions carried explicitly.
