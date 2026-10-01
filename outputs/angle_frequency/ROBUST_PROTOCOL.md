# Bieżące wykrywanie, pamięć pomocnicza i zakłócenia — protokół

Nowy kontroler dopasowuje każdy skan od nowa: 0, 1 lub 2 cele. Pamięć nie ustala liczby celów i nie podtrzymuje znikającego celu. Po zgodnym dopasowaniu może wygładzić kąty wagą .25, tylko gdy zmiana <=.15° i strata dopasowania rośnie nie więcej niż 5%. Przy zmianie liczby celów pamięć jest zastępowana nowym wynikiem.

Filtr: trzy iteracje odpornego dopasowania I/Q. Waga dla pozycji skanu jest wspólna dla obu RX, wyznaczana z normy zespolonych reszt modelu. Próg = 4*mediana norm / sqrt(log(2)); waga min(1,próg/norma). Dodatnia wspólna waga zachowuje międzykanałową różnicę faz danej próbki. Filtr tłumi impulsy odstające od modelu, nie gwarantuje usunięcia wielodrogowości, zakłóceń ciągłych ani ech mylonych z celem.

Wybór dwóch celów wymaga przewagi BIC >6 i obu amplitud ponad 4 oszacowane odchylenia zespolonej amplitudy. Pojedynczy cel także musi przekroczyć ten próg; inaczej count=0. BIC i progi są heurystykami tego pilota, nie skalibrowanymi prawdopodobieństwami. Siatka, wiązka i rozstaw jak stereo_model.py; bez ich strojenia. Metoda zna idealny model wiązki.

60 nowych sekwencji: empty, single, pair, disappear, appear, moving_pair; po 10 ziaren. Cztery skany. Pary: .75° lub 1.5° naprzemiennie; amplituda słabszego .25 lub .5 naprzemiennie, fazy losowe i siły zmienne ±20%. moving_pair ma wspólny ruch .12°/skan. Cele poza siatką o .037°. Dwa warunki na identycznych echach: czysty szum .05 i 8 impulsów na skan (zespolone zakłócenie sigma=1.5, te same pozycje czasu w kanałach, wartości niezależne). Łącznie 120 sekwencji, 480 skanów. Porównać obecny pojedynczy JointEstimator, odporny bieżący detektor oraz odporny detektor z pamięcią. Każdy oceniany na prawdzie bieżącego skanu; stare dane nie służą do doboru progów.

Metryki: poprawna liczba i wszystkie kąty <=.25°, osobno per warunek i scenariusz; fałszywe pary oraz fałszywe cele w pustych skanach. Podawać wyniki wszystkich skanów i osobno skanu 4. Zachować surowe I/Q, hashe i decyzje; nie nadpisywać wyników. Nie ogłaszać działania na rzeczywistym sprzęcie bez danych realnych i walidacji modelu zakłóceń. R/v nie zmieniamy ani ponownie nie oceniamy.
