# ADM Harness CLI service v0.5 self-contained

This package contains the active-rail ADM harness CLI, relative-path V=5 configs, tests, and a small prepared V=5 sample dataset. It should run immediately after unzip.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## Run the built-in tests

```bash
python -m unittest discover -s tests
```

## Validate configs

```bash
python -m adm_harness.cli validate -c configs/v5_service_baseline.yaml --output-json runs/validation_baseline.json
python -m adm_harness.cli validate -c configs/v5_service_flow_off.yaml --output-json runs/validation_flow_off.json
python -m adm_harness.cli validate -c configs/v5_service_identity_synthesis.yaml --output-json runs/validation_identity.json
python -m adm_harness.cli validate -c configs/v5_service_carrying_flow_localizer.yaml --output-json runs/validation_localizer.json
```

## Run the smoke suite

```bash
python -m adm_harness.cli run -c configs/v5_service_baseline.yaml
python -m adm_harness.cli run -c configs/v5_service_flow_off.yaml
python -m adm_harness.cli run -c configs/v5_service_identity_synthesis.yaml
python -m adm_harness.cli run -c configs/v5_service_carrying_flow_localizer.yaml
python -m adm_harness.cli compare --runs runs/v5_service_flow_off runs/v5_service_identity_synthesis runs/v5_service_carrying_flow_localizer --output-dir runs/comparison_v5_smoke
```

Or run the same sequence with:

```bash
bash scripts/run_local_smoke.sh
```

## Run the validation ladder

The support-shell target can be checked with the staged validation ladder. The default run is the primary `V=5` service-factor case:

```bash
python scripts/run_validation_ladder.py
```

This runs the flow-off baseline, the promoted positive support-shell target, a generated negative counterpart, the packet-safety overlay on the matching tuned branch, the richer multi-channel source objective, the signed source/objective comparison, reduced balance bookkeeping, and a positive-amplitude load-bearing ramp. Outputs are written to `runs/<v_label>_validation_ladder/` unless `--output-root` is set.

For the `V=10` edge comparison, the same command infers the `V10` packet member and output directory from the configs:

```bash
python scripts/run_validation_ladder.py \
  --baseline-config configs/v10_service_flow_off.yaml \
  --target-config configs/v10_service_support_shell_target.yaml \
  --max-packet-j-fraction 1e-4 \
  --max-packet-abs-delta-rho 1e-12 \
  --max-rich-packet-increment-abs 1e-10
```

The old `scripts/run_v5_validation_ladder.py` entry point remains as a compatibility wrapper.

### Generate arbitrary service-factor inputs

For an intermediate or exploratory `V` value, the ladder can generate reduced ADM exact-field, substrate-subtraction, point-ledger, and config inputs before it runs:

```bash
python scripts/run_validation_ladder.py \
  --service-factor 7 \
  --generate-service-inputs \
  --skip-amplitude-ramp
```

The generated products are written under `data/generated_service_factors/<v_label>/` and `configs/generated/`, then the ladder consumes those products directly. This path is intended for service-factor hardening and interpolation checks between the tracked reference products. It uses the reduced ADM field builder; pressure/null 4D source projections remain separate heavier diagnostics.

Useful low-cost diagnostics are recorded in `validation_ladder_metadata.json` and `validation_ladder_decision_sheet.csv`, including generated-input provenance, packet norm counts, packet/source fractions, partition closure, and a `gate_margin` value for each hard decision row.

## Regenerate the 4D demanded-source ledger

The report-grade source ledger can be regenerated from the toolkit, rather than treated as an opaque bundle-only artifact:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --outdir runs/source_ledgers/V5_tuned_w0569_eta200
```

This computes the finite-difference demanded-source projections `T_munu = G_munu[g] / (8*pi)`, then writes point, summary, stage, safety, decision, top-bad-point, and manifest tables. Use `--reference` to compare a regenerated ledger to a saved artifact:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --reference ../../included_bundles/active_rail_v_sweep.zip::highres_41x73/V5_tuned_w0569_eta200.csv \
  --reference-case V5_tuned_w0569_eta200
```

