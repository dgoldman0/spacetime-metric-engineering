# Stage 2 beta075 dense endpoint source stability rung

Status: completed dense stability checkpoint.

## Purpose

This rung tests whether the candidate endpoint source-model extension is resolution-stable under dense scaling of the three-part grammar:

1. regenerated source ledger for the repaired `rematch_w6_t1p5` beta075 lead,
2. component/string/intermediate source decomposition,
3. structured endpoint-J source model plus support-edge closure component.

The question is not whether the closure improves one coarse mesh. The question is whether the same finite, smooth, non-live closure family remains small, local, non-singular, and live-clean when the source grammar is sampled more densely over the same physical domain.

## Baseline

Baseline mesh: `189x121`, `s=[-1.5,15.0]`, `ell=[-6.0,6.0]`, derivative stencil `h_s=h_l=0.0025`.

Baseline structured support-edge model:

- selected/current/pOmega ratios: `1.184398 / 1.148680 / 1.153280`
- max coefficient: `0.445425`
- support-edge peak conservation residual norm: `5.244759`
- live leakage: zero

Baseline structured model plus support-edge closure:

- selected/current/pOmega ratios: `1.174889 / 1.149350 / 1.160453`
- max closure coefficient: `0.001114`
- closure coefficient L1: `0.002425`
- support-edge peak conservation residual norm: `2.732194`
- diagnostic read: finite-spread proxy, not conservation proof
- live leakage: zero

## Dense rung definition

Dense mesh: `377x241`, same physical domain and derivative stencil as baseline.

Candidate:

`rematch_w6_t1p5:gain=1.8,width=6.0,temporal=1.5,floor=0.6,shape=trailing_edge`

Output root:

`toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_dense377x241_sharded12`

The original serial `377x241` run was started first under `..._dense377x241`; it had emitted row progress but no result artifacts. After adding sharded source-ledger execution, the active dense rung moved to the `..._dense377x241_sharded12` output root.

## Stability criteria

The dense result supports the source extension if:

- live packet safety remains clean,
- structured endpoint-J source ratios remain near the baseline values rather than growing with resolution,
- the closure is still selected as a tiny finite support-edge term,
- closure max coefficient and L1 scale remain comparable to baseline,
- support-edge conservation residual remains a finite-spread proxy rather than becoming sharper or more singular,
- no live rows are touched by the endpoint closure.

The dense result weakens the source extension if:

- closure coefficients grow strongly with resolution,
- the selected closure support narrows toward grid-scale behavior,
- support-edge residuals become more concentrated even if the scalar ratios look acceptable,
- live leakage appears,
- the best fit shifts from the small closure family into a broad or high-coupling source family.

## Running notes

- Dense source-ledger regeneration completed for `377x241`.
- Sharded source-ledger execution was added during this rung and committed as `3fa07fe Add sharded source ledger execution`.
- Active dense source-ledger regeneration ran with `12` workers across `48` contiguous `s`-row shards.

## Dense source-ledger result

The dense source ledger has `90,857` rows, compared with `22,869` rows in the `189x121` baseline.

Live safety remains clean:

- baseline live points: `238`
- dense live points: `966`
- baseline positive live packet norm count: `0`
- dense positive live packet norm count: `0`
- baseline max live packet norm: `-9.935129`
- dense max live packet norm: `-6.333723`

The dense source ledger therefore does not reopen the live-packet instability. The max live packet norm is less negative on the denser mesh, but still comfortably negative at this rung.

Global source burdens remain close to the baseline under refinement:

| channel | baseline total burden | dense total burden | baseline live fraction | dense live fraction |
| --- | ---: | ---: | ---: | ---: |
| `neg_Tkk_radial` | `482.454247` | `476.990697` | `0.024890` | `0.025052` |
| `abs_p_l` | `83.156015` | `81.979609` | `0.007457` | `0.007623` |
| `abs_pOmega` | `13.561421` | `13.516192` | `0.109498` | `0.111123` |
| `abs_j_l` | `0.726867` | `0.723293` | `0.091279` | `0.094995` |
| `neg_rho_euler` | `3.364766` | `3.349756` | `0.000000` | `0.000000` |
| `neg_rho_packet` | `5.121409` | `5.139885` | `0.000094` | `0.000293` |

Interpretation so far: dense sampling does not destabilize the repaired lead at the source-ledger level. The next question is whether the component/string/intermediate decomposition and the endpoint-J source closure remain finite and comparable on this denser representation.

## Dense intermediate source result

The dense component/string/intermediate grammar completed.

Intermediate live gates remain clean:

| sector | points | live rows | pair L1 | live pair L1 | selected null deficit | live selected null deficit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `J_endpoint_junction_layer` | `28,359` | `0` | `4.954527` | `0.0` | `4.243108` | `0.0` |
| `S0_constant_flux_string_cloud` | `30,881` | `0` | `159.897874` | `0.0` | `0.0` | `0.0` |
| `core_body_residual_leakage` | `2,522` | `0` | `0.084200` | `0.0` | `0.039491` | `0.0` |

Endpoint-J sector split:

| assignment | rows | selected null deficit | abs current | abs pOmega |
| --- | ---: | ---: | ---: | ---: |
| `reset_decompression_endpoint_junction` | `25,769` | `3.656358` | `0.257952` | `3.886152` |
| `support_edge_endpoint_junction` | `2,590` | `0.586750` | `0.112489` | `1.416594` |

