# Stage I Current Candidate Algebra Ledger

## Purpose

This pass ran the focused algebra ledger on the current two-feature radial support candidate instead of the older blend-only release branch. The goal was to ask what the current surviving V5 architecture is actually saying at the top hard points:

```text
Is the remaining burden still the radial support law?
Is it packet beta rematch?
Is it packet carve/lapse support?
Is it cancellation-sensitive radial-null algebra?
Is there a separated design knob left, or are we at diminishing returns?
```

The run was not a broad design sweep. It was an algebraic readout of the current V5 operating embodiment after the radial support core/ring/skirt improvements.

## Current Candidate Tested

The ledger used the current V5 high-resolution operating family:

```text
matched-hold release choreography
minimum-jerk beta fade
support shell amplitude 0.5 with clock-lapse partner 0.1875
packet carve 0.90 with annular carve shoulder 0.18
packet lapse log gain 1.0 on entry/catch/release timing
trailing-edge beta rematch gain 1.8
smooth blended beta floor 0.60
beta sleeve width multiplier 1.6
radial core +0.05 on entry/catch/release
annular radial ring +0.12 on catch-only radius/width 2.4 / 2.4
weak annular radial skirt +0.05 on catch-only inner/outer/width 2.4 / 2.6 / 3.2
```

Output directory:

```text
toolkit/adm_harness_cli/runs/stage1_v5_two_feature_radial_current_ledger/
```

The full source ledger used:

```text
grid: 81 x 109
s range: -0.96 to 1.65
l range: -2.80 to 2.80
rows: 8829
```

The focused channel-cause ledger used the top 30 rows in each channel:

```text
neg_Tkk_radial
abs_p_l
abs_j_l
abs_pOmega
```

## Safety and Global Ledger

The current family remains packet-safe on this full-range high-resolution ledger:

```text
live packet points:          932
positive live packet-norm:   0
max live packet norm:        -5.455491
```

Global compact summary:

```text
channel          total burden   live burden   live fraction   point peak   live point peak
neg_Tkk_radial   403.053712      9.714007      0.024101        1.289256     1.289256
abs_p_l           56.501596      0.396128      0.007011        0.070877     0.070877
abs_pOmega         7.363524      2.746906      0.373042        0.570530     0.570530
abs_j_l            0.371371      0.119451      0.321649        0.031188     0.031188
neg_rho_euler      0.445257      0.000176      0.000395        0.012380     0.001353
neg_rho_packet     0.644673      0.002282      0.003540        0.535333     0.007205
```

Relative to the prior blend-width reference ledger, the current two-feature radial candidate:

```text
lowers radial-null point peak by about 4.0 percent;
lowers live pOmega burden by about 2.45 percent;
lowers live j_l burden slightly;
lowers live negative Eulerian density and packet-comoving density;
slightly raises total and live p_l burden;
leaves the pOmega and j_l point peaks controlled by the same early live packet rows.
```

## Channel-Cause Summary

Top-point cause summary:

```text
channel          live rows   geometric packet rows   dominant derivative finding
abs_j_l          30 / 30     30 / 30                 radial_metric, 30 / 30
abs_pOmega       30 / 30     30 / 30                 radial_metric, 30 / 30
abs_p_l           0 / 30      0 / 30                 radial_metric 19 / 30, lapse_curvature 11 / 30
neg_Tkk_radial    0 / 30      0 / 30                 radial_metric 29 / 30, lapse_curvature 1 / 30
```

The dominant derivative label remains `radial_metric`, but the location and window values matter. The live angular/current rows and the non-live radial-null rows are not the same mechanism.

## Live Angular and Current Rows

The worst live `abs_pOmega` and `abs_j_l` rows live in:

```text
entry_precatch / packet_in_support
```

At the top live angular/current points, the radial support features are essentially inactive:

```text
standing_support_packet_radial_window:          0
standing_support_packet_radial_shoulder_window: 0
standing_support_packet_radial_skirt_window:    0
standing_support_packet_radial_factor:          1
```

But the packet carve and beta rematch are active:

```text
packet carve window:        about 0.85 to 0.96
beta-rematch window:        about 0.62 to 0.70
lapse window:               small, about 0.0008 to 0.014
support-shell window:       negligible
release-profile slope:      0
```

