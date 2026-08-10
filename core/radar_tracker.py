"""
RadarTracker -- a lightweight, Kalman-free multi-object radar tracker
built from the three geometric filters already defined in this
ecosystem (TRM = spatio-temporal coherence, GIA = dominant direction,
TIMDR = change/manoeuvre detection), plus a simple nearest-neighbour
data-association step and an exponential-smoothing stabilizer.

Honest scope note: this is deliberately NOT a replacement for a
Kalman/EKF/particle-filter tracker. It has no explicit process or
measurement noise model and no probabilistic state estimate -- it is a
geometric heuristic tracker. The nearest-neighbour association is
greedy and will mis-assign detections in dense or crossing-track
scenes; the TRM filter is O(n^2) per frame. It is meant to be fast,
easy to reason about, and good for demos or lightweight fusion -- not
for safety-critical tracking.
"""
from __future__ import annotations
import itertools
import numpy as np

from .trm_filter import trm_filter, cluster_centroids
from .gia_direction import gia_direction
from .timdr_change import timdr_change
from .predictor import predict_next


class RadarTracker:
    def __init__(
        self,
        d_max: float = 5.0,
        dt_max: float = 1.0,
        k_min: int = 1,
        assoc_max_dist: float = 8.0,
        history_len: int = 10,
        smoothing: float = 0.5,
        manoeuvre_threshold: float = 0.5,
    ):
        self.d_max = d_max
        self.dt_max = dt_max
        self.k_min = k_min
        self.assoc_max_dist = assoc_max_dist
        self.history_len = history_len
        self.smoothing = smoothing
        self.manoeuvre_threshold = manoeuvre_threshold

        self.tracks: dict[int, list[dict]] = {}
        self._smoothed: dict[int, dict] = {}
        self._id_counter = itertools.count(1)
        self.history: list[dict] = []  # one entry per update() call

    def update(self, points):
        """
        points: list of {'x','y','t'} radar detections for one frame
                (or (x, y, t) tuples).

        Returns: {track_id: {'x','y','t','direction','timdr',
                              'manoeuvre','predicted_next'}}
        """
        # 1. TRM -- drop detections with no space-time neighbours
        coherent = trm_filter(points, d_max=self.d_max, dt_max=self.dt_max, k_min=self.k_min)

        # 1b. merge close-together returns from the same physical object
        # into one detection (see cluster_centroids docstring)
        detections = cluster_centroids(coherent, d_max=self.d_max)

        # 2. associate detections to existing tracks
        assignments, unmatched = self._associate(detections)

        frame_result: dict[int, dict] = {}

        for track_id, point in assignments.items():
            self._append_history(track_id, point)
            frame_result[track_id] = self._advance_track(track_id)

        for point in unmatched:
            track_id = next(self._id_counter)
            self._append_history(track_id, point)
            frame_result[track_id] = self._advance_track(track_id)

        self.history.append(frame_result)
        return frame_result

    # -- internals ---------------------------------------------------

    def _associate(self, coherent_points):
        """Greedy nearest-neighbour association: each track claims the
        closest unclaimed detection within `assoc_max_dist`."""
        assignments: dict[int, dict] = {}
        unmatched: list[dict] = []
        available_tracks = {tid: hist[-1] for tid, hist in self.tracks.items()}

        for raw in coherent_points:
            p = {"x": float(raw["x"]), "y": float(raw["y"]), "t": float(raw["t"])}
            best_id, best_dist = None, None
            for tid, last in available_tracks.items():
                d = float(np.hypot(p["x"] - last["x"], p["y"] - last["y"]))
                if d <= self.assoc_max_dist and (best_dist is None or d < best_dist):
                    best_id, best_dist = tid, d
            if best_id is not None:
                assignments[best_id] = p
                del available_tracks[best_id]  # one detection per track per frame
            else:
                unmatched.append(p)
        return assignments, unmatched

    def _append_history(self, track_id, point):
        hist = self.tracks.setdefault(track_id, [])
        hist.append(point)
        if len(hist) > self.history_len:
            del hist[0]

    def _advance_track(self, track_id):
        hist = self.tracks[track_id]

        # 3. GIA -- dominant local direction
        direction = gia_direction(hist)

        # 4. TIMDR -- is the object changing direction / speed?
        change = timdr_change(hist)

        # 5. manoeuvre flag
        manoeuvring = change["TIMDR"] > self.manoeuvre_threshold

        # 6. Predictor -- project the next position
        predicted = predict_next(hist, direction, change)

        # 7. Stabilizer -- exponential smoothing of the current position
        stable = self._stabilize(track_id, hist[-1])

        return {
            **stable,
            "direction": None if direction is None else tuple(float(v) for v in direction),
            "timdr": change,
            "manoeuvre": manoeuvring,
            "predicted_next": predicted,
        }

    def _stabilize(self, track_id, latest_point):
        prev = self._smoothed.get(track_id, latest_point)
        a = self.smoothing
        smoothed = {
            "x": a * latest_point["x"] + (1 - a) * prev["x"],
            "y": a * latest_point["y"] + (1 - a) * prev["y"],
            "t": latest_point["t"],
        }
        self._smoothed[track_id] = smoothed
        return smoothed

    def prune_stale(self, current_t: float, max_age: float):
        """Remove tracks whose most recent detection is older than
        `max_age` relative to `current_t`. Not part of the original
        README sketch, but without it memory grows unboundedly and
        objects that have left the scene keep generating predictions
        forever. Call this once per frame if you care about that.

        Returns the list of track ids that were removed.
        """
        stale = [tid for tid, hist in self.tracks.items() if current_t - hist[-1]["t"] > max_age]
        for tid in stale:
            del self.tracks[tid]
            self._smoothed.pop(tid, None)
        return stale
