import numpy as np
from core.radar_tracker import RadarTracker
from web_demo import build_demo


def test_models_get_identical_measurements_and_cv_disables_adaptation():
    cv = build_demo('cv', 'mixed', 4)
    timdr = build_demo('timdr', 'mixed', 4)
    assert [f['points'] for f in cv['frames']] == [f['points'] for f in timdr['frames']]
    assert all(tr['score'] == 0 for f in cv['frames'] for tr in f['tracks'])
    assert any(tr['score'] > 0 for f in timdr['frames'] for tr in f['tracks'])


def test_existing_tracker_default_remains_timdr():
    assert RadarTracker().use_timdr is True


def test_robust_option_runs_real_operator_on_same_inputs():
    legacy = build_demo('timdr', 'turning', 4)
    robust = build_demo('robust', 'turning', 4)
    assert robust['model'] == 'robust'
    assert [f['points'] for f in legacy['frames']] == [f['points'] for f in robust['frames']]
    assert any(tr['score'] > 0 for f in robust['frames'] for tr in f['tracks'])


def test_more_objects_generate_more_echoes():
    demo = build_demo('timdr', 'formation', 12)
    assert len(demo['frames']) == 40
    assert all(len(f['points']) == 36 for f in demo['frames'])
    assert all(len(f['truth']) == 12 for f in demo['frames'])


def test_invalid_selections_rejected():
    for args in [('bad', 'mixed', 4), ('cv', 'unknown', 4), ('cv', 'mixed', 1000)]:
        try:
            build_demo(*args)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid demo selection accepted')
