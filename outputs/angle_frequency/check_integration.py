import json
import sys
from pathlib import Path
import numpy as np
from run_angle import ROOT,digest
from rotation_model import BEAMWIDTH,OMEGA,estimate as angle_estimate,simulate as scan_simulate,pointing

sys.path.insert(0,str(ROOT.parent/'minimal_intervention'))
from clock_experiment.radar_compensation import simulate,estimate
from clock_experiment.reference_calibration import calibrate,apply_calibration

def main():
    destination=ROOT/'integration_results.json'
    if destination.exists():
        raise SystemExit('Existing results preserved')
    rows=[]
    conditions={'single':(0.,0.),'clock_0.1ms':(.0001,0.),'clock_2ms':(.002,0.),
                'pair_0.75deg':(0.,np.deg2rad(.75)),'pair_3deg':(0.,np.deg2rad(3.))}
    for seed in range(10):
        x,p,_=simulate(12000000+seed,range_m=900,bearing=-.2)
        cal=calibrate(x,p,900,-.2)
        for ai,theta in enumerate((.4,1.2,2.)):
            x,p,_=simulate(13000000+seed*3+ai,range_m=1500,bearing=theta,speed=2.)
            before=apply_calibration(x,p,cal)
            measured_range=estimate(x,**p)['range_m']
            scan_seed=14000000+ai*1000+seed
            for condition,(offset,separation) in conditions.items():
                data=scan_simulate(scan_seed,theta,variation=.05,clock_offset=offset)
                data['measured_range_m']=measured_range
                if separation:
                    # Independent return powers: no coherent multipath simulation.
                    rng=np.random.default_rng(scan_seed)
                    phase=float(rng.uniform(-np.pi,np.pi))
                    t=data['encoder_time']
                    power2=np.exp(-4*np.log(2)*((pointing(t,.05,phase)-(theta+separation))/BEAMWIDTH)**2)
                    data['iq']=np.sqrt(abs(data['iq'])**2+power2).astype(complex)
                angle=angle_estimate(data)['encoder_centroid']
                acquisition={**p,'bearing':angle}
                corrected=apply_calibration(x,acquisition,{**cal,'bearing_bias':0.})
                assert corrected['range_m']==before['range_m']
                assert corrected['radial_velocity_m_s']==before['radial_velocity_m_s']
                assert np.isclose(corrected['bearing_rad'],angle,rtol=0,atol=1e-12)
                rows.append(dict(seed=seed,theta=theta,condition=condition,estimated_angle=angle,
                                 angle_error_deg=float(np.rad2deg(abs(angle-theta))),
                                 range_m=corrected['range_m'],velocity_m_s=corrected['radial_velocity_m_s']))
    summary={}
    for condition in conditions:
        rr=[r for r in rows if r['condition']==condition]
        e=[r['angle_error_deg'] for r in rr]
        summary[condition]=dict(mae_deg=float(np.mean(e)),p95_deg=float(np.quantile(e,.95)),cases=len(rr))
    result=dict(summary=summary,runs=rows,range_velocity_invariance_checks=len(rows),
                hashes={p.name:digest(p) for p in (ROOT/'INTEGRATION_PROTOCOL.md',ROOT/'check_integration.py',ROOT/'rotation_model.py')})
    with destination.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    lines=['# Mały test połączenia kąta ze skanu z torem R/v','',
           '150 przypadków, 10 ziaren i 3 kąty. W torze pomiarowym zastąpiono wpisany kąt wynikiem enkoder+środek wiązki; wyłączono dodatkową korektę kąta. R i v są dokładnie zgodne z dotychczasowym torem dla tych samych I/Q (150 sprawdzeń). Błąd pomiaru R uwzględniono przy wyrównaniu czasu przelotu.','',
           '| Warunki | MAE kąta [°] | P95 [°] |','|---|---:|---:|']
    for name,v in summary.items():
        lines.append(f"| {name} | {v['mae_deg']:.4f} | {v['p95_deg']:.4f} |")
    lines+=['','Dwa cele są równie silne i nierozdzielone w R/v. Estymator zwraca jeden kąt: środek wspólnej wiązki może leżeć między celami. To błąd względem pierwszego celu, nie miara poprawnego rozdzielenia dwóch celów. Sumowano moce, bez pełnego modelu interferencji.','',
            'Wniosek: pomiar ze skanu można połączyć z obecnym torem bez zmiany R/v. Przy pojedynczym celu i synchronizacji daje mały błąd w tym modelu. Nie jest gotowym rozwiązaniem dla nierozdzielonych bliskich celów. Potrzebny jest osobny detektor i rozdzielanie wiązek; bez tego nie zastępować wszystkich kątów jednym środkiem.','',
            'To ograniczony test integracyjny modeli, bez pełnego skanu wielu komórek i walidacji sprzętowej. Stare pliki i wyniki pozostają zachowane. Odtwarzanie: python check_integration.py w świeżej kopii bez integration_results.json; wymagany sąsiedni katalog minimal_intervention.']
    (ROOT/'WYNIK_INTEGRACJI.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print('150 exact R/v invariance checks passed')

if __name__=='__main__':
    main()
