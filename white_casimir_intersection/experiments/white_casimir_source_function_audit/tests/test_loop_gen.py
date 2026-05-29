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
        generate_loops(1, 10, 123, method="unknown")
    except ValueError as exc:
        assert "unknown loop generation method" in str(exc)
    else:
        raise AssertionError("unknown loop methods should fail")


def test_v_loop_generation_is_reproducible_and_centered():
    loops_a = generate_loops(4, 30, 321, method="v_loop")
    loops_b = generate_loops(4, 30, 321, method="v_loop")
    assert loops_a.shape == (4, 30, 3)
    assert np.allclose(loops_a, loops_b)
    assert np.allclose(loops_a.mean(axis=1), 0.0, atol=1.0e-12)
    assert np.mean(np.sqrt(np.mean(np.sum(loops_a**2, axis=2), axis=1))) > 0.0
