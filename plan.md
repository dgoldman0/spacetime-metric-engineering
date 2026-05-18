# Active-Rail Codex Handoff Plan

## Why this handoff exists

The active-rail project is at a transition point. The early work asked whether a throat-loaded transport metric could be made coherent at all. The recent work has narrowed that into a more useful engineering question: whether the packet can be treated as a protected service object while the hard geometric support is handled by surrounding infrastructure. The project has enough harness machinery to stop arguing about this only in prose. The next agent should turn the distinction into reproducible reports.

The most important conceptual split is this:

```text
Stage I asks what the metric/service architecture is doing.
Stage II asks whether a specific matter-source family can physically realize it.
```

Do not merge those stages. They answer different questions.

Stage I is about the active rail as a metric-engineering service plant. It asks whether the packet worldtube stays out of the main support burden, whether the source ledger places bad channels in infrastructure rather than the packet corridor, and whether the current coupled metric knobs make the demanded source cleaner. This stage uses the current ADM/source-ledger code. It should mostly require focused runs and one report generator.

Stage II is about source-family viability. It asks whether a Barceló-Visser-style nonminimally coupled scalar field, or a closely related scalar-tensor source model, can produce the remaining demanded source without requiring trans-Planckian field amplitudes, trans-Planckian gradients, or other signs that the effective theory has left its trustworthy regime. This stage needs new code because the current harness computes demanded stress-energy from the metric, but does not yet construct a scalar matter model.

The recent discussion kept circling because these two questions were blended. The active rail may bypass ordinary passenger traversability even if a simple scalar source later fails. Conversely, a clean demanded-source placement result does not prove that any real matter source can pay the bill. The next work should make that distinction explicit in the repository.

## Working intuition to test

The intuition to test is not that the active rail magically removes exotic matter. The better intuition is this:

```text
A conventional traversable wormhole asks one throat region to be both the exotic support structure and the passenger corridor.

The active rail may separate those roles. The packet may remain in a safe service worldtube while the support plant carries the hard throat, shift, catch/rematch, lapse, and capacity burdens in surrounding infrastructure.
```

If this is right, the active rail weakens the ordinary Morris-Thorne passenger-traversability requirement. The packet would not need the same region that carries the main exotic support burden to be a comfortable traveler path. It would need a safe operational service corridor coupled to a support plant.

That would be a real engineering improvement. It would not automatically solve the matter-source problem. The remaining support plant may still demand exotic stress-energy somewhere. A pure Barceló-Visser-style scalar source may still demand trans-Planckian scalar values if asked to support the whole standing throat. But the old objection would have to be remapped: it would no longer be simply “the traveler must traverse the same exotic throat.” It would become “can the support plant be realized physically while the packet stays outside the worst source layer?”

That is the dividing line this plan is built around.

## Background the agent should understand before editing anything

The active-rail metric has been organized as a service cycle rather than a static hallway. In project language, the cycle is roughly:

```text
prepare standing support
carry packet through support-contained flow
catch/rematch packet at the support shell
fade the shift
relax/decompress the throat support
reset the plant
```

The current ansatz uses a radial coordinate `l` along the rail/throat and a service/evolution coordinate `s` or `sigma`. The metric contains a lapse/clock channel, a radial spatial metric channel, an angular/throat-capacity channel, and a radial shift/carrying-flow channel. In the ADM-like notation used throughout the project, the important fields are:

```text
alpha              lapse / clock-rate / causal-margin channel
beta               radial shift / carrying-flow channel
gamma_ll           radial rail-stretch channel
gamma_omega        angular/throat-capacity channel
packet_norm        norm of the modeled packet tangent/live packet condition
Tkk / rho / j / p  demanded-source projections from G_munu[g] / 8π
```

The recent validation ladder established a small selected support-shell service component. The component is a positive carrying-flow overlay, localized to catch/rematch support-shell infrastructure. At the selected amplitude, it routed incremental radial-current-like burden into support infrastructure while keeping the packet quiet at both `V = 5` and `V = 10`. Here `V` is the service factor or carried-shift load, not an ordinary passenger velocity.

The continuous 4D source-ledger sweep then corrected an overly optimistic interpretation. Increasing the support-shell carrying-flow amplitude alone did not become source relief. At high amplitude it stayed packet-safe, but it added radial null/current burden. That result matters: the single-channel carrying-flow shell is useful as a controlled actuator, but not as the whole load-bearing support solution.

The high-resolution coupled timing run gave the best current engineering direction. Pairing carrying-flow with a clock-lapse partner improved the demanded-source behavior and produced a coherent timing family. The current best V5 family is roughly:

```text
variant:                     tuned_w0569_eta200
service factor:              V = 5
carrying-flow amplitude:      a_beta = +0.5
catch lead:                  1.45 to 1.55
temporal width:              0.30
clock-lapse ratio:            0.375 to 0.5
rail-stretch ratio:           0.0 by default
```

The remaining ceiling appears to involve angular pressure and shell-throat overlap. That points to throat-capacity coupling as the next metric partner. The next source-placement question is whether a modest throat-capacity partner can lower angular/throat burden without raising radial null/current burden or packet drift.

## Current code inventory

Work from the repository root:

```bash
cd /path/to/spacetime-metric-engineering
```

Main toolkit:

```text
toolkit/adm_harness_cli
```

The important current files are:

```text
toolkit/adm_harness_cli/adm_harness/source_ledger.py
toolkit/adm_harness_cli/scripts/run_source_ledger.py
toolkit/adm_harness_cli/scripts/run_source_overlay_sweep.py
```

The current source ledger already computes a demanded-source ledger from the metric via the Einstein tensor. It already records the core badness channels:

