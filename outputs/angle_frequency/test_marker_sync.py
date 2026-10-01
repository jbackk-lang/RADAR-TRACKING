import unittest
import numpy as np
from marker_sync import estimate_delay,calibrate_zero
from test_sync_calibration import clean_scan
from sync_calibration import read_angle

class TestMarker(unittest.TestCase):
    def test_marker_difference_and_sign(self):
        t=np.arange(8.)*.05
        self.assertAlmostEqual(estimate_delay(t+.002,t),.002,places=12)
        self.assertAlmostEqual(estimate_delay(t-.002,t),-.002,places=12)

    def test_single_speed_zero_calibration(self):
        refs=[clean_scan(1.) for _ in range(3)]
        cal=calibrate_zero(refs,[1.2]*3,.002)
        self.assertAlmostEqual(cal['zero_rad'],.003,places=8)
        self.assertAlmostEqual(read_angle(clean_scan(1.),cal['delay_s'],cal['zero_rad']),1.2,places=8)

    def test_bad_markers_rejected(self):
        for e,k in (([0,1],[0,1]),([0,2,1],[0,1,2]),([0,1,np.nan],[0,1,2])):
            with self.assertRaises(ValueError):
                estimate_delay(e,k)

if __name__=='__main__':
    unittest.main()
