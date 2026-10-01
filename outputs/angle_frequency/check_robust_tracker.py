import json
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import linear_sum_assignment
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from web_demo import build_demo,SCENES


def assess(demo):
    errors=[];missing=0;total=0;switches=0;last={}
    for f in demo['frames']:
        truth=f['truth'];tracks=f['tracks'];total+=len(truth)
        if not tracks:missing+=len(truth);continue
        a=np.array([[p['x'],p['y']] for p in truth]);b=np.array([[p['x'],p['y']] for p in tracks])
        distance=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2)
        ii,jj=linear_sum_assignment(distance);assigned={}
        for i,j in zip(ii,jj):
            if distance[i,j]<=2.:
                errors.append(float(distance[i,j]));assigned[truth[i]['id']]=tracks[j]['id']
                if truth[i]['id'] in last and last[truth[i]['id']]!=tracks[j]['id']:switches+=1
        last=assigned;missing+=len(truth)-len(assigned)
    return dict(mae_matched_m=float(np.mean(errors)),miss_rate=missing/total,id_switches=switches,
                track_ids=len({p['id'] for f in demo['frames'] for p in f['tracks']}))


def main():
    dest=ROOT/'robust_tracker_results.json'
    if dest.exists():raise SystemExit('Existing results preserved')
    rows=[]
    for ci,scene in enumerate(SCENES):
        for seed in range(25):
            input_seed=61000000+ci*1000+seed
            rows.append(dict(scene=scene,seed=seed,legacy=assess(build_demo('timdr',scene,4,input_seed)),
                             robust=assess(build_demo('robust',scene,4,input_seed))))
    summary={}
    for method in ('legacy','robust'):
        summary[method]={key:float(np.mean([r[method][key] for r in rows])) for key in ('mae_matched_m','miss_rate','id_switches','track_ids')}
    passed=summary['robust']['mae_matched_m']<=1.1*summary['legacy']['mae_matched_m'] and summary['robust']['miss_rate']<=summary['legacy']['miss_rate']+.05 and summary['robust']['id_switches']<=summary['legacy']['id_switches']*1.1+.1
    with dest.open('x',encoding='utf-8') as f:json.dump(dict(summary=summary,criteria_passed=passed,runs=rows),f,separators=(',',':'))
    print(json.dumps(dict(summary=summary,criteria_passed=passed),indent=2))

if __name__=='__main__':main()
