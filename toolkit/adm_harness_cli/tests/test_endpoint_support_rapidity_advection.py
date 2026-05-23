from __future__ import annotations

import unittest

import numpy as np

from adm_harness.endpoint_support_rapidity_advection import _apply_budget_limiter, _upwind_step


class EndpointSupportRapidityAdvectionTests(unittest.TestCase):
    def test_upwind_step_does_not_increase_maximum(self):
        values = np.array([0.0, 0.2, 1.0, 0.4, 0.0])

        outward = _upwind_step(values, cfl=0.45, direction="outward")
        inward = _upwind_step(values, cfl=0.45, direction="inward")

        self.assertLessEqual(float(outward.max()), float(values.max()))
        self.assertLessEqual(float(inward.max()), float(values.max()))

    def test_budget_limiter_clips_only_over_budget_values(self):
        values = np.array([0.2, 1.2, 0.5])
        budgets = np.array([1.0, 1.0, 2.0])

        limited, clipped = _apply_budget_limiter(values, budgets, safety_fraction=0.95)

        np.testing.assert_allclose(limited, np.array([0.2, 0.95, 0.5]))
        np.testing.assert_allclose(clipped, np.array([0.0, 0.25, 0.0]))


if __name__ == "__main__":
    unittest.main()
