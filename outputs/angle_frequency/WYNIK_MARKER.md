# Jedna prędkość: czas ze znacznika, zero z reflektora

**Wynik:** niezależne znaczniki rozdzielają przesunięcie zegarów i zero enkodera bez zmiany nominalnej prędkości obrotu. Przy stabilnym czasie sama poprawka kąta jest równie dobra; przewaga aktualizowanych znaczników pojawia się przy zmianie przesunięcia zegara.

Kalibracja przy jednej nominalnej prędkości 1 obr/s: 60 obserwacji reflektora, 10 ziaren. Ocena na 90 nowych echach celów. Każdy zestaw ma 8 niezależnych elektronicznych znaczników, z szumem odczytu 20 us na zegar. Nie są to nowe emisje radarowe, ale są dodatkową informacją instrumentalną.

| Warunki | Raw MAE [°] | Tylko kąt [°] | Zamrożony znacznik [°] | Bieżące znaczniki [°] |
|---|---:|---:|---:|---:|
| constant | 0.7073 | 0.0259 | 0.0262 | 0.0279 |
| variable | 0.7151 | 0.0351 | 0.0288 | 0.0299 |
| clock_change | 0.9074 | 0.1905 | 0.1895 | 0.0282 |

Średni błąd estymacji opóźnienia ze znaczników: 8.77 us.

constant: stały obrót i zegary; variable: chwilowa prędkość ±5% przy niezmienionej nominalnej prędkości; clock_change: taki sam obrót i zmiana przesunięcia czasu o ±.5 ms po kalibracji. Każdy skan dostaje nowe znaczniki; zero enkodera pozostaje zamrożone.

Przy tej samej stałej prędkości kalibracja jednego łącznego błędu kąta także działa, choć nie identyfikuje jego przyczyn. Znaczniki dostarczają brakującego niezależnego pomiaru czasu. Nie przypisujemy tej niejednoznaczności rezonansowi mechanicznemu ani nie twierdzimy, że znaczniki tłumią drgania.

Założenie sprzętowe: zdarzenie znacznika musi reprezentować właściwe punkty czasowe obu torów. Różnica opóźnień przewodów, rejestracji i przetwarzania echa wymaga osobnego pomiaru; sama zgodność zegarów jej nie gwarantuje. Nie wykonano pomiarów sprzętowych, testu wielodrogowości ani integracji z filtrem impulsów. Błędna geometria reflektora nadal może wprowadzić zły zero_bias. R/v bez zmian.

3 testy przeszły. Ponownie odtworzono 10 kalibracji z referencji, 90 wyników celów i wszystkie opóźnienia ze znaczników; sprawdzono hashe. python -m unittest test_marker_sync -v; python report_marker.py. python run_marker.py chroni istniejące parametry i wyniki.
