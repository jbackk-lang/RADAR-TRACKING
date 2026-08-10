"""
Predictor -- simple kinematic extrapolation.

Projects the next position from the object's last known speed and the
GIA-derived dominant direction. The step is damped by the TIMDR change
score: a high TIMDR score means the object is mid-manoeuvre, so a
straight-line extrapolation is less trustworthy and the step is shrunk
accordingly. This is a heuristic, not a probabilistic motion model --
there is no explicit process/measurement noise as in a Kalman filter.
"""
from __future__ import annotations
import numpy as np


def predict_next(track_history, direction, change, dt: float = 1.0):
    """
    track_history: list of {'x','y','t'} for one tracked object, ordered
                   by time (most recent last).
    direction: unit vector (dx, dy) from gia_direction(), or None.
    change: dict returned by timdr_change() (uses the 'TIMDR' key).
    dt: time step to project forward.

    Returns: {'x': float, 'y': float, 't': float}
    """
    last = track_history[-1]

    if len(track_history) >= 2:
        prev = track_history[-2]
        dt_hist = last["t"] - prev["t"]
        dt_hist = dt_hist if dt_hist != 0 else 1e-9
        speed = float(np.hypot(last["x"] - prev["x"], last["y"] - prev["y"]) / dt_hist)
    else:
        speed = 0.0

    if direction is None:
        step = np.array([0.0, 0.0])
    else:
        step = np.array(direction, dtype=float) * speed * dt

    timdr_score = float(change.get("TIMDR", 0.0)) if isinstance(change, dict) else 0.0
    # damping in [0.2, 1.0]: never trust the straight-line guess at 0,
    # never fully discard it at 1 -- a manoeuvring object still has SOME
    # momentum.
    damping = max(0.2, 1.0 - timdr_score)
    step = step * damping

    return {
        "x": last["x"] + float(step[0]),
        "y": last["y"] + float(step[1]),
        "t": last["t"] + dt,
    }
