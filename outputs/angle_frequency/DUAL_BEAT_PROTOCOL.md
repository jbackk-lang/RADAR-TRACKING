# Dwie nośne i pik dudnienia

Po poleceniu zmniejszenia dudnienia o połowę dodano drugi przebieg: 77 i 57.75 GHz, różnica 19.25 GHz. Ta sama energia, odległości i szumy, 300 przypadków w każdym przebiegu. Uruchomienie: `python outputs/angle_frequency/run_dual_beat.py --half-beat`; pierwotny przebieg bez flagi. Oba wyniki zachowane osobno. To porównanie rozwojowe, nie nowy holdout.

77 i 38.5 GHz jednocześnie, taki sam impuls Gaussa (sigma 1.5 próbki) w obu pasmach. Całkowita energia obu nośnych równa energii jednej nośnej: amplituda każdej podzielona przez sqrt(2). 64 impulsy, 20 MHz próbkowania obwiedni, szum .15 na składową I/Q w każdym kanale. 100 losowych odległości dla silnego, słabego i silnego echa z dodatkową różnicą faz kanałów .7 rad. Te same szumy i odległości we wszystkich metodach. Filtr dopasowany we wszystkich wariantach.

Nośnych nie próbkujemy bezpośrednio z częstotliwością 20 MHz. Model zawiera analityczne fazy propagacji i osobno sprowadzone do pasma podstawowego kanały. Z sumy dwóch nośnych można otrzymać dudnienie; zespolony iloczyn kanału pierwszego ze sprzężonym drugim mierzy jego różnicę faz. Nie jest to wygenerowane wolne dudnienie w surowych próbkach ani model fizycznego mieszacza.

Porównujemy jedną nośną, sumę mocy dwóch kanałów, oraz tę sumę z wyborem najbliższej gałęzi odległości z fazy dudnienia. Dodatkowy wariant używa idealnej bezszumowej fazy: diagnozuje niejednoznaczność niezależnie od szumu. Faza dudnienia określa R modulo c/(2*38.5 GHz), nie bezwzględne R. Do wyboru gałęzi nie używamy prawdziwej odległości.

Model zakłada jednakową fazę odbicia w dwóch szeroko rozdzielonych pasmach, poza osobnym scenariuszem przesunięcia .7 rad. To korzystne założenie, nie gwarancja sprzętowa. Pomijamy różnice propagacji, anten, RCS, zakłócenia, wielodrogowość i detekcję bez celu. Nie obiecujemy poprawy R ani rozdzielczości. Skrypt chroni poprzednie wyniki przed nadpisaniem.
