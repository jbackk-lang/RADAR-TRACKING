import json
import numpy as np
from run_angle import ROOT,digest
from stereo_model import CENTER,JointEstimator,simulate
from robust_scan import RobustScanEstimator

def correct(out,truth):
    return len(out['angles'])==len(truth) and bool(np.all(np.rad2deg(abs(np.sort(out['angles'])-np.sort(truth)))<=.25))

def main():
    path=ROOT/'robust_results.json'; iqpath=ROOT/'robust_iq.npz'
    if path.exists() or iqpath.exists():
        raise SystemExit('Existing results preserved')
    arrays={}; rows=[]; baseline=JointEstimator(2); current=RobustScanEstimator(2)
    for kind in ('empty','single','pair','disappear','appear','moving_pair'):
        for seed in range(10):
            sep=.75 if seed%2==0 else 1.5
            ratio=.25 if seed%2==0 else .5
            memories={c:RobustScanEstimator(2) for c in ('clean','impulsive')}
            for step in range(4):
                rng=np.random.default_rng(19000000+seed*10+step)
                center=CENTER+np.deg2rad(.037+(.12*step if kind=='moving_pair' else 0))
                truth=[] if kind=='empty' else [center-np.deg2rad(sep/2)]
                pair=kind in ('pair','moving_pair') or (kind=='disappear' and step<3) or (kind=='appear' and step==3)
                amplitudes=[] if not truth else [rng.uniform(.8,1.2)*np.exp(1j*rng.uniform(-np.pi,np.pi))]
                if pair:
                    truth.append(center+np.deg2rad(sep/2))
                    amplitudes.append(ratio*rng.uniform(.8,1.2)*np.exp(1j*rng.uniform(-np.pi,np.pi)))
                if truth:
                    signal=simulate(20000000+seed*10+step,truth,amplitudes,2)
                else:
                    noise_rng=np.random.default_rng(20000000+seed*10+step)
                    signal=.05*(noise_rng.normal(size=242)+1j*noise_rng.normal(size=242))
                corrupted=signal.copy().reshape(-1,2)
                positions=rng.choice(len(corrupted),8,replace=False)
                corrupted[positions]+=1.5*(rng.normal(size=(8,2))+1j*rng.normal(size=(8,2)))
                for condition,y in (('clean',signal),('impulsive',corrupted.reshape(-1))):
                    key=f'{kind}_{seed}_{step}_{condition}'; arrays[key]=y
                    fresh,_=current.fit_current(y)
                    outputs=dict(baseline=baseline.fit(y),robust_current=fresh,robust_memory=memories[condition].observe(y))
                    rows.append(dict(kind=kind,seed=seed,step=step,condition=condition,truth=truth,iq_key=key,
                                     outputs=outputs,correct={m:correct(o,truth) for m,o in outputs.items()}))
    summary={}
    for condition in ('clean','impulsive'):
        summary[condition]={}
        for kind in ('ALL','empty','single','pair','disappear','appear','moving_pair'):
            rr=[r for r in rows if r['condition']==condition and (kind=='ALL' or r['kind']==kind)]
            summary[condition][kind]=dict(cases=len(rr),correct={m:sum(r['correct'][m] for r in rr) for m in ('baseline','robust_current','robust_memory')},
                                         fourth_correct={m:sum(r['correct'][m] for r in rr if r['step']==3) for m in ('baseline','robust_current','robust_memory')},
                                         fourth_cases=sum(r['step']==3 for r in rr),
                                         false_pairs={m:sum(o['count']==2 for r in rr if len(r['truth'])==1 for name,o in r['outputs'].items() if name==m) for m in ('baseline','robust_current','robust_memory')})
    with iqpath.open('xb') as f:
        np.savez_compressed(f,**arrays)
    result=dict(summary=summary,runs=rows,iq_sha256=digest(iqpath),
                hashes={p.name:digest(p) for p in (ROOT/'ROBUST_PROTOCOL.md',ROOT/'robust_scan.py',ROOT/'run_robust.py',ROOT/'stereo_model.py')})
    with path.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
