# RADAR-TRACKING

Geometryczny tracker wielu obiektów łączący **TRM** (spójność przestrzenno-czasowa), **GIA** (dominujący kierunek) i **TIMDR** (wykrywanie zmiany/manewru) z asocjacją węgierską i bramkowaniem Mahalanobisa.

## Co wnosi TIMDR w tej implementacji

TIMDR jest aktywną częścią głównego trackera. Łączy informację o skręcie, odchyleniu prędkości i współzmienności zmian prędkości oraz kursu. Wynik wpływa na dalsze działanie:

- **Rozpoznanie manewru:** udostępnia składowe T/D/R i wspólny wskaźnik, zamiast oceniać ruch tylko przez pojedynczy dystans między detekcjami.
- **Predykcja:** przy wysokim wyniku skraca krok ekstrapolacji liniowej, ograniczając zaufanie do dotychczasowego kierunku.
- **Asocjacja:** zwiększa modelowaną niepewność i szerokość bramki dopasowania dla manewrującego toru.

Wkład polega więc na połączeniu diagnostyki zmiany z decyzjami trackera. Wykorzystanie klasycznych miar i algorytmów nie odbiera wartości temu połączeniu; jednocześnie sam fakt ich integracji nie dowodzi przewagi nad innymi trackerami. Kod i testy pokazują wymienione zachowania. Do liczbowego określenia korzyści samego TIMDR potrzebne jest porównanie identycznego pipeline'u z TIMDR i bez niego, na tych samych danych.

Ta radarowa adaptacja nie jest pełną implementacją całego formalizmu GIA–TIMDR. W szczególności składowa T mierzy tutaj wielkość skrętu kursu. Wyników osobnych eksperymentów I/Q, filtrów i selektorów nie przypisujemy automatycznie TIMDR. Brak potwierdzenia pojedynczego eksperymentu amplitudowego również nie unieważnia jego zaimplementowanej roli w trackerze.

## Wybór modelu rozpoznawania sceny: CV lub TIMDR

W demo dostępna jest druga, eksperymentalna opcja rozpoznawania sceny. Oba warianty wykorzystują identyczne położenia i Doppler; `cv` stosuje predykcję stałej prędkości, a `timdr` dostosowuje predykcję do wyniku rzeczywistego operatora `core.timdr_change`. Wybór dotyczy nowego modelu sceny, a nie wyłączenia TIMDR w dotychczasowym trackerze.

```powershell
python demo.py --scene-model cv
python demo.py --scene-model timdr
python demo.py --scene-model timdr --scene parallel
python demo.py --scene-model timdr --scene rotating
```

Sceny demo: `diverging` (domyślnie dwa rozchodzące się cele), `parallel` (spójna grupa o nierozstrzygniętej liczbie) i `rotating` (obracająca się spójna grupa). Demo drukuje etykietę, ewentualną liczbę obiektów, obserwowaną rozciągłość grupy w metrach i liczbę wywołań TIMDR. `count: null` oznacza brak rozstrzygnięcia, nie brak celu. Odstęp punktów nie jest automatycznie wielkością pojedynczego obiektu.

Do użycia własnych detekcji:

```python
from core.scene_model import recognize_scene

result = recognize_scene(positions, doppler, times, use_timdr=True)
```

`positions`: tablica `(N, 2, 2)` z dwoma punktami `(x, y)` na klatkę w metrach; `doppler`: `(N, 2)` z radialnymi prędkościami w m/s; `times`: `(N,)` z rosnącym czasem w sekundach, co najmniej trzy klatki. Punkty mogą zmieniać kolejność. Radar jest w początku układu współrzędnych. Domyślny wariant API to CV (`use_timdr=False`). TIMDR korzysta tylko z wcześniejszej historii do asocjacji, a ocena sceny dotyczy całego przekazanego okna.

To ograniczony model dla dwóch detekcji na klatkę; nie obsługuje jeszcze dowolnej liczby punktów, zaników ani pełnej klasyfikacji obiektów. Identycznie współporuszające się obiekty i odbicia jednego obiektu mogą pozostać nierozróżnialne. Standardowe `python demo.py` nadal uruchamia dotychczasowy tracker i wizualizacje, bez nowej analizy sceny; dane `sample_radar.npy` nie zawierają wymaganych tu obserwacji Dopplera.

