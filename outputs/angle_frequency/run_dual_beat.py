"""Analytic two-carrier beat phase plus sampled echo envelopes."""
import json
import argparse
from pathlib import Path
import numpy as np
from run_echo_peak import C, FS, X, KERNEL, power

ROOT=Path(__file__).resolve().parent
F1=77e9
F2=38.5e9
PERIOD_R=C/(2*abs(F1-F2))

def nearest_branch(coarse, phase):
    remainder=(phase/(2*np.pi)*PERIOD_R)%PERIOD_R
    return float(remainder+round((coarse-remainder)/PERIOD_R)*PERIOD_R)

def main():
    global F2, PERIOD_R
    parser=argparse.ArgumentParser()
    parser.add_argument('--half-beat',action='store_true')
    args=parser.parse_args()
    if args.half_beat:
        F2=57.75e9
        PERIOD_R=C/(2*abs(F1-F2))
    dest=ROOT/('dual_half_beat_results.json' if args.half_beat else 'dual_beat_results.json')
    if dest.exists():
        raise SystemExit('Existing results preserved')
    rows=[]
    for case,amp,phase_offset in [('strong',1.,0.),('weak',.08,0.),('channel_phase',1.,.7)]:
        for seed in range(100):
            rng=np.random.default_rng(43000000+seed)
            distance=float(rng.uniform(1100,1300)); center=2*distance/C*FS
            envelope=np.exp(-.5*((X-center)/1.5)**2)
            n1=.15*(rng.normal(size=(64,512))+1j*rng.normal(size=(64,512)))
            n2=.15*(rng.normal(size=(64,512))+1j*rng.normal(size=(64,512)))
            scatter=rng.uniform(-np.pi,np.pi)
            s1=amp*envelope*np.exp(1j*(4*np.pi*F1*distance/C+scatter))
            s2=amp*envelope*np.exp(1j*(4*np.pi*F2*distance/C+scatter+phase_offset))
            single=s1[None,:]+n1
            a=s1[None,:]/np.sqrt(2)+n1
            b=s2[None,:]/np.sqrt(2)+n2
            ps=power(single,True)
            pd=power(a,True)+power(b,True)
            ks=int(np.argmax(ps)); kd=int(np.argmax(pd))
            coarse=kd*C/(2*FS)
            # Two separately downconverted channels; never sample 38.5 GHz at 20 MHz.
            za=np.array([np.convolve(row,KERNEL,'same')[kd] for row in a])
            zb=np.array([np.convolve(row,KERNEL,'same')[kd] for row in b])
            phase=float(np.angle(np.sum(za*np.conj(zb))))
            refined=nearest_branch(coarse,phase)
            exact_phase=float(np.angle(np.exp(1j*4*np.pi*(F1-F2)*distance/C)))
            # Even noiseless beat phase needs the correct integer branch.
            ideal=nearest_branch(coarse,exact_phase)
            assert abs(refined-coarse)<=PERIOD_R/2+1e-9
            assert abs(np.exp(1j*4*np.pi*(F1-F2)*distance/C)-np.exp(1j*4*np.pi*(F1-F2)*(distance+PERIOD_R)/C))<1e-6
            rows.append(dict(case=case,seed=seed,truth_m=distance,single_m=ks*C/(2*FS),dual_m=coarse,
                             beat_m=refined,ideal_phase_m=ideal,correct_integer_branch=abs(ideal-distance)<1e-6))
    summary={}
    for case in ('strong','weak','channel_phase'):
        rr=[r for r in rows if r['case']==case]
        summary[case]={name:float(np.mean([abs(r[name]-r['truth_m']) for r in rr])) for name in ('single_m','dual_m','beat_m','ideal_phase_m')}
        summary[case]['correct_integer_branch_count']=sum(r['correct_integer_branch'] for r in rr)
    result=dict(carriers_hz=[F1,F2],beat_hz=abs(F1-F2),range_ambiguity_m=PERIOD_R,
                beat_period_s=1/abs(F1-F2),sample_interval_s=1/FS,summary=summary,runs=rows)
    with dest.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))

if __name__=='__main__':
    main()
