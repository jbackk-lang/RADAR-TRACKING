"""Four-state causal calibration memory, with optional proposed EMA updates."""
import numpy as np
from .radar_compensation import C

PARAMS={'range_m':('trigger_offset_s',2/C,3.75),'bearing_rad':('bearing_bias',1.,.004),
        'radial_velocity_m_s':('instrument_speed_equivalent_m_s',1.,.05)}

class OnlineCalibration:
    def __init__(self, initial, adapt=True, ttl=2.):
        if not np.isfinite(ttl) or ttl<0: raise ValueError('Nonnegative TTL required')
        self.candidate=dict(initial); self.adapt=adapt; self.ttl=ttl
        self.confirmed={}; self.last_time=None

    def observe(self,time,raw,quality,known_range=1500.,known_bearing=.35):
        if not np.isfinite(time) or (self.last_time is not None and time<=self.last_time):
            raise ValueError('Observation time must increase')
        if not np.isfinite([raw[k] for k in PARAMS]+[known_range,known_bearing]).all():
            raise ValueError('Finite reference values required')
        self.last_time=time
        truth={'range_m':known_range,'bearing_rad':known_bearing,'radial_velocity_m_s':0.}
        selected=dict(self.candidate); states={}; applied={}; proposed_before=dict(self.candidate)
        for key,(parameter,scale,margin) in PARAMS.items():
            observed_error=raw[key]-truth[key]
            if key=='bearing_rad': observed_error=float(np.angle(np.exp(1j*observed_error)))
            residual=observed_error-self.candidate[parameter]/scale
            if key=='bearing_rad': residual=float(np.angle(np.exp(1j*residual)))
            gain=abs(observed_error)-abs(residual)
            if quality and gain>margin:
                self.confirmed[key]=(self.candidate[parameter],time)
                states[key]='confirmed'
            elif quality and gain < -margin:
                self.confirmed.pop(key,None); states[key]='rejected'
            else:
                previous=self.confirmed.get(key)
                states[key]='uncertain' if previous is not None and time-previous[1]<=self.ttl else 'waiting'
            previous=self.confirmed.get(key)
            value=previous[0] if states[key] in ('confirmed','uncertain') else 0.
            selected[parameter]=value; applied[key]=value
            # Update a proposal for the NEXT observation only.
            if quality and self.adapt:
                target=observed_error*scale
                if key=='bearing_rad':
                    delta=float(np.angle(np.exp(1j*(target-self.candidate[parameter]))))
                    self.candidate[parameter]+= .5*delta
                else: self.candidate[parameter]=.5*self.candidate[parameter]+.5*target
        return selected,{'states':states,'candidate_before':proposed_before,
                         'candidate_next':dict(self.candidate),'applied':applied,
                         'additional_observations':0}