```text
neg_Tkk_radial       negative radial null contraction
abs_p_l              radial pressure magnitude
abs_pOmega           angular pressure magnitude
abs_j_l              radial current magnitude
neg_rho_euler        negative Eulerian density
neg_rho_packet       negative packet-comoving density
```

The current `SourceParams` already includes the coupled support-shell knobs needed for Stage I:

```text
support_shell_clock_lapse_log_gain
support_shell_rail_stretch_log_gain
support_shell_throat_capacity_log_gain
```

The current `scalars()` path already applies these partners. In particular, throat-capacity is already wired through `gamma_omega` and recorded through fields like:

```text
support_shell_throat_capacity_factor
support_shell_delta_gamma_omega
gamma_omega_base
gamma_omega
```

The current point ledger already contains the fields needed for a packet-worldtube report:

```text
stage
region
inside_packet_geom
inside_packet_live
packet_norm
support_shell_window
bad_<channel>
point_burden_<channel>
volume_burden_<channel>
```

The existing summary code already distinguishes total burden, geometric packet burden, live packet burden, and infrastructure-or-reset burden. That is why Stage I should not be a rewrite.

The overlay sweep script already supports:

```text
--clock-lapse-ratios
--rail-stretch-ratios
--throat-capacity-ratios
--jobs
--resume
--case-output
```

and writes summary, channel-delta, shell-throat, objective-ranking, failure, metadata, and per-case outputs.

The focused ledger script already writes full point ledgers for individual cases. Use it when the report needs raw worldtube rows for a selected candidate.

## Stage I overview

Stage I is the architecture and demanded-source stage. It has three parts:

```text
Stage I-A: V5 throat-capacity source-placement screen
Stage I-B: minimal-traversability / packet-worldtube report
Stage I-C: V10 edge check for the selected Stage I candidate
```

Stage I answers these questions:

```text
Does the active rail behave like a packet service corridor coupled to a support plant?
Does the packet worldtube overlap the main expensive support-source regions?
Can throat-capacity coupling improve the remaining angular/shell-throat burden?
Does the improved V5 candidate survive a V10 edge check?
```

Stage I does not answer whether a real scalar source exists. It only says what source the metric demands and where that demand appears.

## Current execution update, 2026-05-17

A review of the repository shows that the intended Stage I-A throat-capacity sweeps have already been run at report-grade resolution. Do not rerun them unless a convergence or provenance issue appears. Use the existing outputs as the Stage I-A data source:

```text
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_throat_capacity/
toolkit/adm_harness_cli/runs/source_overlay_sweep_v5_throat_capacity_fine/
```

Both runs used:

```text
variant:          tuned_w0569_eta200
service factor:   V = 5
grid:             ns = 53, nl = 73
amplitude:        +0.5
sign:             pos
catch leads:      1.45, 1.55
temporal width:   0.30
clock ratios:     0.375, 0.5
rail ratio:       0.0
packet exclusion: 1.0
```

The broad run scanned:

```text
throat_capacity_ratios: -0.5, -0.25, 0.0, 0.25, 0.5
```

The fine run scanned:

```text
throat_capacity_ratios: -0.1, -0.05, 0.0, 0.05, 0.1
```

The preliminary result is that throat-capacity coupling does not improve the current V5 candidate as a default load-bearing partner. The objective ranking continues to prefer `throat_capacity_ratio = 0.0`. Small negative throat-capacity ratios can slightly reduce selected radial-null or aggregate readouts, but they add radial-current cost and large point-peak penalties. Positive throat-capacity ratios are worse in radial-null and point-peak channels. Therefore Stage I-A should now be written as a completed source-placement screen, not as a new sweep.

Current selected Stage I candidate for the packet-worldtube report:

```text
variant:                 tuned_w0569_eta200
service factor:          V = 5
support-shell amplitude: +0.5
sign:                    pos
catch lead:              1.55
temporal width:          0.30
clock-lapse ratio:       0.375
clock-lapse log gain:    0.1875
rail-stretch ratio:      0.0
throat-capacity ratio:   0.0
throat-capacity log gain: 0.0
```

Use `clock_lapse_ratio = 0.5` only as the aggregate-burden comparator. It has a slightly lower max total burden, but the richer source objective and packet/radial discipline favor `0.375`.

Revised Stage I order:

```text
1. Write STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md from existing high-resolution sweeps.
2. Add run_minimal_traversability_report.py.
3. Generate focused V5 point ledgers for baseline and selected clock-lapse-only overlay.
4. Run the minimal-traversability report and write STAGE1_V5_MINIMAL_TRAVERSABILITY_SCREEN.md.
5. Run the V10 selected-candidate edge check after the V5 worldtube result is in hand.
```

## Stage I execution result, 2026-05-17

Stage I has now been run through the selected V5 candidate.

New or generated files:

```text
supporting_reports/STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md
toolkit/adm_harness_cli/scripts/run_minimal_traversability_report.py
toolkit/adm_harness_cli/runs/stage1_v5_baseline_ledger/
toolkit/adm_harness_cli/runs/stage1_v5_selected_candidate_ledger/
toolkit/adm_harness_cli/runs/stage1_v5_minimal_traversability_report/
supporting_reports/STAGE1_V5_MINIMAL_TRAVERSABILITY_SCREEN.md
toolkit/adm_harness_cli/runs/stage1_v10_selected_candidate_check/
toolkit/adm_harness_cli/runs/stage1_v10_selected_candidate_ledger/
toolkit/adm_harness_cli/runs/stage1_v10_minimal_traversability_report/
supporting_reports/STAGE1_V10_SELECTED_CANDIDATE_EDGE_CHECK.md
```

Stage I-A result:

```text
status: complete
decision: throat-capacity coupling is not selected
selected V5 candidate: clock-lapse-only support-shell overlay
```

Stage I-B result:

