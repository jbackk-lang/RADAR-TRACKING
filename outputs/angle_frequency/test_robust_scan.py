import unittest
import numpy as np
from stereo_model import CENTER,simulate
from robust_scan import RobustScanEstimator

class TestRobust(unittest.TestCase):
    def test_birth_and_disappearance_replace_memory(self):
        model=RobustScanEstimator(2)
        angles=[CENTER-np.deg2rad(.75),CENTER+np.deg2rad(.75)]
        first=model.observe(simulate(91,[angles[0]],[1.],2))
        pair=model.observe(simulate(92,angles,[1.,.7j],2))
        last=model.observe(simulate(93,[angles[0]],[1.],2))
        self.assertEqual((first['count'],pair['count'],last['count']),(1,2,1))
        self.assertFalse(last['memory_used'])

    def test_empty_scan_does_not_force_target(self):
        rng=np.random.default_rng(9876)
        y=.05*(rng.normal(size=242)+1j*rng.normal(size=242))
        out,_=RobustScanEstimator(2).fit_current(y)
        self.assertEqual(out['count'],0)

    def test_filter_weights_preserve_interchannel_phase(self):
        y=simulate(91,[CENTER],[1.],2)
        y[50:52]+=2+3j
        _,weights=RobustScanEstimator(2).fit_current(y)
        w=weights.reshape(-1,2)
        np.testing.assert_array_equal(w[:,0],w[:,1])
        original=y.reshape(-1,2)
        filtered=(y*np.sqrt(weights)).reshape(-1,2)
        np.testing.assert_allclose(np.angle(filtered[:,1]*np.conj(filtered[:,0])),
                                   np.angle(original[:,1]*np.conj(original[:,0])),atol=1e-12)
        self.assertTrue(np.any(weights<.5))

    def test_zero_and_invalid_signal(self):
        out,_=RobustScanEstimator(2).fit_current(np.zeros(242,complex))
        self.assertEqual(out['count'],0)
        with self.assertRaises(ValueError):
            RobustScanEstimator(2).fit_current(np.full(242,np.nan))

if __name__=='__main__':
    unittest.main()
