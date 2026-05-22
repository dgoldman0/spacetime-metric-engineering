# Stage 2 beta075 endpoint source-class screen

Status: first physical-source class checkpoint completed.

## Purpose

This screen moves one rung above the frozen endpoint-J effective source model. It asks which physical source class is algebraically compatible with the frozen endpoint stress, before attempting a full matter-action or field-equation construction.

Inputs:

```text
baseline freeze:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_j_freeze_source_model_rematch_w6_t1p5

dense freeze:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_j_freeze_source_model_rematch_w6_t1p5
```

New code:

```text
toolkit/adm_harness_cli/adm_harness/endpoint_j_source_class_screen.py
toolkit/adm_harness_cli/scripts/run_endpoint_j_source_class_screen.py
toolkit/adm_harness_cli/tests/test_endpoint_j_source_class_screen.py
```

Outputs:

```text
baseline:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_j_source_class_screen_freeze_rematch_w6_t1p5

dense:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_j_source_class_screen_freeze_rematch_w6_t1p5
```

## Method

For each frozen endpoint-J source row, classify the radial stress block

```text
rho, p_l, j_l
```

by the boost-diagonalization discriminant:

```text
D = (rho + p_l)^2 - 4 j_l^2
```

Interpretation:

- `D > 0`: Type-I / boost-diagonalizable radial block,
- `D = 0`: null boundary,
- `D < 0`: flux-dominant Type-IV block.

The screen also tests rough single-field compatibility:

- canonical scalar compatibility,
- phantom scalar compatibility,
- ordinary Type-I anisotropic heat-flux compatibility,
- regulated anisotropic heat/current medium compatibility.

The regulated model estimates the minimal finite `rho+p_l` cushion needed to make the radial block Type-I:

```text
minimal regulator = max(0, 2 |j_l| - |rho + p_l|)
```

This is not yet a field-equation solve. It is the algebraic construction test that tells us whether the frozen source asks for an ordinary anisotropic medium, a small regulated current medium, or a broader multi-field/effective-potential class.

## Classifier Result

Decision table:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| recommended model class | regulated anisotropic heat/current medium | regulated anisotropic heat/current medium |
| ordinary Type-I anisotropic pass | `false` | `false` |
| regulated anisotropic pass | `true` | `true` |
| single scalar ruled out | `true` | `true` |
| live rows | `0` | `0` |
| Type-IV source-burden fraction | `0.251505` | `0.258979` |
| regulator/source burden ratio | `0.037723` | `0.039030` |

Read: an ordinary anisotropic fluid alone is too narrow because roughly a quarter of the frozen source burden is flux-dominant by the radial block. But the amount of finite regulator needed to restore a Type-I radial block is small, stable, and non-live.

## Assignment Summary

Total endpoint-J source:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| rows | `7,188` | `28,359` |
| Type-I volume fraction | `0.901118` | `0.888047` |
| Type-IV volume fraction | `0.098882` | `0.111253` |
| Type-IV source-burden fraction | `0.251505` | `0.258979` |
| canonical scalar volume fraction | `0.379515` | `0.335594` |
| phantom scalar volume fraction | `0.382312` | `0.407455` |
| regulator/source burden ratio | `0.037723` | `0.039030` |
| peak regulator density | `0.022435` | `0.023392` |
| p99 regulator density | `0.016790` | `0.017314` |

Reset cap:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| Type-I volume fraction | `0.885287` | `0.888751` |
| Type-IV source-burden fraction | `0.278067` | `0.276963` |
| regulator/source burden ratio | `0.042536` | `0.042708` |
| peak regulator density | `0.022435` | `0.023392` |

Support edge:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| Type-I volume fraction | `0.902819` | `0.887977` |
| Type-IV source-burden fraction | `0.161288` | `0.192758` |
| regulator/source burden ratio | `0.021372` | `0.025487` |
| peak regulator density | `0.008559` | `0.008777` |

## Model-Class Read

Single canonical scalar fails: only about `0.34-0.38` of endpoint volume is compatible with the canonical scalar algebra.

Single phantom scalar fails: only about `0.38-0.41` of endpoint volume is compatible with the phantom scalar algebra.

Ordinary Type-I anisotropic heat flux fails as a complete model: most volume is Type-I, but the Type-IV burden fraction is too large to ignore.

Regulated anisotropic heat/current medium passes this first screen: the regulator needed to make the source boost-diagonalizable is small, stable under dense refinement, finite-support, and non-live.

## Feasibility Implication

The physical model class is now identified more sharply:

```text
regulated anisotropic heat/current medium
```

with a possible multi-field/effective-potential fallback if a later field-equation solve cannot realize the regulator.

This is better than where we were before the screen. We do not need to guess among scalar, fluid, vector, or arbitrary effective-potential classes. Scalar-only is ruled out; ordinary anisotropic fluid alone is too narrow; a regulated anisotropic heat/current medium is the first viable physical construction target.

## Remaining Boundary

This screen does not prove a full matter model. The next rung, if needed, is a field-equation construction for the regulated anisotropic heat/current medium: choose variables and constitutive laws that produce the frozen `rho, p_l, j_l, pOmega` plus the small regulator while satisfying local conservation constraints.

Do not reopen endpoint-J effective-source freeze unless that field-equation construction reveals a new incompatibility.
