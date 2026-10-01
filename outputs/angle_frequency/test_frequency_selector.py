import unittest
import numpy as np
from frequency_selector import CENTER,FrequencySelector,template

class TestSelector(unittest.TestCase):
    def test_strong_template_is_removed(self):
        y=template(CENTER,0.)[:,0]
        out=FrequencySelector().scores(y)
        self.assertLess(out['coherent']['score'],1e-20)
        self.assertLess(out['band_power']['score'],1e-20)

    def test_global_phase_does_not_change_scores(self):
        y=template(CENTER,0.)[:,0]+.15j*template(CENTER+np.deg2rad(1.5),.06)[:,0]
        model=FrequencySelector()
        first=model.scores(y); second=model.scores(y*np.exp(.7j))
        for method in first:
            self.assertAlmostEqual(first[method]['score'],second[method]['score'],places=10)

    def test_weak_delayed_target_localized_without_noise(self):
        angle=CENTER+np.deg2rad(1.5)
        y=template(CENTER,0.)[:,0]+.15j*template(angle,.06)[:,0]
        out=FrequencySelector().scores(y)['coherent']
        self.assertLess(abs(np.rad2deg(out['angle']-angle)),.25)
        self.assertLess(abs(out['dr']-.06),.015)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            FrequencySelector().scores(np.full(738,np.nan))

if __name__=='__main__':
    unittest.main()
