# Końcowy test: co jeszcze daje matematyka kształtu echa

Bank Gaussa, wykładniczych ogonów i dwóch odbić z automatyczną oceną dopasowania i zgodności początku. Parametry/progi zapisane przed nowymi600scenami;220 osobnych scen kalibracyjnych. Nie korzystano z prawdziwego R do wyboru modelu.

| Scena (100 prób każda) | Pik: poprawne R | Bank: poprawne R | Bank: błędne R | Bank: brak R | MAE zwróconych R banku [m] |
|---|---:|---:|---:|---:|---:|
| Gauss | 100 | 99 | 0 | 1 | 0.700 |
| Ogon tau8 | 10 | 99 | 0 | 1 | 1.082 |
| Dwa odbicia | 1 | 96 | 0 | 4 | 0.636 |
| Słaby przód | 0 | 28 | 18 | 54 | 14.975 |
| Nieznany ogon odbiornika | 0 | 0 | 78 | 22 | 18.918 |

MAE obejmuje wszystkie zwrócone R, także błędne, ale nie odrzucenia. Poprawne oznacza błąd<7.5m. W100 nowych pustych scenach bank nie zwrócił R, baseline pik/Gauss zwrócił2fałszywe pomiary. Nie gwarantuje to zera alarmów w sprzęcie.

Dla trzech znanych rodzin:294/300 poprawnych,6 odrzuconych,0 błędnych. To korzystne dopasowanie rodzin generatora do banku, nie uniwersalna skuteczność. W trudnych przypadkach bramki nie zapewniły wiarygodności: nieznany odbiornik bywał interpretowany jako inny znany kształt, a niewidoczny przód jako późniejsze czoło. Dobry wynik reszty i zgodność modeli nie gwarantują prawdziwego początku.

Łącznie w500scenach z celem:bank322poprawne,96błędnych,82odrzucone; pik111poprawnych,389błędnych. Tego zestawienia nie traktujemy jako uniwersalnej średniej: zależy od sztucznie ustalonej częstości scen. Pojedynczy Gauss był dobry dla prawdziwego Gaussa, ale nie dla pozostałych rodzin.

## Wniosek praktyczny

Z obecnego I/Q można wyciągnąć więcej niż z samego piku: podpróbkowy czas i dopasowanie kilku składowych są użyteczne. Nie ma podstaw, by zakończyć temat deklaracją gotowego niezawodnego rozwiązania. Największa nierozwiązana przeszkoda to rozdzielenie odpowiedzi instrumentu od odpowiedzi obiektu oraz brak informacji o zbyt słabym przodzie.

Następny uzasadniony krok: pomiar i kalibracja impulsowej odpowiedzi odbiornika oraz test rzeczywistych ech rozciągłych obiektów. Dalsze zwiększanie liczby modeli na tym generatorze może poprawiać liczby bez poprawy na sprzęcie. Szersze pasmo i dodatkowe niezależne kanały mogą dostarczyć informacji, której tutaj brakuje, ale wymagają osobnej walidacji.

Ostateczny test tego wariantu zakończony; nie jest to ostateczna granica radarowej informacji. Brak sprzętu, ruchu w tym banku, pełnej wielodrogowości i polaryzacji. Główny tracker bez zmian. Kontrole odzyskania początku Gaussa i ogona w granicy bezszumowej przeszły.

Protokół FINAL_ECHO_PROTOCOL.md; wszystkie decyzje final_echo_results.json. Uruchomienie `python outputs/angle_frequency/run_final_echo.py`, chroni istniejące wyniki.
