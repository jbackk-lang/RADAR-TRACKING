import hashlib,json
from pathlib import Path
import numpy as np
from .online_calibration import OnlineCalibration
ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'online_results'; r=json.loads((out/'summary.json').read_text())
    source=ROOT/'guard_results/summary.json'; old=json.loads(source.read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest()==r['input_sha256']
    assert hashlib.sha256((ROOT/'ONLINE_PROTOCOL.md').read_bytes()).hexdigest()==r['protocol_sha256']
    assert len(r['runs'])==360 and len(r['decisions'])==240
    for seed in range(10):
        refs=[v for v in old['validations'] if v['seed']==seed]
        for mode in ('memory','online'):
            model=OnlineCalibration(refs[0]['calibration'],adapt=mode=='online')
            for v in refs:
                cal,d=model.observe(v['step'],v['raw'],v['quality_ok'])
                recorded=next(x for x in r['decisions'] if x['seed']==seed and x['step']==v['step'] and x['mode']==mode)
                assert cal==recorded['selected']
                for key,value in d.items(): assert value==recorded[key]
    for group,summary in r['summary_mae'].items():
        rows=[x for x in r['runs'] if group=='ALL' or x['step']==int(group)]
        for mode,metrics in summary.items():
            for key,value in metrics.items():
                assert abs(np.mean([abs(x[mode][key]-x['truth'][key]) for x in rows])-value)<1e-12
    names={'raw':'Bez kompensacji','always':'Stała kompensacja','guarded':'Poprzedni kontroler',
           'memory':'Cztery stany + pamięć','online':'Cztery stany + adaptacja EMA'}
    table='\n'.join(f"| {names[m]} | {v['range_m']:.4f} | {v['bearing_rad']:.5f} | {v['radial_velocity_m_s']:.4f} |" for m,v in r['summary_mae']['ALL'].items())
    text='''# Cztery stany i autokorekta bez dodatkowych pomiarów

**Na tej samej syntetycznej sekwencji pomaga przede wszystkim pamięć ostatniej potwierdzonej decyzji. Adaptacja parametrów daje małą dodatkową poprawę prędkości, ale pogarsza odległość i kąt względem samej pamięci.** Nie ma podstaw do ogłoszenia wariantu uczącego się najlepszym we wszystkich metrykach.

| Wariant | MAE R [m] | MAE kąta [rad] | MAE v [m/s] |
|---|---:|---:|---:|
'''+table+f'''

## Co zmieniono

Confirmed: wiarygodny nowy pomiar potwierdza korzyść propozycji. Rejected: wiarygodny pomiar wykazuje szkodę — wycofujemy zaufanie. Uncertain: brakuje rozstrzygnięcia, ostatnia potwierdzona poprawka zostaje na maksymalnie dwa epizody. Waiting: brak ważnego potwierdzenia, czekamy na zwykłą obserwację i zwracamy odczyt bez poprawki. Niepewność nie odnawia terminu ważności.

Wariant memory nie zmienia parametrów kalibracji. Wariant online po dobrej obserwacji proponuje EMA=.5 na podstawie surowego pomiaru znanego nieruchomego reflektora. Propozycja jest oceniana dopiero na następnej obserwacji. Reflektor kontrolny jest niezależny od śledzonych celów; jego wcześniejsze próbki służą adaptacji, a późniejsze kontroli. To nie dwie niezależne fizyczne referencje w każdym kroku — wspólny błąd reflektora nadal może oszukać system.

## Koszt i zakres

Wykorzystano te same 120 zwykłych obserwacji referencji i 360 pomiarów celów co poprzednio. **Dodatkowe obserwacje: 0.** Odtworzono identyczne zaszumione echa celów i sprawdzono zgodność surowych estymat. Czas samych 120 decyzji na tym komputerze: memory {r['controller_seconds']['memory']:.4f} s, online {r['controller_seconds']['online']:.4f} s. To pojedynczy pomiar, wyklucza pozyskanie danych i przetwarzanie I/Q; różnica tych małych czasów nie dowodzi przewagi wydajnościowej.

Eksperyment rozwojowy na uprzednio znanej sekwencji; progi zapisano przed nowym przebiegiem, ale nie jest to nowy holdout. Brak realnego sprzętu, pełnego skanu, wielodrogowości i walidacji przy ruchu reflektora. TTL wyrażono w epizodach tej symulacji, nie jako uniwersalną liczbę sekund. Pamięć może chwilowo zachować błędną poprawkę, jeżeli instrument zmieni się podczas nieobserwowalności. Nie uzyskano gwarancji bezpieczeństwa ani uniwersalnego samouczenia.

## Pliki i weryfikacja

Kod: online_calibration.py; protokół: ONLINE_PROTOCOL.md; wyniki: online_results/summary.json. Pięć testów kontrolera i jego poprzednika przeszło. Ponownie odtworzono 240 decyzji oraz metryki wszystkich 360 pomiarów. Odtwarzanie z repo: `python -m unittest clock_experiment.test_online_calibration clock_experiment.test_calibration_guard -v`, `python -m clock_experiment.run_online_calibration`, `python -m clock_experiment.report_online`. Istniejące wyniki są chronione przed nadpisaniem.
'''
    (ROOT/'ONLINE_WYNIK.md').write_text(text,encoding='utf-8')
    (out/'verification.json').write_text(json.dumps({'measurements_verified':360,'decisions_replayed':240,'hashes_match':True},indent=2))
    print('Verified 360 measurements and 240 decisions')

if __name__=='__main__': main()
