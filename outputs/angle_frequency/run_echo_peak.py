"""Echo-sounder style delay peak; paired phase reversal experiment."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
C = 299792458.
FS = 20e6
X = np.arange(512)
KERNEL = np.exp(-.5*(np.arange(-6, 7)/1.5)**2)
KERNEL /= np.linalg.norm(KERNEL)

def power(iq, matched=False):
    if matched:
        iq = np.array([np.convolve(row, KERNEL[::-1].conj(), 'same') for row in iq])
    return np.mean(abs(iq)**2, axis=0)

def measure(p, truth_bin):
    k = int(np.argmax(p))
    floor = float(np.mean(p[abs(X-truth_bin)>15]))
    local = float(np.max(p[abs(X-truth_bin)<5]))
    return dict(range_m=float(k*C/(2*FS)), noise_power=floor,
                peak_to_noise_db=float(10*np.log10(local/floor)),
                detected=bool(abs(k-truth_bin)<=3))

def main():
    dest = ROOT/'echo_peak_results.json'
    if dest.exists():
        raise SystemExit('Existing results preserved')
    rows=[]
    for case, amplitude in [('strong',1.), ('weak',.08), ('empty',0.)]:
        for seed in range(100):
            rng=np.random.default_rng(42000000+seed)
            distance=float(rng.uniform(1100,1300)); center=2*distance/C*FS
            signal=amplitude*np.exp(-.5*((X-center)/1.5)**2)*np.exp(1j*rng.uniform(-np.pi,np.pi))
            noise=.15*(rng.normal(size=(64,512))+1j*rng.normal(size=(64,512)))
            iq=signal[None,:]+noise
            inputs={'raw':iq, 'phase_180_all':-iq,
                    'phase_180_echo_only':-signal[None,:]+noise,
                    'subtract_own_inverted_copy':iq-(-iq), 'matched':iq}
            results={name:measure(power(data,name=='matched'),center) for name,data in inputs.items()}
            assert np.array_equal(power(iq),power(-iq))
            assert np.allclose(power(iq-(-iq)),4*power(iq))
            rows.append(dict(case=case,seed=seed,truth_range_m=distance,results=results))
    summary={}
    for case in ('strong','weak','empty'):
        rr=[r for r in rows if r['case']==case]
        summary[case]={name:dict(range_mae_m=float(np.mean([abs(r['results'][name]['range_m']-r['truth_range_m']) for r in rr])) if case!='empty' else None,
                              noise_power=float(np.mean([r['results'][name]['noise_power'] for r in rr])),
                              peak_to_noise_db=float(np.mean([r['results'][name]['peak_to_noise_db'] for r in rr])),
                              peak_near_truth_count=sum(r['results'][name]['detected'] for r in rr)) for name in rr[0]['results']}
    dest.write_text(json.dumps(dict(summary=summary,runs=rows),indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
