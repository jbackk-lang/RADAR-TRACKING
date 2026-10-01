import unittest
import numpy as np
from stereo_model import CENTER,JointEstimator,simulate,templates

class TestStereo(unittest.TestCase):
    def test_signal_is_coherent_sum(self):
        angles=[CENTER-.01,CENTER+.01]
        actual=simulate(1,angles,[1.,-1.],noise=0)
        expected=templates(angles)[:,0]-templates(angles)[:,1]
        np.testing.assert_allclose(actual,expected,atol=1e-12)

    def test_single_target_not_split_without_noise(self):
        model=JointEstimator()
        self.assertEqual(model.fit(simulate(1,[CENTER],[1.],noise=0))['count'],1)

    def test_pair_recovered_without_noise(self):
        angles=[CENTER-np.deg2rad(1.5),CENTER+np.deg2rad(1.5)]
        out=JointEstimator().fit(simulate(1,angles,[1.,.5j],noise=0))
        self.assertEqual(out['count'],2)
        np.testing.assert_allclose(out['angles'],angles,atol=1e-12)

    def test_invalid_signal_rejected(self):
        with self.assertRaises(ValueError):
            JointEstimator().fit(np.zeros(3))

if __name__=='__main__':
    unittest.main()
