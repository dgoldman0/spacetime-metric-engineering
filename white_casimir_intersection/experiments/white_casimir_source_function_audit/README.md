# White Casimir Source-Function Audit

This experiment folder implements the White et al. Casimir/Alcubierre-shell
intersection audit inside `white_casimir_intersection/`.

Scope for the first executable phase:

- write the claim manifest;
- define paper-aligned geometry and readout-role objects;
- generate role-region figures before any physics calculation;
- keep active-rail machinery and provenance out of the model.

Run the first phase from the repository root:

```bash
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_smoke.sh
```

The smoke script writes:

```text
outputs/claim_manifest.json
outputs/geometry_role_metadata.json
reports/fig_roles_plate_pillar.png
reports/fig_roles_sphere_cylinder.png
```

The worldline, stress-tensor, linearized metric, EM, and role-sweep modules are
intentionally not implemented in this first phase. They raise explicit
`NotImplementedError` placeholders rather than producing silent proxy results.

Stage 2 now has a deliberately limited scalar smoke path:

```bash
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage2_smoke.sh
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage2_vloop_smoke.sh
```

The first script uses Brownian-bridge closed loops and labels the result as a
reproduction proxy. The second script uses the paper-style v-loop construction
quoted by White et al. Both scripts write plate validation, gap-scaling,
sphere-cylinder proxy, and throughput-estimate artifacts. The v-loop smoke is
closer to reproduction-grade loop generation, while exact energy normalization
and a high-performance C++ path remain future requirements before paper-scale
claims.

Stage 5 evaluates readout transduction candidates against the Stage 3 shell
template and Stage 4 recovery gate:

```bash
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage5_readout_ladder.sh smoke
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage5_readout_ladder.sh focused
```

The priority physical preset runs first-pass apparatus backends for the three
high-priority physical readouts: differential pressure, high-Q cavity shift,
and superconducting resonator shift.

```bash
bash white_casimir_intersection/experiments/white_casimir_source_function_audit/scripts/run_stage5_readout_ladder.sh priority_physical
```

Stage 5 writes zstd parquet ledgers for candidates, templates, synthetic
observations, recovery fits, false positives, gate results, and physical
backend sweeps. The claim boundary is explicit in every row: a surviving
force, pressure, cavity, or resonator readout is a Casimir-boundary or
material-response result unless a separate metric/transit mechanism passes
the amplitude and false-positive gates.
