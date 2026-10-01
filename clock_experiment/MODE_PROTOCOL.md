# Kandydat M/S–K: rytm błysków, test odłożonego fragmentu

Eksploracja po wykryciu błysków, nie potwierdzona tożsamość gałęzi TIMDR. Używamy wszystkich czterech zapisanych śladów, bez zmiany detektora. Jednoczesne zdarzenia w różnych binach redukujemy do jednego czasu klatki, aby nie mnożyć dowodów tego samego zdarzenia. Nie rozdzielamy tu kilku potencjalnych źródeł Dopplera.

Pierwsze ceil(Nciągłych_fragmentów/2) fragmenty: dopasowanie; reszta: ocena. Wymagamy >=6 różnych czasów zdarzeń w każdej części. Kandydat: stała częstość .1..4 Hz, 4096 punktów, maksymalizacja długości średniego wektora exp(i2pi f t) na train. Faza = argument tego wektora. Test = średnia cos(2pi f t - faza_train) na eval. Nie dopasowujemy ponownie częstości ani fazy i nie bierzemy wartości bezwzględnej, która ukryłaby przeciwną fazę.

Kontrola 999 losowań z seed 20261002. W każdym odłożonym ciągłym fragmencie zachowujemy liczbę unikalnych zdarzeń, losujemy ich położenia spośród faktycznie dostępnych klatek bez zwracania. Nie wypełniamy luk. Dopasowany na train kandydat pozostaje stały. Jednostronne p=(1+liczba null>=score)/1000; Bonferroni x4 dla czterech śladów. Próg eksploracyjny p_corr<.05 i score>0. Brak mocy przy małej liczbie zdarzeń nie oznacza nieistnienia modu.

To test stałego rytmu zdarzeń z fazą przenoszoną przez luki. Brak sukcesu nie wyklucza dryfu, wielu rytmów ani błędów detektora. Ewentualny sukces nie identyfikuje łopaty ani fizycznego modu K; wymaga nowych nagrań i odniesienia fizycznego. Detektor tła używa całego własnego fragmentu, lecz fragmenty train/eval są rozłączne. Dane z poprzednich eksploracji były już oglądane.
