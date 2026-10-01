"""Validate each frozen correction on a separate stationary reference."""
import numpy as np
from .radar_compensation import estimate
from .reference_calibration import apply_calibration

class CalibrationGuard:
    def __init__(self, calibration):
        self.calibration=dict(calibration)
        self.streak={k:0 for k in ('range_m','bearing_rad','radial_velocity_m_s')}

    def validate(self,iq,acquisition,known_range,known_bearing):
        if not np.isfinite([known_range,known_bearing]).all() or known_range<=0:
            raise ValueError('Known stationary validator required')
        raw=estimate(iq,**acquisition); corrected=apply_calibration(iq,acquisition,self.calibration)
        power=np.mean(abs(iq)**2,axis=0); k=int(np.argmax(power)); z=iq[:,k]
        ratio=float(power[k]/max(float(np.median(power)),1e-300))
        coherence=float(abs(np.sum(z[1:]*np.conj(z[:-1])))/max(float(np.sqrt(np.sum(abs(z[1:])**2)*np.sum(abs(z[:-1])**2))),1e-300))
        quality=ratio>=10 and coherence>=.8
        truth={'range_m':known_range,'bearing_rad':known_bearing,'radial_velocity_m_s':0.}
        margins={'range_m':3.75,'bearing_rad':.004,'radial_velocity_m_s':.05}
        enabled={}
        for key in truth:
            a=raw[key]-truth[key]; b=corrected[key]-truth[key]
            if key=='bearing_rad': a=np.angle(np.exp(1j*a)); b=np.angle(np.exp(1j*b))
            good=quality and abs(a)-abs(b)>margins[key]
            self.streak[key]=self.streak[key]+1 if good else 0
            enabled[key]=self.streak[key]>=2
        selected=dict(self.calibration)
        for measurement,parameter in [('range_m','trigger_offset_s'),('bearing_rad','bearing_bias'),('radial_velocity_m_s','instrument_speed_equivalent_m_s')]:
            if not enabled[measurement]: selected[parameter]=0.
        return selected,{'quality_ok':bool(quality),'power_ratio':ratio,'coherence':coherence,
                         'enabled':enabled,'raw':raw,'corrected':corrected}
