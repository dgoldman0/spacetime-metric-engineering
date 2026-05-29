# White Casimir Final Fidelity Probe

Date: 2026-05-29

## Summary

The final local probe replaces the earlier point-hit scalar contact proxy with
a pair-resolved segment/surface kernel. The new kernel uses paper-style
v-loops and counts only loops whose line segments cross both the sphere
surface and the inner cylinder wall surface. This is a cleaner scalar
interaction read for the White et al. sphere-cylinder geometry.

The result strengthens the current morphology read. The mid-scale
`0.75-1.50 um` window remains localized near the intended sphere-cylinder
shell across seeds and wall thicknesses. The broad `0.25-5.00 um` integration
still becomes globally negative, but it keeps its strongest magnitude
concentrated near the sphere shell. The global broad-window field is therefore
best read as scale-channel mixing, while the separated mid-scale channel gives
the cleaner morphology signal.

This remains a scalar morphology probe, not a stress-tensor or metric-source
closure. Within that scope, the final build supports the presence of a real
structured scalar interaction in White's sphere-cylinder setup.

## Final Probe Configuration

```text
kernel: pair-resolved segment/surface crossing
surfaces: sphere surface and inner cylinder wall surface
loop method: paper-style v-loop
baseline seeds: 1, 7, 17
perturbation seed: 1
wall thicknesses: 0.2 um, 0.4 um
baseline windows: 0.75-1.50, 1.50-2.75, 0.25-5.00 um
perturbation windows: 0.75-1.50, 1.50-2.75 um
geometry perturbations: sphere 0.9x, sphere 1.1x, cylinder 3.8 um, cylinder 4.2 um
loops: 96
points per loop: 192
grid: 37 x 37 over +/- 2.5 um
workers: 4
```

Single-body controls are built into the pair-resolved scoring rule: a loop
must cross both the sphere and the inner cylinder wall to contribute.

## Baseline Read

| window | wall um | negative fraction | near-shell magnitude fraction | near-shell enrichment | top-decile near-shell fraction | boundary magnitude fraction | far-field magnitude fraction | peak radius um |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.75-1.50` | `0.2` | `0.347699` | `0.646612` | `9.782` | `0.781228` | `0.000283` | `0.000000` | `1.125` |
| `0.75-1.50` | `0.4` | `0.365961` | `0.726420` | `14.206` | `0.883074` | `0.001319` | `0.000000` | `1.125` |
| `1.50-2.75` | `0.2` | `0.892866` | `0.540825` | `6.289` | `0.771857` | `0.012854` | `0.005076` | `1.125` |
| `1.50-2.75` | `0.4` | `0.893109` | `0.567666` | `7.012` | `0.875146` | `0.023294` | `0.000718` | `0.875` |
| `0.25-5.00` | `0.2` | `1.000000` | `0.504602` | `5.437` | `0.708029` | `0.020623` | `0.014162` | `1.125` |
| `0.25-5.00` | `0.4` | `1.000000` | `0.547679` | `6.464` | `0.790754` | `0.032290` | `0.002884` | `1.125` |

The mid-scale baseline result is the cleanest signal. It is not globally
negative, it carries roughly two-thirds to three-quarters of the negative
magnitude in the near-shell band, and its boundary and far-field fractions are
near zero. The peak radius remains at `1.125 um`.

The upper-scale window fills most of the section, but the top-decile magnitude
still remains shell-concentrated. The broad window fills the full section, yet
the near-shell fraction remains about half the total negative magnitude with
`5x-6x` enrichment. This preserves the earlier conclusion that broad
integration mixes localized and apparatus-wide scale channels.

## Perturbation Read

The mid-scale result remains recognizable under the one-seed geometry
perturbations:

```text
cylinder 3.8 um: near-shell fraction 0.718-0.783, enrichment 13.6-19.2
cylinder 4.2 um: near-shell fraction 0.539-0.633, enrichment 6.3-9.2
sphere 0.9 um:   near-shell fraction 0.628-0.719, enrichment 9.7-14.6
sphere 1.1 um:   near-shell fraction 0.689-0.762, enrichment 10.9-15.7
```

The wider cylinder weakens concentration, as expected, but it does not erase
the shell-localized read. The tighter cylinder and thicker wall strengthen the
near-shell fraction. The peak radius remains near `1.125 um` across the
mid-scale perturbation cases.

The upper-scale perturbation cases are broader but still concentrated in their
strongest pixels:

```text
near-shell fraction range: 0.515-0.595
top-decile near-shell range: 0.719-0.942
far-field magnitude fraction: at most 0.006655
```

## Interpretation

The final fidelity probe supports a positive scalar-morphology statement:
within this normalized v-loop scalar proxy, White's sphere-cylinder geometry
does produce a stable near-shell pair interaction. The result is more than a
diffuse apparatus-wide negative field when the scale channels are separated
and the scoring is restricted to actual sphere-inner-wall surface crossings.

The result also clarifies the broad global negativity. Global negativity
appears when larger loop scales are integrated together with the localized
mid-scale channel. That broad field is not the best morphology object. The
scale-separated pair interaction is the more informative object, and it
localizes around the intended shell band.

The stronger White/Alcubierre interpretation remains outside this final local
probe. A source-function claim would still require stress-tensor channels,
normalization, material response, and metric-source magnitude comparison. A
transport claim would additionally require ordinary electromagnetic readout
competition. The final result says that the scalar morphology is worth taking
seriously as a Casimir-shaping feature; it does not by itself establish a warp
source.

## Artifacts

Final runner:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/white_casimir_audit/fidelity_probe.py
white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage2_fidelity_probe.sh
```

Final outputs:

```text
white_casimir_intersection/experiments/white_casimir_source_function_audit/outputs/fidelity_probe/stage2_final_fidelity_probe_summary.json
white_casimir_intersection/experiments/white_casimir_source_function_audit/outputs/fidelity_probe/stage2_final_fidelity_probe_cases.csv
white_casimir_intersection/experiments/white_casimir_source_function_audit/outputs/fidelity_probe/fields/
```

Verification:

```text
PYTHONPATH=white_casimir_intersection/experiments/white_casimir_source_function_audit python -m pytest white_casimir_intersection/experiments/white_casimir_source_function_audit/tests
11 passed
```
