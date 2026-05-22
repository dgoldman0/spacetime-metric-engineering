# Stage II Beta075 Support-Edge Closure Component

Date: 2026-05-22

## Summary

This report records the first explicit support-edge endpoint closure component.

The prior structured endpoint source model improved the support-edge source
family but left an edge-tail conservation watch. The new closure component is a
finite correction layered on top of that structured source model. It is fitted
only on the non-live support-edge assignment and is selected against:

```text
component fit error,
selected-null/current/angular overburden,
conservation residual proxy,
coefficient scale.
```

Result: the missing component hypothesis is supported at this rung. A tiny
finite support-edge closure component clears the edge-tail conservation watch on
the repaired lead and on the available local bracket intermediates without live
leakage or large coefficients.

This is still not a physical matter Lagrangian or covariant conservation proof.
It is a more explicit effective source-family component that now needs dense
scaling.

## Artifacts

New harness files:

```text
toolkit/adm_harness_cli/adm_harness/endpoint_j_closure_component.py
toolkit/adm_harness_cli/scripts/run_endpoint_j_closure_component.py
toolkit/adm_harness_cli/tests/test_endpoint_j_closure_component.py
```

Main outputs:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_closure_component_baseline_s15_beta075_p003_mid/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_closure_component_rematch_w6_t1p5/
```

Local bracket outputs:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15_local_bracket/endpoint_j_closure_component_rematch_w5p5_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15_local_bracket/endpoint_j_closure_component_rematch_w6p5_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15_local_bracket/endpoint_j_closure_component_rematch_w6_t1p25/
```

## Repaired Lead Result

For `rematch_w6_t1p5`, the selected closure component uses:

```text
mode_count:          1
center_count:        6
width_multiplier:    0.85
ridge:               1e-6
conservation_weight: 0.0
angular_weight:      0.25
max coefficient:     0.001114
coefficient L1:      0.002425
```

The correction is small but targeted. It improves both support-edge overburden
and the conservation watch:

| model | selected ratio | current ratio | pOmega ratio | peak conservation norm | read |
| --- | ---: | ---: | ---: | ---: | --- |
| structured source | `1.184398` | `1.148680` | `1.153280` | `5.244759` | edge-tail watch |
| plus closure component | `1.174889` | `1.149350` | `1.160453` | `2.732194` | finite-spread proxy |

The support-edge selected-null excess drops modestly. The main win is that the
edge-tail conservation diagnostic clears without any large coefficient.

Component L1 errors do not meaningfully improve:

| component | structured L1 | closure L1 |
| --- | ---: | ---: |
| `rho` | `1.142896` | `1.145984` |
| `p_l` | `1.056870` | `1.060401` |
| `j_l` | `0.537328` | `0.537956` |
| `p_omega` | `1.184691` | `1.195589` |

Interpretation: this component is not a better pointwise interpolator. It is a
small closure term that removes the conservation-tail pathology left by the
structured support-edge source family.

## Bracket Stability

The same fixed closure shape was applied across the available local bracket
intermediate artifacts. It remains stable:

| label | selected ratio | current ratio | pOmega ratio | max coefficient |
| --- | ---: | ---: | ---: | ---: |
| `w5.5/t1.5` | `1.174470` | `1.146553` | `1.142429` | `0.001103` |
| `w6.0/t1.5` | `1.174889` | `1.149350` | `1.160453` | `0.001114` |
| `w6.5/t1.5` | `1.174934` | `1.151046` | `1.177288` | `0.001125` |
| `w6.0/t1.25` | `1.174697` | `1.148893` | `1.160380` | `0.001117` |

And it clears the support-edge conservation watch across the bracket:

| label | volume-weighted residual norm | burden-weighted residual norm | peak residual norm | read |
| --- | ---: | ---: | ---: | --- |
| `w5.5/t1.5` | `0.209043` | `0.067680` | `2.713729` | finite-spread proxy |
| `w6.0/t1.5` | `0.208418` | `0.067426` | `2.732194` | finite-spread proxy |
| `w6.5/t1.5` | `0.208484` | `0.067406` | `2.730269` | finite-spread proxy |
| `w6.0/t1.25` | `0.208251` | `0.067391` | `2.727053` | finite-spread proxy |

Interpretation: this does not look like a one-point fix. The support-edge
closure term is tracking a stable endpoint phenomenon across the local bracket.

## Feasibility Implication

This is the first result that looks like the missing source-model component
rather than another reshaping of the existing generic fit.

The collar revealed a support-edge endpoint shoulder. The structured source
model supplied the finite coupled stress-vector plant. The new closure
component supplies a small conservation-tail correction that removes the
remaining edge-tail watch. Together they form a more coherent endpoint source
model:

```text
reset cap: broad finite plant
support edge: coupled stress-vector plant
closure tail: tiny finite support-edge conservation correction
```

The result is encouraging for physical feasibility, but still bounded. The
component is tiny and stable at this resolution, which argues against immediate
singular-support or extreme-coupling failure. The decisive next test is dense
scaling: the closure coefficient, support width, and conservation residuals
must remain finite as the grid is refined.

## Next Work

Run dense-resolution / stricter structured-source scaling:

```text
1. Rebuild the repaired lead intermediate source artifacts on a denser grid.
2. Re-run structured endpoint source model.
3. Re-run support-edge closure component.
4. Compare coefficient scale, effective support width, selected/current/pOmega
   ratios, and conservation residuals against this s15 result.
5. Only after this remains stable should beta100 or higher service-factor
   robustness become the main branch again.
```

Current status:

```text
missing component: found at this rung;
physical source: not proven;
main risk: dense scaling of the support-edge closure component.
```

## Verification

Ran:

```text
python -m py_compile toolkit/adm_harness_cli/adm_harness/endpoint_j_closure_component.py toolkit/adm_harness_cli/scripts/run_endpoint_j_closure_component.py
PYTHONPATH=toolkit/adm_harness_cli python -m unittest discover -s toolkit/adm_harness_cli/tests
```

The test suite passed:

```text
48 tests passed
```
