from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from adm_harness.beta075_source_law_definition_package import (
    SourceLawDefinitionSpec,
    _decision,
    _family_compatibility,
    _source_law_terms,
    _watch_summary,
    write_source_law_definition_outputs,
)


class Beta075SourceLawDefinitionPackageTests(unittest.TestCase):
    def test_source_law_terms_include_hyperbolicity_and_exchange(self):
        terms = _source_law_terms()

        self.assertIn("reduced_principal_symbol", set(terms["term"]))
        self.assertIn("localized_support_exchange", set(terms["term"]))
        self.assertIn("phase_local_source_scaling", set(terms["term"]))

    def test_family_compatibility_promotes_regulated_director_story(self):
        models = pd.DataFrame([
            {"model_class": "single_canonical_scalar", "compatible_volume_fraction": 0.3},
            {"model_class": "single_phantom_scalar", "compatible_volume_fraction": 0.4},
            {"model_class": "ordinary_type_i_anisotropic_heat_flux", "compatible_volume_fraction": 0.89},
            {"model_class": "regulated_anisotropic_heat_flux_medium", "compatible_volume_fraction": 1.0},
            {"model_class": "multi_field_effective_potential_fallback", "compatible_volume_fraction": 1.0},
        ])
        evidence = pd.DataFrame([
            {"evidence": "principal_symbol_hyperbolicity", "watch": True},
            {"evidence": "phase_local_source_law", "watch": True},
        ])

        family = _family_compatibility(models, evidence)

        self.assertEqual(
            family.loc[family["family"].eq("single_scalar"), "status"].iloc[0],
            "ruled_out_as_primary",
        )
        self.assertEqual(
            family.loc[family["family"].eq("regulated_anisotropic_heat_current_medium"), "status"].iloc[0],
            "core_endpoint_medium",
        )
        self.assertIn(
            "watch",
            family.loc[family["family"].eq("entrained_radial_director_or_aether_like_medium"), "status"].iloc[0],
        )

    def test_decision_passes_with_watches_when_hard_evidence_is_clean(self):
        evidence = pd.DataFrame([
            {"evidence": "source_class_screen", "status": "pass", "watch": False},
            {"evidence": "covariant_tensor_identity", "status": "pass", "watch": False},
            {"evidence": "exchange_localization", "status": "pass", "watch": True},
            {"evidence": "principal_symbol_hyperbolicity", "status": "watch", "watch": True},
            {"evidence": "phase_local_source_law", "status": "phase_local_source_law_candidate_with_watches", "watch": True},
            {"evidence": "observed_1p1_proof_class", "status": "constitutive_1p1_observed_class_proof_obligation_pass", "watch": False},
            {"evidence": "discretization_robustness", "status": "discretization_robustness_pass_with_smooth_variation", "watch": False},
        ])
        family = pd.DataFrame([
            {"family": "single_scalar", "status": "ruled_out_as_primary"},
            {"family": "ordinary_type_i_anisotropic_heat_flux", "status": "too_narrow_alone"},
            {"family": "entrained_radial_director_or_aether_like_medium", "status": "lead_physical_family_with_hyperbolicity_watch"},
        ])

        decision = _decision(evidence, family, SourceLawDefinitionSpec()).iloc[0]

        self.assertEqual(
            decision["source_law_definition_status"],
            "source_law_definition_candidate_with_hyperbolicity_watches",
        )
        self.assertTrue(bool(decision["hard_definition_pass"]))

    def test_watch_summary_combines_evidence_and_family_watches(self):
        evidence = pd.DataFrame([
            {"evidence": "a", "status": "watch", "watch": True, "read": "tight"},
            {"evidence": "b", "status": "pass", "watch": False, "read": "ok"},
        ])
        family = pd.DataFrame([
            {"family": "f", "status": "lead_with_watch", "reason": "sharp"},
            {"family": "g", "status": "pass", "reason": "ok"},
        ])

        watches = _watch_summary(evidence, family)

        self.assertEqual(len(watches), 2)
        self.assertEqual(set(watches["source"]), {"evidence", "family"})

    def test_output_writer_emits_structured_artifacts_only(self):
        outputs = {
            "law_definition": pd.DataFrame([{"term": "t"}]),
            "evidence_summary": pd.DataFrame([{"evidence": "e"}]),
            "family_compatibility": pd.DataFrame([{"family": "f"}]),
            "watch_summary": pd.DataFrame([{"watch": "w"}]),
            "decision": pd.DataFrame([{"source_law_definition_status": "pass"}]),
        }

        with tempfile.TemporaryDirectory() as tmp:
            paths = write_source_law_definition_outputs(Path(tmp), outputs, {"source_name": "test"})
            manifest = json.loads(paths["manifest"].read_text())

            self.assertNotIn("report", paths)
            self.assertNotIn("report", manifest["files"])
            self.assertFalse(any(path.suffix == ".md" for path in Path(tmp).iterdir()))


if __name__ == "__main__":
    unittest.main()