Interpretation so far: the dense grammar still isolates endpoint-J as entirely non-live, and the support-edge assignment is still a finite population rather than a vanishing single-line artifact. The endpoint-J source-family and closure fits now need to show whether that finite population can be represented without growing coefficients or grid-scale support.

## Dense structured endpoint-J source result

Structured endpoint-J source fitting completed on the dense intermediate ledger.

Support-edge structured fit:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| rows | `652` | `2,590` |
| mode count | `3` | `3` |
| s centers | `8` | `8` |
| l centers | `6` | `6` |
| width multiplier | `0.45` | `0.45` |
| edge tail count | `8` | `8` |
| fit selected ratio | `1.184398` | `1.182812` |
| fit current ratio | `1.148680` | `1.129122` |
| fit pOmega ratio | `1.153280` | `1.057945` |
| max coefficient | `0.445425` | `0.260813` |
| coefficient L1 | `2.364165` | `2.053525` |
| live fit rows | `0` | `0` |

This is a positive support-edge stability signal: the dense support-edge structured fit uses the same family shape, remains non-live, improves the pOmega ratio, and does not grow its coefficient scale under refinement.

Reset-cap structured fit:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| rows | `6,536` | `25,769` |
| mode count | `4` | `4` |
| s centers | `8` | `8` |
| l centers | `6` | `6` |
| width multiplier | `0.65` | `0.45` |
| fit selected ratio | `1.010002` | `1.011919` |
| fit current ratio | `1.110071` | `1.124634` |
| fit pOmega ratio | `1.044866` | `0.986964` |
| max coefficient | `1.067009` | `4.828322` |
| coefficient L1 | `9.449547` | `27.134964` |
| live fit rows | `0` | `0` |

The reset-cap fit stays accurate and non-live but tightens to a narrower selected width and larger coefficient scale. That is not the support-edge closure question directly, but it is a source-realization watch item for the broader endpoint-J family.

Structured conservation diagnostic:

| scope | baseline peak residual norm | dense peak residual norm | baseline burden-weighted mean residual norm | dense burden-weighted mean residual norm |
| --- | ---: | ---: | ---: | ---: |
| `support_edge` | `5.244759` | `5.197772` | `0.066811` | `0.041417` |
| `reset_cap` | `0.073461` | `0.104682` | `0.009861` | `0.005277` |

The support-edge structured conservation residual remains an edge-tail watch before closure, with peak norm essentially stable rather than diverging. The closure component now decides whether the finite support-edge add-on stays tiny under dense refinement.

## Dense support-edge closure result

The dense closure scan completed and selected the same effective support-edge closure shape as the baseline:

- mode count: `1`
- center count: `6`
- width multiplier: `0.85`
- conservation weight: `0.0`
- angular weight: `0.25`
- live fit rows: `0`

The selected ridge changed from `1e-6` to `1e-8`, but the dense candidate scan shows the top `1e-8`, `1e-7`, and `1e-6` rows are numerically indistinguishable at the printed precision. This is not a meaningful shape change.

Closure assignment comparison:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| target selected null deficit | `0.642179` | `0.586750` |
| base selected null deficit | `0.760595` | `0.694015` |
| fit selected null deficit | `0.754489` | `0.690603` |
| target abs current | `0.115340` | `0.112489` |
| fit abs current | `0.132566` | `0.126865` |
| target abs pOmega | `1.463343` | `1.416594` |
| fit abs pOmega | `1.698140` | `1.500187` |
| fit selected ratio | `1.174889` | `1.176998` |
| fit current ratio | `1.149350` | `1.127796` |
| fit pOmega ratio | `1.160453` | `1.059010` |
| max closure coefficient | `0.001114` | `0.000846` |
| closure coefficient L1 | `0.002425` | `0.002256` |
| closure coefficient L2 | `0.001410` | `0.001172` |

Closure support width comparison:

| metric | baseline `189x121` | dense `377x241` |
| --- | ---: | ---: |
| sigma_s | `0.435173` | `0.441390` |
| sigma_l | `0.595000` | `0.595000` |

Closure conservation comparison:

| scope | baseline peak residual norm | dense peak residual norm | baseline burden-weighted mean residual norm | dense burden-weighted mean residual norm |
| --- | ---: | ---: | ---: | ---: |
| `J_total` | `2.732194` | `2.663523` | `0.019539` | `0.010971` |
| `support_edge` | `2.732194` | `2.663523` | `0.067426` | `0.041478` |
| `reset_cap` | `0.073461` | `0.104682` | `0.009861` | `0.005277` |

Interpretation: the candidate support-edge closure component is resolution-stable on this dense rung. It does not require singular support, does not sharpen toward grid scale, does not grow its effective coupling, and does not leak into live rows. The dense fit selects the same small closure family, with slightly smaller coefficients and slightly improved support-edge conservation burden.

The remaining caution is broader endpoint-J source realization, not this support-edge extension: the dense structured reset-cap fit stayed accurate and non-live but used larger coefficients than the baseline before closure. That should become the next source-family watch item, while the support-edge closure itself now looks like a real missing finite component rather than a coarse-grid patch.
