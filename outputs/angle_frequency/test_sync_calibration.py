import unittest
import numpy as np
from angle_model import C
from sync_calibration import calibrate,read_angle

def clean_scan(turns,delay=.002,zero=.003):
    t=np.arange(0,1.,.0002); angle=2*np.pi*turns*t
    iq=np.exp(-2*np.log(2)*((angle-1.2)/np.deg2rad(1.5))**2).astype(complex)
    return dict(echo_time=t+2*1500/C+delay,iq=iq,encoder_time=t,encoder_angle=angle+zero,
                measured_range_m=1500.,nominal_omega=2*np.pi*turns)

class TestSync(unittest.TestCase):
    def test_separate_delay_and_zero(self):
        refs=[clean_scan(s) for s in (.5,1.,1.5)]
        cal=calibrate(refs,[1.2]*3)
        self.assertAlmostEqual(cal['delay_s'],.002,places=8)
        self.assertAlmostEqual(cal['zero_rad'],.003,places=8)

    def test_correction_applied_before_angle_interpolation(self):
        refs=[clean_scan(s) for s in (.5,1.,1.5)]
        cal=calibrate(refs,[1.2]*3)
        data=clean_scan(1.25)
        self.assertAlmostEqual(read_angle(data,cal['delay_s'],cal['zero_rad']),1.2,places=8)

    def test_same_speed_not_identifiable(self):
        with self.assertRaises(ValueError):
            calibrate([clean_scan(1.) for _ in range(3)],[1.2]*3)

    def test_wrong_reference_zero_bias_is_not_detectable(self):
        refs=[clean_scan(s) for s in (.5,1.,1.5)]
        cal=calibrate(refs,[1.21]*3)
        self.assertAlmostEqual(cal['delay_s'],.002,places=8)
        self.assertAlmostEqual(read_angle(clean_scan(1.25),cal['delay_s'],cal['zero_rad']),1.21,places=8)

if __name__=='__main__':
    unittest.main()
