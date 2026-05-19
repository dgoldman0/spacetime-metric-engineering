# Stage I Shell-Throat Overlap Proxy

## Purpose

This diagnostic asks whether the remaining hard rows in the compact handoff branch line up with mixed support/throat derivative products rather than isolated point peaks.

The proxy is not a symbolic stress-tensor decomposition. It is a top-row comparative diagnostic built from finite-difference products involving:

```text
Wsh          effective standing-support profile W after packet carve
beta         radial shift / carrying-flow channel
gamma_ll     radial metric channel
gamma_Omega  angular/throat-capacity channel
```

The motivating question was:

```text
If top Tkk rows correlate strongly with mixed support/shift/radial/angular products,
then the remaining cost is probably active-rail shell/throat coupling, not just
a removable point-ledger artifact.
```

## Harness Addition

The source ledger now exposes:

```text
shell_throat_mixed_diagnostics(...)
shell_throat_overlap_proxy_ledger(...)
shell_throat_overlap_summary(...)
```

and the runner:

```text
toolkit/adm_harness_cli/scripts/run_shell_throat_overlap_proxy.py
```

For each selected case, the runner recomputes the source grid and evaluates mixed products on the top rows in:

```text
neg_Tkk_radial
abs_p_l
abs_j_l
abs_pOmega
```

The main combined score is:

```text
shell_throat_mixed_score =
  shell_gamma_ll
+ shell_gamma_Omega
+ shell_beta
+ beta_gamma_ll
+ beta_gamma_Omega
+ gamma_ll_gamma_Omega
```

where each term is a product of the relevant support, shift, radial-metric, or angular-capacity derivative scores.

## Run

Selected V5 compact handoff shell/throat proxy:

```text
toolkit/adm_harness_cli/runs/stage1_v5_shell_throat_overlap_compact_61x83/
```

Spec file:

```text
toolkit/adm_harness_cli/specs/compact_handoff_selected.json
```

Grid:

```text
61 x 83
s range: -0.96 to 1.65
l range: -2.80 to 2.80
```

Cases:

```text
split_ref
smooth_edge004_tanh
compact7_wide3_edge100
compact7_wide3_edge120
compact7_wide4_edge160
```

Validation:

```text
pytest toolkit/adm_harness_cli/tests/test_validation_ladder_hardening.py -q
23 passed
```

## Top-Row Location Check

The selected top rows split cleanly by channel:

| case | channel | top rows | live rows | geometric packet rows |
| --- | --- | ---: | ---: | ---: |
| `split_ref` | `neg_Tkk_radial` | 20 | 0 | 0 |
| `split_ref` | `abs_p_l` | 20 | 0 | 0 |
| `split_ref` | `abs_pOmega` | 20 | 18 | 18 |
| `split_ref` | `abs_j_l` | 20 | 20 | 20 |
| `compact7_wide4_edge160` | `neg_Tkk_radial` | 20 | 0 | 0 |
| `compact7_wide4_edge160` | `abs_p_l` | 20 | 0 | 0 |
| `compact7_wide4_edge160` | `abs_pOmega` | 20 | 10 | 10 |
| `compact7_wide4_edge160` | `abs_j_l` | 20 | 20 | 20 |

So the same split persists:

```text
radial-null and radial-pressure top rows are infrastructure-side;
angular/current top rows remain live packet rows.
```

The compact wide4 branch reduces the number of live top `pOmega` rows from `18 / 20` to `10 / 20`, but all top `j_l` rows remain live.

## Mixed-Proxy Summary

### Radial-Null Rows

| case | mean badness | mean mixed score | Spearman badness/mixed | dominant mixed family |
| --- | ---: | ---: | ---: | --- |
| `split_ref` | 0.1569 | 103.4 | 0.450 | `shell_gamma_ll` |
| `smooth_edge004_tanh` | 0.1356 | 105.8 | 0.567 | `shell_gamma_ll` |
| `compact7_wide3_edge100` | 0.1377 | 168.5 | 0.738 | `beta_gamma_ll` |
| `compact7_wide3_edge120` | 0.1388 | 168.6 | 0.568 | `beta_gamma_ll` |
| `compact7_wide4_edge160` | 0.1427 | 247.7 | 0.486 | `beta_gamma_ll` |

