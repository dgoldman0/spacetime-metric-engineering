# Stage I-B V5 Minimal-Traversability Packet-Worldtube Screen

## Why This Test Matters

Stage I-B asks the central architecture question: does the selected active-rail metric behave like a protected packet service corridor coupled to a support plant, or does the live packet still inherit the main source burden of an ordinary passenger-traversed throat?

This is not a matter-source proof. It is a demanded-source placement test using the existing 4D source ledger.

## Inputs

Focused point ledgers were generated from:

```text
toolkit/adm_harness_cli/scripts/run_source_ledger.py
```

Run directories:

```text
toolkit/adm_harness_cli/runs/stage1_v5_baseline_ledger/
toolkit/adm_harness_cli/runs/stage1_v5_selected_candidate_ledger/
toolkit/adm_harness_cli/runs/stage1_v5_minimal_traversability_report/
```

The selected V5 candidate was:

```text
variant:                  tuned_w0569_eta200
service factor:           V = 5
support-shell amplitude:  +0.5
catch lead:               1.55
temporal width:           0.30
clock-lapse log gain:     0.1875
rail-stretch log gain:    0.0
throat-capacity log gain: 0.0
grid:                     ns = 53, nl = 73
```

The report was generated with:

```text
toolkit/adm_harness_cli/scripts/run_minimal_traversability_report.py
```

Repository commit at review time:

```text
f8bb7fe
```

## What Counts As Passing Here

A strong minimal-traversability result would have looked like this:

```text
positive_packet_norm_live = 0
live packet carries tiny fractions of each bad channel
top hard-channel bad points stay outside the live packet
main support and nonpacket infrastructure dominate the burden
active support shell does not contaminate the live packet
```

The selected case gets some of this right, but not enough.

## Main Result

The selected candidate keeps the live packet causally safe:

```text
positive_packet_norm_live = 0
max_packet_norm_live = -255.212
live_packet_active_shell_points = 0
```

The support-shell overlay itself is also packet-separated in this report:

```text
live_packet_core_throat_overlap_points = 0
live_packet_support_edge_overlap_points = 0
live_packet_active_shell_points = 0
```

However, the live packet still carries large fractions of the standing demanded-source burden. The decisive channels are radial null and radial pressure:

| case | channel | total burden | live packet fraction | main support fraction | top bad point in live packet? |
|---|---:|---:|---:|---:|---|
| selected_v5 | neg_Tkk_radial | 466.081628 | 0.221837 | 0.767938 | true |
| selected_v5 | abs_p_l | 87.356268 | 0.261006 | 0.730108 | false |
| selected_v5 | abs_pOmega | 3.922808 | 0.002235 | 0.184113 | false |
| selected_v5 | abs_j_l | 0.264303 | 0.008206 | 0.538475 | false |
| selected_v5 | neg_rho_euler | 0.454030 | 0.000000 | 0.012724 | false |
| selected_v5 | neg_rho_packet | 0.955366 | 0.000000 | 0.085961 | false |

The baseline shows essentially the same architectural issue:

| case | channel | total burden | live packet fraction | main support fraction | top bad point in live packet? |
|---|---:|---:|---:|---:|---|
| baseline_v5 | neg_Tkk_radial | 456.965002 | 0.226262 | 0.763325 | true |
| baseline_v5 | abs_p_l | 87.355739 | 0.261008 | 0.730107 | false |
| baseline_v5 | abs_pOmega | 3.720102 | 0.002357 | 0.149517 | false |
| baseline_v5 | abs_j_l | 0.261223 | 0.008303 | 0.533818 | false |
| baseline_v5 | neg_rho_euler | 0.454030 | 0.000000 | 0.012724 | false |
| baseline_v5 | neg_rho_packet | 0.955366 | 0.000000 | 0.085961 | false |

## Interpretation

The selected support-shell component is not the source of the problem. It stays out of the live packet worldtube and does not create packet-norm failures. The problem is deeper: in the current V5 metric, the live packet still resides in a `packet_in_support` corridor that carries substantial radial-null and radial-pressure burden from the standing support architecture.

That means the current candidate does not yet establish the stronger bypass claim:

```text
The packet worldtube remains safe and does not occupy the main support-source burden region.
```

The safer statement is:

```text
The support-shell overlay is packet-separated, but the current standing V5 packet corridor still carries nontrivial hard-channel demanded-source burden.
```

This is a Stage I-B fail for minimal traversability as defined in the handoff plan. It does not invalidate the active-rail architecture as a source-placement program, but it does mean the present candidate cannot yet be described as having bypassed ordinary passenger traversability.

## Design Consequences

The next redesign should focus on the standing packet/support overlap, not on adding more throat-capacity coupling to the selected support shell. Likely directions:

```text
wider or differently placed packet/support separation
reduced standing radial-null burden inside packet_in_support
support plant shifted away from the live packet corridor
more explicit separation between service packet tube and support substrate
revisit live-packet definition only if the current packet mask is overinclusive
```

The immediate Stage II scalar-source screen should not be treated as the main gate yet. A scalar family could fail or pass locally, but the current Stage I-B result says the metric architecture itself still needs a cleaner packet/support separation before strong claims about weakened ordinary traversability are defensible.

## Output Files

```text
toolkit/adm_harness_cli/scripts/run_minimal_traversability_report.py
toolkit/adm_harness_cli/runs/stage1_v5_minimal_traversability_report/minimal_traversability_report.md
toolkit/adm_harness_cli/runs/stage1_v5_minimal_traversability_report/minimal_traversability_summary.csv
toolkit/adm_harness_cli/runs/stage1_v5_minimal_traversability_report/minimal_traversability_channel_summary.csv
toolkit/adm_harness_cli/runs/stage1_v5_minimal_traversability_report/minimal_traversability_top_bad_points.csv
toolkit/adm_harness_cli/runs/stage1_v5_minimal_traversability_report/minimal_traversability_overlap_summary.csv
```

## Decision

Stage I-B status:

```text
fail
```

Reason:

```text
The packet norm is safe and the active support shell stays outside the live packet, but the live packet still carries about 22% of radial-null badness and 26% of radial-pressure badness. The top radial-null point lies inside the live packet region.
```