```text
status: fail for strong minimal-traversability claim
packet norm at V5: safe
active shell touching live packet: no
problem: live packet still carries about 22% radial-null burden and 26% radial-pressure burden
top hard-channel bad point: inside live packet, region = packet_in_support
```

Stage I-C result:

```text
status: fail at V10
positive_packet_norm_live: 3
max_live_packet_fraction_any_channel: about 0.307
problem: selected high-amplitude coupled candidate does not degrade gracefully to V10
```

Interpretation:

```text
The support-shell overlay itself is packet-separated, but the current standing packet/support architecture is not.
The present candidate cannot yet support the claim that active rail bypasses ordinary passenger traversability.
Stage II scalar-source screening should be paused for this candidate until Stage I redesign produces a cleaner packet/support separation.
```

Recommended next Stage I redesign focus:

```text
reduce standing radial-null and radial-pressure burden in packet_in_support
separate the live packet tube from the standing support substrate more cleanly
recover V10 packet-norm safety before using high-amplitude support-shell coupling as a source-family target
use lower-amplitude or V-aware support-shell scaling as a diagnostic branch
```

## Stage I redesign start, 2026-05-17

The harness now includes an experimental standing-support packet carve-out and a worldtube exposure ranking for overlay sweeps. See:

```text
supporting_reports/STAGE1_PACKET_CARVE_HARNESS_AND_SWEEP.md
```

Key result:

```text
At V5, standing_support_packet_exclusion = 0.20 removes top hard-channel points from the live packet and reduces live radial-null fraction from about 0.222 to 0.072 and live radial-pressure fraction from about 0.261 to 0.123.
```

Important limit:

```text
The V5 carved candidate still fails the strict minimal-traversability rule because live hard-channel burden remains percent-level.
At V10, nonzero carve strengths tested so far worsen packet-norm safety, even while improving hard-channel placement.
```

Next practical sweep:

```text
Combine modest packet carve-out with a causal-margin compensator.
V5 first; V10 only for V5-safe candidates.
Do not use the current carved candidate as a Stage II source-family target yet.
```

## Stage I carve-plus-lapse result, 2026-05-17

The packet-local lapse compensator has been added in the working tree and screened. See:

```text
supporting_reports/STAGE1_CARVE_LAPSE_COMPENSATOR_SWEEP.md
```

Key result:

```text
The first V5/V10 packet-safe compensated branch is:
standing_support_packet_exclusion = 0.12
standing_support_packet_lapse_log_gain = 0.75
schedule = live_only
```

It improves the V10 edge check relative to the uncarved selected candidate:

```text
positive_packet_norm_live: 3 -> 0
top hard-channel point in live packet: yes -> no
live p_l fraction: 0.261 -> 0.169
live Tkk fraction: 0.307 -> 0.283
```

But it still fails the strict Stage I-B criterion because live radial-null exposure remains large. At V5 it also trades the uncarved top-point failure for a higher live radial-null fraction:

```text
uncarved V5 live Tkk fraction: 0.222
carve+lapse V5 live Tkk fraction: 0.252
```

Interpretation:

```text
Packet-local lapse compensation can recover causal margin, but when it is co-located with the carve window it partially reintroduces radial-null burden.
The next harness improvement should separate the packet-carve window from the packet-lapse compensation window.
```

## Stage I decoupled carve/lapse result, 2026-05-17

The harness now separates the standing-support packet carve window from the packet-lapse compensation window. See:

```text
supporting_reports/STAGE1_DECOUPLED_CARVE_LAPSE_COMPENSATOR_SWEEP.md
```

New lapse-window controls:

```text
standing_support_packet_lapse_log_gain
standing_support_packet_lapse_radius_multiplier
standing_support_packet_lapse_width_multiplier
standing_support_packet_lapse_schedule
```

Current best V5/V10-safe decoupled branch:

```text
standing_support_packet_exclusion = 0.16
standing_support_packet_lapse_log_gain = 0.55
standing_support_packet_lapse_radius_multiplier = 1.4
standing_support_packet_lapse_width_multiplier = 1.6
schedule = live_only for both carve and lapse
```

Focused comparison against the uncarved selected candidate:

```text
V5 positive_packet_norm_live:       0 -> 0
V5 top hard channels in live:       1 -> 0
V5 live Tkk fraction:               0.222 -> 0.140
V5 live p_l fraction:               0.261 -> 0.145

V10 positive_packet_norm_live:      3 -> 0
V10 top hard channels in live:      8 -> 0
V10 live Tkk fraction:              0.307 -> 0.160
V10 live p_l fraction:              0.261 -> 0.145
```

This is a real architecture improvement but still not a strict minimal-traversability pass:

```text
packet norm is safe at V5 and V10
top hard-channel bad points have moved out of the live packet
live packet burden remains percent-level in radial-null/radial-pressure channels
```

Updated interpretation:

```text
The original gate fail was not a total kill. It identified a packet/standing-support substrate overlap. Decoupled carve/lapse compensation moves the worst hard-channel points infrastructure-side and restores V10 causal margin, but it has not made live-packet burden tiny enough for Stage I-B pass language.
```

Next practical harness move:

```text
Add offset or annular lapse/carve options, or a two-zone carve with a deeper center and softer shoulder.
Focus on whether the remaining live radial-null/radial-pressure burden is caused by the standing support floor or by carve/lapse transition gradients.
Keep Stage II paused until the live fractions come down another order of magnitude or the project explicitly accepts a warning-grade Stage I target.
```

## Stage I two-zone packet carve result, 2026-05-17

The harness now supports a wider, softer shoulder carve on top of the packet-centered standing-support carve. See:

```text
supporting_reports/STAGE1_TWO_ZONE_PACKET_CARVE_SWEEP.md
```

Current balanced two-zone branch:

