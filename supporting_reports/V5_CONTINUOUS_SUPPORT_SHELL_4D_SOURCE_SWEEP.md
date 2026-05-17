# V5 Continuous Support-Shell 4D Source-Ledger Sweep

This report records the first metric-side 4D source-ledger sweep of the frozen V5 support-shell component. The previous reduced ADM screens showed that a direct support-shell carrying-flow window can route incremental ADM `delta_j_l` into catch/rematch support-shell infrastructure while keeping packet `delta_rho` quiet. This round asked a harder question: when the support-shell component is expressed directly in the continuous metric and the demanded source ledger is recomputed from `G_munu[g] / (8*pi)`, does the component become a useful 4D source-redistribution actuator, or does it merely remain packet-safe?

The answer is mixed and important. The continuous support-shell component is robustly packet-safe over a much wider ramp than the frozen target amplitude. But the high-amplitude source-ledger response is not a useful redistribution. It mostly adds demanded-source burden, especially radial null burden, and at negative amplitude can also inflate packet-comoving negative-density burden. Therefore this is not a failure of the frozen small control component, but it is a failure of the single-channel support-shell carrying-flow overlay as a standalone load-bearing 4D source-relief mechanism.

## Continuous Metric Expression

The support-shell component has now been promoted from a grid-only ADM modifier into the source-ledger metric path. The source metric carrying-flow field is split into:

```text
beta(s,l) = beta_base(s,l) + delta_beta_shell(s,l)
```

with:

```text
delta_beta_shell(s,l) = A * W_shell(s,l)
```

where `A` is the support-shell amplitude and `W_shell` is a smooth support-shell/catch/rematch window. The default frozen V5 target is:

```text
amplitude: +1e-7
catch_lead: 1.0
temporal_width: 0.35
smoothness_order: 1
packet_exclusion: 1.0
support_shell_inner_multiplier: 0.65
support_shell_radial_multiplier: 1.20
```

The continuous radial support band is annular rather than disk-like:

```text
0.65 Rth <= |l| <= 1.20 Rth
```

This matters because the reduced harness support-shell mask is not the full support interior. It is the support edge/shell infrastructure. The metric-side source ledger now records:

```text
beta_base
support_shell_window
support_shell_delta_beta
```

so the added metric-side component can be audited separately from the baseline shaped-catch/radial-soft/lapse-cushion branch.

## Harness Changes

This round added or updated the following reusable harness pieces:

- `toolkit/adm_harness_cli/adm_harness/source_ledger.py`
  - adds frozen support-shell overlay parameters to `SourceParams`;
  - defines the continuous support-shell window;
  - adds the overlay to the metric carrying-flow field;
  - records `beta_base`, `support_shell_window`, and `support_shell_delta_beta` in the point ledger.

- `toolkit/adm_harness_cli/scripts/run_source_ledger.py`
  - exposes `--support-shell-overlay`;
  - exposes amplitude, timing, radial-band, smoothing, and packet-exclusion override flags;
  - expands the default `s` range for overlay runs so the leading catch/support window is not clipped.

- `toolkit/adm_harness_cli/scripts/run_source_overlay_sweep.py`
  - runs matched baseline and overlay source ledgers on the same grid;
  - sweeps amplitude/sign/timing parameters;
  - writes a summary table, per-channel burden deltas, failure table, and metadata.

- `toolkit/adm_harness_cli/tests/test_validation_ladder_hardening.py`
  - verifies that overlay source-ledger runs expand the grid when needed;
  - verifies that the overlay modifies `beta` continuously while preserving packet safety on a small grid.

## Sweep Design

The sweep used the V5 tuned branch:

```text
variant: tuned_w0569_eta200
service_factor: 5.0
catch_lead: 1.0
temporal_width: 0.35
smoothness_order: 1
packet_exclusion: 1.0
support-shell band: 0.65 Rth to 1.20 Rth
```

Each overlay case was compared against a matched baseline source ledger on the same grid. The compact ramp used a 27 x 37 grid to scan a broad amplitude range. The high-resolution confirmation used the expanded 53 x 73 grid for amplitudes `0.5` and `1.0`, where the compact run showed the first meaningful 4D source-ledger degradation.

