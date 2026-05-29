import pytest

from white_casimir_audit.loop_gen import generate_loops


def test_loop_generation_is_explicitly_deferred_in_phase_one():
    with pytest.raises(NotImplementedError, match="Stage 2"):
        generate_loops(1, 10, 123)
