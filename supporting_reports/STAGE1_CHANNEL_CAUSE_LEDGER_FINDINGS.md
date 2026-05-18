# Stage I Channel-Cause Ledger Findings

## Purpose

This pass added a focused diagnostic ledger for the current V5 refreeze branch. The goal was not to make the current branch suddenly work by tuning the same release knobs harder. The goal was to identify what channel family is actually producing the remaining hard points:

```text
beta-gradient dominated
lapse-curvature dominated
radial-metric dominated
angular-capacity dominated
cancellation dominated
```

The diagnostic was run against the two current high-resolution V5 reference cases:

```text
toolkit/adm_harness_cli/runs/stage1_v5_blend_width16_highres_current_code/
toolkit/adm_harness_cli/runs/stage1_v5_infra_coordinated_lapse_highres/
```

## Harness Change

The source-ledger module now includes a channel-cause ledger. For each selected top bad point it records the local projected source pieces:

```text
rho_H
p_l
j_l
rho_H + p_l
2 j_l
Tkk_plus_orthonormal
Tkk_minus_orthonormal
```

It also reconstructs the radial null projections from the orthonormal ADM pieces:

```text
Tkk_plus / alpha^2  = rho_H + p_l - 2 j_l
Tkk_minus / alpha^2 = rho_H + p_l + 2 j_l
```

and records local finite-difference derivative diagnostics:

```text
d_s alpha,          d_l alpha,          d_l^2 alpha
d_s beta^l,         d_l beta^l,         d_l^2 beta^l
d_s gamma_ll,       d_l gamma_ll,       d_l^2 gamma_ll
d_s gamma_Omega,    d_l gamma_Omega,    d_l^2 gamma_Omega
```

The helper runner is:

```text
toolkit/adm_harness_cli/scripts/run_channel_cause_ledger.py
```

It consumes an existing `run_source_ledger.py` output directory and writes:

```text
source_ledger_channel_cause.csv
source_ledger_channel_cause.manifest.json
```

This is intentionally a cheap diagnostic pass. It reuses existing point ledgers and only evaluates derivative-origin diagnostics at the top selected bad points.

## Runs

Commands:

```bash
cd toolkit/adm_harness_cli

python scripts/run_channel_cause_ledger.py \
  --ledger-dir runs/stage1_v5_blend_width16_highres_current_code \
  --limit-per-channel 20 \
  --channels neg_Tkk_radial abs_p_l abs_j_l abs_pOmega

python scripts/run_channel_cause_ledger.py \
  --ledger-dir runs/stage1_v5_infra_coordinated_lapse_highres \
  --limit-per-channel 20 \
  --channels neg_Tkk_radial abs_p_l abs_j_l abs_pOmega
```

Both runs produced 80 rows: four channels times the top 20 points.

## Blend Width 1.6 Baseline

Top-point channel summary:

```text
channel          live rows   worst badness   dominant finding
abs_j_l          20 / 20     0.031188        radial_metric, 20 / 20
abs_pOmega       20 / 20     0.570530        radial_metric, 20 / 20
abs_p_l           0 / 20     0.009521        radial_metric, 20 / 20
neg_Tkk_radial    0 / 20     0.224899        radial_metric, 18 / 20
```

The remaining radial-null hard points are non-live catch/rematch infrastructure:

```text
neg_Tkk_radial:
  catch_rematch / core_throat: 15
  catch_rematch / support_edge: 5
```

The live bad points are not in the radial-null channel. They are mainly packet-in-support angular/current channels:

```text
abs_j_l:
  entry_precatch / packet_in_support: 20 live rows

abs_pOmega:
  entry_precatch / packet_in_support: 20 live rows
```

This says the current refreeze has a coherent packet-norm structure, but the source burden still enters through radial support geometry and its coupling to live angular/current channels.

## Coordinated-Lapse Diagnostic

Top-point channel summary:

```text
channel          live rows   worst badness   dominant finding
abs_j_l          20 / 20     0.031243        radial_metric, 20 / 20
abs_pOmega       20 / 20     0.684952        radial_metric, 20 / 20
abs_p_l           0 / 20     0.009521        radial_metric, 20 / 20
neg_Tkk_radial    0 / 20     0.253209        radial_metric, 20 / 20
```

The coordinated-lapse branch keeps the same non-live radial-null concentration:

```text
neg_Tkk_radial:
  catch_rematch / core_throat: 16
  catch_rematch / support_edge: 4
```

but it moves more live angular-pressure burden into the post-release support region:

```text
abs_pOmega:
  entry_precatch / packet_in_support: 5
  catch_rematch / packet_in_support: 6
  post_release_buffer / packet_in_support: 9
```

This confirms the earlier derivative-smoothing interpretation. Coordinated lapse is useful as a diagnostic because it shows that lapse can trim one radial-null symptom, but it is too broad or too steep as a release driver. It worsens live angular pressure and does not address the underlying radial-metric origin.

## Interpretation

The cause ledger points away from:

```text
stronger beta rematch
V-aware beta timing as the next first move
full coordinated lapse release as the main branch
coordinated carve release as the main branch
```

It points toward:

```text
refining the radial support law itself
```

The current branch did not fail because release choreography is meaningless. It failed because the placeholder radial support geometry is now the weak stand-in. The active branch has reached the point where naive infrastructure profiles are no longer adequate.

The favorable sign is locality. The remaining burden is structured rather than smeared everywhere. The bad points concentrate in:

```text
catch_rematch / core_throat
catch_rematch / support_edge
live packet_in_support angular/current rows
```

That means the next design can target the region and scale of the exotic support more surgically. The unfavorable sign is coupling: when lapse is used as a broad driver, angular/live channels react. That means the next law must place support geometrically rather than merely hiding one channel with another.

## Recommended Next Work

Start a refined radial support law branch. Keep the current V5 candidate as the base:

```text
standing_support_packet_beta_rematch_floor_mode = blend
standing_support_packet_beta_rematch_shape = trailing_edge
standing_support_packet_beta_rematch_width_multiplier = 1.6
standing_support_packet_beta_rematch_schedule = live_only
standing_support_packet_exclusion_schedule = live_only
standing_support_packet_exclusion_shoulder_schedule = live_only
standing_support_packet_lapse_schedule = entry_catch_release
```

Then improve the support geometry rather than the release driver:

```text
smooth gamma_ll / rail-stretch joins
soften support-shell radial shoulders
separate core-throat smoothing from packet-edge smoothing
keep carve live through transport/catch, but smooth its shoulder
use coordinated lapse only later as a small local null-channel cushion constrained against live p_l
```

The viability gate is now sharper:

```text
If refined radial support reduces non-live hard Tkk without raising live pOmega and j_l, the active-rail V5 design path remains serious.

If smoothing the support geometry merely transfers the same burden into live angular/current channels, the required exotic support may be too tightly coupled to the packet geometry at this scale.
```

## Verification

```text
python -m py_compile adm_harness/source_ledger.py scripts/run_channel_cause_ledger.py
python -m unittest tests.test_validation_ladder_hardening
```

Result:

```text
Ran 17 tests
OK
```
