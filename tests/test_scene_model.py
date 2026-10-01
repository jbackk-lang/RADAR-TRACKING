import numpy as np
import unittest
from unittest.mock import patch
from core import scene_model
from core.scene_demo import run_scene_demo


def test_switch_uses_real_timdr_only_in_timdr_mode():
    calls = []
    original = scene_model.timdr_change
    def record(history):
        calls.append(history)
        return original(history)
    with patch.object(scene_model, 'timdr_change', record):
        cv = run_scene_demo('cv', 'diverging')
        assert calls == [] and cv['count'] == 2
        timdr = run_scene_demo('timdr', 'diverging')
    assert len(calls) == timdr['timdr_calls'] == 20
    assert timdr['count'] == 2
    # Association at t=1 uses history ending at t=.5, never current/future data.
    assert calls[0][-1]['t'] == .5


def test_coherent_group_does_not_claim_one_object():
    for model in ('cv', 'timdr'):
        for scenario in ('parallel', 'rotating'):
            result = run_scene_demo(model, scenario)
            assert result['label'] == 'coherent_group_unresolved'
            assert result['count'] is None
            assert abs(result['observed_extent_m'] - 4) < .5


def test_invalid_times_rejected():
    for times in ([0, 1, 1], [0, 1, np.nan]):
        with unittest.TestCase().assertRaises(ValueError):
            scene_model.recognize_scene(np.zeros((3, 2, 2)), np.zeros((3, 2)), times)


def load_tests(loader, tests, pattern):
    for test in (test_switch_uses_real_timdr_only_in_timdr_mode,
                 test_coherent_group_does_not_claim_one_object, test_invalid_times_rejected):
        tests.addTest(unittest.FunctionTestCase(test))
    return tests
