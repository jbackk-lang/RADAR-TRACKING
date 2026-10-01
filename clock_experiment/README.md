# Zegar amplitudy we właściwym RADAR-TRACKING

## Cztery stany, pamięć i adaptacja bez dodatkowych pomiarów

[Wyniki autokorekty](ONLINE_WYNIK.md) · [Protokół](ONLINE_PROTOCOL.md).
`OnlineCalibration` rozdziela confirmed/rejected/uncertain/waiting. Przechowuje ostatnią potwierdzoną decyzję z terminem ważności i opcjonalnie proponuje parametry EMA oceniane dopiero na następnej obserwacji. W tej symulacji pamięć zdecydowanie pomaga; EMA minimalnie poprawia prędkość, ale pogarsza odległość i kąt względem samej pamięci. Zero nowych obserwacji; nadal brak walidacji sprzętowej. Wszystkie decyzje i wariant kontrolny bez adaptacji w `online_results`.

## Niezależna kontrola kalibracji

[Wynik przełącznika z drugim reflektorem](GUARD_WYNIK.md) · [Protokół](GUARD_PROTOCOL.md).
Pierwszy reflektor wyznacza zamrożone poprawki, drugi ocenia ich przydatność zanim trafią do innych celów. Kontrola per parametr, dwa potwierdzenia do włączenia i jedna odmowa do wyłączenia. Test syntetyczny zawiera 360 pomiarów celów w trzech wariantach, narastający dryf, słaby walidator i zanik błędów aparatury. To nie gwarancja dla prawdziwego radaru; wymaga znanych, nieruchomych reflektorów.

## Kalibracja z osobnego reflektora i odporność na dryf

[Test zamrożonej kalibracji](CALIBRATION_WYNIK.md) · [Protokół](CALIBRATION_PROTOCOL.md).
Kalibrator szacuje opóźnienie, offset kierunku i liniowy dryf fazy z osobnego nieruchomego reflektora o znanej pozycji. Nie otrzymuje offsetów generatora. Poprawki są zamrażane przed pomiarem innych celów. Siatka 20 scenariuszy x10 ziaren x3 cele sprawdza szum kalibratora oraz późniejsze zmiany instrumentu, w tym sytuację, gdy stara poprawka szkodzi. Nadal symulacja; znana nieruchomość reflektora jest niezbędnym założeniem. Kod: reference_calibration.py; wyniki: calibration_results.

## Kompensacja znanej aparatury zamiast szukania rytmu celu

[Kontrolowany test kompensacji](COMPENSATION_WYNIK.md) · [Protokół](COMPENSATION_PROTOCOL.md).
`radar_compensation.py` koryguje znane przesunięcie triggera, offset kierunku i fazę instrumentu w impulsowym modelu I/Q. W 30 syntetycznych burstach błąd prędkości spadł z .698 do .012 m/s; ruchomy cel 2 m/s pozostał ruchomy (średnio 1.994 m/s). Kalibracja jest idealnie znana z generatora — nie estymujemy jej z echa. Cztery testy przeszły. Audyt cache Open Radar wykazał brak potrzebnych metadanych; realnej walidacji tej kompensacji nie wykonano. Nie symulowano pełnego obrotu anteny ani wielodrogowości.

## Hipoteza modu z błysków M/S

[Test fazy na odłożonym fragmencie](MODE_WYNIK.md) · [Protokół](MODE_PROTOCOL.md).
Częstość i fazę dopasowano do pierwszych fragmentów, potem oceniono bez ponownego dopasowania na późniejszych fragmentach. Żaden z czterech śladów nie przeszedł kryterium po kontroli losowej i korekcie czterech porównań. To brak potwierdzenia konkretnej hipotezy stałego rytmu, nie dowód nieistnienia innych modów ani mostu M/S–K. Kod `event_mode.py`, `run_event_mode.py`; wyniki `mode_results`.

## Błyski bez zegara

