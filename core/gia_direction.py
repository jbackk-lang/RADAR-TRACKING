"""
GIA direction -- dominant local trajectory operator.

Implements GIA(P) exactly as defined in GIA-and-TIMDR/README.md: the
largest eigenvector of the covariance matrix of a local point cloud.
This is the first principal component of classical PCA -- no separate
mathematics is introduced here beyond that.
"""
from __future__ import annotations
import numpy as np


def gia_direction(points):
    """
    points: list of {'x','y', ...} dicts, ordered by time, describing the
            recent history of ONE tracked object (or any local cloud).

    Returns: a unit numpy vector (dx, dy) for the dominant direction, or
             None if fewer than 2 points are available or the points are
             coincident (zero-variance).
    """
    xy = _xy(points)
    if len(xy) < 2:
        return None

    centered = xy - xy.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigvals, eigvecs = np.linalg.eigh(cov)

    # degenerate case: all points coincide (zero variance in every
    # direction) -- eigh still returns unit-norm eigenvectors here, but
    # they are an arbitrary basis, not a meaningful direction.
    if eigvals.sum() < 1e-12:
        return None

    v = eigvecs[:, int(np.argmax(eigvals))]

    # Orient the (otherwise sign-ambiguous) eigenvector so it points from
    # the earliest to the latest point -- this is a convention, not part
    # of the PCA math itself.
    if np.dot(v, xy[-1] - xy[0]) < 0:
        v = -v

    return v


def gia_stability(points):
    """
    GIA-S: how dominant the largest eigenvalue is relative to the total
    variance (1.0 = points lie on a perfect line, 0.5 = isotropic cloud).
    """
    xy = _xy(points)
    if len(xy) < 2:
        return 0.0
    centered = xy - xy.mean(axis=0)
    cov = np.cov(centered, rowvar=False)
    eigvals = np.linalg.eigvalsh(cov)
    total = eigvals.sum()
    return float(eigvals.max() / total) if total > 1e-12 else 0.0


def _xy(points):
    return np.array([[p["x"], p["y"]] for p in points], dtype=float)
