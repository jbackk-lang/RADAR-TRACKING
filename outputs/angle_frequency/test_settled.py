import unittest
import numpy as np
from run_settled import motion
from sync_calibration import simulate,calibrate

class TestSettled(unittest.TestCase):
    def test_smooth_ramp_reduces_excitation(self):
        _,_,step=motion(1.,12.,False)
        _,_,gentle=motion(1.,12.,True)
        self.assertLess(abs(gentle).max(),.1*abs(step).max())

    def test_waiting_reduces_observation_vibration(self):
        t,_,q=motion(1.,12.,True)
        self.assertLess(abs(q[t>=3.]).max(),np.deg2rad(.001))

    def test_same_speed_refused_without_resonance(self):
        # This generator contains no mechanical resonance at all.
        refs=[simulate(s,1.2,1.,.002,.003) for s in (1,2,3)]
        with self.assertRaisesRegex(ValueError,'not identifiable'):
            calibrate(refs,[1.2]*3)

if __name__=='__main__':
    unittest.main()
