"""
RadarTracker -- a lightweight multi-object radar tracker built from
the geometric filters defined in this ecosystem (TRM = spatio-temporal
coherence, GIA = dominant direction, TIMDR = change/manoeuvre
detection), plus Hungarian data association with Mahalanobis gating
and an exponential-smoothing stabilizer.

Honest scope note: this is still NOT a Kalman/EKF/particle-filter
tracker. There is no measurement-update step that fuses a prior with a
new observation via a Kalman gain -- position "state" is just the raw
(smoothed) detection history, and the covariance used for gating is a
heuristic growth model (see core/motion_model.py), not an estimated
process/measurement noise model. What upgrading to Hungarian +
Mahalanobis DOES buy you: the per-frame assignment is the global
minimum-cost matching (not whatever a greedy scan happens to grab
first), and the gate adapts -- a manoeuvring track gets a wider,
more forgiving gate than a steady one, instead of one fixed radius for
every track. It is still meant for demos and lightweight fusion, not
safety-critical tracking; see the "Ograniczenia" section in the
README.
"""
from __future__ import annotations
import itertools

from .trm_filter import trm_filter, cluster_centroids
from .gia_direction import gia_direction
from .timdr_change import timdr_change
from .predictor import predict_next
from .association import hungarian_associate
from .motion_model import predict_covariance, mahalanobis_distance_sq, CHI2_95_2DOF


class RadarTracker:
    def __init__(
        self,
        d_max: float = 5.0,
        dt_max: float = 1.0,
        k_min: int = 1,
        history_len: int = 10,
        smoothing: float = 0.5,
        manoeuvre_threshold: float = 0.5,
        gate_chi2: float = CHI2_95_2DOF,
        sigma0: float = 1.5,
        manoeuvre_inflation: float = 4.0,
    ):
        self.d_max = d_max
        self.dt_max = dt_max
        self.k_min = k_min
        self.history_len = history_len
        self.smoothing = smoothing
        self.manoeuvre_threshold = manoeuvre_threshold
        self.gate_chi2 = gate_chi2
        self.sigma0 = sigma0
        self.manoeuvre_inflation = manoeuvre_inflation

        self.tracks: dict[int, list[dict]] = {}
        self._smoothed: dict[int, dict] = {}
        self._id_counter = itertools.count(1)
        self.history: list[dict] = []  # one entry per update() call

    def update(self, points):
        """
        points: list of {'x','y','t'} radar detections for one frame
                (or (x, y, t) tuples).

        Returns: {track_id: {'x','y','t','direction','timdr',
                              'manoeuvre','predicted_next',
                              'predicted_covariance'}}
        """
        if not points:
            return {}

        # 1. TRM -- drop detections with no space-time neighbours
        coherent = trm_filter(points, d_max=self.d_max, dt_max=self.dt_max, k_min=self.k_min)

        # 1b. merge close-together returns from the same physical object
        # into one detection (see cluster_centroids docstring)
        detections = cluster_centroids(coherent, d_max=self.d_max)

        # 2. associate detections to existing tracks: Hungarian assignment
        # (global minimum-cost matching, not greedy) gated by Mahalanobis
        # distance under each track's own predicted uncertainty.
        assignments, unmatched_idx, _unmatched_tracks = self._associate(detections)

        frame_result: dict[int, dict] = {}

        for track_id, det_idx in assignments.items():
            self._append_history(track_id, detections[det_idx])
            frame_result[track_id] = self._advance_track(track_id)

        for det_idx in unmatched_idx:
            track_id = next(self._id_counter)
            self._append_history(track_id, detections[det_idx])
            frame_result[track_id] = self._advance_track(track_id)

        self.history.append(frame_result)
        return frame_result

    # -- internals ---------------------------------------------------

    def _associate(self, detections):
        """Hungarian assignment between existing tracks and this
        frame's detections. Each track's cost against a detection is
        the squared Mahalanobis distance between the detection and
        that track's OWN predicted-next position, under a covariance
        that grows with the prediction time gap and with how much the
        track is currently manoeuvring (see motion_model.py). Pairs
        beyond `gate_chi2` (a 95% confidence ellipse by default) are
        never matched."""
        track_ids = list(self.tracks.keys())
        if not track_ids or not detections:
            return {}, list(range(len(detections))), list(track_ids)

        predicted = [self._predicted_state(tid, detections[0]["t"]) for tid in track_ids]

        def cost_fn(i, j):
            pred_xy, cov = predicted[i]
            det_xy = (detections[j]["x"], detections[j]["y"])
            return mahalanobis_distance_sq(det_xy, pred_xy, cov)

        assignments_by_track, unmatched_idx, unmatched_tracks = hungarian_associate(
            track_ids, detections, cost_fn, gate_threshold=self.gate_chi2
        )
        return assignments_by_track, unmatched_idx, unmatched_tracks

    def _predicted_state(self, track_id, target_t: float):
        """Where this track is expected to be at `target_t`, and how
        uncertain that guess is, based ONLY on its history up to now
        (i.e. computed before this frame's detections are known -- so
        it is fair to use for association, not just for reporting)."""
        hist = self.tracks[track_id]
        direction = gia_direction(hist)
        change = timdr_change(hist)
        dt = target_t - hist[-1]["t"]
        dt = dt if dt > 0 else 1.0
        pred = predict_next(hist, direction, change, dt=dt)
        cov = predict_covariance(dt=dt, timdr_score=change["TIMDR"],
                                  sigma0=self.sigma0, manoeuvre_inflation=self.manoeuvre_inflation)
        return (pred["x"], pred["y"]), cov

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

        # 6. Predictor -- project the next position, plus the same
        # heuristic uncertainty used for gating, reported here so a
        # caller can draw/reason about a confidence ellipse instead of
        # trusting a bare point guess.
        predicted = predict_next(hist, direction, change)
        predicted_cov = predict_covariance(dt=1.0, timdr_score=change["TIMDR"],
                                            sigma0=self.sigma0, manoeuvre_inflation=self.manoeuvre_inflation)

        # 7. Stabilizer -- exponential smoothing of the current position
        stable = self._stabilize(track_id, hist[-1])

        return {
            **stable,
            "direction": None if direction is None else tuple(float(v) for v in direction),
            "timdr": change,
            "manoeuvre": manoeuvring,
            "predicted_next": predicted,
            "predicted_covariance": predicted_cov,
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