Run outputs:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_compact
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_compact_high_amp
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_highres_check
```

Important readouts:

- `positive_packet_norm_live`
  - hard packet-safety failure count.
- `packet_norm_live_delta_max_abs`
  - max absolute live-packet norm drift from the matched baseline.
- `max_total_burden_ratio`
  - worst global demanded-source burden ratio across channels.
- `max_point_peak_ratio`
  - worst pointwise demanded-source peak ratio across channels.
- `neg_Tkk_radial_total_ratio`
  - radial null-demand ratio.
- `abs_j_l_total_ratio`
  - radial current magnitude ratio.
- `neg_rho_packet_total_ratio`
  - packet-comoving negative-density ratio.

## Compact Ramp Results

The compact ramp tested both signs through amplitude `2.0`.

| amplitude | sign | packet failures | max live packet-norm drift | max `|delta beta_shell|` | max total burden ratio | max point peak ratio | radial null ratio | radial current ratio | packet-comoving negative-density ratio |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|
| `1e-7` | neg | 0 | `1.71131e-08` | `8.05024e-08` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-7` | pos | 0 | `1.70985e-08` | `8.05024e-08` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-6` | neg | 0 | `1.71043e-07` | `8.05024e-07` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-6` | pos | 0 | `1.71029e-07` | `8.05024e-07` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-5` | neg | 0 | `1.71029e-06` | `8.05024e-06` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-5` | pos | 0 | `1.71027e-06` | `8.05024e-06` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-4` | neg | 0 | `1.71028e-05` | `8.05024e-05` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-4` | pos | 0 | `1.71028e-05` | `8.05024e-05` | `1.000000` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |
| `1e-3` | neg | 0 | `1.71028e-04` | `8.05024e-04` | `1.000048` | `1.000000` | `1.000048` | `1.000046` | `1.000000` |
| `1e-3` | pos | 0 | `1.71028e-04` | `8.05024e-04` | `1.000048` | `1.000000` | `1.000048` | `1.000046` | `1.000000` |
| `1e-2` | neg | 0 | `1.71028e-03` | `8.05024e-03` | `1.000823` | `1.000000` | `1.000823` | `1.000705` | `1.000000` |
| `1e-2` | pos | 0 | `1.71028e-03` | `8.05024e-03` | `1.000819` | `1.000000` | `1.000819` | `1.000705` | `1.000000` |
| `5e-2` | neg | 0 | `8.55140e-03` | `4.02512e-02` | `1.004529` | `1.000000` | `1.004529` | `1.003685` | `1.000000` |
| `5e-2` | pos | 0 | `8.55140e-03` | `4.02512e-02` | `1.004516` | `1.000000` | `1.004516` | `1.003685` | `1.000000` |
| `1e-1` | neg | 0 | `1.71028e-02` | `8.05024e-02` | `1.011538` | `1.000000` | `1.009320` | `1.007418` | `1.000000` |
| `1e-1` | pos | 0 | `1.71028e-02` | `8.05024e-02` | `1.011519` | `1.000000` | `1.009296` | `1.007418` | `1.000000` |
| `2.5e-1` | neg | 0 | `4.27570e-02` | `2.01256e-01` | `1.036682` | `1.000000` | `1.024825` | `1.018797` | `1.000000` |
| `2.5e-1` | pos | 0 | `4.27570e-02` | `2.01256e-01` | `1.036634` | `1.000000` | `1.024764` | `1.018797` | `1.000000` |
| `5e-1` | neg | 0 | `8.55139e-02` | `4.02512e-01` | `1.084251` | `1.226755` | `1.054450` | `1.037832` | `1.000000` |
| `5e-1` | pos | 0 | `8.55140e-02` | `4.02512e-01` | `1.084159` | `1.226755` | `1.054324` | `1.037832` | `1.000000` |
| `1.0` | neg | 0 | `1.71028e-01` | `8.05024e-01` | `2.479439` | `2.447045` | `1.132163` | `1.075754` | `2.479439` |
| `1.0` | pos | 0 | `1.71028e-01` | `8.05024e-01` | `1.194545` | `2.447045` | `1.131901` | `1.075752` | `1.000000` |
| `2.0` | neg | 0 | `3.42055e-01` | `1.61005` | `1.446555` | `6.156847` | `1.342846` | `1.150383` | `0.999999` |
| `2.0` | pos | 0 | `3.42057e-01` | `1.61005` | `1.446409` | `6.156847` | `1.342474` | `1.150381` | `1.000001` |

