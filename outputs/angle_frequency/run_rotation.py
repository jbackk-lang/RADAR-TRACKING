import json
import numpy as np
from run_angle import ROOT,digest
from rotation_model import METHODS,estimate,simulate

def main():
    destination=ROOT/'rotation_results.json'
    if destination.exists():
        raise SystemExit('Existing results preserved')
    rows=[]; summary={}
    for scenario,(variation,offset) in dict(constant_rotation=(0.,0.),variable_rotation=(.05,0.),clock_offset=(.05,.002)).items():
        current=[]
        for ai,theta in enumerate((.4,1.2,2.)):
            for seed in range(200):
                out=estimate(simulate(10000000+ai*1000+seed,theta,variation,offset))
                row=dict(scenario=scenario,theta=theta,seed=seed,estimated=out,errors={m:abs(v-theta) for m,v in out.items()})
                current.append(row); rows.append(row)
        summary[scenario]={}
        for method in METHODS:
            e=[r['errors'][method] for r in current]
            summary[scenario][method]=dict(mae_rad=float(np.mean(e)),mae_deg=float(np.rad2deg(np.mean(e))),
                                           p95_deg=float(np.rad2deg(np.quantile(e,.95))),cases=len(e))
        print(scenario,json.dumps(summary[scenario]),flush=True)
    sources=[ROOT/p for p in ('ROTATION_PROTOCOL.md','rotation_model.py','run_rotation.py','test_rotation_model.py','angle_model.py','run_angle.py')]
    result=dict(summary=summary,runs=rows,hashes={p.name:digest(p) for p in sources},cases=len(rows),scope='New synthetic rotating directional antenna, not old measurements')
    with destination.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)

if __name__=='__main__':
    main()
