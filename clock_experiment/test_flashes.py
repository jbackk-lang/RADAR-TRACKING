import unittest
import numpy as np
from .flashes import detect

class TestFlashes(unittest.TestCase):
    def test_flat(self):
        self.assertEqual(detect(np.ones((30,32)),np.arange(30),np.arange(30),np.arange(32))[0],[])
    def test_injected(self):
        p=np.ones((30,32)); p[15,12:15]=30
        events,_,_=detect(p,np.arange(30)*.05,np.arange(30),np.arange(32))
        self.assertEqual(len(events),1); self.assertEqual(events[0]['time_s'],.75)
    def test_gap(self):
        p=np.ones((30,32)); p[14:16,12:15]=30
        frames=np.r_[np.arange(15),np.arange(100,115)]
        events,_,_=detect(p,frames*.05,frames,np.arange(32))
        self.assertEqual(len(events),2)

if __name__=='__main__': unittest.main()
