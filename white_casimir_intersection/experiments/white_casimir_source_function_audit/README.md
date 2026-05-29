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
