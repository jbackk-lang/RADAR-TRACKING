import hashlib,json
from pathlib import Path
import numpy as np
from .radar_compensation import simulate,estimate
from .reference_calibration import calibrate,apply_calibration
from .calibration_guard import CalibrationGuard

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'guard_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    rows=[]; validations=[]
    changes=[0,.14,.28,.42,.56,.7,.35,0,-.35,-.7,-.7,0]
    for seed in range(10):
        x,p,_=simulate(60000+seed,range_m=900,bearing=-.2)
        p['bearing']+=float(np.random.default_rng(61000+seed).normal(0,.002))
        cal=calibrate(x,p,900,-.2); guard=CalibrationGuard(cal)
        for step,delta in enumerate(changes):
            state={'trigger_samples':0 if step in (9,10) else 3,
                   'bearing_bias':0 if step in (9,10) else .025,'instrument_speed':.7+delta}
            x,p,_=simulate(70000+seed*12+step,range_m=1500,bearing=.35,noise=1. if step in (4,5) else .15,**state)
            p['bearing']+=float(np.random.default_rng(80000+seed*12+step).normal(0,.002))
            selected,decision=guard.validate(x,p,1500,.35)
            validations.append({'seed':seed,'step':step,'state':state,'calibration':cal,'selected':selected,**decision})
            for target,(distance,bearing,speed) in enumerate([(600.,-.4,0.),(1200.,.1,0.),(1800.,.6,2.)]):
                x,p,_=simulate(90000+seed*36+step*3+target,range_m=distance,bearing=bearing,speed=speed,**state)
                rows.append({'seed':seed,'step':step,'target':target,
                    'truth':{'range_m':distance,'bearing_rad':bearing,'radial_velocity_m_s':speed},
                    'raw':estimate(x,**p),'always':apply_calibration(x,p,cal),
                    'guarded':apply_calibration(x,p,selected)})
        print('seed',seed,'complete',flush=True)
    summary={}
    for group in ['ALL']+list(range(12)):
        rr=[r for r in rows if group=='ALL' or r['step']==group]
        summary[str(group)]={mode:{key:float(np.mean([abs(r[mode][key]-r['truth'][key]) for r in rr]))
                              for key in ('range_m','bearing_rad','radial_velocity_m_s')} for mode in ('raw','always','guarded')}
    result={'protocol_sha256':hashlib.sha256((ROOT/'GUARD_PROTOCOL.md').read_bytes()).hexdigest(),
            'runs':rows,'validations':validations,'summary_mae':summary,
            'scope':'Synthetic independent stationary-reflector validation; no hardware validation'}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=[]
    for group,s in summary.items():
        lines.append(f"| {group} | {s['raw']['radial_velocity_m_s']:.4f} | {s['always']['radial_velocity_m_s']:.4f} | {s['guarded']['radial_velocity_m_s']:.4f} |")
    report='''# Kontrola kalibracji na drugim reflektorze

Pierwszy nieruchomy reflektor wyznacza poprawki; drugi, z osobnym szumem, sprawdza je przed pomiarem celów. Prawda celów nigdy nie steruje przełącznikiem. Każda poprawka (czas, kąt, faza) włączana osobno po dwóch kolejnych dobrych kontrolach. Jedna odmowa ją wyłącza; słaby pomiar walidatora wyłącza wszystkie poprawki.

**Symulacja:** 10 ziaren, 12 epizodów, 3 cele = 360 pomiarów x3 warianty. Scenariusz zawiera narastający dryf, zaszumienie walidatora (epizody 4–5), zanik błędów instrumentu (9–10) i ich powrót (11). Nie dobierano progów po wynikach.

| Epizod | Bez kompensacji: MAE v [m/s] | Zawsze włączona | Z kontrolą |
|---|---:|---:|---:|
'''+ '\n'.join(lines)+'''

Wynik ALL jest średnią po ustalonej sekwencji, nie uniwersalną miarą przewagi. Kontrola może tracić poprawę podczas rozruchu, złej jakości reflektora i oczekiwania na drugie potwierdzenie. Ma chronić przed użyciem pogarszającej poprawki, ale nie usuwa szumu, kiedy wybiera wariant surowy. Wszystkie błędy odległości i kąta, stany przełączników oraz pomiary reflektora zapisano w guard_results/summary.json.

Znana, nieruchoma geometria obu reflektorów jest założeniem. Wspólny błąd odniesienia lub ruch obu reflektorów może oszukać kontrolę. Progi są heurystyczne i nie skalibrowano prawdopodobieństwa błędu. Model ma liniowy dryf fazy; nie symuluje pełnego skanu anteny ani wielodrogowości. Nie wykonano walidacji na prawdziwym sensorze.

Kod: calibration_guard.py; protokół: GUARD_PROTOCOL.md. Uruchomienie: `python -m unittest clock_experiment.test_calibration_guard -v`, `python -m clock_experiment.run_calibration_guard`. Wyniki chronione przed nadpisaniem.
'''
    (ROOT/'GUARD_WYNIK.md').write_text(report,encoding='utf-8')
    print(json.dumps(summary['ALL'],indent=2)); print('\n'.join(lines))

if __name__=='__main__': main()