[Porównanie prototypu z wariantem CV](outputs/angle_frequency/WYNIK_TIMDR_SCENE.md): 800 łatwych sekwencji — 100% etykiet obu modeli; 800 trudniejszych — CV 47,0%, TIMDR 48,125%. Spełniono zapisane kryterium niepogorszenia w tym syntetycznym benchmarku. Oba modele wymagają odporniejszego grupowania przy większym szumie. To potwierdzenie możliwości budowy modelu na TIMDR, nie ogólnej równoważności z rzeczywistym radarem.

Testy integracji: `python -m unittest discover -s tests -p test_scene_model.py -v`. Pełny zestaw dotychczasowych testów można nadal uruchamiać przez pytest zgodnie z instrukcją niżej.

## Najnowsze eksperymenty radarowe

Kod i wyniki znajdują się w [outputs/angle_frequency](outputs/angle_frequency). To osobne eksperymenty syntetyczne; główny tracker i demo nie korzystają jeszcze z tych modułów.

- [Pomiar kąta z obrotu anteny i fazy w paśmie](outputs/angle_frequency/WYNIK.md).
- [Spójna estymacja Dopplera z fazy nośnej](outputs/angle_frequency/WYNIK_CARRIER.md): na izolowanych echach błąd v spadł o około 84–97% względem bazowej różnicy faz. Bezwzględne R nie poprawiło się; zmiana R jest wyliczana z v. Nakładające się silne echo i dryf instrumentu pozostają problemem. To osobny test 120 burstów, nie zmiana głównego trackera.
- [Jedna prędkość: czas ze znacznika, zero z reflektora](outputs/angle_frequency/WYNIK_MARKER.md): niezależne elektroniczne znaczniki rozdzielają błędy bez zmiany prędkości. Po zmianie przesunięcia zegara MAE kąta spadło z .19° do .028° w symulacji; przy stabilnym czasie sama korekta kąta była równie dobra. Wymaga właściwego sprzętowego punktu rejestracji znaczników.
- [Kalibracja po łagodnym rozruchu i ustaleniu obrotu](outputs/angle_frequency/WYNIK_SETTLED.md): w modelu drgań skrętnych przyjęto 10/10 kalibracji i uzyskano .037° MAE na późniejszych celach. Czasy rampy i oczekiwania wymagają charakterystyki rzeczywistego napędu; przy jednej stałej prędkości opóźnienie i zero nadal są nierozróżnialne, także bez rezonansu.
- [Wspólna kalibracja czasu echa i zera enkodera](outputs/angle_frequency/WYNIK_SYNC.md): na 180 nowych pomiarach syntetycznych zmniejszyła MAE kąta przy zmiennym obrocie z około .99° do .038°; sama korekta kąta dawała .33°. Wymaga obserwacji znanego reflektora przy różnych prędkościach obrotu. Błędny kąt referencji nadal wprowadza błąd kalibracji.
- [Połączenie pomiaru kąta z torem R/v oraz bliskie cele](outputs/angle_frequency/WYNIK_INTEGRACJI.md).
- [Koherentne nakładanie ech i dwa kanały odbiorcze](outputs/angle_frequency/WYNIK_STEREO.md).
- [Wspólne dopasowanie kilku skanów i kontrola pojawiania/zaniku celów](outputs/angle_frequency/WYNIK_MULTISCAN.md).
- [Bieżący detektor i odporny filtr impulsowych zakłóceń I/Q](outputs/angle_frequency/WYNIK_ROBUST.md).
- [Selektor fazowy słabego echa i fałszywe alarmy](outputs/angle_frequency/WYNIK_SELECTOR.md).

Filtr impulsów poprawił wyniki syntetyczne, ale słabe, bliskie cele nadal bywają pomijane. Selektor fazowy pomagał głównie przy różnicy odległości; próg ustalony przed oceną nie utrzymał zakładanych 5% fałszywych alarmów. Nie wykazano gotowości do pracy na rzeczywistym radarze.

## Opcjonalny zegar amplitudy — pilot integracji

[Czterostanowa pamięć i adaptacja kalibracji](clock_experiment/ONLINE_WYNIK.md): wykorzystują kolejne zwykłe obserwacje reflektora, bez dodatkowej emisji. Nowe propozycje nie potwierdzają się danymi, z których powstały. W badanej symulacji główną poprawę daje pamięć decyzji; uczenie parametrów nie wygrywa we wszystkich metrykach.