[Raport i mapy kandydatów](FLASH_WYNIK.md) · [Protokół](FLASH_PROTOCOL.md).
Detektor `flashes.py` szuka krótkich, połączonych obszarów mocy ponad tłem na mapie czas–Doppler, bez dopasowania okresu. W czterech śladach znalazł 46/23/58/24 kandydatów (człowiek/rower/pojazd/dron). Są to zdarzenia według przyjętych progów, nie zidentyfikowane łopaty. Kontrole przetasowania i wszystkie cztery mapy zapisano w `flash_results`. Długie luki, zwłaszcza drona, uniemożliwiają traktowanie cache jako ciągłego nagrania.

## Zegar w polu częstotliwości: stałe pasma

[Porównanie całego widma z czterema pasmami](BANDS_WYNIK.md) · [Protokół](BANDS_PROTOCOL.md).
Test na tych samych rzeczywistych śladach rozdziela widmo na cztery stałe pasma, prognozuje każde osobno, a następnie odtwarza amplitudę całego echa. Kontrola ze średnimi pasm oddziela korzyść podziału od korzyści zegara. Kod: `run_bands.py`; wszystkie pasma i wyniki zapisano w `band_results`. Nie wybierano pasma po wyniku i nie utożsamiamy go z wirnikiem bez pomiaru odniesienia.

## Monitor samego sygnału i naturalna kontrola

[Wyniki prognozowania sygnału](SIGNAL_WYNIK.md) · [Protokół](SIGNAL_PROTOCOL.md).
`SignalClockMonitor` przewiduje kolejne amplitudy i budzi dopasowanie po trzech kolejnych błędach ponad próg. Osiem dobrych próbek pozwala korzystać z zapamiętanego zegara. Zwraca `keep_position=True` niezależnie od amplitudy: ten przełącznik steruje kosztem analizy sygnału, nie odrzucaniem pozycji. Przy braku wiarygodnego modelu prognozuje średnią 12 poprzednich próbek.

Test: 6 syntetycznych sygnałów i 4 rzeczywiste ślady Open Radar Initiative. Syntetyczne chirpy poprawiły prognozę; szum pozostał przy metodzie bazowej. Na czterech rzeczywistych śladach zegara nie zaakceptowano, wynik jest identyczny z bazową średnią — brak wykazanej korzyści na tych danych. To modulacja amplitudy klatek, bez etykiet RPM, nie walidacja obrotów wirnika.

## Miękka fuzja zamiast odrzucania pomiaru

[Porównanie z samą geometrią](SOFT_WYNIK.md) · [Protokół](SOFT_PROTOCOL.md).
`soft_fusion.fuse_position(measured, predicted, amplitude_bad, mode)` przyjmuje dwie pozycje 2D i zwraca estymatę oraz wagę pomiaru. Tryb `geometry` używa wyłącznie odległości od przewidywania, `hybrid` zmniejsza wagę mocniej przy jednoczesnej anomalii amplitudy. Amplituda sama nie odrzuca zgodnej pozycji. To opcjonalna heurystyka pilota, nie aktualizacja Kalmana. Próba dotyczy jednego obiektu i nie sprawdza rzeczywistych manewrów.

## Nowy pilot przełączania

[Wynik trzech wariantów](ADAPTIVE_WYNIK.md) · [Protokół](ADAPTIVE_PROTOCOL.md).

`AdaptiveAmplitudeGate` w `adaptive.py` daje decyzję `keep` przed `tracker.update(points)`. Tryby: `standard`, `always`, `adaptive`. Po 8 dobrych próbkach adaptive przechodzi do standardu, zachowując tani monitor amplitudy. Niezgodność przywraca sito, a zegar dopasowuje się nie częściej niż co 80 próbek. Rozruch wymaga 100 próbek. To odrębne sito amplitudy, nie wyłączenie geometrycznego TRM.

```python
from clock_experiment.adaptive import AdaptiveAmplitudeGate
gate = AdaptiveAmplitudeGate(mode='adaptive')
# Dla amplitudy skojarzonej z jednym obiektem:
# decision = gate.step(time_s, amplitude)
# result = tracker.update(points if decision['keep'] else [])
```

