import unittest
from unittest.mock import patch
import numpy as np
from core.radar_tracker import RadarTracker
from clock_experiment.track_clock import TrackClockBank

class TestClockBank(unittest.TestCase):
    def tracker(self):
        return RadarTracker(d_max=.1,k_min=1,smoothing=1.)

    def step(self,tr,t):
        result=tr.update([{'x':.2*t-.01,'y':0.,'t':t},{'x':.2*t+.01,'y':0.,'t':t}])
        self.assertEqual(len(result),1)
        return next(iter(result))

    def test_geometric_output_unchanged_and_bounded(self):
        a=self.tracker(); b=self.tracker(); bank=TrackClockBank(a,max_samples=50)
        for i in range(55):
            tid=self.step(a,i*.1); self.step(b,i*.1)
            bank.observe(tid,i*.1,np.sin(i))
            np.testing.assert_equal(a.history[-1],b.history[-1])
        self.assertEqual(len(bank.samples[tid]),50)
        with patch('clock_experiment.track_clock.fit_clock',return_value=({'status':'unreliable'},None)):
            report,_=bank.analyze(tid,(.1,1),(-.01,.01))
        self.assertEqual(report['status'],'unreliable')
        self.assertFalse(report['used_for_trajectory'])

    def test_timestamps_and_missing_amplitude(self):
        tr=self.tracker(); bank=TrackClockBank(tr); tid=self.step(tr,1.)
        self.assertEqual(bank.analyze(tid,(.1,1),(-.01,.01))[0]['status'],'insufficient_data')
        for ident,t,a in [(99,1,2),(tid,2,2),(tid,1,float('nan'))]:
            with self.assertRaises(ValueError): bank.observe(ident,t,a)
        bank.observe(tid,1.,2.)
        with self.assertRaises(ValueError): bank.observe(tid,1.,3.)

    def test_stale_track_cleanup(self):
        tr=self.tracker(); bank=TrackClockBank(tr); tid=self.step(tr,0.)
        bank.observe(tid,0.,1.)
        tr.prune_stale(5.,1.)
        self.assertEqual(bank.prune(),[tid])
        with self.assertRaises(ValueError): bank.analyze(tid,(.1,1),(-.01,.01))

if __name__=='__main__': unittest.main()
