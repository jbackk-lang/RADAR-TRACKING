# Cztery stany i autokorekta bez dodatkowych pomiarów

**Na tej samej syntetycznej sekwencji pomaga przede wszystkim pamięć ostatniej potwierdzonej decyzji. Adaptacja parametrów daje małą dodatkową poprawę prędkości, ale pogarsza odległość i kąt względem samej pamięci.** Nie ma podstaw do ogłoszenia wariantu uczącego się najlepszym we wszystkich metrykach.

| Wariant | MAE R [m] | MAE kąta [rad] | MAE v [m/s] |
|---|---:|---:|---:|
| Bez kompensacji | 18.1836 | 0.02083 | 0.7600 |
| Stała kompensacja | 4.0702 | 0.00585 | 0.3530 |
| Poprzedni kontroler | 9.3051 | 0.01120 | 0.5279 |
| Cztery stany + pamięć | 0.4266 | 0.00157 | 0.2385 |
| Cztery stany + adaptacja EMA | 1.8061 | 0.00234 | 0.2341 |

## Co zmieniono

Confirmed: wiarygodny nowy pomiar potwierdza korzyść propozycji. Rejected: wiarygodny pomiar wykazuje szkodę — wycofujemy zaufanie. Uncertain: brakuje rozstrzygnięcia, ostatnia potwierdzona poprawka zostaje na maksymalnie dwa epizody. Waiting: brak ważnego potwierdzenia, czekamy na zwykłą obserwację i zwracamy odczyt bez poprawki. Niepewność nie odnawia terminu ważności.

Wariant memory nie zmienia parametrów kalibracji. Wariant online po dobrej obserwacji proponuje EMA=.5 na podstawie surowego pomiaru znanego nieruchomego reflektora. Propozycja jest oceniana dopiero na następnej obserwacji. Reflektor kontrolny jest niezależny od śledzonych celów; jego wcześniejsze próbki służą adaptacji, a późniejsze kontroli. To nie dwie niezależne fizyczne referencje w każdym kroku — wspólny błąd reflektora nadal może oszukać system.

## Koszt i zakres

Wykorzystano te same 120 zwykłych obserwacji referencji i 360 pomiarów celów co poprzednio. **Dodatkowe obserwacje: 0.** Odtworzono identyczne zaszumione echa celów i sprawdzono zgodność surowych estymat. Czas samych 120 decyzji na tym komputerze: memory 0.0143 s, online 0.0132 s. To pojedynczy pomiar, wyklucza pozyskanie danych i przetwarzanie I/Q; różnica tych małych czasów nie dowodzi przewagi wydajnościowej.

Eksperyment rozwojowy na uprzednio znanej sekwencji; progi zapisano przed nowym przebiegiem, ale nie jest to nowy holdout. Brak realnego sprzętu, pełnego skanu, wielodrogowości i walidacji przy ruchu reflektora. TTL wyrażono w epizodach tej symulacji, nie jako uniwersalną liczbę sekund. Pamięć może chwilowo zachować błędną poprawkę, jeżeli instrument zmieni się podczas nieobserwowalności. Nie uzyskano gwarancji bezpieczeństwa ani uniwersalnego samouczenia.

## Pliki i weryfikacja

Kod: online_calibration.py; protokół: ONLINE_PROTOCOL.md; wyniki: online_results/summary.json. Pięć testów kontrolera i jego poprzednika przeszło. Ponownie odtworzono 240 decyzji oraz metryki wszystkich 360 pomiarów. Odtwarzanie z repo: `python -m unittest clock_experiment.test_online_calibration clock_experiment.test_calibration_guard -v`, `python -m clock_experiment.run_online_calibration`, `python -m clock_experiment.report_online`. Istniejące wyniki są chronione przed nadpisaniem.
