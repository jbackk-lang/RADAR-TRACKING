# RADAR-TRACKING

Lekki, geometryczny tracker wielu obiektów zbudowany na filtrach już
zdefiniowanych w tym ekosystemie: **TRM** (spójność przestrzenno-czasowa),
**GIA** (dominujący kierunek) i **TIMDR** (wykrywanie zmiany/manewru),
plus **asocjacja węgierska z bramkowaniem Mahalanobisa** i **heurystyczny
model niepewności**.

> **Uczciwie o metodzie:** TRM tutaj to klasyczny filtr gęstościowy typu
> DBSCAN (punkt bez sąsiadów w przestrzeni i czasie = odrzucony jako szum),
> teraz przyspieszony drzewem KD zamiast pętli O(n²). GIA to pierwsza
> składowa PCA (największy wektor własny macierzy kowariancji) lokalnej
> historii pozycji. TIMDR to trzy proste, dobrze znane wielkości (amplituda
> skrętu kursu, z-score prędkości, korelacja zmian prędkości i kursu)
> uśrednione w jeden wskaźnik manewru. Asocjacja to algorytm węgierski
> (`scipy.optimize.linear_sum_assignment`) — globalnie optymalne
> przypisanie, nie zachłanne "najbliższy wolny". Model niepewności to
> **nie jest filtr Kalmana** — to ręcznie skonstruowana kowariancja, która
> rośnie z upływem czasu i z wynikiem TIMDR, używana tylko do bramkowania
> Mahalanobisa i do rysowania elipsy ufności. Żadna z tych rzeczy nie jest
> nową matematyką śledzenia obiektów — to konkretna, działająca
> implementacja klasycznych technik pod nazewnictwem TIMDR/TRM/GIA
> używanym w innych repozytoriach tego autora.

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

To jest pełny tracker, ale bez Kalmanów, bez EKF, bez PF — geometryczny
tracker z opcjonalną, lekką warstwą probabilistyczną do bramkowania, a
nie pełny filtr bayesowski. Zobacz sekcję "Ograniczenia" poniżej, zanim
użyjesz go do czegoś poważniejszego niż demo.

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
- To repozytorium **można pokazać firmie od sensorów jako solidne demo
  podejścia geometrycznego z rozsądną asocjacją**, ale nie jako gotowy,
  walidowany produkt do wdrożenia bez dalszej pracy (testów na realnych
  danych radarowych, strojenia progów, właściwego MHT dla gęstych scen).
