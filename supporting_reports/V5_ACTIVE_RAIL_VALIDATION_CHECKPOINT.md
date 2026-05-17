# V5 Active-Rail Validation Checkpoint

## Purpose

This checkpoint records where the active-rail architecture stands after the V5 support-shell routing, signed objective, and packet-safety overlay work.

V5 remains the reference target-selection case. V10 is useful as an edge stress, but it should not be allowed to redefine the baseline unless the V5 branch first passes the coupled validation ladder.

## Current Architecture

The promoted V5 branch is the shaped-catch/radial-soft/lapse-cushion geometry with a small positive support-shell carrying-flow component:

- service field: `carrying_flow`
- law: `windowed_adjustment`
- scope: `catch_rematch_support_shell`
- allocation: `support_shell`
- amplitude: `+1e-7`
- catch lead: `0.75`
- temporal width: `0.5`

This is a service-layer control ansatz. It should not be read as a matter-source proof, a new geometry freeze, or a final feasibility statement.

## What Has Been Answered

The V5 support-shell routing screen answered the main burden-routing question in the affirmative at tiny-control amplitude:

Can extra radial momentum demand, `delta_j_l`, be routed into catch/rematch and support-shell infrastructure while packet `delta_rho` remains quiet?

For the preferred target, the answer is yes. The incremental `delta_j_l` burden is overwhelmingly localized in catch/rematch support-shell infrastructure, while packet density exposure is negligible.

Representative V5 target metrics:

| metric | value |
|---|---:|
| global abs incremental `delta_j_l` | `1.230138e-07` |
| catch-support incremental fraction | `0.992775` |
| support incremental fraction | `0.992811` |
| packet incremental `delta_j_l` fraction | `1.382323e-07` |
| packet abs incremental `delta_rho` | `5.442060e-16` |

The signed source-objective sign test slightly prefers positive amplitude over negative amplitude across the tested sign pairs. This is a real numerical preference but not yet a physical sign conclusion: the largest relative objective gap is only about `2.89e-6`, so sign is currently a tie-breaker rather than a source-family discovery.

The packet-safety overlay test then asked whether adding the promoted component on top of the existing shaped-catch/radial-soft/lapse-cushion branch preserves packet safety. It recomputed

```text
packet_norm_new = -alpha^2 + gamma_ll * (U_packet/B + beta + delta_beta)^2
```

on the high-resolution V5 tuned branch `highres_41x73/V5_tuned_w0569_eta200.csv`.

The target `+1e-7` component preserved packet safety. The baseline worst live packet norm was about `-251.3313`, and the target changed the worst live packet norm by only about `0.003509`. A broader sign/amplitude overlay sweep through `1e-5`, or 100 times the target amplitude, also remained packet-safe.

## Implication

The architecture now looks like a coherent service system at V5:

1. The control component can be localized to infrastructure.
2. Packet density remains quiet under the support-shell burden route.
3. The sign preference points weakly toward positive amplitude.
4. The same promoted component preserves packet norm safety on the existing tuned freeze branch.

That is enough to promote the support-shell component into the V5 validation ladder. It is not enough to claim source feasibility.

## Validation Discipline Going Forward

The next harness step should make the staged validation explicit:

| stage | question | output |
|---|---|---|
| routing | Does incremental `delta_j_l` land in catch/support infrastructure? | routing summary and pass/fail gates |
| packet overlay | Does the component preserve packet norm safety on the tuned V5 branch? | packet-safety summary |
| signed objective | Does sign/source accounting agree with the routing result? | signed objective summary and pair comparison |
| conservation-style accounting | Does the reduced ledger close its own incremental-burden bookkeeping? | signed and absolute balance summary |
| decision sheet | Did the candidate pass the V5 gates? | compact decision sheet |

V10 should then be run only as an edge stress using the same selected V5 candidate and the same ladder shape.

## Current Status

The V5 active-rail architecture is past the "interesting knob" stage. It has a stable, controllable support-shell burden-routing pattern with packet quietness and packet safety preserved under the promoted tiny-control component.

The open question is now coupled validation: whether richer source/objective accounting and reduced conservation-style summaries remain consistent with the same V5 support-shell branch.

## First Validation-Ladder Run

The staged V5 validation ladder has now been added and run with the promoted target config:

`toolkit/adm_harness_cli/configs/v5_service_support_shell_target.yaml`

The first ladder run passed all required gates:

| gate | result | value |
|---|---|---:|
| catch-support routing fraction | pass | `0.9927751519845942` |
| packet incremental `delta_j_l` fraction | pass | `1.3823230658422633e-07` |
| packet abs incremental `delta_rho` | pass | `5.44206011079721e-16` |
| target live packet-norm violations | pass | `0` |
| all tested packet-overlay variants safe | pass | `true` |
| reduced ledger partition closure error | pass | `2.6469779601696886e-23` |

The signed objective again weakly prefers the positive sign, with relative sign-pair gap `2.89036e-06`. This remains diagnostic rather than decision-grade.

The generated run artifacts are intentionally local outputs under:

`toolkit/adm_harness_cli/runs/v5_validation_ladder/`

The reusable command is:

```bash
python scripts/run_v5_validation_ladder.py
```
