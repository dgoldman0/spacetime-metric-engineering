# White Casimir V-Loop Global Negativity Read

Date: 2026-05-29

## Summary

This note records the current scalar worldline proxy read for the
White et al. sphere-cylinder intersection after adding a paper-style v-loop
generator beside the Brownian-bridge smoke generator.

The plate validation behaves in the expected direction for both generators:
the mean proxy is negative, the field is approximately symmetric, and the
negative magnitude weakens as the plate gap increases. The v-loop generator
improves the plate symmetry read from `0.102105` to `0.029688`, which is a
useful alignment check for the loop construction.

The sphere-cylinder read remains globally negative at smoke resolution. In
the current scalar proxy this means that every sampled grid center has some
translated and scaled loops that touch multiple material bodies and therefore
receive a negative contribution. The field still has contrast, but it is not
yet a localized source-shell map.

## Current Reads

Brownian-bridge scalar proxy:

```text
plate mean negative: true
plate symmetry relative error: 0.102105
gap scaling pass: true
gap 2 um mean negative magnitude: 1.087966
gap 4 um mean negative magnitude: 0.107803
gap 8 um mean negative magnitude: 0.009735
sphere-cylinder proxy minimum: -5.861237
sphere-cylinder proxy mean: -0.442956
sphere-cylinder negative pixels: 625 / 625
sphere-cylinder |min| / |mean| contrast: 13.232099
```

Paper-style v-loop scalar proxy:

```text
plate mean negative: true
plate symmetry relative error: 0.029688
gap scaling pass: true
gap 2 um mean negative magnitude: 0.134296
gap 4 um mean negative magnitude: 0.011391
gap 8 um mean negative magnitude: 0.000449
sphere-cylinder proxy minimum: -0.615142
sphere-cylinder proxy mean: -0.049338
sphere-cylinder negative pixels: 625 / 625
sphere-cylinder |min| / |mean| contrast: 12.467808
```

The v-loop amplitudes are smaller than the Brownian-bridge amplitudes while
preserving the same qualitative checks. That is a helpful distinction: loop
construction changes the scale and plate symmetry, while the sphere-cylinder
field continues to behave as an apparatus-wide interaction map under the
current scalar scoring rule.

## Physical Read

The global negativity is best read as a spatial-discrimination result, not as
a source-function result. The scalar proxy currently counts multi-body loop
contacts and weights those contacts negatively. In the compact sphere-cylinder
geometry, many translated loops can reach both the central sphere and the
cylinder wall, or sample the nearby material boundaries, across the full
section. The output therefore identifies a broad Casimir-interaction support
region before it identifies a resolved shell.

This read places the burden on localization. A White-style Alcubierre analogy
needs a robustly shaped negative-energy morphology, not only a negative
apparatus field. The current data show that the v-loop construction preserves
the expected plate checks and reduces the sphere-cylinder amplitude, but the
coarse sphere-cylinder field still fills the sampled section. A stronger
claim requires the negative support to organize around the intended
sphere-cylinder shell or torus after subtraction, scale selection, and grid
refinement.

The current result is therefore a useful branch point. If tighter scale
windows, thinner boundary representation, explicit control subtraction, and
finer local grids produce a localized shell, the White morphology becomes a
more concrete Casimir-shaping target. If those controls continue to produce a
globally negative section, the calculation reads more naturally as a diffuse
apparatus interaction than as a resolved warp-shell source analogue.

## Next Spatial-Discrimination Gate

The next executable gate should keep the v-loop generator and test whether the
sphere-cylinder field becomes spatially informative under tighter sampling:

```text
loop method: paper-style v-loop
grid: refined sphere-cylinder section around the sphere and inner wall
scale windows: narrow low/mid/high windows rather than one broad 0.25-5.0 um sweep
boundary model: thinner wall-thickness sweep where the grid can resolve it
controls: sphere-only, cylinder-only, and combined-minus-controls subtraction
readout: negative fraction, contrast, minimum coordinate, and shell-region concentration
```

The central readout is shell-region concentration. A spatially informative
result should put a larger fraction of the negative magnitude in the intended
source-shell candidate region than in the far-field or ordinary boundary
region. That is the next clear discriminator between a localized
sphere-cylinder morphology and a broad apparatus interaction field.

## Artifacts

Current summary files:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/outputs/stage2_smoke_summary.json
white_casimir_intersection/experiments/white_casimir_source_function_audit/outputs/stage2_smoke_summary_v_loop.json
```

Current figure files:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/reports/fig_sphere_cylinder_density_proxy_smoke.png
white_casimir_intersection/experiments/white_casimir_source_function_audit/reports/fig_sphere_cylinder_density_proxy_smoke_v_loop.png
```
