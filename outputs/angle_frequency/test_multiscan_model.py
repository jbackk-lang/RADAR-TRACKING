import copy
import json
import unittest
import numpy as np
from multiscan_model import MultiScanEstimator
from stereo_model import CENTER,simulate
from run_angle import ROOT,digest

class TestMultiScan(unittest.TestCase):
    def test_training_does_not_include_confirmation(self):
        model=MultiScanEstimator(2)
        angles=[CENTER-np.deg2rad(1.5),CENTER+np.deg2rad(1.5)]
        train=[simulate(s,angles,[1.,.5j],2) for s in (1,2,3)]
        proposal=model.propose(train)
        saved=copy.deepcopy(proposal)
        out=model.confirm(proposal,simulate(4,angles,[.8j,.6],2))
        self.assertEqual(out['count'],2)
        self.assertEqual(proposal,saved)

    def test_bad_confirmation_is_uncertain(self):
        model=MultiScanEstimator(2)
        train=[simulate(s,[CENTER],[1.],2) for s in (1,2,3)]
        proposal=model.propose(train)
        out=model.confirm(proposal,simulate(4,[CENTER+.06],[1.],2))
        self.assertEqual(out['state'],'uncertain')
        self.assertEqual(out['angles'],[])

    def test_invalid_training(self):
        with self.assertRaises(ValueError):
            MultiScanEstimator(2).propose(np.zeros((1,242)))

    def test_saved_decisions_replay(self):
        r=json.loads((ROOT/'multiscan_results.json').read_text(encoding='utf-8'))
        for name,expected in r['hashes'].items():
            self.assertEqual(digest(ROOT/name),expected)
        self.assertEqual(digest(ROOT/'multiscan_iq.npz'),r['iq_sha256'])
        model=MultiScanEstimator(2)
        with np.load(ROOT/'multiscan_iq.npz',allow_pickle=False) as data:
            for row in r['runs']:
                scans=data[row['iq_key']]
                proposal=model.propose(scans[:3])
                self.assertEqual(proposal,row['proposal'])
                self.assertEqual(model.confirm(proposal,scans[3]),row['multi'])

if __name__=='__main__':
    unittest.main()
