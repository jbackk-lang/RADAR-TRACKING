# Kalibracja z osobnego reflektora i jej starzenie

**Wynik:** przy bazowym szumie reflektora .15 błąd prędkości maleje z .70084 do .01270 m/s (30/30 prób poprawionych). Przy silnym szumie 1.0 średni błąd rośnie po kompensacji do 1.86039 m/s, mimo poprawy w 21/30 prób — kilka porażek dominuje średnią. Gdy dryf instrumentu zanika po kalibracji, stara poprawka zwiększa błąd z .01107 do .69789 m/s. Kompensacja wymaga oceny jakości i aktualności kalibracji; samo jej wykonanie raz nie daje gwarancji.

Kalibrator otrzymał zaszumione echo osobnego nieruchomego reflektora o znanej pozycji. Nie otrzymał prawdziwych offsetów generatora. Zamrożone poprawki użyto dla dwóch nieruchomych i jednego ruchomego celu. To nadal symulacja, nie pomiar sprzętowy.

20 scenariuszy, 10 ziaren, 3 cele: 600 ocen. Identyczny testowy szum w sparowanych porównaniach. Każdy scenariusz zmienia tylko jeden czynnik. W tabeli pokazano odpowiadającą mu wielkość; wszystkie trzy metryki i wszystkie wyniki są w JSON.

| Czynnik | Poziom | Metryka | MAE bez poprawki | MAE z poprawką | Lepsze próby |
|---|---:|---|---:|---:|---:|
| noise | 0.05 | radial_velocity_m_s | 0.70084 | 0.00967 | 30/30 |
| noise | 0.15 | radial_velocity_m_s | 0.70084 | 0.01270 | 30/30 |
| noise | 0.5 | radial_velocity_m_s | 0.70084 | 0.10106 | 30/30 |
| noise | 1.0 | radial_velocity_m_s | 0.70084 | 1.86039 | 21/30 |
| trigger | -6 | range_m | 23.31460 | 45.17641 | 0/30 |
| trigger | -3 | range_m | 0.83017 | 22.69198 | 0/30 |
| trigger | -1 | range_m | 14.15945 | 7.70235 | 30/30 |
| trigger | 1 | range_m | 29.14908 | 7.28727 | 30/30 |
| trigger | 3 | range_m | 44.13870 | 22.27689 | 30/30 |
| trigger | 6 | range_m | 66.62314 | 44.76133 | 30/30 |
| angle | -0.05 | bearing_rad | 0.02500 | 0.05087 | 0/30 |
| angle | -0.025 | bearing_rad | 0.00000 | 0.02587 | 0/30 |
| angle | -0.0125 | bearing_rad | 0.01250 | 0.01337 | 9/30 |
| angle | 0.0125 | bearing_rad | 0.03750 | 0.01163 | 30/30 |
| angle | 0.025 | bearing_rad | 0.05000 | 0.02413 | 30/30 |
| angle | 0.05 | bearing_rad | 0.07500 | 0.04913 | 30/30 |
| phase | -0.7 | radial_velocity_m_s | 0.01107 | 0.69789 | 0/30 |
| phase | -0.35 | radial_velocity_m_s | 0.35031 | 0.34777 | 17/30 |
| phase | 0.35 | radial_velocity_m_s | 1.04929 | 0.35121 | 30/30 |
| phase | 0.7 | radial_velocity_m_s | 1.40094 | 0.70286 | 30/30 |

`noise` to sigma szumu I/Q wyłącznie reflektora kalibracyjnego. `trigger` to zmiana opóźnienia PO kalibracji w próbkach, `angle` — zmiana offsetu kąta w radianach, `phase` — zmiana dryfu fazy wyrażona jako równoważna prędkość m/s. Zmiany liczone względem stanu kalibracji (+3 próbki, +.025 rad, +.7 m/s). Przykład: phase=-.7 oznacza, że aktualny instrument nie ma już dryfu, więc stara poprawka może wprowadzić błąd.

## Granica użyteczności

Dla prostego addytywnego błędu b oraz zamrożonej poprawki bhat warunek poprawy to |b-bhat|<|b|. Nie ma jednej granicy dla wszystkich wielkości. Przy dodatnim bhat i braku szumu oznacza to b>bhat/2. Tutaj to punkt odniesienia dla interpretacji, a nie skalibrowana gwarancja; kwantyzacja, szum oraz aliasing zmieniają praktyczny wynik. Gdy błąd instrumentu zanika albo zmienia znak, stara poprawka może szkodzić. Wysoki szum kalibratora także może zanieczyścić oszacowanie.

## Co jest, a czego nie ma

Estymujemy trzy stałe: offset czasu, offset kierunku i liniowy dryf fazy. Kierunek dostarczony jest jako zaszumiony odczyt enkodera, nie wyznaczany z wiązki. Znana pozycja i nieruchomość reflektora są założeniami; jego ruch błędnie przypisany instrumentowi usunąłby część rzeczywistego ruchu celów. Osobny test kontrolny pokazuje ten problem. Nie rozwiązujemy tu estymacji stanu całej obracającej się anteny, nieliniowej fazy, wielodrogowości ani nieznanej geometrii reflektora. Brak realnej walidacji.

Kod: reference_calibration.py, run_reference_calibration.py. Protokół: CALIBRATION_PROTOCOL.md. Wyniki, wszystkie 200 kalibracji oraz 600 ocen: calibration_results/summary.json. Uruchomienie: `python -m unittest clock_experiment.test_reference_calibration -v`, `python -m clock_experiment.run_reference_calibration`. Wyniki chronione przed nadpisaniem.
