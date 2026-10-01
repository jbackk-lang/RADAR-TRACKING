# Kontrola kalibracji na drugim reflektorze

**Wynik mieszany:** kontrola chroni po zaniku dryfu (epizody 9–10: około .011 m/s wobec .70 m/s starej poprawki), ale pogarsza średni wynik względem kompensacji stale włączonej: .528 vs .353 m/s. Bez kompensacji jest .760 m/s. Koszt rozruchu, wyłączenia przy zaszumionym reflektorze i ponownego potwierdzenia jest w tej sekwencji większy niż zysk z ochrony. Nie wykazano globalnej przewagi tego przełącznika. Podobnie dla odległości: 9.31 m z kontrolą vs 4.07 m stale włączonej, bez kompensacji 18.18 m. Wyniki nie zostały użyte do ponownego dostrojenia progów.

Pierwszy nieruchomy reflektor wyznacza poprawki; drugi, z osobnym szumem, sprawdza je przed pomiarem celów. Prawda celów nigdy nie steruje przełącznikiem. Każda poprawka (czas, kąt, faza) włączana osobno po dwóch kolejnych dobrych kontrolach. Jedna odmowa ją wyłącza; słaby pomiar walidatora wyłącza wszystkie poprawki.

**Symulacja:** 10 ziaren, 12 epizodów, 3 cele = 360 pomiarów x3 warianty. Scenariusz zawiera narastający dryf, zaszumienie walidatora (epizody 4–5), zanik błędów instrumentu (9–10) i ich powrót (11). Nie dobierano progów po wynikach.

| Epizod | Bez kompensacji: MAE v [m/s] | Zawsze włączona | Z kontrolą |
|---|---:|---:|---:|
| ALL | 0.7600 | 0.3530 | 0.5279 |
| 0 | 0.6999 | 0.0129 | 0.6999 |
| 1 | 0.8385 | 0.1402 | 0.1402 |
| 2 | 0.9780 | 0.2797 | 0.2797 |
| 3 | 1.1196 | 0.4213 | 0.4213 |
| 4 | 1.2585 | 0.5602 | 1.2585 |
| 5 | 1.3967 | 0.6984 | 1.3967 |
| 6 | 1.0515 | 0.3532 | 1.0515 |
| 7 | 0.7022 | 0.0126 | 0.0126 |
| 8 | 0.3496 | 0.3487 | 0.3496 |
| 9 | 0.0110 | 0.7008 | 0.0110 |
| 10 | 0.0115 | 0.6964 | 0.0115 |
| 11 | 0.7027 | 0.0122 | 0.7027 |

Wynik ALL jest średnią po ustalonej sekwencji, nie uniwersalną miarą przewagi. Kontrola może tracić poprawę podczas rozruchu, złej jakości reflektora i oczekiwania na drugie potwierdzenie. Ma chronić przed użyciem pogarszającej poprawki, ale nie usuwa szumu, kiedy wybiera wariant surowy. Wszystkie błędy odległości i kąta, stany przełączników oraz pomiary reflektora zapisano w guard_results/summary.json.

Znana, nieruchoma geometria obu reflektorów jest założeniem. Wspólny błąd odniesienia lub ruch obu reflektorów może oszukać kontrolę. Progi są heurystyczne i nie skalibrowano prawdopodobieństwa błędu. Model ma liniowy dryf fazy; nie symuluje pełnego skanu anteny ani wielodrogowości. Nie wykonano walidacji na prawdziwym sensorze.

Kod: calibration_guard.py; protokół: GUARD_PROTOCOL.md. Uruchomienie: `python -m unittest clock_experiment.test_calibration_guard -v`, `python -m clock_experiment.run_calibration_guard`. Wyniki chronione przed nadpisaniem.
