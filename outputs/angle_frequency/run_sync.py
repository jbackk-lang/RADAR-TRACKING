import json
import numpy as np
from run_angle import ROOT,digest
from sync_calibration import simulate,calibrate,read_angle

def main():
    path=ROOT/'sync_results.json'
    if path.exists() or (ROOT/'sync_parameters.json').exists():
        raise SystemExit('Existing calibration or results preserved')
    parameters=[]
    for seed in range(10):
        delay=.002 if seed%2==0 else -.002
        zero=np.deg2rad(.12 if seed%2==0 else -.08)
        refs=[simulate(23000000+seed*10+i,1.2,turns,delay,zero) for i,turns in enumerate((.5,.5,1.,1.,1.5,1.5))]
        fitted=calibrate(refs,[1.2]*6)
        bad=calibrate(refs,[1.2+np.deg2rad(.4)]*6)
        try:
            calibrate(refs[2:4]*2,[1.2]*4)
        except ValueError:
            refused=True
        else:
            refused=False
        assert refused
        parameters.append(dict(seed=seed,truth_delay=delay,truth_zero=float(zero),fitted=fitted,
                               wrong_reference_fit=bad,same_speed_refused=refused))
    with (ROOT/'sync_parameters.json').open('x',encoding='utf-8') as f:
        json.dump(parameters,f,indent=2)
    rows=[]
    for p in parameters:
        seed=p['seed']; cal=p['fitted']; bad=p['wrong_reference_fit']
        for variable in (False,True):
            for ti,theta in enumerate((.4,1.2,2.)):
                for wi,turns in enumerate((.65,1.25,1.8)):
                    data=simulate(24000000+seed*100+int(variable)*30+ti*3+wi,theta,turns,p['truth_delay'],p['truth_zero'],variable)
                    raw=read_angle(data)
                    values=dict(raw=raw,angle_only=raw-cal['angle_only_rad'],
                                joint_sync=read_angle(data,cal['delay_s'],cal['zero_rad']),
                                wrong_reference=read_angle(data,bad['delay_s'],bad['zero_rad']))
                    rows.append(dict(seed=seed,theta=theta,turns=turns,variable=variable,
                                     angles=values,errors_deg={m:float(np.rad2deg(abs(v-theta))) for m,v in values.items()}))
    summary={}
    for variable in (False,True):
        rr=[r for r in rows if r['variable']==variable]
        summary['variable' if variable else 'constant']={m:dict(mae_deg=float(np.mean([r['errors_deg'][m] for r in rr])),
                                                             p95_deg=float(np.quantile([r['errors_deg'][m] for r in rr],.95))) for m in rows[0]['angles']}
    result=dict(parameters_sha256=digest(ROOT/'sync_parameters.json'),summary=summary,runs=rows,
                reference_observations=60,target_observations=180,
                delay_mae_ms=float(np.mean([abs(p['fitted']['delay_s']-p['truth_delay'])*1000 for p in parameters])),
                zero_mae_deg=float(np.mean([np.rad2deg(abs(p['fitted']['zero_rad']-p['truth_zero'])) for p in parameters])),
                hashes={p.name:digest(p) for p in (ROOT/'SYNC_PROTOCOL.md',ROOT/'sync_calibration.py',ROOT/'run_sync.py')})
    with path.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k not in ('runs','hashes')},indent=2))

if __name__=='__main__':
    main()
