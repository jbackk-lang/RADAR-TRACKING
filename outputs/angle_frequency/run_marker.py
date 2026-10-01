import json
import numpy as np
from run_angle import ROOT,digest
from sync_calibration import simulate,read_angle
from marker_sync import marker_samples,estimate_delay,calibrate_zero

def main():
    path=ROOT/'marker_results.json'; parameter_path=ROOT/'marker_parameters.json'
    if path.exists() or parameter_path.exists():
        raise SystemExit('Existing marker calibration/results preserved')
    parameters=[]
    for seed in range(10):
        true_delay=.002 if seed%2==0 else -.002
        echo,encoder=marker_samples(27000000+seed,true_delay)
        delay=estimate_delay(echo,encoder)
        refs=[simulate(28000000+seed*10+i,1.2,1.,true_delay,np.deg2rad(.12)) for i in range(6)]
        parameters.append(dict(seed=seed,truth_delay=true_delay,echo_marks=echo.tolist(),encoder_marks=encoder.tolist(),
                               calibration=calibrate_zero(refs,[1.2]*6,delay)))
    with parameter_path.open('x',encoding='utf-8') as f:
        json.dump(parameters,f,indent=2)
    rows=[]
    for p in parameters:
        for ci,condition in enumerate(('constant','variable','clock_change')):
            seed=p['seed']; cal=p['calibration']
            true_delay=p['truth_delay']+((.0005 if seed%2==0 else -.0005) if condition=='clock_change' else 0)
            for ti,theta in enumerate((.4,1.2,2.)):
                data=simulate(29000000+seed*100+ci*10+ti,theta,1.,true_delay,np.deg2rad(.12),condition!='constant')
                echo,encoder=marker_samples(30000000+seed*100+ci*10+ti,true_delay)
                delay=estimate_delay(echo,encoder)
                raw=read_angle(data)
                values=dict(raw=raw,angle_only=raw-cal['angle_only_rad'],
                            marker_frozen=read_angle(data,cal['delay_s'],cal['zero_rad']),
                            marker_current=read_angle(data,delay,cal['zero_rad']))
                rows.append(dict(seed=seed,condition=condition,theta=theta,echo_marks=echo.tolist(),encoder_marks=encoder.tolist(),
                                 delay_s=delay,truth_delay=true_delay,angles=values,
                                 errors_deg={m:float(np.rad2deg(abs(v-theta))) for m,v in values.items()}))
    summary={}
    for condition in ('constant','variable','clock_change'):
        rr=[r for r in rows if r['condition']==condition]
        summary[condition]={m:dict(mae_deg=float(np.mean([r['errors_deg'][m] for r in rr])),
                                  p95_deg=float(np.quantile([r['errors_deg'][m] for r in rr],.95))) for m in rows[0]['angles']}
    r=dict(summary=summary,runs=rows,parameters_sha256=digest(parameter_path),reference_observations=60,target_observations=90,
           marker_delay_mae_us=float(np.mean([abs(row['delay_s']-row['truth_delay'])*1e6 for row in rows])),
           hashes={p.name:digest(p) for p in (ROOT/'MARKER_PROTOCOL.md',ROOT/'marker_sync.py',ROOT/'run_marker.py',ROOT/'sync_calibration.py')})
    with path.open('x',encoding='utf-8') as f:
        json.dump(r,f,indent=2)
    print(json.dumps(summary,indent=2)); print('Delay MAE us',r['marker_delay_mae_us'])

if __name__=='__main__':
    main()
