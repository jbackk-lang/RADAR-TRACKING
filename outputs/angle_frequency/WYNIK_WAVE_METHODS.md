# Bliskie nośne, chirp i rezonans przy odbiciu

Automatyczny detektor zwraca odległość tylko po przekroczeniu progu. Progi zamrożono na 300 osobnych scenach szumu dla każdej metody; sprawdzono na 600 nowych scenach. Energia nadawania jednakowa.

| Metoda | Silne echo: MAE poprawnych [m] | Słabe: poprawne /100 | Zakłócenie impulsowe: poprawne /100 | Alarmy bez celu /200 |
|---|---:|---:|---:|---:|
| Impuls, filtr dopasowany | 1.828 | 97 | 0 | 3 |
| 77 i 76.999 GHz | 0.899 | 73 | 0 | 0 |
| Chirp 10 MHz | 1.835 | 97 | 51 | 5 |
| Chirp, rezonans w odbiorniku | 1.865 | 39 | 3 | 0 |
| Chirp, rezonans w odbiciu | 2.147 | 6 | 0 | 1 |

Silne echo wykryto poprawnie w 100/100 przypadkach pierwszych czterech metod i 99/100 rezonansu odbicia. MAE w tabeli jest warunkowe: nie zawiera odrzuconych ani błędnie zlokalizowanych obserwacji. Alarmy bez celu są zmierzonymi częstościami na ograniczonej próbie; 0/200 nie oznacza gwarancji braku alarmów.

Bliskie nośne poprawiły silne, skalibrowane echo o około 51% w MAE R, ale pogorszyły wykrywanie słabego echa. Przesunięcie między kanałami .7 rad spowodowało 0/100 poprawnych odległości mimo 100/100 wykryć. Odpowiada ono około 16.7 m błędu fazowej odległości. Metoda wymaga wspólnej synchronizacji i kalibracji faz, a faza odbicia celu też może zależeć od częstotliwości.

Chirp pomógł przy zakłóceniu impulsowym: 51/100 poprawnych zamiast 0/100. Nie uzyskał poprawy MAE R dla izolowanego silnego echa w użytej siatce próbkowania. Zmienił długość i pasmo impulsu; rezultat nie jest dowodem przewagi wszystkich chirpów nad wszystkimi impulsami.

Na życzenie rezonans umieszczono w odbiciu, przed szumem odbiornika. Pasywny model nie dopisuje energii: |H(f)|<=1. Detektor zna odpowiedź rezonansową celu, co jest korzystnym założeniem. Taki wąskopasmowy model odrzucił część energii chirpu i pogorszył wykrywanie. To nie dowodzi, że każdy fizyczny rezonans szkodzi ani że nie może zwiększać odbicia względem konkretnego nierezonującego celu. Nie modelowano rzeczywistego wzrostu przekroju radarowego, geometrii celu ani fizycznego skrętu anteny.

Kontrole: poprawna lokalizacja bezszumowego rezonansowego echa, ograniczenie energii pasywnego filtra, |H(f)|<=1 oraz deterministyczne odtworzenie. Wyniki pierwotnych czterech metod zachowane w wave_methods_results.json; pięciu metod w wave_reflection_results.json. Szczegóły WAVE_METHODS_PROTOCOL.md. Odtworzenie: `python outputs/angle_frequency/run_wave_methods.py --reflection`; chroni istniejący wynik przed nadpisaniem.

Główny tracker bez zmian. Ruch, v, kąt, wielodrogowość i sprzęt nie były walidowane. Najbardziej uzasadniony kierunek dalszej pracy: chirp z odrzucaniem zakłóceń oraz fazowe doprecyzowanie R wyłącznie przy wiarygodnej kalibracji.
