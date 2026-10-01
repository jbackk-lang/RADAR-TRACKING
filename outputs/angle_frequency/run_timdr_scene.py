import hashlib
import argparse
import json
from pathlib import Path
import numpy as np
from run_scene_recognition import simulate,T
from timdr_scene_model import recognize_scene

ROOT=Path(__file__).resolve().parent

def extra_scene(seed,case):
    rng=np.random.default_rng(seed)
    if case=='crossing':
        a=np.column_stack([500+3*T,-6+2*T]);b=np.column_stack([502+3*T,6-2*T])
        va=np.tile([3.,2.],(len(T),1));vb=np.tile([3.,-2.],(len(T),1))
    else:
        a=np.column_stack([500+3*T,-3+.5*T]);b=np.column_stack([502+3*T,3+.5*T])
        b[6:,1]+=2*(T[6:]-T[6]);va=np.tile([3.,.5],(len(T),1));vb=va.copy();vb[6:,1]+=2
    positions=np.stack([a,b],axis=1);velocities=np.stack([va,vb],axis=1)
    d=np.sum(positions*velocities,axis=2)/np.linalg.norm(positions,axis=2)
    p=positions+rng.normal(0,.12,positions.shape);d+=rng.normal(0,.15,d.shape)
    swaps=rng.integers(0,2,len(T)).astype(bool);p[swaps]=p[swaps,::-1];d[swaps]=d[swaps,::-1]
    return p,d

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--stress',action='store_true');args=parser.parse_args()
    dest=ROOT/('timdr_scene_stress_results.json' if args.stress else 'timdr_scene_results.json')
    if dest.exists():raise SystemExit('Existing results preserved')
    labels={'rigid_large':'coherent_group_unresolved','rigid_rotating':'coherent_group_unresolved',
            'two_diverging':'separate_motion','two_parallel':'coherent_group_unresolved',
            'ghost_constant':'coherent_group_unresolved','ghost_inconsistent':'inconsistent_echo',
            'crossing':'separate_motion','independent_turn':'separate_motion'}
    rows=[];summary={}
    for ci,(case,label) in enumerate(labels.items()):
        for seed in range(100):
            input_seed=57000000+ci*1000+seed
            p,v=extra_scene(input_seed,case) if case in ('crossing','independent_turn') else simulate(input_seed,case)
            if args.stress:
                rng=np.random.default_rng(input_seed+10000000)
                p+=rng.normal(0,.6,p.shape);v+=rng.normal(0,.4,v.shape)
                if seed%2==0:
                    frame=int(rng.integers(2,10));point=int(rng.integers(0,2))
                    p[frame,point]+=rng.normal(0,3.,2)
            standard=recognize_scene(p,v,T,False);timdr=recognize_scene(p,v,T,True)
            rows.append(dict(case=case,seed=seed,expected_label=label,standard=standard,timdr=timdr))
        rr=[r for r in rows if r['case']==case]
        summary[case]={m:dict(correct_labels=sum(r[m]['label']==label for r in rr),count_returned=sum(r[m]['count'] is not None for r in rr)) for m in ('standard','timdr')}
        summary[case]['association_sequences_different']=sum([x['swapped'] for x in r['standard']['association']]!=[x['swapped'] for x in r['timdr']['association']] for r in rr)
    diffs=np.array([float(r['timdr']['label']==r['expected_label'])-float(r['standard']['label']==r['expected_label']) for r in rows])
    rng=np.random.default_rng(58000000)
    bootstrap=np.mean(diffs[rng.integers(0,len(rows),(2000,len(rows)))],axis=1)
    low,high=np.quantile(bootstrap,[.025,.975])
    comparison=dict(label_accuracy_standard=float(np.mean([r['standard']['label']==r['expected_label'] for r in rows])),
                    label_accuracy_timdr=float(np.mean([r['timdr']['label']==r['expected_label'] for r in rows])),
                    paired_difference=float(diffs.mean()),paired_bootstrap_95=[float(low),float(high)],
                    noninferiority_margin=.05,criterion_passed=bool(low>=-.05),
                    timdr_calls=sum(r['timdr']['timdr_calls'] for r in rows))
    hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('timdr_reference.py','timdr_scene_model.py','TIMDR_SCENE_PROTOCOL.md')}
    with dest.open('x',encoding='utf-8') as f:json.dump(dict(comparison=comparison,summary=summary,source_hashes=hashes,runs=rows),f,indent=2)
    print(json.dumps(dict(comparison=comparison,summary=summary),indent=2))

if __name__=='__main__':main()
