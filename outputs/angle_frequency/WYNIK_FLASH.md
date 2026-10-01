# Błysk energii przy odbiciu — granica idealnego modelu

Na polecenie użytkownika zamodelowano specjalny reflektor: zwraca tę samą energię w krótszym impulsie (sigma .5 próbki). Nie jest to uzyskane z pasywnego filtra rezonansowego. Założono kształtowanie odpowiedzi, brak strat oraz znaną stałą zwłokę 600 ns, odejmowaną od czasu pomiaru. Nie pokazano sposobu wykonania takiego reflektora ani możliwości wymuszenia go na dowolnym celu.

| Metoda | Silne: MAE R poprawnych [m] | Słabe: poprawne /100 | Słabe: MAE R poprawnych [m] | Impulsowe zakłócenie: poprawne /100 | Alarmy bez celu /200 |
|---|---:|---:|---:|---:|---:|
| Impuls odniesienia | 1.828 | 97 | 2.445 | 0 | 3 |
| Chirp | 1.835 | 97 | 2.477 | 51 | 5 |
| Błysk | 1.820 | 98 | 1.933 | 0 | 0 |

Błysk zmniejszył warunkowy MAE R słabego echa o około 21% względem impulsu. Nie uzyskano istotnego skoku liczby wykryć (98 zamiast 97), ani odporności na zakłócenie impulsowe. Te same piki, które pomagają mierzyć czas, mogą upodobnić echo do zakłócenia.

Progi zamrożone na osobnych 300 obserwacjach szumu, test 600 obserwacji. MAE tylko poprawnych wykryć; nie obejmuje odrzuceń i błędnych lokalizacji. 0/200 alarmów to wynik próbki, nie gwarancja. Krótsza odpowiedź potrzebuje szerszego pasma, a w tym dyskretnym modelu zbliża się do granicy próbkowania. Nie zwalidowano sprzętu, ruchu, kąta, v ani wielodrogowości.

Najważniejsze ryzyko: nieznana zwłoka samego błysku. Bez odjęcia 600 ns błąd R wynosiłby 89.94 m. Zmienność zwłoki o 50 ns oznacza 7.49 m błędu. Błysk musi mieć stabilny, skalibrowany czas odpowiedzi, aby rzeczywiście pomagał.

Sprawdzono energię wzorca =1 i bezszumowy pomiar z kompensacją znanej zwłoki. Protokół FLASH_PROTOCOL.md, pełne wyniki wave_flash_results.json; odtworzenie `python outputs/angle_frequency/run_wave_methods.py --flash` chroni istniejące wyniki. Główny tracker bez zmian.
