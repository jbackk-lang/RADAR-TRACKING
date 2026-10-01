# Jedna prędkość i niezależny znacznik czasu

10 ziaren; 6 obserwacji znanego reflektora na ziarno przy jednej nominalnej prędkości 1 obr/s. Zero enkodera .12°, przesunięcie czasu ±2 ms. Niezależny elektroniczny znacznik rejestrowany przez zegar echa i enkodera: 8 zdarzeń, niezależny szum każdego odczytu sigma=20 us. Przesunięcie estymowane medianą różnic czasów, nie z kąta ani prawdy generatora. Następnie zero enkodera z reflektora, po wyrównaniu czasu.

90 nowych pomiarów celów: .4,1.2,2 rad × 10 ziaren × 3 warunki: stały obrót; rzeczywista prędkość ±5% przy tym samym nominalnym 1 obr/s; ten sam zmienny obrót i zmiana przesunięcia zegara o ±.5 ms po kalibracji. W każdym skanie nowe 8 znaczników aktualizuje przesunięcie czasu; zero pozostaje zamrożone. Porównać raw, angle_only, marker_frozen oraz marker_current. angle_only używa średniej poprawki kąta z referencji, bez niezależnej informacji czasowej.

Ten sam zestaw nowych I/Q dla metod. Znaczniki są nową informacją instrumentalną, nie dodatkowymi emisjami radarowymi. Zakładamy wspólny punkt rejestracji znacznika i echa względem enkodera; nieskorygowane różnice opóźnień ścieżek sprzętowych mogą oszukać tę metodę. Błąd referencji, wielodrogowość i drgania mocowania pozostają osobnymi problemami. Nie wzbudzamy zmian nominalnej prędkości na potrzeby kalibracji. Jedna prędkość bez znaczników nadal nie rozdziela delay i zero.

Parametry przed oceną, bez strojenia. Zachować kalibrację przed celami, surowe elektroniczne znaczniki i wyniki bez nadpisywania. R/v bez zmian. Testy: odzyskanie różnicy zegarów bez szumu, znak poprawki, kalibracja zera przy jednej prędkości, odrzucenie nieprawidłowych znaczników. Nie deklarować wdrożenia sprzętowego.
