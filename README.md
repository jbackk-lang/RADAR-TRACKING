# RADAR-TRACKING — zobacz, jak program śledzi obiekty

Program odbiera kolejne punkty pomiarowe, łączy je w ślady i ocenia, czy obiekt zmienia ruch. Demo pozwala obejrzeć to w przeglądarce i porównać trzy warianty śledzenia.

**Na początek potrzebujesz tylko Pythona i tego katalogu. Nie potrzebujesz radaru.** Demo generuje sztuczne obiekty i zaszumione pomiary. Nie łączy się ze sprzętem i nie potwierdza jego dokładności.

## Pierwsze uruchomienie w Windows

1. Zainstaluj Python, jeśli go nie masz. W instalatorze zaznacz dodanie Pythona do PATH.
2. Otwórz katalog repozytorium, np. `C:\Users\jback\Downloads\a\RADAR-TRACKING`.
3. Otwórz w nim PowerShell: kliknij pasek adresu Eksploratora, wpisz `powershell` i naciśnij Enter.
4. Jednorazowo zainstaluj potrzebne biblioteki:

```powershell
python -m pip install -r requirements.txt
```

5. Dwukrotnie kliknij **Uruchom_demo.bat** albo wpisz:

```powershell
python web_demo.py
```

Otworzy się przeglądarka pod adresem `http://127.0.0.1:8765/`. Zostaw okno uruchamiające program otwarte — obsługuje demo. Wszystko działa lokalnie na Twoim komputerze.

## Co kliknąć i na co patrzeć

1. Wybierz model, scenę oraz 4, 8 lub 12 obiektów.
2. Kliknij **Uruchom analizę**.
3. Odtwarzaj ruch lub przesuwaj czas. Włącz widok odniesienia, aby porównać wynik z pozycjami zadanymi przez symulator.

Punkty pomiarowe zawierają szum. Ślady i ich numery pokazują obiekty rozpoznane przez program. Przewidywane położenie pokazuje, dokąd może przesunąć się ślad. Liczba śladów może różnić się od liczby obiektów: obiekt może zniknąć, a fałszywe odbicie utworzyć dodatkowy ślad. Liczbę prawdziwych obiektów znamy tylko dlatego, że sami wygenerowaliśmy scenę.

W tabeli TIMDR wyższy wynik oznacza silniejszą oznakę zmiany ruchu. **Nie jest to procent pewności.** Przy bardzo krótkiej historii odporny wariant nie ma jeszcze danych do oceny; zerowy wynik nie potwierdza wtedy ruchu prostego.

## Który model wybrać

| Wariant | Co robi | Kiedy go użyć |
|---|---|---|
| Standard CV | Zakłada kontynuację dotychczasowego ruchu, bez TIMDR | Punkt odniesienia do porównania |
| TIMDR dotychczasowy | Ocenia zmianę kierunku i prędkości oraz wpływa na przewidywanie i łączenie pomiarów | Domyślna opcja |
| TIMDR odporny | Uwzględnia czas i zakładany błąd położenia; ogranicza wpływ pojedynczych błędnych punktów | Eksperymentalna opcja do porównań |

TIMDR wnosi ocenę zmian ruchu do decyzji trackera. TRM pomaga odrzucać niespójne punkty, a GIA ocenia kierunek. To radarowa adaptacja tych idei, nie pełna implementacja całego formalizmu. Użycie klasycznych metod matematycznych nie odbiera wartości integracji; jej przewagę trzeba jednak mierzyć.

**Odporny TIMDR nie jest zawsze najlepszy.** W nowych, trudniejszych symulacjach wszystkie warianty radziły sobie podobnie ze zwykłym szumem. Przy dodatkowych odbiciach dotychczasowy TIMDR lepiej utrzymywał numery obiektów. Dlatego pozostaje domyślny.

[Wyniki trudniejszych symulacji](outputs/angle_frequency/WYNIK_REALISTIC_TIMDR.md) zawierają błędy, brakujące ślady, dodatkowe ślady i zmiany numerów. Test obejmuje 40 sekwencji oraz 120 przebiegów na identycznych danych. To symulacje detekcji z szumem, zanikami i zakłóceniami — **nie rzeczywiste nagrania radaru ani pełna symulacja fal**. W repo nie ma danych potrzebnych do starego testu rzeczywistych przejazdów.

## Gdy coś nie działa

| Objaw | Co zrobić |
|---|---|
| System nie znajduje `python` | Spróbuj `py` zamiast `python`; jeśli też nie działa, zainstaluj Python i dodaj go do PATH |
| Brakuje `numpy`, `scipy` lub `matplotlib` | Wykonaj polecenie instalacji bibliotek powyżej |
| Port jest zajęty | Uruchom `python web_demo.py --port 8766` |
| Nie otworzyła się przeglądarka | Otwórz adres wypisany w oknie programu |
| Po aktualizacji widzisz starą wersję | Zatrzymaj program przez Ctrl+C, uruchom ponownie i odśwież stronę przez Ctrl+F5 |

Aby zakończyć pracę, naciśnij **Ctrl+C** w oknie programu. Samo zamknięcie karty przeglądarki nie zatrzymuje serwera.

## Gdzie znaleźć więcej

- [Historia zmian i eksperymentów](HISTORY.md) — wcześniejsze pomysły, wyniki i ograniczenia.
- [Instrukcja techniczna](docs/TECHNICAL.md) — własne dane, ustawienia, testy i odtwarzanie eksperymentów.
- [Pierwsze sprawdzenie odpornego TIMDR](outputs/angle_frequency/WYNIK_TIMDR_ROBUST.md) — test samego operatora i łatwiejszych scen.
- [Warunki wykorzystania](LICENSE) — prawa do tego kodu.

Folder `web` zawiera interfejs, `core` algorytmy, `tests` testy, a `outputs` protokoły i wyniki eksperymentów. Do uruchomienia demo nie musisz ich edytować.
