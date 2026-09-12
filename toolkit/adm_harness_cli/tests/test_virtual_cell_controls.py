import numpy as np
import pytest
from numpy.testing import assert_allclose
from adm_harness.virtual_cell_controls import canonical_actuation


def test_reconstructed_controls_preserve_phase_work_without_conversion_cycles():
    original=np.array([.2,-2e-10,.4,.1,0.])[:,None]
    amplitude,forward,reverse=canonical_actuation(original)
    assert amplitude.min()>=0 and forward.min()>=0 and reverse.min()>=0
    assert_allclose(np.diff(amplitude,axis=0),forward-reverse,atol=0,rtol=0)
    assert np.minimum(forward,reverse).max()==0
    assert_allclose(forward.sum()-reverse.sum(),amplitude[-1,0]-amplitude[0,0])
    assert abs(amplitude-original).max()==2e-10


def test_cycle_removal_reduces_both_incident_work_and_conversion_heat():
    amplitude=np.array([.2,.5,.1,.4])[:,None]
    unused,forward,reverse=canonical_actuation(amplitude)
    cycle=np.array([.3,.2,.6])[:,None]
    eta=.98
    old_heat=(1/eta-1)*(forward+cycle)+(1-eta)*(reverse+cycle)
    new_heat=(1/eta-1)*forward+(1-eta)*reverse
    assert np.all(old_heat>new_heat)
    assert np.all((forward+cycle)/eta>forward/eta)


def test_substantial_negative_phase_is_rejected():
    with pytest.raises(ValueError): canonical_actuation(np.array([[.1],[-.001]]))
