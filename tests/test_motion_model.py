import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from core.motion_model import predict_covariance, mahalanobis_distance_sq, within_gate, CHI2_95_2DOF


def test_covariance_grows_with_dt():
    cov_short = predict_covariance(dt=1.0, timdr_score=0.0)
    cov_long = predict_covariance(dt=5.0, timdr_score=0.0)
    assert cov_long[0, 0] > cov_short[0, 0]


def test_covariance_grows_with_manoeuvring():
    cov_steady = predict_covariance(dt=2.0, timdr_score=0.0)
    cov_manoeuvring = predict_covariance(dt=2.0, timdr_score=1.0)
    assert cov_manoeuvring[0, 0] > cov_steady[0, 0]


def test_covariance_is_isotropic():
    cov = predict_covariance(dt=3.0, timdr_score=0.5)
    assert cov[0, 0] == cov[1, 1]
    assert cov[0, 1] == 0.0 and cov[1, 0] == 0.0


def test_mahalanobis_zero_at_mean():
    cov = predict_covariance(dt=1.0, timdr_score=0.0)
    assert mahalanobis_distance_sq((5, 5), (5, 5), cov) == 0.0


def test_mahalanobis_scales_with_covariance():
    point, mean = (3, 0), (0, 0)
    tight = predict_covariance(dt=1.0, timdr_score=0.0, sigma0=0.5)
    loose = predict_covariance(dt=1.0, timdr_score=0.0, sigma0=5.0)
    d_tight = mahalanobis_distance_sq(point, mean, tight)
    d_loose = mahalanobis_distance_sq(point, mean, loose)
    assert d_tight > d_loose  # same physical offset, "more standard deviations" under a tight covariance


def test_within_gate_true_for_close_point_false_for_far_point():
    cov = predict_covariance(dt=1.0, timdr_score=0.0, sigma0=1.0)
    assert within_gate((0.1, 0.1), (0, 0), cov) is True
    assert within_gate((50, 50), (0, 0), cov) is False


def test_gate_boundary_matches_chi2_threshold():
    cov = np.eye(2)  # unit covariance -> Mahalanobis^2 == Euclidean^2
    r = CHI2_95_2DOF ** 0.5
    just_inside = (r - 1e-6, 0)
    just_outside = (r + 1e-6, 0)
    assert within_gate(just_inside, (0, 0), cov) is True
    assert within_gate(just_outside, (0, 0), cov) is False
