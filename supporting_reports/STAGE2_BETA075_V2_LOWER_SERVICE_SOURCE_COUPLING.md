# Stage II Beta075 V=2 Lower-Service Source Coupling Check

## Status

Overall status: `package_support_source_observed_clean`.

The V=2 lower-service rerun clears the observed full-package reduced `1+1`
support-source coupling sweep. This was not a partial reuse of the V=5 closure:
the run regenerated the V=2 source ledger and rebuilt the downstream component,
string-cloud, intermediate source, endpoint-J, medium closure, covariant audit,
support-stroke, total-closure, and package source-coupling artifacts.

This report is written from the structured run outputs in:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_v2_dense377x241/
```

The code wrote CSV and manifest artifacts only. This report is the human
interpretation layer.

## Run Scope

The V=2 branch used the same promoted `rematch_w6_t1p5` beta075 package shape
as the dense V=5 package:

```text
candidate: rematch_w6_t1p5
grid:      377 x 241
support:   promoted 24x14 support stroke/closure reference
workers:   4 for the dense source ledger and package coupling stages
```

The source manifest changed only the service rating from `V=5.0` to `V=2.0`
before rerunning the package chain.

## Source-Level Read

| channel | total burden | live packet burden | live fraction | point peak | live point peak |
| --- | ---: | ---: | ---: | ---: | ---: |
| negative radial null contraction | 480.680784 | 7.928302 | 0.016494 | 0.617400 | 0.616633 |
| radial pressure magnitude | 81.931358 | 0.606220 | 0.007399 | 0.039412 | 0.011071 |
| angular pressure magnitude | 12.925177 | 1.184321 | 0.091629 | 0.692336 | 0.115373 |
| radial current magnitude | 0.686663 | 0.041237 | 0.060055 | 0.023008 | 0.005111 |
| negative Eulerian density | 3.345889 | 0.000000 | 0.000000 | 0.013079 | 0.000000 |
| negative packet-comoving density | 5.804888 | 0.000046 | 0.000008 | 0.948281 | 0.001286 |

The V=2 live packet-norm safety row remains clean:

```text
live_points: 966
max_packet_norm_live: -6.333722528629708
positive_packet_norm_live: 0
```

## Rebuilt Package Gates

| gate | status | key read |
| --- | --- | --- |
| constrained medium field closure | pass | worst normalized L1 `0.012264`; regulator/source ratio `0.043380`; zero live regulator rows |
| covariant endpoint-medium identity | pass | projection max error `6.94e-17`; live divergence fraction `0.003228` below gate |
| support stroke exchange | pass | active PF L1 `0.450887`; allowed PF L1 `0.364703`; live tail `0.0` |
| total support closure | pass | active L2 ratio `0.452212`; allowed L2 ratio `0.359133`; live support tail `0.0` |
| package source coupling | observed clean | max observed budget fraction `0.615948` |

## Package Source-Coupling Summary

| scenario | status | slices | fail slices | fail rows | max budget fraction | min sampled cone margin | min transport margin |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| observed outward | pass | 682 | 0 | 0 | 0.615948 | 3.451e-05 | 3.843e-05 |
| observed inward | pass | 682 | 0 | 0 | 0.386545 | 4.502e-05 | 4.560e-05 |
| observed outward, budget-audited | pass | 682 | 0 | 0 | 0.615948 | 3.451e-05 | 3.843e-05 |
| large outward | fail | 682 | 4 | 58 | 3.079742 | 4.814e-13 | 7.105e-15 |
| large outward, budget-audited | limited pass | 682 | 0 | 0 | 0.950000 | 1.586e-06 | 2.047e-06 |

The observed-amplitude result is the claim driver. The large-source rows remain
stress context.

## V5 Comparison

The V=5 full-package source-coupling run was a watch:

```text
V=5 observed outward max budget fraction: 2.075621
V=5 observed inward max budget fraction:  1.388222
V=5 large outward max budget fraction:    10.378107
```

The V=2 branch is materially cleaner:

```text
V=2 observed outward max budget fraction: 0.615948
V=2 observed inward max budget fraction:  0.386545
V=2 large outward max budget fraction:    3.079742
```

The large-source stress still localizes to support-edge endpoint-junction
entry/catch slices, but at lower severity and only as a deliberately amplified
stress case. The actual observed V=2 source-coupled evolution does not reproduce
the V=5 observed failure.

## Interpretation

The lower-service run is a positive architecture check. The package does not
look intrinsically unstable under reduced source-coupled evolution: at V=2, the
same rebuilt source and support package clears source safety, medium closure,
covariant identity, support exchange, total closure, and observed package-wide
source coupling.

The V=5 problem is therefore better read as a high-service support-edge source
realization defect than as a global package failure. The right next rung remains
targeted V=5 support-edge source reshaping/normalization for the localized
entry-precatch and catch-rematch slices. There is no current need to run V=3 or
V=4 unless a later repair needs a transition map.

Claim boundary: this is a reduced fixed-background source-coupling diagnostic.
It does not promote the package to full spacetime evolution, a matter-action
proof, or a global hyperbolicity theorem.
