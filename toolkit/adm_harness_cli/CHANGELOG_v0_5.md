# ADM Harness CLI service v0.5

Changes in this revision:

- Added mixed catch/rematch allocation windows for packet-edge/support-shell tests.
- New scope names include `catch_rematch_edge_support_mix` and `catch_rematch_mixed`.
- New `allocation_mode: edge_support_mix` alias.
- Mixed windows build packet-edge and support-shell components separately, apply `packet_exclusion`, `edge_bias`, and `support_shell_gain` before smoothing and normalization, then combine the result.
- `service_modifier_summary.csv` now includes window allocation fractions:
  - `window_packet_edge_fraction`
  - `window_support_shell_fraction`
  - `window_packet_live_fraction`
- Added unit coverage for the mixed allocation behavior.

Interpretation:

The new windowing fixes the old washout where support-shell weights had no effect if the starting scope was only `catch_rematch_edge`. ADM decision metrics may still move weakly; this revision makes the knobs real at the window/allocation level so subsequent screens are meaningful.
