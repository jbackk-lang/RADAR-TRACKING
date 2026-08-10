"""
Lightweight positional uncertainty model.

Honest scope note: this is NOT a Kalman filter. There is no
measurement-update step that fuses a prior estimate with a new
observation via a Kalman gain, and no process/measurement noise
covariance estimated from real sensor data. It is a heuristic
covariance-growth model: uncertainty starts small and grows with
(a) how far into the future a prediction projects, and (b) how much
the object is currently manoeuvring (its TIMDR score), because a
constant-velocity extrapolation is a worse guess for an object that is
actively turning or changing speed.

It exists to support two genuinely useful things without pretending to
be a full Bayesian filter: Mahalanobis-gated association (core/
association.py), and reporting a confidence ellipse alongside a point
prediction instead of a bare (x, y) guess.
"""
from __future__ import annotations
import numpy as np

# 95% confidence threshold for a chi-square distribution with 2 degrees
# of freedom (2D position gating).
CHI2_95_2DOF = 5.991


def predict_covariance(dt: float, timdr_score: float,
                        sigma0: float = 1.0, manoeuvre_inflation: float = 4.0) -> np.ndarray:
    """
    dt: how far ahead the prediction projects (time units).
    timdr_score: the track's current TIMDR['TIMDR'] value in [0, 1]
                 (0 = steady, 1 = strongly manoeuvring).
    sigma0: base positional uncertainty growth rate per unit time for a
            *non*-manoeuvring object (isotropic -- same in x and y).
    manoeuvre_inflation: extra uncertainty (as a multiple of sigma0) a
            fully-manoeuvring object (timdr_score == 1) gets on top of
            the base rate.

    Returns: 2x2 isotropic covariance matrix (independent x/y noise).
    """
    dt = max(float(dt), 1e-6)
    score = float(np.clip(timdr_score, 0.0, 1.0))
    inflated_sigma = sigma0 * (1.0 + manoeuvre_inflation * score)
    variance = (inflated_sigma * dt) ** 2
    return np.eye(2) * variance


def mahalanobis_distance_sq(point_xy, mean_xy, cov: np.ndarray) -> float:
    """Squared Mahalanobis distance between `point_xy` and `mean_xy`
    under covariance `cov`. Falls back to squared Euclidean distance if
    `cov` is singular (should not happen with predict_covariance's
    isotropic output, but kept for safety with hand-built covariances)."""
    diff = np.asarray(point_xy, dtype=float) - np.asarray(mean_xy, dtype=float)
    try:
        inv_cov = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        return float(diff @ diff)
    return float(diff @ inv_cov @ diff)


def within_gate(point_xy, mean_xy, cov: np.ndarray, chi2_threshold: float = CHI2_95_2DOF) -> bool:
    """Whether `point_xy` falls inside the `chi2_threshold` confidence
    ellipse of a 2D Gaussian centered at `mean_xy` with covariance `cov`."""
    return mahalanobis_distance_sq(point_xy, mean_xy, cov) <= chi2_threshold
