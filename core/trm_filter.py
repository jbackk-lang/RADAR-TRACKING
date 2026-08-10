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

Complexity: uses a scipy.spatial.cKDTree over (x, y) for the spatial
query instead of the naive O(n^2) all-pairs distance matrix. Practically
this is O(n log n) for the tree build/query, degrading toward O(n^2)
only in the pathological case where most points sit within `d_max` of
each other (a genuinely dense scene has few candidates to filter no
matter what data structure you use). The temporal check is a cheap
vector comparison over each point's (small) spatial candidate set, so
it does not need its own tree.
"""
from __future__ import annotations
import numpy as np
from scipy.spatial import cKDTree


def trm_filter(points, d_max: float = 5.0, dt_max: float = 1.0, k_min: int = 2):
    """
    points: iterable of {'x','y','t'} dicts (or (x, y, t) tuples), or a
            numpy structured array with fields 'x', 'y', 't'.
    d_max:  spatial neighbourhood radius (strict: distance < d_max).
    dt_max: temporal neighbourhood half-width (inclusive: |dt| <= dt_max).
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

    tree = cKDTree(xy)
    # cKDTree's radius query is inclusive (distance <= r); candidates are
    # a superset of the strict "< d_max" points we actually want, so we
    # re-check distance exactly below.
    candidate_lists = tree.query_ball_point(xy, r=d_max)

    kept = []
    for i, candidates in enumerate(candidate_lists):
        cand = np.asarray(candidates, dtype=int)
        cand = cand[cand != i]
        if len(cand) == 0:
            # no candidates at all -- only k_min == 0 can still pass
            if k_min <= 0:
                kept.append(pts[i])
            continue
        d = np.linalg.norm(xy[cand] - xy[i], axis=1)
        spatial = cand[d < d_max]
        temporal_ok = np.abs(t[spatial] - t[i]) <= dt_max if len(spatial) else np.array([], dtype=bool)
        if temporal_ok.sum() >= k_min:
            kept.append(pts[i])
    return kept


def cluster_centroids(points, d_max: float = 5.0):
    """
    Merge nearby points (within `d_max`) into single centroid
    detections using connected-components clustering.

    Real targets typically produce several close-together returns in
    one frame (an extended target, or radar range/angle bin spread).
    Feeding those raw points straight into a tracker's one-point-per-
    track association would create a duplicate "ghost" track per real
    object. This groups them first so each physical object becomes one
    detection.

    Uses scipy.spatial.cKDTree.query_pairs(d_max) to find all
    within-radius pairs in roughly O(n log n) instead of the naive
    O(n^2) all-pairs scan.

    points: list of {'x','y','t'} dicts (already TRM-filtered, or raw).
    Returns: list of {'x','y','t'} centroids, one per cluster.
    """
    pts = _normalize(points)
    n = len(pts)
    if n == 0:
        return []
    if n == 1:
        return [dict(pts[0])]

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

    tree = cKDTree(xy)
    # query_pairs is inclusive (distance <= d_max); re-check strictly to
    # match the "< d_max" convention used everywhere else in this module.
    for i, j in tree.query_pairs(r=d_max):
        if np.linalg.norm(xy[i] - xy[j]) < d_max:
            union(i, j)

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


def _normalize(points):
    out = []
    for p in points:
        if isinstance(p, dict):
            out.append({"x": float(p["x"]), "y": float(p["y"]), "t": float(p.get("t", 0.0))})
        else:
            out.append({"x": float(p[0]), "y": float(p[1]), "t": float(p[2]) if len(p) > 2 else 0.0})
    return out
