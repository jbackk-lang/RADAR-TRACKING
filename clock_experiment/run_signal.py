import hashlib
import json
from pathlib import Path
import time
import numpy as np
from .signal_monitor import SignalClockMonitor

ROOT=Path(__file__).resolve().parent

def evaluate(t,y,bounds,drift):
    model=SignalClockMonitor(f_bounds=bounds,drift_bounds=drift)
    pred=[]; base=[]; used=[]; states=[]; start=time.perf_counter()
    for tt,a in zip(t,y):
        result=model.step(tt,a)
        pred.append(result['forecast']); base.append(result['baseline'])
        used.append(result['used_clock']); states.append(result['state'])
        assert result['keep_position']
    p=np.asarray(pred[100:],float); b=np.asarray(base[100:],float); observed=y[100:]
    denominator=max(float(np.var(observed)),1e-12)
    return {'nmse_monitor':float(np.mean((p-observed)**2)/denominator),
            'nmse_mean12':float(np.mean((b-observed)**2)/denominator),
            'scored_samples':len(p),'clock_fraction':float(np.mean(used[100:])),
            'fit_calls':model.fit_calls,'seconds':time.perf_counter()-start,
            'events':model.events},p,b,states

def main():
    out=ROOT/'signal_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    rows=[]
    for case in ('chirp','change','noise'):
        for seed in (0,1):
            t=np.arange(480)/20; rng=np.random.default_rng(seed)
            phase=2*np.pi*(.5*t+.5*.008*t*t)
            if case=='change': phase+=2*np.pi*.3*np.maximum(t-t[250],0)
            y=np.sin(phase)+.2*np.cos(2*phase+.4)+rng.normal(0,.1,len(t))
            if case=='noise': y=rng.normal(size=len(t))
            metrics,p,b,states=evaluate(t,y,(.3,1.2),(-.015,.025))
            name=f'{case}_{seed}'; rows.append({'name':name,'source':'synthetic',**metrics})
            np.savez_compressed(out/f'{name}.npz',observed=y[100:],prediction=p,baseline=b,state=states)
            print(name,metrics['nmse_monitor'],metrics['nmse_mean12'],flush=True)
    found=set(); data=Path('C:/Users/jback/Downloads/a/DATA/open_radar/eval')
    for path in sorted(data.glob('*.npz')):
        with np.load(path,allow_pickle=False) as z:
            cls=str(z['cls'])
            if cls in found or len(z['ts'])<=100: continue
            t=(z['ts']-z['ts'][0])/1000.
            y=np.sqrt(np.sum(np.abs(z['spec'].astype(complex))**2,axis=1))
            gaps=int(np.sum(np.diff(z['frames'])!=1))
        found.add(cls)
        metrics,p,b,states=evaluate(t,y,(.1,4.),(-.02,.02))
        name=f'real_{cls}_{path.stem}'
        rows.append({'name':name,'source':'Open Radar','input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'input_path':str(path),'frame_gaps':gaps,**metrics})
        np.savez_compressed(out/f'{name}.npz',observed=y[100:],prediction=p,baseline=b,state=states)
        print(name,metrics['nmse_monitor'],metrics['nmse_mean12'],flush=True)
        if len(found)==4: break
    result={'protocol_sha256':hashlib.sha256((ROOT/'SIGNAL_PROTOCOL.md').read_bytes()).hexdigest(),
            'runs':rows,'real_classes_found':sorted(found)}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

if __name__=='__main__': main()
