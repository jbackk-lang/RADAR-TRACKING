import unittest
from .online_calibration import OnlineCalibration

CAL={'trigger_offset_s':0.,'bearing_bias':0.,'instrument_speed_equivalent_m_s':.7}
def raw(v): return {'range_m':1500.,'bearing_rad':.35,'radial_velocity_m_s':v}

class TestOnline(unittest.TestCase):
    def test_memory_expires_without_refresh(self):
        m=OnlineCalibration(CAL,adapt=False)
        m.observe(0,raw(.7),True)
        for t in (1,2):
            c,d=m.observe(t,raw(9),False); self.assertEqual(c['instrument_speed_equivalent_m_s'],.7)
            self.assertEqual(d['states']['radial_velocity_m_s'],'uncertain')
        c,d=m.observe(3,raw(9),False)
        self.assertEqual(c['instrument_speed_equivalent_m_s'],0)
        self.assertEqual(d['states']['radial_velocity_m_s'],'waiting')
    def test_harm_overrides_memory(self):
        m=OnlineCalibration(CAL); m.observe(0,raw(.7),True)
        c,d=m.observe(1,raw(0),True)
        self.assertEqual(c['instrument_speed_equivalent_m_s'],0)
        self.assertEqual(d['states']['radial_velocity_m_s'],'rejected')
    def test_no_self_confirmation(self):
        m=OnlineCalibration({**CAL,'instrument_speed_equivalent_m_s':0})
        c,d=m.observe(0,raw(1),True)
        self.assertEqual(c['instrument_speed_equivalent_m_s'],0)
        self.assertEqual(d['candidate_next']['instrument_speed_equivalent_m_s'],.5)
        c,d=m.observe(1,raw(1),True)
        self.assertEqual(c['instrument_speed_equivalent_m_s'],.5)

if __name__=='__main__': unittest.main()
