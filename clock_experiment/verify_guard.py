import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'guard_results'; r=json.loads((out/'summary.json').read_text())
    assert len(r['runs'])==360 and len(r['validations'])==120
    assert hashlib.sha256((ROOT/'GUARD_PROTOCOL.md').read_bytes()).hexdigest()==r['protocol_sha256']
    margins={'range_m':3.75,'bearing_rad':.004,'radial_velocity_m_s':.05}
    truth={'range_m':1500.,'bearing_rad':.35,'radial_velocity_m_s':0.}
    for seed in range(10):
        streak=dict.fromkeys(margins,0)
        for v in [x for x in r['validations'] if x['seed']==seed]:
            for key in margins:
                a=v['raw'][key]-truth[key]; b=v['corrected'][key]-truth[key]
                if key=='bearing_rad': a=np.angle(np.exp(1j*a)); b=np.angle(np.exp(1j*b))
                ok=v['quality_ok'] and abs(a)-abs(b)>margins[key]
                streak[key]=streak[key]+1 if ok else 0
                assert v['enabled'][key]==(streak[key]>=2)
    for group,s in r['summary_mae'].items():
        rows=[x for x in r['runs'] if group=='ALL' or x['step']==int(group)]
        for mode,values in s.items():
            for key,value in values.items():
                assert abs(np.mean([abs(x[mode][key]-x['truth'][key]) for x in rows])-value)<1e-12
    result={'target_measurements_verified':360,'reference_decisions_verified':120,'protocol_hash_verified':True}
    (out/'verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

if __name__=='__main__': main()