[Kontroler aktualności kalibracji z drugim reflektorem](clock_experiment/GUARD_WYNIK.md) porównuje brak kompensacji, kompensację stałą i warunkową w syntetycznej sekwencji dryfu oraz zakłóceń. Nie używa prawdy śledzonych celów do przełączania.

[Kalibracja z osobnego reflektora i jej starzenie](clock_experiment/CALIBRATION_WYNIK.md): 600 syntetycznych ocen, poprawki szacowane z pomiaru i zamrożone przed innymi celami. Test bada granice przydatności kompensacji przy szumie i dryfie; nie jest walidacją sprzętową.

[Nowy kierunek: kompensacja znanego stanu aparatury](clock_experiment/COMPENSATION_WYNIK.md) zamiast poszukiwania rytmu obiektu. Kontrolowany test impulsowego I/Q wykazał usunięcie zadanych błędów triggera, kierunku i fazy bez usunięcia ruchu celu. To test syntetyczny z idealną kalibracją; brak jeszcze odpowiednich rzeczywistych danych i pełnego modelu skanowania.

[Hipotezę stałego modu z błysków](clock_experiment/MODE_WYNIK.md) sprawdzono przez przeniesienie częstości i fazy na późniejsze fragmenty czterech śladów. Nie uzyskano potwierdzenia względem losowej kontroli; nie utożsamiamy tego testu z ogólnym odrzuceniem modów fizycznych.

Dodano też [wykrywanie błysków bez zegara](clock_experiment/FLASH_WYNIK.md): lokalne zdarzenia w polu czas–Doppler, mapy czterech rzeczywistych śladów i kontrolę po przetasowaniu. Nie utożsamiamy wykrytych zdarzeń z łopatami ani RPM.

Najnowsza kontrola: [zegary w czterech stałych pasmach rzeczywistego widma](clock_experiment/BANDS_WYNIK.md), z oceną wspólnej amplitudy całego echa i oddzielną kontrolą bez zegara.

Dodano [przełącznik jakości prognozy sygnału](clock_experiment/SIGNAL_WYNIK.md), który nigdy sam nie odrzuca pozycji. Test obejmuje syntetykę i cztery prawdziwe ślady Open Radar. Na prawdziwych śladach zegar nie uzyskał akceptacji i pozostała prosta prognoza średnią; nie wykazano przewagi na tych nagraniach.

Najnowszy pilot: [miękkie ważenie pomiaru — geometria kontra geometria z amplitudą](clock_experiment/SOFT_WYNIK.md). Sprawdza, czy zamiast odrzucać pozycję na podstawie samej amplitudy lepiej zmniejszać jej wagę dopiero przy niezgodności z predykcją. Wyniki są syntetyczne, a próg ręczny.

Dodano także [syntetyczny test przełączania zegar/sito → standard](clock_experiment/ADAPTIVE_WYNIK.md): trzy warianty i kontrole niezależnych zakłóceń amplitudy oraz pozycji. To opcjonalne sito amplitudy przed trackerem; geometryczne TRM nadal działa. Przykład dotyczy jednego obiektu, a nie asocjacji amplitud wielu obiektów.

Dodano [bank zegarów przypisanych do ID torów](clock_experiment/README.md) i [wyniki małego testu syntetycznego](clock_experiment/WYNIK.md). Zegar z astronomii otrzymuje osobny kanał amplitudy, ponieważ pozycje `x,y,t` nie wystarczają do pomiaru okresowości echa. Dwa sygnały przyspieszające zaakceptowano, dwie kontrole szumowe odrzucono. To diagnostyka offline; nie wykazano jeszcze poprawy śledzenia pozycji lub prędkości. Wyniki z TIMDR-Radar-Module nie są wynikami tego repozytorium.

## Z czego zbudowano metodę

TRM używa sąsiedztwa w przestrzeni i czasie, podobnego do metod gęstościowych typu DBSCAN, z drzewem KD. GIA wyznacza dominujący kierunek przez PCA lokalnej historii pozycji. Radarowy TIMDR łączy wielkość skrętu, z-score prędkości i korelację zmian prędkości oraz kursu, a jego wynik steruje predykcją i niepewnością. Asocjacja korzysta z algorytmu węgierskiego (`scipy.optimize.linear_sum_assignment`), który minimalizuje koszt przypisania dla danej klatki.

