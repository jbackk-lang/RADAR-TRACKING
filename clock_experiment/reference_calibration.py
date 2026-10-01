"""Estimate frozen offsets from a separate, known stationary reflector."""
import numpy as np
from .radar_compensation import estimate,C

def calibrate(iq, acquisition, known_range_m, known_bearing_rad):
    if not np.isfinite([known_range_m,known_bearing_rad]).all() or known_range_m<=0:
        raise ValueError('Finite known reference geometry required')
    measured=estimate(iq,**acquisition)
    return {'trigger_offset_s':2*(measured['range_m']-known_range_m)/C,
            'bearing_bias':float(np.angle(np.exp(1j*(measured['bearing_rad']-known_bearing_rad)))),
            'instrument_speed_equivalent_m_s':measured['radial_velocity_m_s'],
            'assumption':'Known stationary reference; linear instrumental phase drift'}

def apply_calibration(iq, acquisition, calibration):
    t=np.arange(len(iq))/acquisition['prf']
    phase=4*np.pi*calibration['instrument_speed_equivalent_m_s']*t/(C/acquisition['carrier'])
    return estimate(iq,**acquisition,trigger_offset_s=calibration['trigger_offset_s'],
                    bearing_bias=calibration['bearing_bias'],instrument_phase=phase)
