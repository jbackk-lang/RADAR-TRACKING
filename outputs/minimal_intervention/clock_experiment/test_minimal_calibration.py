import unittest
from .minimal_calibration import MinimalCalibration
from .online_calibration import PARAMS

CAL = {'trigger_offset_s':0., 'bearing_bias':0., 'instrument_speed_equivalent_m_s':.8}
STRENGTHS = {k:.5 for k in PARAMS}

def raw(v):
    return {'range_m':1500., 'bearing_rad':.35, 'radial_velocity_m_s':v}

class TestMinimal(unittest.TestCase):
    def test_confirms_actual_partial_proposal(self):
        # Full .8 would harm a .3 error; partial .4 helps and must be evaluated.
        m = MinimalCalibration(CAL, STRENGTHS)
        selected,d = m.observe(0,raw(.3),True)
        self.assertEqual(d['states']['radial_velocity_m_s'],'confirmed')
        self.assertAlmostEqual(selected['instrument_speed_equivalent_m_s'],.4)

    def test_decay_uses_confirmation_age_and_expires(self):
        m = MinimalCalibration(CAL, STRENGTHS)
        m.observe(0,raw(.8),True)
        for t,expected in ((1,.2),(2,.1),(3,0.)):
            selected,d = m.observe(t,raw(0),False)
            self.assertAlmostEqual(selected['instrument_speed_equivalent_m_s'],expected)
            self.assertEqual(d['applied']['radial_velocity_m_s'],expected)
        self.assertEqual(d['states']['radial_velocity_m_s'],'waiting')

    def test_rejection_clears_and_good_reference_restores(self):
        m = MinimalCalibration(CAL, STRENGTHS)
        m.observe(0,raw(.8),True)
        selected,d = m.observe(1,raw(0),True)
        self.assertEqual(d['states']['radial_velocity_m_s'],'rejected')
        self.assertEqual(selected['instrument_speed_equivalent_m_s'],0.)
        selected,d = m.observe(2,raw(.8),False)
        self.assertEqual(selected['instrument_speed_equivalent_m_s'],0.)
        selected,d = m.observe(3,raw(.8),True)
        self.assertAlmostEqual(selected['instrument_speed_equivalent_m_s'],.4)

    def test_zero_strength_never_injects_a_correction(self):
        m = MinimalCalibration(CAL, {k:0. for k in PARAMS})
        for t,q in enumerate((True,False,True)):
            selected,d = m.observe(t,raw(.8),q)
            self.assertTrue(all(selected[p] == 0 for p,_,_ in PARAMS.values()))

    def test_invalid_strength_and_time(self):
        for bad in (-.1,1.1,float('nan')):
            with self.assertRaises(ValueError):
                MinimalCalibration(CAL,{**STRENGTHS,'range_m':bad})
        m = MinimalCalibration(CAL,STRENGTHS)
        m.observe(1,raw(.8),True)
        with self.assertRaises(ValueError):
            m.observe(1,raw(.8),False)

if __name__ == '__main__':
    unittest.main()
