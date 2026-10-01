import hashlib,json
from pathlib import Path
import numpy as np
from .radar_compensation import estimate,simulate
from .reference_calibration import calibrate,apply_calibration

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'calibration_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    scenarios=[('noise',v) for v in (.05,.15,.5,1.)]+[('trigger',v) for v in (-6,-3,-1,1,3,6)]+[('angle',v) for v in (-.05,-.025,-.0125,.0125,.025,.05)]+[('phase',v) for v in (-.7,-.35,.35,.7)]
    rows=[]; calibrations=[]
    for si,(kind,value) in enumerate(scenarios):
        for seed in range(10):
            iq,p,_=simulate(10000+seed,range_m=900,bearing=-.2,noise=value if kind=='noise' else .15)
            p['bearing']+=float(np.random.default_rng(50000+seed).normal(0,.002))
            cal=calibrate(iq,p,900,-.2)
            calibrations.append({'scenario':si,'seed':seed,**cal})
            for target,(distance,bearing,speed) in enumerate([(600.,-.4,0.),(1200.,.1,0.),(1800.,.6,2.)]):
                test,q,_=simulate(20000+seed*3+target,range_m=distance,bearing=bearing,speed=speed,
                    trigger_samples=3+(value if kind=='trigger' else 0),
                    bearing_bias=.025+(value if kind=='angle' else 0),
                    instrument_speed=.7+(value if kind=='phase' else 0))
                rows.append({'scenario':si,'kind':kind,'value':value,'seed':seed,'target':target,
                    'truth':{'range_m':distance,'bearing_rad':bearing,'radial_velocity_m_s':speed},
                    'raw':estimate(test,**q),'corrected':apply_calibration(test,q,cal)})
        print(kind,value,'done',flush=True)
    summary=[]
    for si,(kind,value) in enumerate(scenarios):
        rr=[r for r in rows if r['scenario']==si]; record={'kind':kind,'value':value,'metrics':{}}
        for key in ('range_m','bearing_rad','radial_velocity_m_s'):
            a=np.array([abs(r['raw'][key]-r['truth'][key]) for r in rr])
            b=np.array([abs(r['corrected'][key]-r['truth'][key]) for r in rr])
            record['metrics'][key]={'raw_mae':float(a.mean()),'corrected_mae':float(b.mean()),
                                  'better':int(np.sum(b<a)),'worse':int(np.sum(b>a))}
        summary.append(record)
    result={'protocol_sha256':hashlib.sha256((ROOT/'CALIBRATION_PROTOCOL.md').read_bytes()).hexdigest(),
       'calibrations':calibrations,'runs':rows,'summary':summary,'scope':'Synthetic independent-reflector calibration, frozen before other targets'}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=[]
    for r in summary:
        key={'noise':'radial_velocity_m_s','phase':'radial_velocity_m_s','trigger':'range_m','angle':'bearing_rad'}[r['kind']]
        s=r['metrics'][key]
        lines.append(f"| {r['kind']} | {r['value']} | {key} | {s['raw_mae']:.5f} | {s['corrected_mae']:.5f} | {s['better']}/30 |")
    report='''# Kalibracja z osobnego reflektora i jej starzenie

Kalibrator otrzymał zaszumione echo osobnego nieruchomego reflektora o znanej pozycji. Nie otrzymał prawdziwych offsetów generatora. Zamrożone poprawki użyto dla dwóch nieruchomych i jednego ruchomego celu. To nadal symulacja, nie pomiar sprzętowy.

20 scenariuszy, 10 ziaren, 3 cele: 600 ocen. Identyczny testowy szum w sparowanych porównaniach. Każdy scenariusz zmienia tylko jeden czynnik. W tabeli pokazano odpowiadającą mu wielkość; wszystkie trzy metryki i wszystkie wyniki są w JSON.

| Czynnik | Poziom | Metryka | MAE bez poprawki | MAE z poprawką | Lepsze próby |
|---|---:|---|---:|---:|---:|
'''+ '\n'.join(lines)+'''

`noise` to sigma szumu I/Q wyłącznie reflektora kalibracyjnego. `trigger` to zmiana opóźnienia PO kalibracji w próbkach, `angle` — zmiana offsetu kąta w radianach, `phase` — zmiana dryfu fazy wyrażona jako równoważna prędkość m/s. Zmiany liczone względem stanu kalibracji (+3 próbki, +.025 rad, +.7 m/s). Przykład: phase=-.7 oznacza, że aktualny instrument nie ma już dryfu, więc stara poprawka może wprowadzić błąd.

## Granica użyteczności

Dla prostego addytywnego błędu b oraz zamrożonej poprawki bhat warunek poprawy to |b-bhat|<|b|. Nie ma jednej granicy dla wszystkich wielkości. Przy dodatnim bhat i braku szumu oznacza to b>bhat/2. Tutaj to punkt odniesienia dla interpretacji, a nie skalibrowana gwarancja; kwantyzacja, szum oraz aliasing zmieniają praktyczny wynik. Gdy błąd instrumentu zanika albo zmienia znak, stara poprawka może szkodzić. Wysoki szum kalibratora także może zanieczyścić oszacowanie.

## Co jest, a czego nie ma

Estymujemy trzy stałe: offset czasu, offset kierunku i liniowy dryf fazy. Kierunek dostarczony jest jako zaszumiony odczyt enkodera, nie wyznaczany z wiązki. Znana pozycja i nieruchomość reflektora są założeniami; jego ruch błędnie przypisany instrumentowi usunąłby część rzeczywistego ruchu celów. Osobny test kontrolny pokazuje ten problem. Nie rozwiązujemy tu estymacji stanu całej obracającej się anteny, nieliniowej fazy, wielodrogowości ani nieznanej geometrii reflektora. Brak realnej walidacji.

Kod: reference_calibration.py, run_reference_calibration.py. Protokół: CALIBRATION_PROTOCOL.md. Wyniki, wszystkie 200 kalibracji oraz 600 ocen: calibration_results/summary.json. Uruchomienie: `python -m unittest clock_experiment.test_reference_calibration -v`, `python -m clock_experiment.run_reference_calibration`. Wyniki chronione przed nadpisaniem.
'''
    (ROOT/'CALIBRATION_WYNIK.md').write_text(report,encoding='utf-8')
    print('\n'.join(lines))

if __name__=='__main__': main()
