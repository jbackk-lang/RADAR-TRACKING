# Historia projektu

Aktualne uruchamianie opisuje [README](README.md). Ten plik zbiera etapy rozwoju; liczby są wynikami konkretnych eksperymentów, nie parametrami gwarantowanymi na sprzęcie.

## Październik 2026 — czytelna instrukcja i trudniejsze symulacje

- README przebudowano dla osoby zaczynającej: instalacja, uruchamianie, wybór modelu, interpretacja wykresu i rozwiązywanie problemów.
- Dawne opisy i wszystkie odnośniki zachowano w [archiwum](docs/HISTORY_ARCHIVE.md).
- Dodano [realistyczniejszy stress-test](outputs/angle_frequency/REALISTIC_TIMDR_PROTOCOL.md): szum odległości i kąta, zaniki, dodatkowe odbicia, krzyżowania i nieregularny czas. Nadal nie są to rzeczywiste pomiary radarowe.

- [Wyniki trudniejszych symulacji](outputs/angle_frequency/WYNIK_REALISTIC_TIMDR.md): nowy wariant nie wygrywa wszystkich metryk; dotychczasowy TIMDR pozostaje domyślny.

## Odporniejszy operator TIMDR

- Dodano czasowe tempo skrętu i zmiany prędkości, odporną regresję oraz zakładaną niepewność położenia.
- Na 4800 syntetycznych historiach nowy wariant ograniczył fałszywe manewry i lepiej wykrywał zadane zmiany ruchu. Na 100 łatwych sekwencjach tracker miał takie same pozycje i stabilność ID jak dotychczasowy wariant.
- Udostępniono opcję „TIMDR odporny”; dotychczasowy TIMDR pozostaje domyślny.
- [Wyniki i ograniczenia](outputs/angle_frequency/WYNIK_TIMDR_ROBUST.md).

## Demo w przeglądarce i wybór wariantu

- Dodano lokalny interfejs dla Windows, 4/8/12 obiektów, odtwarzanie 40 klatek i rzeczywisty backend RadarTracker.
- Dodano wybór CV, TIMDR dotychczasowego i później odpornego.
- Liczba śladów jest wynikiem trackera, a liczba obiektów w selektorze ustawieniem generatora. Nie utożsamiamy tych liczb.

## Model sceny na TIMDR

- Zbudowano osobny model dwóch detekcji: rzeczywisty operator TIMDR steruje predykcją asocjacji.
- 800 łatwych sekwencji: 100% etykiet w obu wariantach; 800 trudniejszych: 47,0% bez TIMDR i 48,125% z TIMDR. Spełniono lokalne kryterium niepogorszenia, ale reguły grupowania źle znosiły szum.
- Nie wykazano równoważności z każdym radarem ani klasyfikacji semantycznej.
- [Porównanie](outputs/angle_frequency/WYNIK_TIMDR_SCENE.md).

## Kształt echa i rozpoznawanie sceny

- Sprawdzono dopasowanie Gaussa, ogonów, kilku odbić oraz początku echa. Znane rodziny dawały lepszą lokalizację niż sam pik; słaby przód i nieznana odpowiedź odbiornika pozostawały problemem.
- [Końcowy bank kształtów](outputs/angle_frequency/WYNIK_FINAL_ECHO.md), [kształt Gaussa](outputs/angle_frequency/WYNIK_GAUSSIAN_SHAPE.md), [czoło obiektu](outputs/angle_frequency/WYNIK_ECHO_FRONT.md).
- Historia detekcji pozwoliła rozpoznać różny ruch i niektóre niespójności, ale jeden duży obiekt oraz dwa współporuszające się mogą być identyczne obserwacyjnie.
- [Rozpoznawanie sceny](outputs/angle_frequency/WYNIK_SCENE_RECOGNITION.md).

## Faza, ruch, dudnienie i rezonans

- Odwrócenie fazy całego I/Q nie zmienia mocy ani odległości.
- Faza nośnej pomogła mierzyć prędkość izolowanego echa; nie dała bezwzględnego R bez dodatkowej informacji.
- Sprawdzono dwie nośne, mniejszą różnicę częstotliwości, chirp i rezonans. Nie wykazano uniwersalnej korzyści.
- Kompensacja fazy ruchu pomagała przy stałej prędkości, ale zły model przyspieszenia pogarszał wynik.
- [Faza nośnej](outputs/angle_frequency/WYNIK_CARRIER.md), [dudnienie](outputs/angle_frequency/WYNIK_DUAL_BEAT.md), [chirp i rezonans](outputs/angle_frequency/WYNIK_WAVE_METHODS.md), [ruch w widmie](outputs/angle_frequency/WYNIK_RANGE_MOTION.md), [błysk energii](outputs/angle_frequency/WYNIK_FLASH.md).

## Kalibracja, pamięć i synchronizacja

- Pamięć ostatniej potwierdzonej poprawki była korzystniejsza niż adaptacja EMA dla części metryk; nie ogłoszono uniwersalnego zwycięzcy.
- Sprawdzono minimalną ingerencję, starzenie kalibracji, synchronizację czasu i kąta oraz łagodny rozruch.
- [Kalibracja czterostanowa](clock_experiment/ONLINE_WYNIK.md), [synchronizacja](outputs/angle_frequency/WYNIK_SYNC.md), [znaczniki czasu](outputs/angle_frequency/WYNIK_MARKER.md), [łagodny rozruch](outputs/angle_frequency/WYNIK_SETTLED.md).

## Pierwotny tracker

Połączono filtrowanie TRM, kierunek GIA, diagnostykę TIMDR, przypisywanie detekcji metodą węgierską, bramkowanie niepewności i wygładzanie pozycji. Wartością jest działające połączenie tych elementów. Wykorzystuje klasyczne narzędzia matematyczne; nie jest pełnym filtrem Kalmana ani implementacją całego formalizmu GIA-TIMDR.

Pełna wcześniejsza treść i pozostałe odnośniki: [archiwum dokumentacji](docs/HISTORY_ARCHIVE.md).
