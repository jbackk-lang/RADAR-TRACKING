"""Experimental, time-aware TIMDR with robust trajectory fitting.

Position sigma is an assumed per-coordinate measurement standard deviation.
Scores are heuristics, not calibrated probabilities. All inputs are past data.
"""
import numpy as np


def _fit(design, xy, sigma):
    weights = np.ones(len(xy))
    for _ in range(8):
        coef = np.linalg.lstsq(design * np.sqrt(weights[:, None]),
                             xy * np.sqrt(weights[:, None]), rcond=None)[0]
        residual = np.linalg.norm(xy - design @ coef, axis=1) / sigma
        weights = np.minimum(1., 3. / np.maximum(residual, 1e-12))
    residual = np.linalg.norm(xy - design @ coef, axis=1) / sigma
    loss = np.sum(np.where(residual <= 3., residual ** 2, 6. * residual - 9.))
    return coef, float(loss)


def timdr_change_robust(history, position_sigma=.12, turn_rate_scale=.5,
                        acceleration_scale=1.):
    zero = dict(T=0., D=0., R=0., TIMDR=0., confidence=0., model='insufficient')
    if not np.isfinite(position_sigma) or position_sigma <= 0:
        raise ValueError('position_sigma must be positive and finite')
    if not np.isfinite(turn_rate_scale) or turn_rate_scale <= 0 or not np.isfinite(acceleration_scale) or acceleration_scale <= 0:
        raise ValueError('positive finite rate scales required')
    if len(history) < 5:
        return zero
    xy = np.array([[p['x'], p['y']] for p in history], float)
    times = np.array([p['t'] for p in history], float)
    if not np.isfinite(xy).all() or not np.isfinite(times).all() or np.any(np.diff(times) <= 0):
        raise ValueError('finite points and strictly increasing times required')
    span = times[-1] - times[0]
    u = (times - times.mean()) / span
    linear = np.column_stack([np.ones(len(u)), u])
    quadratic = np.column_stack([linear, u ** 2])
    c1, loss1 = _fit(linear, xy, position_sigma)
    c2, loss2 = _fit(quadratic, xy, position_sigma)
    improvement = loss1 - loss2 - 2 * np.log(len(u))
    confidence = float(np.clip((improvement - 6.) / 12., 0., 1.))
    if improvement <= 6.:
        return dict(T=0., D=0., R=0., TIMDR=0., confidence=confidence, model='linear')
    velocity = (c2[1][None, :] + 2 * u[:, None] * c2[2][None, :]) / span
    speed = np.linalg.norm(velocity, axis=1)
    heading = np.unwrap(np.arctan2(velocity[:, 1], velocity[:, 0]))
    dt = np.diff(times)
    # A near-stationary vector has an unreliable heading; do not score its angle.
    speed_floor = 3 * np.sqrt(2) * position_sigma / span
    valid = (speed[:-1] > speed_floor) & (speed[1:] > speed_floor)
    turn_rate = np.where(valid, np.abs(np.diff(heading)) / dt, 0.)
    acceleration = np.abs(np.diff(speed)) / dt
    twist = float(np.clip(np.quantile(turn_rate, .9) / turn_rate_scale, 0., 1.))
    defect = float(np.clip(np.quantile(acceleration, .9) / acceleration_scale, 0., 1.))
    resonance = 0.
    if turn_rate.std() > 1e-8 and acceleration.std() > 1e-8:
        corr = float(np.corrcoef(turn_rate, acceleration)[0, 1])
        resonance = max(0., corr) * min(twist, defect)
    # Either a supported turn or supported speed change can indicate manoeuvre.
    score = 1 - (1 - twist) * (1 - defect) * (1 - resonance)
    return dict(T=twist, D=defect, R=resonance, TIMDR=float(score),
                confidence=confidence, model='quadratic')
