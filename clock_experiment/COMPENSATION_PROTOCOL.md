# Kompensacja znanego stanu radaru — 2026-10-01

Kontrolowany test fizycznego modelu pomiaru, nie walidacja realnego sensora. Model impulsowego, monostatycznego radaru zespolonego 77 GHz: 64 spójne impulsy, PRF=8000 Hz, 2048 próbek przy fs=20 MHz. Trzy rozdzielone w odległości cele (600,1200,1800 m); radialne prędkości 0,0,2 m/s; azymuty -.4,.1,.6 rad. Każdy cel dostaje osobny burst, w obrębie którego znane są jego pomiary kierunku. Nie symulujemy pełnej wiązki skanującej ani asocjacji wielu ech.

Znany stan aparatury: przesunięcie triggera +3 próbki; offset enkodera +.025 rad; liniowy dryf fazy równoważny +.7 m/s. Sygnał jest opóźnionym impulsem Gaussa (sigma 1.5 próbki) z Dopplerem celu i instrumentu; szum zespolony sigma .15. Pozycja radialna w krótkim burst traktowana jako stała (maks. przemieszczenie .016 m <<7.5 m/bin). 10 ziaren, bez strojenia. Ten sam zaszumiony sygnał w obu wariantach.

Estimator: maksimum uśrednionej mocy po fast-time -> opóźnienie; faza sumy iloczynów kolejnych impulsów w wykrytym binie -> prędkość radialna; odczyt kierunku jako bearing. Przed: surowa siatka czasu, enkoder i I/Q. Po: odjęcie znanego opóźnienia triggera i błędu enkodera oraz przemnożenie I/Q przez exp(-i*phi_instrument). Nie odejmujemy sygnału transmitowanego ani 'czystej geometrii'. Brak dostępu estymatora do prawdy celu; kalibrację podajemy z generatora i jawnie nazywamy idealnie znaną.

Kontrole: brak błędów instrumentu (kompensacja zerowa identyczna); ruchomy cel po kompensacji zachowuje 2 m/s; błędny znak kalibracji powinien pogorszyć wynik; osobna demonstracja aliasingu fazy między obrotami co 1 s. Główne metryki: błędy R, bearing i radialnego v dla wszystkich 30 burstów, zapis obu wariantów. Nie wyciągamy wniosku o przewadze TIMDR ani o odtworzeniu kalibracji z nieznanego echa.

Realne dane: sprawdzamy pola istniejących czterech cache Open Radar. Bez per-pulse I/Q, stanów enkodera i niezależnej kalibracji nie wykonujemy fikcyjnej walidacji tej kompensacji. Jeżeli brak metadanych, raportujemy brak walidacji realnej.
