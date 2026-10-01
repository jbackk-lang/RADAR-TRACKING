import unittest
import numpy as np
from angle_model import C,D,estimate,simulate

class TestAngle(unittest.TestCase):
    def test_clean_angles_recovered(self):
        for theta in (-.6,-.2,0.,.2,.6):
            f,iq=simulate(1,theta,noise=0)
            for v in estimate(f,iq).values():
                self.assertAlmostEqual(v['angle_rad'],theta,places=10)

    def test_constant_phase_cancels_only_in_frequency_slope(self):
        f,iq=simulate(1,.3,phase_offset=.15,noise=0)
        out=estimate(f,iq)
        for method in ('slope_two','slope_all'):
            self.assertAlmostEqual(out[method]['angle_rad'],.3,places=10)
        self.assertGreater(abs(out['phase_all']['angle_rad']-.3),.01)

    def test_channel_delay_is_indistinguishable_from_angle(self):
        theta=.3; delay=.2e-12
        equivalent=float(np.arcsin(np.sin(theta)+C*delay/D))
        f,a=simulate(10,theta,phase_offset=.15,channel_delay=delay,noise=0)
        _,b=simulate(10,equivalent,phase_offset=.15,noise=0)
        np.testing.assert_allclose(a,b,atol=1e-12)
        self.assertAlmostEqual(estimate(f,a)['slope_all']['angle_rad'],equivalent,places=10)

    def test_common_phase_does_not_change_estimate(self):
        f,iq=simulate(1,.3,noise=0)
        rotated=iq*np.exp(1j*np.linspace(0,10,len(f)))[:,None,None]
        self.assertAlmostEqual(estimate(f,rotated)['slope_all']['angle_rad'],.3,places=10)

    def test_out_of_domain_is_invalid_not_clipped(self):
        f,iq=simulate(1,.6,channel_delay=10e-12,noise=0)
        self.assertIsNone(estimate(f,iq)['slope_all']['angle_rad'])

    def test_invalid_data(self):
        f,iq=simulate(1,.3)
        for bad_f,bad_iq in ((f[::-1],iq),(f,iq[:,0]),(f,np.zeros_like(iq))):
            with self.assertRaises(ValueError):
                estimate(bad_f,bad_iq)

if __name__=='__main__':
    unittest.main()
