"""Frozen model bank, model mismatch and onset agreement gates."""
import json
from pathlib import Path
import numpy as np
from run_echo_shape import shape,C,FS,X

ROOT=Path(__file__).resolve().parent

def simulate(seed,case):
    rng=np.random.default_rng(seed); front=float(rng.uniform(150,175))
    if case=='tail':s=shape(X-front,8.)
    elif case=='receiver':s=shape(X-front,8.,6.)
    elif case in ('pair','weak_front'):
        s=shape(X-front,0.).astype(complex)*(.15 if case=='weak_front' else .8)
        s+=shape(X-front-5,0.)*np.exp(1j*rng.uniform(-np.pi,np.pi))
    else:s=shape(X-front,0.)
    s=s/np.linalg.norm(s)*(0. if case=='empty' else .5)*np.exp(1j*rng.uniform(-np.pi,np.pi))
    iq=s[None,:]+.15*(rng.normal(size=(64,512))+1j*rng.normal(size=(64,512)))
    return front,iq

def analyze(iq):
    z=np.mean(iq,axis=0); noise=max(float(np.mean(abs(z[:64])**2)),1e-12)
    k=int(np.argmax(abs(z[64:448])**2))+64
    idx=np.arange(max(0,k-16),min(512,k+49)); data=z[idx]
    centers=k+np.arange(-32,9)/4; candidates=[]
    for tau in (0.,4.,8.,12.):
        t=shape(idx[None,:]-centers[:,None],tau)
        t/=np.linalg.norm(t,axis=1)[:,None]
        coefficients=t@data; explained=abs(coefficients)**2
        for j,center in enumerate(centers):
            residual=max(0.,float(np.sum(abs(data)**2)-explained[j]))
            bic=residual/noise+3*np.log(len(idx))
            candidates.append(dict(model=f'tail_{tau}',sample=float(center),bic=float(bic),residual=residual,
                                   gain=float(explained[j]/noise),parameters=3))
    for sep in (3.,5.,8.):
        a=shape(idx[None,:]-centers[:,None],0.); b=shape(idx[None,:]-centers[:,None]-sep,0.)
        a/=np.linalg.norm(a,axis=1)[:,None]; b/=np.linalg.norm(b,axis=1)[:,None]
        cross=np.sum(a*b,axis=1); ca=a@data; cb=b@data
        aa=(ca-cross*cb)/(1-cross**2);bb=(cb-cross*ca)/(1-cross**2)
        explained=np.real(np.conj(ca)*aa+np.conj(cb)*bb)
        for j,center in enumerate(centers):
            residual=max(0.,float(np.sum(abs(data)**2)-explained[j]))
            # Refuse to call an almost-zero first component a visible front.
            component_snr=float(abs(aa[j])**2*(1-cross[j]**2)/noise)
            candidates.append(dict(model=f'pair_{sep}',sample=float(center),bic=float(residual/noise+5*np.log(len(idx))),
                residual=residual,gain=float(explained[j]/noise),parameters=5,front_snr=component_snr))
    best=min(candidates,key=lambda c:c['bic'])
    near=[c for c in candidates if c['bic']<=best['bic']+2]
    spread=max(c['sample'] for c in near)-min(c['sample'] for c in near)
    best=dict(best,spread_samples=float(spread),normalized_residual=float(best['residual']/noise/(len(idx)-best['parameters'])))
    peak=float(k);gauss=min((c for c in candidates if c['model']=='tail_0.0'),key=lambda c:c['bic'])
    return dict(best=best,peak=peak,gauss_sample=gauss['sample'],noise=noise)

def main():
    dest=ROOT/'final_echo_results.json'
    if dest.exists():raise SystemExit('Existing results preserved')
    dev_noise=[analyze(simulate(54000000+s,'empty')[1]) for s in range(100)]
    dev_good=[analyze(simulate(54100000+ci*1000+s,case)[1]) for ci,case in enumerate(('gaussian','tail','pair')) for s in range(40)]
    gain_threshold=float(np.quantile([r['best']['gain'] for r in dev_noise],.99,method='higher'))
    residual_threshold=float(np.quantile([r['best']['normalized_residual'] for r in dev_good],.99,method='higher'))
    rows=[];summary={}
    for ci,case in enumerate(('empty','gaussian','tail','pair','weak_front','receiver')):
        for seed in range(100):
            front,iq=simulate(55000000+ci*1000+seed,case);out=analyze(iq);b=out['best']
            detected=b['gain']>gain_threshold
            reliable=detected and b['normalized_residual']<=residual_threshold and b['spread_samples']<=1.
            if 'front_snr' in b:reliable=reliable and b['front_snr']>9.
            out.update(detected=bool(detected),accepted=bool(reliable),truth_sample=front)
            rows.append(dict(case=case,seed=seed,analysis=out))
        rr=[r['analysis'] for r in rows if r['case']==case];summary[case]={}
        for method in ('peak','gauss','bank'):
            found=[r for r in rr if r['accepted']] if method=='bank' else [r for r in rr if r['detected']]
            errors=[((r['best']['sample'] if method=='bank' else r['gauss_sample'] if method=='gauss' else r['peak'])-r['truth_sample'])*C/(2*FS) for r in found]
            summary[case][method]=dict(returned=len(found),correct=sum(abs(e)<7.5 for e in errors) if case!='empty' else None,
                wrong=sum(abs(e)>=7.5 for e in errors) if case!='empty' else None,
                mae_returned_m=float(np.mean(np.abs(errors))) if errors and case!='empty' else None)
    with dest.open('x',encoding='utf-8') as f:json.dump(dict(gain_threshold=gain_threshold,residual_threshold=residual_threshold,summary=summary,runs=rows),f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
