from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generate_service_factor_inputs as generator
import run_source_ledger as source_runner
import run_source_overlay_sweep as overlay_sweep
import run_validation_ladder as ladder
from adm_harness import source_ledger


class ValidationLadderHardeningTests(unittest.TestCase):
    def test_service_factor_is_inferred_from_matching_configs(self):
        args = SimpleNamespace(service_factor=None)
        baseline = {"service": {"velocity": 5.0}}
        target = {"service": {"velocity": 5.0}}

        self.assertEqual(ladder._infer_service_factor(args, baseline, target), 5.0)

    def test_service_factor_mismatch_is_rejected(self):
        args = SimpleNamespace(service_factor=5.0)
        baseline = {"service": {"velocity": 5.0}}
        target = {"service": {"velocity": 10.0}}

        with self.assertRaises(SystemExit):
            ladder._infer_service_factor(args, baseline, target)

    def test_defaults_are_derived_from_service_factor(self):
        args = SimpleNamespace(output_root=None, packet_member=None)

        output_root, output_inferred = ladder._resolve_output_root(args, "v10")
        packet_member, packet_inferred = ladder._resolve_packet_member(args, 10.0)

        self.assertTrue(output_inferred)
        self.assertEqual(output_root, Path("runs/v10_validation_ladder"))
        self.assertTrue(packet_inferred)
        self.assertEqual(packet_member, "highres_41x73/V10_tuned_w0569_eta200.csv")

    def test_ramp_envelope_keeps_warning_and_failure_separate(self):
        ramp = pd.DataFrame(
            [
                {"amplitude": 1e-4, "status_class": "pass", "hard_gate_passed": True, "warning_flag": False},
                {"amplitude": 5e-4, "status_class": "warning", "hard_gate_passed": True, "warning_flag": True},
                {"amplitude": 1e-3, "status_class": "fail", "hard_gate_passed": False, "warning_flag": True},
            ]
        )

        envelope = ladder._ramp_envelope(ramp)

        self.assertTrue(envelope["enabled"])
        self.assertEqual(envelope["last_no_warning_pass_amplitude"], 1e-4)
        self.assertEqual(envelope["last_hard_pass_amplitude"], 5e-4)
        self.assertEqual(envelope["first_warning_amplitude"], 5e-4)
        self.assertEqual(envelope["first_hard_failure_amplitude"], 1e-3)
        self.assertEqual(envelope["status_counts"], {"fail": 1, "pass": 1, "warning": 1})

    def test_service_factor_generator_writes_reusable_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            metadata = generator.generate_products(
                SimpleNamespace(
                    service_factor=6.0,
                    output_dir=base / "data",
                    config_dir=base / "configs",
                    ns=9,
                    nl=13,
                    w_th=0.569,
                    eta_N=2.0,
                    support_radius=1.75,
                )
            )

            for path in metadata["files"].values():
                self.assertTrue(Path(path).exists(), path)
            self.assertEqual(metadata["service_factor_label"], "v6")
            self.assertIn("max_live_packet_norm", metadata["diagnostics"])
            self.assertIn("catch_support_delta_j_l_fraction", metadata["diagnostics"])

    def test_service_factor_generator_rejects_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            args = SimpleNamespace(
                service_factor=0.0,
                output_dir=base / "data",
                config_dir=base / "configs",
                ns=9,
                nl=13,
                w_th=0.569,
                eta_N=2.0,
                support_radius=1.75,
            )

            with self.assertRaises(SystemExit):
                generator.generate_products(args)

    def test_source_ledger_small_grid_has_heavy_channels(self):
        case = source_ledger.branch_case("tuned_w0569_eta200", service_factor=5.0)
        points = source_ledger.compute_case(case, ns=3, nl=3, progress=False)
        summary, compact, stage, safety, decision = source_ledger.summarize(points)

        self.assertEqual(len(points), 9)
        self.assertIn("Tkk_min_radial", points.columns)
        self.assertIn("p_l_unit", points.columns)
        self.assertIn("rho_packet", points.columns)
        self.assertIn("neg_Tkk_radial", set(compact["channel"]))
        self.assertIn("abs_p_l", set(compact["channel"]))
        self.assertEqual(int(safety["positive_packet_norm_live"].iloc[0]), 0)
        self.assertIn("score", decision.columns)
        self.assertFalse(summary.empty)
        self.assertFalse(stage.empty)
        self.assertFalse(source_ledger.top_bad_points(points, limit=2).empty)

    def test_source_ledger_reference_compare_identity(self):
        case = source_ledger.branch_case("conservative_w0565_eta200", service_factor=5.0)
        points = source_ledger.compute_case(case, ns=3, nl=3, progress=False)
        comparison = source_ledger.compare_to_reference(points, points, reference_case=case.name)

        self.assertGreater(len(comparison), 0)
        self.assertEqual(float(comparison["max_abs_error"].max()), 0.0)

    def test_channel_cause_ledger_decomposes_top_bad_points(self):
        case = source_ledger.branch_case("tuned_w0569_eta200", service_factor=5.0)
        points = source_ledger.compute_case(case, ns=5, nl=5, progress=False)
        cause = source_ledger.channel_cause_ledger(
            points,
            case.params,
            h_s=2.5e-3,
            h_l=2.5e-3,
            limit_per_channel=1,
            channels=["neg_Tkk_radial"],
        )

        self.assertEqual(len(cause), 1)
        row = cause.iloc[0]
        self.assertEqual(row["channel"], "neg_Tkk_radial")
        self.assertIn(row["dominant_derivative_family"], {
            "beta_gradient",
            "lapse_curvature",
            "radial_metric",
            "angular_capacity",
        })
        self.assertAlmostEqual(
            row["Tkk_plus_orthonormal"],
            row["Tkk_plus_orthonormal_reconstructed"],
            places=8,
        )
        self.assertAlmostEqual(
            row["Tkk_minus_orthonormal"],
            row["Tkk_minus_orthonormal_reconstructed"],
            places=8,
        )

    def test_source_ledger_overlay_grid_expands_for_lead_window(self):
        args = SimpleNamespace(
            s_min=None,
            s_max=1.65,
            ns=None,
            nl=73,
            l_min=-2.8,
            l_max=2.8,
            h_s=2.5e-3,
            h_l=2.5e-3,
        )
        baseline = source_ledger.branch_case("tuned_w0569_eta200", service_factor=5.0)
        overlay = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            support_shell_overlay_enabled=True,
        )

        baseline_grid = source_runner._resolve_grid(args, baseline)
        overlay_grid = source_runner._resolve_grid(args, overlay)

        self.assertEqual(baseline_grid["s_min"], -0.35)
        self.assertEqual(baseline_grid["ns"], 41)
        self.assertLess(overlay_grid["s_min"], -0.35)
        self.assertGreater(overlay_grid["ns"], 41)

    def test_source_ledger_support_shell_overlay_changes_metric_smoothly(self):
        case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            support_shell_overlay_enabled=True,
            support_shell_clock_lapse_log_gain=0.10,
            support_shell_rail_stretch_log_gain=-0.05,
            support_shell_throat_capacity_log_gain=0.025,
            support_shell_temporal_profile="minjerk_pulse",
            support_shell_radial_profile="raised_cosine_annulus",
        )
        points = source_ledger.compute_case(
            case,
            ns=5,
            nl=7,
            s_min=-1.0,
            s_max=0.4,
            l_min=-2.8,
            l_max=2.8,
            progress=False,
        )
        safety = source_ledger.summarize_safety(points)

        self.assertIn("support_shell_window", points.columns)
        self.assertIn("support_shell_delta_beta", points.columns)
        self.assertIn("support_shell_delta_alpha", points.columns)
        self.assertIn("support_shell_delta_gamma_ll", points.columns)
        self.assertIn("support_shell_delta_gamma_omega", points.columns)
        self.assertGreater(float(points["support_shell_window"].max()), 0.0)
        self.assertLessEqual(float(points["support_shell_window"].max()), 1.0)
        self.assertGreater(float(points["support_shell_delta_beta"].abs().max()), 0.0)
        self.assertGreater(float(points["support_shell_delta_alpha"].abs().max()), 0.0)
        self.assertGreater(float(points["support_shell_delta_gamma_ll"].abs().max()), 0.0)
        self.assertGreater(float(points["support_shell_delta_gamma_omega"].abs().max()), 0.0)
        self.assertLess(
            float((points["beta"] - points["beta_base"] - points["support_shell_delta_beta"]).abs().max()),
            1.0e-15,
        )
        self.assertLess(
            float((points["alpha"] - points["alpha_base"] - points["support_shell_delta_alpha"]).abs().max()),
            1.0e-15,
        )
        self.assertLess(
            float((points["gamma_ll"] - points["gamma_ll_base"] - points["support_shell_delta_gamma_ll"]).abs().max()),
            1.0e-12,
        )
        self.assertLess(
            float((points["gamma_omega"] - points["gamma_omega_base"] - points["support_shell_delta_gamma_omega"]).abs().max()),
            1.0e-12,
        )
        self.assertEqual(int(safety["positive_packet_norm_live"].iloc[0]), 0)

    def test_source_ledger_packet_radial_smoothing_changes_gamma_ll(self):
        case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            standing_support_packet_radial_log_gain=-0.05,
            standing_support_packet_radial_radius_multiplier=1.2,
            standing_support_packet_radial_width_multiplier=1.6,
            standing_support_packet_radial_schedule="entry_catch_release",
            standing_support_packet_radial_temporal_profile="minimum_jerk",
            standing_support_packet_radial_shoulder_log_gain=0.02,
            standing_support_packet_radial_shoulder_mode="annular",
            standing_support_packet_radial_shoulder_radius_multiplier=1.8,
            standing_support_packet_radial_shoulder_width_multiplier=2.4,
            standing_support_packet_radial_skirt_log_gain=0.01,
            standing_support_packet_radial_skirt_mode="annular",
            standing_support_packet_radial_skirt_inner_radius_multiplier=1.8,
            standing_support_packet_radial_skirt_radius_multiplier=2.2,
            standing_support_packet_radial_skirt_width_multiplier=2.8,
            standing_support_packet_radial_skirt_schedule="entry_catch_release",
            standing_support_packet_radial_skirt_temporal_profile="minimum_jerk",
        )
        points = source_ledger.compute_case(case, ns=5, nl=7, progress=False)

        self.assertIn("standing_support_packet_radial_window", points.columns)
        self.assertIn("standing_support_packet_radial_shoulder_window", points.columns)
        self.assertIn("standing_support_packet_radial_skirt_window", points.columns)
        self.assertIn("standing_support_packet_radial_factor", points.columns)
        self.assertIn("standing_support_packet_delta_gamma_ll", points.columns)
        self.assertGreater(float(points["standing_support_packet_radial_window"].max()), 0.0)
        self.assertGreater(float(points["standing_support_packet_radial_skirt_window"].max()), 0.0)
        self.assertGreater(float(points["standing_support_packet_radial_factor"].sub(1.0).abs().max()), 0.0)
        self.assertGreater(float(points["standing_support_packet_delta_gamma_ll"].abs().max()), 0.0)

    def test_source_overlay_sweep_reports_shell_throat_overlap(self):
        grid = {
            "ns": 5,
            "nl": 9,
            "s_min": -1.0,
            "s_max": 0.4,
            "l_min": -2.8,
            "l_max": 2.8,
            "h_s": 2.5e-3,
            "h_l": 2.5e-3,
        }
        base_case = source_ledger.branch_case("tuned_w0569_eta200", service_factor=5.0)
        overlay_case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            support_shell_overlay_enabled=True,
            support_shell_amplitude=0.5,
            support_shell_catch_lead=1.0,
            support_shell_temporal_width=0.35,
        )
        base_points = source_ledger.compute_case(base_case, progress=False, **grid)
        overlay_points = source_ledger.compute_case(overlay_case, progress=False, **grid)

        summary, _channels, shell_throat = overlay_sweep._compare_case(
            base_points,
            overlay_points,
            {
                "abs_amplitude": 0.5,
                "sign": "pos",
                "amplitude": 0.5,
                "catch_lead": 1.0,
                "temporal_width": 0.35,
                "temporal_profile": "gaussian",
                "temporal_shoulder": None,
                "radial_profile": "smooth_box",
                "support_shell_radial_width": None,
                "clock_lapse_ratio": 0.0,
                "clock_lapse_log_gain": 0.0,
                "rail_stretch_ratio": 0.0,
                "rail_stretch_log_gain": 0.0,
                "throat_capacity_ratio": 0.0,
                "throat_capacity_log_gain": 0.0,
            },
        )

        self.assertGreater(summary["shell_throat_overlap_points"], 0)
        self.assertIn("neg_Tkk_radial_shell_throat_weighted_ratio", summary)
        self.assertIn("abs_j_l_shell_throat_peak_ratio", summary)
        self.assertIn("abs_pOmega_total_ratio", summary)
        self.assertIn("source_objective_score", summary)
        self.assertIn("support_shell_delta_gamma_omega_abs_max", summary)
        self.assertEqual({row["channel"] for row in shell_throat}, set(source_ledger.CHANNELS))

    def test_source_overlay_sweep_specs_include_throat_capacity(self):
        args = SimpleNamespace(
            amplitudes=[0.5],
            signs=["pos"],
            catch_leads=[1.45],
            temporal_widths=[0.30],
            temporal_profiles=["gaussian", "minjerk_pulse"],
            temporal_shoulders=[None],
            radial_profiles=["smooth_box"],
            support_shell_radial_widths=[None, 0.12],
            clock_lapse_ratios=[0.375, 0.5],
            rail_stretch_ratios=[0.0],
            throat_capacity_ratios=[-0.25, 0.0, 0.25],
        )

        specs = overlay_sweep._build_specs(args)

        self.assertEqual(len(specs), 24)
        self.assertEqual({spec["throat_capacity_ratio"] for spec in specs}, {-0.25, 0.0, 0.25})
        self.assertEqual({spec["temporal_profile"] for spec in specs}, {"gaussian", "minjerk_pulse"})
        self.assertEqual({spec["support_shell_radial_width"] for spec in specs}, {None, 0.12})
        for spec in specs:
            self.assertAlmostEqual(spec["throat_capacity_log_gain"], spec["amplitude"] * spec["throat_capacity_ratio"])
            slug = overlay_sweep._case_slug(spec)
            self.assertIn("tp", slug)
            self.assertIn("rp", slug)
            self.assertIn("tc", slug)

    def test_source_overlay_sweep_can_normalize_delta_beta_strength_by_shape(self):
        args = SimpleNamespace(
            amplitudes=[0.5],
            signs=["pos"],
            catch_leads=[1.45],
            temporal_widths=[0.25],
            temporal_profiles=["gaussian"],
            temporal_shoulders=[None],
            radial_profiles=["smooth_box", "raised_cosine_annulus"],
            support_shell_radial_widths=[None],
            clock_lapse_ratios=[0.375],
            rail_stretch_ratios=[0.0],
            throat_capacity_ratios=[0.0],
        )
        config = {
            "variant": "tuned_w0569_eta200",
            "service_factor": 5.0,
            "smoothness_order": 1,
            "support_shell_inner_multiplier": 0.65,
            "support_shell_radial_multiplier": 1.20,
            "support_shell_radial_width": None,
            "packet_exclusion": 1.0,
        }
        grid = {
            "ns": 9,
            "nl": 13,
            "s_min": -0.96,
            "s_max": 0.4,
            "l_min": -2.8,
            "l_max": 2.8,
        }

        specs = overlay_sweep._apply_delta_beta_normalization(
            overlay_sweep._build_specs(args),
            grid,
            config,
            target_delta_beta_abs_max=0.2,
        )

        self.assertEqual(len(specs), 2)
        self.assertEqual({spec["amplitude_normalization"] for spec in specs}, {"target_delta_beta_abs_max"})
        self.assertEqual({spec["target_delta_beta_abs_max"] for spec in specs}, {0.2})
        self.assertNotEqual(specs[0]["abs_amplitude"], specs[1]["abs_amplitude"])
        for spec in specs:
            self.assertAlmostEqual(spec["abs_amplitude"] * spec["window_max_for_normalization"], 0.2)
            self.assertAlmostEqual(spec["clock_lapse_log_gain"], spec["amplitude"] * spec["clock_lapse_ratio"])
            self.assertIn("tdb0p2", overlay_sweep._case_slug(spec))

    def test_source_overlay_sweep_expands_multiple_delta_beta_targets(self):
        args = SimpleNamespace(
            amplitudes=[0.5],
            signs=["pos"],
            catch_leads=[1.45],
            temporal_widths=[0.30],
            temporal_profiles=["gaussian"],
            temporal_shoulders=[None],
            radial_profiles=["raised_cosine_annulus"],
            support_shell_radial_widths=[0.48125],
            clock_lapse_ratios=[0.375],
            rail_stretch_ratios=[0.0],
            throat_capacity_ratios=[0.0],
        )
        config = {
            "variant": "tuned_w0569_eta200",
            "service_factor": 5.0,
            "smoothness_order": 1,
            "support_shell_inner_multiplier": 0.65,
            "support_shell_radial_multiplier": 1.20,
            "support_shell_radial_width": None,
            "packet_exclusion": 1.0,
        }
        grid = {
            "ns": 9,
            "nl": 13,
            "s_min": -0.96,
            "s_max": 0.4,
            "l_min": -2.8,
            "l_max": 2.8,
        }
        base_specs = overlay_sweep._build_specs(args)

        specs = [
            spec
            for target in [0.15, 0.25]
            for spec in overlay_sweep._apply_delta_beta_normalization(base_specs, grid, config, target)
        ]

        self.assertEqual(len(specs), 2)
        self.assertEqual({spec["target_delta_beta_abs_max"] for spec in specs}, {0.15, 0.25})
        self.assertEqual(len({overlay_sweep._case_slug(spec) for spec in specs}), 2)

    def test_packet_temporal_profiles_are_wired_into_windows_and_sweeps(self):
        tanh_case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            standing_support_packet_lapse_log_gain=1.0,
            standing_support_packet_lapse_schedule="entry_catch_release",
            standing_support_packet_lapse_temporal_profile="tanh",
        )
        smooth_case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            standing_support_packet_lapse_log_gain=1.0,
            standing_support_packet_lapse_schedule="entry_catch_release",
            standing_support_packet_lapse_temporal_profile="smoothstep7",
        )

        s = -0.55
        l = s
        tanh_window = source_ledger.standing_support_packet_lapse_window(s, l, tanh_case.params)
        smooth_window = source_ledger.standing_support_packet_lapse_window(s, l, smooth_case.params)

        self.assertGreaterEqual(smooth_window, 0.0)
        self.assertLessEqual(smooth_window, 1.0)
        self.assertNotAlmostEqual(tanh_window, smooth_window)

        args = SimpleNamespace(
            amplitudes=[0.5],
            signs=["pos"],
            catch_leads=[1.55],
            temporal_widths=[0.30],
            temporal_profiles=["gaussian"],
            temporal_shoulders=[None],
            radial_profiles=["smooth_box"],
            support_shell_radial_widths=[None],
            clock_lapse_ratios=[0.375],
            rail_stretch_ratios=[0.0],
            throat_capacity_ratios=[0.0],
            standing_support_packet_lapse_log_gains=[1.0],
            standing_support_packet_lapse_schedules=["entry_catch_release"],
            standing_support_packet_lapse_temporal_profiles=["tanh", "smoothstep7"],
        )

        specs = overlay_sweep._build_specs(args)

        self.assertEqual(len(specs), 2)
        self.assertEqual(
            {spec["standing_support_packet_lapse_temporal_profile"] for spec in specs},
            {"tanh", "smoothstep7"},
        )
        self.assertEqual(len({overlay_sweep._case_slug(spec) for spec in specs}), 2)

    def test_support_shell_shape_defaults_are_compatible_and_profiles_change_window(self):
        default_case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            support_shell_overlay_enabled=True,
        )
        explicit_default_case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            support_shell_overlay_enabled=True,
            support_shell_temporal_profile="gaussian",
            support_shell_radial_profile="smooth_box",
        )
        shaped_case = source_ledger.branch_case(
            "tuned_w0569_eta200",
            service_factor=5.0,
            support_shell_overlay_enabled=True,
            support_shell_temporal_profile="minjerk_pulse",
            support_shell_radial_profile="raised_cosine_annulus",
        )

        s = -0.50
        l = 1.55
        default_window = source_ledger.support_shell_overlay_window(s, l, default_case.params)
        explicit_default_window = source_ledger.support_shell_overlay_window(s, l, explicit_default_case.params)
        shaped_window = source_ledger.support_shell_overlay_window(s, l, shaped_case.params)

        self.assertAlmostEqual(default_window, explicit_default_window)
        self.assertGreater(default_window, 0.0)
        self.assertGreater(shaped_window, 0.0)
        self.assertNotAlmostEqual(default_window, shaped_window)


if __name__ == "__main__":
    unittest.main()
