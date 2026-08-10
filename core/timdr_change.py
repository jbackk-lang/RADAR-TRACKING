"""
TIMDR change -- local topological-change operator.

Implements TIMDR(t) as defined in GIA-and-TIMDR/README.md, combining
three classical signal-processing primitives computed on a track's
recent (speed, heading) history:

  T -- skret / turning magnitude (how sharply the heading is changing)
  D -- defekt / z-score of the latest speed against its own window
  R -- rezonans / coherence between speed changes and heading changes
       (do they tend to happen together, i.e. a coordinated manoeuvre?)

Note on T: the abstract TIMDR formalism defines T as a zero-crossing
rate on a scalar signal's derivative. Heading is an angle -- it wraps
and has no natural "sign" -- so a literal zero-crossing count on it is
not meaningful (a straight line and an S-curve can both come out as
"zero crossings" depending on discretisation). T here is adapted to
directly measure turning *magnitude*, wrapped correctly into [-pi, pi],
which is the practically useful question for a tracker.
"""
from __future__ import annotations
import numpy as np


def _twist(headings) -> float:
    """T: largest single-step heading change in the window, normalized
    to [0, 1] (0 = perfectly straight, 1 = a full 180 degree reversal
    in one step). Uses the max (not mean) so a single sharp turn is
    still detected even if it is surrounded by many straight steps."""
    headings = np.asarray(headings, dtype=float)
    if len(headings) < 2:
        return 0.0
    d = np.diff(headings)
    d = (d + np.pi) % (2 * np.pi) - np.pi  # wrap into [-pi, pi]
    return float(np.clip(np.max(np.abs(d)) / np.pi, 0.0, 1.0))


def _defect(series, clip: float = 3.0) -> float:
    """D: |z-score| of the most recent value relative to the window,
    normalized by `clip` into [0, 1]."""
    series = np.asarray(series, dtype=float)
    if len(series) < 2:
        return 0.0
    mu, sigma = series.mean(), series.std()
    if sigma < 1e-12:
        return 0.0
    z = abs((series[-1] - mu) / sigma)
    return float(min(z, clip) / clip)


def _resonance(speed, heading) -> float:
    """R: Pearson correlation between the magnitude of speed changes
    and the magnitude of heading changes, rescaled from [-1, 1] to
    [0, 1]. High R means speed and direction tend to change together
    (a coordinated manoeuvre); low R means they change independently."""
    speed = np.asarray(speed, dtype=float)
    heading = np.asarray(heading, dtype=float)
    if len(speed) < 3 or len(heading) < 3:
        return 0.0
    d_speed = np.abs(np.diff(speed))
    d_heading = np.diff(heading)
    d_heading = np.abs((d_heading + np.pi) % (2 * np.pi) - np.pi)
    if d_speed.std() < 1e-12 or d_heading.std() < 1e-12:
        return 0.0
    corr = np.corrcoef(d_speed, d_heading)[0, 1]
    if np.isnan(corr):
        return 0.0
    return float((corr + 1.0) / 2.0)


def timdr_change(track_history):
    """
    track_history: list of {'x','y','t'} for ONE tracked object, ordered
                   by time (oldest first, most recent last).

    Returns: {'T': float, 'D': float, 'R': float, 'TIMDR': float}, all
             in [0, 1]. TIMDR is the mean of T, D, R -- a high value
             means the object is manoeuvring (turning sharply and/or
             showing an anomalous, coordinated speed+heading change).
    """
    if len(track_history) < 3:
        return {"T": 0.0, "D": 0.0, "R": 0.0, "TIMDR": 0.0}

    xs = np.array([p["x"] for p in track_history], dtype=float)
    ys = np.array([p["y"] for p in track_history], dtype=float)
    ts = np.array([p["t"] for p in track_history], dtype=float)

    dx, dy, dt = np.diff(xs), np.diff(ys), np.diff(ts)
    dt = np.where(dt == 0, 1e-9, dt)

    speed = np.hypot(dx, dy) / dt
    heading = np.arctan2(dy, dx)

    T = _twist(heading)
    D = _defect(speed)
    R = _resonance(speed, heading)

    return {"T": T, "D": D, "R": R, "TIMDR": float(np.mean([T, D, R]))}
