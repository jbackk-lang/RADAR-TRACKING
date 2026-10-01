import json
import numpy as np
from run_angle import ROOT,digest
from stereo_model import CENTER,JointEstimator,simulate

def main():
    result_path=ROOT/'stereo_results.json'
    iq_path=ROOT/'stereo_iq.npz'
    if result_path.exists() or iq_path.exists():
        raise SystemExit('Existing results preserved')
    models={n:JointEstimator(n) for n in (1,2)}
    rows=[]; arrays={}
    cases=[]
    for separation in (.75,1.5,3.):
        for ratio in (.25,.5,1.,2.):
            for phase in (0.,np.pi/2,np.pi):
                for seed in range(5):
                    center=CENTER+np.deg2rad(.037)
                    truth=[center-np.deg2rad(separation/2),center+np.deg2rad(separation/2)]
                    cases.append(dict(kind='pair',separation_deg=separation,ratio=ratio,phase=phase,seed=seed,
                                      truth=truth,amplitudes=[1.,ratio*np.exp(1j*phase)]))
    for seed in range(20):
        cases.append(dict(kind='single',seed=seed,truth=[CENTER+np.deg2rad(.037)],amplitudes=[1.]))
    for case_id,case in enumerate(cases):
        outcomes={}
        for receivers in (1,2):
            signal=simulate(15000000+case_id,case['truth'],case['amplitudes'],receivers)
            key=f'case_{case_id}_rx_{receivers}'
            arrays[key]=signal
            out=models[receivers].fit(signal)
            out['iq_key']=key
            out['matched_mae_deg']=None
            out['resolved']=False
            if case['kind']=='pair' and out['count']==2:
                e=np.rad2deg(abs(np.array(out['angles'])-case['truth']))
                out['matched_mae_deg']=float(e.mean())
                out['resolved']=bool(np.all(e<=.25))
            outcomes[str(receivers)]=out
        rows.append({k:v for k,v in case.items() if k!='amplitudes'}|dict(case_id=case_id,outcomes=outcomes))
    summary={}
    for receivers in ('1','2'):
        pairs=[r for r in rows if r['kind']=='pair']
        single=[r for r in rows if r['kind']=='single']
        def group(rr):
            valid=[r['outcomes'][receivers]['matched_mae_deg'] for r in rr if r['outcomes'][receivers]['count']==2]
            return dict(cases=len(rr),two_selected=sum(r['outcomes'][receivers]['count']==2 for r in rr),
                        resolved=sum(r['outcomes'][receivers]['resolved'] for r in rr),
                        mae_when_two_selected_deg=float(np.mean(valid)) if valid else None)
        summary[receivers]=dict(all_pairs=group(pairs),
                               by_separation={str(s):group([r for r in pairs if r['separation_deg']==s]) for s in (.75,1.5,3.)},
                               by_ratio={str(s):group([r for r in pairs if r['ratio']==s]) for s in (.25,.5,1.,2.)},
                               false_split_single=sum(r['outcomes'][receivers]['count']==2 for r in single),single_cases=len(single))
    pairs=[r for r in rows if r['kind']=='pair']
    comparison=dict(only_two_rx_resolved=sum(r['outcomes']['2']['resolved'] and not r['outcomes']['1']['resolved'] for r in pairs),
                    only_one_rx_resolved=sum(r['outcomes']['1']['resolved'] and not r['outcomes']['2']['resolved'] for r in pairs))
    with iq_path.open('xb') as f:
        np.savez_compressed(f,**arrays)
    result=dict(summary=summary,comparison=comparison,runs=rows,iq_sha256=digest(iq_path),
                hashes={p.name:digest(p) for p in (ROOT/'STEREO_PROTOCOL.md',ROOT/'stereo_model.py',ROOT/'run_stereo.py',ROOT/'test_stereo_model.py')})
    with result_path.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(dict(summary=summary,comparison=comparison),indent=2))

if __name__=='__main__':
    main()
