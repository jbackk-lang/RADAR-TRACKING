# Mały test połączenia kąta ze skanu z torem R/v

150 przypadków, 10 ziaren i 3 kąty. W torze pomiarowym zastąpiono wpisany kąt wynikiem enkoder+środek wiązki; wyłączono dodatkową korektę kąta. R i v są dokładnie zgodne z dotychczasowym torem dla tych samych I/Q (150 sprawdzeń). Błąd pomiaru R uwzględniono przy wyrównaniu czasu przelotu.

| Warunki | MAE kąta [°] | P95 [°] |
|---|---:|---:|
| single | 0.0282 | 0.0674 |
| clock_0.1ms | 0.0400 | 0.0989 |
| clock_2ms | 0.7190 | 0.7959 |
| pair_0.75deg | 0.3703 | 0.4021 |
| pair_3deg | 1.4601 | 1.5115 |

Dwa cele są równie silne i nierozdzielone w R/v. Estymator zwraca jeden kąt: środek wspólnej wiązki może leżeć między celami. To błąd względem pierwszego celu, nie miara poprawnego rozdzielenia dwóch celów. Sumowano moce, bez pełnego modelu interferencji.

Wniosek: pomiar ze skanu można połączyć z obecnym torem bez zmiany R/v. Przy pojedynczym celu i synchronizacji daje mały błąd w tym modelu. Nie jest gotowym rozwiązaniem dla nierozdzielonych bliskich celów. Potrzebny jest osobny detektor i rozdzielanie wiązek; bez tego nie zastępować wszystkich kątów jednym środkiem.

To ograniczony test integracyjny modeli, bez pełnego skanu wielu komórek i walidacji sprzętowej. Stare pliki i wyniki pozostają zachowane. Odtwarzanie: python check_integration.py w świeżej kopii bez integration_results.json; wymagany sąsiedni katalog minimal_intervention.
