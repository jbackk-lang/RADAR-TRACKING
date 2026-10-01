import unittest
import numpy as np
from .soft_fusion import fuse_position

class TestSoftFusion(unittest.TestCase):
    def test_amplitude_alone_does_not_reject_position(self):
        p,w=fuse_position([.02,.03],[0,0],True)
        np.testing.assert_array_equal(p,[.02,.03]); self.assertEqual(w,1)

    def test_no_amplitude_warning_matches_geometry(self):
        a,w=fuse_position([1,0],[0,0],False,'hybrid')
        b,v=fuse_position([1,0],[0,0],False,'geometry')
        np.testing.assert_array_equal(a,b); self.assertEqual(w,v)

    def test_joint_warning_reduces_but_does_not_remove_measurement(self):
        _,a=fuse_position([1,0],[0,0],True,'hybrid')
        _,b=fuse_position([1,0],[0,0],True,'geometry')
        self.assertGreater(a,0); self.assertLess(a,b)

    def test_bad_input(self):
        with self.assertRaises(ValueError): fuse_position([np.nan,0],[0,0])

if __name__=='__main__': unittest.main()
