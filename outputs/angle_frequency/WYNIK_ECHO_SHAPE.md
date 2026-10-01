# Czy spadek echa pomaga mierzyć odległość?

Tak, w tym modelu dopasowanie narastania i spadku razem poprawiło lokalizację względem samego maksimum. Sam spadek wykładniczy nie identyfikuje czasu nadejścia przy nieznanej amplitudzie: przesunięcie czasu można zamienić na zmianę amplitudy. Potrzebny jest początek echa lub inny niezależny znacznik.

| Scena | Pik: poprawne /100 | Cały kształt, bank modeli: poprawne /100 | Pik: MAE wykryć [m] | Cały kształt: MAE wykryć [m] |
|---|---:|---:|---:|---:|
| Gauss bez ogona | 100 | 100 | 2.515 | 0.950 |
| Ogon tau8 | 11 | 96 | 23.468 | 2.750 |
| Zmieniony ogon tau12 | 9 | 96 | 20.534 | 2.430 |
| Dodatkowy nierozpoznany ogon odbiornika | 0 | 0 | 53.678 | 23.476 |

MAE obejmuje wszystkie wykrycia danej metody, również błędnie zlokalizowane, ale nie odrzucenia. Liczba wykryć: Gauss 100/100 obie metody; tau8 pik84/bank98; tau12 pik65/bank97; odbiornik pik27/bank88. Dlatego wartości MAE mają różne zbiory warunkowe i nie stanowią same w sobie porównania na wszystkich obserwacjach. Najbardziej czytelny wynik to liczba poprawnych lokalizacji wśród wszystkich 100 scen.

Poprawa dla Gaussa pochodzi z dopasowania wielu próbek i podpróbkowego czasu, nie informacji ze spadku rezonansowego. Dopasowanie Gaussa bez banku osiągnęło 0.830 m. Dla prawdziwego ogona tau8 dopasowanie znanego właściwego ogona dało 97/100 poprawnych i 2.695 m MAE wykryć. Narzucenie ogona tau8 na echo bez ogona dało 17.416 m błędu: nie wolno zakładać rezonansu wszędzie.

Bank modeli pozwolił rozpoznać zmianę ogona tau8 na tau12, ale nie rozdzielił nieznanej odpowiedzi celu i dodatkowego filtra odbiornika. W scenie odbiornika pozostał systematyczny błąd około 23.5 m. Nie uzyskano gwarancji dokładnego czasu powrotu bez kalibracji toru odbiorczego.

160 osobnych scen szumu ustaliło progi; 500 nowych scen testowych. Na 100 nowych pustych scenach pik miał 1 alarm, metody dopasowania 0; ograniczona próba nie gwarantuje zera alarmów. Ta sama odebrana energia dla kształtów izoluje informację czasową; nie dowodzi, że rzeczywisty rezonans wzmacnia echo. Znany zakres modeli jest korzystnym założeniem. Bez ruchu, wielodrogowości i sprzętu. Główny tracker bez zmian.

Kontrole: bezszumowe odzyskanie początku i tau8, algebraiczna niejednoznaczność samego spadku oraz odtworzenie zapisanych estymat. Protokół ECHO_SHAPE_PROTOCOL.md, dane echo_shape_results.json. Uruchomienie: `python outputs/angle_frequency/run_echo_shape.py`; istniejące wyniki chronione.
