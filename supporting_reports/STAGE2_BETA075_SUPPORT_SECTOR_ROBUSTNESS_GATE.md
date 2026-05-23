# Stage II Beta075 Support-Sector Robustness Gate

Generated: 2026-05-22

## Status

Overall status: `watch`.

This is the first harder gate after finite-difference endpoint/support closure. It is a necessary-condition robustness gate over the existing support-stroke and total-closure outputs, not a final matter-action or PDE hyperbolicity proof.

## Inputs

- `baseline_24x14`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5` and `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5`
- `dense_24x14`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_exchange_freeze_rematch_w6_t1p5` and `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_total_closure_24x14_freeze_rematch_w6_t1p5`
- `baseline_compact22x13`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5` and `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_support_total_closure_compact22x13_freeze_rematch_w6_t1p5`
- `dense_compact22x13`: `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_stroke_compact22x13_freeze_rematch_w6_t1p5` and `toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12/endpoint_support_total_closure_compact22x13_freeze_rematch_w6_t1p5`

## Gate Summary

| gate | status | metric | gate | read |
| --- | --- | ---: | ---: | --- |
| reference_total_closure | watch | 0.009878 | 0.050000 | 24x14 clears gates but dense local margin is tight |
| compact_cross_bracket | watch | 0.597527 | 0.550000 | compact 22x13 is a bracket only; dense local closure misses the promoted gate |
| hyperbolic_proxy_guards | pass | 4.036e-09 | 0.000000 | necessary h_reg, transport-margin, Type-I, and high-psi guards remain positive/on-gate |
| local_hyperbolic_proxy_watch | watch | 2.407067 | 1.000000 | one or more dense local support-edge phases sit closer to the heat-current/psi boundary than the aggregate guard shows |
| locality_and_hidden_channel | pass | 6.358e-06 | 0.001000 | support exchange stays non-live, localized, and angular-free |
| coefficient_stability | pass | 1.974109 | 2.000000 | coefficients stay bounded across baseline/dense |
| residual_concentration_scaling | watch | 2.244502 | 2.000000 | peak residual growth needs denser or frozen-structure confirmation |
| overall_support_sector_next_gate | watch | nan | nan | support sector survives necessary proxy gates but stays on watch before action-level promotion |

## Reference 24x14 Closure Read

| mesh | closure status | active PF residual | local max PF residual | outside support tail | live support tail | min gate margin fraction |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| baseline | support_total_exchange_closure_pass | 0.222933 | 0.302640 | 2.082e-06 | 0.000000 | 0.449746 |
| dense | support_total_exchange_closure_pass | 0.449018 | 0.544567 | 6.358e-06 | 0.000000 | 0.009878 |

Read: the promoted `24x14` sector still clears baseline and dense closure. The dense local PF residual is close to the `0.55` gate, with only about `0.009878` fractional margin on the tightest closure metric. That is enough to proceed to a harder gate, but not enough to call the sector comfortably robust.

## Compact Cross-Bracket

| mesh | closure status | local max PF residual | PF gate | local max L2 residual | L2 gate |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline | support_total_exchange_closure_pass | 0.301894 | 0.550000 | 0.297812 | 0.550000 |
| dense | support_total_exchange_closure_watch | 0.597527 | 0.550000 | 0.581325 | 0.550000 |

Read: compact `22x13` is useful evidence against a pure large-basis artifact, but it is not the promoted closure reference. Dense compact misses the local gate, so cross-bracket robustness remains a watch.

## Dense Local Residuals

| assignment | stage | region | residual / endpoint L2 | residual / PF | top 1pct share |
| --- | --- | --- | ---: | ---: | ---: |
| reset_decompression_endpoint_junction | reset_decompression | core_throat | 0.521951 | 0.544567 | 0.404781 |
| support_edge_endpoint_junction | held_carry | support_edge | 0.335008 | 0.463656 | 0.122778 |
| reset_decompression_endpoint_junction | reset_decompression | support_edge | 0.443077 | 0.460917 | 0.342466 |
| support_edge_endpoint_junction | release_shift_fade | support_edge | 0.379679 | 0.442140 | 0.127007 |
| support_edge_endpoint_junction | catch_rematch | support_edge | 0.230265 | 0.285493 | 0.142573 |

Read: dense reset/core remains the sharpest local watch. This is exactly where a later frozen-structure or action-level test should try to break the model.

## Hyperbolic And Locality Proxies

| proxy | dense 24x14 value | read |
| --- | ---: | --- |
| minimum h_reg / Type-I margin | 4.036e-09 | positive but thin |
| p01 transport margin | 0.024445 | near-luminal but inside proxy gate |
| p99 heat-flux ratio | 0.975555 | close to the causal boundary |
| high-psi source fraction | 0.000765 | below 0.005 gate |
| outside support fraction | 1.802e-05 | tiny localized tail |
| live support fraction | 0.000000 | no live support current |

Aggregate read: the necessary hyperbolic/admissibility proxies pass, but the support edge remains a thin-cushion, near-luminal medium. This is not yet a characteristic-speed theorem.

Dense local guard rows with the hottest heat-current phases:

| assignment | stage | region | h_reg min | p01 transport margin | p99 heat ratio | high-psi source fraction |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| support_edge_endpoint_junction | release_shift_fade | support_edge | 2.554e-07 | 0.002077 | 0.997923 | 0.010917 |
| support_edge_endpoint_junction | held_carry | support_edge | 1.882e-07 | 0.005310 | 0.994690 | 0.000000 |
| support_edge_endpoint_junction | post_release_buffer | support_edge | 2.896e-05 | 0.009046 | 0.990954 | 0.000000 |
| support_edge_endpoint_junction | entry_precatch | support_edge | 4.036e-09 | 0.015630 | 0.984370 | 0.000000 |
| support_edge_endpoint_junction | catch_rematch | support_edge | 3.364e-08 | 0.023002 | 0.976998 | 0.000000 |
| reset_decompression_endpoint_junction | reset_decompression | support_edge | 8.272e-07 | 0.025025 | 0.974975 | 0.000589 |

Local read: the aggregate proxy is cleaner than the phase-local picture. Dense support-edge release and held-carry phases are the first causal/hyperbolic watch rows for a real action-level model.

## Concentration And Scaling

| mesh | peak residual density | p99 residual density | residual top 1pct share | support top 1pct share |
| --- | ---: | ---: | ---: | ---: |
| baseline | 0.100841 | 0.022727 | 0.388418 | 0.195228 |
| dense | 0.226339 | 0.036876 | 0.383105 | 0.209399 |

Read: the residual remains concentrated but does not show a simple peak blow-up across the baseline-to-dense step. That is favorable for finite-width interpretation, while the top-share concentration keeps the reset/core watch alive.

## Interpretation

The next gate does not kill the support-sector story. The promoted `24x14` support-stroke/stress sector clears total closure on both meshes, keeps support exchange non-live and angular-free, and preserves the necessary h_reg/transport/Type-I guards.

It also does not promote the model to a final action. The dense local gate is tight, the compact dense bracket fails locally, the coefficient count is high, and the hyperbolic read is still proxy-level. The right next move is a stricter frozen-structure or action-level PDE test aimed at dense reset/core, not more same-level closure fitting.

## Decision

Status: `watch-pass` for proceeding to a true action-level gate.

Allowed next:

```text
1. Freeze the 24x14 support-sector structure from baseline or dense and evaluate it across the alternate mesh without refitting.
2. Build a reduced support-sector evolution/characteristic proxy for the two-channel P/F stroke law.
3. Stress dense reset/core with bracketed widths/ridges and require no growth in local residual or coefficient concentration.
4. Keep compact 22x13 as a compactness bracket, not as the promoted reference.
```

Claim boundary:

```text
This gate supports continuing to action-level modeling. It does not certify a matter action, hyperbolicity theorem, global causal structure, or broad beta/service-factor robustness.
```
