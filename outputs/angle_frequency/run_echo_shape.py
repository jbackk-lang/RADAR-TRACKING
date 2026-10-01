"""Range from peak vs whole-echo shape, unknown complex amplitude."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
C=299792458.; FS=20e6; X=np.arange(512); TAUS=(0.,2.,4.,8.,12.)
METHODS=('peak','gaussian_fit','fixed_tail_fit','adaptive_shape')

def shape(u,tau,receiver_tau=0.):
    # Continuous Gaussian convolved with discrete causal decay, sampled at u.
    def base(v):
        if tau==0:
            return np.exp(-.5*(v/1.5)**2)
        n=np.arange(65); w=np.exp(-n/tau); w/=w.sum()
        return np.exp(-.5*((v[...,None]-n)/1.5)**2)@w
    if receiver_tau:
        n=np.arange(49); w=np.exp(-n/receiver_tau); w/=w.sum()
        return sum(wi*base(u-ni) for ni,wi in zip(n,w))
    return base(u)

def estimate(iq):
    p=np.mean(abs(iq)**2,axis=0); k=int(np.argmax(p[64:448]))+64
    noise=max(float(np.median(p[64:448])),1e-12); results={'peak':dict(score=float(p[k]/noise),sample=float(k))}
    idx=np.arange(max(0,k-16),min(512,k+41))
    centers=k+np.arange(-80,21)/10
    data=iq[:,idx]
    candidates=[]
    for tau in TAUS:
        t=shape(idx[None,:]-centers[:,None],tau)
        t/=np.linalg.norm(t,axis=1)[:,None]
        score=np.mean(abs(t@data.T)**2,axis=1)/noise
        best=int(np.argmax(score))
        candidates.append(dict(score=float(score[best]),sample=float(centers[best]),tau=tau))
    results['gaussian_fit']=candidates[0]
    results['fixed_tail_fit']=candidates[3]
    results['adaptive_shape']=max(candidates,key=lambda r:r['score'])
    return results

def simulate(seed,case):
    rng=np.random.default_rng(seed); center=float(rng.uniform(148,174))
    tau={'empty':0.,'gaussian':0.,'tail_known':8.,'tail_changed':12.,'receiver_tail':8.}[case]
    s=shape(X-center,tau,6. if case=='receiver_tail' else 0.)
    s/=np.linalg.norm(s)
    amp=0. if case=='empty' else .65
    s=amp*s*np.exp(1j*rng.uniform(-np.pi,np.pi))
    iq=s[None,:]+.15*(rng.normal(size=(16,512))+1j*rng.normal(size=(16,512)))
    return center,iq

def main():
    dest=ROOT/'echo_shape_results.json'
    if dest.exists():
        raise SystemExit('Existing results preserved')
    dev=[estimate(simulate(46000000+s,'empty')[1]) for s in range(160)]
    thresholds={m:float(np.quantile([r[m]['score'] for r in dev],.99,method='higher')) for m in METHODS}
    rows=[]; summary={}
    for ci,case in enumerate(('empty','gaussian','tail_known','tail_changed','receiver_tail')):
        for seed in range(100):
            center,iq=simulate(47000000+ci*1000+seed,case)
            result=estimate(iq)
            for m,out in result.items():
                out['detected']=bool(out['score']>thresholds[m])
                out['error_m']=float((out['sample']-center)*C/(2*FS)) if case!='empty' else None
            rows.append(dict(case=case,seed=seed,truth_sample=center,results=result))
        rr=[r for r in rows if r['case']==case]
        summary[case]={}
        for m in METHODS:
            detected=[r['results'][m] for r in rr if r['results'][m]['detected']]
            errors=[r['error_m'] for r in detected if r['error_m'] is not None]
            summary[case][m]=dict(detections=len(detected),mae_detected_m=float(np.mean(np.abs(errors))) if errors else None,
                                  bias_detected_m=float(np.mean(errors)) if errors else None,
                                  correct=sum(abs(e)<7.5 for e in errors) if errors else None)
    with dest.open('x',encoding='utf-8') as f:
        json.dump(dict(thresholds=thresholds,summary=summary,runs=rows),f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
