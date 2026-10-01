"""Causal amplitude quality gate before RadarTracker.update.

Single, externally associated amplitude stream. An amplitude anomaly is NOT
proof of a positional error: use only after validating that relation for the
sensor. No multi-target amplitude association is performed here.
"""
from collections import deque
import time
import numpy as np
from .astronomy_clock import fit_clock

class AdaptiveAmplitudeGate:
    def __init__(self, mode='adaptive', window=200, warmup=100, cadence=80,
                 recovery=8, f_bounds=(.3,1.2), drift_bounds=(-.015,.025)):
        if mode not in ('standard','always','adaptive'):
            raise ValueError('Unknown mode')
        if not 50 <= warmup <= window or cadence<1 or recovery<1:
            raise ValueError('Invalid sample counts')
        self.mode=mode; self.window=window; self.warmup=warmup
        self.cadence=cadence; self.recovery=recovery
        self.f_bounds=f_bounds; self.drift_bounds=drift_bounds
        self.history=deque(maxlen=window); self.count=0; self.last_fit=0
        self.model=None; self.good=0; self.state='standard' if mode=='standard' else 'learning'
        self.fit_calls=0; self.fit_seconds=0.; self.events=[]
        self.last_time=None

    @staticmethod
    def basis(t,origin,f0,drift,duration):
        t=np.asarray(t)-origin
        phase=2*np.pi*(f0*t+.5*drift*t*t)
        return np.column_stack([np.ones(len(t)),t/duration,
                                np.cos(phase),np.sin(phase),np.cos(2*phase),np.sin(2*phase)])

    def step(self,t,amplitude):
        """Return keep/reject for CURRENT sample using ONLY past fit.

        Any refit happens after that decision and applies to future samples.
        Missing amplitude passes through and invalidates the cached model.
        """
        if not np.isfinite(t) or (self.last_time is not None and t<=self.last_time):
            raise ValueError('Time must be finite and strictly increasing')
        if amplitude is not None and not np.isfinite(amplitude):
            raise ValueError('Amplitude must be finite or None')
        self.last_time=float(t)
        self.count+=1
        if amplitude is None:
            self.model=None; self.history.clear(); self.good=0
            self.state='standard' if self.mode=='standard' else 'learning'
            return {'keep':True,'state':self.state,'reason':'missing_amplitude','fit_calls':self.fit_calls}
        bad=False
        if self.model is not None and self.count-self.model['created']>2*self.window:
            self.model=None; self.state='learning'; self.good=0
        if self.model is not None:
            m=self.model
            predicted=float((self.basis([t],m['origin'],m['f0'],m['drift'],m['duration'])@m['coef'])[0])
            bad=abs(amplitude-predicted)>m['threshold']
            if bad:
                self.state='active'; self.good=0
            else:
                self.good+=1
                if self.good>=self.recovery:
                    self.state='standard' if self.mode=='adaptive' else 'active'
        keep=not bad if self.mode!='standard' else True
        decision={'keep':keep,'state':self.state,'reason':'amplitude_mismatch' if bad else 'pass',
                  'fit_calls':self.fit_calls}
        self.history.append((float(t),float(amplitude)))
        due=len(self.history)>=self.warmup and (self.fit_calls==0 or self.count-self.last_fit>=self.cadence)
        if self.mode!='standard' and due and (self.mode=='always' or self.state!='standard'):
            self._fit()
        decision['fit_calls']=self.fit_calls
        return decision

    def _fit(self):
        a=np.asarray(self.history)
        self.last_fit=self.count; self.fit_calls+=1
        start=time.perf_counter()
        if np.ptp(a[:,1])==0:
            report={'status':'unreliable','reasons':['constant_amplitude']}
        else:
            report,_=fit_clock(a[:,0],a[:,1],self.f_bounds,self.drift_bounds,seed=91)
        self.fit_seconds+=time.perf_counter()-start
        self.events.append({'sample':self.count,'time':float(a[-1,0]),'status':report['status']})
        if report['status']=='accepted_model':
            origin=report['time_origin']; duration=float(np.ptp(a[:,0]))
            mat=self.basis(a[:,0],origin,report['frequency_initial'],report['frequency_drift'],duration)
            coef=np.linalg.lstsq(mat,a[:,1],rcond=None)[0]
            residual=a[:,1]-mat@coef
            sigma=1.4826*np.median(abs(residual-np.median(residual)))
            self.model={'origin':origin,'duration':duration,'f0':report['frequency_initial'],
                        'drift':report['frequency_drift'],'coef':coef,
                        'threshold':float(max(4.5*sigma,.35*np.std(a[:,1]),1e-8)),'created':self.count}
            self.state='active'; self.good=0
