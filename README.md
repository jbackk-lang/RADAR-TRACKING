# RADAR-TRACKING

1. Pobierz punkty z radaru (frame).
2. TRM → usuń punkty bez sąsiadów (fałszywe odbicia).
3. GIA → wyznacz lokalny kierunek ruchu.
4. TIMDR → sprawdź, czy nastąpiła zmiana kierunku / prędkości.
5. Jeśli TIMDR wysoki → obiekt wykonuje manewr.
6. Predictor → przewidź nową pozycję na podstawie GIA.
7. Stabilizer → wygładź trajektorię.
8. Zapisz wynik jako nowy stan trackera.
