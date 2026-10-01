# Przewaga rozpoznawania sceny zamiast liczenia pików

600syntetycznych sekwencji,12 zwykłych obserwacji każda. Dane:położenia2D i Doppler, nie nowy pomiar ani surowy detektor I/Q. Dwa punkty na klatkę mogą pochodzić z dwóch obiektów, dwóch części jednego lub odbicia dodatkowego.

| Scena | Wynik historii /100 | Zwrócona liczba obiektów | Rozciągłość grupy, mediana [m] |
|---|---|---|---:|
| Jeden sztywny duży | 100 spójnych grup | nierozstrzygnięta | 3.993 |
| Jeden obracający się | 100 spójnych grup | nierozstrzygnięta | 4.010 |
| Dwa rozchodzące się | 100 różnych ruchów | 2 w100/100 | 7.935 |
| Dwa równolegle poruszające się | 100 spójnych grup | nierozstrzygnięta | 4.001 |
| Obiekt i stały ghost | 100 spójnych grup | nierozstrzygnięta | 6.004 |
| Obiekt i ghost niespójny z Dopplerem | 100 niespójnych ech | nierozstrzygnięta | 8.459 |

Liczenie dwóch punktów jako dwóch obiektów było błędne w400/600 scenach. Analiza historii podała liczbę2tylko dla100sekwencji z różnym ruchem; pozostałe500 pozostawiła nierozstrzygnięte. Nie oznacza to100%rozpoznania: algorytm zmniejszył nadmierną pewność kosztem dużej liczby odmów.

Niespójność Dopplera z położeniem wskazuje problem z hipotezą bezpośredniego odbicia. Nie dowodzi, że to multipath, ani nie określa automatycznie liczby rzeczywistych obiektów. Scena niespójnego ghosta została specjalnie skonstruowana z dodatkową zmianą opóźnienia .9m/s bez zmiany Dopplera; nie jest pełnym fizycznym modelem wielodrogowości.

Sztywny obiekt i dwa równoległe obiekty mogą być identyczne obserwacyjnie. Kontrola na tym samym ziarnie potwierdziła dokładną zgodność wszystkich danych tych dwóch scen. Żaden klasyfikator na tych danych nie może wiarygodnie rozstrzygnąć takiej pary bez dodatkowych założeń lub informacji.

Rozciągłość grupy jest zmierzonym odstępem punktów. Nie jest automatycznie wielkością pojedynczego obiektu:6m w scenie ghosta nie oznacza6-metrowego celu. Wynik powinien zawierać grupę, widoczną rozciągłość, hipotezę ruchu i nierozstrzygniętą liczbę, zamiast pewnej nazwy obiektu.

W tym eksperymencie jest korzyść względem naiwnego liczenia punktów, ale nie wykazano przewagi nad standardowym trackerem. Prosty klasyczny algorytm wykorzystuje zgodność geometryczno-czasową; nie wdrożono ani nie ablowano TIMDR/TRM/GIA. Następny miarodajny krok to porównanie z istniejącym trackerem na tych samych detekcjach oraz sceny z zanikami, deformacją i rzeczywistym multipath.

Kontrole:nieodróżnialność jednego i dwóch współporuszających się celów, niezmienność na kolejność punktów, zachowanie grupy przy sztywnym obrocie. Protokół SCENE_RECOGNITION_PROTOCOL.md; pełne wyniki scene_recognition_results.json. Uruchomienie `python outputs/angle_frequency/run_scene_recognition.py`; chroni wyniki. Bez sprzętu, klasyfikacji semantycznej i integracji z głównym trackerem.
