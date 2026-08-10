import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.timdr_change import timdr_change


def test_straight_constant_speed_is_zero():
    pts = [{"x": i, "y": 0, "t": i} for i in range(6)]
    r = timdr_change(pts)
    assert r["T"] == 0.0
    assert r["D"] == 0.0
    assert r["TIMDR"] < 0.05


def test_sharp_turn_raises_T():
    straight = [{"x": i, "y": 0, "t": i} for i in range(4)]
    turned = [{"x": 3, "y": i - 3, "t": i} for i in range(4, 7)]
    r = timdr_change(straight + turned)
    assert r["T"] > 0.3


def test_speed_burst_raises_D():
    steady = [{"x": i, "y": 0, "t": i} for i in range(5)]
    burst = [{"x": 4 + (i - 4) * 6, "y": 0, "t": i} for i in range(5, 8)]
    r = timdr_change(steady + burst)
    assert r["D"] > 0.2


def test_too_short_history_returns_zeros():
    r = timdr_change([{"x": 0, "y": 0, "t": 0}, {"x": 1, "y": 0, "t": 1}])
    assert r == {"T": 0.0, "D": 0.0, "R": 0.0, "TIMDR": 0.0}


def test_all_scores_bounded_0_1():
    import random
    random.seed(3)
    pts = [{"x": random.uniform(-10, 10), "y": random.uniform(-10, 10), "t": i} for i in range(15)]
    r = timdr_change(pts)
    for key in ("T", "D", "R", "TIMDR"):
        assert 0.0 <= r[key] <= 1.0
