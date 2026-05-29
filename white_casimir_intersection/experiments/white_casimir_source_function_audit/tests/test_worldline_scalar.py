import numpy as np

from white_casimir_audit.geometry import ParallelPlates, make_xy_grid
from white_casimir_audit.loop_gen import generate_loops
from white_casimir_audit.worldline_scalar import estimate_density_proxy


def test_density_proxy_records_negative_plate_signal_and_metadata():
    loops = generate_loops(8, 40, 7)
    grid = make_xy_grid(-0.5, 0.5, -0.5, 0.5, 3, 3)
    result = estimate_density_proxy(
        ParallelPlates(gap_um=2.0, width_um=10.0, height_um=10.0, thickness_um=0.4),
        grid,
        loops,
        np.linspace(0.5, 3.0, 6),
        random_seed=7,
    )
    assert result["density_proxy"].shape == (3, 3)
    assert np.nanmean(result["density_proxy"]) < 0.0
    assert result["metadata"]["normalization"] == "normalized_morphology_proxy"
    assert result["metadata"]["proxy_status"] == "reproduction_proxy_not_exact_white_method"
