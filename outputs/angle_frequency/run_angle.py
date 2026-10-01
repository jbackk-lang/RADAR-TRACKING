import hashlib
import json
from pathlib import Path
import numpy as np
from angle_model import C,D,F0,METHODS,estimate,simulate

ROOT=Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    destination=ROOT/'results.json'
    if destination.exists():
        raise SystemExit('Existing results preserved')
    rows=[]; summary={}
    scenarios={'clean':(0.,0.),'constant_phase':(.15,0.),'channel_delay':(.15,.2e-12)}
    for bandwidth in (1e9,4e9):
        summary[str(bandwidth)]={}
        for scenario,(offset,delay) in scenarios.items():
            current=[]
            for angle_index,theta in enumerate((-.6,-.4,-.2,0.,.2,.4,.6)):
                for seed in range(200):
                    # Shared noise across scenarios and bandwidths; isolated target.
                    f,iq=simulate(9000000+angle_index*1000+seed,theta,bandwidth,offset,delay)
                    estimated=estimate(f,iq)
                    row=dict(bandwidth_hz=bandwidth,scenario=scenario,theta=theta,seed=seed,estimated=estimated,
                             errors={m:abs(v['angle_rad']-theta) if v['angle_rad'] is not None else None for m,v in estimated.items()})
                    current.append(row); rows.append(row)
            metrics={}
            for method in METHODS:
                valid=[r['errors'][method] for r in current if r['errors'][method] is not None]
                metrics[method]=dict(mae_rad=float(np.mean(valid)),mae_deg=float(np.rad2deg(np.mean(valid))),
                                     p95_rad=float(np.quantile(valid,.95)),p95_deg=float(np.rad2deg(np.quantile(valid,.95))),
                                     invalid=len(current)-len(valid),cases=len(current))
            summary[str(bandwidth)][scenario]=metrics
            print(bandwidth,scenario,json.dumps({m:round(v['mae_deg'],4) for m,v in metrics.items()}),flush=True)
    sources=[ROOT/'PROTOCOL.md',ROOT/'angle_model.py',ROOT/'run_angle.py',ROOT/'test_angle_model.py']
    result=dict(summary=summary,runs=rows,hashes={p.name:digest(p) for p in sources},
                spacing_m=D,center_frequency_hz=F0,frequency_count=17,snapshots_per_frequency=64,
                cases=len(rows),scope='New synthetic two-receiver frequency-resolved data, not old measurements')
    with destination.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)

if __name__=='__main__':
    main()
