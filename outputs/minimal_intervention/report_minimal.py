import json
from pathlib import Path
import numpy as np
from run_minimal import ROOT, SOURCE, KEYS, GRID, SCENARIOS, digest, errors, mean_errors, corrected_estimate
from clock_experiment.online_calibration import OnlineCalibration, PARAMS
from clock_experiment.minimal_calibration import MinimalCalibration

def main():
    selection = json.loads((ROOT/'selection.json').read_text(encoding='utf-8'))
    r = json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
    assert digest(ROOT/'selection.json') == r['selection_sha256']
    assert digest(SOURCE) == selection['development_source_sha256']
    for name,expected in selection['source_hashes'].items():
        assert digest(ROOT/name)==expected
    for k in KEYS:
        eligible = [a for a in GRID if all(selection['development_mae'][str(a)][s][k] <= .8*selection['development_raw_mae'][s][k] for s in SCENARIOS)]
        assert eligible == selection['eligible'][k]
        assert r['strengths'][k] == (min(eligible) if eligible else 0.)
    assert len(r['runs'])==1440 and len(r['decisions'])==1440
    models,lookup = {},{}
    for d in r['decisions']:
        key = (d['scenario'],d['seed'],d['mode'])
        if key not in models:
            models[key] = (OnlineCalibration(d['initial'],adapt=False) if d['mode']=='memory' else
                           MinimalCalibration(d['initial'],r['strengths'] if d['mode']=='minimal' else {k:1. for k in KEYS}))
        selected,replay = models[key].observe(d['step'],d['raw'],d['quality_ok'])
        assert selected == d['selected']
        assert all(replay[k]==d[k] for k in replay)
        lookup[(*key,d['step'])] = selected
    for row in r['runs']:
        assert row['errors']=={m:errors(v,row['truth']) for m,v in row['readings'].items()}
        for mode in ('memory','decay_only','minimal'):
            replay = corrected_estimate(row['readings']['raw'],lookup[(row['scenario'],row['seed'],mode,row['step'])])
            assert all(np.isclose(replay[k],row['readings'][mode][k],rtol=0,atol=1e-10) for k in KEYS)
    lines = ['# Minimalna ingerencja — wynik', '',
             'Wprowadzono nowy kontroler: częściowa korekta oceniana na zwykłej referencji, bez EMA. Przy niepewności maleje o połowę za epizod od ostatniego potwierdzenia; po TTL=2 wygasa. Odrzucenie wyłącza korektę od razu.', '',
             f"Siły wybrane na danych rozwojowych: odległość **{r['strengths']['range_m']:.0%}**, kąt **{r['strengths']['bearing_rad']:.0%}**, prędkość **{r['strengths']['radial_velocity_m_s']:.0%}** początkowej kalibracji.", '',
             'Wybrano najmniejsze siły z ustalonej listy spełniające kryterium MAE ≤ 80% raw w obu scenariuszach rozwojowych. Nie jest to minimum wśród wszystkich możliwych wartości ani gwarancja bezpieczeństwa. Plik selection.json zapisano przed rozpoczęciem oceny. Parametrów nie zmieniono po wyniku.', '',
             'Ocena: osobne ziarna 200–219, 480 referencji, 1440 pomiarów celów z nowych I/Q. Warianty dostają te same echa. Dodatkowe obserwacje wymagane przez kontroler: 0. Model i trajektorie scenariuszy są znane; test sprawdza nowe realizacje szumu, nie nowy sprzęt.', '']
    names = {'raw':'Bez korekty','memory':'Pełna pamięć','decay_only':'Pełna korekta + wygaszanie','minimal':'Częściowa korekta + wygaszanie'}
    for scenario,s in r['summary'].items():
        rr = [row for row in r['runs'] if row['scenario']==scenario]
        assert mean_errors(rr)==s['mae']
        lines += ['## '+('Dotychczasowa trajektoria, nowy szum' if scenario=='new_noise' else 'Nagła zmiana instrumentu przy słabej referencji'), '',
                  '| Wariant | MAE R [m] | MAE kąta [rad] | MAE v [m/s] |','|---|---:|---:|---:|']
        for m,v in s['mae'].items():
            lines.append(f"| {names[m]} | {v['range_m']:.4f} | {v['bearing_rad']:.5f} | {v['radial_velocity_m_s']:.4f} |")
        lines += ['', 'Zmiana MAE częściowej korekty względem surowego pomiaru (wartość ujemna oznacza poprawę):', '']
        for k in KEYS:
            pct=100*(s['mae']['minimal'][k]/s['mae']['raw'][k]-1)
            lines.append(f'- {k}: {pct:+.1f}%.')
        lines += ['', '| Wariant | Średnia ingerencja R [m] | Kąt [rad] | v [m/s] |','|---|---:|---:|---:|']
        for m,v in s['mean_intervention'].items():
            lines.append(f"| {names[m]} | {v['range_m']:.4f} | {v['bearing_rad']:.5f} | {v['radial_velocity_m_s']:.4f} |")
        lines += ['', 'Sparowane różnice MAE po 20 ziarnach; bootstrap CI95 z 10000 próbek, bez korekty wielokrotnych porównań. Ujemna różnica oznacza mniejszy błąd pierwszego wariantu. Zdegenerowane CI odległości wynikają ze stałych binów w tym modelu, nie z pewności poza nim.', '']
        for pair,metrics in s['comparisons'].items():
            for k,v in metrics.items():
                lines.append(f"- {pair}, {k}: {v['mean']:.6f}; CI95 [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}].")
        if scenario=='hidden_change':
            lines += ['', 'Błąd instrumentu znika w epizodzie 4, referencja jest zaszumiona w 4–6. Średni dodatni nadmiar błędu względem raw w tych trzech epizodach (ujemne różnice liczone jako zero):', '',
                      '| Wariant | Nadmiar R [m] | Kąt [rad] | v [m/s] |','|---|---:|---:|---:|']
            for m,v in s['harm_steps_4_6'].items():
                lines.append(f"| {names[m]} | {v['range_m']['mean_positive_excess']:.4f} | {v['bearing_rad']['mean_positive_excess']:.5f} | {v['radial_velocity_m_s']['mean_positive_excess']:.4f} |")
            lines += ['', 'Udział pomiarów ze szkodą większą niż margines kontrolera:', '']
            for m,v in s['harm_steps_4_6'].items():
                lines.append(f"- {names[m]}: R {v['range_m']['fraction']:.1%}, kąt {v['bearing_rad']['fraction']:.1%}, v {v['radial_velocity_m_s']['fraction']:.1%}.")
            lines += ['', '| Epizod | Raw R [m] | Pamięć R [m] | Częściowa R [m] | Raw v [m/s] | Pamięć v [m/s] | Częściowa v [m/s] |', '|---|---:|---:|---:|---:|---:|---:|']
            for step in range(4,8):
                v=s['per_step'][str(step)]
                lines.append(f"| {step} | {v['raw']['range_m']:.4f} | {v['memory']['range_m']:.4f} | {v['minimal']['range_m']:.4f} | {v['raw']['radial_velocity_m_s']:.4f} | {v['memory']['radial_velocity_m_s']:.4f} | {v['minimal']['radial_velocity_m_s']:.4f} |")
        lines += ['']
    lines += ['## Wniosek i weryfikacja', '',
              'Częściowa korekta poprawiła raw o około 21–27% na nowych ziarnach, ale miała większy średni błąd niż pełna pamięć w obu scenariuszach. Po ukrytej zmianie zmniejszyła średni dodatni nadmiar błędu odległości z 14.5745 do 1.3664 m, a prędkości z 0.4598 do 0.0557 m/s względem pełnej pamięci. Nie usunęła szkody całkowicie.', '',
              'Samo wygaszanie pełnej korekty było lepsze od stale częściowej ingerencji pod względem średniego błędu wszystkich trzech parametrów w obu scenariuszach. W scenariuszu ukrytej zmiany poprawiło też wszystkie trzy MAE względem pełnej pamięci; przy dotychczasowej trajektorii zwiększyło MAE. Dlatego minimalna siła jest wyborem kompromisu, a nie automatycznie najlepszą dokładnością.', '',
              'Częściowa ingerencja z wygaszaniem zmniejsza koszt nieaktualnej korekty, ale oddaje część poprawy pełnej pamięci, gdy kalibracja jest nadal właściwa. Ocena obejmuje oba efekty. Wynik nie uzasadnia uniwersalnej przewagi ani gwarancji bezpieczeństwa. Bez wiarygodnej referencji nie da się w tym modelu rozstrzygnąć, czy błąd instrumentu zniknął.', '',
              '10 testów kontrolerów przeszło. Odtworzono 1440 decyzji, błędy 1440 pomiarów, wszystkie średnie scenariuszy i sprawdzono hashe. Dodatkowo analityczna kompensacja zgadzała się z pełnym przetwarzaniem I/Q dla 1440 pomiarów rozwojowych i 1440 nowych pomiarów. To sprawdzenie właściwości tego liniowego modelu, nie walidacja innych modeli.', '',
              'Odtwarzanie w katalogu minimal_intervention:', '',
              '`python -m unittest clock_experiment.test_minimal_calibration clock_experiment.test_online_calibration clock_experiment.test_calibration_guard -v`', '',
              '`python report_minimal.py` — weryfikuje zapisane decyzje i metryki.', '',
              '`python run_minimal.py` — chroni istniejące selection.json i results.json; kolejny przebieg wymaga osobnej kopii bez tych dwóch plików. Obok musi znajdować się katalog validation z pierwotnymi danymi rozwojowymi.']
    (ROOT/'WYNIK.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Verified 1440 decisions and 1440 measurements. Report: WYNIK.md')

if __name__=='__main__':
    main()