Przy odrzuceniu detekcji trzeba nadal raportować brak pomiaru lub predykcję trackera — nie traktować jej jako nowej obserwacji. Pełny przykład wraz z pomiarem błędu jest w `run_adaptive.py`. Ta integracja jest pilotażowa i jednoobiektowa. Nie wolno użyć jednej amplitudy do odrzucenia całej wieloobiektowej klatki. Nie wykazano jeszcze, że błędy amplitudy są wiarygodną miarą błędów pozycji rzeczywistego sensora.

```powershell
python -m unittest clock_experiment.test_track_clock clock_experiment.test_adaptive -v
python -m clock_experiment.run_adaptive
python -m clock_experiment.report_adaptive
```

Repo bazowe: https://github.com/jbackk-lang/RADAR-TRACKING, commit `74916877dd0982b7dfef7f3c4921999e0ba3d275`. To inny projekt niż TIMDR-Radar-Module i RADAR-TRACKING-TIMDR.

`TrackClockBank` przechowuje osobną historię amplitudy dla istniejącego ID toru. Dopasowuje skopiowany bez zmian zegar astronomiczny dopiero na jawne żądanie. Nie wylicza obrotów z samego x/y, nie zmienia czasu pomiaru i nie steruje prędkością postępową. Wynik jest diagnostyką offline. Estymowana częstość modulacji nie identyfikuje jednoznacznie fizycznych obrotów.

```python
from core.radar_tracker import RadarTracker
from clock_experiment.track_clock import TrackClockBank

tracker = RadarTracker()
clocks = TrackClockBank(tracker)
# Po tracker.update(points): amplituda musi być prawidłowo przypisana
# przez źródło danych do konkretnego ID zwróconego toru.
# clocks.observe(track_id, time_s, amplitude)
# Po >=50 próbkach, z fizycznie uzasadnionymi granicami wyszukiwania:
# report, curve = clocks.analyze(track_id, (.3, .85), (-.015, .025))
# Po tracker.prune_stale(...): clocks.prune()
```

## Uruchomienie z katalogu głównego repo

```powershell
python -m pip install -r clock_experiment/requirements.txt
python -m unittest clock_experiment.test_track_clock -v
python -m clock_experiment.run
```

Wyniki pierwotnego przebiegu są już w `results/summary.json`; skrypt chroni je przed nadpisaniem. Ponowne uruchomienie wymaga osobnej kopii z nowym katalogiem wyników. Protokół jest w `PROTOCOL.md`, źródło i hash kopii zegara w `provenance.json`.

## Wynik

Mały test integracji obejmuje 4 przebiegi po 400 klatek: 2 przyspieszające modulacje oraz 2 próby z samym szumem. Zegar używa tylko pierwszych 300 amplitud, ostatnie 100 służy ocenie prognozy. Oba sygnały zaakceptował, oba szumy odrzucił. Wszystkie przebiegi zachowały jeden ID toru. Szczegółowe błędy i czasy są w `WYNIK.md` i JSON.

Nie jest to nowa walidacja na rzeczywistym radarze: repo nie zawiera zsynchronizowanych amplitud i niezależnej referencji obrotów. Generator ma strukturę zgodną z estymatorem, granice częstości podano z góry, próba jest mała. Nie wykazano poprawy pozycji, asocjacji ani prędkości lotu. Poprzednia poprawa 7,6% na Open Radar dotyczyła innego repo i innego algorytmu; nie przenosimy jej tutaj.

## Ograniczenie istniejących testów repo

Pełne zbieranie testów zatrzymuje się na `tests/test_real_data_validation.py`: repo bazowe nie zawiera importowanego `data/validate_on_real_trips.py` ani wskazanego pliku CSV. Nie zastąpiono tych danych syntetyką i nie usunięto testu. Pozostałe testy można uruchomić jawnie:

```powershell
python -m pytest tests clock_experiment/test_track_clock.py --ignore=tests/test_real_data_validation.py -q
```
