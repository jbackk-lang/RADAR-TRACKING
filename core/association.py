"""
Hungarian (optimal) data association with gating.

Replaces greedy nearest-neighbour assignment. The greedy version claims
the closest *available* detection track-by-track in whatever order it
happens to iterate, which can produce a locally-plausible but globally
wrong assignment when tracks cross or compete for the same detection --
the classic failure mode where two converging tracks swap identities.
The Hungarian algorithm instead finds the assignment that minimizes
total cost across ALL track-detection pairs simultaneously.

Gating: pairs whose cost exceeds `gate_threshold` are marked infeasible
before solving, and filtered out again after solving as a defensive
check (linear_sum_assignment on a rectangular matrix can still be
forced to return a pair that has no better alternative, even if that
pair is a bad match in absolute terms).
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import linear_sum_assignment

INFEASIBLE = 1e6


def hungarian_associate(track_ids, detections, cost_fn, gate_threshold: float):
    """
    track_ids: list of track identifiers (any hashable), length T.
    detections: list of detections, length D (opaque to this function
                -- only `cost_fn` needs to know their shape).
    cost_fn: callable(track_index, detection_index) -> float, lower is
             a better match. Lets the caller plug in Euclidean,
             Mahalanobis, or any other distance without this module
             needing to know about track state/covariances.
    gate_threshold: pairs with cost_fn(...) > gate_threshold are never
                    matched, regardless of what the optimizer would
                    otherwise prefer.

    Returns: (assignments, unmatched_detection_idx, unmatched_track_ids)
        assignments: dict {track_id: detection_index}
    """
    T = len(track_ids)
    D = len(detections)

    if T == 0 or D == 0:
        return {}, list(range(D)), list(track_ids)

    cost = np.full((T, D), INFEASIBLE, dtype=float)
    for i in range(T):
        for j in range(D):
            c = cost_fn(i, j)
            if c <= gate_threshold:
                cost[i, j] = c

    row_idx, col_idx = linear_sum_assignment(cost)

    assignments = {}
    matched_tracks = set()
    matched_dets = set()
    for r, c in zip(row_idx, col_idx):
        if cost[r, c] <= gate_threshold:
            assignments[track_ids[r]] = int(c)
            matched_tracks.add(track_ids[r])
            matched_dets.add(int(c))

    unmatched_detections = [j for j in range(D) if j not in matched_dets]
    unmatched_tracks = [tid for tid in track_ids if tid not in matched_tracks]
    return assignments, unmatched_detections, unmatched_tracks
