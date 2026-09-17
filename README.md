# Active Rail Refined Design Base

Current status, 2026-09-17: the beta075 `V=5` package is the archived
prescribed-metric service reference. The
[rail storage and interface status](supporting_reports/RAIL_STORAGE_AND_INTERFACE_STATUS.md)
connects the current multicomponent containment, mechanical holding,
finite transfer, thermal routing, electrical leads, and microscopic material
results. The moving thermal routes preserve the conditional history bounds.
Physical materials, their joint interfaces, and complete source assembly
remain open.

The [component cross-reference and joint-coordination review](supporting_reports/RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md)
provides the broader source-construction map. It preserves bulk
radial support, angular response, directional quantum support, handoff currents,
and reservoir exchange as explicit responsibilities. Complete source assembly
and a coupled active-rail solution remain open. The support-exchange fit,
static material branches, and tested quantum source each retain their stated
scope and normalization.

The [bounded reorientation](supporting_reports/COUPLED_REORIENTATION_INVESTIGATION.md)
counts backbone, condensate, directional quantum targets, and host separately.
A 95% backbone allocation leaves a small throat quantum target, while angular
response and finite transitions retain larger requirements. The tested
independent planar holders and longitudinal-channel continuation encounter
their stated mechanical and integrated-null-stress barriers.

The [geometry-history cross-reference](supporting_reports/GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md)
connects those new source tests to the existing radius, clock, radial-shape,
transition, and service comparisons, including the archived reasons for
preferring compact support.

The [archived-control source reassessment](supporting_reports/ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md)
tests thirteen transfers on the repaired beta075 static background at fixed
quantum strength. None removes a reference opening-gate exclusion; the small-
coefficient longitudinal route remains below the required supply. The bounded
geometry comparison stops at that source barrier.

Do not describe the current package as a `V=10` final refreeze. The latest
service-rating ladder makes `V=5` the active engineered scope:

- `V=5`: archived operating reference with Stage II effective-model evidence
  and subsequent boundary/source-construction findings.
- `V=2.5`: live-packet source safety remains clean, but the current
  service-independent medium/support closure calibration does not close.
- `V=10`: fails live-packet source safety in the current beta075 ladder.

Primary entry points:

- [Rail storage and interface status](supporting_reports/RAIL_STORAGE_AND_INTERFACE_STATUS.md):
  current subsystem results, shared allocation, physical normalization,
  and remaining material/interface requirements.
- `supporting_reports/ARCHIVED_GEOMETRY_SOURCE_REASSESSMENT.md`: measured
  opening ratios, source-demand tradeoffs, and the geometry-comparison stop.
- `supporting_reports/GEOMETRY_DESIGN_HISTORY_CROSS_REFERENCE.md`: established
  geometry tradeoffs, service constraints, and their relation to the newer
  source-construction tests.
- `supporting_reports/COUPLED_REORIENTATION_INVESTIGATION.md`: counted support
  allocation and construction gates with clock-profile freedom.
- `supporting_reports/RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md`:
  current architecture, trial cross-reference, and joint interaction contract.
- `supporting_reports/COUPLED_SOURCE_ROLE_AUDIT.md`: measured bulk-load
  allocation and static spatial stress requirements.
- `active_rail_technical_disclosure.tex`: current technical disclosure source.
- `active_rail_technical_disclosure.pdf`: generated disclosure PDF when present.
- `supporting_reports/STAGE2_BETA075_MODERATE_3P1_V5_CAPSTONE.md`: latest
  local 3+1/backreaction capstone report for the sealed `V=5` target.
- `supporting_reports/STAGE2_BETA075_SERVICE_RATING_LADDER_DIAGNOSTIC.md`:
  current `V=2.5` and `V=10` service-rating diagnostics.
- `supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_ENERGY_CERTIFICATE.md` and
  `supporting_reports/STAGE2_BETA075_SOURCE_FAMILY_ENERGY_CONSTANT_AUDIT.md`:
  fixed-background source-family energy evidence.
- `toolkit/adm_harness_cli/README.md`: software harness usage, test commands,
  run scripts, and `SourceParams` reference.
- `plan.md`: long-form working handoff for continuing the internal analysis.

Repository map:

- `toolkit/adm_harness_cli/`: ADM/source-ledger harness, scripts, and tests.
- `supporting_reports/`: narrative audit trail and milestone reports.
- `toolkit/adm_harness_cli/runs/`: local/generated run products. This path is
  ignored because the run tree is large; committed reports summarize the key
  decisions and provenance.
- `tables/`, `included_bundles/`, and `included_bundles_manifest.*`:
  historical reduced/refreeze artifacts and archived session bundles. Treat
  them as provenance, not as the current claim.

General harness and disclosure build commands:

```bash
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp active_rail_technical_disclosure.tex
```