Compact-grid interpretation:

1. Packet safety is robust throughout the tested ramp. There are zero live packet-norm violations through amplitude `2.0`.
2. The frozen target amplitude `1e-7` is effectively invisible in the 4D source ledger. That matches the earlier finding: it is safe and controlled, but not load-bearing in the 4D demanded-source sense.
3. The first visible global source-burden growth begins around `1e-3` to `1e-2`, but is still tiny.
4. By amplitude `0.5`, the source burden has started degrading materially: max total burden ratio is about `1.084`, radial null burden is about `1.054`, and the worst point peak is about `1.227`.
5. By amplitude `1.0`, the negative sign becomes distinctly worse because it inflates packet-comoving negative-density burden. Positive amplitude avoids that particular packet-comoving density spike, but still increases radial null and radial current burdens.
6. By amplitude `2.0`, both signs show large point-peak growth and clear radial null burden growth.

## High-Resolution Confirmation

The high-resolution confirmation reran the interesting amplitudes `0.5` and `1.0` on the expanded 53 x 73 grid.

| amplitude | sign | packet failures | max live packet norm | max live packet-norm drift | max `|delta beta_shell|` | max total burden ratio | max point peak ratio | radial null ratio | radial current ratio | radial pressure ratio | packet-comoving negative-density ratio |
|---:|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `0.5` | neg | 0 | `-255.212` | `0.189770` | `0.402699` | `1.090855` | `1.286096` | `1.056230` | `1.040021` | `1.000013` | `0.999996` |
| `0.5` | pos | 0 | `-255.212` | `0.189771` | `0.402699` | `1.090805` | `1.286096` | `1.056153` | `1.040020` | `1.000013` | `1.000004` |
| `1.0` | neg | 0 | `-255.212` | `0.379539` | `0.805398` | `1.415726` | `2.539049` | `1.133930` | `1.080441` | `1.000050` | `1.415726` |
| `1.0` | pos | 0 | `-255.212` | `0.379542` | `0.805398` | `1.208618` | `2.539049` | `1.133794` | `1.080440` | `1.000050` | `1.000008` |

High-resolution channel deltas:

| amplitude | sign | channel | total burden delta | total burden ratio | live packet burden delta | live packet burden ratio | point peak ratio |
|---:|:---|:---|---:|---:|---:|---:|---:|
| `0.5` | neg | `abs_j_l` | `0.0104543` | `1.040021` | `4.42886e-11` | `1.000000` | `1.000000` |
| `0.5` | neg | `abs_p_l` | `0.00110122` | `1.000013` | `-1.49416e-10` | `1.000000` | `1.000000` |
| `0.5` | neg | `neg_Tkk_radial` | `25.6951` | `1.056230` | `-2.04539e-05` | `1.000000` | `1.286096` |
| `0.5` | neg | `neg_rho_packet` | `-3.78695e-06` | `0.999996` | `0` | n/a | `1.000000` |
| `0.5` | pos | `abs_j_l` | `0.0104541` | `1.040020` | `-4.42920e-11` | `1.000000` | `1.000000` |
| `0.5` | pos | `abs_p_l` | `0.00110122` | `1.000013` | `1.49416e-10` | `1.000000` | `1.000000` |
| `0.5` | pos | `neg_Tkk_radial` | `25.6601` | `1.056153` | `2.04527e-05` | `1.000000` | `1.286096` |
| `0.5` | pos | `neg_rho_packet` | `3.78737e-06` | `1.000004` | `0` | n/a | `1.000000` |
| `1.0` | neg | `abs_j_l` | `0.0210131` | `1.080441` | `8.85736e-11` | `1.000000` | `1.000000` |
| `1.0` | neg | `abs_p_l` | `0.00440187` | `1.000050` | `-2.98829e-10` | `1.000000` | `1.000000` |
| `1.0` | neg | `neg_Tkk_radial` | `61.2012` | `1.133930` | `-4.09092e-05` | `1.000000` | `2.539049` |
| `1.0` | neg | `neg_rho_packet` | `0.397171` | `1.415726` | `0` | n/a | `1.000000` |
| `1.0` | pos | `abs_j_l` | `0.0210128` | `1.080440` | `-8.85878e-11` | `1.000000` | `1.000000` |
| `1.0` | pos | `abs_p_l` | `0.00440186` | `1.000050` | `2.98833e-10` | `1.000000` | `1.000000` |
| `1.0` | pos | `neg_Tkk_radial` | `61.1391` | `1.133794` | `4.09042e-05` | `1.000000` | `2.539049` |
| `1.0` | pos | `neg_rho_packet` | `7.57517e-06` | `1.000008` | `0` | n/a | `1.000000` |

