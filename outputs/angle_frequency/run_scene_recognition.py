"""Recognition from ordinary radar detections, no extra measurements."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
DT=.5; T=np.arange(12)*DT

def simulate(seed,case):
    rng=np.random.default_rng(seed)
    origin=np.array([500.,rng.uniform(-30,30)])
    center=origin+T[:,None]*np.array([3.,.5])
    if case=='rigid_rotating':
        u=np.stack([np.cos(.5*T),np.sin(.5*T)],axis=1)*2
        positions=np.stack([center-u,center+u],axis=1)
        center_v=np.tile([3.,.5],(12,1));du=np.stack([-np.sin(.5*T),np.cos(.5*T)],axis=1)
        velocities=np.stack([center_v-du,center_v+du],axis=1)
    else:
        p=center+np.array([0.,-2.]);q=center+np.array([0.,2.])
        vp=np.tile([3.,.5],(12,1));vq=vp.copy()
        if case=='two_diverging':q=q+T[:,None]*np.array([1.5,1.]);vq+=np.array([1.5,1.])
        if case in ('ghost_constant','ghost_inconsistent'):
            radial=center/np.linalg.norm(center,axis=1)[:,None]
            extra=6.+(.9*T if case=='ghost_inconsistent' else np.zeros_like(T))
            q=p+radial*extra[:,None]
        positions=np.stack([p,q],axis=1);velocities=np.stack([vp,vq],axis=1)
    true_radial=np.sum(positions*velocities,axis=2)/np.linalg.norm(positions,axis=2)
    detections=positions+rng.normal(0,.12,positions.shape)
    radial_v=true_radial+rng.normal(0,.15,true_radial.shape)
    # Unordered detections; no persistent truth ID supplied to the recognizer.
    swaps=rng.integers(0,2,len(T)).astype(bool)
    detections[swaps]=detections[swaps,::-1];radial_v[swaps]=radial_v[swaps,::-1]
    return detections,radial_v

def recognize(detections,doppler):
    p=np.array(detections,copy=True);v=np.array(doppler,copy=True)
    if p.shape!=(12,2,2) or v.shape!=(12,2):raise ValueError('12 frames, two 2D detections and radial velocities required')
    for i in range(1,len(T)):
        prediction=p[i-1] if i==1 else p[i-1]+(p[i-1]-p[i-2])
        if np.sum((p[i,::-1]-prediction)**2)<np.sum((p[i]-prediction)**2):
            p[i]=p[i,::-1];v[i]=v[i,::-1]
    ranges=np.linalg.norm(p,axis=2)
    slopes=np.array([np.polyfit(T,ranges[:,j],1)[0] for j in range(2)])
    radial_mismatch=float(np.max(abs(slopes-v.mean(axis=0))))
    separation=np.linalg.norm(p[:,1]-p[:,0],axis=1)
    # Observed extent is a property of the detection group, not proven object size.
    extent=float(np.median(separation));spread=float(np.std(separation))
    if radial_mismatch>.6:
        label='inconsistent_echo';count=None
    elif spread>.35:
        label='separate_motion';count=2
    else:
        label='coherent_group_unresolved';count=None
    return dict(label=label,count=count,observed_extent_m=extent,extent_std_m=spread,radial_mismatch_mps=radial_mismatch)

def main():
    dest=ROOT/'scene_recognition_results.json'
    if dest.exists():raise SystemExit('Existing results preserved')
    cases={'rigid_large':1,'rigid_rotating':1,'two_diverging':2,'two_parallel':2,'ghost_constant':1,'ghost_inconsistent':1}
    rows=[];summary={}
    for ci,(case,truth_count) in enumerate(cases.items()):
        for seed in range(100):
            p,v=simulate(56000000+ci*1000+seed,case);result=recognize(p,v)
            rows.append(dict(case=case,seed=seed,true_count=truth_count,result=result))
        rr=[r for r in rows if r['case']==case]
        summary[case]=dict(peak_count_correct=sum(r['true_count']==2 for r in rr),
            temporal_count_returned=sum(r['result']['count'] is not None for r in rr),
            temporal_count_correct=sum(r['result']['count']==r['true_count'] for r in rr),
            temporal_count_wrong=sum(r['result']['count'] is not None and r['result']['count']!=r['true_count'] for r in rr),
            labels={label:sum(r['result']['label']==label for r in rr) for label in ('separate_motion','coherent_group_unresolved','inconsistent_echo')},
            median_observed_extent_m=float(np.median([r['result']['observed_extent_m'] for r in rr])))
    with dest.open('x',encoding='utf-8') as f:json.dump(dict(summary=summary,runs=rows),f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
