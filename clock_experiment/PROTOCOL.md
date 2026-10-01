# Test integracji zegara z właściwym RADAR-TRACKING

2026-09-30. Lokalny protokół zapisany przed uruchomieniem tego testu. Kod bazowy: jbackk-lang/RADAR-TRACKING, commit 74916877dd0982b7dfef7f3c4921999e0ba3d275. Nie RADAR-TRACKING-TIMDR ani TIMDR-Radar-Module.

Bez zmiany geometrii/asocjacji: oddzielny bank amplitud przypisany do istniejących ID torów, osobna historia >=50 próbek, dopasowanie jawnie wywoływane offline. Zegar z astronomii skopiowany bez zmian, hash w provenance.json. Brak amplitudy => brak estymacji. Słaby zegar nie steruje pozycją ani prędkością postępową. Dopasowanie nie jest uruchamiane na każdej klatce.

Test end-to-end: 2 przypadki (narastająca częstość i szum), po 2 ziarna (0,1), 400 klatek 20 Hz, pojedynczy cel x=.2t, y=0; 2 echa +/- .01 wokół pozycji. Amplituda sin(theta)+.2cos(2theta+.4)+szum sigma .15, theta=2pi(.5t+.5*.01t²); kontrola negatywna: sam szum. Dostarczone priori f0 .3..85 Hz, drift -.015..025 Hz/s. Pierwsze 300 próbek służy dopasowaniu, ostatnie 100 tylko ocenie ekstrapolowanej częstotliwości. Prawda syntetyczna nie trafia do estymatora. Ocena poprawnego ID toru, akceptacji zegara, błędu częstości na końcowym fragmencie, czasu dopasowania. Prosty stałoczęstotliwościowy Lomb–Scargle na identycznych 300 próbkach jest odniesieniem. Zapis także odrzuconych estymacji; brak dobierania parametrów po wyniku.

To test integracji i prostej syntetycznej hipotezy, nie pomiar przewagi śledzenia pozycji ani realnego radaru. Generator należy do rodziny modelu zegara; priori ogranicza niejednoznaczność harmonicznych. W repo są dane pozycyjne, bez kanału amplitudy i niezależnych RPM. Dawne wyniki Open Radar 7,6% nie są wynikiem tego repo ani tego testu.