This is the cautionary result. The compact branches reduce broad live handoff burden, but their top non-live radial-null rows line up more strongly with mixed support/shift/radial-metric products. Wide4 is not simply cleaner in the radial-null peak structure. It has the largest mean mixed score on top `Tkk` rows.

### Live Angular/Current Rows

| case | channel | mean badness | mean mixed score | mean `beta_gamma_ll` |
| --- | --- | ---: | ---: | ---: |
| `split_ref` | `abs_pOmega` | 0.1290 | 4298.3 | 2958.2 |
| `smooth_edge004_tanh` | `abs_pOmega` | 0.1414 | 4315.2 | 2998.9 |
| `compact7_wide3_edge100` | `abs_pOmega` | 0.1208 | 1524.7 | 1068.1 |
| `compact7_wide3_edge120` | `abs_pOmega` | 0.1266 | 1514.0 | 1064.5 |
| `compact7_wide4_edge160` | `abs_pOmega` | 0.0835 | 919.1 | 652.3 |
| `split_ref` | `abs_j_l` | 0.00566 | 3439.3 | 2341.4 |
| `smooth_edge004_tanh` | `abs_j_l` | 0.00595 | 3569.1 | 2448.1 |
| `compact7_wide3_edge100` | `abs_j_l` | 0.00664 | 1421.5 | 929.2 |
| `compact7_wide3_edge120` | `abs_j_l` | 0.00695 | 1407.5 | 923.3 |
| `compact7_wide4_edge160` | `abs_j_l` | 0.00588 | 985.0 | 629.1 |

This is the encouraging result. The compact handoff sharply reduces mixed support/shift/radial-metric overlap on the live angular/current rows.

Relative to `split_ref`, `compact7_wide4_edge160` lowers:

| channel | mixed score change | `beta_gamma_ll` change |
| --- | ---: | ---: |
| `abs_pOmega` | -78.6% | -78.0% |
| `abs_j_l` | -71.4% | -73.1% |

That agrees with the previous channel-cause and smeared-null results: wide4 really does relieve the live handoff coupling surface.

### Radial Pressure Rows

Top `p_l` rows remain infrastructure-side and are not strongly explained by the mixed proxy:

| case | mean badness | mean mixed score | dominant mixed family |
| --- | ---: | ---: | --- |
| `split_ref` | 0.00939 | 8.86 | `ll_omega` |
| `compact7_wide4_edge160` | 0.00947 | 4.14 | `ll_omega` |

The wide4 pressure cost is not showing up as the same mixed shell/throat derivative problem. It still looks more like a core radial pressure-balance issue.

## Interpretation

The proxy gives a split verdict.

It supports the compact handoff as a real component:

```text
wide4 greatly reduces live angular/current mixed overlap;
wide4 reduces live pOmega badness and reduces live top pOmega row count;
wide4 keeps top radial-null and radial-pressure rows out of the live packet.
```

But it also preserves a real Stage I warning:

```text
top non-live radial-null rows correlate positively with mixed products;
compact branches, especially wide4, raise the mixed score on top Tkk rows;
the dominant mixed family shifts toward beta/gamma_ll coupling.
```

So the residual is not merely a harmless point-inspection artifact. The data says the remaining infrastructure-side radial-null peak is plausibly a shell/throat coupling cost.

## Freeze Implication

Do not freeze this as a clean Stage I closure.

The branch is strong enough to carry into Stage II as a serious demanded-source target, but it should be labeled provisional:

```text
Stage II target: compact7_wide4_edge160 as the best current handoff candidate.
Stage I caveat: non-live radial-null residual still has a mixed shell/throat signature.
```

The practical next decision is therefore:

```text
If the goal is to test source-family viability, proceed to Stage II with this caveat.
If the goal is a final Stage I geometry freeze, one more topology/support-dependence discriminator is justified.
```

In particular, the next Stage I-only discriminator would be to vary broader support geometry and ask whether the top `Tkk` mixed score scales down. If it does, the problem is engineering/topology support width. If it sticks, Stage II should treat it as an intrinsic source requirement.