```text
standing_support_packet_exclusion = 0.17
standing_support_packet_exclusion_shoulder = 0.05
standing_support_packet_exclusion_shoulder_radius_multiplier = 1.3
standing_support_packet_exclusion_shoulder_width_multiplier = 1.6
standing_support_packet_lapse_log_gain = 0.70
standing_support_packet_lapse_radius_multiplier = 1.4
standing_support_packet_lapse_width_multiplier = 1.6
schedule = live_only for carve, shoulder, and lapse
```

Focused comparison against the previous decoupled carve/lapse branch:

```text
V5 live Tkk fraction:     0.140 -> 0.121
V5 live p_l fraction:     0.145 -> 0.114
V10 live Tkk fraction:    0.160 -> 0.130
V10 live p_l fraction:    0.145 -> 0.114
packet norm safety:       preserved at V5 and V10
top hard points in live:  remains 0
```

Interpretation:

```text
The two-zone carve confirms that the residual live hard-channel burden is partly a standing-support-floor problem. The shoulder lowers live packet exposure at both V5 and V10. It still fails strict minimal traversability because live fractions remain percent-level, and stronger shoulders raise V5 point peaks.
```

Next practical harness move:

```text
Add annular or offset shoulder shapes, or widen the shoulder temporal schedule, to reduce V5 point peaks while preserving the live-fraction gain.
Keep Stage II paused unless the project deliberately chooses a warning-grade metric target.
```

## Stage I annular shoulder probe, 2026-05-18

The harness now supports annular shoulder shaping:

```text
standing_support_packet_exclusion_shoulder_mode = filled | annular
```

See:

```text
supporting_reports/STAGE1_ANNULAR_SHOULDER_SHAPING_PROBE.md
```

Moderate annular branch:

```text
standing_support_packet_exclusion = 0.32
standing_support_packet_exclusion_shoulder = 0.08
standing_support_packet_exclusion_shoulder_mode = annular
standing_support_packet_lapse_log_gain = 1.00
```

Focused result:

```text
V5 live Tkk/p_l:   0.0965 / 0.0754, packet safe
V10 live Tkk/p_l:  0.0957 / 0.0754, packet safe
```

Deep annular diagnostic:

```text
standing_support_packet_exclusion = 0.60
standing_support_packet_exclusion_width_multiplier = 1.4
standing_support_packet_exclusion_shoulder = 0.12
standing_support_packet_lapse_log_gain = 1.00
```

Focused result:

```text
V5 live Tkk/p_l:   0.0572 / 0.0237, packet safe
V10 live Tkk/p_l:  0.0419 / 0.0235, but positive_packet_norm_live = 165
```

Interpretation:

```text
Annular shoulder shaping improves live fractions, especially radial pressure, but it does not produce a V5/V10-safe order-of-magnitude reduction. Deep carving reaches diagnostic low live fractions but breaks the V10 packet-norm gate and creates large point peaks.
```

Updated next direction:

```text
Shoulder shaping alone is probably insufficient. The next harness improvement should target radial-null exposure more directly, likely with a packet-local beta rematch / beta-gradient softening partner or a temporal carve-ramp schedule, plus a ranking objective that penalizes causal-margin loss and point peaks.
```

## Stage I packet beta rematch / temporal probe, 2026-05-18

The harness now includes a packet-local beta rematch control:

```text
standing_support_packet_beta_rematch_gain
standing_support_packet_beta_rematch_radius_multiplier
standing_support_packet_beta_rematch_width_multiplier
standing_support_packet_beta_rematch_schedule
```

See:

```text
supporting_reports/STAGE1_PACKET_BETA_REMATCH_TEMPORAL_PROBE.md
```

Beta rematch alone improves point peaks but does not improve V10 live radial-null exposure:

```text
moderate annular V10:       live Tkk/p_l = 0.095680 / 0.075388, peak = 4.100704
beta gain 0.10 V10:         live Tkk/p_l = 0.098485 / 0.075389, peak = 3.534678
beta gain 0.20 V10:         live Tkk/p_l = 0.106604 / 0.075389, peak = 3.648101
```

Temporal packet-lapse gating plus beta rematch found a better V5 diagnostic branch:

```text
V5 lapse entry_catch_release + beta gain 0.20:
live Tkk/p_l = 0.073763 / 0.075393
positive_packet_norm_live = 0
max point peak ratio = 3.362681
```

But the same structure does not produce a better V10-safe radial-null branch:

```text
V10 low-Tkk temporal/beta cases remain packet-unsafe.
V10-safe high-beta cases restore causal safety but raise live Tkk to >= 0.099771.
```

A V8 service-class check was also run:

```text
moderate annular V8:
positive_packet_norm_live = 0
live Tkk/p_l = 0.095756 / 0.075388
max point peak ratio = 5.123597

low-Tkk temporal/beta V8 cases remain packet-unsafe unless high beta rematch is used.
high-beta V8 safety recovery raises live Tkk to about 0.105505.
```

Updated interpretation:

```text
Packet-local beta rematch is useful as a peak and causal-margin actuator.
Temporal lapse gating exposes a real lower-Tkk branch at V5.
The V8 and V10 gates convert that branch back into radial-null cost.
The moderate annular branch remains the selected V5-V8 operational architecture.
V10 should be treated as a warning-grade edge check rather than the immediate optimization target.
```

Next practical harness move:

```text
Do not keep pushing local beta amplitude alone.
Add independent temporal ramp-width controls for packet lapse and beta rematch.
Consider V-aware/service-factor-scaled timing and beta control laws.
Test nonuniform beta rematch shapes that soften packet-edge gradients instead of rematching the whole packet tube uniformly.
Leave higher-load clean-up to a future higher-load control-law pass unless the project explicitly re-prioritizes V10 optimization.
```

