"""Experimental soft innovation weighting; not a Kalman update."""
import numpy as np

def fuse_position(measured, predicted, amplitude_bad=False, mode='hybrid', radius=.12):
    """Use geometry alone unless BOTH geometry and amplitude disagree.

    radius is a supplied spatial tolerance in metres, not learned confidence.
    The returned point is a fused estimate, never a raw sensor observation.
    """
    z=np.asarray(measured,dtype=float); p=np.asarray(predicted,dtype=float)
    if z.shape!=(2,) or p.shape!=(2,) or not np.isfinite(z).all() or not np.isfinite(p).all():
        raise ValueError('Expected finite 2D positions')
    if mode not in ('geometry','hybrid') or not np.isfinite(radius) or radius<=0:
        raise ValueError('Invalid mode or radius')
    distance=float(np.linalg.norm(z-p))
    weight=min(1.,radius/max(distance,1e-15))
    if mode=='hybrid' and amplitude_bad and distance>radius:
        weight=weight**2
    weight=max(.02,weight)
    return p+weight*(z-p),float(weight)
