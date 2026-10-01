import unittest
from unittest.mock import patch
import numpy as np
from clock_experiment.adaptive import AdaptiveAmplitudeGate

class TestAdaptive(unittest.TestCase):
    def model(self,g):
        g.model={'origin':0.,'duration':10.,'f0':.5,'drift':0.,
                 'coef':np.zeros(6),'threshold':1.,'created':0}
        g.state='active'

    def test_switch_back_on_first_anomaly(self):
        g=AdaptiveAmplitudeGate(); self.model(g)
        for i in range(8): self.assertTrue(g.step(i,0.)['keep'])
        self.assertEqual(g.state,'standard')
        self.assertFalse(g.step(8,4.)['keep'])
        self.assertEqual(g.state,'active')

    def test_standard_never_fits_or_drops(self):
        g=AdaptiveAmplitudeGate('standard')
        with patch.object(g,'_fit',side_effect=AssertionError('fit')):
            for i in range(210): self.assertTrue(g.step(i,float(i%7))['keep'])

    def test_fit_cannot_change_current_decision(self):
        g=AdaptiveAmplitudeGate(warmup=50); self.model(g)
        # Avoid settling into standard by using persistent anomalies.
        for i in range(49): g.step(i,4.)
        with patch.object(g,'_fit',side_effect=lambda: setattr(g,'model',None)):
            self.assertFalse(g.step(49,4.)['keep'])

    def test_missing_resets_model_not_time_validation(self):
        g=AdaptiveAmplitudeGate(); self.model(g)
        self.assertTrue(g.step(10,None)['keep'])
        self.assertIsNone(g.model)
        with self.assertRaises(ValueError): g.step(9,1.)

if __name__=='__main__': unittest.main()
