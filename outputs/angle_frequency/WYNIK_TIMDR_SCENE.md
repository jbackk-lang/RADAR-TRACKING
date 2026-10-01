# Można zbudować model sceny wykorzystujący TIMDR

Zbudowano wywoływalny model timdr_scene_model.recognize_scene. Używa rzeczywistego operatora z core/timdr_change.py, nie tylko nazwy. Niezmieniona kopia timdr_reference.py ma SHA2566512bebd4e2b343c8b34023687f0a76a44ace1c32e0f24b3287b02fd4be8ed6b, zweryfikowany względem repo. T,D,R,TIMDR z wcześniejszej historii sterują predykcją asocjacji. Model zwraca hipotezę sceny, ewentualną liczbę2, rozciągłość obserwowanej grupy i diagnostykę TIMDR.

Porównanie lokalnego modelu standardowego stałej prędkości z tym samym modelem z TIMDR. Dane i pozostałe reguły identyczne. Kryterium przed przebiegiem:dolna granica parowanego95%bootstrapu różnicy trafności nie niższa niż-5punktów procentowych.

| Test | Sekwencje | Standard CV | Model z TIMDR | Różnica TIMDR-CV | Kryterium porównywalności |
|---|---:|---:|---:|---:|---|
| Mały szum | 800 | 100% | 100% | 0pp | spełnione |
| Większy szum i błędne detekcje | 800 | 47.0% | 48.125% | +1.125pp | spełnione |

Trafność dotyczy trzech etykiet:rozdzielny ruch, spójna grupa o nierozstrzygniętej liczbie, niespójne echo. Nie jest to100%identyfikacji obiektów w łatwym teście. W scenach nierozróżnialnych prawidłowym wynikiem jest brak dokładnej liczby.

Łatwy test był nasycony:0różnic asocjacji, więc sam nie wykazał znaczenia TIMDR. Osobno dodany stress-test dał108/800sekwencji z różną asocjacją. TIMDR wywołano16000razy w każdym przebiegu. Zmiana jest faktycznie aktywna, nie ozdobna. W stress-teście:rozchodzące się cele poprawne94->99/100, krzyżujące85->88/100, niezależny skręt98->99/100; niespójne echo99->99/100. Nie przesądzamy przewagi uniwersalnej.

Parowany bootstrap dla różnicy stress-testu:[+0.125,+2.125]pp. To opis empirycznego zestawu i jego resamplingu, nie dowód na rzeczywistych radarach. Stress-test dodano po stwierdzeniu nasycenia pierwszego przebiegu, przed jego uruchomieniem zapisano warunki; nie był od początku zaplanowany holdout.

## Uczciwy wniosek

Można zbudować działający model rozpoznawania sceny wykorzystujący rzeczywisty moduł TIMDR. Na tym syntetycznym benchmarku spełnił ustalone kryterium niepogorszenia względem lokalnego klasycznego wariantu CV. To potwierdzenie wykonalności i ograniczonej porównywalności, nie równoważności ze wszystkimi standardowymi radarami ani pełnymi trackerami.

Oba modele słabo znoszą większy szum:stałe reguły geometryczne mylą sztywne grupy z rozdzielnym ruchem. Dla dużego, obracającego się, równoległych celów i stałego ghosta stress-test miał0/100poprawnych etykiet w obu wariantach. TIMDR nie naprawia sam źle dobranej oceny niepewności grupy. Następna potrzebna poprawa:grupowanie uwzględniające niepewność pomiaru, porównanie z pełnym standardowym trackerem i realne detekcje. Bez strojenia po tym teście nie ogłaszamy gotowego rozpoznawania obiektów.

Pięć oryginalnych testów TIMDR przeszło. Sprawdzono zgodność źródła, faktyczne wywołania i niezerowy wpływ na predykcję. Model jest osobnym prototypem; główne demo i tracker nie zostały zmienione. Nie wdrożono całego formalizmu GIA-TIMDR ani klas semantycznych.

Pliki:timdr_scene_model.py, timdr_reference.py, run_timdr_scene.py, TIMDR_SCENE_PROTOCOL.md; wyniki timdr_scene_results.json i timdr_scene_stress_results.json. Odtworzenie: `python outputs/angle_frequency/run_timdr_scene.py` oraz `python outputs/angle_frequency/run_timdr_scene.py --stress`. Istniejące wyniki chronione. Wpisane w pierwszym wyniku hashe protokołu odnoszą się do jego wersji przed późniejszym dopisaniem stress-testu; źródło operatora i modelu bez zmian.
