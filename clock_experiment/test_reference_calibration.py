import unittest
from .radar_compensation import simulate
from .reference_calibration import calibrate,apply_calibration

class TestReferenceCalibration(unittest.TestCase):
    def test_separate_moving_target_preserves_motion(self):
        iq,p,_=simulate(0,range_m=900,bearing=-.2,noise=0)
        cal=calibrate(iq,p,900,-.2)
        test,q,_=simulate(1,range_m=1800,bearing=.6,speed=2,noise=0)
        result=apply_calibration(test,q,cal)
        self.assertAlmostEqual(result['radial_velocity_m_s'],2,places=10)
        self.assertLess(abs(result['range_m']-1800),7.5)
        self.assertAlmostEqual(result['bearing_rad'],.6)
    def test_moving_reference_is_not_instrument_calibration(self):
        iq,p,_=simulate(0,range_m=900,bearing=-.2,speed=1,noise=0)
        cal=calibrate(iq,p,900,-.2)
        test,q,_=simulate(1,speed=2,noise=0)
        self.assertAlmostEqual(apply_calibration(test,q,cal)['radial_velocity_m_s'],1,places=10)
    def test_invalid_reference(self):
        iq,p,_=simulate(0)
        with self.assertRaises(ValueError): calibrate(iq,p,-1,0)

if __name__=='__main__': unittest.main()
