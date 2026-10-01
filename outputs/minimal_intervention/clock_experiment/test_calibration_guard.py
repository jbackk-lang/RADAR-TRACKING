import unittest
from .radar_compensation import simulate
from .reference_calibration import calibrate
from .calibration_guard import CalibrationGuard

class TestGuard(unittest.TestCase):
    def make(self):
        x,p,_=simulate(0,range_m=900,bearing=-.2,noise=0)
        return CalibrationGuard(calibrate(x,p,900,-.2))
    def test_two_confirmations_and_immediate_disable(self):
        guard=self.make(); x,p,_=simulate(1,range_m=1500,bearing=.35,noise=0)
        _,a=guard.validate(x,p,1500,.35); self.assertFalse(any(a['enabled'].values()))
        _,a=guard.validate(x,p,1500,.35); self.assertTrue(all(a['enabled'].values()))
        x,p,_=simulate(2,range_m=1500,bearing=.35,trigger_samples=0,bearing_bias=0,instrument_speed=0,noise=0)
        c,a=guard.validate(x,p,1500,.35)
        self.assertFalse(any(a['enabled'].values())); self.assertEqual(c['instrument_speed_equivalent_m_s'],0)
    def test_bad_reference_quality_disables(self):
        guard=self.make(); x,p,_=simulate(1,range_m=1500,bearing=.35,noise=3)
        for _ in range(3): c,a=guard.validate(x,p,1500,.35)
        self.assertFalse(a['quality_ok']); self.assertFalse(any(a['enabled'].values()))

if __name__=='__main__': unittest.main()
