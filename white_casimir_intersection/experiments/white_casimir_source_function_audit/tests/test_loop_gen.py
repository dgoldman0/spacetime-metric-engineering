import numpy as np

from white_casimir_audit.loop_gen import generate_loops


def test_brownian_bridge_loop_generation_is_reproducible_and_closed():
    loops_a = generate_loops(3, 20, 123)
    loops_b = generate_loops(3, 20, 123)
    assert loops_a.shape == (3, 20, 3)
    assert np.allclose(loops_a, loops_b)
    assert np.allclose(loops_a.mean(axis=1), 0.0, atol=1.0e-12)


def test_unknown_loop_method_is_deferred():
    try:
        generate_loops(1, 10, 123, method="v_loop")
    except NotImplementedError as exc:
        assert "brownian_bridge" in str(exc)
    else:
        raise AssertionError("v_loop should remain deferred until exact implementation")