## Stage I-A: V5 throat-capacity source-placement screen

### Purpose

This screen tests the next missing metric partner. The current best V5 coupled family uses positive support-shell carrying-flow plus clock-lapse. That family improved the ledger but left an angular-pressure/shell-throat ceiling. Since angular pressure is naturally tied to the angular/throat-capacity sector, the next screen should test `support_shell_throat_capacity_log_gain` rather than pushing carrying-flow amplitude harder.

The goal is not to produce a final physical source. The goal is to see whether the metric-side support plant becomes cleaner when angular/throat-capacity burden is given its own coupled channel.

### Candidate grid

Use the current best family as the center:

```text
variant:                     tuned_w0569_eta200
service factor:              V = 5
amplitude:                   +0.5
sign:                        pos
catch leads:                 1.45, 1.55
temporal widths:             0.30
clock-lapse ratios:           0.375, 0.5
rail-stretch ratios:          0.0
throat-capacity ratios:      -0.5, -0.25, 0.0, 0.25, 0.5
radial profile:               smooth_box
smoothness order:             1
support shell radial band:    0.65 Rth to 1.20 Rth
packet exclusion:             1.0
```

### First smoke run

Run from the toolkit directory:

```bash
cd toolkit/adm_harness_cli
```

Use a small grid first:

```bash
python scripts/run_source_overlay_sweep.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --outdir runs/stage1_v5_throat_capacity_smoke \
  --amplitudes 0.5 \
  --signs pos \
  --catch-leads 1.45 1.55 \
  --temporal-widths 0.30 \
  --clock-lapse-ratios 0.375 0.5 \
  --rail-stretch-ratios 0.0 \
  --throat-capacity-ratios -0.5 -0.25 0.0 0.25 0.5 \
  --ns 27 \
  --nl 37 \
  --jobs 1 \
  --case-output \
  --quiet
```

The smoke run is only for code health, output shape, and obvious sign/pathology detection. Do not use it for final claims. As of the 2026-05-17 execution update above, this screen already has high-resolution outputs, so this smoke run is retained as provenance/replay guidance rather than an immediate next command.

### High-resolution run

After the smoke run succeeds:

```bash
python scripts/run_source_overlay_sweep.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --outdir runs/stage1_v5_throat_capacity_highres \
  --amplitudes 0.5 \
  --signs pos \
  --catch-leads 1.45 1.55 \
  --temporal-widths 0.30 \
  --clock-lapse-ratios 0.375 0.5 \
  --rail-stretch-ratios 0.0 \
  --throat-capacity-ratios -0.5 -0.25 0.0 0.25 0.5 \
  --ns 53 \
  --nl 73 \
  --jobs 4 \
  --resume \
  --case-output
```

Use fewer jobs if the machine is memory constrained.

### Stage I-A win condition

A useful throat-capacity result should improve the angular/throat channel without damaging the radial and packet channels. The best result should be judged by both the existing objective ranking and direct physical readouts.

Preferred signs:

```text
positive_packet_norm_live == 0
packet_norm_live_delta_max_abs remains near or below the current 0.02 to 0.025 band
max_total_burden_ratio improves below the current ~1.053 ceiling if possible
abs_pOmega_total_ratio improves relative to the clock-lapse-only case
neg_Tkk_radial_total_ratio stays near the current ~1.02 band
abs_j_l_total_ratio stays near the current ~1.01 band
neg_rho_packet_total_ratio does not increase materially
shell-throat angular-pressure concentration drops if possible
source_objective_score improves relative to the throat_capacity_ratio = 0 baseline
```

A mixed result is still useful. If throat-capacity lowers angular pressure but raises radial null burden, classify it as a local/peak-shaping partner rather than the default load-bearing partner. If it worsens both aggregate and radial/null channels, keep the clock-lapse-only family as the current best Stage I candidate.

### Deliverable for I-A

Create:

```text
supporting_reports/STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md
```

The report should be prose-first. It should not just dump tables. It should explain:

1. Why throat-capacity was tested.
2. Which current design problem it addresses.
3. Whether it improved the angular-pressure/shell-throat ceiling.
4. Whether it introduced radial null/current or packet penalties.
5. Which candidate should be passed to the worldtube report.

Also include a compact candidate table with the top 5 cases by objective score and a short reason for selecting the final Stage I candidate.

## Stage I-B: minimal-traversability / packet-worldtube report

### Purpose

This is the main architecture test. It asks whether the active rail still behaves like an ordinary passenger-traversable wormhole or whether the packet is better described as a protected service worldtube coupled to a non-passenger support plant.

This report is not just another burden ranking. It should answer the question that has been causing conceptual drift:

```text
Does the packet need the main exotic/support region to be an ordinary passenger-traversable throat?
```

The report should use the selected V5 candidate from Stage I-A. It should compare that candidate to the baseline and, if useful, to the clock-lapse-only `throat_capacity_ratio = 0` case.

### Needed data

The overlay sweep summary may be enough for some global conclusions, but the worldtube report should preferably consume full point ledgers. Use `run_source_ledger.py` to generate focused ledgers for:

```text
baseline tuned_w0569_eta200 at V = 5
selected Stage I-A candidate at V = 5
optional clock-lapse-only comparator at V = 5
```

Example focused run for a selected case:

```bash
python scripts/run_source_ledger.py \
  --variant tuned_w0569_eta200 \
  --service-factor 5 \
  --outdir runs/stage1_v5_selected_candidate_ledger \
  --support-shell-overlay \
  --support-shell-amplitude 0.5 \
  --support-shell-catch-lead <SELECTED_LEAD> \
  --support-shell-temporal-width 0.30 \
  --support-shell-clock-lapse-log-gain <0.5 * SELECTED_CLOCK_RATIO> \
  --support-shell-rail-stretch-log-gain 0.0 \
  --support-shell-throat-capacity-log-gain <0.5 * SELECTED_THROAT_CAPACITY_RATIO> \
  --ns 53 \
  --nl 73 \
  --force
```

