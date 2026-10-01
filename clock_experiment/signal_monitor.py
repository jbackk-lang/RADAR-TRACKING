"""Signal-only refit scheduler. Never rejects a positional observation."""
import numpy as np
from .adaptive import AdaptiveAmplitudeGate

class SignalClockMonitor(AdaptiveAmplitudeGate):
    def __init__(self, **kwargs):
        super().__init__(mode='adaptive',**kwargs)
        self.bad_count=0

    def step(self,t,amplitude):
        if not np.isfinite(t) or (self.last_time is not None and t<=self.last_time):
            raise ValueError('Time must increase')
        if amplitude is None or not np.isfinite(amplitude):
            raise ValueError('Finite amplitude required')
        self.last_time=float(t); self.count+=1
        baseline=float(np.mean([a for _,a in list(self.history)[-12:]])) if self.history else None
        forecast=baseline; used=False
        if self.model is not None and self.count-self.model['created']>2*self.window:
            self.model=None; self.state='learning'; self.good=0
        if self.model is not None:
            m=self.model
            forecast=float((self.basis([t],m['origin'],m['f0'],m['drift'],m['duration'])@m['coef'])[0])
            used=True
            bad=abs(amplitude-forecast)>m['threshold']
            self.bad_count=self.bad_count+1 if bad else 0
            self.good=0 if bad else self.good+1
            if self.bad_count>=3: self.state='active'
            elif self.good>=self.recovery: self.state='standard'
        self.history.append((float(t),float(amplitude)))
        due=len(self.history)>=self.warmup and (self.fit_calls==0 or self.count-self.last_fit>=self.cadence)
        if due and self.state!='standard': self._fit()
        return {'forecast':forecast,'baseline':baseline,'used_clock':used,'state':self.state,
                'keep_position':True,'fit_calls':self.fit_calls}
