"""Estimate Doppler from I/Q, then align phase and range migration."""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
C=299792458.; FC=3e9; LAMBDA=C/FC; FS=20e6; PRF=32000.
N=512; X=np.arange(384); T=(np.arange(N)-(N-1)/2)/PRF
L=np.arange(-6,7); H=np.exp(-.5*(L/1.5)**2); H/=np.linalg.norm(H)
METHODS=('power_fit','coherent_unaligned','phase_only','phase_and_range')

def fit(profile,k):
    idx=np.arange(max(0,k-10),min(len(X),k+11))
    centers=k+np.arange(-50,51)/10
    templates=np.exp(-.5*((idx[None,:]-centers[:,None])/1.5)**2)
    templates/=np.linalg.norm(templates,axis=1)[:,None]
    if profile.ndim==2:
        scores=np.mean(abs(profile[:,idx]@templates.T)**2,axis=0)
    else:
        scores=abs(templates@profile[idx])**2
    j=int(np.argmax(scores))
    return float(centers[j]),float(scores[j])

def estimate(iq):
    energy=np.mean(abs(iq)**2,axis=0); k=int(np.argmax(energy[64:320]))+64
    idx=np.arange(max(0,k-8),min(384,k+9))
    # Frequency estimation does not use true R or v.
    spec=np.sum(abs(np.fft.fft(iq[:,idx],4096,axis=0))**2,axis=1)
    j=int(np.argmax(spec)); a,b,c=spec[(j-1)%4096],spec[j],spec[(j+1)%4096]
    off=float(np.clip(.5*(a-c)/(a-2*b+c),-.5,.5)) if a-2*b+c else 0.
    f=((j+off+2048)%4096-2048)*PRF/4096
    velocity=float(f*LAMBDA/2)
    corrected=iq*np.exp(-2j*np.pi*f*T[:,None])
    shifts=2*velocity*T/C*FS
    aligned=np.array([np.interp(X+shift,X,row.real)+1j*np.interp(X+shift,X,row.imag)
                      for shift,row in zip(shifts,corrected)])
    return velocity,{ 'power_fit':fit(iq,k), 'coherent_unaligned':fit(np.mean(iq,axis=0),k),
                      'phase_only':fit(np.mean(corrected,axis=0),k),
                      'phase_and_range':fit(np.mean(aligned,axis=0),k)}

def simulate(seed,case):
    rng=np.random.default_rng(seed); center=float(rng.uniform(150,175))
    velocity={'empty':0.,'stationary':0.,'ordinary':30.,'fast':600.,'acceleration':100.}[case]
    acceleration=3000. if case=='acceleration' else 0.
    motion=velocity*T+.5*acceleration*T*T
    envelope=np.exp(-.5*((X[None,:]-center-2*motion[:,None]/C*FS)/1.5)**2)
    envelope/=np.linalg.norm(envelope,axis=1)[:,None]
    phase=rng.uniform(-np.pi,np.pi)+4*np.pi*motion/LAMBDA
    amp=0. if case=='empty' else .25
    iq=amp*envelope*np.exp(1j*phase[:,None])+.15*(rng.normal(size=(N,384))+1j*rng.normal(size=(N,384)))
    return center,velocity,iq

def main():
    dest=ROOT/'range_motion_results.json'
    if dest.exists():
        raise SystemExit('Existing results preserved')
    dev=[estimate(simulate(48000000+s,'empty')[2])[1] for s in range(100)]
    thresholds={m:float(np.quantile([r[m][1] for r in dev],.99,method='higher')) for m in METHODS}
    rows=[]; summary={}
    for ci,case in enumerate(('empty','stationary','ordinary','fast','acceleration')):
        for seed in range(60):
            center,v,iq=simulate(49000000+ci*1000+seed,case)
            estimate_v,outputs=estimate(iq)
            results={m:dict(range_error_m=float((pos-center)*C/(2*FS)),detected=bool(score>thresholds[m]),score=score)
                     for m,(pos,score) in outputs.items()}
            rows.append(dict(case=case,seed=seed,velocity=v,estimated_v=estimate_v,results=results))
        rr=[r for r in rows if r['case']==case]
        summary[case]={'v_mae':float(np.mean([abs(r['estimated_v']-r['velocity']) for r in rr])) if case!='empty' else None}
        for m in METHODS:
            found=[r['results'][m] for r in rr if r['results'][m]['detected']]
            summary[case][m]=dict(detected=len(found),correct=sum(abs(r['range_error_m'])<7.5 for r in found) if case!='empty' else None,
                mae_detected_m=float(np.mean([abs(r['range_error_m']) for r in found])) if found and case!='empty' else None)
    with dest.open('x',encoding='utf-8') as f:
        json.dump(dict(thresholds=thresholds,summary=summary,runs=rows),f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
