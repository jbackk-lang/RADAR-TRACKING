import hashlib,json,time
from pathlib import Path
import numpy as np
from .online_calibration import OnlineCalibration
from .radar_compensation import simulate,estimate
from .reference_calibration import apply_calibration

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'online_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    source=ROOT/'guard_results/summary.json'; old=json.loads(source.read_text())
    rows=[]; decisions=[]; timings={'memory':0.,'online':0.}
    for seed in range(10):
        refs=[v for v in old['validations'] if v['seed']==seed]
        models={name:OnlineCalibration(refs[0]['calibration'],adapt=name=='online') for name in timings}
        for v in refs:
            chosen={}
            for name,model in models.items():
                start=time.perf_counter(); chosen[name],d=model.observe(v['step'],v['raw'],v['quality_ok'])
                timings[name]+=time.perf_counter()-start
                decisions.append({'seed':seed,'step':v['step'],'mode':name,'selected':chosen[name],**d})
            for target,(distance,bearing,speed) in enumerate([(600.,-.4,0.),(1200.,.1,0.),(1800.,.6,2.)]):
                prior=next(r for r in old['runs'] if r['seed']==seed and r['step']==v['step'] and r['target']==target)
                iq,p,_=simulate(90000+seed*36+v['step']*3+target,range_m=distance,bearing=bearing,speed=speed,**v['state'])
                assert estimate(iq,**p)==prior['raw']
                row=dict(prior)
                for name,cal in chosen.items(): row[name]=apply_calibration(iq,p,cal)
                rows.append(row)
        print('seed',seed,'complete',flush=True)
    summary={}
    for group in ['ALL']+list(range(12)):
        rr=[r for r in rows if group=='ALL' or r['step']==group]
        summary[str(group)]={mode:{key:float(np.mean([abs(r[mode][key]-r['truth'][key]) for r in rr]))
                 for key in ('range_m','bearing_rad','radial_velocity_m_s')} for mode in ('raw','always','guarded','memory','online')}
    r={'protocol_sha256':hashlib.sha256((ROOT/'ONLINE_PROTOCOL.md').read_bytes()).hexdigest(),
       'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runs':rows,'decisions':decisions,
       'summary_mae':summary,'controller_seconds':timings,'additional_observations':0}
    (out/'summary.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
    print(json.dumps(summary['ALL'],indent=2)); print('controller_seconds',timings)

if __name__=='__main__': main()
