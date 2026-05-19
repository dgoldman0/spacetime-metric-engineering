# Stage I Smeared-Null Diagnostic Progress

## Purpose

The compact handoff branch improved the high-resolution V5 channel-cause ledger, but it also raised a natural question: are we making the design more physically plausible, or only shifting pointwise burden into a form that our current gates like?

The new smeared-null diagnostic is a harness-side answer to that question. It does not change the metric design. It adds a semilocal radial-null summary inspired by the SNEC paper:

```text
toolkit/adm_harness_cli/academic_sources/2503.19955v2.pdf
```

This is not a full SNEC proof. It is a source-ledger proxy that asks whether the negative radial-null contraction remains concentrated across local packet/support windows after smoothing.

## Harness Addition

The source ledger now exposes:

```text
smeared_null_summary(points, smear_widths=(0.25, 0.50, 1.00), ...)
```

and `run_source_ledger.py` writes:

```text
source_ledger_smeared_null.csv
```

The diagnostic uses Gaussian windows centered on the worst radial-null points in selected scopes:

```text
global
live_packet
geometric_packet
catch_rematch
catch_rematch_live_packet
packet_in_support
catch_packet_in_support
```

For each scope and smearing width it reports:

```text
smeared_Tkk_min_radial
smeared_neg_Tkk_part
benchmark_B
benchmark_geometric_floor
margin_to_benchmark_geometric_floor
```

The benchmark floor is the geometric SNEC scale:

```text
-8 pi B / tau^2
```

with `B = 1/(32 pi)` by default. In this first harness proxy, `tau` is identified with the grid-coordinate smearing width. That makes the benchmark useful for relative screening, but it should not be read as a final affine-geodesic SNEC certification.

## Validation

The focused harness test now covers the new summary:

```text
pytest toolkit/adm_harness_cli/tests/test_validation_ladder_hardening.py -q
```

Result:

```text
22 passed
```

## Initial V5 Compact-Handoff Comparison

The first selected run is:

```text
toolkit/adm_harness_cli/runs/stage1_v5_smeared_null_compact_handoff_61x83/
```

Cases:

```text
split_ref
smooth_edge004_tanh
compact7_wide3_edge100
compact7_wide4_edge160
```

The most informative scope is `catch_rematch_live_packet`, because it isolates the packet/support handoff where the channel-cause ledger has been pointing.

| case | smear width | smeared Tkk min | smeared negative part | benchmark floor | margin |
| --- | ---: | ---: | ---: | ---: | ---: |
| `split_ref` | 1.00 | -0.2317 | 0.2519 | -0.2500 | 0.0183 |
| `smooth_edge004_tanh` | 1.00 | -0.2314 | 0.2512 | -0.2500 | 0.0186 |
| `compact7_wide3_edge100` | 1.00 | -0.2100 | 0.2371 | -0.2500 | 0.0400 |
| `compact7_wide4_edge160` | 1.00 | -0.1974 | 0.2211 | -0.2500 | 0.0526 |

At the broad local window, the smeared-null proxy agrees with the channel-cause ledger:

```text
split_ref and tanh smoothing are nearly identical;
wide3 improves the broad handoff accumulation but worsens narrower concentration;
wide4 gives the cleanest broad semilocal relief.
```

At narrower width `0.25`, `compact7_wide3_edge100` is worse than the references, while `compact7_wide4_edge160` remains near the reference. That is why wide3 is not the better candidate despite some live `Tkk` improvement: it still has a sharper local concentration. Wide4 is the better compact branch because it improves the broad handoff burden without creating the same narrow-window penalty.

## Interpretation

This diagnostic strengthens the compact-handoff result. It says the wide4 compact branch is not merely hiding the problem from pointwise gates. It reduces the broad catch/rematch live-packet radial-null accumulation, and it does so in the same direction as the channel-cause derivative reductions.

The result also keeps us honest. The compact branch is not a final SNEC pass. The benchmark margin at broad width is positive for all selected cases, but this is a coordinate-window proxy, not an affine null-geodesic integral. The proper role of the new diagnostic is comparative:

```text
does a candidate reduce local accumulated radial-null burden
without violating packet safety or dumping cost into other live channels?
```

On that question, `compact7_wide4_edge160` is the best current diagnostic candidate.

## Pressure-Aware But Not Dynamic

The user discussion clarified an important design boundary. We are not building dynamic regulators in Stage I. The next design move should remain prescribed choreography, not feedback control.

The data suggests a pressure-aware prescribed law:

```text
entry containment        -> radial pressure balance / live p_l control
broad compact handoff    -> angular-current relief / derivative concentration control
edge recovery            -> live Tkk recovery with peak/current cost
```

Weakening entry is not the answer. It lowers point peaks and angular/current channels, but it makes live `p_l` much worse. Therefore, the next branch should preserve the compact wide4 handoff while adding or reshaping an entry pressure hold that is derivative-limited and centered in the entry/core-throat pressure region.

Recommended next design probe:

```text
base: compact7_wide4_edge160
preserve entry_carve = 0.75
preserve broad catch/edge widths near 3.4 / 7.2
add a pressure-aware entry/core hold or radial-pressure balancing factor
reject variants that recover p_l by losing wide4's j_l, pOmega, or smeared-null gains
```

This keeps the architecture compatible with a future physical regulator idea, but does not introduce dynamic feedback into the current harness.
