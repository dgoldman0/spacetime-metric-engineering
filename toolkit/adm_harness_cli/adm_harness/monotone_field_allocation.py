"""C1 field allocation preserving the registered intervalwise safety bounds."""
import numpy as np
from scipy.interpolate import PchipInterpolator


def monotone_allocation(knots,values):
    """Return shape-preserving values and gradients between safe knot values.

    Each registered endpoint value is below both neighboring interval minima.
    PCHIP stays between each pair of endpoint values, so it preserves that
    intervalwise cap while allowing continuous nonzero slopes at ordinary knots.
    """
    knots,values=np.asarray(knots),np.asarray(values)
    if knots.shape!=values.shape or np.any(np.diff(knots)<=0) or np.any(values<0):
        raise ValueError('ordered covered knots and nonnegative safe values required')
    spline=PchipInterpolator(knots,values,extrapolate=False)
    derivative=spline.derivative()
    return lambda x:(spline(x),derivative(x))
