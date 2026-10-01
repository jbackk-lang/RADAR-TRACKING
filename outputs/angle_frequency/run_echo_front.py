"""First detectable surface vs dominant peak of an extended target."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
C=299792458.; FS=20e6; X=np.arange(384)
L=np.arange(-6,7); H=np.exp(-.5*(L/1.5)**2); H/=np.linalg.norm(H)

def simulate(seed,case):
    rng=np.random.default_rng(seed); front=rng.uniform(150,170)
    distance=30. if case!='unresolved' else 5.
    sep=2*distance/C*FS
    amp={'empty':0.,'visible_front':.8,'weak_front':.15,'unresolved':.8}[case]
    back=0. if case=='empty' else 1.
    s=amp*np.exp(-.5*((X-front)/1.5)**2)*np.exp(1j*rng.uniform(-np.pi,np.pi))
    s+=back*np.exp(-.5*((X-front-sep)/1.5)**2)*np.exp(1j*rng.uniform(-np.pi,np.pi))
    if np.linalg.norm(s): s/=np.linalg.norm(s)
    iq=.8*s[None,:]+.15*(rng.normal(size=(64,384))+1j*rng.normal(size=(64,384)))
    filtered=np.array([np.convolve(row,H,'same') for row in iq])
    p=np.mean(abs(filtered)**2,axis=0)
    score=p/max(float(np.median(p[64:320])),1e-12)
    return front,score

def locate(score,threshold):
    peaks=[k for k in range(65,319) if score[k]>threshold and score[k]>=score[k-1] and score[k]>score[k+1]]
    if not peaks:return {'dominant':None,'first_peak':None}
    def refine(k):
        a,b,c=score[k-1:k+2]; denominator=a-2*b+c
        off=float(np.clip(.5*(a-c)/denominator,-.5,.5)) if denominator else 0.
        return k+off
    return {'dominant':refine(max(peaks,key=lambda k:score[k])),'first_peak':refine(min(peaks))}

def main():
    dest=ROOT/'echo_front_results.json'
    if dest.exists():raise SystemExit('Existing results preserved')
    maxima=[float(np.max(simulate(50000000+s,'empty')[1][64:320])) for s in range(200)]
    threshold=float(np.quantile(maxima,.99,method='higher'))
    rows=[];summary={}
    for ci,case in enumerate(('empty','visible_front','weak_front','unresolved')):
        for seed in range(100):
            front,score=simulate(51000000+ci*1000+seed,case)
            out=locate(score,threshold)
            rows.append(dict(case=case,seed=seed,front_sample=front,outputs=out))
        rr=[r for r in rows if r['case']==case];summary[case]={}
        for method in ('dominant','first_peak'):
            errors=[(r['outputs'][method]-r['front_sample'])*C/(2*FS) for r in rr if r['outputs'][method] is not None]
            summary[case][method]=dict(detections=len(errors),correct_front=sum(abs(e)<7.5 for e in errors) if case!='empty' else None,
                mae_detected_m=float(np.mean(np.abs(errors))) if errors and case!='empty' else None)
    with dest.open('x',encoding='utf-8') as f:json.dump(dict(threshold=threshold,summary=summary,runs=rows),f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
