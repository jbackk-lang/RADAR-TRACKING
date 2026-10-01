import unittest
import numpy as np
from rotation_model import OMEGA,estimate,simulate

class TestRotation(unittest.TestCase):
    def test_known_constant_rotation(self):
        theta=OMEGA*.2
        data=simulate(1,theta,noise=0,encoder_noise=0)
        for value in estimate(data).values():
            self.assertAlmostEqual(value,theta,places=9)

    def test_clock_offset_shifts_angle(self):
        theta=OMEGA*.2
        data=simulate(1,theta,clock_offset=.002,noise=0,encoder_noise=0)
        for value in estimate(data).values():
            self.assertAlmostEqual(value,theta+OMEGA*.002,places=9)

    def test_encoder_zero_bias_survives(self):
        theta=OMEGA*.2
        data=simulate(1,theta,noise=0,encoder_noise=0)
        data['encoder_angle']+=.01
        out=estimate(data)
        self.assertAlmostEqual(out['encoder_centroid'],theta+.01,places=9)
        self.assertAlmostEqual(out['nominal_time_peak'],theta,places=9)

    def test_missing_encoder_coverage_rejected(self):
        data=simulate(1,.4)
        data['encoder_time']+=1.
        with self.assertRaises(ValueError):
            estimate(data)

if __name__=='__main__':
    unittest.main()
