import unittest
import numpy as np
from .signal_monitor import SignalClockMonitor

class TestSignalMonitor(unittest.TestCase):
    def make(self):
        m=SignalClockMonitor()
        m.model={'origin':0.,'duration':10.,'f0':.5,'drift':0.,'coef':np.array([1.,0,0,0,0,0]),
                 'threshold':.2,'created':0}
        m.state='standard'
        return m

    def test_current_amplitude_cannot_change_current_forecast(self):
        a=self.make().step(0,1.)
        b=self.make().step(0,100.)
        self.assertEqual(a['forecast'],b['forecast'])
        self.assertTrue(b['keep_position'])

    def test_three_errors_then_recovery(self):
        m=self.make()
        for t in range(2): self.assertEqual(m.step(t,5.)['state'],'standard')
        self.assertEqual(m.step(2,5.)['state'],'active')
        for t in range(3,11): m.step(t,1.)
        self.assertEqual(m.state,'standard')

    def test_forecast_fallback_only_uses_past(self):
        m=SignalClockMonitor()
        self.assertIsNone(m.step(0,2.)['forecast'])
        self.assertEqual(m.step(1,200.)['forecast'],2.)
        with self.assertRaises(ValueError): m.step(1,1.)

if __name__=='__main__': unittest.main()