This is the key algebraic result. The worst live pOmega/j_l peaks are not caused by the new radial core/ring/skirt profile. They occur before that radial profile turns on. The current live angular/current ceiling is produced by the early packet-in-support combination of:

```text
large baseline gamma_ll curvature;
active packet carve;
active packet beta rematch;
small or negligible radial-support contribution;
small or negligible support-shell overlay contribution.
```

The top live `abs_pOmega` point has:

```text
s = -0.927375
l = -1.140741
stage / region = entry_precatch / packet_in_support
pOmega = -0.570530
j_l = -0.025682
rho_H + p_l = 0.070233
2 j_l = -0.051363
radial metric score = 34.020602
lapse curvature score = 14.902529
beta gradient score = 11.996448
angular capacity score = 0.970902
```

The top live `abs_j_l` point has:

```text
s = -0.960000
l = -1.192593
stage / region = entry_precatch / packet_in_support
j_l = -0.031188
pOmega = -0.520274
rho_H + p_l = 0.088038
2 j_l = -0.062377
radial metric score = 43.874296
lapse curvature score = 19.091304
beta gradient score = 16.082077
angular capacity score = 0.954845
```

The angular/current hard rows are partially cancellation-sensitive in the null reconstruction, but their actual channel peaks are not radial-null failures. They are live angular/current exposure in the early packet support region.

## Non-Live Radial-Null Rows

The top radial-null rows live outside the live packet:

```text
catch_rematch / core_throat: 22 / 30
catch_rematch / support_edge: 6 / 30
entry_precatch / support_edge: 2 / 30
```

The top radial-null point is:

```text
s = 0.377625
l = 0.985185
stage / region = catch_rematch / core_throat
bad neg_Tkk_radial = 0.210382
rho_H = 0.007462
p_l = -0.007462
rho_H + p_l = -4.603e-7
2 j_l = 2.200e-6
Tkk_plus / alpha^2 = -2.657e-6
Tkk_minus / alpha^2 = 1.737e-6
null cancellation ratio = 0.998726
```

This is not a large local orthonormal null imbalance. It is a small null residual in a region with very large lapse/metric amplification. The row is not cancellation-sensitive by the ledger threshold; rather, the orthonormal pieces show that `rho_H` and `p_l` nearly cancel while a small `j_l` term selects the bad radial null branch. The coordinate `Tkk` peak is large because the local metric scale is large, not because the local ADM pieces are huge.

The top `abs_p_l` rows are also non-live and concentrated in:

```text
catch_rematch / core_throat
entry_precatch / core_throat
```

They are dominated by `rho_H = -p_l` structure with nearly zero `j_l`, again indicating a throat/core radial-metric balance rather than a packet-current failure.

## Local Perturbation Checks

A few local checks at the top points show which knobs are coupled to which symptoms.

At the top live `abs_pOmega` point:

```text
lower beta rematch gain from 1.8 to 1.4:
  pOmega drops by 0.446
  j_l drops by 0.0074
  p_l drops by 0.0143
  local packet norm becomes more negative

reduce beta floor from 0.60 to 0.30:
  pOmega drops by 0.0897
  j_l drops by 0.0110
  p_l drops by 0.0167

reduce packet carve from 0.90 to 0.70:
  pOmega drops by 0.561
  j_l drops by 0.0250
  p_l drops by 0.0159
  local radial-null burden appears

make packet lapse live-only at this point:
  pOmega drops by 0.510
  j_l drops by 0.0162
  p_l drops by 0.0223
  local radial-null burden appears
```

At the top non-live radial-null point:

```text
change beta-rematch gain or beta floor:
  almost no effect

reduce packet carve:
  almost no effect

lower packet lapse gain from 1.0 to 0.8:
  radial-null badness drops by about 0.039

raise packet lapse gain from 1.0 to 1.2:
  radial-null badness rises by about 0.050
```

Thus the live angular/current peak and the non-live radial-null peak are separated. The live peak responds strongly to carve/beta-rematch structure. The non-live radial-null peak responds more to local lapse scaling and radial-metric amplification.

## Low-Resolution Case-Level Probe

