import numpy as np
from sync_calibration import read_angle

def estimate_delay(echo_marks,encoder_marks):
    echo=np.asarray(echo_marks,float); encoder=np.asarray(encoder_marks,float)
    if (echo.ndim!=1 or encoder.shape!=echo.shape or len(echo)<3 or
        not np.isfinite(echo).all() or not np.isfinite(encoder).all() or
        np.any(np.diff(echo)<=0) or np.any(np.diff(encoder)<=0)):
        raise ValueError('At least three ordered finite paired timestamps required')
    return float(np.median(echo-encoder))

def marker_samples(seed,delay):
    rng=np.random.default_rng(seed); common=np.linspace(0,.4,8)
    return common+delay+rng.normal(0,20e-6,8),common+rng.normal(0,20e-6,8)

def calibrate_zero(references,known_angles,delay):
    if len(references)<3 or len(references)!=len(known_angles) or not np.isfinite(known_angles).all() or not np.isfinite(delay):
        raise ValueError('At least three known reference observations and finite delay required')
    zero=float(np.mean([read_angle(data,delay)-known for data,known in zip(references,known_angles)]))
    angle_only=float(np.mean([read_angle(data)-known for data,known in zip(references,known_angles)]))
    return dict(delay_s=float(delay),zero_rad=zero,angle_only_rad=angle_only)
