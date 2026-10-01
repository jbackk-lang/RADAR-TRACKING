# Dla osób chcących użyć własnych danych

## Tracker wielu śladów

```python
from core.radar_tracker import RadarTracker

tracker = RadarTracker(timdr_variant="robust", position_sigma=0.4)
points = [{"x": 100.0, "y": 5.0, "t": 0.0},
          {"x": 100.2, "y": 5.1, "t": 0.0}]
result = tracker.update(points)
tracker.prune_stale(current_t=0.0, max_age=2.0)
```

Położenia w metrach, czas w sekundach. Jedno `update` oznacza jedną klatkę; punkty w klatce powinny mieć wspólny czas. Używaj uporządkowanego czasu. Przy domyślnym `k_min=1` pojedynczy punkt bez sąsiada może zostać odrzucony. `d_max` określa odległość grupowania, nie rozmiar obiektu.

- `RadarTracker()` — dotychczasowy TIMDR.
- `RadarTracker(use_timdr=False)` — ten sam tracker bez adaptacji TIMDR; nadal używa TRM, GIA, asocjacji i wygładzania.
- `RadarTracker(timdr_variant="robust", position_sigma=...)` — odporny operator.

`position_sigma` to odchylenie standardowe błędu jednej składowej punktów używanych przez operator. Nie jest rozdzielczością radaru. Po grupowaniu centroidy mogą mieć inną niepewność niż pojedyncze echa; parametry trzeba skalibrować.

Wynik zawiera położenie, kierunek, diagnostykę TIMDR, flagę manewru, predykcję i heurystyczną kowariancję. `predicted_next` domyślnie dotyczy jednej sekundy w przyszłość, nie koniecznie następnej klatki. Nie jest to filtr Kalmana: nie ma aktualizacji stanu przez gain ani estymowanego modelu szumu procesu.

## Osobny model sceny dla dwóch detekcji

```python
from core.scene_model import recognize_scene
result = recognize_scene(positions, doppler, times, use_timdr=True)
```

`positions`: `(N,2,2)` z dwoma punktami x/y na klatkę; `doppler`: `(N,2)` z prędkościami radialnymi w m/s; `times`: `(N,)`, co najmniej trzy rosnące czasy. Radar w początku układu. Model może pozostawić liczbę obiektów nierozstrzygniętą; pracuje na całym przekazanym oknie. Używa pierwotnego TIMDR, nie nowego odpornego operatora.

```powershell
python demo.py --scene-model cv
python demo.py --scene-model timdr --scene rotating
```

To oddzielna funkcja badawcza, nie automatyczna semantyczna klasyfikacja w przeglądarce.

## Uruchomienie eksperymentów

```powershell
python outputs/angle_frequency/run_timdr_robust.py
python outputs/angle_frequency/check_robust_tracker.py
python outputs/angle_frequency/run_realistic_timdr.py
```

Skrypty chronią istniejące wyniki. Jeśli plik już istnieje, nie wykonają nowego przebiegu pod tą samą nazwą. Przed celowym powtórzeniem zachowaj kopię wyniku i przeczytaj właściwy protokół. Stare raporty oraz kompletny indeks eksperymentów są w [historii](../HISTORY.md).

## Testy

```powershell
python -m pip install pytest
python -m pytest tests --ignore=tests/test_real_data_validation.py -q
```

Pominięty moduł wymaga plików `data/validate_on_real_trips.py` i `data/real_trips_sample.csv`, których nie ma w tej kopii. Nie zastępujemy ich danymi syntetycznymi pod nazwą „real”. Jeśli odzyskasz oryginalne dane i źródło z udokumentowanym pochodzeniem, można ponownie włączyć ten test. Dotychczas dostępne funkcje testowe wykonano bezpośrednio, gdy pytest nie było zainstalowane.

## Pliki

| Katalog lub plik | Rola |
|---|---|
| `core/` | tracker, TIMDR, grupowanie i predykcja |
| `web/` | widok przeglądarkowy |
| `web_demo.py` | lokalny serwer i generator demo |
| `data/sample_radar.npy` | syntetyczne dane starego demo |
| `tests/` | testy implementacji |
| `outputs/angle_frequency/` | protokoły i wyniki eksperymentów |
| `clock_experiment/` | wcześniejsze badania kalibracji i sygnału |
