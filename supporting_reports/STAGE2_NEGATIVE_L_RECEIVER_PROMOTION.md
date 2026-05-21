# Stage II Negative-L Receiver Promotion

Date: 2026-05-20

## Decision

Promote the beta075 negative-l angular receiver branch from orientation smoke
to dose/localization ladder.

This is not a matter-model claim. It is a source-grammar promotion: the
negative-l receiver is now the first local beta-memory angular realization
that has shown selected-null relief without importing the positive-l
current/angular penalty.

## Basis

The first beta-memory receiver smoke showed that the receiver geometry is
live-safe but that direct beta relaxation plus positive-l angular actuation was
too costly. The lapse/radial realization confirmed the squeeze on simple local
metric knobs: lapse and radial actuation did not relieve J, and adding a small
positive-l angular term restored selected-null relief only by reviving the
current/angular burden.

The angular-orientation smoke changed the narrative. All six cases were
live-clean. Positive-l and bilateral angular actuation remained costly, but
the negative-l p0015 flange improved J selected-null while leaving
support-edge current and angular burden nearly unchanged:

| case | J selected-null | support-edge current | support-edge angular |
| --- | ---: | ---: | ---: |
| beta075 baseline | `0.964417` | `0.105033` | `1.912497` |
| positive-l p0015 | `0.957289` | `0.215404` | `2.011666` |
| bilateral p0015 | `0.947820` | `0.217551` | `2.011519` |
| negative-l p0015 | `0.954948` | `0.107180` | `1.912350` |

Transfer accounting supports the same read. The negative-l p0015 case has
positive selected net relief while current and angular net transfer are nearly
neutral:

```text
selected net J relief:   +0.006197
current net J relief:    -0.000755
angular net J relief:    -0.000039
```

## Interpretation

The branch is no longer best described as "angular helps but is too expensive."
The more accurate story is orientation-sensitive coupling. Positive-l angular
capacity appears to couple into support-edge current and angular burden;
bilateral actuation inherits that cost. Negative-l angular capacity appears to
hit the selected-null deficit through a cleaner channel at this smoke-grid
resolution.

This raises confidence in physical feasibility modestly. The result is exactly
the kind of selective, localized behavior expected from a real endpoint
receiver rather than a broad metric smear. It does not yet raise confidence to
report-grade physical-source status, because the finding still needs dose
response, localization stability, denser-grid confirmation, and a companion
endpoint SNEC/conservation read.

## Promotion Ladder

The promoted ladder keeps beta075 fixed and tests negative-l angular dose plus
mask placement:

```text
baseline beta075
negative-l p00075, default outer cap
negative-l p0015, default outer cap
negative-l p00225, default outer cap
negative-l p003, default outer cap
negative-l p0015, inner cap
negative-l p0015, narrow outer cap
negative-l p0015, shorter post-release memory
```

Promotion criteria:

```text
positive live packet-norm samples remain 0
J selected-null improves versus 0.964417 baseline
support-edge current stays close to 0.105033
support-edge angular stays close to 1.912497
selected relief shows a coherent dose/localization pattern
```

If p0015 is an isolated lucky point, hold promotion and return to the
source-family counterterm branch. If p00225 or p003 continues the same relief
without current/angular penalty, promote the best dose to a denser grid. If the
localization variants beat the default outer cap, use their mask geometry as
the next promoted receiver basis before adding any radial/current companion.