Replace the selected values with the I-A result. For example, if `clock_lapse_ratio = 0.375`, the log gain is `0.5 * 0.375 = 0.1875`. If `throat_capacity_ratio = -0.25`, the log gain is `0.5 * -0.25 = -0.125`.

### New script to add

Add a small analysis script, not a core rewrite:

```text
toolkit/adm_harness_cli/scripts/run_minimal_traversability_report.py
```

The script should accept one or more point ledgers and produce a markdown report plus CSV summaries.

Suggested CLI:

```bash
python scripts/run_minimal_traversability_report.py \
  --point-ledger runs/stage1_v5_selected_candidate_ledger/source_ledger_point_ledger.csv \
  --label selected_v5 \
  --outdir runs/stage1_v5_minimal_traversability_report
```

Optional comparator support:

```bash
python scripts/run_minimal_traversability_report.py \
  --point-ledger runs/stage1_v5_selected_candidate_ledger/source_ledger_point_ledger.csv \
  --label selected_v5 \
  --compare-point-ledger runs/stage1_v5_baseline_ledger/source_ledger_point_ledger.csv \
  --compare-label baseline_v5 \
  --outdir runs/stage1_v5_minimal_traversability_report
```

### What the script should compute

The report should compute the following for each case:

```text
live packet point count
live packet packet_norm max, min, and positive count
live packet overlap by region
live packet overlap by stage
live packet overlap with core_throat
live packet overlap with support_edge
live packet overlap with shell active region, e.g. support_shell_window > 1e-3
fraction of each bad channel inside live packet
fraction of each bad channel in geometric packet
fraction of each bad channel outside live packet
fraction of each bad channel in core_throat + support_edge
fraction of each bad channel in support_edge during catch_rematch
location of top bad points by channel
whether top bad points touch live packet
whether top bad points touch geometric packet
packet exposure ratios relative to global burden
```

Use the existing columns:

```text
inside_packet_live
inside_packet_geom
region
stage
packet_norm
support_shell_window
volume_burden_<channel>
bad_<channel>
```

Suggested derived regions:

```text
live_packet_worldtube: inside_packet_live == true
geometric_packet_tube: inside_packet_geom == true
support_plant: region in {core_throat, support_edge, outer_quarantine_shell}
main_support: region in {core_throat, support_edge}
active_shell: support_shell_window > 1e-3
catch_support_shell: stage == catch_rematch and region == support_edge
nonpacket_infrastructure: not inside_packet_live and region in support plant regions
```

The key table should look like this conceptually:

```text
channel | total burden | live packet burden | live packet fraction | main support burden | main support fraction | top bad point region | top bad point in live packet?
```

The script should also emit a compact decision sheet:

```text
packet_norm_safe: true/false
live_packet_core_throat_overlap_points: integer
live_packet_support_edge_overlap_points: integer
max_live_packet_fraction_any_channel: float
max_top_bad_points_in_live_packet: integer
support_burden_dominates_packet_burden: true/false
minimal_traversability_status: pass / warning / fail
```

### Suggested status rules

Use these as first-pass rules. They can be adjusted after seeing the numbers.

Pass:

```text
positive_packet_norm_live == 0
live_packet_core_throat_overlap_points == 0 or clearly negligible and explained
live_packet_support_edge_overlap_points is negligible or low-burden
max_live_packet_fraction_any_channel is tiny, preferably below 1e-4 to 1e-3
no top bad point in any hard channel lies inside the live packet worldtube
main source burden is infrastructure-side, not packet-side
```

Warning:

```text
packet norm remains safe but live packet overlaps support_edge with nontrivial burden
or one hard channel has a live packet fraction large enough to require redesign
or top bad points sit close to the packet boundary
```

Fail:

```text
positive_packet_norm_live > 0
or top radial null / negative density burden sits inside live packet
or live packet burden is not meaningfully separated from support burden
or the packet worldtube effectively crosses the same expensive support region that a passenger-traversable throat would require
```

### How to write the report

The report should be narrative, not just computational. It should explain the meaning of the result in human terms.

A good report structure:

```text
1. Why this test matters
2. What counts as ordinary passenger traversability here
3. What the active rail would need instead if the bypass intuition is right
4. How the packet worldtube was identified
5. Where the demanded source burden lives
6. Whether the packet overlaps the hard support burden
7. Decision: ordinary traversability inherited, weakened, or bypassed provisionally
8. Limits of the conclusion
9. Next gate: V10 edge check or Stage II source-family screen
```

The strongest provisional conclusion would be:

```text
The packet worldtube remains timelike/safe and does not occupy the main support-source burden region. The active rail therefore behaves less like a Morris-Thorne passenger-traversed throat and more like a packet service corridor coupled to a support plant.
```

Only write that if the data support it.

### Deliverables for I-B

Create:

```text
toolkit/adm_harness_cli/scripts/run_minimal_traversability_report.py
runs/stage1_v5_minimal_traversability_report/minimal_traversability_report.md
runs/stage1_v5_minimal_traversability_report/minimal_traversability_summary.csv
supporting_reports/STAGE1_V5_MINIMAL_TRAVERSABILITY_SCREEN.md
```

The supporting report can summarize the run output in a polished form.

## Stage I-C: V10 edge check

### Purpose

Do not use V10 to choose the V5 candidate. Use V10 to stress the selected candidate after V5 stabilizes.

The earlier validation ladder showed that the selected tiny target survived V10, while high-amplitude ramping became more restrictive. The current high-amplitude coupled candidate is a different object. It needs an edge check after V5 selection.

