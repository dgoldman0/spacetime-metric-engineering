# Stage II Beta075 Moderate 3+1 V5 Capstone

Status: `stage2_moderate_3p1_v5_capstone_watch_pass`.

This is the first moderate local 3+1/backreaction capstone for the sealed
beta075 target service rating, V=5. The run deliberately excludes V=10 because
the current tree does not contain a full V10 Stage II source-family ladder with
the required closure, covariant-audit, and support-reservoir provenance. It also
does not use the lower-service V=2 dense ladder in this first pass. The main
article is the sealed dense V5 surface; the sealed baseline V5 surface is kept
only as a lower-resolution reference and provenance check.

The important distinction from the earlier light proxy is that this run evolves
the current source-family data through an explicit angular and time grid. It
does not merely apply a small scenario multiplier to the closure table. The
capstone writes the time-response field as Parquet under the symlinked external
`runs` tree so the artifacts remain part of the project bundle:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_beta075_moderate_3p1_v5_capstone/
```

## Scope

The run uses:

- service rating: sealed V5 only;
- surfaces: sealed dense V5 as the main article, sealed baseline V5 as a
  reference surface;
- angular lift: `24` azimuthal samples;
- time evolution: `64` scheduled steps;
- scenarios: scheduled axisymmetric, m1 off-axis tilt, m2 shear feedback, and
  mixed off-axis/backreaction;
- heavy output: `218,400,768` time-response rows in Parquet;
- artifact size: about `2.8G` compressed.

The provenance gate passed. The V5 closure and covariant decision files match
their manifests, and both V5 surfaces inherit the support-total closure,
covariant identity, ADM projection, subluminal boost, real mixed eigenvalue,
and exchange-localization passes. No V10 or non-current service surface is
silently substituted into the run.

## Result

The decision row is:

```text
capstone_status: stage2_moderate_3p1_v5_capstone_watch_pass
hard_capstone_pass: true
failed_gate_count: 0
watch_count: 4
time_response_rows: 218400768
worst_driver_surface: sealed_dense_v5
worst_driver_scenario: mixed_offaxis_backreaction
worst_peak_driver_to_endpoint_ratio: 1.6517180604788275
min_cone_margin_proxy: 0.01020650972476278
max_state_to_cumulative_abs_ratio: 1.0
max_feedback_multiplier: 1.0587624648529372
```

The hard read is favorable. The scheduled mean driver stays under budget:

```text
max scheduled mean driver: 0.47612246094557814 / 0.55
```

No live rows are evolved. No limiter clipping is used. The evolved
constraint-response state never exceeds the injected absolute source burden:

```text
live rows evolved: 0
limiter clipping used: false
max state/injected-absolute ratio: 1.0 / 1.000000001
max feedback multiplier: 1.0587624648529372 / 1.08
```

Localization is also clean at this rung. The evolved outside-driver fraction is
zero in the capstone response, inherited live divergence remains below the
audit gate, and support tails remain tiny:

```text
outside response fraction: 0 / 0.006
inherited live driver fraction: 0.00355340101507 / 0.005
outside support tail: 6.35806380433e-06 / 0.001
live support tail: 0 / 0.0001
```

## Watches

The run carries four watches.

The first is the instantaneous scheduled peak. The mixed off-axis/backreaction
case on sealed dense V5 reaches:

```text
peak instantaneous driver: 1.6517180604788275 / 1.75
```

This is not a hard failure because it is a scheduled peak, not the
time-averaged burden. The time-averaged driver remains below the V5 endpoint
budget. Still, the academic interpretation should not hide this number. It says
that timing is a real part of the V5 design, and final 3+1 work should monitor
peak concentration rather than only integrated source strength. The strongest
point-level rows remain reset-decompression/support-edge endpoint-junction
rows, so the familiar tight region stays visible as a watch location. It does
not re-open same-level component tuning, because the pass is achieved without
live rows, clipping, or state growth.

The second watch is the cone margin:

```text
minimum cone-margin proxy: 0.01020650972476278
```

The cone proxy stays subluminal, but the margin is inherited-thin. This agrees
with the previous principal-symbol, energy-estimate, and light backreaction
reads: the package is not wide-margin, but it is not presently running into a
hard hyperbolicity wall at V5.

The third watch is the inherited reset-sector P/F closure:

```text
local P/F ratio: 0.5445669544804586 / 0.55
```

The fourth is the inherited theorem constant:

```text
energy work utilization: 0.8196203784683543
```

These are not new failures from the capstone. They are the same safety-margin
debt carried forward from the formal source-family proof.

## Interpretation

The result is stronger than the earlier proxy because it tests the sealed V5
package as a scheduled angular/time system with full current provenance. The
main driver, localization, state, and feedback gates all pass on the dense V5
article. The capstone therefore supports the claim that beta075 at V5 is not
just an interesting prescribed-metric artifact: the current physical-source
package survives a moderate local 3+1/backreaction stress without relying on
the usual forbidden escape hatches.

The uncomfortable part is also clear. V5 looks viable, but it is timing- and
margin-sensitive. The design is not saying "any schedule works" or "arbitrary
headroom exists." It is saying that the sealed scheduled evolution works, with
peak concentration, cone margin, reset-sector P/F closure, and the energy
constant all marked for the final analysis.

This is enough to move the Stage II narrative toward local evidence synthesis
and external-compute handoff for real off-axis 3+1 grids and final coupled
Einstein-matter/source-family checks. It does not justify a V10 claim. A V10
claim still requires building the full current V10 source-family ladder first.

