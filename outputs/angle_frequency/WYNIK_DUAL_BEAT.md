# Dudnienie dwóch nośnych i zmniejszenie go o połowę

Zrealizowano model dwóch jednoczesnych impulsowych nośnych. Oceniono pik czasu powrotu jak w echosondzie i dodatkową fazę dudnienia. Energia łączna jest stała: dodanie drugiej nośnej dzieli energię między dwa kanały.

| Para nośnych | Dudnienie | Okres niejednoznaczności R | MAE R silnego echa z fazą dudnienia |
|---|---:|---:|---:|
| 77 + 38.5 GHz | 38.5 GHz | 3.893 mm | 1.89247 m |
| 77 + 57.75 GHz | 19.25 GHz | 7.787 mm | 1.89267 m |

Jedna nośna z filtrem dopasowanym: MAE silnego echa 1.89253 m. Zmniejszenie dudnienia o połowę podwoiło odstęp powtarzających się faz, lecz nie poprawiło bezwzględnej odległości. W obu wariantach idealna, bezszumowa faza wybrała prawidłową gałąź tylko w 1/100 silnych przypadków. Główną przeszkodą jest niejednoznaczność: zgrubny pomiar ma błąd metrów, a faza powtarza się co kilka milimetrów.

Słabe echo: jedna nośna MAE 529.87 m, pierwotna para z dudnieniem 885.55 m, para z połową dudnienia 856.07 m. Oba podziały energii pogorszyły wynik względem jednej nośnej w tym modelu. Maksimum bez progu detekcji może wybrać szum; te duże błędy nie oznaczają wiarygodnego wykrycia celu. Małych różnic przy zmianie fazy kanału nie traktujemy jako zalety częstotliwości.

600 realizacji łącznie, 300 na parę nośnych. Nie próbkowano bezpośrednio GHz przy 20 MHz; analityczne fazy propagacji i osobno zdemodulowane I/Q pozwalają obliczyć różnicę faz. Dwa pasma wymagają osobnych odpowiednich torów odbiorczych. Model zakłada taką samą fazę odbicia w obu pasmach, poza przypadkiem dodatkowego przesunięcia .7 rad; rzeczywisty cel nie musi spełniać tego założenia.

Sprawdzono okresowość fazy odległości oraz ograniczenie przesunięcia po wyborze najbliższej gałęzi do połowy okresu. Wyniki zapisano w dual_beat_results.json i dual_half_beat_results.json. Główny tracker pozostaje bez zmian. Nie wykazano poprawy odległości ani usuwania zakłóceń przez dudnienie.
