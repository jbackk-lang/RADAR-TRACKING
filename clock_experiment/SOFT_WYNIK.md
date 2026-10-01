# Miękkie ważenie amplitudy i geometrii

**Pilotaż syntetyczny, 16 nowych przebiegów; średnie z 2 ziaren.** Sprawdzono te same cztery scenariusze, bez dobierania parametrów po wyniku. Standard i twarde sito są wynikami poprzedniego przebiegu na identycznych danych. Użyto wcześniejszych decyzji zegara: to samo wejście czasu/amplitudy, zweryfikowane hashe; nie powtarzano kosztownego dopasowania.

| Scenariusz | Standard RMSE [m] | Dawne twarde sito [m] | Sama geometria [m] | Geometria + amplituda [m] |
|---|---:|---:|---:|---:|
| clean | 0.01447 | 0.01469 | 0.01447 | 0.01447 |
| correlated | 0.20009 | 0.03291 | 0.18923 | 0.14442 |
| amplitude_only | 0.01447 | 0.03291 | 0.01447 | 0.01447 |
| position_only | 0.20009 | 0.20010 | 0.18923 | 0.18923 |

`clean`: brak dodatkowych zakłóceń; `correlated`: wspólny błąd pozycji i amplitudy; `amplitude_only`: błąd tylko amplitudy; `position_only`: błąd tylko pozycji.

## Wniosek z tego przebiegu

Przy wspólnym zakłóceniu hybryda osiąga 14,44 cm RMSE wobec 18,92 cm samej geometrii, ale twarde sito z poprzedniego testu było lepsze (3,29 cm). Przy błędzie samej amplitudy miękka hybryda zachowuje dokładność standardu (1,45 cm), zamiast pogarszać ją do 3,29 cm. Przy błędzie samej pozycji zegar niczego nie dodaje do geometrii. Nie ma jednego zwycięzcy we wszystkich warunkach; ten wariant pozostaje eksperymentalny, nie zastępuje domyślnie trackera ani poprzedniego sita.

## Reguła

Pomiar zgodny z predykcją do 0,12 m zachowuje pełną wagę bez względu na amplitudę. Powyżej progu geometria daje wagę 0,12/dystans. Hybryda dodatkowo podnosi wagę do kwadratu przy ostrzeżeniu amplitudowym. Waga nie spada poniżej 0,02. Żadna klatka nie znika z oceny. Punkt łączący predykcję i pomiar jest estymatą, nie surową obserwacją.

## Ograniczenia

Ręczny próg odpowiada skali tego syntetycznego testu; nie został zweryfikowany dla innych sensorów. Test nie obejmuje prawdziwych manewrów, błędnej asocjacji ani rzeczywistego radaru. Stały ruch i zgodna z zegarem modulacja są ułatwieniem dla modelu. Ten sam błąd amplitudy może mieć inne znaczenie w realnym pomiarze. Wynik nie dowodzi uniwersalnej przewagi zegara nad geometrią. Nowe czasy w JSON wykluczają dopasowanie zegara; dawny koszt zegara podano osobno, więc nie deklarujemy tu przyspieszenia pełnej hybrydy.

Kod: `soft_fusion.py`. Uruchomienie z repo: `python -m clock_experiment.run_soft_fusion`, potem `python -m clock_experiment.report_soft`. Benchmark nie nadpisuje istniejącego podsumowania. Protokół: `SOFT_PROTOCOL.md`. Wszystkie predykcje i wejściowe hashe: `soft_results/`.

Weryfikacja: 11 testów jednostkowych integracji/przełączania/fuzji przeszło; ponownie przeliczono RMSE wszystkich 16 przebiegów i sprawdzono granice wag oraz hashe. Nie jest to ponowne uruchomienie całego historycznego zestawu testów repo.