The frozen support-shell carrying-flow overlay can be included directly in the metric expression:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --support-shell-overlay \
  --outdir runs/source_ledgers/V5_tuned_w0569_eta200_support_shell
```

The overlay defaults to the frozen reduced-harness target: amplitude `1e-7`, catch lead `1.0`, temporal width `0.35`, smoothness order `1`, packet exclusion `1.0`, and an annular support-shell band from `0.65 Rth` to `1.20 Rth`. The point ledger records `beta_base`, `support_shell_window`, and `support_shell_delta_beta` so the metric-side contribution can be audited separately from the baseline shaped-catch/radial-soft/lapse-cushion branch.

Overlay runs expand the default `s` range when needed to include the leading catch/support window while preserving roughly the standard `ds = 0.05` sampling. Pin `--s-min` and `--ns` explicitly when comparing against a fixed historical source-ledger grid.

Dense source-ledger grids can split the independent `s` rows across local worker processes:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --ns 377 \
  --nl 241 \
  --jobs 8 \
  --outdir runs/source_ledgers/V5_tuned_w0569_eta200_dense
```

The parallel path preserves the same point-ledger schema and downstream summary files as the serial path. By default `--jobs N` uses `4*N` contiguous `s`-row shards, capped at `ns`; set `--s-shards` explicitly when you want coarser or finer progress checkpoints. The beta-collar manifest regenerator has the same `--jobs` and `--s-shards` controls, so dense endpoint-source rungs can use parallel source construction and then feed the resulting ledger directory into the existing component, string-cloud, intermediate, structured-source, and closure diagnostics unchanged.

To ramp the continuous overlay and compare each case against a matched baseline source ledger:

```bash
python scripts/run_source_overlay_sweep.py \
  --outdir runs/source_overlay_sweep_v5 \
  --amplitudes 1e-7 1e-6 1e-5 1e-4 1e-3 1e-2 \
  --signs pos neg
```

Coupled metric-side timing/refinement sweeps can add support-shell clock-lapse and rail-stretch partners as log-gain ratios against the signed carrying-flow amplitude:

```bash
python scripts/run_source_overlay_sweep.py \
  --outdir runs/source_overlay_sweep_v5_coupled \
  --amplitudes 0.5 \
  --signs pos \
  --catch-leads 1.0 1.25 \
  --temporal-widths 0.35 0.5 \
  --clock-lapse-ratios 0 0.25 0.5 \
  --rail-stretch-ratios 0 0.5
```

The same sweep driver also supports a throat-capacity partner, parallel execution, resumable per-case outputs, and a source-objective ranking table:

```bash
python scripts/run_source_overlay_sweep.py \
  --outdir runs/source_overlay_sweep_v5_throat_capacity \
  --amplitudes 0.5 \
  --signs pos \
  --catch-leads 1.45 1.55 \
  --temporal-widths 0.30 \
  --clock-lapse-ratios 0.375 0.5 \
  --rail-stretch-ratios 0 \
  --throat-capacity-ratios -0.5 -0.25 0 0.25 0.5 \
  --jobs 4 \
  --case-output \
  --resume
```

The throat-capacity ratio is a log-gain against the signed carrying-flow amplitude applied to `gamma_omega`. The summary table includes `support_shell_delta_gamma_omega_abs_max`, channel ratios for angular pressure, named source-objective sub-scores, and `source_objective_score`. The sorted objective table is written to `source_overlay_sweep_objective_ranking.csv`.

Shape-selection sweeps can vary the support-shell temporal and radial window families while keeping the same coupled metric amplitudes:

