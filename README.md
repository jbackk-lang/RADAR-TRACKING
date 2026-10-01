# RADAR-TRACKING

Geometryczny tracker wielu obiektów łączący **TRM** (spójność przestrzenno-czasowa), **GIA** (dominujący kierunek) i **TIMDR** (wykrywanie zmiany/manewru) z asocjacją węgierską i bramkowaniem Mahalanobisa.

## Co wnosi TIMDR w tej implementacji

TIMDR jest aktywną częścią głównego trackera. Łączy informację o skręcie, odchyleniu prędkości i współzmienności zmian prędkości oraz kursu. Wynik wpływa na dalsze działanie:

- **Rozpoznanie manewru:** udostępnia składowe T/D/R i wspólny wskaźnik, zamiast oceniać ruch tylko przez pojedynczy dystans między detekcjami.
- **Predykcja:** przy wysokim wyniku skraca krok ekstrapolacji liniowej, ograniczając zaufanie do dotychczasowego kierunku.
- **Asocjacja:** zwiększa modelowaną niepewność i szerokość bramki dopasowania dla manewrującego toru.

Wkład polega więc na połączeniu diagnostyki zmiany z decyzjami trackera. Wykorzystanie klasycznych miar i algorytmów nie odbiera wartości temu połączeniu; jednocześnie sam fakt ich integracji nie dowodzi przewagi nad innymi trackerami. Kod i testy pokazują wymienione zachowania. Do liczbowego określenia korzyści samego TIMDR potrzebne jest porównanie identycznego pipeline'u z TIMDR i bez niego, na tych samych danych.

Ta radarowa adaptacja nie jest pełną implementacją całego formalizmu GIA–TIMDR. W szczególności składowa T mierzy tutaj wielkość skrętu kursu. Wyników osobnych eksperymentów I/Q, filtrów i selektorów nie przypisujemy automatycznie TIMDR. Brak potwierdzenia pojedynczego eksperymentu amplitudowego również nie unieważnia jego zaimplementowanej roli w trackerze.

## Najnowsze eksperymenty radarowe

Kod i wyniki znajdują się w [outputs/angle_frequency](outputs/angle_frequency). To osobne eksperymenty syntetyczne; główny tracker i demo nie korzystają jeszcze z tych modułów.

- [Pomiar kąta z obrotu anteny i fazy w paśmie](outputs/angle_frequency/WYNIK.md).
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