### Run pattern

Use the selected Stage I-A candidate and rerun both source-overlay summary and minimal-traversability report at `V = 10`.

Example:

```bash
python scripts/run_source_overlay_sweep.py \
  --variant tuned_w0569_eta200 \
  --service-factor 10 \
  --outdir runs/stage1_v10_selected_candidate_check \
  --amplitudes 0.5 \
  --signs pos \
  --catch-leads <SELECTED_LEAD> \
  --temporal-widths 0.30 \
  --clock-lapse-ratios <SELECTED_CLOCK_RATIO> \
  --rail-stretch-ratios 0.0 \
  --throat-capacity-ratios <SELECTED_THROAT_CAPACITY_RATIO> \
  --ns 53 \
  --nl 73 \
  --jobs 1 \
  --case-output
```

Then generate a focused V10 point ledger and run the minimal-traversability report on it.

### V10 decision

The V10 check should not be expected to look as clean as V5. It should answer whether the selected architecture degrades gracefully.

Important readouts:

```text
positive_packet_norm_live
packet_norm_live_delta_max_abs
live packet channel fractions
radial null total ratio
radial current total ratio
angular pressure total ratio
shell-throat overlap concentration
whether any top bad points enter the live packet worldtube
```

A strong V10 result would preserve packet safety and keep top bad points infrastructure-side even if total burden ratios worsen.

### Deliverable for I-C

Create:

```text
supporting_reports/STAGE1_V10_SELECTED_CANDIDATE_EDGE_CHECK.md
```

This report should say whether V10 supports the architecture or exposes a redesign need.

## Stage II overview

Stage II begins only after Stage I identifies the best metric-side candidate and the packet-worldtube result. Stage II adds a source-family compatibility screen.

The current code can compute:

```text
This metric demands this stress-energy here.
```

Stage II asks:

```text
Can a Barceló-Visser-style nonminimally coupled scalar field produce that demanded stress-energy with physically tolerable field values and gradients?
```

This is a new layer. Do not try to fake it by renaming the demanded-source ledger. A demanded-source ledger is not a scalar-source model.

## Stage II-A: scalar-source compatibility screen

### Purpose

The Barceló-Visser issue is not just “negative energy exists.” Their work matters because nonminimally coupled scalar fields can violate classical energy conditions and support traversable wormhole solutions, but the traversable wormhole branch can require trans-Planckian scalar values somewhere. For the active rail, the question becomes:

```text
If the packet worldtube bypasses ordinary passenger traversability, does the remaining support plant still require scalar amplitudes or gradients that are trans-Planckian in a Barceló-Visser-like source model?
```

Stage II does not need to produce a theorem at first. It should produce a compatibility screen that says whether the scalar family looks promising, obviously bad, or undecidable under simple ansatz families.

### New files to add

Add a small source-family module and script:

```text
toolkit/adm_harness_cli/adm_harness/scalar_source_screen.py
toolkit/adm_harness_cli/scripts/run_scalar_source_screen.py
supporting_reports/STAGE2_V5_SCALAR_SOURCE_COMPATIBILITY.md
```

### Inputs

The screen should consume the selected Stage I point ledger and metadata. It should focus first on the dangerous support regions, not the whole grid equally.

Input point ledger:

```text
runs/stage1_v5_selected_candidate_ledger/source_ledger_point_ledger.csv
```

Priority regions:

```text
core_throat
support_edge
shell_throat_overlap if available
catch_rematch + support_edge
top bad neg_Tkk_radial points
top bad abs_pOmega points
top bad abs_j_l points
live packet worldtube as a safety exclusion/check
```

### What the module should model first

Begin with a restricted 2D scalar profile over `(s,l)` aligned with the support windows. Do not attempt a full symbolic tensor derivation if it derails the first screen. The first module can implement a numerical stress-tensor evaluator for a nonminimally coupled scalar ansatz on the existing metric grid.

Candidate scalar profiles:

```text
phi(s,l) = phi0 * support_bump(l) * q(s)
phi(s,l) = phi0 * support_shell_window(s,l)
phi(s,l) = phi0 * [core_throat_profile + shell_partner_profile]
phi(s,l) = phi0 * exp/window combinations with separate throat and shell amplitudes
```

Parameters to scan:

```text
phi0 amplitude
xi nonminimal coupling
throat amplitude ratio
shell amplitude ratio
temporal timing / width if using dynamic scalar shell
radial width / smoothing
```

### Required diagnostics

The scalar screen should report:

```text
max |phi|
max |grad phi| in metric-weighted form if possible
max |box phi| or second-derivative proxy
max |xi * phi^2|
minimum effective gravitational coupling denominator, if using the standard scalar-tensor rearrangement
stress-tensor sign compatibility with demanded channels
channel residuals versus demanded source
residuals in core_throat
residuals in support_edge
residuals in live packet worldtube
whether fitted/scanned solutions require super-Planckian field amplitudes under chosen normalization
whether gradients concentrate at shell-throat overlap
```

A first implementation can use dimensionless Planck units and treat thresholds explicitly as screening conventions:

```text
|phi| > 1          Planck-scale amplitude warning
|grad phi| > 1     Planck-scale gradient warning, subject to coordinate normalization caveats
|xi phi^2| near the effective coupling singular scale   hard warning
large residual in neg_Tkk_radial or abs_pOmega          poor source match
large live-packet scalar burden                          packet contamination warning
```

### Important caution

Do not overclaim the scalar screen. A simple scalar ansatz failing does not prove no scalar-tensor source can work. A simple scalar ansatz passing signs does not prove physical viability. The deliverable is a compatibility screen.

Use language like:

```text
This screen tests whether simple Barceló-Visser-like scalar support is obviously incompatible, provisionally plausible, or still undecided for the selected active-rail support plant.
```

