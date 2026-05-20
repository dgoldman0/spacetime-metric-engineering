# Stage II Hard Affine SNEC Screen: Promoted Pair

## Purpose

This is the first hard SNEC-oriented calculation after the component-source ledger, component algebra ledger, and H-promoted composite source ansatz.

Input component assignment:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_component_source_promoted_pair_61x83_full_roles/
```

Output directory:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_hard_affine_snec_promoted_pair_61x83_with_H/
```

The screen traces sampled radial null branches through the `(s, l)` grid using the ADM fields:

```text
dl/ds = -beta +/- alpha / sqrt(gamma_ll)
d lambda = alpha ds
```

It then computes affine-normalized Gaussian smeared radial null averages for the orthonormal null contraction:

```text
T_hat_kk = rho + p_l +/- 2 j_l
```

The tested affine smear widths are:

```text
tau = 0.25, 0.50, 1.00
```

The benchmark floor follows the existing harness convention:

```text
T_hat_kk_smeared >= -8 pi B / tau^2
B = 1 / (32 pi)
```

This is a harder SNEC screen than the earlier two-dimensional smeared-null proxy, but it is still not a quantum RSET calculation, conservation proof, or physical matter-model solve.

## Scan Size

| candidate | windows scanned |
| --- | ---: |
| `compact7_wide4_edge160` | 30,210 |
| `wide4_radius205` | 30,183 |
| total | 60,393 |

No benchmark-floor violations were found.

## Worst Windows

The table reports the worst window for each candidate and width, collapsing over the two radial null branches.

| candidate | tau | worst smeared `T_hat_kk` | floor | margin | critical `B` | benchmark / critical `B` | dominant sector |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `compact7_wide4_edge160` | 0.25 | -0.02542 | -4.000 | 3.97458 | 6.32e-5 | 157.36 | H current relaxation |
| `compact7_wide4_edge160` | 0.50 | -0.02156 | -1.000 | 0.97844 | 2.14e-4 | 46.39 | H current relaxation |
| `compact7_wide4_edge160` | 1.00 | -0.02133 | -0.250 | 0.22867 | 8.49e-4 | 11.72 | angular capacity |
| `wide4_radius205` | 0.25 | -0.02031 | -4.000 | 3.97969 | 5.05e-5 | 196.98 | angular capacity |
| `wide4_radius205` | 0.50 | -0.01817 | -1.000 | 0.98183 | 1.81e-4 | 55.04 | angular capacity |
| `wide4_radius205` | 1.00 | -0.01817 | -0.250 | 0.23183 | 7.23e-4 | 13.76 | angular capacity |

Interpretation:

```text
at the harness benchmark B, both candidates pass all sampled affine windows;
the broadest tau = 1.00 window is the tightest floor comparison;
compact is slightly more negative than radius205 in this screen, but both remain well above the benchmark floor.
```

## Sector Readout

The H-promoted source-sector decomposition is useful. The screen does not merely say "pass"; it identifies where the accumulated negative null average comes from.

Largest sector-level negative smeared contributions:

| candidate | sector | tau = 0.25 | tau = 0.50 | tau = 1.00 |
| --- | --- | ---: | ---: | ---: |
| `compact7_wide4_edge160` | angular capacity G | -0.02149 | -0.02107 | -0.02095 |
| `compact7_wide4_edge160` | H current relaxation | -0.01249 | -0.00996 | -0.00682 |
| `compact7_wide4_edge160` | reset sink D | -0.01330 | -0.00955 | -0.00565 |
| `compact7_wide4_edge160` | live handoff C/E/F | -0.00299 | -0.00255 | -0.00215 |
| `wide4_radius205` | angular capacity G | -0.01551 | -0.01551 | -0.01550 |
| `wide4_radius205` | H current relaxation | -0.01011 | -0.00827 | -0.00567 |
| `wide4_radius205` | reset sink D | -0.01177 | -0.00826 | -0.00471 |
| `wide4_radius205` | live handoff C/E/F | -0.00160 | -0.00138 | -0.00117 |

The A/B radial infrastructure sector is not the SNEC driver in this ansatz. Its worst sector-level smeared contribution stays at cancellation-residual scale:

```text
compact: <= 4.3e-5 in magnitude
wide205: <= 2.4e-5 in magnitude
```

That is consistent with the algebra ledger: A/B is a large support burden, but its fitted source form is close to `rho ~= -p_l`, so its direct affine radial-null accumulation is small.

## Meaning

This is a favorable Stage II result.

Before Stage II, the source problem looked like one simple scalar being asked to pay the whole support plant. That failed. After decomposition, the first hard affine SNEC screen says the H-promoted anisotropic sector picture is not killed by the sampled SNEC benchmark.

The risk has also moved into a clearer shape:

```text
small-width compact risk: non-live H/D current-relaxation/reset sector;
longer-width compact risk: angular-capacity infrastructure G;
live packet trim C/E/F: present but not dominant;
A/B radial support: large burden, small direct smeared null residual.
```

The `sector_closure_residual` remains nonzero and sometimes comparable to H/D. That means the reduced ansatz is not a final physical source model. It is good enough to justify the next phase, but not enough to call the matter model solved.

## Next Step

The immediate next work should be a convergence and robustness pass, not another broad geometry search:

```text
rerun the compact target at higher grid resolution if feasible;
add narrower and broader affine widths around tau = 1.0;
track whether G remains the long-width limiting sector;
track whether H/D remains the short-width limiting sector;
then start replacing the effective sectors with explicit candidate source families.
```

The current result does not certify SNEC viability in the full physical sense, but it moves the project from "needs hard calculation" to "passes the first hard affine SNEC benchmark screen."
