import numpy as np
from core.timdr_robust import timdr_change_robust
from core.radar_tracker import RadarTracker


def history(times, xy):
    return [dict(x=float(p[0]), y=float(p[1]), t=float(t)) for p, t in zip(xy, times)]


def test_straight_outlier_does_not_create_manoeuvre():
    t = np.arange(0, 5.01, .5)
    xy = np.column_stack([3*t, np.zeros(len(t))])
    xy[5] += [3, -3]
    result = timdr_change_robust(history(t, xy), .12)
    assert result['TIMDR'] < .5


def test_turn_rate_stable_across_sampling():
    values = []
    for dt in (.25, .5, 1.):
        t = np.arange(0, 5.01, dt)
        xy = np.column_stack([6*np.sin(.5*t), 6*(1-np.cos(.5*t))])
        values.append(timdr_change_robust(history(t, xy), .12)['TIMDR'])
    assert max(values)-min(values) < .05
    assert min(values) > .5


def test_acceleration_and_reversal_detected():
    t = np.arange(0, 5.01, .5)
    for x in (3*t+.7*t*t, 3*np.where(t<=2.5,t,5-t)):
        assert timdr_change_robust(history(t, np.column_stack([x, np.zeros(len(t))])), .12)['TIMDR'] > .5


def test_invalid_time_and_noise_rejected():
    t = np.array([0., 1., 1., 2., 3.])
    h = history(t, np.zeros((5, 2)))
    for sigma in (.12, 0., float('nan')):
        try:
            timdr_change_robust(h, sigma)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid time or noise accepted')


def test_short_history_is_explicitly_insufficient():
    result = timdr_change_robust([dict(x=0., y=0., t=0.)])
    assert result['TIMDR'] == 0 and result['confidence'] == 0 and result['model'] == 'insufficient'


def test_tracker_robust_switch_and_default_compatibility():
    assert RadarTracker().timdr_variant == 'legacy'
    tracker = RadarTracker(timdr_variant='robust', position_sigma=.12)
    t = np.arange(0, 5.01, .5)
    xy = np.column_stack([6*np.sin(.5*t), 6*(1-np.cos(.5*t))])
    assert tracker._change(history(t, xy))['model'] == 'quadratic'
    assert tracker._change(history(t, xy))['TIMDR'] > .5
