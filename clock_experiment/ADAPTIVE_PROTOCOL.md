# Przełączanie zegar/sito → standard: pilot syntetyczny

2026-09-30. Protokół lokalny przed wynikami, bez strojenia po teście.

Porównanie identycznych danych: standardowy RadarTracker; zegar z sitem amplitudowym dopasowywany regularnie; adaptacyjny zegar z sitem. Rdzeń TRM/geometrii pozostaje identyczny. Sito to odrzucenie całej detekcji przy niezgodności amplitudy z prognozą, nie istniejący filtr gęstościowy TRM. Dodatkowy kanał amplitudy jest przypisany do jednego obiektu; nie rozwiązujemy asocjacji amplitud wielu obiektów.

100 próbek rozruchu; okno 200; dopasowanie nie częściej niż co 80 próbek. Zegar: f0 .3..1.2 Hz, drift -.015..025 Hz/s, 2 harmoniczne. Próg reszty max(4.5*MAD_sigma, .35*std, 1e-8). Dopasowanie zawsze po decyzji dla aktualnej próbki: aktualnej próbki nie używa się do jej własnego odrzucenia. W trybie adaptacyjnym 8 dobrych próbek przełącza do standardu; tani monitor prognozy amplitudy nadal działa. Anomalia natychmiast przywraca sito. Model wygasa po 400 próbkach. Zegar odrzucony przez własną kontrolę jakości nie zastępuje poprzedniego; stary model nadal wygasa. To offline fit na przeszłym oknie w przyczynowym przepływie próbek; obliczenia blokują obsługę podczas dopasowania, nie gwarantujemy czasu rzeczywistego.

4 scenariusze x 2 ziarna: clean, correlated (zakłócenia pozycji i amplitudy jednocześnie), amplitude_only (niezależność kanałów — kontrola negatywna założenia), position_only (zegarem nie widać błędu pozycji). 480 klatek 20 Hz, x=.2t, y=0; dwa echa +/- .01, wspólny szum pozycji sigma .015. Amplituda sin(theta)+.2cos(2theta+.4)+szum .1, theta=2pi(.5t+.5*.008t²). Bursty na indeksach 180..194 i 320..334: przesunięcie amplitudy +4 oraz/lub x +.8. Prawda syntetyczna służy tylko ocenie. Brak doboru parametrów na niej.

Metryki na wszystkich 480 klatkach: RMSE pozycji, liczba różnych ID, liczba odrzuconych klatek, liczba dopasowań, czas całego wariantu i osobno dopasowań. Gdy sito odrzuci detekcję, raportujemy predykcję istniejącego trackera dla tej chwili, więc utrata danych nie znika z wyniku. Standard porównawczy też dostaje ten sam strumień. Wszystkie wyniki zachowane. Jedno uruchomienie czasowe, kolejność wariantów rotowana między scenariuszami; liczby czasowe orientacyjne, bez wniosków statystycznych przy N=2.

Testuje konkretną hipotezę sprzężenia błędu amplitudy i pozycji na zgodnym z estymatorem generatorze, nie rzeczywisty radar ani przewagę uniwersalną. Zegar nie jest pomiarem prędkości postępowej. Nie przenosimy wyniku 7,6% z innego eksperymentu.
