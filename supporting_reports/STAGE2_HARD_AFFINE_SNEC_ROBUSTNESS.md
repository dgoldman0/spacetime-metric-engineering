# Stage II Hard Affine SNEC Robustness Pass

## Purpose

This pass asks whether the first hard affine SNEC result breaks under two deeper checks:

```text
1. expanded affine smear-width ladder on the 61 x 83 promoted pair;
2. denser 81 x 109 compact-target rerun with the same width ladder.
```

It keeps the H-promoted sector assumptions from the composite source ansatz.

## Output Directories

```text
61 x 83 width ladder:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_promoted_pair_61x83_width_ladder/

81 x 109 compact source ledger:
toolkit/adm_harness_cli/runs/stage2_external/stage2_compact_kill_candidate_ledger_81x109/

81 x 109 compact component ledger:
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_source_compact_81x109_full_roles/

81 x 109 compact width ladder:
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_compact_81x109_width_ladder/
```

## Expanded Width Ladder

The expanded ladder used:

```text
tau = 0.125, 0.25, 0.50, 1.00, 1.50, 2.00
```

The `61 x 83` promoted-pair ladder scanned `120,918` windows. It found no benchmark-floor violations.

| candidate | tau | worst `T_hat_kk` | floor | margin | benchmark / critical `B` | dominant sector |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `compact7_wide4_edge160` | 0.125 | -0.02709 | -16.000 | 15.97291 | 590.57 | H current relaxation |
| `compact7_wide4_edge160` | 0.250 | -0.02542 | -4.000 | 3.97458 | 157.36 | H current relaxation |
| `compact7_wide4_edge160` | 0.500 | -0.02156 | -1.000 | 0.97844 | 46.39 | H current relaxation |
| `compact7_wide4_edge160` | 1.000 | -0.02133 | -0.250 | 0.22867 | 11.72 | angular capacity |
| `compact7_wide4_edge160` | 1.500 | -0.02132 | -0.11111 | 0.08979 | 5.21 | angular capacity |
| `compact7_wide4_edge160` | 2.000 | -0.02131 | -0.06250 | 0.04119 | 2.93 | angular capacity |
| `wide4_radius205` | 0.125 | -0.02146 | -16.000 | 15.97854 | 745.48 | angular capacity |
| `wide4_radius205` | 0.250 | -0.02031 | -4.000 | 3.97969 | 196.98 | angular capacity |
| `wide4_radius205` | 0.500 | -0.01817 | -1.000 | 0.98183 | 55.04 | angular capacity |
| `wide4_radius205` | 1.000 | -0.01817 | -0.250 | 0.23183 | 13.76 | angular capacity |
| `wide4_radius205` | 1.500 | -0.01817 | -0.11111 | 0.09294 | 6.12 | angular capacity |
| `wide4_radius205` | 2.000 | -0.01817 | -0.06250 | 0.04433 | 3.44 | angular capacity |

Interpretation:

```text
short-width compact risk remains H/current relaxation;
broad-width risk is G/angular capacity;
the result tightens at tau = 2.0, but does not break.
```

## High-Resolution Compact Rerun

The compact target was rerun at:

```text
81 x 109 grid
8829 point-ledger rows
0 live packet norm failures
```

The high-resolution component ledger still gives complete live packet residual coverage:

| channel | live total burden | live residual burden | live residual fraction |
| --- | ---: | ---: | ---: |
| `neg_Tkk_radial` | 8.6226 | 0.0000 | 0.0000 |
| `abs_p_l` | 0.4484 | 0.0000 | 0.0000 |
| `abs_j_l` | 0.0584 | 0.0000 | 0.0000 |
| `abs_pOmega` | 1.2336 | 0.0000 | 0.0000 |

The `81 x 109` compact affine width ladder scanned `105,924` windows. It found no benchmark-floor violations.

| tau | worst `T_hat_kk` | floor | margin | benchmark / critical `B` | dominant sector |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0.125 | -0.02718 | -16.000 | 15.97282 | 588.65 | H current relaxation |
| 0.250 | -0.02550 | -4.000 | 3.97450 | 156.85 | H current relaxation |
| 0.500 | -0.02158 | -1.000 | 0.97842 | 46.34 | H current relaxation |
| 1.000 | -0.02130 | -0.250 | 0.22870 | 11.74 | angular capacity |
| 1.500 | -0.02129 | -0.11111 | 0.08982 | 5.22 | angular capacity |
| 2.000 | -0.02129 | -0.06250 | 0.04121 | 2.94 | angular capacity |

## Convergence Readout

The high-resolution compact result is very close to the `61 x 83` result.

| tau | `61 x 83` worst margin | `81 x 109` worst margin | change |
| ---: | ---: | ---: | ---: |
| 0.125 | 15.97291 | 15.97282 | -0.00009 |
| 0.250 | 3.97458 | 3.97450 | -0.00008 |
| 0.500 | 0.97844 | 0.97842 | -0.00002 |
| 1.000 | 0.22867 | 0.22870 | +0.00004 |
| 1.500 | 0.08979 | 0.08982 | +0.00003 |
| 2.000 | 0.04119 | 0.04121 | +0.00002 |

That is the important robustness result. The pass is not a coarse-grid artifact at this resolution step.

## Verdict

The deeper pass holds.

The current weakest point is not an immediate SNEC benchmark violation. It is the shrinking broad-width margin:

```text
tau = 2.0 compact margin ~= 0.0412
benchmark / critical B ~= 2.94
dominant sector: G angular capacity
```

This means the next deeper analysis should focus on the angular-capacity sector and on even broader affine accumulation, not on returning to a pure scalar source search.

## Next Analysis

Recommended next steps:

```text
1. Extend broad affine widths beyond tau = 2.0, with careful boundary/truncation accounting.
2. Run a G-sector sensitivity test: reduce/remove G fit contribution and quantify margin loss.
3. Run an H/D current-relaxation sensitivity test for tau <= 0.5.
4. Begin explicit source-family replacement for G first, because it is the broad-window limiting sector.
```

The source-sector picture has survived the first robustness ladder. The remaining question is no longer whether the first hard screen immediately breaks, but which sector can be made physical without consuming the SNEC margin.
