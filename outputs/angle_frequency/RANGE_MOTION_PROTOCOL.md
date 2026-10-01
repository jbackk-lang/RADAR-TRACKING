# Ruch w widmie: faza i migracja odległości

Protokół przed testem: 3 GHz (osobny model, nie zmiana wcześniejszego 77 GHz), 32 kHz PRF, 512 impulsów, CPI15.97 ms, 20 MHz zakres. Doppler bez aliasingu do około +/-799 m/s. Energia impulsu stała, amplituda .25 i szum .15/składową. Gauss sigma1.5 próbki. Losowa odległość, wynik R odniesiony do środka okna czasowego.

Metody: dopasowanie Gaussa do niespójnej mocy, sumowanie zespolone bez wyrównania, wyrównanie fazy z oszacowanego Dopplera, oraz faza + interpolacyjne wyrównanie migracji zakresu z tej samej oszacowanej prędkości. Doppler z FFT4096 lokalnego wybranego okna zakresu, interpolacja piku; R dopasowanie krok .1 próbki. Bez użycia prawdziwej prędkości. Zera FFT nie zwiększają fizycznej rozdzielczości. Doppler estymowany z tych samych danych co test piku, więc próg wykrycia kalibrowany na pełnym przeszukiwaniu, nie na znanej częstotliwości.

100 osobnych scen szumu ustala 99.percentyl progów (higher). Test po60: pusty, nieruchomy, v30m/s, v600m/s, v100m/s z a3000m/s2. 600m/s służy pokazaniu migracji (~9.58m w oknie), nie typowemu ruchowi naziemnemu. Przy30m/s migracja .48m; wyrównanie zakresu może nie pomóc w tej siatce. Przyspieszenie testuje niedopasowanie modelu stałej prędkości.

MAE R wśród wykryć, poprawne gdy błąd<7.5m, fałszywe alarmy osobno. Bez obrotu, ogona rezonansowego, rozmiaru celu, wielodrogowości i sprzętu. To badanie ruchu izolowanego punktowego echa. Interpolacja może zmieniać szum i kształt — każdy wariant ma własny zamrożony próg. Nie gwarantujemy przeniesienia na77GHz ani zachowania poprzednich metryk. Główny tracker bez zmian. Wyniki chronione.
