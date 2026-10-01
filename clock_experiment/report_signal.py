import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent

def main():
    out=ROOT/'signal_results'; result=json.loads((out/'summary.json').read_text())
    assert hashlib.sha256((ROOT/'SIGNAL_PROTOCOL.md').read_bytes()).hexdigest()==result['protocol_sha256']
    lines=[]
    for r in result['runs']:
        with np.load(out/(r['name']+'.npz'),allow_pickle=False) as z:
            variance=max(float(np.var(z['observed'])),1e-12)
            for key,field in [('prediction','nmse_monitor'),('baseline','nmse_mean12')]:
                assert np.isclose(np.mean((z[key]-z['observed'])**2)/variance,r[field],atol=1e-12)
        if 'input_path' in r:
            assert hashlib.sha256(Path(r['input_path']).read_bytes()).hexdigest()==r['input_sha256']
        lines.append(f"| {r['name']} | {r['scored_samples']} | {r['nmse_monitor']:.3f} | {r['nmse_mean12']:.3f} | {100*r['clock_fraction']:.0f}% | {r['fit_calls']} |")
    text='''# Przełącznik jakości prognozy sygnału

Monitor przewiduje amplitudę następnej próbki na podstawie modelu dopasowanego do przeszłości. Trzy kolejne błędy ponad próg uruchamiają stan analizy; osiem zgodnych próbek pozwala korzystać z zapamiętanego zegara. Dopasowania są ograniczone do jednego na 80 próbek. **Monitor nigdy nie odrzuca pozycji.**

Reszta prognozy modelu harmonicznego może odzwierciedlać zmianę fazy, częstości lub amplitudy, ale nie rozpoznaje jednoznacznie przyczyny. To rozszerzenie istniejącego zegara, nie osobny fizyczny detektor fazy/wirnika.

## Wyniki (mniejsze NMSE jest lepsze)

Wszystkie próbki po 100-próbkowym rozruchu oceniane są bez wybierania tylko dobrych fragmentów. Gdy zegar nie zostaje zaakceptowany, używamy średniej 12 wcześniejszych amplitud. Ten sam filtr jest odniesieniem. Kolumna „zegar” podaje udział ocenianych prognoz rzeczywiście pochodzących z zegara.

| Próba | Ocenione próbki | Monitor NMSE | Średnia 12 NMSE | Zegar | Dopasowania |
|---|---:|---:|---:|---:|---:|
'''+ '\n'.join(lines)+'''

## Naturalny test

**Wynik naturalnej kontroli jest negatywny dla korzyści zegara:** w każdym z czterech śladów jego udział w prognozach wyniósł 0%. Monitor pozostał przy średniej 12 próbek. To poprawna odmowa w ramach zastosowanych kryteriów, ale nie dowód, że w danych nie ma żadnej okresowości: mogły nie pasować okno, priori lub model. Syntetyczne wyniki nie zastępują tej walidacji.

Rzeczywiste dane: [Open Radar Initiative](https://github.com/openradarinitiative/open_radar_datasets), Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, CC BY-NC 4.0. Wybrano pierwszą alfabetycznie ścieżkę z ponad 100 klatkami dla każdej klasy z lokalnego cache eval. Amplituda to pierwiastek sumy mocy dostarczonego widma Dopplera. To rzeczywisty sygnał po przetworzeniu przez autorów, nie surowe ADC ani odczyt jasności kamery. Parametry wyszukiwania .1–4 Hz dotyczą modulacji obwiedni klatek, nie częstotliwości łopat. Dane zawierają przerwy; model korzysta z rzeczywistych czasów, ale nie odtwarza brakujących obserwacji.

Cztery krótkie ślady nie pozwalają dowieść przewagi ani określić RPM. Bez zewnętrznego tachometru oceniamy jedynie prognozę amplitudy. Wariant ze zmianą częstości i szumem jest syntetyczny. Generator chirpu odpowiada rodzinie modelu, co mu sprzyja. Nie zmieniano parametrów po wynikach.

## Kod i ograniczenia

`signal_monitor.py` — monitor; `run_signal.py` — 6 prób syntetycznych i do 4 rzeczywistych; `report_signal.py` — odtworzenie metryk i kontrola hashy. `SIGNAL_PROTOCOL.md` zapisuje wybór danych i progi przed wynikiem. Wyniki i prognozy są w `signal_results`. Optymalizacja zegara blokuje strumień podczas dopasowania: nie jest to gwarancja działania w czasie rzeczywistym.

Uruchomienie z repo: `python -m unittest clock_experiment.test_signal_monitor -v`, `python -m clock_experiment.run_signal`, `python -m clock_experiment.report_signal`. Istniejące podsumowanie jest chronione przed nadpisaniem.
'''
    (ROOT/'SIGNAL_WYNIK.md').write_text(text,encoding='utf-8')
    (out/'verification.json').write_text(json.dumps({'runs_verified':len(result['runs']),'metrics_and_hashes_verified':True},indent=2))
    print('\n'.join(lines))

if __name__=='__main__': main()