Model niepewności jest heurystyczną kowariancją rosnącą z czasem i wynikiem TIMDR. Służy do bramkowania Mahalanobisa i wizualizacji niepewności; nie zawiera aktualizacji stanu jak filtr Kalmana. Wartość tego projektu oceniamy przez działanie całego pipeline'u i kontrolowane porównania jego części, z oddzielnym wskazaniem znanych narzędzi matematycznych oraz sposobu ich połączenia.

## 1. Pipeline

1. Pobierz punkty z radaru (frame).
2. **TRM** (drzewo KD) → usuń punkty bez sąsiadów w przestrzeni i czasie.
3. Scal blisko leżące punkty w jedną detekcję na obiekt (jeden realny cel
   zwykle daje kilka bliskich odbić — bez tego kroku dostałbyś kilka
   "duchów" na jeden prawdziwy obiekt).
4. Dla każdego istniejącego toru: **GIA** → kierunek, **TIMDR** → wynik
   manewru, **Predictor** + **model niepewności** → gdzie tor "powinien"
   być w chwili tej klatki i jak bardzo można w to wątpić.
5. **Asocjacja węgierska** dopasowuje tory do detekcji minimalizując
   łączny koszt (dystans Mahalanobisa), z bramkowaniem — pary powyżej
   progu ufności nigdy się nie łączą.
6. Dopasowane detekcje trafiają do historii toru; niedopasowane detekcje
   zakładają nowe tory.
7. **Stabilizer** → wygładza raportowaną pozycję (wykładnicze wygładzanie).
8. `prune_stale()` → usuwa tory, które nie były aktualizowane od dawna.

Pipeline obejmuje filtrowanie detekcji, asocjację, historię torów, diagnostykę manewru, predykcję i wygładzanie pozycji. Pracuje na detekcjach `x,y,t`; eksperymenty z surowym I/Q są osobnymi modułami. Model niepewności wspiera bramkowanie, a jego interpretacja wymaga kalibracji dla docelowych danych.

## 2. Szybki start

```python
from core.radar_tracker import RadarTracker

tracker = RadarTracker(d_max=3.0, dt_max=1.0, k_min=1, gate_chi2=5.991)

# points: lista {'x','y','t'} dla jednej klatki radaru
result = tracker.update(points)

for track_id, info in result.items():
    print(track_id, info["x"], info["y"], info["manoeuvre"],
          info["predicted_next"], info["predicted_covariance"])
```

`gate_chi2` to próg chi-kwadrat dla 2 stopni swobody — domyślnie 5.991
(elipsa ufności 95%). `sigma0` i `manoeuvre_inflation` sterują tym, jak
szybko rośnie niepewność z czasem i z manewrowaniem (patrz `core/motion_model.py`).

Pełny, uruchamialny przykład na syntetycznych danych: `python3 demo.py`
(wczytuje `data/sample_radar.npy`, drukuje podsumowanie klatka po klatce,
zapisuje wizualizacje do `demo_output/`).

## 3. Co ten tracker wykrywa

- nagłe skręty (TIMDR / T),
- zmianę prędkości (TIMDR / D),
- fałszywe/odosobnione punkty (TRM),
- dominujący kierunek (GIA),
- trajektorię obiektu (GIA + predictor),
- manewry (próg na łącznym wyniku TIMDR),
- utratę obiektu ze sceny (`prune_stale`, usuwa nieaktualizowane tory),
- **poprawnie przetrwaną przerwę w detekcjach** — jeśli klatka zostanie
  pominięta, predykcja uwzględnia realny upływ czasu (`dt`), a nie stały
  promień na klatkę (zobacz test
  `test_association_survives_a_missed_detection_gap`).

## 4. Struktura repozytorium