```bash
python scripts/run_source_overlay_sweep.py \
  --outdir runs/source_overlay_sweep_v5_shape_screen \
  --amplitudes 0.5 \
  --signs pos \
  --catch-leads 1.45 1.55 \
  --temporal-widths 0.25 0.30 0.35 \
  --temporal-profiles gaussian raised_cosine minjerk_pulse \
  --radial-profiles smooth_box raised_cosine_annulus \
  --clock-lapse-ratios 0.375 0.5 \
  --rail-stretch-ratios 0 \
  --throat-capacity-ratios 0 \
  --jobs 4 \
  --case-output \
  --resume
```

The default `gaussian` temporal profile and `smooth_box` radial profile preserve the earlier support-shell window. Compact temporal profiles are normalized against the active catch/rematch edge, so they remain usable when the nominal support-shell center is earlier than the catch/rematch band. The radial profile options are `smooth_box`, `gaussian_annulus`, and `raised_cosine_annulus`.

For fair shape comparisons, use `--target-delta-beta-abs-max` to normalize each case to the same effective peak support-shell carrying-flow strength:

```bash
python scripts/run_source_overlay_sweep.py \
  --outdir runs/source_overlay_sweep_v5_shape_normalized \
  --amplitudes 0.5 \
  --target-delta-beta-abs-max 0.15 0.20 0.25 0.30 0.35 \
  --signs pos \
  --catch-leads 1.45 1.55 \
  --temporal-widths 0.25 0.30 \
  --temporal-profiles gaussian minjerk_pulse \
  --radial-profiles smooth_box raised_cosine_annulus \
  --clock-lapse-ratios 0.375 0.5 \
  --rail-stretch-ratios 0 \
  --throat-capacity-ratios 0 \
  --jobs 4 \
  --case-output \
  --resume
```

The nominal value passed through `--amplitudes` remains in the output as `nominal_abs_amplitude`; the normalized per-case value is written as `abs_amplitude`, with each matching target and measured window peak recorded in `target_delta_beta_abs_max` and `window_max_for_normalization`.

Overlay sweeps also write `source_overlay_sweep_shell_throat_overlap.csv`. This table measures each demanded-source channel inside the band where the support-shell window overlaps the support/throat gradient. It is intended to catch warp-shell/throat-mismatch behavior: radial-null, radial-current, angular-pressure, or point-peak growth concentrated in the active shell/throat overlap rather than distributed across the full grid.

## SourceParams reference

`adm_harness/source_ledger.py` builds a reduced 4D metric from a `SourceParams` dataclass, evaluates finite-difference Einstein-tensor projections, and records source-ledger channels. The fields below are the durable parameter reference for that harness. Experiment reports may name selected values, but this section describes the knobs as reusable system controls.

The coordinates are:

- `s`: service/evolution coordinate used for timing, catch/rematch, release, and reset.
- `l`: radial rail/throat coordinate.
- The packet tube is centered approximately on `l = s`; live-packet accounting uses `abs(l - s) <= Rpass` until the configured live end.

The main metric channels are:

- `alpha`: lapse / clock-rate channel. It is built from the standing support lapse, radial lapse cushion, support-shell clock-lapse partner, and packet-local lapse compensator.
- `beta`: radial shift / carrying-flow channel. It is built from the baseline carried shift, optional support-shell carrying-flow overlay, and optional packet-local beta rematch.
- `gamma_ll`: radial spatial metric channel. It is built from the standing support rail-stretch factor and optional support-shell rail-stretch partner.
- `gamma_omega`: angular/throat-capacity channel. It is built from the baseline angular jacket and optional support-shell throat-capacity partner.

### Baseline packet and service speed

| Field | Meaning |
|---|---|
| `V` | Main service/load factor used to scale the carried packet/support shift during the live service. It is the V in V5, V8, V10 checks, not an ordinary passenger velocity claim. |
| `v_exit` | Residual/exit service speed after catch/rematch has finished; `U_beta` and `U_packet` interpolate between `V` and `v_exit`. |
| `p_beta` | Power applied to the standing support bump in the baseline beta term. Larger values localize baseline carrying flow more strongly to the prepared support region. |
| `Rpass` | Packet-tube radius. It controls packet geometry windows, packet/live masks, and packet-local carve/lapse/beta-rematch windows before multipliers are applied. |

