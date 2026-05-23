# Stage II Beta075 Finite-Domain Radial ANEC Diagnostic

Date: 2026-05-23

Status: `diagnostic_anec_negative_with_residual_dominated_attribution`.

## Purpose

This diagnostic follows the post-closeout question: the repaired beta075
`rematch_w6_t1p5` package is clean in affine-reparameterized finite-window
SNEC screens, but does the same package look acceptable under an averaged
radial-null test?

The runner reuses the hard-affine SNEC trace machinery. It follows radial null
branches with the affine reparameterization, then integrates `Tkk d_lambda`
over the longest available in-domain finite trace. This is a finite-domain
diagnostic, not a complete-null-geodesic ANEC theorem, quantum RSET
calculation, conservation proof, or physical matter-model solve.

## Code And Storage

New harness entry points:

```text
toolkit/adm_harness_cli/adm_harness/finite_domain_anec.py
toolkit/adm_harness_cli/scripts/run_finite_domain_anec.py
```

The upgraded runner supports process concurrency over independent seed chunks:

```text
--max-workers 6
```

Heavy trace output is written as zstd Parquet:

```text
finite_domain_anec_traces.parquet
```

Small seed, summary, sector-summary, and top-negative sidecars remain CSV/JSON.

## Main Run

Command shape:

```text
python toolkit/adm_harness_cli/scripts/run_finite_domain_anec.py \
  --component-dir toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/component_rematch_w6_t1p5 \
  --outdir toolkit/adm_harness_cli/runs/finite_domain_anec_rematch_w6_t1p5_s15_parallel \
  --seed-stride 16 \
  --top-per-branch 120 \
  --snec-top-windows toolkit/adm_harness_cli/runs/beta_collar_generator_beta075_p003_mid_s15/affine_snec_rematch_w6_t1p5_full_tau050_100_200/hard_affine_snec_top_windows.csv \
  --top-limit 160 \
  --max-workers 6
```

Runtime was about `72.3 s` for `3,452` traces.

| branch | traces | negative traces | worst integral | p01 integral | median integral | best integral |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| minus | `1,701` | `1,495` | `-1.796825` | `-0.239549` | `-0.067083` | `4.683190` |
| plus | `1,751` | `1,607` | `-1.143288` | `-0.231385` | `-0.067097` | `251.391548` |

The main finite-domain radial ANEC diagnostic is therefore not clean.

The attribution is the key result. Dominant negative sector counts are:

```text
plus / sector_closure_residual:  1712 traces
minus / sector_closure_residual: 1701 traces
plus / live_handoff_trim:          39 traces
```

So the baseline finite-domain ANEC negativity is overwhelmingly a
sector-closure residual story, not a failure of the near-NEC-saturating radial
string-cloud scaffold.

## Residual Ablation

The first ablation removes `sector_closure_residual` and uses sector-sum total:

```text
--total-mode sector_sum
--sector-scale sector_closure_residual=0
```

Output:

```text
toolkit/adm_harness_cli/runs/finite_domain_anec_rematch_w6_t1p5_s15_parallel_no_closure_residual/
```

| branch | traces | negative traces | worst integral | p01 integral | median integral | best integral |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| minus | `1,709` | `848` | `-0.004643` | `-0.002366` | `0.000000` | `305.089831` |
| plus | `1,736` | `903` | `-34.301012` | `-0.009349` | `-0.000011` | `221.251079` |

This almost removes the minus-branch problem. The plus branch still has a large
extreme negative trace dominated by `live_handoff_trim` at
`post_release_buffer / support_edge`.

## Residual Plus Live-Trim Ablation

The second ablation removes both `sector_closure_residual` and
`live_handoff_trim`:

```text
--total-mode sector_sum
--sector-scale sector_closure_residual=0
--sector-scale live_handoff_trim=0
```

Output:

```text
toolkit/adm_harness_cli/runs/finite_domain_anec_rematch_w6_t1p5_s15_parallel_no_closure_no_live_trim/
```

| branch | traces | negative traces | worst integral | p01 integral | median integral | best integral |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| minus | `1,708` | `849` | `-0.004643` | `-0.002366` | `0.000000` | `308.675923` |
| plus | `1,734` | `883` | `-0.009361` | `-0.006382` | `-0.000000027` | `248.643828` |

This says the remaining explicit non-live sector package is close to
finite-domain radial-ANEC balanced under this diagnostic convention. Small
negative traces remain, mostly at the `1e-3` to `1e-2` level.

## Interpretation

The result should not be summarized as "ANEC passes." It does not. The geometric
demanded total is finite-domain radial-ANEC negative on the sampled
adversarial/uniform seed set.

The result also should not be summarized as "the V5 design is killed." The
dominant negative contribution is not the A/B/I radial scaffold; that sector
remains tiny in integrated radial-null cost. The principal issue is the
unresolved closure/completion layer, with a secondary plus-branch live-handoff
trim extreme. That is consistent with the current disclosure narrative:

```text
protected live packet corridor
plus near-NEC-saturating radial infrastructure
plus finite endpoint/support source package
plus residual source-completion and live handoff watches
```

The ANEC diagnostic therefore sharpens the feasibility boundary. The SNEC
result remains strong: finite-window affine radial-null exposure stays above
the selected benchmark floor. But the stronger averaged radial-null story is
not yet earned for the demanded geometric total. To improve the narrative, the
next work should target source-basis completion and handoff-trim averaging,
not same-level collar retuning by default.

## Next Checks

Recommended follow-ups:

```text
1. Run the same finite-domain ANEC diagnostic on the intermediate S0/J/R source package.
2. Add a residual-completion source model and rerun the geometric-total comparison.
3. Separate endpoint/support, live-handoff, and far-exterior trace classes in the summary.
4. Repeat on extended domains to classify huge-affine-span traces and boundary sensitivity.
5. Add off-axis/null-family analogues only after the radial residual story is understood.
```

Claim language after this diagnostic:

```text
Allowed:
  The repaired beta075 V5 package is affine-SNEC-clean but finite-domain
  radial-ANEC-negative on the demanded geometric total, with negativity
  dominated by closure residual rather than the radial scaffold.

Avoid:
  The repaired beta075 V5 package satisfies ANEC.
  The finite-domain ANEC diagnostic proves physical inadmissibility.
```
