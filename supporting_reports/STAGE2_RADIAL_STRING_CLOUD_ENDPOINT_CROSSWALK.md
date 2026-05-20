# Stage II Radial String-Cloud Endpoint Crosswalk

## Summary

This pass promotes the A/B/I source-family target from a generic radial-tension
shell into a more explicit intermediate source picture:

```text
constant-areal-flux radial string-cloud core
  plus
support-edge shoulder trim
  plus
reset/decompression endpoint cap
```

The result supports the Stage I design architecture. The core radial scaffold is
not the current blocker. After subtracting

```text
rho =  Phi / gamma_omega
p_l = -Phi / gamma_omega
j_l = 0
pOmega = 0
```

the remaining burden is almost entirely non-live and localized in the
support-edge shoulder and reset/decompression cap. That means the next physical
source question is endpoint/anchor closure, not another broad geometry or scalar
search.

## Artifacts

Input dense closure:

```text
toolkit/adm_harness_cli/runs/stage2_external/stage2_entry_sector_closure_component_source_151x225_refined_roles/
```

String-cloud replacement diagnostic:

```text
toolkit/adm_harness_cli/runs/radial_string_cloud_replacement_entry_closure_151x225/
```

Endpoint/shoulder design crosswalk:

```text
toolkit/adm_harness_cli/runs/endpoint_shoulder_crosswalk_entry_closure_151x225/
```

Tooling added:

```text
toolkit/adm_harness_cli/adm_harness/radial_string_cloud.py
toolkit/adm_harness_cli/scripts/run_radial_string_cloud_replacement.py
toolkit/adm_harness_cli/adm_harness/endpoint_shoulder_crosswalk.py
toolkit/adm_harness_cli/scripts/run_endpoint_shoulder_crosswalk.py
```

The original radial-shell viability helper was also tightened so point-level
aggregation is keyed by `label, point_index`, which keeps the diagnostic safe
for future multi-ledger manifests.

These are demanded-source diagnostics. They are not a matter model,
conservation proof, or quantum stress-tensor construction.

## String-Cloud Replacement Result

The constant-flux fit is stable:

```text
Phi global:             0.039772
Phi body-only:          0.039783
Phi pair-L2:            0.039753
body/global delta:      0.0273%
pair residual fraction: 0.4634%
live residual pair:     0.000000
live selected deficit:  0.000000
```

The body/cap split is:

| residual zone | points | pair residual | selected-null deficit | current | angular |
| --- | ---: | ---: | ---: | ---: | ---: |
| core cloud body | `4,966` | `0.064628` | `0.019700` | `0.012137` | `0.205733` |
| support-edge shoulder | `5,222` | `0.337507` | `0.443187` | `0.066263` | `1.499727` |
| reset cap | `4,269` | `0.314444` | `0.567268` | `0.315088` | `2.462061` |

Fractions of the total residual burden:

| residual zone | selected-null | radial pair | current | angular |
| --- | ---: | ---: | ---: | ---: |
| core cloud body | `1.912%` | `9.019%` | `3.085%` | `4.937%` |
| support-edge shoulder | `43.021%` | `47.100%` | `16.840%` | `35.986%` |
| reset cap | `55.066%` | `43.881%` | `80.076%` | `59.077%` |

The practical reading is sharp:

```text
core body: clean enough to promote as a constant-flux string cloud target
support-edge shoulder: handoff/carrying-flow-associated endpoint trim
reset cap: true reset/decompression endpoint closure target
```

## Comparison To Stage I Design Components

The Stage I picture identified these major knobs and gates:

```text
entry service gate
entry pressure containment
compact catch/edge handoff
radial support edge / gamma_ll bearing
carrying-flow beta and current relaxation
throat-capacity / angular jacket
release choreography
reset/decompression infrastructure
live packet vs non-live infrastructure accounting
```

The new residual split aligns with those roles.

The core cloud body corresponds to the prepared non-live standing support
substrate and radial scaffold. It is the piece most compatible with a simple
radial string-cloud law.

The support-edge shoulder corresponds to the compact handoff/support-edge
system. Its residuals still overlap carrying-flow/current, beta-rematch, entry
pressure, and release activity in the design crosswalk. This is not a pure reset
effect, and it should not be hidden inside the live handoff trim.

The reset cap corresponds to reset/decompression endpoint infrastructure. It
carries most of the current residual and a majority of the angular endpoint
residual, but with negligible overlap against the active packet-handoff axes.
That argues for treating it as an endpoint cap model, not as merely the late
tail of the support-edge shoulder.

## Model Implication

The next source model should stay compressed enough to be falsifiable, but it
should no longer be a single radial shell. The recommended intermediate model is:

```text
S0: constant-flux radial string-cloud core
    rho = Phi / gamma_omega
    p_l = -Phi / gamma_omega
    j_l = 0
    pOmega = 0

S1: support-edge shoulder trim
    non-live support-edge radial pair / selected-null trim
    coupled to carrying-flow/current and beta-rematch activity
    allowed to hand off small angular load to G

S2: reset/decompression endpoint cap
    non-live reset/core and reset/support-edge cap
    owns most D/H current relaxation and angular endpoint closure

G: angular/throat-capacity jacket
    separate capacity for transverse pressure, especially endpoint rows

D/H: current relaxation
    non-live current family, especially reset cap first

C/E/F: live handoff trim
    keep separate; no leakage from S0/S1/S2 into live packet rows
```

This is still a simplified source model. It does not promote every Stage I knob
to a separate physical source family. That is deliberate. Entry containment,
beta-rematch, compact edge smoothing, release choreography, and support-shell
overlay remain diagnostic ownership axes until the endpoint model shows where a
true physical family is needed.

## Decision

The design architecture still holds as a source-placement architecture:

```text
live packet safety remains clean;
the radial string-cloud core has zero live burden;
the support-edge and reset endpoint residuals are non-live;
the residual split maps onto existing Stage I components.
```

The source-family selection needs refinement:

```text
single scalar: rejected
single generic radial shell: too coarse
constant-flux radial cloud plus one trim: still too coarse
constant-flux radial cloud plus shoulder trim plus reset cap: current target
```

## Next Work

Build the intermediate source-replacement diagnostic for the model above:

```text
1. Replace the core body with S0.
2. Split support-edge shoulder residual into radial-pair, current, and angular targets.
3. Split reset cap residual into endpoint radial-pair, D/H current, and G angular targets.
4. Produce a sectorized replacement ledger with S0/S1/S2/G/DH/C-E-F/residual columns.
5. Run a light sector-sum hard-affine SNEC comparison before any heavier matter solve.
```

Promotion criterion:

```text
Promote if the S0/S1/S2 split keeps live burden zero, keeps the residual
localized, and does not degrade the existing broad hard-affine SNEC margin.
```

Failure criterion:

```text
If S1 and S2 cannot be separated without large transverse stress, live leakage,
or uncontrolled current divergence, then the source-family problem remains
endpoint-gated even though the metric/service architecture still holds.
```
