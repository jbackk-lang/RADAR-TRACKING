import unittest
import numpy as np
from carrier_phase import WAVELENGTH,PRF,TIMES,estimate

class TestCarrier(unittest.TestCase):
    def test_velocity_without_noise(self):
        envelope=np.exp(-.5*((np.arange(512)-160)/1.5)**2)
        for v in (.04,1.,-1.):
            iq=envelope[None,:]*np.exp(1j*4*np.pi*v*TIMES[:,None]/WAVELENGTH)
            out,_=estimate(iq)
            self.assertAlmostEqual(out['baseline_v'],v,places=10)
            self.assertLess(abs(out['carrier_v']-v),1e-4)

    def test_unknown_constant_phase_does_not_change_velocity(self):
        envelope=np.exp(-.5*((np.arange(512)-160)/1.5)**2)
        iq=envelope[None,:]*np.exp(1j*4*np.pi*.04*TIMES[:,None]/WAVELENGTH)
        a,_=estimate(iq); b,_=estimate(iq*np.exp(1.7j))
        self.assertAlmostEqual(a['carrier_v'],b['carrier_v'],places=10)
        self.assertEqual(a['range_m'],b['range_m'])

    def test_invalid_data(self):
        with self.assertRaises(ValueError):
            estimate(np.full((64,512),np.nan))

if __name__=='__main__':
    unittest.main()
