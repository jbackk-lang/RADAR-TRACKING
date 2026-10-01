import hashlib
import json
from pathlib import Path
import numpy as np
from .run_signal import evaluate

ROOT=Path(__file__).resolve().parent

def reconstruct(bands):
    a=np.asarray(bands,dtype=float)
    if a.ndim!=2 or not np.isfinite(a).all(): raise ValueError('Finite samples x bands required')
    return np.sqrt(np.sum(np.maximum(a,0.)**2,axis=1))

def main():
    out=ROOT/'band_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    previous=json.loads((ROOT/'signal_results/summary.json').read_text())
    rows=[]
    for old in previous['runs']:
        if old['source']!='Open Radar': continue
        path=Path(old['input_path'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==old['input_sha256']
        with np.load(path,allow_pickle=False) as z:
            power=np.abs(z['spec'].astype(complex))**2
            t=(z['ts']-z['ts'][0])/1000.
            freq=(np.arange(power.shape[1])-power.shape[1]//2)*float(z['prf'])/power.shape[1]
        edges=np.linspace(0,power.shape[1],5,dtype=int)
        amplitudes=np.column_stack([np.sqrt(power[:,edges[k]:edges[k+1]].sum(1)) for k in range(4)])
        full=np.sqrt(power.sum(1))
        np.testing.assert_allclose(reconstruct(amplitudes),full,rtol=1e-12)
        forecasts=[]; bases=[]; details=[]
        for k in range(4):
            metrics,p,b,states=evaluate(t,amplitudes[:,k],(.1,4.),(-.02,.02))
            forecasts.append(p); bases.append(b)
            details.append({'band':k,'bin_start':int(edges[k]),'bin_stop_exclusive':int(edges[k+1]),
              'first_bin_hz':float(freq[edges[k]]),'last_bin_hz':float(freq[edges[k+1]-1]),**metrics})
            print(old['name'],'band',k,'clock',metrics['clock_fraction'],flush=True)
        p=reconstruct(np.column_stack(forecasts)); b=reconstruct(np.column_stack(bases))
        with np.load(ROOT/'signal_results'/(old['name']+'.npz')) as z:
            np.testing.assert_allclose(z['observed'],full[100:],rtol=1e-12)
            full_pred=z['prediction'].copy(); full_base=z['baseline'].copy()
        truth=full[100:]; variance=max(float(np.var(truth)),1e-12)
        models={'full_clock':full_pred,'full_mean12':full_base,'bands_clock':p,'bands_mean12':b}
        row={'name':old['name'],'input_sha256':old['input_sha256'],'input_path':str(path),
             'scored_samples':len(truth),'bands':details,
             'nmse':{m:float(np.mean((x-truth)**2)/variance) for m,x in models.items()}}
        rows.append(row)
        np.savez_compressed(out/(old['name']+'.npz'),observed=truth,**models)
        print(row['name'],row['nmse'],flush=True)
    result={'protocol_sha256':hashlib.sha256((ROOT/'BANDS_PROTOCOL.md').read_bytes()).hexdigest(),
            'scope':'Fixed-band real-radar amplitude forecast, not spin or position validation','runs':rows}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

if __name__=='__main__': main()