### Catch/rematch timing

| Field | Meaning |
|---|---|
| `x_catch_beta` | Center of the support-side beta catch. More negative values make support infrastructure start rematching earlier. |
| `w_catch_beta` | Temporal width of the beta catch transition. Wider values smooth the support-side catch over more service time. |
| `x_catch_packet` | Center of the packet rematch. The selected branch keeps this close behind the support-side catch. |
| `w_catch_packet` | Temporal width of the packet rematch transition. |
| `catch_profile` | Transition family for catch/rematch. Current options are `minjerk` and `tanh`; `minjerk` is the mature shaped-catch default. |

### Standing support plant

| Field | Meaning |
|---|---|
| `C0` | Standing radial rail-stretch scale. It enters `a_spatial = exp(q * W * log(C0))`, then contributes to `gamma_ll`. |
| `lam` | Lapse-to-rail-stretch multiplier. It enters `t_lapse = exp(q * W * log(lam * C0))`, so it sets how strongly the standing support affects `alpha`. |
| `B0` | Baseline throat/carrying-flow capacity factor. It enters `B = 1 + (B0 - 1) * W * q` and divides the packet coordinate velocity and baseline beta. |
| `eta_N` | Strength of the radial lapse cushion near the support shoulder. It buys packet causal margin for radial-softened support branches. |
| `Rth` | Main support/throat radius used by the standing support bump and region labels. |
| `w_th` | Default transition width of the standing support bump at `Rth`. Wider values soften radial support edges but can consume packet safety margin. |
| `w_th_inner` | Optional inner-side support transition width. When paired with `w_th_outer`, it replaces the symmetric `w_th` width inside `Rth`. |
| `w_th_outer` | Optional outer-side support transition width. When paired with `w_th_inner`, it replaces the symmetric `w_th` width outside `Rth`. |
| `w_pass` | Packet-window transition width for baseline packet bump `S` and packet-local windows before width multipliers. |
| `eps` | Small regularization used in packet-window radius calculations to avoid exact zero-width/singular center behavior. |

### Carrying-flow release and reset

| Field | Meaning |
|---|---|
| `x_beta` | Center of the carrying-flow release/fade. It also anchors the end of the live-packet accounting window. |
| `w_beta` | Width of the carrying-flow release/fade and the default smoothing scale for several live-window schedules. |
| `q_t0` | Start time for support decompression/reset through the minimum-jerk `q` factor. |
| `q_Tr` | Duration of support decompression/reset. Larger values make reset slower and smoother. |
| `release_choreography_mode` | Release law family. `legacy` keeps the historical tanh-like release; `matched_hold` delays release, then applies a finite smooth beta fade. |
| `release_matched_hold_widths` | Hold duration before beta fade, in multiples of `w_beta`. This keeps the packet rematched while the trailing edge settles. |
| `release_beta_profile` | Beta fade profile for non-legacy choreography: `tanh`, `minimum_jerk` / `smoothstep5`, or `smoothstep7`. Minimum-jerk and smoothstep7 have vanishing endpoint derivatives. |
| `release_beta_width_multiplier` | Duration multiplier for the beta fade. In non-legacy modes the fade duration is `4 * w_beta * release_beta_width_multiplier`. |
| `release_lapse_lag_widths` | Extra hold lag for packet-local lapse support when using `coordinated_release` schedules, in multiples of `w_beta`. |
| `release_carve_lag_widths` | Extra hold lag for packet carve/shoulder relaxation when using `coordinated_release` schedules, in multiples of `w_beta`. |

### Angular/throat-capacity jacket

| Field | Meaning |
|---|---|
| `aOmega` | Amplitude of the baseline angular jacket applied to `gamma_omega`. |
| `ROmega` | Radial placement radius for the angular jacket. |
| `wOmega` | Radial width of the angular jacket. |
| `xOmega` | Service-time center/anchor for the angular jacket fade factor. |
| `wtOmega` | Temporal width for the angular jacket fade factor. |

