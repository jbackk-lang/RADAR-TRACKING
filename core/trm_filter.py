"""
TRM filter -- spatio-temporal local coherence filter.

Implements TRM(p) exactly as defined in the GIA-and-TIMDR / TRM-Geometry-Core
formalization: a detection p is kept if it has at least `k_min` neighbours
within a spatial radius `d_max` AND a temporal window `dt_max`.

This is the classical density-based / DBSCAN-style "core point" criterion
(points with too few space-time neighbours are dropped as noise), applied
independently along space and time and then intersected. It is not a novel
algorithm -- it is that criterion under the TRM name used across this
ecosystem.
"""
from __future__ import annotations
import numpy as np


def trm_filter(points, d_max: float = 5.0, dt_max: float = 1.0, k_min: int = 2):
    """
    points: iterable of {'x','y','t'} dicts (or (x, y, t) tuples), or a
            numpy structured array with fields 'x', 'y', 't'.
    d_max:  spatial neighbourhood radius.
    dt_max: temporal neighbourhood half-width.
    k_min:  minimum number of neighbours (excluding self) required to
            keep a point.

    Returns: list of the same point dicts that pass the coherence test,
             in the original order.
    """
    pts = _normalize(points)
    n = len(pts)
    if n == 0:
        return []

    xy = np.array([[p["x"], p["y"]] for p in pts], dtype=float)
    t = np.array([p["t"] for p in pts], dtype=float)

    kept = []
    for i in range(n):
        d = np.linalg.norm(xy - xy[i], axis=1)
        spatial = d < d_max
        temporal = np.abs(t - t[i]) <= dt_max
        neighbours = spatial & temporal
        neighbours[i] = False
        if neighbours.sum() >= k_min:
            kept.append(pts[i])
    return kept


def _normalize(points):
    out = []
    for p in points:
        if isinstance(p, dict):
            out.append({"x": float(p["x"]), "y": float(p["y"]), "t": float(p.get("t", 0.0))})
        else:
            out.append({"x": float(p[0]), "y": float(p[1]), "t": float(p[2]) if len(p) > 2 else 0.0})
    return out


def cluster_centroids(points, d_max: float = 5.0):
    """
    Merge nearby points (within `d_max`) into single centroid
    detections using simple connected-components clustering.

    Real targets typically produce several close-together returns in
    one frame (an extended target, or radar range/angle bin spread).
    Feeding those raw points straight into a tracker's one-point-per-
    track association would create a duplicate "ghost" track per real
    object. This groups them first so each physical object becomes one
    detection.

    points: list of {'x','y','t'} dicts (already TRM-filtered, or raw).
    Returns: list of {'x','y','t'} centroids, one per cluster.
    """
    pts = _normalize(points)
    n = len(pts)
    if n == 0:
        return []

    xy = np.array([[p["x"], p["y"]] for p in pts], dtype=float)

    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        d = np.linalg.norm(xy - xy[i], axis=1)
        for j in np.where(d < d_max)[0]:
            if j != i:
                union(i, int(j))

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    centroids = []
    for members in groups.values():
        centroids.append({
            "x": float(np.mean([pts[i]["x"] for i in members])),
            "y": float(np.mean([pts[i]["y"] for i in members])),
            "t": float(np.mean([pts[i]["t"] for i in members])),
        })
    return centroids
