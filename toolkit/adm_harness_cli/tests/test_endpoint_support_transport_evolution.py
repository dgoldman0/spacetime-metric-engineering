from __future__ import annotations

import unittest

import numpy as np

from adm_harness.endpoint_support_transport_evolution import (
    EvolutionScenario,
    _evolved_ratio,
)


class EndpointSupportTransportEvolutionTests(unittest.TestCase):
    def test_raw_ratio_can_cross_transport_boundary(self):
        ratio, psi = _evolved_ratio(
            np.array([0.99995]),
            EvolutionScenario("raw", "raw_ratio", 1.0e-4, 0.0),
            0.0,
        )

        self.assertGreater(float(ratio[0]), 1.0)
        self.assertTrue(np.isinf(float(psi[0])))

    def test_rapidity_model_keeps_ratio_bounded(self):
        ratio, psi = _evolved_ratio(
            np.array([0.99995]),
            EvolutionScenario("bounded", "rapidity", 1.0e-4, 0.0),
            0.0,
        )

        self.assertLess(float(ratio[0]), 1.0)
        self.assertTrue(np.isfinite(float(psi[0])))


if __name__ == "__main__":
    unittest.main()
