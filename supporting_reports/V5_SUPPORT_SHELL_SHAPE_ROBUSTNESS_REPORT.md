# V5 Support-Shell Shape and Robustness Report

This report records the V5 support-shell shape-selection and matched-strength robustness stage. The purpose was to determine whether the improved source behavior seen in the support-shell screen came from a real shape advantage or from a lower effective carrying-flow strength, and then to map the local strength envelope around the preferred support-shell-bearing ansatz.

The tested family is the continuous support-shell metric overlay on the V5 reference branch:

```text
service factor:                  V = 5
variant:                         tuned_w0569_eta200
sign:                            positive carrying-flow overlay
rail-stretch ratio:              0.0
throat-capacity ratio:           0.0
support-shell radial multiplier: default
support-shell inner multiplier:  default
grid:                            ns = 53, nl = 73
```

The support-shell shape controls now cover temporal profile, radial profile, radial half-width, and matched effective support-shell strength. The matched-strength control is the peak absolute support-shell carrying-flow perturbation,

```text
target max |delta beta_shell|
```

which is recorded in the sweep output as `target_delta_beta_abs_max`. For each shape, the harness measures the peak support-shell window on the active grid, then adjusts the per-case amplitude so that

```text
abs_amplitude * max |W_shell| = target_delta_beta_abs_max.
```

This makes the shape comparison a comparison at equal effective peak carrying-flow strength.

## Runs Used

The first shape screen was:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_shape_screen
```

That run compared temporal profile families and radial profile families at fixed nominal amplitude:

```text
cases:              72
failures:           0
amplitude:          +0.5
catch leads:        1.45, 1.55
temporal widths:    0.25, 0.30, 0.35
temporal profiles:  gaussian, raised_cosine, minjerk_pulse
radial profiles:    smooth_box, raised_cosine_annulus
clock ratios:       0.375, 0.5
```

The matched-strength shape comparison was:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_shape_normalized
```

That run compared the radial families at equal effective support-shell carrying-flow strength:

```text
cases:                         48
failures:                      0
target max |delta beta_shell|: 0.25
catch leads:                   1.45, 1.55
temporal widths:               0.25, 0.30
temporal profiles:             gaussian, minjerk_pulse
radial profiles:               smooth_box, gaussian_annulus, raised_cosine_annulus
clock ratios:                  0.375, 0.5
```

The radial-width confirmation was:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_raised_cosine_radial_width_normalized
```

That run held the raised-cosine annulus family and swept radial half-width:

```text
cases:                         40
failures:                      0
target max |delta beta_shell|: 0.25
radial half-widths:            0.48125, 0.55, 0.65, 0.80, 1.00
```

The strength ladder was:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_preferred_strength_ladder
```

That run used the preferred radial family and mapped the local matched-strength envelope:

```text
cases:                         120
failures:                      0
target max |delta beta_shell|: 0.15, 0.20, 0.25, 0.30, 0.35
catch leads:                   1.45, 1.55
temporal widths:               0.25, 0.30, 0.35
temporal profiles:             gaussian, minjerk_pulse
radial profile:                raised_cosine_annulus
radial half-width:             0.48125
clock ratios:                  0.375, 0.5
```

## Shape Result

The matched-strength comparison confirms that the raised-cosine annulus is a real improvement over the earlier smooth-box shell. The best cases by radial family were:

| radial profile | best source objective | max burden | packet norm drift | radial-null ratio | radial-current ratio | angular-pressure ratio |
|---|---:|---:|---:|---:|---:|---:|
| `raised_cosine_annulus` | `0.803284` | `1.013261` | `3.09e-08` | `1.007942` | `1.002684` | `1.013261` |
| `gaussian_annulus` | `0.829022` | `1.016165` | `1.51e-03` | `1.008492` | `1.003251` | `1.016165` |
| `smooth_box` | `1.064162` | `1.052003` | `1.81e-02` | `1.019290` | `1.011380` | `1.052003` |

