# Kompensacja znanego stanu radaru

**W kontrolowanej symulacji poprawka znanych błędów aparatury działa. Nie jest to jeszcze walidacja na prawdziwym radarze ani dowód wyprowadzenia „czystej geometrii”.**

30 zaszumionych burstów: 10 ziaren x 3 cele. Dwa nieruchome i jeden o prędkości radialnej 2 m/s. Wprowadzono opóźnienie triggera 3 próbki, błąd enkodera .025 rad i dryf fazy równoważny .7 m/s. Każdą poprawkę podano dokładnie z generatora. To idealnie znana kalibracja, nie odtworzenie jej z nieznanego echa.

| Średni błąd bezwzględny | Przed | Po |
|---|---:|---:|
| range_m | 21.654266 | 0.830168 |
| bearing_rad | 0.025000 | 0.000000 |
| radial_velocity_m_s | 0.698068 | 0.011715 |

Średnia estymata ruchomego celu po kompensacji: **1.994266 m/s** przy prawdzie 2 m/s. Korekta usuwa dodany wkład instrumentu, a nie cały ruch. Pozostaje szum i kwantyzacja odległości (7.49 m/bin). Nie dopasowywano progów po wyniku.

## Co naprawdę policzono

Model impulsowego radaru 77 GHz, fs=20 MHz, PRF=8 kHz, 64 impulsy po 2048 próbek. Opóźnienie impulsu wyznacza odległość, iloczyny kolejnych spójnych impulsów dają Doppler. Kierunek pochodzi z zasymulowanego enkodera; nie estymujemy go z antenowej wiązki. Cele są w osobnych burstach. Nie symulujemy pełnego obrotu anteny, kształtu RCS, wielodrogowości ani asocjacji celów.

Poprawki: odjęcie przesunięcia triggera od osi opóźnienia; odjęcie offsetu enkodera; przemnożenie I/Q przez exp(-i*phi_instrument). Sam kąt obrotu anteny nie jest taką fazą. Nie wykonujemy operacji echo minus sygnał nadany.

## Dlaczego nie faza raz na pełny obrót

Dla odstępu 1 s jednoznaczny zakres wynosi +/-0.0009734 m/s. Cel 2 m/s w demonstracji z samej zawiniętej różnicy faz daje 0.0007347 m/s. To aliasing, którego nie usuwa zwykłe unwrap bez dodatkowych informacji. W tym eksperymencie prędkość liczymy z impulsów co 1/8000 s, a nie z pełnych skanów.

## Audyt naturalnych danych

Sprawdzono pola czterech dotychczasowych cache Open Radar. Są w nich widma, czasy klatek, odległość i referencyjna prędkość. Brakuje zestawu: per-pulse I/Q, kąt enkodera na impuls, kalibracja triggera i fazy instrumentu. Nie wykonano na tych plikach pozornej kompensacji obracającej się anteny. Audyt wszystkich pól jest w compensation_results/summary.json. To ograniczenie naszego cache, nie twierdzenie o wszystkich danych źródłowych.

## Weryfikacja i odtwarzanie

Cztery testy: nieruchome i ruchome cele, zerowa kompensacja, błędny znak fazy, odrzucenie pustego sygnału. Kod: radar_compensation.py; protokół: COMPENSATION_PROTOCOL.md. Z repo: `python -m unittest clock_experiment.test_compensation -v`, `python -m clock_experiment.run_compensation`. Skrypt chroni istniejące wyniki.

Następny krok fizyczny wymaga nagrania spójnych impulsów z metadanymi i niezależnym pomiarem stanu radaru. Dopiero wtedy można sprawdzić, czy poprawa utrzymuje się przy niedokładnej kalibracji i rzeczywistym skanowaniu. Nazwy K*/G mogą opisywać tę architekturę, ale ten test nie dowodzi nowego prawa ani nowego mostu formalnego TIMDR.
