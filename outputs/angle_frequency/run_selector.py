import json
import numpy as np
from run_angle import ROOT,digest
from frequency_selector import FrequencySelector,generate

def main():
    selection=ROOT/'selector_thresholds.json'; results=ROOT/'selector_results.json'; iqpath=ROOT/'selector_iq.npz'
    if any(p.exists() for p in (selection,results,iqpath)):
        raise SystemExit('Existing thresholds or results preserved')
    model=FrequencySelector(); development=[]
    for seed in range(100):
        y,_=generate(21000000+seed,impulsive=seed%2==0)
        development.append(model.scores(y))
    thresholds={m:float(np.quantile([r[m]['score'] for r in development],.95)) for m in ('coherent','band_power')}
    frozen=dict(thresholds=thresholds,development=development,
                hashes={p.name:digest(p) for p in (ROOT/'SELECTOR_PROTOCOL.md',ROOT/'frequency_selector.py',ROOT/'run_selector.py')})
    with selection.open('x',encoding='utf-8') as f:
        json.dump(frozen,f,indent=2)
    print('Thresholds frozen',thresholds,flush=True)
    cases=[]
    for kind in ('strong_only','empty'):
        for seed in range(100):
            cases.append(dict(kind=kind,seed=seed,separation=.75,dr=0.))
    for separation in (.75,1.5):
        for dr in (0.,.02,.06):
            for seed in range(10):
                cases.append(dict(kind='weak',seed=seed,separation=separation,dr=dr))
    rows=[]; arrays={}
    for ci,case in enumerate(cases):
        y,truth=generate(22000000+ci,weak=case['kind']=='weak',empty=case['kind']=='empty',
                         separation=case['separation'],dr=case['dr'],impulsive=case['seed']%2==0)
        key=f'case_{ci}'; arrays[key]=y
        score=model.scores(y); outcomes={}
        for name,v in score.items():
            detected=v['score']>thresholds[name]
            localized=abs(np.rad2deg(v['angle']-truth['weak_angle']))<=.25 and abs(v['dr']-truth['dr'])<=.015
            outcomes[name]=dict(**v,detected=bool(detected),weak_correct=bool(detected and localized and case['kind']=='weak'))
        rows.append(dict(**case,truth=truth,iq_key=key,outcomes=outcomes))
    summary={}
    for kind in ('strong_only','empty','weak'):
        rr=[r for r in rows if r['kind']==kind]
        summary[kind]=dict(cases=len(rr),metrics={m:dict(detected=sum(r['outcomes'][m]['detected'] for r in rr),
                                                        weak_correct=sum(r['outcomes'][m]['weak_correct'] for r in rr)) for m in thresholds})
    summary['weak_by_range']={str(dr):{m:sum(r['outcomes'][m]['weak_correct'] for r in rows if r['kind']=='weak' and r['dr']==dr) for m in thresholds} for dr in (0.,.02,.06)}
    with iqpath.open('xb') as f:
        np.savez_compressed(f,**arrays)
    result=dict(summary=summary,runs=rows,thresholds_sha256=digest(selection),iq_sha256=digest(iqpath))
    with results.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
