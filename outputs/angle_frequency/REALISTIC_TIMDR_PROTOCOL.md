# Realistyczniejsze symulacje detekcji — przed przebiegiem

To symulacje, nie pomiary rzeczywistego radaru ani pełna symulacja elektromagnetyczna. W repo brakuje data/real_trips_sample.csv i data/validate_on_real_trips.py wskazywanych przez stary test, więc nie potwierdzamy deklarowanej w nim walidacji GPS.

5scen po8nowych ziaren,40klatek,4obiekty:szum pomiarowy,zaniki,fałszywe grupy/ghosty,bliskie krzyżowanie,nieregularny czas z nieznanym większym szumem. Każda scena zawiera ruch stały,skręt,stop-and-go i obiekt nieruchomy, z wyjątkiem skrzyżowania zmieniającego dwie trajektorie. Położenia obserwowane przez szum odległości(.3m) i kąta(.002rad), zależny od dystansu błąd poprzeczny; wspólna skorelowana odchyłka AR(1)rho.8 i3echa powierzchni po.1m. Nie symulujemy propagacji RF ani pola anteny.

Zaniki:niezależna utrata20%obiektów na klatkę,6klatek utraty jednego celu i3puste klatki. Zakłócenia:2pojedyncze fałszywe punkty/klatkę i losowa para fałszywych odbić przesunięta o[5,4]m. Scena nieregularna:odstępy czasu.15–.85s,sigma radialna1m,kąt.006rad,operatorowi nadal ustawiono sigma.4m — celowe naruszenie założenia znanej niepewności.

CV,legacy irobust dostają dokładnie te same detekcje i czasy; żadnej prawdy w trackerze. Identyczne grupowanie i parametry:dmax1.2,kmin1,sigma0=1.5,gate30,smoothing.7,history10,prune2s,robust position_sigma.4m. Brak strojenia po wynikach.

Ocena każdej klatki przez Hungarian do wszystkich prawdziwych4obiektów z bramką2m (nie tylko widocznych). Raport:MAE dopasowanych pozycji,odsetek brakujących dopasowań,nadmiar śladów niepasujących do prawdy,zmianyID po kolejnych widocznych dopasowaniach. ZmianaID po zaniku również liczona. MAE jest warunkowy, nie wolno interpretować mniejszego MAE przy wielu odrzuceniach jako ogólnej przewagi.

Wynik opisowy per scena,bez deklaracji uniwersalnej równoważności lub nowego kryterium wdrożeniowego. Opcja robust pozostaje eksperymentalna nawet gdy wyniki będą dobre.40sekwencji to mały stress-test, nie holdout rzeczywistego sprzętu. Dane wejściowe odtwarzalne z ziaren, zapisujemy ich SHA256 i kompaktowe metryki zamiast dużych surowych logów. Głównych progów po tym teście nie zmieniamy.
