# Bieżący detektor i odporny filtr I/Q

**Wynik:** bieżące dopasowanie naprawia problem zamrożonej liczby celów. Filtr impulsów wyraźnie poprawił wyniki przy zakłóceniach, ale nie rozdzielił wszystkich słabych, bliskich par. Pamięć nie zwiększyła liczby poprawnych wyników w tej próbie.

Nowe sekwencje: 60 scen × 4 skany, ocenione bez impulsów i z impulsami na tych samych echach; 480 skanów. Poprawny wynik oznacza zgodną liczbę celów i błąd każdego kąta <=.25°. Liczba celów i kąty dopasowywane na bieżącym skanie. Pamięć tylko wygładza zgodne kąty; nie ustala liczby celów.

| Warunki | Skany | Zwykłe dopasowanie poprawne | Odporny detektor poprawny | Odporny + pamięć poprawny |
|---|---:|---:|---:|---:|
| clean | 240 | 182 | 222 | 222 |
| impulsive | 240 | 87 | 180 | 180 |

Zwykły poprzednik wymusza 1 lub 2 cele i nie ma modelu pustego skanu. Z 93 dodatkowych poprawnych wyników z impulsami 40 pochodzi z rozpoznania pustych skanów. Na 200 niepustych skanach: zwykły 87/200, odporny 140/200. Korzyść nie pochodzi wyłącznie z filtrowania: zmieniono także regułę wyboru liczby celów i progi istotności amplitud.

| Scenariusz z impulsami | Skany | Zwykły poprawny | Odporny poprawny | Skan 4: odporny poprawny / 10 |
|---|---:|---:|---:|---:|
| empty | 40 | 0 | 40 | 10 |
| single | 40 | 35 | 40 | 10 |
| pair | 40 | 6 | 20 | 5 |
| disappear | 40 | 13 | 25 | 10 |
| appear | 40 | 28 | 35 | 5 |
| moving_pair | 40 | 5 | 20 | 5 |

Po zaniku drugiego celu odporny detektor poprawnie zwrócił pojedynczy cel na skanie 4 w 10/10 sekwencji z impulsami. Przy pojawieniu drugiego celu poprawnie rozdzielił 5/10 — nie wszystkie. Fałszywe pary przy pojedynczym celu z impulsami: zwykły 6, odporny 0 w badanej próbie. Puste skany: odporny poprawnie odmówił detekcji w 40/40, zarówno z impulsami jak i bez.

## Filtr i ograniczenia

Filtr odporny wyznacza reszty zespolonego modelu i zmniejsza wagi odstających pozycji skanu. Oba kanały dostają tę samą dodatnią wagę, co zachowuje różnicę faz między nimi dla danej próbki. To ważenie przy dopasowaniu, nie trwała zmiana zapisanych I/Q. Surowe dane są zachowane.

Tłumienie impulsowych zakłóceń jest sprawdzone syntetycznie. Nie sprawdzono rzeczywistych zakłóceń ciągłych, listków bocznych, wielodrogowości, dryfu fazy i niezgodnego kształtu wiązki. Model zna idealną wiązkę. Nie deklarujemy gotowości sprzętowej ani usunięcia wszystkich zakłóceń. Do realnego toru potrzebne są próbki zakłóceń, kalibracja kanałów i sprawdzenie filtrów na tych danych.

Pamięć nie poprawiła skuteczności rozdzielania; nie ma podstaw do przypisywania jej przewagi. Bliskie pary ze słabym drugim echem nadal wymagają lepszej informacji przestrzennej lub bardziej wiarygodnego modelu. R/v nie zostały zmienione ani zweryfikowane na nowo.

## Weryfikacja

4 testy kontrolne przeszły. Ponownie obliczono poprawność 480 skanów, sprawdzono zgodność liczby celów wersji bieżącej i z pamięcią oraz hashe. Odtworzono 96 kolejnych decyzji wersji z pamięcią z zapisanych I/Q (ziarna 0 i 9 dla wszystkich scenariuszy i warunków).

python -m unittest test_robust_scan -v

python report_robust.py

python run_robust.py chroni istniejące robust_results.json i robust_iq.npz; kolejny przebieg wymaga osobnej kopii bez tych plików.
