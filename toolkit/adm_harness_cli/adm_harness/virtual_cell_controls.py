"""Explicit physical reconstruction of a numerical phase-amplitude history."""
import numpy as np


def canonical_actuation(amplitude, *, correction_limit=1e-8):
    """Return nonnegative phases and one conversion direction per time panel.

    The small nonnegative-amplitude projection is an explicit design change.
    Its resulting controls require fresh propagation and stress validation.
    Large negative input phases are rejected instead of being repaired here.
    """
    amplitude=np.asarray(amplitude,dtype=float)
    if not np.isfinite(amplitude).all() or amplitude.min() < -correction_limit:
        raise ValueError('phase history exceeds the allowed explicit reconstruction correction')
    physical=np.maximum(amplitude,0.)
    change=np.diff(physical,axis=0)
    return physical,np.maximum(change,0.),np.maximum(-change,0.)
