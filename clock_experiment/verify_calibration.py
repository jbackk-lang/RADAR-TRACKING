import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'calibration_results'; r=json.loads((out/'summary.json').read_text())
    assert len(r['runs'])==600 and len(r['calibrations'])==200
    assert hashlib.sha256((ROOT/'CALIBRATION_PROTOCOL.md').read_bytes()).hexdigest()==r['protocol_sha256']
    checked=0
    for si,summary in enumerate(r['summary']):
        rows=[x for x in r['runs'] if x['scenario']==si]; assert len(rows)==30
        for key,metrics in summary['metrics'].items():
            a=np.array([abs(x['raw'][key]-x['truth'][key]) for x in rows])
            b=np.array([abs(x['corrected'][key]-x['truth'][key]) for x in rows])
            assert np.isfinite(a).all() and np.isfinite(b).all()
            assert abs(a.mean()-metrics['raw_mae'])<1e-12
            assert abs(b.mean()-metrics['corrected_mae'])<1e-12
            assert int(np.sum(b<a))==metrics['better']
            assert int(np.sum(b>a))==metrics['worse']; checked+=1
    result={'runs':600,'calibrations':200,'metric_groups_verified':checked,'protocol_hash_matches':True}
    (out/'verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))

if __name__=='__main__': main()
