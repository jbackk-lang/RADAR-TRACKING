"""Run frozen synthetic adaptive gate vs always-on gate vs standard tracker."""
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from core.radar_tracker import RadarTracker
from .adaptive import AdaptiveAmplitudeGate

ROOT=Path(__file__).resolve().parent

def simulate(case,seed):
    rng=np.random.default_rng(seed); t=np.arange(480)/20.
    truth=.2*t
    measured=truth+rng.normal(0,.015,len(t))
    phase=2*np.pi*(.5*t+.5*.008*t*t)
    amp=np.sin(phase)+.2*np.cos(2*phase+.4)+rng.normal(0,.1,len(t))
    burst=((np.arange(len(t))>=180)&(np.arange(len(t))<195))|((np.arange(len(t))>=320)&(np.arange(len(t))<335))
    if case in ('correlated','amplitude_only'): amp[burst]+=4
    if case in ('correlated','position_only'): measured[burst]+=.8
    return t,truth,measured,amp

def run(mode,t,measured,amp):
    tracker=RadarTracker(d_max=.1,k_min=1,smoothing=1.)
    gate=AdaptiveAmplitudeGate(mode)
    positions=[]; states=[]; keeps=[]; ids=set(); current=None
    start=time.perf_counter()
    for tt,x,a in zip(t,measured,amp):
        decision=gate.step(tt,a)
        fallback=tracker._predicted_state(current,tt)[0][0] if current is not None else x
        points=[{'x':x-.01,'y':0.,'t':tt},{'x':x+.01,'y':0.,'t':tt}]
        result=tracker.update(points if decision['keep'] else [])
        if result:
            # Expected single-target scene; fail instead of using truth to select a track.
            if len(result)!=1: raise AssertionError('Multiple detections in single-target experiment')
            current=next(iter(result)); ids.add(current); positions.append(result[current]['x'])
        else: positions.append(fallback)
        keeps.append(decision['keep']); states.append(decision['state'])
    return np.asarray(positions),np.asarray(keeps),np.asarray(states),{
        'seconds':time.perf_counter()-start,'clock_fit_seconds':gate.fit_seconds,
        'fit_calls':gate.fit_calls,'track_ids':sorted(ids),'rejected_frames':int(np.sum(~np.asarray(keeps))),
        'events':gate.events}

def main():
    out=ROOT/'adaptive_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved.')
    rows=[]
    for ci,case in enumerate(('clean','correlated','amplitude_only','position_only')):
        for seed in (0,1):
            t,truth,measured,amp=simulate(case,seed)
            methods=['standard','always','adaptive']; shift=(ci+seed)%3
            for mode in methods[shift:]+methods[:shift]:
                position,keeps,states,stats=run(mode,t,measured,amp)
                row={'case':case,'seed':seed,'mode':mode,'rmse_m':float(np.sqrt(np.mean((position-truth)**2))),**stats}
                rows.append(row)
                np.savez_compressed(out/f'{case}_{seed}_{mode}.npz',time=t,truth=truth,measured=measured,
                                    amplitude=amp,predicted=position,keep=keeps,state=states)
                print(case,seed,mode,'RMSE',round(row['rmse_m'],5),'fits',row['fit_calls'],flush=True)
    summary={}
    for case in ('clean','correlated','amplitude_only','position_only'):
        summary[case]={}
        for mode in ('standard','always','adaptive'):
            group=[r for r in rows if r['case']==case and r['mode']==mode]
            summary[case][mode]={k:float(np.mean([r[k] for r in group])) for k in ('rmse_m','seconds','fit_calls','rejected_frames')}
    result={'scope':'Synthetic single-target amplitude-position correlation hypothesis, not real-radar validation',
        'protocol_sha256':hashlib.sha256((ROOT/'ADAPTIVE_PROTOCOL.md').read_bytes()).hexdigest(),
        'code_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('adaptive.py','run_adaptive.py','astronomy_clock.py')},
        'summary':summary,'runs':rows}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__': main()
