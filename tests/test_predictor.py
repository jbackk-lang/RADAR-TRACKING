import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.predictor import predict_next


def test_predicts_along_constant_velocity():
    hist = [{"x": 0, "y": 0, "t": 0}, {"x": 1, "y": 0, "t": 1}]
    pred = predict_next(hist, direction=(1.0, 0.0), change={"TIMDR": 0.0}, dt=1.0)
    assert abs(pred["x"] - 2.0) < 1e-9
    assert abs(pred["y"]) < 1e-9
    assert pred["t"] == 2.0


def test_high_timdr_damps_the_step():
    hist = [{"x": 0, "y": 0, "t": 0}, {"x": 1, "y": 0, "t": 1}]
    calm = predict_next(hist, direction=(1.0, 0.0), change={"TIMDR": 0.0}, dt=1.0)
    excited = predict_next(hist, direction=(1.0, 0.0), change={"TIMDR": 1.0}, dt=1.0)
    calm_step = calm["x"] - hist[-1]["x"]
    excited_step = excited["x"] - hist[-1]["x"]
    assert excited_step < calm_step
    assert excited_step > 0  # damping floor keeps some momentum


def test_no_direction_means_no_step():
    hist = [{"x": 5, "y": 5, "t": 0}, {"x": 5, "y": 5, "t": 1}]
    pred = predict_next(hist, direction=None, change={"TIMDR": 0.0}, dt=1.0)
    assert pred["x"] == 5
    assert pred["y"] == 5


def test_single_point_history_zero_speed():
    hist = [{"x": 3, "y": 3, "t": 0}]
    pred = predict_next(hist, direction=(1.0, 0.0), change={"TIMDR": 0.0}, dt=1.0)
    assert pred["x"] == 3
    assert pred["y"] == 3
