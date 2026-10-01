import unittest
import numpy as np

from .event_mode import fit_mode,score_mode

class TestMode(unittest.TestCase):
    def test_phase_transfers(self):
        grid=np.array([.7,1.,1.3])
        f,p,r=fit_mode(np.arange(10)+.2,grid)
        self.assertEqual(f,1.)
        self.assertAlmostEqual(score_mode(np.arange(10,20)+.2,f,p),1.)
    def test_opposite_phase_fails(self):
        self.assertAlmostEqual(score_mode(np.arange(10)+.5,1.,0.),-1.)

if __name__=='__main__': unittest.main()
