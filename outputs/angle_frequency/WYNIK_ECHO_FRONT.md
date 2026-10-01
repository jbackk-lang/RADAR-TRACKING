# Czoło zamiast dominującego piku

400 nowych scen po zamrożeniu progu na200 osobnych scenach szumu. Odległość prawdziwa oznacza najbliższą powierzchnię. Dwa odbicia sumowane zespolenie z losową różnicą faz.

| Scena | Dominujący pik: poprawne czoło /100 | Pierwszy wiarygodny pik: poprawne czoło /100 | MAE R dominujący [m] | MAE R pierwszy [m] |
|---|---:|---:|---:|---:|
| Przód .8, tył1, rozciągłość30m | 0 | 56 | 28.318 | 12.240 |
| Słaby przód .15, tył1, rozciągłość30m | 0 | 0 | 29.987 | 29.987 |
| Nierozdzielone powierzchnie5m | 88 | 88 | 4.193 | 4.257 |

Wszystkie sceny z obiektem wykryte100/100. To nie znaczy, że wykryto czoło: słaby przód pozostał niewidoczny, a oba algorytmy wskazały tył.100 nowych pustych scen:0 alarmów w obu metodach, bez gwarancji braku alarmów w rzeczywistości.

Pierwszy wiarygodny lokalny pik pomógł w56/100 przypadkach mocniejszego przodu. Przy tej szerokości odpowiedzi powierzchnie mogą się zlewać, a interferencja może stłumić przednie odbicie. Wybór pierwszego piku nie rekonstruuje utraconej informacji. Przy5m brak rozdzielenia; poprawność z tolerancją7.5m nie dowodzi osobnego wykrycia przedniej powierzchni.

R zmieniło definicję względem modeli punktowych: tutaj najbliższa powierzchnia, nie środek ani dominujący reflektor. Nie porównujemy bezpośrednio tych błędów z wcześniejszymi MAE punktowych celów. Brak ruchu, zakłóceń impulsowych i sprzętu. To nie jest jeszcze tarcza obiektu ani estymacja kierunku. Główny tracker bez zmian.

Kontrole wyboru pierwszego i najsilniejszego piku oraz odrzucenia profilu bez piku przeszły. Protokół ECHO_FRONT_PROTOCOL.md; pełne wyniki echo_front_results.json. Odtworzenie `python outputs/angle_frequency/run_echo_front.py`, chroni istniejące wyniki.
