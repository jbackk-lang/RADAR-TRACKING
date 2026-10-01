# Przełącznik jakości prognozy sygnału

Monitor przewiduje amplitudę następnej próbki na podstawie modelu dopasowanego do przeszłości. Trzy kolejne błędy ponad próg uruchamiają stan analizy; osiem zgodnych próbek pozwala korzystać z zapamiętanego zegara. Dopasowania są ograniczone do jednego na 80 próbek. **Monitor nigdy nie odrzuca pozycji.**

Reszta prognozy modelu harmonicznego może odzwierciedlać zmianę fazy, częstości lub amplitudy, ale nie rozpoznaje jednoznacznie przyczyny. To rozszerzenie istniejącego zegara, nie osobny fizyczny detektor fazy/wirnika.

## Wyniki (mniejsze NMSE jest lepsze)

Wszystkie próbki po 100-próbkowym rozruchu oceniane są bez wybierania tylko dobrych fragmentów. Gdy zegar nie zostaje zaakceptowany, używamy średniej 12 wcześniejszych amplitud. Ten sam filtr jest odniesieniem. Kolumna „zegar” podaje udział ocenianych prognoz rzeczywiście pochodzących z zegara.

| Próba | Ocenione próbki | Monitor NMSE | Średnia 12 NMSE | Zegar | Dopasowania |
|---|---:|---:|---:|---:|---:|
| chirp_0 | 380 | 0.072 | 1.157 | 100% | 2 |
| chirp_1 | 380 | 0.025 | 1.156 | 100% | 2 |
| change_0 | 380 | 0.929 | 1.409 | 100% | 4 |
| change_1 | 380 | 1.053 | 1.410 | 100% | 5 |
| noise_0 | 380 | 1.093 | 1.093 | 0% | 5 |
| noise_1 | 380 | 1.062 | 1.062 | 0% | 5 |
| real_person_track_013 | 100 | 0.309 | 0.309 | 0% | 2 |
| real_bicycle_track_014 | 20 | 0.919 | 0.919 | 0% | 1 |
| real_vehicle_track_025 | 60 | 1.086 | 1.086 | 0% | 1 |
| real_uav_track_157 | 100 | 0.453 | 0.453 | 0% | 2 |

## Naturalny test

**Wynik naturalnej kontroli jest negatywny dla korzyści zegara:** w każdym z czterech śladów jego udział w prognozach wyniósł 0%. Monitor pozostał przy średniej 12 próbek. To poprawna odmowa w ramach zastosowanych kryteriów, ale nie dowód, że w danych nie ma żadnej okresowości: mogły nie pasować okno, priori lub model. Syntetyczne wyniki nie zastępują tej walidacji.

Rzeczywiste dane: [Open Radar Initiative](https://github.com/openradarinitiative/open_radar_datasets), Gusland et al. 2021, DOI 10.1109/RadarConf2147009.2021.9455239, CC BY-NC 4.0. Wybrano pierwszą alfabetycznie ścieżkę z ponad 100 klatkami dla każdej klasy z lokalnego cache eval. Amplituda to pierwiastek sumy mocy dostarczonego widma Dopplera. To rzeczywisty sygnał po przetworzeniu przez autorów, nie surowe ADC ani odczyt jasności kamery. Parametry wyszukiwania .1–4 Hz dotyczą modulacji obwiedni klatek, nie częstotliwości łopat. Dane zawierają przerwy; model korzysta z rzeczywistych czasów, ale nie odtwarza brakujących obserwacji.

Cztery krótkie ślady nie pozwalają dowieść przewagi ani określić RPM. Bez zewnętrznego tachometru oceniamy jedynie prognozę amplitudy. Wariant ze zmianą częstości i szumem jest syntetyczny. Generator chirpu odpowiada rodzinie modelu, co mu sprzyja. Nie zmieniano parametrów po wynikach.

## Kod i ograniczenia

`signal_monitor.py` — monitor; `run_signal.py` — 6 prób syntetycznych i do 4 rzeczywistych; `report_signal.py` — odtworzenie metryk i kontrola hashy. `SIGNAL_PROTOCOL.md` zapisuje wybór danych i progi przed wynikiem. Wyniki i prognozy są w `signal_results`. Optymalizacja zegara blokuje strumień podczas dopasowania: nie jest to gwarancja działania w czasie rzeczywistym.

Uruchomienie z repo: `python -m unittest clock_experiment.test_signal_monitor -v`, `python -m clock_experiment.run_signal`, `python -m clock_experiment.report_signal`. Istniejące podsumowanie jest chronione przed nadpisaniem.
