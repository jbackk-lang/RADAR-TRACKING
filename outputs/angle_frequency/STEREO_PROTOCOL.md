# Koherentne nakładanie ech i dwa kanały — mały test

Zespolone I/Q dwóch celów są sumowane przed dodaniem szumu. Ta sama komórka R/v, nieruchome cele, stała faza względna podczas skanu. Nośna 77 GHz, rozstaw odbiorników lambda/2, wspólna znana pozycja anteny, idealna wiązka o FWHM mocy 1.5°. 121 pozycji skanu na odcinku ±6° wokół kierunku 1.2 rad; 101 kandydatów kąta co .1° na odcinku ±5°. Cele przesunięte o .037° względem środka siatki, aby nie trafiały idealnie w kandydatów.

180 par: separacje .75°,1.5°,3° × stosunki amplitud drugiego do pierwszego .25,.5,1,2 × fazy 0,pi/2,pi × 5 ziaren. 20 pojedynczych celów kontrolnych. Porównanie 1 i 2 kanałów. W obu wariantach taka sama łączna energia sygnału (amplitudy podzielone przez sqrt(liczby kanałów)), taki sam szum .05 na składową kanału. Dwa kanały dają więcej danych, ale nie przewagę samej sumarycznej energii. Kanały są idealnie zsynchronizowane i skalibrowane.

Dopasowanie znanego zespolonego wzorca skanu. Sprawdzić jeden cel i wszystkie pary kandydatów o separacji >=.3°. Amplitudy i fazy dopasować wspólnie zespoloną metodą najmniejszych kwadratów. Model wybiera BIC: dla jednego celu 3 parametry (kąt + amplituda zespolona), dla dwóch 6. RSS poniżej wartości maszynowej ograniczyć tylko dla logarytmu. Nie zmieniać siatki, minimalnej separacji, BIC ani progów po wyniku.

Metryki: odsetek wyboru dwóch celów, odsetek poprawnego rozdzielenia (dwa kąty, oba z błędem <=.25°), MAE przyporządkowanych kątów tylko dla wyboru dwóch (jawnie warunkowe), fałszywe rozdzielenia pojedynczych celów. Osobno według separacji i stosunku amplitud. Porównanie sparowane po przypadkach: tylko 2 kanały poprawne / tylko 1 kanał poprawny.

To idealizowany test modelu, nie gwarancja identyfikowalności ani sprzęt. Brak dryfu fazy, błędu enkodera, wielodrogowości i nieznanego kształtu wiązki; model dopasowania zna model generowania. R/v nie są zmieniane i nie są ponownie symulowane. Poprzednie wyniki zachowane. Zapis surowych I/Q w NPZ, decyzji i metryk w JSON, hash kodu i protokołu. Wyniki nie mogą być nadpisane.
