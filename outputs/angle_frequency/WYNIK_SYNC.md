# Synchronizacja czasu echa i kąta anteny

**Wynik:** wspólna kalibracja przesunięcia czasu i zera enkodera poprawiła pomiar kąta na nowych echach oraz przy innych prędkościach obrotu. Stała korekta samego kąta nie przenosiła się równie dobrze między prędkościami.

Kalibracja: 60 obserwacji znanego, nieruchomego reflektora przy .5,1,1.5 obrotu/s. Test: 180 osobnych ech celów przy .65,1.25,1.8 obrotu/s i trzech kątach. Parametry zamrożone przed pomiarem celów; nie korzystano z prawdy celów do kalibracji. To nowe obserwacje syntetyczne, nie eksperyment bez dodatkowych obserwacji.

| Obrót | Bez kalibracji: MAE [°] | Tylko kąt: MAE [°] | Czas + zero: MAE [°] | Czas + zero: P95 [°] |
|---|---:|---:|---:|---:|
| constant | 0.9897 | 0.3337 | 0.0318 | 0.0748 |
| variable | 0.9878 | 0.3329 | 0.0381 | 0.0738 |

Średni błąd oszacowania przesunięcia czasu: 0.067 ms. Średni błąd zera enkodera: 0.0226°.

Najpierw odejmujemy czas przelotu 2R/c z użyciem zmierzonej odległości (sigma błędu R=2 m), następnie kalibrowane przesunięcie czasu. Po interpolacji rzeczywistego położenia enkodera odejmujemy jego zero. Przesunięcie dotyczy osi czasu echa względem enkodera; nie jest automatycznie poprawką czasu przelotu ani wszystkich zegarów radaru. R i v nie są zmieniane.

## Kontrole i ograniczenia

Przy jednakowych prędkościach obrotu kalibrator odmawia rozdzielania delay i zero. Sprawdzono 10/10 odmów. Rozrzut prędkości jest warunkiem identyfikowalności; zmiana prędkości musi być faktycznie obecna w danych.

Podanie błędnego kąta reflektora o .4° nadal oszukało kalibrację: MAE celów przy zmiennym obrocie wyniosło 0.4038°. Synchronizacja usuwa badane sprzężenie czasu z kątem, ale nie gwarantuje poprawności referencji.

Model zakłada stałe opóźnienie i zero, izolowaną symetryczną wiązkę, brak ruchu reflektora i wielodrogowości. Nie wykonano testu na sprzęcie, przy dryfie kalibracji ani przy silnych zakłóceniach impulsowych. W realnym torze pozostaje potrzebny odporny filtr zakłóceń oraz kontrola jakości referencji; ten test nie łączy jeszcze filtra z kalibratorem.

4 testy przeszły. Ponownie dopasowano wszystkie 10 kalibracji z odtworzonych ech referencji, odtworzono 180 wyników nowych celów i sprawdzono hashe. Odtwarzanie: python -m unittest test_sync_calibration -v; python report_sync.py. python run_sync.py chroni istniejące parametry i wyniki.
