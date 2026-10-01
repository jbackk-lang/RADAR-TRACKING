# Miękka fuzja amplitudy i geometrii — 2026-09-30

Test rozwojowy po obejrzeniu wcześniejszych wyników, nie ślepa walidacja. Cztery te same scenariusze i ziarna 0,1. Generator bez zmian z run_adaptive.py. Porównanie geometry vs hybrid. Standard i dawne twarde sito są historycznymi odniesieniami, bez powtórnego pomiaru czasu.

Przed aktualizacją trackera obliczamy jego predykcję. Jeśli dystans pomiaru od predykcji <=0.12 m, pozostawiamy pomiar niezależnie od amplitudy. Inaczej waga geometryczna=min(1,.12/dystans); w hybrydzie podnosimy ją do kwadratu tylko przy jednoczesnym ostrzeżeniu amplitudy. Dolna granica wagi .02. Wynik=predykcja+w*(pomiar-predykcja). To heurystyczna fuzja, nie Kalman; próg ręczny dla syntetycznej skali, nie dopasowany na nowym wyniku. Oba warianty aktualizują tracker każdą klatką (nie pomijają trudnych próbek). Punkt wynikowy jest estymatą, nie surową obserwacją.

Oszczędność obliczeń: ponowne użycie zapisanych decyzji keep z adaptive_results. Zegar operuje wyłącznie na czasie i amplitudzie, niezależnie od pozycji, więc decyzje pozostają te same. Każdy cache ma sprawdzenie zgodności time/amplitude z generatorem i zapisany hash. Nie ponawiamy optymalizacji zegara; nie ogłaszamy przez to przyspieszenia pełnej hybrydy. Nowy czas obejmuje geometrię i ważenie, wyklucza obliczenie zegara; jego dawny czas podajemy oddzielnie.

16 nowych przebiegów, RMSE na wszystkich 480 klatkach; liczba ID oraz udział zmniejszonych wag. Zapis wszystkich przewidywań i hashy. Brak tuningu po wynikach. N=2 na scenariusz, ruch prostoliniowy, generator korzystny dla zegara, brak realnego radaru i próby manewrów: brak podstaw do uniwersalnej przewagi. Sam błąd amplitudy nie dowodzi błędu pozycji.
