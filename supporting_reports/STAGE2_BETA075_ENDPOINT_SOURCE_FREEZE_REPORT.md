# Stage 2 beta075 endpoint source freeze report

Status: endpoint-J source freeze candidate accepted for the beta075 repaired lead.

## Freeze Decision

Freeze the beta075 repaired endpoint-source design around:

- repaired lead: `rematch_w6_t1p5`
- reset-cap source family: bounded structured endpoint-J body
- support-edge source family: finite support-edge closure component
- dense validation mesh: `377x241`

The active endpoint-J source risk was reset-cap coefficient growth in the dense structured fit. That risk resolves as a model-selection issue: the high coefficients came from allowing edge-tail counterterms in the reset-cap family. A bounded no-tail reset-cap body stays accurate enough, non-live, broad, and coefficient-stable across baseline and dense meshes.

This freeze does not claim a matter Lagrangian or global theorem. It freezes the effective endpoint-J source realization as viable and constrainable for the repaired beta075 prescribed-metric design.

## Freeze Source Model

Reset-cap bounded structured source:

```text
mode_count = 4
s_centers = 8
l_centers = 6
width_multiplier = 0.45
ridge = 1e-6
edge_tail_count = 0
```

Support-edge closure component:

```text
mode_count = 1
center_count = 6
width_multiplier = 0.85
ridge = 1e-6
conservation_weight = 0.0
angular_weight = 0.25
```

Output roots:

```text
baseline:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/
  endpoint_j_structured_source_freeze_reset_bounded_rematch_w6_t1p5
  endpoint_j_freeze_source_model_rematch_w6_t1p5

dense:
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/
  endpoint_j_structured_source_freeze_reset_bounded_rematch_w6_t1p5
  endpoint_j_freeze_source_model_rematch_w6_t1p5
```

## Freeze Gates

The freeze candidate was judged against these gates:

- endpoint J remains entirely non-live,
- reset-cap selected-null ratio stays below `1.05`,
- reset-cap current ratio stays below `1.18`,
- reset-cap pOmega ratio stays between `0.90` and `1.08`,
- reset-cap max coefficient stays below `0.15`,
- reset-cap coefficient scale is stable from baseline to dense,
- support-edge closure remains finite-width and low-coupling,
- support-edge conservation residual remains finite-spread, not singular,
- dense source ledger remains live-clean.

## Reset-Cap Result

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| rows | `6,536` | `25,769` |
| fit selected ratio | `1.014940` | `1.016476` |
| fit current ratio | `1.147008` | `1.158275` |
| fit pOmega ratio | `0.935034` | `0.938630` |
| live fit rows | `0` | `0` |
| max coefficient | `0.091883` | `0.093333` |
| coefficient L1 | `2.259648` | `2.414477` |
| coefficient L2 | `0.248594` | `0.254249` |
| burden-weighted residual norm | `0.010071` | `0.005157` |
| peak residual norm | `0.052803` | `0.031618` |

Read: reset-cap is now bounded and stable. Dense refinement does not grow the maximum coefficient, does not introduce live leakage, and improves the conservation residual proxy. The model gives up some pointwise current interpolation accuracy relative to the unconstrained edge-tail fit, but that is the correct freeze trade: bounded support and stable coupling over local polish.

Component normalized L1 errors are also stable:

| component | baseline | dense |
| --- | ---: | ---: |
| rho | `0.070879` | `0.070840` |
| p_l | `0.359409` | `0.367983` |
| j_l | `0.664642` | `0.656715` |
| pOmega | `0.551751` | `0.536966` |

These are not exact pointwise matter fits. They are effective finite-family source fits with stable integrated burden and conservation behavior.

## Support-Edge Result

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| support rows | `652` | `2,590` |
| closure fit selected ratio | `1.196216` | `1.203337` |
| closure fit current ratio | `1.194992` | `1.180779` |
| closure fit pOmega ratio | `1.131519` | `1.068720` |
| live fit rows | `0` | `0` |
| max closure coefficient | `0.000154` | `0.002203` |
| closure coefficient L1 | `0.000625` | `0.004915` |
| sigma_s | `0.435173` | `0.441390` |
| sigma_l | `0.595000` | `0.595000` |
| peak support-edge residual norm | `2.026101` | `2.837687` |

Read: the all-in freeze candidate keeps the support-edge closure finite, non-live, and low-coupling. The dense closure coefficient is larger than the baseline coefficient, but it remains absolutely tiny and below the freeze coupling budget. The earlier dedicated support-edge dense rung remains the stronger support-specific evidence: same closure family, max coefficient `0.001114 -> 0.000846`, and peak residual norm `2.732 -> 2.664`. This freeze run shows the support closure still remains viable even when paired with the bounded reset-cap body.

## Source-Ledger And Dense Stability

Dense source regeneration:

- rows: `90,857`
- positive live packet norm count: `0`
- max live packet norm: `-6.333723`

Dense endpoint-J intermediate grammar:

- endpoint-J live rows: `0`
- support-edge assignment rows: `2,590`
- reset-cap assignment rows: `25,769`

This rules out the two main failure modes we were worried about here: live leakage and hidden singular support. The endpoint-J source population remains non-live and finite under dense sampling.

## Feasibility Interpretation

The endpoint-J source risk is resolved enough to freeze the beta075 repaired design. The support-edge closure is no longer an open phenomenon; it is a finite missing component. The reset-cap risk is now constrained by choosing a broad no-tail body rather than the unconstrained edge-tail fit that produced coefficient growth.

The freeze design is viable as an effective-source construction: finite support, bounded coefficients, stable dense/coarse behavior, and no live leakage. The remaining caveat is category-level, not local-design-level: this is still not a physical matter model or a covariant conservation proof. It is a source-realization freeze for the prescribed-metric feasibility track.

## Stop Rule

Do not keep incrementally retesting endpoint-J unless a new failure mode appears. The next project movement should be consolidation and freeze packaging, or a higher-level matter/source construction rung if the goal shifts from effective-source feasibility to physical matter realization.
