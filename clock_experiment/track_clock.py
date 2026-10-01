"""Bounded amplitude histories keyed by existing RadarTracker IDs.

The caller must associate amplitude to the correct target. Positions alone
cannot supply a rotational clock. Fits are explicit offline diagnostics;
never used to overwrite timestamps, velocity, identity or track prediction.
"""
from collections import deque
import numpy as np
from .astronomy_clock import fit_clock

class TrackClockBank:
    def __init__(self, tracker, max_samples=600):
        if not isinstance(max_samples,int) or max_samples<50:
            raise ValueError('max_samples must be an integer >=50')
        self.tracker=tracker
        self.max_samples=max_samples
        self.samples={}

    def observe(self, track_id, time_s, amplitude):
        if track_id not in self.tracker.tracks:
            raise ValueError('Amplitude requires an existing, associated track ID')
        if not np.isfinite(time_s) or not np.isfinite(amplitude):
            raise ValueError('Time and amplitude must be finite')
        if time_s != self.tracker.tracks[track_id][-1]['t']:
            raise ValueError('Amplitude time must match latest associated detection')
        history=self.samples.setdefault(track_id,deque(maxlen=self.max_samples))
        if history and time_s <= history[-1][0]:
            raise ValueError('Amplitude times must strictly increase')
        history.append((float(time_s),float(amplitude)))

    def prune(self):
        removed=[tid for tid in self.samples if tid not in self.tracker.tracks]
        for tid in removed: del self.samples[tid]
        return removed

    def analyze(self, track_id, f_bounds, drift_bounds, seed=91):
        if track_id not in self.tracker.tracks:
            raise ValueError('Unknown or stale track ID')
        samples=np.asarray(self.samples.get(track_id,[]),dtype=float)
        base={'track_id':track_id,'samples':len(samples),'physical_rotation_identified':False,
              'used_for_trajectory':False,'units':'seconds, cycles/second',
              'scope':'offline amplitude periodicity, not translational velocity'}
        if len(samples)<50:
            return {**base,'status':'insufficient_data','reasons':['need_50_amplitude_samples']},None
        if np.ptp(samples[:,1])==0:
            return {**base,'status':'unreliable','reasons':['constant_amplitude']},None
        report,clock=fit_clock(samples[:,0],samples[:,1],f_bounds,drift_bounds,seed=seed)
        return {**report,**base},clock