### Live-packet accounting

| Field | Meaning |
|---|---|
| `live_packet_end_margin_widths` | Number of `w_beta` widths after `x_beta` to keep points in live-packet accounting. It affects live masks and `live_only` packet-local schedules. |

### Support-shell overlay and metric partners

These fields define an infrastructure-local support-shell actuator. The overlay is disabled by default so historical baseline ledgers regenerate unchanged.

| Field | Meaning |
|---|---|
| `support_shell_overlay_enabled` | Enables the support-shell overlay and its coupled metric partners. |
| `support_shell_amplitude` | Signed amplitude of the support-shell carrying-flow contribution added to `beta` through `support_shell_delta_beta`. |
| `support_shell_catch_lead` | How far ahead of packet catch/rematch the support-shell temporal window is centered. |
| `support_shell_temporal_width` | Width of the support-shell temporal window. |
| `support_shell_temporal_profile` | Temporal profile family for the support-shell window: `gaussian`, `raised_cosine`, `minjerk_pulse`, or `smooth_box`. |
| `support_shell_temporal_shoulder` | Optional temporal shoulder/edge width used by compact temporal profiles. `None` means use the profile default. |
| `support_shell_radial_profile` | Radial profile family for the support-shell window: `smooth_box`, `gaussian_annulus`, or `raised_cosine_annulus`. |
| `support_shell_smoothness_order` | Repeated smoothing order for the support-shell radial box profile. Higher values soften edges more strongly. |
| `support_shell_inner_multiplier` | Inner radius of the annular support-shell band as a multiplier of `Rth`. |
| `support_shell_radial_multiplier` | Outer radius of the annular support-shell band as a multiplier of `Rth`. |
| `support_shell_radial_width` | Optional radial edge/width override for support-shell profiles. `None` uses the profile-specific default. |
| `support_shell_packet_exclusion` | Strength of packet exclusion inside the support-shell window. `1.0` fully suppresses shell activity in the packet tube. |
| `support_shell_time_anchor` | Optional direct temporal anchor for the support-shell window. `None` derives it from catch/rematch timing and `support_shell_catch_lead`. |
| `support_shell_catch_edge_width` | Optional edge width for catch-anchored shell timing. `None` derives it from catch widths. |
| `support_shell_clock_lapse_log_gain` | Log-gain applied to `alpha` on the support-shell window. Positive values increase lapse locally. |
| `support_shell_rail_stretch_log_gain` | Log-gain applied to `gamma_ll` on the support-shell window. |
| `support_shell_throat_capacity_log_gain` | Log-gain applied to `gamma_omega` on the support-shell window. |

### Beta-memory support-edge receiver

These fields define the endpoint receiver branch used after the beta/support
co-design screen. The receiver is disabled by default. When enabled, it builds a
non-live support-edge window from accumulated beta release, not just the
instantaneous release slope, and applies split R1/R2 metric partners.

| Field | Meaning |
|---|---|
| `support_edge_receiver_enabled` | Enables the beta-memory support-edge receiver family. |
| `support_edge_receiver_memory_reference_width` | Beta-width baseline treated as no-transfer reference. Width above this value drives receiver memory. |
| `support_edge_receiver_memory_gain` | Gain applied to beta-width excess before clipping the memory driver. |
| `support_edge_receiver_post_release_widths` | Number of `w_beta` widths to keep memory active after beta fade. |
| `support_edge_receiver_inner_multiplier` | Inner support-edge receiver radius as a multiplier of `Rth`. |
| `support_edge_receiver_outer_multiplier` | Outer support-edge receiver radius as a multiplier of `Rth`. |
| `support_edge_receiver_radial_width` | Optional receiver radial edge width. `None` uses the band-derived default. |
| `support_edge_receiver_outer_power` | Outer weighting power inside the receiver band. |
| `support_edge_receiver_packet_exclusion` | Suppresses receiver activity in the live packet tube. |
| `support_edge_receiver_lapse_log_gain` | Optional R1 lapse partner on the radial/current receiver cap. |
| `support_edge_receiver_radial_log_gain` | R1 rail-stretch partner on the radial/current receiver cap. |
| `support_edge_receiver_beta_relaxation_gain` | R1 local beta-relaxation partner for current transfer. |
| `support_edge_receiver_angular_log_gain` | R2 angular-capacity partner on the receiver flange. |
| `support_edge_receiver_angular_side` | Side selector for the R2 flange: `positive`, `negative`, or `bilateral`. |