The shape improvement therefore survives peak-amplitude normalization. At the same peak `delta beta_shell`, the raised-cosine annulus lowers aggregate burden, radial-null burden, radial-current burden, angular-pressure burden, and live packet-norm drift. The improvement is especially strong against the smooth-box support shell, where the packet readout and angular-pressure ceiling remain visibly worse.

The best matched-strength shape case was:

| target `max |delta beta_shell|` | catch lead | temporal width | temporal profile | radial profile | clock ratio | source objective | max burden | packet drift |
|---:|---:|---:|---|---|---:|---:|---:|---:|
| `0.25` | `1.45` | `0.30` | `gaussian` | `raised_cosine_annulus` | `0.375` | `0.803284` | `1.013261` | `3.09e-08` |

This is a major shift relative to the previous smooth-box candidate. The earlier high-resolution coupled-timing family sat near a `5.3%` max burden increase with packet drift around `0.02`. The raised-cosine annulus version brings the best matched-strength cases to about a `1.3%` max burden increase with packet drift at the numerical quiet level.

## Radial Width

The radial-width screen indicates that the default raised-cosine annulus half-width, `0.48125`, is the current preferred width. The best case at each tested width was:

| radial half-width | best source objective | max burden | packet drift | point-peak ratio |
|---:|---:|---:|---:|---:|
| `0.48125` | `0.803284` | `1.013261` | `3.09e-08` | `1.124667` |
| `0.55` | `0.819495` | `1.015849` | `2.38e-07` | `1.120648` |
| `0.65` | `0.864313` | `1.019825` | `3.46e-04` | `1.124487` |
| `0.80` | `0.900131` | `1.027396` | `3.56e-02` | `1.113648` |
| `1.00` | `1.695481` | `1.037854` | `3.13e+00` | `1.124362` |

The implication is that the support shell wants a localized bearing band. A modest broadening to `0.55` remains usable but loses cleanliness. Broader annuli begin to reintroduce packet motion and source burden. By width `1.00`, the support shell has spread far enough into the packet-sensitive geometry that the packet diagnostic degrades strongly.

## Strength Ladder

The matched-strength ladder shows a coherent local basin. The best source-objective case at each target strength was:

| target `max |delta beta_shell|` | catch lead | temporal width | temporal profile | clock ratio | source objective | max burden | packet drift | point-peak ratio |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| `0.15` | `1.55` | `0.30` | `gaussian` | `0.375` | `0.598918` | `1.008329` | `1.98e-08` | `1.000000` |
| `0.20` | `1.55` | `0.30` | `gaussian` | `0.375` | `0.669478` | `1.011213` | `2.64e-08` | `1.014307` |
| `0.25` | `1.45` | `0.35` | `gaussian` | `0.375` | `0.763342` | `1.012886` | `2.70e-08` | `1.029960` |
| `0.30` | `1.45` | `0.35` | `gaussian` | `0.375` | `0.898201` | `1.015473` | `3.24e-08` | `1.161818` |
| `0.35` | `1.45` | `0.35` | `gaussian` | `0.375` | `1.036320` | `1.018006` | `3.78e-08` | `1.294386` |

Across the whole local neighborhood, the threshold counts were:

| target `max |delta beta_shell|` | cases | cases with max burden `<= 1.02` | cases with objective `< 1` | cases with packet drift `< 1e-6` | cases with point peak `<= 1.2` |
|---:|---:|---:|---:|---:|---:|
| `0.15` | `24` | `24` | `24` | `24` | `24` |
| `0.20` | `24` | `23` | `23` | `24` | `22` |
| `0.25` | `24` | `24` | `22` | `24` | `16` |
| `0.30` | `24` | `22` | `16` | `24` | `6` |
| `0.35` | `24` | `16` | `0` | `24` | `0` |

The preferred operating range is therefore `0.15` to `0.25` in matched peak `delta beta_shell`. The `0.15` and `0.20` targets are broadly quiet. The `0.25` target remains attractive and still gives the best shape-comparison result, but point peaks begin to matter. The `0.30` target is a usable stress point for selected timing choices. The `0.35` target is an upper-edge stress case for boundary mapping.