```
radar-tracking/
│
├── core/
│   ├── trm_filter.py       # filtr spójności (drzewo KD) + scalanie klastrów w detekcje
│   ├── gia_direction.py    # PCA -> dominujący kierunek + stabilność
│   ├── timdr_change.py     # skręt / defekt / rezonans -> wynik manewru
│   ├── association.py      # asocjacja węgierska z bramkowaniem
│   ├── motion_model.py     # heurystyczna kowariancja (NIE Kalman) do bramkowania Mahalanobisa
│   ├── radar_tracker.py    # RadarTracker: asocjacja, historia, orkiestracja
│   └── predictor.py        # kinematyczna ekstrapolacja tłumiona przez TIMDR
│
├── visualizer/
│   └── tracking_visualizer.py   # podgląd klatki i pełnych trajektorii (matplotlib)
│
├── data/
│   ├── sample_radar.npy            # wygenerowane dane demo (3 cele + szum)
│   └── generate_sample_radar.py    # skrypt, który je wygenerował
│
├── tests/
│   ├── test_trm_filter.py
│   ├── test_gia_direction.py
│   ├── test_timdr_change.py
│   ├── test_predictor.py
│   ├── test_association.py         # dowód: węgierski >= zachłanny (przykład liczbowy)
│   ├── test_motion_model.py
│   └── test_radar_tracker.py       # testy integracyjne całego pipeline'u
│
├── demo.py            # pełny przebieg end-to-end na sample_radar.npy
└── README.md
```

Uruchomienie testów: `python3 -m pytest tests/ -v` (41 testów, wszystkie
przechodzą na czysto zsyntetyzowanych scenariuszach: linia prosta, ostry
skręt, seria przyspieszenia, szum bez sąsiadów, zbyt krótka historia,
przykład węgierski-vs-zachłanny z jawnie policzonym kosztem, przerwa w
detekcjach).

## 5. Ograniczenia (uczciwie)

- **Asocjacja węgierska jest optymalna tylko dla macierzy kosztu tej
  jednej klatki** — to nie jest tracker wielohipotezowy (MHT); jeśli sama
  odległość Mahalanobisa jest niejednoznaczna (np. dwa tory dokładnie w
  momencie krzyżowania), globalny optimum może nadal zamienić tożsamości.
  Rozwiązuje to problem "zachłanny w złej kolejności", nie problem
  "fundamentalnej niejednoznaczności krzyżujących się torów".
- **Model niepewności to NIE filtr Kalmana** — nie ma kroku aktualizacji
  łączącego wcześniejszy stan z nowym pomiarem przez wzmocnienie Kalmana,
  nie ma szumu procesu/pomiaru estymowanego z rzeczywistych danych. To
  ręcznie dobrana kowariancja rosnąca z czasem i wynikiem TIMDR — działa
  do bramkowania i rysowania elipsy ufności, ale to nie jest estymacja
  bayesowska.
- **TRM z drzewem KD jest średnio szybszy, nie gwarantowanie szybszy** —
  w gęstej scenie, gdzie większość punktów leży blisko siebie, złożoność
  nadal zbliża się do O(n²) (bo tyle właśnie trzeba przetworzyć par).
- **TIMDR-P (predykcja punktu krytycznego)** z dokumentu `GIA-and-TIMDR`
  nie jest tu zaimplementowany wprost — `predict_next` to prosta
  ekstrapolacja liniowa tłumiona wynikiem TIMDR, nie osobny predyktor
  punktów krytycznych.
- Repozytorium dostarcza działający punkt wyjścia do badań nad integracją
  geometrii, diagnostyki zmiany i asocjacji. Testy syntetyczne sprawdzają
  zachowania implementacji; ocenę przewagi TIMDR oraz całego trackera
  trzeba uzupełnić o porównania z wariantami bazowymi i dane rzeczywiste.
  Wdrożenie wymaga kalibracji progów i sprawdzenia niejednoznacznych scen.


### Pik czasu powrotu

[Pik odwróconej fazy](outputs/angle_frequency/WYNIK_ECHO_PEAK.md) — odwrócenie fazy I/Q nie zmienia piku ani szumu. Filtr dopasowany poprawił lokalizację słabego echa z 4/100 do 45/100 w syntetycznym teście; bez progu detekcji nadal może wskazać szum. Eksperyment nie zmienia głównego trackera.


[Dwie nosne i dudnienie](outputs/angle_frequency/WYNIK_DUAL_BEAT.md) — zmniejszenie dudnienia z 38.5 do 19.25 GHz podwaja okres niejednoznacznosci R z 3.893 do 7.787 mm, lecz nie poprawilo odleglosci. Przy stalej energii dwa pasma pogorszyly wynik slabego echa. Osobny eksperyment syntetyczny.


