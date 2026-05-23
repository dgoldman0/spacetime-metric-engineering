# Active Rail Refined Design Base

Current status, 2026-05-23: the active article is the sealed beta075
`V=5` engineered operating embodiment. The current claim is bounded to
prescribed-metric, fixed-background, effective source-family, source-law,
energy-estimate, and local 3+1/backreaction evidence. It is not a physical
matter construction proof, a coupled Einstein-matter evolution, a semiclassical
stress-tensor result, or a service-family theorem.

Do not describe the current package as a `V=10` final refreeze. The latest
service-rating ladder makes `V=5` the active engineered scope:

- `V=5`: sealed operating point with Stage II watch-pass evidence.
- `V=2.5`: live-packet source safety remains clean, but the current
  service-independent medium/support closure calibration does not close.
- `V=10`: fails live-packet source safety in the current beta075 ladder.

Primary entry points:

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

Verification used for the current cleanup review:

```bash
PYTHONPATH=toolkit/adm_harness_cli python -m pytest toolkit/adm_harness_cli/tests
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=/tmp active_rail_technical_disclosure.tex
```
