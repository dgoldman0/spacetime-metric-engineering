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


def canonical_matched_actuation(amplitude, *, correction_limit=1e-8):
    """Remove only numerical mismatch from an explicitly matched pair.

    A common phase is a constrained design choice in the optimizer. This
    reconstruction rejects independent histories instead of imposing that
    physical change during post-processing.
    """
    amplitude=np.asarray(amplitude,dtype=float)
    if amplitude.ndim!=2 or amplitude.shape[1]<2 or not np.isfinite(amplitude).all():
        raise ValueError('a finite spatially sampled phase history is required')
    common=np.broadcast_to(amplitude.mean(axis=1,keepdims=True),amplitude.shape).copy()
    if np.max(np.abs(common-amplitude))>correction_limit:
        raise ValueError('pair phase mismatch exceeds the explicit reconstruction limit')
    physical,forward,reverse=canonical_actuation(common,correction_limit=correction_limit)
    if np.max(np.abs(physical-amplitude))>correction_limit:
        raise ValueError('combined matched-phase correction exceeds the reconstruction limit')
    return physical,forward,reverse
