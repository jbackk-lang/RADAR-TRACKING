import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from core.timdr_change import timdr_change
from core.timdr_robust import timdr_change_robust


def trajectory(t,case):
    if case in ('straight','outlier'):return np.column_stack([3*t,np.zeros(len(t))])
    if case=='curve':return np.column_stack([6*np.sin(.5*t),6*(1-np.cos(.5*t))])
    if case=='acceleration':return np.column_stack([3*t+.7*t*t,np.zeros(len(t))])
    if case=='sharp_turn':return np.column_stack([3*np.minimum(t,2.5),3*np.maximum(0,t-2.5)])
    if case=='reversal':return np.column_stack([3*np.where(t<=2.5,t,5-t),np.zeros(len(t))])
    raise ValueError(case)


def main():
    dest=ROOT/'timdr_robust_results.json'
    if dest.exists():raise SystemExit('Existing results preserved')
    samplings={'dt025':np.arange(0,5.001,.25),'dt05':np.arange(0,5.001,.5),'dt1':np.arange(0,5.001,1.),
               'irregular':np.array([0,.4,.7,1.3,1.8,2.6,3.1,3.8,4.2,5.])}
    cases=('straight','outlier','curve','acceleration','sharp_turn','reversal')
    rows=[];summary={}
    for noise_index,sigma in enumerate((.12,.6)):
        for ci,case in enumerate(cases):
            for si,(sampling,t) in enumerate(samplings.items()):
                for seed in range(100):
                    rng=np.random.default_rng(60000000+noise_index*100000+ci*10000+si*1000+seed)
                    xy=trajectory(t,case)+rng.normal(0,sigma,(len(t),2))
                    if case=='outlier':xy[len(t)//2]+=rng.normal(0,3,2)
                    history=[dict(x=float(p[0]),y=float(p[1]),t=float(ti)) for p,ti in zip(xy,t)]
                    rows.append(dict(sigma=sigma,case=case,sampling=sampling,seed=seed,
                                     legacy=timdr_change(history),robust=timdr_change_robust(history,sigma)))
        rr=[r for r in rows if r['sigma']==sigma];summary[str(sigma)]={}
        for case in cases:
            cc=[r for r in rr if r['case']==case]
            summary[str(sigma)][case]={method:float(np.mean([r[method]['TIMDR']>.5 for r in cc])) for method in ('legacy','robust')}
        null=[r for r in rr if r['case'] in ('straight','outlier')]
        manoeuvres=[r for r in rr if r['case'] not in ('straight','outlier')]
        summary[str(sigma)]['overall']={method:dict(false_alarm=float(np.mean([r[method]['TIMDR']>.5 for r in null])),
            detection=float(np.mean([r[method]['TIMDR']>.5 for r in manoeuvres]))) for method in ('legacy','robust')}
    variation={}
    for method in ('legacy','robust'):
        values=[]
        for case in cases[2:]:
            scores=[]
            for t in samplings.values():
                history=[dict(x=float(p[0]),y=float(p[1]),t=float(ti)) for p,ti in zip(trajectory(t,case),t)]
                scores.append((timdr_change(history) if method=='legacy' else timdr_change_robust(history,.12))['TIMDR'])
            values.append(float(np.ptp(scores)))
        variation[method]=float(np.median(values))
    passed=all(s['overall']['robust']['false_alarm']<=s['overall']['legacy']['false_alarm'] and
               s['overall']['robust']['detection']>=s['overall']['legacy']['detection']-.05 for s in summary.values()) and variation['robust']<=variation['legacy']
    result=dict(summary=summary,noiseless_sampling_variation=variation,criteria_passed=passed,runs=rows)
    with dest.open('x',encoding='utf-8') as f:json.dump(result,f,separators=(',',':'))
    print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))

if __name__=='__main__':main()
