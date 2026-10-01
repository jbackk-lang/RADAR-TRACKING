"""Run the frozen, small synthetic integration pilot from the repository root."""
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from scipy.signal import lombscargle
from core.radar_tracker import RadarTracker
from clock_experiment.track_clock import TrackClockBank

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists():
        raise SystemExit('Existing results preserved. Use a separate checkout for a new run.')
    rows=[]
    for case in ('accelerating','noise'):
        for seed in (0,1):
            rng=np.random.default_rng(seed); t=np.arange(400)/20
            phase=2*np.pi*(.5*t+.5*.01*t*t)
            y=np.sin(phase)+.2*np.cos(2*phase+.4)+.15*rng.normal(size=len(t))
            if case=='noise': y=rng.normal(size=len(t))
            tracker=RadarTracker(d_max=.1,k_min=1,smoothing=1.)
            bank=TrackClockBank(tracker)
            ids=set(); fit_time=None
            for i,tt in enumerate(t):
                result=tracker.update([{'x':.2*tt-.01,'y':0.,'t':tt},{'x':.2*tt+.01,'y':0.,'t':tt}])
                if len(result)!=1: raise AssertionError('Unexpected track count')
                tid=next(iter(result)); ids.add(tid)
                bank.observe(tid,tt,y[i])
                if i==299:
                    start=time.perf_counter()
                    report,clock=bank.analyze(tid,(.3,.85),(-.015,.025),seed=91+seed)
                    fit_time=time.perf_counter()-start
            freq=np.linspace(.3,.85,4096)
            start=time.perf_counter()
            power=lombscargle(t[:300],y[:300]-np.mean(y[:300]),2*np.pi*freq)
            constant=float(freq[np.argmax(power)]); baseline_time=time.perf_counter()-start
            predicted=report['frequency_initial']+report['frequency_drift']*(t[300:]-report['time_origin'])
            row={'case':case,'seed':seed,'track_ids':sorted(ids),'train_samples':300,'test_samples':100,
                 'clock_report':report,'clock_fit_seconds':fit_time,'constant_fit_seconds':baseline_time,
                 'constant_frequency_hz':constant,'clock_test_mae_hz':None,'constant_test_mae_hz':None}
            if case!='noise':
                truth=.5+.01*t[300:]
                row['clock_test_mae_hz']=float(np.mean(abs(predicted-truth)))
                row['constant_test_mae_hz']=float(np.mean(abs(constant-truth)))
            np.savez_compressed(out/f'{case}_{seed}.npz',time=t,amplitude=y,test_frequency=predicted)
            rows.append(row)
            print(case,seed,report['status'],row['clock_test_mae_hz'],flush=True)
    result={'scope':'Synthetic amplitude clock attached to original RADAR-TRACKING; no trajectory improvement measured',
            'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),'runs':rows}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    source=ROOT/'astronomy_clock.py'
    (ROOT/'provenance.json').write_text(json.dumps({'source_repository':'https://github.com/jbackk-lang/TIMDR-orbital-tracker',
      'source_path':'timdr_orbit/rotation_clock.py','copy_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
      'tracker_repository':'https://github.com/jbackk-lang/RADAR-TRACKING',
      'tracker_base_commit':'74916877dd0982b7dfef7f3c4921999e0ba3d275'},indent=2),encoding='utf-8')

if __name__=='__main__': main()