Sweep ratios such as `--clock-lapse-ratios`, `--rail-stretch-ratios`, and `--throat-capacity-ratios` are convenience inputs that convert to these log gains by multiplying the signed support-shell amplitude.

### Packet-local standing-support redesign controls

These knobs edit the standing support under or around the packet tube. They are not source-family models; they are metric-side controls for asking whether the packet can be separated from the support substrate in the demanded-source ledger.

Common schedule choices:

- `live_only`: active through the live packet interval and tapered off after release.
- `entry_catch_release`: active in a bounded entry/catch/release interval.
- `catch_release`: active mainly from catch/rematch through release, skipping most entry/precatch exposure.
- `coordinated_release`: active through the explicit release choreography and then faded by the selected release profile. Carve/shoulder and lapse calls use their respective release lag widths.
- `always`: active wherever the packet-shaped radial window is active, independent of service time.

| Field | Meaning |
|---|---|
| `standing_support_packet_exclusion` | Core carve strength applied to the standing support bump under the packet tube. `0.0` disables the carve; `1.0` would remove the standing support contribution where the core packet window is one. |
| `standing_support_packet_exclusion_radius_multiplier` | Radius multiplier for the core carve window relative to `Rpass`. |
| `standing_support_packet_exclusion_width_multiplier` | Transition-width multiplier for the core carve window relative to `w_pass`. |
| `standing_support_packet_exclusion_schedule` | Temporal schedule for the core carve window. |
| `standing_support_packet_exclusion_temporal_profile` | Temporal edge profile for the core carve schedule. `tanh` preserves historical behavior; `minimum_jerk` / `smoothstep5` and `smoothstep7` provide derivative-limited schedule edges. |
| `standing_support_packet_exclusion_shoulder` | Additional wider/softer shoulder carve strength. It is added to the core carve contribution and clipped before applying to the standing support bump. |
| `standing_support_packet_exclusion_shoulder_mode` | Shoulder shape. `filled` uses the full outer shoulder window; `annular` uses outer minus inner so the shoulder softens the ring around the core. |
| `standing_support_packet_exclusion_shoulder_radius_multiplier` | Radius multiplier for the shoulder carve window relative to `Rpass`. |
| `standing_support_packet_exclusion_shoulder_width_multiplier` | Transition-width multiplier for the shoulder carve window relative to `w_pass`. |
| `standing_support_packet_exclusion_shoulder_schedule` | Temporal schedule for the shoulder carve window. |
| `standing_support_packet_exclusion_shoulder_temporal_profile` | Temporal edge profile for the shoulder carve schedule. |
| `standing_support_packet_lapse_log_gain` | Packet-local lapse compensator log-gain applied to `alpha` on its own packet window. It can restore causal margin consumed by carving, but may add radial-null cost. |
| `standing_support_packet_lapse_radius_multiplier` | Radius multiplier for the packet-local lapse window relative to `Rpass`. |
| `standing_support_packet_lapse_width_multiplier` | Transition-width multiplier for the packet-local lapse window relative to `w_pass`. |
| `standing_support_packet_lapse_schedule` | Temporal schedule for the packet-local lapse window. |
| `standing_support_packet_lapse_temporal_profile` | Temporal edge profile for the packet-local lapse schedule. |
| `standing_support_packet_beta_rematch_gain` | Packet-local beta rematch gain. Positive values add `delta_beta_packet = -gain * window * (vcoord + beta_pre_rematch)`, nudging the local shift toward cancelling packet coordinate velocity. |
| `standing_support_packet_beta_rematch_shape` | Shape family for the beta rematch window. `core` is the old filled packet-local window; `shoulder`, `annular`, `edge_soften`, and `trailing_edge` target packet shoulders/edges more selectively. |
| `standing_support_packet_beta_rematch_radius_multiplier` | Radius multiplier for the packet-local beta rematch window relative to `Rpass`. |
| `standing_support_packet_beta_rematch_width_multiplier` | Transition-width multiplier for the packet-local beta rematch window relative to `w_pass`. |
| `standing_support_packet_beta_rematch_inner_radius_multiplier` | Inner radius multiplier for annular, edge-soften, and trailing-edge beta rematch sleeves. |
| `standing_support_packet_beta_rematch_outer_radius_multiplier` | Outer radius multiplier for annular, edge-soften, and trailing-edge beta rematch sleeves. Values near `1.10` target just outside the packet edge. |
| `standing_support_packet_beta_rematch_edge_softness` | Extra radial/side softness multiplier for shaped beta rematch sleeve edges. |
| `standing_support_packet_beta_rematch_temporal_width_multiplier` | Temporal smoothing multiplier for the beta rematch schedule. |
| `standing_support_packet_beta_rematch_temporal_profile` | Temporal edge profile for the beta rematch schedule. Leave this at `tanh` when testing infrastructure-side release/carve/lapse smoothing without changing beta support timing. |
| `standing_support_packet_beta_rematch_center_floor` | Weak filled-core floor mixed into shaped beta rematch windows. This can restore causal margin without making the center as active as the edge sleeve. |
| `standing_support_packet_beta_rematch_floor_mode` | How shaped beta-rematch sleeves combine with `standing_support_packet_beta_rematch_center_floor`: `max` uses a hard union, `blend` uses a smooth union, and `add` clips the sum. |
| `standing_support_packet_beta_rematch_schedule` | Temporal schedule for the packet-local beta rematch window. |