High-resolution interpretation:

1. The compact-grid degradation pattern survives the finer check.
2. Packet safety remains robust at amplitudes far beyond the frozen target.
3. The high-amplitude support-shell overlay does not reduce the main 4D source burdens.
4. Radial null burden increases materially.
5. Radial current burden increases moderately.
6. Radial pressure barely changes.
7. Positive amplitude remains the better sign at high amplitude because negative amplitude can add a packet-comoving negative-density burden spike.

## What Passed

The continuous support-shell metric expression passed the packet-safety test. This is not trivial. The support-shell overlay can be increased by many orders of magnitude above the frozen `1e-7` target without producing live packet-norm violations at V5 on the tested grids. The packet corridor remains protected by the annular support placement and packet-exclusion structure.

The component is also controllable. The metric-side contribution scales cleanly with amplitude, and live packet-norm drift scales in the expected way. There is no chaotic threshold or immediate metric breakdown in the tested range.

The sign result is now clearer than it was in the tiny-control regime. At frozen amplitude the sign is effectively a tie-breaker. At high amplitude, positive remains safer because it avoids the negative sign's packet-comoving negative-density burden growth at amplitude `1.0`.

## What Failed

The high-amplitude continuous support-shell carrying-flow overlay did not produce a strong 4D demanded-source redistribution. In a successful load-bearing redistribution, we would expect some expensive source burden to move out of the packet corridor or out of the harder null/current channels and into benign support-shell infrastructure. Instead, the higher-amplitude overlay mostly adds demanded-source burden.

The clearest failure channel is radial null demand. On the high-resolution grid, amplitude `1.0` increases `neg_Tkk_radial` total burden by about `13.4%` for both signs, and the worst point peak rises by about `2.54x`. That is not relief. It is an added null-exposure cost.

The negative sign also produces a distinct packet-comoving density penalty at amplitude `1.0`: `neg_rho_packet_total_ratio = 1.415726`. The positive sign does not show that spike, which makes positive the better high-amplitude sign. But positive amplitude still increases the radial null and radial current burdens, so the sign preference does not rescue the single-channel overlay as a load-bearing source-redistribution mechanism.

## Design Interpretation

This is a partial design failure, not a full architecture failure.

It is not a failure of the frozen small support-shell target. The frozen target was selected as a low-amplitude, packet-quiet, support-localized control component in the reduced ADM ladder. The 4D source-ledger result agrees that it is packet-safe and essentially non-disruptive.

It is a failure of the stronger single-channel hypothesis:

```text
If we make the support-shell carrying-flow overlay larger, it will become a useful 4D source-relief or source-redistribution actuator.
```

The data do not support that. Larger single-channel carrying-flow support-shell overlays create added 4D demanded-source cost. They preserve packet safety, but they do not improve the source ledger.

The likely reason is structural. The overlay changes the off-diagonal carrying-flow part of the metric while leaving the clock-lapse, rail-stretch, and throat-capacity parts unchanged. The source ledger then sees gradients and curvature associated with an added carrying-flow feature, but not the compensating metric structure that would make that feature source-cheaper. A standalone carrying-flow shell is therefore too one-sided to carry load in the full 4D source ledger.

