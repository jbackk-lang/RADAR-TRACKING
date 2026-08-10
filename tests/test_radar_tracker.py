import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.radar_tracker import RadarTracker


def _cluster(cx, cy, t, n=2, spread=0.6, rng=random):
    return [{"x": cx + rng.uniform(-spread, spread),
             "y": cy + rng.uniform(-spread, spread),
             "t": t} for _ in range(n)]


def _build_scenario():
    rng = random.Random(42)
    frames = []
    for t in range(8):
        pts = []
        pts += _cluster(2 * t, 0, t, rng=rng)                 # target A: straight
        if t <= 3:
            bx, by = 2 * t, 20
        else:
            bx, by = 6, 20 + 2 * (t - 3)
        pts += _cluster(bx, by, t, rng=rng)                    # target B: turns at t=3
        pts.append({"x": rng.uniform(-50, 50), "y": rng.uniform(-50, 50), "t": t})  # clutter
        frames.append(pts)
    return frames


def test_two_real_targets_become_two_tracks_not_four():
    tracker = RadarTracker(d_max=3.0, dt_max=1.0, k_min=1, gate_chi2=30.0)
    frames = _build_scenario()
    last_result = None
    for frame in frames:
        last_result = tracker.update(frame)
    assert len(last_result) == 2


def test_clutter_never_produces_a_persistent_track():
    tracker = RadarTracker(d_max=3.0, dt_max=1.0, k_min=1, gate_chi2=30.0)
    frames = _build_scenario()
    for frame in frames:
        tracker.update(frame)
    # only 2 track ids should ever have been allocated across the whole run
    assert (tracker._id_counter.__reduce__()[1][0] - 1) == 2


def test_turning_target_gets_flagged_as_manoeuvring():
    tracker = RadarTracker(d_max=3.0, dt_max=1.0, k_min=1, gate_chi2=30.0,
                            manoeuvre_threshold=0.4)
    frames = _build_scenario()
    flagged_any = False
    for frame in frames:
        result = tracker.update(frame)
        if any(info["manoeuvre"] for info in result.values()):
            flagged_any = True
    assert flagged_any


def test_empty_frame_does_not_crash():
    tracker = RadarTracker()
    result = tracker.update([])
    assert result == {}


def test_prune_stale_removes_old_tracks():
    tracker = RadarTracker(d_max=3.0, gate_chi2=30.0)
    tracker.update([{"x": 0, "y": 0, "t": 0}, {"x": 0.2, "y": 0.1, "t": 0}])
    assert len(tracker.tracks) == 1
    removed = tracker.prune_stale(current_t=100, max_age=5)
    assert len(removed) == 1
    assert len(tracker.tracks) == 0


def test_single_frame_single_target_no_crash_no_direction_yet():
    tracker = RadarTracker(d_max=3.0, gate_chi2=30.0)
    result = tracker.update([{"x": 0, "y": 0, "t": 0}, {"x": 0.2, "y": 0.1, "t": 0}])
    assert len(result) == 1
    info = next(iter(result.values()))
    assert info["direction"] is None  # only one detection in history so far
    assert info["manoeuvre"] is False


def test_association_survives_a_missed_detection_gap():
    """
    Track A moves at a steady 5 units/frame, established over 3 frames
    (t=0,1,2 -> x=0,5,10). Then a detection is MISSED at t=3, and the
    next real detection only arrives at t=4, continuing the same
    steady motion to x=20.

    The old greedy association compared new detections against each
    track's LAST observed position using one fixed-radius gate,
    regardless of how much time had passed -- so a 2-frame gap (dt=2)
    covering 10 units of honest, constant-speed motion could fall
    outside a gate sized for a single frame step. This tracker instead
    predicts forward using the actual elapsed dt (here, 2 frames worth
    of the track's own established speed), so the same continuation
    lands almost exactly on the prediction and is correctly matched.
    """
    tracker = RadarTracker(d_max=3.0, dt_max=1.0, k_min=0, gate_chi2=15.0)

    for t in range(3):
        tracker.update([{"x": 5 * t, "y": 0, "t": t}])  # x = 0, 5, 10

    track_id = next(iter(tracker.tracks))
    last_known_x = tracker.tracks[track_id][-1]["x"]
    assert last_known_x == 10.0

    # t=3 missed entirely (empty frame); next detection at t=4
    tracker.update([])
    result = tracker.update([{"x": 20.0, "y": 0, "t": 4}])  # 10 units from last-known

    assert len(tracker.tracks) == 1        # matched to the SAME track
    assert track_id in result
    # the raw detection was appended to the SAME track's history (this
    # is what proves correct association -- the smoothed report itself
    # deliberately lags behind, that's what a stabilizer is for)
    assert tracker.tracks[track_id][-1]["x"] == 20.0
