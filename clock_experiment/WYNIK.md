# Test zegara: RADAR-TRACKING, 2026-09-30

Właściwe repo: https://github.com/jbackk-lang/RADAR-TRACKING . Bazowy commit: 74916877dd0982b7dfef7f3c4921999e0ba3d275.

Dodano opcjonalny kanał amplitudy przypisany do istniejących ID obiektów. Rdzeń geometrii pozostaje bez zmian. Zegar jest kopią modułu astronomicznego, zgodność SHA-256 sprawdzona.

| Sygnał | Ziarno | Status | MAE zegara [Hz] | MAE stałej częstości [Hz] | Dopasowanie zegara [s] |
|---|---:|---|---:|---:|---:|
| accelerating | 0 | accepted_model | 0.001158 | 0.101295 | 3.45 |
| accelerating | 1 | accepted_model | 0.000185 | 0.101295 | 2.99 |
| noise | 0 | unreliable | - | - | 2.95 |
| noise | 1 | unreliable | - | - | 2.64 |

Błąd dotyczy ostatnich 100 próbek, których nie użyto do dopasowania (pierwsze 300 próbek). Wszystkie cztery przebiegi zachowały jedno ID toru. Kontrola z samym szumem nie ma prawdziwej częstości, więc nie przypisano jej fikcyjnego błędu Hz. Wszystkie estymacje, również odrzucone, zapisano w JSON.

To mały test syntetyczny, z generatorem zgodnym z modelem zegara i zadanymi granicami wyszukiwania. Nie dowodzi poprawy prędkości postępowej ani identyfikacji fizycznych obrotów. Nie jest testem na prawdziwej amplitudzie radarowej. Wynik 7,6% z poprzedniego repo nie odnosi się do tego eksperymentu.

Testy: 44 passed (41 istniejących oraz 3 nowe). Pełna kolekcja zgłasza brak data.validate_on_real_trips w istniejącym teście rzeczywistych tras; uruchomiono pozostałe testy z jawnym pominięciem tego pliku. Nie twierdzimy, że cały zestaw bazowego repo przeszedł. Zwrócono także istniejące ostrzeżenie o itertools.

Ścieżka lokalnej kopii repo: C:/Users/jback/Documents/Codex/2026-09-29/filtracja-w-przestrzeni/outputs/RADAR-TRACKING . Utworzenie katalogu Downloads/a/RADAR-TRACKING zostało zablokowane przez system plików; praca została zapisana w katalogu wyników. Nie wykonano commit ani push.

Następny test rzeczywisty wymaga amplitudy echa przypisanej do toru, czasów w sekundach i niezależnego odniesienia okresu/obrotów. Pozycje GPS same nie dostarczają zegara amplitudy.