A small full-range `31 x 55` screen checked whether the local signal survives as a case-level trend. It should not be treated as a selected design, but it clarifies the tradeoff.

```text
current:
  positive live packet norm:     0
  max live packet norm:          -5.483597
  pOmega peak:                   0.543241
  j_l peak:                      0.028443
  p_l peak:                      0.066059
  neg_Tkk peak:                  1.227705

beta gain 1.4:
  positive live packet norm:     2
  pOmega peak ratio:             0.546
  j_l peak ratio:                0.737
  p_l peak ratio:                0.649
  neg_rho_packet live burden:    about 48x current

beta floor 0.3:
  positive live packet norm:     19
  pOmega peak ratio:             0.704
  j_l peak ratio:                0.764
  p_l peak ratio:                0.361

carve 0.7:
  positive live packet norm:     0
  max live packet norm:          -50.178381
  pOmega peak ratio:             0.152
  j_l peak ratio:                0.317
  p_l peak ratio:                0.175
  neg_Tkk peak ratio:            0.658
  live neg_Tkk burden ratio:     1.353
  live p_l burden ratio:         2.087

lapse live-only:
  positive live packet norm:     0
  max live packet norm:          -23.082264
  pOmega peak ratio:             0.419
  j_l peak ratio:                0.391
  p_l peak ratio:                0.292
  neg_Tkk peak ratio:            2.009
```

The case-level probe confirms the separation:

```text
weaker beta rematch improves source channels but loses packet safety;
weaker carve preserves packet safety and dramatically reduces point peaks, but raises live integrated Tkk and p_l exposure;
live-only lapse improves angular/current/pressure point peaks but sharply worsens radial-null point peak;
there is no one-knob free lunch.
```

## Interpretation

The current branch is not out of ideas. It is out of easy single-knob radial-profile gains.

The radial core/ring/skirt profile is doing useful fine-trim work, but the worst live angular/current peaks occur before the new radial support profile is active. Those peaks are early-entry packet-in-support effects dominated by radial metric derivatives under active packet carve and beta-rematch windows.

The non-live radial-null peaks are separate. They are catch/rematch core-throat/support-edge rows where small orthonormal null residuals are amplified by local lapse/metric scale. Those points are not primarily solved by lowering beta rematch or by broad radial skirts.

This means the Stage I architecture remains viable in a meaningful sense: the packet safety architecture is robust at V5, the expensive channels are structured and local, and the remaining hard points are not smeared through the live packet. But the architecture is not yet sealed as an optimized hard-bounded source-placement design because live angular/current peaks and non-live radial-null peaks are being controlled by different algebraic mechanisms.

## Recommended Next Design Move

The next design move should be a refined carve/support containment law, not another broad radial skirt.

The most promising direction is to separate packet carve/support into at least two timed roles:

```text
1. softer early live-entry containment, where the current carve/beta-rematch combination creates pOmega and j_l peaks;
2. stronger catch/rematch containment, where packet safety and radial-null exposure still require support.
```

Then add only a small local null-channel cushion where the reduced-carve branch exposes live Tkk or p_l burden. That cushion should be constrained against live p_l and should not become a broad lapse release driver.

Operationally, the next harness branch should test:

```text
two-stage packet carve schedule;
entry/catch separated carve amplitudes;
entry-soft / catch-strong carve shoulder;
beta-rematch safety recovery only where reduced carve weakens packet norm;
local lapse/null cushion only in the exposed catch/support region;
same V5 hard gates, with V10 retained as an edge smoke after V5 cleanup.
```

This is a stronger design target than simply adding more radial geometry. The algebra says the remaining live peak is a packet containment/choreography problem, while the non-live radial-null peak is a local null-balance/amplification problem.

## Verification

Commands run:

```text
python scripts/run_source_ledger.py ... --outdir runs/stage1_v5_two_feature_radial_current_ledger --ns 81 --nl 109 --s-min -0.96 --force --quiet

python scripts/run_channel_cause_ledger.py \
  --ledger-dir runs/stage1_v5_two_feature_radial_current_ledger \
  --limit-per-channel 30 \
  --channels neg_Tkk_radial abs_p_l abs_j_l abs_pOmega
```

Results:

```text
source-ledger rows:       8829
channel-cause rows:       120
positive packet failures: 0
```
