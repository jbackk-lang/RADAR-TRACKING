import json
import numpy as np
from run_angle import ROOT,digest
from carrier_phase import CASES,TIMES,simulate,estimate

def main():
    path=ROOT/'carrier_results.json'; phasepath=ROOT/'carrier_phasors.npz'
    if path.exists() or phasepath.exists():
        raise SystemExit('Existing results preserved')
    rows=[]; arrays={}
    for ci,case in enumerate(CASES):
        for seed in range(20):
            input_seed=31000000+ci*100+seed
            iq,truth_v=simulate(input_seed,case)
            out,phasor=estimate(iq); key=f'{case}_{seed}'; arrays[key]=phasor
            rows.append(dict(case=case,seed=seed,input_seed=input_seed,truth_v=truth_v,truth_delta_m=float(truth_v*TIMES[-1]),
                             estimates=out,phasor_key=key))
    summary={}
    for case in CASES:
        rr=[r for r in rows if r['case']==case]
        summary[case]=dict(range_mae_m=float(np.mean([abs(r['estimates']['range_m']-1200) for r in rr])),
                           baseline_v_mae=float(np.mean([abs(r['estimates']['baseline_v']-r['truth_v']) for r in rr])),
                           carrier_v_mae=float(np.mean([abs(r['estimates']['carrier_v']-r['truth_v']) for r in rr])),
                           baseline_delta_mae_mm=float(np.mean([abs(r['estimates']['baseline_delta_m']-r['truth_delta_m'])*1000 for r in rr])),
                           carrier_delta_mae_mm=float(np.mean([abs(r['estimates']['carrier_delta_m']-r['truth_delta_m'])*1000 for r in rr])))
    with phasepath.open('xb') as f:
        np.savez_compressed(f,**arrays)
    result=dict(summary=summary,runs=rows,phasors_sha256=digest(phasepath),
                hashes={p.name:digest(p) for p in (ROOT/'CARRIER_PROTOCOL.md',ROOT/'carrier_phase.py',ROOT/'run_carrier.py')})
    with path.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
