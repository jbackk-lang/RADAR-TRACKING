# Kąt z obrotu i czasu — protokół przed testem

Osobna, idealizowana symulacja obracającej się kierunkowej anteny. Znany początek obrotu, nominalnie 1 obrót/s, wiązka o FWHM mocy 1.5 stopnia. Odstęp próbek echa .2 ms, obserwacja .5 s. Cel nieruchomy, izolowany, odległość 1500 m. I/Q z zespolonym szumem .1 na składową. Enkoder z próbkami co .2 ms, szum .02 stopnia; bez błędu zera i bez pełnego modelu mechanicznego.

200 ziaren × kąty [.4,1.2,2.] rad × 3 scenariusze = 1800 przypadków. Scenariusze: stały obrót; prędkość obrotu zmienia się sinusoidalnie o ±5% (2 Hz, losowa faza); taki sam zmienny obrót i nieskorygowane przesunięcie zegara echa +2 ms względem enkodera. Czas przelotu 2R/c jest jawnie uwzględniany. Algorytm dostaje zmierzoną odległość równą 1500 m w tym eksperymencie; nie dostaje kąta celu ani fazy zmian obrotu.

Metody: omega_nominalna×czas maksimum echa; interpolowany enkoder dla maksimum echa; średni kąt enkodera ważony mocą echa w oknie ±3 szerokości wiązki wokół maksimum. Poziom tła estymowany jako mediana mocy / ln(2); ujemne wagi zerowane. Dane echa i enkodera identyczne dla wszystkich metod. Zapisać MAE, P95, wszystkie estymaty, hash protokołu i kodu. Brak strojenia po ocenie. Testy: znany obrót bez szumu, wpływ przesunięcia czasu, brak rozróżnienia kąta i błędu zera enkodera.

To wymaga obserwacji echa w trakcie przejścia wiązki oraz czasu i położenia anteny, których nie ma w starych danych. Nie deklarować, że metoda działa na starym pojedynczym I/Q ani że nie potrzebuje danych o obrocie. Wynik odnosi się do izolowanego celu i idealizowanej wiązki bez listków bocznych; nie pełny skan wielu celów ani walidacja sprzętowa. MAE nie porównywać bezpośrednio z innym modelem częstotliwościowym jako dowodu wyższości sprzętu.
