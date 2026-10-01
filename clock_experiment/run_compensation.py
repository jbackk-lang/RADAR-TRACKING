import json
import hashlib
from pathlib import Path
import numpy as np
from .radar_compensation import estimate,simulate,C

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'compensation_results'; out.mkdir(exist_ok=True)
    if (out/'summary.json').exists(): raise SystemExit('Existing results preserved')
    rows=[]
    for seed in range(10):
        for idx,(distance,bearing,speed) in enumerate([(600.,-.4,0.),(1200.,.1,0.),(1800.,.6,2.)]):
            iq,p,cal=simulate(seed*3+idx,range_m=distance,bearing=bearing,speed=speed)
            raw=estimate(iq,**p); corrected=estimate(iq,**p,**cal)
            rows.append({'seed':seed,'target':idx,'truth':{'range_m':distance,'bearing_rad':bearing,'radial_velocity_m_s':speed},
                         'raw':raw,'corrected':corrected})
    metrics={}
    for name in ('raw','corrected'):
        metrics[name]={key:float(np.mean([abs(r[name][key]-r['truth'][key]) for r in rows]))
                       for key in ('range_m','bearing_rad','radial_velocity_m_s')}
    cached=json.loads((ROOT/'signal_results/summary.json').read_text())
    audit=[]
    for r in cached['runs']:
        if r['source']!='Open Radar': continue
        with np.load(r['input_path'],allow_pickle=False) as z:
            audit.append({'file':r['input_path'],'fields':z.files,'spectrum_shape':list(z['spec'].shape),
              'missing_for_this_test':['per-pulse I/Q','encoder orientation per pulse','trigger calibration','instrument phase calibration']})
    wavelength=C/77e9; dt=1.; actual=2.
    principal=float(np.angle(np.exp(1j*4*np.pi*actual*dt/wavelength)))
    alias={'true_speed_m_s':actual,'scan_interval_s':dt,'unambiguous_speed_m_s':wavelength/(4*dt),
           'apparent_pair_phase_speed_m_s':wavelength*principal/(4*np.pi*dt)}
    result={'protocol_sha256':hashlib.sha256((ROOT/'COMPENSATION_PROTOCOL.md').read_bytes()).hexdigest(),
      'source_sha256':hashlib.sha256((ROOT/'radar_compensation.py').read_bytes()).hexdigest(),
      'metrics_mae':metrics,'alias_demo':alias,'real_data_audit':audit,'runs':rows,
      'scope':'Synthetic known-calibration model, no full antenna scan or real-data validation'}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    table='\n'.join(f"| {key} | {metrics['raw'][key]:.6f} | {metrics['corrected'][key]:.6f} |" for key in metrics['raw'])
    moving=float(np.mean([r['corrected']['radial_velocity_m_s'] for r in rows if r['target']==2]))
    report=f'''# Kompensacja znanego stanu radaru

**W kontrolowanej symulacji poprawka znanych błędów aparatury działa. Nie jest to jeszcze walidacja na prawdziwym radarze ani dowód wyprowadzenia „czystej geometrii”.**

30 zaszumionych burstów: 10 ziaren x 3 cele. Dwa nieruchome i jeden o prędkości radialnej 2 m/s. Wprowadzono opóźnienie triggera 3 próbki, błąd enkodera .025 rad i dryf fazy równoważny .7 m/s. Każdą poprawkę podano dokładnie z generatora. To idealnie znana kalibracja, nie odtworzenie jej z nieznanego echa.

| Średni błąd bezwzględny | Przed | Po |
|---|---:|---:|
{table}

Średnia estymata ruchomego celu po kompensacji: **{moving:.6f} m/s** przy prawdzie 2 m/s. Korekta usuwa dodany wkład instrumentu, a nie cały ruch. Pozostaje szum i kwantyzacja odległości (7.49 m/bin). Nie dopasowywano progów po wyniku.

## Co naprawdę policzono

Model impulsowego radaru 77 GHz, fs=20 MHz, PRF=8 kHz, 64 impulsy po 2048 próbek. Opóźnienie impulsu wyznacza odległość, iloczyny kolejnych spójnych impulsów dają Doppler. Kierunek pochodzi z zasymulowanego enkodera; nie estymujemy go z antenowej wiązki. Cele są w osobnych burstach. Nie symulujemy pełnego obrotu anteny, kształtu RCS, wielodrogowości ani asocjacji celów.

Poprawki: odjęcie przesunięcia triggera od osi opóźnienia; odjęcie offsetu enkodera; przemnożenie I/Q przez exp(-i*phi_instrument). Sam kąt obrotu anteny nie jest taką fazą. Nie wykonujemy operacji echo minus sygnał nadany.

## Dlaczego nie faza raz na pełny obrót

Dla odstępu 1 s jednoznaczny zakres wynosi +/-{alias['unambiguous_speed_m_s']:.7f} m/s. Cel 2 m/s w demonstracji z samej zawiniętej różnicy faz daje {alias['apparent_pair_phase_speed_m_s']:.7f} m/s. To aliasing, którego nie usuwa zwykłe unwrap bez dodatkowych informacji. W tym eksperymencie prędkość liczymy z impulsów co 1/8000 s, a nie z pełnych skanów.

## Audyt naturalnych danych

Sprawdzono pola czterech dotychczasowych cache Open Radar. Są w nich widma, czasy klatek, odległość i referencyjna prędkość. Brakuje zestawu: per-pulse I/Q, kąt enkodera na impuls, kalibracja triggera i fazy instrumentu. Nie wykonano na tych plikach pozornej kompensacji obracającej się anteny. Audyt wszystkich pól jest w compensation_results/summary.json. To ograniczenie naszego cache, nie twierdzenie o wszystkich danych źródłowych.

## Weryfikacja i odtwarzanie

Cztery testy: nieruchome i ruchome cele, zerowa kompensacja, błędny znak fazy, odrzucenie pustego sygnału. Kod: radar_compensation.py; protokół: COMPENSATION_PROTOCOL.md. Z repo: `python -m unittest clock_experiment.test_compensation -v`, `python -m clock_experiment.run_compensation`. Skrypt chroni istniejące wyniki.

Następny krok fizyczny wymaga nagrania spójnych impulsów z metadanymi i niezależnym pomiarem stanu radaru. Dopiero wtedy można sprawdzić, czy poprawa utrzymuje się przy niedokładnej kalibracji i rzeczywistym skanowaniu. Nazwy K*/G mogą opisywać tę architekturę, ale ten test nie dowodzi nowego prawa ani nowego mostu formalnego TIMDR.
'''
    (ROOT/'COMPENSATION_WYNIK.md').write_text(report,encoding='utf-8')
    print(json.dumps({'mae':metrics,'moving_target_after':moving,'alias':alias},indent=2))

if __name__=='__main__': main()
