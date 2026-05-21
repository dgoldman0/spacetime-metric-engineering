# Stage II Beta-Memory Receiver Angular Symmetry Memo

Date: 2026-05-20

## Scope

This memo records the third `61 x 83` smoke test of the beta-memory
support-edge receiver branch. The batch keeps the beta075 receiver
localization fixed and varies only the angular flange orientation and dose.

Outputs:

```text
toolkit/adm_harness_cli/runs/endpoint_beta_memory_receiver_angular_symmetry_smoke_61x83/
```

Spec:

```text
toolkit/adm_harness_cli/specs/endpoint_beta_memory_receiver_angular_symmetry_smoke.json
```

## Result

All six source-ledger cases were live-clean:

| label | positive live packet-norm samples |
| --- | ---: |
| `receiver_ang_sym_baseline_beta075` | `0` |
| `receiver_ang_sym_pos_p0015_beta075` | `0` |
| `receiver_ang_sym_neg_p0015_beta075` | `0` |
| `receiver_ang_sym_bilateral_p0015_beta075` | `0` |
| `receiver_ang_sym_pos_p00075_beta075` | `0` |
| `receiver_ang_sym_bilateral_p00075_beta075` | `0` |

The important finding is orientation-specific. Positive-l angular actuation
still buys selected-null relief at a large current/angular cost, but the
negative-l angular flange gives comparable or better selected-null relief
without that cost.

| label | J selected-null deficit | support-edge current | support-edge angular |
| --- | ---: | ---: | ---: |
| `receiver_ang_sym_baseline_beta075` | `0.964417` | `0.105033` | `1.912497` |
| `receiver_ang_sym_pos_p0015_beta075` | `0.957289` | `0.215404` | `2.011666` |
| `receiver_ang_sym_neg_p0015_beta075` | `0.954948` | `0.107180` | `1.912350` |
| `receiver_ang_sym_bilateral_p0015_beta075` | `0.947820` | `0.217551` | `2.011519` |
| `receiver_ang_sym_pos_p00075_beta075` | `0.960264` | `0.160109` | `1.961996` |
| `receiver_ang_sym_bilateral_p00075_beta075` | `0.955558` | `0.161180` | `1.961874` |

Transfer accounting agrees with the endpoint table. The negative-l p0015
variant has positive selected net relief with nearly neutral current/angular
transfer:

| label | target | reset relief | support transfer | net J relief |
| --- | --- | ---: | ---: | ---: |
| `receiver_ang_sym_neg_p0015_beta075` | selected | `0.014694` | `0.008497` | `0.006197` |
| `receiver_ang_sym_neg_p0015_beta075` | current | `0.002074` | `0.002829` | `-0.000755` |
| `receiver_ang_sym_neg_p0015_beta075` | angular | `0.002369` | `0.002408` | `-0.000039` |

By contrast, the positive-l p0015 case transfers about `0.110914` current
burden and `0.100370` angular burden to support-edge rows, overwhelming the
selected-null improvement. Bilateral p0015 combines the negative-l selected
relief with the positive-l current/angular penalty, so symmetry is not the
escape route.

## Interpretation

This batch weakens the squeeze narrative. The project is still squeezed out of
the cheap positive-l angular, lapse, and radial metric knobs, but not out of
angular receiver realizations. The sign/orientation of the angular flange is
material.

Narrative update:

```text
Positive-l angular capacity is expensive.
Bilateral angular capacity inherits the positive-l cost.
Negative-l angular capacity is the first tested local receiver realization
that improves J selected-null while leaving support-edge current and angular
burden nearly unchanged.
```

The next search should promote the negative-l branch, not the bilateral branch.
Recommended follow-up:

```text
1. Run a negative-l angular dose/localization ladder:
   p00075, p0015, p00225, p003 if live-clean;
   compare outer cap, inner cap, and narrower post-release support-edge masks.

2. Pair negative-l angular with the mild radial/current cap only after the
   negative-l dose response is understood.

3. Keep beta100 as a later stress case; beta075 is the clean promotion target.
```

