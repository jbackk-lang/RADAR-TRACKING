import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import linear_sum_assignment
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from core.radar_tracker import RadarTracker
CASES=('measurement_noise','dropouts','interference','close_crossing','irregular_unknown_noise')


def truth_at(t,case):
    x=np.array([100+2*t,120+8*np.sin(.18*t),140+2*min(t,3)+3*max(0,t-5),155.])
    y=np.array([-18.,-3+8*(1-np.cos(.18*t)),16.,32.])
    if case=='close_crossing':
        x[:2]=[110+1.5*t,112+1.5*t];y[:2]=[-6+.8*t,6-.8*t]
    return np.column_stack([x,y])


def generate(seed,case):
    rng=np.random.default_rng(seed);frames=[];t=0.;bias=np.zeros((4,2))
    for frame in range(40):
        if frame:t+=float(rng.uniform(.15,.85)) if case=='irregular_unknown_noise' else .5
        truth=truth_at(t,case);points=[]
        bias=.8*bias+rng.normal(0,.08,bias.shape)
        for obj,p in enumerate(truth):
            if case=='dropouts' and (rng.random()<.2 or (obj==0 and 10<=frame<=15) or 18<=frame<=20):continue
            sigma_r,sigma_angle=(1.,.006) if case=='irregular_unknown_noise' else (.3,.002)
            distance=np.linalg.norm(p)+rng.normal(0,sigma_r)
            angle=np.arctan2(p[1],p[0])+rng.normal(0,sigma_angle)
            observed=np.array([distance*np.cos(angle),distance*np.sin(angle)])+bias[obj]
            for _ in range(3):
                q=observed+rng.normal(0,.1,2)
                points.append(dict(x=float(q[0]),y=float(q[1]),t=t))
        if case=='interference':
            for _ in range(2):points.append(dict(x=float(rng.uniform(90,170)),y=float(rng.uniform(-25,40)),t=t))
            if rng.random()<.35:
                ghost=truth[int(rng.integers(0,4))]+[5.,4.]
                for _ in range(2):
                    q=ghost+rng.normal(0,.15,2);points.append(dict(x=float(q[0]),y=float(q[1]),t=t))
        rng.shuffle(points);frames.append(dict(t=t,truth=truth.tolist(),points=points))
    return frames


def assess(frames,model):
    tracker=RadarTracker(d_max=1.2,k_min=1,gate_chi2=30.,smoothing=.7,
        use_timdr=model!='cv',timdr_variant='robust' if model=='robust' else 'legacy',position_sigma=.4)
    errors=[];missing=extra=switches=total=0;last={}
    for frame in frames:
        result=tracker.update(frame['points']);tracker.prune_stale(frame['t'],2.)
        truth=np.array(frame['truth']);tracks=list(result.items());total+=len(truth)
        if not tracks:missing+=len(truth);continue
        xy=np.array([[tr['x'],tr['y']] for _,tr in tracks]);distance=np.linalg.norm(truth[:,None,:]-xy[None,:,:],axis=2)
        ii,jj=linear_sum_assignment(distance);matched=0
        for i,j in zip(ii,jj):
            if distance[i,j]<=2.:
                errors.append(float(distance[i,j]));matched+=1;tid=tracks[j][0]
                if i in last and last[i]!=tid:switches+=1
                last[i]=tid
        missing+=len(truth)-matched;extra+=len(tracks)-matched
    return dict(mae_matched_m=float(np.mean(errors)) if errors else None,miss_rate=missing/total,
                extra_per_frame=extra/len(frames),id_switches=switches)


def main():
    dest=ROOT/'realistic_timdr_results.json'
    if dest.exists():raise SystemExit('Existing results preserved')
    rows=[];summary={}
    for ci,case in enumerate(CASES):
        for seed in range(8):
            input_seed=62000000+ci*1000+seed;frames=generate(input_seed,case)
            digest=hashlib.sha256(json.dumps(frames,separators=(',',':')).encode()).hexdigest()
            rows.append(dict(case=case,seed=input_seed,input_sha256=digest,
                             results={m:assess(frames,m) for m in ('cv','legacy','robust')}))
        rr=[r for r in rows if r['case']==case];summary[case]={}
        for model in ('cv','legacy','robust'):
            summary[case][model]={key:float(np.mean([r['results'][model][key] for r in rr])) for key in ('mae_matched_m','miss_rate','extra_per_frame','id_switches')}
        print(case,flush=True)
    hashes={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in {
        'operator':ROOT.parents[1]/'core/timdr_robust.py','protocol':ROOT/'REALISTIC_TIMDR_PROTOCOL.md',
        'runner':Path(__file__)}.items()}
    with dest.open('x',encoding='utf-8') as f:json.dump(dict(summary=summary,source_hashes=hashes,runs=rows),f,separators=(',',':'))
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
