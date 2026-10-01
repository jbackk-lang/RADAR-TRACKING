# Adaptacyjny zegar i sito przed RADAR-TRACKING

Zaimplementowano trzy warianty: standard; zegar i sito z regularnym dopasowaniem; adaptacyjne przełączanie do standardu po stabilizacji amplitudy. Po przełączeniu tani monitor wciąż sprawdza amplitudę. Przy jej niezgodności sito wraca natychmiast, a dopasowanie zegara ma ograniczoną częstość.

**To pilot syntetyczny, nie test na prawdziwym radarze.** Sito amplitudowe odrzuca detekcję, jeśli jej amplituda odbiega od przewidywanej. To nowa opcjonalna warstwa przed trackerem; istniejące geometryczne TRM pozostaje włączone we wszystkich wariantach. Amplituda musi pochodzić od tego samego obiektu, nie rozwiązano asocjacji amplitud wielu obiektów.


Najważniejszy wynik: przy wspólnym zakłóceniu amplitudy i pozycji RMSE wynosi 0.2001 m (standard), 0.0237 m (stałe dopasowanie) i 0.0329 m (adaptacyjne). W spokojnym sygnale liczba dopasowań spada z 5.0 do 3.0. Jednak przy błędzie samej amplitudy wariant adaptacyjny ma RMSE 0.0329 m wobec 0.0145 m standardu. **Nie ma podstaw do domyślnego włączenia sita amplitudy dla dowolnego radaru.**

## Wyniki

Średnia z dwóch ziaren; 480 klatek w każdym przebiegu. RMSE obejmuje także odrzucone klatki: zamiast znikać z oceny, otrzymują predykcję geometryczną trackera. Czas obejmuje cały przebieg, w tym dopasowania; pojedynczy pomiar na wariant, więc jest orientacyjny.

| Scenariusz | Wariant | RMSE pozycji [m] | Czas [s] | Dopasowania zegara | Odrzucone klatki |
|---|---|---:|---:|---:|---:|
| clean | standard | 0.01447 | 2.78 | 0.0 | 0.0 |
| clean | always | 0.01475 | 11.04 | 5.0 | 6.0 |
| clean | adaptive | 0.01469 | 8.35 | 3.0 | 7.5 |
| correlated | standard | 0.20009 | 2.88 | 0.0 | 0.0 |
| correlated | always | 0.02370 | 13.56 | 5.0 | 95.5 |
| correlated | adaptive | 0.03291 | 11.75 | 5.0 | 163.0 |
| amplitude_only | standard | 0.01447 | 2.03 | 0.0 | 0.0 |
| amplitude_only | always | 0.02370 | 12.80 | 5.0 | 95.5 |
| amplitude_only | adaptive | 0.03291 | 11.31 | 5.0 | 163.0 |
| position_only | standard | 0.20009 | 2.24 | 0.0 | 0.0 |
| position_only | always | 0.20011 | 11.90 | 5.0 | 6.0 |
| position_only | adaptive | 0.20010 | 7.62 | 3.0 | 7.5 |

Scenariusze: `clean` — bez dodatkowych zakłóceń; `correlated` — błąd amplitudy i pozycji jednocześnie; `amplitude_only` — błąd amplitudy przy poprawnej pozycji; `position_only` — błąd pozycji bez ostrzeżenia w amplitudzie.

## Jak interpretować

Warstwa może pomóc tylko przy odpowiednim związku między jakością amplitudy i pozycji. Sama niezgodność amplitudy nie dowodzi złej pozycji. Kontrola amplitude_only pokazuje koszt odrzucania poprawnych detekcji; position_only pokazuje ograniczenie obserwowalności. Nie wolno wybierać wyłącznie korzystnego scenariusza i deklarować ogólnej poprawy.

Generator okresowości należy do rodziny modelu zegara; granice wyszukiwania podano z góry. Sprawdzono mały zbiór z pojedynczym, wolno poruszającym się obiektem. To nie pomiar obrotów wirnika, nie wyznaczanie prędkości postępowej z błysku, nie dowód skuteczności na dronach. Nie dostrajano parametrów po wynikach.

Monitor i sito są przyczynowe: decyzja dla bieżącej próbki używa dopasowania z przeszłości. Sam optymalizator pracuje na minionym oknie i może zatrzymać obsługę strumienia na kilka sekund. Mały łączny koszt lub przepustowość nie oznacza gwarancji czasu rzeczywistego. Zegar wygasa, żeby stara prognoza nie była używana bez końca.

## Odtwarzanie i testy

Z katalogu repo: `python -m unittest clock_experiment.test_track_clock clock_experiment.test_adaptive -v`; `python -m clock_experiment.run_adaptive`; `python -m clock_experiment.report_adaptive`. Benchmark chroni istniejący summary.json przed nadpisaniem. Protokół: ADAPTIVE_PROTOCOL.md; kod: adaptive.py i run_adaptive.py. Wszystkie 24 przebiegi i predykcje zapisano w adaptive_results.

Siedem testów jednostkowych integracji i przełączania przeszło. W tym etapie pełny pytest był niedostępny z powodu odmowy odczytu jego lokalnych plików; nie przedstawiamy poprzednich 44 testów jako ponownego uruchomienia obecnej wersji. Rdzenia geometrycznego nie zmieniono. Wcześniej ujawniony brak data.validate_on_real_trips w repo bazowym pozostaje osobnym ograniczeniem.