## Implications For The Active-Rail Design

The active-rail architecture still has a viable support-shell service component. It remains useful as a small, controlled support-shell placement element. It should stay in the frozen V5 branch as a packet-safe support/control overlay.

The architecture should not treat that component as the main 4D source-redistribution mechanism. The main load-bearing refinement probably has to be coupled: carrying-flow plus clock-lapse and/or rail-stretch and/or throat-capacity changes with matched gradients.

The reduced ADM support-shell routing result is still informative, but it is not enough by itself for source feasibility. It told us that the harness can place an incremental ADM burden in support infrastructure. The 4D sweep now tells us that making the corresponding single-channel metric component large does not automatically create a better demanded-source distribution.

## Refinement Directions

The next design stage should stop asking whether the single support-shell carrying-flow overlay can become load-bearing by amplitude alone. It cannot, at least not in this form. The better question is which coupled metric family can preserve the packet-safe support placement while reducing the radial null/current penalty introduced by carrying-flow gradients.

Candidate refinements:

1. Coupled carrying-flow and clock-lapse shell

   Add a clock-lapse partner with the same support-shell timing and radial band. The purpose would be to offset the radial-null exposure caused by the carrying-flow gradient. This is the most natural first refinement because packet norm depends strongly on both carrying-flow and lapse. The test should sweep paired amplitudes, not just independent amplitudes.

2. Coupled carrying-flow and rail-stretch shell

   Add a rail-stretch partner so the support-shell region changes its radial metric capacity while carrying-flow is adjusted. This may reduce radial current/null cost by changing the metric channel in which the carrying-flow gradient is expressed.

3. Support-shell transition broadening

   The high-amplitude penalty is likely gradient-driven. Broader radial and temporal shoulders may reduce point peaks and radial null spikes. This should be tested as a source-ledger convergence question, not only as a reduced ADM routing question.

4. Two-lobe or balanced carrying-flow shell

   Instead of one same-sign support-shell addition, use a balanced shell with an inner/outer compensation lobe so the net carrying-flow addition has smaller large-scale curvature cost. This may preserve local support-shell action while lowering global burden growth.

5. Source-aware objective optimization

   Build a 4D source-ledger objective directly around `neg_Tkk_radial`, `abs_j_l`, `neg_rho_packet`, packet norm, and support-region localization. The reduced ADM objective was enough to choose placement; the 4D objective is needed to tune metric-family coupling.

6. Positive-sign branch as the only high-amplitude branch

   Negative amplitude is still useful as a comparator, but high-amplitude negative runs should not be a serious candidate unless a coupled partner removes the packet-comoving density penalty. Positive is the safer default.

## Recommended Next Test

The next test should be a small coupled metric-side sweep at V5:

```text
carrying_flow amplitude: 0.05, 0.1, 0.25, 0.5
clock_lapse partner amplitude: signed ratios against carrying_flow
rail_stretch partner amplitude: optional second axis or separate follow-up
catch_lead: 1.0
temporal_width: 0.35 and 0.50
support band: 0.65 Rth to 1.20 Rth, plus one broader radial edge
```

Gate it on:

```text
positive_packet_norm_live == 0
max live packet-norm drift bounded
neg_Tkk_radial total ratio not increasing
abs_j_l total ratio not increasing materially
neg_rho_packet total ratio not increasing
point peaks not increasing
```

The goal is not to find a higher-amplitude support-shell overlay. The goal is to find a coupled support-shell metric family whose demanded-source response is not additive in the radial null/current channels.

## Bottom Line

This round turns the support-shell story from "maybe the control overlay can be made load-bearing by amplitude" into a sharper statement:

```text
The frozen support-shell carrying-flow overlay is packet-safe and controllable.
It is not, by itself, a strong 4D source-redistribution mechanism.
Load-bearing redistribution likely requires coupled metric shaping.
```

That is a design constraint, not a dead end. It narrows the next search substantially.
