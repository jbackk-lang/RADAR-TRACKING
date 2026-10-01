import unittest
import numpy as np
from .radar_compensation import estimate,simulate

class TestCompensation(unittest.TestCase):
    def test_stationary_and_moving(self):
        for speed in (0.,2.):
            iq,params,cal=simulate(1,speed=speed,noise=0.)
            result=estimate(iq,**params,**cal)
            self.assertAlmostEqual(result['radial_velocity_m_s'],speed,places=10)
            self.assertAlmostEqual(result['bearing_rad'],.1)
            self.assertLess(abs(result['range_m']-1200),4.)
    def test_zero_calibration_is_identity(self):
        iq,p,c=simulate(2,trigger_samples=0,bearing_bias=0,instrument_speed=0)
        self.assertEqual(estimate(iq,**p),estimate(iq,**p,**c))
    def test_wrong_phase_sign(self):
        iq,p,c=simulate(3,noise=0.)
        c['instrument_phase']=-c['instrument_phase']
        self.assertAlmostEqual(estimate(iq,**p,**c)['radial_velocity_m_s'],1.4)
    def test_empty_signal_rejected(self):
        with self.assertRaises(ValueError): estimate(np.zeros((4,4)),1,1,1,0)

if __name__=='__main__': unittest.main()