### Ledger outputs tied to these knobs

Useful point-ledger fields for interpreting parameter effects include:

- `W`, `W_raw`, `standing_support_packet_carve_contribution`, and `standing_support_packet_carve_factor` for support-bump carving.
- `alpha`, `alpha_base`, `standing_support_packet_lapse_factor`, `standing_support_packet_delta_alpha`, and `support_shell_delta_alpha` for lapse changes.
- `beta`, `beta_base`, `beta_pre_packet_rematch`, `support_shell_delta_beta`, and `standing_support_packet_delta_beta` for carrying-flow and rematch changes.
- `gamma_ll_base`, `gamma_ll`, and `support_shell_delta_gamma_ll` for rail-stretch changes.
- `gamma_omega_base`, `gamma_omega`, and `support_shell_delta_gamma_omega` for throat-capacity changes.
- `inside_packet_live`, `inside_packet_geom`, `packet_norm`, `stage`, and `region` for packet-worldtube accounting.

## Send results back

After the smoke suite finishes, create a results ZIP:

```bash
python scripts/collect_results.py --runs runs --output local_test_results.zip
```

Upload `local_test_results.zip` here. The most useful files are `decision_sheet.csv`, `status.json`, `validation_report.json`, `field_delta_summary.csv`, `service_modifier_summary.csv`, and `comparison_report.md`.

## Config path policy

All included configs use paths relative to the config file location. No `/mnt/data` or machine-local paths are required.

## Service-facing names

Public configs and outputs use service terms:

- `carrying_flow`
- `clock_lapse`
- `rail_stretch`
- `throat_capacity`
- `carrying_flow_off`

The loader still accepts legacy internal array keys from older bundles where needed, but generated configs and reports use service-facing names.