Packet norm itself stays quiet throughout this ladder. Every tested case has live packet-norm drift below `1e-6`. The limiting behavior is source quality: point-peak growth, shell-throat concentration, and in a few short-timing cases packet-comoving density burden outside the live-packet safety readout.

## Boundary Behavior

The most useful boundary signal comes from the short temporal-width edge, especially `temporal_width = 0.25`. One outlier at target `0.20` has:

```text
target max |delta beta_shell|: 0.20
catch lead:                   1.45
temporal width:               0.25
temporal profile:             gaussian
clock ratio:                  0.375
source objective:             2.250785
max total burden ratio:       1.306769
packet norm drift:            3.16e-08
```

The channel table identifies the outlier channel as `neg_rho_packet`, whose total burden ratio rises to `1.306769`, while the live packet-norm readout remains quiet. This is an important distinction. The active metric can keep the live packet norm safe while still producing a packet-comoving source-accounting penalty elsewhere in the grid. That makes `temporal_width = 0.25` a boundary setting for this family. The preferred timing lives at `0.30` to `0.35`.

The broader pattern points toward `temporal_width = 0.30` to `0.35` as the stable timing band. The best source-objective point shifts from width `0.30` at targets `0.15` and `0.20` to width `0.35` at targets `0.25` through `0.35`. This suggests a simple load-bearing rule: as matched support-shell strength increases, the temporal support event should broaden slightly to keep gradients aligned.

## Current Preferred Ansatz

The current V5 support-shell-bearing ansatz should be carried forward as:

```text
radial profile:                 raised_cosine_annulus
radial half-width:              0.48125
matched peak delta beta_shell:  0.20 to 0.25 for design work
catch lead:                     1.45 to 1.55
temporal profile:               gaussian
temporal width:                 0.30 to 0.35
clock-lapse ratio:              0.375
rail-stretch ratio:             0.0
throat-capacity ratio:          0.0
```

For conservative robustness, use:

```text
target max |delta beta_shell|: 0.20
catch lead:                    1.55
temporal width:                0.30
temporal profile:              gaussian
clock-lapse ratio:             0.375
```

For stronger load-bearing with still-clean aggregate behavior, use:

```text
target max |delta beta_shell|: 0.25
catch lead:                    1.45
temporal width:                0.35
temporal profile:              gaussian
clock-lapse ratio:             0.375
```

The `0.30` and `0.35` strength targets should be retained as stress checks. They help reveal where point peaks and shell-throat concentration start to dominate, but the default design center should stay below that edge until richer source objectives and conservation-style checks agree.

## Implications

The active-rail support-shell branch now has a genuine shape-selection result. The smoother radial annulus does what the architecture needs: it lets the extra carrying-flow demand sit in the support-shell bearing layer while keeping the traveler-corridor packet readout quiet and reducing the main source-burden channels. The result aligns with the gradient-matching interpretation developed in the preceding reports. Sharp or poorly matched support-shell edges charge the source ledger; a localized raised-cosine annulus routes the same effective peak support into a much cleaner source pattern.

This result also narrows the design work. The previous same-window throat-capacity screen points away from direct default throat-capacity coupling. The present result says the next improvement should focus on timing and gradient matching of the support-shell window itself, plus richer source diagnostics. Broad radial shells and same-window intrinsic throat response should remain comparator/stress branches.

The branch is ready for the next validation tier as a selected local ansatz. The next tier should combine:

1. richer source-objective accounting around the `0.20` to `0.25` matched-strength band;
2. conservation-style incremental bookkeeping for the selected cases;
3. high-resolution mixed-derivative diagnostics in the shell-throat overlap band;
4. V10 edge stress using the same selected V5 ansatz after the V5 diagnostics remain coherent.

The practical design lesson is direct: the current active-rail service system wants a smooth, localized radial bearing shell, Gaussian catch/rematch timing, moderate matched carrying-flow strength, and clock-lapse coupling. Within that basin, packet safety is robust and the demanded-source cost is much cleaner than the earlier smooth-box support-shell branch.
