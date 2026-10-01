# Kąt z częstotliwości — protokół przed testem

2026-10-01. Obecny radar_compensation.py generuje jeden kanał pulses×samples przy stałej carrier=77 GHz; bearing jest metadanymi, nie wynikiem z I/Q. sample_radar.npy zawiera jedynie frame,x,y,t. Nie można z tych danych odzyskać różnic faz antenowych ani ich zależności od częstotliwości.

Osobna symulacja idealizowanego, izolowanego celu dalekiego pola. Dwie zsynchronizowane anteny; f0=77 GHz, pasma 1 i 4 GHz, 17 równomiernych częstotliwości, 64 wspólne próbki na częstotliwość, rozstaw d=c/(2·79 GHz), niezależny zespolony szum z odchyleniem .15 dla każdej składowej. Kąty [-.6,-.4,-.2,0,.2,.4,.6] rad; 200 ziaren na kąt/pasmo/scenariusz. 8400 przypadków. Wszystkie metody korzystają z tego samego zestawu I/Q.

Faza między antenami: phi(f)=2*pi*f*(d*sin(theta)/c + channel_delay) + phase_offset. Scenariusze: clean (offset=0, delay=0), constant_phase (offset=.15 rad, delay=0), channel_delay (offset=.15 rad, delay=.2 ps). Stały offset w tej fazie nie jest tym samym co dodany błąd bearing w poprzednim modelu.

Metody: faza środkowej częstotliwości; dopasowanie fazy po całym paśmie z założeniem offset=0; nachylenie fazy z dwóch krańców; nachylenie fazy po wszystkich częstotliwościach z dopasowaniem nieznanego stałego offsetu. Każda metoda wyznacza sin(theta), a następnie arcsin. Wartości spoza [-1,1] są jawnie nieważne, bez ukrytego przycinania. Faza jest rozwijana wzdłuż częstotliwości; ten test ma jednoznaczny zakres dla zadanych kątów, mały odstęp częstotliwości i wysokie SNR.

Metryki: MAE i percentyl 95 błędu kąta w rad i stopniach, liczba nieważnych wyników. Raportować wszystkie scenariusze i oba pasma. Bez strojenia po wyniku. Testy bez szumu: odzyskanie kąta, usunięcie stałego offsetu, nierozróżnialność opóźnienia kanału od kąta, poprawność walidacji danych. Wyniki chronione przed nadpisaniem; hash protokołu i źródeł.

To nie FMCW z pełnym mieszaniem, nie wielodrogowość ani pomiar sprzętowy. Symulujemy dostępne próbki pasma RF już z izolowanym celem i wspólną fazą. 17 częstotliwości i drugi kanał są nowymi założeniami danych; nie deklarować zero dodatkowych danych względem starego eksperymentu. Wniosek o braku identyfikowalności channel_delay wynika z równania, nie tylko z MAE.
