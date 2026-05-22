# Stage II Beta075 Endpoint J Source-Family Rung

Date: 2026-05-22

## Summary

This report unifies the first two endpoint-J source-family steps for the
promoted repaired beta075 lead `rematch_w6_t1p5`.

The work asks two sequential questions:

```text
1. Does the demanded intermediate J layer look finite-width, non-live, and
   approximately self-closed under assignment-local conservation proxies?
2. Can finite smooth endpoint-family envelopes span the J target without live
   leakage, singular support, or extreme effective coupling proxies?
```

The answer is narrow but useful: the project is not blocked at this rung, and
the reset cap looks like a broad finite plant. The remaining hard problem is the
support-edge shoulder, especially its angular component. A generic smooth basis
can make the conservation proxy benign, but it over-carries support-edge
selected-null/current/angular burden. The next source model needs coupled
stress-vector modes and a targeted support-edge counterterm, not simply more
independent interpolation blobs.

This remains an effective-source diagnostic. It is not a physical matter
Lagrangian, semiclassical RSET result, global horizon theorem, or covariant
conservation proof.

## Artifacts

New harness files:

```text
toolkit/adm_harness_cli/adm_harness/endpoint_j_conservation.py
toolkit/adm_harness_cli/scripts/run_endpoint_j_conservation_diagnostic.py
toolkit/adm_harness_cli/tests/test_endpoint_j_conservation.py
toolkit/adm_harness_cli/adm_harness/endpoint_j_family_fit.py
toolkit/adm_harness_cli/scripts/run_endpoint_j_family_fit.py
toolkit/adm_harness_cli/tests/test_endpoint_j_family_fit.py
```

Diagnostic outputs:

```text
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_conservation_baseline_s15_beta075_p003_mid/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_conservation_rematch_w6_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_family_fit_baseline_s15_beta075_p003_mid/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_family_fit_rematch_w6_t1p5/
toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/endpoint_j_family_fit_rematch_w6_t1p5_tight12x8/
```

## Conservation Proxy

The conservation diagnostic isolates `J_endpoint_junction_layer` and computes
assignment-local finite differences before aggregating `J_total`:

```text
continuity-like residual:      d_s rho + d_l j_l
radial-momentum-like residual: d_s j_l + d_l p_l
angular-capacity gradient:     d_l p_omega
```

The J layer remains strictly non-live in both baseline and repaired lead. The
source-family question therefore stays in the endpoint plant, not the packet
worldtube.

| scope | baseline selected-null | repaired selected-null | baseline eff. volume frac | repaired eff. volume frac | repaired diagnostic read |
| --- | ---: | ---: | ---: | ---: | --- |
| `J_total` | `4.311039` | `4.338263` | `0.087001` | `0.087521` | edge-tail residual watch |
| `support_edge` | `0.615485` | `0.642179` | `0.032455` | `0.031734` | edge-tail residual watch |
| `reset_cap` | `3.695554` | `3.696084` | `0.701327` | `0.701676` | finite-spread proxy |

The repaired lead improves the support-edge conservation proxy relative to
baseline even though support-edge selected-null burden is slightly higher:

| scope | mean residual density baseline | mean residual density repaired | peak residual density baseline | peak residual density repaired |
| --- | ---: | ---: | ---: | ---: |
| `support_edge` | `0.000890` | `0.000632` | `0.280635` | `0.152879` |
| `reset_cap` | `0.005265` | `0.005229` | `0.081532` | `0.069108` |

The high normalized support-edge residual peak is an edge-tail signal, not a
main-burden concentration:

| scope | repaired volume-weighted norm | repaired burden-weighted norm | repaired peak norm | peak burden share |
| --- | ---: | ---: | ---: | ---: |
| `support_edge` | `0.417507` | `0.088288` | `21.399965` | `0.000022` |
| `reset_cap` | `0.008794` | `0.008432` | `0.164701` | `0.000378` |

Support-edge angular capacity also moves favorably:

```text
support-edge abs_pomega:                  1.976812 -> 1.463343
support-edge angular-gradient norm proxy: 108.670757 -> 20.255763
```

Interpretation: reset cap is broad, stable, and low-residual. The support-edge
shoulder is the place where a physical source model has to do real work.

## Finite Family Fit

The first explicit family fit uses assignment-local Gaussian RBF envelopes plus
a uniform assignment mode to fit the demanded J components:

```text
rho
p_l
j_l
p_omega
```

The repaired-lead `8 x 6` check used width multiplier `1.25` and ridge `1e-8`.
The tighter repaired-lead check used `12 x 8`, width multiplier `0.8`, and ridge
`1e-9`.

The generic smooth basis stays non-live and makes the conservation proxy benign,
but it over-carries support-edge burden:

| fit | support selected ratio | support current ratio | support pOmega ratio | support conservation read |
| --- | ---: | ---: | ---: | --- |
| `8x6/w1.25` | `1.291900` | `1.364444` | `1.874795` | finite-spread proxy |
| `12x8/w0.8` | `1.206752` | `1.187725` | `1.401555` | finite-spread proxy |

The tighter fit improves the component match, but support-edge angular remains
the limiting channel:

| component | `8x6` normalized L1 | `12x8` normalized L1 | `12x8` max abs coeff |
| --- | ---: | ---: | ---: |
| support `rho` | `1.077518` | `0.890176` | `0.057359` |
| support `p_l` | `0.962721` | `0.792400` | `0.206564` |
| support `j_l` | `0.688063` | `0.424721` | `0.073237` |
| support `p_omega` | `1.868828` | `1.141477` | `9.471895` |

Reset cap remains much less concerning in the tight repaired-lead check:

| component | normalized L1 | max abs coeff |
| --- | ---: | ---: |
| reset `rho` | `0.045325` | `0.024686` |
| reset `p_l` | `0.304535` | `0.016583` |
| reset `j_l` | `0.660835` | `0.015307` |
| reset `p_omega` | `0.802346` | `0.370669` |

The reset selected-null ratio is close to unity:

```text
target reset selected-null: 3.696084
fit reset selected-null:    3.768902
fit / target:               1.019701
```

## Feasibility Implication

This result informs overall active-rail feasibility, not only local collar
design. The live rail architecture is still passing the higher-rung effective
tests; the remaining risk has crystallized into a finite source-plant
realization problem at a non-live support edge.

The endpoint J target does not obviously require live leakage, singular support,
or vanishing support volume at this resolution. A finite smooth envelope can
make the conservation proxy look benign. But the naive independent-component
smooth fit is not a physical source-family answer: it overproduces
support-edge selected-null/current/angular burden, and support `p_omega` still
looks like the effective-coupling bottleneck.

Current status:

```text
not blocked;
not proven;
reset cap: finite-width plant looks plausible;
support edge: main beta075 physical-source feasibility task;
next blocker: physically structured coupled support-edge modes.
```

## Next Work

Do not broaden to beta100 yet. The next beta075 source-family step should be:

```text
1. Keep reset-cap as a broad finite plant.
2. Build support-edge modes with coupled stress vectors, not independent
   component fits.
3. Add a targeted edge-tail/counterterm basis aligned to the conservation
   residual rows.
4. Penalize extra selected-null/current/angular burden directly in the fit.
5. Re-run endpoint_j_conservation on the fitted family.
6. Run the same diagnostics on the local collar bracket once the remaining
   temporal point lands.
7. Repeat on a denser grid to check that effective volume, residual measures,
   and coefficient proxies do not sharpen pathologically.
```
