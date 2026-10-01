"""Test a Gaussian echo hypothesis; distinguish envelope from noise law."""
import json
from pathlib import Path
import numpy as np
from run_echo_shape import shape,C,FS,X

ROOT=Path(__file__).resolve().parent
WIDTHS=(.75,1.,1.5,2.,3.,4.,6.,8.,12.)

def fit(iq):
    # Stationary coherent echoes only. Unknown complex amplitude is eliminated.
    z=np.mean(iq,axis=0); k=int(np.argmax(abs(z[64:448])**2))+64
    idx=np.arange(max(0,k-32),min(512,k+49))
    centers=k+np.arange(-32,33)/4
    data=z[idx]; noise=float(np.mean(abs(z[:64])**2))
    best=None
    for sigma in WIDTHS:
        templates=np.exp(-.5*((idx[None,:]-centers[:,None])/sigma)**2)
        templates/=np.linalg.norm(templates,axis=1)[:,None]
        coefficients=templates@data
        j=int(np.argmax(abs(coefficients)**2))
        residual=float(np.sum(abs(data-coefficients[j]*templates[j])**2))
        if best is None or residual<best['residual']:
            best=dict(center=float(centers[j]),sigma=sigma,residual=residual)
    total=float(np.sum(abs(data)**2))
    # Descriptive noise-subtracted mismatch, not a formal Gaussianity p-value.
    excess=max(0.,best['residual']-(len(idx)-1)*noise)
    best['shape_mismatch']=float(excess/max(total-len(idx)*noise,1e-12))
    best['coherent_peak_to_noise']=float(max(abs(z[idx])**2)/max(noise,1e-12))
    return best

def simulate(seed,case):
    rng=np.random.default_rng(seed); center=float(rng.uniform(150,175))
    if case=='tail': s=shape(X-center,8.)
    elif case=='two_reflections':
        s=shape(X-center,0.).astype(complex)+.8*np.exp(1j*rng.uniform(-np.pi,np.pi))*shape(X-center-5,0.)
    else:s=shape(X-center,0.)
    if np.linalg.norm(s):s=s/np.linalg.norm(s)
    s=(0. if case=='empty' else .65)*s*np.exp(1j*rng.uniform(-np.pi,np.pi))
    noise=.15*(rng.normal(size=(64,512))+1j*rng.normal(size=(64,512)))
    return center,s[None,:]+noise,noise

def moments(values):
    x=np.asarray(values).ravel(); mean=float(np.mean(x)); std=float(np.std(x)); z=(x-mean)/std
    return dict(mean=mean,std=std,skew=float(np.mean(z**3)),excess_kurtosis=float(np.mean(z**4)-3))

def main():
    dest=ROOT/'gaussian_shape_results.json'
    if dest.exists():raise SystemExit('Existing results preserved')
    dev_gauss=[fit(simulate(52000000+s,'gaussian')[1]) for s in range(100)]
    dev_noise=[fit(simulate(52100000+s,'empty')[1]) for s in range(100)]
    mismatch_threshold=float(np.quantile([r['shape_mismatch'] for r in dev_gauss],.95,method='higher'))
    detection_threshold=float(np.quantile([r['coherent_peak_to_noise'] for r in dev_noise],.99,method='higher'))
    rows=[];summary={}
    for ci,case in enumerate(('gaussian','tail','two_reflections','empty')):
        for seed in range(100):
            center,iq,noise=simulate(53000000+ci*1000+seed,case)
            out=fit(iq);out['detected']=bool(out['coherent_peak_to_noise']>detection_threshold)
            out['gaussian_compatible']=bool(out['detected'] and out['shape_mismatch']<=mismatch_threshold)
            rows.append(dict(case=case,seed=seed,truth_center=center,fit=out,
                             noise_real=moments(noise.real),noise_imag=moments(noise.imag)))
        rr=[r for r in rows if r['case']==case]
        found=[r for r in rr if r['fit']['detected']]
        summary[case]=dict(detections=len(found),gaussian_compatible=sum(r['fit']['gaussian_compatible'] for r in rr),
            median_mismatch=float(np.median([r['fit']['shape_mismatch'] for r in found])) if found else None,
            range_mae_detected_m=float(np.mean([abs(r['fit']['center']-r['truth_center'])*C/(2*FS) for r in found])) if found and case!='empty' else None,
            median_sigma_samples=float(np.median([r['fit']['sigma'] for r in found])) if found else None)
    with dest.open('x',encoding='utf-8') as f:json.dump(dict(mismatch_threshold=mismatch_threshold,detection_threshold=detection_threshold,summary=summary,runs=rows),f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
