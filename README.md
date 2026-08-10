# RADAR-TRACKING

Lekki, geometryczny tracker wielu obiektów zbudowany na filtrach już
zdefiniowanych w tym ekosystemie: **TRM** (spójność przestrzenno-czasowa),
**GIA** (dominujący kierunek) i **TIMDR** (wykrywanie zmiany/manewru).

> **Uczciwie o metodzie:** TRM tutaj to klasyczny filtr gęstościowy typu
> DBSCAN (punkt bez sąsiadów w przestrzeni i czasie = odrzucony jako szum).
> GIA to pierwsza składowa PCA (największy wektor własny macierzy
> kowariancji) lokalnej historii pozycji. TIMDR to trzy proste, dobrze
> znane wielkości (amplituda skrętu kursu, z-score prędkości, korelacja
> zmian prędkości i kursu) uśrednione w jeden wskaźnik manewru. To NIE
> jest odkrycie nowej matematyki śledzenia obiektów — to konkretna,
> działająca implementacja klasycznych technik pod nazewnictwem TIMDR/TRM/GIA
> używanym w innych repozytoriach tego autora.

## 1. Pipeline

1. Pobierz punkty z radaru (frame).
2. **TRM** → usuń punkty bez sąsiadów w przestrzeni i czasie (fałszywe odbicia).
3. Scal blisko leżące punkty w jedną detekcję na obiekt (jeden realny cel
   zwykle daje kilka bliskich odbić — bez tego kroku dostałbyś kilka
   "duchów" na jeden prawdziwy obiekt).
4. **GIA** → wyznacz lokalny kierunek ruchu (PCA na historii pozycji).
5. **TIMDR** → sprawdź, czy nastąpiła zmiana kierunku / prędkości.
6. Jeśli TIMDR wysoki → obiekt wykonuje manewr.
7. **Predictor** → przewiduje nową pozycję na podstawie GIA, tłumiony przez TIMDR.
8. **Stabilizer** → wygładza trajektorię (wykładnicze wygładzanie).
9. Zapisz wynik jako nowy stan trackera.

To jest pełny tracker, ale bez Kalmanów, bez EKF, bez PF — czysty
geometryczny tracker, lekki i szybki, ale też **bez probabilistycznego
modelu ruchu/szumu**. Zobacz sekcję "Ograniczenia" poniżej, zanim użyjesz
go do czegoś poważniejszego niż demo.

## 2. Szybki start

```python
from core.radar_tracker import RadarTracker

tracker = RadarTracker(d_max=3.0, dt_max=1.0, k_min=1, assoc_max_dist=8.0)

# points: lista {'x','y','t'} dla jednej klatki radaru
result = tracker.update(points)

for track_id, info in result.items():
    print(track_id, info["x"], info["y"], info["manoeuvre"], info["predicted_next"])
```

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
- utratę obiektu ze sceny (`prune_stale`, usuwa nieaktualizowane tory).

## 4. Struktura repozytorium

```
radar-tracking/
│
├── core/
│   ├── trm_filter.py       # filtr spójności + scalanie klastrów w detekcje
│   ├── gia_direction.py    # PCA -> dominujący kierunek + stabilność
│   ├── timdr_change.py     # skręt / defekt / rezonans -> wynik manewru
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
│   └── test_radar_tracker.py       # testy integracyjne całego pipeline'u
│
├── demo.py            # pełny przebieg end-to-end na sample_radar.npy
└── README.md
```

Uruchomienie testów: `python3 -m pytest tests/ -v` (27 testów, wszystkie
przechodzą na czysto zsyntetyzowanych scenariuszach: linia prosta, ostry
skręt, seria przyspieszenia, szum bez sąsiadów, zbyt krótka historia).

## 5. Ograniczenia (uczciwie)

- **Asocjacja jest zachłanna typu najbliższy-sąsiad** — w gęstej scenie
  albo przy krzyżujących się torach będzie się mylić. Nie ma tu żadnego
  globalnie optymalnego przypisania (jak np. algorytm węgierski).
- **TRM działa w O(n²)** na klatkę — wystarczające dla dziesiątek/setek
  detekcji na klatkę, nie dla radaru dającego tysiące zwrotów.
- **Brak modelu szumu/procesu** — w przeciwieństwie do Kalmana/EKF/PF nie
  ma tu żadnej estymacji niepewności, tylko punktowe przewidywanie.
- **TIMDR-P (predykcja punktu krytycznego)** z dokumentu `GIA-and-TIMDR`
  nie jest tu zaimplementowany wprost — `predict_next` to prosta
  ekstrapolacja liniowa tłumiona wynikiem TIMDR, nie osobny predyktor
  punktów krytycznych.
- To repozytorium **można pokazać firmie od sensorów jako demo podejścia
  geometrycznego**, ale nie jako gotowy, walidowany produkt do wdrożenia
  bez dalszej pracy (testów na realnych danych radarowych, strojenia
  progów, obsługi zgubionych/nowych celów w gęstszych scenach).
