import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.gia_direction import gia_direction, gia_stability


def test_direction_on_straight_line():
    pts = [{"x": i, "y": 0, "t": i} for i in range(5)]
    v = gia_direction(pts)
    assert v is not None
    assert abs(v[0] - 1.0) < 1e-9
    assert abs(v[1]) < 1e-9


def test_direction_orientation_follows_time():
    # line goes from (0,0) to (-5,0): direction should point negative-x
    pts = [{"x": -i, "y": 0, "t": i} for i in range(5)]
    v = gia_direction(pts)
    assert v[0] < 0


def test_direction_none_for_single_point():
    assert gia_direction([{"x": 0, "y": 0, "t": 0}]) is None


def test_direction_none_for_coincident_points():
    pts = [{"x": 1, "y": 1, "t": i} for i in range(4)]
    assert gia_direction(pts) is None


def test_stability_perfect_line_is_one():
    pts = [{"x": i, "y": 2 * i, "t": i} for i in range(6)]
    assert abs(gia_stability(pts) - 1.0) < 1e-9


def test_stability_isotropic_cloud_is_low():
    import random
    random.seed(0)
    # symmetric 4-point cross has no dominant axis -> stability = 0.5
    pts = [{"x": 1, "y": 0}, {"x": -1, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": -1}]
    s = gia_stability(pts)
    assert abs(s - 0.5) < 1e-9
