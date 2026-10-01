"""Equal-energy waveforms, independent noise thresholds, held-out detection."""
import json
import argparse
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
C=299792458.; FS=20e6; F0=77e9; DF=1e6; PERIOD=C/(2*DF)
X=np.arange(512); PULSES=16; NOISE=.15
METHODS=('pulse','two_close','chirp','chirp_resonance','echo_resonance','energy_flash')
LAGS=np.arange(-48,49)

def waveform(offset,chirp=False):
    sigma=12. if chirp else 1.5
    env=np.exp(-.5*(offset/sigma)**2)
    if chirp:
        slope=10e6/(6*sigma/FS)
        env=env*np.exp(1j*np.pi*slope*(offset/FS)**2)
    return env/np.sqrt(np.sum(abs(env)**2))

TEMPLATES={kind:waveform(LAGS,kind=='chirp') for kind in ('pulse','chirp')}
RL=np.arange(-32,33)
RESONATOR=np.exp(-abs(RL)/8)*np.exp(2j*np.pi*1e6*RL/FS)
RESONATOR/=np.linalg.norm(RESONATOR)
# Passive resonant target: causal response, transfer magnitude <= 1.
ECHO_KERNEL=np.where(RL>=0,np.exp(-np.maximum(RL,0)/8)*np.exp(2j*np.pi*1e6*RL/FS),0.)
ECHO_KERNEL/=np.sum(abs(ECHO_KERNEL))
TEMPLATES['echo']=np.convolve(TEMPLATES['chirp'],ECHO_KERNEL,'same')
ECHO_TEMPLATE_ENERGY=float(np.sum(abs(TEMPLATES['echo'])**2))
# Engineered emitter: equal returned energy, narrower response, known latency.
TEMPLATES['flash']=np.exp(-.5*(LAGS/.5)**2)
TEMPLATES['flash']/=np.linalg.norm(TEMPLATES['flash'])
FLASH_DELAY_SAMPLES=12

def correlate(data,kind,resonance=False):
    if resonance:
        data=np.array([np.convolve(row,RESONATOR,'same') for row in data])
    h=np.conj(TEMPLATES[kind][::-1])
    output=np.array([np.convolve(row,h,'same') for row in data])
    if kind=='echo':
        output/=np.sqrt(ECHO_TEMPLATE_ENERGY)
    return output

def evaluate(seed,case):
    rng=np.random.default_rng(seed)
    distance=float(rng.uniform(1100,1300)); center=2*distance/C*FS
    amp={'empty':0.,'strong':1.6,'weak':.35,'impulse':.35,'phase_offset':1.6}[case]
    phase=rng.uniform(-np.pi,np.pi)
    n1=NOISE*(rng.normal(size=(PULSES,512))+1j*rng.normal(size=(PULSES,512)))
    n2=NOISE*(rng.normal(size=(PULSES,512))+1j*rng.normal(size=(PULSES,512)))
    if case=='impulse':
        loc=rng.integers(80,430)
        n1[:,loc]+=1.5*np.exp(1j*rng.uniform(-np.pi,np.pi,PULSES))
        n2[:,loc]+=1.5*np.exp(1j*rng.uniform(-np.pi,np.pi,PULSES))
    pulse=amp*waveform(X-center)*np.exp(1j*phase)
    chirp=amp*waveform(X-center,True)*np.exp(1j*phase)
    resonant_echo=np.convolve(chirp,ECHO_KERNEL,'same')
    flash=np.exp(-.5*((X-center-FLASH_DELAY_SAMPLES)/.5)**2)
    flash=amp*flash/np.linalg.norm(flash)*np.exp(1j*phase)
    # Common scattering phase; deliberately violate it in phase_offset scenario.
    difference=4*np.pi*DF*distance/C+(.7 if case=='phase_offset' else 0.)
    a=correlate(pulse[None,:]/np.sqrt(2)+n1,'pulse')
    b=correlate(pulse[None,:]*np.exp(-1j*difference)/np.sqrt(2)+n2,'pulse')
    outputs={'pulse':np.mean(abs(correlate(pulse[None,:]+n1,'pulse'))**2,axis=0),
             'two_close':np.mean(abs(a)**2+abs(b)**2,axis=0),
             'chirp':np.mean(abs(correlate(chirp[None,:]+n1,'chirp'))**2,axis=0),
             'chirp_resonance':np.mean(abs(correlate(chirp[None,:]+n1,'chirp',True))**2,axis=0),
             'echo_resonance':np.mean(abs(correlate(resonant_echo[None,:]+n1,'echo'))**2,axis=0),
             'energy_flash':np.mean(abs(correlate(flash[None,:]+n1,'flash'))**2,axis=0)}
    result={}
    # Same search region for every method; no true-range-dependent gate.
    for method,p in outputs.items():
        k=int(np.argmax(p[64:448]))+64
        floor=float(np.median(p[64:448]))
        score=float(p[k]/floor)
        r=float(k*C/(2*FS))
        if method=='energy_flash':
            r-=FLASH_DELAY_SAMPLES*C/(2*FS)
        if method=='two_close':
            beat_phase=np.angle(np.sum(a[:,k]*np.conj(b[:,k])))
            remainder=(beat_phase/(2*np.pi)*PERIOD)%PERIOD
            r=float(remainder+round((r-remainder)/PERIOD)*PERIOD)
        result[method]=dict(score=score,range_m=r)
    return distance,result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reflection',action='store_true')
    parser.add_argument('--flash',action='store_true')
    args=parser.parse_args()
    dest=ROOT/('wave_flash_results.json' if args.flash else 'wave_reflection_results.json' if args.reflection else 'wave_methods_results.json')
    if dest.exists():
        raise SystemExit('Existing results preserved')
    calibration=[evaluate(44000000+s,'empty')[1] for s in range(300)]
    thresholds={m:float(np.quantile([r[m]['score'] for r in calibration],.99,method='higher')) for m in METHODS}
    rows=[]
    for ci,case in enumerate(('empty','strong','weak','impulse','phase_offset')):
        count=200 if case=='empty' else 100
        for seed in range(count):
            distance,result=evaluate(45000000+ci*1000+seed,case)
            for m,out in result.items():
                out['detected']=bool(out['score']>thresholds[m])
                out['correct']=bool(out['detected'] and abs(out['range_m']-distance)<7.5)
            rows.append(dict(case=case,seed=seed,truth_m=distance,results=result))
    summary={}
    for case in ('empty','strong','weak','impulse','phase_offset'):
        rr=[r for r in rows if r['case']==case]
        summary[case]={}
        for m in METHODS:
            errors=[abs(r['results'][m]['range_m']-r['truth_m']) for r in rr if r['results'][m]['correct']]
            summary[case][m]=dict(total=len(rr),detections=sum(r['results'][m]['detected'] for r in rr),
                correct=sum(r['results'][m]['correct'] for r in rr) if case!='empty' else None,
                mae_correct_m=float(np.mean(errors)) if errors and case!='empty' else None)
    with dest.open('x',encoding='utf-8') as f:
        json.dump(dict(thresholds=thresholds,summary=summary,runs=rows),f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
