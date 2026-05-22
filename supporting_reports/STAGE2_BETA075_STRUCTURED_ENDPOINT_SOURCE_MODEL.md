# Stage II Beta075 Structured Endpoint Source Model

Date: 2026-05-22

## Summary

This report records the first cleaned-up endpoint source model for the promoted
repaired beta075 lead `rematch_w6_t1p5`.

The new model replaces the previous independent-component smooth interpolation
with assignment-local coupled stress-vector modes. Candidate selection includes
explicit penalties for excess support-edge selected-null, current, and angular
burden, plus coefficient/effective-coupling proxy reporting. A targeted
edge-tail counterterm basis is included as an optional finite support mode.

This is still an effective source-family model. It is not a physical matter
Lagrangian or a covariant conservation solve.

## Artifacts

New harness files:

```text
toolkit/adm_harness_cli/adm_harness/endpoint_j_structured_source.py
toolkit/adm_harness_cli/scripts/run_endpoint_j_structured_source_model.py
toolkit/adm_harness_cli/tests/test_endpoint_j_structured_source.py
```

Main outputs:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_structured_source_baseline_s15_beta075_p003_mid/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_structured_source_rematch_w6_t1p5/
```

Local bracket outputs with available intermediate ledgers:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15_local_bracket/endpoint_j_structured_source_rematch_w5p5_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15_local_bracket/endpoint_j_structured_source_rematch_w6p5_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15_local_bracket/endpoint_j_structured_source_rematch_w6_t1p25/
```

The completed `rematch_w6_t1p75` bracket point is source-ledger-clean, but does
not yet have the component/string/intermediate companion artifacts needed for
this structured source comparison.

## Model Form

For each endpoint assignment, the model builds finite spatial envelopes and
fits coupled stress-vector modes:

```text
spatial support:
  assignment-wide uniform mode
  finite Gaussian grid modes
  optional edge-tail counterterm modes at high conservation-residual rows

stress vector:
  coupled rho / p_l / j_l / p_omega directions derived assignment-locally

selection objective:
  weighted component fit error
  plus excess selected-null/current/angular burden penalty
  plus coefficient proxy penalty
  plus hard live-leakage rejection
```

The selected repaired-lead support-edge model uses:

```text
mode_count:       3
width_multiplier: 0.45
ridge:            1e-6
edge_tail_count:  8
```

## Repaired Lead Result

Relative to the previous tight generic smooth fit, the structured model trades
some pointwise component fit for much cleaner support-edge burden and much
smaller coefficients.

| model | support selected ratio | support current ratio | support pOmega ratio | max coefficient |
| --- | ---: | ---: | ---: | ---: |
| generic smooth `12x8/w0.8` | `1.206752` | `1.187725` | `1.401555` | `9.471895` |
| structured support-edge | `1.184398` | `1.148680` | `1.153280` | `0.445425` |

The structured model therefore substantially reduces the angular overcarry and
coefficient/effective-coupling proxy. This is the first source-model cleanup
that moves the support-edge result in the right direction.

Component errors remain imperfect:

| support component | normalized L1 | weighted RMSE | max abs error |
| --- | ---: | ---: | ---: |
| `rho` | `1.142896` | `0.000276` | `0.005804` |
| `p_l` | `1.056870` | `0.000243` | `0.014322` |
| `j_l` | `0.537328` | `0.000095` | `0.002495` |
| `p_omega` | `1.184691` | `0.005095` | `0.323805` |

Interpretation: the structured model improves the burden and coefficient
problem, but it is not yet a high-fidelity physical source representation. It
is a better source-family candidate than generic interpolation, not a closure
proof.

## Conservation Proxy

The fitted structured family remains strictly non-live. The reset cap stays
benign. The support edge still carries an edge-tail conservation watch:

| scope | effective volume fraction | volume-weighted residual norm | burden-weighted residual norm | peak residual norm | read |
| --- | ---: | ---: | ---: | ---: | --- |
| `support_edge` | `0.053250` | `0.277435` | `0.066811` | `5.244759` | edge-tail watch |
| `reset_cap` | `0.758742` | `0.009332` | `0.009861` | `0.073461` | finite-spread proxy |

Interpretation: the structured model improves burden/coupling proxies, but the
edge-tail counterterm has not fully eliminated the conservation-residual watch.
The watch remains localized and low in burden-weighted terms, but it still has
to be beaten before calling the support-edge plant physically clean.

## Local Bracket Comparison

The structured source result is stable across the available local bracket
intermediate artifacts:

| label | target support selected-null | fit selected ratio | fit current ratio | fit pOmega ratio | max coefficient |
| --- | ---: | ---: | ---: | ---: | ---: |
| `w5.5/t1.5` | `0.638110` | `1.183982` | `1.145615` | `1.135540` | `0.426625` |
| `w6.0/t1.5` | `0.642179` | `1.184398` | `1.148680` | `1.153280` | `0.445425` |
| `w6.5/t1.5` | `0.646253` | `1.184370` | `1.150547` | `1.169951` | `0.459466` |
| `w6.0/t1.25` | `0.642335` | `1.184200` | `1.148229` | `1.153180` | `0.446668` |

The bracket read is unchanged: width mostly trades live relief against
support-edge burden, but the source-model burden ratios are controlled by the
structured source family rather than by a fragile one-point collar setting.

## Feasibility Implication

The structured model improves the situation materially. The support-edge
endpoint plant no longer looks like it needs the very large angular coefficient
seen in the generic smooth fit. It also keeps live leakage at zero and gives
similar behavior across nearby collar points.

The result is not yet sufficient for a physical-source claim. The support-edge
fit still has high component L1 errors and an edge-tail conservation watch.
The next meaningful test is not beta100 or higher service factor; it is a
denser-grid and stricter structured-source check to see whether the residual
watch and coefficients stay finite or sharpen.

Current status:

```text
structured endpoint model: improved and stable;
reset cap: still broad and finite;
support edge: no longer an obvious extreme-coupling failure, but not closed;
next blocker: edge-tail conservation residual and dense-resolution scaling.
```

## Verification

Ran:

```text
python -m py_compile toolkit/adm_harness_cli/adm_harness/endpoint_j_structured_source.py toolkit/adm_harness_cli/scripts/run_endpoint_j_structured_source_model.py
PYTHONPATH=toolkit/adm_harness_cli python -m unittest discover -s toolkit/adm_harness_cli/tests
```

The test suite passed:

```text
47 tests passed
```
