# White Casimir Spatial-Discrimination Findings

Date: 2026-05-29

## Summary

The White et al. sphere-cylinder audit now has a scale-separated v-loop
spatial-discrimination read. This is the most informative scalar result so far:
the broad integrated field remains globally negative, but the separated scale
windows show stable near-shell concentration across seeds and wall-thickness
settings.

The current result supports the view that the sphere-cylinder scalar
morphology contains a real structured component in this proxy. It does not
establish an Alcubierre source-function claim. It does identify a useful final
probe: replace point-hit multi-body counting with a pair-resolved
segment/surface kernel and ask whether the near-shell concentration remains.

## Current Robustness Read

The robust spatial-discrimination run used:

```text
loop method: paper-style v-loop
seeds: 1, 7, 17
wall thicknesses: 0.2 um, 0.4 um
grid: 41 x 41 section over +/- 2.5 um
scale windows: 0.25-0.75, 0.75-1.50, 1.50-2.75, 0.25-5.00 um
loops: 128
points per loop: 200
```

Aggregate read:

| scale window | wall um | negative fraction | near-shell magnitude fraction | near-shell enrichment | top-decile near-shell fraction | boundary magnitude fraction | far-field magnitude fraction | peak radius um |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.25-0.75` | `0.2` | `0.000595` | `0.333333` | sparse | `0.333333` | `0.000000` | `0.000000` | `0.542` |
| `0.25-0.75` | `0.4` | `0.005949` | `0.961516` | high | `1.000000` | `0.000000` | `0.000000` | `1.125` |
| `0.75-1.50` | `0.2` | `0.346421` | `0.638334` | `9.311` | `0.769436` | `0.000239` | `0.000000` | `1.125` |
| `0.75-1.50` | `0.4` | `0.373984` | `0.717771` | `13.414` | `0.879032` | `0.000708` | `0.000000` | `1.125` |
| `1.50-2.75` | `0.2` | `0.918897` | `0.539890` | `6.192` | `0.791065` | `0.006081` | `0.003999` | `1.125` |
| `1.50-2.75` | `0.4` | `0.919096` | `0.567207` | `6.916` | `0.855660` | `0.017108` | `0.000575` | `0.958` |
| `0.25-5.00` | `0.2` | `1.000000` | `0.501386` | `5.305` | `0.727811` | `0.009848` | `0.012458` | `1.125` |
| `0.25-5.00` | `0.4` | `1.000000` | `0.543677` | `6.286` | `0.773176` | `0.026325` | `0.002626` | `1.125` |

The `0.75-1.50 um` window is the cleanest current signal. It is not globally
negative, it places most of the negative magnitude in the near-shell region,
and it keeps boundary and far-field magnitude fractions near zero. The peak
radial bin is stable near `1.125 um` from the sphere center.

The `1.50-2.75 um` window is broader and fills most of the section, but its
top-decile magnitude remains concentrated near the sphere shell. The broad
`0.25-5.00 um` field becomes globally negative because it mixes the localized
scale channels with larger loop support that covers the apparatus. The broad
field is useful as an integration warning, not as the primary morphology read.

## Interpretation

The scale-separated v-loop read is more favorable to White's scalar morphology
than the first global-negativity smoke result. The robust mid-scale window
looks like a localized sphere-cylinder interaction band rather than a uniform
apparatus background. This is the first result in this audit that makes the
White sphere-cylinder morphology worth a final fidelity probe.

The current result remains a scalar morphology result. It does not carry SI
energy normalization, stress-tensor channels, metric-source magnitude closure,
or ordinary electromagnetic readout competition. It also still uses a point-hit
multi-body contact proxy. The next build should improve the physical fidelity
of the contact kernel instead of only increasing loop count.

## Final Build Target

The final build for this side audit should answer one question:

```text
Does a paper-style scalar worldline sphere-wall interaction term remain
localized near the intended sphere-cylinder shell when point-hit body counting
is replaced by pair-resolved segment/surface crossing?
```

The final runner should use:

```text
loop method: paper-style v-loop only
kernel: segment/surface crossing against the sphere and cylinder wall
scoring: pair-resolved sphere-wall interaction, scale windows kept separate
primary windows: 0.75-1.50 um and 1.50-2.75 um
reference window: 0.25-5.00 um broad integration
robustness: 3 seeds, 2 wall thicknesses, modest geometry perturbations
readouts: near-shell magnitude fraction, enrichment, radial peak, top-decile localization, boundary/far/readout leakage
outputs: JSON and CSV summaries, plus averaged fields for the central cases
```

This build is the right local endpoint for the White question. A stable
near-shell result would support the presence of a real scalar morphology in
White's geometry. A fragile or diffuse result would point toward apparatus
integration rather than a robust shell. Either outcome is informative without
turning this side audit into a multi-day reproduction project.

## Artifacts

Current spatial-discrimination outputs:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/outputs/spatial_discrimination/stage2_vloop_spatial_discrimination_summary.json
white_casimir_intersection/experiments/white_casimir_source_function_audit/outputs/spatial_discrimination/stage2_vloop_spatial_discrimination_cases.csv
```

Current runner:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/white_casimir_audit/spatial_discrimination.py
white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage2_spatial_discrimination.sh
```
