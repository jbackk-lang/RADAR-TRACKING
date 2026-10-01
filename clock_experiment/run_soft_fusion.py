import hashlib
import json
from pathlib import Path
import time
import numpy as np
from core.radar_tracker import RadarTracker
from .run_adaptive import simulate
from .soft_fusion import fuse_position

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'soft_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    old=json.loads((ROOT/'adaptive_results/summary.json').read_text())
    rows=[]; inputs=[]
    for case in ('clean','correlated','amplitude_only','position_only'):
        for seed in (0,1):
            t,truth,measured,amp=simulate(case,seed)
            path=ROOT/'adaptive_results'/f'{case}_{seed}_adaptive.npz'
            with np.load(path,allow_pickle=False) as cached:
                np.testing.assert_array_equal(t,cached['time'])
                np.testing.assert_array_equal(amp,cached['amplitude'])
                bad=~cached['keep']
            inputs.append({'name':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            for mode in ('geometry','hybrid'):
                tracker=RadarTracker(d_max=.1,k_min=1,smoothing=1.)
                current=None; ids=set(); positions=[]; weights=[]
                start=time.perf_counter()
                for tt,x,warning in zip(t,measured,bad):
                    prediction=tracker._predicted_state(current,tt)[0] if current is not None else (x,0.)
                    xy,w=fuse_position((x,0.),prediction,bool(warning),mode)
                    result=tracker.update([{'x':xy[0]-.01,'y':xy[1],'t':tt},{'x':xy[0]+.01,'y':xy[1],'t':tt}])
                    if len(result)!=1: raise AssertionError('Single target expected')
                    current=next(iter(result)); ids.add(current)
                    positions.append(result[current]['x']); weights.append(w)
                elapsed=time.perf_counter()-start
                positions=np.asarray(positions); weights=np.asarray(weights)
                clock=next(r['clock_fit_seconds'] for r in old['runs'] if r['case']==case and r['seed']==seed and r['mode']=='adaptive')
                row={'case':case,'seed':seed,'mode':mode,'rmse_m':float(np.sqrt(np.mean((positions-truth)**2))),
                    'seconds_excluding_clock':elapsed,'historical_clock_fit_seconds':clock if mode=='hybrid' else 0.,
                    'weighted_frames':int(np.sum(weights<1)),'track_ids':sorted(ids)}
                rows.append(row)
                np.savez_compressed(out/f'{case}_{seed}_{mode}.npz',predicted=positions,truth=truth,time=t,weight=weights)
                print(case,seed,mode,round(row['rmse_m'],6),flush=True)
    result={'scope':'Exploratory synthetic soft fusion; cached amplitude decisions, no new clock timing',
      'protocol_sha256':hashlib.sha256((ROOT/'SOFT_PROTOCOL.md').read_bytes()).hexdigest(),
      'code_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('soft_fusion.py','run_soft_fusion.py','run_adaptive.py')},
      'inputs':inputs,'runs':rows}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

if __name__=='__main__': main()
