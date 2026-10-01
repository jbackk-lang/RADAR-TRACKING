# Wspólny model trzech skanów, potwierdzenie na czwartym

Stałe kąty, zmienne zespolone amplitudy i fazy; 60 sekwencji, 240 skanów, dwa kanały. Czwarty skan nie służy do dobierania kątów wieloskanowego modelu. Niezależny wariant bazowy dopasowuje wyłącznie skan 4.

| Warunki | Przypadki | Wieloskanowy poprawny | Jeden skan poprawny | Odmowy wieloskanowego |
|---|---:|---:|---:|---:|
| pair | 30 | 30 | 30 | 0 |
| single | 10 | 10 | 10 | 0 |
| disappear | 10 | 0 | 10 | 8 |
| appear | 10 | 0 | 10 | 0 |

Poprawność: liczba celów zgodna z prawdą skanu 4 i wszystkie kąty z błędem <=.25°. Odmowa oznacza brak potwierdzonych kątów, nie usunięcie toru. Przy zaniku lub pojawieniu celu założenie stałych celów nie jest spełnione. To osobne kontrole ograniczeń pamięci, nie dane do strojenia.

Nie wykazujemy uniwersalnej przewagi. Model wieloskanowy wykorzystuje więcej danych i zna idealny model wiązki. Brak ruchu, wielodrogowości, błędów synchronizacji i rzeczywistego sprzętu. Pojawienie nowego celu wymaga uruchomienia nowego dopasowania, nie samego potwierdzania starych kątów.

Odtwarzanie: python run_multiscan.py w osobnej kopii bez multiscan_results.json i multiscan_iq.npz. Surowe I/Q zapisane; wyniki chronione przed nadpisaniem.