[Bliskie nosne, chirp i rezonans odbicia](outputs/angle_frequency/WYNIK_WAVE_METHODS.md) — automatyczna detekcja na nowych scenach po zamrozeniu progow szumu. Bliskie nosne poprawily silne skalibrowane R (~51%), lecz szkodzily slabemu echu i przy bledzie fazy. Chirp poprawil lokalizacje przy zakloceniu impulsowym (51/100 zamiast 0/100). Pasywny rezonans odbicia pogorszyl wynik w tym modelu. Bez integracji z trackerem.


[Blysk energii](outputs/angle_frequency/WYNIK_FLASH.md) — idealny model specjalnego reflektora z kompresja odpowiedzi przy stalej energii. Slabe echo: warunkowy MAE R 2.445 do 1.933 m, wykrycia 97 do 98/100; bez odpornosci na zaklocenia impulsowe. Wymaga znanej zwloki, szerszego pasma i specjalnego celu; nie zwykly pasywny rezonans.


[Dopasowanie calego echa](outputs/angle_frequency/WYNIK_ECHO_SHAPE.md) — bank ksztaltow poprawil lokalizacje zmiennego ogona z 9 do 96/100; nierozpoznany ogon odbiornika nadal dawal ~23.5 m bledu. Sam spadek nie identyfikuje czasu przy nieznanej amplitudzie. Eksperyment syntetyczny, bez integracji z trackerem.


[Ruch w widmie](outputs/angle_frequency/WYNIK_RANGE_MOTION.md) — wyrownanie fazy z Dopplera poprawilo R o ~25% przy stalej predkosci30m/s w osobnym modelu3GHz, ale model stalej predkosci pogorszyl R przy przyspieszeniu. Migracja zakresu dala maly dodatkowy zysk. Bez walidacji czola rozciaglego celu i bez integracji z trackerem.


[Czolo rozciaglego celu](outputs/angle_frequency/WYNIK_ECHO_FRONT.md) — pierwszy wiarygodny pik poprawil lokalizacje przedniej powierzchni z0 do56/100 przy rozciaglosci30m, ale slaby przod pozostal niewykryty (0/100). Wykrycie obiektu nie gwarantuje wykrycia jego czola. Osobna symulacja bez integracji z trackerem.


[Ksztalt Gaussa i statystyka szumu](outputs/angle_frequency/WYNIK_GAUSSIAN_SHAPE.md) — test zaakceptowal93/100 Gaussow, odrzucil96/100 ogonow i100/100 podwojnych odbic. Narzucenie Gaussa na ogon dalo~29m bledu. Skalarne I/Q nie okresla polaryzacji; szum Gaussa w generatorze nie dowodzi normalnosci zaklocen sprzetowych. Tracker bez zmian.


[Koncowy test banku echa](outputs/angle_frequency/WYNIK_FINAL_ECHO.md) — znane rodziny:294/300poprawnych R i6odrzucen. Slaby przod oraz nieznany odbiornik nadal dawaly bledy (18 i78/100). Zgodnosc modeli nie gwarantuje prawdziwego czola; potrzebna kalibracja odbiornika i realne dane. Bez integracji z trackerem.


[Rozpoznawanie sceny z historii](outputs/angle_frequency/WYNIK_SCENE_RECOGNITION.md) — 600sekwencji detekcji: rozny ruch pozwolil wskazac2obiekty w100przypadkach; pozostale500pozostawiono nierozstrzygniete. Historia ogranicza nadmierna pewnosc liczenia pikow, ale nie rozroznia jednego duzego i dwoch wspolporuszajacych sie obiektow. Rozciaglosc grupy nie jest pewna wielkoscia celu. Bez dowodu przewagi nad standardowym trackerem i bez integracji z glownym pipeline.


[Model sceny wykorzystujacy TIMDR](outputs/angle_frequency/WYNIK_TIMDR_SCENE.md) — rzeczywisty operator core/timdr_change.py steruje predykcja prototypu. Na800latwych sekwencjach wynik porownywalny z klasycznym CV (100%etykiet obu); na800trudniejszych48.125% vs47.0%, kryterium niepogorszenia spelnione. TIMDR zmienil asocjacje w108sekwencjach. To dowod wykonalnosci modelu na TIMDR, nie rownowaznosci ze wszystkimi radarami. Oba warianty wymagaja odporniejszego grupowania; bez integracji z glownym demo.
