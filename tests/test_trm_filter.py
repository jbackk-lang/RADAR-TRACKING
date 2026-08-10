import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.trm_filter import trm_filter, cluster_centroids


def test_isolated_point_is_dropped():
    points = [
        {"x": 0, "y": 0, "t": 0},
        {"x": 0.5, "y": 0.5, "t": 0},   # has a neighbour -> kept
        {"x": 50, "y": 50, "t": 0},     # isolated -> dropped
    ]
    kept = trm_filter(points, d_max=2.0, dt_max=1.0, k_min=1)
    assert len(kept) == 2
    assert all(p["x"] != 50 for p in kept)


def test_temporal_window_matters():
    points = [
        {"x": 0, "y": 0, "t": 0},
        {"x": 0.1, "y": 0.1, "t": 10},  # spatially close, temporally far
    ]
    kept = trm_filter(points, d_max=2.0, dt_max=1.0, k_min=1)
    assert len(kept) == 0  # neither has a neighbour within dt_max


def test_empty_input():
    assert trm_filter([], d_max=1.0, dt_max=1.0, k_min=1) == []


def test_k_min_threshold():
    # a pair of points only satisfies k_min=1, not k_min=2
    points = [{"x": 0, "y": 0, "t": 0}, {"x": 0.5, "y": 0, "t": 0}]
    assert len(trm_filter(points, d_max=2.0, dt_max=1.0, k_min=1)) == 2
    assert len(trm_filter(points, d_max=2.0, dt_max=1.0, k_min=2)) == 0


def test_cluster_centroids_merges_close_points():
    points = [
        {"x": 0.0, "y": 0.0, "t": 0}, {"x": 0.2, "y": -0.1, "t": 0},   # cluster A
        {"x": 10.0, "y": 10.0, "t": 0}, {"x": 10.1, "y": 9.9, "t": 0}, # cluster B
    ]
    centroids = cluster_centroids(points, d_max=1.0)
    assert len(centroids) == 2


def test_cluster_centroids_empty():
    assert cluster_centroids([], d_max=1.0) == []