### Possible implementation strategy

A practical first implementation can proceed in layers:

1. Load the selected point ledger.
2. Reconstruct or re-evaluate the metric at each grid point using existing `SourceParams` and selected case metadata.
3. Define scalar profile families on the same `(s,l)` grid.
4. Compute numerical first and second derivatives of `phi` over `s` and `l`.
5. Compute a simplified nonminimal scalar stress tensor in the 2D dynamic sector, with clear documentation of approximations.
6. Project the scalar stress tensor into the same channel language where feasible.
7. Compare signs and magnitudes against demanded-source channels.
8. Scan parameter families and rank them by residual plus Planck-scale penalties.

If full tensor implementation is too much for the first pass, create an explicit reduced screen:

```text
sign/order compatibility for Tkk-like radial null channel
radial current compatibility
angular pressure compatibility proxy
field amplitude and gradient penalties
packet contamination penalty
```

Mark it as reduced and avoid presenting it as a final scalar viability proof.

### Stage II output

Create:

```text
runs/stage2_v5_scalar_source_screen/scalar_source_screen_summary.csv
runs/stage2_v5_scalar_source_screen/scalar_source_screen_candidates.csv
runs/stage2_v5_scalar_source_screen/scalar_source_screen_report.md
supporting_reports/STAGE2_V5_SCALAR_SOURCE_COMPATIBILITY.md
```

The report should answer:

```text
Does a pure/simple Barceló-Visser-like scalar source look viable for the selected support plant?
Does it immediately recreate trans-Planckian amplitude or gradient demand?
Does it match the demanded radial-null/current/angular-pressure signs?
Does it contaminate the packet worldtube?
Does the result suggest pure scalar support, hybrid support, or a different source family?
```

## Expected interpretation logic

Use the following interpretation rules when writing the final reports.

### If Stage I-B passes and Stage II fails

This is a meaningful result. It means the active rail likely changes the traversability architecture, but the tested scalar family is not the right physical source. The next path would be hybrid source assignment, not abandoning the architecture.

Write the conclusion like:

```text
The packet-service architecture is supported, while pure scalar support remains physically strained. The active rail shifts the old traversable-wormhole problem into a narrower support-plant source-realization problem.
```

### If Stage I-B fails

This is serious. It means the packet still overlaps the hard support burden in a way that resembles ordinary passenger traversability. In that case the classic wormhole objections map more directly onto the active rail.

Write the conclusion like:

```text
The current candidate does not yet establish a packet/support separation strong enough to claim bypass of ordinary passenger traversability.
```

Then recommend design changes, likely wider packet exclusion, shifted support shell timing, softer support edge, or different catch/rematch choreography.

### If Stage I-A improves and Stage I-B passes

This is the best near-term result. It means the metric architecture is becoming a real source-placement design rather than a tuned artifact.

Write the conclusion like:

```text
The active rail provisionally behaves as a packet service corridor coupled to a support plant, with demanded source concentrated outside the live packet worldtube and improved by coupled throat-capacity/lapse shaping.
```

### If Stage II finds a plausible scalar candidate

Be cautious. Say it is a promising compatibility result, not a proof. Recommend convergence, sensitivity, and comparison against alternative source families.

### If Stage II finds scalar support is trans-Planckian

This is not surprising. It should be framed as narrowing the source search:

```text
A pure Barceló-Visser-like scalar source remains strained for the selected support plant. The active rail still improves packet/source separation, but physical realization likely requires hybrid or different source families.
```

## Quality requirements for Codex

Do not produce only tables. Every report should explain why the test was run and what conclusion the numbers support.

Do not make physics claims stronger than the code supports. The current source ledger is demanded-source accounting, not a matter-source proof.

Do not treat `V` as ordinary velocity. In prose call it service factor, carried-shift load, or active-rail service factor.

Do not rewrite the existing metric code unless a real bug appears. Stage I should use current code. The main new Stage I code should be the minimal-traversability report script.

Keep report filenames simple and descriptive. Avoid version tombstones in the prose.

Preserve provenance in outputs: command, grid, selected parameters, source files, run directory, and any commit hash if available.

## Final deliverables checklist

Stage I-A:

```text
runs/stage1_v5_throat_capacity_smoke/
runs/stage1_v5_throat_capacity_highres/
supporting_reports/STAGE1_V5_THROAT_CAPACITY_SOURCE_PLACEMENT.md
```

Stage I-B:

```text
toolkit/adm_harness_cli/scripts/run_minimal_traversability_report.py
runs/stage1_v5_selected_candidate_ledger/
runs/stage1_v5_minimal_traversability_report/
supporting_reports/STAGE1_V5_MINIMAL_TRAVERSABILITY_SCREEN.md
```

Stage I-C:

```text
runs/stage1_v10_selected_candidate_check/
runs/stage1_v10_minimal_traversability_report/
supporting_reports/STAGE1_V10_SELECTED_CANDIDATE_EDGE_CHECK.md
```

Stage II:

```text
toolkit/adm_harness_cli/adm_harness/scalar_source_screen.py
toolkit/adm_harness_cli/scripts/run_scalar_source_screen.py
runs/stage2_v5_scalar_source_screen/
supporting_reports/STAGE2_V5_SCALAR_SOURCE_COMPATIBILITY.md
```

Final project-level synthesis after both stages:

```text
supporting_reports/ACTIVE_RAIL_TRAVERSABILITY_AND_SOURCE_COMPATIBILITY_SYNTHESIS.md
```

This synthesis should state, in plain terms, whether the evidence supports the active rail as:

```text
a conventional traversable-wormhole variant,
a packet-service support plant that weakens ordinary traversability requirements,
or an architecture that still needs redesign before that distinction can be defended.
```
