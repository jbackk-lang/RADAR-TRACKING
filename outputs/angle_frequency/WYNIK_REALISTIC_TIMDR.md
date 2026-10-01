# TIMDR w trudniejszych symulacjach

**Wniosek: odporny operator nie daje uniwersalnej poprawy całego trackera. Dotychczasowy TIMDR pozostaje domyślny.**

40 sekwencji (5 scen × 8 ziaren), po 40 klatek i 4 obiekty. CV, dotychczasowy TIMDR i odporny TIMDR przetwarzają identyczne detekcje: łącznie 120 przebiegów. Protokół zapisano przed przebiegiem; parametrów po wynikach nie strojono.

| Scena | Wariant | MAE dopasowanych [m] | Brak dopasowania [%] | Dodatkowe ślady / klatkę | Zmiany ID / sekwencję |
|---|---|---:|---:|---:|---:|
| Szum pomiarowy | CV | 0.4567 | 0.00 | 0.000 | 0.000 |
| Szum pomiarowy | TIMDR dotychczasowy | 0.4567 | 0.00 | 0.000 | 0.000 |
| Szum pomiarowy | TIMDR odporny | 0.4567 | 0.00 | 0.000 | 0.000 |
| Zaniki pomiarów | CV | 0.5240 | 28.67 | 0.009 | 1.625 |
| Zaniki pomiarów | TIMDR dotychczasowy | 0.5261 | 29.06 | 0.025 | 1.875 |
| Zaniki pomiarów | TIMDR odporny | 0.5236 | 29.22 | 0.031 | 1.750 |
| Dodatkowe odbicia | CV | 0.4699 | 0.39 | 0.381 | 3.750 |
| Dodatkowe odbicia | TIMDR dotychczasowy | 0.4562 | 0.08 | 0.369 | 0.250 |
| Dodatkowe odbicia | TIMDR odporny | 0.4720 | 0.39 | 0.381 | 4.250 |
| Bliskie krzyżowanie | CV | 0.4524 | 0.00 | 0.000 | 0.000 |
| Bliskie krzyżowanie | TIMDR dotychczasowy | 0.4524 | 0.00 | 0.000 | 0.000 |
| Bliskie krzyżowanie | TIMDR odporny | 0.4524 | 0.00 | 0.000 | 0.000 |
| Nieregularny czas i większy szum | CV | 0.9726 | 9.06 | 0.363 | 64.750 |
| Nieregularny czas i większy szum | TIMDR dotychczasowy | 0.9228 | 5.62 | 0.225 | 12.625 |
| Nieregularny czas i większy szum | TIMDR odporny | 0.9490 | 7.42 | 0.297 | 39.875 |

## Co z tego wynika

Przy zwykłym szumie i zadanym krzyżowaniu wszystkie trzy warianty mają identyczne wyniki. Ten test krzyżowania nie wykazał różnicy — nie jest dowodem odporności na wszystkie nierozdzielone cele.

Przy dodatkowych odbiciach dotychczasowy TIMDR ma średnio 0,25 zmiany ID na sekwencję, odporny 4,25, a CV 3,75. Odporny wypada tu gorzej od obu porównań. Przy nieregularnym czasie i większym szumie odporny ma mniej zmian ID niż CV (39,875 wobec 64,75), ale więcej niż dotychczasowy (12,625). Przy zanikach ma minimalnie mniejszy MAE, lecz więcej brakujących dopasowań i dodatkowych śladów niż CV. Nie wybieramy zwycięzcy na podstawie samego MAE.

Poprzedni test wykazał poprawę rozpoznawania manewrów przez sam operator. Obecny pokazuje, że jego połączenie z bramkowaniem i predykcją wymaga dalszej pracy. Progi oraz skala wyników obu operatorów różnią się; wynik opisuje kompletne warianty przy obecnych ustawieniach, nie przewagę każdej możliwej konfiguracji.

## Zakres i odtwarzanie

Szum odległości i kąta, skorelowany błąd położenia, trzy odbicia na obiekt, zaniki, fałszywe grupy i nieregularny czas. W ostatniej scenie niepewność podana odpornemu operatorowi celowo nie odpowiada większemu szumowi. Nie symulujemy propagacji RF, pełnego skanu anteny ani fizycznego sprzętu. Nie są to rzeczywiste dane radarowe.

MAE obejmuje tylko pozycje dopasowane do prawdy z bramką 2 m. Braki liczone są względem wszystkich czterech obiektów, również w czasie zaniku echa. Zmiany ID uwzględniają ponowne pojawienie się po przerwie. Liczby w tabeli to średnie z ośmiu sekwencji, bez przedziałów ufności; próba jest mała.

[Protokół](REALISTIC_TIMDR_PROTOCOL.md), [wyniki i hashe danych wejściowych](realistic_timdr_results.json), [skrypt](run_realistic_timdr.py).

```powershell
python outputs/angle_frequency/run_realistic_timdr.py
```

Skrypt chroni istniejący plik wyników przed nadpisaniem. Do kolejnego przebiegu zachowaj poprzedni wynik i wybierz nową lokalizację zapisu w kopii skryptu.
