"""Offline candidate flashes, not blade/rotation identification."""
import numpy as np
from scipy.ndimage import label, find_objects

def detect(power,times,frames,frequency):
    power=np.asarray(power,float); times=np.asarray(times,float); frames=np.asarray(frames)
    frequency=np.asarray(frequency,float)
    if power.shape!=(len(times),len(frequency)) or len(frames)!=len(times) or not len(times):
        raise ValueError('Shape mismatch')
    if not np.isfinite(power).all() or np.any(power<0) or not np.isfinite(times).all() or not np.isfinite(frequency).all():
        raise ValueError('Invalid values')
    if np.any(np.diff(times)<=0) or np.any(np.diff(frames)<=0): raise ValueError('Nonincreasing time/frame')
    chunks=np.split(np.arange(len(times)),np.flatnonzero(np.diff(frames)!=1)+1)
    events=[]; ratio=np.ones_like(power); skipped=0
    for ci,ix in enumerate(chunks):
        if len(ix)<10:
            skipped+=len(ix); continue
        p=power[ix]
        floor=max(float(np.median(p))*1e-12,1e-300)
        relative=p/np.maximum(np.median(p,axis=0),floor)
        ratio[ix]=relative
        spectral=p/np.maximum(np.median(p,axis=1,keepdims=True),floor)
        mask=(relative>=10)&(spectral>=10)
        components,n=label(mask,np.ones((3,3),int))
        for ident,box in enumerate(find_objects(components),1):
            if box is None: continue
            local=components[box]==ident
            count=int(local.sum()); duration=box[0].stop-box[0].start
            if count<3 or duration>5: continue
            scores=np.where(local,relative[box],-np.inf)
            a,b=np.unravel_index(np.argmax(scores),scores.shape)
            ti=box[0].start+a; fi=box[1].start+b
            events.append({'chunk':ci,'frame_index':int(ix[ti]),'time_s':float(times[ix[ti]]),
              'doppler_hz':float(frequency[fi]),'peak_db_above_temporal_median':float(10*np.log10(relative[ti,fi])),
              'pixels':count,'duration_frames':duration,'start_time_s':float(times[ix[box[0].start]]),
              'end_time_s':float(times[ix[box[0].stop-1]]),'frequency_min_hz':float(frequency[box[1].start]),
              'frequency_max_hz':float(frequency[box[1].stop-1])})
    return sorted(events,key=lambda e:(e['time_s'],e['doppler_hz'])),ratio,skipped
