# Kąt z sygnału: częstotliwości oraz obrót anteny

**Wniosek:** w badanej symulacji obracającej się anteny korzystanie z enkodera i środka przejścia wiązki daje dobry pomiar kąta bez dodawania korekty bearing. Sam czas przy założeniu stałej prędkości obrotu zawodzi, gdy obrót jest nierówny. Metoda nachylenia fazy po częstotliwości usuwa idealny stały offset fazy, ale jest podatna na szum i nie odróżnia opóźnienia kanałów od kierunku.

## Czy istniejące dane wystarczą?

Nie. clock_experiment/radar_compensation.py ma I/Q o wymiarach impulsy × próbki, jedną nośną 77 GHz i kąt zapisany w metadanych. Nie ma kanałów dwóch anten, próbek wielu częstotliwości RF, czasu przejścia wiązki ani enkodera. data/sample_radar.npy ma 83 gotowe detekcje z polami frame,x,y,t. Żaden z tych plików nie pozwala sprawdzić nowego fizycznego pomiaru kąta.

Testy poniżej używają osobnych, nowych danych syntetycznych. Nie zmieniono starego kontrolera ani jego wyników. Nie deklarujemy braku dodatkowych danych względem starego modelu.

## Obrót anteny i czas echa

Kąt wynika z kierunku anteny podczas przejścia echa przez wiązkę. Czas przelotu 2R/c dotyczy odległości; czas od początku obrotu wraz z położeniem anteny określa azymut. Jest to standardowa zasada radaru z obracającą się anteną: [FAA — Radar](https://www.faa.gov/air_traffic/publications/atpubs/AIM/aim0405.html).

1800 przypadków: 200 ziaren, 3 kąty, 3 scenariusze. Nominalnie 1 obrót/s, FWHM mocy wiązki 1.5°, odstęp echa i enkodera .2 ms, szum enkodera .02°. Środek wiązki oszacowano przez średnią kąta enkodera ważoną mocą echa po odjęciu oszacowanego tła. W tym eksperymencie zmierzona odległość jest bezbłędna i służy wyrównaniu czasu przelotu.

| Warunki | Czas × nominalny obrót: MAE [°] | Enkoder w maksimum: MAE [°] | Enkoder + środek wiązki: MAE [°] | P95 środka [°] |
|---|---:|---:|---:|---:|
| Stały obrót | 0.1793 | 0.1796 | 0.0271 | 0.0656 |
| Prędkość obrotu ±5% | 1.4033 | 0.1833 | 0.0295 | 0.0724 |
| Obrót ±5%, przesunięcie zegara 2 ms | 1.4865 | 0.7139 | 0.7176 | 0.7876 |

Przy 1 obrocie/s przesunięcie czasu o 2 ms odpowiada 0.72°. Test pokazał około 0.718° MAE mimo enkodera. Błąd zera enkodera również pozostaje błędem kąta — żadna z tych metod nie usuwa go sama.

To wynik dla nieruchomego, izolowanego celu i idealnej symetrycznej wiązki. Brak listków bocznych, wielodrogowości, sąsiednich celów, drgań mocowania i walidacji sprzętowej. Środek wiązki wymaga obserwacji całego przejścia, więc wynik jest dostępny później niż pojedyncze echo.

## Różne częstotliwości i faza

Pomiar fazy między rozdzielonymi antenami jest podstawą wyznaczania kąta: [TI — MIMO Radar](https://www.ti.com/lit/an/swra554/swra554.pdf). Nasz model przyjmuje phi(f)=2πf(d sin(theta)/c + delay)+offset. Dopasowanie nachylenia usuwa stały offset, ale mierzy sumę opóźnienia geometrycznego i opóźnienia kanału. Są one nierozróżnialne bez dodatkowej informacji lub kalibracji; potwierdza to test dwóch identycznych zestawów I/Q dla różnych kątów i opóźnień.

8400 przypadków: dwie anteny, 17 częstotliwości, 64 próbki/f, pasma 1 i 4 GHz wokół 77 GHz, szum .15 na składową zespoloną. Wyniki MAE odnoszą się do ważnych estymat; liczbę nieważnych pokazano jawnie. Nie przycinano sin(theta) do [-1,1].

| Pasmo [GHz] | Warunki | Metoda | MAE [°] | P95 [°] | Nieważne / 1400 |
|---|---|---:|---:|---:|
| 1 | Bez błędu kanałów | Faza na środkowej częstotliwości | 0.4201 | 1.0434 | 0 |
| 1 | Bez błędu kanałów | Faza po paśmie, założony offset=0 | 0.1064 | 0.2593 | 0 |
| 1 | Bez błędu kanałów | Nachylenie z dwóch częstotliwości | 31.7053 | 72.8450 | 466 |
| 1 | Bez błędu kanałów | Nachylenie z 17 częstotliwości | 22.1419 | 52.6890 | 177 |
| 1 | Stały offset fazy .15 rad | Faza na środkowej częstotliwości | 3.0611 | 4.0191 | 0 |
| 1 | Stały offset fazy .15 rad | Faza po paśmie, założony offset=0 | 3.0571 | 3.5441 | 0 |
| 1 | Stały offset fazy .15 rad | Nachylenie z dwóch częstotliwości | 31.5422 | 73.7878 | 470 |
| 1 | Stały offset fazy .15 rad | Nachylenie z 17 częstotliwości | 22.7129 | 54.9546 | 171 |
| 1 | Offset .15 rad + opóźnienie .2 ps | Faza na środkowej częstotliwości | 5.0443 | 6.2361 | 0 |
| 1 | Offset .15 rad + opóźnienie .2 ps | Faza po paśmie, założony offset=0 | 5.0409 | 5.8579 | 0 |
| 1 | Offset .15 rad + opóźnienie .2 ps | Nachylenie z dwóch częstotliwości | 31.5033 | 75.9403 | 473 |
| 1 | Offset .15 rad + opóźnienie .2 ps | Nachylenie z 17 częstotliwości | 22.7682 | 53.3441 | 171 |
| 4 | Bez błędu kanałów | Faza na środkowej częstotliwości | 0.4201 | 1.0434 | 0 |
| 4 | Bez błędu kanałów | Faza po paśmie, założony offset=0 | 0.1064 | 0.2568 | 0 |
| 4 | Bez błędu kanałów | Nachylenie z dwóch częstotliwości | 12.0825 | 30.9951 | 16 |
| 4 | Bez błędu kanałów | Nachylenie z 17 częstotliwości | 6.5291 | 15.9763 | 0 |
| 4 | Stały offset fazy .15 rad | Faza na środkowej częstotliwości | 3.0611 | 4.0191 | 0 |
| 4 | Stały offset fazy .15 rad | Faza po paśmie, założony offset=0 | 3.0564 | 3.5430 | 0 |
| 4 | Stały offset fazy .15 rad | Nachylenie z dwóch częstotliwości | 12.1519 | 31.3436 | 15 |
| 4 | Stały offset fazy .15 rad | Nachylenie z 17 częstotliwości | 6.5691 | 16.4161 | 0 |
| 4 | Offset .15 rad + opóźnienie .2 ps | Faza na środkowej częstotliwości | 5.0443 | 6.2361 | 0 |
| 4 | Offset .15 rad + opóźnienie .2 ps | Faza po paśmie, założony offset=0 | 5.0402 | 5.8585 | 0 |
| 4 | Offset .15 rad + opóźnienie .2 ps | Nachylenie z dwóch częstotliwości | 12.1191 | 30.9877 | 22 |
| 4 | Offset .15 rad + opóźnienie .2 ps | Nachylenie z 17 częstotliwości | 6.7500 | 16.6915 | 1 |

Bez szumu obie metody nachylenia odzyskują kąt mimo stałego offsetu fazy. Przy badanym szumie i paśmie 4 GHz nachylenie z 17 częstotliwości daje około 6.5° MAE, a faza po paśmie około 0.11° przy braku błędu kanałów. Wąskie względnie do nośnej pasmo daje małą zmianę fazy geometrycznej, więc różnicowanie wzmacnia wpływ szumu. Większe pasmo lub rozstaw anten mogą zmienić kompromis, ale nie zostały dostrojone w tym teście.

Wyników obrotu i częstotliwości nie porównujemy jako dowodu wyższości konkretnego radaru: mają różne dane, model szumu i sposób pozyskania informacji. Oba testy sprawdzają mechanizm i jego ograniczenia.

## Weryfikacja i użycie

10 testów przeszło. Ponownie obliczono błędy i metryki 8400 przypadków częstotliwościowych oraz 1800 przypadków obrotu. Odtworzono z I/Q 84 przypadki częstotliwościowe i 18 przypadków obrotu (ziarna 0 i 199 dla wszystkich warunków). Sprawdzono hashe kodu i obu protokołów.

W katalogu angle_frequency:

`python -m unittest test_angle_model test_rotation_model -v`

`python report_angle.py`

`python run_angle.py` oraz `python run_rotation.py` chronią istniejące wyniki. Kolejny przebieg wymaga osobnej kopii bez results.json i rotation_results.json.

Przed użyciem w realnym systemie potrzebne są surowe echa podczas skanu oraz zsynchronizowane znaczniki czasu i kąta anteny. Jeśli są już zapisywane, można przetestować tę metodę na istniejących skanach bez nowych emisji. W obecnych plikach ich nie ma.
