# Niezależna kontrola kalibracji — 2026-10-01

Symulacja tego samego modelu impulsowego; reflektor kalibracyjny R=900m, bearing=-.2, v=0. Osobny reflektor walidacyjny R=1500m, bearing=.35, v=0 z niezależnym szumem. Cele pomiarowe jak wcześniej, nie służą wyborowi poprawek. Kalibracja zamrożona przez całą sekwencję.

10 ziaren, 12 epizodów. Przyrosty dryfu fazy w równoważnych m/s: [0,.14,.28,.42,.56,.7,.35,0,-.35,-.7,-.7,0], względem bazowych .7. Opóźnienie triggera zmienia się o -3 próbki w epizodach 9–10, offset kąta o -.025 rad również 9–10, potem wraca. Szum walidatora sigma=1 w epizodach 4–5, poza tym .15. Szum kalibratora i celów .15; bearing reflektorów dodatkowo niezależny szum sigma .002 rad. Trzy warianty na tym samym echu celu: raw, always, guarded.

Walidator przed celami oblicza błędy względem znanej własnej pozycji i nieruchomości. Każda poprawka osobno wymaga zmniejszenia błędu o margines: range 3.75 m, bearing .004 rad, speed .05 m/s. Ponadto pik widma fast-time musi przekraczać medianę mocy >=10 razy, a spójność impuls–impuls w tym binie >=.8. Wymagane dwa kolejne pozytywne epizody do włączenia; jedna odmowa wyłącza. Przy słabej jakości poprawki wyłączone, nie ekstrapolowane. Progi stałe, nie dostrajane do wyników. Nie nazywamy ich skalibrowanymi prawdopodobieństwami.

360 pomiarów celów x3 warianty. Raport MAE osobno dla R, bearing, v; per epizod i całość, liczby włączeń. Weryfikacja nie korzysta z prawdy celów do przełączania. Znana i stabilna geometria obu reflektorów jest założeniem. Drugi reflektor nie jest gwarancją przy błędzie wspólnym geometrii odniesienia, aliasingu lub wielodrogowości; brak realnego sensora, pełnego skanowania i nieliniowej fazy.
